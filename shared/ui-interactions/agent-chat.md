# Agent 对话类：交互模式库

> 适用：AI 助手、Agent 工作台、对话式生成工具、Copilot 类产品。
> 所有关键帧和时长均来自线上产品的真实样式定义，可直接用。

---

## 1. 消息流：用户发出 → Agent 接收

**用户消息入场**
- 用户气泡：opacity 0 → 1，translateY(2px) → 0，140ms，ease-out
- 发送按钮：scale(1) → scale(0.8) → scale(1)，150ms

**Agent "正在思考"**——三种主流写法，按产品调性选一：

A. 跳动点——三个 6px 圆点，错相位

```css
@keyframes dot-bounce {
  0%, 80%, 100% { transform: scale(0.84) translateY(0); opacity: .4; }
  30%           { transform: scale(1.5) translateY(-3px); opacity: 1; }
}
.dot { animation: dot-bounce 1.2s infinite; }
.dot:nth-child(2) { animation-delay: .15s; }
.dot:nth-child(3) { animation-delay: .3s; }
```

B. 文字省略号——用 content 切换

```css
@keyframes dots {
  0% { content: ""; } 25% { content: "."; }
  50% { content: ".."; } 75% { content: "..."; }
}
.thinking::after { content: ""; animation: dots 1.4s steps(1) infinite; }
```

C. 文字流光——"正在分析需求…"几个字上有渐变扫光

```css
.ai-text {
  background: linear-gradient(90deg, var(--text-3) 0%, var(--text-1) 50%, var(--text-3) 100%);
  background-size: 200% 100%;
  -webkit-background-clip: text;
  color: transparent;
  animation: ai-shimmer 2s linear infinite;
}
@keyframes ai-shimmer {
  0% { background-position: 200% center; }
  100% { background-position: -200% center; }
}
```

**光标闪烁**（流式输出时跟随文字）

```css
@keyframes caret-blink { 0%, 70%, 100% { opacity: 1; } 20%, 50% { opacity: 0; } }
.caret {
  display: inline-block; width: 2px; height: 1.1em;
  background: var(--accent); vertical-align: text-bottom;
  animation: caret-blink 1s steps(1) infinite;
}
```

---

## 2. 流式文本输出

逐字 / 逐词出现，不要一次性整段渲染。

- 文本容器：`aria-live="polite"`（不要 assertive）
- 每个新 token 淡入：`opacity .3 → 1`，120ms
- 段落完成后，光标停在末尾闪烁
- Markdown 渲染：代码块出现时先 `height: 0 → auto`（200ms），再内容 fade

**打字效果**（演示用，非真实流式）：

```css
@keyframes keypress { 0% { background: var(--accent-a12); } 100% { background: transparent; } }
.key { animation: keypress .2s ease-out; }
```

---

## 3. 工具调用 / 推理过程（可折叠）

**核心模式：默认折叠 + 可展开 + 状态图标**

```
折叠态（一行）：
┌──────────────────────────────────────────────┐
│ ▸  🔍 搜索了 3 个文件                     1.2s │
└──────────────────────────────────────────────┘

展开态：
┌──────────────────────────────────────────────┐
│ ▾  🔍 搜索了 3 个文件                     1.2s │
│    ├─ src/app/page.tsx                       │
│    ├─ src/components/pricing.tsx             │
│    └─ src/lib/utils.ts                       │
│    找到 "PricingSection" 在第 42 行            │
└──────────────────────────────────────────────┘
```

动效：
- 展开：`height: 0 → auto`，200ms
- 内容淡入：opacity 0 → 1，150ms
- 折叠态箭头：`rotate: -90deg → 0`，200ms

**状态图标**（按阶段）：

| 阶段 | 图标 | 动效 |
|---|---|---|
| 进行中 | 旋转环 | `spin 1s linear infinite` |
| 推理中 | 脉冲点 | `ping`：scale 1→2，opacity .6→0，1s |
| 成功 | ✓ | fill 灰→蓝 300ms；或 clip-path 从左划出 |
| 失败 | ✗ | 环旋转 190° 后碎裂淡出，500ms |

**推理过程文本**（thinking 展开后）：
- 字号小一号（12px），颜色 `--text-3`，等宽或斜体
- 整段 `opacity .7`，hover 提到 1
- 左侧 2px 竖线 `--border` 色

---

## 4. 卡片式回复（结构化输出）

Agent 返回的卡片（代码、表格、图片、文件变更）有固定入场：

| 元素 | 动效 | 时长 |
|---|---|---|
| 卡片 | opacity 0 + translateY(4px) → 正常 | 200ms |
| 小标签 chip | opacity 0 + scale(.85) → 正常 | 150ms |
| 进度条 | scaleX(0) → scaleX(1) | 300ms |
| 状态点 | scale(.4) → scale(1) | 150ms |
| 边框 | border-color transparent → 实色 | 200ms |

**代码块卡片**：

```
┌─ page.tsx                     [复制] [预览] ┐
│ 1  import { Pricing } from ...             │
│ 2  export default function ...             │
│ +3 const tiers = [                         │  ← 新增行
└────────────────────────────────────────────┘
```

- 新增行：背景 `accent-a6`，左边 2px accent 竖线
- 删除行：背景 `red-a6`，文字删除线，opacity .6
- 行号：等宽，`--text-4`
- 复制按钮：hover 才显示；点击后 ✓ 弹一下（scale .8→1.1→1，300ms）

**生成中代码块**——对角线扫光覆盖：

```css
.shimmer-overlay {
  background: linear-gradient(135deg, transparent 40%, var(--white-a8) 50%, transparent 60%);
  animation: regen 1.5s ease-in-out infinite;
}
@keyframes regen {
  0% { transform: translate(-100%, -100%); }
  100% { transform: translate(100%, 100%); }
}
```

**多卡片堆叠**：stagger 入场，每张延迟 60ms

---

## 5. 任务执行时间线（Agent 长任务）

**核心模式：垂直时间线 + 步骤卡片 + 实时状态**

```
  ●  分析需求                     完成 ✓   1.2s
  │
  ●  搜索代码库                   完成 ✓   0.8s
  │   └─ 找到 5 个相关文件
  │
  ◉  生成定价组件                 进行中…  ⟳
  │   ┌──────────────────────────┐
  │   │ ▓▓▓▓▓▓▓▓▓▓▓░░░░░░░  65%  │
  │   └──────────────────────────┘
  │
  ○  运行测试                     等待中
  │
  ○  部署预览                     等待中
```

**状态动效**：
- 完成节点：scale .4→1 后填充实色，✓ 图标弹一下
- 进行中节点：外环 `ping` + 中心点 `pulse`
- 竖线：随进度向下生长 `scaleY(0→1)`，`transform-origin: top`
- 新步骤出现：translateY(2px)→0 + opacity，150ms

**进度条**：

```css
/* 确定进度：宽度直接设 */
.progress-bar { transition: width 300ms ease-out; }

/* 不确定进度：来回扫 */
@keyframes progress {
  0% { transform: scaleX(0); }
  5% { transform: scaleX(.1); }
  100% { transform: scaleX(.95); }
}
```

**步骤耗时**：右侧对齐，等宽数字，`--text-4`

**实时日志区**（可选）：等宽字，新行 opacity .3→1，自动滚动到底，底部渐隐

---

## 6. 任务排期 / 甘特（项目管理）

**核心模式：横向时间轴 + 任务条 + 依赖线**

```
         周一    周二    周三    周四    周五
设计    ▓▓▓▓▓▓▓▓────────────────────────────
              ╲
开发            ╲▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
                              ╲
测试                           ╲▓▓▓▓▓▓▓▓
```

- 任务条：圆角 4–6px，高度 28–32px，颜色按状态（待办 `--text-4` / 进行 `--accent` / 完成 `--success` / 阻塞 `--danger`）
- 拖拽调整：拖动时 `opacity .8` + `scale(1.02)` + shadow-md，松手回弹
- 依赖线：SVG 贝塞尔曲线，1.5px stroke，`--text-4`
- 今日线：1px 竖线，`--danger` 或 `--accent`，顶部小三角
- 任务条内文字：12px，`overflow: hidden; text-overflow: ellipsis`
- 进度填充：任务条内左侧深色区域按比例 scaleX

**看板视图**：
- 卡片拖起：`rotate(2deg) scale(1.03)`，shadow md→lg
- 目标列高亮：背景 `accent-a6`，200ms
- 放下：opacity 0 + scale(.7) → 正常，200ms

**日历排期**：
- 事件块入场：opacity 0 + scale(.85) → 正常
- 拖拽跨天：实时 ghost 预览（opacity .5; border 1px dashed accent）
- 冲突检测：抖动（translateX -6/+5/-4/+3/0，400ms）

---

## 7. 命令面板（⌘K）

- 入场：opacity 0 + translateY(10px) scale(.96) → 正常，150ms，ease-out
- 遮罩：opacity 0→1 + `backdrop-filter: blur(4px)`，150ms
- 结果列表：每项 translateX(-2px)→0，stagger 30ms
- 选中项：背景 `accent-a6`，左侧 2px 竖线，transition 80ms
- 键盘导航时选中项平滑移动（不闪烁）
- 空结果：居中图标 + 文案，opacity .5

---

## 8. 通用缓动与时长

| 场景 | 曲线 | 时长 |
|---|---|---|
| 微交互（hover / 按下） | `cubic-bezier(.4,0,.2,1)` | 150ms |
| 元素入场 | `cubic-bezier(.25,1,.5,1)` | 200ms |
| 弹性（成功 / 点赞） | `cubic-bezier(.34,1.56,.64,1)` | 300ms |
| 面板展开 | `ease-out` | 200ms |
| 大面积转场 | `cubic-bezier(.2,.7,.2,1)` | 300–400ms |
| 状态切换（思考→输出） | linear fade | 120ms |
| 循环（spinner / pulse） | linear / ease-in-out | 1–2s |

**尊重 `prefers-reduced-motion`**：所有 animation 设 `0.001ms`，transition 只保留 opacity。

---

## 9. 无障碍

- 消息流容器：`aria-live="polite"`（不要 assertive，会打断读屏）
- 状态变化：`role="status"`
- 进度：`role="progressbar"` + `aria-valuenow`
- 工具调用折叠：`aria-expanded` + `aria-controls`
- 时间线：`role="list"` + 每步 `role="listitem"`
