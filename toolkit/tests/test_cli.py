"""gen CLI 的单元测试：dry-run 无需 key、缺配置/缺 key 的友好错误。"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GEN = REPO / "toolkit" / "gen.py"
GEN_SH = REPO / "toolkit" / "gen"

FIXTURE_TOML = """\
[providers.testrelay]
enable = true
key_env = "TESTGEN_KEY"
key_file = "~/.testgen-key"
base = "https://relay.test.example.com"
protocol = "openai-chat"

[providers.testrelay.caps.image.models."img-model"]
tier = "final"

[providers.testrelay.caps.video.models."vid-model-fast"]
tier = "draft"

[providers.testrelay.caps.video.models."vid-model"]
tier = "final"

[defaults.image]
draft = "testrelay:img-model"
final = "testrelay:img-model"

[defaults.video]
draft = "testrelay:vid-model-fast"
final = "testrelay:vid-model"

[defaults.llm]
draft = ""
final = ""
"""


def run_gen(argv: list[str], extra_env: dict | None = None) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items()
           if k not in ("TESTGEN_KEY", "XIAOMA_PROVIDERS")}
    if extra_env:
        env.update(extra_env)
    return subprocess.run([sys.executable, str(GEN), *argv],
                          capture_output=True, text=True, timeout=60, env=env)


class DryRunTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cfg = Path(self._tmp.name) / "providers.toml"
        self.cfg.write_text(FIXTURE_TOML, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_image_dry_run_without_key_ok(self):
        r = run_gen(["image", "--prompt", "一张海报", "--dry-run",
                     "--config", str(self.cfg)])
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
        self.assertIn("DRY-RUN", r.stdout)
        self.assertIn("testrelay", r.stdout)
        self.assertIn("img-model", r.stdout)

    def test_video_dry_run_shows_tier_model(self):
        r = run_gen(["video", "--prompt", "猫跳舞", "--dry-run",
                     "--config", str(self.cfg)])
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
        self.assertIn("vid-model-fast", r.stdout)  # 默认 draft 档

    def test_dry_run_counts_refs(self):
        r = run_gen(["image", "--prompt", "参考图", "--ref", "a.jpg", "--ref", "b.jpg",
                     "--dry-run", "--config", str(self.cfg)])
        self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
        self.assertIn("refs=2", r.stdout)


class ErrorPathTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cfg = Path(self._tmp.name) / "providers.toml"
        self.cfg.write_text(FIXTURE_TOML, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_config_points_to_example(self):
        r = run_gen(["image", "--prompt", "x", "--dry-run", "--config", "/nonexistent.toml"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("providers.example.toml", r.stderr)

    def test_real_call_without_key_exits_2_with_guidance(self):
        r = run_gen(["image", "--prompt", "x", "--config", str(self.cfg)])
        self.assertEqual(r.returncode, 2)
        self.assertIn("TESTGEN_KEY", r.stderr)
        self.assertIn("~/.testgen-key", r.stderr)


class WrapperTests(unittest.TestCase):
    def test_bash_wrapper_executes_gen_py(self):
        r = subprocess.run(["bash", str(GEN_SH), "--help"],
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("image", r.stdout)


if __name__ == "__main__":
    unittest.main()
