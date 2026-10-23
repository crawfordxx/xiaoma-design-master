"""install.sh 的单元测试：临时 HOME 下真实执行 bash 脚本，断言 symlink 行为。"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL = REPO / "install.sh"


def run_install(home: Path, *args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, HOME=str(home))
    return subprocess.run(
        ["bash", str(INSTALL), *args],
        capture_output=True, text=True, timeout=60, env=env, cwd=str(REPO),
    )


class InstallTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        self.pi_dir = self.home / ".pi" / "agent" / "skills"
        self.claude_dir = self.home / ".claude" / "skills"
        self.pi_dir.mkdir(parents=True)
        self.claude_dir.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def _installed(self, skills_dir: Path) -> set[str]:
        return {p.name for p in skills_dir.iterdir()}

    def test_install_symlinks_all_skills_to_detected_targets(self):
        r = run_install(self.home)
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
        expected = {p.name for p in (REPO / "skills").iterdir() if p.is_dir()}
        self.assertEqual(self._installed(self.pi_dir), expected)
        self.assertEqual(self._installed(self.claude_dir), expected)
        # symlink 指向仓库真身
        link = self.pi_dir / "xiaoma-ppt"
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), (REPO / "skills" / "xiaoma-ppt").resolve())

    def test_rerun_is_idempotent(self):
        run_install(self.home)
        r = run_install(self.home)
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
        expected = {p.name for p in (REPO / "skills").iterdir() if p.is_dir()}
        self.assertEqual(self._installed(self.pi_dir), expected)

    def test_existing_real_dir_is_skipped_with_warning(self):
        conflict = self.pi_dir / "xiaoma-ppt"
        conflict.mkdir()  # 真实目录，非本仓库 symlink
        (conflict / "keep.txt").write_text("user data")
        r = run_install(self.home)
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
        self.assertIn("SKIP", r.stdout + r.stderr)
        self.assertTrue((conflict / "keep.txt").exists())  # 不覆盖
        self.assertFalse(conflict.is_symlink())

    def test_target_pi_only(self):
        r = run_install(self.home, "--target", "pi")
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
        self.assertTrue(self._installed(self.pi_dir))
        self.assertEqual(self._installed(self.claude_dir), set())

    def test_skills_subset(self):
        r = run_install(self.home, "--skills", "xiaoma-ppt,xiaoma-designer")
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
        self.assertEqual(self._installed(self.pi_dir), {"xiaoma-ppt", "xiaoma-designer"})

    def test_uninstall_removes_only_our_symlinks(self):
        run_install(self.home)
        foreign = self.pi_dir / "someone-else"
        foreign.mkdir()  # 非本仓库的目录，卸载不能动
        r = run_install(self.home, "--uninstall")
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
        self.assertEqual(self._installed(self.pi_dir), {"someone-else"})
        self.assertTrue(foreign.exists())
        # 再次卸载（无链接）也成功
        r2 = run_install(self.home, "--uninstall")
        self.assertEqual(r2.returncode, 0)


if __name__ == "__main__":
    unittest.main()
