# candy-playground — 电紫 · 荧光绿 · 品红 · 超大圆角

> 创意机构的玩心美学：高饱和撞色、药丸形一切、字体粗而紧。快乐、大胆、不正经。
> 适合：创意机构、活动页、Z 世代品牌、音乐/潮流/实验项目、任何想让人笑的站。

## Tokens

```css
:root {
  /* 画布：极深靛蓝，让荧光色跳出来 */
  --bg-body: #120042;       --bg-panel: #1a0a4f;
  /* 主色：电紫，大面积 */
  --electric: #6630ff;      --electric-deep: #4a1fd9;
  /* 荧光三色：绿、品红、天蓝——每屏最多用两个 */
  --lime: #70f74a;          --magenta: #ff61f8;      --sky: #29daff;
  /* 中性：亮紫灰 */
  --text-1: #f4f0ff;        --text-2: #aca6bd;       --text-3: #5f5f5f;
  /* 字体：展示用黑体，正文用几何无衬线 */
  --font-display: "FKScreamer", "Anton", "Bebas Neue", "Impact", sans-serif;
  --font-body: "Inter", "Outfit", "DM Sans", system-ui, sans-serif;
  /* 字阶：rem 制，超大标题 */
  --fs-hero: 6rem;   --lh-hero: 1;          /* 96px */
  --fs-display: 3.2rem; --lh-display: 110%;  /* 51px */
  --fs-h2: 3rem;     --lh-h2: 120%;         /* 48px */
  --fs-h3: 2.4rem;   --lh-h3: 130%;
  --fs-body: 1.5rem; --lh-body: 1.5;        /* 24px */
  --fs-small: 1.4rem;
  --fw-regular: 400; --fw-medium: 500; --fw-bold: 700;
  --track-display: -.04em;  --track-label: .02em;
  /* 圆角：一切皆药丸 */
  --r-md: 1.2rem;   /* 19px */   --r-lg: 1.6rem;  /* 26px */
  --r-xl: 2.4rem;   /* 38px */   --r-2xl: 3.2rem; /* 51px */
  --r-pill: 999px;
  /* 玻璃 */
  --glass-bg: rgba(255,255,255,.08);  --glass-blur: 24px;  --glass-border: rgba(255,255,255,.16);
  /* 动效：两个弹性曲线，强过冲 */
  --ease-snap: cubic-bezier(.13, .93, .13, .93);      /* 快进慢出，几乎弹 */
  --ease-bounce: cubic-bezier(.87, .07, .87, .07);    /* 强弹 */
  --ease-glide: cubic-bezier(.06, .93, .07, .93);
  /* 间距 */
  --sp-2: 8px; --sp-3: 12px; --sp-4: 16px; --sp-6: 24px; --sp-8: 32px; --sp-12: 48px;
}
```

## 组件基调

| 组件 | 规格 |
|---|---|
| 主按钮 | 荧光绿底 `--lime` + 深紫字，**药丸** 999px，字 24/700 大写，高 64，hover 弹性 scale 1.05 |
| 次按钮 | 玻璃底 + 白 alpha 描边，药丸 |
| 卡片 | 玻璃 `--glass-bg` + `blur(24px)` + 白 alpha 描边，圆角 38px（`--r-xl`），hover 换荧光描边 |
| 标签 | 药丸，荧光实色底，深紫字，大写 |
| 输入框 | 玻璃底，药丸，字 24 |
| 导航 | 悬浮玻璃药丸条，居中或右上 |

## 版式

- hero 标题 96px，字重 700，字距 `-.04em`，行高 1，可跨行错位
- 正文 24px，比常规大一号——整站字号整体放大
- 一屏两个荧光色封顶，紫色是底不算
- 元素可倾斜、旋转 2–5°、重叠
- 大量留白，但留白里放小装饰（圆点、星号、几何）

## 媒体策略（必做）

玩心风格靠视觉堆出来。**必须生成**：
- hero：1 张 3D 渲染风主视觉（软糖质感/金属流体/抽象几何，荧光配色）
- 3–4 个 3D 小元素（球、环、星、笑脸），透明背景 PNG，散布页面
- 有条件：6–8 秒循环视频（弹性变形的 3D 物体）

生图提示词方向：3D render, candy colors, glossy plastic, electric purple background, lime green and magenta accents, playful, soft studio lighting, octane render。

## 动效

- 进场：`--ease-snap` 弹入 + 旋转
- hover：scale 1.05 + 轻微旋转，`--ease-bounce`
- 滚动：元素交错进出，`--ease-glide`
- 鼠标跟随：hero 元素轻微跟随光标

## Icon

面性 + 荧光色填充，圆润粗线；或 3D 小图标。容器药丸形，荧光底。敢用笑脸、星星、闪电这种直白符号。
