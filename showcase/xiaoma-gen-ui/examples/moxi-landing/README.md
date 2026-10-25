# 墨隙 Moxi · 示例落地页

xiaoma-gen-ui 按技能流程生成的示例站点。产品、数据与引用均为虚构。

```bash
npm install
npm run dev      # 本地开发
npm run build    # 产出 dist/
```

## 结构

```
src/
├── content.ts              # 全站文案，组件只管排版
├── index.css               # design tokens（暗色墨色 + 琥珀光 + 冷蓝引用）
├── components/ui/          # shadcn/ui（Nova 风格）：button / badge / card
└── components/site/        # 区块：Nav → Hero(+DemoCard) → Facts → Bento → Steps → FAQ / CTA / Footer
```

## 技术栈

| 能力 | 用的库 |
|---|---|
| UI 组件 | shadcn/ui（Nova 风格，`components.json` 的 style 为 `base-nova`） |
| 图标 | lucide-react |
| 动画 | motion（`motion/react`），`MotionConfig reducedMotion="user"` |
| 样式 | Tailwind CSS v4，tokens 写在 `index.css` 的 CSS 变量里，经 `@theme inline` 映射 |

页面不需要拖拽、分栏和跨组件状态，所以没装 dnd-kit、react-resizable-panels、Zustand。`tw-animate-css` 是 shadcn 组件自带的进出场样式，不是第二个动画库。
