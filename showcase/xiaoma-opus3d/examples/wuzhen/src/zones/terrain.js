// 地形区块：河道以外的地面铺装、条石驳岸（墙 + 压顶石 + 路沿）、河床、河埠头。
// 不做水面。所有尺寸从 layout 推导；随机数一律 rng('terrain-…')。
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const COPING = { land: 0.4, over: 0.1, thick: 0.25, top: 0.02, jitter: 0.004 }; // 压顶石
const CURB = { width: 0.4, thick: 0.25, top: 0.04 };                           // 南岸石板街路沿
const STEP = { count: 6, bottom: -1.7, chamfer: 0.02, seg: 0.05, joint: 0.005 };             // 河埠头石阶
const WALL_COL = 0.5;                                                          // 驳岸墙顶点列距
const WALL_ROWS = [0, -0.3, -0.55, -0.68, -0.75, -0.82, -0.88, -0.94, -1.0, -1.1, -1.2, -1.3, -1.42, -1.6, -2.0, -2.6, -3.2];
const GRID_HALF = 150;  // 精细铺装网格范围（正方形半边长）
const EARTH_R = 460;    // 远景屋顶范围外缘，再往外是田野
const FIELD_R = 1200;
const RING_SEG = 96;
const EPS = 1e-6;

// ---------- 小工具 ----------
const inRect = (r, x, z) => x > r.x0 && x < r.x1 && z > r.z0 && z < r.z1;
const inAny = (rs, x, z) => rs.some((r) => inRect(r, x, z));
const clamp01 = (v) => Math.min(1, Math.max(0, v));
// 允许 e0 > e1（值越往下越大）
const smooth = (e0, e1, x) => { const k = clamp01((x - e0) / (e1 - e0)); return k * k * (3 - 2 * k); };

function bridgeRect(b) {
  const half = b.width / 2;
  return b.axis === 'z'
    ? { x0: b.at - half, x1: b.at + half, z0: Math.min(b.from, b.to), z1: Math.max(b.from, b.to) }
    : { x0: Math.min(b.from, b.to), x1: Math.max(b.from, b.to), z0: b.at - half, z1: b.at + half };
}

// 区间 [a0,a1] 减去若干区间
function subtract([a0, a1], gaps) {
  let out = [[a0, a1]];
  for (const [g0, g1] of gaps) {
    out = out.flatMap(([s0, s1]) => (g1 <= s0 || g0 >= s1 ? [[s0, s1]]
      : [[s0, g0], [g1, s1]].filter(([p, q]) => q - p > EPS)));
  }
  return out;
}

// 确定性值噪声（种子表来自 rng）
function makeNoise(rng) {
  const r = rng('terrain-noise');
  const T = Array.from({ length: 256 }, () => r.next());
  const P = Array.from({ length: 256 }, (_, i) => i);
  for (let i = 255; i > 0; i--) { const j = r.int(0, i); [P[i], P[j]] = [P[j], P[i]]; }
  const h = (i, j) => T[P[(P[i & 255] + j) & 255]];
  return (x, y) => {
    const xi = Math.floor(x); const yi = Math.floor(y);
    const fx = x - xi; const fy = y - yi;
    const sx = fx * fx * (3 - 2 * fx); const sy = fy * fy * (3 - 2 * fy);
    const a = h(xi, yi) + (h(xi + 1, yi) - h(xi, yi)) * sx;
    const b = h(xi, yi + 1) + (h(xi + 1, yi + 1) - h(xi, yi + 1)) * sx;
    return a + (b - a) * sy;
  };
}

// ---------- 程序化纹理 ----------
function canvasTex(THREE, size, draw, color) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  draw(c.getContext('2d'), size);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.colorSpace = color ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  t.anisotropy = 8;
  return t;
}

// 可平铺的斑块（每个斑块在四周重复画，保证无缝）
function wrapBlot(ctx, s, x, y, rad, inner, outer) {
  for (const dx of [-s, 0, s]) for (const dy of [-s, 0, s]) {
    const g = ctx.createRadialGradient(x + dx, y + dy, 0, x + dx, y + dy, rad);
    g.addColorStop(0, inner); g.addColorStop(1, outer);
    ctx.fillStyle = g;
    ctx.fillRect(x + dx - rad, y + dy - rad, rad * 2, rad * 2);
  }
}

// 青石（河埠头、压顶石、路沿）：青灰底、矿物颗粒、斧剁纹。覆盖 1m × 1m
function drawGranite(r) {
  return (ctx, s) => {
    ctx.fillStyle = '#80847f';
    ctx.fillRect(0, 0, s, s);
    for (let i = 0; i < 40; i++) {
      const v = r.range(-1, 1) > 0 ? '150,152,146' : '70,74,74';
      wrapBlot(ctx, s, r.range(0, s), r.range(0, s), r.range(40, 200), `rgba(${v},0.12)`, `rgba(${v},0)`);
    }
    for (let i = 0; i < 420; i++) { // 斧剁纹：细密平行斜线
      ctx.strokeStyle = `rgba(${r.chance(0.5) ? '40,42,42' : '170,172,166'},${r.range(0.04, 0.12)})`;
      ctx.lineWidth = r.range(0.6, 1.6);
      const x = r.range(-s * 0.2, s); const y = r.range(0, s); const len = r.range(20, 80);
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + len * 0.35, y + len); ctx.stroke();
    }
    for (let i = 0; i < 26000; i++) {
      ctx.globalAlpha = r.range(0.05, 0.4);
      ctx.fillStyle = r.pick(['#4a4e4e', '#9a9d97', '#5d625f', '#b8b9b2', '#3b3e3e']);
      const d = r.range(1, 2.6);
      ctx.fillRect(r.range(0, s), r.range(0, s), d, d);
    }
    ctx.globalAlpha = 1;
  };
}

// 青苔噪声：灰度斑块，覆盖 1m × 1m
function drawMossNoise(r) {
  return (ctx, s) => {
    ctx.fillStyle = '#808080';
    ctx.fillRect(0, 0, s, s);
    for (let i = 0; i < 260; i++) {
      const v = r.chance(0.5) ? 255 : 0;
      wrapBlot(ctx, s, r.range(0, s), r.range(0, s), r.range(6, 60), `rgba(${v},${v},${v},${r.range(0.15, 0.4)})`, `rgba(${v},${v},${v},0)`);
    }
    for (let i = 0; i < 9000; i++) { // 细碎颗粒，让青苔边缘碎而不糊
      const v = r.chance(0.5) ? 255 : 0;
      ctx.globalAlpha = r.range(0.1, 0.35);
      ctx.fillStyle = `rgb(${v},${v},${v})`;
      ctx.beginPath(); ctx.arc(r.range(0, s), r.range(0, s), r.range(0.8, 3), 0, Math.PI * 2); ctx.fill();
    }
    ctx.globalAlpha = 1;
  };
}

// 湿石材质：顶点属性 aWet（0 干 ~ 1 湿：变暗、变光滑）和 aMoss（青苔量，用噪声纹理切出斑块）
function wetStoneMaterial(THREE, base, name, mossNoise, { wetDark, wetRough }) {
  const m = base.clone();
  m.name = name;
  const mossColor = new THREE.Color(0x56692e);
  m.onBeforeCompile = (sh) => {
    sh.uniforms.mossNoise = { value: mossNoise };
    sh.uniforms.mossColor = { value: mossColor };
    sh.vertexShader = 'attribute float aWet;\nattribute float aMoss;\nvarying float vWet;\nvarying float vMoss;\nvarying vec2 vUvM;\n'
      + sh.vertexShader.replace('#include <uv_vertex>', '#include <uv_vertex>\nvWet = aWet; vMoss = aMoss; vUvM = uv;');
    sh.fragmentShader = 'uniform sampler2D mossNoise;\nuniform vec3 mossColor;\nvarying float vWet;\nvarying float vMoss;\nvarying vec2 vUvM;\nfloat mossMask = 0.0;\n'
      + sh.fragmentShader
        .replace('#include <map_fragment>', `#include <map_fragment>
  float mN = texture2D(mossNoise, vUvM * 0.8).r * 0.65 + texture2D(mossNoise, vUvM * 3.1 + 0.37).r * 0.35;
  mossMask = smoothstep(1.02 - vMoss, 1.07 - vMoss, mN);
  diffuseColor.rgb *= mix(1.0, ${wetDark.toFixed(3)}, vWet);
  diffuseColor.rgb = mix(diffuseColor.rgb, mossColor * (0.6 + 0.7 * mN) * mix(1.0, 0.75, vWet), mossMask);`)
        .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
  roughnessFactor = mix(roughnessFactor, ${wetRough.toFixed(3)} + 0.22 * mN, vWet * (1.0 - 0.45 * mossMask));`);
  };
  m.customProgramCacheKey = () => `terrain-${name}`;
  return m;
}

// 给非索引几何加 aWet / aMoss（按世界坐标顶点逐个计算）
function addWetAttrs(THREE, g, fn) {
  const p = g.attributes.position; const n = p.count;
  const wet = new Float32Array(n); const moss = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const [w, ms] = fn(p.getX(i), p.getY(i), p.getZ(i), i);
    wet[i] = clamp01(w); moss[i] = clamp01(ms);
  }
  g.setAttribute('aWet', new THREE.BufferAttribute(wet, 1));
  g.setAttribute('aMoss', new THREE.BufferAttribute(moss, 1));
  return g;
}

// ---------- 驳岸布局：墙线、压顶石、路沿 ----------
// 主河 M（东西向）与支河 B（南北向）十字相交
function bankPlan(layout) {
  const M = layout.rivers.find((r) => r.id === 'main').rect;
  const B = layout.rivers.find((r) => r.id === 'branch').rect;
  const { land: c, over: o } = COPING;
  const bRects = layout.bridges.map(bridgeRect);
  // 跨过某条岸线的桥，在压顶石上开口（桥台自己落地，避免压顶石穿进桥台）
  const gapsAlongX = (z) => bRects.filter((r) => r.z0 < z && r.z1 > z).map((r) => [r.x0, r.x1]);
  const gapsAlongZ = (x) => bRects.filter((r) => r.x0 < x && r.x1 > x).map((r) => [r.z0, r.z1]);

  const walls = [];  // { axis, fixed, a0, a1, dir }：dir = 水在 fixed 的哪一侧（±1）
  const copings = []; // { x0,x1,z0,z1, axis }
  const xSegs = [[M.x0, B.x0], [B.x1, M.x1]];
  const zSegs = [[B.z0, M.z0], [M.z1, B.z1]];
  for (const [z, dir] of [[M.z1, -1], [M.z0, 1]]) {
    for (const s of xSegs) walls.push({ axis: 'x', fixed: z, a0: s[0], a1: s[1], dir });
    const zr = dir < 0 ? [z - o, z + c] : [z - c, z + o];
    // 西段让出端墙压顶、盖住十字口转角；东段反之
    for (const seg of [[M.x0 + o, B.x0 + o], [B.x1 - o, M.x1 - o]]) {
      for (const [x0, x1] of subtract(seg, gapsAlongX(z))) copings.push({ x0, x1, z0: zr[0], z1: zr[1], axis: 'x' });
    }
  }
  for (const [x, dir] of [[B.x0, 1], [B.x1, -1]]) {
    for (const s of zSegs) walls.push({ axis: 'z', fixed: x, a0: s[0], a1: s[1], dir });
    const xr = dir < 0 ? [x - o, x + c] : [x - c, x + o];
    for (const seg of [[B.z0 + o, M.z0 - c], [M.z1 + c, B.z1 - o]]) {
      for (const [z0, z1] of subtract(seg, gapsAlongZ(x))) copings.push({ x0: xr[0], x1: xr[1], z0, z1, axis: 'z' });
    }
  }
  // 河道尽头的端墙（主河东西两端、支河南北两端）
  for (const [x, dir] of [[M.x0, 1], [M.x1, -1]]) {
    walls.push({ axis: 'z', fixed: x, a0: M.z0, a1: M.z1, dir });
    const xr = dir < 0 ? [x - o, x + c] : [x - c, x + o];
    copings.push({ x0: xr[0], x1: xr[1], z0: M.z0 - c, z1: M.z1 + c, axis: 'z' });
  }
  for (const [z, dir] of [[B.z0, 1], [B.z1, -1]]) {
    walls.push({ axis: 'x', fixed: z, a0: B.x0, a1: B.x1, dir });
    const zr = dir < 0 ? [z - o, z + c] : [z - c, z + o];
    copings.push({ x0: B.x0 - c, x1: B.x1 + c, z0: zr[0], z1: zr[1], axis: 'x' });
  }
  // 南岸沿河石板街靠水一侧的条石路沿（让开支河口和桥）
  const S = layout.streets.find((s) => s.id === 'south-street').rect;
  const cz = [S.z0 + c, S.z0 + c + CURB.width];
  const curbGaps = [[B.x0 - c, B.x1 + c], ...bRects.filter((r) => r.z0 < cz[1] && r.z1 > cz[0]).map((r) => [r.x0, r.x1])];
  const curbs = subtract([S.x0, S.x1], curbGaps).map(([x0, x1]) => ({ x0, x1, z0: cz[0], z1: cz[1], axis: 'x' }));
  return { M, B, walls, copings, curbs };
}

// ---------- 地面 ----------
function quadsGeometry(THREE, rects, y) {
  const pos = []; const uv = []; const nor = []; const idx = [];
  for (const r of rects) {
    const k = pos.length / 3;
    for (const [x, z] of [[r.x0, r.z0], [r.x1, r.z0], [r.x1, r.z1], [r.x0, r.z1]]) {
      pos.push(x, y, z); nor.push(0, 1, 0); uv.push(x, -z);
    }
    idx.push(k, k + 2, k + 1, k, k + 3, k + 2);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  return g;
}

// 用所有矩形的边切成网格，逐格判定铺装，同一行相邻同材质的格子合并
function groundRects(layout, plan) {
  const { EXTENT, streets, dyeYard, backdrop } = layout;
  const waters = [plan.M, plan.B];
  const voids = [...plan.copings, ...plan.curbs];
  const all = [...waters, ...voids, ...streets.map((s) => s.rect), dyeYard.rect, ...backdrop.fillRects, EXTENT];
  const cut = (keys) => [...new Set([-GRID_HALF, GRID_HALF, ...all.flatMap((r) => keys.map((k) => r[k]))]
    .map((v) => Math.round(v * 1e4) / 1e4).filter((v) => v >= -GRID_HALF && v <= GRID_HALF))].sort((a, b) => a - b);
  const xs = cut(['x0', 'x1']); const zs = cut(['z0', 'z1']);
  const earthy = [dyeYard.rect, ...backdrop.fillRects];
  const kind = (x, z) => {
    if (inAny(waters, x, z) || inAny(voids, x, z)) return null;
    if (!inRect(EXTENT, x, z) || inAny(earthy, x, z)) return 'earth';
    return 'slab';
  };
  const out = { slab: [], earth: [] };
  for (let j = 0; j < zs.length - 1; j++) {
    const z0 = zs[j]; const z1 = zs[j + 1]; const zc = (z0 + z1) / 2;
    let run = null;
    for (let i = 0; i < xs.length - 1; i++) {
      const k = kind((xs[i] + xs[i + 1]) / 2, zc);
      if (run && run.k === k) { run.x1 = xs[i + 1]; continue; }
      if (run?.k) out[run.k].push(run);
      run = { k, x0: xs[i], x1: xs[i + 1], z0, z1 };
    }
    if (run?.k) out[run.k].push(run);
  }
  return out;
}

// 圆形多边形（顺序一致，田野内圈和泥地外圈共用顶点，避免 T 形接缝）
const ring = (THREE, R) => Array.from({ length: RING_SEG }, (_, i) => {
  const a = (i / RING_SEG) * Math.PI * 2;
  return new THREE.Vector2(Math.cos(a) * R, Math.sin(a) * R);
});

function flatShape(THREE, shape) {
  const g = new THREE.ShapeGeometry(shape);
  g.rotateX(-Math.PI / 2);
  return g;
}

function buildGround(ctx, plan) {
  const { THREE, layout, materials: M } = ctx;
  const rects = groundRects(layout, plan);
  // 区块外泥地：中心挖掉网格范围（向内多挖 2m 与网格边缘同材质重叠，避免接缝）
  const earthShape = new THREE.Shape(ring(THREE, EARTH_R));
  const h = GRID_HALF - 2;
  earthShape.holes.push(new THREE.Path([[-h, -h], [h, -h], [h, h], [-h, h]].map(([x, y]) => new THREE.Vector2(x, y))));
  const fieldShape = new THREE.Shape(ring(THREE, FIELD_R));
  fieldShape.holes.push(new THREE.Path(ring(THREE, EARTH_R)));
  const earth = mergeGeometries([quadsGeometry(THREE, rects.earth, 0), flatShape(THREE, earthShape)]);
  const meshes = [
    new THREE.Mesh(quadsGeometry(THREE, rects.slab, 0), M.stoneSlab),
    new THREE.Mesh(earth, M.earth),
    new THREE.Mesh(flatShape(THREE, fieldShape), M.field),
  ];
  for (const m of meshes) m.receiveShadow = true;
  return meshes;
}

// ---------- 河床 ----------
function buildBed(ctx, plan) {
  const { THREE, layout } = ctx;
  const { M, B } = plan;
  const rects = [M, { ...B, z1: M.z0 }, { ...B, z0: M.z1 }];
  const mud = new THREE.MeshStandardMaterial({ name: 'terrain-mud', color: 0x2a2820, roughness: 1 });
  const mesh = new THREE.Mesh(quadsGeometry(THREE, rects, layout.LEVELS.bed), mud);
  mesh.receiveShadow = true;
  return mesh;
}

// ---------- 驳岸墙 ----------
function wallGeometry(THREE, w, noise, seed) {
  const cols = Math.max(1, Math.ceil((w.a1 - w.a0) / WALL_COL));
  const pos = []; const uv = []; const nor = []; const idx = [];
  const n = w.axis === 'x' ? [0, 0, w.dir] : [w.dir, 0, 0];
  for (let i = 0; i <= cols; i++) {
    const a = w.a0 + ((w.a1 - w.a0) * i) / cols;
    for (const y of WALL_ROWS) {
      pos.push(...(w.axis === 'x' ? [a, y, w.fixed] : [w.fixed, y, a]));
      nor.push(...n); uv.push(a, y);
    }
  }
  const R = WALL_ROWS.length;
  // 默认三角形法线 = (+a) × (−y)；与朝水方向不一致时翻转绕序
  const flip = (w.axis === 'x' ? -1 : 1) * w.dir < 0;
  for (let i = 0; i < cols; i++) for (let j = 0; j < R - 1; j++) {
    const p = i * R + j; const q = p + R;
    if (flip) idx.push(p, p + 1, q, q, p + 1, q + 1); else idx.push(p, q, p + 1, q, q + 1, p + 1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  return addWetAttrs(THREE, g, (x, y, z) => {
    const a = w.axis === 'x' ? x : z;
    const line = 0.24 * (noise(a * 0.5, seed) - 0.5);             // 水渍线上沿起伏
    const streak = Math.max(0, noise(a * 1.7, seed + 5) - 0.6) * 2.2; // 压顶石下的雨水垂痕
    const wet = Math.max(smooth(-0.76 + line, -0.9 + line, y), streak * smooth(-0.05, -0.8, y) * 0.5);
    const band = Math.exp(-(((y + 1.12 - line) / 0.2) ** 2)) * (0.45 + 0.55 * noise(a * 0.9, seed + 11));
    const under = smooth(-1.35, -1.7, y) * 0.55;
    const dry = 0.15 * noise(a * 2.3, seed + 23) * smooth(-0.2, -0.6, y);
    return [wet, Math.max(band, under, dry)];
  });
}

// ---------- 条石（压顶石、路沿）：沿走向切成 1~1.8m 一块，顶面高差几毫米 ----------
function stoneRun(THREE, geom, r, rect, { thick, top, jitter }, mossAt) {
  const along = rect.axis === 'x' ? [rect.x0, rect.x1] : [rect.z0, rect.z1];
  const across = rect.axis === 'x' ? rect.z1 - rect.z0 : rect.x1 - rect.x0;
  const out = [];
  let a = along[0];
  while (along[1] - a > EPS) {
    let len = r.range(1.0, 1.8);
    if (along[1] - (a + len) < 0.5) len = along[1] - a;
    const t = top + r.range(-jitter, jitter);
    const g = rect.axis === 'x' ? geom.boxM(len, thick, across) : geom.boxM(across, thick, len);
    const uv = g.attributes.uv; const du = r.range(0, 1); const dv = r.range(0, 1);
    for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) + du, uv.getY(i) + dv);
    const c = a + len / 2; const m = (rect.axis === 'x' ? rect.z0 + rect.z1 : rect.x0 + rect.x1) / 2;
    geom.place(g, rect.axis === 'x' ? { x: c, y: t - thick / 2, z: m } : { x: m, y: t - thick / 2, z: c });
    out.push(addWetAttrs(THREE, g.toNonIndexed(), (x, y, z) => [0, mossAt(x, y, z)]));
    a += len;
  }
  return out;
}

// ---------- 河埠头 ----------
// 朝水方向 d、沿岸方向 e = d × up，原点在岸线上 e 方向的起点
const BANKS = {
  S: (s) => ({ d: [0, 0, -1], o: [s.rect.x0, s.rect.z1] }),
  N: (s) => ({ d: [0, 0, 1], o: [s.rect.x1, s.rect.z0] }),
  BW: (s) => ({ d: [1, 0, 0], o: [s.rect.x0, s.rect.z0] }),
  BE: (s) => ({ d: [-1, 0, 0], o: [s.rect.x1, s.rect.z1] }),
};

// 一级踏步的剖面（u=离岸距离, v=高度）：从岸墙到踏步前沿 u1，前沿上角倒角。
// 只在露出来的踢面和踏面（u0~u1）加密顶点给湿度/青苔用；压在上一级下面的部分和水下深处不加密
function stepProfile(THREE, u0, u1, vTop, vBot) {
  const c = STEP.chamfer;
  const pts = [[0, vBot], [u1, vBot]];
  const line = (x1, y1) => {
    const [x0, y0] = pts[pts.length - 1];
    const k = Math.max(1, Math.round(Math.hypot(x1 - x0, y1 - y0) / STEP.seg));
    for (let i = 1; i <= k; i++) pts.push([x0 + ((x1 - x0) * i) / k, y0 + ((y1 - y0) * i) / k]);
  };
  if (vBot < -1.8) pts.push([u1, -1.8]);
  line(u1, vTop - c); line(u1 - c, vTop); line(u0, vTop);
  pts.push([0, vTop]); // 由闭合边贴着岸墙回到起点
  return new THREE.Shape(pts.map(([x, y]) => new THREE.Vector2(x, y)));
}

// 河埠头：每级踏步由 1~3 块条石拼成，块端倒角形成 V 形石缝（不留真缝，免得透出下一级的反光），上下级错缝；顶面高差几毫米
function buildWaterStep(ctx, s, noise) {
  const { THREE, layout } = ctx;
  const n = STEP.count; const t = s.depth / n; const rise = -STEP.bottom / n;
  const top = (i) => -(i + 1) * rise;
  const nosings = Array.from({ length: n }, (_, i) => [(i + 1) * t, top(i)]);
  const inners = Array.from({ length: n }, (_, i) => [i * t, top(i)]);
  const seed = s.id.charCodeAt(2) * 13.7;
  const r = ctx.rng(`terrain-${s.id}`);
  const near = (list, x, y) => Math.min(...list.map(([px, py]) => Math.hypot(x - px, y - py)));
  // 在局部坐标 (u, v, w=沿岸) 里算湿度和青苔：前沿、阴角、两侧边缘长苔，越靠近水面越多
  const attrs = (u, v, w) => {
    const dw = Math.min(w, s.width - w);
    const edge = Math.max(Math.exp(-near(nosings, u, v) / 0.05), 0.85 * Math.exp(-near(inners, u, v) / 0.05),
      0.7 * Math.exp(-dw / 0.06));
    const hf = smooth(-0.3, -1.0, v);
    const moss = edge * (0.2 + 0.8 * hf) * (0.5 + 0.65 * noise(w * 5 + seed, u * 3 + v * 5)) + 0.55 * smooth(-1.25, -1.6, v);
    return [smooth(-0.5, -1.0, v), moss];
  };
  const parts = [];
  for (let i = 0; i < n; i++) {
    const vTop = top(i) + r.range(-0.004, 0.004);
    const shape = stepProfile(THREE, i * t, (i + 1) * t, vTop, i === n - 1 ? layout.LEVELS.bed : top(i + 1));
    for (const [w0, w1] of splitWidth(r, s.width)) {
      const b = STEP.joint;
      const g = new THREE.ExtrudeGeometry(shape, { depth: w1 - w0 - 2 * b, steps: Math.ceil((w1 - w0) / 0.1),
        bevelEnabled: true, bevelThickness: b, bevelSize: b, bevelOffset: -b, bevelSegments: 1 });
      g.translate(0, 0, w0 + b);
      const uv = g.attributes.uv; const du = r.range(0, 1); const dv = r.range(0, 1);
      for (let k = 0; k < uv.count; k++) uv.setXY(k, uv.getX(k) + du, uv.getY(k) + dv);
      parts.push(addWetAttrs(THREE, g, attrs));
    }
  }
  const g = mergeGeometries(parts);
  const { d, o } = BANKS[s.bank](s);
  const D = new THREE.Vector3(...d); const up = new THREE.Vector3(0, 1, 0);
  const E = new THREE.Vector3().crossVectors(D, up);
  g.applyMatrix4(new THREE.Matrix4().makeBasis(D, up, E).setPosition(o[0], 0, o[1]));
  return g;
}

function splitWidth(r, width) {
  const cuts = [0];
  let w = r.range(0.5, 1.3);
  while (width - w > 0.45) { cuts.push(w); w += r.range(0.8, 1.4); }
  cuts.push(width);
  return cuts.slice(0, -1).map((c, i) => [c, cuts[i + 1]]);
}

// ---------- 入口 ----------
export function build(ctx) {
  const { THREE, layout, materials: M, rng, geom } = ctx;
  const noise = makeNoise(rng);
  const plan = bankPlan(layout);
  const group = new THREE.Group();

  group.add(...buildGround(ctx, plan), buildBed(ctx, plan));

  const mossNoise = canvasTex(THREE, 512, drawMossNoise(rng('terrain-mossnoise')), false);
  // 墙面湿了主要是发暗；踏步湿了要有反光
  const wallMat = wetStoneMaterial(THREE, M.embankment, 'bankWall', mossNoise, { wetDark: 0.36, wetRough: 0.5 });
  const graniteCanvas = canvasTex(THREE, 1024, drawGranite(rng('terrain-granite')), true);
  const graniteBump = new THREE.CanvasTexture(graniteCanvas.image);
  Object.assign(graniteBump, { wrapS: THREE.RepeatWrapping, wrapT: THREE.RepeatWrapping, colorSpace: THREE.NoColorSpace });
  const stoneMat = wetStoneMaterial(THREE, new THREE.MeshStandardMaterial({
    map: graniteCanvas, bumpMap: graniteBump, bumpScale: 0.6, roughness: 0.72,
  }), 'bankStone', mossNoise, { wetDark: 0.45, wetRough: 0.08 });

  const walls = mergeGeometries(plan.walls.map((w, i) => wallGeometry(THREE, w, noise, i * 31.7)));
  const wallMesh = new THREE.Mesh(walls, wallMat);
  wallMesh.castShadow = true; wallMesh.receiveShadow = true;

  const r = rng('terrain-coping');
  // 压顶石临水一侧下沿带一点青苔
  const copingMoss = (x, y, z) => (y < -0.1 ? 0.3 * noise(x * 0.7, z * 0.7) : 0);
  const stones = [
    ...plan.copings.flatMap((c) => stoneRun(THREE, geom, r, c, COPING, copingMoss)),
    ...plan.curbs.flatMap((c) => stoneRun(THREE, geom, rng('terrain-curb'), c, { ...CURB, jitter: COPING.jitter }, () => 0)),
    ...layout.waterSteps.map((s) => buildWaterStep(ctx, s, noise)),
  ];
  const stoneMesh = new THREE.Mesh(mergeGeometries(stones), stoneMat);
  stoneMesh.castShadow = true; stoneMesh.receiveShadow = true;
  group.add(wallMesh, stoneMesh);
  return group;
}
