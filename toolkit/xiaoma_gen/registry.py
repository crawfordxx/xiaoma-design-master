"""providers.toml 注册表：唯一允许出现具体模型名的地方。

结构:
    [providers.<name>]        enable/key_env/key_file/base/protocol
    [providers.<name>.caps.<cap>.models."<model>"]   tier/ref 等模型属性
    [defaults.<cap>]          draft = "provider:model" / final = "provider:model"
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


class ConfigError(Exception):
    """注册表配置错误（文件缺失/语法错/字段缺失/模型不存在）。"""


@dataclass
class Resolution:
    provider: str
    model: str
    cfg: dict  # 该 provider 的完整配置块（base/protocol/key_env/...）


class Registry:
    def __init__(self, data: dict, path: Path):
        self._data = data
        self._path = path

    # ---- 内部工具 -------------------------------------------------------
    def _providers(self) -> dict:
        return self._data.get("providers") or {}

    def _fail(self, msg: str) -> "ConfigError":
        return ConfigError(f"[{self._path}] {msg}")

    def _find_model(self, model: str) -> tuple[str, dict] | None:
        """在所有 provider 的所有 cap 里找模型，返回 (provider_name, provider_cfg)。"""
        for pname, pcfg in self._providers().items():
            if not pcfg.get("enable", True):
                continue
            caps = pcfg.get("caps") or {}
            for cap in caps.values():
                models = (cap or {}).get("models") or {}
                if model in models:
                    return pname, pcfg
        return None

    # ---- 对外接口 -------------------------------------------------------
    def resolve(self, cap: str, tier: str | None, model: str | None) -> Resolution:
        """按 (能力, 档位) 或显式模型名解析出 provider+model。"""
        providers = self._providers()
        if model:
            found = self._find_model(model)
            if not found:
                raise self._fail(f"模型未注册: {model}")
            pname, pcfg = found
            return Resolution(provider=pname, model=model, cfg=pcfg)

        if not tier:
            raise self._fail(f"必须提供 tier 或 model 之一 (cap={cap})")
        defaults = (self._data.get("defaults") or {}).get(cap)
        if not defaults or tier not in defaults or not defaults[tier]:
            raise self._fail(f"defaults.{cap}.{tier} 未配置")
        ref = defaults[tier]  # "provider:model"
        if ":" not in ref:
            raise self._fail(f"defaults.{cap}.{tier} 格式应为 provider:model，实际: {ref}")
        pname, mname = ref.split(":", 1)
        if pname not in providers:
            raise self._fail(f"defaults.{cap}.{tier} 引用了未定义的 provider: {pname}")
        pcfg = providers[pname]
        # 校验模型确实注册在该 provider 的该 cap 下
        cap_cfg = (pcfg.get("caps") or {}).get(cap) or {}
        if mname not in ((cap_cfg.get("models")) or {}):
            raise self._fail(
                f"defaults.{cap}.{tier} 引用的模型 {mname} 未注册在 {pname}.{cap}.models"
            )
        return Resolution(provider=pname, model=mname, cfg=pcfg)

    def providers_of(self, cap: str) -> list[str]:
        """返回支持某能力且启用的 provider 名列表（故障转移顺序 = toml 声明顺序）。"""
        out = []
        for pname, pcfg in self._providers().items():
            if not pcfg.get("enable", True):
                continue
            if cap in (pcfg.get("caps") or {}):
                out.append(pname)
        return out

    def provider_cfg(self, name: str) -> dict:
        pcfg = self._providers().get(name)
        if pcfg is None:
            raise self._fail(f"未定义的 provider: {name}")
        return pcfg


def load_registry(path: Path) -> Registry:
    path = Path(path)
    if not path.is_file():
        raise ConfigError(f"注册表文件不存在: {path}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"[{path}] TOML 语法错误: {e}") from e
    return Registry(data, path)
