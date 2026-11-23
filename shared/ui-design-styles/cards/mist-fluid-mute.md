# mist-fluid-mute — 中性灰画布 · 流式字号 · 低饱和

> 27 个站聚出的结构原型，6 个获奖。特征：底色亮度 0.246 / 字阶跨度 4.159× / 大写 0.1 / 圆角中位 13px / blur 2.444 / 渐变 0.689。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 2px;  --r-md: 20px;  --r-lg: 999px;
/* 字阶众数 */ --fs: 16px, 14px, 13px, 1rem, 12px, 24px, 20px;
/* 缓动 */ --ease: cubic-bezier(0.34,1.56,0.64,1);  --ease-2: cubic-bezier(0.58,0.01,0.44,1);
```

### 版式与组件


### 动效

- 缓动：cubic-bezier(0.34,1.56,0.64,1), cubic-bezier(0.58,0.01,0.44,1), cubic-bezier(.2,.8,.2,1), cubic-bezier(.625,.05,0,1)
- 高频关键帧：swiper-preloader-spin, logo-list-animA, logo-list-animB, loading, spin, acceleratedCheckoutLoadingSkeleton, shopify-dash, shopify-rotator, btn-draw, spin___S3UuE, indicate, shake

### 品类
animation, nominees, interaction-design, sites_of_the_day, colorful
标签：colorful, storytelling, transitions, typography, microinteractions, minimal, clean

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 亮底，点缀橙/橙
来源：Honorable Mention · minimal / parallax / typography

```css
--bg-body: #fff0ca;  --bg-panel: #ffe3d4;
--text-1: #050505;  --text-2: #131415;
--accent-1: #bc6f45;  /* 橙 */
--accent-2: #964317;  /* 橙 */
/* 字体 */ Lay Grotesk Regular | Inter | EL PACRE Regular
/* 圆角 */ 2 / 2 / 2px
/* 缓动 */ cubic-bezier(0.66,0,0,1)
/* 关键帧 */ casa-pulse, casa-scroll-hint
```

### 方案 2 — 深底，点缀红/红
来源：Honorable Mention · colorful / photo-video

```css
--bg-body: #151010;  --bg-panel: #32373c;
--text-1: #cdcdcd;  --text-2: #eeeeee;
--accent-1: #f78da7;  /* 红 */
--accent-2: #cf2e2e;  /* 红 */
--accent-3: #ff6900;  /* 橙 */
--neutral: #abb8c3;
/* 字体 */ Proxima Nova | Transforma | Transforma Script
/* 圆角 */ 5 / 15 / 20px
/* 缓动 */ cubic-bezier(0.64, -0.48, 0.28, 1.38)
/* 关键帧 */ fade-in, fade-out, hand, rotate-infinite, shaka-pop-left, shaka-pop-right
```

### 方案 3 — 亮底，点缀蓝/绿
来源：Honorable Mention · clean / minimal / photographic

```css
--bg-body: #f3f2f2;  --bg-panel: #f8f8f8;
--text-1: #38302e;  --text-2: #17140f;
--accent-1: #65b2e8;  /* 蓝 */
--accent-2: #66d631;  /* 绿 */
--accent-3: #e1b115;  /* 黄 */
--neutral: #a6a6a5 #88847c #55534e;
/* 字体 */ Heading Font Italic | Heading Font Regular | Heading Font Secondary
/* 圆角 */ 4 / 4 / 4px
/* 关键帧 */ acceleratedCheckoutLoadingSkeleton, favorites-recent-skeleton-pulse, favorites-recent-slide-in, shopify-dash, shopify-rotator, swiper-preloader-spin
```

### 方案 4 — 亮底，点缀红/红
来源：Honorable Mention · experimental / transitions / sound-audio

```css
--bg-body: #f2ede4;  --bg-panel: #e8e2d6;
--text-1: #0b0908;  --text-2: #0b0908;
--accent-1: #ff6b6b;  /* 红 */
--accent-2: #c8503c;  /* 红 */
--neutral: #a39a8f #5a534c;
/* 关键帧 */ bootbreathe, bootturn
```

### 方案 5 — 深底，点缀青/蓝
来源：Honorable Mention · unusual-navigation / transitions / gestures-interaction

```css
--bg-body: #32373c;  --bg-panel: #313131;
--text-1: #dcdcde;  --text-2: #dad0ec;
--accent-1: #00d084;  /* 青 */
--accent-2: #0693e3;  /* 蓝 */
--accent-3: #3858e9;  /* 蓝 */
/* 字体 */ -apple-system
/* 圆角 */ 4 / 4 / 4px
```

### 方案 6 — 深底，点缀青/蓝
来源：Nominee · colorful / typography / transitions

```css
--bg-body: #32373c;  --bg-panel: #313131;
--text-1: #dad0ec;  --text-2: #fafae1;
--accent-1: #00d084;  /* 青 */
--accent-2: #0693e3;  /* 蓝 */
--accent-3: #868eff;  /* 蓝 */
/* 字体 */ Exat-Bold
/* 圆角 */ 3 / 10 / 10px
/* 缓动 */ cubic-bezier(0.34, 1.56, 0.64, 1)
/* 关键帧 */ loading, swiper-preloader-spin
```
