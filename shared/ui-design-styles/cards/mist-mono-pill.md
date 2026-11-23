# mist-mono-pill — 中性灰画布 · 等宽工程 · 超大圆角

> 66 个站聚出的结构原型，13 个获奖。特征：底色亮度 0.196 / 字阶跨度 3.861× / 大写 0.71 / 圆角中位 15px / blur 3.833 / 渐变 0.777。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 2px;  --r-md: 30px;  --r-lg: 999px;
/* 字阶众数 */ --fs: 12px, 13px, 14px, 16px, 11px, 18px, 10px;
/* 缓动 */ --ease: cubic-bezier(.4,0,.2,1);  --ease-2: cubic-bezier(.16,1,.3,1);
```

### 版式与组件

- 按钮 / 标签 / 输入框全部药丸形 ≥20px

### 动效

- 缓动：cubic-bezier(.4,0,.2,1), cubic-bezier(.16,1,.3,1), cubic-bezier(.22,1,.36,1), cubic-bezier(.65,0,.35,1)
- 高频关键帧：spin, blink, swiper-preloader-spin, marquee, astroFadeIn, astroFadeInOut, astroFadeOut, astroSlideFromLeft, astroSlideFromRight, astroSlideToLeft, astroSlideToRight, fadeIn

### 品类
sites_of_the_day, interaction-design, 3d, webgl, animation
标签：typography, storytelling, transitions, experimental, clean, microinteractions, minimal

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 亮底，点缀品红/青
来源：Honorable Mention · experimental / colorful

```css
--bg-body: #fff6fd;  --bg-panel: #f0e6fa;
--text-1: #111;  --text-2: #111;
--accent-1: #ff2bd6;  /* 品红 */
--accent-2: #00f0ff;  /* 青 */
--accent-3: #ff7a1a;  /* 橙 */
--neutral: #c9b6dd;
/* 字体 */ Bungee Shade | Bungee | Space Grotesk
/* 圆角 */ 3 / 4 / 4px
/* 缓动 */ cubic-bezier(.2,1.6,.4,1)
/* 关键帧 */ blinkTxt, bounce, eq, lookpop, lookpulse, nudge
```

### 方案 2 — 深底，点缀红/黄绿
来源：Honorable Mention · retro / gestures-interaction / colorful

```css
--bg-body: #0e0e0e;  --bg-panel: #0e0e0e;
--text-1: #f3f4f6;  --text-2: #e5e7eb;
--accent-1: #dc3232;  /* 红 */
--accent-2: #62dd08;  /* 黄绿 */
--accent-3: #12b612;  /* 绿 */
--neutral: #6b7280 #9ca3af;
/* 字体 */ -apple-system | Golos Text | Hobeaux
/* 圆角 */ 6 / 16 / 40px
/* 缓动 */ cubic-bezier(0.33,0.01,0.31,0.99)
/* 关键帧 */ blink, floating, scrollAnim, spin
```

### 方案 3 — 亮底，点缀红
来源：Honorable Mention · typography / video

```css
--bg-body: #f4f4f2;  --bg-panel: #f4f4f4;
--text-1: #191919;  --text-2: #0f0f0e;
--accent-1: #ff3b1d;  /* 红 */
--neutral: #797979 #686868;
/* 字体 */ Suisse | Suisse Mono
/* 圆角 */ 6 / 8 / 8px
/* 缓动 */ cubic-bezier(.16,1,.3,1)
/* 关键帧 */ brand-logo-links, edHeroReveal, edHeroZoom, heroIn, logo-wrapper-left, logoDrift
```

### 方案 4 — 深底，点缀红
来源：Honorable Mention · video / transitions / storytelling

```css
--bg-body: #404040;  --bg-panel: #0a0a0a;
--text-1: #e5e5e5;  --text-2: #fafafa;
--accent-1: #f97066;  /* 红 */
--neutral: #737373 #9ca3af #808285;
/* 字体 */ Instrument Sans | Space Grotesk
/* 圆角 */ 4 / 22 / 28px
/* 缓动 */ cubic-bezier(.4,0,.2,1)
/* 关键帧 */ bookingOverlay, bookingRise, covered-orbit, covered-orbit-counter, focus-in, footerReveal
```

### 方案 5 — 深底，点缀蓝
来源：Honorable Mention · footer-design / minimal

```css
--bg-body: #272727;  --bg-panel: #343434;
--text-1: #fafafa;  --text-2: #c8c8c8;
--accent-1: #2895f7;  /* 蓝 */
--neutral: #a0a0a0 #aaadb0;
/* 字体 */ IBM Plex Mono
/* 圆角 */ 12 / 18 / 24px
/* 缓动 */ cubic-bezier(.34,1.56,.64,1)
/* 关键帧 */ dpm-float, growth-draw, growth-label-in, growth-pop, orbit, scroll
```

### 方案 6 — 亮底，点缀红/红
来源：Honorable Mention · typography / microinteractions

```css
--bg-body: #f6f5f3;  --bg-panel: #e4e1dc;
--text-1: #32373c;  --text-2: #17140f;
--accent-1: #f78da7;  /* 红 */
--accent-2: #cf2e2e;  /* 红 */
--accent-3: #ff6900;  /* 橙 */
--neutral: #abb8c3;
/* 字体 */ NHG Fallback | neue-haas-grotesk-display | Satoshi
/* 圆角 */ 2 / 3 / 3px
/* 缓动 */ cubic-bezier(0.7, 0, 0.2, 1)
/* 关键帧 */ coin-pop, fade-up, feature-float, feature-in, loader-in, slide-wipe
```
