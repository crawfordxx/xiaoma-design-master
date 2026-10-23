import { launch } from './browser.mjs';
import fs from 'node:fs';
const [src, dst] = process.argv.slice(2);
const svg = fs.readFileSync(src, 'utf8');
const w = Number(svg.match(/width="(\d+)"/)[1]); const h = Number(svg.match(/height="(\d+)"/)[1]);
const b = await launch(); const p = await b.newPage({ viewport: { width: w, height: h } });
await p.setContent(`<body style="margin:0">${svg}</body>`); await p.screenshot({ path: dst }); await b.close();
