# mist-poster-mute — 中性灰画布 · 极端字阶 · 低饱和

> 72 个站聚出的结构原型，15 个获奖。特征：底色亮度 0.227 / 字阶跨度 7.55× / 大写 0.878 / 圆角中位 4px / blur 2.306 / 渐变 1.431。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 0px;  --r-md: 4px;  --r-lg: 22px;
/* 字阶众数 */ --fs: 1rem, 16px, 14px, 12px, 13px, 1.6rem, 1.5rem;
/* 缓动 */ --ease: cubic-bezier(.22,1,.36,1);  --ease-2: cubic-bezier(.16,1,.3,1);
```

### 版式与组件

- 导航 / 标签 / 按钮全大写，letter-spacing .04–.1em
- display ≥64px 与正文 14–16px 并存，跨度 ≥9×，标题字距 -.02em 起

### 动效

- 缓动：cubic-bezier(.22,1,.36,1), cubic-bezier(.16,1,.3,1), cubic-bezier(.215,.61,.355,1), cubic-bezier(.19,1,.22,1)
- 高频关键帧：acceleratedCheckoutLoadingSkeleton, marquee, shopify-dash, shopify-rotator, swiper-preloader-spin, pulse, fadeIn, map-player-animation, astroFadeIn, astroFadeInOut, astroFadeOut, astroSlideFromLeft

### 品类
sites_of_the_month, honorable, sites_of_the_day, interaction-design, animation
标签：typography, transitions, gestures-interaction, colorful, storytelling, experimental, clean

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 深底，点缀蓝/蓝
来源：Honorable Mention · microinteractions / fullscreen

```css
--bg-body: #080808;  --bg-panel: #2a2a2a;
--text-1: #f5f5f0;  --text-2: #c9c9c4;
--accent-1: #0d99ff;  /* 蓝 */
--accent-2: #378ef0;  /* 蓝 */
--accent-3: #a996ff;  /* 紫 */
--neutral: #bdbdbd #bdbdb8;
/* 字体 */ Impacta | Delila | Barlow
/* 缓动 */ cubic-bezier(.16,1,.3,1)
/* 关键帧 */ barf, bob, bounce, cell, draw, drip
```

### 方案 2 — 亮底，点缀橙/橙
来源：Honorable Mention · transitions / sound-audio / microinteractions

```css
--bg-body: #f5f5f5;  --bg-panel: #d7d6d5;
--text-1: #0d0b0c;  --text-2: #181618;
--accent-1: #ec651d;  /* 橙 */
--accent-2: #ff7d33;  /* 橙 */
--accent-3: #ff3131;  /* 红 */
--neutral: #999999 #77777a #8d8d90;
/* 字体 */ Humane | Thunder
/* 圆角 */ 2 / 6 / 6px
/* 缓动 */ cubic-bezier(.22,.61,.36,1)
/* 关键帧 */ consenso-entra, dialogo-entra, dialogo-sale, grain-flicker, ingresso-entra, preordine-entra
```

### 方案 3 — 深底，点缀红/橙
来源：Honorable Mention · typography / sound-audio / storytelling

```css
--bg-body: #030303;  --bg-panel: #171717;
--text-1: #d4d4d4;  --text-2: #f5f5f5;
--accent-1: #ed3833;  /* 红 */
--accent-2: #ff5100;  /* 橙 */
--accent-3: #f66f1d;  /* 橙 */
/* 字体 */ PP Monument Extended
/* 圆角 */ 3 / 4 / 8px
/* 缓动 */ cubic-bezier(.33,1,.68,1)
/* 关键帧 */ _coverWinControls_gxvao_1, _coverWinControls_j4o7e_1, _coverWinScale_gxvao_1, _coverWinScale_j4o7e_1, _coverWinSide_gxvao_1, _coverWinSide_j4o7e_1
```

### 方案 4 — 亮底，点缀红/蓝
来源：Honorable Mention · gestures-interaction / transitions

```css
--bg-body: #f0f0f0;  --bg-panel: #fefefe;
--text-1: #363636;  --text-2: #1e1e1e;
--accent-1: #fb2c36;  /* 红 */
--accent-2: #2b7fff;  /* 蓝 */
--accent-3: #ff8f91;  /* 红 */
--neutral: #9c9c9c;
/* 字体 */ APK Systema Regular | APK-Narrative-Regular
/* 圆角 */ 4 / 4 / 4px
/* 缓动 */ cubic-bezier(.51,.92,.24,1)
/* 关键帧 */ skeleton-loading
```

### 方案 5 — 亮底，点缀红/蓝
来源：Honorable Mention · fullscreen / typography / photo-video

```css
--bg-body: #c2e0d3;  --bg-panel: #bfded0;
--text-1: #121212;  --text-2: #121212;
--accent-1: #ea3323;  /* 红 */
--accent-2: #007aff;  /* 蓝 */
--accent-3: #1990c6;  /* 蓝 */
--neutral: #799086;
/* 字体 */ Maison Neue | Ambiant Light Spiky | Ambiant Light Sans
/* 圆角 */ 4 / 8 / 10px
/* 缓动 */ cubic-bezier(.65,.05,.36,1)
/* 关键帧 */ MoveScaleUpEnd, MoveScaleUpEndRed, MoveScaleUpInitial, acceleratedCheckoutLoadingSkeleton, insta-text, insta-text-mobile
```

### 方案 6 — 亮底，点缀红/蓝
来源：Honorable Mention · fullscreen / typography / photo-video

```css
--bg-body: #c2e0d3;  --bg-panel: #bfded0;
--text-1: #121212;  --text-2: #121212;
--accent-1: #ea3323;  /* 红 */
--accent-2: #007aff;  /* 蓝 */
--accent-3: #1990c6;  /* 蓝 */
--neutral: #799086;
/* 字体 */ Maison Neue | Ambiant Light Spiky | Ambiant Light Sans
/* 圆角 */ 4 / 8 / 10px
/* 缓动 */ cubic-bezier(.65,.05,.36,1)
/* 关键帧 */ MoveScaleUpEnd, MoveScaleUpEndRed, MoveScaleUpInitial, acceleratedCheckoutLoadingSkeleton, insta-text, insta-text-mobile
```
