#!/usr/bin/env bash
# xiaoma-design-master 冒烟检查（无 key 即可全绿；有 key 追加余额检查）。
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

echo "== 1/4 单元测试 =="
python3 -m unittest discover -s toolkit/tests -v 2>&1 | tail -3
python3 -m unittest discover -s tools/tests 2>&1 | tail -1

echo "== 2/4 技能 smoke =="
# 新生成类技能走 strict-gen（禁模型名/禁直连）；旧技能 basic。
NEW_GEN_SKILLS="xiaoma-write-article xiaoma-write-xhs xiaoma-de-ai xiaoma-gen-image xiaoma-gen-infographic xiaoma-gen-cover xiaoma-gen-video xiaoma-video-script xiaoma-gen-ui"
fail=0
for d in skills/*/; do
  name="$(basename "$d")"
  if echo "$NEW_GEN_SKILLS" | grep -qw "$name"; then
    python3 tools/smoke_skill.py "$d" --strict-gen || fail=1
  else
    python3 tools/smoke_skill.py "$d" || fail=1
  fi
done
[ "$fail" -eq 0 ] || { echo "smoke 失败"; exit 1; }

echo "== 3/4 生成 dry-run（用 example 配置，不需要 key） =="
python3 toolkit/gen.py image --prompt "冒烟" --dry-run --config toolkit/providers.example.toml
python3 toolkit/gen.py video --prompt "冒烟" --dry-run --config toolkit/providers.example.toml

echo "== 4/4 公开内容清洁检查 =="
if grep -rniE 'youmind|逆向|reverse[ -]engineer|#reversed|luminaapis|kkhub|kkidc' \
    --include='*.md' --include='*.py' --include='*.toml' --include='*.sh' \
    README.md CONTRIBUTING.md AGENT-INSTALL.md skills/ shared/ toolkit/ showcase/ 2>/dev/null \
    | grep -v 'toolkit/providers.toml' \
    | grep -v 'providers.example.toml' | grep -v 'verify.sh'; then
  echo "清洁检查失败：公开内容包含敏感词" >&2
  exit 1
fi

# 有 key 时追加余额检查（不产生成）
if [ -n "${XIAOMA_PROVIDERS:-}" ] || [ -f toolkit/providers.toml ]; then
  echo "== 附加: 余额查询（有配置才跑） =="
  python3 toolkit/gen.py balance || true
fi

echo "verify: ALL OK"
