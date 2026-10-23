---
name: xiaoma-gen-ui
version: 0.1.0
description: 网站 UI 设计生产线——指定技术栈保证 oneshot 出高品质前端：shadcn/ui 组件体系、Lucide 图标、Motion 动画、react-resizable-panels 布局、dnd-kit 拖拽、Zustand 状态；配 10 个顶级设计参考源和 awwwards 级品质自检循环。当用户说"做个网站""设计落地页""做个网页 UI""写个前端页面"时使用。
triggers: [网站设计, 网页设计, 落地页, 前端页面, UI设计, landing page, 网站UI, 做个网页, web design]
group: ui
requires: gen
---

# 网站 UI 设计（gen-ui）

指定技术栈 + 统一设计语言 + awwwards 级自检循环 = oneshot 也能出获奖品质的前端。

## Onboarding

> ✅ **网站 UI 设计已就绪！**
> 告诉我：做什么（落地页/作品集/工具站/活动页）+ 给谁看 + 期望调性（高级黑/明亮活泼/科技感…）。
> 不懂前端也能用：我按指定技术栈搭，交付可运行的代码。

## Usage

- "做一个 AI 产品的落地页，深色高级感"
- "给摄影师做个作品集网站"
- "做个数据分析 dashboard，要能拖拽面板"

## 四条铁律

1. **优先复用成熟库**——不重复造轮子，把创造力花在设计和体验上
2. **组件源代码可控**——用 shadcn/ui 这类"复制进项目"的组件体系，不用黑盒依赖
3. **统一设计语言**——全站一套 design tokens（色板/字体/间距/圆角/阴影），一处定义处处引用
4. **严格限制重复依赖**——同类能力只装一个库（见下表），装第二个之前必须先删第一个

## 指定技术栈（oneshot 品质的根基）

| 能力 | 唯一指定库 | 用法要点 |
|---|---|---|
| UI 组件 | **shadcn/ui**（Nova 风格） | 初始化时选 Nova 风格（已有项目看 `components.json` 的 `style`），CLI 添加组件进项目源码，改起来完全可控；按钮/卡片/对话框/表单全从这来 |
| 图标 | **Lucide** | `<Icon size={18} className="..." />`，全站只此一家图标库 |
| 动画 | **Motion**（motion.dev） | 滚动动画/进出场/微交互全用它，不引第二个动画库 |
| 面板布局 | **react-resizable-panels** | 可拖拽调宽的分栏布局（dashboard/编辑器场景） |
| 拖拽 | **dnd-kit** | 列表排序/看板/自由拖放，键盘可达性内置 |
| 状态管理 | **Zustand** | 跨组件状态一个 store 搞定，不引 Redux/其他 |
| 样式 | **Tailwind CSS v4** | design tokens 写成 CSS 变量，在 `@theme` 里映射成工具类（v4 没有 `tailwind.config.js`） |

依赖纪律检查（交付前必过）：`package.json` 里动画库只有 motion、图标库只有 lucide、拖拽库只有 dnd-kit、状态库只有 zustand。出现同类第二个 = 违规。

## Pipeline

下文 `S=<本技能目录>`；需要生成图片/视频时用 `$S/toolkit/gen`（见 Step 6）。

**Step 1 需求定义**：页面类型 / 目标受众 / 核心转化目标（一个）/ 调性关键词（3 个以内）。产出一句话设计 brief。

**Step 2 设计语言**：先定 design tokens 再写任何组件——色板（主色/强调色/中性阶/暗色模式）、字体（标题/正文，最多两款）、间距系统、圆角、阴影层级。写成 CSS 变量并在 `@theme` 里映射。**中文站字体**：正文用系统字体栈（`"PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif`）；标题要个性时选可商用开源字体（思源黑体/宋体、霞鹜文楷等）并按页面实际用字子集化——整包中文字体动辄几 MB，会拖垮首屏。**从这一步开始所有视觉决策只从 tokens 取值，不写魔法数。**

**Step 3 参考研究**：按当前环节查对应资源（10 个参考源见 [`shared/ui-design.md`](shared/ui-design.md) 的"设计资源速查"）——做导航前看 navbar.gallery，做页脚前看 footer.design，做 CTA 前看 cta.gallery，做布局前看 bentogrids.com，写动画前看 60fps.design 和 motion.dev 文档。**每个大区块动手前先看 2–3 个参考再写。**

**Step 4 组件搭建**：shadcn/ui CLI 加组件 → 用 tokens 定制样式 → Lucide 图标。区块顺序：导航 → Hero → 内容区（Bento 网格优先考虑）→ CTA → 页脚。Bento 网格（参考 bentogrids.com）是内容区默认布局思路：大小不一的卡片拼出信息层级和视觉节奏。

**Step 5 动画层**（Motion）：
- 滚动动画：`useScroll` + `useTransform` 做滚动联动（视差/进度条/滚动揭示），参考 https://motion.dev/docs/react-scroll-animations
- 进出场：`whileInView` + `AnimatePresence`，stagger 排布列表项
- 微交互：hover/press 的 spring 弹性反馈（参考 https://motion.dev/examples?platform=react 和 60fps.design 的细节标准）
- 3D 场景：需要时用 **three.js**（产品 3D 展示/粒子背景），与 Motion 的 DOM 动画分层不混用
- **动画纪律**：每个动画要有目的（引导注意/反馈/空间连续），无目的的炫技动画删掉；60fps 是底线

**Step 6 媒体资产**：按 [`shared/ui-design.md`](shared/ui-design.md) 的媒体工具链路由生成图片/人物/场景/视频，不要现场换工具。

**Step 7 品质自检循环（awwwards 标准，不过不放行）**：

按 awwwards 评审维度给当前版本打分（每维 0–10）：
| 维度 | 权重 | 检查什么 |
|---|---|---|
| Design | 40% | 视觉层级/留白/排版/色彩一致性/是否像模板 |
| Usability | 30% | 首屏直觉/可点区域明确/移动端适配/加载态 |
| Creativity | 20% | 有没有记忆点/独家交互/不落俗套的布局 |
| Content | 10% | 文案质量/信息密度/是否对受众说话 |

**先过硬指标，不过不打分**（自评分容易虚高，硬指标是客观底线）：
- 375px 宽无横向滚动，触控目标 ≥44px
- 正文对比度 ≥4.5:1，大字 ≥3:1
- 浏览器控制台零报错；依赖纪律检查通过
- 动画尊重 `prefers-reduced-motion`；首屏大图有宽高、不跳版
- Lighthouse（移动端）Performance ≥90、Accessibility ≥95

流程：跑起来 → 全页截图（桌面+移动）→ 硬指标 → 逐维度找问题（具体到"Hero 副标题对比度不足"这种粒度）→ 修 → 重新打分。每个维度的分数必须引用截图里的具体证据，给 9 分以上要说出"记忆点是什么"。**任何一维 < 9 分就再来一轮，最多 3 轮**；3 轮后仍有短板，如实标注交付（"移动端 Usability 8 分：xx 原因"）。

## 执行模式

auto：brief 确认后全自动到 Step 7 第 2 轮自检，然后带截图汇报。interactive：设计语言/区块结构/动画方案三节点确认。

## 弹性规则

参考站打不开 → 用内置的设计原则清单继续（tokens 纪律/Bento 布局/微交互标准已内化在本文件）。shadcn CLI 不可用 → 手写同 API 组件保持源码可控原则。three.js 场景生成失败 → 降级为静态 3D 渲染图（媒体工具链出图）。

## Gotchas

- **魔法数瘟疫**：组件里出现 `#3b82f6`、`mt-[17px]` 这种硬编码 = 设计语言已破，回 Step 2
- **依赖膨胀**：装了 motion 又装 react-spring、装了 dnd-kit 又引 sortablejs——同类第二库出现即违规
- **模板脸**：shadcn 默认样式不改 tokens 直接上 = 一眼假官网，Nova 主题调性必须先落到自己的色板字体上
- **动画堆砌**：每个区块都在动 = 没有重点；一屏最多一个主动画事件
- **跳过自检**：不看截图就交付 = Design 维度自动 5 分起评，循环必须真实跑
- **参考当模板抄**：navbar.gallery 是看构图逻辑，不是复制配色和文案
