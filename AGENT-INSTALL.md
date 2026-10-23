# Agent 安装说明（给 AI Agent 看的，人类用户请看 README 的一句话提示词）

收到「安装这个仓库的技能」类请求时，按以下步骤执行：

## 安装

```bash
D="$HOME/.xiaoma-design-master"
if [ -d "$D/.git" ]; then git -C "$D" pull --ff-only; else git clone https://github.com/crawfordxx/xiaoma-design-master.git "$D"; fi
"$D/install.sh"
```

仓库必须放在长期存在的目录（上面的 `~/.xiaoma-design-master`），**不要克隆到 `/tmp`**——技能是指向仓库的 symlink，
`/tmp` 被系统清理后所有技能都会失效。

`install.sh` 会把 `skills/` 下每个技能 symlink 到已检测到的 Agent 技能目录
（pi: `~/.pi/agent/skills/`，Claude Code: `~/.claude/skills/`）。
可选参数：`--target pi|claude|all`、`--skills 名字,名字`、`--uninstall`。

## 安装后验证

```bash
for s in ~/.claude/skills/xiaoma-*/ ~/.pi/agent/skills/xiaoma-*/; do
  [ -d "$s" ] && python3 ~/.xiaoma-design-master/tools/smoke_skill.py "$s"
done
```

这里检查的是装好的 symlink 路径本身，全部 `OK` 即安装成功。出现 `SKIP` 说明用户已有同名技能（目录或指向别处的链接），
把冲突告诉用户，由用户决定是否删掉旧的再重装。向用户报告：装了哪些技能、各自一句话能力（见 README 技能矩阵）。

## 注意

- 生成类技能（xiaoma-gen-*）需要用户先配置自己的模型 API：
  复制 `~/.xiaoma-design-master/toolkit/providers.example.toml` → 同目录 `providers.toml` 并填入密钥。
  未配置时这些技能会明确提示，不影响其他技能使用。
- 安装位置是 symlink：仓库更新（git pull）后技能自动更新，无需重装。
