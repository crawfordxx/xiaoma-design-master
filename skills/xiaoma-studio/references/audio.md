# 声音：配乐、音效、旁白

## 先决定声音形态

| 形态 | 样本占比 | 适合 |
|---|---|---|
| 纯音乐 + 屏幕字幕 | 14/25 | 知识短片、品牌片、showreel。**默认选这个** |
| 歌曲（歌词即字幕） | 7/25 | MV |
| 人声旁白 | 4/25 | 闯关式教学、儿童科普、长纪录片（30 分钟以上） |

旁白会决定节奏：有旁白时，镜头时长跟着台词走，而不是跟着拍子走。

## 代码合成（零依赖、零版权风险）

```bash
python3 engine/audio.py synth cues.json out/audio.wav
```

`cues.json` 需要定义：BPM、时长、根音、和弦进行、乐器层（pad / bass / kick / hat / clap / pluck）、drop（鼓从哪里进）、breakdown（安静段）、音效列表。完整示例见 `examples/*/cues.json`。

音效类型和用法：

| 类型 | 用在 |
|---|---|
| `whoosh` | 泛洪 / 推镜开始前 0.3 秒 |
| `hit` | drop、大字砸下、整屏换色的拍点 |
| `thud` | 物件落地 |
| `pop` | 弹簧弹出的图标、分裂 |
| `tick` | 数字跳动、逐项列出、形变完成 |
| `riser` | drop 前 2 秒 |
| `swell` | 揭晓答案 |
| `chime` | 标题出现、结论 |
| `glitch` | 赛博 / 故障风的切换 |

规矩：
- 音效对齐画面里的事件，事件对齐拍点。泛洪的 `whoosh` 放在 `beat(n) - 0.32`，`hit` 放在 `beat(n)`。
- 先写画面，再从分镜里抄出事件时刻生成 cues，不要反过来。
- 输出自动响度归一到 **−14 LUFS**（各平台的标准）。

## 用现成音乐

```bash
python3 engine/audio.py analyze song.mp3 > beats.json   # bpm / offset / beats[] / sections[quiet|mid|loud]
```
把 `bpm`、`offset` 填进 `MS.setup({ bpm, beatOffset })`。最大的变化落在 drop（第一个 loud 段落的开头），最空的画面放在 quiet 段。

免费可商用的音乐和音效：Mixkit、Pixabay Music、YouTube 音频库。twoclipping 的做法是每个事件都下载一个真实音效，放在测得的峰值上。真实采样的质感比合成更好，有条件就用。

## 旁白 TTS 选型

| 模型 | 强项 | 备注 |
|---|---|---|
| **豆包 TTS（火山引擎 v3）** | 中文自然度高，**能返回逐字时间戳** | 字幕逐字点亮可以和声音精确对齐。要时间戳必须走 v3 异步接口 |
| **Fish Audio S2.x Pro** | 83 种语言、声音克隆、情绪控制 | 样本教程（Lukas / Andy Lo）都用它；有 MCP，可以直接接进 Claude Code / Codex |
| **ElevenLabs Eleven v4** | 英文 / 日文表现力最强，音色库大 | 按字符计费，长片会比较贵 |
| **Gemini Flash TTS** | 便宜、稳定、叙事感好 | LLMJunky 那条 36 分钟的《光的历史》全程用它配旁白 |
| **MiniMax Speech** | 中英都不错，有音色克隆 | 也有配套的音乐模型 |

旁白工作流：
1. 分镜里每个场景写一句台词，按场景分别生成音频（Andy Lo 的做法：一个场景一个文件，方便单独重做）。
2. 读每段音频的时长，镜头时长 = 台词时长 + 0.4 到 0.8 秒的余量。
3. 有逐字时间戳就做逐字字幕：第 i 个字在 `ts[i]` 点亮。
4. 混音时让音乐给人声让路：
   ```bash
   ffmpeg -i vo.wav -i music.wav -filter_complex "[1][0]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=300[m];[0][m]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1" mix.wav
   ```
5. 旁白语气写进 prompt：「温暖、好奇的年轻女声，像在讲绘本；留出停顿让人惊叹，不要赶。」

## 音乐生成模型

- **Lyria 3**：LLMJunky 的长片背景音乐用的是它，作者评价「基本完美」。
- **MiniMax Music**：日本创作者 aicreataro 的 Blender 视觉作品用它做配乐。
- 歌曲 MV：先有歌（Suno 或真人歌曲），再用 `analyze` 测拍，画面跟着歌走。
