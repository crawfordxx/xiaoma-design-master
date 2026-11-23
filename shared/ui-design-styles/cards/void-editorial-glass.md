# void-editorial-glass — 深色画布 · 全大写编辑 · 毛玻璃

> 29 个站聚出的结构原型，8 个获奖。特征：底色亮度 0.132 / 字阶跨度 5.247× / 大写 0.868 / 圆角中位 10px / blur 17.724 / 渐变 5.79。
> 结构和色彩分开定：下面结构规格是簇的共性，调色板是从簇内真实站点各提取一套，任选一套套上去。

## 结构规格（簇共性）

```css
/* 圆角 */ --r-sm: 2px;  --r-md: 8px;  --r-lg: 999px;
/* 字阶众数 */ --fs: 14px, 12px, 15px, 16px, 13px, 11px, 18px;
/* 缓动 */ --ease: cubic-bezier(.23,1,.32,1);  --ease-2: cubic-bezier(.16,1,.3,1);
```

### 版式与组件

- 导航 / 标签 / 按钮全大写，letter-spacing .04–.1em
- 毛玻璃层 blur(18px 上下)，半透明底 + 1px 白 alpha 描边
- 大面积渐变背景 / 光晕，多色叠加

### 动效

- 缓动：cubic-bezier(.23,1,.32,1), cubic-bezier(.16,1,.3,1), cubic-bezier(.22,1,.36,1), cubic-bezier(.2,.7,.2,1)
- 高频关键帧：swiper-preloader-spin, fadeIn, spin, fadeOut, BoatPhoto_innerClipPath__BVFuS, BoatPhoto_mediaScale__LEeXS, BoatPhoto_photoFadeIn__3SD7f, BoatPhoto_wrapperScale__zl0ku, CareersDropdown_select-enter__qI_D4, CareersDropdown_select-exit__06OXs, Checkbox_toggleIn__XwrQz, Footer_parallax__XK28M

### 品类
3d, storytelling, animation, interaction-design, honorable
标签：storytelling, glsl, photo-video, experimental, typography, transitions, infinite-scroll

## 调色板（每套来自簇内一个真实站点）

### 方案 1 — 深底，点缀橙
来源：Honorable Mention · 综合

```css
--bg-body: #050506;  --bg-panel: #1a1a22;
--text-1: #fbf4e6;  --text-2: #f6ebc2;
--accent-1: #c0602e;  /* 橙 */
--neutral: #b9b7a0;
/* 字体 */ Quelia | Manrope
/* 圆角 */ 1 / 2 / 3px
/* 缓动 */ cubic-bezier(.2,.7,.2,1)
/* 关键帧 */ mui-breeze, mui-cat, mui-ch, mui-clear, mui-clearsight, mui-dapple
```

### 方案 2 — 亮底，点缀橙/橙
来源：Honorable Mention · experimental / footer-design / typography

```css
--bg-body: #f9f9f9;  --bg-panel: #e9e6ed;
--text-1: #0a0a0a;  --text-2: #1c1616;
--accent-1: #ad6646;  /* 橙 */
--accent-2: #fb5711;  /* 橙 */
--accent-3: #958e09;  /* 黄 */
--neutral: #8f8f8f #828282 #767676;
/* 圆角 */ 3 / 6 / 12px
/* 缓动 */ cubic-bezier(.23,1,.32,1)
/* 关键帧 */ enigma-auction-pulse, enigma-toast-in, fp-caret, hero-rise, mb-marquee, preloader-lift
```

### 方案 3 — 深底，点缀红
来源：Honorable Mention · gestures-interaction / photo-video / minimal

```css
--bg-body: #0b0b0c;  --bg-panel: #0d0d0d;
--text-1: #ececee;  --text-2: #e9e6df;
--accent-1: #ff7a70;  /* 红 */
/* 字体 */ Bradford | HD Colton Wide | HD Colton
/* 圆角 */ 1 / 5 / 14px
/* 缓动 */ cubic-bezier(.2,.8,.2,1)
/* 关键帧 */ bgswap, capIn, cast, cfFade, cfIn, cfUp
```

### 方案 4 — 深底，点缀紫/红
来源：Honorable Mention · sound-audio / storytelling / typography

```css
--bg-body: #080808;  --bg-panel: #111111;
--text-1: #c9c2da;  --text-2: #f5f5f2;
--accent-1: #bd6cf7;  /* 紫 */
--accent-2: #ff8a7a;  /* 红 */
--neutral: #929292 #626262;
/* 字体 */ Manrope Variable | Manrope Fallback
/* 圆角 */ 2 / 2 / 2px
/* 缓动 */ cubic-bezier(.2,.7,.2,1)
/* 关键帧 */ btn-focus, btn-orbit, btn-spin, clients-run, clients-run-reverse, crawl-shoot
```

### 方案 5 — 亮底，点缀橙/橙
来源：Honorable Mention · transitions / gallery / colorful

```css
--bg-body: #f5f5f7;  --bg-panel: #fff2c9;
--text-1: #1a1a1a;  --text-2: #16161a;
--accent-1: #f05722;  /* 橙 */
--accent-2: #ff8a63;  /* 橙 */
/* 字体 */ PP Neue Montreal
/* 圆角 */ 8 / 14 / 14px
/* 缓动 */ cubic-bezier(.22,1,.36,1)
/* 关键帧 */ bg-drift, hero-lockup-reveal, hero-lockup-wipe, hero-scroll-move, hero-scroll-pulse, loading-card-1
```

### 方案 6 — 深底，点缀蓝/红
来源：Honorable Mention · 综合

```css
--bg-body: #1a1d23;  --bg-panel: #2c2e38;
--text-1: #f2f3f5;  --text-2: #f4f4f4;
--accent-1: #00a1ff;  /* 蓝 */
--accent-2: #ff5151;  /* 红 */
--accent-3: #204ce5;  /* 蓝 */
--neutral: #66717e #a7b2bf #686e77;
/* 字体 */ Magnetik | inherit !important
/* 圆角 */ 2 / 5 / 10px
/* 缓动 */ cubic-bezier(0.51, 0.01, 0.2, 1)
/* 关键帧 */ gfadeIn, gfadeOut, gformLoader, gslideInLeft, gslideInRight, gslideOutLeft
```
