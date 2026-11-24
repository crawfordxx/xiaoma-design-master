---
name: xiaoma-gen-ui
version: 0.2.0
description: 网站 UI 设计生产线——先按产品匹配设计风格（18 个结构原型 × 6 套真实调色板，从 1015 个站点聚类得出），再按指定技术栈 oneshot 出高品质前端：shadcn/ui、Lucide、Motion、Tailwind v4；复杂风格自动推图/视频生成，每个功能点必配语义图标，文案禁数据堆砌。当用户说"做个网站""设计落地页""做个网页 UI""写个前端页面"时使用。
triggers: [网站设计, 网页设计, 落地页, 前端页面, UI设计, landing page, 网站UI, 做个网页, web design, 官网, 产品页]
group: ui
requires: gen
---

# 网站 UI 设计（gen-ui）

匹配风格 → tokens 先行 → 组件搭建 → 媒体填充 → 自检循环 = oneshot 也能出获奖品质的前端。

## Onboarding

> ✅ **网站 UI 设计已就绪！**
> 告诉我：做什么 + 给谁看 + 一句话调性。
> 不懂前端也能用：我按指定技术栈搭，风格我来匹配，交付可运行的代码。

## Usage

- "做一个 AI 产品的落地页"
- "给摄影师做个作品集网站"
- "做个数据分析 dashboard，要能拖拽面板"

## 五条铁律

1. **先匹配风格**——走 [`shared/ui-design-styles/README.md`](../../shared/ui-design-styles/README.md) 决策树：底色 × 排版 × 表面 → 锁一个结构原型，再从它的 6 套调色板挑一套。tokens 直接抄，不凭感觉配色
2. **按品类选交互**——走 [`shared/ui-interactions/README.md`](../../shared/ui-interactions/README.md)，Agent 对话 / SaaS 仪表盘 / 创意工具 & 移动端三套模式库，动效不自己发明
3. **优先复用成熟库**——不重复造轮子，创造力花在设计和体验上
4. **组件源代码可控**——shadcn/ui 这类"复制进项目"的体系，不用黑盒依赖
5. **视觉资产不留空**——复杂风格必须生成图/视频，每个功能点必配语义图标

## 指定技术栈（oneshot 品质的根基）

| 能力 | 唯一指定库 | 用法要点 |
|---|---|---|
| UI 组件 | **shadcn/ui** | 初始化选 zinc/slate 基准 + CSS variables；CLI 添加组件进项目源码；按风格 tokens 覆写 `--background/--primary/--radius` 等 |
| 图标 | **Lucide** | `<Icon size={18} />`，全站只此一家；**每个功能点必配，禁首字母/文字占位** |
| 动画 | **Motion**（motion.dev） | 滚动/进出场/微交互全用它，缓动曲线从风格文件取 |
| 面板布局 | **react-resizable-panels** | 可拖拽调宽分栏（dashboard / 编辑器） |
| 拖拽 | **dnd-kit** | 列表排序 / 看板 / 自由拖放 |
| 状态管理 | **Zustand** | 跨组件状态一个 store |
| 样式 | **Tailwind CSS v4** | tokens 写成 CSS 变量，在 `@theme` 里映射成工具类 |

依赖纪律：`package.json` 里动画库只有 motion、图标库只有 lucide、拖拽库只有 dnd-kit、状态库只有 zustand。同类第二个 = 违规。

## Pipeline

`S=<本技能目录>`；图片/视频用 `$S/toolkit/gen`。

**Step 1 需求定义**：页面类型 / 目标受众 / 核心转化目标（一个）/ 调性关键词（≤3）。产出一句话 brief。

**Step 2 风格匹配**（不可跳）：
读 [`shared/ui-design-styles/README.md`](../../shared/ui-design-styles/README.md) 决策树，三步定位：底色（Void/Ink/Dusk/Mist/Daylight）× 排版（Console/Mono/Editorial/Literary/Poster/Fluid）× 表面（Glass/Hard/Pill/Mute/Pop/Soft）→ 在 `cards/` 里找最接近的结构原型。打开那张卡，把**结构规格**（圆角/字阶/缓动）抄进 `@theme`，再从卡内 6 套调色板按点缀色系挑 **1 套**，整段抄进去。
用户给了风格词 → 映射到最近的原型，原话留作参考。用户没给 → 按品类推荐，一句理由，直接开做，不问。

**Step 2b 交互模式匹配**（不可跳）：
读 [`shared/ui-interactions/README.md`](../../shared/ui-interactions/README.md)，按产品品类选模式库：Agent 对话类 → `agent-chat.md`；仪表盘/SaaS → `saas-dashboard.md`；编辑器/画布/App → `creative-mobile.md`。混合产品两个都读。记下要用到的模式（流式输出 / 工具调用折叠 / 任务时间线 / 状态灯 / 部署流水线……），Step 6 照着实现。

**Step 3 设计语言**：在风格 tokens 基础上确认色板 / 字体 / 间距 / 圆角 / 阴影。**中文字体**：正文用系统栈（`"PingFang SC","Microsoft YaHei","Noto Sans SC",sans-serif`）；标题要个性时选可商用开源字体（思源黑体/宋体、霞鹜文楷）并按用字子集化。**从这一步起所有视觉决策只从 tokens 取值。**

**Step 4 参考研究**：按 [`shared/ui-design.md`](../../shared/ui-design.md) "设计资源速查"——导航前看 navbar.gallery，CTA 前 cta.gallery，布局前 bentogrids.com，动画前 motion.dev。每个大区块动手前看 2–3 个参考。

**Step 5 组件搭建**：shadcn CLI 加组件 → tokens 定制 → Lucide 图标。顺序：导航 → Hero → 内容区（Bento 优先）→ CTA → 页脚。

**Step 6 动画层**（Motion）：
先读 [`shared/ui-interactions/README.md`](../../shared/ui-interactions/README.md) 按产品品类选交互模式库（Agent 对话 / SaaS 仪表盘 / 创意工具 & 移动端），关键帧和时长直接复用。
- 滚动：`useScroll` + `useTransform`（视差 / 进度 / 揭示）
- 进出场：`whileInView` + `AnimatePresence`，stagger 列表（卡片 50ms / 列表项 30ms）
- 微交互：hover / press spring 反馈
- **状态动效四种必有**：进行中（spin / ping）/ 成功（iconSuccess 弹一下）/ 失败（shake + 红）/ 等待（静态灰）
- **流式输出**：逐 token 淡入 + 光标闪烁 + `aria-live="polite"`
- **工具调用**：默认折叠一行，点击 accordion 展开，状态图标随阶段切换
- 缓动：以原型卡里的 `--ease` 为准（簇内高频曲线），不自己发明
- 3D：需要时 three.js，与 Motion 分层不混用
- **纪律**：一屏一个主动画事件，每个动效有目的，60fps 底线，`prefers-reduced-motion` 必处理

**Step 7 媒体资产**（必做，不是可选）：
按风格文件的"媒体策略"生成，走 [`shared/ui-design.md`](../../shared/ui-design.md) 媒体路由。
- 表面含 Glass / Pill / Poster → **必须** hero 视觉图 + 2–3 张场景图，有条件加循环视频
- 底色 Void / Ink → **必须** hero 拼贴 + 3–4 张示例作品（深底空荡最致命）
- 其余原型 → **至少** 1–3 张风格匹配图
- 主动建议："这个风格靠视觉撑，建议生成 hero 图 + 8 秒循环视频，我可以直接出。"
- 页面里**不允许**空占位框 / 灰色方块 / 空 `src`

**Step 8 Icon 体系**（不可跳）：
读 [`shared/icon-design.md`](../../shared/icon-design.md) 选流派——工具类产品用**实心镂空派**（工具型 A / Linear 参数），消费级用描边派。
- 默认用 Lucide 时，主功能图标**重绘成"线即形状"**：24 网格、线宽 2、圆角 1.0、`fill="currentColor"`、`evenodd` 镂空（建模模板见文档 §5.2）
- 每个功能点、Bento 卡片、定价档、步骤都有语义图标，找不到贴切的就按模板画
- **禁止**首字母 / 首字 / "01" / 空方块占位；品牌标识用抽象图形
- 14px 渲染检查：边缘干净不发虚、交叉处无鼓包

**Step 9 文案检查**：
删百分比 / 客户数 / 市场排名；删"致力于/赋能/打造/一站式"；删"功能强大/易于使用"。只留：做什么 + 给谁 + 凭什么不一样。标题 ≤8 字，副标题 ≤25 字，段落 ≤3 行。

**Step 10 品质自检循环**（awwwards 标准）：

| 维度 | 权重 | 检查 |
|---|---|---|
| Design | 40% | 层级 / 留白 / 排版 / 色彩一致性 / 是否像模板 |
| Usability | 30% | 首屏直觉 / 可点明确 / 移动端 / 加载态 |
| Creativity | 20% | 记忆点 / 独家交互 / 不落俗套 |
| Content | 10% | 文案质量 / 信息密度 / 是否对受众说话 |

**硬指标先过**：
- 375px 无横向滚动，触控目标 ≥44px
- 正文对比度 ≥4.5:1，大字 ≥3:1
- 控制台零报错；依赖纪律通过
- 动画尊重 `prefers-reduced-motion`；首屏图有宽高
- Lighthouse 移动端 Performance ≥90、Accessibility ≥95
- **每个功能点有语义图标，无首字母/文字占位；主功能图标是实心镂空建模**
- **无空占位框，所有视觉位有真实资产**
- **文案无百分比/客户数/形容词堆砌**
- **状态动效四种齐全**（进行中/成功/失败/等待），流式输出有 aria-live

流程：跑起来 → 全页截图（桌面 + 移动）→ 硬指标 → 逐维度找问题（具体到"Hero 副标题对比度不足"）→ 修 → 重打分。每维分数引用截图证据，9 分以上要说出记忆点。**任一维 <9 再来一轮，最多 3 轮**；3 轮后仍有短板如实标注交付。

## 执行模式

auto：brief 确认后全自动到 Step 10 第 2 轮自检，带截图汇报。interactive：风格匹配 / 区块结构 / 动画方案三节点确认。

## 弹性规则

风格文件打不开 → 用内置原则继续（tokens 纪律 / Bento / 微交互标准已内化）。shadcn CLI 不可用 → 手写同 API 组件。生成工具不可用 → 用高质量免费图库（Unsplash 按风格关键词）临时替代，**标注需替换**。three.js 失败 → 降级静态渲染图。

## Gotchas

- **跳过风格匹配**：直接凭感觉配色 = 模板脸，回 Step 2
- **调色板混搭**：从两套调色板各拿 accent = 色彩体系破，只选一套
- **魔法数瘟疫**：`#3b82f6`、`mt-[17px]` 出现 = tokens 已破，回 Step 3
- **依赖膨胀**：同类第二库出现即违规
- **空占位框**：灰色方块 / 空 src = 半成品，回 Step 7
- **首字母图标**："X" 方块 / "AI" 字块 = 偷懒，回 Step 8
- **数据堆砌文案**："提升 300%" = 廉价，回 Step 9
- **动画堆砌**：每区块都在动 = 没重点；一屏一个主动画
- **跳过自检**：不看截图就交付 = Design 自动 5 分起评
- **参考当模板抄**：navbar.gallery 是看构图逻辑，不是复制配色文案
