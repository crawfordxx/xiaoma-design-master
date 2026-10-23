"""registry 加载与 resolve 的单元测试（针对真实 providers.toml）。"""
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "toolkit"))

from xiaoma_gen.models import GenResult, ImageRequest, LlmRequest, VideoRequest  # noqa: E402
from xiaoma_gen.registry import ConfigError, Registry, load_registry  # noqa: E402

TOML = REPO / "toolkit" / "providers.example.toml"


class LoadAndResolveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = load_registry(TOML)

    def test_resolve_video_draft_defaults(self):
        r = self.reg.resolve("video", "draft", None)
        self.assertEqual(r.provider, "my-relay")
        self.assertEqual(r.model, "my-video-model-fast")

    def test_resolve_video_final_defaults(self):
        r = self.reg.resolve("video", "final", None)
        self.assertEqual(r.provider, "my-relay")
        self.assertEqual(r.model, "my-video-model")

    def test_resolve_image_final(self):
        r = self.reg.resolve("image", "final", None)
        self.assertEqual(r.provider, "my-relay")
        self.assertEqual(r.model, "my-image-model")

    def test_resolve_with_explicit_model(self):
        r = self.reg.resolve("video", None, "my-video-model-fast")
        self.assertEqual(r.provider, "my-relay")
        self.assertEqual(r.model, "my-video-model-fast")

    def test_resolution_carries_provider_cfg(self):
        r = self.reg.resolve("video", "final", None)
        self.assertEqual(r.cfg["base"], "https://your-relay.example.com")
        self.assertEqual(r.cfg["protocol"], "openai-chat")


class ConfigErrorTests(unittest.TestCase):
    def test_bad_toml_raises_config_error_with_path(self):
        with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
            f.write("this is [not valid toml {{{")
            bad = Path(f.name)
        try:
            with self.assertRaises(ConfigError) as cm:
                load_registry(bad)
            self.assertIn(str(bad), str(cm.exception))
        finally:
            bad.unlink()

    def test_unknown_tier_raises_config_error_with_field(self):
        reg = load_registry(TOML)
        with self.assertRaises(ConfigError) as cm:
            reg.resolve("video", "ultra", None)
        self.assertIn("defaults.video.ultra", str(cm.exception))

    def test_unknown_model_raises_config_error(self):
        reg = load_registry(TOML)
        with self.assertRaises(ConfigError):
            reg.resolve("video", None, "no-such-model")


class ModelDataclassTests(unittest.TestCase):
    def test_request_and_result_shapes(self):
        img = ImageRequest(prompt="p", refs=[], ratio="3:4", tier="draft",
                           model=None, out=None, dry_run=True)
        vid = VideoRequest(prompt="p", refs=["a.jpg"], duration=10, ratio=None,
                           tier="final", model=None, out=None, dry_run=False)
        llm = LlmRequest(prompt="p", system="s", model=None, json_mode=False)
        res = GenResult(ok=True, urls=["https://x"], local_paths=[], raw="r", error=None)
        self.assertTrue(img.dry_run and not vid.dry_run)
        self.assertEqual(vid.duration, 10)
        self.assertIsNone(llm.model)
        self.assertTrue(res.ok)


if __name__ == "__main__":
    unittest.main()
