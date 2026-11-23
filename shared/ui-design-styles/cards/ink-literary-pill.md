# ink-literary-pill — 深色画布 · 衬线书卷 · 超大圆角

> 30 个站聚出的结构原型，1 个获奖。特征：底色亮度 0.151 / 字阶跨度 4.522× / 大写 0.241 / 圆角中位 19px / blur 4.033 / 渐变 1.01。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 3px;  --r-md: 20px;  --r-lg: 999px;
/* 字阶众数 */ --fs: 14px, 18px, 1rem, 16px, 24px, 12px, 3rem;
/* 缓动 */ --ease: cubic-bezier(.19,1,.22,1);  --ease-2: cubic-bezier(0.22,1,0.36,1);
```

### 版式与组件

- 标题衬线，正文可无衬线
- 按钮 / 标签 / 输入框全部药丸形 ≥20px

### 动效

- 缓动：cubic-bezier(.19,1,.22,1), cubic-bezier(0.22,1,0.36,1), cubic-bezier(.33,1,.68,1), cubic-bezier(.17,.84,.44,1)
- 高频关键帧：spin, translateX, calendly-bouncedelay, gradient-move, in, lab-skeleton, skeleton-shimmer, plyr-fade-in, plyr-popup, plyr-progress, heroLetterPop, heroTitleEntrance

### 品类
sites_of_the_day, clean, typography, minimal, 3d
标签：clean, typography, experimental, transitions, minimal, storytelling, colorful

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 亮底，点缀蓝/蓝
来源：Honorable Mention · colorful

```css
--bg-body: #fafafa;  --bg-panel: #f2f2f2;
--text-1: #111;  --text-2: #111;
--accent-1: #007aff;  /* 蓝 */
--accent-2: #2895f7;  /* 蓝 */
--neutral: #aaadb0;
/* 圆角 */ 8 / 20 / 36px
/* 关键帧 */ spin, swiper-preloader-spin
```

### 方案 2 — 亮底，点缀蓝
来源：Nominee · clean / minimal / typography

```css
--bg-body: #fafafa;  --bg-panel: #c8c8c8;
--text-1: #1f1f1f;  --text-2: #1f1f1f;
--accent-1: #2895f7;  /* 蓝 */
--neutral: #aaadb0 #9e9e9e #747474;
/* 圆角 */ 1 / 10 / 26px
/* 缓动 */ cubic-bezier(0.4, 0, 0.2, 1)
/* 关键帧 */ spin, translateX
```

### 方案 3 — 深底，点缀红/蓝
来源：Nominee · big-background-images / parallax

```css
--bg-body: #08080a;  --bg-panel: #222326;
--text-1: #fafafa;  --text-2: #c8c8c8;
--accent-1: #ff7480;  /* 红 */
--accent-2: #2895f7;  /* 蓝 */
--neutral: #7f808a #b9b9b9 #aaadb0;
/* 圆角 */ 2 / 32 / 42px
/* 缓动 */ cubic-bezier(0.42, 0, 0.58, 1)
/* 关键帧 */ spin
```

### 方案 4 — 深底，点缀红/黄绿
来源：Nominee · clean

```css
--bg-body: #3c3c3c;  --bg-panel: #3c3c3c;
--text-1: #fafafa;  --text-2: #c8c8c8;
--accent-1: #dc5b5b;  /* 红 */
--accent-2: #88c159;  /* 黄绿 */
--accent-3: #2895f7;  /* 蓝 */
--neutral: #aaadb0 #686868;
/* 圆角 */ 3 / 3 / 3px
/* 关键帧 */ spin
```

### 方案 5 — 亮底，点缀红/红
来源：Nominee · clean / typography

```css
--bg-body: #e2e2e2;  --bg-panel: #fafafa;
--text-1: #2a2a2a;  --text-2: #3a3a3a;
--accent-1: #ff4f2a;  /* 红 */
--accent-2: #dc6060;  /* 红 */
--accent-3: #ad60dc;  /* 紫 */
--neutral: #aaadb0;
/* 缓动 */ cubic-bezier(0.22, 1, 0.36, 1)
/* 关键帧 */ calendly-bouncedelay, gradient-move, in, lab-skeleton, skeleton-shimmer, spin
```

### 方案 6 — 深底，点缀蓝/红
来源：Nominee · experimental / unusual-navigation / transitions

```css
--bg-body: #191919;  --bg-panel: #191919;
--text-1: #fdfaf7;  --text-2: #fdfaf7;
--accent-1: #00b2ff;  /* 蓝 */
--accent-2: #d15151;  /* 红 */
--neutral: #787a7f;
/* 字体 */ JetBrains Mono | Signifier | Founders Grotesk
/* 圆角 */ 1 / 4 / 4px
/* 缓动 */ cubic-bezier(.33,1,.68,1)
/* 关键帧 */ plyr-fade-in, plyr-popup, plyr-progress
```
