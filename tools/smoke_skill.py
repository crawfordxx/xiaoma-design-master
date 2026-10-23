#!/usr/bin/env python3
"""技能目录冒烟检查。

用法:
    python3 tools/smoke_skill.py <skill_dir> [--strict-gen]

basic 级（所有技能）:
    - SKILL.md 必须存在（ERROR）
    - frontmatter name 必须等于目录名（ERROR）
    - 相对 markdown 链接目标必须存在（ERROR）
    - version/description/triggers 缺失 → WARN（不失败）

--strict-gen 级（新生成类技能，额外）:
    - frontmatter 必须含 name/version/description/triggers（ERROR）
    - 禁止具体模型名 / provider 域名 / curl 直连（ERROR）

退出码: 0 通过 / 1 有 ERROR / 2 用法错误
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# 禁词表：模型名 / Provider 域名 / 直连调用（大小写不敏感）
STRICT_BANNED = [
    "seed-2", "seedance", "tt-image", "gpt-image", "nano-banana",
    "veo", "kling", "midjourney",
    "agentwan", "wdsheng", "lumina", "lk888", "lk666", "ai6800", "lingkeai",
    "curl -",
]

REQUIRED_KEYS = ["name", "version", "description", "triggers"]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def parse_frontmatter(text: str) -> dict[str, str]:
    """解析 `---` 包裹的 frontmatter（简单 key: value 行）。"""
    if not text.startswith("---"):
        return {}
    lines = text.split("\n")
    fm: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def check_links(skill_dir: Path, text: str) -> list[str]:
    """校验相对链接目标存在；返回错误列表。"""
    errors = []
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "#", "mailto:", "data:")):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        resolved = (skill_dir / path_part).resolve()
        if not resolved.exists():
            errors.append(f"链接目标不存在: {target} -> {resolved}")
    return errors


def check_banned(text: str) -> list[str]:
    """strict-gen 禁词检查；返回错误列表（含命中的词）。"""
    lower = text.lower()
    return [f"禁止出现: {word}" for word in STRICT_BANNED if word in lower]


def smoke(skill_dir: Path, strict_gen: bool) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not skill_dir.is_dir():
        print(f"ERROR: 目录不存在: {skill_dir}")
        return 1
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        print(f"ERROR: 缺少 SKILL.md: {skill_md}")
        return 1

    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)

    # name == 目录名（两级一致：frontmatter 与目录必须同名）
    fm_name = fm.get("name", "")
    if not fm_name:
        warnings.append("frontmatter 缺少 name")
    elif fm_name != skill_dir.name:
        errors.append(f"name 不匹配: frontmatter={fm_name} 目录={skill_dir.name}")

    # 其余必填字段：basic 只警告，strict 报错
    for key in REQUIRED_KEYS:
        if key == "name":
            continue
        if not fm.get(key):
            msg = f"frontmatter 缺少 {key}"
            (errors if strict_gen else warnings).append(msg)

    # 链接完整性（两级都硬失败）
    errors.extend(check_links(skill_dir, text))

    # strict-gen 禁词
    if strict_gen:
        errors.extend(check_banned(text))

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"FAIL: {skill_dir.name} ({len(errors)} errors)")
        return 1
    print(f"OK: {skill_dir.name}" + (" [strict-gen]" if strict_gen else ""))
    return 0


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if a != "--strict-gen"]
    strict_gen = "--strict-gen" in argv[1:]
    if len(args) != 1:
        print(__doc__)
        return 2
    return smoke(Path(args[0]).resolve(), strict_gen)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
