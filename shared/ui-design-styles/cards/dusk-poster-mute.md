# dusk-poster-mute — 中灰深底 · 极端字阶 · 低饱和

> 117 个站聚出的结构原型，25 个获奖。特征：底色亮度 0.156 / 字阶跨度 6.455× / 大写 0.626 / 圆角中位 4px / blur 3.581 / 渐变 1.188。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 2px;  --r-md: 6px;  --r-lg: 12px;
/* 字阶众数 */ --fs: 14px, 16px, 1rem, 12px, 18px, 1.4rem, 1.2rem;
/* 缓动 */ --ease: cubic-bezier(.4,0,.2,1);  --ease-2: cubic-bezier(.22,1,.36,1);
```

### 版式与组件

- display ≥64px 与正文 14–16px 并存，跨度 ≥9×，标题字距 -.02em 起

### 动效

- 缓动：cubic-bezier(.4,0,.2,1), cubic-bezier(.22,1,.36,1), cubic-bezier(.16,1,.3,1), cubic-bezier(0,0,.2,1)
- 高频关键帧：spin, swiper-preloader-spin, pulse, blink, fadeIn, fadeOut, accordion-down, accordion-up, enter, exit, acceleratedCheckoutLoadingSkeleton, shopify-dash

### 品类
sites_of_the_day, honorable, microinteractions, 3d, webgl
标签：storytelling, clean, microinteractions, typography, experimental, transitions, minimal

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 亮底，点缀橙/蓝
来源：Honorable Mention · transitions / photo-video / big-background-images

```css
--bg-body: #fffdf2;  --bg-panel: #f5f2e5;
--text-1: #212529;  --text-2: #343a40;
--accent-1: #ff9557;  /* 橙 */
--accent-2: #0d6efd;  /* 蓝 */
--accent-3: #dc3545;  /* 红 */
--neutral: #6c757d #6b635c #495057;
/* 字体 */ Moderat | Moderat Extended | Moderat Mono
/* 圆角 */ 4 / 8 / 10px
/* 缓动 */ cubic-bezier(.19,1,.22,1)
```

### 方案 2 — 亮底，点缀黄/红
来源：Honorable Mention · minimal / typography / transitions

```css
--bg-body: #e9e6ed;  --bg-panel: #cfc8d8;
--text-1: #050505;  --text-2: #050505;
--accent-1: #958e09;  /* 黄 */
--accent-2: #d9534f;  /* 红 */
--accent-3: #1e85be;  /* 蓝 */
--neutral: #767676 #515151 #69727d;
/* 字体 */ TikTok Sans | star
/* 圆角 */ 2 / 5 / 8px
/* 缓动 */ cubic-bezier(.18,.82,.16,1)
/* 关键帧 */ bgBreathe, copyIn, eicon-spin, logoFirstIn, logoPulse, spin
```

### 方案 3 — 亮底，点缀红
来源：Honorable Mention · clean / minimal / gallery

```css
--bg-body: #fafafa;  --bg-panel: #f5f5f5;
--text-1: #171717;  --text-2: #262626;
--accent-1: #ff6568;  /* 红 */
--neutral: #737373 #a1a1a1 #525252;
/* 字体 */ sfProDisplay | Geist Mono
/* 圆角 */ 2 / 2 / 2px
/* 缓动 */ cubic-bezier(.22,1,.36,1)
/* 关键帧 */ accordion-down, accordion-up, caret-blink, enter, exit, image-shimmer
```

### 方案 4 — 深底，点缀橙
来源：Honorable Mention · experimental / unusual-navigation / glsl

```css
--bg-body: #151515;  --bg-panel: #303030;
--text-1: #d3d8e2;  --text-2: #b3d9ff;
--accent-1: #957c4b;  /* 橙 */
/* 字体 */ condensed | walsheim
/* 缓动 */ cubic-bezier(.4, 0, .2, 1)
/* 关键帧 */ ntch-shake
```

### 方案 5 — 深底，点缀红
来源：Honorable Mention · experimental / transitions / storytelling

```css
--bg-body: #050505;  --bg-panel: #11100f;
--text-1: #f1eee6;  --text-2: #d8d5cc;
--accent-1: #ff3b12;  /* 红 */
--neutral: #aaa79f #66625b #bbb8b0;
/* 字体 */ Archivo Variable | IBM Plex Mono | archivo
/* 圆角 */ 10 / 10 / 10px
/* 缓动 */ cubic-bezier(.215,.61,.355,1)
/* 关键帧 */ contact-confirmation-arrive, contact-form-arrive, meal-drift, nudge, world-breathe
```

### 方案 6 — 深底，点缀青/蓝
来源：Honorable Mention · 综合

```css
--bg-body: #101214;  --bg-panel: #101214;
--text-1: #ded4e6;  --text-2: #e6dfe4;
--accent-1: #0f7f69;  /* 青 */
--accent-2: #3687ff;  /* 蓝 */
--accent-3: #ff4f36;  /* 红 */
--neutral: #b8a5b8 #544d56 #746a76;
/* 字体 */ KHTeka | Dela Gothic One | KHTekaMono
/* 缓动 */ cubic-bezier(.22,.31,0,1)
/* 关键帧 */ crossRotate-6ed73f98, pixelMotion, pixelMotion2x
```
