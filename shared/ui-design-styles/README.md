# UI 风格库（ui-design-styles）

> 18 个结构原型 × 各 6 套真实调色板，从 1015 个获奖/提名站点的线上 CSS 聚类得出。
> **结构与色彩解耦**：先按产品调性选结构原型（底色 × 排版 × 表面），再从它的调色板里挑一套——每套都来自一个真实站点，可直接抄 tokens。

## 决策树

```
产品是"创作/沉浸/影院式"体验？ → 底色 Void / Ink
产品给专业人士用（数据 / 开发 / B2B）？ → 底色 Dusk
内容站 / 作品集 / 不确定？ → 底色 Mist
教育 / 轻消费 / 需要"轻盈感"？ → 底色 Daylight
         ↓
Agent / 开发者工具 → Console / Mono 排版
杂志 / 文化 / 作品集 / 时尚 → Editorial / Literary
活动页 / 发布会 / 海报式落地页 → Poster
通用 Web / 响应式 → Fluid
         ↓
消费级 AI / 未来感 → Glass 表面
硬科技 / 工程 → Hard
年轻 / 活力 / Z 世代 → Pill
高端 / 克制 / 奢侈 → Mute
高饱和点缀 / 潮流 → Pop
不确定 → Soft
         ↓
在 cards/ 里找最接近的原型，从它的 6 套调色板中按点缀色系挑一套
```

## 场景适配

| 场景 | 用法 |
|---|---|
| **网站 / 落地页** | 卡的全套照用：结构 + 调色板 + 缓动 + 关键帧 |
| **PPT** | 借调色板 + 字体气质 + 字阶跨度；动效不适用 |
| **App** | 借色彩 / 圆角 / 字阶；触控 ≥44px，底部导航优先 |
| **品牌物料** | 借调色板 + 字体，交给 xiaoma-designer 执行 |

## 组合规则

- 主原型定结构，调色板只选一套，不混两套的 accent
- 深底原型想加亲和力 → 换它里面的暖色点缀调色板，**不是**把暗底调亮
- 说不清"这是 ×× 结构 + ×× 色系" = 没想清楚，回决策树

## 通用铁律

### Icon：禁止首字母 / 首文字
- ❌ 产品名首字母做 logo、功能名首字做图标、"01"/"AI" 占位、空方块
- ✅ 每个功能点配语义图标（Lucide / Phosphor / Heroicons），找不到贴切的就生成
- 品牌标识用抽象图形，不用文字缩写

### 媒体：复杂结构必须生成图 / 视频
- Glass / Pill / Poster 原型 → **必须** hero 视觉图 + 2–3 张场景图，有条件加 6–10 秒循环视频
- Void / Ink 原型 → **必须** 3–4 张示例作品填画廊（深底空荡最致命）
- 任何原型 → 页面里不留空占位框 / 灰方块 / 空 src
- 主动建议："这个风格靠视觉撑，建议生成 hero 图 + 8 秒循环视频，我可以直接出。"

### 文案：不摆数据、不列依据、不说废话
- ❌ "提升 300%"、"服务 500+ 客户"、"致力于 / 赋能 / 一站式"、"功能强大 / 易于使用"
- ✅ 做什么 + 给谁 + 凭什么不一样；标题 ≤8 字，副标题 ≤25 字，段落 ≤3 行
- 每句话自问：删掉它页面少了什么？答不出就删

---

## 原型索引

| 原型 | 站点数 | 调色板 | 结构 | 适合 |
|---|---|---|---|---|
| [`dusk-literary-hard`](cards/dusk-literary-hard.md) | 132 | 6 | dusk · literary · hard | 专业工具 / 数据 / B2B · 出版 / 时尚 / 人文 |
| [`dusk-poster-mute`](cards/dusk-poster-mute.md) | 117 | 6 | dusk · poster · mute | 专业工具 / 数据 / B2B · 活动页 / 发布会 / 品牌 |
| [`dusk-mono-soft`](cards/dusk-mono-soft.md) | 80 | 6 | dusk · mono · soft | 专业工具 / 数据 / B2B · 开发者 / 数据 / 文档 |
| [`mist-poster-mute`](cards/mist-poster-mute.md) | 72 | 6 | mist · poster · mute | 通用 SaaS / 内容站 / 作品集 · 活动页 / 发布会 / 品牌 |
| [`dusk-editorial-soft`](cards/dusk-editorial-soft.md) | 68 | 6 | dusk · editorial · soft | 专业工具 / 数据 / B2B · 杂志 / 文化 / 作品集 |
| [`mist-console-glass`](cards/mist-console-glass.md) | 68 | 6 | mist · console · glass | 通用 SaaS / 内容站 / 作品集 · Agent / 开发者 / 工程 |
| [`mist-mono-pill`](cards/mist-mono-pill.md) | 66 | 6 | mist · mono · pill | 通用 SaaS / 内容站 / 作品集 · 开发者 / 数据 / 文档 |
| [`dusk-console-soft`](cards/dusk-console-soft.md) | 64 | 6 | dusk · console · soft | 专业工具 / 数据 / B2B · Agent / 开发者 / 工程 |
| [`mist-literary-soft`](cards/mist-literary-soft.md) | 54 | 6 | mist · literary · soft | 通用 SaaS / 内容站 / 作品集 · 出版 / 时尚 / 人文 |
| [`daylight-fluid-pop`](cards/daylight-fluid-pop.md) | 44 | 6 | daylight · fluid · pop | 内容 / 教育 / 轻消费 · 通用 Web / 响应式站 |
| [`mist-poster-hard`](cards/mist-poster-hard.md) | 38 | 6 | mist · poster · hard | 通用 SaaS / 内容站 / 作品集 · 活动页 / 发布会 / 品牌 |
| [`daylight-mono-hard`](cards/daylight-mono-hard.md) | 38 | 6 | daylight · mono · hard | 内容 / 教育 / 轻消费 · 开发者 / 数据 / 文档 |
| [`mist-literary-soft-4`](cards/mist-literary-soft-4.md) | 37 | 6 | mist · literary · soft · 4 | 通用 SaaS / 内容站 / 作品集 · 出版 / 时尚 / 人文 |
| [`void-console-glass`](cards/void-console-glass.md) | 31 | 6 | void · console · glass | 创作工具 / 影院 / 沉浸叙事 · Agent / 开发者 / 工程 |
| [`ink-literary-pill`](cards/ink-literary-pill.md) | 30 | 6 | ink · literary · pill | 高端品牌 / 画廊 / 奢侈 · 出版 / 时尚 / 人文 |
| [`void-editorial-glass`](cards/void-editorial-glass.md) | 29 | 6 | void · editorial · glass | 创作工具 / 影院 / 沉浸叙事 · 杂志 / 文化 / 作品集 |
| [`mist-fluid-mute`](cards/mist-fluid-mute.md) | 27 | 6 | mist · fluid · mute | 通用 SaaS / 内容站 / 作品集 · 通用 Web / 响应式站 |
| [`void-fluid-glass`](cards/void-fluid-glass.md) | 20 | 6 | void · fluid · glass | 创作工具 / 影院 / 沉浸叙事 · 通用 Web / 响应式站 |