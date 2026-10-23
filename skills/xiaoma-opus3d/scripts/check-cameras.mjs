// 镜头路径碰撞检查（通用版）：按 1/30 秒采样每个镜头的相机位置，看是否进到 layout.CHECK.volumes 里
// 或低于地面。volumes 是粗体积（占地 × 高度，外加安全余量），只抓明显穿模；细节靠 contact.mjs 接触表看。
import * as L from '../src/layout.js';
import { SHOTS, SHOT_LEN } from '../src/cameras.js';

const vols = L.CHECK.volumes ?? [];
const floorAt = L.CHECK.floorAt ?? (() => (L.LEVELS.ground ?? 0) + 0.3); // 可在 CHECK 里自定义（比如水面比地面低）
let bad = 0;
SHOTS.forEach((shot, i) => {
  const hits = new Map();
  const add = (id, u) => hits.set(id, (hits.get(id) ?? []).concat(u.toFixed(2)));
  for (let f = 0; f < SHOT_LEN * 30; f++) {
    const u = f / 30; const t = i * SHOT_LEN + u;
    const { pos: [x, y, z] } = shot.pose(u, t);
    if (y < floorAt(x, z)) add('地面以下', u);
    for (const v of vols) {
      const r = v.rect;
      if (x > r.x0 && x < r.x1 && z > r.z0 && z < r.z1 && y > v.y0 && y < v.y1 && !v.open?.(x, y, z)) add(v.id, u);
    }
  }
  if (hits.size) bad++;
  console.log(`${hits.size ? '✗' : '✓'} ${shot.name}`);
  for (const [id, us] of hits) console.log(`    ${id}: u=${us[0]}–${us[us.length - 1]}（${us.length} 帧）`);
});
process.exit(bad ? 1 : 0);
