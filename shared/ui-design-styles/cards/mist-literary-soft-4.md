# mist-literary-soft-4 — 中性灰画布 · 衬线书卷 · 中小圆角

> 37 个站聚出的结构原型，9 个获奖。特征：底色亮度 0.428 / 字阶跨度 4.856× / 大写 0.56 / 圆角中位 4px / blur 2.081 / 渐变 0.786。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 1px;  --r-md: 5px;  --r-lg: 16px;
/* 字阶众数 */ --fs: 14px, 16px, 13px, 12px, 15px, 10px, 9px;
/* 缓动 */ --ease: cubic-bezier(.32,.94,.6,1);  --ease-2: cubic-bezier(0,0,.2,1);
```

### 版式与组件

- 标题衬线，正文可无衬线

### 动效

- 缓动：cubic-bezier(.32,.94,.6,1), cubic-bezier(0,0,.2,1), cubic-bezier(.25,.46,.45,.94), cubic-bezier(.76,0,.24,1)
- 高频关键帧：bounceAnim, circular-spin-3b1265d4, jitter-subtle, jitter-subtle-rtl, joystick-y-3b1265d4, ken-burns, quick-flick-3b1265d4, shadowAnim, shake1, squishAnim, fadeIn, page-enter

### 品类
honorable, sites_of_the_month, storytelling, sites_of_the_day, animation
标签：clean, storytelling, typography, photo-video, parallax, transitions, microinteractions

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 亮底，点缀红
来源：Honorable Mention · typography / big-background-images / parallax

```css
--bg-body: #f3e5de;  --bg-panel: #d5cac4;
--text-1: #111;  --text-2: #111;
--accent-1: #a3402c;  /* 红 */
/* 字体 */ Gen Interface JP-aa1df9adf44a6d02 | Shippori Mincho-fd992fb70b84b1db | Shippori Mincho-fd992fb70b84b1db fallbac
/* 缓动 */ cubic-bezier(.22, 1, .36, 1)
/* 关键帧 */ sections-nav-dot
```

### 方案 2 — 亮底，点缀绿/黄
来源：Honorable Mention · clean / storytelling

```css
--bg-body: #e3ddd8;  --bg-panel: #fcfbfe;
--text-1: #32373c;  --text-2: #32373c;
--accent-1: #007518;  /* 绿 */
--accent-2: #ffba00;  /* 黄 */
--accent-3: #2ea2cc;  /* 蓝 */
--neutral: #515151 #767676 #abb8c3;
/* 字体 */ neue-haas-unica | ivypresto-headline
/* 圆角 */ 3 / 8 / 20px
/* 缓动 */ cubic-bezier(0.65, 0, 0.35, 1)
/* 关键帧 */ jet-engine-map-spin, jet-engine-spin
```

### 方案 3 — 亮底，点缀蓝
来源：Honorable Mention · photo-video / microinteractions / storytelling

```css
--bg-body: #dbdbdb;  --bg-panel: #cdcdcd;
--text-1: #181513;  --text-2: #181513;
--accent-1: #007aff;  /* 蓝 */
--neutral: #9e9e9e #727272;
/* 字体 */ General Sans Variable | Playfair Display
/* 圆角 */ 2 / 2 / 2px
/* 缓动 */ cubic-bezier(.28,.11,.32,1)
/* 关键帧 */ pulse, pulse-0077d089, pulse-00a2b8b9, pulse-017399b6, pulse-0b039abe, pulse-149ae9ef
```

### 方案 4 — 深底，点缀绿/红
来源：Honorable Mention · typography / video / photo-video

```css
--bg-body: #050505;  --bg-panel: #050505;
--text-1: #f3f0e9;  --text-2: #fdfaf5;
--accent-1: #4cc352;  /* 绿 */
--accent-2: #ff2142;  /* 红 */
/* 字体 */ Noto Serif | Canela Web Thin | Suisse Intl Regular
/* 圆角 */ 20 / 20 / 20px
/* 缓动 */ cubic-bezier(.44,0,.56,1)
/* 关键帧 */ header-timezone-enter, header-timezone-exit
```

### 方案 5 — 亮底，点缀橙
来源：Honorable Mention · sound-audio / storytelling

```css
--bg-body: #eef3fa;  --bg-panel: #f1ebdd;
--text-1: #2a241d;  --text-2: #2a241d;
--accent-1: #5e4e3b;  /* 橙 */
/* 字体 */ Derive Titre | Derive Main
/* 缓动 */ cubic-bezier(.6,.1,.3,1)
/* 关键帧 */ splash-draw, splash-in, splash-ink, splash-line, splash-rise
```

### 方案 6 — 深底，点缀红/品红
来源：Honorable Mention · transitions

```css
--bg-body: #202020;  --bg-panel: #0a0a0a;
--text-1: #efece8;  --text-2: #eae2b7;
--accent-1: #d62828;  /* 红 */
--accent-2: #db5b7f;  /* 品红 */
--accent-3: #a13d27;  /* 红 */
/* 字体 */ Poppins
/* 圆角 */ 4 / 14.5 / 16px
/* 缓动 */ cubic-bezier(.6,0,.2,1)
/* 关键帧 */ accent-in-5d82e9ff, ambient-petal-fall-19a6e7e8, ambient-petal-sway-19a6e7e8, blossom-open-552031a3, bud-open-552031a3, client-title-reveal-b7f8e743
```
