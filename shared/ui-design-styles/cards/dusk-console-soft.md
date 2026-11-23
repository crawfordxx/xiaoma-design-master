# dusk-console-soft — 中灰深底 · 大写等宽 · 中小圆角

> 64 个站聚出的结构原型，15 个获奖。特征：底色亮度 0.178 / 字阶跨度 4.272× / 大写 0.777 / 圆角中位 4px / blur 5.281 / 渐变 1.089。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 1px;  --r-md: 5px;  --r-lg: 12px;
/* 字阶众数 */ --fs: 14px, 12px, 16px, 1rem, 1.25rem, 18px, 15px;
/* 缓动 */ --ease: cubic-bezier(.4,0,.2,1);  --ease-2: cubic-bezier(.16,1,.3,1);
```

### 版式与组件

- 导航 / 标签 / 按钮全大写，letter-spacing .04–.1em

### 动效

- 缓动：cubic-bezier(.4,0,.2,1), cubic-bezier(.16,1,.3,1), cubic-bezier(.215,.61,.355,1), cubic-bezier(.19,1,.22,1)
- 高频关键帧：spin, pulse, noise, swiper-preloader-spin, marquee, astroFadeIn, astroFadeInOut, astroFadeOut, astroSlideFromLeft, astroSlideFromRight, astroSlideToLeft, astroSlideToRight

### 品类
sites_of_the_day, honorable, 3d, typography, interaction-design
标签：storytelling, typography, microinteractions, experimental, transitions, sound-audio, colorful

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 亮底，点缀橙
来源：Honorable Mention · experimental / storytelling / retro

```css
--bg-body: #f2f2ee;  --bg-panel: #f2f2ee;
--text-1: #0a0b0e;  --text-2: #23262d;
--accent-1: #ff5a00;  /* 橙 */
/* 字体 */ ui-monospace | Space Mono | JetBrains Mono
/* 圆角 */ 4 / 7 / 9px
/* 关键帧 */ schp
```

### 方案 2 — 深底，点缀青/品红
来源：Honorable Mention · typography / transitions / storytelling

```css
--bg-body: #0b0c0e;  --bg-panel: #0b0c0e;
--text-1: #f1f0ea;  --text-2: #e9ecef;
--accent-1: #22d3ee;  /* 青 */
--accent-2: #ff29c4;  /* 品红 */
--accent-3: #0e7490;  /* 青 */
--neutral: #5d6168 #8a9099 #767c85;
/* 字体 */ Söhne | Söhne Mono
/* 圆角 */ 1 / 2 / 2px
/* 缓动 */ cubic-bezier(0.76, 0, 0.24, 1)
/* 关键帧 */ astroFadeIn, astroFadeInOut, astroFadeOut, astroSlideFromLeft, astroSlideFromRight, astroSlideToLeft
```

### 方案 3 — 亮底，点缀红/红
来源：Honorable Mention · typography

```css
--bg-body: #f3efe4;  --bg-panel: #e8e4d8;
--text-1: #0b0f0c;  --text-2: #0b0f0c;
--accent-1: #ff3b3b;  /* 红 */
--accent-2: #ff2d55;  /* 红 */
--accent-3: #1f8f4e;  /* 绿 */
--neutral: #8f867d #8d8a80;
/* 字体 */ OC Blimp | Zombie Punks | Zombie Punks Alt
/* 圆角 */ 1 / 4 / 15px
/* 缓动 */ cubic-bezier(.2,.8,.2,1)
/* 关键帧 */ blink, cue-drop, deck-base, glitch-cyan, glitch-red, head-switch
```

### 方案 4 — 深底，点缀蓝
来源：Honorable Mention · typography / photographic

```css
--bg-body: #333333;  --bg-panel: #1a1a1a;
--text-1: #f2f2f2;  --text-2: #eeeeee;
--accent-1: #007cff;  /* 蓝 */
--neutral: #999999 #4d4d4d #616161;
/* 字体 */ inherit !important | Menlo
/* 圆角 */ 2 / 6 / 8px
/* 缓动 */ cubic-bezier(.4,.4,0,1)
/* 关键帧 */ c-6e1bd60f0bd6584bec25c8ff246d2513-scroll, c-6e1bd60f0bd6584bec25c8ff246d2513-scroll-mini, c-6e1bd60f0bd6584bec25c8ff246d2513-scroll-mobile, c-6e1bd60f0bd6584bec25c8ff246d2513-scroll-small, c-6e1bd60f0bd6584bec25c8ff246d2513-scroll-tablet, c-768fcc38be04d59449c5b9689e20c83d-scroll
```

### 方案 5 — 深底，点缀蓝/红
来源：Honorable Mention · transitions / storytelling

```css
--bg-body: #3a3a3a;  --bg-panel: #2a2a2a;
--text-1: #f5f5f5;  --text-2: #f5f5f5;
--accent-1: #8b7bf7;  /* 蓝 */
--accent-2: #ff6b5b;  /* 红 */
--neutral: #6b6b6b #7a7a7a #b3b3b3;
/* 缓动 */ cubic-bezier(.2,.9,.2,1)
```

### 方案 6 — 亮底，点缀青
来源：Honorable Mention · transitions / storytelling

```css
--bg-body: #f1eee6;  --bg-panel: #ecebea;
--text-1: #171e1e;  --text-2: #191919;
--accent-1: #265d44;  /* 青 */
--neutral: #5a6a6d #5d5d5d;
/* 字体 */ Manrope | RedHatMono
/* 圆角 */ 4 / 10 / 10px
/* 缓动 */ cubic-bezier(.215,.61,.355,1)
```
