"""build_portal.py 的单元测试：来源齐全、只读仓库内文件、产出符合纯知识口径。"""
import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools" / "build_portal.py"

spec = importlib.util.spec_from_file_location("build_portal", SCRIPT)
portal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(portal)

# 产出里不允许出现的平台名 / 产品名 / 样本 ID
BANNED = re.compile(
    r"抖音|即梦|红果|剪映|快手|小红书|Seedance|Claude|GPT|Higgsfield|可灵|douyin"
)
SAMPLE_ID = re.compile(r"(?<!\d)7\d{18}(?!\d)")


class TestSources(unittest.TestCase):
    def test_all_sources_exist(self):
        missing = [str(p) for _, entries in portal.GROUPS for _, _, p, _ in entries if not p.is_file()]
        self.assertEqual(missing, [])

    def test_sources_stay_inside_repo(self):
        outside = [
            str(p) for _, entries in portal.GROUPS for _, _, p, _ in entries
            if not p.resolve().is_relative_to(REPO.resolve())
        ]
        self.assertEqual(outside, [])

    def test_entry_ids_unique(self):
        ids = [eid for _, entries in portal.GROUPS for eid, _, _, _ in entries]
        self.assertEqual(len(ids), len(set(ids)))


class TestCleaning(unittest.TestCase):
    def test_platform_names_replaced(self):
        out = portal.clean_text("均来自抖音，用剪映剪，Seedance 出片")
        self.assertIsNone(BANNED.search(out))

    def test_strip_links_keeps_text(self):
        out = portal.strip_links("[样本](https://www.douyin.com/video/7690344836800913785)")
        self.assertEqual(out, "样本")


class TestBuild(unittest.TestCase):
    def test_build_output_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = portal.OUT
            portal.OUT = Path(tmp) / "index.html"
            try:
                self.assertEqual(portal.build(), 0)
                html = portal.OUT.read_text(encoding="utf-8")
            finally:
                portal.OUT = original
        self.assertIsNone(BANNED.search(html), BANNED.search(html))
        self.assertIsNone(SAMPLE_ID.search(html))
        self.assertNotIn("class='missing'", html)


if __name__ == "__main__":
    unittest.main()
