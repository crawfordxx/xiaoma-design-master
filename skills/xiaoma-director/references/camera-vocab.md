# 运镜词汇:中文词条 ↔ 结构化网关枚举

分镜表里的 `movement` 是中文自由词条(片种卡用语)。走**结构化后端**(VIDEO_BACKEND=structured)出片时,`video_render.py` 会把能对上的词条转成网关的官方运镜枚举;对不上的词条省略该字段,交给端点自动导演。映射代码在 `scripts/video_backends.py` 的 `_ZH_MOVEMENTS`。

## 运镜枚举(33 值)

| 中文词条 | 枚举值 | 中文词条 | 枚举值 |
|---|---|---|---|
| 推 / 推镜头 | `dolly-in` | 拉 / 拉镜头 | `dolly-out` |
| 缓推 | `slow-zoom-in` | 缓拉 | `slow-zoom-out` |
| 急推 | `crush-zoom` | 变焦推 | `dolly-zoom` |
| 甩 / 甩镜头 | `whip-pan` | 摇 / 右摇 | `pan-right` |
| 左摇 | `pan-left` | 上摇 | `tilt-up` |
| 下摇 | `tilt-down` | 移 / 右移 | `truck-right` |
| 左移 | `truck-left` | 滑轨 | `slider-right` |
| 跟 / 跟镜头 | `tracking` | 侧跟 | `side-tracking` |
| 环绕 / 穿越机 | `drone-orbit` | 弧线 / 右弧 | `arc-right` |
| 左弧 | `arc-left` | 摇臂升 | `crane-up` |
| 摇臂降 | `crane-down` | 升 | `pedestal-up` |
| 降 | `pedestal-down` | 手持 | `handheld` |
| 绑身 | `snorricam` | 机械臂 | `robot-arm` |
| 子弹时间 | `bullet-time` | 航拍后拉 | `aerial-pullback` |
| 直升机 | `helicopter-shot` | 移焦 | `rack-focus` |
| 第一视角 | `pov` | 固定 / 静止 | `static-shot` |

其余枚举值(如 `slider-left`)可直接写英文原值,原样透传。

## 结构化后端还认这些导演参数

出片提示词之外,结构化端点通常还接受结构化导演参数,按端点文档选用,常见的一组:

- **镜头** `clean-sharp / anamorphic / vintage-anamorphic / warm-vintage / halation-vintage`
- **机身** `modern / 35mm-film / 8mm-film / dv-camcorder`
- **光圈** `f14-wide-open / f4-moderate / f11-deep-focus`
- **年代 / 类型 / 光位 / 节奏**:1960s–2020s;epic/drama/noir/comedy/horror/action;silhouette/practicals/window/overhead-fall/contre-jour/soft-cross;chaotic/dynamic/calm/single-shot
- 多数端点还带一批**命名调色板**(如 neon-rain-at-midnight、gasoline-sunset 一类的整片色彩预设),按端点文档填

## 纯文本提示词里的运镜写法

走 chat / task 后端时运镜只写在提示词里,两派都有效:

- **重术语流**:景别 + 机位 + 焦段 + 运镜逐项写清(「略低机位、50mm、中景、缓推」),再补风格与氛围、质感词(胶片颗粒、浅景深、伦勃朗光)
- **极简流**:主体 + 光线 + 一个动作(「金色阳光,镜头缓缓上移」),轻内容更稳
