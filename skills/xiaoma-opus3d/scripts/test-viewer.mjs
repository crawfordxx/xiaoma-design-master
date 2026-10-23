// 交互模型测试（先跑 node scripts/build.mjs）：node scripts/test-viewer.mjs
// 用 file:// 打开 dist/scene.html（验证不需要服务器也能跑），分别在像素比 1 和 2 下检查：
//   加载无报错 · 画布显示尺寸 = 容器 · 拖动会转、滚轮会缩放、右键会平移 · 三档画质都能切换 · 各档帧率
// 截图写到 out/viewer-test/，用 Read 看。
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { launch } from './browser.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(ROOT, 'out/viewer-test');
fs.mkdirSync(OUT, { recursive: true });
const url = pathToFileURL(path.join(ROOT, 'dist/scene.html')).href;
const fails = [];
const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) fails.push(msg); };
const fpsOf = (p) => p.evaluate(() => new Promise((res) => { let n = 0; const t = performance.now(); (function f() { if (++n === 90) res(+(90000 / (performance.now() - t)).toFixed(1)); else requestAnimationFrame(f); })(); }));
const cam = (p) => p.evaluate(() => ({ pos: viewer.camera.position.toArray(), target: viewer.controls.target.toArray() }));
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

const b = await launch();
for (const dpr of [1, 2]) {
  console.log(`\n—— 像素比 ${dpr}`);
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: dpr });
  const errs = []; p.on('pageerror', (e) => errs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  const t0 = Date.now();
  await p.goto(url);
  await p.waitForFunction(() => window.__viewerReady, null, { timeout: 180000 });
  await p.waitForTimeout(1200);
  console.log(`  加载 ${Date.now() - t0}ms`);
  const size = await p.evaluate(() => { const c = document.querySelector('canvas'); return { css: [c.clientWidth, c.clientHeight], px: [c.width, c.height], win: [innerWidth, innerHeight] }; });
  check(size.css[0] === size.win[0] && size.css[1] === size.win[1], `画布显示尺寸 ${size.css} = 容器 ${size.win}（物理像素 ${size.px}）`);
  await p.screenshot({ path: path.join(OUT, `dpr${dpr}-0-initial.png`) });

  const c0 = await cam(p);
  await p.mouse.move(640, 360); await p.mouse.down(); await p.mouse.move(500, 340, { steps: 15 }); await p.mouse.up(); await p.waitForTimeout(700);
  const c1 = await cam(p); check(dist(c0.pos, c1.pos) > 1, '左键拖动会旋转');
  await p.screenshot({ path: path.join(OUT, `dpr${dpr}-1-drag.png`) });
  await p.mouse.move(640, 400); for (let i = 0; i < 8; i++) { await p.mouse.wheel(0, -200); await p.waitForTimeout(30); }
  await p.waitForTimeout(700);
  const c2 = await cam(p); check(dist(c2.pos, c2.target) < dist(c1.pos, c1.target), '滚轮会拉近');
  await p.screenshot({ path: path.join(OUT, `dpr${dpr}-2-zoom.png`) });
  await p.mouse.down({ button: 'right' }); await p.mouse.move(560, 330, { steps: 12 }); await p.mouse.up({ button: 'right' }); await p.waitForTimeout(700);
  const c3 = await cam(p); check(dist(c2.target, c3.target) > 0.1, '右键拖动会平移');
  await p.screenshot({ path: path.join(OUT, `dpr${dpr}-3-pan.png`) });

  for (const q of ['high', 'medium', 'low']) {
    await p.evaluate((q) => viewer.setQuality(q), q); await p.waitForTimeout(500);
    console.log(`  ${q.padEnd(6)} ${await fpsOf(p)} fps`);
  }
  check(errs.length === 0, `没有报错${errs.length ? '：' + errs.slice(0, 3).join(' | ') : ''}`);
  await p.close();
}
await b.close();
console.log(fails.length ? `\n✗ ${fails.length} 项失败` : '\n✓ 全部通过（注意：这台机器的帧率不代表普通设备，见 pitfalls.md“实时”）');
process.exit(fails.length ? 1 : 0);
