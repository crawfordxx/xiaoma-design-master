// 由 layout.CHECK 生成俯视平面图 plan.svg（北在上）。转 PNG：node scripts/svg2png.mjs plan.svg out/plan.png
import fs from 'node:fs';
import * as L from '../src/layout.js';

const S = 4; const pad = 20; const v = L.EXTENT;
const W = (v.x1 - v.x0) * S + pad * 2; const H = (v.z1 - v.z0) * S + pad * 2;
const px = (x) => (x - v.x0) * S + pad; const pz = (z) => (z - v.z0) * S + pad;
const rect = (r, fill, extra = '') => `<rect x="${px(r.x0)}" y="${pz(r.z0)}" width="${(r.x1 - r.x0) * S}" height="${(r.z1 - r.z0) * S}" fill="${fill}" ${extra}/>`;
const label = (x, z, t, size = 9, color = '#222') => `<text x="${px(x)}" y="${pz(z)}" font-size="${size}" fill="${color}" text-anchor="middle" dominant-baseline="middle" font-family="PingFang SC, sans-serif">${t}</text>`;
const { solids = [], keepOut = [], zones = [], paths = [] } = L.CHECK;
const parts = [`<rect width="${W}" height="${H}" fill="#e9e4d8"/>`];
for (const z of zones) parts.push(rect(z.rect, '#d4cbb8'), label((z.rect.x0 + z.rect.x1) / 2, z.rect.z0 + 2, z.id, 8, '#6b6252'));
for (const k of keepOut) parts.push(rect(k.rect, '#7fa3b5'));
for (const s of solids) parts.push(rect(s.rect, '#55565e', 'stroke="#f4f1ea" stroke-width="0.8"'), label((s.rect.x0 + s.rect.x1) / 2, (s.rect.z0 + s.rect.z1) / 2, s.id, 7, '#f4f1ea'));
for (const p of paths) parts.push(`<polyline points="${p.points.map(([x, z]) => `${px(x)},${pz(z)}`).join(' ')}" fill="none" stroke="#1d3557" stroke-dasharray="6 4"/>`);
parts.push(`<line x1="${pad}" y1="${H - 8}" x2="${pad + 50 * S}" y2="${H - 8}" stroke="#222" stroke-width="2"/>`, label(v.x0 + 25, v.z1 + 2.4, '50 m', 10));
parts.push(`<g transform="translate(${W - 40},40)"><path d="M0 18 L8 -14 L16 18 L8 10 Z" fill="#222"/><text x="8" y="-20" font-size="12" text-anchor="middle">N</text></g>`);
fs.writeFileSync(new URL('../plan.svg', import.meta.url), `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${parts.join('\n')}</svg>`);
console.log('plan.svg 已生成');
