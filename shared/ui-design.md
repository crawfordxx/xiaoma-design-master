# UI 设计资源与媒体路由（ui-design）

> gen-ui / ppt / app 三条线共用的：风格库入口、交互模式库入口、媒体工具链路由、获奖品质标准。
> 模型名只允许出现在本文件与 prompt-library。

---

## 一、先定风格，再动手

做网站 / PPT / App，**Step 2 之前**必须走一遍 [`ui-design-styles/README.md`](ui-design-styles/README.md) 的决策树，锁定一个主风格。

| 风格 | 一句话 | 典型产品 |
|---|---|---|
| [`dark-studio`](ui-design-styles/dark-studio.md) | 近黑画布，冰白字，一点青 | 创作工具、编辑器、AI 生成器、作品集 |
| [`violet-immersive`](ui-design-styles/violet-immersive.md) | 深紫宇宙，3D 漂浮，霓虹点缀 | 沉浸叙事、游戏、WebGL 体验、AI 品牌故事 |
| [`ink-editorial`](ui-design-styles/ink-editorial.md) | 纸白墨黑锈红，全大写，印刷感 | 独立创作者作品集、文化项目、出版社 |
| [`candy-playground`](ui-design-styles/candy-playground.md) | 电紫荧光绿品红，药丸一切 | 创意机构、活动页、Z 世代品牌 |
| [`industrial-mono`](ui-design-styles/industrial-mono.md) | 纯黑国际橙，等宽字，零圆角 | 航天、无人机、机器人、B2B 硬件 |
| [`quiet-luxury`](ui-design-styles/quiet-luxury.md) | 米白炭黑，字小，无圆角 | 建筑、地产、画廊、精品品牌 |

每个风格文件 = 完整 tokens + 组件规格 + 媒体策略 + 动效 + icon 规则。**抄 tokens，不抄形容词。**

用户没说风格 → 按产品品类走决策树，给出推荐 + 一句理由，直接开做（不问"你想要什么风格"）。
用户说了风格词 → 映射到最近的风格文件，保留用户原话作副标题参考。

**PPT 适配**：只借色彩系统 + 字体气质 + 版式密度。动效不适用，改入场层级。
**App 适配**：借色彩/圆角/字阶/文案语气，触控目标 ≥44px，底部导航优先。

---

## 一b、按品类选交互模式

风格定了"长什么样"，交互定"怎么动"。走 [`ui-interactions/README.md`](ui-interactions/README.md)：

| 产品品类 | 模式库 | 核心交互 |
|---|---|---|
| AI 助手 / Agent 工作台 / 对话式生成 | [`agent-chat.md`](ui-interactions/agent-chat.md) | 消息流、流式输出、工具调用折叠、卡片渲染、任务时间线、甘特排期 |
| 仪表盘 / 监控 / 部署 / 日志 / 数据 | [`saas-dashboard.md`](ui-interactions/saas-dashboard.md) | 状态灯、指标卡、图表、表格、日志流、流水线、Toast、协作光标 |
| 设计/编辑工具 / 画布 / 视频编辑 / 移动 App | [`creative-mobile.md`](ui-interactions/creative-mobile.md) | 工作台布局、滑块、生成进度、画布交互、时间线、页面转场、手势 |

混合产品两个都读。关键帧和时长直接复用，不自己发明。

---

## 二、媒体工具链路由（缺就生成，不留占位）

| 需求 | 工具 | 调用 |
|---|---|---|
| 网页配图（hero / 产品图 / 氛围图 / 展示画廊） | **gpt-image-2** | `$S/toolkit/gen image --prompt "<提示词>" --ratio 16:9 --tier draft` → 确认后 `--tier final` |
| **人物**（头像 / 团队 / 用户故事） | **midjourney** | 按 [`character-design.md`](character-design.md) 出角色卡；无通道降级 gpt-image-2 |
| **场景 / 3D 主视觉**（沉浸式 hero、星球、抽象几何） | **midjourney** | 氛围与艺术性优先；文字层后期加 |
| **网页视频**（hero 背景 / 产品演示 / 循环动效） | **seedance** | `$S/toolkit/gen video --prompt "<导演式提示词>" --duration 8 --tier draft` → final |
| 网页 DOM 动画 | **Motion** | 不用视频模型 |
| 3D 交互场景 | **three.js** | 不用视频替代 |

生成纪律沿用 [`runtime-rules.md`](runtime-rules.md)：draft 先行、final 需确认、批量先报预估。

### 主动推媒体，不等用户要

风格越复杂，视觉资产越不能空。交付前对照：

| 风格 | 不生成就是半成品 |
|---|---|
| violet-immersive | hero 3D 场景图 + 3 张章节图，有条件加循环视频 |
| candy-playground | hero 3D 主视觉 + 3–4 个透明小元素，有条件加弹性视频 |
| dark-studio | hero 拼贴图 + 3–4 张示例作品（黑底空荡最致命） |
| quiet-luxury | 1–3 张建筑/空间大图 |
| ink-editorial | 1–2 张胶片质感氛围图 |
| industrial-mono | 1 张产品渲染 |

页面里出现空占位框、灰色方块、`<img src="">`——**必须**生成填充，不能交付。
话术："这个风格靠视觉撑，建议生成一张 hero 背景图和一段 8 秒循环视频，我可以直接出。"——直接建议，不等用户开口。

---

## 三、Icon 铁律：禁用首字母 / 首文字

**绝对禁止**：
- 用产品名首字母做 logo（"X" 方块）
- 用功能名首字做区块图标（"智" "AI" "数"）
- 用 "01" "02" 做步骤图标占位
- 空白方块 / 灰色圆形占位

**必须做到**：
- 每个功能点、每个 Bento 卡片、每个定价档、每个步骤——**都配一个语义图标**
- 来源：Lucide（默认）/ Phosphor / Heroicons，挑形状贴切的，不要硬凑
- 品牌标识用抽象图形（几何 / 笔触 / 负空间），或生成一个
- 风格文件里有 icon 规则（线性/面性/双色/3D），照做
- 实在找不到贴切的图标 → 生成一个与风格同系的，别用文字凑

---

## 四、文案纪律：不摆数据、不列依据、不说废话

**删掉这些**：
- 任何百分比 / 倍数 / 客户数 / 市场排名——"提升 300%"、"服务 500+ 企业"——没人信，还显得廉价
- "致力于 / 赋能 / 打造 / 助力 / 引领 / 一站式 / 全方位"
- "功能强大 / 易于使用 / 灵活 / 高效 / 专业"
- 三段式排比、对仗口号、押韵标语
- "在当今快速发展的数字时代"

**只写这些**：
- 做什么（动词 + 名词，一句话）
- 给谁（具体人群，不是"广大用户"）
- 凭什么不一样（一个具体的差异点，不是"更好"）
- 标题 ≤8 字，副标题 ≤25 字，段落 ≤3 行
- 每句话自问：删掉它页面少了什么？答不出就删

好的例子："把录音变成纪要，发给没来开会的人。" / "给独立开发者的支付工具，不抽成。"
坏的例子："智能高效的会议纪要解决方案，助力企业提升协作效率。"

---

## 五、设计资源速查（按环节用）

| 环节 | 资源 | 怎么用 |
|---|---|---|
| **导航栏** | navbar.gallery | 做导航前看 3–5 个：透明转实底 / 滚动收缩 / 全屏菜单，挑与风格匹配的交互模式 |
| **页脚** | footer.design | 大字页脚 / 分栏链接 / CTA 融合页脚 |
| **CTA** | cta.gallery | 按钮措辞 / 视觉权重 / 紧迫感 |
| **布局** | bentogrids.com | 内容区默认先想 Bento：大小错落卡片，层级 + 节奏 |
| **模块参考** | unsection.com | hero / feature / pricing / testimonial 找信息结构，按自己 tokens 重做 |
| **滚动动画** | motion.dev/docs/react-scroll-animations | useScroll / useTransform 官方范式 |
| **动画范式** | motion.dev/examples?platform=react | 进出场 / 手势 / layout 动画 |
| **动画提示词** | prompt-motion.com | 自然语言 → Motion 代码 |
| **微交互** | 60fps.design | hover / 按压 / 加载的精致细节 |
| **提示词库** | jiro.build | 1200+ 设计提示词，卡壳时按场景搜 |
| **获奖作品** | awwwards.com/websites | 按风格标签（3d / minimal / typography / colorful）筛，看构图与交互，不抄配色 |

**使用原则**：每个大区块动手前看 2–3 个案例；看构图与交互逻辑，**不抄配色不抄文案**；结论落到自己 tokens 上。

---

## 六、获奖品质标准（自检锚）

**四维打分**（gen-ui Step 7 依据）：

1. **Design 40%** —— 层级清晰？留白是设计还是空旷？像模板还是有自己的脸？
2. **Usability 30%** —— 首屏 5 秒明白是什么给谁？可点的东西看起来可点？移动端真适配？
3. **Creativity 20%** —— 有一个让人记住的瞬间？还是每个区块都"标准实现"？
4. **Content 10%** —— 文案在对受众说话？有没有占位废话、数据堆砌？

**及格线**：Design ≥9、Usability ≥9、Creativity ≥8、Content ≥8。

**硬指标先过**（不过不打分）：
- 375px 无横向滚动，触控目标 ≥44px
- 正文对比度 ≥4.5:1，大字 ≥3:1
- 控制台零报错；依赖纪律通过
- 动画尊重 `prefers-reduced-motion`；首屏图有宽高
- **每个功能点都有语义图标，没有首字母/文字占位**
- **没有空占位框，所有视觉位都有真实资产**
- **文案里没有百分比/客户数/形容词堆砌**
- **状态动效四种齐全**（进行中/成功/失败/等待），流式输出有 `aria-live`

**自检方法**：真实跑起来 → 桌面/移动全页截图 → 逐屏对照四维 + 硬指标 → 问题具体到可执行 → 修 → 重评。最多 3 轮。
