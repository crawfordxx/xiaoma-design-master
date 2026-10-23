// 镜头小样：每个镜头取 u = 0, 1, 3, 7 秒四帧，拼成一张接触表，检查拉远路径有没有穿模
// node scripts/contact.mjs [--shots 1,2,3] [--zones ...]
import fs from 'node:fs';
import { serve } from './serve.mjs';
import { launch } from './browser.mjs';

const argv = process.argv.slice(2);
const get = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const shots = get('--shots', '1,2,3,4,5,6,7,8,9,10').split(',').map(Number);
const zones = get('--zones', '');
const U = [0, 1, 3, 6.99];
fs.mkdirSync('out/contact', { recursive: true });
const s = await serve(0); const b = await launch();
const p = await b.newPage({ viewport: { width: 640, height: 360 } });
p.on('pageerror', (e) => console.log('pageerror', e.message));
await p.goto(`http://127.0.0.1:${s.address().port}/?w=640&h=360${zones ? `&zones=${zones}` : ''}`);
await p.waitForFunction(() => window.__status?.ready, null, { timeout: 300000 });
const rows = [];
for (const n of shots) {
  const cells = [];
  for (const u of U) {
    const t = (n - 1) * 7 + u;
    await p.evaluate((tt) => { window.setView(null); window.renderFrame(tt); }, t);
    cells.push((await p.locator('canvas').screenshot()).toString('base64'));
  }
  rows.push(`<div class="r"><b>${n}</b>${cells.map((c, i) => `<figure><img src="data:image/png;base64,${c}"><figcaption>u=${U[i]}</figcaption></figure>`).join('')}</div>`);
}
const sheet = await b.newPage({ viewport: { width: 1640, height: 400 } });
await sheet.setContent(`<style>body{margin:0;background:#111;color:#ddd;font:12px monospace}.r{display:flex;gap:4px;align-items:center;margin:4px}b{width:24px;text-align:center}figure{margin:0}img{width:400px;display:block}</style>${rows.join('')}`);
const out = `out/contact/shots-${shots.join('_')}.png`;
await sheet.screenshot({ path: out, fullPage: true });
console.log(out);
await b.close(); s.close();
