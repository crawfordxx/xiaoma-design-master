// 镜头调度：10 个镜头 × 7 秒。每个镜头从小物件特写开始 → 停留约 1 秒 → 加速拉远 → 最后约 1.5 秒缓停。
// 拉远用“指数距离”：相机到焦点的距离按 d0·(d1/d0)^p 变化，画面缩放感是匀速的，
// 不会出现一开始就把特写物件甩没的情况。
import * as THREE from 'three';
import { boatAt, smoothstep } from './paths.js';

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

// 1 号船在镜头 2 的起点（t=7）的 x，用来让焦点跟船
const boat1X7 = boatAt('boat1', 7).x;
const followBoat = (t, p) => new THREE.Vector3((boatAt('boat1', t).x - boat1X7) * (1 - smoothstep(0.2, 0.9, p)), 0, 0);

// 特写坐标来自各区块的汇报（review-*.md）；标 TODO 的等 landmarks 汇报后校准
export const SHOTS = [
  makeShot({ name: '1 廊棚灯笼穗 → 整条廊棚街', // houses-south：lp3 第一盏，挂钩 (7.53, 2.678, 6.8)
    close: { pos: [7.66, 1.98, 6.44], target: [7.53, 1.95, 6.8], fov: 40 },
    wide: { pos: [45, 5, -4], target: [4, 2.5, 8], fov: 50 } }),
  makeShot({ name: '2 船橹入水 → 摇橹船穿过通济桥', // water：t≈7.3 橹叶入水点 (-22.48, 1.85)
    close: { pos: [-21.8, -0.8, 2.7], target: [-22.48, -1.1, 1.85], fov: 40 },
    wide: { pos: [6, 1.6, 1.6], target: [-14, 1.8, 0.2], fov: 48 }, focusOffset: followBoat }), // 从拱洞中部穿过
  makeShot({ name: '3 通济桥望柱 → 桥里桥全貌', // bridges：拱顶西侧望柱头
    close: { pos: [-16.25, 6.45, 1.25], target: [-15.65, 6.35, 0.78], fov: 38 },
    wide: { pos: [-48, 5.5, 2], target: [-10, 2.5, -8], fov: 46 }, focusEase: [0.35, 1] }), // 从主河西段的河面上看过去，太阳在身后
  makeShot({ name: '4 蓝印花布 → 染坊晒布场', // landmarks：参考机位 28.5,4.5,40.2 → 31,5,43.9，推近到 1.2m
    close: { pos: [30.33, 4.87, 42.9], target: [31, 5, 43.9], fov: 40 },
    wide: { pos: [63, 9, 36], target: [34, 4, 52], fov: 52 } }), // 机位在 SB/SC 两排之间的巷子上空
  makeShot({ name: '5 河埠头湿石阶 → 支河两岸人家', // terrain：ws6 在支河东岸 (x=4, z=60)，朝西受光（ws3 朝北，傍晚背光）
    close: { pos: [0.9, -0.35, 60.1], target: [3.6, -0.95, 60], fov: 42 }, // 用地形 Agent 验证过的 ws6 正面机位
    wide: { pos: [0.5, 4.5, 88], target: [0, 3, 25], fov: 48 }, focusEase: [0.4, 1], arcUp: 3 }),
  makeShot({ name: '6 檐口滴水瓦 → 连片黛瓦屋顶', // NA06 临水檐口 y≈6.2, z≈-5.4
    close: { pos: [-46.5, 5.9, -4.6], target: [-46.9, 6.15, -5.4], fov: 40 },
    wide: { pos: [-52, 32, 22], target: [-55, 6, -22], fov: 50 }, focusEase: [0.45, 1] }), // 向南向上拉，从河面上方升起，不横穿邻屋
  makeShot({ name: '7 水阁花窗 → 水阁一排和倒影', // NA05 水阁外墙 z=-4.1
    close: { pos: [-64.3, 2.0, -3.4], target: [-64.4, 1.95, -4.1], fov: 40 },
    wide: { pos: [-48, 2.2, 4.5], target: [-68, 2.5, -6], fov: 50 } }),
  makeShot({ name: '8 柳枝梢 → 顺着支河的长镜头', // landmarks：wNW4 梢头 (-0.96, 0.54, -38.54)
    close: { pos: [-0.45, 0.7, -38.5], target: [-0.94, 0.54, -38.5], fov: 40 },
    wide: { pos: [1.5, 3.5, -22], target: [0, 3, -80], fov: 40 }, focusEase: [0.3, 1] }),
  makeShot({ name: '9 酒旗"三白酒" → 街市', // houses-south：旗面中心 (-50.82, 5.23, 6.08)，正面朝河
    close: { pos: [-50.7, 5.3, 3.9], target: [-50.82, 5.4, 6.08], fov: 40 }, // 起幅要露出完整的“三”字
    wide: { pos: [-25, 4, -4], target: [-55, 3, 9], fov: 50 } }),
  makeShot({ name: '10 逆光柳叶 → 整片水乡航拍', // landmarks：wS3 梢头 (120.62, 0.48, 4.81)；主河东头朝西整条河开阔，夕阳正在叶子背后
    close: { pos: [121.25, 0.42, 4.86], target: [120.62, 0.52, 4.83], fov: 40 }, // 平视略仰，叶子背后正是西边地平线上的夕阳
    wide: { pos: [150, 70, 25], target: [-30, 0, -20], fov: 50 }, focusEase: [0.4, 1], arcUp: 4 }), // 朝西航拍：夕阳、全镇、西北角的白莲塔剪影
];

export function shotAt(t) {
  if (!SHOTS.length) return { pos: [-60, 40, 60], target: [0, 0, 0], fov: 45 };
  const i = Math.min(SHOTS.length - 1, Math.floor(t / SHOT_LEN));
  return SHOTS[i].pose(t - i * SHOT_LEN, t);
}

export { makeShot, boatAt };
