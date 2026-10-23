"""executor 的单元测试：tier/余额前置/下载/meta/history/故障转移。"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "toolkit"))

from xiaoma_gen.adapters.base import Adapter  # noqa: E402
from xiaoma_gen.executor import run_generation  # noqa: E402
from xiaoma_gen.models import GenResult, ImageRequest  # noqa: E402
from xiaoma_gen.registry import load_registry  # noqa: E402

TOML = """\
[providers.alpha]
enable = true
key_env = "K_ALPHA"
base = "https://a.example.com"
protocol = "openai-chat"
[providers.alpha.caps.image.models."a-img"]
tier = "final"
[providers.alpha.caps.image.models."a-img-fast"]
tier = "draft"

[providers.beta]
enable = true
key_env = "K_BETA"
base = "https://b.example.com"
protocol = "openai-chat"
[providers.beta.caps.image.models."b-img"]
tier = "final"

[defaults.image]
draft = "alpha:a-img-fast"
final = "alpha:a-img"
"""


class FakeAdapter(Adapter):
    def __init__(self, name, result: GenResult, balance=None):
        super().__init__(name, {}, transport=lambda *a: (0, ""))
        self.result = result
        self._balance = balance
        self.gen_calls = 0

    def generate_image(self, req):
        self.gen_calls += 1
        return self.result

    def generate_video(self, req):
        self.gen_calls += 1
        return self.result

    def get_balance(self):
        return self._balance


OK = GenResult(ok=True, urls=["https://cdn.example.com/pic.png"], raw="ok")
FAIL = GenResult(ok=False, error="provider A 挂了")


class ExecutorTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.cfg = self.root / "p.toml"
        self.cfg.write_text(TOML, encoding="utf-8")
        self.reg = load_registry(self.cfg)
        self.workspace = self.root / "workspace"

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, req, adapters, downloader=None):
        return run_generation(req, self.reg, adapters,
                              repo_root=self.root, downloader=downloader)

    def test_success_writes_output_meta_history(self):
        alpha = FakeAdapter("alpha", OK)
        r = self._run(ImageRequest(prompt="猫", tier="final", model=None),
                      {"alpha": alpha},
                      downloader=lambda url: b"pngdata")
        self.assertTrue(r.ok)
        out_dir = self.workspace / "output"
        files = list(out_dir.glob("*"))
        media = [f for f in files if f.suffix == ".png"]
        metas = [f for f in files if f.name.endswith(".meta.json")]
        self.assertEqual(len(media), 1)
        self.assertEqual(len(metas), 1)
        meta = json.loads(metas[0].read_text(encoding="utf-8"))
        self.assertEqual(meta["provider"], "alpha")
        self.assertEqual(meta["model"], "a-img")
        self.assertEqual(meta["tier"], "final")
        self.assertIn("prompt", meta)
        hist = (self.workspace / "history.jsonl").read_text(encoding="utf-8").strip()
        self.assertEqual(len(hist.splitlines()), 1)
        self.assertTrue(json.loads(hist)["ok"])

    def test_download_failure_keeps_meta_and_no_regen(self):
        alpha = FakeAdapter("alpha", OK)

        def bad_downloader(url):
            raise OSError("404 not found")

        r = self._run(ImageRequest(prompt="猫", tier="final", model=None),
                      {"alpha": alpha}, downloader=bad_downloader)
        self.assertFalse(r.ok)
        self.assertIn("下载失败", r.error or "")
        self.assertEqual(alpha.gen_calls, 1)  # 绝不重复生成
        metas = list((self.workspace / "output").glob("*.meta.json"))
        self.assertEqual(len(metas), 1)
        meta = json.loads(metas[0].read_text(encoding="utf-8"))
        self.assertFalse(meta["downloaded_ok"])

    def test_final_zero_balance_blocks_generation(self):
        alpha = FakeAdapter("alpha", OK, balance={"balance": 0})
        r = self._run(ImageRequest(prompt="猫", tier="final", model=None),
                      {"alpha": alpha}, downloader=lambda url: b"x")
        self.assertFalse(r.ok)
        self.assertIn("余额", r.error or "")
        self.assertEqual(alpha.gen_calls, 0)  # 未发生成请求

    def test_final_balance_unsupported_continues(self):
        alpha = FakeAdapter("alpha", OK, balance=None)
        r = self._run(ImageRequest(prompt="猫", tier="final", model=None),
                      {"alpha": alpha}, downloader=lambda url: b"x")
        self.assertTrue(r.ok)
        self.assertEqual(alpha.gen_calls, 1)

    def test_provider_failover_to_beta(self):
        alpha = FakeAdapter("alpha", FAIL)
        beta = FakeAdapter("beta", OK)
        r = self._run(ImageRequest(prompt="猫", tier="final", model=None),
                      {"alpha": alpha, "beta": beta},
                      downloader=lambda url: b"x")
        self.assertTrue(r.ok)
        self.assertEqual(alpha.gen_calls, 1)
        self.assertEqual(beta.gen_calls, 1)

    def test_all_providers_fail_reports_last_error(self):
        alpha = FakeAdapter("alpha", FAIL)
        beta = FakeAdapter("beta", GenResult(ok=False, error="B 也挂了"))
        r = self._run(ImageRequest(prompt="猫", tier="final", model=None),
                      {"alpha": alpha, "beta": beta})
        self.assertFalse(r.ok)
        self.assertIn("B 也挂了", r.error)

    def test_out_path_also_saved(self):
        alpha = FakeAdapter("alpha", OK)
        out = self.root / "proj" / "cover.png"
        r = self._run(ImageRequest(prompt="猫", tier="final", model=None, out=str(out)),
                      {"alpha": alpha}, downloader=lambda url: b"pngdata")
        self.assertTrue(r.ok)
        self.assertTrue(out.is_file())
        self.assertEqual(out.read_bytes(), b"pngdata")

    def test_data_url_download(self):
        import base64
        payload = base64.b64encode(b"dataurlbytes").decode()
        ok = GenResult(ok=True, urls=[f"data:image/png;base64,{payload}"], raw="ok")
        alpha = FakeAdapter("alpha", ok)
        r = self._run(ImageRequest(prompt="猫", tier="final", model=None),
                      {"alpha": alpha}, downloader=None)  # 默认下载器
        self.assertTrue(r.ok)
        self.assertEqual(len(r.local_paths), 1)
        self.assertEqual(Path(r.local_paths[0]).read_bytes(), b"dataurlbytes")


if __name__ == "__main__":
    unittest.main()
