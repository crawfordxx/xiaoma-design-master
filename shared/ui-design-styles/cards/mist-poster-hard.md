# mist-poster-hard — 中性灰画布 · 极端字阶 · 零圆角

> 38 个站聚出的结构原型，2 个获奖。特征：底色亮度 0.554 / 字阶跨度 23.312× / 大写 0.946 / 圆角中位 3px / blur 1.605 / 渐变 0.397。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 2px;  --r-md: 12px;  --r-lg: 999px;
/* 字阶众数 */ --fs: 12px, 16px, 14px, 11px, 3.2rem, 1.8rem, 18px;
/* 缓动 */ --ease: cubic-bezier(.19,1,.22,1);  --ease-2: cubic-bezier(.075,.82,.165,1);
```

### 版式与组件

- 导航 / 标签 / 按钮全大写，letter-spacing .04–.1em
- display ≥64px 与正文 14–16px 并存，跨度 ≥9×，标题字距 -.02em 起
- 全部直角，靠 1px 线分隔，不用卡片阴影

### 动效

- 缓动：cubic-bezier(.19,1,.22,1), cubic-bezier(.075,.82,.165,1), cubic-bezier(.215,.61,.355,1), cubic-bezier(.87,0,.13,1)
- 高频关键帧：spin, blink, tick-458dfb20, animated-shape-module-scss-module__OfwSaG__reset-scale, animated-shape-module-scss-module__OfwSaG__reset-translate, asset-for-project-module-scss-module__lcQrYq__reset-scale, asset-for-project-module-scss-module__lcQrYq__reset-translate, asset-module-scss-module__OXOYYW__reset-scale, asset-module-scss-module__OXOYYW__reset-translate, asset-module-scss-module__fGURiW__reset-scale, asset-module-scss-module__fGURiW__reset-translate, assets-module-scss-module__rFhaxG__reset-scale

### 品类
sites_of_the_day, sites_of_the_month, honorable, 3d, sites_of_the_year
标签：storytelling, colorful, experimental, typography, transitions, unusual-navigation, minimal

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 亮底，点缀蓝/青
来源：Honorable Mention · transitions / storytelling

```css
--bg-body: #f1ede4;  --bg-panel: #f1ede4;
--text-1: #111;  --text-2: #111;
--accent-1: #2a5cff;  /* 蓝 */
--accent-2: #12c3e3;  /* 青 */
--accent-3: #ff7a00;  /* 橙 */
--neutral: #5b5664 #bcb6c6;
/* 字体 */ Hubot Sans | Kalnia | Kelvin Narrow
/* 缓动 */ cubic-bezier(0.2,0.7,0.2,1)
/* 关键帧 */ hero-aura, hero-band, hero-band-in, hero-date, hero-ring, hero-rise
```

### 方案 2 — 深底，点缀黄
来源：Nominee · 综合

```css
--bg-body: #0b0b0a;  --bg-panel: #10100f;
--text-1: #e9e6df;  --text-2: #f7f5ef;
--accent-1: #8f6200;  /* 黄 */
/* 字体 */ gazzetta-variable | helvetica-neue-lt-pro-cond | helvetica-neue-lt-pro
/* 缓动 */ cubic-bezier(.2,.8,.2,1)
/* 关键帧 */ projectsGalleryLoop, projectsImageZoomIn, projectsZoomIn
```

### 方案 3 — 亮底，点缀橙
来源：Nominee · big-background-images / fullscreen / parallax

```css
--bg-body: #d9d9d9;  --bg-panel: #f8f8f8;
--text-1: #181615;  --text-2: #181615;
--accent-1: #e97e00;  /* 橙 */
--neutral: #979696;
/* 字体 */ Louize Display | Beausite Classic
/* 圆角 */ 2 / 4 / 4px
/* 缓动 */ cubic-bezier(.165,.84,.44,1)
/* 关键帧 */ Button-module-scss-module__VLzsWq__loading, DressDiscover-module-scss-module__6gNPWa__enter, DressDiscover-module-scss-module__6gNPWa__leave, EditoMediaCarousel-module-scss-module__Kf5NSa__fade-in, EditoMediaCarousel-module-scss-module__Kf5NSa__fade-out, GalleryMediaGrid-module-scss-module__GiwTpa__fade-in
```

### 方案 4 — 亮底，点缀蓝
来源：Nominee · storytelling

```css
--bg-body: #b7c6d4;  --bg-panel: #e3f4ff;
--text-1: #111;  --text-2: #111;
--accent-1: #5f87b9;  /* 蓝 */
/* 字体 */ HashgraphWeb | NeueMontrealWeb | ParaboleWeb
/* 缓动 */ cubic-bezier(.14,1,.34,1)
/* 关键帧 */ btn-shimmer, dash-reveal, dash-wipe
```

### 方案 5 — 深底，点缀红/红
来源：Nominee · photographic / storytelling

```css
--bg-body: #241f21;  --bg-panel: #524945;
--text-1: #ebe7df;  --text-2: #f2efea;
--accent-1: #f76c46;  /* 红 */
--accent-2: #c73623;  /* 红 */
--accent-3: #bbb95c;  /* 黄 */
--neutral: #988f8b #c3bcbb #7a716d;
/* 字体 */ Zimula
/* 圆角 */ 2 / 12 / 24px
/* 缓动 */ cubic-bezier(.19,1,.22,1)
/* 关键帧 */ imageLoading, leafShadowDrift-4d1adb8d, orbit-068e8402, scrollLabelBob-89fcf866, wishlistTimer-9cce6942
```

### 方案 6 — 亮底，点缀橙/橙
来源：Nominee · transitions / microinteractions

```css
--bg-body: #d2c9a0;  --bg-panel: #d2c9a0;
--text-1: #382c28;  --text-2: #382c28;
--accent-1: #faad17;  /* 橙 */
--accent-2: #dd6900;  /* 橙 */
--accent-3: #794330;  /* 橙 */
/* 字体 */ Garnett | GT America
```
