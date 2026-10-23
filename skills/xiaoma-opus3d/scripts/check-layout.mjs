// 平面图检查（通用版）：读 layout.CHECK
//   1. solids 两两不重叠（同 group 除外）
//   2. solids 不压进 keepOut（id 前缀在 allow 里的除外）
//   3. paths 整段留在 mustStayIn 的并集里，且不碰 solids
//   4. layout.extraChecks() 里的项目特有规则
import * as L from '../src/layout.js';

const EPS = 1e-6;
const overlap = (a, b) => a.x0 < b.x1 - EPS && b.x0 < a.x1 - EPS && a.z0 < b.z1 - EPS && b.z0 < a.z1 - EPS;
const inside = (a, b) => a.x0 >= b.x0 - EPS && a.x1 <= b.x1 + EPS && a.z0 >= b.z0 - EPS && a.z1 <= b.z1 + EPS;
const { solids = [], keepOut = [], paths = [] } = L.CHECK;
const errors = [];

for (let i = 0; i < solids.length; i++) {
  for (let j = i + 1; j < solids.length; j++) {
    const a = solids[i]; const b = solids[j];
    if (a.group && a.group === b.group) continue;
    if (overlap(a.rect, b.rect)) errors.push(`重叠：${a.id} × ${b.id}`);
  }
}
for (const s of solids) {
  for (const k of keepOut) {
    if ((k.allow ?? []).some((p) => s.id.startsWith(p))) continue;
    if (overlap(s.rect, k.rect)) errors.push(`压进禁区：${s.id} × ${k.id}`);
  }
}
for (const p of paths) {
  const areas = keepOut.filter((k) => (p.mustStayIn ?? []).includes(k.id)).map((k) => k.rect);
  for (let i = 0; i < p.points.length - 1; i++) {
    const [ax, az] = p.points[i]; const [bx, bz] = p.points[i + 1];
    const n = Math.max(2, Math.ceil(Math.hypot(bx - ax, bz - az)));
    for (let k = 0; k <= n; k++) {
      const x = ax + ((bx - ax) * k) / n; const z = az + ((bz - az) * k) / n; const hw = p.halfWidth ?? 0.5;
      const box = { x0: x - hw, x1: x + hw, z0: z - hw, z1: z + hw };
      if (areas.length && !areas.some((a) => inside(box, a))) { errors.push(`路径越界：${p.id} @ (${x.toFixed(1)}, ${z.toFixed(1)})`); k = n; i = p.points.length; break; }
      const hit = solids.find((s) => !(p.ignore ?? []).some((q) => s.id.startsWith(q)) && overlap(box, s.rect));
      if (hit) { errors.push(`路径撞到：${p.id} × ${hit.id} @ (${x.toFixed(1)}, ${z.toFixed(1)})`); k = n; i = p.points.length; break; }
    }
  }
}
errors.push(...(L.extraChecks?.() ?? []));

console.log(`实体 ${solids.length} 个，禁区 ${keepOut.length} 个，路径 ${paths.length} 条`);
if (errors.length) {
  console.error(`✗ ${errors.length} 个问题：\n  ` + errors.join('\n  '));
  process.exit(1);
}
console.log('✓ layout 检查通过');
