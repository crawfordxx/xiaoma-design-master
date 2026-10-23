// 运动路径与缓动（子 Agent 只读）。所有运动都只由时间 t（秒）决定。

// 沿折线 path（[[x,z], ...]）以 speed m/s 循环移动；offset 用来对齐“某时刻经过某处”。
// 返回的 rotY 让物体本地 +X 朝前进方向
export function loopAlong(path, speed, offset, t) {
  const segs = []; let total = 0;
  for (let i = 0; i < path.length - 1; i++) {
    const [ax, az] = path[i]; const [bx, bz] = path[i + 1];
    const len = Math.hypot(bx - ax, bz - az); segs.push({ ax, az, bx, bz, len }); total += len;
  }
  let s = (((t * speed + offset) % total) + total) % total;
  for (const g of segs) {
    if (s <= g.len) {
      const k = s / g.len; const dx = (g.bx - g.ax) / g.len; const dz = (g.bz - g.az) / g.len;
      return { x: g.ax + (g.bx - g.ax) * k, z: g.az + (g.bz - g.az) * k, rotY: Math.atan2(-dz, dx), dir: [dx, dz] };
    }
    s -= g.len;
  }
  const g = segs[segs.length - 1];
  return { x: g.bx, z: g.bz, rotY: 0, dir: [1, 0] };
}

export const clamp01 = (v) => Math.min(1, Math.max(0, v));
export const lerp = (a, b, k) => a + (b - a) * k;
export const smoothstep = (a, b, v) => { const k = clamp01((v - a) / (b - a)); return k * k * (3 - 2 * k); };
export const easeInOutCubic = (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
