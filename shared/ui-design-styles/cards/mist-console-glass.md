# mist-console-glass — 中性灰画布 · 大写等宽 · 毛玻璃

> 68 个站聚出的结构原型，15 个获奖。特征：底色亮度 0.26 / 字阶跨度 4.598× / 大写 0.737 / 圆角中位 5px / blur 6.971 / 渐变 2.175。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 2px;  --r-md: 8px;  --r-lg: 9999px;
/* 字阶众数 */ --fs: 14px, 12px, 13px, 15px, 16px, 18px, 1rem;
/* 缓动 */ --ease: cubic-bezier(.4,0,.2,1);  --ease-2: cubic-bezier(.19,1,.22,1);
```

### 版式与组件

- 导航 / 标签 / 按钮全大写，letter-spacing .04–.1em
- 标题衬线，正文可无衬线
- 毛玻璃层 blur(7px 上下)，半透明底 + 1px 白 alpha 描边

### 动效

- 缓动：cubic-bezier(.4,0,.2,1), cubic-bezier(.19,1,.22,1), cubic-bezier(.2,.8,.2,1), cubic-bezier(.22,1,.36,1)
- 高频关键帧：spin, swiper-preloader-spin, pulse, grain, enter, exit, blink, overlay-menu__fade-in-animation, fade-in, ping, shimmer, marquee

### 品类
sites_of_the_day, honorable, interaction-design, typography, microinteractions
标签：typography, transitions, storytelling, microinteractions, clean, experimental, colorful

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 深底，点缀橙/红
来源：Honorable Mention · typography

```css
--bg-body: #1e1e1e;  --bg-panel: #1e1e1e;
--text-1: #f1f1ec;  --text-2: #e3ecff;
--accent-1: #ff7e25;  /* 橙 */
--accent-2: #ff3e24;  /* 红 */
--accent-3: #ffb31b;  /* 黄 */
--neutral: #8e8e8e #9b9b9b #606060;
/* 圆角 */ 3 / 4 / 4px
/* 缓动 */ cubic-bezier(.45,0,.2,1)
/* 关键帧 */ horror-noise-jitter, r808-fill-blink, r808-rotate-hint
```

### 方案 2 — 深底，点缀蓝/橙
来源：Honorable Mention · experimental

```css
--bg-body: #1a1a19;  --bg-panel: #2e2f31;
--text-1: #e5e5e5;  --text-2: #e5e5e5;
--accent-1: #007bc4;  /* 蓝 */
--accent-2: #ff8a3d;  /* 橙 */
--accent-3: #5bb872;  /* 绿 */
--neutral: #6d6a66;
/* 缓动 */ cubic-bezier(.22,1,.36,1)
/* 关键帧 */ call-live-dot-01636bea, error-rise-9aac72a1, fade-in-up-74ee3584, fade-in-up-8c9fb0da, fade-in-up-d15767ac, hire-badge-spin-163802bc
```

### 方案 3 — 深底，点缀青/蓝
来源：Honorable Mention · transitions / big-background-images / infinite-scroll

```css
--bg-body: #313131;  --bg-panel: #313131;
--text-1: #f0f0f0;  --text-2: #dad0ec;
--accent-1: #00d084;  /* 青 */
--accent-2: #0693e3;  /* 蓝 */
--accent-3: #007cba;  /* 蓝 */
--neutral: #abb8c3;
/* 缓动 */ cubic-bezier(.16,1,.3,1)
/* 关键帧 */ jm-pattern-frame-open, overlay-menu__fade-in-animation
```

### 方案 4 — 亮底，点缀红/黄
来源：Honorable Mention · unusual-navigation / microinteractions

```css
--bg-body: #fffdf8;  --bg-panel: #fbf6e9;
--text-1: #4a3d31;  --text-2: #2e2620;
--accent-1: #b2364f;  /* 红 */
--accent-2: #e8b931;  /* 黄 */
--accent-3: #c96b5e;  /* 红 */
/* 字体 */ Caveat
/* 圆角 */ 3 / 6 / 8px
/* 缓动 */ cubic-bezier(.25,1.3,.5,1)
/* 关键帧 */ _cardOpen_120it_1, _chartGrow_120it_1, _chatDot_120it_1, _chatIn_120it_5273, _compareIn_120it_1, _courseIn_120it_1
```

### 方案 5 — 亮底，点缀蓝/蓝
来源：Honorable Mention · typography / transitions

```css
--bg-body: #f6beb1;  --bg-panel: #fafafa;
--text-1: #111;  --text-2: #111;
--accent-1: #838dff;  /* 蓝 */
--accent-2: #3d4bff;  /* 蓝 */
--accent-3: #5c68ff;  /* 蓝 */
/* 字体 */ Figtree Variable | Sometype Mono
/* 圆角 */ 3 / 10 / 18px
/* 缓动 */ cubic-bezier(.25,1,.5,1)
/* 关键帧 */ astroFadeIn, astroFadeInOut, astroFadeOut, astroSlideFromLeft, astroSlideFromRight, astroSlideToLeft
```

### 方案 6 — 亮底，点缀蓝/品红
来源：Honorable Mention · clean / fullscreen / minimal

```css
--bg-body: #fafafa;  --bg-panel: #c8c8c8;
--text-1: #0a0a0a;  --text-2: #2c2c2c;
--accent-1: #2d62ff;  /* 蓝 */
--accent-2: #dd23bb;  /* 品红 */
--accent-3: #269d4e;  /* 绿 */
--neutral: #727272 #aaadb0;
/* 圆角 */ 3 / 3 / 3px
/* 缓动 */ cubic-bezier(.645, .045, .355, 1)
/* 关键帧 */ spin
```
