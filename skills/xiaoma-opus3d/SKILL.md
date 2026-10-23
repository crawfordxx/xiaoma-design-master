---
name: xiaoma-opus3d
description: 用 three.js 纯代码（不用任何 3D 模型、贴图、照片）程序化搭建一整片建筑场景——古镇、寺庙、园林、街区、景区、村落、港口——并交付一个可以嵌入任何网页的交互式 3D 模型：鼠标/触摸拖动旋转、滚轮/双指缩放、右键平移，打包成可直接双击打开或用 iframe 嵌入的单个 HTML，外加一个 script 挂载版。方法是：先出 layout.js 平面图并用脚本检查碰撞，再写公共生成器和材质，然后派多个子 Agent 并行各建一个区块、各自截图对比，最后定交互视角、做画质分级、打包并测试。只要用户想用 three.js / WebGL / 代码生成一个有多栋建筑的 3D 场景、做可拖拽缩放的场景模型、把某个景点做成可嵌入网页的 3D 模型、或者提到“平面图 + 分区块 Agent”这类流程，就使用本 skill，即使用户没说“程序化”。需要导出漫游视频时也适用（见附录）。不适用于：单个物件建模、加载 glTF 的项目、2D 动画、AI 文生视频。
---

# xiaoma-opus3d：平面图 → 分区施工 → 截图对比 → 交互模型 → 打包嵌入

交付物是一个**可以嵌进网页、能拖动旋转和缩放的 3D 模型**：

| 文件 | 用法 |
|---|---|
| `dist/scene.html` | 自包含单文件（three.js 和场景全部内联），双击就能打开，或 `<iframe src="scene.html">` 嵌入 |
| `dist/scene-embed.js` | `<div data-scene='{...}'></div><script src="scene-embed.js"></script>` 挂到任意 div |
| `dist/embed-demo.html` | 两种嵌法的演示页，交给用户时一起给 |

这套流程能让多个 Agent 合力搭出一个经得起近看的大场景，靠的是四条约束：

1. **坐标只有一个来源**：所有位置都从 `layout.js` 读，并用脚本检查过。没有平面图，各 Agent 各建各的，塔会建进池塘里。
2. **每个文件只有一个主人**：子 Agent 只改自己的区块文件；公共件只有主 Agent 改。
3. **画面只由时间决定**：固定种子随机数，动画是 t 的纯函数。截图对比才可重复；交互模型里光照（`lightT`）和动画（`animT`）也能分开控制。
4. **每一步都有验收**：平面图有检查脚本，区块有截图对比，交互模型有自动测试。

你（主 Agent）负责第 0、1、2、4、5 阶段和全部公共件；第 3 阶段派给子 Agent。

先读 `references/pitfalls.md`，那是实战里真踩过的坑，能省下大量排查时间。

## 第 0 阶段：定参数

和用户确认这几项（用户已经给了的就不要再问）：

| 参数 | 例子 |
|---|---|
| 主题和范围 | 乌镇西栅一段 240m×160m 的十字河口，不做整个景区 |
| 时段和光线 | 日落后、灯笼刚亮；太阳方位 260°，高度约 2° |
| 区块清单 | 6 个：地形 / 水和船 / 桥 / 北岸 / 南岸 / 地标 |
| 公共生成器 | 大量同类物件（民居）要不要参数化生成器 |
| 值得近看的细节 | 灯笼穗、望柱石刻、蓝印花布……决定哪些区块要做到经得起贴近看 |
| 目标设备 | 只在电脑上看，还是也要手机流畅（决定性能预算） |
| 参考图 | 用户给的照片；没有就写一份“参考特征”描述 |

范围宁小勿大：一个细节密、处处经得起近看的代表性片段，比一个稀疏的全景好得多。

**过关条件**：用户确认了区块清单和目标设备。

## 第 1 阶段：搭项目、出平面图

```bash
P=<项目目录>; S=<本 skill 目录>
mkdir -p $P/scripts && cp -r $S/assets/template/* $P/ && cp $S/scripts/* $P/scripts/
cd $P && npm init -y && npm pkg set type=module && npm i three@0.170.0 playwright@1.49.1 && npm i -D esbuild@0.24.0
node scripts/gpu-check.mjs           # 确认无头浏览器拿到的是真 GPU
```

`npm i` 卡住不动时，先看 `node_modules` 里是不是已经装好了（见 pitfalls.md“环境”）。

然后写 `src/layout.js`（约定见 `references/layout-schema.md`）：
- 独特建筑逐个写；成批的同类建筑写“排”的定义，用固定种子展开成逐栋记录，每条带 `footprint`。
- 运动物体写路径和速度。
- 从内容数据推导出 `CHECK`（实体、禁区、碰撞体、路径、`floorAt`），项目特有规则写进 `extraChecks()`。
- 写 `viewer`：场景名、光照时刻、初始视角、最近和最远距离。

```bash
node scripts/check-layout.mjs        # 不过就改 layout，直到通过
node scripts/plan-svg.mjs && node scripts/svg2png.mjs plan.svg out/plan.png   # 用 Read 看图
```

交互模型可以从任何角度看，所以要特别留意两件事：
- **区块内的大片空地**：登记成填充区，交给某个区块用低精度建筑群填满。
- **场景边界**：远景要一直铺到相机拉到最远时也看不到边，`viewer.maxDistance` 要和远景范围匹配。

**过关条件**：check-layout 通过；平面图给用户看过。

## 第 2 阶段：公共件（派活前必须完成）

主 Agent 写这些，子 Agent 只读：

| 文件 | 内容 |
|---|---|
| `src/materials.js` | 全局材质，Canvas 程序化纹理，UV 按米。发光物亮度统一由 `setGlowLevel` 控制 |
| `src/shared.js` | 公共生成器。场景里有大量同类物件、又会分给多个 Agent 时必须写，否则风格对不上 |
| `src/lighting.js` + `src/sky.js` | 模板已有：自写渐变天空、太阳、天光、雾、环境贴图、少量点光源 |
| `src/zones/index.js` | 区块注册表（静态 import，打包需要）；`src/zones/_ground.js` 等临时背景区块 |
| `scripts/views.mjs` | 截图机位：俯视 + 每个区块至少一个人眼高度（1.6m）机位 + 每个近看细节一个特写机位 |
| `BRIEF.md` | 从 `references/brief-template.md` 填出来的施工规范，**含实时性能预算** |

`src/scene.js`（场景核心、画质分级）、`src/viewer.js`（交互）、`src/main.js`（截图测试入口）、`src/embed.js`（打包入口）模板里已经写好，一般不用改。

**公共生成器先自测再派活**：写一个临时区块把所有实例生成出来，截近景、中景、俯视各一张，用 Read 看图，确认比例、细节密度、颜色。好几个 Agent 都依赖它，它有 bug 就是好几份返工。

**过关条件**：`node scripts/shot.mjs --zones _ground,<临时测试区块> --views top,<近景机位>` 出图正常、没有 errors。

## 第 3 阶段：分区施工（并行子 Agent）

一条消息里同时派出所有子 Agent（`run_in_background: true`），每个 Agent 的 prompt 包括：
- 先读 BRIEF.md、layout.js、要用的公共件。
- 只能写 `src/zones/<区块>.js`、`review-<区块>.md`、`out/shots/<区块>/`。
- 具体要做的东西，以及本区块负责的**近看细节**（“望柱头 0.5m 距离不穿帮”）。
- **实时性能预算**（BRIEF.md 里写的 draw call、三角形上限），以及“交互模型可以从任何角度看，背面、侧面和高处俯视都要过得去”。
- 截图对比：`shot.mjs` 截俯视（检查位置）+ 人眼视角（检查比例、颜色、细节），最多 3 轮，写进 review。
- 完成标准，以及汇报格式：做了什么、draw call 和三角形数、近看细节的世界坐标、发现的公共件问题（只报告不改）。

施工期间你要做的：
- **处理公共件问题**：Agent 报告后由你改，改完通知正在用它的 Agent，并说明“不要在自己的文件里补偿”。
- **转达跨区块衔接**：比如“桥宽范围内压顶石断开了，桥台要贴岸落地”。Agent 之间互相看不到对方的文件。
- 调天空和曝光，这些归你管。
- 某个区块先完成后，告诉还在做的 Agent 最后一轮截图可以换上真实区块。

**过关条件**：所有区块状态 ok、没有 errors；全部区块合在一起截一轮，没有明显的衔接问题。

## 第 4 阶段：交互视角与画质

1. **初始视角**：一眼能看懂整个场景的高位斜视，最好顺着主要光线方向，让剪影和亮灯都看得到。写进 `layout.viewer.view`。
2. **视角限制**：`minDistance` 要能推到近看细节；`maxDistance` 不能拉到看见场景边界；`CHECK.floorAt` 不让相机钻进地下或水下（`viewer.js` 已经接好）。
3. **光照时刻**：交互模型里光照固定在一刻（`viewer.time`），挑最好看的那一刻，比如灯笼刚亮、天还没黑。
4. **画质分级**：`scene.js` 里有 high / medium / low 三档（像素比、MSAA、阴影、bloom、反射）。`quality: 'auto'` 时手机从 low 起步、电脑从 high 起步，帧率持续低于约 40fps 自动降一档。有区块自己做了昂贵效果（反射、体积雾）时，要让它在低档能关掉。
5. **全场景 NaN 回归**：`node scripts/nan-test.mjs '' 200`。交互时相机会去到任何位置，比固定镜头更容易撞上 NaN。报失败的机位要截图确认（深色材质在阴影里也会读出纯黑）。

调交互时起一个本地服务：`node scripts/serve.mjs 5173`，然后打开 `http://127.0.0.1:5173/viewer.html`。

**过关条件**：初始视角截图给用户看过；nan-test 的失败项都确认过；拉到最远、推到最近、贴地平视都没有穿帮。

## 第 5 阶段：打包与测试

```bash
node scripts/build.mjs          # → dist/scene.html、dist/scene-embed.js、dist/embed-demo.html
node scripts/test-viewer.mjs    # file:// 打开单文件，在像素比 1 和 2 下测：尺寸、拖动、缩放、平移、画质切换、帧率
```

用 Read 看 `out/viewer-test/` 里的截图。开发机（比如 M 系列 Mac）上的帧率不代表普通设备：用户要求手机流畅时，要守住 BRIEF 的预算，并在 low 档实际看一眼画面能不能接受。

**过关条件**：test-viewer 全部 ✓；在用户的浏览器里打开 `embed-demo.html` 确认能用。

**要开源到 GitHub 时（可选）**：README 不能运行 WebGL，交互模型放到 GitHub Pages 上，README 里用两样东西展示：
- 顶部放一张预览动图（相机绕场景转一圈），链接到 Pages 上的 `scene.html`。
- 按附录导出一段漫游视频。README 里的 `<video>` 标签会被 GitHub 过滤掉，能出播放器的只有网页上传的视频附件：压到 10MB 以内（免费账号上限），在任意 Issue 或评论框里上传（不用提交），拿到 `https://github.com/user-attachments/assets/…` 地址后单独一行贴进 README。再放一个清晰版到 `docs/`，附直接打开的链接兜底。

## 交付时告诉用户

- 三个文件分别怎么用（iframe、script、演示页），以及可用参数：`quality`、`time`、`hint`。
- 操作方式：左键拖动旋转、滚轮缩放（朝鼠标位置推进）、右键平移；手机单指旋转、双指缩放和平移。
- 文件大小、加载时间、在哪些设备上测过。
- 已知的不完美之处，以及和用户原始要求不一样的地方。
- 改场景后怎么重新打包：改 `src/` → `node scripts/build.mjs` → `node scripts/test-viewer.mjs`。

## 附录：导出漫游视频（可选）

用户另外要视频时：在 `src/cameras.js` 里排“特写 → 拉远”的镜头，依次跑 `check-cameras.mjs`（路径穿模）→ `contact.mjs`（接触表）→ `render.mjs --verify`（确定性）→ `render.mjs`（逐帧渲染、ffmpeg 合成 mp4）。镜头语法见 `references/camera-grammar.md`。

## 文件索引

| 路径 | 什么时候读 |
|---|---|
| `references/pitfalls.md` | 开工前读一遍；出问题时按阶段查 |
| `references/layout-schema.md` | 写 layout.js 时 |
| `references/brief-template.md` | 写 BRIEF.md 时 |
| `references/camera-grammar.md` | 只在要导出视频时 |
| `references/examples/wuzhen.md` | 完整实战：区块划分、交互模型参数、改动轨迹 |
| `references/examples/temple.md` | 原版寺庙提示词怎么映射成参数 |
| `assets/template/` | 项目骨架，第 1 阶段复制 |
| `scripts/` | 复制到项目的 scripts/。交互模型用：gpu-check、serve、browser、shot、views、check-layout、plan-svg、svg2png、montage、nan-test、build、test-viewer；视频附录另用：check-cameras、contact、render |
