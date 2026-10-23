"""OpenaiChatAdapter（通用 OpenAI 兼容端点适配器）的单元测试。"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "toolkit"))

from xiaoma_gen.adapters.base import AdapterError  # noqa: E402
from xiaoma_gen.adapters.openai_chat import OpenaiChatAdapter  # noqa: E402
from xiaoma_gen.models import ImageRequest, VideoRequest  # noqa: E402

CFG = {
    "key_env": "TEST_OAI_KEY",
    "key_file": "~/.test-oai-key",
    "base": "https://relay.example.com",
    "protocol": "openai-chat",
}


def chat_response(content: str) -> tuple[int, str]:
    return 200, json.dumps({
        "choices": [{"message": {"content": content}}],
    })


class FakeTransport:
    def __init__(self, status=200, content="结果: https://cdn.example.com/x.mp4"):
        self.status = status
        self.content = content
        self.calls: list[dict] = []

    def __call__(self, url, headers, body, timeout):
        self.calls.append({"url": url, "headers": headers, "body": body, "timeout": timeout})
        if isinstance(self.content, Exception):
            raise self.content
        if self.status != 200:
            return self.status, self.content  # 错误路径：原文
        return chat_response(self.content)     # 成功路径：(200, chat JSON)


def make_adapter(transport, key_env_value="sk-test"):
    with mock.patch.dict(os.environ, {"TEST_OAI_KEY": key_env_value}):
        # 在环境变量存在的情况下构造
        return OpenaiChatAdapter("relay", CFG, transport=transport)


class OkCases(unittest.TestCase):
    def test_generate_video_extracts_url(self):
        ft = FakeTransport(content="视频已生成：https://cdn.example.com/a.mp4 请查收")
        ad = make_adapter(ft)
        r = ad.generate_video(VideoRequest(prompt="一只猫在跳舞", model="video-model"))
        self.assertTrue(r.ok)
        self.assertEqual(r.urls, ["https://cdn.example.com/a.mp4"])
        self.assertIn("a.mp4", r.raw)
        # 请求走 chat 协议
        call = ft.calls[0]
        self.assertTrue(call["url"].endswith("/v1/chat/completions"))
        self.assertEqual(call["headers"]["Authorization"], "Bearer sk-test")

    def test_generate_image_extracts_url(self):
        ft = FakeTransport(content="![img](https://cdn.example.com/b.png)")
        ad = make_adapter(ft)
        r = ad.generate_image(ImageRequest(prompt="海报", model="image-model"))
        self.assertTrue(r.ok)
        self.assertEqual(r.urls, ["https://cdn.example.com/b.png"])

    def test_request_body_is_openai_chat_shape(self):
        ft = FakeTransport()
        ad = make_adapter(ft)
        ad.generate_video(VideoRequest(prompt="一只猫在跳舞", model="video-model"))
        body = ft.calls[0]["body"]
        self.assertIn("messages", body)
        self.assertEqual(body["messages"][0]["role"], "user")
        self.assertIn("一只猫在跳舞", body["messages"][0]["content"])

    def test_ratio_and_duration_embedded_in_prompt(self):
        ft = FakeTransport()
        ad = make_adapter(ft)
        ad.generate_video(VideoRequest(prompt="猫", duration=10, ratio="9:16", model="video-model"))
        content = ft.calls[0]["body"]["messages"][0]["content"]
        self.assertIn("9:16", content)
        self.assertIn("10", content)


class ErrorCases(unittest.TestCase):
    def test_no_url_in_response_is_error_with_raw(self):
        ft = FakeTransport(content="抱歉，余额不足，请充值后重试")
        ad = make_adapter(ft)
        r = ad.generate_video(VideoRequest(prompt="猫", model="video-model"))
        self.assertFalse(r.ok)
        self.assertIn("余额不足", r.error)
        self.assertIn("余额不足", r.raw)

    def test_http_error_status_is_error(self):
        ft = FakeTransport(status=401, content=json.dumps({"error": "Invalid token"}))
        ad = make_adapter(ft)
        r = ad.generate_image(ImageRequest(prompt="猫", model="image-model"))
        self.assertFalse(r.ok)
        self.assertIn("Invalid token", r.error)

    def test_transport_exception_is_error_not_crash(self):
        ft = FakeTransport(content=TimeoutError("read timeout"))
        ad = make_adapter(ft)
        r = ad.generate_image(ImageRequest(prompt="猫", model="image-model"))
        self.assertFalse(r.ok)
        self.assertIn("timeout", r.error.lower())

    def test_missing_key_raises_with_guidance(self):
        env = {k: v for k, v in os.environ.items() if k != "TEST_OAI_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), \
             mock.patch("xiaoma_gen.adapters.base.Path") as mph:
            mph.return_value.expanduser.return_value.is_file.return_value = False
            with self.assertRaises(AdapterError) as cm:
                OpenaiChatAdapter("relay", CFG, transport=FakeTransport())
        msg = str(cm.exception)
        self.assertIn("TEST_OAI_KEY", msg)
        self.assertIn("~/.test-oai-key", msg)


class RefCases(unittest.TestCase):
    def test_local_ref_becomes_data_url(self):
        ft = FakeTransport()
        ad = make_adapter(ft)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"\xff\xd8\xff\xe0fakejpg")
            ref = f.name
        try:
            ad.generate_video(VideoRequest(prompt="让画面动起来", refs=[ref], model="video-model"))
        finally:
            os.unlink(ref)
        content = ft.calls[0]["body"]["messages"][0]["content"]
        self.assertIsInstance(content, list)
        types = [c["type"] for c in content]
        self.assertIn("text", types)
        self.assertIn("image_url", types)
        img_part = next(c for c in content if c["type"] == "image_url")
        self.assertTrue(img_part["image_url"]["url"].startswith("data:image/jpeg;base64,"))

    def test_remote_ref_kept_as_url(self):
        ft = FakeTransport()
        ad = make_adapter(ft)
        ad.generate_image(ImageRequest(
            prompt="参考这张", refs=["https://cdn.example.com/r.jpg"], model="image-model"))
        content = ft.calls[0]["body"]["messages"][0]["content"]
        img_part = next(c for c in content if c["type"] == "image_url")
        self.assertEqual(img_part["image_url"]["url"], "https://cdn.example.com/r.jpg")


class MetaCases(unittest.TestCase):
    def test_get_balance_unsupported_returns_none(self):
        ad = make_adapter(FakeTransport())
        self.assertIsNone(ad.get_balance())

    def test_list_models_failure_returns_empty(self):
        ft = FakeTransport(status=500, content="err")
        ad = make_adapter(ft)
        self.assertEqual(ad.list_models("video"), [])


if __name__ == "__main__":
    unittest.main()
