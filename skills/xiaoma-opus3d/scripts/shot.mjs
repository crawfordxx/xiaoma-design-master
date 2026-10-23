// 截图：node scripts/shot.mjs --zones terrain,water --views top,river-east --t 0 --out out/shots/water
// 自定义机位：--view "name:px,py,pz:tx,ty,tz:fov"（可多次）
import fs from 'node:fs';
import path from 'node:path';
import { serve } from './serve.mjs';
import { launch } from './browser.mjs';
import { VIEWS } from './views.mjs';

function parseArgs(argv) {
  const a = { zones: '', views: 'top,aerial', t: 0, out: 'out/shots', custom: [], w: 1600, h: 900, overlay: true };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i]; const v = argv[i + 1];
    if (k === '--zones') { a.zones = v; i++; } else if (k === '--views') { a.views = v; i++; }
    else if (k === '--t') { a.t = Number(v); i++; } else if (k === '--out') { a.out = v; i++; }
    else if (k === '--w') { a.w = Number(v); i++; } else if (k === '--h') { a.h = Number(v); i++; }
    else if (k === '--no-overlay') { a.overlay = false; }
    else if (k === '--rect') {
      // 局部正交俯视：--rect "name:x0,x1,z0,z1"
      const [name, r] = v.split(':'); const [x0, x1, z0, z1] = r.split(',').map(Number);
      a.custom.push([name, { ortho: true, rect: { x0, x1, z0, z1 } }]); i++;
    } else if (k === '--view') {
      const [name, p, tg, fov] = v.split(':');
      a.custom.push([name, { pos: p.split(',').map(Number), target: tg.split(',').map(Number), fov: Number(fov ?? 50) }]); i++;
    } else throw new Error(`未知参数 ${k}`);
  }
  return a;
}

const args = parseArgs(process.argv.slice(2));
const views = [...args.views.split(',').filter(Boolean).map((n) => {
  if (!VIEWS[n]) throw new Error(`没有预设机位 ${n}，可选：${Object.keys(VIEWS).join(', ')}`);
  return [n, VIEWS[n]];
}), ...args.custom];
fs.mkdirSync(args.out, { recursive: true });

const server = await serve(0);
const port = server.address().port;
const browser = await launch();
try {
  for (const [name, view] of views) {
    const page = await browser.newPage({ viewport: { width: args.w, height: args.h } });
    page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.log(`[page ${m.type()}] ${m.text()}`); });
    page.on('pageerror', (e) => console.log(`[pageerror] ${e.message}`));
    const q = new URLSearchParams({ w: args.w, h: args.h, t: args.t });
    if (args.zones) q.set('zones', args.zones);
    if (view.ortho && args.overlay) q.set('overlay', '1');
    const t0 = Date.now();
    await page.goto(`http://127.0.0.1:${port}/?${q}`);
    await page.waitForFunction(() => window.__status?.ready || window.__status?.errors?.length > 0 && window.__status.ready, null, { timeout: 180000 });
    const status = await page.evaluate(async ({ view, t }) => {
      window.setView(view);
      window.renderFrame(t);
      return window.__status;
    }, { view, t: args.t });
    const file = path.join(args.out, `${name}.png`);
    await page.locator('canvas').screenshot({ path: file });
    console.log(`✓ ${file}  (${Date.now() - t0}ms)  zones=${JSON.stringify(status.zones)}`);
    if (status.errors.length) console.log(`  ✗ errors: ${status.errors.join(' | ')}`);
    await page.close();
  }
} finally {
  await browser.close();
  server.close();
}
