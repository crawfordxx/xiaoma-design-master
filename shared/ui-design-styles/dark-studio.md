# dark-studio — 近黑画布 · 冰白字 · 一点青

> 内容优先的创作工具美学：界面退成画框，让用户生成的图/视频成为主角。
> 适合：AI 图像/视频生成器、剪辑/设计工具、3D 工具、作品集、影院式产品。

## Tokens

```css
:root {
  /* 画布：近黑带蓝，不是纯黑 */
  --bg-body: #0f0f12;      --bg-panel: #15161a;     --bg-elevated: #171a22;
  --bg-deep: #232324;      --bg-tooltip: #1e1e28;
  /* 文字：冰白系，带蓝调，不用纯白 */
  --text-1: #f5fbff;       --text-2: #cacace;       --text-3: #95959d;   --text-4: #62626d;
  /* 灰阶全走 alpha 不走色相：暗色叠白，亮色叠黑 */
  --white-a4: #ffffff0a;   --white-a8: #ffffff14;   --white-a12: #ffffff1f;
  --white-a20: #ffffff33;  --white-a30: #ffffff4d;  --white-a50: #ffffff80;
  --black-a3: #00000008;   --black-a5: #0000000d;   --black-a7: #00000012;
  /* 品牌青：只做墨水不做墙 */
  --accent: #00cae0;       --accent-hover: #00b1cc; --accent-pressed: #0099b8;
  --accent-a6: rgba(0,202,224,.06);  --accent-a12: rgba(0,202,224,.12);  --accent-a40: rgba(0,202,224,.4);
  /* 商业线用橙，与产品线解耦 */
  --commerce: #ff6f00;     --commerce-hover: #ff6a00;
  /* 字体 */
  --font-cn: "FZYaShiHeiS", "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-en: "Albert Sans", "Montserrat", "Inter", system-ui, sans-serif;
  /* 字阶：14/20 是主力 */
  --fs-title: 36px; --lh-title: 56px;   --fs-h1: 32px; --lh-h1: 48px;
  --fs-h2: 24px;   --lh-h2: 32px;       --fs-h3: 18px; --lh-h3: 24px;
  --fs-body: 14px; --lh-body: 20px;     --fs-body-lg: 16px; --lh-body-lg: 24px;
  --fs-caption: 12px; --lh-caption: 16px; --fs-display: 40px; --lh-display: 110%;
  --fw-regular: 400; --fw-medium: 500; --fw-semibold: 600;
  /* 圆角：卡片大、控件小 */
  --r-tiny: 4px;  --r-sm: 8px;  --r-md: 12px;  --r-lg: 16px;  --r-xl: 24px;  --r-pill: 999px;
  /* 阴影：蓝灰基调，三层弥散 */
  --shadow-sm: 0 2px 8px rgba(0,0,0,.06);
  --shadow-md: 0 8px 24px rgba(0,0,0,.08);
  --shadow-card: 0 18.5px 100.6px rgba(0,0,0,.04), 0 8.7px 37.3px rgba(0,0,0,.015), 0 3.3px 13.2px rgba(0,0,0,.003);
  --shadow-blue: 0 8px 24px rgba(31,66,102,.16);
  --ring: 0 0 0 2px rgba(0,193,205,.2);
  /* 动效：标准曲线几乎无过冲，弹性只给生成时刻 */
  --ease-standard: cubic-bezier(.34,.69,.1,1);
  --ease-spring: cubic-bezier(.3,1.3,.3,1);
  /* 间距 4px 网格 */
  --sp-1: 4px; --sp-2: 8px; --sp-3: 12px; --sp-4: 16px; --sp-5: 20px; --sp-6: 24px; --sp-8: 32px;
  --content-max: 1320px;
}
```

## 组件基调

| 组件 | 规格 |
|---|---|
| 主按钮 | **近黑底** `#0f0f12`（不是青！）→ hover `#24272c`，字 `#f5fbff` 14/500，高 48，圆角 10 |
| 次按钮 | 白 alpha 8% 底 → hover 12%，字 `#cacace` |
| 输入框 | 边框白 alpha 7%，focus 换青 + `--ring` |
| 卡片 | `--bg-panel` 底，圆角 16，inset 白描边 `inset 0 0 0 1px #ffffff0a, inset 0 1px #ffffff14` |
| 顶栏 | `backdrop-filter: blur(8px)` + 白 alpha 4% 底 |
| 分割线 | 白 alpha 8% / 4% |
| 标签 | 胶囊 999px，青 alpha 12% 底 + 青字 |

## 版式

- 大标题 36–40px，字重 500，letter-spacing `-.02em`
- 西文小标签：12px 大写，letter-spacing `.3em`，字 `--text-3`
- 正文 14/20，行高 1.43；说明文字 12/16
- 三栏工作台：左工具栏 / 中画布 / 右参数面板；营销页单栏 1320 宽

## 媒体策略（必做）

黑底空荡最致命。**必须生成**：
- Hero 区：1 张 16:9 示例作品拼贴或抽象光效图
- 展示画廊：3–4 张示例作品（不同风格，证明产品能力）
- 有视频能力：6–10 秒循环背景（缓慢流动的光/粒子），放 hero 底层

生图提示词方向：暗背景、单一光源、高对比、电影感、冷色调、体积光。

## 动效

- 页面进出场：`--ease-standard` 250ms
- 生成完成 / 点赞 / 付费成功：`--ease-spring` 300ms
- 图片 hover：scale 1.02 + 阴影 sm→md，150ms
- 一屏最多一个主动画事件

## Icon

Lucide 线性图标，stroke 1.5，颜色 `--text-2`；激活态换 `--accent`。每个功能点必配，不用文字缩写。
