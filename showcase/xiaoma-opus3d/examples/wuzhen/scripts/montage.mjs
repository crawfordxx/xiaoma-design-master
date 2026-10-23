// 把多张截图拼成一张对比图：node scripts/montage.mjs out.png a.png b.png ...（2 列）
import { launch } from './browser.mjs';
import fs from 'node:fs';
const [dst, ...srcs] = process.argv.slice(2);
const imgs = srcs.map((f) => `<figure><img src="data:image/png;base64,${fs.readFileSync(f).toString('base64')}"><figcaption>${f}</figcaption></figure>`).join('');
const b = await launch(); const p = await b.newPage({ viewport: { width: 1600, height: 400 } });
await p.setContent(`<style>body{margin:0;display:grid;grid-template-columns:1fr 1fr;gap:4px;background:#111;width:1600px}figure{margin:0}img{width:100%;display:block}figcaption{color:#ccc;font:12px monospace;padding:2px 4px}</style>${imgs}`);
await p.screenshot({ path: dst, fullPage: true }); await b.close();
