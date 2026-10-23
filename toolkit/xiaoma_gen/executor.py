"""生成执行器：tier 解析 → 余额前置 → 生成（含故障转移）→ 下载 → meta/history 落盘。

成本安全铁律:
    - final 档先查余额（provider 支持时），余额 0/负 → 拒绝生成
    - 下载失败只重试下载，绝不重新生成
    - 每个 provider 只调用一次，超时不重试（防重复扣费）
"""
from __future__ import annotations

import base64
import datetime
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

from .adapters.base import Adapter
from .models import GenResult, ImageRequest, LlmRequest, VideoRequest
from .registry import Registry, ConfigError

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DATA_URL_RE = re.compile(r"^data:image/([\w+.-]+);base64,(.*)$", re.DOTALL)


def default_downloader(url: str) -> bytes:
    m = _DATA_URL_RE.match(url)
    if m:
        return base64.b64decode(m.group(2))
    req = urllib.request.Request(url, headers={"User-Agent": "xiaoma-gen/0.1"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return resp.read()


def _ext_for(url: str, data: bytes) -> str:
    m = _DATA_URL_RE.match(url)
    if m:
        return "png" if m.group(1) == "jpeg" else m.group(1).split("+")[0]
    from urllib.parse import urlparse
    path = urlparse(url).path
    suffix = Path(path).suffix.lstrip(".")
    if suffix.isalnum() and len(suffix) <= 5:
        return suffix.lower()
    if data[:3] == b"\xff\xd8\xff":
        return "jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    return "bin"


def _warn(msg: str) -> None:
    print(f"WARN: {msg}", file=sys.stderr)


def _save_all(req, res: GenResult, provider: str, model: str, cap: str,
              repo_root: Path, downloader) -> GenResult:
    """下载所有 URL → output/ + meta.json + history.jsonl。下载失败不重新生成。"""
    out_dir = repo_root / "workspace" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    local_paths: list[str] = []
    downloaded_ok = True
    error = res.error
    for url in res.urls:
        digest = hashlib.sha1(url.encode()).hexdigest()[:16]
        try:
            data = downloader(url)
        except Exception as e:
            downloaded_ok = False
            error = f"下载失败: {e}（生成已成功，原始 URL: {url}）"
            _warn(error)
            continue
        ext = _ext_for(url, data)
        media = out_dir / f"{digest}.{ext}"
        media.write_bytes(data)
        local_paths.append(str(media))
        if req.out:
            out_path = Path(req.out).expanduser()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(data)
            local_paths.append(str(out_path))

    meta = {
        "cap": cap,
        "prompt": req.prompt,
        "provider": provider,
        "model": model,
        "tier": req.tier,
        "params": {"ratio": getattr(req, "ratio", None),
                   "duration": getattr(req, "duration", None),
                   "refs": list(req.refs)},
        "urls": res.urls,
        "local_paths": local_paths,
        "downloaded_ok": downloaded_ok,
        "error": error,
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    digest = hashlib.sha1((res.urls[0] if res.urls else req.prompt).encode()).hexdigest()[:16]
    (out_dir / f"{digest}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

    hist = {
        "ts": meta["created_at"], "cap": cap, "provider": provider,
        "model": model, "tier": req.tier, "ok": bool(res.ok and downloaded_ok),
        "urls": len(res.urls), "local": local_paths, "error": error,
    }
    with (repo_root / "workspace" / "history.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(hist, ensure_ascii=False) + "\n")

    if not downloaded_ok:
        return GenResult(ok=False, urls=res.urls, local_paths=local_paths,
                         raw=res.raw, error=error)
    return GenResult(ok=True, urls=res.urls, local_paths=local_paths,
                     raw=res.raw, error=None)


def _models_for_provider(registry: Registry, cap: str, tier: str, provider: str) -> str:
    """在该 provider 的 cap 里找匹配 tier 的第一个模型。"""
    cfg = registry.provider_cfg(provider)
    models = ((cfg.get("caps") or {}).get(cap) or {}).get("models") or {}
    for mname, mcfg in models.items():
        if mcfg.get("tier") == tier:
            return mname
    raise ConfigError(f"provider {provider} 的 {cap} 能力下没有 tier={tier} 的模型")


def run_generation(req, registry: Registry, adapters: dict[str, Adapter],
                   repo_root: Path | None = None, downloader=None) -> GenResult:
    """统一生成入口。req.model 会被按 provider 逐一解析覆盖。"""
    repo_root = Path(repo_root) if repo_root else _REPO_ROOT
    downloader = downloader or default_downloader
    cap = "image" if isinstance(req, ImageRequest) else "video"
    generate = "generate_image" if cap == "image" else "generate_video"

    # 解析首选 + 故障转移顺序
    first = registry.resolve(cap, req.tier if not req.model else None, req.model)
    order = [first.provider] + [p for p in registry.providers_of(cap)
                                if p not in (first.provider,)]
    tried: list[str] = []
    last_error = "没有可用的 provider"

    for pname in order:
        adapter = adapters.get(pname)
        if adapter is None:
            continue
        model = req.model if (req.model and pname == first.provider and
                              req.model == first.model) else _models_for_provider(
            registry, cap, req.tier, pname)
        tried.append(pname)

        # final 档余额前置（协议不支持则警告继续）
        if req.tier == "final":
            try:
                b = adapter.get_balance()
            except Exception as e:
                b = None
                _warn(f"{pname} 余额查询异常: {e}")
            if isinstance(b, dict):
                balance = b.get("balance")
                if isinstance(balance, (int, float)) and balance <= 0:
                    return GenResult(
                        ok=False, error=f"{pname} 余额不足（{balance}），已拒绝生成；请充值后重试")

        req.model = model
        try:
            res: GenResult = getattr(adapter, generate)(req)
        except Exception as e:
            res = GenResult(ok=False, error=f"{type(e).__name__}: {e}")
        if res.ok and res.urls:
            return _save_all(req, res, pname, model, cap, repo_root, downloader)
        if res.ok and not res.urls:
            res = GenResult(ok=False, raw=res.raw, error="生成成功但无媒体 URL")
        last_error = f"{pname}: {res.error}"

    return GenResult(ok=False, error=f"所有 provider 均失败（尝试: {', '.join(tried)}）。最后错误: {last_error}")
