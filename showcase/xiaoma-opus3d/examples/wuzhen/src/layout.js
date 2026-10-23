// 乌镇（西栅原型）场景平面图 —— 全项目唯一的坐标来源。
// 单位：米。原点 = 十字河口中心；+X 朝东，+Z 朝南，Y 朝上。
// 地面（驳岸顶面）y = 0，水面 y = -1.2。
// 本文件只放数据，不依赖 three.js，node 可以直接 import 做检查。
import { rng } from './rng.js';

export const EXTENT = { x0: -120, x1: 120, z0: -80, z1: 80 };
export const LEVELS = { ground: 0, water: -1.2, bed: -3.2 };
export const BAY = 3.6; // 开间

// ---------- 河道 ----------
// rect 为水面范围；centerline 用于船线和镜头
export const rivers = [
  { id: 'main', name: '市河（东西向主河）', width: 12, rect: { x0: -130, x1: 130, z0: -6, z1: 6 },
    centerline: [[-130, 0], [130, 0]] },
  { id: 'branch', name: '支河（南北向）', width: 8, rect: { x0: -4, x1: 4, z0: -90, z1: 90 },
    centerline: [[0, -90], [0, 90]] },
];

// ---------- 桥 ----------
// axis = 桥面走向；from/to = 桥面两端在 axis 上的坐标（落在驳岸以外的地面上）
export const bridges = [
  { id: 'tongji', name: '通济桥', type: 'arch', axis: 'z', at: -14, from: -14, to: 14, width: 3.6,
    span: 10, riseAboveWater: 5, crosses: 'main' },
  { id: 'renji', name: '仁济桥', type: 'arch', axis: 'x', at: -14, from: -10, to: 10, width: 3.2,
    span: 7, riseAboveWater: 3.8, crosses: 'branch' },
  { id: 'flat-east', name: '东平桥', type: 'flat', axis: 'z', at: 62, from: -7, to: 7, width: 2.4,
    deckY: 1.2, crosses: 'main' },
  { id: 'flat-south', name: '南街小平桥', type: 'flat', axis: 'x', at: 8, from: -5, to: 5, width: 3,
    deckY: 1.0, crosses: 'branch' },
];

// ---------- 街巷与空地（只用于检查和地面铺装，不放建筑） ----------
export const streets = [
  { id: 'south-street', name: '南岸沿河石板街（廊棚下）', rect: { x0: -120, x1: 120, z0: 6, z1: 10 } },
  { id: 'north-lane', name: '北岸后巷', rect: { x0: -120, x1: 120, z0: -21, z1: -16 } },
  { id: 'south-lane', name: '南岸后巷', rect: { x0: -120, x1: 120, z0: 20, z1: 24 } },
  { id: 'branch-path-w', name: '支河西岸小路', rect: { x0: -7, x1: -4, z0: -80, z1: 80 } },
  { id: 'branch-path-e', name: '支河东岸小路', rect: { x0: 4, x1: 7, z0: -80, z1: 80 } },
  { id: 'plaza-nw', name: '桥里桥西北桥头', rect: { x0: -17, x1: -4, z0: -16, z1: -6 } },
  { id: 'plaza-ne', name: '仁济桥东桥头', rect: { x0: 4, x1: 11, z0: -16, z1: -6 } },
];

// ---------- 民居 ----------
// facing = 正门朝向；waterSide = 临水一侧（枕水人家），null 表示不临水
// detail: 'high' 临河第一排（镜头会近看），'low' 后排（主要看屋顶）
const ROWS = [
  { id: 'NA', zone: 'north', axis: 'x', band: [-16, -6], facing: 'N', waterSide: 'S', detail: 'high',
    pavilionChance: 0.5, segments: [[-118, -17.5], [11.5, 58.8], [65.2, 118]] },
  { id: 'NB', zone: 'north', axis: 'x', band: [-31, -21], facing: 'S', waterSide: null, detail: 'low',
    segments: [[-118, -7.5], [7.5, 118]] },
  { id: 'NW', zone: 'north', axis: 'z', band: [-17, -7], facing: 'E', waterSide: null, detail: 'high',
    segments: [[-78, -33]] },
  { id: 'NE', zone: 'north', axis: 'z', band: [7, 17], facing: 'W', waterSide: null, detail: 'high',
    segments: [[-78, -33]] },
  { id: 'SA', zone: 'south', axis: 'x', band: [10, 20], facing: 'N', waterSide: null, detail: 'high',
    shop: true, segments: [[-118, -17.5], [7.5, 118]] },
  { id: 'SB', zone: 'south', axis: 'x', band: [24, 34], facing: 'N', waterSide: null, detail: 'low',
    segments: [[-118, -7.5], [7.5, 118]] },
  { id: 'SW', zone: 'south', axis: 'z', band: [-17, -7], facing: 'E', waterSide: null, detail: 'high',
    segments: [[38, 78]] },
  { id: 'SC', zone: 'south', axis: 'x', band: [38, 48], facing: 'N', waterSide: null, detail: 'low',
    segments: [[62, 118]] },
];

const ROT = { S: 0, E: Math.PI / 2, N: Math.PI, W: -Math.PI / 2 };

function fillRow(row) {
  const r = rng(`row-${row.id}`);
  const out = [];
  const [b0, b1] = row.band;
  const depth = b1 - b0;
  for (const [s0, s1] of row.segments) {
    let cursor = s0;
    while (true) {
      const remaining = s1 - cursor;
      if (remaining < BAY * 2) break;
      const maxBays = Math.min(4, Math.floor(remaining / BAY));
      const bays = remaining < BAY * 5 ? maxBays : r.int(2, maxBays);
      const width = bays * BAY;
      const c = cursor + width / 2;
      const id = `${row.id}${String(out.length + 1).padStart(2, '0')}`;
      const floors = r.chance(0.12) ? 1 : 2;
      const eaveHeight = floors === 1 ? r.range(3.8, 4.3) : r.range(6.0, 6.9);
      const pavilion = row.pavilionChance && r.chance(row.pavilionChance)
        ? { depth: Number(r.range(1.8, 2.5).toFixed(2)) } : null;
      const footprint = row.axis === 'x'
        ? { x0: cursor, x1: cursor + width, z0: b0, z1: b1 }
        : { x0: b0, x1: b1, z0: cursor, z1: cursor + width };
      const center = row.axis === 'x' ? { x: c, z: (b0 + b1) / 2 } : { x: (b0 + b1) / 2, z: c };
      out.push({
        id, row: row.id, zone: row.zone, ...center,
        width, depth, bays, floors, eaveHeight: Number(eaveHeight.toFixed(2)),
        facing: row.facing, rotY: ROT[row.facing], waterSide: row.waterSide,
        gable: r.pick(['plain', 'plain', 'guanyin', 'horse']),
        shop: Boolean(row.shop), detail: row.detail, waterPavilion: pavilion, footprint,
      });
      // 约三分之一的位置留 1.2m 弄堂，其余山墙相接
      cursor += width + (r.chance(0.35) ? 1.2 : 0);
    }
  }
  return out;
}

export const houses = ROWS.flatMap(fillRow);

// 水阁：从临水一侧伸出到河面上，石柱木桩支撑
export function pavilionFootprint(h) {
  if (!h.waterPavilion) return null;
  const d = h.waterPavilion.depth;
  const f = h.footprint;
  switch (h.waterSide) {
    case 'S': return { x0: f.x0, x1: f.x1, z0: f.z1, z1: f.z1 + d };
    case 'N': return { x0: f.x0, x1: f.x1, z0: f.z0 - d, z1: f.z0 };
    default: return null;
  }
}

// ---------- 廊棚（南岸沿河，挂灯笼） ----------
// 在桥头处断开
export const corridors = [
  [-112, -17.5], [-10.5, -5.5], [5.5, 59.5], [64.5, 112],
].map(([x0, x1], i) => ({ id: `lp${i + 1}`, x0, x1, z0: 6.2, z1: 9.6, roofHigh: 3.4, roofLow: 2.7 }));

// 河埠头：伸进河里的下水石阶
export const waterSteps = [
  { id: 'ws1', bank: 'S', x: -86, width: 2.4, depth: 1.4 },
  { id: 'ws2', bank: 'S', x: -40, width: 2.4, depth: 1.4 },
  { id: 'ws3', bank: 'S', x: 24, width: 2.4, depth: 1.4 },
  { id: 'ws4', bank: 'S', x: 88, width: 2.4, depth: 1.4 },
  { id: 'ws5', bank: 'BW', z: -56, width: 2.0, depth: 1.2 },
  { id: 'ws6', bank: 'BE', z: 60, width: 2.0, depth: 1.2 },
].map((s) => {
  const half = s.width / 2;
  const rect = {
    S: { x0: s.x - half, x1: s.x + half, z0: 6 - s.depth, z1: 6 },
    BW: { x0: -4, x1: -4 + s.depth, z0: s.z - half, z1: s.z + half },
    BE: { x0: 4 - s.depth, x1: 4, z0: s.z - half, z1: s.z + half },
  }[s.bank];
  return { ...s, rect };
});

// ---------- 地标 ----------
export const dyeYard = {
  id: 'dye', name: '染坊晒布场', rect: { x0: 8, x1: 60, z0: 38, z1: 76 },
  workshop: { x0: 10, x1: 30, z0: 64, z1: 75 },        // 染坊作坊（一栋长屋）
  racks: { x0: 14, x1: 56, z0: 42, z1: 60, height: 8, rows: 5 }, // 晒布架区域
};

export const pagoda = { id: 'bailian', name: '白莲塔', x: -215, z: -215, floors: 7, height: 50, baseWidth: 9 };

// 区块以外的远景屋顶，填到半径 450m，外面是田野和雾
// fillRects = 区块内部的后排空地，用低精度屋顶群填满，避免航拍露出空地
export const backdrop = {
  innerRect: { x0: -125, x1: 125, z0: -85, z1: 85 },
  outerRadius: 450,
  fillRects: [
    { id: 'fill-nw', x0: -120, x1: -20, z0: -80, z1: -36 },
    { id: 'fill-ne', x0: 20, x1: 120, z0: -80, z1: -36 },
    { id: 'fill-sw', x0: -120, x1: -20, z0: 38, z1: 80 },
    { id: 'fill-se', x0: 62, x1: 120, z0: 51, z1: 80 },
  ],
};

// ---------- 树（trunk 为树干占地半径） ----------
export const trees = [
  ...[-116, -113.5, 114, 117].map((x, i) => ({ id: `wS${i}`, kind: 'willow', x, z: 7.2 })),
  ...[-75, -66, -57, -48, -39].map((z, i) => ({ id: `wNW${i}`, kind: 'willow', x: -5.6, z })),
  ...[-71, -62, -53, -44].map((z, i) => ({ id: `wNE${i}`, kind: 'willow', x: 5.6, z })),
  ...[43, 52, 62, 71].map((z, i) => ({ id: `wSW${i}`, kind: 'willow', x: -5.6, z })),
  ...[44, 58, 72].map((z, i) => ({ id: `wSE${i}`, kind: 'willow', x: 5.6, z })),
  { id: 'cNE', kind: 'camphor', x: 8.6, z: -8.6 },
  { id: 'cD1', kind: 'camphor', x: 57, z: 73 },
  { id: 'cD2', kind: 'camphor', x: 36, z: 70 },
].map((t) => ({ ...t, trunk: t.kind === 'willow' ? 0.35 : 0.6 }));

// ---------- 摇橹船航线 ----------
// 位置 = 起点 + (t * speed + offset) 沿航线取模；offset 已算好，让 1 号船在 t≈10.5s 穿过通济桥
export const boats = [
  { id: 'boat1', from: [-125, 2.0], to: [125, 2.0], speed: 1.1, offset: 99.45, length: 7.5, beam: 1.7 },
  { id: 'boat2', from: [125, -1.0], to: [-125, -1.0], speed: 0.9, offset: 40, length: 7.0, beam: 1.6 },
  { id: 'boat3', from: [0.8, -85], to: [0.8, 85], speed: 1.0, offset: 20, length: 6.5, beam: 1.5 },
];

// ---------- 光照 ----------
// 太阳在正西偏南约 10°（基本顺着主河），高度 6° → 1°；灯笼 0.25 → 1
export const lighting = {
  // 方位角：0=北(-Z)，90=东(+X)，180=南(+Z)，270=西(-X)。正西偏南 10° = 260°
  // 水平方向向量 = (sin(b), -cos(b))
  sunBearingDeg: 260,
  sunElevationStartDeg: 6,
  sunElevationEndDeg: 1,
  lanternStart: 0.25,
  lanternEnd: 1.0,
  duration: 70,
};
