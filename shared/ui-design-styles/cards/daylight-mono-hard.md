# daylight-mono-hard — 亮色画布 · 等宽工程 · 零圆角

> 38 个站聚出的结构原型，4 个获奖。特征：底色亮度 0.909 / 字阶跨度 4.957× / 大写 0.569 / 圆角中位 2px / blur 1.789 / 渐变 0.476。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 1px;  --r-md: 12px;  --r-lg: 9999px;
/* 字阶众数 */ --fs: 1rem, 1.125rem, 1.25rem, 11px, 14px, 2rem, 12px;
/* 缓动 */ --ease: cubic-bezier(.4,0,.2,1);  --ease-2: cubic-bezier(.19,1,.22,1);
```

### 版式与组件

- 全部直角，靠 1px 线分隔，不用卡片阴影

### 动效

- 缓动：cubic-bezier(.4,0,.2,1), cubic-bezier(.19,1,.22,1), cubic-bezier(.16,1,.3,1), cubic-bezier(.23,1,.32,1)
- 高频关键帧：pulse, spin, blink, grain, nprogress-spinner, caret-blink, hsstFadeIn, hsstFadeOut, ltBlink, rtSpin, svg-sign-draw, svg-sign-show

### 品类
sites_of_the_day, webgl, 3d, animation, scrolling
标签：storytelling, clean, experimental, typography, microinteractions, transitions, minimal

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 亮底，点缀红
来源：Honorable Mention · sound-audio / clean / flat-design

```css
--bg-body: #e5f9d7;  --bg-panel: #f9eddc;
--text-1: #111;  --text-2: #111;
--accent-1: #ff7452;  /* 红 */
--neutral: #768978 #8c8277 #8f7e77;
/* 字体 */ Druk | Share Tech Mono | Silkscreen
/* 圆角 */ 2 / 10 / 10px
/* 缓动 */ cubic-bezier(.4,-.01,0,.99)
/* 关键帧 */ arcade-blink, blink, flicker, footer-pulse, loader-blink, loader-bracket-left
```

### 方案 2 — 深底，点缀红/红
来源：Honorable Mention · experimental / sound-audio / storytelling

```css
--bg-body: #08090b;  --bg-panel: #08090b;
--text-1: #edeff2;  --text-2: #c8f2ff;
--accent-1: #ff8a6b;  /* 红 */
--accent-2: #ff4a3d;  /* 红 */
/* 字体 */ Archivo | JetBrains Mono
/* 缓动 */ cubic-bezier(.2,.7,.2,1)
/* 关键帧 */ blink, eq, spin
```

### 方案 3 — 深底，点缀红/绿
来源：Honorable Mention · clean / minimal

```css
--bg-body: #1d1d1b;  --bg-panel: #1d1d1b;
--text-1: #f9fafb;  --text-2: #f9fafb;
--accent-1: #f56565;  /* 红 */
--accent-2: #93c572;  /* 绿 */
--accent-3: #78b551;  /* 绿 */
--neutral: #ababab;
/* 圆角 */ 6 / 6 / 6px
/* 缓动 */ cubic-bezier(.625,.05,0,1)
```

### 方案 4 — 深底，点缀红
来源：Nominee · experimental / clean / storytelling

```css
--bg-body: #393939;  --bg-panel: #1a1a1a;
--text-1: #c8c8c8;  --text-2: #c3c3c3;
--accent-1: #e8271c;  /* 红 */
--neutral: #afafaf #6e6e6e #636363;
/* 字体 */ PP Supply Sans | PP Supply Mono
/* 缓动 */ cubic-bezier(.22,.61,.36,1)
/* 关键帧 */ ftr-run, grain, hud-hatch, is, lineFadeOnly, lineIn
```

### 方案 5 — 亮底，点缀红/蓝
来源：Nominee · experimental

```css
--bg-body: #f0f4f7;  --bg-panel: #d4dae0;
--text-1: #242c31;  --text-2: #1e2428;
--accent-1: #da382e;  /* 红 */
--accent-2: #007aff;  /* 蓝 */
--accent-3: #369763;  /* 绿 */
--neutral: #4f4f4f #a7a4a4 #64605e;
/* 字体 */ monospace | ff("primary") | HelveticaNowDisplay
/* 圆角 */ 4 / 10 / 10px
/* 缓动 */ cubic-bezier(0.215, 0.61, 0.355, 1)
/* 关键帧 */ fall, featuredProjectsAllFlash, lisaCursor, lisaDisclaimerFlash, lisaDisclaimerProcedure, lisaLoader
```

### 方案 6 — 深底，点缀青/黄
来源：Nominee · gallery

```css
--bg-body: #191b1b;  --bg-panel: #191b1b;
--text-1: #efede7;  --text-2: #efede7;
--accent-1: #00784a;  /* 青 */
--accent-2: #8a6a00;  /* 黄 */
--accent-3: #5e53e3;  /* 蓝 */
/* 缓动 */ cubic-bezier(0.65, 0, 0.35, 1)
/* 关键帧 */ caret-blink, hsstFadeIn, hsstFadeOut, ltBlink, rtSpin, svg-sign-draw
```
