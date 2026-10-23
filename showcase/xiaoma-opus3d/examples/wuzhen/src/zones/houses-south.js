// 南岸区块（houses-south）：SA/SB/SW/SC 四排民居 + 沿河廊棚（木柱、单坡瓦顶、挂落、美人靠）
// + 廊下红灯笼（随 t 轻摆）+ 店招、招幌 + 三白酒旗（布面顶点动画）。
// 坐标全部由 layout 推导；随机数一律 rng('houses-south-<物件>')；update(t) 只由 t 决定。
const ZONE = 'houses-south';

// ---------- 廊棚尺寸（z 方向的位置都落在 layout.corridors 的 z0~z1 内） ----------
const PITCH = 3.6;        // 目标柱距
const INSET = 0.25;       // 端柱离廊棚端头
const ROOF_SAG = 0.03;    // 单坡屋面举折
const UNDER = 0.12;       // 望板在瓦面下的距离（与 house.js 一致）
const Z_WATER = 6.42;     // 靠水一排柱中心
const Z_SHOP = 9.42;      // 靠店一排柱中心
const Z_MID = 7.92;       // 中檩
const Z_LANTERN = 6.8;    // 灯笼挂点
const Y_CURB = 0.04;      // 靠水柱脚落在 terrain 的路沿（z 6.4–6.8）顶面
const Y_COPING = 0.02;    // 驳岸压顶石顶面（酒旗杆脚）
const STEP_KEEP = 1.0;    // 边柱附近 1m 内的原有柱子去掉，避免柱子挤在一起
const BACK_Z0 = 6.34;     // 美人靠靠背根部
const BACK_LEAN = 0.3;    // 靠背向河面外弯的距离
const SIGN = { w: 2.4, h: 0.45, y: 2.78 }; // 门楣上，避开廊棚靠店一侧的檐枋
const BANNER = { w: 0.4, h: 1.6, z: 8.85 };

// ---------- 灯笼尺寸（局部坐标：原点 = 挂钩，向 -Y 下垂） ----------
const LAN = { cord: 0.12, cap: 0.035, rx: 0.21, ry: 0.19 };
LAN.bodyTop = -LAN.cord - LAN.cap + 0.025;
LAN.yc = LAN.bodyTop - LAN.ry;
LAN.capBottom = LAN.yc - LAN.ry + 0.025 - LAN.cap;
LAN.tassel = LAN.capBottom - 0.004; // 穗子挂点

// ---------- 酒旗 ----------
const FLAG = { w: 0.95, h: 2.375, poleH: 6.9, armY: 6.45, armLen: 1.2, z: 6.08, poleR: 0.045 };

const SHOP_NAMES = [
  { sign: '同泰酱园', banner: '酱' }, { sign: '望河茶馆', banner: '茶' }, { sign: '恒丰布庄', banner: '布' },
  { sign: '姑嫂糕点', banner: '糕点' }, { sign: '枕水客栈', banner: '客栈' }, { sign: '竹器老铺', banner: '竹器' },
  { sign: '蓝印染坊布', banner: '染坊' }, { sign: '南北杂货', banner: '杂货' }, { sign: '济世药号', banner: '药' },
  { sign: '丝绵老行', banner: '丝绵' }, { sign: '临河酒楼', banner: '酒楼' }, { sign: '翰墨书画', banner: '书画' },
  { sign: '协和米行', banner: '米' }, { sign: '香烛纸马', banner: '香烛' }, { sign: '杭白菊茶庄', banner: '白菊' },
  { sign: '木梳作坊', banner: '木梳' },
];
const WINE = { sign: '三白酒坊', banner: '酒' };
const SERIF = '"Songti SC", "STSong", "Noto Serif CJK SC", "Source Han Serif SC", serif';
const BRUSH = '"Kaiti SC", "STKaiti", "KaiTi", "LXGW WenKai", "Songti SC", "STSong", serif';

const anim = { lanterns: [], meshes: null, tassels: [], flag: null, levels: null };

// ---------------------------------------------------------------- 工具
function flipFaces(g) {
  const idx = g.index.array;
  for (let i = 0; i < idx.length; i += 3) { const t = idx[i + 1]; idx[i + 1] = idx[i + 2]; idx[i + 2] = t; }
  g.computeVertexNormals();
  return g;
}

function cylM(THREE, rt, rb, h, seg = 10, open = false) {
  const g = new THREE.CylinderGeometry(rt, rb, h, seg, 1, open);
  const uv = g.attributes.uv; const circ = Math.PI * (rt + rb);
  for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * circ, uv.getY(i) * h);
  return g;
}

function roofY(c, z) {
  const s = (c.z1 - z) / (c.z1 - c.z0);
  return c.roofHigh - (c.roofHigh - c.roofLow) * s - ROOF_SAG * Math.sin(Math.PI * s);
}
const underY = (c, z) => roofY(c, z) - UNDER;

// 柱位：等距排开；遇到河埠头，在埠头两侧各立一根边柱，缺口里不立柱
function postXs(c, steps) {
  const n = Math.max(1, Math.round((c.x1 - c.x0) / PITCH));
  const p = (c.x1 - c.x0 - 2 * INSET) / n;
  let xs = Array.from({ length: n + 1 }, (_, i) => c.x0 + INSET + i * p);
  for (const s of steps.filter((st) => st.x > c.x0 && st.x < c.x1)) {
    const half = s.width / 2 + 0.1;
    xs = [...xs.filter((x) => Math.abs(x - s.x) > half + STEP_KEEP), s.x - half, s.x + half];
  }
  return xs.sort((a, b) => a - b);
}

// 把 buildHouse 返回的组烘到世界坐标，按材质跨房屋合并（一排房子只剩每材质一个网格）
function mergeHouses(ctx, list) {
  const parts = [];
  for (const h of list) {
    const g = ctx.buildHouse(h, { materials: ctx.materials, rng: ctx.rng });
    g.updateMatrixWorld(true);
    for (const mesh of g.children) parts.push({ geom: mesh.geometry.applyMatrix4(mesh.matrixWorld), mat: mesh.material });
  }
  return ctx.geom.mergeByMaterial(parts);
}

// ---------------------------------------------------------------- 廊棚
function corridorRoof(ctx, c, add) {
  const { geom: G, materials: M } = ctx;
  const L = c.x1 - c.x0; const cx = (c.x0 + c.x1) / 2;
  const run = c.z1 - c.z0; const rise = c.roofHigh - c.roofLow;
  const opts = { width: L, run, rise, sag: ROOF_SAG };
  const at = { x: cx, y: c.roofHigh, z: c.z1, ry: Math.PI };
  add(G.tiledRoofSlope({ ...opts, detail: 'high' }), M.tile, at);
  add(flipFaces(G.tiledRoofSlope({ ...opts, detail: 'low', tileDepth: 0 })), M.wood, { ...at, y: c.roofHigh - UNDER });
  for (const p of G.eaveTiles(L, M)) add(p.geom, p.mat, { x: cx, y: c.roofLow, z: c.z0, ry: Math.PI });
  add(G.boxM(L, 0.16, 0.05), M.woodDark, { x: cx, y: c.roofLow - 0.06, z: c.z0 });         // 封檐板
  add(G.boxM(L, 0.1, 0.3), M.tileRidge, { x: cx, y: c.roofHigh + 0.02, z: c.z1 - 0.12 });   // 高边压脊
  const slope = Math.hypot(run, rise); const ang = -Math.atan2(rise, run);
  const zc = (c.z0 + c.z1) / 2; const yc = (c.roofHigh + c.roofLow) / 2;
  for (const x of [c.x0 + 0.02, c.x1 - 0.02]) {                                             // 博风板
    add(G.boxM(0.04, 0.2, slope), M.woodDark, { x, y: yc - 0.1, z: zc, rx: ang });
  }
  for (let x = c.x0 + 0.15; x < c.x1 - 0.1; x += 0.33) {                                    // 椽子
    add(G.boxM(0.05, 0.04, slope - 0.1), M.woodDark, { x, y: yc - UNDER - ROOF_SAG - 0.03, z: zc, rx: ang });
  }
}

function corridorFrame(ctx, c, xs, add, houseAt) {
  const { THREE, geom: G, materials: M } = ctx;
  const L = xs[xs.length - 1] - xs[0]; const cx = (xs[0] + xs[xs.length - 1]) / 2;
  const topW = underY(c, Z_WATER); const topS = underY(c, Z_SHOP); const topM = underY(c, Z_MID);
  const tieY = topW - 0.27;
  for (const x of xs) {
    for (const [z, top, foot] of [[Z_WATER, topW, Y_CURB], [Z_SHOP, topS, 0]]) {
      const b = foot + 0.14;
      add(cylM(THREE, 0.15, 0.17, 0.14, 8), M.embankment, { x, y: foot + 0.07, z });       // 柱础
      add(cylM(THREE, 0.085, 0.095, top - b), M.woodDark, { x, y: b + (top - b) / 2, z });
    }
    add(G.boxM(0.1, 0.16, Z_SHOP - Z_WATER), M.woodDark, { x, y: tieY, z: (Z_WATER + Z_SHOP) / 2 }); // 穿枋
    const sh = topM - 0.12 - (tieY + 0.08);
    add(G.boxM(0.08, sh, 0.08), M.woodDark, { x, y: tieY + 0.08 + sh / 2, z: Z_MID });           // 瓜柱
    if (houseAt(x)) add(G.boxM(0.08, 0.12, 0.56), M.woodDark, { x, y: topS - 0.1, z: Z_SHOP + 0.3 }); // 搭进店面
  }
  add(G.boxM(L + 0.2, 0.18, 0.12), M.woodDark, { x: cx, y: topW - 0.1, z: Z_WATER });   // 檐枋
  add(G.boxM(L + 0.2, 0.18, 0.12), M.woodDark, { x: cx, y: topS - 0.1, z: Z_SHOP });
  add(G.boxM(L + 0.2, 0.12, 0.12), M.woodDark, { x: cx, y: topM - 0.06, z: Z_MID });   // 中檩
  return topW - 0.19; // 挂落的上沿
}

// 挂落：檐枋下的木格花牙子，两端下垂成“脚”
function guaLuo(G, M, xa, xb, yTop, add) {
  const span = xb - xa; const mid = (xa + xb) / 2; const H = 0.3; const d = 0.035; const z = Z_WATER;
  const wd = M.woodDark;
  add(G.boxM(span, 0.035, d), wd, { x: mid, y: yTop - H, z });
  for (const [x, sx] of [[xa + 0.02, 1], [xb - 0.02, -1]]) {
    add(G.boxM(0.04, H + 0.14, d), wd, { x, y: yTop - (H + 0.14) / 2, z });
    add(G.boxM(0.36, 0.035, d), wd, { x: x + sx * 0.18, y: yTop - H - 0.14, z });
    add(G.boxM(0.03, 0.14, d * 0.8), wd, { x: x + sx * 0.34, y: yTop - H - 0.07, z });
    add(G.boxM(0.2, 0.02, d * 0.7), wd, { x: x + sx * 0.12, y: yTop - H - 0.07, z, rz: sx * 0.6 });
  }
  // 格心：三道横棂，竖向短棂逐层错开半格（步步锦）
  const bar = 0.018; const band = H / 3;
  for (let j = 1; j < 3; j++) add(G.boxM(span, bar, d * 0.7), wd, { x: mid, y: yTop - band * j, z });
  for (let j = 0; j < 3; j++) {
    for (let x = xa + 0.1 + (j % 2) * 0.09; x < xb - 0.08; x += 0.18) {
      add(G.boxM(bar, band, d * 0.7), wd, { x, y: yTop - band * (j + 0.5), z });
    }
  }
}

// 美人靠：坐板 + 槛板 + 向河面外弯的鹅颈靠背（靠背竖条用实例化，见 slatGeometry）
function meiRenKao(ctx, xa, xb, add, slatXs) {
  const { THREE, geom: G, materials: M } = ctx;
  const span = xb - xa; const mid = (xa + xb) / 2;
  add(G.boxM(span, 0.06, 0.42), M.wood, { x: mid, y: 0.45, z: Z_WATER + 0.1 });
  add(G.boxM(span, 0.36, 0.03), M.wood, { x: mid, y: 0.24, z: Z_WATER + 0.28 });
  add(G.boxM(span, 0.36, 0.03), M.wood, { x: mid, y: 0.24, z: Z_WATER - 0.08 });
  add(G.boxM(span, 0.05, 0.05), M.woodDark, { x: mid, y: 0.5, z: BACK_Z0 });
  add(cylM(THREE, 0.035, 0.035, span, 8), M.woodDark, { x: mid, y: 0.985, z: BACK_Z0 - BACK_LEAN, rz: Math.PI / 2 });
  for (let x = xa + 0.06; x <= xb - 0.05; x += 0.11) slatXs.push(x);
}

function slatGeometry(ctx) {
  const { geom: G } = ctx;
  const pts = Array.from({ length: 6 }, (_, i) => {
    const u = i / 5;
    return [0.48 + 0.48 * u, BACK_Z0 - BACK_LEAN * Math.sin((u * Math.PI) / 2)];
  });
  const segs = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const [y0, z0] = pts[i]; const [y1, z1] = pts[i + 1];
    const len = Math.hypot(y1 - y0, z1 - z0) + 0.01;
    segs.push(G.place(G.boxM(0.022, len, 0.032), { y: (y0 + y1) / 2, z: (z0 + z1) / 2, rx: Math.atan2(z1 - z0, y1 - y0) }));
  }
  return mergeIndexed(ctx.THREE, segs);
}

function mergeIndexed(THREE, list) {
  const pos = []; const nor = []; const uv = []; const col = []; const idx = []; let base = 0;
  const colored = list.every((g) => g.attributes.color);
  for (const g of list) {
    pos.push(...g.attributes.position.array); nor.push(...g.attributes.normal.array); uv.push(...g.attributes.uv.array);
    if (colored) col.push(...g.attributes.color.array);
    for (const i of g.index.array) idx.push(i + base);
    base += g.attributes.position.count;
  }
  const out = new THREE.BufferGeometry();
  out.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  out.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  out.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  if (colored) out.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  out.setIndex(idx);
  return out;
}

function buildCorridors(ctx, add, saHouses) {
  const { layout, geom: G, materials: M } = ctx;
  const steps = layout.waterSteps.filter((s) => s.bank === 'S');
  const houseAt = (x) => saHouses.some((h) => x > h.footprint.x0 + 0.1 && x < h.footprint.x1 - 0.1);
  const slatXs = []; const spots = []; const bays = [];
  for (const c of layout.corridors) {
    const xs = postXs(c, steps);
    corridorRoof(ctx, c, add);
    const yGua = corridorFrame(ctx, c, xs, add, houseAt);
    for (let i = 0; i < xs.length - 1; i++) {
      const xa = xs[i] + 0.09; const xb = xs[i + 1] - 0.09; const mid = (xs[i] + xs[i + 1]) / 2;
      guaLuo(G, M, xa, xb, yGua, add);
      const atStep = steps.some((s) => Math.abs(mid - s.x) < 0.01); // 埠头缺口那一间：美人靠断开
      if (!atStep) meiRenKao(ctx, xa, xb, add, slatXs);
      spots.push({ id: `${c.id}-${i}`, x: mid, y: underY(c, Z_LANTERN) - 0.01, z: Z_LANTERN });
      bays.push({ c, mid, xa: xs[i], xb: xs[i + 1] });
    }
  }
  return { slatXs, spots, bays };
}

// ---------------------------------------------------------------- 灯笼
function lanternGeometries(ctx) {
  const { THREE } = ctx;
  const body = new THREE.SphereGeometry(1, 28, 18);
  body.scale(LAN.rx, LAN.ry, LAN.rx).translate(0, LAN.yc, 0);

  const frame = [];
  frame.push(new THREE.TorusGeometry(0.016, 0.003, 6, 16));                                         // 挂钩环
  frame.push(new THREE.CylinderGeometry(0.004, 0.004, LAN.cord, 6).translate(0, -LAN.cord / 2, 0)); // 提绳
  frame.push(new THREE.CylinderGeometry(0.06, 0.108, LAN.cap, 20).translate(0, -LAN.cord - LAN.cap / 2, 0));
  frame.push(new THREE.CylinderGeometry(0.108, 0.07, LAN.cap, 20).translate(0, LAN.capBottom + LAN.cap / 2, 0));
  frame.push(new THREE.CylinderGeometry(0.02, 0.02, 0.012, 10).translate(0, -LAN.cord + 0.005, 0));
  for (let k = 0; k < 6; k++) {                                                                     // 竹骨（经线，透过灯纸只见细线）
    const rib = new THREE.TorusGeometry(1, 0.0013 / LAN.rx, 3, 40);
    rib.scale(LAN.rx + 0.001, LAN.ry + 0.001, LAN.rx + 0.001).rotateY((k / 6) * Math.PI).translate(0, LAN.yc, 0);
    frame.push(rib);
  }
  return { body, frame: mergeIndexed(THREE, frame) };
}

// 穗子：串珠 + 束腰（三道箍）+ 170 根上粗下细、微微散开的丝线。原点 = 挂点。
// 颜色写在顶点色里：丝线逐根深浅不一，根部偏暗；箍和串珠用对比色
const TASSEL_COLORS = {
  red: { silk: [0.62, 0.05, 0.035], trim: [0.85, 0.6, 0.16] },
  gold: { silk: [0.8, 0.55, 0.1], trim: [0.6, 0.06, 0.04] },
};

function tint(g, [r, gg, b], k = 1) {
  const n = g.attributes.position.count; const c = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) c.set([r * k, gg * k, b * k], i * 3);
  g.setAttribute('color', new g.attributes.position.constructor(c, 3));
  return g;
}

function tasselGeometry(ctx, kind) {
  const { THREE, rng } = ctx;
  const r = rng(`${ZONE}-tassel-${kind}`);
  const { silk, trim } = TASSEL_COLORS[kind];
  const list = [];
  list.push(tint(new THREE.CylinderGeometry(0.003, 0.003, 0.03, 6).translate(0, -0.015, 0), silk));
  list.push(tint(new THREE.SphereGeometry(0.017, 16, 12).translate(0, -0.047, 0), trim));
  list.push(tint(new THREE.SphereGeometry(0.009, 12, 8).translate(0, -0.071, 0), silk));
  list.push(tint(new THREE.CylinderGeometry(0.013, 0.017, 0.055, 20).translate(0, -0.108, 0), silk));
  for (const y of [-0.088, -0.108, -0.128]) {
    list.push(tint(new THREE.TorusGeometry(0.0158, 0.0021, 6, 24).rotateX(Math.PI / 2).translate(0, y, 0), trim));
  }
  const N = 170; const top = -0.125;
  for (let i = 0; i < N; i++) {
    const a = i * 2.39996 + r.range(-0.2, 0.2); const rr = 0.0145 * Math.sqrt((i + 0.5) / N);
    const len = r.range(0.235, 0.26); const spread = r.range(0.004, 0.014); const ph = r.range(0, 6.28);
    const lean = r.range(-0.003, 0.003);
    const g = new THREE.CylinderGeometry(0.0009, 0.0004, len, 3, 5, true).translate(0, -len / 2, 0);
    const p = g.attributes.position;
    for (let k = 0; k < p.count; k++) {
      const u = Math.max(0, -p.getY(k) / len);
      const out = rr + spread * Math.pow(u, 1.6);
      const wig = 0.0012 * Math.sin(u * 6 + ph) * u;
      p.setXYZ(k, p.getX(k) + Math.cos(a) * out + lean * u + wig, top + p.getY(k), p.getZ(k) + Math.sin(a) * out - wig);
    }
    g.computeVertexNormals();
    const shade = r.range(0.55, 1.2);
    tint(g, silk, shade);
    const c = g.attributes.color;
    for (let k = 0; k < c.count; k++) { // 根部被束腰压着、偏暗
      const u = Math.max(0, -(p.getY(k) - top) / len); const dark = 0.65 + 0.35 * Math.min(1, u * 4);
      c.setXYZ(k, c.getX(k) * dark, c.getY(k) * dark, c.getZ(k) * dark);
    }
    list.push(g);
  }
  return mergeIndexed(THREE, list);
}

// 自发光也乘顶点色（不然红穗金箍会被同一个发光色洗掉）
function tasselMaterial(THREE) {
  const m = new THREE.MeshStandardMaterial({ name: 'tassel', color: 0xffffff, vertexColors: true, roughness: 0.5, emissive: 0x9a3a1c });
  m.onBeforeCompile = (sh) => {
    sh.fragmentShader = sh.fragmentShader.replace('#include <emissivemap_fragment>',
      '#include <emissivemap_fragment>\n\ttotalEmissiveRadiance *= vColor.rgb;');
  };
  return m;
}

function buildLanterns(ctx, spots, group) {
  const { THREE, materials: M, rng } = ctx;
  const { body, frame } = lanternGeometries(ctx);
  const tasselMat = tasselMaterial(THREE);
  const kinds = spots.map((s) => (rng(`${ZONE}-lantern-${s.id}`).chance(0.72) ? 'red' : 'gold'));
  const inst = (g, mat, n) => {
    const m = new THREE.InstancedMesh(g, mat, n);
    m.castShadow = false; m.receiveShadow = false; m.frustumCulled = false;
    group.add(m);
    return m;
  };
  anim.meshes = {
    body: inst(body, M.lantern, spots.length),
    frame: inst(frame, M.lanternFrame, spots.length),
    red: inst(tasselGeometry(ctx, 'red'), tasselMat, kinds.filter((k) => k === 'red').length),
    gold: inst(tasselGeometry(ctx, 'gold'), tasselMat, kinds.filter((k) => k === 'gold').length),
  };
  anim.tassels = [tasselMat];
  const count = { red: 0, gold: 0 };
  anim.lanterns = spots.map((s, i) => {
    const r = rng(`${ZONE}-lantern-${s.id}`); r.next();
    return {
      ...s, kind: kinds[i], slot: count[kinds[i]]++,
      w: r.range(1.1, 1.7), p: r.range(0, 6.28), p2: r.range(0, 6.28), ax: r.range(0.025, 0.045), az: r.range(0.015, 0.03),
    };
  });
  anim.levels = ctx.layout.lighting;
  anim.paths = ctx.paths;
  anim.THREE = THREE;
}

function swing(l, t) {
  return [
    l.ax * Math.sin(l.w * t + l.p) + 0.35 * l.ax * Math.sin(2.13 * l.w * t + 1.7 * l.p),
    l.az * Math.sin(0.77 * l.w * t + l.p2),
  ];
}

function updateLanterns(t) {
  const THREE = anim.THREE;
  const m = new THREE.Matrix4(); const mt = new THREE.Matrix4(); const off = new THREE.Matrix4();
  const q = new THREE.Quaternion(); const e = new THREE.Euler(); const v = new THREE.Vector3(); const one = new THREE.Vector3(1, 1, 1);
  const { body, frame } = anim.meshes;
  anim.lanterns.forEach((l, i) => {
    const [ax, az] = swing(l, t);
    m.compose(v.set(l.x, l.y, l.z), q.setFromEuler(e.set(ax, 0, az)), one);
    body.setMatrixAt(i, m);
    frame.setMatrixAt(i, m);
    const [bx, bz] = swing(l, t - 0.3); // 穗子比灯体慢半拍、甩得更开
    off.compose(v.set(0, LAN.tassel, 0), q.setFromEuler(e.set(bx * 1.6 - ax, 0, bz * 1.6 - az)), one);
    mt.multiplyMatrices(m, off);
    anim.meshes[l.kind].setMatrixAt(l.slot, mt);
  });
  for (const k of ['body', 'frame', 'red', 'gold']) anim.meshes[k].instanceMatrix.needsUpdate = true;
  // 穗子被上方灯体照亮：亮度跟 lighting.js 的灯笼曲线一致（同一套 layout.lighting 参数）
  const { lerp, smoothstep, clamp01 } = anim.paths; const L = anim.levels;
  const level = lerp(L.lanternStart, L.lanternEnd, smoothstep(0, 0.9, clamp01(t / L.duration)));
  for (const mat of anim.tassels) mat.emissiveIntensity = 0.05 + 0.4 * level;
}

// ---------------------------------------------------------------- 招牌 / 招幌（共用一张 Canvas 图集）
const ATLAS = { w: 2048, h: 2048, sign: { w: 1024, h: 192 }, banner: { w: 128, h: 512, y: 1536 } };

function speckleCanvas(g, r, x, y, w, h, n, colors, aMax) {
  for (let i = 0; i < n; i++) {
    g.globalAlpha = r.range(0.03, aMax); g.fillStyle = r.pick(colors);
    const s = r.range(1, 3); g.fillRect(x + r.range(0, w), y + r.range(0, h), s, s);
  }
  g.globalAlpha = 1;
}

function drawSign(g, r, cell, text, style) {
  const { x, y, w, h } = cell;
  const pal = [
    { bg: '#1c130e', rim: '#b08a3e', ink: '#d9b45c', shadow: 'rgba(0,0,0,0.8)' },   // 黑漆金字
    { bg: '#5b3a25', rim: '#2a1a10', ink: '#1a0e08', shadow: 'rgba(200,160,110,0.35)' }, // 原木刻字
    { bg: '#6e1a12', rim: '#c59a45', ink: '#e8c46a', shadow: 'rgba(0,0,0,0.7)' },   // 朱漆金字
  ][style];
  g.fillStyle = pal.bg; g.fillRect(x, y, w, h);
  if (style === 1) {
    for (let k = 0; k < 40; k++) {
      g.strokeStyle = `rgba(30,18,10,${r.range(0.1, 0.3)})`; g.lineWidth = r.range(1, 3);
      const yy = y + r.range(0, h); g.beginPath(); g.moveTo(x, yy);
      for (let xx = 0; xx <= w; xx += 32) g.lineTo(x + xx, yy + Math.sin(xx * 0.01 + k) * 4);
      g.stroke();
    }
  }
  g.strokeStyle = pal.rim; g.lineWidth = 10; g.strokeRect(x + 14, y + 14, w - 28, h - 28);
  g.lineWidth = 3; g.strokeRect(x + 28, y + 28, w - 56, h - 56);
  const chars = [...text]; const n = chars.length;
  const size = Math.min(118, ((w - 150) / n) * 0.86);
  g.font = `900 ${size}px ${SERIF}`; g.textAlign = 'center'; g.textBaseline = 'middle';
  const step = (w - 150) / n;
  chars.forEach((ch, i) => {
    const cx = x + 75 + step * (i + 0.5); const cy = y + h / 2 + 4;
    g.fillStyle = pal.shadow; g.fillText(ch, cx + 3, cy + 3);
    g.fillStyle = pal.ink; g.fillText(ch, cx, cy);
  });
  speckleCanvas(g, r, x, y, w, h, 2500, ['#000000', '#8a7a60'], 0.25);
}

function drawBanner(g, r, cell, text, style) {
  const { x, y, w, h } = cell;
  const pal = [
    { bg: '#e2d6bb', hem: '#22406e', ink: '#1b1410' }, // 本白布墨字
    { bg: '#23406c', hem: '#14284a', ink: '#efe9da' }, // 靛蓝布白字
    { bg: '#9c2418', hem: '#5e130b', ink: '#f2dca0' }, // 红布黄字
  ][style];
  g.fillStyle = pal.bg; g.fillRect(x, y, w, h);
  g.fillStyle = pal.hem; g.fillRect(x, y, w, 30); g.fillRect(x, y + h - 22, w, 22);
  g.fillRect(x, y + 30, 6, h - 52); g.fillRect(x + w - 6, y + 30, 6, h - 52);
  const chars = [...text]; const n = chars.length;
  const size = Math.min(100, (h - 90) / n * 0.88);
  g.font = `900 ${size}px ${SERIF}`; g.textAlign = 'center'; g.textBaseline = 'middle';
  const step = (h - 90) / n;
  chars.forEach((ch, i) => { g.fillStyle = pal.ink; g.fillText(ch, x + w / 2, y + 48 + step * (i + 0.5)); });
  for (let k = 0; k < 12; k++) {                     // 布面竖向褶痕
    g.fillStyle = `rgba(0,0,0,${r.range(0.03, 0.09)})`; g.fillRect(x + r.range(8, w - 12), y + 30, r.range(2, 6), h - 52);
  }
  speckleCanvas(g, r, x, y, w, h, 900, ['#000000', '#ffffff'], 0.15);
}

function atlasUV(THREE, geomPlane, cell) {
  const uv = geomPlane.attributes.uv; const pad = 3;
  const u0 = (cell.x + pad) / ATLAS.w; const u1 = (cell.x + cell.w - pad) / ATLAS.w;
  const vt = 1 - (cell.y + pad) / ATLAS.h; const vb = 1 - (cell.y + cell.h - pad) / ATLAS.h;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, u0 + uv.getX(i) * (u1 - u0), vb + uv.getY(i) * (vt - vb));
  return geomPlane;
}

function buildShops(ctx, saHouses, bays, add, group) {
  const { THREE, rng, geom: G, materials: M } = ctx;
  const r = rng(`${ZONE}-shops`);
  const pool = [...SHOP_NAMES];
  for (let i = pool.length - 1; i > 0; i--) { const j = r.int(0, i); [pool[i], pool[j]] = [pool[j], pool[i]]; }
  const wineHouse = pickWineHouse(saHouses);
  const canvas = document.createElement('canvas'); canvas.width = ATLAS.w; canvas.height = ATLAS.h;
  const g2 = canvas.getContext('2d');
  const signParts = [];
  saHouses.forEach((h, i) => {
    const name = h === wineHouse ? WINE : pool.pop();
    const hr = rng(`${ZONE}-shop-${h.id}`);
    const sCell = { x: (i % 2) * ATLAS.sign.w, y: Math.floor(i / 2) * ATLAS.sign.h, ...ATLAS.sign };
    drawSign(g2, hr, sCell, name.sign, hr.int(0, 2));
    const z0 = h.footprint.z0;
    add(G.boxM(SIGN.w + 0.1, SIGN.h + 0.1, 0.05), M.woodDark, { x: h.x, y: SIGN.y, z: z0 - 0.03 });
    signParts.push({ geom: G.place(atlasUV(THREE, new THREE.PlaneGeometry(SIGN.w, SIGN.h), sCell), { x: h.x, y: SIGN.y, z: z0 - 0.058, ry: Math.PI }) });
    if (h !== wineHouse && !hr.chance(0.55)) return;
    const bay = nearestBay(bays, h.x - h.width * 0.22, h);
    if (!bay) return;
    const bCell = { x: i * ATLAS.banner.w, y: ATLAS.banner.y, ...ATLAS.banner };
    drawBanner(g2, hr, bCell, name.banner, hr.int(0, 2));
    bannerStand(ctx, bay.mid, add, signParts, bCell);
  });
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const mat = new THREE.MeshStandardMaterial({ name: 'shopSigns', map: tex, roughness: 0.7 });
  const mesh = new THREE.Mesh(mergeIndexed(THREE, signParts.map((p) => p.geom)), mat);
  mesh.receiveShadow = true;
  group.add(mesh);
  return wineHouse;
}

function nearestBay(bays, x, h) {
  let best = null;
  for (const b of bays) {
    if (b.mid < h.footprint.x0 + 0.6 || b.mid > h.footprint.x1 - 0.6) continue;
    if (!best || Math.abs(b.mid - x) < Math.abs(best.mid - x)) best = b;
  }
  return best;
}

// 落地招幌：两根细木杆 + 顶横杆，挂一条垂直于街面的布幌（两面各贴一张，正反都读得通）
function bannerStand(ctx, x, add, signParts, cell) {
  const { THREE, geom: G, materials: M } = ctx;
  const zc = BANNER.z; const hw = BANNER.w / 2 + 0.06; const top = 0.5 + BANNER.h + 0.12;
  for (const z of [zc - hw, zc + hw]) {
    add(G.boxM(0.045, top, 0.045), M.woodDark, { x, y: top / 2, z });
    add(G.boxM(0.36, 0.05, 0.07), M.woodDark, { x, y: 0.025, z });
  }
  add(G.boxM(0.05, 0.05, 2 * hw + 0.12), M.woodDark, { x, y: top - 0.03, z: zc });
  const y = 0.5 + BANNER.h / 2;
  for (const s of [1, -1]) {
    const p = atlasUV(THREE, new THREE.PlaneGeometry(BANNER.w, BANNER.h), cell);
    signParts.push({ geom: G.place(p, { x: x + s * 0.004, y, z: zc, ry: s * Math.PI / 2 }) });
  }
}

// 酒旗挂在 x≈-40~-60 之间的 SA 商铺前（取中心落在这一段里的第一栋）
function pickWineHouse(saHouses) {
  return saHouses.find((h) => h.x <= -45 && h.x >= -58) ?? saHouses.find((h) => h.x <= -40 && h.x >= -60);
}

// ---------------------------------------------------------------- 酒旗
function drawFlag(ctx) {
  const r = ctx.rng(`${ZONE}-flag-tex`);
  const W = 512; const H = 1280;
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const g = c.getContext('2d');
  g.clearRect(0, 0, W, H);
  const tooth = 34; const edge = 30; // 犬牙边：右侧（自由边）和底边
  g.fillStyle = '#e4d7b8';
  g.fillRect(0, 0, W - edge, H - edge);
  g.fillStyle = '#9a2216';
  g.beginPath(); g.moveTo(W - edge - 2, 120);
  for (let y = 120; y < H - edge; y += tooth) { g.lineTo(W, y + tooth / 2); g.lineTo(W - edge - 2, y + tooth); }
  g.closePath(); g.fill();
  g.beginPath(); g.moveTo(W - edge, H - edge - 2);
  for (let x = W - edge; x > 0; x -= tooth) { g.lineTo(x - tooth / 2, H); g.lineTo(x - tooth, H - edge - 2); }
  g.closePath(); g.fill();
  g.fillStyle = '#9a2216'; g.fillRect(W - edge - 16, 120, 16, H - edge - 120); g.fillRect(0, H - edge - 16, W - edge, 16);
  g.fillStyle = '#1f355c'; g.fillRect(0, 0, W, 120);                       // 顶部靛蓝旗头
  g.fillStyle = '#e8e0cc';
  for (let x = 30; x < W; x += 56) { g.beginPath(); g.arc(x, 60, 13, 0, Math.PI * 2); g.fill(); }
  g.fillStyle = '#1f355c';
  for (let x = 30; x < W; x += 56) { g.beginPath(); g.arc(x, 60, 6, 0, Math.PI * 2); g.fill(); }
  // 布纹 + 旧渍
  for (let i = 0; i < 26; i++) {
    const x = r.range(0, W); const y = r.range(120, H); const rad = r.range(30, 140);
    const gr = g.createRadialGradient(x, y, 0, x, y, rad);
    gr.addColorStop(0, `rgba(120,95,60,${r.range(0.04, 0.12)})`); gr.addColorStop(1, 'rgba(120,95,60,0)');
    g.fillStyle = gr; g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
  }
  g.globalCompositeOperation = 'source-atop';
  for (let y = 0; y < H; y += 3) { g.fillStyle = `rgba(60,40,20,${r.range(0.02, 0.06)})`; g.fillRect(0, y, W, 1); }
  for (let x = 0; x < W; x += 3) { g.fillStyle = `rgba(60,40,20,${r.range(0.01, 0.04)})`; g.fillRect(x, 0, 1, H); }
  // 墨字：三白酒（竖排，略有洇墨）
  const chars = ['三', '白', '酒']; const size = 330;
  g.font = `900 ${size}px ${BRUSH}`; g.textAlign = 'center'; g.textBaseline = 'middle';
  chars.forEach((ch, i) => {
    const cx = (W - edge) / 2; const cy = 120 + 70 + (i + 0.5) * 335;
    g.shadowColor = 'rgba(20,12,8,0.55)'; g.shadowBlur = 6;
    g.fillStyle = '#16100c'; g.fillText(ch, cx, cy);
  });
  g.shadowBlur = 0;
  g.fillStyle = '#a3241a'; g.fillRect(W - edge - 96, H - edge - 150, 58, 76);          // 朱印
  g.fillStyle = '#e4d7b8'; g.font = `900 30px ${SERIF}`;
  g.fillText('老', W - edge - 67, H - edge - 131); g.fillText('號', W - edge - 67, H - edge - 95);
  g.globalCompositeOperation = 'source-over';
  speckleCanvas(g, r, 0, 120, W - edge, H - 150, 3000, ['#5a4630', '#fff6e0'], 0.18);
  const tex = new ctx.THREE.CanvasTexture(c);
  tex.colorSpace = ctx.THREE.SRGBColorSpace; tex.anisotropy = 8;
  return tex;
}

function buildWineFlag(ctx, wineHouse, bays, add, group) {
  const { THREE, geom: G, materials: M } = ctx;
  // 竖杆贴着离铺子中心最近的靠水柱，立在驳岸沿上
  const posts = bays.filter((b) => b.c.x0 < wineHouse.x && b.c.x1 > wineHouse.x).flatMap((b) => [b.xa, b.xb]);
  const px = posts.reduce((a, b) => (Math.abs(b - wineHouse.x) < Math.abs(a - wineHouse.x) ? b : a));
  const pz = FLAG.z;
  add(cylM(THREE, FLAG.poleR * 0.8, FLAG.poleR, FLAG.poleH, 10), M.woodDark, { x: px, y: Y_COPING + FLAG.poleH / 2, z: pz });
  add(cylM(THREE, 0.06, 0.06, 0.03, 10), M.lanternFrame, { x: px, y: Y_COPING + FLAG.poleH + 0.015, z: pz });
  for (const y of [1.0, 2.2]) add(G.boxM(0.03, 0.04, Z_WATER - pz), M.lanternFrame, { x: px, y, z: (pz + Z_WATER) / 2 }); // 铁箍
  add(cylM(THREE, 0.022, 0.03, FLAG.armLen, 8), M.woodDark, { x: px - FLAG.armLen / 2, y: FLAG.armY, z: pz, rz: Math.PI / 2 });
  const sx = FLAG.armLen - 0.05; const sy = FLAG.poleH - 0.06 - FLAG.armY; // 拉索：杆顶 → 挑杆端
  add(cylM(THREE, 0.006, 0.006, Math.hypot(sx, sy), 5), M.lanternFrame,
    { x: px - sx / 2, y: FLAG.armY + sy / 2, z: pz, rz: Math.atan2(sx, sy) });
  for (let x = px - 0.1; x > px - FLAG.w - 0.05; x -= 0.16) {
    add(new THREE.TorusGeometry(0.03, 0.004, 4, 12), M.lanternFrame, { x, y: FLAG.armY - 0.01, z: pz });
  }
  const geom = new THREE.PlaneGeometry(FLAG.w, FLAG.h, 28, 64);
  geom.rotateY(Math.PI).translate(-FLAG.w / 2, -FLAG.h / 2, 0); // 正面朝河（-Z），x∈[-W,0]，旗杆在 x=0
  const mat = new THREE.MeshStandardMaterial({ name: 'wineFlag', map: drawFlag(ctx), roughness: 0.92, side: THREE.DoubleSide, alphaTest: 0.5 });
  const mesh = new THREE.Mesh(geom, mat);
  mesh.position.set(px - FLAG.poleR - 0.01, FLAG.armY - 0.035, pz);
  mesh.frustumCulled = false;
  group.add(mesh);
  anim.flag = { geom, base: Float32Array.from(geom.attributes.position.array) };
  return { x: mesh.position.x - FLAG.w / 2, y: mesh.position.y - FLAG.h / 2, z: pz, pole: [px, pz] };
}

function updateFlag(t) {
  const { geom, base } = anim.flag;
  const p = geom.attributes.position.array;
  const W = FLAG.w; const H = FLAG.h; const TAU = Math.PI * 2;
  const gust = 0.75 + 0.25 * Math.sin(0.37 * t) * Math.sin(0.11 * t + 1.0);
  for (let i = 0; i < p.length; i += 3) {
    const x0 = base[i]; const y0 = base[i + 1];
    const u = Math.max(0, -x0 / W); const v = Math.max(0, -y0 / H); // u：离旗杆的距离，v：离顶边的距离
    const amp = 0.095 * Math.pow(u, 1.1) * (0.35 + 0.65 * v) * gust;
    const wave = Math.sin(TAU * (u * W / 0.85) - 3.1 * t + 1.6 * v) + 0.4 * Math.sin(TAU * (u * W / 0.38) - 5.3 * t + 2.9 * v + 0.8);
    // 静态褶皱：顶边吊环之间的小皱 + 布面几道斜向长褶
    const folds = 0.016 * Math.sin((u * W * TAU) / 0.16) * (1 - v) ** 4
      + 0.022 * Math.sin(TAU * (u * W / 0.42 + v * H / 1.6) + 0.6) * Math.min(1, u * 3) * (0.5 + 0.5 * v);
    const swing = 0.05 * v * v * Math.sin(0.9 * t + 0.4) * gust; // 下角被风带着前后甩
    p[i] = x0 * (1 - 0.03 * gust * u * v) + swing * u;
    p[i + 2] = amp * wave + folds - 0.05 * u * v * gust;
  }
  geom.attributes.position.needsUpdate = true;
  geom.computeVertexNormals();
}

// ---------------------------------------------------------------- 入口
export async function build(ctx) {
  const { THREE, layout, geom: G } = ctx;
  try { await document.fonts.load(`900 64px ${SERIF}`, '酒'); await document.fonts.load(`900 64px ${BRUSH}`, '酒'); } catch { /* 系统字体可直接用 */ }
  const group = new THREE.Group();
  const south = layout.houses.filter((h) => h.zone === 'south');
  for (const row of ['SA', 'SB', 'SW', 'SC']) {
    const g = mergeHouses(ctx, south.filter((h) => h.row === row));
    g.name = `houses-${row}`;
    group.add(g);
  }
  const saHouses = south.filter((h) => h.row === 'SA');

  const parts = [];
  const add = (geom, mat, t) => parts.push({ geom: G.place(geom, t), mat });
  const { slatXs, spots, bays } = buildCorridors(ctx, add, saHouses);
  const wineHouse = buildShops(ctx, saHouses, bays, add, group);
  const flagAt = buildWineFlag(ctx, wineHouse, bays, add, group);
  const corridor = G.mergeByMaterial(parts);
  corridor.name = 'corridors';
  group.add(corridor);

  const slats = new THREE.InstancedMesh(slatGeometry(ctx), ctx.materials.woodDark, slatXs.length);
  const m = new THREE.Matrix4();
  slatXs.forEach((x, i) => slats.setMatrixAt(i, m.makeTranslation(x, 0, 0)));
  slats.receiveShadow = true;
  group.add(slats);

  buildLanterns(ctx, spots, group);
  update(0);
  group.userData.wineFlag = { ...flagAt, house: wineHouse.id };
  return group;
}

export function update(t) {
  if (anim.meshes) updateLanterns(t);
  if (anim.flag) updateFlag(t);
}
