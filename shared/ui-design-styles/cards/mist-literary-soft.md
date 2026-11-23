# mist-literary-soft — 中性灰画布 · 衬线书卷 · 中小圆角

> 54 个站聚出的结构原型，11 个获奖。特征：底色亮度 0.263 / 字阶跨度 4.946× / 大写 0.68 / 圆角中位 12px / blur 3.296 / 渐变 1.502。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 2px;  --r-md: 8px;  --r-lg: 999px;
/* 字阶众数 */ --fs: 14px, 12px, 16px, 13px, 1rem, 18px, 24px;
/* 缓动 */ --ease: cubic-bezier(.22,1,.36,1);  --ease-2: cubic-bezier(.4,0,.2,1);
```

### 版式与组件

- 标题衬线，正文可无衬线

### 动效

- 缓动：cubic-bezier(.22,1,.36,1), cubic-bezier(.4,0,.2,1), cubic-bezier(.19,1,.22,1), cubic-bezier(.165,.84,.44,1)
- 高频关键帧：spin, blink, swiper-preloader-spin, shake, eq, pulse, animInteraction, arrow-cascade, blink-fade, ripple, shake2, shake3

### 品类
sites_of_the_month, animation, typography, interaction-design, honorable
标签：typography, storytelling, transitions, clean, experimental, minimal, microinteractions

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 亮底，点缀黄绿
来源：Honorable Mention · minimal / typography

```css
--bg-body: #eef0e5;  --bg-panel: #dedfd7;
--text-1: #20221c;  --text-2: #252820;
--accent-1: #4b603c;  /* 黄绿 */
--neutral: #62665b;
/* 圆角 */ 2 / 35 / 40px
/* 关键帧 */ screen-in
```

### 方案 2 — 深底，点缀红
来源：Honorable Mention · infinite-scroll

```css
--bg-body: #0a0a0b;  --bg-panel: #0a0a0b;
--text-1: #f2f2f2;  --text-2: #f2f2f2;
--accent-1: #ff9b92;  /* 红 */
/* 字体 */ Instrument Serif | Inter Tight | Editorial Old Italic
/* 圆角 */ 2 / 12 / 22px
/* 缓动 */ cubic-bezier(0.22, 1, 0.36, 1)
/* 关键帧 */ ld-draw, ld-settle, nudge
```

### 方案 3 — 亮底，点缀红
来源：Honorable Mention · horizontal-layout / minimal / storytelling

```css
--bg-body: #f4ede4;  --bg-panel: #fffdf8;
--text-1: #323325;  --text-2: #2b2d20;
--accent-1: #9a675c;  /* 红 */
--neutral: #b9a59c #bcb8a6 #b7a397;
/* 字体 */ Cormorant
/* 圆角 */ 1 / 6 / 14px
/* 缓动 */ cubic-bezier(.22,1,.36,1)
/* 关键帧 */ walk-cue, walk-cue-slide
```

### 方案 4 — 深底，点缀红
来源：Honorable Mention · experimental

```css
--bg-body: #040404;  --bg-panel: #121212;
--text-1: #d9d9d9;  --text-2: #faf9f6;
--accent-1: #fb5a53;  /* 红 */
--neutral: #727272 #909090 #929292;
/* 字体 */ Inter Tight | Apophis
/* 圆角 */ 2 / 20 / 30px
/* 缓动 */ cubic-bezier(.22,1,.36,1)
/* 关键帧 */ boot-blink, close-icon-turn
```

### 方案 5 — 亮底，点缀蓝/蓝
来源：Honorable Mention · gestures-interaction / unusual-navigation

```css
--bg-body: #f4f2ff;  --bg-panel: #f4f2ff;
--text-1: #111;  --text-2: #111;
--accent-1: #545388;  /* 蓝 */
--accent-2: #0d99ff;  /* 蓝 */
--accent-3: #0a6fc2;  /* 蓝 */
/* 字体 */ Big Shoulders | Melodrama | NameFallback
/* 圆角 */ 2 / 12 / 26px
/* 缓动 */ cubic-bezier(.2,.8,.2,1)
/* 关键帧 */ csspin, ddfloat, ddtwinkle, ddtype, ddwave, drip
```

### 方案 6 — 亮底，点缀绿/橙
来源：Honorable Mention · experimental / sound-audio / storytelling

```css
--bg-body: #ffdcb4;  --bg-panel: #ffebd2;
--text-1: #070506;  --text-2: #0b0b0c;
--accent-1: #7bbf8a;  /* 绿 */
--accent-2: #c8a36a;  /* 橙 */
--accent-3: #b08a50;  /* 橙 */
--neutral: #8a8578;
/* 字体 */ Astakhov Dished Glamour | Caveat
/* 圆角 */ 3 / 14 / 18px
/* 缓动 */ cubic-bezier(.7,0,.2,1)
/* 关键帧 */ barInBottom-57767159, barInTop-57767159, closed-note-5309eaf7, consentIn-1ce469e9, contentIn-1ce469e9, contentIn-69fa7169
```
