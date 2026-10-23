# Agent 安装说明（给 AI Agent 看的，人类用户请看 README 的一句话提示词）

收到「安装这个仓库的技能」类请求时，按以下步骤执行：

## 安装

```bash
git clone https://github.com/crawfordxx/xiaoma-design-master.git /tmp/xiaoma-design-master 2>/dev/null || true
# 若已克隆过则先 git pull
cd /tmp/xiaoma-design-master && git pull --ff-only 2>/dev/null
./install.sh
```

`install.sh` 会把 `skills/` 下每个技能 symlink 到已检测到的 Agent 技能目录
（pi: `~/.pi/agent/skills/`，Claude Code: `~/.claude/skills/`）。
可选参数：`--target pi|claude|all`、`--skills 名字,名字`、`--uninstall`。

## 安装后验证

```bash
for s in /tmp/xiaoma-design-master/skills/*/; do
  python3 /tmp/xiaoma-design-master/tools/smoke_skill.py "$s"
done
```

全部 `OK` 即安装成功。向用户报告：装了哪些技能、各自一句话能力（见 README 技能矩阵）。

## 注意

- 生成类技能（xiaoma-gen-*）需要用户先配置自己的模型 API：
  复制 `toolkit/providers.example.toml` → `toolkit/providers.toml` 并填入密钥。
  未配置时这些技能会明确提示，不影响其他技能使用。
- 安装位置是 symlink：仓库更新（git pull）后技能自动更新，无需重装。
