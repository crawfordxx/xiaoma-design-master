"""AsyncVideoAdapter（异步任务协议：提交 + 轮询）的单元测试。"""
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "toolkit"))

from xiaoma_gen.adapters.async_video import AsyncVideoAdapter  # noqa: E402
from xiaoma_gen.models import ImageRequest, VideoRequest  # noqa: E402

CFG = {
    "key_env": "VIDEO_API_KEY",
    "base": "https://video-gateway.example.com",
    "protocol": "async-video",
}


class ScriptedTransport:
    """按调用序返回预设响应：第 1 次提交，其余轮询。"""

    def __init__(self, submit_resp, poll_resps):
        self.submit_resp = submit_resp
        self.poll_resps = list(poll_resps)
        self.calls = []

    def __call__(self, url, headers, body, timeout, method="POST", poll=None):
        # 统一签名：transport(url, headers, body|None, timeout, method)
        self.calls.append({"url": url, "body": body, "method": method})
        if method == "POST":
            return self.submit_resp
        if self.poll_resps:
            return self.poll_resps.pop(0)
        return (200, json.dumps({"code": "task_not_exist", "data": None}))


def submit_ok(task_id="task_123"):
    # 实测：/v1/video/generations 提交返回 OpenAI 风格（顶层 id/task_id），不是网关信封
    return 200, json.dumps({"id": task_id, "task_id": task_id, "object": "video",
                            "model": "seed-2-mini", "status": "queued", "progress": 0})


def poll(status, video_url="https://cdn.example.com/v.mp4", fail_reason=""):
    return 200, json.dumps({
        "code": "success",
        "data": {
            "status": status, "fail_reason": fail_reason, "progress": "50%",
            "data": {"content": {"video_url": video_url}},
        },
    })


def make_adapter(transport):
    getter = lambda url, headers, timeout: transport(url, headers, None, timeout, method="GET")  # noqa: E731
    with mock.patch.dict(os.environ, {"VIDEO_API_KEY": "sk-kk"}):
        return AsyncVideoAdapter("async-video", CFG, transport=transport,
                                 getter=getter, poll_interval=0)


class OkTests(unittest.TestCase):
    def test_submit_then_poll_to_success(self):
        ft = ScriptedTransport(submit_ok(), [
            poll("IN_PROGRESS"), poll("SUCCESS", video_url="https://t.x/a.mp4")])
        ad = make_adapter(ft)
        r = ad.generate_video(VideoRequest(prompt="猫跳舞", model="seed-2-mini",
                                            duration=5, ratio="9:16"))
        self.assertTrue(r.ok, msg=r.error)
        self.assertEqual(r.urls, ["https://t.x/a.mp4"])
        # 提交体：模型 + prompt + metadata(时长/比例)
        submit = ft.calls[0]
        body = submit["body"]
        self.assertTrue(submit["url"].endswith("/v1/video/generations"))
        self.assertEqual(body["model"], "seed-2-mini")
        self.assertEqual(body["metadata"]["duration"], 5)
        self.assertEqual(body["metadata"]["ratio"], "9:16")

    def test_duration_default_and_audio_flag(self):
        ft = ScriptedTransport(submit_ok(), [poll("SUCCESS")])
        ad = make_adapter(ft)
        ad.generate_video(VideoRequest(prompt="x", model="seed-2-mini"))
        body = ft.calls[0]["body"]
        self.assertNotIn("duration", body["metadata"])  # 未指定不传
        self.assertIn("generate_audio", body["metadata"])

    def test_url_ref_passed_as_image(self):
        ft = ScriptedTransport(submit_ok(), [poll("SUCCESS")])
        ad = make_adapter(ft)
        ad.generate_video(VideoRequest(prompt="动起来", model="seed-2-mini",
                                        refs=["https://cdn.example.com/kf.png"]))
        body = ft.calls[0]["body"]
        self.assertEqual(body["image"], "https://cdn.example.com/kf.png")


class ErrorTests(unittest.TestCase):
    def test_local_ref_rejected_with_hint(self):
        ad = make_adapter(ScriptedTransport(submit_ok(), [poll("SUCCESS")]))
        r = ad.generate_video(VideoRequest(prompt="x", model="seed-2-mini",
                                            refs=["./local.png"]))
        self.assertFalse(r.ok)
        self.assertIn("公网 URL", r.error)

    def test_failure_status_reported_not_fake_url(self):
        # 失败时 video_url 里装的是错误文案——只能信状态
        ft = ScriptedTransport(submit_ok(), [
            poll("FAILURE", video_url="版权拦截：画面含受限内容", fail_reason="版权拦截")])
        ad = make_adapter(ft)
        r = ad.generate_video(VideoRequest(prompt="x", model="seed-2-mini"))
        self.assertFalse(r.ok)
        self.assertIn("版权拦截", r.error)
        self.assertEqual(r.urls, [])

    def test_submit_http_error(self):
        ft = ScriptedTransport((401, json.dumps({"message": "Invalid token"})), [])
        ad = make_adapter(ft)
        r = ad.generate_video(VideoRequest(prompt="x", model="seed-2-mini"))
        self.assertFalse(r.ok)
        self.assertIn("Invalid token", r.error)

    def test_image_unsupported(self):
        ad = make_adapter(ScriptedTransport(submit_ok(), [poll("SUCCESS")]))
        r = ad.generate_image(ImageRequest(prompt="x", model="m"))
        self.assertFalse(r.ok)


if __name__ == "__main__":
    unittest.main()
