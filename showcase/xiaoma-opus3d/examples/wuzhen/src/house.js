// 参数化民居生成器（子 Agent 只读）。两岸所有民居都必须用 buildHouse 生成，保证风格统一。
// 局部坐标：开间方向 = X（-W/2 ~ W/2），进深方向 = Z（-D/2 ~ D/2），正门朝 +Z，地面 y=0。
// 摆放：position = (h.x, 0, h.z)，rotation.y = h.rotY（layout 已算好）。
import * as THREE from 'three';
import { boxM, place, mergeByMaterial, tiledRoofSlope, eaveTiles } from './geom.js';
import { pavilionFootprint } from './layout.js';

export const HOUSE = {
  plinth: 0.3,      // 台基高
  firstFloor: 3.2,  // 底层层高
  gable: 0.24,      // 山墙厚
  overhang: 0.6,    // 前后檐出挑
  slope: 0.5,       // 屋面坡度（高/水平距）
};

function flipFaces(g) {
  const idx = g.index.array;
  for (let i = 0; i < idx.length; i += 3) { const t = idx[i + 1]; idx[i + 1] = idx[i + 2]; idx[i + 2] = t; }
  g.computeVertexNormals();
  return g;
}

// 一面坡（瓦面 + 檐下底板 + 封檐板 + 可选滴水瓦），局部坐标与 tiledRoofSlope 相同
function roofSlope(parts, M, { width, run, rise, sag, detail, eave = true }) {
  const out = [];
  out.push({ geom: tiledRoofSlope({ width, run, rise, sag, detail }), mat: M.tile });
  const under = flipFaces(tiledRoofSlope({ width, run, rise, sag, detail: 'low', tileDepth: 0 }));
  out.push({ geom: place(under, { y: -0.12 }), mat: M.woodDark });
  out.push({ geom: place(boxM(width, 0.16, 0.05), { y: -rise - 0.06, z: run }), mat: M.woodDark });
  if (eave && detail === 'high') {
    for (const p of eaveTiles(width, M)) out.push({ geom: place(p.geom, { y: -rise, z: run }), mat: p.mat });
  }
  return (t) => { for (const p of out) parts.push({ geom: place(p.geom, t), mat: p.mat }); };
}

// 花格窗：底板（亮灯或暗）+ 外框 + 格心。局部：窗面中心在原点，朝 +Z
function latticeWindow(parts, M, { w, h, lit, detail }) {
  const out = [];
  out.push({ geom: boxM(w, h, 0.03), mat: lit ? M.windowGlow : M.darkInterior });
  const f = 0.07;
  out.push({ geom: place(boxM(w + f, f, 0.08), { y: h / 2, z: 0.03 }), mat: M.woodDark });
  out.push({ geom: place(boxM(w + f, f, 0.08), { y: -h / 2, z: 0.03 }), mat: M.woodDark });
  out.push({ geom: place(boxM(f, h, 0.08), { x: -w / 2, z: 0.03 }), mat: M.woodDark });
  out.push({ geom: place(boxM(f, h, 0.08), { x: w / 2, z: 0.03 }), mat: M.woodDark });
  if (detail === 'high') {
    const bar = 0.025;
    for (let x = -w / 2 + 0.15; x < w / 2 - 0.05; x += 0.15) {
      out.push({ geom: place(boxM(bar, h, 0.03), { x, z: 0.04 }), mat: M.woodDark });
    }
    for (let y = -h / 2 + 0.2; y < h / 2 - 0.05; y += 0.2) {
      out.push({ geom: place(boxM(w, bar, 0.03), { y, z: 0.045 }), mat: M.woodDark });
    }
  }
  return (t) => { for (const p of out) parts.push({ geom: place(p.geom, t), mat: p.mat }); };
}

function gableShape(type, D, E, R) {
  const s = new THREE.Shape();
  const P = HOUSE.plinth; const S = HOUSE.slope; const half = D / 2;
  s.moveTo(-half, P);
  s.lineTo(half, P);
  if (type === 'horse') {
    const u1 = 0.62 * half; const u2 = 0.28 * half;
    const t0 = E + (half - u1) * S + 0.7; const t1 = E + (half - u2) * S + 0.7; const t2 = R + 0.7;
    [[half, t0], [u1, t0], [u1, t1], [u2, t1], [u2, t2], [-u2, t2], [-u2, t1], [-u1, t1], [-u1, t0], [-half, t0]]
      .forEach(([u, v]) => s.lineTo(u, v));
    return { shape: s, steps: [[u1, half, t0], [u2, u1, t1], [-u2, u2, t2], [-u1, -u2, t1], [-half, -u1, t0]] };
  }
  if (type === 'guanyin') {
    s.lineTo(half, E + 0.3);
    s.bezierCurveTo(half * 0.8, E + 0.5, half * 0.45, R + 1.0, 0, R + 1.0);
    s.bezierCurveTo(-half * 0.45, R + 1.0, -half * 0.8, E + 0.5, -half, E + 0.3);
    s.closePath();
    return { shape: s, curve: true };
  }
  s.lineTo(half, E + 0.15);
  s.lineTo(0, R + 0.3);
  s.lineTo(-half, E + 0.15);
  s.closePath();
  return { shape: s };
}

// 山墙 + 墙帽。side = -1（左）或 1（右）
function addGable(parts, M, h, side, W, D, E, R) {
  const T = HOUSE.gable;
  const { shape, steps, curve } = gableShape(h.gable, D, E, R);
  const g = new THREE.ExtrudeGeometry(shape, { depth: T, bevelEnabled: false, curveSegments: 10 });
  // 旋转后：shape.x → 局部 z，shape.y → y，拉伸方向 → 局部 -x（宽度 T）
  place(g, { ry: -Math.PI / 2, x: side < 0 ? -W / 2 + T : W / 2 });
  parts.push({ geom: g, mat: M.wall });
  const cx = side < 0 ? -W / 2 + T / 2 : W / 2 - T / 2;
  const capW = T + 0.28;
  if (steps) {
    for (const [a, b, top] of steps) {
      parts.push({ geom: place(boxM(capW, 0.16, b - a + 0.3), { x: cx, y: top + 0.08, z: (a + b) / 2 }), mat: M.tileRidge });
    }
  } else if (curve) {
    const half = D / 2;
    const c1 = new THREE.CubicBezierCurve(new THREE.Vector2(half, E + 0.3), new THREE.Vector2(half * 0.8, E + 0.5),
      new THREE.Vector2(half * 0.45, R + 1.0), new THREE.Vector2(0, R + 1.0));
    const pts = [...c1.getPoints(12), ...c1.getPoints(12).reverse().slice(1).map((p) => new THREE.Vector2(-p.x, p.y))];
    for (let i = 0; i < pts.length - 1; i++) {
      const a = pts[i]; const b = pts[i + 1];
      const len = a.distanceTo(b) + 0.04;
      const ang = Math.atan2(b.y - a.y, b.x - a.x);
      parts.push({ geom: place(boxM(capW, 0.14, len), { x: cx, y: (a.y + b.y) / 2 + 0.06, z: (a.x + b.x) / 2, rx: -ang }), mat: M.tileRidge });
    }
  } else {
    const half = D / 2; const top = R + 0.3; const base = E + 0.15;
    const len = Math.hypot(half, top - base); const ang = Math.atan2(top - base, half);
    for (const dir of [1, -1]) {
      parts.push({ geom: place(boxM(capW, 0.14, len + 0.1), { x: cx, y: (top + base) / 2 + 0.07, z: (dir * half) / 2, rx: dir * ang }), mat: M.tileRidge });
    }
  }
}

// 某一面立面（front: z=+D/2 朝 +Z；back: z=-D/2 朝 -Z）
function addFacade(parts, M, r, h, which, W, D, E) {
  const T = HOUSE.gable; const P = HOUSE.plinth; const F1 = HOUSE.firstFloor;
  const hi = h.detail === 'high';
  const Wi = W - 2 * T; const bays = h.bays; const bw = Wi / bays;
  const ry = which === 'front' ? 0 : Math.PI;
  const zEdge = D / 2;
  // 把立面局部坐标（x, y, 距墙面向外 dz）转到房屋局部坐标
  const at = (x, y, dz, extra = {}) => (which === 'front'
    ? { x, y, z: zEdge + dz, ry, ...extra } : { x: -x, y, z: -zEdge - dz, ry, ...extra });
  const watery = which === 'back' && h.waterSide;
  const woodUpper = which === 'front' || watery;
  const twoFloors = h.floors === 2;
  const f2 = P + F1;

  if (which === 'back' && !watery) {
    // 不临水的背立面：整面粉墙，二层开小窗
    parts.push({ geom: place(boxM(Wi, E - P, 0.2), at(0, (E + P) / 2, -0.1)), mat: M.wall });
    if (twoFloors) {
      for (let b = 0; b < bays; b += 2) {
        const x = -Wi / 2 + bw * (b + 0.5);
        latticeWindow(parts, M, { w: 0.9, h: 0.8, lit: r.chance(0.3), detail: h.detail })(at(x, f2 + 1.4, 0.02));
      }
    }
    return;
  }

  // 柱与梁
  for (let k = 0; k <= bays; k++) {
    parts.push({ geom: place(boxM(0.2, E - P, 0.2), at(-Wi / 2 + k * bw, (E + P) / 2, -0.1)), mat: M.woodDark });
  }
  parts.push({ geom: place(boxM(Wi, 0.2, 0.24), at(0, E - 0.1, -0.1)), mat: M.woodDark });
  if (twoFloors) parts.push({ geom: place(boxM(Wi, 0.25, 0.24), at(0, f2, -0.1)), mat: M.woodDark });

  // 底层
  const groundTop = twoFloors ? f2 - 0.12 : E - 0.2;
  const gh = groundTop - P;
  for (let b = 0; b < bays; b++) {
    const x = -Wi / 2 + bw * (b + 0.5); const inner = bw - 0.2;
    if (watery) {
      // 临水底层：粉墙，开一扇后门或小窗
      parts.push({ geom: place(boxM(inner, gh, 0.18), at(x, P + gh / 2, -0.12)), mat: M.wall });
      if (b === Math.floor(bays / 2)) {
        parts.push({ geom: place(boxM(1.0, 2.1, 0.08), at(x, P + 1.05, -0.0)), mat: M.wood });
      } else if (hi) {
        latticeWindow(parts, M, { w: 0.9, h: 0.7, lit: r.chance(0.35), detail: h.detail })(at(x, P + 1.9, 0.0));
      }
      continue;
    }
    const open = which === 'front' && h.shop && r.chance(0.6);
    if (open && hi) {
      // 敞开的店面：退进去的室内暖光 + 柜台
      parts.push({ geom: place(boxM(inner, gh, 0.05), at(x, P + gh / 2, -1.6)), mat: M.interiorGlow });
      parts.push({ geom: place(boxM(0.05, gh, 1.5), at(x - inner / 2, P + gh / 2, -0.85)), mat: M.darkInterior });
      parts.push({ geom: place(boxM(0.05, gh, 1.5), at(x + inner / 2, P + gh / 2, -0.85)), mat: M.darkInterior });
      parts.push({ geom: place(boxM(inner, 0.05, 1.5), at(x, groundTop - 0.03, -0.85)), mat: M.woodDark });
      parts.push({ geom: place(boxM(inner * 0.7, 0.9, 0.45), at(x, P + 0.45, -0.5)), mat: M.wood });
    } else {
      // 排门板
      parts.push({ geom: place(boxM(inner, gh, 0.08), at(x, P + gh / 2, -0.15)), mat: M.wood });
      if (hi) parts.push({ geom: place(boxM(inner, 0.1, 0.1), at(x, P + 0.05, -0.1)), mat: M.woodDark }); // 门槛
    }
  }

  // 二层
  if (twoFloors) {
    const y0 = f2 + 0.13; const h2 = E - 0.2 - y0;
    parts.push({ geom: place(boxM(Wi, h2, 0.08), at(0, y0 + h2 / 2, -0.18)), mat: woodUpper ? M.wood : M.wall });
    for (let b = 0; b < bays; b++) {
      const x = -Wi / 2 + bw * (b + 0.5);
      const w = Math.min(bw - 0.6, 2.2); const wh = Math.min(1.15, h2 - 0.5);
      latticeWindow(parts, M, { w, h: wh, lit: r.chance(0.45), detail: h.detail })(at(x, y0 + h2 * 0.55, -0.12));
    }
    // 腰檐（前立面，或临水但没有水阁的背立面）
    if (which === 'front' || !h.waterPavilion) {
      roofSlope(parts, M, { width: W, run: 0.9, rise: 0.42, sag: 0.03, detail: h.detail })(at(0, f2 + 0.62, -0.05));
    }
  }
}

function addPavilion(parts, M, r, h, W, D) {
  const d = h.waterPavilion.depth; const hi = h.detail === 'high';
  const Wp = W - 0.2; const z0 = -D / 2; const zOut = z0 - d;
  const floorTop = 0.4; const wallTop = 2.6;
  // 石柱 + 横梁
  const n = Math.max(2, Math.round(Wp / 2.4) + 1);
  for (let i = 0; i < n; i++) {
    const x = -Wp / 2 + 0.15 + ((Wp - 0.3) * i) / (n - 1);
    parts.push({ geom: place(boxM(0.3, 3.4, 0.3), { x, y: -3.2 + 1.7, z: zOut + 0.2 }), mat: M.embankment });
    if (hi) parts.push({ geom: place(boxM(0.12, 0.12, d), { x, y: 0.08, z: z0 - d / 2 }), mat: M.woodDark });
  }
  parts.push({ geom: place(boxM(Wp, 0.25, d), { y: floorTop - 0.125, z: z0 - d / 2 }), mat: M.wood });
  parts.push({ geom: place(boxM(Wp, 0.22, 0.2), { y: floorTop - 0.3, z: zOut + 0.2 }), mat: M.woodDark });
  // 外墙：下槛板 + 通长花窗
  parts.push({ geom: place(boxM(Wp, 0.9, 0.06), { y: floorTop + 0.45, z: zOut + 0.03 }), mat: M.wood });
  const panes = Math.max(2, Math.round(Wp / 1.2));
  const pw = Wp / panes;
  for (let i = 0; i < panes; i++) {
    const x = -Wp / 2 + pw * (i + 0.5);
    latticeWindow(parts, M, { w: pw - 0.12, h: wallTop - floorTop - 1.0, lit: r.chance(0.4), detail: h.detail })(
      { x, y: (floorTop + 0.9 + wallTop) / 2, z: zOut, ry: Math.PI });
  }
  // 两侧山面：木板墙上开一扇花窗，从河道纵向看过去不至于是整块木板
  for (const sx of [-1, 1]) {
    parts.push({ geom: place(boxM(0.06, wallTop - floorTop, d), { x: sx * Wp / 2, y: (floorTop + wallTop) / 2, z: z0 - d / 2 }), mat: M.wood });
    latticeWindow(parts, M, { w: Math.min(1.1, d - 0.6), h: wallTop - floorTop - 1.2, lit: r.chance(0.4), detail: h.detail })(
      { x: sx * (Wp / 2 + 0.04), y: (floorTop + 0.9 + wallTop) / 2 + 0.1, z: z0 - d / 2, ry: sx * Math.PI / 2 });
  }
  // 单坡屋面，从主墙向河面外挑
  const run = d + 0.5; const rise = run * 0.3;
  roofSlope(parts, M, { width: Wp + 0.3, run, rise, sag: 0.04, detail: h.detail })({ y: wallTop + rise + 0.1, z: z0, ry: Math.PI });
}

export function buildHouse(h, { materials: M, rng }) {
  const r = rng(`house-${h.id}`);
  const W = h.width; const D = h.depth; const E = h.eaveHeight;
  const P = HOUSE.plinth; const S = HOUSE.slope; const OVER = HOUSE.overhang;
  const R = E + (D / 2) * S;
  const parts = [];

  parts.push({ geom: place(boxM(W, P, D), { y: P / 2 }), mat: M.embankment });
  addGable(parts, M, h, -1, W, D, E, R);
  addGable(parts, M, h, 1, W, D, E, R);
  addFacade(parts, M, r, h, 'front', W, D, E);
  addFacade(parts, M, r, h, 'back', W, D, E);

  // 双坡屋面 + 屋脊
  const run = D / 2 + OVER; const sag = 0.12 + r.range(0, 0.08);
  const slopeOpts = { width: W, run, rise: run * S, sag, detail: h.detail };
  roofSlope(parts, M, slopeOpts)({ y: R + 0.05 });
  roofSlope(parts, M, slopeOpts)({ y: R + 0.05, ry: Math.PI });
  parts.push({ geom: place(boxM(W + 0.1, 0.34, 0.3), { y: R + 0.2 }), mat: M.tileRidge });
  if (h.detail === 'high') {
    for (const sx of [-1, 1]) { // 屋脊两端微微起翘
      parts.push({ geom: place(boxM(0.45, 0.22, 0.26), { x: sx * (W / 2 - 0.1), y: R + 0.45, rz: -sx * 0.45 }), mat: M.tileRidge });
    }
  }
  if (h.waterPavilion) addPavilion(parts, M, r, h, W, D);

  const group = mergeByMaterial(parts);
  group.name = `house-${h.id}`;
  group.position.set(h.x, 0, h.z);
  group.rotation.y = h.rotY;
  group.userData.house = h;
  return group;
}

// 房屋局部坐标 → 世界坐标
export function houseToWorld(h, x, y, z) {
  const c = Math.cos(h.rotY); const s = Math.sin(h.rotY);
  return { x: h.x + x * c + z * s, y, z: h.z - x * s + z * c };
}

// 挂灯笼、招幌用的锚点（世界坐标）
// frontEave: 正门一侧每开间檐下的挂点；waistEave: 腰檐下挂点（仅两层）；doors: 每开间底层中心
// waterEave: 临水一侧（含水阁）每开间檐下挂点
export function houseAnchors(h) {
  const T = HOUSE.gable; const P = HOUSE.plinth; const F1 = HOUSE.firstFloor;
  const Wi = h.width - 2 * T; const bw = Wi / h.bays; const D = h.depth; const E = h.eaveHeight;
  const xs = Array.from({ length: h.bays }, (_, b) => -Wi / 2 + bw * (b + 0.5));
  const front = xs.map((x) => houseToWorld(h, x, E - 0.7, D / 2 + 0.35));
  const waist = h.floors === 2 ? xs.map((x) => houseToWorld(h, x, P + F1 + 0.05, D / 2 + 0.6)) : [];
  const doors = xs.map((x) => houseToWorld(h, x, P + 1.2, D / 2 + 0.05));
  let water = [];
  if (h.waterSide) {
    water = pavilionFootprint(h)
      ? xs.map((x) => houseToWorld(h, -x, 2.3, -D / 2 - h.waterPavilion.depth - 0.4))
      : xs.map((x) => houseToWorld(h, -x, E - 0.7, -D / 2 - 0.4));
  }
  return { front, waist, doors, water, ridgeY: E + (D / 2) * HOUSE.slope };
}
