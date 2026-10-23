# 代码规则与引擎参考

## 为什么不用 Remotion / AE / 视频生成模型

样本里的作者普遍发现：不指定框架时，Opus 5.5 倾向于零依赖、从头写一个 `index.html`，用无头浏览器逐帧截图，再交给 ffmpeg 编码（Tommy Rossi 的复盘；Vincent 用的是 WebGL / Canvas 逐帧加 NumPy 合成音乐）。这条路依赖最少，任何模型都能写，也最可控。本 skill 把它固化成 `runtime.js` + `render.mjs`。

已经在用 Remotion / HyperFrames 的项目照样适用本 skill 的审美和流程规则，只把渲染层换掉即可。

## 合成文件骨架

```html
<link rel="stylesheet" href="engine/base.css">
<link rel="stylesheet" href="engine/themes.css">
<div id="stage" class="theme-museum">
  <canvas id="cv" class="layer"></canvas>       <!-- 证据、粒子、图表 -->
  <div class="caption" id="cap">…</div>         <!-- DOM 放文字 -->
  <div class="vignette"></div><div class="grain"></div>
</div>
<script src="engine/runtime.js"></script>
<script>
MS.setup({ width: 1920, height: 1080, fps: 30, duration: 24, bpm: 80, background: '#0b0a08' });
MS.render((t) => {
  MS.shots(t, [[0, opening], [5.6, evidence], [20.4, ending]]);  // 镜头内容
  globalLayers(t);                                               // 跨镜头的层：每帧都要处理
});
</script>
```

浏览器直接打开 = 预览器（空格播放，← → 逐帧，Shift+← → 逐拍，`?t=7.5` 定位到指定时刻）。加 `?render=1` 是渲染模式。

## runtime API（`MS.*`）

| API | 说明 |
|---|---|
| `setup({width,height,fps,duration,bpm,beatOffset,background})` | 全片参数 |
| `render(fn)` | 注册 `fn(t)`；可以是 async（比如等视频 seek） |
| `shots(t, [[start, fn(t, lt, dur)], …])` | 按时间分镜，返回当前镜头下标 |
| `prog(t, a, b, ease)` | 区间进度，带缓动，区间外夹到 0 / 1 |
| `ease.*` | linear, in/out/inOut Quad / Cubic / Quart / Expo / Back, outElastic |
| `spring(t, t0, {stiffness, damping, mass})` | 闭式阻尼弹簧，0→1 |
| `springTo(t, init, [[t0, v], …])` | 多目标弹簧叠加 |
| `lerp / invLerp / clamp / mix` | 基础数学 |
| `rng(seed)` / `hash(i, seed)` / `noise(x, seed)` | 确定性随机：mulberry32、整数哈希、平滑一维噪声 |
| `beat(n)` / `beatOf(t)` / `beatLen()` / `pulse(t, decay)` | 节拍网格 |
| `$ / $$ / css(el, styles) / show(el, bool)` | DOM |
| `split(el, 'chars' / 'words')` / `reveal(el, t, t0, opts)` | 逐字动画；`style: rise / fade / blur`，`out` 可设退场时刻 |
| `typewriter(str, t, t0, cps)` / `counter(t, a, b, from, to, opts)` | 打字机、数字滚动 |
| `canvas('#id')` | 取 2D 上下文并清屏（处理了 DPR），返回 `{ctx, w, h}` |
| `drawPath(ctx, pts, p)` | 按长度比例描出折线 |
| `videoAt(video, time)` | 视频素材精确 seek（await） |
| `ready(promise)` | 首帧前要等的东西（数据、图片、字体） |

## 渲染 CLI（`engine/render.mjs`）

```bash
node render.mjs comp.html --sheet out/sheet.jpg [--every beat|1|0.5] [--max 48]   # 拼图，带时间戳标签
node render.mjs comp.html --stills 2.5,7,12.25 --dir out/stills                    # 原尺寸静帧
node render.mjs comp.html --out out/v.mp4 [--fps 60] [--subframes 2] [--audio a.wav] [--from 3 --to 8] [--crf 16]
node render.mjs deck.html --slides out/slides --pdf out/deck.pdf                   # 幻灯片
```
- `--subframes N`：每帧渲染 N 个子帧，用 ffmpeg `tmix` 混合成运动模糊。60fps 用 2，30fps 用 4。
- `--scale 0.5`：半分辨率，快速预览。
- 编码固定为 H.264 / yuv420p / CRF 16 / faststart，各平台都能直接上传。

速度参考（M 系列 Mac）：1080p 30fps 的 24 秒片约 40 秒；60fps 加 2 子帧的 12 秒片约 3 分钟。

## 体检（`engine/qa.py`）

报告规格、响度、单帧跳变（某帧变化量是邻居的 3 倍以上）和静止段（变化像素低于 0.05%、持续 ≥ 2 秒）。跳变通常意味着元素提前或晚了一帧出现，或者转场层级错了；静止段说明违反了「每 2–4 秒有新事」。

## 自动检查（`engine/lint.mjs`）

不需要看图，专门抓三类问题：
- **确定性**：同一批时刻先顺序渲染、再打乱顺序渲染，像素不一致就说明有帧间状态。典型原因是坑 1 的残留层：上一个镜头的标题只在自己的镜头里淡出，跳着 seek 时一直挂在画面上。
- **对比度**：把文字设成透明后截图，取文字框内背景像素的平均亮度，和文字颜色比较。大字要求 ≥ 3:1，小字要求 ≥ 2:1。典型问题是「亮底页忘了改字色」。
- **重叠**：两个可见文字块相交面积超过较小者的 25%。

装饰性的元信息（放在 `.hud`、`.meta` 或带 `data-decor` 属性的元素里）允许很淡，不参与检查。canvas 里画的字不在检查范围内。

## 坑（都是真实踩过的）

1. **残留帧**：只在镜头 A 里画的 canvas，seek 到镜头 C 时还留着 A 的最后一帧。拼图是跳着渲染的，最容易暴露这个问题。修法：跨镜头存在的层放在 `shots()` 之外，每帧都画或清空；或者在每个镜头函数里显式隐藏不属于它的层。
2. **转场层级**：泛洪如果画在底层，盖不住上层的旧元素，它们会在拍点上突然消失（单帧跳变）。泛洪 / 擦除要画在内容之上的独立层；新场景的元素等转场铺满后再入场。
3. **泛洪半径**：必须大于画面对角线（`Math.hypot(W, H) * 1.05`），时长约 0.3 秒，否则角落会晚一帧被盖住。
4. **CSS transition / animation**：浏览器会按真实时间播放它们，和 seek 无关，渲染出来全是错帧。`base.css` 已经全局禁用，不要在合成里重新打开。
5. **Math.random()**：每次 seek 结果都不一样，画面会闪。一律用 `MS.hash(i)` / `MS.rng(seed)`。
6. **字体**：渲染前会等 `document.fonts.ready`。国内网络别依赖 Google Fonts，用本地字体栈（`themes.css` 已经配好），或者用 `@font-face` 引本地字体文件。canvas 里写字要用和 DOM 相同的字体名。
7. **视频素材**：最稳的做法是用 `ffmpeg -i clip.mp4 -vf fps=30 frames/%04d.jpg` 拆成 JPEG 序列，每帧换 `img.src` 并 `await img.decode()`（twoclipping 的 UGC 广告就是这样做的）。其次是先 `ffmpeg -i in.mp4 -g 1 -an all_intra.mp4` 转全帧内编码，再用 blob URL 或本地文件加载，并且 `await MS.videoAt(v, t)`。`python -m http.server` 不支持 range 请求，没法 seek。
8. **backdrop-filter 做液态玻璃**：Chromium 对 `backdrop-filter: url()` 的位移贴图支持有问题。做法是让玻璃元素持有一份它背后场景的克隆，对克隆用 SVG `feDisplacementMap`（twoclipping 的经验）。
9. **visibility**：子元素设了 `visibility: visible` 时，父元素隐藏了它也照样显示。用 `display:none`（`MS.show`），或者子元素用 `inherit`。
10. **逐字拆分只拆一次**：`MS.split` 会把结果缓存在元素上。换文字时要先清掉 `el.__msSplit = null`（字幕轮换时）。
11. **canvas 清屏**：`MS.canvas()` 每次调用都会清屏。同一帧里不要对同一个 canvas 调用两次。
12. **大量 DOM 节点**：上千个点用 canvas 画，不要用 div。
13. **颜色也要过渡**：形状从白卡片变成黑 toast 时，如果 `background` 直接取「当前状态的颜色」，就会在一帧内跳变，`qa.py` 会报单帧跳变。颜色和尺寸一样，要在 0.2–0.3 秒内插值（见 `examples/launch-morph` 的 `bgAt`）。

## 性能

- 渲染瓶颈在截图，不在你的代码。单帧 JS 控制在 30ms 以内就行。
- 粒子超过 5000 个、需要真 3D 或着色器时，用 WebGL / Three.js（自己通过 `<script>` 引入），一样遵守 seek(t)：相机和物体的状态都从 t 算出来。
- 4K 用 `--scale 2`（deviceScaleFactor），合成坐标照样按 1920×1080 写。
