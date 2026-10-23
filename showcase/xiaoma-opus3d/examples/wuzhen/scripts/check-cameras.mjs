// 镜头路径碰撞检查：按 1/30 秒采样每个镜头的相机位置，看是否进到房屋、桥体、地面以下。
// 体积用 layout 粗算（房屋 = 占地 × 屋脊高 + 檐口外挑；桥 = 桥面范围 × 桥面高），只抓明显穿模。
import * as L from '../src/layout.js';
import { SHOTS, SHOT_LEN } from '../src/cameras.js';

const boxes = [];
for (const h of L.houses) {
  const f = h.footprint; const ridge = h.eaveHeight + (h.depth / 2) * 0.5 + 0.5;
  const pad = 0.8; // 檐口外挑 + 安全距离
  boxes.push({ id: `house ${h.id}`, x0: f.x0 - 0.2, x1: f.x1 + 0.2, z0: f.z0 - pad, z1: f.z1 + pad, y0: -0.5, y1: ridge });
  const p = L.pavilionFootprint(h);
  if (p) boxes.push({ id: `水阁 ${h.id}`, ...p, z0: p.z0 - 0.5, z1: p.z1 + 0.5, y0: -3.2, y1: 3.6 });
}
for (const b of L.bridges) {
  const half = b.width / 2 + 0.3;
  const top = b.type === 'arch' ? L.LEVELS.water + b.riseAboveWater + 1.2 + 1.3 : b.deckY + 1.0;
  const r = b.axis === 'z' ? { x0: b.at - half, x1: b.at + half, z0: b.from, z1: b.to } : { x0: b.from, x1: b.to, z0: b.at - half, z1: b.at + half };
  // 拱桥的拱洞是开口：半圆（圆心在水面、半径 span/2）内侧留 0.6m 余量算可通过
  const open = b.type === 'arch' ? (x, y, z) => {
    const across = b.axis === 'z' ? z : x; const center = 0; // 两座拱桥都跨在河中心线上
    return Math.hypot(across - center, y - L.LEVELS.water) < b.span / 2 - 0.6 && y > L.LEVELS.water;
  } : null;
  boxes.push({ id: `bridge ${b.id}`, ...r, y0: -3.2, y1: top, open });
}
for (const c of L.corridors) boxes.push({ id: `廊棚顶 ${c.id}`, x0: c.x0, x1: c.x1, z0: c.z0 - 0.5, z1: c.z1, y0: c.roofLow - 0.15, y1: c.roofHigh + 0.4 });
const w = L.dyeYard.workshop; boxes.push({ id: '染坊作坊', ...w, y0: 0, y1: 10 });

const inWater = (x, z) => L.rivers.some((r) => x > r.rect.x0 && x < r.rect.x1 && z > r.rect.z0 && z < r.rect.z1);
let bad = 0;
SHOTS.forEach((shot, i) => {
  const hits = new Map();
  for (let f = 0; f < SHOT_LEN * 30; f++) {
    const u = f / 30; const t = i * SHOT_LEN + u;
    const { pos: [x, y, z] } = shot.pose(u, t);
    const floor = inWater(x, z) ? L.LEVELS.water + 0.15 : 0.3;
    if (y < floor) hits.set('地面/水面以下', (hits.get('地面/水面以下') ?? []).concat(u.toFixed(2)));
    for (const b of boxes) {
      if (x > b.x0 && x < b.x1 && z > b.z0 && z < b.z1 && y > b.y0 && y < b.y1 && !b.open?.(x, y, z)) hits.set(b.id, (hits.get(b.id) ?? []).concat(u.toFixed(2)));
    }
  }
  const ok = hits.size === 0;
  if (!ok) bad++;
  console.log(`${ok ? '✓' : '✗'} ${shot.name}`);
  for (const [id, us] of hits) console.log(`    ${id}: u=${us[0]}–${us[us.length - 1]}（${us.length} 帧）`);
});
process.exit(bad ? 1 : 0);
