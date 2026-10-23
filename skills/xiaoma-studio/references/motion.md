# 动效语法

下面的代码都基于 `engine/runtime.js`（全局 `MS`）。`t` 是全片时间，`lt` 是镜头内时间。

## 缓动怎么选

| 场景 | 缓动 |
|---|---|
| 元素入场、文字升起 | `outCubic` / `outExpo`（快进慢停） |
| 元素退场 | `inCubic`（慢起快走） |
| 镜头移动、形变、泛洪 | `inOutCubic` / `inOutQuart` |
| 弹出、落地、图标、数字跳动 | `MS.spring()`（过冲回弹） |
| 卡点的「砸」 | `outBack`，或 0.12 秒的 `outQuad` 加运动模糊 |
| 匀速 | 只用于跑马灯、星空漂移、时间码 |

几乎没有东西是匀速运动的。直接 `lerp` 看起来很机械，要先过一道缓动。

## 弹簧

```js
const s = MS.spring(t, 2.0, { stiffness: 300, damping: 14 }); // 2.0 秒起跳，0→1，会过冲
css(el, { transform: `scale(${s})` });
// 一个值依次去多个目标：每次变化各自叠一个弹簧，仍然是 t 的纯函数
const x = MS.springTo(t, 0, [[1.0, 200], [2.5, -80], [4.0, 0]]);
```
stiffness 越大越快，damping 越小越弹。小图标用 300/14，大面板用 170/22，「重」的东西用 120/26。

## 转场目录（按样本里的出现频率）

**1. 泛洪 flood**：一个圆（或品牌形状）从某点扩满全屏，成为下一个场景的底色。
```js
// 画在内容之上的独立 canvas；半径要超过对角线；约 0.3 秒，在拍点刚好铺满
const p = MS.prog(t, beat(8) - 0.32, beat(8), MS.ease.inOutCubic);
octx.fillStyle = next; octx.beginPath(); octx.arc(x, y, p * Math.hypot(W, H) * 1.05, 0, 7); octx.fill();
```
反向用法：满屏收缩成下一个场景里的一个点 / 胶囊。

**2. 形变 morph**：A 形状直接变成 B。把两个形状都采样成同样数量的点（如 120 个），逐点插值。圆 → 方 → 三角 → 星，字母 → 图标，胶囊 → 窗口。实现见 `examples/swiss-reel` 的 `circle/polygon/star/morph`。DOM 元素可以插值 `border-radius`、`width`、`height`、`clip-path: polygon(...)`（两端的点数要相同）。

**3. 遮罩升起 mask rise**：文字从一条看不见的线下面升起。
```html
<span class="mask"><span id="w">EVERY</span></span>
```
```js
MS.reveal($('#w'), t, 2.0, { stagger: 0.04, dur: 0.45, style: 'rise', e: MS.ease.outExpo });
```

**4. 推镜穿越 camera push-through**：镜头推进上一场景里的某个物件（一幅画、一个格子、一个屏幕），它变成下一个场景。Blackwell 那条从机房一路推到原子，全程不切。
```js
css(world, { transform: `translate(${-fx}px, ${-fy}px) scale(${Math.pow(40, MS.prog(t, a, b, MS.ease.inOutCubic))})`, transformOrigin: `${fx}px ${fy}px` });
```
指数缩放（`Math.pow(k, p)`）比线性缩放自然得多。

**5. 光圈 iris**：六片叶片在一个点上收拢，再张开到下一个画面（发布片），或者圆形遮罩收拢到角色脸上（卡通）。`clip-path: circle(r at x y)`。

**6. 匹配剪辑 match cut**：上一镜的形状、动作或颜色在下一镜继续。旋转的硬币切成旋转的地球；红点切成落日。

**7. 擦除 wipe / 卷轴**：纸艺原型里背景像卷轴一样卷起，露出下一张画好的背景；`clip-path: inset()`，再加一条带阴影的卷边。

**8. 动作中切 cut on action**：动作做到一半时切，到下一个镜头再完成。这是唯一被允许的「硬切」，此外只能切在拍点上。

禁用：交叉淡化（crossfade）当默认转场、模糊进入、亮度「显影」、3D 翻转（除非这个原型本身就是 3D）。

## 文字动画

| 手法 | 用于 | API |
|---|---|---|
| 逐字升起 | 标题、大字 | `MS.reveal(el, t, t0, {style:'rise'})` |
| 逐字淡入 | 字幕（纪录片） | `MS.reveal(el, t, t0, {style:'fade', stagger:.045})` |
| 打字机 + 光标 | 终端、问话、AI 题材 | `el.textContent = MS.typewriter(str, t, t0, 18)` |
| 数字滚动 | 数据、年份、价格 | `MS.counter(t, a, b, from, to, {decimals})` |
| 卡拉 OK 点亮 | 歌词 | 逐字设置颜色：`i < (t - t0) * cps ? accent : muted` |
| 砸字 | reel、MV 副歌 | 弹簧位移 + 0.12 秒横向 `skewX` + `blur` |
| 环形文字 / 跑马灯 | reel 收尾、技能列表 | SVG `textPath`，或 `translateX` 匀速运动 |

字幕的规矩：一句一屏，逐字出现，读完后留 0.5 秒再淡出；中文下面跟一行英文斜体，透明度 0.55。

## 数据动画

- 先画坐标轴和网格（发丝线），再画数据，最后出结论数字。
- 曲线按路径长度描出：`MS.drawPath(ctx, pts, p)`。描的过程中给曲线头加一个发光的点，它是观众视线的锚。
- 已经出现过的数据留成暗色痕迹，当前数据高亮（复利示例里，每条曲线画完就变暗留在背景里）。
- 点阵比例（73 / 100 个点亮起）比饼图更有冲击力，用 `MS.hash(i)` 决定点亮顺序，看起来是随机的，但每帧结果一致。
- 计数器、规格表的数值和画面同步变化。

## 角色动画（纸艺 / 卡通原型）

出自 ClaudeAnimationBase 指南，也是 Sweet Tooth、《我不难过》好看的原因：
- **预备动作**：大动作之前先往反方向做一个小动作（起跳前先蹲，出拳前先后撤）。
- **挤压拉伸**：落地时压扁，高速运动时拉长，保持体积不变。
- **慢入慢出、弧线**：活物沿弧线运动；抛出的东西走抛物线（Sweet Tooth 甚至把抛物线用虚线画了出来）。
- **重叠与跟随**：眼睛先动，身体跟上，帽子、尾巴最后停下。各部分的时间错开一点。
- **避免双胞胎**：代码会复制数值，结果两只手角度一样、两只眼同时眨、一群人同步弹跳。要给它们错开相位和种子。
- **夸张**：短片里，克制等于没做。
- **清晰的关键姿势**：每个镜头的关键姿势单拿出来，看剪影就能读懂。
- **永不静止**：每种情绪都有自己的待机动作，线条一直在抖（boil，每秒重新播种 12 次），镜头一直在漂。
- **不用文字**：角色的反应用画出来的符号表达（!、?、汗滴、爱心、灯泡），不用字。举一块写着「我迷路了」的牌子，这个镜头就失败了。

boil 的实现：
```js
const boil = Math.floor(t * 12);                  // 每秒 12 次
const j = (i) => (MS.hash(i, boil) - 0.5) * 2.5;  // 每个顶点 ±1.25px 的抖动，同一 boil 周期内不变
```

## 镜头永远在动

**不在静止帧上切**（prompt-motion 热门作品 notdwd 的规则）：每个镜头进入时已经在运动（指数缓出，每帧走完剩余距离的 12%–19%），离开时用加速运动或模糊斜坡带走；模糊的方向和强度跟随速度。
```js
// 指数缓出：等价于每帧走剩余距离的 k，写成 t 的纯函数
const expoIn = (lt, k = 0.15, fps = 30) => 1 - Math.pow(1 - k, lt * fps);
```

- 全片底层加一个 1%–3% 的缓推（`scale(1 + 0.03 * p)`）或缓慢漂移（`MS.noise(t * 0.3) * 20`）。
- 每拍一个 1.5% 的「冲击缩放」：`scale(1 + 0.015 * MS.pulse(t, 0.12))`。只在 reel / MV 里用。
- 运动模糊：渲染时加 `--subframes 2`（60fps）或 `--subframes 4`（30fps），快速移动会自然拖影。
