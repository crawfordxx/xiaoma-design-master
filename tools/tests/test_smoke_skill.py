"""smoke_skill.py 的单元测试：通过子进程调用真实接口（退出码）。"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SMOKE = REPO / "tools" / "smoke_skill.py"


def run_smoke(skill_dir: str, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SMOKE), skill_dir, *extra],
        capture_output=True, text=True, timeout=30,
    )


VALID_FRONTMATTER = """---
name: xiaoma-demo
version: 0.1.0
description: 演示技能，用于 smoke 测试。
triggers: [写演示, demo]
---

# 演示技能

正文内容，见 [方法论](shared/guide.md)。
生成时调用 `$S/toolkit/gen image --tier draft`。
"""


def make_skill(root: Path, name: str, skill_md: str | None,
               with_shared: bool = True) -> Path:
    """构造一个临时技能目录；with_shared 时同时建仓库级 shared/guide.md
    和技能内的相对 symlink `shared -> ../../shared`（与真实仓库结构一致）。"""
    skill_dir = root / "skills" / name
    skill_dir.mkdir(parents=True)
    if skill_md is not None:
        (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    if with_shared:
        shared = root / "shared"
        shared.mkdir(exist_ok=True)
        (shared / "guide.md").write_text("# guide\n", encoding="utf-8")
        (skill_dir / "shared").symlink_to("../../shared")
    return skill_dir


class SmokeBasicTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_valid_skill_passes_basic_and_strict(self):
        d = make_skill(self.root, "xiaoma-demo", VALID_FRONTMATTER)
        for extra in ([], ["--strict-gen"]):
            r = run_smoke(str(d), *extra)
            self.assertEqual(r.returncode, 0, msg=f"{extra}: {r.stdout}{r.stderr}")

    def test_missing_skill_md_fails(self):
        d = make_skill(self.root, "xiaoma-demo", None)
        r = run_smoke(str(d))
        self.assertEqual(r.returncode, 1)
        self.assertIn("SKILL.md", r.stdout + r.stderr)

    def test_broken_relative_link_fails(self):
        md = VALID_FRONTMATTER + "\n坏链接 [x](shared/missing.md)\n"
        d = make_skill(self.root, "xiaoma-demo", md)
        r = run_smoke(str(d))
        self.assertEqual(r.returncode, 1)
        self.assertIn("missing.md", r.stdout + r.stderr)


class SmokeInstalledPathTests(unittest.TestCase):
    """技能以 symlink 装进 ~/.claude/skills/ 后，路径按字面规整（Read 工具的行为）也必须可解析。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _install_link(self, skill_dir: Path) -> Path:
        agent_skills = self.root / "home" / ".claude" / "skills"
        agent_skills.mkdir(parents=True)
        link = agent_skills / skill_dir.name
        link.symlink_to(skill_dir)
        return link

    def test_link_escaping_skill_dir_fails(self):
        md = VALID_FRONTMATTER + "\n旧写法 [x](../../shared/guide.md)\n"
        d = make_skill(self.root, "xiaoma-demo", md)
        r = run_smoke(str(d))
        self.assertEqual(r.returncode, 1)
        self.assertIn("../../shared/guide.md", r.stdout + r.stderr)

    def test_parent_dir_command_path_fails(self):
        md = VALID_FRONTMATTER + "\n执行 `../../toolkit/gen image`\n"
        d = make_skill(self.root, "xiaoma-demo", md)
        r = run_smoke(str(d))
        self.assertEqual(r.returncode, 1)
        self.assertIn("../", r.stdout + r.stderr)

    def test_valid_skill_passes_through_install_symlink(self):
        d = make_skill(self.root, "xiaoma-demo", VALID_FRONTMATTER)
        r = run_smoke(str(self._install_link(d)), "--strict-gen")
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)


class SmokeFrontmatterTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_version_warns_only_at_basic(self):
        md = VALID_FRONTMATTER.replace("version: 0.1.0\n", "")
        d = make_skill(self.root, "xiaoma-demo", md)
        r = run_smoke(str(d))
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
        self.assertIn("WARN", r.stdout + r.stderr)
        r = run_smoke(str(d), "--strict-gen")
        self.assertEqual(r.returncode, 1)

    def test_name_mismatch_fails_at_strict(self):
        md = VALID_FRONTMATTER.replace("name: xiaoma-demo", "name: other-name")
        d = make_skill(self.root, "xiaoma-demo", md)
        r = run_smoke(str(d), "--strict-gen")
        self.assertEqual(r.returncode, 1)
        self.assertIn("name", r.stdout + r.stderr)


class SmokeStrictGenTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _strict_violation(self, snippet: str, needle: str):
        d = make_skill(self.root, "xiaoma-demo", VALID_FRONTMATTER + "\n" + snippet + "\n")
        r_basic = run_smoke(str(d))
        self.assertEqual(r_basic.returncode, 0, msg=r_basic.stdout + r_basic.stderr)
        r = run_smoke(str(d), "--strict-gen")
        self.assertEqual(r.returncode, 1)
        self.assertIn(needle, r.stdout + r.stderr)

    def test_banned_model_name(self):
        self._strict_violation("用 seed-2.5 生成", "seed-2")

    def test_banned_provider_domain(self):
        self._strict_violation("请求 agentwan.wdsheng.com 接口", "agentwan")

    def test_banned_curl_direct(self):
        self._strict_violation("执行 curl -X POST https://api.example.com/v1", "curl")


if __name__ == "__main__":
    unittest.main()
