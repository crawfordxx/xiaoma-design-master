# 配图与视频的审美逻辑

视频和网页共用。`ai-assets.md` 讲怎么调模型、怎么接进合成；这一份讲**要什么样的图和视频**，以及为什么。规则来自一个官网和三支宣传片的实际制作：60 多张生图、20 多段图生视频、两轮人物重做、一轮被老板否掉的配图（「像卖房地产的」）。

## 1. 先定三件事，再写 prompt

1. **这张图在页面 / 镜头里干什么**：铺底（上面要压字）、证据（正中央，被人看）、氛围（一闪而过）。铺底的图要留出安静的暗部或天空给文字，证据图主体要大而清楚。
2. **它属于哪个主题**：色板跟页面或片子的主题变量一致。纸墨编辑风就是墨黑、雾白、一点朱砂；深空信号风就是深青阴影 + 暖琥珀高光。把色板用颜色词写进 prompt，不靠后期硬调。
3. **真实到什么程度**：对外的产品官网、宣传片默认写实，像实拍；只有科普、绘本、歌词 MV 才用插画风。写实图看起来像 CG，比没有图更伤。

## 2. 写实照片 prompt 公式

```
[画种] Cinematic wide photograph / Editorial portrait photograph / Travel photograph
[主体] 一个具体的真实地点或具体的人（年龄、职业、在做什么），不要泛称
[时刻与光] blue-hour dawn / golden afternoon / late evening fluorescent mixed with warm desk lamp
[机位与镜头] shot on ARRI Alexa with anamorphic lens / 50mm at f/2 / Leica color / drone
[色板] muted palette of ink black, mist white and vermilion（和页面主题一致）
[构图] lots of negative space in the sky for typography / quiet dark area on the left third for text
[禁止] no text, no logo, no watermark, no signage lettering; screens show illegible blurred charts
```

真实用过的一条（首屏铺底）：

> Cinematic wide photograph of a classical Jiangnan water town at blue-hour dawn, still canal reflecting whitewashed walls and dark tiled roofs, a stone arch bridge in the middle distance, thin mist floating on the water, a single wooden boat with a red lantern gliding slowly, warm lantern glow against cool blue fog, shot on ARRI Alexa with anamorphic lens, film grain, muted elegant palette of ink black, mist white and vermilion, lots of negative space in the sky for typography, no people facing camera, no text, no watermark

要点：
- **地点要真，细节要具体**：说出真实的地名和这个地方特有的东西（石拱桥、蓝印花布作坊、牌坊街），不要「一个美丽的古镇」。先在网上找这个地方的实拍照，学它的布局、光线、陈设（不照搬招牌、品牌和他人肖像），记下来源。
- **画面里永远不要字**：招牌、屏幕、标签都写 illegible。字由代码排，图里的字改不了，还会和标题打架。
- **人不正脸对镜头**，除非这张图就是人物肖像：背影、侧身、远景里的游客更像实拍，也避开肖像问题。
- **同一个产品多张图**：先出一张白底产品图，之后每个场景都拿它做参考图改，外观才一致。
- 场景要和受众的行业对上：给工厂老板看的「企业侧」配图用工厂、仓库，不用写字楼和城市天际线（被否过：「像卖房地产的」）。
- 尺寸：GPT Image 的宽高要是 16 的倍数；首屏 2560×1440，竖版封面 1024×1536，卡片 1536×1024。入库转 webp，再出一张 `-s` 小图给卡片和移动端。

## 3. 人物：先四视图，再出镜

凭一句 prompt 直接出的人，每张都不是同一个人，而且像 CG。流程：

1. 每个角色先出一张**写实四视图设定**：同一个人、同一套衣服，正面 / 3/4 侧 / 左侧 / 背面，全身站立，浅灰无缝背景，柔光。prompt 里写清年龄、职业、发型、眼镜、每件衣服的颜色和材质、手里拿的东西。
2. 之后这个人出现的每张图、每段视频都**带四视图做参考图**。两个人同框，把两张四视图拼成一张参考。
3. 换装：每套衣服在四视图基础上再出一张四视图。
4. 人像写实度：Midjourney（`--style raw`）出的人比通用生图模型更像照片；场景、物件、产品用 GPT Image。
5. 不要用「圆圈里一个首字」当头像。要头像就用真实人像裁出来。

## 4. 视频素材

- **先图后视频**：每个镜头先出一张首帧（就是上面那种写实照片），再图生视频。直接文生视频的构图不可控。
- **一个镜头一个运镜，5 秒**：`Slow drone push forward over the rooftops at sunrise, mist drifting, gentle and cinematic.` 只写镜头怎么动、画面里什么在轻轻动（雾、水波、布、灯笼）。不要在 5 秒里塞剧情。
- 常用运镜词：slow drone push forward / slow dolly along / slow lateral dolly / slow pan through / gentle camera push in / slow camera rise revealing / slow orbit。全部 slow。
- 视频模型通常拒收写实人脸作首帧：带人的镜头用背影、远景、手部特写做首帧。
- 比例用 adaptive（跟随首帧），别让模型裁画面。
- **网页背景视频**：三段 5 秒素材叠化成 13–15 秒无缝循环，720p，1.5–4.5 MB，`muted loop playsinline autoplay`，下面压一张同构图的 `poster` 海报图（视频没加载出来时页面也是完整的）。**播完不能停在最后一帧**——被点名过。
- **宣传片**：每片 5–7 个镜头，每镜 5 秒，镜头之间叠化，开头一个航拍定场，结尾回到开头的地点（首尾呼应）。配乐剪在乐句的终止处，不要硬截；整片响度 −14 LUFS。

## 5. 放进页面时怎么处理

| 用途 | 处理 |
|---|---|
| 首屏 / CTA 铺底 | `saturate(.8)`，上面压一层从下往上的暗渐变（底部 .9、中部 .25），文字放在暗部；CTA 背景再降到不透明度 .38 |
| 卡片图 | 默认 `scale(1.06) saturate(.8) brightness(.8)`，悬停或选中 1.2 秒回到 `scale(1)`、饱和 1；图上压字时加底部暗渐变 |
| 步骤 / 流程图 | 统一比例（4:3），统一圆角，统一 `saturate(.85)` |
| 视频 | 同上降饱和；入口页的门在悬停时 `saturate(.75) brightness(.7) → saturate(1) brightness(.85)`，同时从 `scale(1.08)` 推到 1 |
| 背景纹理 | 全局胶片颗粒，不另加纸纹、网格、粒子 |

统一降饱和是让几十张来源不同的生图看起来像一组照片的关键：单张图怎么好看都不如整页色调一致。

## 6. 3D 素材

- 图生 3D（Tripo 一类）：先用 GPT Image 出一张白底、45° 俯视、单个物件的参考图，再生成模型。
- 压缩：`gltf-transform optimize in.glb out.glb --compress meshopt --texture-compress webp --texture-size 1024 --simplify-ratio 0.006 --simplify-error 0.004`，单个物件压到几百 KB。
- 生成模型和程序化几何体混用：先用程序化方块占位，模型做好一个换一个。
- 场景不要自动旋转，镜头给一个好看的固定角度，让人自己拖。「复刻一个真实地点」的大模型很容易被嫌弃，宁可做风格化的小场景。

## 7. 交付前查一遍

- [ ] 每张图、每段视频都登记了：用途、prompt、参考图、文件名（放在 `gen/*.json` 或 STORYBOARD.md）
- [ ] 画面里没有字、没有别人的 logo 和招牌
- [ ] 人物都有四视图，同一个人在不同图里是同一张脸、同一套衣服
- [ ] 整页 / 整片的图色调一致（统一降饱和、统一色板）
- [ ] 视频循环没有卡帧，播完不停在最后一帧
- [ ] 物料里没有「画面由 AI 生成」之类的字样，演示数据有「演示示意」
- [ ] 没有地图、行政区轮廓、线路示意（国内对外物料需要送审）
