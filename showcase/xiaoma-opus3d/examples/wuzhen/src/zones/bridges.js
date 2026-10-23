// 桥区块：通济桥、仁济桥（单孔石拱，两桥直角相接成"桥里桥"）+ 东平桥、南街小平桥（石板平桥）。
// 局部坐标：u 沿桥面走向（0 = 桥中点），y 向上，w 横跨桥宽；建完按 axis 转到世界坐标。
// 全部几何按材质合并：条石、整石、桥面石、灰缝、湿石、石匾、草、藤叶，共 8 个 draw call。
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const STEP_H = 0.15; const STEP_D = 0.35;           // 拱桥踏步
const FLAT_STEP_H = 0.2; const FLAT_STEP_D = 0.3;   // 平桥踏步
const SILL_W = 0.3; const SILL_LIP = 0.04; const SILL_RISE = 0.18; // 地栿：宽、外挑、高出踏步线
const POST = 0.22; const POST_H = 0.95; const POST_GAP = 1.7;      // 望柱
const PANEL_H = 0.62;                                // 栏板高（地栿以上）
const JOINT = 0.012;                                 // 拱石缝宽
const COURSE = 0.32;                                 // 条石层高
const ASHLAR_W = 4.8; const ASHLAR_H = 9.6;          // 条石纹理覆盖范围（竖向不重复，从河床算起）
const PIER_T = 0.34; const CAP_T = 0.22; const SLAB_T = 0.26; // 平桥桥墩厚、盖梁厚、桥面石厚
const BOAT_CLEAR = 0.3;                              // 平桥桥墩离船舷最小距离
const MAX_SLAB = 4.2;                                // 平桥石板最大跨度

// ---------- 纹理 ----------

function canvas(w, h) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return c;
}

function canvasTex(c, repeatX, repeatY, color = true) {
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(repeatX, repeatY);
  t.colorSpace = color ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  t.anisotropy = 8;
  return t;
}

// 径向渐变斑块，水平方向环绕绘制保证纹理无缝
function blot(ctx, w, x, y, rad, rgb, alpha) {
  for (const dx of [-w, 0, w]) {
    const cx = x + dx;
    if (cx + rad < 0 || cx - rad > w) continue;
    const g = ctx.createRadialGradient(cx, y, 0, cx, y, rad);
    g.addColorStop(0, `rgba(${rgb},${alpha})`);
    g.addColorStop(1, `rgba(${rgb},0)`);
    ctx.fillStyle = g;
    ctx.fillRect(cx - rad, y - rad, rad * 2, rad * 2);
  }
}

function speckle(ctx, w, h, r, count, alphaMax, colors) {
  for (let i = 0; i < count; i++) {
    ctx.globalAlpha = r.range(0.03, alphaMax);
    ctx.fillStyle = r.pick(colors);
    const s = r.range(1, 2.5);
    ctx.fillRect(r.range(0, w), r.range(0, h), s, s);
  }
  ctx.globalAlpha = 1;
}

// 拱肩条石：青灰，0.32m 一层、长短不一错缝。纹理 v 对应世界高度（河床 → +6.4m），
// 所以能画出水线以下的深色水渍、水线附近的青苔和桥面淌下来的雨痕。
function drawAshlar(ctx, w, h, r, { bed, water }) {
  const ppm = w / ASHLAR_W;
  const yPx = (y) => h - (y - bed) * ppm;
  ctx.fillStyle = '#464a48';
  ctx.fillRect(0, 0, w, h);
  const rows = Math.round(ASHLAR_H / COURSE);
  const jp = 1.2;
  for (let j = 0; j < rows; j++) {
    const top = yPx(bed + (j + 1) * COURSE); const rh = COURSE * ppm;
    const lens = []; let sum = 0;
    while (sum < ASHLAR_W - 0.7) { const l = r.range(0.7, 1.6); lens.push(l); sum += l; }
    let x = r.range(0, w);
    for (const l of lens) {
      const lw = (l * ASHLAR_W / sum) * ppm;
      const v = r.range(-11, 11); const tint = r.range(-4, 4);
      for (const dx of [0, -w]) {
        const x0 = x + dx + jp; const sw = lw - 2 * jp;
        const g = ctx.createLinearGradient(0, top, 0, top + rh); // 每块石头上亮下暗，像微微凸出的石面
        g.addColorStop(0, `rgb(${104 + v + tint},${112 + v},${115 + v - tint})`);
        g.addColorStop(1, `rgb(${90 + v + tint},${98 + v},${101 + v - tint})`);
        ctx.fillStyle = g;
        ctx.fillRect(x0, top + jp, sw, rh - 2 * jp);
        ctx.fillStyle = 'rgba(190,194,188,0.14)';
        ctx.fillRect(x0, top + jp, sw, 2);
      }
      x = (x + lw) % w;
    }
  }
  // 水线以下常年浸水：发黑发绿
  const wl = yPx(water);
  const wet = ctx.createLinearGradient(0, wl - 0.7 * ppm, 0, h);
  wet.addColorStop(0, 'rgba(46,58,40,0)');
  wet.addColorStop(0.22, 'rgba(46,58,40,0.5)');
  wet.addColorStop(0.32, 'rgba(30,38,30,0.78)');
  wet.addColorStop(1, 'rgba(22,28,24,0.9)');
  ctx.fillStyle = wet;
  ctx.fillRect(0, wl - 0.7 * ppm, w, h);
  for (let i = 0; i < 90; i++) {
    blot(ctx, w, r.range(0, w), wl - r.range(-0.2, 0.9) * ppm, r.range(8, 46), '58,74,40', r.range(0.15, 0.4));
  }
  // 桥面淌下的雨痕
  for (let i = 0; i < 70; i++) {
    const x = r.range(0, w); const y0 = yPx(r.range(1.5, 6.2)); const len = r.range(0.4, 2.4) * ppm;
    const g = ctx.createLinearGradient(0, y0, 0, y0 + len);
    g.addColorStop(0, `rgba(36,40,38,${r.range(0.1, 0.26)})`);
    g.addColorStop(1, 'rgba(36,40,38,0)');
    ctx.fillStyle = g;
    ctx.fillRect(x, y0, r.range(3, 14), len);
  }
  for (let i = 0; i < 160; i++) { // 跨石块的风化色斑，打破砖墙一样的整齐感
    blot(ctx, w, r.range(0, w), r.range(0, h), r.range(30, 140), r.chance(0.5) ? '70,76,72' : '150,152,144', r.range(0.06, 0.16));
  }
  for (let i = 0; i < 50; i++) blot(ctx, w, r.range(0, w), r.range(0, h), r.range(6, 26), '170,170,140', r.range(0.08, 0.2));
  speckle(ctx, w, h, r, 26000, 0.25, ['#4a4e4d', '#a3a8a4', '#5d6553']);
}

// 整块青石（拱石、栏板、望柱、石板）：没有砌缝，只有风化色斑、石英颗粒和少量地衣。覆盖 1m × 1m
function drawStone(ctx, w, h, r) {
  ctx.fillStyle = '#717878';
  ctx.fillRect(0, 0, w, h);
  for (let i = 0; i < 40; i++) {
    blot(ctx, w, r.range(0, w), r.range(0, h), r.range(80, 260), r.chance(0.5) ? '150,154,150' : '84,90,90', r.range(0.12, 0.3));
  }
  for (let i = 0; i < 260; i++) {
    blot(ctx, w, r.range(0, w), r.range(0, h), r.range(6, 40), r.chance(0.5) ? '160,162,156' : '70,76,76', r.range(0.08, 0.25));
  }
  for (let i = 0; i < 30; i++) blot(ctx, w, r.range(0, w), r.range(0, h), r.range(10, 34), '120,128,92', r.range(0.15, 0.35));
  speckle(ctx, w, h, r, 60000, 0.2, ['#3f4444', '#a4a8a5', '#5a605f', '#4b5150']);
}

// 桥名石匾图集：上半"通济桥"，下半"仁济桥"。字是阴刻：浅色错位高光 + 深色字口
const PLAQUE_ROWS = { tongji: 0, renji: 1 };
function drawPlaques(ctx, w, h, r, names) {
  const rowH = h / 2;
  names.forEach((name, row) => {
    const y0 = row * rowH;
    ctx.fillStyle = '#8a8f8c';
    ctx.fillRect(0, y0, w, rowH);
    for (let i = 0; i < 40; i++) {
      const x = r.range(0, w); const y = y0 + r.range(0, rowH); const rad = r.range(10, 60);
      const g = ctx.createRadialGradient(x, y, 0, x, y, rad);
      g.addColorStop(0, `rgba(${r.chance(0.5) ? '60,66,64' : '170,172,166'},${r.range(0.1, 0.25)})`);
      g.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = g;
      ctx.fillRect(x - rad, y - rad, rad * 2, rad * 2);
    }
    ctx.strokeStyle = '#4c504e'; ctx.lineWidth = 7;
    ctx.strokeRect(18, y0 + 18, w - 36, rowH - 36);
    ctx.font = `${Math.round(rowH * 0.66)}px "Kaiti SC", "STKaiti", "KaiTi", "Songti SC", "STSong", serif`;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.letterSpacing = `${Math.round(w * 0.06)}px`;
    const cy = y0 + rowH / 2 + rowH * 0.03; const cx = w / 2 + w * 0.03;
    ctx.fillStyle = 'rgba(200,202,196,0.8)';
    ctx.fillText(name, cx + 3, cy + 3);
    ctx.fillStyle = '#252827';
    ctx.fillText(name, cx, cy);
  });
  speckle(ctx, w, h, r, 9000, 0.25, ['#4a4e4d', '#b0b4b0']);
}

function createBridgeMaterials(M, rng, LEVELS, layout) {
  const ac = canvas(1024, 2048);
  drawAshlar(ac.getContext('2d'), ac.width, ac.height, rng('bridges-tex-ashlar'), LEVELS);
  const ashlarMap = canvasTex(ac, 1 / ASHLAR_W, 1 / ASHLAR_H);
  ashlarMap.offset.set(0, -LEVELS.bed / ASHLAR_H); // uv.y = 世界高度 → 纹理里 bed 在最下沿
  ashlarMap.wrapT = THREE.ClampToEdgeWrapping;

  const sc = canvas(1024, 1024);
  drawStone(sc.getContext('2d'), sc.width, sc.height, rng('bridges-tex-stone'));

  const pc = canvas(1024, 512);
  const name = (id) => layout.bridges.find((b) => b.id === id).name;
  drawPlaques(pc.getContext('2d'), pc.width, pc.height, rng('bridges-tex-plaque'), [name('tongji'), name('renji')]);
  const plaqueMap = canvasTex(pc, 1, 1);

  const std = (name, p) => Object.assign(new THREE.MeshStandardMaterial(p), { name });
  return {
    ashlar: std('bridgeAshlar', { map: ashlarMap, roughness: 0.9 }),
    stone: std('bridgeStone', { map: canvasTex(sc, 1, 1), bumpMap: canvasTex(sc, 1, 1, false), bumpScale: 1.2, roughness: 0.88 }),
    mortar: std('bridgeMortar', { color: 0x252725, roughness: 1, side: THREE.DoubleSide }),
    wet: std('bridgeWet', { color: 0x313a31, roughness: 0.55 }),                       // 平桥石柱水线以下
    plaque: std('bridgePlaque', { map: plaqueMap, bumpMap: canvasTex(pc, 1, 1, false), bumpScale: 2, roughness: 0.85 }),
    slab: M.stoneSlab,
    grass: M.foliageWillow,
    leaf: M.foliageCamphor,
  };
}

// ---------- 几何工具 ----------

const V = (a) => new THREE.Vector3(a[0], a[1], a[2]);

// 一组四边形 → 平面着色几何；ctr 给定时自动把法线翻到朝外。UV 按面内米制投影，du/dv 用来错开纹理取样
function quadsGeom(quads, ctr, du = 0, dv = 0) {
  const pos = []; const nor = []; const uv = [];
  const e1 = new THREE.Vector3(); const e2 = new THREE.Vector3(); const d = new THREE.Vector3();
  for (const q of quads) {
    let [p0, p1, p2, p3] = q.map(V);
    const n = new THREE.Vector3().subVectors(p1, p0).cross(new THREE.Vector3().subVectors(p3, p0));
    const fc = p0.clone().add(p1).add(p2).add(p3).multiplyScalar(0.25);
    if (ctr && n.dot(fc.sub(ctr)) < 0) { [p1, p3] = [p3, p1]; n.negate(); }
    n.normalize();
    e1.subVectors(p1, p0).normalize();
    e2.crossVectors(n, e1);
    for (const p of [p0, p1, p2, p0, p2, p3]) {
      pos.push(p.x, p.y, p.z); nor.push(n.x, n.y, n.z);
      d.subVectors(p, p0);
      uv.push(d.dot(e1) + du, d.dot(e2) + dv);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  return g;
}

// 8 个角点的六面体（角点下标 = a + 2b + 4c）
function hexa(c, du, dv) {
  const ctr = c.reduce((s, p) => s.add(V(p)), new THREE.Vector3()).multiplyScalar(1 / 8);
  const faces = [[0, 2, 6, 4], [1, 3, 7, 5], [0, 1, 5, 4], [2, 3, 7, 6], [0, 1, 3, 2], [4, 5, 7, 6]];
  return quadsGeom(faces.map((f) => f.map((i) => c[i])), ctr, du, dv);
}

function shiftUV(g, du, dv) {
  const uv = g.attributes.uv;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) + du, uv.getY(i) + dv);
  return g;
}

// (u,y) 多边形沿 w 拉伸，w ∈ [w0, w0 + depth]
function extrudeUY(pts, depth, w0, holes = []) {
  const shape = new THREE.Shape(pts.map(([u, y]) => new THREE.Vector2(u, y)));
  for (const h of holes) shape.holes.push(new THREE.Path(h.map(([u, y]) => new THREE.Vector2(u, y))));
  const g = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: false, curveSegments: 1 });
  g.translate(0, 0, w0);
  // 竖直面统一按（水平距离, 世界高度）取 UV，否则侧壁上的条石层会竖着排
  const pos = g.attributes.position; const nor = g.attributes.normal; const uv = g.attributes.uv;
  for (let i = 0; i < pos.count; i++) {
    const nx = nor.getX(i); const nz = nor.getZ(i);
    if (Math.abs(nor.getY(i)) > 0.5) continue;
    uv.setXY(i, -nz * pos.getX(i) + nx * pos.getZ(i), pos.getY(i));
  }
  return g;
}

// 沿 [ua,ub] 的斜带：底边 f(u)+bot，顶边 f(u)+top，在 kinks 处折
function band(ua, ub, f, bot, top, kinks) {
  const us = [ua, ...kinks.filter((k) => k > ua + 1e-4 && k < ub - 1e-4), ub];
  const pts = us.map((u) => [u, f(u) + bot]);
  for (let i = us.length - 1; i >= 0; i--) pts.push([us[i], f(us[i]) + top]);
  return pts;
}

// 沿 [a,b] 随机切段（错缝），返回 [[s0,s1]]，段间留 gap
function splits(r, a, b, first, min, max, gap) {
  const out = []; let s = a; let len = first;
  while (b - s - len > min * 0.6) { out.push([s, s + len - gap / 2]); s += len + gap / 2; len = r.range(min, max); }
  out.push([s, b]);
  return out;
}

// ---------- 望柱头：覆莲 + 束腰 + 两重仰莲 + 火焰宝珠 ----------

// 一片莲瓣。局部：沿 +y 生长，外表面朝 +z；u 沿瓣长，v 横向。curl = 瓣尖外卷量
function petal(len, wid, thick, curl, su, sv) {
  const width = (u) => wid * Math.pow(Math.sin(Math.PI * (0.18 + 0.82 * u)), 0.5);
  const pos = []; const uv = []; const idx = [];
  for (const side of [1, -1]) {
    const base = pos.length / 3;
    for (let i = 0; i <= su; i++) {
      const u = i / su; const wu = width(u);
      for (let j = 0; j <= sv; j++) {
        const v = -1 + (2 * j) / sv;
        const bulge = Math.sqrt(Math.max(0, 1 - v * v)) * (wu / wid);
        const rib = Math.exp(-((v / 0.22) ** 2)) * (1 - u) * 0.35; // 中脊
        const z = curl * u * u * len + (side > 0 ? thick * (bulge + rib * bulge) : -thick * 0.35 * bulge);
        pos.push((v * wu) / 2, u * len, z);
        uv.push((v * wu) / 2, u * len);
      }
    }
    const row = sv + 1;
    for (let i = 0; i < su; i++) {
      for (let j = 0; j < sv; j++) {
        const a = base + i * row + j; const b = a + 1; const c = a + row; const d = c + 1;
        if (side > 0) idx.push(a, b, c, b, d, c); else idx.push(a, c, b, b, c, d);
      }
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

// 旋转体轮廓 [半径, 高]，高从柱头方座顶面算起
const HEAD_PROFILE = [
  [0, 0], [0.086, 0], [0.09, 0.012], [0.091, 0.03], [0.082, 0.05], [0.064, 0.068],      // 覆莲座
  [0.053, 0.082], [0.05, 0.096], [0.055, 0.106],                                          // 束腰
  [0.068, 0.117], [0.077, 0.127], [0.062, 0.136], [0.046, 0.142],                         // 仰莲座
  [0.048, 0.157], [0.055, 0.177], [0.058, 0.197], [0.054, 0.218], [0.043, 0.238],          // 宝珠
  [0.028, 0.256], [0.014, 0.271], [0.005, 0.284], [0, 0.292],
];
const PEARL_Y = [0.146, 0.292];
const COLLAR_H = 0.03;
const HEAD_SCALE = 1.15; // 轮廓按 0.19m 柱身设计，随柱身放大

function lotusHead(detail) {
  const hi = detail === 'high';
  const seg = hi ? 48 : 20;
  const parts = [];
  const collar = new THREE.BoxGeometry(0.215, COLLAR_H, 0.215);
  collar.translate(0, COLLAR_H / 2, 0);
  parts.push(collar);

  const np = HEAD_PROFILE.length;
  const lathe = new THREE.LatheGeometry(HEAD_PROFILE.map(([r, y]) => new THREE.Vector2(r, y + COLLAR_H)), seg);
  const pos = lathe.attributes.position;
  for (let k = 0; k < pos.count; k++) { // 宝珠上刻 8 道焰纹棱
    const y = pos.getY(k) - COLLAR_H;
    if (y <= PEARL_Y[0]) continue;
    const x = pos.getX(k); const z = pos.getZ(k);
    const fade = Math.sin((Math.PI * (y - PEARL_Y[0])) / (PEARL_Y[1] - PEARL_Y[0]));
    const f = 1 + 0.085 * Math.cos(8 * Math.atan2(x, z)) * fade;
    pos.setXYZ(k, x * f, pos.getY(k), z * f);
  }
  lathe.computeVertexNormals();
  const nor = lathe.attributes.normal; const uv = lathe.attributes.uv;
  for (let j = 0; j < np; j++) { // 接缝两侧法线取平均，近看不出竖线
    const a = j; const b = seg * np + j;
    const n = new THREE.Vector3().fromBufferAttribute(nor, a).add(new THREE.Vector3().fromBufferAttribute(nor, b)).normalize();
    nor.setXYZ(a, n.x, n.y, n.z); nor.setXYZ(b, n.x, n.y, n.z);
  }
  for (let i = 0; i <= seg; i++) {
    let s = 0;
    for (let j = 0; j < np; j++) {
      if (j > 0) s += Math.hypot(HEAD_PROFILE[j][0] - HEAD_PROFILE[j - 1][0], HEAD_PROFILE[j][1] - HEAD_PROFILE[j - 1][1]);
      uv.setXY(i * np + j, (i / seg) * 0.55, s);
    }
  }
  parts.push(lathe);

  const [su, sv] = hi ? [8, 6] : [3, 2];
  const ring = (count, phase, y, rad, len, wid, thick, curl, tilt, down) => {
    for (let k = 0; k < count; k++) {
      const phi = phase + (k / count) * Math.PI * 2;
      const p = petal(len, wid, thick, curl, su, sv);
      if (down) p.rotateZ(Math.PI);
      p.rotateX(down ? -tilt : tilt);
      p.rotateY(phi);
      p.translate(rad * Math.sin(phi), y + COLLAR_H, rad * Math.cos(phi));
      parts.push(p);
    }
  };
  ring(12, 0, 0.064, 0.074, 0.056, 0.05, 0.012, 0.2, 0.36, true);                    // 覆莲：瓣尖朝下贴着座身
  ring(12, Math.PI / 12, 0.108, 0.055, 0.058, 0.054, 0.012, 0.22, 0.46, false);     // 外重仰莲
  ring(12, 0, 0.118, 0.046, 0.052, 0.044, 0.01, 0.16, 0.22, false);                 // 内重仰莲
  const g = mergeGeometries(parts.map((p) => (p.index ? p.toNonIndexed() : p)), false);
  return g.scale(HEAD_SCALE, HEAD_SCALE, HEAD_SCALE);
}

// 抹角方柱身（沿 +y 拉伸）
function postShaft(height) {
  const s = POST / 2; const c = 0.018;
  const pts = [[-s + c, -s], [s - c, -s], [s, -s + c], [s, s - c], [s - c, s], [-s + c, s], [-s, s - c], [-s, -s + c]];
  const g = new THREE.ExtrudeGeometry(new THREE.Shape(pts.map(([x, y]) => new THREE.Vector2(x, y))), { depth: height, bevelEnabled: false });
  g.rotateX(-Math.PI / 2);
  return g;
}

// ---------- 草、藤 ----------

function grassTufts(r, spots) {
  const pos = []; const nor = []; const uv = [];
  for (const { p, n } of spots) {
    const blades = r.int(5, 10);
    for (let k = 0; k < blades; k++) {
      const len = r.range(0.08, 0.28);
      const dir = new THREE.Vector3(r.range(-0.5, 0.5), 1, r.range(-0.5, 0.5)).addScaledVector(n, r.range(0.3, 0.9)).normalize();
      const side = new THREE.Vector3().crossVectors(dir, n).normalize();
      if (side.lengthSq() < 1e-6) side.set(1, 0, 0);
      const base = p.clone().addScaledVector(side, r.range(-0.03, 0.03));
      const tip = base.clone().addScaledVector(dir, len).addScaledVector(side, r.range(-0.03, 0.03));
      const bw = r.range(0.004, 0.008);
      const a = base.clone().addScaledVector(side, -bw); const b = base.clone().addScaledVector(side, bw);
      for (const q of [a, b, tip]) { pos.push(q.x, q.y, q.z); nor.push(n.x, n.y, n.z); }
      uv.push(0, 0, 0.01, 0, 0.005, len);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  return g;
}

// 从栏杆下沿垂下来的藤蔓（薜荔），贴着拱肩立面。floor(u) = 藤梢最低能到的高度
function vineCurtain(r, { u0, spread, top, floor, face, s }) {
  const quads = [];
  const strands = r.int(9, 15);
  for (let k = 0; k < strands; k++) {
    let u = u0 + r.range(-spread / 2, spread / 2);
    let y = top(u) - r.range(0, 0.08);
    const len = r.range(0.5, 2.6) * (1 - Math.abs(u - u0) / spread);
    const yEnd = Math.max(y - len, floor(u));
    while (y > yEnd) {
      const size = r.range(0.06, 0.1);
      const off = r.range(0.012, 0.06);
      const c = [u + r.range(-0.03, 0.03), y, s * (face + off)];
      const ang = r.range(-0.9, 0.9);
      const e1 = [Math.sin(ang) * size * 0.5, -Math.cos(ang) * size * 0.5, s * r.range(-0.3, 0.5) * size];
      const e2 = [Math.cos(ang) * size * 0.32, Math.sin(ang) * size * 0.32, 0];
      quads.push([
        [c[0] + e1[0], c[1] + e1[1], c[2] + e1[2]], [c[0] + e2[0], c[1] + e2[1], c[2]],
        [c[0] - e1[0], c[1] - e1[1], c[2] - e1[2]], [c[0] - e2[0], c[1] - e2[1], c[2]],
      ]);
      y -= r.range(0.04, 0.07);
      u += r.range(-0.025, 0.025);
    }
  }
  return quadsGeom(quads, null);
}

// ---------- 布置辅助 ----------

function riverHalf(b, layout) {
  const rect = layout.rivers.find((rv) => rv.id === b.crosses).rect;
  return b.axis === 'z' ? (rect.z1 - rect.z0) / 2 : (rect.x1 - rect.x0) / 2;
}

// 从桥下穿过的船线 → 局部 u 坐标上的占用区间 [lo, hi]（船宽）
function boatLanes(b, layout) {
  const u0 = (b.from + b.to) / 2;
  const lanes = [];
  for (const boat of layout.boats) {
    const [fx, fz] = boat.from; const [tx, tz] = boat.to;
    const along = b.axis === 'z' ? fz === tz && Math.min(fx, tx) <= b.at && b.at <= Math.max(fx, tx)
      : fx === tx && Math.min(fz, tz) <= b.at && b.at <= Math.max(fz, tz);
    if (!along) continue;
    const c = (b.axis === 'z' ? fz : fx) - u0;
    lanes.push({ id: boat.id, lo: c - boat.beam / 2, hi: c + boat.beam / 2 });
  }
  return lanes.sort((a, c) => a.lo - c.lo);
}

function bridgeMatrix(b) {
  const u0 = (b.from + b.to) / 2;
  return b.axis === 'x'
    ? new THREE.Matrix4().makeTranslation(u0, 0, b.at)
    : new THREE.Matrix4().makeTranslation(b.at, 0, u0).multiply(new THREE.Matrix4().makeRotationY(-Math.PI / 2));
}

const oddRound = (x) => { const n = Math.round(x); return n % 2 ? n : n + 1; };

// ---------- 拱桥 ----------

function archBridge(b, { layout, geom, rng }, mats, heads) {
  const { water, bed } = layout.LEVELS;
  const r = rng(`bridges-${b.id}`);
  const parts = []; const add = (g, mat) => parts.push({ geom: g, mat });
  const R = b.span / 2; const yc = water + b.riseAboveWater - R; const t = 0.3 + 0.04 * R;
  const ext = R + t; const crownExt = yc + ext;
  const L = (b.to - b.from) / 2; const W = b.width; const hw = W / 2;
  const bank = riverHalf(b, layout);
  const plaqueH = 0.08 * R;
  const N = Math.ceil((crownExt + plaqueH + 0.25) / STEP_H - 1e-6);
  const H = N * STEP_H; const P = L - N * STEP_D;
  if (P < 0.8) throw new Error(`${b.id}: 桥长不够放下踏步（平台半长 ${P.toFixed(2)}m）`);
  const I = (u) => Math.min(H, Math.max(0, ((L - Math.abs(u)) * STEP_H) / STEP_D)); // 踏步内角线
  const T = (u) => I(u) + SILL_RISE;                                                 // 地栿顶
  const kinks = [-P, P];
  const wc = hw - SILL_W / 2 + SILL_LIP / 2; // 栏杆中线

  // 桥身（拱肩 + 桥台）：条石。拱券位置留空给拱石
  const outline = [[-L, 0], [-bank, 0], [-bank, bed], [-R, bed], [-R, yc], [-ext, yc]];
  const ARC = 72;
  for (let i = 1; i < ARC; i++) { const a = Math.PI - (Math.PI * i) / ARC; outline.push([ext * Math.cos(a), yc + ext * Math.sin(a)]); }
  outline.push([ext, yc], [R, yc], [R, bed], [bank, bed], [bank, 0], [L, 0], [P, H - 0.05], [-P, H - 0.05]); // 顶面低于平台石，避免共面闪烁
  add(extrudeUY(outline, W, -hw), mats.ashlar);

  // 拱券：一圈楔形拱石，沿桥宽分节错缝；拱石比拱肩外凸 3cm，拱心石再凸出
  const n = oddRound((Math.PI * R) / 0.42);
  const g = JOINT / 2 / R;
  for (let i = 0; i < n; i++) {
    const key = i === (n - 1) / 2;
    const th0 = (Math.PI * i) / n + g; const th1 = (Math.PI * (i + 1)) / n - g;
    const r1 = ext + (key ? 0.05 : r.range(-0.02, 0.02));
    const wOut = hw + 0.03 + (key ? 0.03 : 0);
    const first = i % 2 ? r.range(0.45, 0.75) : r.range(0.95, 1.3);
    for (const [s0, s1] of splits(r, -wOut, wOut, first, 0.9, 1.4, JOINT)) {
      const c = [];
      for (let k = 0; k < 8; k++) {
        const a = k & 1 ? th1 : th0; const rr = k & 2 ? r1 : R; const ww = k & 4 ? s1 : s0;
        c.push([-rr * Math.cos(a), yc + rr * Math.sin(a), ww]);
      }
      add(hexa(c, r.range(0, 1), r.range(0, 1)), mats.stone);
    }
  }
  // 灰缝：拱腹后面一层暗色筒面 + 两个立面的半圆环，石缝里看进去是深色
  const Wm = 2 * (hw + 0.03);
  const barrel = new THREE.CylinderGeometry(R + 0.02, R + 0.02, Wm, 96, 1, true, Math.PI / 2, Math.PI);
  barrel.rotateX(Math.PI / 2); barrel.translate(0, yc, 0);
  add(barrel, mats.mortar);
  for (const s of [1, -1]) {
    const ann = new THREE.RingGeometry(R + 0.003, ext - 0.003, 96, 1, 0, Math.PI);
    ann.translate(0, yc, s * (hw + 0.005));
    add(ann, mats.mortar);
  }

  // 踏步与拱顶平台：桥面石
  const treadW = W - 2 * SILL_W + 0.04;
  for (let k = 1; k <= N; k++) {
    for (const s of [1, -1]) {
      const uc = s * (L - (k - 0.5) * STEP_D + 0.01);
      const pieces = r.chance(0.45) ? splits(r, -treadW / 2, treadW / 2, r.range(0.8, treadW - 0.8), 9, 9, 0.012) : [[-treadW / 2, treadW / 2]];
      for (const [w0, w1] of pieces) {
        const box = geom.boxM(STEP_D + 0.02, STEP_H + 0.04, w1 - w0);
        add(shiftUV(geom.place(box, { x: uc, y: k * STEP_H - (STEP_H + 0.04) / 2, z: (w0 + w1) / 2 }), r.range(0, 2.4), r.range(0, 2.4)), mats.slab);
      }
    }
  }
  for (const [u0, u1] of splits(r, -P, P, r.range(0.9, 1.3), 0.9, 1.4, 0.012)) {
    const box = geom.boxM(u1 - u0, 0.14, treadW);
    add(shiftUV(geom.place(box, { x: (u0 + u1) / 2, y: H - 0.07, z: 0 }), r.range(0, 2.4), r.range(0, 2.4)), mats.slab);
  }

  // 栏杆：地栿 + 望柱 + 栏板 + 两端抱鼓石，两侧对称
  const uPost = L - 0.75;
  const M = oddRound((2 * uPost) / POST_GAP);
  const posts = Array.from({ length: M + 1 }, (_, j) => -uPost + (2 * uPost * j) / M);
  for (const s of [1, -1]) {
    const w0 = s > 0 ? hw - SILL_W : -hw - SILL_LIP;
    add(extrudeUY(band(-L, L, I, -0.06, SILL_RISE, kinks), SILL_W + SILL_LIP, w0), mats.stone);
    for (const u of posts) {
      const shaft = postShaft(POST_H + 0.08);
      shaft.translate(u, T(u) - 0.08, s * wc);
      add(shaft, mats.stone);
      const head = heads[b.id === 'tongji' && Math.abs(u) < 4 ? 'high' : 'low'].clone();
      head.translate(u, T(u) + POST_H, s * wc);
      add(head, mats.stone);
    }
    for (let j = 0; j < M; j++) {
      const ua = posts[j] + POST / 2 - 0.02; const ub = posts[j + 1] - POST / 2 + 0.02;
      add(extrudeUY(band(ua, ub, T, -0.03, PANEL_H, kinks), 0.085, s * wc - 0.0425), mats.stone);
      const hole = band(ua + 0.08, ub - 0.08, T, 0.08, PANEL_H - 0.08, kinks);
      add(extrudeUY(band(ua, ub, T, -0.03, PANEL_H, kinks), 0.12, s * wc - 0.06, [hole]), mats.stone);
    }
    for (const e of [1, -1]) { // 抱鼓石
      const ud = e * (L - 0.4);
      const [ua, ub] = e > 0 ? [uPost, L - 0.05] : [-(L - 0.05), -uPost];
      add(extrudeUY(band(ua, ub, T, -0.03, 0.14, kinks), 0.17, s * wc - 0.085), mats.stone);
      const drum = new THREE.CylinderGeometry(0.24, 0.24, 0.15, 36);
      drum.rotateX(Math.PI / 2); drum.translate(ud, T(ud) + 0.36, s * wc);
      add(drum, mats.stone);
      const boss = new THREE.CylinderGeometry(0.15, 0.15, 0.18, 28);
      boss.rotateX(Math.PI / 2); boss.translate(ud, T(ud) + 0.36, s * wc);
      add(boss, mats.stone);
      const [pa, pb] = e > 0 ? [uPost, ud] : [ud, -uPost];
      add(extrudeUY(band(pa, pb, T, 0.1, 0.36, kinks), 0.085, s * wc - 0.0425), mats.stone);
    }
  }

  // 桥名石匾：拱心石正上方，两个立面各一块
  const pw = plaqueH * 4; const yP = (crownExt + H - 0.06) / 2;
  const row = PLAQUE_ROWS[b.id];
  for (const s of [1, -1]) {
    add(geom.place(geom.boxM(pw + 0.12, plaqueH + 0.12, 0.06), { x: 0, y: yP, z: s * (hw + 0.03) }), mats.stone);
    const face = new THREE.PlaneGeometry(pw, plaqueH);
    const uv = face.attributes.uv;
    for (let k = 0; k < uv.count; k++) uv.setY(k, uv.getY(k) * 0.5 + (row === 0 ? 0.5 : 0)); // 图集第 0 行在上半
    if (s < 0) face.rotateY(Math.PI);
    face.translate(0, yP, s * (hw + 0.0605));
    add(face, mats.plaque);
  }

  // 石缝里的草：拱肩立面沿条石横缝、桥脚、踏步与地栿交角
  const floorAt = (u) => (Math.abs(u) >= bank ? 0 : water);
  const spots = [];
  for (const s of [1, -1]) {
    for (let k = 0; k < 48; k++) {
      const u = r.range(-L + 0.6, L - 0.6);
      const lo = floorAt(u) + 0.08; const hi = I(u) - 0.25;
      if (hi <= lo) continue;
      let y = lo + (hi - lo) * r.next() ** 2;
      y = bed + Math.round((y - bed) / COURSE) * COURSE + 0.01;
      const inArch = Math.abs(u) < ext + 0.08 && y < yc + Math.sqrt(Math.max(0, (ext + 0.08) ** 2 - u * u));
      if (inArch || y < lo || y > hi) continue;
      spots.push({ p: new THREE.Vector3(u, y, s * (hw + 0.005)), n: new THREE.Vector3(0, 0, s) });
    }
    for (let k = 0; k < 10; k++) {
      const kk = r.int(1, N - 1); const e = r.chance(0.5) ? 1 : -1;
      spots.push({ p: new THREE.Vector3(e * (L - kk * STEP_D + 0.03), kk * STEP_H, s * (hw - SILL_W - 0.02)), n: new THREE.Vector3(0, 1, 0) });
    }
  }
  add(grassTufts(r, spots), mats.grass);

  // 藤蔓：每个立面挂在一侧或两侧拱肩上
  for (const s of [1, -1]) {
    for (const e of [1, -1]) {
      if (!r.chance(0.7)) continue;
      const u0 = e * r.range(ext + 0.4, Math.min(bank + 1.2, L - 2));
      const floor = (u) => {
        const a = Math.abs(u);
        if (a < ext + 0.02) return yc + Math.sqrt(ext * ext - a * a) + 0.03;
        return floorAt(u) + 0.25;
      };
      add(vineCurtain(r, { u0, spread: r.range(0.8, 1.5), top: (u) => I(u) - 0.07, floor, face: hw + SILL_LIP, s }), mats.leaf);
    }
  }

  const lanes = boatLanes(b, layout).map((ln) => {
    const edge = Math.max(Math.abs(ln.lo), Math.abs(ln.hi));
    return { id: ln.id, clearAtBeamEdge: Number((yc + Math.sqrt(Math.max(0, R * R - edge * edge)) - water).toFixed(2)) };
  });
  return { parts, info: { id: b.id, voussoirs: n, steps: N, deckH: H, platform: 2 * P, posts: posts.length * 2, crownIntrados: yc + R, lanes } };
}

// ---------- 石板平桥 ----------

function flatBridge(b, { layout, geom, rng }, mats) {
  const { bed, water } = layout.LEVELS;
  const r = rng(`bridges-${b.id}`);
  const parts = []; const add = (g, mat) => parts.push({ geom: g, mat });
  const L = (b.to - b.from) / 2; const W = b.width; const hw = W / 2;
  const bank = riverHalf(b, layout);
  const N = Math.max(2, Math.round(b.deckY / FLAT_STEP_H)); const h = b.deckY / N;
  const deckEnd = L - (N - 1) * FLAT_STEP_D; const e1 = deckEnd - 0.3;
  if (e1 >= bank) throw new Error(`${b.id}: 踏步全落在岸上，桥台算不出来`);
  const under = b.deckY - SLAB_T;

  // 桥台：岸上托踏步，水里伸出一截托石板端头
  for (const s of [1, -1]) {
    const pts = [[L, 0], [bank, 0], [bank, bed], [e1, bed], [e1, under], [deckEnd, under], [deckEnd, (N - 1) * h]].map(([u, y]) => [s * u, y]);
    add(extrudeUY(pts, W, -hw), mats.ashlar);
    for (let k = 1; k < N; k++) {
      const box = geom.boxM(FLAT_STEP_D + 0.02, h + 0.04, W + 0.03); // 比桥台略宽，避免侧面共面
      add(shiftUV(geom.place(box, { x: s * (L - (k - 0.5) * FLAT_STEP_D + 0.01), y: k * h - (h + 0.04) / 2, z: 0 }), r.range(0, 2.4), r.range(0, 2.4)), mats.slab);
    }
  }

  // 桥墩：避开船线，贴着船道两侧和船道之间放
  const lanes = boatLanes(b, layout);
  const piers = [];
  const pad = BOAT_CLEAR + PIER_T / 2;
  lanes.forEach((ln, i) => {
    if (i === 0) piers.push(ln.lo - pad);
    if (i < lanes.length - 1) piers.push((ln.hi + lanes[i + 1].lo) / 2);
    if (i === lanes.length - 1) piers.push(ln.hi + pad);
  });
  const ok = piers.filter((p) => Math.abs(p) < e1 - 0.6);
  if (lanes.some((ln, i) => i < lanes.length - 1 && lanes[i + 1].lo - ln.hi < PIER_T + 2 * BOAT_CLEAR)) {
    throw new Error(`${b.id}: 两条船线之间放不下桥墩`);
  }
  const supports = [-deckEnd, ...ok.sort((a, c) => a - c), deckEnd];
  for (let i = supports.length - 2; i >= 0; i--) { // 跨度太大时在中间补墩
    const gap = supports[i + 1] - supports[i];
    const lane = lanes.find((ln) => ln.lo - pad < supports[i] + gap / 2 && supports[i] + gap / 2 < ln.hi + pad);
    if (gap > MAX_SLAB && !lane) supports.splice(i + 1, 0, supports[i] + gap / 2);
  }
  const nC = Math.max(2, Math.round((W + 0.2) / 0.9)); const colTop = under - CAP_T; const wetTop = water + 0.28;
  for (const u of supports.slice(1, -1)) {
    for (let k = 0; k < nC; k++) { // 一排竖立的方石柱
      const z = (-(W - PIER_T) / 2) + ((W - PIER_T) * k) / (nC - 1);
      add(shiftUV(geom.place(geom.boxM(PIER_T, colTop - wetTop, PIER_T), { x: u, y: (colTop + wetTop) / 2, z }), r.range(0, 1), r.range(0, 1)), mats.stone);
      add(geom.place(geom.boxM(PIER_T + 0.008, wetTop - bed, PIER_T + 0.008), { x: u, y: (wetTop + bed) / 2, z }), mats.wet);
    }
    add(shiftUV(geom.place(geom.boxM(PIER_T + 0.16, CAP_T, W + 0.4), { x: u, y: under - CAP_T / 2, z: 0 }), r.range(0, 1), r.range(0, 1)), mats.stone);
  }

  // 桥面：几条长石板并排，在墩上断开
  const nS = Math.max(2, Math.round(W / 0.8)); const sw = W / nS;
  for (let i = 0; i < supports.length - 1; i++) {
    const u0 = supports[i] + 0.01; const u1 = supports[i + 1] - 0.01;
    for (let k = 0; k < nS; k++) {
      const box = geom.boxM(u1 - u0, SLAB_T, sw - 0.015);
      const sink = r.range(0, 0.012); // 老石板微微高低不平
      add(shiftUV(geom.place(box, { x: (u0 + u1) / 2, y: b.deckY - SLAB_T / 2 - sink, z: -hw + (k + 0.5) * sw }), r.range(0, 1), r.range(0, 1)), mats.stone);
    }
  }

  const spots = [];
  for (const s of [1, -1]) {
    for (let k = 0; k < 6; k++) {
      const e = r.chance(0.5) ? 1 : -1; const kk = r.int(1, N - 1);
      spots.push({ p: new THREE.Vector3(e * (L - kk * FLAT_STEP_D + 0.03), kk * h, s * (hw - 0.03)), n: new THREE.Vector3(0, 1, 0) });
    }
  }
  add(grassTufts(r, spots), mats.grass);
  return { parts, info: { id: b.id, steps: N - 1, piers: supports.slice(1, -1).map((u) => Number(u.toFixed(2))), lanes: lanes.map((ln) => ln.id), clearance: Number((under - layout.LEVELS.water).toFixed(2)) } };
}

// ---------- 入口 ----------

export function build(ctx) {
  const { layout, materials: M, geom, rng } = ctx;
  const mats = createBridgeMaterials(M, rng, layout.LEVELS, layout);
  const heads = { high: lotusHead('high'), low: lotusHead('low') };
  const all = []; const info = [];
  for (const b of layout.bridges) {
    const res = b.type === 'arch' ? archBridge(b, ctx, mats, heads) : flatBridge(b, ctx, mats);
    const m = bridgeMatrix(b);
    for (const p of res.parts) { p.geom.applyMatrix4(m); all.push(p); }
    info.push(res.info);
  }
  const grassMats = new Set([mats.grass, mats.leaf]);
  const group = new THREE.Group();
  group.add(geom.mergeByMaterial(all.filter((p) => !grassMats.has(p.mat))));
  group.add(geom.mergeByMaterial(all.filter((p) => grassMats.has(p.mat)), { castShadow: false }));
  group.userData.bridges = info;
  return group;
}
