# 视觉提示词工程（visual-prompts）

> 所有图片服务于内容本身——不是装饰。每张图必须挣得自己的位置。

---

## 提示词五要素（每条生图提示词必须包含）

1. **比例**："3:4 aspect ratio"（小红书竖版）/ "16:9"（内文配图）/ "2.35:1"（公众号封面）
2. **无文字指令**："no text, no letters, no words, no characters, no writing, no captions"——生图模型写字必乱，文字一律后期加
3. **风格描述词 ≥3 个**：与内容调性匹配（cinematic lighting / flat design / hand-drawn / editorial illustration…）
4. **色彩对齐**：与整套内容的主题色系一致
5. **具象场景**：描述具体可视元素，绝不写抽象概念

❌ 坏提示词："一张体现高效工作的图，现代风格"（抽象，无视觉锚点）
✅ 好提示词："深夜书桌前的人，笔记本电脑的蓝光照亮侧脸，旁边三个空咖啡杯，窗外是城市灯光，冷暖光对比，电影感，16:9，no text no letters no words"

---

## 封面三创意方向（每次生成 3 个方向供选择）

**Creative A — 直接冲击**（数据/工具/方法/技术类）
- 核心概念的视觉隐喻，平面设计风
- 提示词模板：`[核心概念的视觉隐喻], flat design, bold [主题色] and white, geometric shapes, minimalist, clean background, no text no letters no words, 2.35:1 aspect ratio, 主体放左侧三分之一留出标题位`

**Creative B — 氛围**（故事/观点/叙事/情感类）
- 唤起文章情绪的场景
- 提示词模板：`[唤起情绪的场景], cinematic lighting, [暖/冷]色调以[主题色]为中心, atmospheric, soft focus, depth of field, no text no letters no words, 2.35:1 aspect ratio, 留出标题叠加位`

**Creative C — 信息可视化**（对比/清单/流程/趋势类）
- 数据或结构的图形化表达
- 提示词模板：`[数据/流程的抽象表达], infographic style, clean layout, [主题色] accent, icons and geometric shapes, white background, professional, no text no letters no words, 2.35:1 aspect ratio`

封面技术规格（公众号）：2.35:1，900×383 起步、1280×544 推荐；中心 1:1 安全区会被裁成缩略图——关键视觉元素居中；<5MB；PNG/JPG（不用 WebP）。

---

## 内文配图决策表

| 段落类型 | 要图吗 | 为什么 |
|---|---|---|
| 数据/证据段 | ✅ | 可视化数据，读者记得住图表 |
| 场景/叙事段 | ✅ | 给读者正在想象的画面 |
| 转折点/高潮 | ✅ | 放大情绪冲击 |
| 纯观点段 | ❌ | 让文字自己发力，图稀释观点 |
| 开头钩子段 | ❌ | 别打断钩子 |
| CTA/结尾段 | ❌ | 保持行动焦点 |
| 过渡段 | ❌ | 桥不是目的地 |

## 布局规则

| 规则 | 规格 |
|---|---|
| 总量 | 每篇 3–6 张 |
| 最小间距 | 图与图 ≥300 字 |
| 最佳节奏 | 约每 600 字一张 |
| 禁区 | 开头段、CTA 段 |
| 格式 | 内文图统一 16:9 |

## 风格一致性四锁（同一篇内容所有图必须）

- **色温**：全暖或全冷（跟主题色）
- **艺术风格**：全摄影或全插画，绝不混
- **复杂度**：全极简或全细节，绝不混
- **光感**：整套一致

---

## 迭代规则（用 gen 的 draft→final 流程）

1. draft 档出 3 个方向各 1 张 → 用户选
2. 选中方向用同一提示词微调（一次只改一个变量：光/构图/色）
3. 文字校验：生成图里若出现乱码文字，加严 no-text 指令重试一次；仍乱则改用无文字版后期加字
4. 满意后 final 档出正式版

## 参考图用法（image-to-image）

提示词里必须写清**保什么、改什么**：
✅ "保持原图人物的五官、姿势、服装和艺术风格不变，把背景换成雨夜街头，霓虹灯反射在湿地面"
❌ "把这张图改好看一点"

保真类需求（证件/头像/翻新）优先声明："Preserve the original subject's recognizable features"。
