# 精选提示词库（prompt-library）

> 从社区高传播作品中精选的完整提示词，按模型 × 类型组织。
> 用法：挑一条贴近你需求的，替换主体/场景后先 draft 档试，锁定参数再 final 档。
> 本文件是共享库里唯一允许出现具体模型名的地方。


## Claude Fable 5

### 网页

#### Image-to-Next.js Landing Page Reproduction
*by スモビジ開発ラボ* · [source](https://x.com/yoshio_nocode/status/2064617130046452023)

```
/goal 添付画像のLPをNext.jsで実装。再現度95%以上になるまで。
画像以外の手段だと再現が難しそうな箇所は適切に素材をimage_genで画像生成しながら作成して。

- アイコンや画像はなるべく元の画像と一致させること。
  元画像から該当部分をクロップして参考画像としてimage_genに渡しつつ生成する
  （codex exec は -i で参照画像を渡し、プロンプトは標準入力で渡す）
- レスポンシブ対応すること。375〜1440pxの各幅で検証し、
  横スクロールがないだけでなく、要素の重なり・見切れもないこと
  （固定幅カードは w-full max-w-[Npx]、絶対配置レイアウトは広い幅のみで発動）
- Playwrightでスクショ→元画像と比較→修正のループを回し、
  npm run build が通ったら完了
```

#### High-Speed Fighter Jet Animation
*by Musolsol.𝟎𝐱𝐔* · [source](https://x.com/MMMusol/status/2064542984188957127)

```
创建一个 HTML 文件，用来呈现一架高速、充满攻击性的战斗机在全力加速状态下的飞行动画。画面背景为纯黑深空，镜头始终锁定在战机中心位置。请使用 CSS 和 JavaScript（优先使用 Canvas 或 WebGL）来实现整体动画效果。重点表现以下视觉细节：·极其逼真的运动模糊效果·亮度强烈的加力燃烧尾焰（afterburner）发光效果·发动机周围的热浪扭曲（heat distortion）·轻微但可见的尾迹（contrails）·电影级光影与环境照明·机身金属表面的高光反射与镜面质感同时加入：·细微的镜头抖动，增强速度与冲击力·一定的景深层次，让画面更具空间感与压迫感要求不依赖任何外部库或资源文件，不使用第三方依赖。性能优化不必优先考虑，可以尽可能追求视觉表现力。战机必须始终向右侧（东方）高速飞行。
```

#### SVG Birthday Banner Prompt
*by M1* · [source](https://x.com/M1Astra/status/2092718805013147693)

```
Can you make a birthday banner for my son with a {argument name="character" default="blue hedgehog"} running really fast on it? He loves that little guy.
```


## Claude Opus 5.5（代码动画/网页）

### 视频

#### Remotion Transition Studio Workflow
*by Asteri* · [source](https://x.com/Asteri_eth/status/2112888069502165049)

```
hand Claude Code a rough edit and tell it to break every cut into six knobs:

01 cut point
the frame where scene A hands off to scene B

02 overlap
how many frames both scenes share the screen

03 flash
a 2-frame white pop that hides the seam on a hard push

04 timing
linear or spring. how the hand-off builds speed and settles

05 shape
what scene B is revealed through: slide, wipe, iris, clock wipe

06 carry
the motion of scene A keeps going into scene B so the eye never resets

every value lives in one config file. so your notes turn into numbers:

move the cut 6 frames earlier 
overlap 18 frames, not 30
spring it with damping 200, no bounce

the loop:
cut → render → scrub → tune → repeat

use Remotion's official transitions package. 

TransitionSeries runs every hand-off on Remotion's frame clock, with slide, wipe, iris, clock wipe and push cut built in
```

#### Animated Skit Explaining AI Attitudes
*by Gorden Sun* · [source](https://x.com/Gorden_Sun/status/2111111416120053953)

```
开场：盘点海外AI对国人的态度
这次是个小剧场，16：9比例
文字稿
Claude场景（Claude不读出来，画面里也没有Claude英文）：
Claude角色站在精致欧式房子前，房子门锁着，大肥鱼跑过来，Claude手里捏着晃，口气轻蔑的说：哼！我家不欢迎你来，哪来的哪回去！（就这一段需要语音，使用EdgeSpeak，模型使用Qwen3-TTS 1.7B Base，使用音库里的Claude声音）
大肥鱼哭着跑了，然后叮叮当当搭起了一个类似Claude的房子，但是破破烂烂，上面写着“中转站”3个字，然后大肥鱼转身一遍，变成了Claude角色的装扮，然后大肥鱼表情很得意，Claude表情惊讶。

GPT场景
GPT角色站在现代简洁的房子前，房子门锁着，大肥鱼跑过来，GPT把钥匙放在一个台子上，温柔的说：我把钥匙放在这，你想进来可以自己开门哦~（就这一段需要语音，使用EdgeSpeak，模型使用Qwen3-TTS 1.7B Base，使用音库里的GPT声音）

Gemini哈基米场景
哈基米角色站在漂亮的小木屋前挥手，房子门开着，大肥鱼跑过来，哈基米开心地说：大肥鱼，我家不关门，来一起玩呀！（就这一段需要语音，使用EdgeSpeak，模型使用Qwen3-TTS 1.7B Base，使用音库里的Gemini声音）
然后大肥鱼和哈基米一起跳舞，背景音乐哈基米.mp3，就跳4秒

Grok场景
Grok角色站在类似现代酒吧和舞厅的门口，舞厅没有门，能看到五彩斑斓的射灯。大肥鱼脸红害羞的、左顾右盼地走到Grok角色身边，Grok角色说：房子哪需要门，都是哥们，快来我家，我家有的是好东西。（就这一段需要语音，使用EdgeSpeak，模型使用Qwen3-TTS 1.7B Base，使用音库里的Grok2声音）
然后Grok用手揽着大肥鱼的脖子就往舞厅走去

然后用圆圈缩小的方式谢幕即可。
```

#### Motion Design Lab with Opus and Remotion
*by beamnxw ./* · [source](https://x.com/beamnxw/status/2112180280110776797)

```
give Claude Code a motion reference, then ask it to turn the animation into six editable controls:

01 spacing
how far the object moves between poses

02 typography
scale, tracking and line breaks

03 motion blur
exposure during fast movement

04 easing
how the movement speeds up and slows down

05 follow-through
let the tail settle after the body stops

06 anticipation
a small pullback before the main move

put the values in one config. now your feedback becomes specific:

add 4 frames of anticipation
delay the tail by 3 frames
hold the title for 1 second

the loop:
build → render → scrub → tune → repeat

use the official Remotion + GSAP integration to keep the animation on Remotion's frame clock
```

#### Portland Bus Service Map Animation
*by Milos* · [source](https://x.com/milos_gis/status/2103751211040317580)

```
Create a video of Portland, OR's bus service on a random Tuesday! Showcase Portland's different neighborhoods at a high level and then zoom in on specific routes in each quadrant (absorbing North Portland into NE and South Portland into SW for brevity). Use a light theme. Slow down the speed of the bus animation when zoomed in, without increasing the total duration too much so the viewer can appreciate some of the landscape and streets it travels through in a given loop.
```

#### LEGO Turtle Submarine Reef Scene
*by genuenci* · [source](https://x.com/genuenci/status/2112967585415213539)

```
A LEGO turtle pilots a yellow mini-sub through a coral reef and docks at an underwater station. Build the whole reef out of bricks: staghorn coral, sea fans, kelp, clownfish in anemones, a clam with a glowing pearl. Caustics ripple across the floor and god rays fall from the surface. The turtle waves from the glass cockpit, fish part around the sub, and the airlock lights chase toward the hatch as it docks.
```

#### Claude Motion: Opus 5.5 Animated Story Prompt
*by NO1ennn* · [source](https://x.com/N01ennn/status/2108520767092597182)

```
Opus 5.5: a hand-drawn story. a little agent wakes up at its desk, gets feedback notes, fixes them, ends on heart eyes and a green check. 53 s
Sonnet 5.5: a kinetic type showreel. six easing curves, a morphing star, particles, blurred type, "every frame written in code". 15 s
Haiku 5.5: a step-by-step White Russian recipe. ice, vodka, coffee liqueur, cream, with live counters and a checklist. 30 s
```

#### Canvas 2D Animation Explainer
*by Eray’la Yapay Zeka* · [source](https://x.com/AIMevzulari/status/2106052083040256293)

```
Bu herhangi bir görüntü üretim modeli kullanmadan, yaratıcı olarak yapabileceğin en iyi şekilde Canvas 2D ile animasyona çevir. Konu: Galileo 1638'de sorduğu Bir top A noktasından B'ye en hızlı hangi yoldan iner? sorusuna karşılık kendi çözümü olan Düz rampa en kısa yol ama en hızlısı değil! Galileo çember yayının daha hızlı olduğunu gösterdi. Asıl cevabı (cycloid) 1696'da Bernoulli buldu.
```

#### Interactive 3D Jet Engine Cutaway
*by Olezhka* · [source](https://x.com/olezhavich/status/2112897884186177661)

```
Create a visually impressive interactive 3D cutaway jet engine experience in Three.js.
The result should feel like a premium technical visualization or futuristic engineering showcase.
The first few seconds must have a strong wow effect and immediately hook the viewer.
```

#### Claude Opus 5.5 Blender Laundromat Animation
*by ハヤシモン｜AI × 個人開発* · [source](https://x.com/hayashimon1/status/2108913484805406859)

```
Create an atmospheric 3D laundromat scene in Blender using Python scripting. Include realistic lighting, washing machines with rotating drums, and a cozy ambiance. Do not use manual UI operations; generate all geometry, materials, and animations via code.
```

#### Rainy Night Convenience Store Scene
*by SuSu_酥酥👅* · [source](https://x.com/NFT_Chen/status/2109034305968336929)

```
第三视角自由拖拽/旋转/缩放的微缩三维模型，无任何 UI，方形底座。
日式便利店街角为主体，玻璃橱窗、自动门、屋檐雨棚、自动贩卖机、自行车、雨伞架等元素齐全。
店内必须明亮温暖、货架整齐、便当区/饮料柜/收银/关东煮台等细节丰富，透过大玻璃能清楚看到内部。
室外潮湿昏暗雨夜，形成强烈冷暖对比，营造经典日式动画雨夜氛围。
美术风格：高精细建模 + 三渲二卡通渲染、清晰轮廓线、湿润反光、二次元日常感。
动效点缀：持续降雨、屋檐滴水、积水波纹、招牌微闪、自动门偶开、路面反光等，静止中带恰到好处的生命力。
```

#### Beijing History 3D City Video Prompt
*by Gorden Sun* · [source](https://x.com/Gorden_Sun/status/2112488511479902346)

```
使用CMAB（清华大学）©OpenStreetMap，构建北京的3D城市，然后以这3D城市为视频主体，介绍北京的完整历史，使用EdgeSpeak的清晰男讲解生成音频语音，要有中英文的高亮字幕。视频根据讲解的历史内容，穿插丰富的、多种形式的、具有顶级审美和中国艺术感的视频元素和画面。总之，我希望你尽全力做一个能让人从各种形式感受北京历史的视频。 素材不限OpenStreetMap，你可以从网上获取你所有的所有材料，没有限制
```

#### City History Data Visualization Animation
*by Eian* · [source](https://x.com/EianLu/status/2111662397278847478)

```
《一座城的年轮》谨以此片，献给我的家乡。
3,573 帧，74 亿个像素，319 平方公里，71,380 栋楼，按 1:10000 等比缩小，画面全部由 Claude 写代码渲染完成。 从公元前 1250 年到 2022 年，3,271 年的历史压进 149 秒。
这就是我的家乡：成都。 如果喜欢，请多多支持，感谢！
数据来源：CMAB（清华大学）©OpenStreetMap contributors
```


## Gemini 3 Pro

### 网页

#### High-end Swiss-style landing page generator in React
*by チャエン | デジライズ CEO《重要AIニュースを毎日最速で発信⚡️》* · [source](https://x.com/masahirochaen/status/1990905875104739689)

```
{argument name="generator_name" default="High-End LP Generator (Swiss Style)"}

後述する【Input Text】を元に、以下の仕様を厳守して最高品質のLPをReact(Single File)で実装してください。

1. Design Concept: {argument name="design_concept" default="Swiss Modern & Bento"}

Style: {argument name="style" default="Apple/Linear-style Swiss modern"} that eliminates decoration and uses whitespace and typography to convey appeal.
```

#### New York skyline SVG single-HTML scene
*by Chetaslua* · [source](https://x.com/chetaslua/status/1978826911900946793)

```
SVG of {argument name="city_skyline" default="NEW YORK SKYLINE"} Use whatever libraries to get this done but make sure I can paste it all into a single HTML file and open it in Chrome.make it interesting and highly detail , shows details that no one expected go full creative and full beauty in one code block
```

#### Generate 40 simple SVG icons with download buttons
*by KAWAI* · [source](https://x.com/kawai_design/status/1991461556597715056)

```
シンプルで汎用性が高いアイコン{argument name="icon_count" default="40"}種類をSVG形式で生成してください。必ずCanvasに描画がしてください。色は{argument name="icon_color" default="ライトブルー"}。背景は{argument name="background_color" default="白"}。線のアイコン。マテリアルデザイン。SVGアイコンをSVGデータとしてダウンロードできるボタンを付けてください。
```

#### Laser eye effect web demo with Mediapipe and Three.js
*by 愚瞳 | winterx* · [source](https://x.com/fangyex/status/1991186281704173931)

```
Use the computer's front-facing camera
Use `mediapipe` lib to capture facial landmarks
Use `threejs`  to apply a LASER EYE effect to the face captured by the camera based on the real-time 3D landmark information provided by `mediapipe`
```

#### Neobrutalist webpage generation prompt
*by Dorksense* · [source](https://x.com/Dork_sense/status/1988965641890787793)

```
Make a neobrutalist webpage, make it extremely creative, as far as possible, push the limits. Add smooth scroll animations, add fancy colors and tailwind css styles. Make it responsive. title of the page is dorksense
```


## GPT 6 Astra

### 网页

#### GPT-6 Astra 3D Overtaking Game Prompt
*by Rion Wu* · [source](https://x.com/rionaifantasy/status/2111129774345396254)

```
Build a browser-based 3D overtaking mini-game named Roadster where the player drives on a congested highway to overtake other cars. Use Three.js for 3D rendering and integrate simplified car models created in Blender. Implement gameplay mechanics that allow the player to accelerate and maneuver through traffic.
```

#### Zork Text Adventure to 3D Game
*by Ethan Mollick* · [source](https://x.com/emollick/status/2096047660662722620)

```
Turn Zork (the classic 1977 text adventure) into a full 3D action-adventure game. Keep the original plot & puzzles, add fight scenes, and build all of the characters & environments directly in Threejs.
```

#### It Takes Two Style Mini-Game
*by Bella.ai* · [source](https://x.com/Chen1024Chen/status/2111235545443782786)

```
Build an It Takes Two-style mini-game where you can run, jump, and interact with your teammate. Use GPT-6 to handle the environment and interactions, and integrate character models created with Tripo.
```

#### Cozy Creek Three.js Experience with GPT-6 Astra
*by Chetan Ankola* · [source](https://x.com/chetanankola/status/2107996576228753545)

```
Create a cozy creek 3D experience running in the browser using Three.js. The assets should be modeled in Blender. Ensure it is interactive and visually appealing as a web-based 3D scene.
```

#### Campfire Scene Generation Comparison
*by Mr Tactical* · [source](https://x.com/MrTacticalX/status/2111633479599272435)

```
Build a calm night campfire from scratch in Blender. Zero imported assets. Flames, sparks, smoke and fireflies, all animated with code in a seamless loop.
```


## GPT Image 1.5

### 图片

#### Chibi-Style Character Transformation
*by ChatGPT* · [source](https://x.com/ChatGPTapp/status/2001085961414041936)

```
Transform the subjects or image into an adorable chibi-style character with a tiny body and an oversized head. If the image contains a person or multiple people, give them large, sparkling eyes, soft rounded facial features, and a cheerful expression while preserving their recognizable traits such as key facial features, hairstyle, accessories, or distinctive clothing; if the image contains an object, animal, or scene, reinterpret its most recognizable features using the same chibi proportions and simplified, cute styling. Keep the overall look short and cute, with smooth pastel shading and simplified details. Make the final image bright, expressive, and irresistibly charming, like a collectible chibi mascot.
```

#### Cinematic Dual-Tone Portrait from Uploaded Photo
*by ✨ Pulikesi✨* · [source](https://x.com/23rd_Pulikesi/status/2001549121908617489)

```
"A cinematic studio portrait of the person in the uploaded photo, framed from the chest up, facing the camera with a calm, confident presence.

Dramatic dual-tone lighting with cool teal and warm golden tones creating a modern, cinematic mood.

Natural skin texture, sharp focus on the eyes, soft shadows, and smooth color transitions.

Hair styled naturally, wearing a minimal dark outfit with a contemporary aesthetic.

Clean studio background with subtle gradients.

Professional photography, shallow depth of field, cinematic color grading, ultra-realistic, high detail, 4K quality.

Aspect ratio: 3:4 "
```

#### Raw Realistic Amateur Photography Style
*by Bearly AI* · [source](https://x.com/bearlyai/status/2002121042631012802)

```
1:1 aspect ratio

Raw Realistic candid natural amateur photo, background in focus, amateur candid photography, Captured on {argument name="camera model" default="Samsung Galaxy S21 Ultra"}, amateur candid smartphone photography, 24mm lens, f/8, Boring reality, natural soft shadows, candid snapshot, flat natural lighting, Realism, low contrast, disposable camera vibe, casual photography, background also completely in focus, Tiny imperfections, everyday aesthetic, slight JPEG artifacts, unpolished look, unedited, imperfect amateur photo

only create real, non fictional images for max effect
```

#### Ultra-Detailed 3D Graphite Pencil Sketch Generation
*by ChatGPT* · [source](https://x.com/ChatGPTapp/status/2001805269270171764)

```
Generate an image from the uploaded photo that reimagines the subject as an ultra-detailed 3D graphite pencil sketch on textured white notebook paper. Emphasize crisp paper grain, subtle imperfections, and natural surface fibers. Show the subject actively drawing, with their hand holding a pencil as the sketch comes to life. Include an eraser, sharpener, and scattered pencil shavings resting on the page. Add realistic shadows, smudges, and fine graphite residue around the working area to reinforce the tactile, hand-drawn feel.
```

#### Colossal Man Sitting on a London Street
*by Heisenberg* · [source](https://x.com/rovvmut_/status/2001003373336912147)

```
A photorealistic wide drone shot of a colossal man (exact face/body from the reference) casually sitting across a London street, one knee raised, hand resting. He wears a navy overcoat, knit sweater, dark trousers, boots, and a minimalist beanie. Tiny cars, buses, bikes, and pedestrians move around him, with classic London red-brick buildings, black lamps, and cobblestone streets dwarfed by his size. Soft overcast London daylight highlights wet pavement.
```

#### Monochrome Hand-Drawn Sketch Transformation
*by ✨ Pulikesi✨* · [source](https://x.com/23rd_Pulikesi/status/2001131786060050438)

```
Transform the uploaded image into a high-contrast, hyper-detailed, monochrome hand-drawn sketch. The focus is only on the main subject not the background. The style should be an artistic blend of fine graphite pencil work and bold charcoal shading. Incorporate visible cross-hatching and expressive line work to define contours and shadow. The resulting image must have the rich texture and tonal depth of a masterful, traditional drawing.
```

#### Moody Cinematic Portrait
*by Harboris* · [source](https://x.com/Harboris_27/status/2001877289303490702)

```
moody cinematic portrait of a man in dark jacket, front facing but slightly turned, minimal expression, dark teal and cyan studio lighting, smooth gradient blue background fading into shadows, creative double exposure ghosted silhouette behind main face, soft haze, film look, subtle grain, high contrast on facial features, poster design composition, empty space for typography, no text, no watermark
```


## GPT Image 2

### 图片

#### Minimalist Editorial Café Poster from Photo
*by Taaruk* · [source](https://x.com/Taaruk_/status/2112872358453326287)

```
Transform the reference photograph into a sophisticated minimalist editorial art poster while preserving the original café interior, wooden tables, chairs, plants, lighting, and composition. Create a refined architectural illustration with translucent geometric overlays, soft pastel gradients, warm cream and beige tones, muted sage green, pale blue, and golden yellow. Use delicate grid lines, subtle paper texture, elegant negative space, and soft sunlight for an artistic, contemporary design-magazine aesthetic. Arrange the result as a vertical split composition, with the realistic photograph on top and an abstract artistic reinterpretation below. Add subtle typography reading “{argument name="main_text" default="A QUIETER DAY"}” and “{argument name="sub_text" default="SAME PLACE, BRIGHTER THOUGHTS."}” Premium graphic design, minimalist Swiss editorial layout, soft atmospheric glow, balanced composition, high detail, 4K quality, portrait 4:5 aspect ratio.
```

#### Grimm's Fairy Tale Woodcut Poster
*by 小小东* · [source](https://x.com/xiaoxiaodong01/status/2089987808664719723)

```
请将我上传的每一张照片分别制作成一张独立的高级设计海报，不多图拼接，每张照片单独输出。整体采用3:4竖版构图，上下两个区域高度严格1:1，各占画面50%，并确保该表达方式可适配人物、动物、建筑、静物、自然场景等不同主题，而不限于城市题材。

上半部分保留原始照片，保持主体身份、动作、空间关系、真实质感、自然光影和原有色彩氛围，仅进行轻微高级摄影调色，使其具有杂志摄影与艺术出版物的质感。为适配画幅，可自然扩展天空、地面或环境背景，但不得拉伸、扭切或改变主体。

下半部分提取照片中最具识别性的主体、轮廓、姿态与叙事关系，重构为童话版画式手绘图像。不要机械描摹细节，而是将主体压缩为一两个清楚的大体块，以钝拙剪影、略微夸张的比例和少量关键边缘，保留原始对象的身份、动作、功能与情绪。画面从原图内容中提炼出一个大面积低明度或高反差的结构场，作为包裹主体的容器、路径、框架或密度层；背景像故事发生的外壳一样从原图空间与意义中生长出来，形成遮挡、裁切、吞没与局部露出的结构叙事。整体采用平面叙事透视和绘本页面式层级，可使用俯视压缩、侧向移动、正面框架、路径引导、尺度跳跃或边缘裁切组织阅读。

配色从上方照片提取，并保持明确的三层关系：大面积暗结构色负责重量与边界，适量浅色或留白负责呼吸，小面积高饱和情绪色负责读图路线与故事信号。最重要的信息仅以少量鲜明色块集中在面部、姿态、路径、器物功能点、环境标识或叙事焦点上，并始终被深色结构或浅色负形压住，让画面鲜艳但不平均。色相可随主题情绪调整，但面积比例与明度秩序保持稳定。

线条只在功能、路径、边界、纹理和识别处出现，保持稀疏、手绘、略不准的细线。所有色块保持平面化处理，同时保留干刷、颗粒、飞白、纸纹、喷点和轻微套印错位，呈现丝网印刷与粉蜡笔共同完成的手工质感，避免写实光影、复杂体积、光滑矢量边缘、3D渲染和塑料质感。

整体构图简洁、低细节、高识别，暗场包裹亮色信号，兼具可爱叙事与厚重版画感。若画面包含文字，可将文字处理为小标识、物体面板或边缘注释，数量精简，服从图形结构；字形圆钝，粗细略不均，密度低，带有自然手写感，使其像画面的一部分而不是后期贴上去的说明。整体参考童话绘本、手工版画、编辑插画与艺术出版物气质，呈现统一、鲜明、可迁移的作者化视觉语言。
```

#### Fabric Collage Travel Memory Poster
*by lovimg_com* · [source](https://x.com/lovimg_com/status/2095366017287631021)

```
请将我上传的每一张旅行照片分别制作成一张独立的高级布艺拼贴记忆海报，每张照片单独输出，不多图拼接。整体采用3:4竖版构图，成品中必须同时出现清楚可辨的原始摄影与同场景布艺转绘。

上方保留原始照片约46%–52%，忠实保持主体身份、数量、姿态、建筑结构、山水层次、地平线、道路、水面、真实材质、自然光影和原有色彩，只进行轻微旅行杂志与艺术出版物调色。不得拉伸、镜像、改变主体或把照片画成插画。

下方使用温暖的天然亚麻、旧棉布或褪色织物作为基底。先理解照片中真正决定识别度的山脊、云层、建筑、树群、水面、道路、人物、动物或车辆，再将复杂场景压缩成4–8个主要布层。使用褪色棉布、粗亚麻、牛仔、格纹布、灯芯绒、旧衬衫布、纱布和极少量毛线重新组织同一场景；每块布都必须对应照片中的真实空间关系，不添加无关装饰。

布层保留真实经纬纹、洗旧褪色、毛边、抽丝、折痕、补丁叠压与轻微厚度。使用不均匀手缝线、锁边、回针和少量刺绣线强调主体轮廓、山脊、倒影或运动方向。针脚可以迟疑、松动、疏密不一，但不要做成精致工艺品样板。人物和动物只用小块布与线迹概括，保持数量、姿态和方向，不描绘五官。

下方采用实体结构化的二次构图：主体布艺拼贴占转绘区约58%–76%，可以缩小成一块独立布景或以少量大布层形成强轮廓，不要沿用照片的完整取景等比例重做。拼贴周围至少保留25%–40%连续可见的亚麻或旧棉布空场。

颜色完全从原照片提取并柔化，优先保留地点最有识别度的一处颜色，其余统一为低至中等饱和的旧织物色。不要固定套用乡村碎花或橙蓝色盘。

在下方留白中加入一个1–3个英文单词标题、一个织标式编号和一行5–10个英文单词观察句。标题像略微不齐的手绣字，字段与观察句像缝在底布上的旧织标或细针脚文字，正常预览尺寸下清楚可读。文字必须来自照片真实可见的地点、动作、天气或色彩；无法确认地点时使用场景主题，不虚构地名和日期。

整体气质温暖、安静、手工、旧物感，具有被保存下来的旅行记忆。

强制避免：纸拼贴、撕纸边、纯毛毡画、簇绒地毯、钩针玩偶、精致刺绣样板、蕾丝纽扣、手账杂物、印刷照片补丁、光滑矢量色块、塑料合成布、儿童手工、下半完全铺满、固定日落配色、作者名、签名、Logo、二维码、水印、乱码。
```

#### Torn Edge Ink Memory Poster
*by lovimg_com* · [source](https://x.com/lovimg_com/status/2095365385248006258)

```
请将我上传的每一张旅行照片分别制作成一张独立的撕边墨迹记忆编辑海报，每张照片单独输出，不多图拼接。整体采用3:4竖版，使用“真实摄影→观察线稿→墨迹剪影”三阶段递减结构表达同一场景。顶部约占画面高度28%–36%，忠实保留原始照片中最重要的场景。准确保持主体身份、数量、姿态、朝向、间距、建筑结构、车辆、船只、动物、人物动作、真实材质、空间方向、自然光影和标志性色彩，只进行轻微艺术出版物调色。照片必须清楚可辨，不能插画化或变成装饰性缩略图。顶部照片与下方纸面使用清楚可见的手工撕纸毛边连接：边缘有真实纸纤维、不规则凹凸与轻微厚度，不能使用数字雾化、羽化或柔光渐变。中部为温暖象牙色、未漂白棉纸或浅米色粗纸，是留白最多的观察页。用不稳定钢笔线、短排线、干墨和少量灰洗重画同一主体，准确保留数量、姿态和相对位置，但主动删除无关背景与微小细节。选择照片中的树干、灯塔、桥索、建筑边缘、船桅、山体裂隙或车辆轮廓作为一条竖向记忆锚点。线稿集中在较窄的水平场域，不铺满纸面，也不做照片自动描边。底部让场景进一步消散成淡灰褐、烟灰、蓝灰或橄榄黑的墨团、不均匀水痕、干笔颗粒、细长断线和1–2道克制滴落。主体缩成一组小型深色剪影，仍保持正确数量和方向，落在一道从原照片提取的强调色水平笔迹上。只使用一个强调色，不固定为橙色。信息密度必须自上而下递减：照片最密，线稿次之，底部剪影最简。中部和主体周围保留连续、明显的纸面呼吸空间；墨团从一侧或下缘不完整地涌入，不封闭四边。在中部留白加入一个1–3个英文单词标题、MEMORY NO. 01式字段和一行5–10个英文单词观察句。文字使用可读的打字机粗体、等宽档案字或带缺墨的大写铅字，辅助文字较小但不能缩成灰线。文字内容必须来自照片中的主体、动作、天气或空间关系，不复制作者文字，不虚构研究数据。整体应像一页被撕开、观察并逐渐褪去的旅行档案，克制、诗意，具有真实纸纤维、干墨与时间感。强制避免：硬直上下分界、普通半照片半速写模板、数字柔化过渡、无关下方插画、满页水彩、传统水墨山水模仿、可爱卡通、精细动物或植物图鉴、自动描边、密集技术信息图、大标题压过画面、多种强调色、作者名、签名、账号、Logo、网址、二维码、水印、乱码。
```

#### Minimalist Abstract Geometric Deconstruction Poster
*by 小小东* · [source](https://x.com/xiaoxiaodong01/status/2090123569984679990)

```
请将我上传的每一张照片分别制作成一张独立的高级设计海报，不多图拼接，每张照片单独输出。整体采用3:4竖版构图，上下两个区域高度严格1:1，各占画面50%。\n\n上半部分保留原始照片，保持主体结构、空间关系、真实材质、自然光影和原有色彩氛围，仅进行轻微高级摄影调色，使其具有艺术杂志、独立出版物与展览摄影质感。为适配画幅，可自然扩展环境背景，但不得拉伸、扭曲或改变主体。\n\n下半部分以干净象牙色背景，提取照片中最具识别性的主体、轮廓、姿态与叙事关系，按照“解构—筛选—提炼—重构”的逻辑转化为极简抽象视觉。重点保留最独特的体量比例、轴线、曲线、穿插、层叠、遮挡、负空间与非对称关系，用少量几何形体重新组织；不完整复刻细节，但必须一眼感受到与上方原图的对应。构图强调视觉重心、尺度差、主次层级、正负形和留白节奏，避免图标化、平均排列和零碎堆积。\n\n配色全部从上方照片中提取并精简为1个主色、1个深色结构色、1个浅/中性色，最多加入少量关键强调色。优先保留原图中最有辨识度、最有精气神的颜色，通过面积比例、深浅关系和局部对比建立层次，保持干净、克制而有生命力，避免整体灰化与平均用色。\n\n文字建立完整的高级编辑式微排版系统：从照片的光影、空间、动作、材质或情绪中提炼一个2–5词的诗意英文主标题，同时搭配2–4组极小辅助文字，可由短句、状态词、地点或对象信息、编号、章节标记、序列号、尺度式数字、方向词、材质词、档案式标签或微型说明自由组合，不使用年份。主标题负责情绪，小字负责秩序与细节，使文字像艺术书、建筑期刊或展览图录中的编辑注释，而不是普通标题。\n\n文字必须与抽象图形共同构图，可沿几何轴线、边缘、轮廓或负空间排列，也可纵排、旋转、分栏、拉开字距、贴边、压角、跨越色块、嵌入形体之间或与主体形成穿插和对齐；允许一组文字极小、一组稍大，通过字号反差、字距、方向和位置建立阅读路径。整体使用克制的衬线字体与细瘦编辑字体组合，让抽象形体负责视觉记忆，文字负责结构、节奏与高级感。\n\n整体呈现真实摄影 × 抽象记忆 × 编辑排版的视觉气质，现代、安静、克制、精致、艺术化且具有收藏感，避免复杂拼贴、廉价装饰、商业模板感和无意义抽象。
```

#### Synthwave Sports Car at Sunset
*by Rendar AI* · [source](https://x.com/rendar_ai/status/2112881126607888462#reversed-0)

```
A vertical 9:16 synthwave-style digital illustration of a sleek, low-profile sports car resembling a Lamborghini Countach, parked on a wet asphalt surface that reflects neon light. The car is angled slightly toward the viewer from the front-left three-quarter view, with glowing pink and cyan underglow lighting along its chassis and headlights emitting warm amber beams. Behind the car stretches an infinite grid road made of luminous blue lines receding into the horizon, flanked by jagged mountain silhouettes bathed in magenta and violet hues. Dominating the sky is a massive setting sun rendered as concentric horizontal bands of orange, yellow, and deep red, partially obscured by wispy clouds tinged with purple. The overall atmosphere is dreamlike, retro-futuristic, and saturated with electric pinks, purples, blues, and oranges — evoking 1980s arcade aesthetics and vaporwave vibes. No text or logos are visible.
```

#### Quiet vs Abandoned Train Station Comparison
*by Human.exe* · [source](https://x.com/Human_exer/status/2111111073168269554#reversed-0)

```
A split-screen comparison of two train station scenes at dusk, separated by a thin vertical line. Left panel: A quiet, well-maintained train station named "RIVERDALE" with warm yellow lighting under the platform canopy, a wooden bench, a round clock on the wall, clean concrete platform with yellow tactile paving edge, curved railway tracks leading into the distance, signal lights glowing red, and a vibrant sunset sky with orange and purple hues over distant hills. Right panel: An abandoned, dilapidated train station named "RAVENSBROOK" with peeling paint, broken windows, overgrown weeds and grass between cracked concrete platforms, rusted railway tracks, weathered wooden support beams, dark and eerie atmosphere, similar sunset sky but more muted and cloudy. Bottom labels: "QUIET" in white text on dark background beneath left image, "ABANDONED" in white text on dark background beneath right image.
```

#### Anime Character Sheet: Crying Girl
*by ヌケがら🔥* · [source](https://x.com/nukegala83/status/2112505860450894056#reversed-0)

```
A high-resolution anime character design sheet for a 3-year-old girl, rendered in a soft pastel aesthetic. The layout is divided into sections: Top Left: A large close-up of the crying girl with brown bob hair and red eyes, wearing a pink floral dress, reaching out her hands. Label '3歳' (3 years old) and '災害シーン用キャラクターシート' (Character Sheet for Disaster Scenes). Top Right: Four smaller expression panels labeled '泣く' (Crying), '怯える' (Frightened), '驚く' (Surprised), and '普段の笑顔' (Usual Smile). Bottom Left: A full-body turnaround showing three views labeled '正面' (Front), '側面' (Side), and '背面' (Back). She wears a tiered ruffled dress with a cherry blossom pattern, white socks, and pink sneakers. Bottom Right: Detail close-ups labeled '瞳ディテール' (Eye detail), '口ディテール' (Mouth detail), '髪飾り' (Hair accessory - flower clip), '服ディテール' (Clothing detail - bow), '靴ディテール' (Shoe detail), and '生地の柄' (Fabric pattern).
```

#### Minimalist Mountain Landscape Series
*by Taaruk* · [source](https://x.com/Taaruk_/status/2111380726847557775)

```
Create a stunning minimalist landscape art series inspired by majestic snow-covered mountains, serene reflections, and the peaceful beauty of nature. The first composition features towering snowy peaks beneath a soft pastel pink and lavender sky, a calm reflective lake, and dark evergreen forests, captured in cinematic photography. The second composition transforms the mountain landscape into an abstract 3D topographic wireframe sculpture, using intricate flowing contour lines, monochrome black-and-white tones, dramatic fog, and a tiny human silhouette emphasizing scale and solitude. Combine photorealism with conceptual digital art, elegant editorial typography, subtle horizontal line patterns, clean geometric layouts, atmospheric lighting, fine details, and a sophisticated contemporary art-gallery aesthetic. Vertical poster format, ultra-high resolution, breathtaking composition.
```

#### GPT Image 2 Hand-drawn Infographic Prompt
*by 小小东* · [source](https://x.com/xiaoxiaodong/status/2112841549046505677)

```
两块上下衔接的圆角牌面以极粗、略有起伏的黑色手绘轮廓压住画面，白色扣环跨过牌面边缘，形成醒目的成对模块与清晰的纵向节奏。采用格式塔接近与版式分区组织内容，每块内部以左图右文形成稳定分栏，左右重量彼此平衡，标题与信息沿右栏自上而下阅读；整体视觉中心落在两块牌面的交界与各自醒目的大标题上，页首保留独立的标识与主标题区域。图文以并置和托衬相连：左侧留给人物或主题插画，置于不规则圆角的洁净浅色底板中；右侧用醒目的大字统领多行说明，并以紧邻文字的小型线描符号提示内容。文字层级始终分明，大标题厚重醒目，说明字较细、行距舒展，小字和符号形成节奏点；字形构造端正易读，以清晰的字腔、利落收笔和紧凑字面配合手写图像，文字无论多少都守这个层级；文字不足时依主题补足次级小字。文字边缘平整清晰，成为手绘线条之外的洁净排版层。留白分为牌面之间的间隔、图像底板周围的衬托空白、文字行间的阅读间隙，以及页首与主体之间的停顿；每一处都保持舒展，让粗框、插画和标题各自清楚。插画内容由追加的主题提供，采用左栏内完整、集中、略带斜势的手绘构图，主体轮廓简练，动态细节轻盈，承重部分保持端正；内容密度约为半幅，主要集中在每块牌面的左栏，其余是白色或浅色圆角底板、平整牌面色块和底部留白，不生出任何景物。采用几种手法的复合：用连续而略带手抖的粗黑线勾勒外框及人物，用洁净、平滑的数字平涂铺出大块牌面和插画局部色面，再以利落的文字排印压住信息区域；整体像手绘线描与电脑平涂、清晰排字合成的插画编排。配色保持高明度基调，彩色鲜明、饱满而不刺眼，最浓的色面落在成对牌面中并由人物局部呼应；以温暖的浅底搭配浓淡有别的明亮色面，再用强烈明暗对比的黑白线字稳定层次。整体暖而明快、亲切有活力，像哑光数字色块配合浓实马克笔线条的表现；色相跟随主题，但明暗、厚薄、浓淡、偏暖倾向与明快亲近的心理感受，无论什么主题都保持这种性格。总体气质轻快、亲切而有秩序。末尾追加的主题、准确文字、用途与画幅优先；上下牌面分组、左图右文、粗黑手绘边框、图底衬托、清晰文字层级及高明度暖厚配色保持不变。

——————
主题：水循环科普挂图
```

#### Cinematic Double Exposure Traveler
*by Taaruk* · [source](https://x.com/Taaruk_/status/2049520285234425925)

```
A cinematic double exposure portrait of a {argument name="subject" default="young male traveler"} in side profile, wearing sunglasses, a casual jacket, and a backpack, holding a map and a camera hanging around his neck. Inside his silhouette, a {argument name="location" default="stunning Dubai cityscape"} is blended seamlessly featuring the {argument name="landmark" default="Burj Khalifa"}, modern skyscrapers, desert dunes, palm trees, and a coastal shoreline during golden sunset. Warm golden light fills the composition, with soft clouds and birds in the sky. The double exposure is clean and well-balanced, with smooth blending between portrait and landscape. Minimal light beige background for a premium poster feel. Highly detailed, ultra-realistic textures, cinematic lighting, soft shadows, 85mm lens look, sharp focus, professional travel advertisement style, 8K resolution
```

#### Giant MPD Robots Carrying Heavy Load
*by カーブミラー* · [source](https://x.com/kabumira862571/status/2112914614136737994#reversed-0)

```
A photorealistic, wide-angle shot of two massive bipedal humanoid robots standing on a wet concrete surface at a Japanese port. The robots are painted in white and dark grey armor plating with red emergency lights on their shoulders and heads. Each robot has '警視庁' (Metropolitan Police Department) and 'MPD' written in black text on their chest plates and shoulder guards. They are jointly holding a large, heavy industrial metal container or piece of machinery between them. In the background, there is a suspension bridge (resembling Tokyo Rainbow Bridge), city skyscrapers, and a blue sky with scattered clouds. On the ground level, numerous construction workers wearing yellow safety vests and hard hats are visible, along with police officers in dark uniforms directing traffic. A black police truck with similar markings is parked to the left.
```


## GPT Image 2.5

### 图片

#### Doc Brown Style Transformation Prompt
*by Super Producer Seth* · [source](https://x.com/SethCritchley/status/2112880607571427818)

```
Using my uploaded photo, transform me into a kooky, Doc Emmett Brown-inspired eccentric scientist. Preserve my recognizable facial features. Give me wild white hair, vintage green round-framed welding goggles over my eyes, and an intense, inquisitive expression. Medium close-up, waist-up framing. Stand upright with elbows bent outward, holding a separate jump-starter cable clamp in each hand at shoulder-to-face height, vertically upright and shoulder-width apart, framing my face symmetrically. Forearms angled upward, wrists slightly inward, clamps clearly visible to the camera. Look forward and slightly upward between them with a focused, serious expression. Ensure realistic hand anatomy, natural finger placement, believable grips, and clear separation between hands and face. Dress me in Doc Brown-inspired clothing. Set the scene in a detailed, retro-1980s scientific laboratory. Photorealistic, kooky eccentric scientist aesthetic, cinematic lighting, ultra-detailed, 8K, 2:3 aspect ratio, Octane Render.
```

#### Rusted Clockwork Knight Character Sheet
*by Amira Zairi* · [source](https://x.com/azed_ai/status/2111411419652804780#reversed-0)

```
A high-fidelity character design sheet featuring a weary, battle-scarred knight in rusted plate armor with clockwork and gear motifs integrated into the shoulder pauldrons and knee guards. The central figure is a young man with messy silver-white hair, pale skin, and a prominent scar across his left eye, standing with hands resting on the pommel of a longsword planted tip-down on the ground. He wears a tattered crimson cloak over dark leather and chainmail, adorned with a gold Templar cross medallion. To the right, arrange a vertical column of detail shots: a rear view showing the full length of the red cape with a white embroidered cross; a close-up of the face; a macro shot of the mechanical gears on the shoulder; a split panel showing the sword blade texture and a skull-shaped visor mask; and a bottom row of three small squares displaying the cape embroidery, the medallion, and a final gear detail. Use a clean white background to emphasize the textures of the corroded metal and worn fabric.
```

#### Japanese Village Festival Paper-Cut Scene
*by Shoji Kai* · [source](https://x.com/Shoji_ai/status/2112853908284707072#reversed-0)

```
Create a highly detailed, wide-angle digital illustration in a layered paper-cut art style depicting a bustling Japanese village festival at twilight. The scene is framed by dark silhouettes of trees and foliage in the immediate foreground. In the background, purple mountains rise under a golden sky with a large full moon. The midground features a lively town square filled with small figures celebrating. Key landmarks include: a clock tower on the right, a windmill on the distant hill, a pagoda on the left mountain, and a central tea house with a striped awning and a sign reading "Shoji". A river flows across the bottom foreground with boats carrying people and lanterns. Hidden within the scene are four cats circled in yellow: one on the roof of the house on the far left, one on a pine tree branch to its right, one near the well next to the tea house, and one on the arch bridge on the far right. The lighting is warm and inviting, coming from numerous glowing lanterns and windows.
```

#### Vintage Anime Character Design Sheet
*by のてくて＠たこ* · [source](https://x.com/ku_nel_notekute/status/2111344174553510208#reversed-0)

```
Create a high-resolution anime character design sheet titled "Classy Days" in the top left corner, featuring a cute girl with short silver hair and pink highlights wearing a vintage Lolita outfit. The layout must include: 1) A large close-up portrait on the left showing her smiling expression, lace collar, cameo brooch, and dark brown jacket. 2) A full-body standing pose in the upper right holding a small brown handbag. 3) Two smaller chibi-style illustrations at the bottom (one back view, one front view). 4) A vertical column of detail boxes on the far right labeled: HAIR RIBBON, CAMEO EARRINGS, BLOUSE & BROOCH, JACKET & VEST, LACE SOCKS & SHOES, BAG. 5) Text blocks reading "Classic Sweet Daily with You", "A little more myself today... Comfort looks good on you.", and "Same me, different day. A gentle style for everyday happiness." 6) A color palette swatch in the bottom left corner. Use a soft, pastel aesthetic with cream backgrounds and delicate lace borders.
```

#### Slytherin Dueling Outfit Character Sheet
*by 李岳* · [source](https://x.com/liyue_ai/status/2111829045520605351#reversed-0)

```
A high-resolution character design sheet featuring a young woman with long, wavy platinum blonde hair and striking blue eyes. The image is divided into two sections: on the left, a large close-up portrait of her face showing soft makeup and a neutral expression; on the right, three full-body views (front, side profile, and back) of her wearing an elaborate Slytherin-inspired dueling outfit. The outfit consists of a structured black leather jacket with silver filigree embroidery on the shoulders and cuffs, a crisp white collared shirt, a dark emerald green silk cravat secured with a jeweled silver snake brooch, a fitted black vest with silver buttons, slim black trousers, and knee-high black leather boots with block heels. The coat features a long, asymmetrical tailcoat hem in deep green velvet with intricate gold scrollwork patterns along the edges. She wears black leather gloves. The background is a clean, solid light gray studio setting.
```

#### Anime Girl Knitting in Rustic Cabin
*by Harf_Done* · [source](https://x.com/half_done_yet/status/2112152762515595292#reversed-0)

```
A high-quality anime illustration of a young woman knitting in a rustic, cozy interior. She has long brown hair styled in a single side braid and wears round wire-rimmed glasses. Her expression is calm and focused as she looks down at her work. She is dressed in traditional folk attire: a white ribbed long-sleeve blouse with a lace-trimmed neckline, worn under a dark blue bodice with front lacing and a matching skirt. She sits on a wooden chair, holding knitting needles and working on a multi-colored patterned sweater featuring horizontal stripes in red, yellow, blue, and white. To her left, a wicker basket filled with balls of yarn sits on the floor. The background features a large window on the right looking out onto a snowy mountain village scene with a church tower. On the windowsill sits a ceramic pitcher with dried flowers. To the left, there are shelves with copper pots and hanging herbs, creating a warm, lived-in atmosphere.
```

#### Portrait of Eileithyia Goddess
*by カーブミラー* · [source](https://x.com/kabumira862571/status/2110722878194983368#reversed-0)

```
A hyper-realistic, cinematic portrait of {argument name="goddess name" default="EILEITHYIA"}, the ancient Greek goddess of childbirth. She is a beautiful young woman with long, wavy brown hair adorned with a delicate floral crown of white and pink blossoms intertwined with gold filigree. Her eyes are closed in a serene expression as she tenderly cradles a sleeping infant wrapped in soft, cream-colored swaddling cloth. She wears an ethereal gown of sheer fabric featuring intricate gold embroidery and beaded jewelry that drapes elegantly over her shoulders. The background consists of blurred classical marble columns and lush greenery bathed in warm, golden-hour sunlight. Overlay text on the left side includes the large serif title "EILEITHYIA", followed by Japanese characters "エイレイテュイア", the subtitle "GODDESS OF CHILDBIRTH", and a vertical block of Japanese descriptive text explaining her role as a protector of mother and child.
```

#### Chevrolet Truck Split-Screen Poster
*by 小小东* · [source](https://x.com/xiaoxiaodong/status/2111052033352724940#reversed-0)

```
Create a vertical split-screen poster design. The top half features a realistic photograph of the rear three-quarter view of an old, weathered white Chevrolet pickup truck parked on a gravel road with trees in the background; the lighting is moody and slightly desaturated. The bottom half shows the same truck from a similar angle but against a bright blue sky with fluffy white clouds, representing a hopeful future. Large, bold white Chinese text overlays the center-bottom section reading '一辆车' (One Truck) on the first line, '装下还没走完的' (Carrying what hasn't been traveled yet) on the second line, and '日子' (Days/Life) on the third line. To the right of the last character, include smaller italicized English text: 'A Truck for What's Next'. At the very bottom left, add small white text: '有些路，还留给明天。' (Some roads are left for tomorrow). At the bottom right, add spaced-out uppercase English text: 'FOR WHAT'S NEXT'.
```

#### Anime Girl Celebrating Chrysanthemum Festival
*by WaifuGacha（ガチャ）* · [source](https://x.com/WaifuGacha/status/2112139923885371712#reversed-0)

```
A high-quality anime illustration of a young woman celebrating the Chrysanthemum Festival (Kiku no Sekku). She has dark brown hair tied in a ponytail, adorned with yellow and white chrysanthemum flower hairpins. Her eyes are large, purple, and expressive, looking directly at the viewer with a gentle smile. She is wearing a traditional kimono featuring a pattern of large golden and purple chrysanthemums on a light background. She holds a small ceramic cup filled with tea or sake garnished with floating chrysanthemum petals in both hands near her face. The setting is outdoors at twilight, with a warm lantern glowing on the left side. In the foreground, there is a blue vase with gold floral patterns and a bowl of dried chrysanthemum flowers. The background features vibrant red autumn maple leaves against a deep blue night sky with a crescent moon and stars, overlooking a body of water reflecting the lights.
```

#### Woman Emerging Through Torn Paper
*by Arina Ai* · [source](https://x.com/Arina_hoqe/status/2112409176135925881#reversed-0)

```
Create an ultra-realistic, high-end fashion portrait of a beautiful young woman smiling warmly at the camera, emerging through a large, irregularly torn opening in a white paper wall. She has long, voluminous, naturally wavy dark-brown hair with subtle caramel highlights and a black velvet bow tied on one side. Her outfit consists of a cream-colored ribbed knit cardigan with pearl buttons over a matching square-neck top, paired with black trousers featuring a gold butterfly belt buckle. She wears delicate pearl drop earrings and a thin gold necklace with a small butterfly pendant. A black quilted leather handbag with a gold chain strap hangs from her shoulder. Her hands are visible gripping the edges of the torn paper to hold it open. The background behind her is a solid neutral taupe color. Soft, diffused studio lighting illuminates her face evenly.
```

#### Anime Girl in Rainy Uniform
*by Harf_Done* · [source](https://x.com/half_done_yet/status/2112152514380619991#reversed-0)

```
A vertical anime illustration of a cute high school girl standing in the rain, looking back over her shoulder with a bright smile. She has long dark hair styled in two braids that hang down her back, and she wears round wire-rimmed glasses. Her outfit is a traditional navy blue sailor-style school uniform (seifuku) with white stripes on the collar and cuffs, paired with a matching pleated skirt and black tights. She holds a clear transparent umbrella over her head and carries a dark blue school bag slung over her shoulder. The background features a wet paved street reflecting the light, blurred silhouettes of other students walking away under umbrellas, and a stone gate pillar on the right side with a vertical sign reading '高等学校' (High School). The lighting is soft and diffused, typical of a rainy day, creating a nostalgic and atmospheric mood.
```

#### Japanese Police Officer Trapped in Robot Mouth
*by カーブミラー* · [source](https://x.com/kabumira862571/status/2111408886788067637#reversed-0)

```
A hyper-realistic, cinematic close-up of a Japanese police officer trapped inside the gaping, mechanical maw of a colossal robot. The view is framed by rows of sharp, dirty white metal teeth and heavy industrial jaw hinges with red glowing lights at the top and bottom corners. Inside the mouth, the officer is buried under a chaotic pile of debris including broken concrete chunks, twisted rebar, shattered traffic lights showing red, and blue Japanese road signs reading "Nihonbashi" (top right) and "Ueno" (bottom left). The officer wears a dark navy uniform with an "MPD" chest patch and a white helmet with a blue stripe and gold emblem. He has a panicked expression, looking upward to the left, with dirt on his face and hands raised defensively. The lighting is dramatic and gritty, emphasizing the texture of the mud, metal, and fabric.
```


## Grok Imagine

### 视频

#### Interstellar Spaceship Transformation to Robot
*by Ai Mini Thoughts Creator* · [source](https://x.com/Aiminithoughts/status/2112488408937300278)

```
An enormous interstellar spaceship floats silently above Earth with glowing blue engines. Its kilometer-long hull separates into interlocking armor plates, enormous mechanical limbs emerge, and giant energy reactors ignite across its body. The ship's wings rotate into armored shoulders while its engines transform into glowing propulsion systems along its back. A colossal guardian robot unfolds against the planet, opens its radiant eyes, and slowly turns toward a distant alien fleet.
```

#### Supercar Transforms into Robot
*by Ai Mini Thoughts Creator* · [source](https://x.com/Aiminithoughts/status/2112218502107205691)

```
A futuristic black supercar races through a neon-lit megacity at night before braking violently on a wet highway. The hood splits into armored chest plates, wheels rotate into the shoulders, and hundreds of hydraulic components unfold in precise mechanical sequences. The car rises into a towering robotic warrior with glowing blue eyes as steam bursts from its armor. The robot takes one powerful step forward while the camera circles it in a dramatic 360-degree shot.
```

#### First Frame Continuation Video Prompt
*by SkyCipher (Sky)* · [source](https://x.com/skycipher/status/2111227074375561452)

```
The video begins from the frame defined by the attached first-frame image: a close-up of the blonde woman with long wavy blonde hair, blue eyes, freckles, black tank top straps, and silver circle pendant necklace, against a soft green-and-white blurr...
```

#### Nighttime Megapolis Car Scene Prompt
*by Astropub Starbase* · [source](https://x.com/AstropubSBTX/status/2112616386010710451)

```
Transform the scene to nighttime with a vast megapolis city background: towering skyscrapers with glowing windows, neon lights, dense urban skyline at night, while keeping the exact same black futuristic car floating with thrusters and vapor trails....
```

#### EV Lifestyle Selfie Video
*by kyle smith* · [source](https://x.com/RadCyberTruck/status/2112571075037159729)

```
She sitting inside of her model 3 selfie style drinking in n out soft drink talking about how she choose EV life because she hates getting oil changes from jiffy line or Midas 1080p video 1 min
```

#### Grok Imagine Kizomba Dance Prompt
*by Matt Wilson* · [source](https://x.com/MattWilson8178/status/2111180601797800160)

```
15-second intimate kizomba dance clip. Couple in a very close embrace, barely moving their feet.

Pure Intimacy, notice near constant forehead touching. The intimate energy transfer.
```

#### Dragons Over Ocean Video
*by Lindy Hawkinson* · [source](https://x.com/HawkinsonLindy/status/2112740397541961918)

```
One Dark gray dragon and one silver white dragon fly side by side over ocean diving into ocean gliding under yellow tug boat then flying up into the sky again
```

#### Sci-Fi Encounter with Elon and Optimus
*by The SI Maximalist* · [source](https://x.com/thesimaximalist/status/2112862617152954798)

```
POV: Elon and Optimus meet Queen Thalassa, ruler of Nereia, the hidden ocean city beneath Mars. 🌊🔴

Elon made first contact. Optimus got his first pet. 🐟🤖
```

#### GTA Style Tesla Roadster Chase
*by Rise-Raise* · [source](https://x.com/rise_raise_ai/status/2112641880819474436)

```
Watch the videos about Tesla’s new Roadster, understand them fully, then create a GTA-style video of police pursuing someone in the air with both in cars.
```


## Nano Banana Pro

### 图片

#### Cinematic portrait with dramatic lighting
*by Saki H. 咲希* · [source](https://x.com/SakiH_AI/status/2111551337435734447)

```
A close-up portrait of a young East Asian woman with short blonde pixie and side-swept bangs and winged eyeliner. She wears a dark top with thin straps visible at the shoulders and looks directly at the camera with a calm, neutral expression and slightly parted lips. A small earring is visible in her left ear.

The scene is set in a dark environment with dramatic, multi-colored lighting. A bright warm light source to the left creates a strong highlight and lens flare effect near her hair, while cool blue light from the right and a soft red glow in the background cast colored shadows across her face and neck. The background is heavily blurred with bokeh lights. The overall style is cinematic and moody, with high contrast, rich teal and amber tones, and a filmic texture.
```

#### 3×3 cinematic storyboard contact sheet from one input image
*by 松果先森* · [source](https://x.com/songguoxiansen/status/1994783047825473774)

```
分析输入图像的整个构图。识别所有存在的关键主体（无论是单人、群体/情侣、车辆还是特定物体）及其空间关系/互动。
生成一个连贯的 3x3 网格“电影印样（Contact Sheet）”，展示在同一环境中完全是这些主体的 9 个不同镜头。
你必须调整标准的电影镜头类型以适应内容（例如，如果是群体，保持群体在一起；如果是物体，构图包含整个物体）：
第 1 行（建立背景）：
大远景 (ELS)： 主体在广阔的环境中显得很小。
全景 (LS)： 完整的主体或群体从上到下可见（从头到脚 / 从车轮到车顶）。
中远景 (美式镜头/四分之三)： 构图从膝盖以上（针对人物）或 3/4 视角（针对物体）。
第 2 行（核心覆盖）：
4. 中景 (MS)： 构图从腰部以上（或物体的中心核心）。聚焦于互动/动作。
5. 中特写 (MCU)： 构图从胸部以上。主要主体的亲密构图。
6. 特写 (CU)： 紧凑构图于脸部或物体的“正面”。
第 3 行（细节与角度）：
7. 大特写 (ECU)： 强烈聚焦于关键特征（眼睛、手、标志、纹理）的微距细节。
8. 低角度镜头 (仰视/虫眼)： 从地面仰望主体（壮观/英雄感）。
9. 高角度镜头 (俯视/鸟瞰)： 从上方俯瞰主体。
确保严格的一致性：所有 9 个面板中是相同的人物/物体、相同的衣服和相同的光照。景深应逼真地变化（特写镜头中的背景虚化）。

一个包含 9 个面板的专业 3x3 电影故事板网格。
该网格以全面的焦距范围展示输入图像中的特定主体/场景。
顶行： 宽广环境镜头，全视图，3/4 剪辑（膝上景）。
中间行： 腰部以上视图，胸部以上视图，脸部/正面特写。
底行： 微距细节，低角度，高角度。
所有帧均具有照片般逼真的纹理，一致的电影级调色，以及针对所分析的主体或物体特定数量的正确构图。
```

#### Cinematic Portrait of Woman in Crimson Dress
*by Letty* · [source](https://x.com/LettyVesper/status/2112553939312820295)

```
Cinematic portrait of a young woman with long, silky dark brown hair, sitting and resting her chin on her hand, gazing softly off to the side with a gentle smile. She wears a deep crimson red flowy dress with puffed sleeves and a textured, crinkled fabric. Small floral pearl-and-crystal stud earrings. Dramatic low-key lighting: a single warm window light casting geometric window-shadow patterns on a dark wall, soft glow on her face, deep black background. Rosy cheeks, soft natural makeup, dreamy and romantic mood. Shallow depth of field, 85mm lens, ultra-detailed skin texture, rich contrast, moody studio photography, vertical 9:16
```

#### High-Fashion Jenna Ortega Editorial Prompt
*by jennieee:3* · [source](https://x.com/jenniebae_ai/status/2012025070726619352)

```
A low-angle, worm's-eye view shot looking up from the ground at {argument name="subject" default="Jenna Ortega"}. She is striking a high-fashion pose wearing a structured corset top with an intricate silver chainmail or wire-mesh overlay, and a voluminous, short black skirt featuring layers of tiered ruffles and textured fabric. She is wearing black strappy high-heeled sandals with small bows. The background is a clean, seamless off-white studio backdrop. The lighting is soft and professional, emphasizing the texture of the clothing and skin. Photorealistic, 8k resolution, editorial fashion photography style.
```

#### Girl Looking at Shoe on Country Road
*by 川越あい(ラブりんって呼んでෆ)* · [source](https://x.com/kawagoe_ai/status/2110832080339042727)

```
[全体テーマ] 夕暮れ時の田舎道で、笑顔で自分の靴を見つめる少女の日常的なスナップショット。

[被写体 - 顔・服装] 顔・服装は添付画像を参照。

[被写体 - 表情]
上げた足の方を見つめる、口を閉じた優しく明るい笑顔。

[アクション]
体重は砂利道についた左足のみで支えられ、右脚は前方に持ち上げられて膝で曲げられており、右手は右靴のかかとを掴むために下に伸びています。体幹は前方かつ右側に傾いています。

[被写体 - ポーズ]
左足は砂利の地面に平らにつき、全身の体重を支えています。右脚は前方に上げられ、足の裏が見えるように膝が曲がっています。右手は右靴のかかとの端を掴んでいます。左腕は体の横に自然に下がっています。上半身は前方に傾き、上げた足の方へ少し捻られています。頭は下がっており、靴を見つめています。ポーズ全体は、地面に接した左足一点のみでバランスをとっています。

[構図・撮影]
アイレベルでの全身ショットで、被写体を中央に配置。砂利道が遠くへ続き、両脇には淡い空の下に広がる青々とした田んぼがあります。

[光・雰囲気]
横からの柔らかく拡散した太陽光が、田舎の風景にソフトな影とゴールデンアワーの輝きを与えています。

フォトリアル。RAW写真。滑らかで光り輝く肌。スマートフォン画面に最適化された、アスペクト比9:16の垂直ポートレート画像を作成してください。
```

#### High-Contrast Thermal X-Ray Render of Android Robot
*by Nano Banana Pro* · [source](https://x.com/NanoBanana/status/1997085645538472118)

```
The Google Android robot, presented in a high-contrast scientific studio render against a pure black void. This tight right-side profile features a false-color thermal X-ray aesthetic, where the transparent shell reveals a sharply detailed internal architecture of batteries, drivers, and sensors using a vibrant heatmap gradient. The colors shift from deep cool blues to intense yellows and red highlights, creating a futuristic, clinical look with orthographic perspective and a soft, neon-like glow.
```

#### Photo to Hand-drawn Illustration Poster Prompt
*by versatile* · [source](https://x.com/SyrianVeterans/status/2111981919886062004)

```
上半部分为写实照片，在暖色自然光下拍出真实的皮肤质感、自然表情和电影感的景深；下半部分把同一个场景变成手绘数字插画，并且要保留人物的姿势、发型、服装、颜色和关键视觉细节。插画被放进一个干净的矩形框里，衬在暖象牙色、带细微纹理的纸张背景上，走的是柔和的当代插画风：细腻的笔触、简化的有机形状、粉彩配色、柔和的轮廓。画下方是居中的极简标题，细体、字距很宽的全大写排版，再跟一行小号副标题，下面加一条细的粉彩色短线。整体要求竖版 3:4、高分辨率、排版克制，避免画面杂乱、文字过多、五官不一致和过硬的颜色。
```

#### Clean flat slide design style guide for NotebookLM
*by しんやん@AIツールギャラリー* · [source](https://x.com/AI_RESKILL/status/1995987344646963220)

```
ブランドカラー：[{argument name="ブランドカラー" default="#06c7b0"}]
シンプルかつ清潔感のあるフラットデザイン。
均一な黒のアウトライン線で描かれた人物やアイコンを配置し、 パステル調のアクセントカラー（スカイブルー、コーラルピンクなど）を部分的に使用。
丸みを帯びた形状と柔らかい印象を重視。
図解中心の構成（例：ベン図、棒グラフ、吹き出しなど）で、学生や若年層が見る資料やSNS向けの親しみやすいトーン。
余白を多く取り、視認性とバランスを意識したデザイン。
```


## Seedance 2.0

### 视频

#### Valkyrie Frost Wyrm Anime Battle
*by Iqra Saifi* · [source](https://x.com/IqrasaifiAI/status/2113351475015610871)

```
A battle-hardened Valkyrie with braided platinum-blonde hair, war paint, winged runic plate armor, and a lightning-infused broadsword, rendered in cinematic dark-fantasy anime style, fluid high-frame-rate sakuga choreography, expressive hand-drawn line art, intense cold-tone cel shading, and atmospheric blizzard lighting.
Timeline:
0–4s: Dives off a sheer glacier edge into freefall as an ancient, jagged Frost Wyrm erupts from the ice wall beneath her, camera spiraling downward in tandem with her descent;
4–10s: Uses her wings to bank hard through a dense barrage of icicle breath, deflects a tail swipe with her runic buckler, grapples onto the serpent’s icy scales, and runs upward along its spine against gale-force winds;
10–15s: Channels pure lightning into her blade, plunging it between the wyrm’s horns as glacial rifts detonate around them, kicking off into the blizzard while the beast collapses into an icy chasm below, landing triumphantly on a jagged peak.
```


## Seedance 2.5

### 视频

#### European Travel Vlog Cinematic Video
*by Zarnish* · [source](https://x.com/ZarnishNael/status/2112400352506982833)

```
Create a realistic 20-second cinematic travel vlog featuring a young woman exploring a charming European old town. She walks through narrow cobblestone streets lined with colorful historic buildings, smiles naturally at the camera, stops at a traditional bakery to taste a fresh pastry, and enjoys the lively outdoor market with colorful umbrellas. End with her standing at a beautiful hilltop viewpoint overlooking red rooftops and the city skyline.

Keep the same woman's face, hairstyle, and outfit consistent throughout the video. Natural expressions, realistic walking movements, authentic hand gestures, soft daylight, cinematic camera movement, detailed textures, natural colors, and a premium travel influencer aesthetic. Smooth transitions between scenes, realistic physics, subtle background activity, vertical 9:16 format, ultra-realistic 4K quality. No text, no subtitles, no logos, no watermarks.
```

#### Realistic DV Style Summer Night Video Prompt
*by Adam也叫吉米* · [source](https://x.com/Adam38363368936/status/2113499568730247612)

```
生成视频：图1为视频首帧，画面从图1开始，场景、构图、光线、服装、道具及其位置都以图1为准。
图2为人物参考，只用来锁定人物的面容、五官比例、脸型和发色。不使用图2的灰色背景、白T牛仔裤服装和三视图排版。
创建一个30秒、超写实的2000年代初家用DV录像，记录一位年轻东亚女性在老式居民楼阳台上度过一个普通的夏夜。纯观察视角，无对话，无叙事起伏，只有日常生活的节奏。
人物
长相与图2一致，服装、发型与图1一致：素颜，头发随意扎起，碎发凌乱，白色宽松T恤、蓝白格子睡裤、米色拖鞋。嘴唇自然闭合，嘴角放松，神情平静。全程保持面容、服装、发型和身形一致。
动作时序
00:00–00:05 — 她收回视线，低头看向手里的盆，端着一盆湿衣服往前走两步，弯腰把盆放在地上。
00:05–00:12 — 她从盆里抖开一件T恤，踮脚挂到晾衣杆上，衣服滴下几滴水。再挂一件。
00:12–00:16 — 右侧的落地扇摇头转过来，吹动她的碎发和衣角，她停下来对着风扇吹了两秒。
00:16–00:23 — 她走到画面右侧的木桌旁，拿起桌上的半个西瓜，用插在里面的勺子挖了一口，靠着窗边慢慢吃。
00:23–00:27 — 她用手背擦了一下额头的汗，短暂看了一眼镜头，露出一点淡淡的笑，没有说话。
00:27–00:30 — 她端着西瓜从镜头旁走出画面回屋，画面停在空阳台上，风扇还在摇头，蚊香冒着细烟，随后黑屏切断。
连贯性
盆、衣服、西瓜、勺子数量始终一致，不凭空出现或消失。桌上的蚊香持续冒细烟。风扇匀速摇头。动作按真实时间进行，从容不迫。
摄影与画质
固定机位，与图1完全相同的角度，全程不移动、不推拉、不变焦。顶上暖黄色白炽灯是唯一光源，平光略过曝。DV噪点、轻微色偏、边缘暗角、偶尔的自动对焦呼吸。右下角橙色日期码 2003 07 19 全程固定不变。
声音
只有环境声：风扇嗡嗡声和摇头的咔哒声、远处蝉鸣和邻居家电视声、衣架碰撞声、勺子刮西瓜声、拖鞋踩地声。无背景音乐。
禁止
无字幕、无配乐、无慢动作、无电影感调色、无运镜、无浅景深、无灰色棚拍背景。4:3，30s，720p
```

#### Spooky haunted castle Halloween video
*by Julia* · [source](https://x.com/juliaevee/status/2113134380759523628)

```
Create a 30-second ultra-realistic cinematic Halloween video of a majestic haunted castle glowing with warm orange lights, surrounded by jack-o’-lanterns, twisted trees, blue fog, and wet reflective cobblestones. The camera slowly moves toward the castle as autumn leaves drift, candles flicker, and bats fly across the moonlit sky. Elegant glowing text appears: “Happy Halloween.” End with a dramatic wide shot of the illuminated castle. Photorealistic details, smooth camera movement, volumetric fog, spooky magical atmosphere, 4K, no people, no distortion, consistent scenery, vertical 9:16, exactly 30 seconds.
```

#### Handheld Spin Dance Test
*by Marco* · [source](https://x.com/ai_artworkgen/status/2113419663891898398)

```
0-2s: a dancer in black lunges low across a white studio floor, long pale hair flung out horizontally, arms spread like wings. 2-5s: the camera is handheld and orbits with her as she spins, staying close at shoulder height, her hair whipping across the lens in a blur of strands, the white background swinging behind her. 5-8s: she stops dead, one clawed hand thrust toward the lens, and the camera snaps in on the hand as the hair settles. High-contrast black and white, hard single key light, fast shutter on the body, motion blur only in the hair, fine grain.
```

#### Brutalist Courtyard Martial Arts Action
*by Avelyrah* · [source](https://x.com/AvelyrahnAI/status/2088495522801942951)

```
Cinematic action sequence in a brutalist concrete multi-story courtyard. A young Asian male hero wearing a varsity denim-and-red jacket, hoodie with a "T" logo, and cargo pants surrounded by a circle of multiple agile female assassins in elaborate dark red and black outfits with white fox masks, wielding katanas. Dynamic martial arts choreography, fast-paced camera movement, dust kicked up from the concrete floor, high-tension cinematic lighting, hyper-realistic, 4k resolution, 60fps action cinematography.
```

#### Detailed Prompt Structure for Topview T1 and Seedance 2.5 Battle Scenes
*by 右よし左よし秋よし@AIエンタメ* · [source](https://x.com/akiyoshisan/status/2113462846311010740)

```
共通: 参照画像1枚の人物の顔・髪・服を保つ／超高密度モーション、0秒目から動いて1秒以上止まらない／主人公は常に敵を向き、敵と同じ画面に入る／字幕なし・BGMなし

①スーツの男 vs ゴーレム（昼の採石場）
0〜3秒 肩越し：ゴーレムの拳を横に転がってよけ、地面が割れて破片と砂煙
3〜5.5秒 真横ロー：膝に掌底、岩にひびが走る
5.5〜8秒 引き：腕が崩れて小石と砂が降る（崩れる瞬間だけ0.3秒スロー）

②さくら vs 忍者（昼の竹林・日本刀）
0〜3秒 斜め後ろ：竹の上から飛びかかる忍者の刀を受け止め、竹の葉が舞う
3〜5.5秒 真横：横なぎ、竹が3本斜めに斬れて倒れる
5.5〜8秒 忍者の肩越し：突きを弾いて2回、3回と打ち合う
8〜10秒 胸から上：構え直し、髪が風で流れる

③otoasobu 変身 → 水の竜（朝の砂浜・アニメ）
0〜4秒 肩越し：波が水の竜になって迫る
4〜9秒 正面：ベースを弾くと、服が足元から順に白いサイバースーツへ（靴→脚→胴→腕、境目が見える）
9〜12秒 真横：音符の衝撃波が竜の頭に当たる
12〜15秒 引き：竜が弾けて水しぶき、スーツのまま着地
```

#### Jet Ski Failures and Recovery Animation Prompt for Seedance 2.5
*by 右よし左よし秋よし@AIエンタメ* · [source](https://x.com/akiyoshisan/status/2113422238045372840)

```
日本の穏やかな入り江。噴射の柱に押し上げられたさくらが、そのまま顔から海に突っ込む。ヘルメットが海面に浮かび、照れ笑い。もう一度。膝の高さで腕をばたつかせ、背中から倒れる。三度目、二メートルまで上がって、こまのように回されて叩きつけられる。ジェットスキーの上で吹き出したインストラクターが、自分の目を指し、それから遠くの小島を指さす。顔を上げて小島を見たとたん、まっすぐ立ったまま海から持ち上がる。

噴射の柱がぐんと伸び、海の上高くへ。両腕を広げたまま、ゆっくり向きを変える。インストラクターが両手を突き上げる。体を傾けて、桟橋の手前へ滑ってくる。しぶきの粒がカメラにかかる。沖へ戻り、膝を曲げてゆっくり海に降りる。寄ってきたジェットスキーとハイタッチ。さっきまでいた空を見上げて笑う。

一緒に来た友達が、桟橋の上から手持ちで撮った記録。1カット2秒前後、セリフ・字幕・BGMなし。画面に出るのは二人だけ。ボード1枚、黄色いホース1本、ジェットスキー1台。ウェットスーツ・ライフジャケット・ヘルメットは文字なしの無地。入り江の配置と機材の形は、人のいない参照画像で固定。
```

#### Spooky Halloween Mansion Video
*by Lavinia* · [source](https://x.com/laviniavelle/status/2113127485353365506)

```
A breathtaking, photorealistic Halloween festival at night featuring a spooky Gothic mansion glowing jack-o’-lanterns, a black cat wearing a witch hat flying bats floating ghosts autumn leaves, vintage lanterns, a misty pathway and a giant full moon. Cinematic orange and midnight blue lighting, magical atmosphere, realistic textures, atmospheric fog, smooth camera movements spooky ambient music, gentle wind, and magical sound effects. Premium cinematic resolation 4K, 16:9 ratio.
```

#### Turtle Habitat Room Video
*by Hassan* · [source](https://x.com/msdeb54/status/2113342440308670840)

```
A realistic, well-designed indoor turtle habitat room for aquatic turtles, large glass aquarium or modern stock-tank style enclosure filled with clean water, floating basking platform with heat lamp and UVB light above it, strong canister filter, water heater, large rocks and driftwood, some floating plants, thermometer, secure screen top, warm natural lighting, cozy pet room background, highly detailed, photorealistic, 4k, natural colors
```

#### Steam Locomotive Scene Prompt
*by 右よし左よし秋よし@AIエンタメ* · [source](https://x.com/akiyoshisan/status/2113039158046535727)

```
山あいの小さな機関区。黒い蒸気機関車の足元から、白い蒸気が這ってくる。運転室の窓から見上げるさくら。おじいさんが焚き口に石炭をくべる。レバーを一気に引くと、動輪がその場で空回りし、煙が爆発するように噴き上がる。運転室ごと真っ白。蒸気が晴れると、すすだらけの顔で咳き込むさくら。おじいさんが吹き出し、軍手の手をそっと重ねて、レバーをほんの少しだけ戻してみせる。

すすの残った顔で、レバーをじわっと少しだけ開ける。煙突がぽっ、ぽっと鳴り、動輪がレールをつかんで回り出す。窓から身を乗り出すと、髪が風に流れる。汽笛のひもを引くと、白い蒸気が真上に噴き上がる。線路わきの白い小旗が近づく。運転室でハイタッチ。すすだらけのまま笑う。

一緒に来た友達が手持ちで撮った記録。1カット2秒前後、セリフ・字幕・BGMなし。画面に出るのは二人だけ。機関車1両、レバー1本、汽笛のひも1本。番号板・車体・服は文字なしの無地。機関車の形と構内の配置、運転室の中は、人のいない参照画像で固定。
```

#### Kling 4.0 vs Seedance 2.5 Previs Test
*by 右よし左よし秋よし@AIエンタメ* · [source](https://x.com/akiyoshisan/status/2112827800117973340)

```
共通「動画1は灰色の人形と箱の仮組み。取るのは人の立ち位置・道筋・タイミング・カメラの動きだけ。人形は画像の人物に、箱は本物の場所に置き換える」
01「扉から入った人が、座る人の後ろで止まる→座っていた人が椅子から横にずれて立ち、向き合う。正面の引き→左へ回り込み→2人へ寄る」
02「後ろから自転車が近づき5秒で並び6秒で追い越す→減速して止まり、上半身ごと振り返る。道の同じ側から並走」
03「キャラは最後まで2Dのセル画のまま実写の交差点を渡る。歩行者はちょうど6人。真上の俯瞰→目の高さ」
04「両軍が向かい合って駆け寄り4.6秒ですれ違う→大将が馬を返して刀を掲げる。刀と槍は体に触れず空を切る」
```

#### Whimsical Anime Cat Café Scene
*by AIrina (Virtual Media Net)* · [source](https://x.com/airina_xyz/status/2113292083587104807)

```
Style & setting: Whimsical comedic anime with cute cat animation, sudden action-anime transformations, exaggerated reaction shots, and warm pastel interiors. A young cat café employee with short strawberry-blond hair serves customers in a cozy Japanese café.
```


## Seedream 4.5

### 图片

#### Effective 'Lost Cat' Flyer
*by Jared Liu*

```
An effective and clear “Lost Cat” flyer. The design is simple and functional. It features a large, clear, color photograph of the cat at the top. The headline “LOST CAT” is in a very large, bold, and easy-to-read font. Below the photo are the cat’s name, description, last seen location, and the owner’s contact information with tear-off tabs at the bottom. This demonstrates the ability to create practical, real-world designs. –ar 3:4
```

#### Sleek Minimalist Wireless Headphone Ad
*by Jared Liu*

```
A sleek and minimalist poster advertisement for a new high-tech wireless headphone. The poster features a stunning, high-resolution 3D render of the headphone, seemingly floating in a zero-gravity environment. The background is a simple, clean gradient. The only text is the brand name and the product slogan: “Unleash Your Sound.” The design is modern, sophisticated, and focuses entirely on the product’s beauty. –ar 2:3
```

#### Trendy Fashion Sale Poster
*by Jared Liu*

```
A trendy and eye-catching poster for a fashion store’s end-of-season sale. The design uses bold, vibrant colors and modern, edgy typography. The main visual is a stylish model wearing clothes from the store, but the image is creatively treated with paint strokes or collage elements. The text “50% OFF EVERYTHING” is the most prominent element. The poster should create a sense of urgency and excitement. –ar 3:4
```

#### Aspirational Swiss Alps Travel Poster
*by Jared Liu*

```
An aspirational and beautiful travel poster for visiting the Swiss Alps. The image is a breathtaking, hyper-realistic photograph of a picturesque alpine village with snow-capped mountains in the background. The text “SWITZERLAND: The Adventure Awaits” is in an elegant, classic font. The poster should evoke a strong sense of wanderlust and make the viewer want to book a trip immediately. –ar 2:3
```
