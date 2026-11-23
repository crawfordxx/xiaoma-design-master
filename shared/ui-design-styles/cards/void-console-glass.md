# void-console-glass — 深色画布 · 大写等宽 · 毛玻璃

> 31 个站聚出的结构原型，11 个获奖。特征：底色亮度 0.124 / 字阶跨度 4.009× / 大写 0.75 / 圆角中位 10px / blur 14.806 / 渐变 5.094。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 2px;  --r-md: 10px;  --r-lg: 999px;
/* 字阶众数 */ --fs: 12px, 16px, 13px, 14px, 15px, 11px, 1rem;
/* 缓动 */ --ease: cubic-bezier(.22,1,.36,1);  --ease-2: cubic-bezier(.16,1,.3,1);
```

### 版式与组件

- 导航 / 标签 / 按钮全大写，letter-spacing .04–.1em
- 毛玻璃层 blur(15px 上下)，半透明底 + 1px 白 alpha 描边
- 大面积渐变背景 / 光晕，多色叠加

### 动效

- 缓动：cubic-bezier(.22,1,.36,1), cubic-bezier(.16,1,.3,1), cubic-bezier(.4,0,.2,1), cubic-bezier(.65,0,.35,1)
- 高频关键帧：spin, blink, pulse, bounce, fade-up, fadeInUp, modalFadeIn, enter, exit, angle-rotate, animate-in-bottom, animate-in-bottom-left

### 品类
interaction-design, 3d, animation, honorable, storytelling
标签：storytelling, clean, typography, transitions, minimal, experimental, microinteractions

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 亮底，点缀蓝/蓝
来源：Honorable Mention · typography / data-visualization

```css
--bg-body: #dceaf4;  --bg-panel: #dfe6ef;
--text-1: #0b0c0e;  --text-2: #111318;
--accent-1: #87bfff;  /* 蓝 */
--accent-2: #2667ff;  /* 蓝 */
--accent-3: #ff6b70;  /* 红 */
--neutral: #aeb8c6;
/* 圆角 */ 4 / 8 / 22px
/* 缓动 */ cubic-bezier(.16,1,.3,1)
/* 关键帧 */ accordion-down, accordion-up, aurora-a, aurora-b, aurora-c, beam
```

### 方案 2 — 深底，点缀蓝/红
来源：Honorable Mention · clean / parallax

```css
--bg-body: #37474f;  --bg-panel: #161616;
--text-1: #efefef;  --text-2: #dad0ec;
--accent-1: #7986cb;  /* 蓝 */
--accent-2: #d9534f;  /* 红 */
--accent-3: #5cb85c;  /* 绿 */
--neutral: #69727d;
/* 字体 */ Manrope
/* 圆角 */ 2 / 5 / 45px
/* 缓动 */ cubic-bezier(.75,0,.125,1)
/* 关键帧 */ a, eaelAnim-moema-1, eaelAnim-moema-2, eicon-spin, fa-spin, ghost-cursor-rips
```

### 方案 3 — 亮底，点缀蓝/蓝
来源：Honorable Mention · storytelling / parallax

```css
--bg-body: #d0e8ff;  --bg-panel: #c0c0c0;
--text-1: #111;  --text-2: #111;
--accent-1: #1f52f6;  /* 蓝 */
--accent-2: #0a8cff;  /* 蓝 */
--accent-3: #12b876;  /* 青 */
--neutral: #808080;
/* 字体 */ Coolvetica HC | Inter
/* 圆角 */ 1 / 10 / 40px
/* 缓动 */ cubic-bezier(.2, .8, .2, 1)
/* 关键帧 */ blink, os-alarm, os-charge, os-glitch, os-nudge, os-pulse
```

### 方案 4 — 深底，点缀紫/橙
来源：Honorable Mention · minimal / data-visualization

```css
--bg-body: #050606;  --bg-panel: #050606;
--text-1: #f2f3ef;  --text-2: #eceef1;
--accent-1: #906bff;  /* 紫 */
--accent-2: #ff9d45;  /* 橙 */
--neutral: #b5bec8 #91a39b #b9bdb6;
/* 字体 */ Herbik | TWK Lausanne | Terra Entry
/* 圆角 */ 4 / 14 / 28px
/* 缓动 */ cubic-bezier(.16,1,.3,1)
/* 关键帧 */ attente-calque, beta-reveal, caret-dos, earth-arrive, earth-decode, earth-settle
```

### 方案 5 — 亮底，点缀紫/绿
来源：Honorable Mention · experimental / unusual-navigation / transitions

```css
--bg-body: #f4f3ef;  --bg-panel: #f5f5f7;
--text-1: #16161a;  --text-2: #1d1d1f;
--accent-1: #a370ff;  /* 紫 */
--accent-2: #4ade80;  /* 绿 */
/* 圆角 */ 12 / 16 / 18px
/* 缓动 */ cubic-bezier(.16,1,.3,1)
/* 关键帧 */ about-overlay-fade, af-loading-in, af-loading-spin, board-settle, boot-mark-in, case-media-in
```

### 方案 6 — 亮底，点缀蓝/蓝
来源：Honorable Mention · storytelling / microinteractions

```css
--bg-body: #f4f6fb;  --bg-panel: #e1f5fa;
--text-1: #1c1c1c;  --text-2: #141414;
--accent-1: #7ab1fe;  /* 蓝 */
--accent-2: #2b7fff;  /* 蓝 */
--accent-3: #1261eb;  /* 蓝 */
--neutral: #8a8a8a;
/* 字体 */ Inter | DM Sans
/* 圆角 */ 4 / 12 / 24px
/* 缓动 */ cubic-bezier(.22,1,.36,1)
/* 关键帧 */ bento-analytics-module__oWwJFq__appear, bento-analytics-module__oWwJFq__bloom, bento-analytics-module__oWwJFq__bloom-num, bento-analytics-module__oWwJFq__bob, bento-analytics-module__oWwJFq__dimA, bento-analytics-module__oWwJFq__dimB
```
