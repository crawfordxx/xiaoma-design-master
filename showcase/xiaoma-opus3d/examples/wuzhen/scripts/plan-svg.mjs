// 由 layout.js 生成俯视平面图 plan.svg（北在上：-Z 朝上）
import fs from 'node:fs';
import * as L from '../src/layout.js';

const S = 4; // 每米像素
const pad = 20;
const view = { x0: -125, x1: 125, z0: -85, z1: 85 };
const W = (view.x1 - view.x0) * S + pad * 2;
const H = (view.z1 - view.z0) * S + pad * 2;
const px = (x) => (x - view.x0) * S + pad;
const pz = (z) => (z - view.z0) * S + pad;
const rect = (r, fill, extra = '') =>
  `<rect x="${px(r.x0)}" y="${pz(r.z0)}" width="${(r.x1 - r.x0) * S}" height="${(r.z1 - r.z0) * S}" fill="${fill}" ${extra}/>`;
const label = (x, z, t, size = 10, color = '#222') =>
  `<text x="${px(x)}" y="${pz(z)}" font-size="${size}" fill="${color}" text-anchor="middle" dominant-baseline="middle" font-family="PingFang SC, sans-serif">${t}</text>`;

const parts = [`<rect width="${W}" height="${H}" fill="#e9e4d8"/>`];
for (const r of L.backdrop.fillRects) parts.push(rect(r, 'url(#fill)'));
for (const s of L.streets) parts.push(rect(s.rect, '#d4cbb8'));
for (const r of L.rivers) parts.push(rect(r.rect, '#7fa3b5'));
for (const s of L.waterSteps) parts.push(rect(s.rect, '#9a9184'));
for (const c of L.corridors) parts.push(rect(c, 'none', 'stroke="#8b3a2b" stroke-width="2" stroke-dasharray="4 3"'));
parts.push(rect(L.dyeYard.rect, '#dfe6ee', 'stroke="#2f4f7f" stroke-width="1.5"'));
parts.push(rect(L.dyeYard.racks, 'url(#racks)'));
parts.push(rect(L.dyeYard.workshop, '#6b6b72'));
for (const h of L.houses) {
  const p = L.pavilionFootprint(h);
  if (p) parts.push(rect(p, '#a58c6f', 'stroke="#5a4632" stroke-width="0.8"'));
  parts.push(rect(h.footprint, h.detail === 'high' ? '#55565e' : '#7d7e86', 'stroke="#f4f1ea" stroke-width="0.8"'));
  parts.push(label(h.x, h.z, h.id, 7, '#f4f1ea'));
}
for (const b of L.bridges) {
  const half = b.width / 2;
  const r = b.axis === 'z' ? { x0: b.at - half, x1: b.at + half, z0: b.from, z1: b.to } : { x0: b.from, x1: b.to, z0: b.at - half, z1: b.at + half };
  parts.push(rect(r, b.type === 'arch' ? '#c9b48a' : '#b8ad98', 'stroke="#3b2f1e" stroke-width="1.2"'));
}
for (const t of L.trees) {
  parts.push(`<circle cx="${px(t.x)}" cy="${pz(t.z)}" r="${(t.kind === 'willow' ? 2.2 : 4) * S}" fill="${t.kind === 'willow' ? '#8fae6a' : '#4f7a46'}" fill-opacity="0.75"/>`);
}
for (const b of L.boats) {
  parts.push(`<line x1="${px(b.from[0])}" y1="${pz(b.from[1])}" x2="${px(b.to[0])}" y2="${pz(b.to[1])}" stroke="#1d3557" stroke-width="1" stroke-dasharray="6 4"/>`);
}
parts.push(label(-14, -18.5, '通济桥', 11, '#3b2f1e'), label(-2, -18.5, '仁济桥', 11, '#3b2f1e'));
parts.push(label(34, 39.8, '染坊晒布场', 11, '#2f4f7f'), label(-70, 3, '市 河', 14, '#fff'), label(0, 30, '支河', 11, '#fff'));
parts.push(`<g transform="translate(${W - 50},40)"><path d="M0 18 L8 -14 L16 18 L8 10 Z" fill="#222"/>${'<text x="8" y="-20" font-size="12" text-anchor="middle">N</text>'}</g>`);
parts.push(`<line x1="${pad}" y1="${H - 8}" x2="${pad + 50 * S}" y2="${H - 8}" stroke="#222" stroke-width="2"/>${label(-100, view.z1 + 2.4, '50 m', 10)}`);
// 白莲塔在画外，用箭头指示
parts.push(`<path d="M${pad + 4} ${pad + 4} l24 0 m-24 0 l0 24 m0 -24 l30 30" stroke="#8b3a2b" stroke-width="1.5" fill="none"/>${label(-112, -73, '白莲塔 ↖ 300m', 10, '#8b3a2b')}`);

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
<defs><pattern id="fill" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="#cfc9bd"/><path d="M0 10 L10 0" stroke="#a9a397"/></pattern><pattern id="racks" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#dfe6ee"/><rect width="8" height="3" fill="#2f4f7f"/></pattern></defs>
${parts.join('\n')}
</svg>`;
fs.writeFileSync(new URL('../plan.svg', import.meta.url), svg);
console.log('plan.svg 已生成');
