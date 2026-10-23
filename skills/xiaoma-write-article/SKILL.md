---
name: xiaoma-write-article
version: 0.1.0
description: 长文生产线——从一句话想法到可发布的深度文章。选题五维评分、原子洞察、六大框架、四级去 AI 味、配图、SEO 一条龙。当用户说"写文章""写公众号""写长文""帮我写一篇关于 XX 的深度内容"时使用。
triggers: [写文章, 写公众号, 长文, 深度文章, write article, 公众号文章, 写一篇关于]
group: text
requires: gen
---

# 长文生产线（write-article）

把一个模糊的话题变成一篇有原子洞察、有人味、完读率高的长文。

## Onboarding（首次使用时展示）

> ✅ **长文生产线已就绪！**
> 给我一个话题（越具体越好），或者一句"帮我写一篇关于 XX 的文章"。
> 我会先出 10 个候选角度给你挑（或 auto 模式自动选最优），然后走完框架→写作→去 AI 味→配图→定稿全流程。
> 想要配图的话提前说风格偏好；不想配图说"不要图"。

## Usage

- "帮我写一篇关于 AI 编程趋势的文章" —— 全自动管线
- "写公众号：远程办公的真相" —— 默认公众号调性
- "交互模式写这篇" —— 选题/框架/配图每步停下来等确认

## Pipeline

下文 `S=<本技能目录>`（直接用安装路径，不必解 symlink）；`$S/toolkit/gen` 是生成能力的唯一入口。

**Step 1 选题**：读 [`shared/topic-selection.md`](shared/topic-selection.md)。生成 10 个候选（五维评分 + 原子洞察草稿 + 转发理由），对照 `workspace/history.jsonl` 近 7 天去重。auto 模式选最高分；interactive 模式列表格等选择。

**Step 2 框架**：读 [`shared/frameworks.md`](shared/frameworks.md)。按选择矩阵出 5 个框架提案（含开头策略/情绪弧/金句位），auto 选最高分。

**Step 3 写前思考**：读 [`shared/writing-guide.md`](shared/writing-guide.md) 的"写前思考框架"，在思考区内完成 8 项（读者场景/情绪旅程/核心矛盾/原子洞察/最强反驳/电影场景/赌注/信息不对称）。说不出原子洞察就回 Step 1。

**Step 4 写作**：按选中框架写 1500–2500 字。全程执行 writing-guide 的具体性铁律和情绪架构（峰值放 60–70% 处）。写完跑三重自检：深度清单（≥2 个三级"So What"）/ 截图测试（≥1 段截图级）/ 声音校验。

**Step 5 去 AI 味 + 标题**：读 [`shared/de-ai-protocol.md`](shared/de-ai-protocol.md)，四级协议全跑（L1 词表全量清扫 → L2 结构 → L3 认知 → L4 终检）。标题出 3 个候选（不同策略）选最具体的。任何一级不过回炉，不带着 AI 味进入下一步。

**Step 6 配图**：读 [`shared/visual-prompts.md`](shared/visual-prompts.md)。先问图片范围（封面+内文/仅封面/不要图）和风格。封面走三创意方向，内文按决策表选段。生成统一走：
```bash
$S/toolkit/gen image --prompt "..." --ratio 16:9 --tier draft   # 试稿
# 用户确认后
$S/toolkit/gen image --prompt "..." --ratio 16:9 --tier final --out workspace/projects/<slug>/images/cover.png
```

**Step 7 交付**：定稿存 `workspace/projects/<slug>/final.md`，按 [`shared/runtime-rules.md`](shared/runtime-rules.md) 的结果链接区收尾（文件路径 + 下一步建议 1 条）。

## 执行模式

- **auto（默认）**：Step 1–5 自动跑，Step 6 前问一次图片范围/风格（必问），其余不停
- **interactive**：选题、框架、配图方案、成稿四个节点等确认

## 弹性规则

配图生成失败 → 输出完整提示词包（用户可去任何工具生成），文章照常交付。联网调研失败 → 基于已有知识写并在文末标注"未联网核验"。绝不断管线。

## Gotchas

- **选题即胜负**：洞察 9 分热度 7 分的话题 > 热度 10 分洞察 3 分
- **框架填空题**：六框架执行得完美但内容通用 = 白写，深度清单先过
- **去 AI 味后置**：写的时候别自我审查，写完 L1–L4 一次跑完
- **AI 论文腔**：具体性表格里左列的每一个词都是死刑信号
