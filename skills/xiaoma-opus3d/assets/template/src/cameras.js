// 镜头调度：10 个镜头 × 7 秒。每个镜头从小物件特写开始 → 停留约 1 秒 → 加速拉远 → 最后约 1.5 秒缓停。
// 拉远用“指数距离”：相机到焦点的距离按 d0·(d1/d0)^p 变化，画面缩放感是匀速的，
// 不会出现一开始就把特写物件甩没的情况。
import * as THREE from 'three';
import { smoothstep } from './paths.js';

export const SHOT_LEN = 7;
const HOLD = 1.0;

// 拉远进度 0~1：停留段几乎不动；之后二次方加速，k=A 处平滑衔接四次方缓停
const A = 0.35;
const CA = 1 / (A * A + (A * (1 - A)) / 2);
const CB = (CA * A) / (2 * Math.pow(1 - A, 3));
export function pullProgress(u) {
  if (u <= HOLD) return 0.012 * (u / HOLD);
  const k = Math.min(1, (u - HOLD) / (SHOT_LEN - HOLD));
  const f = k < A ? CA * k * k : 1 - CB * Math.pow(1 - k, 4);
  return 0.012 + 0.988 * f;
}

const v3 = (a) => new THREE.Vector3(...a);

// close/wide: { pos, target, fov }。focusOffset(t) 可选：让焦点跟着运动物体（比如船）
// focusEase：焦点从特写物件移向远景目标的进度区间（按拉远进度 p）。相机离物件还近时焦点不能先走，否则会被带进墙里
function makeShot({ name, close, wide, focusOffset, arcUp = 0, focusEase = [0, 0.85] }) {
  const c0 = v3(close.pos); const f0 = v3(close.target);
  const c1 = v3(wide.pos); const f1 = v3(wide.target);
  const off0 = c0.clone().sub(f0); const off1 = c1.clone().sub(f1);
  const d0 = off0.length(); const d1 = off1.length();
  const dir0 = off0.normalize(); const dir1 = off1.normalize();
  return {
    name,
    pose(u, t) {
      const p = pullProgress(u);
      const focus = f0.clone().lerp(f1, smoothstep(focusEase[0], focusEase[1], p));
      if (focusOffset) focus.add(focusOffset(t, p));
      const dir = dir0.clone().lerp(dir1, smoothstep(0, 1, p)).normalize();
      const d = d0 * Math.pow(d1 / d0, p);
      const pos = focus.clone().addScaledVector(dir, d);
      pos.y += arcUp * Math.sin(Math.PI * p); // 中途抬高一点，避免穿过屋檐
      return { pos: pos.toArray(), target: focus.toArray(), fov: close.fov + (wide.fov - close.fov) * p };
    },
  };
}

// 每个镜头：close = 特写起幅，wide = 远景落幅。坐标从各区块的 review 汇报里拿。
// 写完先跑 scripts/check-cameras.mjs（路径穿模）和 scripts/contact.mjs（接触表），两样都过了再出片。
// 例：
// makeShot({ name: '1 灯笼穗 → 整条街',
//   close: { pos: [7.66, 1.98, 6.44], target: [7.53, 1.95, 6.8], fov: 40 },
//   wide: { pos: [45, 5, -4], target: [4, 2.5, 8], fov: 50 },
//   focusEase: [0.4, 1],   // 相机还贴着物件时焦点别先走，否则会被带进墙里
//   arcUp: 4,              // 路径中途抬高，越过屋顶
//   focusOffset: (t, p) => new THREE.Vector3(...) }) // 焦点跟运动物体
export const SHOTS = [];

export function shotAt(t) {
  if (!SHOTS.length) return { pos: [-60, 40, 60], target: [0, 0, 0], fov: 45 };
  const i = Math.min(SHOTS.length - 1, Math.floor(t / SHOT_LEN));
  return SHOTS[i].pose(t - i * SHOT_LEN, t);
}

export { makeShot };
