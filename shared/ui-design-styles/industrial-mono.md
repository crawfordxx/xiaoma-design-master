# industrial-mono — 纯黑 · 国际橙 · 等宽字 · 零圆角

> 硬科技的工程美学：像航天器的控制面板。等宽字、坐标标记、零圆角、一个橙色警示灯。
> 适合：航天/无人机/机器人/工程机械、B2B 硬件、国防科技、工程软件。

## Tokens

```css
:root {
  /* 画布：近纯黑，无色相 */
  --bg-body: #050505;       --bg-panel: #0c0c0c;      --bg-muted: #141414;
  /* 文字：冷白到冷灰 */
  --text-1: #fafafa;        --text-2: #dddddd;        --text-3: #c8c8c8;   --text-4: #5d6c7b;
  /* 唯一点缀：国际橙，警示灯级别的饱和 */
  --orange: #fc4f00;        --orange-dim: rgba(252,79,0,.15);
  /* 辅助蓝极少用 */
  --blue: #0082f3;
  /* 字体：等宽为主，衬线做罕见强调 */
  --font-mono: "Geist Mono", "JetBrains Mono", "IBM Plex Mono", ui-monospace, monospace;
  --font-sans: "Geist", "Inter", system-ui, sans-serif;
  /* 字阶：rem 制，精确到 4 位小数——工程感 */
  --fs-hero: 5rem;        --lh-hero: 90%;       /* 80px */
  --fs-h2: 2rem;          --lh-h2: 100%;        /* 32px */
  --fs-body: 1rem;        --lh-body: 130%;
  --fs-small: .69444rem;  --lh-small: 100%;     /* 11.1px */
  --fs-micro: .625rem;    --lh-micro: 88%;      /* 10px */
  --fs-tiny: .55556rem;   --lh-tiny: 75%;       /* 8.9px */
  --fw-regular: 400; --fw-medium: 500; --fw-bold: 700;
  --track-body: -.00972rem;  --track-hero: -.25rem;  --track-hud: -.06667rem;
  /* 圆角：零 */
  --r-none: 0;  --r-tag: 3px;  --r-full: 50%;
  /* 阴影：硬，不带模糊 */
  --shadow-hard: 0 0 0 1px rgba(0,0,0,.1), 0 1px 3px rgba(0,0,0,.1);
  --shadow-glow: 0 0 3px rgba(51,51,51,.4);
  /* 动效：单一曲线，精准 */
  --ease: cubic-bezier(.25, 1, .5, 1);
  /* 间距 */
  --sp-1: 4px; --sp-2: 8px; --sp-3: 12px; --sp-4: 16px; --sp-6: 24px; --sp-8: 32px;
}
```

## 组件基调

| 组件 | 规格 |
|---|---|
| 主按钮 | 橙底 `--orange` + 黑字，**直角**，等宽字 12 **大写** + 字距，高 44 |
| 次按钮 | 透明 + 1px 冷灰线，直角 |
| 输入框 | 无底色，底部 1px 线，等宽字，focus 换橙线 |
| 卡片 | `--bg-panel` 底，无圆角，1px `#1a1a1a` 线，左上角坐标标记 `[01]` |
| 导航 | 顶部等宽小字，无背景，项之间用 `/` 分隔 |
| 标签 | 等宽 micro 字，`<>` 或 `[]` 包裹，橙色 |
| 状态灯 | 8px 圆点，橙色 + `--shadow-glow` |

## 版式

- hero 标题 80px，行高 90%，字距 `-.25rem`（紧到几乎贴）
- **全文大写**（等宽字大写才有面板感）
- 大量 HUD 元素：四角坐标、版本号 `v2.4.1`、状态 `[ACTIVE]`、时间戳、进度条
- 严格网格 + 可见的辅助线（1px `#1a1a1a`）
- 等宽数字用于一切数据

## 媒体策略

- **必须**生成：1 张产品渲染图（无人机/机器人/机械，黑底 + 橙色 rim light，工程视角）
- 可选：1 张线稿/蓝图风示意图
- 可选：网格背景 / 坐标纸纹理
- 图像处理：高对比、去饱和，只留橙

生图提示词方向：industrial product render, matte black material, orange rim light, technical illustration, blueprint aesthetic, studio lighting, hard shadows, dark background。

## 动效

- 全部用 `--ease`，200–300ms，精准不弹
- 数据数字滚动更新
- 状态灯闪烁 `animation: blink 2s steps(1) infinite`
- 进场：元素从下 8px 淡入，无缩放

## Icon

极细线性，1px stroke，冷灰；激活态橙色。几何、直角、无圆角容器。用 `+` `-` `×` `/` `→` 这类字符符号做辅助。
