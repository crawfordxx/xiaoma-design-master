"""标准 OpenAI 图像接口适配器（openai-images）。

POST <base>/images/generations，标准请求/响应结构。
支持 url 与 b64_json 两种返回（b64 转为 data URL 统一交付）。
"""
from __future__ import annotations

import json

from ..models import GenResult, ImageRequest, VideoRequest
from .base import Adapter, resolve_key

_TIMEOUT = 300

# 比例 → OpenAI size（就近映射；未匹配则不传 size 由模型自定）
RATIO_TO_SIZE = {
    "1:1": "1024x1024",
    "3:4": "1024x1536",
    "4:3": "1536x1024",
    "9:16": "1024x1536",
    "16:9": "1536x1024",
    "3:2": "1536x1024",
    "2:3": "1024x1536",
}


class OpenaiImagesAdapter(Adapter):
    def __init__(self, name: str, cfg: dict, transport=None, getter=None):
        super().__init__(name, cfg, transport=transport, getter=getter)
        self._api_key = resolve_key(cfg)

    def generate_image(self, req: ImageRequest) -> GenResult:
        if req.refs:
            return GenResult(ok=False, error="openai-images 协议暂不支持参考图；请配置 openai-chat 协议的 provider")
        body: dict = {"model": req.model, "prompt": req.prompt, "n": 1}
        if req.ratio and req.ratio in RATIO_TO_SIZE:
            body["size"] = RATIO_TO_SIZE[req.ratio]
        url = self.cfg["base"].rstrip("/") + "/images/generations"
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            status, text = self._post(url, headers, body, _TIMEOUT)
        except Exception as e:
            return GenResult(ok=False, error=f"{type(e).__name__}: {e}")
        if status != 200:
            return GenResult(ok=False, raw=text, error=self._err(status, text))
        try:
            data = json.loads(text).get("data", [])
        except Exception:
            return GenResult(ok=False, raw=text, error=f"响应不是 images 结构: {text[:300]}")
        urls = []
        for item in data:
            if item.get("url"):
                urls.append(item["url"])
            elif item.get("b64_json"):
                urls.append(f"data:image/png;base64,{item['b64_json']}")
        if not urls:
            return GenResult(ok=False, raw=text, error=f"响应中没有图片: {text[:300]}")
        return GenResult(ok=True, urls=urls, raw=text)

    def generate_video(self, req: VideoRequest) -> GenResult:
        return GenResult(ok=False, error="openai-images 协议不支持视频生成")

    @staticmethod
    def _err(status: int, text: str) -> str:
        try:
            msg = json.loads(text).get("error", {})
            if isinstance(msg, dict):
                msg = msg.get("message", str(msg))
        except Exception:
            msg = text
        return f"HTTP {status}: {msg}"
