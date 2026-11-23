# void-fluid-glass — 深色画布 · 流式字号 · 毛玻璃

> 20 个站聚出的结构原型，3 个获奖。特征：底色亮度 0.102 / 字阶跨度 2.696× / 大写 0.202 / 圆角中位 6px / blur 16.45 / 渐变 4.07。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 2px;  --r-md: 8px;  --r-lg: 20px;
/* 字阶众数 */ --fs: 14px, 12px, 16px, 13px, 20px, 1rem, 18px;
/* 缓动 */ --ease: cubic-bezier(.19,1,.22,1);  --ease-2: cubic-bezier(.215,.61,.355,1);
```

### 版式与组件

- 毛玻璃层 blur(16px 上下)，半透明底 + 1px 白 alpha 描边
- 大面积渐变背景 / 光晕，多色叠加

### 动效

- 缓动：cubic-bezier(.19,1,.22,1), cubic-bezier(.215,.61,.355,1), cubic-bezier(.4,0,.2,1), cubic-bezier(.33,1,.68,1)
- 高频关键帧：spin, swiper-preloader-spin, fadeIn, bounce, fade-in, fade-out, plyr-fade-in, scroll, arrow-hover, blinker, bounce-dr, bounce-l

### 品类
colorful, animation, storytelling, illustration, sites_of_the_month
标签：storytelling, clean, colorful, transitions, typography, gallery, microinteractions

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 深底，点缀绿/蓝
来源：Honorable Mention · storytelling

```css
--bg-body: #1e1b18;  --bg-panel: #4c4a45;
--text-1: #efefef;  --text-2: #f1f1f1;
--accent-1: #428445;  /* 绿 */
--accent-2: #2252b5;  /* 蓝 */
--accent-3: #d02e2e;  /* 红 */
--neutral: #b7b7b7 #9b9b9b #adadad;
/* 字体 */ Mona Sans
/* 圆角 */ 4 / 8 / 8px
/* 缓动 */ cubic-bezier(.12,.67,.53,1)
/* 关键帧 */ announcement-bar-animation, announcement-bar-animation-rtl, dash, fadeIn, lds-ring, loader
```

### 方案 2 — 深底，点缀绿/蓝
来源：Honorable Mention · storytelling

```css
--bg-body: #1e1b18;  --bg-panel: #4c4a45;
--text-1: #efefef;  --text-2: #f1f1f1;
--accent-1: #428445;  /* 绿 */
--accent-2: #2252b5;  /* 蓝 */
--accent-3: #d02e2e;  /* 红 */
--neutral: #b7b7b7 #9b9b9b #adadad;
/* 字体 */ Mona Sans
/* 圆角 */ 4 / 8 / 8px
/* 缓动 */ cubic-bezier(.12,.67,.53,1)
/* 关键帧 */ announcement-bar-animation, announcement-bar-animation-rtl, dash, fadeIn, lds-ring, loader
```

### 方案 3 — 亮底，点缀青/蓝
来源：Honorable Mention · experimental / big-background-images / transitions

```css
--bg-body: #f5f5f5;  --bg-panel: #e5e5e5;
--text-1: #1a1a1a;  --text-2: #0c0c0c;
--accent-1: #2bbbdc;  /* 青 */
--accent-2: #0d70ff;  /* 蓝 */
--accent-3: #3290ff;  /* 蓝 */
--neutral: #9c9c9c #6b7280;
/* 字体 */ Host Grotesk Regular | Host Grotesk SemiBold | Host Grotesk Bold
/* 圆角 */ 3 / 6 / 12px
/* 关键帧 */ spin
```

### 方案 4 — 亮底，点缀黄/蓝
来源：Nominee · colorful / transitions / gallery

```css
--bg-body: #f4e9e1;  --bg-panel: #dee2e6;
--text-1: #212529;  --text-2: #313131;
--accent-1: #ffb200;  /* 黄 */
--accent-2: #00b2ff;  /* 蓝 */
--accent-3: #0072e3;  /* 蓝 */
--neutral: #6c757d;
/* 圆角 */ 2 / 10 / 30px
/* 缓动 */ cubic-bezier(.19,1,.22,1)
/* 关键帧 */ arrow-hover, blinker, bounce, bounce-dr, bounce-l, bounce-u
```

### 方案 5 — 亮底，点缀绿/橙
来源：Nominee · flat-design / fullscreen / gallery

```css
--bg-body: #f2f2f2;  --bg-panel: #e1e2e3;
--text-1: #111;  --text-2: #111;
--accent-1: #318b55;  /* 绿 */
--accent-2: #b3916b;  /* 橙 */
--neutral: #b3b2b2 #aeaeae #9a9797;
/* 字体 */ Graphik | Optima
/* 圆角 */ 1 / 7 / 20px
/* 缓动 */ cubic-bezier(.215,.61,.355,1)
/* 关键帧 */ OUckgw, _1OlxlK, _1SjA86, _1XFyPc, _2N6Nz4, _3ACv_q
```

### 方案 6 — 深底，点缀绿/绿
来源：Nominee · fullscreen / transitions / storytelling

```css
--bg-body: #282828;  --bg-panel: #121212;
--text-1: #ffd2d7;  --text-2: #c8e0fc;
--accent-1: #1ed760;  /* 绿 */
--accent-2: #3be477;  /* 绿 */
--accent-3: #1abc54;  /* 绿 */
--neutral: #b3b3b3 #a7a7a7;
/* 字体 */ CircularSp-Deva | CircularSp-Grek | CircularSp-Arab
/* 圆角 */ 2 / 6 / 16px
/* 缓动 */ cubic-bezier(.3,0,.4,1)
/* 关键帧 */ DCT3kOyeCwB0c2uCYEM5, HCNd68NXRpQXOHXmnHDE, HSfIXIsuj4JtQYRrhMHc, JHMAhdPuzplCMmYd5w6p, KkF0lBb1Dz2F8_5F0TwH, KrcVF2B3Oh5E_7U1TQi5
```
