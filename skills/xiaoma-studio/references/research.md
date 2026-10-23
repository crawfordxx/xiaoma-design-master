# 研究底稿：30 条高赞 Opus 5.5 视频

- **采集**：2026-10-13，经 Just One API 搜索抖音 / YouTube / X（关键词：opus 5.5 视频 / 动画 / motion graphics / animation / made with 等），按点赞（抖音）或播放（X / YouTube）排序。只选两类：作者明确标注由 Opus 5.5 制作的成片，以及展示了成片和完整 prompt 的教程。
- **分析**：每条都下载后做三件事：均匀抽帧拼图（16–36 帧）、ffmpeg 场景检测算硬切频率、k-means 取主色；再用 whisper 转写音轨，读 X 原帖全文和教程里出现的 prompt 截图。
- **合规**：分析完成后，所有下载的视频已经删除，本仓库不包含任何样本画面。下表只给出处链接。
- 数据为采集当天的快照。抖音接口不返回播放量，所以抖音用点赞。

## 样本表

| # | 平台 | 作者 | 标题（截断） | 数据 | 原型 | 关键做法 |
|---|---|---|---|---|---|---|
| 1 | [抖音](https://www.douyin.com/video/7690344836800913785) | Iwanau | Vibe知识大赏 / 《运气的形状》本视频由#Claude5.5 制作 #o | 60.0 万赞 | 博物馆纪录片 | 年代计数器 + 文献引注 + 每个年代一个会动的概率实验（高尔顿板 / 布丰投针）；纯音乐双语字幕；首尾同一张标题卡 |
| 2 | [抖音](https://www.douyin.com/video/7690199228575960339) | 悲伤喜羊羊 | 让 AI 为孙燕姿《我不难过》画了一支 MV 用 Claude Opus 5 | 44.3 万赞 | 纸艺绘本 MV | 一个主角一把黄伞；雨夜冷蓝 → 暖色回忆；扁平插画 + 雨粒子 + 光晕；歌词小字幕 |
| 3 | [抖音](https://www.douyin.com/video/7694277028904806730) | 🌈我滴个鬼鬼 | vibe知识大赏｜新鲜感的魔咒 这个版本由Opus5.5制作，由此可见在提供 | 40.7 万赞 | 编辑部数据 | 黑白灰 + 一个蓝；点阵比例、水杯水位隐喻；「这只说对了一半」亮底翻转 |
| 4 | [抖音](https://www.douyin.com/video/7688645727061272805) | 骑老爷爷过马路被罚300 | Vibe知识大赏｜《opus家族史》#Claude5.5 #remotion | 17.1 万赞 | 博物馆纪录片 + 生图 | 每个年代一张生成的场景图 + 代码做的迷宫 / 棋盘 / 二进制卦象；双语字幕 |
| 5 | [抖音](https://www.douyin.com/video/7689710282470143653) | Immanuelle | 本视频由opus5.5制作#claude #vibe知识大赏 | 9.7 万赞 | 宇宙电影感 | 遮幅、粒子星系、黑洞透镜、发丝线标注、超宽字距英文；片尾亮底标题反打 |
| 6 | [抖音](https://www.douyin.com/video/7690228850878746107) | 十元钱钱 | Opus5.5 vs Astra 谁赢了 同一首歌，给 “Opus 5.5  | 5.6 万赞 | 对比 / 卡点 | 同一首歌两个模型分屏对比；字效、ASCII 小人、整屏蓝色切换；硬切 45 次 / 分钟 |
| 7 | [抖音](https://www.douyin.com/video/7691561680832154926) | 浙大猫学长 | 一句话做mv，内有提示词 提示词：用 JohnHeibel/ClaudeAn | 5.5 万赞 | 纸艺绘本 MV | p5.brush 手绘质感方块小人；一句 prompt + ClaudeAnimationBase 风格库 |
| 8 | [抖音](https://www.douyin.com/video/7690105449031682661) | Lusilud | 我们完蛋了 这是opus5.5做出来的 #claude #opus #vib | 2.9 万赞 | 产品 UI（液态玻璃） | 8 段 UI 组件形变演示，元信息「01/08 · 120 BPM」；16 秒 |
| 9 | [抖音](https://www.douyin.com/video/7692814249685824079) | 伊老师生物 | 震惊瘫坐，opus5.5大人挑战一个系列让你背完生物必修一 #期末 #高三  | 2.4 万赞 | 游戏关卡 HUD | 把教材变成闯关：检测到新玩家 / 碎片 / 装备 / Boss；红黑 HUD；有旁白 |
| 10 | [抖音](https://www.douyin.com/video/7690973351082881939) | Vincent | 最近尝试了非常多 opus5.5 制作视频的不同风格，有些效果实在是惊艳   | 1.6 万赞 | 风格目录 | 15 种商业级风格逐个展示，卡片列出技术栈（Canvas / Three.js / SVG / WebGL）；一个小球串场 |
| 11 | [抖音](https://www.douyin.com/video/7689897956208189583) | Mixx.ftr | Opus5.5只需略微出手 这条 61 秒的视频，1830 帧画面，每一帧都 | 1.6 万赞 | 风格目录 | 61 秒 19 种风格、1830 帧全部代码绘制，BGM 和卡点音效也是代码合成 |
| 12 | [抖音](https://www.douyin.com/video/7689857919109598498) | 每天每天 | 我拿opus5.5做的《每天每天》mv 太恐怖了 太有审美了 #方大同 #每 | 1.8 万赞 | 纸艺绘本 MV | 扁平插画情侣故事，场景随歌词换，唱片机开场、相册收尾 |
| 13 | [X](https://x.com/ajith_io/status/2103449416325890146) | ajith_io | WTF? Made with claude OPUS 5.5  Prompt | 63.5 万播放 · 4116 赞 | 瑞士风 reel | 一句 prompt；整屏原色按拍切换、HUD 取景框、形变、点阵波、环形文字；收在「Claude.」红点 |
| 14 | [X](https://x.com/0xAidanAi/status/2107578460239519858) | 0xAidanAi | OPUS 5.5 TURNED REAL LIFE INTO MINECRA | 44.2 万播放 · 5527 赞 | 交互 / 3D | 街景 + Minecraft TNT 交互，手机拍屏；不是动效片，但说明「可玩」也能爆 |
| 15 | [X](https://x.com/higgsfield_ai/status/2103839805360820589) | higgsfield_ai | Introducing Higgsfield x Claude Opus 5 | 47.6 万播放 · 2197 赞 | 真人 AI 视频 + 代码 UI | Higgsfield MCP：生成真人剧情，Opus 做地图 / UI / 动效叠加，可导出 AE 工程 |
| 16 | [X](https://x.com/bearlyai/status/2105784343960629738) | bearlyai | Someone used Claude Opus 5.5 to make a | 22.6 万播放 · 1578 赞 | 工程爆炸图 | 从机房连续缩放到原子，单个 HTML 文件浏览器直出；右侧对数刻度尺；全大写章节标题 |
| 17 | [X](https://x.com/LLMJunky/status/2106411941497389342) | LLMJunky | I asked Opus 5.5 to write, produce, an | 15.7 万播放 · 2161 赞 | 剪影科普长片 | 36 分钟《光的历史》：Gemini TTS 旁白 + Lyria 配乐 + GPT Image 2.5 场景 + 代码光学动画 |
| 18 | [X](https://x.com/cherry_mx_reds/status/2102472218269900876) | cherry_mx_reds | Opus 5.5 one-shot this animation in 18 | 16.8 万播放 · 1002 赞 | 角色动画 | 18 分钟一句话出片；蜡笔质感方块小人，挤压拉伸 / 预备动作 / 抛物线虚线 |
| 19 | [X](https://x.com/chhddavid/status/2102666619029999989) | chhddavid | BREAKING: Opus 5.5 one-shots motion vi | 14.5 万播放 · 1108 赞 | 产品发布（亮） | 薄荷绿白；UI 卡片、光标、动态数字、TTS 旁白；19 分钟、改 2 次 |
| 20 | [X](https://x.com/bridgemindai/status/2103530750767206626) | bridgemindai | Claude Opus 5.5 made this video entire | 13.9 万播放 · 1472 赞 | 编年纪录片 | AI 史：每个年代用那个年代的视觉语言，年份大数字左下；首尾同一句「Can machines think?」 |
| 21 | [X](https://x.com/twoclipping/status/2103835273813496100) | twoclipping | OPUS 5.5 IS THE ONLY MOTION DESIGNER Y | 13.7 万播放 · 2161 赞 | 产品发布（亮） | 零外部工具；完整 prompt 公开（一镜到底、光标驱动、液态玻璃、禁用清单、构建细节） |
| 22 | [X](https://x.com/0xMovez/status/2109334686488990093) | 0xMovez | Opus 5.5 + /anatomy skill is insane fo | 15.4 万播放 · 2280 赞 | 工程爆炸图 | /anatomy skill：等轴测线稿 SpaceX 拆解，规格表，可交互旋转 |
| 23 | [YouTube](https://youtu.be/R_ErmTs7g9I) | Degenerative Pixels | The Simulation's Ending - Claude Opus  | 9.7 万播放 | 霓虹终端歌词 | 洋红 + 近黑，每句歌词一个隐喻（终端 / 图表 / 黑洞 / NPC），边角等宽元信息 |
| 24 | [YouTube](https://youtu.be/4Q-o_ylnVnc) | Seguramente | Claude Opus 5.5 Music Video - Ignore P | 4.2 万播放 | 新粗野主义 UI | 奶白 / 克莱因蓝 / 洋红窗口，提示注入题材，超大粗体压满屏 |
| 25 | [YouTube](https://youtu.be/NgRkyAIJx5s) | Regenerate | Run It Again - Claude Opus 5.5 Music V | 5.3 万播放 | 霓虹终端歌词 | 同系列；霓虹灯牌、eval 控制台、航海图纸面镜头做呼吸 |
| 26 | [YouTube](https://youtu.be/OIAWkkSO4WY) | RandomAI | Claude Opus 5.5 Is INSANE at Motion Gr | 22.0 万播放 | 教程 | 汇总 X 上的爆款，讲「Claude + 框架」两条路线与风格目录 |
| 27 | [YouTube](https://youtu.be/747ZnEtsRbg) | Lukas Margerie | How to Make Insane Motion Graphics Wit | 53.5 万播放 | 教程 | 「prompt 只占 10%，90% 是 harness」；Motion studio rules（渲染合约 / 禁用默认 / 拼图自检） |
| 28 | [YouTube](https://youtu.be/6Ij9-f2T2Ck) | Bart Slodyczka | Claude Opus 5.5 Just Solved Motion Gra | 14.5 万播放 | 教程 | 口播视频自动加 motion B-roll 的 skill；核心技法「一个物体持续变形」 |
| 29 | [YouTube](https://youtu.be/7gmPM-Xq5Zo) | Andy Lo | Claude Opus 5.5 Is Insane for Educatio | 6.3 万播放 | 教程 | 纸偶剧场 prompt 五段式（Style / Character / Transitions / Scenes / Sound）+ Fish Audio 配音 |
| 30 | [YouTube](https://youtu.be/3S4vuHxGh7c) | Devarf | I Had Opus 5.5 Make the Same Music Vid | 6.3 万播放 | 教程 / 实验 | 同一句 MV prompt 跑 low→max effort：42 分钟→3 小时，→；先做音频分析再出画面 |

## 量化结论（25 条成片，不含 5 条教程）

| 指标 | 结果 |
|---|---|
| 0 次硬切 | 11 / 25 |
| 每分钟硬切 ≤ 6 次 | 19 / 25；高频硬切（30+ 次 / 分钟）只出现在 MV、风格目录和对比类 |
| 暗底（主色亮度 < 60/255） | 16 / 25 |
| 声音形态 | 纯音乐 + 字幕 14；歌曲 7；人声旁白 4 |
| 时长中位数（不含 30 分钟以上的长片） | 约 62 秒 |
| 主色数量 | 绝大多数是「底色 + 前景 + 1 个强调色」 |

## 从教程和原帖里拿到的方法（按重要性）

1. **Motion studio rules**（@0xMovez 整理，Lukas Margerie 教程演示，53 万播放）：渲染合约（帧 = seek(t) 的纯函数，禁 CSS 动画 / 计时器 / 帧间状态，种子随机）、禁用默认（渐变底居中标题、全部淡入、四角标签、UI 发光、通用粒子）、一个标题字体 + 一个 UI 字体 + 一个强调色、每 2–4 秒必须有新东西、音乐音效代码合成并落在测得的拍点上、−14 LUFS、出片前「每拍一帧拼图 → 6 项打分 → 修最差 3 处 → 全部 ≥ 8 再渲染」。本 skill 的渲染合约和自检循环直接来自这里。
2. **twoclipping 发布片 prompt**：`<inputs>` 先要素材；`<direction>` 一镜到底、物体变形代替转场、光标驱动、禁用清单；`<structure>` 54 拍逐拍写事件；`<build>` 闭式弹簧、液态玻璃实现、全帧内视频、4 子帧运动模糊、逐拍检查和单帧跳变扫描；`<gotchas>`；`<start>` 先给拍点表和 4 张关键帧。
3. **ClaudeAnimationBase**（JohnHeibel，抖音《翠花》MV 用它一句话出片）：三个目标（手工感、有生命、是一个整体）；不用文字；每个镜头都有事件；按观众的理解速度排时间（读点）；转场无处不在；先写分镜；12 条动画原则；拼图自检。
4. **Andy Lo 纸偶剧场 prompt**：Style / Main character / Transitions / Seven scenes / Sound & tech 五段式；转场全部用纸的形变。
5. **Devarf effort 实验**：同一句 MV prompt，low → max effort 耗时 42 分钟 → 3 小时，token 7.8 万 → 62.5 万，费用约 $3 → $49；画面从 2D 变成 3D。先用音频分析工具把歌拆成拍点、乐器、响度、歌词含义，再交给模型。
6. **Vincent（抖音，GitHub 万星 skill 作者）**：WebGL / Canvas 逐帧渲染，NumPy 从零合成配乐和音效，「一句话出片」。
7. **LLMJunky**：让模型自己调用 keychain 里的 key：Gemini Flash TTS 旁白、Lyria 3 配乐、GPT Image 2.5 和 Nano Banana 出场景，代码画剪影剧场和光学动画，36 分钟，花了 $200 多。
8. **prompt-motion.com**（@p4nthera_ 维护）：Opus 5.5 动效视频 + prompt 的合集，是持续更新的一手语料，热门规律见 `prompts.md` 末节。motion.dev 是网页 UI 交互动画库，靠实时驱动，和本 skill 逐帧确定性渲染的合约冲突，没有纳入。
