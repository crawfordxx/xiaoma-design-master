// 平面图检查：建筑互不重叠、除水阁/桥/河埠头外不落水、桥两端落在驳岸外、不压街巷
import * as L from '../src/layout.js';

const EPS = 1e-6;
const overlap = (a, b) => a.x0 < b.x1 - EPS && b.x0 < a.x1 - EPS && a.z0 < b.z1 - EPS && b.z0 < a.z1 - EPS;
const inRect = (x, z, r) => x > r.x0 + EPS && x < r.x1 - EPS && z > r.z0 + EPS && z < r.z1 - EPS;
const circleRect = (t) => ({ x0: t.x - t.trunk, x1: t.x + t.trunk, z0: t.z - t.trunk, z1: t.z + t.trunk });

function bridgeRect(b) {
  const half = b.width / 2;
  return b.axis === 'z'
    ? { x0: b.at - half, x1: b.at + half, z0: b.from, z1: b.to }
    : { x0: b.from, x1: b.to, z0: b.at - half, z1: b.at + half };
}

const errors = [];
const solids = [
  ...L.houses.map((h) => ({ id: `house ${h.id}`, rect: h.footprint, kind: 'house' })),
  { id: '染坊作坊', rect: L.dyeYard.workshop, kind: 'yard' },
  { id: '晒布架', rect: L.dyeYard.racks, kind: 'yard' },
  ...L.backdrop.fillRects.map((r) => ({ id: `远景填充 ${r.id}`, rect: r, kind: 'fill' })),
  ...L.trees.map((t) => ({ id: `tree ${t.id}`, rect: circleRect(t), kind: 'tree' })),
];
const bridgeSolids = L.bridges.map((b) => ({ id: `bridge ${b.id}`, rect: bridgeRect(b), bridge: b }));

// 1. 实体之间不重叠（建筑、晒布场、树干）
for (let i = 0; i < solids.length; i++) {
  for (let j = i + 1; j < solids.length; j++) {
    if (overlap(solids[i].rect, solids[j].rect)) errors.push(`重叠：${solids[i].id} × ${solids[j].id}`);
  }
}

// 2. 实体不落水；水阁只能伸进自己所临的河
for (const s of solids) {
  for (const r of L.rivers) if (overlap(s.rect, r.rect)) errors.push(`落水：${s.id} 进入 ${r.id}`);
}
for (const h of L.houses) {
  const p = L.pavilionFootprint(h);
  if (!p) continue;
  const main = L.rivers.find((r) => r.id === 'main').rect;
  if (p.z1 - p.z0 > 2.6) errors.push(`水阁过深：${h.id}`);
  if (!overlap(p, main)) errors.push(`水阁没有临水：${h.id}`);
  // 北岸水阁最多伸到 z=-3.5，给船让道
  if (Math.max(p.z0, p.z1) > -3.5 + EPS) errors.push(`水阁挡航道：${h.id}`);
}

// 3. 桥：不压实体、两端落在驳岸外的地面上
for (const b of bridgeSolids) {
  for (const s of solids) if (overlap(b.rect, s.rect)) errors.push(`桥压到实体：${b.id} × ${s.id}`);
  const ends = b.bridge.axis === 'z'
    ? [[b.bridge.at, b.bridge.from], [b.bridge.at, b.bridge.to]]
    : [[b.bridge.from, b.bridge.at], [b.bridge.to, b.bridge.at]];
  for (const [x, z] of ends) {
    if (L.rivers.some((r) => inRect(x, z, r.rect))) errors.push(`桥端落水：${b.id} @ (${x}, ${z})`);
  }
}

// 4. 建筑不压街巷（树可以种在路边）；晒布场整体也不能压到民居
for (const h of L.houses) {
  if (overlap(h.footprint, L.dyeYard.rect)) errors.push(`民居进了晒布场：${h.id}`);
  for (const st of L.streets) if (overlap(h.footprint, st.rect)) errors.push(`压街：house ${h.id} × ${st.id}`);
}

// 5. 河埠头必须贴着河，船线必须在水里且不碰水阁
for (const s of L.waterSteps) {
  if (!L.rivers.some((r) => overlap(s.rect, r.rect))) errors.push(`河埠头不临水：${s.id}`);
}
for (const boat of L.boats) {
  const [fx, fz] = boat.from; const [tx, tz] = boat.to;
  for (let k = 0; k <= 200; k++) {
    const x = fx + ((tx - fx) * k) / 200; const z = fz + ((tz - fz) * k) / 200;
    const hull = { x0: x - boat.beam / 2, x1: x + boat.beam / 2, z0: z - boat.beam / 2, z1: z + boat.beam / 2 };
    const wet = L.rivers.some((r) => hull.x0 >= r.rect.x0 && hull.x1 <= r.rect.x1 && hull.z0 >= r.rect.z0 && hull.z1 <= r.rect.z1);
    if (!wet) { errors.push(`船线搁浅：${boat.id} @ (${x.toFixed(1)}, ${z.toFixed(1)})`); break; }
    const hit = L.houses.find((h) => { const p = L.pavilionFootprint(h); return p && overlap(hull, p); });
    if (hit) { errors.push(`船撞水阁：${boat.id} × ${hit.id}`); break; }
  }
}

const rows = Object.groupBy(L.houses, (h) => h.row);
console.log(`民居 ${L.houses.length} 栋：` + Object.entries(rows).map(([k, v]) => `${k}=${v.length}`).join(' '));
console.log(`水阁 ${L.houses.filter((h) => h.waterPavilion).length} 处，桥 ${L.bridges.length} 座，树 ${L.trees.length} 棵`);
if (errors.length) {
  console.error(`✗ ${errors.length} 个问题：\n  ` + errors.join('\n  '));
  process.exit(1);
}
console.log('✓ layout 检查通过');
