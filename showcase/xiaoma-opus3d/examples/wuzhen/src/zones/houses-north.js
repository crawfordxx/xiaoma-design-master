// 北岸枕水人家：NA/NB/NW/NE 四排民居（全部 buildHouse）+ 临水红灯笼、晾衣竹竿、半卷竹帘、
// 花盆、私家下水石阶、屋顶烟囱/老虎窗/青苔。位置全部由 layout 记录 + HOUSE 常量推导。
// 坐标约定：
//   立面坐标 (u, y, v)：临水背立面，u 沿墙（= house.js 里背立面的 x），v = 离墙面向外的距离
//   坡面坐标：民居局部坐标的前坡（屋脊在 z=0，向 +Z 下降）；后坡再绕 y 转 180°
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const ZONE = 'houses-north';
const CHUNK = 60; // 合并分块长度（米），保留一点视锥剔除
const TILE_DEPTH = 0.05; // 与 geom.tiledRoofSlope 默认瓦垄高度一致

// 灯笼尺寸（局部原点 = 灯笼顶盖挂点，向 -Y 垂下）
const LAN = { a: 0.21, b: 0.26, phi: 1.15, top: -0.045 };
LAN.yc = LAN.top - LAN.b * Math.sin(LAN.phi);
LAN.bottom = LAN.yc - LAN.b * Math.sin(LAN.phi);

let rig = null; // { lanterns, meshes, tmp }

export function build(ctx) {
  const { THREE, layout, materials: M, rng, geom, buildHouse, houseToWorld, HOUSE } = ctx;
  const own = ownMaterials(THREE, M, rng);
  const root = new THREE.Group();
  const chunks = new Map();
  const details = [];
  const mossParts = [];
  const lanterns = [];
  const env = { THREE, M, own, geom, HOUSE, rng, houseToWorld, details, mossParts, lanterns };

  for (const h of layout.houses.filter((x) => x.zone === 'north')) {
    const g = buildHouse(h, { materials: M, rng });
    g.updateMatrixWorld(true);
    const isDetailed = h.detail === 'high';
    const sag = isDetailed ? measureSag(env, h, g) : 0;
    const axisPos = h.row === 'NW' || h.row === 'NE' ? h.z : h.x;
    const key = `${h.row}-${Math.floor((axisPos + 120) / CHUNK)}`;
    if (!chunks.has(key)) chunks.set(key, []);
    const list = chunks.get(key);
    for (const mesh of g.children) {
      list.push({ geom: mesh.geometry.clone().applyMatrix4(mesh.matrixWorld), mat: mesh.material });
      mesh.geometry.dispose();
    }
    if (h.row === 'NA') addWaterside(env, h);
    if (isDetailed) addRoofDetails(env, h, sag);
  }

  for (const [key, parts] of chunks) {
    const merged = geom.mergeByMaterial(parts);
    merged.name = `${ZONE}-${key}`;
    root.add(merged);
  }
  if (details.length) {
    const d = geom.mergeByMaterial(details, { castShadow: false });
    d.name = `${ZONE}-details`;
    root.add(d);
  }
  if (mossParts.length) {
    const moss = geom.mergeByMaterial(mossParts.map((g) => ({ geom: g, mat: own.moss })), { castShadow: false });
    moss.name = `${ZONE}-moss`;
    moss.children.forEach((m) => { m.renderOrder = 1; });
    root.add(moss);
  }
  root.add(buildLanternRig(env));
  update(0);
  for (const m of rig.meshes) m.computeBoundingSphere();

  const stats = countStats(root);
  root.userData.stats = stats;
  if (typeof window !== 'undefined') window.__housesNorthStats = stats;
  return root;
}

// 灯笼随风轻摆：只由 t 决定
export function update(t) {
  if (!rig) return;
  const { lanterns, meshes: [body, frame, tassel, cord], tmp } = rig;
  lanterns.forEach((l, i) => {
    const ax = l.amp * (0.7 * Math.sin(1.9 * t + l.p1) + 0.3 * Math.sin(0.73 * t + l.p2));
    const az = l.amp * 0.45 * Math.sin(1.31 * t + l.p3);
    tmp.e.set(ax, l.yaw, az, 'YXZ');
    tmp.q.setFromEuler(tmp.e);
    tmp.base.compose(l.pivot, tmp.q, tmp.one);
    tmp.m.makeTranslation(0, -l.len, 0).premultiply(tmp.base);
    body.setMatrixAt(i, tmp.m);
    frame.setMatrixAt(i, tmp.m);
    tassel.setMatrixAt(i, tmp.m);
    tmp.m.makeScale(1, l.len, 1).premultiply(tmp.base);
    cord.setMatrixAt(i, tmp.m);
  });
  for (const m of rig.meshes) m.instanceMatrix.needsUpdate = true;
}

// ---------------------------------------------------------------- 材质

function ownMaterials(THREE, M, rng) {
  const std = (name, p) => Object.assign(new THREE.MeshStandardMaterial(p), { name: `${ZONE}-${name}` });
  return {
    bamboo: std('bamboo', { color: 0x8a7848, roughness: 0.7 }),
    blind: std('blind', { map: blindTexture(THREE, rng(`${ZONE}-tex-blind`).next), roughness: 0.85 }),
    pot: std('pot', { color: 0x74462f, roughness: 0.92 }),
    flower: std('flower', { color: 0xa8303a, roughness: 0.8 }),
    tassel: std('tassel', { color: 0x7e1a12, roughness: 0.85 }),
    wetStone: std('wetStone', { map: M.embankment.map, color: 0x6c7862, roughness: 0.55 }),
    moss: std('moss', {
      map: mossAtlas(THREE, rng(`${ZONE}-tex-moss`).next), transparent: true, depthWrite: false, roughness: 0.95,
      polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -4,
    }),
  };
}

// 竹帘：横向细篾，0.5m × 0.5m 一张
function blindTexture(THREE, r) {
  const c = document.createElement('canvas');
  c.width = 64; c.height = 256;
  const g = c.getContext('2d');
  g.fillStyle = '#6f5f3c';
  g.fillRect(0, 0, 64, 256);
  for (let y = 0; y < 256; y += 6) {
    const v = r() * 24 - 12;
    g.fillStyle = `rgb(${150 + v},${128 + v},${84 + v * 0.6})`;
    g.fillRect(0, y, 64, 4);
  }
  g.fillStyle = 'rgba(40,30,18,0.7)'; // 两道编绳
  g.fillRect(14, 0, 2, 256); g.fillRect(48, 0, 2, 256);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(2, 2);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// 屋面青苔/地衣斑：2×2 图集，四种形状，边缘透明
function mossAtlas(THREE, r) {
  const S = 256;
  const c = document.createElement('canvas');
  c.width = S * 2; c.height = S * 2;
  const g = c.getContext('2d');
  for (let cell = 0; cell < 4; cell++) {
    const ox = (cell % 2) * S; const oy = Math.floor(cell / 2) * S;
    g.save();
    g.beginPath(); g.rect(ox, oy, S, S); g.clip();
    for (let i = 0; i < 70; i++) {
      // 斑块集中在中间，越往边越稀
      const a = r() * Math.PI * 2; const d = Math.pow(r(), 1.6) * S * 0.36;
      const x = ox + S / 2 + Math.cos(a) * d * 1.2; const y = oy + S / 2 + Math.sin(a) * d * 0.8;
      const rad = S * (0.05 + r() * 0.12);
      const lichen = r() < 0.25;
      const col = lichen ? [112, 108, 76] : [56 + r() * 16, 70 + r() * 14, 42 + r() * 10];
      const grd = g.createRadialGradient(x, y, 0, x, y, rad);
      grd.addColorStop(0, `rgba(${col.map(Math.round).join(',')},${0.45 + r() * 0.35})`);
      grd.addColorStop(1, `rgba(${col.map(Math.round).join(',')},0)`);
      g.fillStyle = grd;
      g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
    }
    g.restore();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// ---------------------------------------------------------------- 坐标工具

function houseFrame(THREE, h) {
  return new THREE.Matrix4().makeRotationY(h.rotY).setPosition(h.x, 0, h.z);
}

// 临水背立面坐标 → 世界
function facadeFrame(THREE, h) {
  return houseFrame(THREE, h)
    .multiply(new THREE.Matrix4().makeTranslation(0, 0, -h.depth / 2))
    .multiply(new THREE.Matrix4().makeRotationY(Math.PI));
}

function bayCenters(HOUSE, h) {
  const Wi = h.width - 2 * HOUSE.gable; const bw = Wi / h.bays;
  return { bw, xs: Array.from({ length: h.bays }, (_, b) => -Wi / 2 + bw * (b + 0.5)) };
}

// 主屋面参数（与 buildHouse 一致）
function roofParams(HOUSE, h) {
  const run = h.depth / 2 + HOUSE.overhang; const rise = run * HOUSE.slope;
  const R = h.eaveHeight + (h.depth / 2) * HOUSE.slope;
  const len = Math.hypot(run, rise);
  return { run, rise, R, ny: run / len, nz: rise / len };
}

// buildHouse 的举折 sag 带随机成分：从生成好的瓦面上量出来（s=0.5、瓦垄零点处打一条竖线）
function measureSag({ THREE, M, HOUSE, houseToWorld }, h, g) {
  const tile = g.children.find((m) => m.material === M.tile);
  const { run, rise, R } = roofParams(HOUSE, h);
  const o = houseToWorld(h, 0.1, R + 4, run * 0.5);
  const ray = new THREE.Raycaster(new THREE.Vector3(o.x, o.y, o.z), new THREE.Vector3(0, -1, 0));
  const hit = ray.intersectObject(tile, false)[0];
  return hit ? R + 0.05 - rise * 0.5 - hit.point.y : 0.16;
}

// 坡面上一点（坡面坐标，含瓦垄起伏），lift = 沿法线抬高
function roofPoint(rp, sag, x, s, lift = 0) {
  const bump = TILE_DEPTH * Math.cos((2 * Math.PI * x) / 0.4) + lift;
  return [x, rp.R + 0.05 - rp.rise * s - sag * Math.sin(Math.PI * s) + bump * rp.ny, rp.run * s + bump * rp.nz];
}

// 把几何（局部坐标）放好再乘上 frame，压进 list
function put(list, g, mat, frame, t = {}, place) {
  place(g, t);
  g.applyMatrix4(frame);
  list.push({ geom: g, mat });
}

// ---------------------------------------------------------------- 临水一侧

function addWaterside(env, h) {
  const { THREE, HOUSE, rng } = env;
  const F = facadeFrame(THREE, h);
  const { bw, xs } = bayCenters(HOUSE, h);
  const r = rng(`${ZONE}-${h.id}-water`);
  const lanternBays = addHouseLanterns(env, h, xs, r);

  const twoFloors = h.floors === 2;
  const poleBay = twoFloors && r.chance(0.45) ? r.int(0, h.bays - 1) : -1;
  if (poleBay >= 0) addClothesPole(env, h, F, xs[poleBay], r);
  if (twoFloors) {
    const P = HOUSE.plinth; const y0 = P + HOUSE.firstFloor + 0.13; const h2 = h.eaveHeight - 0.2 - y0;
    const w = Math.min(bw - 0.6, 2.2); const wh = Math.min(1.15, h2 - 0.5);
    xs.forEach((u, b) => {
      if (b !== poleBay && r.chance(0.35)) addBlind(env, F, u, y0 + h2 * 0.55 + wh / 2, w, wh, 0.03, r);
    });
  }

  if (h.waterPavilion) {
    const d = h.waterPavilion.depth; const Wp = h.width - 0.2;
    const panes = Math.max(2, Math.round(Wp / 1.2)); const pw = Wp / panes;
    const paneU = Array.from({ length: panes }, (_, i) => -(-Wp / 2 + pw * (i + 0.5)));
    paneU.forEach((u) => { if (r.chance(0.3)) addBlind(env, F, u, 2.55, pw - 0.12, 1.2, d + 0.085, r); });
    const free = paneU.filter((u) => lanternBays.every((lu) => Math.abs(lu - u) > 0.55));
    if (free.length && r.chance(0.6)) addPots(env, F, r.pick(free), 1.3, d + 0.13, pw * 0.8, r);
  } else {
    const doorBay = Math.floor(h.bays / 2);
    xs.forEach((u, b) => {
      if (b !== doorBay && r.chance(0.45)) addPots(env, F, u, 1.8, 0.17, 0.8, r);
    });
    addPrivateSteps(env, h, F, xs[doorBay], r);
  }
}

// 每栋 1–3 盏：有水阁挂水阁檐下，没有水阁挂背立面腰檐下（单层挂主檐下）
function addHouseLanterns({ HOUSE, houseToWorld, lanterns }, h, xs, r) {
  const roll = r.next(); // 1 盏 20%、2 盏 45%、3 盏 35%：倒影是最后一镜的主角，宁多勿少
  const count = Math.min(h.bays, roll < 0.2 ? 1 : roll < 0.65 ? 2 : 3);
  const order = xs.map((u, b) => ({ u, k: r.next(), b })).sort((a, b) => a.k - b.k).slice(0, count);
  let v; let pivotY; let lenRange;
  if (h.waterPavilion) {
    // 水阁单坡：墙顶 2.6，run = d + 0.5，rise = 0.3·run，sag 0.04（见 house.js addPavilion）
    const d = h.waterPavilion.depth; const run = d + 0.5; const rise = run * 0.3;
    v = d + 0.36; const s = v / run;
    pivotY = 2.6 + rise + 0.1 - rise * s - 0.04 * Math.sin(Math.PI * s) - 0.14;
    lenRange = [0.24, 0.32];
  } else if (h.floors === 2) {
    // 背立面腰檐：起点 (v=-0.05, y=f2+0.62)，run 0.9，rise 0.42，sag 0.03
    const f2 = HOUSE.plinth + HOUSE.firstFloor;
    v = 0.55; const s = (v + 0.05) / 0.9;
    pivotY = f2 + 0.62 - 0.42 * s - 0.03 * Math.sin(Math.PI * s) - 0.14;
    lenRange = [0.16, 0.24];
  } else {
    const rp = roofParams(HOUSE, h);
    v = 0.35; const s = (h.depth / 2 + v) / rp.run;
    pivotY = rp.R + 0.05 - rp.rise * s - 0.16 * Math.sin(Math.PI * s) - 0.14;
    lenRange = [0.3, 0.4];
  }
  const sameLen = r.range(...lenRange);
  for (const { u } of order) {
    const p = houseToWorld(h, -u, pivotY, -h.depth / 2 - v);
    lanterns.push({
      pivot: p, len: sameLen + r.range(-0.03, 0.03), yaw: h.rotY + r.range(-0.4, 0.4),
      amp: r.range(0.035, 0.06), p1: r.range(0, 6.28), p2: r.range(0, 6.28), p3: r.range(0, 6.28),
    });
  }
  return order.map((o) => o.u);
}

// 二层窗口伸出的晾衣竹竿，衣服挂在衣架上，面朝河
function addClothesPole({ THREE, geom, M, own, HOUSE, details }, h, F, u, r) {
  const P = HOUSE.plinth; const y0 = P + HOUSE.firstFloor + 0.13; const h2 = h.eaveHeight - 0.2 - y0;
  const y = y0 + h2 * 0.55 + 0.2; const len = 1.9; const tilt = r.range(0.06, 0.12);
  const pole = new THREE.CylinderGeometry(0.022, 0.026, len, 6);
  put(details, pole, own.bamboo, F, { x: u, y: y + Math.sin(tilt) * len / 2, z: len / 2, rx: Math.PI / 2 - tilt }, geom.place);
  const n = r.int(2, 4);
  for (let i = 0; i < n; i++) {
    const v = 0.45 + i * 0.4 + r.range(-0.05, 0.05);
    const gw = r.range(0.42, 0.62); const gh = r.range(0.5, 0.78);
    const py = y + Math.sin(tilt) * v - 0.03;
    const mat = r.pick([M.cloth, M.flagCloth, M.flagCloth]);
    put(details, geom.planeM(gw, gh), mat, F, { x: u + r.range(-0.04, 0.04), y: py - 0.06 - gh / 2, z: v, rz: r.range(-0.04, 0.04) }, geom.place);
    put(details, geom.boxM(gw * 0.9, 0.02, 0.02), M.woodDark, F, { x: u, y: py - 0.05, z: v }, geom.place); // 衣架
  }
}

// 半卷的竹帘：上横杆 + 放下的帘子 + 底下卷起的一卷。top = 窗洞上沿，v = 离墙距离
function addBlind({ THREE, geom, M, own, details }, F, u, top, w, wh, v, r) {
  const hb = wh * r.range(0.3, 0.65); const bwid = w + 0.1;
  put(details, geom.boxM(bwid + 0.06, 0.04, 0.04), M.woodDark, F, { x: u, y: top + 0.05, z: v + 0.02 }, geom.place);
  put(details, geom.boxM(bwid, hb, 0.012), own.blind, F, { x: u, y: top + 0.03 - hb / 2, z: v + 0.02 }, geom.place);
  const roll = new THREE.CylinderGeometry(0.035, 0.035, bwid, 8);
  put(details, roll, own.bamboo, F, { x: u, y: top + 0.03 - hb, z: v + 0.035, rz: Math.PI / 2 }, geom.place);
}

// 窗下小木搁板 + 几盆花
function addPots({ THREE, geom, M, own, details }, F, u, y, v, span, r) {
  put(details, geom.boxM(span, 0.04, 0.2), M.woodDark, F, { x: u, y, z: v }, geom.place);
  for (const sx of [-0.4, 0.4]) {
    put(details, geom.boxM(0.03, 0.14, 0.18), M.woodDark, F, { x: u + sx * span, y: y - 0.09, z: v }, geom.place);
  }
  const n = r.int(2, 3);
  for (let i = 0; i < n; i++) {
    const x = u - span / 2 + (span * (i + 0.5)) / n + r.range(-0.05, 0.05);
    const ph = r.range(0.13, 0.19);
    put(details, new THREE.CylinderGeometry(0.085, 0.062, ph, 8), own.pot, F, { x, y: y + 0.02 + ph / 2, z: v }, geom.place);
    const leaf = new THREE.IcosahedronGeometry(r.range(0.1, 0.15), 0);
    leaf.scale(1, r.range(0.7, 1.1), 1);
    put(details, leaf, M.foliageCamphor, F, { x, y: y + 0.02 + ph + 0.07, z: v, ry: r.range(0, 3) }, geom.place);
    if (r.chance(0.6)) {
      for (let k = 0; k < 3; k++) {
        put(details, new THREE.IcosahedronGeometry(0.028, 0), own.flower, F,
          { x: x + r.range(-0.08, 0.08), y: y + ph + r.range(0.12, 0.2), z: v + r.range(-0.08, 0.06) }, geom.place);
      }
    }
  }
}

// 没有水阁的临水户：后门外一块石台，石阶贴着驳岸横向下到水面（伸出 0.9m）
function addPrivateSteps({ geom, M, own, details }, h, F, uDoor, r) {
  const sgn = uDoor > 0.01 ? -1 : uDoor < -0.01 ? 1 : (r.chance(0.5) ? 1 : -1);
  const out = 0.9; const bed = -3.2;
  const block = (u0, u1, top) => {
    const mat = top <= -0.85 ? own.wetStone : M.embankment;
    put(details, geom.boxM(Math.abs(u1 - u0), top - bed, out), mat, F, { x: (u0 + u1) / 2, y: (top + bed) / 2, z: out / 2 }, geom.place);
  };
  block(uDoor - 0.65, uDoor + 0.65, 0.15);
  for (let k = 1; k <= 8; k++) {
    const u0 = uDoor + sgn * (0.65 + 0.3 * (k - 1));
    block(u0, u0 + sgn * 0.3, 0.15 - 0.2 * k);
  }
}

// ---------------------------------------------------------------- 屋顶

function addRoofDetails(env, h, sag) {
  const { THREE, HOUSE, rng, mossParts } = env;
  const r = rng(`${ZONE}-${h.id}-roof`);
  const rp = roofParams(HOUSE, h);
  const slopeFrame = (side) => houseFrame(THREE, h).multiply(new THREE.Matrix4().makeRotationY(side > 0 ? 0 : Math.PI));
  const W = h.width;
  if (r.chance(0.18)) addChimney(env, slopeFrame(r.pick([1, -1])), rp, sag, r.range(-W / 2 + 1, W / 2 - 1), r);
  if (W >= 10 && r.chance(0.14)) addDormer(env, slopeFrame(r.pick([1, -1])), rp, sag, r.range(-W / 2 + 1.6, W / 2 - 1.6), r);
  const patches = r.chance(0.7) ? r.int(1, 3) : 0;
  for (let i = 0; i < patches; i++) {
    const pw = Math.min(W - 1, r.range(1.6, 4.2)); const span = r.range(0.25, 0.5);
    const x0 = r.range(-W / 2 + 0.5, W / 2 - 0.5 - pw); const s0 = r.range(0.08, 0.95 - span);
    const g = mossPatch(THREE, rp, sag, x0, x0 + pw, s0, s0 + span, r.int(0, 3));
    mossParts.push(g.applyMatrix4(slopeFrame(r.pick([1, -1]))));
  }
}

function mossPatch(THREE, rp, sag, xa, xb, sa, sb, cell) {
  const nx = Math.max(2, Math.ceil((xb - xa) / 0.1)); const ns = 6;
  const pos = []; const uv = []; const idx = [];
  const ou = (cell % 2) * 0.5; const ov = 0.5 - Math.floor(cell / 2) * 0.5;
  for (let j = 0; j <= ns; j++) {
    for (let i = 0; i <= nx; i++) {
      const x = xa + ((xb - xa) * i) / nx; const s = sa + ((sb - sa) * j) / ns;
      pos.push(...roofPoint(rp, sag, x, s, 0.025));
      uv.push(ou + (0.5 * i) / nx, ov + 0.5 - (0.5 * j) / ns);
    }
  }
  for (let j = 0; j < ns; j++) {
    for (let i = 0; i < nx; i++) {
      const a = j * (nx + 1) + i; const b = a + 1; const c = a + nx + 1; const d = c + 1;
      idx.push(a, c, b, b, c, d);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

// 灶间烟囱：粉墙砌的方墩 + 瓦帽，根部埋进屋面
function addChimney({ geom, M, details }, F, rp, sag, x, r) {
  const s = r.range(0.12, 0.3);
  const [, yR, z] = roofPoint(rp, sag, x, s, -TILE_DEPTH);
  const hgt = r.range(0.8, 1.1);
  put(details, geom.boxM(0.46, hgt + 0.5, 0.46), M.wall, F, { x, y: yR - 0.5 + (hgt + 0.5) / 2, z }, geom.place);
  put(details, geom.boxM(0.5, 0.18, 0.5), M.tileRidge, F, { x, y: yR + hgt - 0.15, z }, geom.place); // 熏黑的一圈
  put(details, geom.boxM(0.66, 0.07, 0.66), M.tileRidge, F, { x, y: yR + hgt + 0.1, z }, geom.place);
  put(details, geom.boxM(0.3, 0.12, 0.3), M.tileRidge, F, { x, y: yR + hgt + 0.2, z }, geom.place);
}

// 老虎窗：前墙 + 两侧墙埋进屋面，小双坡顶顺着坡向
function addDormer({ THREE, geom, M, details }, F, rp, sag, x, r) {
  const s = r.range(0.42, 0.55);
  const [, yR, z] = roofPoint(rp, sag, x, s, -TILE_DEPTH);
  const wallH = 0.85; const base = yR - 0.12; const top = base + wallH;
  put(details, geom.boxM(1.1, wallH, 0.08), M.wall, F, { x, y: base + wallH / 2, z }, geom.place);
  for (const sx of [-1, 1]) {
    put(details, geom.boxM(0.08, wallH, 1.8), M.wall, F, { x: x + sx * 0.51, y: base + wallH / 2, z: z - 0.9 }, geom.place);
  }
  const lit = r.chance(0.4);
  put(details, geom.boxM(0.6, 0.42, 0.03), lit ? M.interiorGlow : M.darkInterior, F, { x, y: base + 0.45, z: z + 0.045 }, geom.place);
  for (const [w, hh, dx, dy] of [[0.68, 0.05, 0, 0.23], [0.68, 0.05, 0, -0.23], [0.05, 0.46, -0.32, 0], [0.05, 0.46, 0.32, 0], [0.03, 0.42, 0, 0]]) {
    put(details, geom.boxM(w, hh, 0.04), M.woodDark, F, { x: x + dx, y: base + 0.45 + dy, z: z + 0.06 }, geom.place);
  }
  const ang = 0.5; const slab = 0.78; const ridgeY = top + Math.sin(ang) * slab * 0.92;
  const len = 2.5; const zc = z + 0.22 - len / 2;
  for (const sx of [-1, 1]) {
    put(details, geom.boxM(slab, 0.05, len), M.tile, F,
      { x: x + sx * (Math.cos(ang) * slab) / 2, y: ridgeY - (Math.sin(ang) * slab) / 2, z: zc, rz: -sx * ang }, geom.place);
  }
  put(details, geom.boxM(0.1, 0.09, len), M.tileRidge, F, { x, y: ridgeY + 0.02, z: zc }, geom.place);
  const tri = new THREE.Shape();
  tri.moveTo(-0.6, 0); tri.lineTo(0.6, 0); tri.lineTo(0, ridgeY - top - 0.02); tri.closePath();
  const gable = new THREE.ExtrudeGeometry(tri, { depth: 0.06, bevelEnabled: false });
  put(details, gable, M.wall, F, { x, y: top - 0.01, z: z - 0.03 }, geom.place);
}

// ---------------------------------------------------------------- 灯笼

function lanternGeometries(THREE, geom) {
  const { a, b, phi, yc } = LAN;
  const prof = [];
  for (let i = 0; i <= 12; i++) {
    const p = -phi + (2 * phi * i) / 12;
    prof.push(new THREE.Vector2(a * Math.cos(p), yc + b * Math.sin(p)));
  }
  const body = new THREE.LatheGeometry(prof, 18);

  const frameParts = [
    geom.place(new THREE.CylinderGeometry(0.07, 0.085, 0.05, 12), { y: -0.025 }),
    geom.place(new THREE.CylinderGeometry(0.085, 0.07, 0.05, 12), { y: LAN.bottom - 0.02 }),
    geom.place(new THREE.TorusGeometry(0.02, 0.005, 4, 8), { y: 0.012 }),
  ];
  for (let k = 0; k < 8; k++) { // 竹篾骨
    const ang = (k / 8) * Math.PI * 2;
    const pts = prof.map((p) => new THREE.Vector3(Math.cos(ang) * p.x * 1.015, p.y, Math.sin(ang) * p.x * 1.015));
    frameParts.push(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 12, 0.0045, 3, false));
  }
  const frame = mergeClean(frameParts);

  const tassel = mergeClean([
    geom.place(new THREE.SphereGeometry(0.024, 8, 6), { y: LAN.bottom - 0.065 }),
    geom.place(new THREE.CylinderGeometry(0.012, 0.034, 0.2, 8, 1, true), { y: LAN.bottom - 0.19 }),
  ]);
  const cord = geom.place(new THREE.CylinderGeometry(0.006, 0.006, 1, 4, 1, true), { y: -0.5 });
  return { body, frame, tassel, cord };
}

function mergeClean(geoms) {
  return mergeGeometries(geoms.map((g) => {
    const n = g.index ? g.toNonIndexed() : g;
    for (const k of Object.keys(n.attributes)) if (!['position', 'normal', 'uv'].includes(k)) n.deleteAttribute(k);
    return n;
  }), false);
}

function buildLanternRig({ THREE, M, own, geom, lanterns }) {
  const g = lanternGeometries(THREE, geom);
  const n = lanterns.length;
  const mk = (geo, mat, name) => {
    const m = new THREE.InstancedMesh(geo, mat, n);
    m.name = `${ZONE}-lantern-${name}`;
    m.castShadow = false; m.receiveShadow = false;
    return m;
  };
  const meshes = [mk(g.body, M.lantern, 'body'), mk(g.frame, M.lanternFrame, 'frame'),
    mk(g.tassel, own.tassel, 'tassel'), mk(g.cord, M.lanternFrame, 'cord')];
  rig = {
    lanterns: lanterns.map((l) => ({ ...l, pivot: new THREE.Vector3(l.pivot.x, l.pivot.y, l.pivot.z) })),
    meshes,
    tmp: { e: new THREE.Euler(), q: new THREE.Quaternion(), one: new THREE.Vector3(1, 1, 1), base: new THREE.Matrix4(), m: new THREE.Matrix4() },
  };
  const group = new THREE.Group();
  group.name = `${ZONE}-lanterns`;
  meshes.forEach((m) => group.add(m));
  return group;
}

function countStats(root) {
  let drawCalls = 0; let triangles = 0; let lanternCount = 0;
  root.traverse((o) => {
    if (!o.isMesh) return;
    drawCalls += 1;
    const tri = (o.geometry.index ? o.geometry.index.count : o.geometry.attributes.position.count) / 3;
    triangles += tri * (o.isInstancedMesh ? o.count : 1);
    if (o.isInstancedMesh) lanternCount = o.count;
  });
  return { drawCalls, triangles: Math.round(triangles), lanterns: lanternCount };
}
