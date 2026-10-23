---
name: xiaoma-director
description: 编导分镜与视频出片：用户想做视频时，判定片种，按片种的结构、节奏、镜头语言写出专业分镜表（镜号、时间码、景别角度运镜、画面、台词旁白字幕、音效音乐、转场、叙事目的、片种扩展列），出图前过一道导演审核（节奏机检 + 独立审片，判断每镜秒数拖沓还是过紧），再用用户配置的生图模型（GPT Image、Midjourney 等）给每一镜出分镜图，渲染成可直接发给人的单文件 HTML；配置了视频模型时还能把分镜逐镜生成视频片段并做七维质检（修复走局部修改优先）。覆盖 17 个片种：TVC 广告、品牌宣传片、竖屏短剧、教程、产品宣传片、文旅城市宣传片、微电影、动画短片、知识科普、MG 动画、达人口播带货、纪录片、MV、Vlog、预告片/游戏 PV、片头/开场片、活动纪实。用户说「做个视频」「拍条片子」「出分镜」「分镜表」「分镜脚本」「拍摄脚本」「镜头脚本」「storyboard」「shot list」「帮我策划一条广告/宣传片/短剧/教程」时使用；用户只要单张 3×3 分镜提示词时用 ai-storyboard。
---

# 小马导演（xiaoma-director）

把「我想做个视频」变成一份能拿去拍、能拿去审的分镜表：先定片种，再按片种的规矩写分镜，每一镜配分镜图，最后出一个 HTML。

脚本目录：安装目标下的 `xiaoma-director/scripts`（Claude Code: `~/.claude/skills/xiaoma-director/scripts`；pi: `~/.pi/agent/skills/xiaoma-director/scripts`）（依赖 Python 3.9+、Pillow；出图要先配置生图模型，见下文第 7 步）

## 片种速查

| # | id | 片种 | 判定信号 | 默认时长 · 画幅 |
|---|---|---|---|---|
| 1 | `tvc` | TVC 广告（含公益广告） | 广告片、TVC、15/30 秒、电视/电梯/贴片投放、公益广告 | 15/30s · 16:9 |
| 2 | `brand-film` | 品牌形象宣传片 | 企业宣传片、品牌片、形象片、企业文化、招聘片、周年片 | 60–180s · 16:9 |
| 3 | `short-drama` | 竖屏短剧 | 短剧、红果/抖音短剧、爽剧、霸总、逆袭、单集 | 60–120s · 9:16 |
| 4 | `tutorial` | 教程 / 操作演示 | 教程、教学、怎么用、操作步骤、软件演示、手工 | 1–5min · 16:9 |
| 5 | `product-promo` | 产品宣传片 | 产品片、新品发布视频、功能展示、电商主图视频、开箱质感 | 30–90s · 16:9 |
| 6 | `city-tourism` | 文旅 / 城市宣传片 | 城市宣传片、旅游宣传、景区、古镇、乡村振兴、城市形象 | 60–180s · 16:9 |
| 7 | `micro-film` | 微电影 / 剧情短片 | 微电影、剧情短片、学生作业片、影展短片 | 3–15min · 2.39:1 |
| 8 | `animation` | 动画短片 | 动画、2D/3D 动画短片、绘本动画、剧情动画 | 1–5min · 16:9 |
| 9 | `explainer` | 知识科普 / 解说 | 科普、知识视频、解说、为什么……、原理讲解 | 1–5min · 16:9 |
| 10 | `motion-graphics` | MG 动画 / 数据可视化 | MG、扁平动画、数据可视化、政策解读、流程说明动画 | 30–120s · 16:9 |
| 11 | `creator-ad` | 达人口播 / 带货种草 | 口播、种草、带货、探店、测评、UGC、达人视频 | 15–60s · 9:16 |
| 12 | `documentary` | 纪录片 / 人物纪实 | 纪录片、人物故事、访谈、纪实、非虚构 | 3–30min · 16:9 |
| 13 | `mv` | MV / 音乐短片 | MV、音乐视频、歌曲画面、婚礼 MV | 3–4min · 16:9 |
| 14 | `vlog` | Vlog | vlog、旅行记录、日常记录、一天的生活 | 3–10min · 16:9 |
| 15 | `trailer-pv` | 预告片 / 游戏 PV | 预告片、先导片、游戏 PV、CG 宣传片 | 60–120s · 2.39:1 |
| 16 | `opening-title` | 片头 / 活动开场片 | 片头、开场视频、大会开场、晚会倒计时、栏目包装 | 15–60s · 16:9 |
| 17 | `event-recap` | 发布会 / 活动纪实 | 活动回顾、发布会花絮、赛事集锦、年会记录 | 1–3min · 16:9 |

## 工作流

### 1. 需求门：先定片种

- **用户说清了**（「给咖啡品牌拍条 30 秒广告」）→ 直接匹配，回一句「按 TVC 广告来做，因为……」，进第 2 步。
- **夹在两个片种之间**（「做个产品视频」可能是产品宣传片，也可能是达人带货）→ 只问这一处分歧，给两个选项。
- **完全看不出来** → 用 AskUserQuestion 分两层问：
  1. 先问大类：广告营销（TVC / 产品片 / 品牌片 / 达人带货）· 剧情故事（短剧 / 微电影 / 动画 / MV）· 知识信息（教程 / 科普 / MG）· 纪实记录（纪录片 / Vlog / 活动纪实 / 文旅）；预告片、片头开场从「其他」里接住
  2. 再在大类里选具体片种
  3. 还说不清，问三个问题收敛：片子放在哪播 · 画面主角是真人、产品还是界面 · 核心要交付故事、卖点还是信息。三问后仍定不下，给出最接近的片种和理由，让用户拍板，不硬猜

### 2. 规格补齐

需要：时长、画幅、平台、受众、核心信息、已有素材（产品图、logo、演员、歌曲、文案）。用户给了定稿的旁白、台词或屏幕文字时逐字照用，在 `project.assumptions` 里写明「旁白 / 字幕为用户定稿」；导演审片对这些字只提节奏和画面意见，要删改的标 wontfix 并注明用户定稿。logo 和品牌标识不让模型画，出图留空位、后期用用户的文件合成（见 `references/frame-prompts.md`）。
缺项能合理推断就推断，写进 `project.assumptions`，继续做；只有缺了做不下去的（比如产品是什么）才问。不搞长问卷。

长片种（微电影、纪录片、教程等）全片超过 3 分钟时，默认先做开头 60–90 秒的完整段落，`scope` 设为 `segment`，告诉用户可以接着做后面的段落。

### 3. 读片种卡

只读匹配的那一张：`genres/<id>.md`。它给出结构模板、节奏基准、招牌镜头、扩展列、画风前缀、声音要点和常见坑，这些都按国内外顶尖作品的拉片实测校过。卡末的「顶尖范本」列了这个片种公认的好片子和它们怎么排镜头：先挑一部最接近用户需求的，照它的排法走。需要查术语时读 `references/shot-language.md`。

卡里写了子类型（如竖屏短版、一镜到底、长版）而用户的片子属于它时，把子类型的平均镜长和钩子时限写进 `project.asl`、`project.hook`。

### 4. 写 storyboard.json

字段见 `references/storyboard-schema.md`。顺序：
1. `project` 和 `strategy`：一句话核心 → 节拍（按片种卡的结构模板分配时长）→ 视觉风格、调性、音乐
2. `refs`：跨镜出现的角色、产品、场景
3. `shots`：按节拍逐镜写；每镜先想清楚叙事目的，再定景别、角度、运镜，最后写画面、声音和出图提示词（写法见 `references/frame-prompts.md`）
4. `post` 和 `open_questions`

输出目录默认 `./storyboard/<英文或拼音 slug>/storyboard.json`，用户指定了就按用户的。

### 5. 校验

```bash
python3 $SD/validate.py <dir>/storyboard.json
```
有 ❌ 就改到通过；⚠️ 逐条判断，确有意图的可以保留。

### 6. 导演审核

出图之前审：改秒数、改台词不用重出图，拆镜、并镜、改画面才要补图。

```bash
python3 $SD/review.py <dir>/storyboard.json
```

1. **节奏机检**：按景别、台词、字幕算出每镜的所需下限和拖沓上限，列出偏紧和拖沓的镜头，以及整体快慢、匀速、钩子太晚。偏紧和拖沓要处理：改秒数（总时长不变，在镜头之间挪）、删字、给镜头标 `tempo`（快切 / 停留）、给有动作或要看界面的镜头填 `action_s`；有意为之的写 `pace_note` 说明。退出码 0 才算过
2. **导演审片**：派一个没参与创作的子代理，按 `references/director-review.md` 逐镜审，只给它 storyboard.json、片种卡和机检报告。它判断规则抓不到的问题：重场还是过场、刺激性台词后有没有反应镜、动作做没做完、有没有重复信息、情绪顶点后有没有降温。没有子代理时自审，在 `review.reviewer` 里写「自审」
3. **闭环**：只改被指出的镜头，改完重跑 `validate.py` 和 `review.py`，最多 3 轮。结论写进 `review` 字段（verdict、reviewer、date、summary、rounds、issues）；需要拆镜、并镜的意见标 open，交给用户决定

### 7. 出图

出图模型由用户自己配置，全部通过环境变量：
- **OpenAI 兼容接口**（默认）：GPT Image 或任何兼容网关。`IMAGE_API_KEY`（没设时读 `OPENAI_API_KEY`）、`IMAGE_API_BASE`（默认 `https://api.openai.com`）、`IMAGE_MODEL`（默认 `gpt-image-1`）、`IMAGE_QUALITY`（默认 low）、`IMAGE_SIZES`（standard 只请求三种标准尺寸再裁切；网关支持任意尺寸时用 exact）
- **自定义命令**：Midjourney 等没有标准接口的模型，设 `IMAGE_BACKEND=command` 和 `IMAGE_CMD`（命令模板，占位符 `{prompt}` `{size}` `{aspect}` `{out}` `{refs}`），命令负责把图写到 `{out}`
- `IMAGE_PRICE`：每张图的价格，填了 `--dry-run` 会给预估费用

```bash
python3 $SD/frames.py <dir>/storyboard.json --dry-run   # 先看张数（和预估费用）
python3 $SD/frames.py <dir>/storyboard.json              # 实际出图
```
- 先把张数和预估费用告诉用户；超过 30 张先确认再跑
- 用户还没配置出图模型时，脚本会给出提示；可以先跳过出图，直接渲染不带图的分镜表
- 单张约 1 分钟，带设定图改图约 2–3 分钟；镜头多时放后台跑
- 失败的用 `--only s03,s07` 重出；画面不对也用 `--only` 重出，先改 `frame_prompt` 或 `prompt_prefix`
- 改过分镜后直接重跑即可：脚本在 `frames/.prompts.json` 记着每张图生成时的提示词，提示词变了（包括所挂设定的提示词变了）的镜头会自动重出，没变的跳过。增删镜头导致镜号整体后移时，后面的镜头都会重出

### 7b. 视频出片(可选)

用户要成片且配置了视频模型时走这步(配置见 README「配置视频模型」,路线筛选见 `references/video-pipeline.md`——不是每个片种都该用生成):

```bash
python3 $SD/video_render.py <dir>/storyboard.json            # 干跑:每镜提示词写回 shot.video.prompt
python3 $SD/video_render.py <dir>/storyboard.json --live     # 真出片(默认只出缺的镜头)
python3 $SD/video_render.py <dir>/storyboard.json --live --shots 1,3   # 指定镜头重出
```

- 先干跑把提示词给用户过目,确认再 `--live`;先低档模型出小样,满意再换高档逐镜升级
- 提示词自动带画风前缀、景别/角度/运镜、设定图描述、台词/旁白/音效合并段,并遵守「画面里不要文字」
- 每镜时长、画幅从分镜表带过去;换模型后同签名镜头跳过、不同签名自动重出
- 实拍为主体的片种(教程/口播/纪实)只补生成空镜,不整片生成

### 7c. 出片质检

```bash
python3 $SD/video_qa.py <dir>/storyboard.json --scores '{"1": {"画面质量": 82, "主体一致性": 78, "构图": 80, "运镜": 76, "时长": 100, "合规": 100, "提示词忠实": 85}}'
```

- 七维打分(画面质量/主体一致性/构图/运镜/时长/合规/提示词忠实),阈值 75,写回 `shot.video.qa`
- 判决即修复路由:**repair(75–60)→ 局部修改**(原片加指令只改问题点,省额度保画面);**fail(<60)→ 整镜重出**(`video_render.py --shots`)

### 8. 渲染

```bash
python3 $SD/render.py <dir>/storyboard.json        # 生成同目录的 storyboard.html
python3 $SD/validate.py <dir>/storyboard.json --frames
```
HTML 是单文件，分镜图内嵌，可以直接发人或打印（A4 横向）。需要给用户看时用 ego-browser 打开。

### 9. 自检交付

按 `references/review-checklist.md` 过一遍。交付时告诉用户：片种和理由、做的是整片还是哪一段、镜数和时长、导演审核结论、HTML 路径、待确认事项。

## 写作红线

- 画面内容只写镜头拍得到的：不写心理描写（意识到、内心、心想、感到），不写括号暗示
- 一镜一个主导景别；一镜一个职责
- 台词和旁白必须在本镜时长内说得完（中文每秒不超过 5 字）
- 不编造产品功效、数据、奖项；不冒用真实品牌和名人
- 叙事目的写功能和效果，不写「氛围感拉满」这类空话

## 文件索引

- `genres/<id>.md`：17 张片种卡
- `references/shot-language.md`：景别、角度、运镜、转场、连续性、动作-反应、叙事目的写法
- `references/storyboard-schema.md`：storyboard.json 字段
- `references/frame-prompts.md`：分镜图提示词写法、画风库、一致性
- `references/director-review.md`：导演审片标准（节奏机检规则、拖沓与过紧信号、按剧情功能定时长、意见格式与结论）
- `references/review-checklist.md`：交付前自检
- `scripts/validate.py` · `scripts/review.py` · `scripts/frames.py` · `scripts/render.py`
