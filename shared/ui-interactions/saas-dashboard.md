# SaaS 数据与状态类：交互模式库

> 适用：仪表盘、监控面板、部署平台、数据分析、日志流、邮件/消息平台。
> 关键帧与时长来自一线 SaaS 与监控平台的线上样式实测。

---

## 1. 状态指示（全局通用）

**状态灯 / 徽章**

```
● 绿 成功    ● 蓝 进行中    ● 黄 警告    ● 红 失败    ● 灰 未开始
```

- 尺寸：6px（行内）/ 8px（卡片）/ 10px（头部）
- 进行中：外环 `ping`（scale 1→1.7，opacity .6→0，1s infinite）+ 中心点 `pulse`（opacity 1→.4）
- 实时脉冲：scale 1→3.5，opacity .5→0，1.5s
- 成功入场：scale .9→1 + opacity 0→1，200ms
- 成功确认：scale 1→1.06→1，300ms，完成时轻轻一弹

**状态文案**：等宽数字，大写小字（11px），letter-spacing `.04em`，搭配图标 CheckCircle2 / Loader2 / AlertTriangle / XCircle / Circle

---

## 2. 数据卡片（指标卡）

```
┌──────────────────────────────────┐
│ 总用户                        ↑  │
│ 12,483                           │
│ ━━╱━━╱━━╱━━╱━━━  +4.2%          │
└──────────────────────────────────┘
```

- 入场：opacity 0 + translateY(4px) → 正常，200ms，stagger 50ms
- 数字：`font-variant-numeric: tabular-nums`，变化时不跳宽度
- 数字滚动：旧值→新值 tween，300ms，ease-out
- 趋势：↑ 绿 ↓ 红（看指标含义），12px
- 迷你图：SVG 120×32，折线用 `stroke-dasharray` + `stroke-dashoffset` 从 0 画到位，600ms
- hover：边框 transparent → `--border`，200ms；**不上浮**（仪表盘卡片不上浮）

---

## 3. 图表

**入场**：
- 折线：路径 `stroke-dashoffset` 总长度 → 0，600ms，ease-out
- 柱状：`scaleY(0) → 1`，`transform-origin: bottom`，stagger 40ms，300ms
- 面积：opacity 0 → 1，400ms，延迟折线 200ms
- 数据点：scale .4→1

**交互**：
- hover 十字线：1px 虚线，`--text-4`，跟随鼠标 x，无延迟
- tooltip：opacity 0 + scale(.98) translateY(5px) → 正常，120ms
- 数据点高亮：scale 1→1.4，中心填白，150ms
- 系列切换：点击图例，对应系列 opacity 1→.2（不消失），200ms

**实时流**：
- 新数据点从右侧推入，整条线 translateX(-1 步长)，300ms linear
- 最新点：`ping` 一次后消失
- y 轴自适应：范围变化时刻度标签 fade 切换

---

## 4. 表格 / 列表

**加载**：
- 骨架屏 shimmer（background-position -200% → 200%，1.5s infinite）
- 行数与真实数据一致，不跳版

**行交互**：
- hover：背景 `--hover`，100ms
- 选中：背景 `accent-a12` + 左侧 2px accent 竖线
- 点击展开详情：height 0 → auto，200ms
- 行内操作按钮：hover 行才显示，opacity 0→1，100ms

**排序**：
- 点击列头，箭头 rotate 0→180deg，150ms
- 行重排：FLIP 动画，每行 250ms，ease-out

**分页**：页码 tabular-nums；切换时内容 opacity .3→1，150ms

**虚拟滚动**：行高固定，overscan 5 行

---

## 5. 日志流 / 实时输出

```
12:03:41.203  INFO   Request received  GET /api/users
12:03:41.215  INFO   Query executed    12ms
12:03:41.220  WARN   Cache miss        key=user:42
12:03:41.238  INFO   Response sent     200  35ms
```

- 等宽字，13px，行高 20px
- 时间戳 `--text-4`，级别按色（INFO 蓝 / WARN 黄 / ERROR 红 / DEBUG 灰）
- 新行入场：opacity .3→1，120ms
- 自动滚动：用户滚到顶部时暂停，显示"↓ N 条新日志"悬浮按钮
- 底部渐隐：`mask-image: linear-gradient(to bottom, black 90%, transparent)`
- 顶部同样渐隐，hover 显示滚动阴影线
- 暂停/恢复：悬浮按钮，`role="button"`

---

## 6. 部署 / 构建流水线

```
●  构建        完成 ✓    1m 23s
│  ├─ Cloning repository      ✓  2s
│  ├─ Installing dependencies ✓  18s
│  ├─ Building                ✓  1m 02s
│  └─ Finalizing              ✓  1s
│
◉  部署        进行中…  ⟳
│  ├─ Uploading assets        ▓▓▓▓▓▓░░░░  60%
│  └─ Assigning domains       等待
│
○  监控        等待
```

- 步骤入场：translateY(2px)→0 + opacity，150ms，stagger
- 子步骤缩进 16px，竖线连接
- 进行中：图标 spin，进度条先 scaleX 入场再按实际进度
- 完成：图标切换 ✓ 弹一下，耗时右侧显示
- 失败：整步抖动，✗ 图标红，子步骤显示错误日志（默认折叠）
- 整体完成：顶部状态轻弹

---

## 7. 通知 / Toast

**入场**：
- 从右下角：translateX(100%) → 0，200ms，ease-out
- 图标：opacity 0 + blur(4px) + scale(.4) → 正常，250ms

**停留**：4 秒，hover 暂停倒计时

**退场**：opacity 1→0 + translateY(8px)，150ms

**堆叠**：新 toast 推旧的上移，每层 250ms

**类型**：success（✓ 绿）/ error（✗ 红）/ info（i 蓝）/ loading（⟳，完成后 morph 成 ✓）

---

## 8. 空状态 / 错误状态

**空状态**：
- 图标 48px，`--text-4`，轻微浮动（translateY 0→8→0，3s infinite）
- 标题 16px medium，说明 14px regular `--text-3`
- CTA 按钮
- 整块 opacity .8，hover 1

**错误**：
- 图标 scale .68→1.04→1
- 错误码等宽字
- "重试"按钮，点击后 loading 态

**骨架屏**：比 spinner 好，保持布局稳定

---

## 9. 命令面板 / 搜索

通用命令面板见 `agent-chat.md` §7。

**仪表盘专属**：
- 时间范围选择器：下拉，选中项背景 `accent-a6`
- 筛选器：多选 chips，选中 accent 底 + scale(.85)→1 入场
- 保存的视图：列表，hover 显示删除

---

## 10. 键盘快捷键

- 全局：`⌘K` 命令面板、`/` 搜索、`g` 然后 `i` 跳收件箱
- `<kbd>` 样式：等宽 11px，边框 1px，圆角 4px，padding 2px 6px
- 按下时：背景闪一下 accent-a12 → transparent，200ms

---

## 11. 多人协作

- 他人光标：彩色小箭头 + 名字标签，位置 lerp 平滑跟随（不瞬移）
- 他人选中：对应元素边框变为该用户颜色，2px，border-in 200ms
- 头像堆叠：右下角，重叠 -8px，hover 展开
- 评论气泡：入场 scale .75→1，150ms
- 实时状态：小点 blink + ping

---

## 12. 时长与缓动速查

| 场景 | 时长 | 曲线 |
|---|---|---|
| hover | 100–150ms | ease-out |
| 状态切换 | 120–200ms | ease-out |
| 卡片入场 | 200ms | `cubic-bezier(.25,1,.5,1)` |
| 面板展开 | 200ms | ease-out |
| 数字 tween | 300ms | ease-out |
| 图表绘制 | 600ms | ease-out |
| Toast | 200ms in / 150ms out | ease-out |
| 失败抖动 | 400ms | steps |
| 循环脉冲 | 1–2s | ease-in-out |
