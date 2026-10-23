# HTML 幻灯片

幻灯片就是一条带暂停点的时间轴。同一个 HTML 文件有三种用法：

- **演讲**：浏览器打开，→ / 空格 / 点击播到下一个暂停点，← 回退，F 全屏。
- **视频**：`node engine/render.mjs deck.html --out deck.mp4`，按每页的 `data-dur` 连续播放。
- **PDF / PNG**：`node engine/render.mjs deck.html --slides out/slides --pdf out/deck.pdf`，每页取最终状态截一张。

起步：复制 `templates/slides/index.html`。完整示例：`examples/research-deck/`。

## 写法

```html
<div id="stage" class="theme-editorial">
  <section class="slide" data-dur="6" data-tr="push">
    <div class="over" data-fx="fade">章节小标题</div>
    <h2 data-fx="rise" data-in="0.2">一句话结论，<em>关键词</em>用强调色</h2>
    <div class="n" data-fx="count" data-to="73" data-suf="%" data-in="0.6">0</div>
    <p data-fx="rise" data-step="1">按一下才出现的补充</p>
  </section>
  …
  <div class="foot"><span>品牌</span><span id="deck-num"></span></div>
  <div id="deck-progress"></div>
</div>
<script src="engine/runtime.js"></script>
<script src="engine/deck.js"></script>
<script>MS.deck({ width: 1920, height: 1080, fps: 30, background: '#0a0a0a' });</script>
```

| 属性 | 取值 |
|---|---|
| `data-fx` | `rise` 遮罩升起 · `chars` 逐字升起 · `fade` · `blur` · `scale` 弹簧弹出 · `left` / `right` 侧入 · `draw` SVG 描边 · `count` 数字滚动（`data-to` `data-pre` `data-suf` `data-dec`）· `type` 打字机 · `bar` 宽度生长（`data-to` 为百分比） |
| `data-in` | 本页内第几秒开始（相对转场结束后） |
| `data-step` | 第 N 次按键后出现（导出视频时按 `step × 1.1s` 排布） |
| `data-d` | 动画时长，默认 0.7 秒 |
| `data-tr`（section） | 进入本页的转场：`push`（默认）· `fade` · `zoom` · `flood` · `wipe` |
| `data-dur`（section） | 本页在视频里的最短时长；不写就按最后一个动画结束后 + 1.2 秒 |

## 幻灯片的审美规矩

和视频共用 `aesthetics.md`，另外几条：
- **一页一个结论**，标题本身就是结论句（「16/25 用暗底；每条只有一个强调色」），而不是「配色分析」这种话题词。
- 大数字是幻灯片最强的视觉：200px 细体，配一行小字说明。
- 左对齐，靠留白分组；正文 ≥ 30px。一页超过 3 个要点就拆成两页。
- 亮暗页交替用来分章节（`class="slide light"`），不要每页都换。
- 每页最多 4 个动画节拍：小标题 → 标题 → 证据 → 补充（用 step）。
- 页码和进度条常驻；署名放左下角，字号小。

## 验收

导出 PDF 后把所有页拼成一张图看（`ffmpeg -i out/slides/%03d.png -vf "scale=640:-2,tile=3x3" sheet.jpg`），检查：
- 有没有某页的元素停在半透明状态（动画没跑完：`data-in` 太晚，或者 `data-dur` 太短）
- 亮页上有没有忘了改色、看不见的文字
- 每页标题是不是结论句
