# violet-immersive — 深紫宇宙 · 3D 漂浮 · 霓虹点缀

> 让用户"进入一个世界"的沉浸式 microsite。深紫底、WebGL 场景、字体大而飘。
> 适合：AI 安防叙事、游戏宣传、品牌互动站、产品故事页、WebGL 驱动的任何体验。

## Tokens

```css
:root {
  /* 画布：极深紫黑，比黑更有空间感 */
  --bg-body: #160923;       --bg-panel: #1f0f33;      --bg-elevated: #2a1847;
  /* 文字：暖白，不用冷白 */
  --text-1: #fbfbfb;        --text-2: #d4d2c8;        --text-3: #9a96a8;
  /* 主色：饱和紫，大面积铺，不克制 */
  --violet: #6d2d93;        --violet-deep: #5d3b9b;   --violet-light: #b48eda;
  /* 点缀：电光紫 + 荧光绿，各一处 */
  --neon: #7b19c8;          --lime: #7bf583;          --lavender: #7a7ceb;
  /* 字体：人文字体做标题 + 几何无衬线做正文 */
  --font-display: "Season", "Cormorant", "Playfair Display", serif;
  --font-body: "Haffer", "Outfit", "DM Sans", system-ui, sans-serif;
  /* 字阶：标题大、行高紧 */
  --fs-display: 40px; --lh-display: .9;    --fs-h1: 32px; --lh-h1: 1.1;
  --fs-h2: 22px;     --lh-h2: 1.2;         --fs-body: 16px; --lh-body: 24px;
  --fs-small: 14px;  --lh-small: 18px;
  --fw-regular: 400; --fw-medium: 500;
  /* 圆角：大圆角 + 完整圆，几何感 */
  --r-sm: 4px;  --r-md: 12px;  --r-lg: 16px;  --r-xl: 30px;  --r-full: 50%;
  /* 动效：弹性 + 过冲，漂浮感 */
  --ease-out-back: cubic-bezier(.34, 1.56, .64, 1);
  --ease-in-out-back: cubic-bezier(.68, -.6, .32, 1.6);
  --ease-out-expo: cubic-bezier(.16, 1, .3, 1);
  /* 间距 */
  --sp-2: 8px; --sp-3: 12px; --sp-4: 16px; --sp-6: 24px; --sp-8: 32px;
}
```

## 组件基调

| 组件 | 规格 |
|---|---|
| 主按钮 | 紫底 `--violet` → hover `--neon`，圆角 30px（胶囊偏圆），字白 16/500，高 48 |
| 次按钮 | 透明 + 白 alpha 20% 描边，圆角 30px |
| 卡片 | 玻璃：`rgba(255,255,255,.06)` 底 + `backdrop-blur(16px)` + 白 alpha 12% 描边，圆角 16 |
| 导航 | 悬浮胶囊，圆角 30px，玻璃底 |
| 标签 | 完整圆 `--r-full`，`--lime` 或 `--neon` 实色，小字 |
| 分割 | 不用线，用空间 |

## 版式

- 标题用衬线 display 字体，40–80px，行高 .9–1.1，letter-spacing `-.02em`
- 正文 16/24，字重 500 为主，letter-spacing `-.01em`
- 全屏 hero：WebGL/3D 场景铺满，文字浮在上层，居中或左下
- 滚动叙事：分章节，每章一个"星球"/场景

## 媒体策略（必做）

这是**最需要生成资产**的风格。没有视觉撑不住。
- **必须**：hero 3D 场景图（星球/飞船/抽象几何体，深紫背景 + 体积光）
- **必须**：3 个章节各一张场景图（统一紫色调，不同主体）
- **强烈建议**：6–10 秒循环视频（缓慢旋转的 3D 物体 / 粒子流动）
- 可选：2–3 个小 3D 元素做装饰（用 three.js 或生成 PNG 带透明通道）

生图提示词方向：deep purple cosmos, volumetric lighting, floating geometric object, cinematic, ultra-detailed, dark background, neon rim light。

## 动效

- 进场：`--ease-out-back` 带过冲，元素从下方浮起 + 缩放
- 持续：场景元素缓慢漂浮（y 轴 ±10px，6–8s 循环）
- 滚动：章节切换用 `--ease-in-out-expo`
- 鼠标：hover 放大 1.05，`--ease-out-back`

## Icon

线性 + 双色（紫 + 白），stroke 1.5；或用小 3D 图标（生成）。圆角容器 `--r-full`，紫 alpha 底。
