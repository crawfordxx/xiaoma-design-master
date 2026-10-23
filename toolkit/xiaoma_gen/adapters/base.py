"""适配器基类：密钥解析 + 统一接口。

适配器只认 (name, cfg)，cfg 来自 providers.toml 的 provider 配置块。
生成请求里的 req.model 必须已由 executor 解析填好（tier→model）。
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path

from .. import transport as transport_mod
from ..models import GenResult, ImageRequest, LlmRequest, VideoRequest


class AdapterError(Exception):
    """适配器配置/调用前置错误（缺 key、模型未解析等）。"""


def resolve_key(cfg: dict) -> str:
    """按 env → key_file 优先级解析密钥；都没有则抛带指引的 AdapterError。"""
    key_env = cfg.get("key_env", "")
    key_file = cfg.get("key_file", "")
    if key_env and os.environ.get(key_env):
        return os.environ[key_env]
    if key_file:
        p = Path(key_file).expanduser()
        if p.is_file():
            return p.read_text(encoding="utf-8").strip()
    raise AdapterError(
        f"缺少 API key：请设置环境变量 {key_env or '(未配置 key_env)'}，"
        f"或把 key 存入 {key_file or '(未配置 key_file)'}（文件权限建议 600）"
    )


class Adapter(ABC):
    """生成能力适配器的统一接口。transport/getter 可注入用于测试。"""

    name: str

    def __init__(self, name: str, cfg: dict, transport=None, getter=None):
        self.name = name
        self.cfg = cfg
        self._post = transport or transport_mod.http_post
        self._get = getter or transport_mod.http_get

    @abstractmethod
    def generate_image(self, req: ImageRequest) -> GenResult: ...

    @abstractmethod
    def generate_video(self, req: VideoRequest) -> GenResult: ...

    def generate_llm(self, req: LlmRequest) -> GenResult:
        raise AdapterError(f"{self.name} 不支持 llm 能力")

    def list_models(self, cap: str) -> list[dict]:
        """尽力而为的模型发现；失败返回空列表。"""
        return []

    def get_balance(self) -> dict | None:
        """余额查询；协议不支持则返回 None。"""
        return None
