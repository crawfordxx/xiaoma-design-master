# quiet-luxury — 米白 · 炭黑 · 极小字 · 无圆角

> 建筑与高端品牌的美学：安静、克制、昂贵感来自留白和字距。字小，图大，无圆角。
> 适合：建筑事务所、高端地产、画廊、精品品牌、设计师酒店、高端咨询。

## Tokens

```css
:root {
  /* 画布：米白，有温度 */
  --bg-body: #f0f0f0;       --bg-panel: #f5f5f5;      --bg-dark: #0f0f0f;
  /* 文字：炭黑 */
  --text-1: #0f0f0f;        --text-2: #3a3a3a;        --text-3: #8c8c8c;   --text-4: #bfbfbf;
  /* 无彩色点缀。唯一的"颜色"是材质本身 */
  --line: rgba(15,15,15,.12);
  /* 字体：Helvetica 血统的无衬线，不花哨 */
  --font-sans: "Helvetica Neue", "Inter", "Neue Haas Grotesk", system-ui, sans-serif;
  /* 字阶：小。正文 14，说明 10–12，标题也不夸张 */
  --fs-display: 2.0625rem;  --lh-display: 115%;   /* 33px */
  --fs-h2: 1.75rem;         --lh-h2: 115%;        /* 28px */
  --fs-body: 1rem;          --lh-body: 128%;
  --fs-small: .875rem;      --lh-small: 119%;     /* 14px */
  --fs-caption: .75rem;     --lh-caption: 128%;   /* 12px */
  --fs-micro: .625rem;      --lh-micro: 87%;      /* 10px */
  --fw-regular: 400; --fw-medium: 500;    /* 不用粗体 */
  --track-heading: -.03em;  --track-body: -.02em;  --track-label: -.05em;
  /* 圆角：无 */
  --r-none: 0;  --r-full: 50%;
  /* 阴影：无 */
  /* 动效：慢，一条曲线 */
  --ease: cubic-bezier(.25, 1, .5, 1);   --duration: 600ms;
  /* 间距：大 */
  --sp-2: 8px; --sp-4: 16px; --sp-6: 24px; --sp-8: 32px; --sp-12: 48px; --sp-16: 64px; --sp-24: 96px;
}
```

## 组件基调

| 组件 | 规格 |
|---|---|
| 按钮 | **看起来不像按钮**：小字 + 下划线，或纯文字 + `→`。hover 下划线消失 |
| 链接 | 文字 + 底部 1px 线，hover 线变 `--text-3` |
| 输入框 | 无边框，只有底部线，字 14，focus 线变黑 |
| 卡片 | 无。图片直接放，不加容器 |
| 导航 | 顶部：左 logo、右几个文字链接，字 12，大写，字距 `.1em`，无背景 |
| 分割 | `--line` 1px，或者用空白 |
| 页脚 | 大量空白后，几列小字 |

## 版式

- 字小：正文 14–16，标题最大 33。**字越小人越觉得贵**
- 留白是主角：区块间距 96–128px
- 图片占 70%+ 面积，文字退到角落
- 大写小标签 10px，字距 `.1em`，灰
- 严格对齐到网格，左右边距对称
- 一屏一件事，滚动慢

## 媒体策略

- **必须**生成：1–3 张建筑/空间/材质大图（自然光、无人物、无杂物）
- 可选：1 张材质特写（石材/木纹/织物）
- 图像处理：低饱和、柔光、不要锐利；灰度或接近灰度
- 视频：可选，极慢的推拉镜头，10–20 秒

生图提示词方向：architectural photography, natural light, minimalist interior, concrete and wood, soft shadows, muted tones, editorial, Hasselblad, no people。

## 动效

- 慢：600–800ms，`--ease`
- 图片进场：clip-path 从下揭示，或 opacity 慢淡入
- hover：图片 scale 1.03，2s 极慢
- 滚动：固定背景视差，克制

## Icon

极细 1px 线，灰色，小（16px）；或不用图标，用文字。无容器。
