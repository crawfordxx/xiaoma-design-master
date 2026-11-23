# dusk-literary-hard — 中灰深底 · 衬线书卷 · 零圆角

> 132 个站聚出的结构原型，30 个获奖。特征：底色亮度 0.195 / 字阶跨度 4.992× / 大写 0.549 / 圆角中位 3px / blur 3.826 / 渐变 1.149。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 2px;  --r-md: 4px;  --r-lg: 12px;
/* 字阶众数 */ --fs: 14px, 18px, 1rem, 24px, 12px, 1.25rem, 1.5rem;
/* 缓动 */ --ease: cubic-bezier(0.625,0.05,0,1);  --ease-2: cubic-bezier(.625,.05,0,1);
```

### 版式与组件

- 标题衬线，正文可无衬线
- 全部直角，靠 1px 线分隔，不用卡片阴影

### 动效

- 缓动：cubic-bezier(0.625,0.05,0,1), cubic-bezier(.625,.05,0,1), cubic-bezier(.4,0,.2,1), cubic-bezier(.16,1,.3,1)
- 高频关键帧：spin, swiper-preloader-spin, marquee, pulse, acceleratedCheckoutLoadingSkeleton, shopify-dash, shopify-rotator, fadeIn, fadeOut, rotate, sprite, wiggle

### 品类
sites_of_the_day, honorable, microinteractions, interaction-design, typography
标签：typography, clean, transitions, microinteractions, storytelling, photo-video, footer-design

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 亮底，点缀蓝
来源：Honorable Mention · microinteractions / transitions

```css
--bg-body: #fafafa;  --bg-panel: #c8c8c8;
--text-1: #131313;  --text-2: #131313;
--accent-1: #2895f7;  /* 蓝 */
--neutral: #aaadb0;
/* 圆角 */ 3 / 3 / 3px
/* 缓动 */ cubic-bezier(0.35, 1.75, 0.6, 1)
/* 关键帧 */ spin, sprite, wiggle
```

### 方案 2 — 亮底，点缀蓝/橙
来源：Honorable Mention · storytelling / microinteractions

```css
--bg-body: #efeeec;  --bg-panel: #fafafa;
--text-1: #212121;  --text-2: #343434;
--accent-1: #2895f7;  /* 蓝 */
--accent-2: #ff4800;  /* 橙 */
--accent-3: #ff2020;  /* 红 */
--neutral: #717171 #aaadb0 #a8a8a8;
/* 圆角 */ 3 / 3 / 3px
/* 缓动 */ cubic-bezier(.65,.05,0,1)
/* 关键帧 */ eyebrow-blink, rf-appear, rf-flicker, spin
```

### 方案 3 — 深底，点缀蓝/品红
来源：Honorable Mention · transitions / photo-video

```css
--bg-body: #101010;  --bg-panel: #131313;
--text-1: #fafafa;  --text-2: #c8c8c8;
--accent-1: #2895f7;  /* 蓝 */
--accent-2: #ff4cb8;  /* 品红 */
--accent-3: #ff4c24;  /* 红 */
--neutral: #aaadb0 #838383;
/* 圆角 */ 2 / 3 / 3px
/* 缓动 */ cubic-bezier(0.625, 0.05, 0, 1)
/* 关键帧 */ ab-hero-failopen, abLoaderOut, abNavGenShow, abShow, slide, spin
```

### 方案 4 — 亮底，点缀绿/绿
来源：Honorable Mention · fullscreen

```css
--bg-body: #dce4cb;  --bg-panel: #fffef2;
--text-1: #111;  --text-2: #111;
--accent-1: #405c36;  /* 绿 */
--accent-2: #516a43;  /* 绿 */
/* 字体 */ VT323 | Courier New
/* 圆角 */ 2 / 7 / 18px
/* 关键帧 */ boot-cursor-blink, cat-breathe, cat-stack-tumble, pet-tail
```

### 方案 5 — 深底，点缀红/橙
来源：Honorable Mention · clean / minimal

```css
--bg-body: #1c1c1c;  --bg-panel: #1c1c1c;
--text-1: #f3f0ec;  --text-2: #fafafa;
--accent-1: #ff6f6f;  /* 红 */
--accent-2: #f59958;  /* 橙 */
--accent-3: #90715d;  /* 橙 */
--neutral: #686868 #aaadb0;
/* 缓动 */ cubic-bezier(.19, 1, .22, 1)
/* 关键帧 */ footer-wave, hero-wave, icon-pulse, pulse-ring, spin
```

### 方案 6 — 亮底，点缀红/蓝
来源：Honorable Mention · storytelling / photo-video / microinteractions

```css
--bg-body: #efeeec;  --bg-panel: #fafafa;
--text-1: #494341;  --text-2: #312426;
--accent-1: #ff4c24;  /* 红 */
--accent-2: #2895f7;  /* 蓝 */
--accent-3: #9d420a;  /* 橙 */
--neutral: #aaadb0 #9e948a;
/* 圆角 */ 3 / 3 / 3px
/* 缓动 */ cubic-bezier(0.5, 0.5, 0, 1)
/* 关键帧 */ spin
```
