# ink-editorial — 纸白 · 墨黑 · 一点锈红 · 印刷感

> 独立创作者的作品集美学：像一本印刷精致的杂志。大写、等宽、网格、留白。
> 适合：独立设计师/摄影师/艺术家作品集、文化项目、出版社、精品内容站。

## Tokens

```css
:root {
  /* 纸感底色，不用纯白 */
  --bg-body: #fdfcfb;       --bg-panel: #f7f7f7;      --bg-muted: #eae8e4;
  /* 墨色文字，不是纯黑 */
  --text-1: #1e1e1e;        --text-2: #262626;        --text-3: #484848;   --text-4: #d6d6d5;
  /* 点缀：锈红，只用在一处 */
  --rust: #b03a1e;          --rust-light: #e06a4a;
  /* 字体：无衬线 + 等宽 + 像素，三轨 */
  --font-sans: "Oracle", "Helvetica Neue", "Inter", sans-serif;
  --font-mono: "PP Neue Montreal Mono", "Geist Mono", "JetBrains Mono", ui-monospace, monospace;
  --font-pixel: "Geist Pixel Square", monospace;
  /* 字阶：语义变量，全部 clamp 流式 */
  --fs-display: clamp(3rem, 8vw, 7rem);   --lh-display: .95;
  --fs-h2: clamp(1.5rem, 3vw, 2.5rem);    --lh-heading: 1.1;
  --fs-h3: 1.25rem;                       --lh-tight: 1.2;
  --fs-body: 1rem;   --fs-body-sm: .875rem;   --fs-nav: .75rem;   --fs-mono-sm: .6875rem;
  --lh-body: 1.5;
  --fw-regular: 400; --fw-medium: 500;    /* 可变字体 100–900 全用 */
  /* 字距：等宽小标签宽字距，标题紧字距 */
  --track: -.02em;   --track-heading: -.04em;   --track-display: -.08em;   --track-hud: .08em;
  /* 圆角：小到无，印刷是直角 */
  --r-sm: 2px;  --r-md: 4px;  --r-lg: 6px;  --r-2xl: 8px;  --r-pill: 999px;  --r-full: 50%;
  /* 阴影：几乎无，靠线 */
  --shadow-card: 0 1px 2px rgba(30,30,30,.06);
  --shadow-modal: 0 24px 48px rgba(30,30,30,.12);
  /* 动效：完整缓动库 */
  --ease: cubic-bezier(.16, 1, .3, 1);           /* out-expo 默认 */
  --ease-front: cubic-bezier(.76, 0, .2, 1);
  --ease-back-soft: cubic-bezier(.58, 0, .38, 1);
  --ease-out-back: cubic-bezier(.34, 1.56, .64, 1);
  --ease-in-out-back: cubic-bezier(.68, -.6, .32, 1.6);
  /* 间距 */
  --sp-2: 8px; --sp-3: 12px; --sp-4: 16px; --sp-6: 24px; --sp-8: 32px; --sp-12: 48px;
}
```

## 组件基调

| 组件 | 规格 |
|---|---|
| 主按钮 | 墨黑底 `--text-1` → hover `--rust`，白字 14/500 **大写** + 字距 `.08em`，高 44，圆角 4 |
| 次按钮 | 透明 + 1px 墨线，圆角 4 |
| 输入框 | 无底色，只有 1px 下划线，focus 换墨黑实线 |
| 卡片 | 无底色，1px `--bg-muted` 线框，圆角 4，hover 换墨线 |
| 导航 | 顶部细线 + 等宽小字大写，无背景 |
| 标签 | 等宽小字 `.6875rem`，方括号包裹 `[ TAG ]`，锈红 |
| 分割线 | 1px `--text-1`，页面级；1px `--bg-muted`，区块级 |

## 版式

- **全部大写**：导航、标签、按钮、小标题全大写 + 宽字距
- 标题 display 7rem，字距 `-.08em`，行高 .95
- 等宽字体用于：导航、页码、坐标、时间戳、元数据——制造"印刷标记"感
- 严格网格：12 列，元素对齐到网格线，可见的细线分隔
- 大量留白，一屏一个主体
- 悬浮 HUD：右上角/左下角固定等宽小字（坐标、计数、状态）

## 媒体策略

- 作品图必须高清、有颗粒感或胶片质感（不要数码锐利）
- 生成 1–2 张带纸张纹理/印刷网点的氛围图
- 人物头像：黑白或单色调
- 图片处理：`filter: grayscale(1) contrast(1.1)` 或 `mix-blend-mode: multiply`

生图提示词方向：editorial photography, film grain, printed matter aesthetic, natural light, muted tones, paper texture, risograph。

## 动效

- 页面切换：`--ease-front` 横向推入
- 元素进场：`--ease` 上浮 + 淡入，stagger 50ms
- hover：下划线从左划入，`--ease` 300ms
- 滚动：视差，`--ease-back-soft`

## Icon

极简线性，1px stroke，墨色；或等宽字符符号（`→` `*` `#` `+`）。容器圆角 2px 或无。
