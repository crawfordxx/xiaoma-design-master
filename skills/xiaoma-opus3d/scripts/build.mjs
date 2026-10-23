// 打包交互模型：node scripts/build.mjs
//   dist/scene-embed.js    一个 JS 文件，<script src> 引入后挂到任意容器
//   dist/scene.html        自包含单文件（脚本内联），可直接双击打开，也可以用 <iframe> 嵌入
//   dist/embed-demo.html   两种嵌入方式的演示页
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIST = path.join(ROOT, 'dist');
fs.mkdirSync(DIST, { recursive: true });
const { viewer } = await import(new URL('../src/layout.js', import.meta.url));
const TITLE = viewer?.name ?? path.basename(ROOT); // 页面标题：layout.viewer.name，没写就用项目目录名

const result = await build({
  entryPoints: [path.join(ROOT, 'src/embed.js')],
  bundle: true, minify: true, format: 'iife', globalName: 'Scene3D', target: 'es2020',
  alias: { 'three/addons': 'three/examples/jsm' },
  legalComments: 'none', write: false, metafile: true,
});
const js = result.outputFiles[0].text;
fs.writeFileSync(path.join(DIST, 'scene-embed.js'), js);

const page = (title, body) => `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<link rel="icon" href="data:,">
${body}`;

// 单文件：脚本内联。内容里的 </script 要转义，否则 HTML 解析会提前结束脚本
const inline = js.replace(/<\/script/gi, '<\\/script');
fs.writeFileSync(path.join(DIST, 'scene.html'), page(TITLE, `<style>html,body{margin:0;height:100%;background:#1b1a22;overflow:hidden}#scene{position:fixed;inset:0}</style>
</head>
<body>
<div id="scene"></div>
<script>${inline}</script>
<script>
// URL 参数：?quality=auto|high|medium|low&time=0~70&hint=0
const q = new URLSearchParams(location.search);
const opts = {};
if (q.get('quality')) opts.quality = q.get('quality');
if (q.get('time')) opts.time = Number(q.get('time'));
if (q.get('hint') === '0') opts.hint = false;
Scene3D.mount(document.getElementById('scene'), opts).then((v) => { window.viewer = v; window.__viewerReady = true; });
</script>
</body>
</html>
`));

fs.writeFileSync(path.join(DIST, 'embed-demo.html'), page(`${TITLE} · 嵌入演示`, `<style>
body{margin:0;background:#f4f1ea;color:#2b2622;font:16px/1.7 "PingFang SC",system-ui,sans-serif}
main{max-width:960px;margin:0 auto;padding:32px 16px}
.frame{width:100%;height:540px;border:0;border-radius:8px;overflow:hidden;background:#1b1a22;display:block}
pre{background:#2b2622;color:#f4f1ea;padding:12px 14px;border-radius:6px;overflow:auto;font-size:13px}
</style>
</head>
<body>
<main>
<h1>${TITLE} · 可交互模型</h1>
<p>下面这块是嵌在普通网页里的 3D 模型：左键拖动旋转，滚轮缩放，右键拖动平移；手机上单指旋转、双指缩放。</p>
<h2>方式一：iframe（最省事）</h2>
<iframe class="frame" src="scene.html" title="${TITLE} 3D 模型" loading="lazy"></iframe>
<pre>&lt;iframe src="scene.html?quality=auto&amp;time=55" style="width:100%;height:540px;border:0"&gt;&lt;/iframe&gt;</pre>
<h2>方式二：script 挂到任意 div</h2>
<p>同一页面里嵌多个时，iframe 互相隔离更稳；想和页面脚本交互（比如自己做按钮切画质）用这种。</p>
<pre>&lt;div data-scene='{"quality":"auto","time":55}' style="height:540px"&gt;&lt;/div&gt;
&lt;script src="scene-embed.js"&gt;&lt;/script&gt;

&lt;!-- 或者手动挂载 --&gt;
&lt;script&gt;
  Scene3D.mount(document.getElementById('scene'), { quality: 'medium' })
    .then((viewer) =&gt; { /* viewer.setQuality('low'); viewer.dispose(); */ });
&lt;/script&gt;</pre>
<p>参数：<code>quality</code> = auto / high / medium / low（auto 会在帧率不够时自动降档）；<code>time</code> = 0~70，0 是日落前，70 是华灯初上；<code>hint</code> = false 关掉左下角的操作提示。</p>
</main>
</body>
</html>
`));

fs.writeFileSync(path.join(DIST, 'embed-div-demo.html'), page(`${TITLE} · div 嵌入测试`, `<style>body{margin:0;padding:24px;background:#f4f1ea;font:15px system-ui}</style>
</head>
<body>
<p>script 方式嵌入测试：</p>
<div id="scene" data-scene='{"quality":"auto"}' style="height:480px;border-radius:8px;overflow:hidden"></div>
<script src="scene-embed.js"></script>
<script>
const poll = setInterval(() => { const p = document.getElementById('scene').__scene; if (p) { clearInterval(poll); p.then((v) => { window.viewer = v; window.__viewerReady = true; }); } }, 50);
</script>
</body>
</html>
`));

const kb = (f) => (fs.statSync(path.join(DIST, f)).size / 1024).toFixed(0);
console.log(`✓ dist/scene-embed.js ${kb('scene-embed.js')} KB  dist/scene.html ${kb('scene.html')} KB  dist/embed-demo.html  dist/embed-div-demo.html`);
