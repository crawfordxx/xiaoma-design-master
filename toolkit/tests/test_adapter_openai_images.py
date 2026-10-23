"""OpenaiImagesAdapter（标准 /v1/images/generations 协议）的单元测试。"""
import base64
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "toolkit"))

from xiaoma_gen.adapters.openai_images import OpenaiImagesAdapter  # noqa: E402
from xiaoma_gen.models import ImageRequest, VideoRequest  # noqa: E402

CFG = {
    "key_env": "TEST_OAI_IMG_KEY",
    "base": "https://api.test.example.com/v1",
    "protocol": "openai-images",
}


class FakeTransport:
    def __init__(self, status=200, payload=None):
        self.status = status
        self.payload = payload or {"data": [{"url": "https://cdn.example.com/x.png"}]}
        self.calls = []

    def __call__(self, url, headers, body, timeout):
        self.calls.append({"url": url, "headers": headers, "body": body})
        return self.status, json.dumps(self.payload)


def make_adapter(transport):
    with mock.patch.dict(os.environ, {"TEST_OAI_IMG_KEY": "sk-img"}):
        return OpenaiImagesAdapter("std", CFG, transport=transport)


class OkCases(unittest.TestCase):
    def test_url_response(self):
        ad = make_adapter(FakeTransport())
        r = ad.generate_image(ImageRequest(prompt="猫", model="gpt-image-1"))
        self.assertTrue(r.ok)
        self.assertEqual(r.urls, ["https://cdn.example.com/x.png"])

    def test_b64_response_becomes_data_url(self):
        b64 = base64.b64encode(b"pngbytes").decode()
        ad = make_adapter(FakeTransport(payload={"data": [{"b64_json": b64}]}))
        r = ad.generate_image(ImageRequest(prompt="猫", model="gpt-image-1"))
        self.assertTrue(r.ok)
        self.assertTrue(r.urls[0].startswith("data:image/png;base64,"))

    def test_request_hits_images_endpoint_with_model(self):
        ft = FakeTransport()
        ad = make_adapter(ft)
        ad.generate_image(ImageRequest(prompt="猫", model="gpt-image-1"))
        call = ft.calls[0]
        self.assertTrue(call["url"].endswith("/images/generations"))
        self.assertEqual(call["body"]["model"], "gpt-image-1")
        self.assertEqual(call["headers"]["Authorization"], "Bearer sk-img")

    def test_ratio_mapped_to_openai_size(self):
        ft = FakeTransport()
        ad = make_adapter(ft)
        ad.generate_image(ImageRequest(prompt="猫", model="m", ratio="3:4"))
        ad.generate_image(ImageRequest(prompt="猫", model="m", ratio="4:3"))
        ad.generate_image(ImageRequest(prompt="猫", model="m", ratio="1:1"))
        ad.generate_image(ImageRequest(prompt="猫", model="m", ratio="2.35:1"))
        ad.generate_image(ImageRequest(prompt="猫", model="m", ratio="4:1"))
        self.assertEqual(ft.calls[0]["body"]["size"], "1024x1536")
        self.assertEqual(ft.calls[1]["body"]["size"], "1536x1024")
        self.assertEqual(ft.calls[2]["body"]["size"], "1024x1024")
        self.assertEqual(ft.calls[3]["body"]["size"], "1920x816")
        self.assertEqual(ft.calls[4]["body"]["size"], "1600x400")


class ErrorCases(unittest.TestCase):
    def test_http_error(self):
        ad = make_adapter(FakeTransport(status=429, payload={"error": {"message": "rate limited"}}))
        r = ad.generate_image(ImageRequest(prompt="猫", model="m"))
        self.assertFalse(r.ok)
        self.assertIn("rate limited", r.error)

    def test_empty_data_is_error(self):
        ad = make_adapter(FakeTransport(payload={"data": []}))
        r = ad.generate_image(ImageRequest(prompt="猫", model="m"))
        self.assertFalse(r.ok)

    def test_video_unsupported(self):
        ad = make_adapter(FakeTransport())
        r = ad.generate_video(VideoRequest(prompt="猫", model="m"))
        self.assertFalse(r.ok)
        self.assertIn("不支持", r.error)

    def test_refs_unsupported(self):
        ad = make_adapter(FakeTransport())
        r = ad.generate_image(ImageRequest(prompt="猫", model="m",
                                           refs=["https://x/y.jpg"]))
        self.assertFalse(r.ok)
        self.assertIn("参考图", r.error)


if __name__ == "__main__":
    unittest.main()
