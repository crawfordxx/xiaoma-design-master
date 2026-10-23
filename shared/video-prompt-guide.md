# 视频提示词导演指南（video-prompt-guide）

> 生视频的瓶颈从来不是模型，是输入提示词的那句话。
> 本指南把"导演级提示词工程"标准化：任何模型都能用同一套结构喂出稳定结果。

---

## 核心结构：场景总述 + 时间轴

工业级视频提示词 = **一段场景总述 + 逐段时间轴**。总述定人/风格/渲染，时间轴控节奏与动作。

### 范式

```
[主体完整描述（外貌/服装/材质）]，[整体风格与渲染词]。

Timeline:
0–4s: [第一拍：动作 + 镜头]；
4–10s: [第二拍：动作 + 镜头 + 反应]；
10–15s: [第三拍：高潮动作 + 镜头收束]。
```

### 范例

> A battle-hardened Valkyrie with braided platinum-blonde hair, war paint, winged runic plate armor, and a lightning-infused broadsword, rendered in cinematic dark-fantasy anime style, fluid high-frame-rate sakuga choreography, expressive hand-drawn line art, intense cold-tone cel shading, and atmospheric blizzard lighting.
> Timeline:
> 0–4s: Dives off a sheer glacier edge into freefall as an ancient Frost Wyrm erupts from the ice wall beneath her, camera spiraling downward in tandem with her descent;
> 4–10s: Uses her wings to bank hard through a barrage of icicle breath, deflects a tail swipe, grapples onto the serpent's icy scales, runs upward along its spine against gale-force winds;
> 10–15s: Channels lightning into her blade, plunges it between the wyrm's horns as glacial rifts detonate, kicking off into the blizzard while the beast collapses, landing triumphantly on a jagged peak.

每拍 = 动作（谁在做什么）+ 镜头（机器在哪）。两样缺一个，模型就自己瞎编一样。

---

## 四维控制（每条提示词过一遍）

| 维度 | 控制什么 | 示例 |
|---|---|---|
| **视觉** | 风格/色调/光线/质感 | cinematic lighting, cold-tone cel shading, film grain |
| **物理** | 运动逻辑/速度/重量 | fluid high-frame-rate, slow-motion debris, fabric physics |
| **空间** | 镜头位/景别/机位运动 | FPV drone, tracking shot, rack focus, wide-angle |
| **时间** | 节奏/时长分配/转场 | Timeline 三段式, 4s build → 6s action → 5s payoff |

第五属性**风格锚**贯穿四维：全部维度向同一个风格锚对齐（"纪录片质感"就全维度纪录片，别混"赛博朋克光+柔光日系"）。

---

## 主体锚定 + 负约束（防漂移/防闪烁）

**主体锚定**：主体描述要完整到可以画出来（发色/材质/服装结构/标志物），并在时间轴每拍重复关键锚点（"the armored Valkyrie"），防止多拍之间主体漂移。

**负约束**：明确写出不要什么：
- "no text, no letters, no captions"（画面文字必乱）
- "consistent character design across all shots, no morphing"
- "stable camera unless specified"（防无意义晃动）

---

## 多参考图：资产分派写法

图生视频带多张参考图时，用**资产分派**结构明确每张图的角色：

```
Asset Assignment:
- Image 1: Fixed opening frame（首帧锁定）
- Image 2: The white wedge coupe, rear wing raised（主体车）
- Image 3: Environment reference — wet concrete port at dusk（环境）

Motion: Camera orbits the car slowly, spray kicks off the rear wheels...
```

不指派 = 模型随机选一张当主参考 = 结果不可控。

---

## 格式头写法（复杂项目）

```
FORMAT: 15s · 9:16 · 24fps cinematic
CONCEPT: 一句话概念
STYLE: 风格关键词串
SHOT 1 (0-5s): ...
SHOT 2 (5-10s): ...
SHOT 3 (10-15s): ...
```

大写头 + 分镜编号的结构化提示词，在长视频（20s+）上远比散文段落稳定。

---

## 常见病症与处方

| 病症 | 处方 |
|---|---|
| 主体漂移（脸/服装变） | 加主体锚定 + "consistent character design" 负约束 |
| 画面闪烁 | 降风格词冲突（两种光效打架），加 "stable lighting" |
| 动作拖沓 | 每拍动作写满（模型闲着就乱动），或压缩 Timeline 段数 |
| 镜头乱晃 | 明确机位："fixed camera" / "slow dolly in" |
| 文字乱码 | no-text 指令 + 文字后期加 |
| 时长不对 | 时间轴总秒数 = 请求时长；比例写进 prompt 尾部 |

---

## 生成流程（配合 toolkit/gen 两档制）

1. **分镜先行**：先出完整分镜表（镜号/时长/画面/镜头/台词），人工过一遍再生成
2. **draft 档试参数**：每条提示词先用低价快速档出样，看构图/主体/运动对不对
3. **一次只改一个变量**：不对就改一个参数重来，别同时改三个
4. **final 档出正片**：参数锁定后旗舰档生成
5. **逐镜质检**：主体一致性/运动逻辑/画面文字/时长，任一不过重出该镜（局部重出，不整片重来）

## 视频提示词自查清单

- [ ] 场景总述完整（主体可画、风格词 ≥5、渲染词明确）
- [ ] Timeline 每拍 = 动作 + 镜头
- [ ] 四维（视觉/物理/空间/时间）全部显式声明
- [ ] 主体锚点在每拍重复
- [ ] 负约束（no-text / no-morphing）在场
- [ ] 多图时资产分派明确
- [ ] 时长与比例写进提示词
