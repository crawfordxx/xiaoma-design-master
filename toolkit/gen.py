#!/usr/bin/env python3
"""xiaoma-gen — 生成能力统一入口（技能只允许通过这里调用模型 API）。

用法:
    gen image --prompt "..." [--ref 图] [--ratio 3:4] [--tier draft|final] [--model M] [--out 路径] [--dry-run]
    gen video --prompt "..." [--ref 图] [--duration 10] [--ratio 9:16] [--tier] [--model] [--out] [--dry-run]
    gen llm   --prompt "..." [--system "..."] [--model M] [--json]
    gen models [--cap image|video|llm]
    gen balance

配置: --config 路径 > $XIAOMA_PROVIDERS > <toolkit>/providers.toml（用户自己的配置，
复制 providers.example.toml 而来）。--dry-run 不需要任何 key。
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

TOOLKIT = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLKIT))

from xiaoma_gen.adapters.base import AdapterError  # noqa: E402
from xiaoma_gen.adapters.openai_chat import OpenaiChatAdapter  # noqa: E402
from xiaoma_gen.adapters.openai_images import OpenaiImagesAdapter  # noqa: E402
from xiaoma_gen.executor import run_generation  # noqa: E402
from xiaoma_gen.models import ImageRequest, LlmRequest, VideoRequest  # noqa: E402
from xiaoma_gen.registry import ConfigError, load_registry  # noqa: E402

ADAPTERS = {"openai-chat": OpenaiChatAdapter, "openai-images": OpenaiImagesAdapter}  # protocol -> class


def default_config_path() -> Path:
    if os.environ.get("XIAOMA_PROVIDERS"):
        return Path(os.environ["XIAOMA_PROVIDERS"]).expanduser()
    return TOOLKIT / "providers.toml"


def load_or_die(path: Path):
    if not Path(path).is_file():
        print(
            f"未找到 Provider 配置: {path}\n"
            f"请复制模板并填入你自己的 API:\n"
            f"  cp {TOOLKIT / 'providers.example.toml'} {path}",
            file=sys.stderr,
        )
        sys.exit(2)
    try:
        return load_registry(Path(path))
    except ConfigError as e:
        print(f"配置错误: {e}", file=sys.stderr)
        sys.exit(2)


def build_adapter(registry, provider: str, fatal: bool = True):
    cfg = registry.provider_cfg(provider)
    cls = ADAPTERS.get(cfg.get("protocol", ""))
    if cls is None:
        msg = f"不支持的协议: {cfg.get('protocol')}（provider={provider}）"
        if fatal:
            print(msg, file=sys.stderr)
            sys.exit(2)
        print(f"WARN: {msg}，跳过故障转移候选", file=sys.stderr)
        return None
    try:
        return cls(provider, cfg)
    except AdapterError as e:
        if fatal:
            print(str(e), file=sys.stderr)
            sys.exit(2)
        print(f"WARN: {provider} 不可用（{e}），跳过故障转移候选", file=sys.stderr)
        return None


def build_adapters_for_cap(registry, cap: str, first_provider: str) -> dict:
    """首选 provider 缺配置直接报错；其余候选缺配置只警告跳过。"""
    adapters = {}
    a = build_adapter(registry, first_provider, fatal=True)
    if a:
        adapters[first_provider] = a
    for pname in registry.providers_of(cap):
        if pname in adapters:
            continue
        a = build_adapter(registry, pname, fatal=False)
        if a:
            adapters[pname] = a
    return adapters


def dry_run_line(cap: str, req) -> str:
    parts = [f"DRY-RUN cap={cap}", f"tier={req.tier}"]
    if req.model:
        parts.append(f"model={req.model}")
    if getattr(req, "ratio", None):
        parts.append(f"ratio={req.ratio}")
    if getattr(req, "duration", None):
        parts.append(f"duration={req.duration}")
    parts.append(f"refs={len(req.refs)}")
    parts.append(f"prompt={req.prompt[:80]}")
    return " ".join(parts)


def cmd_image(args) -> int:
    reg = load_or_die(args.config)
    req = ImageRequest(prompt=args.prompt, refs=args.ref or [], ratio=args.ratio,
                       tier=args.tier, model=args.model, out=args.out,
                       dry_run=args.dry_run)
    res = reg.resolve("image", req.tier if not req.model else None, req.model)
    req.model = res.model
    if req.dry_run:
        print(dry_run_line("image", req) + f" provider={res.provider}")
        return 0
    adapters = build_adapters_for_cap(reg, "image", res.provider)
    r = run_generation(req, reg, adapters)
    print_result(r)
    return 0 if r.ok else 1


def cmd_video(args) -> int:
    reg = load_or_die(args.config)
    req = VideoRequest(prompt=args.prompt, refs=args.ref or [], duration=args.duration,
                       ratio=args.ratio, tier=args.tier, model=args.model,
                       out=args.out, dry_run=args.dry_run)
    res = reg.resolve("video", req.tier if not req.model else None, req.model)
    req.model = res.model
    if req.dry_run:
        print(dry_run_line("video", req) + f" provider={res.provider}")
        return 0
    adapters = build_adapters_for_cap(reg, "video", res.provider)
    r = run_generation(req, reg, adapters)
    print_result(r)
    return 0 if r.ok else 1


def cmd_llm(args) -> int:
    reg = load_or_die(args.config)
    req = LlmRequest(prompt=args.prompt, system=args.system,
                     model=args.model, json_mode=args.json)
    if not req.model:
        res = reg.resolve("llm", "final", None)
        req.model = res.model
    else:
        res = reg.resolve("llm", None, req.model)
    adapter = build_adapter(reg, res.provider)
    r = adapter.generate_llm(req)
    if r.ok:
        print(r.raw)
    else:
        print(f"ERROR: {r.error}", file=sys.stderr)
    return 0 if r.ok else 1


def cmd_models(args) -> int:
    reg = load_or_die(args.config)
    cap = args.cap
    printed = 0
    for pname in reg.providers_of(cap):
        adapter = build_adapter(reg, pname)
        for m in adapter.list_models(cap):
            print(f"{pname}\t{m.get('id', '')}")
            printed += 1
    if not printed:
        print(f"（{cap} 能力下没有可动态发现的模型；请直接编辑 providers.toml 注册）")
    return 0


def cmd_balance(args) -> int:
    reg = load_or_die(args.config)
    found = False
    for pname in reg.providers_of("image") + reg.providers_of("video"):
        try:
            adapter = build_adapter(reg, pname)
        except SystemExit:
            continue
        b = adapter.get_balance()
        if b is not None:
            print(f"{pname}: {b}")
            found = True
    if not found:
        print("当前协议没有 provider 支持余额查询（openai-chat 协议无标准余额接口）")
    return 0


def print_result(r) -> None:
    if r.ok:
        for p in (r.local_paths or r.urls):
            print(p)
    else:
        print(f"ERROR: {r.error}", file=sys.stderr)
        for u in r.urls:
            print(u, file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gen", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default=None, help="providers.toml 路径")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", default=argparse.SUPPRESS,
                        help="providers.toml 路径")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_gen(sp):
        sp.add_argument("--prompt", required=True)
        sp.add_argument("--ref", action="append", help="参考图（可多次）")
        sp.add_argument("--ratio")
        sp.add_argument("--tier", choices=["draft", "final"], default="draft")
        sp.add_argument("--model")
        sp.add_argument("--out")
        sp.add_argument("--dry-run", action="store_true")

    add_gen(sub.add_parser("image", parents=[common], help="生成图片"))
    v = sub.add_parser("video", parents=[common], help="生成视频")
    add_gen(v)
    v.add_argument("--duration", type=int)

    l = sub.add_parser("llm", parents=[common], help="批量文本任务")
    l.add_argument("--prompt", required=True)
    l.add_argument("--system")
    l.add_argument("--model")
    l.add_argument("--json", action="store_true")

    m = sub.add_parser("models", parents=[common], help="列出可动态发现的模型")
    m.add_argument("--cap", choices=["image", "video", "llm"], default="llm")

    sub.add_parser("balance", parents=[common], help="查询余额（协议支持时）")
    return p


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv[1:])
    if args.config is None:
        args.config = default_config_path()
    try:
        return {
            "image": cmd_image, "video": cmd_video, "llm": cmd_llm,
            "models": cmd_models, "balance": cmd_balance,
        }[args.cmd](args)
    except ConfigError as e:
        print(f"配置错误: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
