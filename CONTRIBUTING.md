# 贡献指南

## 目录结构

```
xiaoma-design-master/
├── skills/<技能名>/          # 每个技能一个目录（安装单元）
│   ├── SKILL.md             # 技能本体（frontmatter + 工作流）
│   ├── references/          # 技能专属参考文档（运行时会被 Agent 读取）
│   └── ...                  # scripts/genres 等运行时资产
├── shared/                  # 跨技能共享方法论（写作指南/提示词工程/平台规则/人物设计…）
├── toolkit/                 # 生成能力统一入口（gen 命令 + Provider 注册表 + 测试）
├── showcase/                # 展示资产（不随技能安装）
└── tools/                   # 结构自检工具
```

## 新增一个技能

1. 建目录 `skills/xiaoma-<名字>/SKILL.md`，frontmatter 必含 `name`（与目录同名）、`version`（semver）、`description`（中文一句话 + 触发场景）、`triggers`、`group`
2. 工作流写在正文，方法论沉淀到 `shared/` 用相对路径引用（`../../shared/xxx.md`）
3. **生成类技能（group 含 gen 调用）的硬规矩**：
   - 不出现任何具体模型名 / 服务商域名 / 直连 API 调用——一律走 `../../toolkit/gen <能力> --tier draft|final`
   - 模型名只允许出现在 `toolkit/providers.toml`（用户自己的配置）和 `shared/prompt-library.md`
4. 自检：`python3 tools/smoke_skill.py skills/xiaoma-<名字> --strict-gen`（生成类）或不带参数（其他）
5. 全仓冒烟：`./toolkit/verify.sh`（含单测、全部技能冒烟、敏感词检查）

## 新增一个生成服务商

1. 在 `toolkit/xiaoma_gen/adapters/` 写协议适配器（参照 `openai_chat.py` / `openai_images.py` / `async_video.py`），TDD：先写 mock 测试
2. 在 `toolkit/gen.py` 的 `ADAPTERS` 注册协议名
3. 用户侧只需在 `toolkit/providers.toml`（gitignore，不入库）加一段配置——**仓库零密钥**
4. 模板见 `toolkit/providers.example.toml`

## 硬性红线

- 公开内容（README/技能/共享库/文档）不提及研究过程、不提及任何其他平台名
- 仓库零密钥：密钥只走环境变量或用户本地文件
- 已有技能只增不改结构（改了请附迁移说明）

## 提交规范

`feat|fix|docs|chore: 中文一句话`
