# dusk-mono-soft — 中灰深底 · 等宽工程 · 中小圆角

> 80 个站聚出的结构原型，21 个获奖。特征：底色亮度 0.166 / 字阶跨度 4.373× / 大写 0.63 / 圆角中位 11px / blur 2.35 / 渐变 1.261。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 2px;  --r-md: 12px;  --r-lg: 9999px;
/* 字阶众数 */ --fs: 14px, 12px, 1rem, 16px, 15px, 13px, 1.125rem;
/* 缓动 */ --ease: cubic-bezier(.4,0,.2,1);  --ease-2: cubic-bezier(.16,1,.3,1);
```

### 版式与组件


### 动效

- 缓动：cubic-bezier(.4,0,.2,1), cubic-bezier(.16,1,.3,1), cubic-bezier(.22,1,.36,1), cubic-bezier(0,0,.2,1)
- 高频关键帧：spin, pulse, swiper-preloader-spin, shake, fadeIn, fall, featuredProjectsAllFlash, lisaCursor, lisaDisclaimerFlash, lisaDisclaimerProcedure, lisaLoader, preloaderAppear

### 品类
sites_of_the_day, honorable, microinteractions, typography, storytelling
标签：microinteractions, typography, clean, storytelling, colorful, gallery, experimental

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 亮底，点缀蓝/蓝
来源：Honorable Mention · icons / typography / transitions

```css
--bg-body: #d3d3d3;  --bg-panel: #f0f0f0;
--text-1: #2e2e2e;  --text-2: #4b4b4b;
--accent-1: #216ba5;  /* 蓝 */
--accent-2: #1d5d90;  /* 蓝 */
--neutral: #aeaeae #b3b3b3 #a6a6a6;
/* 字体 */ fontGroteskB
/* 圆角 */ 4 / 12 / 24px
/* 缓动 */ cubic-bezier(.625,.05,0,1)
/* 关键帧 */ HeroMediaBoxReveal, NavMegaMenuReveal, NavRegionSwitcherReveal, NavigationMobileItemReveal, iso-marquee-scroll, logos-marquee-scroll
```

### 方案 2 — 亮底，点缀蓝/蓝
来源：Honorable Mention · minimal / storytelling / colorful

```css
--bg-body: #f3e9da;  --bg-panel: #f5f5f7;
--text-1: #3c3c43;  --text-2: #0b0b0c;
--accent-1: #2f5bea;  /* 蓝 */
--accent-2: #2563eb;  /* 蓝 */
--accent-3: #16a34a;  /* 绿 */
--neutral: #767680 #9ca3af #8e8e93;
/* 字体 */ ui-monospace | Caveat
/* 圆角 */ 10 / 17 / 24px
/* 缓动 */ cubic-bezier(.4,0,.2,1)
/* 关键帧 */ eq, loading, ping, pulse, spin
```

### 方案 3 — 深底，点缀红/红
来源：Honorable Mention · storytelling / photo-video

```css
--bg-body: #1d1d1b;  --bg-panel: #32373c;
--text-1: #f4f2e9;  --text-2: #cdcdcd;
--accent-1: #f78da7;  /* 红 */
--accent-2: #cf2e2e;  /* 红 */
--accent-3: #ff6900;  /* 橙 */
--neutral: #6b6b6b #adadad #abb8c3;
/* 字体 */ ui-monospace | Outfit Bold
/* 圆角 */ 14 / 20 / 24px
/* 缓动 */ cubic-bezier(0.65,0,0.35,1)
/* 关键帧 */ bz-breathe, bz-draw, bz-fill, bz-hero-drop, bz-hero-fade-down, bz-hero-fade-up
```

### 方案 4 — 亮底，点缀红/橙
来源：Honorable Mention · minimal / typography / microinteractions

```css
--bg-body: #e4e4e6;  --bg-panel: #e5e5e5;
--text-1: #070707;  --text-2: #191919;
--accent-1: #ff667f;  /* 红 */
--accent-2: #ff4500;  /* 橙 */
--neutral: #787878 #878787 #525252;
/* 圆角 */ 18 / 22 / 28px
/* 缓动 */ cubic-bezier(.4, 0, .6, 1)
/* 关键帧 */ bounce, pulse
```

### 方案 5 — 深底，点缀紫/红
来源：Honorable Mention · big-background-images / minimal / video

```css
--bg-body: #3b3b3b;  --bg-panel: #1b1b1b;
--text-1: #f5f5f5;  --text-2: #e4e4e4;
--accent-1: #ba73ff;  /* 紫 */
--accent-2: #ff5721;  /* 红 */
--accent-3: #ffb400;  /* 黄 */
--neutral: #9a9a9a #7d7d7d #656565;
/* 字体 */ Neue Helvetica W01 | Helvetica Neue LT Std Condensed
/* 圆角 */ 5 / 10 / 30px
/* 缓动 */ cubic-bezier(.4, 0, .2, 1)
/* 关键帧 */ spin
```

### 方案 6 — 深底，点缀红/绿
来源：Honorable Mention · footer-design / colorful

```css
--bg-body: #0b0b0b;  --bg-panel: #1a1a1a;
--text-1: #f5f5f5;  --text-2: #dadadb;
--accent-1: #ed4a1c;  /* 红 */
--accent-2: #16c847;  /* 绿 */
--accent-3: #ff7ac6;  /* 品红 */
--neutral: #b5b5b5 #aaa9ad #5b5b5b;
/* 圆角 */ 12 / 24 / 36px
/* 缓动 */ cubic-bezier(.34,1.56,.64,1)
/* 关键帧 */ cursor, fill, live, pop, scroll, scroll-px
```
