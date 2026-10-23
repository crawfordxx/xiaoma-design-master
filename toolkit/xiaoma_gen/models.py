"""请求与结果的统一数据模型。生成类技能只依赖这些结构，不感知具体 Provider。"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ImageRequest:
    prompt: str
    refs: list[str] = field(default_factory=list)   # 参考图路径/URL
    ratio: str | None = None                        # 如 "3:4" / "16:9"
    tier: str = "draft"                             # draft | final
    model: str | None = None                        # 显式指定模型名（覆盖 tier 默认）
    out: str | None = None                          # 产出另存路径（默认 workspace/output/）
    dry_run: bool = False


@dataclass
class VideoRequest:
    prompt: str
    refs: list[str] = field(default_factory=list)
    duration: int | None = None                     # 秒
    ratio: str | None = None
    tier: str = "draft"
    model: str | None = None
    out: str | None = None
    dry_run: bool = False


@dataclass
class LlmRequest:
    prompt: str
    system: str | None = None
    model: str | None = None
    json_mode: bool = False


@dataclass
class GenResult:
    ok: bool
    urls: list[str] = field(default_factory=list)   # provider 返回的媒体 URL
    local_paths: list[str] = field(default_factory=list)  # 下载后的本地路径
    raw: str = ""                                    # 原始响应文本（审计/排错）
    error: str | None = None
