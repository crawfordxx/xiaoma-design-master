# dusk-editorial-soft — 中灰深底 · 全大写编辑 · 中小圆角

> 68 个站聚出的结构原型，15 个获奖。特征：底色亮度 0.153 / 字阶跨度 4.058× / 大写 0.808 / 圆角中位 9px / blur 4.206 / 渐变 1.481。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 2px;  --r-md: 10px;  --r-lg: 999px;
/* 字阶众数 */ --fs: 14px, 16px, 12px, 13px, 15px, 18px, 20px;
/* 缓动 */ --ease: cubic-bezier(.215,.61,.355,1);  --ease-2: cubic-bezier(.4,0,.2,1);
```

### 版式与组件

- 导航 / 标签 / 按钮全大写，letter-spacing .04–.1em

### 动效

- 缓动：cubic-bezier(.215,.61,.355,1), cubic-bezier(.4,0,.2,1), cubic-bezier(.16,1,.3,1), cubic-bezier(.22,1,.36,1)
- 高频关键帧：spin, pulse, fa-spin, plyr-fade-in, plyr-popup, plyr-progress, fade-out, acceleratedCheckoutLoadingSkeleton, fadeIn, shopify-dash, shopify-rotator, swiper-preloader-spin

### 品类
animation, honorable, 3d, storytelling, sites_of_the_day
标签：storytelling, typography, microinteractions, fullscreen, transitions, clean, colorful

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 深底，点缀红/红
来源：Honorable Mention · minimal / typography / storytelling

```css
--bg-body: #32373c;  --bg-panel: #404044;
--text-1: #cccccc;  --text-2: #f7f7f4;
--accent-1: #f78da7;  /* 红 */
--accent-2: #cf2e2e;  /* 红 */
--accent-3: #ff6900;  /* 橙 */
--neutral: #abb8c3 #babdc4;
/* 缓动 */ cubic-bezier(0.4, 0, 0.2, 1)
/* 关键帧 */ btn-arrow-loop, home-intro-scroll, splide-loading
```

### 方案 2 — 深底，点缀红/红
来源：Honorable Mention · colorful

```css
--bg-body: #32373c;  --bg-panel: #32373c;
--text-1: #efefe3;  --text-2: #edeae0;
--accent-1: #f78da7;  /* 红 */
--accent-2: #cf2e2e;  /* 红 */
--accent-3: #ff6900;  /* 橙 */
--neutral: #abb8c3;
/* 字体 */ Archivo | Barlow Condensed | Source Sans 3
/* 圆角 */ 4 / 16 / 30px
/* 缓动 */ cubic-bezier(.3, 1.8, .5, 1)
/* 关键帧 */ aqui, dish-bob, drip, drop, float, intro-safety
```

### 方案 3 — 深底，点缀蓝/青
来源：Honorable Mention · clean / colorful

```css
--bg-body: #171717;  --bg-panel: #262626;
--text-1: #ebebeb;  --text-2: #fafafa;
--accent-1: #476cff;  /* 蓝 */
--accent-2: #16a779;  /* 青 */
--accent-3: #fb2c36;  /* 红 */
/* 字体 */ Inter | geistPixel
/* 缓动 */ cubic-bezier(.34,1.4,.64,1)
/* 关键帧 */ c15t-ui-enter-EoZFn, c15t-ui-enter-oqaf_, c15t-ui-exit-Yh5ig, c15t-ui-exit-Z4gI_, c15t-ui-fadeIn-moBzd, home-loader-module__8FYZjG__loader-failsafe
```

### 方案 4 — 深底，点缀红/红
来源：Honorable Mention · typography

```css
--bg-body: #1d1d1d;  --bg-panel: #1d1d1d;
--text-1: #f7efdc;  --text-2: #fdfdfd;
--accent-1: #ff819e;  /* 红 */
--accent-2: #f46d8c;  /* 红 */
--accent-3: #ff8562;  /* 红 */
--neutral: #797979 #a2a2a2;
/* 字体 */ Inter Tight
/* 圆角 */ 3 / 30 / 30px
/* 缓动 */ cubic-bezier(.215,.61,.355,1)
/* 关键帧 */ backInDown, backInLeft, backInRight, backInUp, backOutDown, backOutLeft
```

### 方案 5 — 深底，点缀蓝/蓝
来源：Honorable Mention · big-background-images / storytelling

```css
--bg-body: #3d3d3d;  --bg-panel: #1d1d1f;
--text-1: #f5edda;  --text-2: #faf6ec;
--accent-1: #586aea;  /* 蓝 */
--accent-2: #6e5ce6;  /* 蓝 */
--accent-3: #30d158;  /* 绿 */
--neutral: #b8afa8 #9ca3af #6e6e73;
/* 字体 */ Inter | Onest
/* 圆角 */ 2 / 8 / 30px
/* 缓动 */ cubic-bezier(.22,1,.36,1)
/* 关键帧 */ burst-stage-module__mqgODW__ghost, burst-stage-module__mqgODW__ghostEarly, burst-stage-module__mqgODW__outroIn, burst-stage-module__mqgODW__outroOut, burst-stage-module__mqgODW__veil, burst-stage-module__mqgODW__veilHold
```

### 方案 6 — 亮底，点缀橙
来源：Honorable Mention · transitions / storytelling

```css
--bg-body: #f7e8d2;  --bg-panel: #f7e8d2;
--text-1: #111;  --text-2: #111;
--accent-1: #6b4c34;  /* 橙 */
/* 字体 */ Gabarito | Instrument Sans
/* 圆角 */ 2 / 2 / 2px
/* 缓动 */ cubic-bezier(.3,.7,.2,1)
/* 关键帧 */ hero-lift, hero-light, hero-shift, hero-sink, hero-sway-cut, hero-sway-raised
```
