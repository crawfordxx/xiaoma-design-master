"""KKHub 视频适配器（kkhub-video 协议：异步任务提交 + 轮询）。

提交: POST <base>/v1/video/generations  {model, prompt, image?, metadata:{duration, ratio, generate_audio, watermark}}
轮询: GET  <base>/v1/video/generations/{task_id} → data.status: NOT_START/SUBMITTED/QUEUED/IN_PROGRESS → SUCCESS/FAILURE
注意: 失败时 data.data.content.video_url 里装的是错误文案——只能信状态，不能信 URL。
"""
from __future__ import annotations

import json
import time

from ..models import GenResult, ImageRequest, VideoRequest
from .base import Adapter, resolve_key

_SUBMIT_TIMEOUT = 60
_POLL_TOTAL = 600  # 视频生成几分钟属正常


class KkhubVideoAdapter(Adapter):
    def __init__(self, name: str, cfg: dict, transport=None, getter=None,
                 poll_interval: float = 10.0):
        super().__init__(name, cfg, transport=transport, getter=getter)
        self._api_key = resolve_key(cfg)
        self._poll_interval = poll_interval

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._api_key}"}

    @staticmethod
    def _parse(status: int, text: str) -> dict:
        try:
            j = json.loads(text)
        except Exception:
            return {"_raw": text, "_status": status}
        if isinstance(j, dict):
            j["_http"] = status
            return j
        return {"_raw": text, "_status": status}

    def generate_video(self, req: VideoRequest) -> GenResult:
        body: dict = {"model": req.model, "prompt": req.prompt}
        # 参考图：只收公网 URL（该网关 base64 会 asset_ref_invalid）
        if req.refs:
            for ref in req.refs:
                if not ref.startswith(("http://", "https://")):
                    return GenResult(
                        ok=False,
                        error="kkhub 视频接口的参考图只收公网 URL（本地图请先上传取 URL）")
            body["image"] = req.refs[0]  # 首帧图
        meta: dict = {"generate_audio": True, "watermark": False}
        if req.duration:
            meta["duration"] = req.duration
        if req.ratio:
            meta["ratio"] = req.ratio
        body["metadata"] = meta

        base = self.cfg["base"].rstrip("/")
        try:
            status, text = self._post(base + "/v1/video/generations",
                                      self._headers(), body, _SUBMIT_TIMEOUT)
        except Exception as e:
            return GenResult(ok=False, error=f"提交失败: {type(e).__name__}: {e}")
        j = self._parse(status, text)
        # 兼容两种提交响应：OpenAI 风格（顶层 id/task_id）与网关信封（data.task_id）
        task_id = j.get("task_id") or j.get("id")
        if not task_id and isinstance(j.get("data"), dict):
            task_id = j["data"].get("task_id")
        if status != 200 or not task_id:
            msg = j.get("message") or j.get("_raw") or text[:200]
            return GenResult(ok=False, raw=text, error=f"提交失败 HTTP {status}: {msg}")

        # 轮询
        deadline = time.monotonic() + _POLL_TOTAL
        while time.monotonic() < deadline:
            try:
                s, t = self._get(f"{base}/v1/video/generations/{task_id}",
                                 self._headers(), 30)
            except Exception as e:
                return GenResult(ok=False, error=f"轮询失败: {type(e).__name__}: {e}")
            j = self._parse(s, t)
            data = j.get("data") or {}
            st = data.get("status", "")
            if st == "SUCCESS":
                inner = data.get("data") or {}
                content = inner.get("content") or {}
                url = content.get("video_url") or inner.get("video_url") or ""
                if url.startswith(("http://", "https://")):
                    return GenResult(ok=True, urls=[url], raw=t)
                return GenResult(ok=False, raw=t,
                                 error=f"任务成功但无视频 URL: {t[:300]}")
            if st in ("FAILURE", "UNKNOWN"):
                reason = data.get("fail_reason") or t[:300]
                return GenResult(ok=False, raw=t, error=f"任务失败: {reason}")
            time.sleep(self._poll_interval)
        return GenResult(ok=False, error=f"轮询超时（{_POLL_TOTAL}s），task_id={task_id}")

    def generate_image(self, req: ImageRequest) -> GenResult:
        return GenResult(ok=False, error="kkhub-video 协议只支持视频；图像请配置 openai-images 协议的 provider")
