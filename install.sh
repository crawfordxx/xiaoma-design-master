#!/usr/bin/env bash
# xiaoma-design-master 技能安装器
#
# 用法:
#   ./install.sh                          # 检测 pi 与 Claude Code，全部技能 symlink
#   ./install.sh --target pi              # 仅 pi（~/.pi/agent/skills/）
#   ./install.sh --target claude          # 仅 Claude Code（~/.claude/skills/）
#   ./install.sh --target all             # 全部目标
#   ./install.sh --skills a,b             # 只装指定技能
#   ./install.sh --uninstall              # 移除本仓库建立的 symlink
#
# 原则: symlink 而非复制（仓库 git pull 即全部技能更新）; 幂等; 绝不覆盖用户已有文件。
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$REPO/skills"

TARGET="auto"
UNINSTALL=0
ONLY=""

usage() { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --skills) ONLY="$2"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数: $1" >&2; usage >&2; exit 2 ;;
  esac
done

# 目标目录定义: 名称 -> 目录
target_dirs() {
  case "$1" in
    pi)     echo "$HOME/.pi/agent/skills" ;;
    claude) echo "$HOME/.claude/skills" ;;
    all)    echo "$HOME/.pi/agent/skills" "$HOME/.claude/skills" ;;
    *)      ;; # auto 在下面处理
  esac
}

resolve_targets() {
  if [ "$TARGET" = "auto" ]; then
    [ -d "$HOME/.pi/agent/skills" ] && echo "pi"
    [ -d "$HOME/.claude/skills" ] && echo "claude"
  else
    echo "$TARGET"
  fi
}

all_skills() {
  find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort
}

wanted_skills() {
  if [ -n "$ONLY" ]; then
    echo "$ONLY" | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep -v '^$'
  else
    all_skills
  fi
}

do_uninstall() {
  local removed=0
  for tname in $(resolve_targets); do
    local tdir
    tdir="$(target_dirs "$tname")"
    [ -d "$tdir" ] || continue
    for link in "$tdir"/*; do
      [ -e "$link" ] || [ -L "$link" ] || continue
      if [ -L "$link" ]; then
        local dest
        dest="$(readlink "$link" 2>/dev/null || true)"
        case "$dest" in
          "$SKILLS_DIR"/*) rm "$link"; removed=$((removed+1)); echo "removed: $link" ;;
        esac
      fi
    done
  done
  echo "卸载完成，移除 $removed 个链接。"
}

do_install() {
  local targets
  targets="$(resolve_targets)"
  if [ -z "$targets" ]; then
    echo "未检测到已安装的 Agent 技能目录（pi / Claude Code）。" >&2
    echo "可手动指定: ./install.sh --target pi 或 --target claude" >&2
    exit 1
  fi

  local count=0
  for skill in $(wanted_skills); do
    local src="$SKILLS_DIR/$skill"
    if [ ! -d "$src" ]; then
      echo "ERROR: 技能不存在: $skill" >&2
      exit 1
    fi
    for tname in $targets; do
      local tdir
      tdir="$(target_dirs "$tname")"
      [ -d "$tdir" ] || continue
      local dest="$tdir/$skill"
      if [ -L "$dest" ]; then
        rm "$dest"                       # 本仓库旧链接 → 重建（幂等）
      elif [ -e "$dest" ]; then
        echo "SKIP: $dest 已存在且不是本仓库的链接，未覆盖" >&2
        continue
      fi
      ln -s "$src" "$dest"
      count=$((count+1))
    done
  done
  echo "已安装 $count 个技能链接到: $targets"
  echo "冒烟检查: for s in $SKILLS_DIR/*/; do python3 $REPO/tools/smoke_skill.py \"\$s\"; done"
}

if [ "$UNINSTALL" -eq 1 ]; then
  do_uninstall
else
  do_install
fi
