# 交互模式库（ui-interactions）

> 风格决定"长什么样"，这里决定"怎么动"。
> 所有关键帧、时长、缓动均从线上成熟产品的真实样式定义中采集，不是猜的。

## 按产品品类选

| 文件 | 适用 | 核心模式 |
|---|---|---|
| [`agent-chat.md`](agent-chat.md) | AI 助手、Agent 工作台、对话式生成 | 消息流、流式输出、工具调用折叠、卡片渲染、任务时间线、甘特排期、命令面板 |
| [`saas-dashboard.md`](saas-dashboard.md) | 仪表盘、监控、部署平台、日志、数据 | 状态灯、指标卡、图表、表格、日志流、流水线、Toast、协作光标 |
| [`creative-mobile.md`](creative-mobile.md) | 设计/编辑工具、画布、视频编辑、移动 App | 工作台布局、滑块、生成进度、画布交互、时间线、页面转场、手势、引导 |

## 使用原则

1. **先匹配品类**：产品是 Agent 对话 → 读 agent-chat；是仪表盘 → saas-dashboard；是编辑器/App → creative-mobile。混合产品（如 Agent + 仪表盘）两个都读。
2. **复用关键帧**：文件里的 `@keyframes` 直接可用，命名已归一化。
3. **时长统一**：同一产品内，同类动效时长一致。参考各文件末尾的速查表。
4. **尊重 `prefers-reduced-motion`**：所有 animation 降到 0.001ms，transition 只留 opacity。
5. **无障碍同步**：`aria-live="polite"` 用于流式输出，`role="status"` 用于状态变化，`role="progressbar"` 用于进度。

## 三条铁律

- **一屏一个主动画事件**：有流式输出就不要再有背景动；有时间线滚动就不要再有卡片入场
- **状态动效必须有**：进行中 / 成功 / 失败 / 等待，四种状态各有对应动效，不能只有 spinner
- **入场有层次**：卡片 stagger 50ms，列表 stagger 30ms，不要全部同时出现

## 来源

采集自 16 个一线 AI 工具、SaaS 平台、创意工具与移动应用的线上样式定义，共 400+ 关键帧，按品类归档，命名已去除哈希前缀。
