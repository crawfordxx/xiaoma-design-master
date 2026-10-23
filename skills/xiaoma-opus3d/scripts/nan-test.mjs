// NaN/黑帧回归测试：随机 N 个机位（贴地 / 高空俯视 / 正对太阳 / 背对太阳 / 任意）× 随机 t，
// 再加上每个镜头路径上的采样帧。每帧读中心和四角像素，任何一个纯黑 (0,0,0) 就算失败，另外统计 9×9 网格里的纯黑点。
// 用法：node scripts/nan-test.mjs [zones] [N]
// 注意：深色材质在阴影里也可能读出纯黑。报失败的机位要用 shot.mjs 截图看一眼，确认是 NaN 还是真的暗。
// 最初版本由乌镇项目的水面 Agent 写成，用它抓到了水面 shader 的第二处 NaN。
import * as L from '../src/layout.js';
import { SHOTS, SHOT_LEN } from '../src/cameras.js';
import { serve } from './serve.mjs';
import { launch } from './browser.mjs';

const zones = process.argv[2] || '';
const N = Number(process.argv[3] || 200);
let seed = 20261021; // 固定种子，测试可复现
const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
const R = (a, b) => a + (b - a) * rnd();
const E = L.EXTENT; const g0 = L.LEVELS.ground ?? 0; const low = L.LEVELS.water ?? g0;
const b = (L.lighting.sunBearingDeg * Math.PI) / 180; const SUN = [Math.sin(b), -Math.cos(b)];
const dur = L.lighting.duration ?? SHOTS.length * SHOT_LEN;

const views = [];
for (let i = 0; i < N; i++) {
  const kind = ['ground', 'aerial', 'sun', 'antisun', 'any'][i % 5];
  const px = R(E.x0, E.x1); const pz = R(E.z0, E.z1);
  let pos; let target;
  if (kind === 'ground') { pos = [px, R(low + 0.1, g0 + 1.8), pz]; target = [px + R(-20, 20), R(low, g0 + 3), pz + R(-20, 20)]; }
  else if (kind === 'aerial') { pos = [R(E.x0, E.x1) * 1.3, R(40, 220), R(E.z0, E.z1) * 1.3]; target = [R(-30, 30), g0, R(-30, 30)]; }
  else if (kind === 'sun' || kind === 'antisun') {
    const s = kind === 'sun' ? 1 : -1; const d = R(10, 60);
    pos = [px, R(low + 0.1, g0 + 6), pz]; target = [px + s * SUN[0] * d, R(low, g0 + 4), pz + s * SUN[1] * d];
  } else { pos = [R(E.x0, E.x1), R(low + 0.1, 30), R(E.z0, E.z1)]; target = [R(E.x0, E.x1), R(low, 10), R(E.z0, E.z1)]; }
  views.push({ name: `${kind}-${i}`, t: +R(0, dur).toFixed(2), view: { pos, target, fov: R(30, 70) } });
}
SHOTS.forEach((shot, i) => {
  for (let u = 0; u < SHOT_LEN; u += 0.5) {
    const t = i * SHOT_LEN + u;
    views.push({ name: `${shot.name} u=${u}`, t, view: shot.pose(u, t) });
  }
});

const s = await serve(0); const br = await launch();
const p = await br.newPage({ viewport: { width: 320, height: 180 } });
p.on('pageerror', (e) => console.log(`[pageerror] ${e.message}`));
await p.goto(`http://127.0.0.1:${s.address().port}/?w=320&h=180${zones ? `&zones=${zones}` : ''}`);
await p.waitForFunction(() => window.__status?.ready, null, { timeout: 300000 });
const res = await p.evaluate((views) => {
  const gl = window.__three.renderer.getContext();
  const px = new Uint8Array(4);
  const black = (x, y) => { gl.readPixels(x, y, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); return px[0] + px[1] + px[2] === 0; };
  const fails = []; let gridBlack = 0;
  for (const v of views) {
    window.setView(v.view); window.renderFrame(v.t);
    const bad = [[160, 90], [0, 0], [319, 0], [0, 179], [319, 179]].filter(([x, y]) => black(x, y));
    let g = 0;
    for (let i = 0; i < 9; i++) for (let j = 0; j < 9; j++) if (black(20 + i * 35, 10 + j * 20)) g++;
    gridBlack += g;
    if (bad.length || g > 40) fails.push({ name: v.name, t: v.t, bad: bad.length, grid: g, view: v.view });
  }
  window.setView(null);
  return { n: views.length, fails, gridBlack, errors: window.__status.errors };
}, views);
console.log(`frames=${res.n} fails=${res.fails.length} pureBlackGridPixels=${res.gridBlack} errors=${JSON.stringify(res.errors)}`);
for (const f of res.fails.slice(0, 20)) {
  const v = f.view;
  console.log(`  ✗ ${f.name} t=${f.t} 角点黑=${f.bad} 网格黑=${f.grid}  复查：--view "chk:${v.pos.map((n) => n.toFixed(2))}:${v.target.map((n) => n.toFixed(2))}:${Math.round(v.fov)}" --t ${f.t}`);
}
await br.close(); s.close();
process.exit(res.fails.length ? 1 : 0);
