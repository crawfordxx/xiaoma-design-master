# storyboard.json 字段说明

一份分镜 = 一个 storyboard.json。脚本都读它：`validate.py` 校验，`frames.py` 出图，`render.py` 出 HTML。
时间码不写进 JSON，由脚本按各镜 `duration_s` 累加算出。

## project（必填）

| 字段 | 必填 | 说明 |
|---|---|---|
| `title` | ✅ | 片名 |
| `genre` | ✅ | 片种 id，必须是 `genres/` 下某张卡的文件名（如 `tvc`） |
| `duration_s` | ✅ | 本分镜覆盖的总时长（秒）。取段落时填段落时长，不是全片时长 |
| `aspect` | ✅ | 画幅：`16:9`、`9:16`、`1:1`、`4:3`、`2.39:1` |
| `platform` | | 投放平台（电视、抖音、B站、发布会大屏…） |
| `audience` | | 目标受众 |
| `core_message` | | 这条片子要让观众记住的一件事 |
| `scope` | | `full`（整片）或 `segment`（取段落） |
| `segment_note` | | 取段落时写清楚：全片多长、取的是哪一段 |
| `assumptions` | | 用户没说、你推断出来的规格，逐条列 |
| `extra_columns` | | 片种扩展列名，如 `["卖点"]`；每一镜的 `extra` 里都要填这些列 |
| `asl` | | `[下限, 上限]`，覆盖片种卡的平均镜长区间，用于卡里的子类型（如一镜到底 MV） |
| `hook` | | 秒数，覆盖片种卡的钩子时限，用于卡里的子类型（如竖屏短版收紧、长版放宽）；0 表示不查 |

## strategy

| 字段 | 说明 |
|---|---|
| `logline` | 一句话核心创意 |
| `beats` | 节拍列表 `[{name, duration_s, purpose}]`，时长之和必须等于 `project.duration_s`。第一个节拍就写钩子本身（钩子之后的铺垫另起一拍），机检按它的结束时间查钩子时限 |
| `visual_style` | 视觉风格：影调、色彩、构图倾向、参考 |
| `tone` | 调性 |
| `music` | 音乐方向：风格、速度、情绪走向、卡点位置 |

## style

| 字段 | 说明 |
|---|---|
| `frame_style` | 画风 id，见 `frame-prompts.md` |
| `prompt_prefix` | 每张分镜图提示词的统一前缀，锁定全片画风 |
| `allow_text` | 画面里需要出现界面文字、图表标注、标题字时设为 `true`，默认不出字 |

## refs（设定，可选）

需要跨镜保持一致的角色、产品、场景，各建一条：

| 字段 | 说明 |
|---|---|
| `id` | 英文短 id，如 `hero`、`bottle` |
| `type` | `character`、`product`、`location`、`prop` |
| `name` | 中文名 |
| `description` | 给人看的设定说明（外观、服装、材质、性格特征） |
| `prompt` | 设定图提示词（只写外观，不写剧情） |
| `image` | 设定图路径，由 `frames.py` 按 id 生成 `frames/ref_<id>.jpg`，不用手写 |

## shots（必填）

| 字段 | 必填 | 说明 |
|---|---|---|
| `no` | ✅ | 镜号，从 1 连续递增 |
| `duration_s` | ✅ | 本镜时长（秒，数字，≥ 0.5） |
| `beat` | | 属于哪个节拍，对应 `strategy.beats[].name` |
| `shot_size` | ✅ | 景别，枚举：大远景、远景、全景、中全景、中景、中近景、近景、特写、大特写 |
| `angle` | ✅ | 角度 |
| `movement` | ✅ | 运镜 |
| `lens` | | 焦段或镜头（24mm、85mm、微距…） |
| `visual` | ✅ | 画面内容，只写拍得到的 |
| `dialogue` | | 台词，写明谁说：`林夏：……` |
| `vo` | | 旁白 / 画外音 |
| `on_screen_text` | | 屏幕字幕、花字、标题字 |
| `sfx` | | 音效 |
| `music` | | 本镜音乐提示（进入、卡点、停顿） |
| `transition` | ✅ | 切到下一镜的方式 |
| `purpose` | ✅ | 叙事目的 |
| `notes` | | 执行备注：拍摄难点、道具、备选方案 |
| `extra` | | 片种扩展列的值 `{列名: 内容}` |
| `action_s` | | 画面里的动作做完、界面或信息看清需要的秒数（编导估算），节奏机检把它算进所需下限 |
| `tempo` | | 节奏意图：快切、正常（缺省）、停留。快切放宽看清画面的下限，停留放宽拖沓的上限 |
| `pace_note` | | 机检报偏紧或拖沓、但有意为之时写理由，机检记为「已说明」 |
| `refs` | | 本镜出现的设定 id 列表，出图时带上这些设定图保持一致 |
| `frame_prompt` | ✅ | 本镜出图提示词（写法见 `frame-prompts.md`） |
| `video` | | 本镜视频出片结果（`video_render.py` 写回，不用手写）：`{prompt, backend, url, ts, error?, qa?}`；`backend` 是出片签名，换模型自动重出；`qa` 是七维质检 `{scores, total, verdict, advice}` |
| `frame` | | 分镜图路径，由 `frames.py` 按镜号生成 `frames/sNN.jpg`，不用手写；增删镜头后自动重算 |

## review（导演审片结论）

| 字段 | 说明 |
|---|---|
| `verdict` | `APPROVE` 通过、`APPROVE_WITH_NOTES` 有备注通过、`REVISE` 退回修改 |
| `reviewer` | 谁审的（独立审片或自审） |
| `date` / `rounds` | 审片日期、第几轮 |
| `summary` | 一句话总评 |
| `issues` | 意见列表 `[{shot, severity, symptom, evidence, fix, status}]`；`shot` 是镜号，全片问题写 null；`severity` 为 P0 / P1 / P2；`status` 为 fixed / open / wontfix |

## post / open_questions

- `post`：`{edit, color, sound}`，剪辑节奏、调色、声音设计各一条可执行建议。HTML 只渲染这三项，别的后期说明（logo 合成、字幕规范）并进最相关的一项
- `open_questions`：会影响执行、事实或授权的待确认项，没有就留空数组

## 校验规则摘要

error：必填缺失；片种或画幅不认识；景别不在枚举；镜号不连续；各镜时长或节拍时长之和 ≠ 总时长；台词 + 旁白超过每秒 5 字；扩展列没填；引用不存在的设定；单镜短于 0.5 秒。

warning：单镜超过 15 秒（纪录片、vlog 除外）；画面内容出现心理描写词；连续 3 镜景别、角度、运镜完全相同。
