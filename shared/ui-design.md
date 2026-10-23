# UI 设计参考与媒体工具链（ui-design）

> gen-ui 技能的设计资源速查 + 媒体生成路由。模型名只允许出现在本文件与 prompt-library。

---

## 媒体工具链路由（做图/人物/视频，各归各位）

| 需求 | 工具 | 调用方式 |
|---|---|---|
| 网页配图（hero 背景/产品图/装饰图） | **gpt-image-2** | `../../toolkit/gen image --prompt "<提示词>" --ratio 16:9 --tier draft` → 确认后 `--tier final` |
| **人物设计**（需要真人在页面里：头像/团队/用户故事） | **midjourney** | 按 [`character-design.md`](character-design.md) 出角色卡，走 midjourney 通道生成；无通道时降级 gpt-image-2 并告知差异 |
| **场景设计**（概念场景/氛围大图） | **midjourney** | 同上；MJ 的氛围感和艺术性优先，构图确定后文字层后期加 |
| 网页视频（hero 背景视频/产品演示） | **seedance** | `../../toolkit/gen video --prompt "<导演式提示词>" --duration 10 --tier draft` → 确认后 final |
| 网页动画 | **React Motion** | 不用视频模型——DOM 动画用 motion.dev（滚动/进出场/微交互），见 gen-ui Step 5 |
| 3D 场景 | **three.js** | 产品 3D/粒子背景用 three.js 写，不用视频模型替代 |

生成纪律沿用 [`runtime-rules.md`](runtime-rules.md)：draft 先行、final 需确认、批量先报预估。

---

## 设计资源速查（10 个参考源，按环节用）

| 环节 | 资源 | 怎么用 |
|---|---|---|
| **导航栏** | navbar.gallery | 做导航前看 3–5 个：透明转实底/滚动收缩/全屏菜单的构图逻辑，挑与调性匹配的交互模式 |
| **页脚** | footer.design | 做页脚前看：大字页脚/分栏链接/CTA 融合页脚，页脚是被低估的品牌空间 |
| **CTA 转化区** | cta.gallery | 做 CTA 前看：按钮措辞/视觉权重/紧迫感设计的灵感 |
| **布局（Bento 网格）** | bentogrids.com | 内容区默认先想 Bento：日式便当盒式大小错落卡片，信息层级+视觉节奏一举两得 |
| **现成模块** | unsection.com | hero/feature/pricing/testimonial 等区块找可应用模块参考，理解其信息结构后按自己 tokens 重做 |
| **滚动动画** | motion.dev/docs/react-scroll-animations | 写滚动动画前必读：useScroll/useTransform 官方范式，视差和滚动揭示的标准写法 |
| **动画范式** | motion.dev/examples?platform=react | Motion 官方示例库：进出场/手势/layout 动画，直接对着写 |
| **动画提示词** | prompt-motion.com | 用自然语言描述动画意图 → 转 Motion 代码的参考 |
| **微交互细节** | 60fps.design | hover/按压/加载的精致细节标准，追求 60fps 手感 |
| **AI 设计提示词库** | jiro.build | 1200+ 现成设计提示词，卡壳时按场景搜（导航/hero/定价页…） |

**使用原则**：每个大区块动手前先看对应参考源的 2–3 个案例；看构图与交互逻辑，**不抄配色不抄文案**；参考结论要落到自己的 design tokens 上。

---

## awwwards 级品质标准（自检循环的锚）

**四大评审维度**（gen-ui Step 7 的打分依据）：

1. **Design 40%** —— 视觉层级清晰吗？留白是设计还是空旷？排版有节奏吗？第一眼像模板还是有自己的脸？暗色/亮色统一吗？
2. **Usability 30%** —— 首屏 5 秒内能明白这是什么给谁的吗？所有可点的东西看起来可点吗？移动端是真适配还是缩放？空态/加载态处理了吗？
3. **Creativity 20%** —— 有一个让人记住的瞬间吗（独特交互/意外布局/标志性动效）？还是每个区块都"标准实现"？
4. **Content 10%** —— 文案在对受众说话还是自说自话？信息密度舒适吗？有没有占位废话？

**获奖品质的操作性定义**：Design ≥ 9（敢留白、层级毒辣、细节到 1px）、Usability ≥ 9（无一处迟疑）、Creativity ≥ 8（至少一个记忆点）、Content ≥ 8（每句文案都挣了自己的位置）。

**自检方法**：真实跑起来（不是看代码）→ 桌面/移动全页截图 → 逐屏对照四维度找问题 → 问题具体到可执行（"Hero 副标题 16px 在 1080p 下对比度 3.2:1，提到 4.5:1"）→ 修 → 重评。循环最多 3 轮，宁可在第 2 轮收敛也要每轮都真实截图。
