"""OpenAI 兼容聊天协议适配器（openai-chat）。

适用于任何「POST /v1/chat/completions，媒体 URL 在回复文本里」的端点：
多数中转站、聊天协议生图/生视频网关。prompt 进 messages，结果用正则提取 URL。
"""
from __future__ import annotations

import base64
import json
import mimetypes
import re

from ..models import GenResult, ImageRequest, LlmRequest, VideoRequest
from .base import Adapter, AdapterError, resolve_key

URL_RE = re.compile(r"https?://[^\s)\]】>]+")
_TIMEOUT = 600  # 生成耗时几分钟属正常


def _augment_prompt(prompt: str, ratio: str | None, duration: int | None) -> str:
    parts = [prompt]
    if ratio:
        parts.append(f"Aspect ratio: {ratio}.")
    if duration:
        parts.append(f"Duration: about {duration} seconds.")
    return "\n".join(parts)


def _ref_to_part(ref: str) -> dict:
    """本地文件 → base64 data URL；http(s) URL 原样。"""
    if ref.startswith(("http://", "https://", "data:")):
        return {"type": "image_url", "image_url": {"url": ref}}
    with open(ref, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    mime = mimetypes.guess_type(ref)[0] or "image/jpeg"
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}}


class OpenaiChatAdapter(Adapter):
    def __init__(self, name: str, cfg: dict, transport=None, getter=None):
        super().__init__(name, cfg, transport=transport, getter=getter)
        self._api_key = resolve_key(cfg)  # 构造时解析，缺 key 立即报错

    def _call(self, model: str, prompt: str, refs: list[str]) -> GenResult:
        if not model:
            raise AdapterError("req.model 未解析：executor 应先通过注册表 resolve 后再调用")
        headers = {"Authorization": f"Bearer {self._api_key}"}
        if refs:
            content: list | str = [
                {"type": "text", "text": prompt},
                *[_ref_to_part(r) for r in refs],
            ]
        else:
            content = prompt
        body = {"model": model, "messages": [{"role": "user", "content": content}]}
        url = self.cfg["base"].rstrip("/") + "/v1/chat/completions"
        try:
            status, text = self._post(url, headers, body, _TIMEOUT)
        except Exception as e:  # 网络层异常不向上炸
            return GenResult(ok=False, error=f"{type(e).__name__}: {e}")
        if status != 200:
            return GenResult(ok=False, raw=text, error=self._http_error(status, text))
        return self._extract(text)

    @staticmethod
    def _http_error(status: int, text: str) -> str:
        try:
            j = json.loads(text)
            msg = j.get("error") or j.get("message") or text
            if isinstance(msg, dict):
                msg = msg.get("message", str(msg))
        except Exception:
            msg = text
        return f"HTTP {status}: {msg}"

    @staticmethod
    def _extract(text: str) -> GenResult:
        """从 chat 回复里提取媒体 URL。"""
        try:
            content = json.loads(text)["choices"][0]["message"]["content"]
        except Exception:
            return GenResult(ok=False, raw=text, error=f"响应不是 chat 结构: {text[:300]}")
        urls = URL_RE.findall(content or "")
        if not urls:
            return GenResult(ok=False, raw=content or text,
                             error=f"回复中没有媒体 URL: {(content or text)[:300]}")
        return GenResult(ok=True, urls=urls, raw=content)

    # ---- Adapter 接口 ----------------------------------------------------
    def generate_image(self, req: ImageRequest) -> GenResult:
        prompt = _augment_prompt(req.prompt, req.ratio, None)
        return self._call(req.model, prompt, req.refs)

    def generate_video(self, req: VideoRequest) -> GenResult:
        prompt = _augment_prompt(req.prompt, req.ratio, req.duration)
        return self._call(req.model, prompt, req.refs)

    def generate_llm(self, req: LlmRequest) -> GenResult:
        headers = {"Authorization": f"Bearer {self._api_key}"}
        messages = []
        if req.system:
            messages.append({"role": "system", "content": req.system})
        messages.append({"role": "user", "content": req.prompt})
        body = {"model": req.model, "messages": messages}
        if req.json_mode:
            body["response_format"] = {"type": "json_object"}
        url = self.cfg["base"].rstrip("/") + "/v1/chat/completions"
        try:
            status, text = self._post(url, headers, body, 300)
        except Exception as e:
            return GenResult(ok=False, error=f"{type(e).__name__}: {e}")
        if status != 200:
            return GenResult(ok=False, raw=text, error=self._http_error(status, text))
        try:
            content = json.loads(text)["choices"][0]["message"]["content"]
        except Exception:
            return GenResult(ok=False, raw=text, error=f"响应不是 chat 结构: {text[:300]}")
        return GenResult(ok=True, raw=content)

    def list_models(self, cap: str) -> list[dict]:
        if cap != "llm":
            return []  # 聊天协议的 /v1/models 只有 LLM 子集，图/视频模型靠注册表
        try:
            headers = {"Authorization": f"Bearer {self._api_key}"}
            status, text = self._get(self.cfg["base"].rstrip("/") + "/v1/models", headers, 30)
            if status != 200:
                return []
            return [{"id": m.get("id", ""), "cap": "llm"} for m in json.loads(text).get("data", [])]
        except Exception:
            return []
