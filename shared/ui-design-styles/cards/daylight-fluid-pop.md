# daylight-fluid-pop — 亮色画布 · 流式字号 · 高饱和点缀

> 44 个站聚出的结构原型，8 个获奖。特征：底色亮度 0.702 / 字阶跨度 3.103× / 大写 0.086 / 圆角中位 3px / blur 0.659 / 渐变 0.33。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 2px;  --r-md: 12px;  --r-lg: 30px;
/* 字阶众数 */ --fs: 14px, 16px, 12px, 10px, 1.6rem, 18px, 13px;
/* 缓动 */ --ease: cubic-bezier(.22,1,.36,1);  --ease-2: cubic-bezier(.215,.61,.355,1);
```

### 版式与组件


### 动效

- 缓动：cubic-bezier(.22,1,.36,1), cubic-bezier(.215,.61,.355,1), cubic-bezier(.19,1,.22,1), cubic-bezier(.23,1,.32,1)
- 高频关键帧：spin, dafZtH, fIeEtv, hqtXGH, about-what-in, beat, bounce, fade-reveal, fadeOutUp, filter-shake, line-expand, menu-sprite

### 品类
sites_of_the_day, honorable, webgl, sites_of_the_month, typography
标签：typography, colorful, storytelling, clean, transitions, unusual-navigation, experimental

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 深底，点缀红
来源：Honorable Mention · experimental / transitions / unusual-navigation

```css
--bg-body: #080808;  --bg-panel: #171713;
--text-1: #e7e7e2;  --text-2: #e7e7e2;
--accent-1: #e45a4d;  /* 红 */
--neutral: #77776f #b9b8b2 #84847d;
/* 字体 */ Inter | Zen Kaku Gothic New
/* 圆角 */ 2 / 3 / 4px
/* 缓动 */ cubic-bezier(.22,1,.36,1)
/* 关键帧 */ contact-invalid-shake, fine-grain, loader-sweep
```

### 方案 2 — 深底，点缀橙/橙
来源：Honorable Mention · typography / minimal

```css
--bg-body: #201e1c;  --bg-panel: #201e1c;
--text-1: #e9c79e;  --text-2: #e9c79e;
--accent-1: #ff933c;  /* 橙 */
--accent-2: #6c5942;  /* 橙 */
/* 字体 */ Helixa
/* 圆角 */ 12 / 16 / 16px
/* 缓动 */ cubic-bezier(.22,1,.36,1)
/* 关键帧 */ artocea-hero-copy-enter, artocea-hero-title-enter, client-seamless-drift
```

### 方案 3 — 深底，点缀品红/青
来源：Honorable Mention · typography / microinteractions

```css
--bg-body: #0b0b0a;  --bg-panel: #1b1a17;
--text-1: #f4f2ea;  --text-2: #d9d6cc;
--accent-1: #f29ab1;  /* 品红 */
--accent-2: #4fb3a3;  /* 青 */
--accent-3: #8f66f2;  /* 紫 */
--neutral: #8d8a80;
/* 字体 */ Supermagic | AndreD | Andre JT
/* 圆角 */ 3 / 8 / 8px
/* 缓动 */ cubic-bezier(.7,0,.2,1)
/* 关键帧 */ ahop, drpC, drpS, hop, lgdrop, mpfree
```

### 方案 4 — 深底，点缀红
来源：Honorable Mention · experimental / transitions

```css
--bg-body: #0b0b0b;  --bg-panel: #050505;
--text-1: #f4f2ee;  --text-2: #d8ffd0;
--accent-1: #ff481b;  /* 红 */
/* 字体 */ proxima-nova | elevon | VT323
/* 圆角 */ 2 / 5 / 5px
/* 缓动 */ cubic-bezier(.16, 1, .3, 1)
/* 关键帧 */ drift, eq, fill, iris-nudge, key, knob
```

### 方案 5 — 亮底，点缀青/品红
来源：Honorable Mention · typography / transitions / microinteractions

```css
--bg-body: #f3c6b1;  --bg-panel: #f3c6b1;
--text-1: #111;  --text-2: #111;
--accent-1: #0daa75;  /* 青 */
--accent-2: #f08fc7;  /* 品红 */
/* 字体 */ Poppins Regular | Poppins Black | Poppins Bold
/* 关键帧 */ framer-infinite-logo-marquee, getInTouchSpin, tickerLeft, tickerRight
```

### 方案 6 — 亮底，点缀蓝/紫
来源：Nominee · 综合

```css
--bg-body: #fbfbfb;  --bg-panel: #eeede7;
--text-1: #111;  --text-2: #111;
--accent-1: #7a7ceb;  /* 蓝 */
--accent-2: #9565ff;  /* 紫 */
--accent-3: #ce72f5;  /* 紫 */
--neutral: #787771;
/* 字体 */ Haffer | Season
/* 圆角 */ 2 / 12 / 30px
/* 关键帧 */ empty-rotate, loader-particle-float-a, loader-particle-float-b, loader-particle-float-c, mulShdSpin, rotate
```
