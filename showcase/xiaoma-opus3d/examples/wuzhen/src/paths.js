// 船线与缓动（子 Agent 只读）。所有运动都只由时间 t（秒）决定。
import { boats, LEVELS } from './layout.js';

// 船在 t 时刻的位置。船头朝本地 +X；返回的 rotY 直接赋给 group.rotation.y
export function boatAt(boatOrId, t) {
  const b = typeof boatOrId === 'string' ? boats.find((x) => x.id === boatOrId) : boatOrId;
  const [fx, fz] = b.from; const [tx, tz] = b.to;
  const len = Math.hypot(tx - fx, tz - fz);
  const dx = (tx - fx) / len; const dz = (tz - fz) / len;
  const s = (((t * b.speed + b.offset) % len) + len) % len;
  return { x: fx + dx * s, y: LEVELS.water, z: fz + dz * s, rotY: Math.atan2(-dz, dx), dir: [dx, dz] };
}

export const clamp01 = (v) => Math.min(1, Math.max(0, v));
export const lerp = (a, b, k) => a + (b - a) * k;
export const smoothstep = (a, b, v) => { const k = clamp01((v - a) / (b - a)); return k * k * (3 - 2 * k); };
export const easeInOutCubic = (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
