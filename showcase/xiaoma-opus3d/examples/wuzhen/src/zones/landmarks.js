// 地标区块：染坊（作坊、晒布架、蓝印花布）、白莲塔、柳树与香樟、远景民居群。
// 布条和柳条的摆动在顶点着色器里算，只由 uTime = t 决定；update(t) 只写 uniform。
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { sunDirection } from '../lighting.js';

const ZONE = 'landmarks';
const TAU = Math.PI * 2;
const V3 = THREE.Vector3;
const WIND = new THREE.Vector2(0.6, 0.8); // 风吹向（x, z），布条和柳条共用
const lerp = (a, b, k) => a + (b - a) * k;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

// ---------- 共享 uniform ----------
const U = {
  uTime: { value: 0 },
  uSunDir: { value: new V3(-1, 0.1, 0) },
  uSunCol: { value: new THREE.Color(0, 0, 0) },
  uWind: { value: WIND.clone() },
};
let sunLight = null;
const HERO = {}; // 特写柳枝梢：treeId → { rest, s, phase, amp }

// ---------- 动画着色器 ----------
// 布条：aCloth = (横向 u 米, 距杆顶 s 米（<=0 为搭在杆上的部分）, 相位, 布长)
const GLSL_CLOTH = /* glsl */`
uniform float uTime;
attribute vec4 aCloth;
vec3 clothAt(float u, float s) {
  if (s <= 0.0) return vec3(0.0);
  float ph = aCloth.z; float L = aCloth.w; float t = uTime;
  float k = s / L;
  float pin = smoothstep(0.0, 0.3, s);
  float gust = 0.6 + 0.4 * sin(0.27 * t + 0.4 * ph) * sin(0.71 * t + 1.3 + 0.25 * ph);
  float lean = 0.13 * gust * s * k;
  float wave = 0.24 * sin(1.6 * t - 1.0 * s + ph) + 0.09 * sin(2.7 * t - 2.2 * s + 1.7 * ph + 1.9 * u);
  float dz = lean + wave * pow(k, 1.4) * (0.5 + 0.5 * gust);
  dz += 0.035 * sin(20.0 * u + 3.0 * ph + 0.8 * sin(0.9 * t + 0.8 * s)) * (0.2 + 0.8 * k);
  dz += 0.05 * sin(5.0 * u - 2.4 * t + 1.6 * s + ph) * k * k;
  float dx = 0.07 * k * k * sin(1.2 * t + 1.7 * ph + 0.6 * s);
  float dy = 0.45 * dz * dz / max(s, 0.3);
  return vec3(dx, dy, dz) * pin;
}
vec3 clothDisp() { return clothAt(aCloth.x, aCloth.y); }
vec3 clothNormal(vec3 n0) {
  if (aCloth.y <= 0.0) return n0;
  float e = 0.03; vec3 p = clothAt(aCloth.x, aCloth.y);
  vec3 tu = vec3(e, 0.0, 0.0) + clothAt(aCloth.x + e, aCloth.y) - p;
  vec3 ts = vec3(0.0, -e, 0.0) + clothAt(aCloth.x, aCloth.y + e) - p;
  return normalize(cross(ts, tu));
}
`;

// 柳条：aSway = (距挂点 s 米, 相位, 幅度)；与下面的 willowAt() 是同一个公式
const GLSL_WILLOW = /* glsl */`
uniform float uTime;
uniform vec2 uWind;
attribute vec3 aSway;
vec3 willowAt(float s, float ph, float amp) {
  float t = uTime;
  float f = pow(max(s, 0.0), 1.2) * amp;
  float g = 0.6 + 0.4 * sin(0.31 * t + ph * 0.37);
  float a = 0.07 * g + 0.05 * sin(0.9 * t + ph) + 0.02 * sin(2.3 * t + 1.7 * ph + 1.3 * s);
  float b = 0.035 * sin(0.7 * t + 2.1 * ph) + 0.015 * sin(2.9 * t + ph + 2.0 * s);
  vec2 d = (uWind * a + vec2(-uWind.y, uWind.x) * b) * f;
  return vec3(d.x, 0.5 * dot(d, d) / max(s, 0.3), d.y);
}
vec3 willowDisp() { return willowAt(aSway.x, aSway.y, aSway.z); }
#ifdef LEAF_GROW
attribute vec3 aLeaf;
#endif
`;

function willowAt(s, ph, amp, t) {
  const f = Math.pow(Math.max(s, 0), 1.2) * amp;
  const g = 0.6 + 0.4 * Math.sin(0.31 * t + ph * 0.37);
  const a = 0.07 * g + 0.05 * Math.sin(0.9 * t + ph) + 0.02 * Math.sin(2.3 * t + 1.7 * ph + 1.3 * s);
  const b = 0.035 * Math.sin(0.7 * t + 2.1 * ph) + 0.015 * Math.sin(2.9 * t + ph + 2.0 * s);
  const x = (WIND.x * a - WIND.y * b) * f; const z = (WIND.y * a + WIND.x * b) * f;
  return { x, y: (0.5 * (x * x + z * z)) / Math.max(s, 0.3), z };
}

// 背光透射：太阳在叶片/布背后时，按阴影图判断这片是否真被晒到，透出暖光
const TRANS_VS = /* glsl */`
#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
  vSunCoord = directionalShadowMatrix[ 0 ] * vec4( worldPosition.xyz + uSunDir * 0.3, 1.0 );
#endif
`;
const TRANS_FS_HEAD = 'uniform vec3 uSunDir;\nuniform vec3 uSunCol;\nuniform float uTransK;\nvarying vec4 vSunCoord;';
const TRANS_FS = /* glsl */`
{
  vec3 Lv = normalize( ( viewMatrix * vec4( uSunDir, 0.0 ) ).xyz );
  vec3 Vv = normalize( vViewPosition );
  float back = max( -dot( normal, Lv ), 0.0 );
  float fwd = pow( max( dot( -Vv, Lv ), 0.0 ), 5.0 );
  float lit = 1.0;
  #if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
    lit = getShadow( directionalShadowMap[ 0 ], directionalLightShadows[ 0 ].shadowMapSize, directionalLightShadows[ 0 ].shadowIntensity,
      directionalLightShadows[ 0 ].shadowBias, directionalLightShadows[ 0 ].shadowRadius, vSunCoord );
  #endif
  outgoingLight += diffuseColor.rgb * vec3( 1.15, 1.08, 0.6 ) * uSunCol * uTransK * lit * ( 0.3 * back + fwd * ( 0.3 + 0.7 * back ) );
}
`;

// 远处的叶片按相机距离放大（15m 内为真实尺寸），让远看的树冠覆盖率不随距离掉光；阴影 pass 不放大
const LEAF_GROW_VS = `
#ifdef LEAF_GROW
  vec3 leafBase = position - aLeaf;
  float leafK = clamp( distance( ( modelMatrix * vec4( leafBase, 1.0 ) ).xyz, cameraPosition ) / 15.0, 1.0, 12.0 );
  transformed += aLeaf * ( leafK - 1.0 );
#endif
`;
// alpha 随 mip 级别放大，远处细叶不会被 alphaTest 整片裁掉
const ALPHA_MIP_FS = (w, h) => `
#ifdef USE_MAP
{
  vec2 mdx = dFdx( vMapUv * vec2( ${w}.0, ${h}.0 ) ); vec2 mdy = dFdy( vMapUv * vec2( ${w}.0, ${h}.0 ) );
  diffuseColor.a *= 1.0 + max( 0.0, 0.5 * log2( max( dot( mdx, mdx ), dot( mdy, mdy ) ) ) ) * 0.35;
}
#endif
#include <alphatest_fragment>`;

function animate(mat, kind, trans = 0, grow = false) {
  const head = kind === 'cloth' ? GLSL_CLOTH : GLSL_WILLOW;
  mat.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, U, { uTransK: { value: trans } });
    let vs = sh.vertexShader
      .replace('#include <common>', `#include <common>\n${head}`)
      .replace('#include <begin_vertex>', `vec3 transformed = position + ${kind}Disp();${grow ? LEAF_GROW_VS : ''}`);
    if (kind === 'cloth') {
      vs = vs.replace('#include <beginnormal_vertex>', '#include <beginnormal_vertex>\nobjectNormal = clothNormal(objectNormal);');
    }
    if (trans > 0) {
      vs = vs.replace('#include <common>', '#include <common>\nuniform vec3 uSunDir;\nvarying vec4 vSunCoord;')
        .replace('#include <shadowmap_vertex>', `#include <shadowmap_vertex>\n${TRANS_VS}`);
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <common>', `#include <common>\n${TRANS_FS_HEAD}`)
        .replace('#include <opaque_fragment>', `${TRANS_FS}\n#include <opaque_fragment>`);
    }
    if (grow) {
      vs = `#define LEAF_GROW\n${vs}`;
      sh.fragmentShader = sh.fragmentShader.replace('#include <alphatest_fragment>', ALPHA_MIP_FS(64, 256));
    }
    sh.vertexShader = vs;
  };
  mat.customProgramCacheKey = () => `${ZONE}-${kind}-${trans}-${grow}`;
  return mat;
}

function animatedMesh(geom, mat, kind, { trans = 0, map = null, grow = false } = {}) {
  const mesh = new THREE.Mesh(geom, animate(mat, kind, trans, grow));
  mesh.customDepthMaterial = animate(new THREE.MeshDepthMaterial({
    depthPacking: THREE.RGBADepthPacking, map, alphaTest: map ? 0.5 : 0, side: THREE.DoubleSide,
  }), kind);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

// ---------- 几何累加器（大量小件直接写进同一份数组，最后一次成网格） ----------
function newBatch(extra = {}) {
  return { p: [], n: [], uv: [], i: [], c: 0, ex: Object.fromEntries(Object.entries(extra).map(([k, s]) => [k, { s, a: [] }])) };
}
function vtx(b, p, n, u, v, ex) {
  b.p.push(p.x, p.y, p.z); b.n.push(n.x, n.y, n.z); b.uv.push(u, v);
  if (ex) for (const k in ex) b.ex[k].a.push(...ex[k]);
  return b.c++;
}
function toGeom(b) {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(b.p, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(b.n, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(b.uv, 2));
  for (const [k, { s, a }] of Object.entries(b.ex)) g.setAttribute(k, new THREE.Float32BufferAttribute(a, s));
  g.setIndex(b.i);
  g.computeBoundingSphere();
  return g;
}

// 沿折线的圆管（平行移动标架），UV 以米计。exFn(i, s) 给每一环的附加属性
function tubeInto(b, pts, radii, radial, exFn) {
  const n = pts.length; const ss = [0];
  for (let i = 1; i < n; i++) ss.push(ss[i - 1] + pts[i].distanceTo(pts[i - 1]));
  const base = b.c; let N = null; const t = new V3(); const B = new V3(); const d = new V3(); const q = new V3();
  for (let i = 0; i < n; i++) {
    t.subVectors(pts[Math.min(i + 1, n - 1)], pts[Math.max(i - 1, 0)]).normalize();
    if (!N) N = new V3().crossVectors(Math.abs(t.y) < 0.9 ? new V3(0, 1, 0) : new V3(1, 0, 0), t).normalize();
    else N.addScaledVector(t, -N.dot(t)).normalize();
    B.crossVectors(t, N);
    const ex = exFn ? exFn(i, ss[i]) : null;
    for (let k = 0; k <= radial; k++) {
      const a = (k / radial) * TAU;
      d.copy(N).multiplyScalar(Math.cos(a)).addScaledVector(B, Math.sin(a));
      vtx(b, q.copy(pts[i]).addScaledVector(d, radii[i]), d, (k / radial) * TAU * radii[0], ss[i], ex);
    }
  }
  for (let i = 0; i < n - 1; i++) {
    for (let k = 0; k < radial; k++) {
      const a = base + i * (radial + 1) + k; const c = a + radial + 1;
      b.i.push(a, a + 1, c, a + 1, c + 1, c);
    }
  }
  return ss;
}

// 带米制 UV 的八角/圆柱
function cylM(rt, rb, h, seg = 8, open = false, theta = Math.PI / 8) {
  const g = new THREE.CylinderGeometry(rt, rb, h, seg, 1, open, theta);
  const uv = g.attributes.uv; const circ = Math.PI * (rt + rb);
  for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * circ, uv.getY(i) * h);
  return g;
}

// ---------- Canvas 纹理 ----------
function canvasTex(w, h, metersW, metersH, draw, { color = true, wrap = true } = {}) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  if (wrap) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1 / metersW, 1 / metersH); }
  t.colorSpace = color ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  t.anisotropy = 8;
  return t;
}

function speckle(g, w, h, r, count, aMax, colors) {
  for (let i = 0; i < count; i++) {
    g.globalAlpha = r.range(0.02, aMax); g.fillStyle = r.pick(colors);
    const s = r.range(1, 3); g.fillRect(r.range(0, w), r.range(0, h), s, s);
  }
  g.globalAlpha = 1;
}

// 蓝印花布：与 materials.js 的 cloth 同一套纹样（六瓣团花 + 点线边），但 1024px/米，经得起特写；加了布纹和冰裂纹
function drawBluePrint(g, w, h) {
  const r = rng(`${ZONE}-tex-cloth`);
  g.fillStyle = '#1d3a6c'; g.fillRect(0, 0, w, h);
  for (let y = 0; y < h; y += 3) { g.fillStyle = `rgba(10,22,45,${r.range(0.04, 0.12)})`; g.fillRect(0, y, w, 1); }
  for (let x = 0; x < w; x += 3) { g.fillStyle = `rgba(60,90,140,${r.range(0.02, 0.08)})`; g.fillRect(x, 0, 1, h); }
  const n = 4; const cell = w / n;
  for (let j = 0; j < n; j++) {
    for (let i = -1; i <= n; i++) {
      const cx = (i + 0.5) * cell + (j % 2 ? cell / 2 : 0); const cy = (j + 0.5) * cell;
      g.fillStyle = '#e4e8ec';
      for (let p = 0; p < 6; p++) {
        const a = (p / 6) * TAU;
        g.beginPath();
        g.ellipse(cx + Math.cos(a) * cell * 0.16, cy + Math.sin(a) * cell * 0.16, cell * 0.09, cell * 0.05, a, 0, TAU);
        g.fill();
      }
      g.beginPath(); g.arc(cx, cy, cell * 0.05, 0, TAU); g.fill();
      g.fillStyle = '#1d3a6c'; g.beginPath(); g.arc(cx, cy, cell * 0.018, 0, TAU); g.fill(); // 花心留蓝点
      g.fillStyle = '#dfe4ea'; // 团花之间的小点
      for (let p = 0; p < 4; p++) {
        const a = (p / 4) * TAU + Math.PI / 4;
        g.beginPath(); g.arc(cx + Math.cos(a) * cell * 0.36, cy + Math.sin(a) * cell * 0.36, cell * 0.018, 0, TAU); g.fill();
      }
    }
  }
  g.fillStyle = '#e4e8ec';
  for (let x = 0; x < w; x += 40) { g.beginPath(); g.arc(x, 24, 8, 0, TAU); g.arc(x + 20, h - 24, 8, 0, TAU); g.fill(); }
  // 冰裂纹：靛蓝底上的浅色细裂
  g.strokeStyle = 'rgba(120,150,195,0.22)'; g.lineWidth = 1.2;
  for (let k = 0; k < 120; k++) {
    let x = r.range(0, w); let y = r.range(0, h); g.beginPath(); g.moveTo(x, y);
    for (let s = 0; s < 4; s++) { x += r.range(-30, 30); y += r.range(-30, 30); g.lineTo(x, y); }
    g.stroke();
  }
  speckle(g, w, h, r, 12000, 0.2, ['#132849', '#3a5a8f', '#c9d2dc']);
}

// 素布纹理（灰度，颜色由材质 color 给）
function drawWeave(g, w, h) {
  const r = rng(`${ZONE}-tex-weave`);
  g.fillStyle = '#e8e8e8'; g.fillRect(0, 0, w, h);
  for (let y = 0; y < h; y += 2) { g.fillStyle = `rgba(0,0,0,${r.range(0.02, 0.08)})`; g.fillRect(0, y, w, 1); }
  for (let x = 0; x < w; x += 2) { g.fillStyle = `rgba(0,0,0,${r.range(0.01, 0.06)})`; g.fillRect(x, 0, 1, h); }
  speckle(g, w, h, r, 3000, 0.15, ['#9a9a9a', '#ffffff']);
}

// 竹竿：0.45m 一节，节处一道暗环一道亮环
function drawBamboo(g, w, h) {
  const r = rng(`${ZONE}-tex-bamboo`);
  g.fillStyle = '#9a8a62'; g.fillRect(0, 0, w, h);
  for (let x = 0; x < w; x += 2) { g.fillStyle = `rgba(60,50,30,${r.range(0.03, 0.15)})`; g.fillRect(x, 0, 1, h); }
  g.fillStyle = 'rgba(55,45,28,0.75)'; g.fillRect(0, 0, w, 4);
  g.fillStyle = 'rgba(210,200,165,0.5)'; g.fillRect(0, 4, w, 3);
  const grd = g.createLinearGradient(0, 0, 0, h);
  grd.addColorStop(0, 'rgba(60,50,30,0.25)'); grd.addColorStop(0.2, 'rgba(60,50,30,0)'); grd.addColorStop(1, 'rgba(60,50,30,0.15)');
  g.fillStyle = grd; g.fillRect(0, 0, w, h);
  speckle(g, w, h, r, 600, 0.3, ['#4b4030', '#c8bc98']);
}

// 柳叶：狭长披针形，灰度 + alpha，颜色走顶点色。v=0 叶柄，v=1 叶尖
function drawWillowLeaf(g, w, h) {
  g.clearRect(0, 0, w, h);
  const half = (v) => 0.47 * w * Math.pow(Math.sin(Math.PI * Math.pow(v, 0.8)), 0.85);
  const Y = (v) => h * (1 - v);
  g.beginPath(); g.moveTo(w / 2, Y(0));
  for (let k = 1; k <= 40; k++) { const v = 0.04 + (0.96 * k) / 40; g.lineTo(w / 2 + half(v), Y(v)); }
  for (let k = 40; k >= 0; k--) { const v = 0.04 + (0.96 * k) / 40; g.lineTo(w / 2 - half(v), Y(v)); }
  g.closePath();
  const grd = g.createLinearGradient(0, 0, w, 0);
  grd.addColorStop(0, '#9c9c9c'); grd.addColorStop(0.45, '#d6d6d6'); grd.addColorStop(0.5, '#f0f0f0');
  grd.addColorStop(0.55, '#d0d0d0'); grd.addColorStop(1, '#949494');
  g.fillStyle = grd; g.fill();
  g.strokeStyle = 'rgba(255,255,255,0.55)'; g.lineWidth = 1.5; // 中脉
  g.beginPath(); g.moveTo(w / 2, Y(0)); g.lineTo(w / 2, Y(0.97)); g.stroke();
  g.strokeStyle = 'rgba(255,255,255,0.22)'; g.lineWidth = 0.8; // 侧脉
  for (let v = 0.12; v < 0.9; v += 0.06) {
    for (const sd of [-1, 1]) { g.beginPath(); g.moveTo(w / 2, Y(v)); g.lineTo(w / 2 + sd * half(v + 0.05) * 0.9, Y(v + 0.07)); g.stroke(); }
  }
  g.fillStyle = '#8a8a8a'; g.fillRect(w / 2 - 1.5, Y(0.05), 3, h * 0.05); // 叶柄
}

// 香樟叶簇：一根小枝上的十来片椭圆叶
function drawCamphorSpray(g, w, h) {
  const r = rng(`${ZONE}-tex-camphor`);
  g.clearRect(0, 0, w, h);
  g.strokeStyle = '#555'; g.lineWidth = 3;
  g.beginPath(); g.moveTo(w * 0.5, h * 0.98); g.quadraticCurveTo(w * 0.45, h * 0.5, w * 0.52, h * 0.1); g.stroke();
  for (let k = 0; k < 13; k++) {
    const v = 0.15 + 0.8 * (k / 13); const x = w * (0.5 - 0.03 * Math.sin(v * 3)); const y = h * (1 - v);
    const a = (k % 2 ? 1 : -1) * r.range(0.5, 1.1) - Math.PI / 2;
    const L = w * r.range(0.16, 0.22);
    const cx = x + Math.cos(a) * L * 0.55; const cy = y + Math.sin(a) * L * 0.55;
    const tone = Math.round(r.range(150, 225));
    g.fillStyle = `rgb(${tone},${tone},${tone})`;
    g.beginPath(); g.ellipse(cx, cy, L * 0.55, L * 0.24, a, 0, TAU); g.fill();
    g.strokeStyle = 'rgba(255,255,255,0.35)'; g.lineWidth = 1;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * L * 1.05, y + Math.sin(a) * L * 1.05); g.stroke();
  }
}

let rng = null; // build 时从 ctx 取

// ---------- 染坊 ----------
function buildDyeYard(ctx, group, own) {
  const { layout, materials: M, geom } = ctx;
  const D = layout.dyeYard; const W = D.workshop; const R = D.racks;
  const ROT = { S: 0, E: Math.PI / 2, N: Math.PI, W: -Math.PI / 2 };

  // 作坊：一栋朝北的长屋，记录字段照 layout.houses
  const width = W.x1 - W.x0; const depth = W.z1 - W.z0;
  const rec = {
    id: 'DYE', row: 'DYE', zone: 'landmarks', x: (W.x0 + W.x1) / 2, z: (W.z0 + W.z1) / 2,
    width, depth, bays: Math.round(width / layout.BAY), floors: 1, eaveHeight: 4.4,
    facing: 'N', rotY: ROT.N, waterSide: null, gable: 'horse', shop: true, detail: 'high',
    waterPavilion: null, footprint: { ...W },
  };
  group.add(ctx.buildHouse(rec, { materials: M, rng }));

  // 晒布架：每排沿 X，竖杆 + 顶部横杆，排与排之间顶部和下部有拉杆
  const r = rng(`${ZONE}-dye-racks`);
  const parts = [];
  const pole = 0.07; const barR = 0.055; const top = R.height;
  const rowZ = Array.from({ length: R.rows }, (_, i) => R.z0 + ((i + 0.5) * (R.z1 - R.z0)) / R.rows);
  const nPoles = Math.round((R.x1 - R.x0) / 4.2);
  const poleX = Array.from({ length: nPoles + 1 }, (_, k) => R.x0 + (k * (R.x1 - R.x0)) / nPoles);
  const bamboo = (len, rad) => cylM(rad, rad * 1.05, len, 8, true, 0);
  for (const z of rowZ) {
    for (const x of poleX) {
      parts.push({ geom: geom.place(bamboo(top + 0.7, pole), { x, y: (top + 0.7) / 2 - 0.3, z }), mat: own.bamboo });
      parts.push({ geom: geom.place(cylM(0.1, 0.1, 0.16, 8), { x, y: top, z }), mat: own.rope }); // 绑扎
      parts.push({ geom: geom.place(geom.boxM(0.3, 0.2, 0.3), { x, y: 0.05, z }), mat: M.embankment }); // 柱础
    }
    parts.push({ geom: geom.place(bamboo(R.x1 - R.x0 + 0.8, barR), { x: (R.x0 + R.x1) / 2, y: top, z, rz: Math.PI / 2 }), mat: own.bamboo });
    // 两端斜撑
    for (const [x, sx] of [[R.x0, -1], [R.x1, 1]]) {
      const len = Math.hypot(2.2, top - 0.5);
      parts.push({ geom: geom.place(bamboo(len, 0.05), { x: x + sx * 1.1, y: (top - 0.5) / 2, z, rz: sx * Math.atan2(2.2, top - 0.5) }), mat: own.bamboo });
    }
  }
  const zSpan = rowZ[rowZ.length - 1] - rowZ[0] + 0.6;
  for (const x of poleX) {
    for (const y of [top - 0.18, 1.7]) {
      parts.push({ geom: geom.place(bamboo(zSpan, 0.045), { x, y, z: (rowZ[0] + rowZ[rowZ.length - 1]) / 2, rx: Math.PI / 2 }), mat: own.bamboo });
    }
  }

  // 布条
  const clothB = { print: [], indigo: [], light: [], white: [] };
  rowZ.forEach((z, row) => {
    for (let k = 0; k < nPoles; k++) {
      if (r.chance(0.08)) continue; // 偶尔空一档
      let x = poleX[k] + 0.3 + r.range(0, 0.15);
      while (true) {
        const w = r.range(0.85, 0.95);
        if (x + w > poleX[k + 1] - 0.3) break;
        const kind = r.chance(0.66) ? 'print' : r.pick(['indigo', 'light', 'white', 'white']);
        const L = r.range(4, 6);
        clothB[kind].push(clothStrip(x, z, top, barR, w, L, x * 0.17 + row * 1.3 + r.range(0, 0.6), r.chance(0.3) ? 0.62 : 1, r.range(0, 1)));
        x += w + r.range(0.1, 0.32);
      }
    }
  });
  for (const [kind, list] of Object.entries(clothB)) {
    if (!list.length) continue;
    const mesh = animatedMesh(mergeGeometries(list), own.cloth[kind], 'cloth', { trans: 0.35 });
    mesh.name = `cloth-${kind}`;
    group.add(mesh);
  }

  // 染缸（作坊前两排）
  const vatProfile = [[0, 0], [0.4, 0], [0.52, 0.12], [0.6, 0.4], [0.59, 0.7], [0.52, 0.85], [0.55, 0.9], [0.55, 0.95], [0.49, 0.95], [0.47, 0.8]]
    .map(([a, b]) => new THREE.Vector2(a, b));
  const vr = rng(`${ZONE}-dye-vats`);
  const vatXs = [13, 14.4, 15.8, 22.6, 24, 25.4, 26.8];
  vatXs.forEach((x, i) => {
    const z = i % 2 ? 61.4 : 62.7; const ry = vr.range(0, TAU);
    const lathe = new THREE.LatheGeometry(vatProfile, 20);
    parts.push({ geom: geom.place(lathe, { x, z, ry }), mat: own.vat });
    if (vr.chance(0.35)) {
      parts.push({ geom: geom.place(cylM(0.56, 0.56, 0.05, 20), { x, y: 0.98, z }), mat: M.wood });
    } else {
      parts.push({ geom: geom.place(new THREE.CircleGeometry(0.48, 20), { x, y: 0.82, z, rx: -Math.PI / 2 }), mat: own.dye });
      if (vr.chance(0.6)) { // 搅缸的竹竿
        const lean = vr.range(0.25, 0.4);
        parts.push({ geom: geom.place(bamboo(2.6, 0.025), { x: x + Math.sin(lean) * 1.1, y: 1.6, z, rz: -lean }), mat: own.bamboo });
      }
    }
  });

  // 竹竿堆：晒布架北侧，两只木架上码三层
  const px0 = 40; const pz = R.z0 - 2.2;
  for (const x of [px0 + 0.8, px0 + 6.2]) parts.push({ geom: geom.place(geom.boxM(0.14, 0.7, 1.4), { x, y: 0.35, z: pz }), mat: M.woodDark });
  [7, 6, 5].forEach((n, layer) => {
    for (let k = 0; k < n; k++) {
      const z = pz + (k - (n - 1) / 2) * 0.13; const y = 0.75 + layer * 0.11;
      parts.push({ geom: geom.place(bamboo(7, 0.055), { x: px0 + 3.5 + r.range(-0.2, 0.2), y, z, rz: Math.PI / 2 }), mat: own.bamboo });
    }
  });

  const g = geom.mergeByMaterial(parts);
  g.traverse((o) => { if (o.isMesh && o.material === own.rope) o.castShadow = false; });
  group.add(g);
}

// 一条布：背面短搭头 → 绕过横杆 → 正面垂下 L 米。世界坐标，法线朝 +Z
function clothStrip(x0, zBar, yBar, barR, w, L, phase, uvScale, uvOff) {
  const rb = barR + 0.012; const nu = 12;
  const path = []; // [y, z, s]
  for (let k = 0; k <= 3; k++) path.push([yBar - 0.3 + (0.3 * k) / 3, zBar - rb, -1]);
  for (let k = 1; k < 8; k++) { const a = Math.PI - (Math.PI * k) / 8; path.push([yBar + rb * Math.sin(a), zBar + rb * Math.cos(a), -1]); }
  const ns = Math.ceil(L / 0.12);
  for (let k = 0; k <= ns; k++) path.push([yBar - (L * k) / ns, zBar + rb, (L * k) / ns]);
  const pos = []; const uv = []; const cl = []; const idx = [];
  let acc = 0;
  path.forEach(([y, z, s], j) => {
    if (j) acc += Math.hypot(y - path[j - 1][0], z - path[j - 1][1]);
    for (let i = 0; i <= nu; i++) {
      const u = (w * i) / nu;
      pos.push(x0 + u, y, z); uv.push(u * uvScale + uvOff, -acc * uvScale + uvOff); cl.push(u, s, phase, L);
    }
  });
  const row = nu + 1;
  for (let j = 0; j < path.length - 1; j++) {
    for (let i = 0; i < nu; i++) { const a = j * row + i; const c = a + row; idx.push(a, c, a + 1, a + 1, c, c + 1); }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setAttribute('aCloth', new THREE.Float32BufferAttribute(cl, 4));
  g.setIndex(idx);
  g.computeVertexNormals();
  // 正面法线应朝 +Z（与着色器里重算的法线一致）
  if (g.attributes.normal.getZ(g.attributes.normal.count - 1) < 0) {
    for (let k = 0; k < idx.length; k += 3) { const t = idx[k + 1]; idx[k + 1] = idx[k + 2]; idx[k + 2] = t; }
    g.setIndex(idx); g.computeVertexNormals();
  }
  return g;
}

// ---------- 树 ----------
function nearestWater(x, z, rivers) {
  let best = null;
  for (const rv of rivers) {
    const R = rv.rect; const dx = clamp(x, R.x0, R.x1) - x; const dz = clamp(z, R.z0, R.z1) - z;
    const d = Math.hypot(dx, dz);
    if (!best || d < best.d) best = { d, dx, dz };
  }
  const len = best.d || 1;
  return new THREE.Vector2(best.dx / len, best.dz / len);
}
const overWater = (x, z, rivers) => rivers.some(({ rect: R }) => x > R.x0 && x < R.x1 && z > R.z0 && z < R.z1);

// 一根曲枝：起点、方向、长度、末端下垂量
function limbPts(start, dir, len, droop, n, wob = 0, r = null) {
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const s = (len * i) / n; const k = i / n;
    const p = start.clone().addScaledVector(dir, s);
    p.y -= droop * k * k;
    if (wob && r && i > 0 && i < n) { p.x += r.range(-wob, wob); p.y += r.range(-wob, wob) * 0.5; p.z += r.range(-wob, wob); }
    pts.push(p);
  }
  return pts;
}
const along = (pts, f) => { const x = f * (pts.length - 1); const i = Math.min(pts.length - 2, Math.floor(x)); return pts[i].clone().lerp(pts[i + 1], x - i); };

const WILLOW_GREENS = ['#8ba65a', '#7e9a4e', '#93ad5e', '#a3b866', '#76924a', '#86a052'].map((c) => new THREE.Color(c));
const WILLOW_TIP = new THREE.Color('#b4c473');

function buildWillow(t, layout, B, heroWanted) {
  const r = rng(`${ZONE}-${t.id}`);
  const rivers = layout.rivers;
  const lean = nearestWater(t.x, t.z, rivers); const leanAz = Math.atan2(lean.y, lean.x);
  const H = r.range(3.2, 4.1); const leanAmt = r.range(0.9, 1.5); const sway = r.range(-0.4, 0.4);
  const trunk = []; const trunkR = [];
  for (let i = 0; i <= 6; i++) {
    const k = i / 6; const off = leanAmt * Math.pow(k, 1.6); const wob = sway * Math.sin(Math.PI * k);
    trunk.push(new V3(t.x + lean.x * off - lean.y * wob, -0.3 + (H + 0.3) * k, t.z + lean.y * off + lean.x * wob));
    trunkR.push(t.trunk * (1 + 0.4 * Math.pow(1 - k, 4)) * (1 - 0.4 * k));
  }
  tubeInto(B.bark, trunk, trunkR, 10);

  const phase0 = t.x * 0.11 + t.z * 0.07 + r.range(0, 0.5);
  const strands = [];
  const nL = r.int(4, 6);
  for (let l = 0; l < nL; l++) {
    const az = leanAz + (l / nL) * TAU + r.range(-0.4, 0.4);
    const facing = Math.cos(az - leanAz);
    const len = r.range(2.2, 3.1) * (1 + 0.4 * facing); const el = r.range(0.55, 1.0) + 0.25 * Math.max(0, -facing); // 背水一侧短而陡，不伸进民居
    const dir = new V3(Math.cos(el) * Math.cos(az), Math.sin(el), Math.cos(el) * Math.sin(az));
    const start = along(trunk, r.range(0.82, 0.95));
    const limb = limbPts(start, dir, len, 0.25 * len, 6, 0.08, r);
    tubeInto(B.bark, limb, limb.map((_, i) => lerp(0.15, 0.05, i / 6)), 7);
    const nS = r.int(5, 8);
    for (let s = 0; s < nS; s++) {
      const az2 = az + r.range(-0.9, 0.9); const el2 = r.range(-0.1, 0.5); const len2 = r.range(0.8, 1.8);
      const dir2 = new V3(Math.cos(el2) * Math.cos(az2), Math.sin(el2), Math.cos(el2) * Math.sin(az2));
      const sec = limbPts(along(limb, r.range(0.35, 1)), dir2, len2, 0.35 * len2, 4, 0.04, r);
      tubeInto(B.bark, sec, sec.map((_, i) => lerp(0.045, 0.012, i / 4)), 5);
      const hdir = new THREE.Vector2(dir2.x, dir2.z).normalize();
      const nStr = r.int(6, 9);
      for (let k = 0; k < nStr; k++) strands.push(strandSpec(along(sec, r.range(0.1, 1)), hdir, r, rivers, phase0));
    }
    const lh = new THREE.Vector2(dir.x, dir.z).normalize();
    for (let k = 0; k < 4; k++) strands.push(strandSpec(along(limb, r.range(0.5, 1)), lh, r, rivers, phase0));
  }

  // 特写枝：梢头在水面上方、高度合适、在全树最东边（镜头从东侧逆光看过去不被挡）
  let hero = null;
  if (heroWanted) {
    for (const s of strands) {
      s.tip = strandPts(s)[0];
      const ok = waterDepthInside(s.tip.x, s.tip.z, rivers) > 0.8 && s.tip.y > -0.3 && s.tip.y < 1.6;
      if (ok && (!hero || s.tip.x > hero.tip.x)) hero = s;
    }
    if (!hero) hero = strands.reduce((m, s) => (s.tip.x > m.tip.x ? s : m));
    hero.amp = 0.3; hero.hero = true;
  }

  for (const s of strands) emitStrand(s, B, r, heroWanted, t.id);
}

function strandSpec(a, hdir, r, rivers, phase0) {
  const wet = overWater(a.x, a.z, rivers);
  return { a, hdir: hdir.clone().rotateAround(new THREE.Vector2(), r.range(-0.6, 0.6)), e0: r.range(0.15, 1.0), bend: r.range(1.8, 3.4),
    yEnd: Math.min(a.y - 1.2, wet ? r.range(-0.6, 0.9) : r.range(0.6, 2.6)), phase: phase0 + r.range(0, 1.6), amp: 1, wig: r.range(0, TAU) };
}

// 点在河道里、离最近岸线多远（不在水上返回 0）
function waterDepthInside(x, z, rivers) {
  let best = 0;
  for (const { rect: R } of rivers) {
    if (x > R.x0 && x < R.x1 && z > R.z0 && z < R.z1) best = Math.max(best, Math.min(x - R.x0, R.x1 - x, z - R.z0, R.z1 - z));
  }
  return best;
}

// 柳条中心线（静止形状）：先斜向上拱出，在重力下弯垂，最后几乎竖直垂到 yEnd。返回 [tip, pts]
function strandPts(s) {
  const dir = new V3(s.hdir.x * Math.cos(s.e0), Math.sin(s.e0), s.hdir.y * Math.cos(s.e0));
  const p = s.a.clone(); const pts = [p.clone()]; let len = 0;
  while ((p.y > s.yEnd || len < 1.2) && len < 7) {
    const step = dir.y > -0.97 ? 0.14 : 0.45;
    dir.y -= step * s.bend; dir.normalize();
    p.addScaledVector(dir, step); len += step;
    const w = 0.012 * Math.sin(len * 2.1 + s.wig);
    pts.push(new V3(p.x - s.hdir.y * w, p.y, p.z + s.hdir.x * w));
  }
  return [pts[pts.length - 1], pts];
}

function emitStrand(s, B, r, fine, treeId) {
  const [, pts] = strandPts(s);
  const radial = fine ? 4 : 3;
  const ss = tubeInto(B.twig, pts, pts.map((_, i) => lerp(0.0055, 0.0022, i / (pts.length - 1))), radial,
    (i, sv) => ({ aSway: [sv, s.phase, s.amp] }));
  const L = ss[ss.length - 1];
  if (s.hero) HERO[treeId] = { rest: pts[pts.length - 1].clone(), s: L, phase: s.phase, amp: s.amp };

  // 叶：互生，螺旋排布，沿枝斜向下外伸
  const spacing = s.hero ? 0.04 : fine ? 0.055 : 0.1;
  const tng = new V3(); const R = new V3(); const A = new V3(); const S = new V3(); const N = new V3(); const P = new V3();
  let seg = 0; let k = 0;
  for (let sv = 0.06 + r.range(0, spacing); sv < L - 0.01; sv += spacing * r.range(0.8, 1.2), k++) {
    while (seg < ss.length - 2 && ss[seg + 1] < sv) seg++;
    const f = (sv - ss[seg]) / (ss[seg + 1] - ss[seg]);
    P.copy(pts[seg]).lerp(pts[seg + 1], f);
    tng.subVectors(pts[seg + 1], pts[seg]).normalize();
    const phi = k * 2.4 + r.range(-0.3, 0.3);
    R.set(Math.cos(phi), 0, Math.sin(phi));
    R.addScaledVector(tng, -R.dot(tng)).normalize();
    const tipK = clamp((sv - (L - 0.45)) / 0.45, 0, 1);
    const beta = lerp(r.range(0.35, 0.75), 0.25, tipK);
    A.copy(tng).multiplyScalar(Math.cos(beta)).addScaledVector(R, Math.sin(beta)).normalize();
    S.crossVectors(A, R).normalize().applyAxisAngle(A, r.range(-0.6, 0.6));
    N.crossVectors(S, A).normalize();
    const len = lerp(fine ? r.range(0.09, 0.13) : r.range(0.1, 0.14), r.range(0.045, 0.07), tipK);
    const col = r.chance(0.5 * tipK + 0.05) ? WILLOW_TIP : r.pick(WILLOW_GREENS);
    leafInto(B.leaf, P, A, S, N, len, len * 0.17, col, [sv, s.phase, s.amp], len * 0.6);
  }
  // 梢头收一片小叶
  P.copy(pts[pts.length - 1]); A.set(s.hdir.x * 0.2, -1, s.hdir.y * 0.2).normalize();
  S.set(-A.z, 0, A.x).normalize(); if (S.lengthSq() < 0.5) S.set(1, 0, 0); N.crossVectors(S, A).normalize();
  leafInto(B.leaf, P, A, S, N, 0.045, 0.008, WILLOW_TIP, [L, s.phase, s.amp], 0.03);
}

// 一片叶：沿中脉对折的 2×3 网格（4 个三角形），叶形靠贴图 alpha 裁出
function leafInto(b, P, A, S, N, len, wid, col, sway, dS) {
  const fold = wid * 0.22; const curl = len * 0.1;
  const base = b.c; const q = new V3();
  for (let v = 0; v <= 1; v++) {
    for (let c = -1; c <= 1; c++) {
      q.copy(P).addScaledVector(A, len * v).addScaledVector(S, (c * wid) / 2).addScaledVector(N, (c ? -fold : 0) - curl * v);
      vtx(b, q, N, (c + 1) / 2, v, { color: [col.r, col.g, col.b], aSway: [sway[0] + dS * v, sway[1], sway[2]], aLeaf: [q.x - P.x, q.y - P.y, q.z - P.z] });
    }
  }
  b.i.push(base, base + 1, base + 4, base, base + 4, base + 3, base + 1, base + 2, base + 5, base + 1, base + 5, base + 4);
}

const CAMPHOR_GREENS = ['#3e6536', '#456d3a', '#36592f', '#4b7240', '#3a5f34'].map((c) => new THREE.Color(c));

function buildCamphor(t, layout, B) {
  const r = rng(`${ZONE}-${t.id}`);
  const small = t.id === 'cNE';
  const rx = small ? 4.0 : 5.6; const ry = small ? 3.4 : 4.2;
  const toWater = nearestWater(t.x, t.z, layout.rivers);
  const shift = small ? 1.2 : 0.4;
  const C = new V3(t.x + toWater.x * shift, 2.6 + ry * 0.95 + 0.8, t.z + toWater.y * shift);
  const trunk = []; const tr = [];
  for (let i = 0; i <= 5; i++) {
    const k = i / 5;
    trunk.push(new V3(lerp(t.x, C.x, k * 0.4) + r.range(-0.08, 0.08) * (i % 5 ? 1 : 0), -0.3 + 3.1 * k, lerp(t.z, C.z, k * 0.4)));
    tr.push(t.trunk * (1 + 0.5 * Math.pow(1 - k, 5)) * (1 - 0.25 * k));
  }
  tubeInto(B.bark, trunk, tr, 12);
  const nL = r.int(5, 6);
  for (let l = 0; l < nL; l++) {
    const az = (l / nL) * TAU + r.range(-0.3, 0.3); const el = r.range(0.2, 0.8);
    const end = C.clone().add(new V3(Math.cos(az) * Math.cos(el) * rx * 0.6, Math.sin(el) * ry * 0.5, Math.sin(az) * Math.cos(el) * rx * 0.6));
    const start = along(trunk, r.range(0.75, 1));
    const dir = end.clone().sub(start); const len = dir.length(); dir.normalize();
    const limb = limbPts(start, dir, len, -0.6, 5, 0.15, r);
    tubeInto(B.bark, limb, limb.map((_, i) => lerp(0.3, 0.1, i / 5) * (small ? 0.85 : 1)), 8);
  }
  // 叶团：椭球壳上撒一圈抖动的二十面体，压暗下沿
  const nBlob = small ? 40 : 58; const tmp = new V3(); const nrm = new V3();
  const ico = new THREE.IcosahedronGeometry(1, 1); const ip = ico.attributes.position;
  for (let k = 0; k < nBlob; k++) {
    const u = new V3(r.range(-1, 1), r.range(-0.55, 1), r.range(-1, 1)); if (u.lengthSq() > 1 || u.lengthSq() < 0.05) { k--; continue; }
    u.normalize(); const rho = r.range(0.6, 0.95);
    const c = C.clone().add(new V3(u.x * rx * rho, u.y * ry * rho, u.z * rx * rho));
    const rad = r.range(1.3, 2.1) * (small ? 0.85 : 1); const seed = r.range(0, 100);
    const base = r.pick(CAMPHOR_GREENS);
    const b0 = B.blob.c;
    for (let i = 0; i < ip.count; i++) {
      nrm.fromBufferAttribute(ip, i).normalize();
      const j = 1 + 0.16 * Math.sin(12.9 * nrm.x + 78.2 * nrm.y + 37.7 * nrm.z + seed);
      tmp.copy(c).addScaledVector(nrm, rad * j);
      const shade = 0.55 + 0.45 * clamp((tmp.y - (C.y - ry)) / (2 * ry), 0, 1);
      vtx(B.blob, tmp, nrm, nrm.x, nrm.y, { color: [base.r * shade, base.g * shade, base.b * shade] });
    }
    for (let i = 0; i < ip.count; i++) B.blob.i.push(b0 + i);
    // 叶簇卡片：贴在叶团外表面，打破剪影
    for (let q = 0; q < 8; q++) {
      const d = new V3(r.range(-1, 1), r.range(-0.4, 1), r.range(-1, 1)).normalize();
      const p = c.clone().addScaledVector(d, rad * r.range(0.85, 1.05));
      const out = p.clone().sub(C).normalize().lerp(d, 0.5).normalize();
      const S = new V3().crossVectors(out, new V3(0, 1, 0)); if (S.lengthSq() < 1e-4) S.set(1, 0, 0); S.normalize().applyAxisAngle(out, r.range(0, TAU));
      const A = new V3().crossVectors(S, out).normalize();
      const size = r.range(0.7, 1.0); const shade = 0.7 + 0.3 * clamp((p.y - (C.y - ry)) / (2 * ry), 0, 1);
      const col = [base.r * shade * 1.1, base.g * shade * 1.1, base.b * shade * 1.1];
      const b1 = B.card.c;
      for (const [cu, cv] of [[0, 0], [1, 0], [1, 1], [0, 1]]) {
        tmp.copy(p).addScaledVector(S, (cu - 0.5) * size).addScaledVector(A, (cv - 0.5) * size);
        vtx(B.card, tmp, out, cu, cv, { color: col });
      }
      B.card.i.push(b1, b1 + 1, b1 + 2, b1, b1 + 2, b1 + 3);
    }
  }
}

function buildTrees(ctx, group, own) {
  const { layout, materials: M } = ctx;
  const B = {
    bark: newBatch(), twig: newBatch({ aSway: 3 }), leaf: newBatch({ color: 3, aSway: 3, aLeaf: 3 }),
    blob: newBatch({ color: 3 }), card: newBatch({ color: 3 }),
  };
  const heroIds = ['wNW4', 'wS3'];
  for (const t of layout.trees) {
    if (t.kind === 'willow') buildWillow(t, layout, B, heroIds.includes(t.id));
    else buildCamphor(t, layout, B);
  }
  const bark = new THREE.Mesh(toGeom(B.bark), M.bark); bark.castShadow = bark.receiveShadow = true; bark.name = 'tree-bark';
  const twig = animatedMesh(toGeom(B.twig), own.twig, 'willow'); twig.name = 'willow-twig';
  const leaf = animatedMesh(toGeom(B.leaf), own.willowLeaf, 'willow', { trans: 0.9, map: own.willowLeaf.map, grow: true }); leaf.name = 'willow-leaf';
  const blob = new THREE.Mesh(toGeom(B.blob), own.camphorBlob); blob.castShadow = blob.receiveShadow = true; blob.name = 'camphor-blob';
  const card = new THREE.Mesh(toGeom(B.card), own.camphorCard); card.castShadow = card.receiveShadow = true; card.name = 'camphor-card';
  group.add(bark, twig, leaf, blob, card);
}

// ---------- 白莲塔 ----------
function buildPagoda(ctx, group, own) {
  const { layout, materials: M, geom } = ctx;
  const P = layout.pagoda;
  const parts = [];
  const C8 = Math.cos(Math.PI / 8);
  const corner = (j) => { const a = (j * TAU) / 8 + Math.PI / 8; return [Math.cos(a), Math.sin(a)]; };
  const oct = (Rr, j, s) => { const [x0, z0] = corner(j); const [x1, z1] = corner(j + 1); return [Rr * lerp(x0, x1, s), Rr * lerp(z0, z1, s)]; };
  const faceRy = (j) => { const a = (j * TAU) / 8 + Math.PI / 4; return Math.atan2(Math.cos(a), Math.sin(a)); };
  const faceDir = (j) => { const a = (j * TAU) / 8 + Math.PI / 4; return [Math.cos(a), Math.sin(a)]; };

  // 八角檐：内缘 (R0,y0) → 外缘 (R1,y1)，翼角处外挑 flare、起翘 lift；返回外缘线供封檐板/风铃
  function skirt(mat, { R0, y0, R1, y1, flare, lift, sag, flip = false, nS = 8, nR = 6 }) {
    const pos = []; const uv = []; const idx = []; const edge = [];
    const slope = Math.hypot(R1 - R0, y0 - y1);
    for (let j = 0; j < 8; j++) {
      const b = pos.length / 3;
      for (let k = 0; k <= nR; k++) {
        const q = k / nR;
        for (let i = 0; i <= nS; i++) {
          const s = i / nS; const c = Math.pow(Math.abs(2 * s - 1), 3);
          const Rr = lerp(R0, R1, q) + flare * c * q * q;
          const y = lerp(y0, y1, q) - sag * Math.sin(Math.PI * q) + lift * c * q * q * q;
          const [x, z] = oct(Rr, j, s);
          pos.push(x, y, z); uv.push((j + s) * 2 * R1 * Math.sin(Math.PI / 8), q * slope);
          if (k === nR) edge.push([x, y, z, c]);
        }
      }
      for (let k = 0; k < nR; k++) {
        for (let i = 0; i < nS; i++) {
          const a = b + k * (nS + 1) + i; const d = a + nS + 1;
          if (flip) idx.push(a, a + 1, d, a + 1, d + 1, d); else idx.push(a, d, a + 1, a + 1, d, d + 1);
        }
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    g.setIndex(idx); g.computeVertexNormals();
    parts.push({ geom: g, mat });
    return edge;
  }
  // 檐下封檐板：瓦面外缘与檐底外缘之间的竖向窄带（两面都画）
  function fascia(top, under) {
    const pos = []; const idx = [];
    for (let k = 0; k < top.length; k++) pos.push(...top[k].slice(0, 3), ...under[k].slice(0, 3));
    for (let k = 0; k < top.length - 1; k++) {
      if (k % 9 === 8) continue; // 每面 9 个点，面与面之间不连
      const a = 2 * k; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2, a, a + 2, a + 1, a + 1, a + 2, a + 3);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(new Array((pos.length / 3) * 2).fill(0), 2));
    g.setIndex(idx); g.computeVertexNormals();
    parts.push({ geom: g, mat: M.woodDark });
  }

  // 须弥座
  parts.push({ geom: geom.place(cylM(7.6, 7.8, 2.5), { y: -0.75 }), mat: M.embankment });
  parts.push({ geom: geom.place(cylM(7.0, 7.0, 0.6), { y: 0.8 }), mat: M.embankment });
  parts.push({ geom: geom.place(cylM(7.4, 7.2, 0.5), { y: 1.35 }), mat: M.embankment });

  let y = 1.6;
  const R = (i) => (9 * Math.pow(0.93, i)) / (2 * C8);
  for (let i = 0; i < P.floors; i++) {
    const Ri = R(i); const T = 6.0 * Math.pow(0.92, i); const sc = Ri / R(0);
    const hb = (i === 0 ? 0.7 : 0.62) * T; const plat = i > 0 ? 0.3 : 0;
    const last = i === P.floors - 1;
    if (i > 0) { // 平座 + 栏杆
      const Rp = Ri + 0.95; const Rr = Ri + 0.85;
      parts.push({ geom: geom.place(cylM(Rp, Rp, 0.3), { y: y + 0.15 }), mat: M.woodDark });
      for (let j = 0; j < 8; j++) {
        for (const s of [0, 0.5]) { const [x, z] = oct(Rr, j, s); parts.push({ geom: geom.place(geom.boxM(0.1, 0.95, 0.1), { x, y: y + 0.77, z }), mat: M.woodDark }); }
        const [cx, cz] = oct(Rr, j, 0.5); const fl = 2 * Rr * Math.sin(Math.PI / 8);
        for (const hy of [0.45, 0.9]) parts.push({ geom: geom.place(geom.boxM(fl, 0.07, 0.06), { x: cx, y: y + 0.3 + hy, z: cz, ry: faceRy(j) }), mat: M.woodDark });
      }
    }
    const h = hb - plat;
    parts.push({ geom: geom.place(cylM(Ri * 0.99, Ri, h, 8, true), { y: y + plat + h / 2 }), mat: M.wall });
    const fw = 2 * Ri * Math.sin(Math.PI / 8);
    for (let j = 0; j < 8; j++) {
      const [x, z] = oct(Ri + 0.02, j, 0);
      parts.push({ geom: geom.place(geom.boxM(0.3, h, 0.3), { x, y: y + plat + h / 2, z }), mat: M.woodDark });
      const [dx, dz] = faceDir(j); const rc = Ri * C8;
      const door = j % 2 === 0;
      const ph = door ? h * 0.62 : h * 0.34; const pw = door ? fw * 0.42 : fw * 0.34; const py = y + plat + (door ? ph / 2 + 0.1 : h * 0.58);
      parts.push({ geom: geom.place(geom.boxM(pw, ph, 0.08), { x: dx * (rc + 0.03), y: py, z: dz * (rc + 0.03), ry: faceRy(j) }), mat: M.woodDark });
      parts.push({ geom: geom.place(geom.boxM(pw * 0.76, ph * 0.86, 0.08), { x: dx * (rc + 0.07), y: py - ph * 0.04, z: dz * (rc + 0.07), ry: faceRy(j) }), mat: M.darkInterior });
    }
    // 斗拱带
    parts.push({ geom: geom.place(cylM(Ri + 0.4, Ri + 0.12, 0.55), { y: y + hb - 0.27 }), mat: M.woodDark });
    // 屋檐（瓦面 + 檐底 + 封檐板）+ 角脊 + 风铃
    const proj = 1.9 * sc + 0.3; const flare = 0.75 * sc; const lift = 1.0 * sc;
    const y1 = y + hb + 0.25;
    const R0 = last ? 0.3 : R(i + 1); const y0 = last ? y + T + 4.2 : y + T;
    const edge = skirt(M.tile, { R0, y0, R1: Ri + proj, y1, flare, lift, sag: last ? 0.9 : 0.3 * sc, flip: true }); // 网格按 (外伸, 绕向) 排，flip 后瓦面法线朝上
    const under = skirt(M.woodDark, { R0: Ri + 0.4, y0: y + hb, R1: Ri + proj, y1: y1 - 0.18, flare, lift, sag: 0, nR: 2 });
    fascia(edge, under);
    for (let j = 0; j < 8; j++) {
      const ridge = [];
      for (let k = 1; k <= 6; k++) {
        const q = k / 6; const Rr = lerp(R0, Ri + proj, q) + flare * q * q; const yy = lerp(y0, y1, q) - (last ? 0.9 : 0.3 * sc) * Math.sin(Math.PI * q) + lift * q * q * q;
        const [x, z] = oct(Rr, j, 0); ridge.push(new V3(x, yy + 0.1, z));
      }
      for (let k = 0; k < ridge.length - 1; k++) {
        const a = ridge[k]; const b = ridge[k + 1]; const d = b.clone().sub(a);
        const g = geom.boxM(0.22, 0.2, d.length() + 0.05);
        g.lookAt(d); geom.place(g, { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, z: (a.z + b.z) / 2 });
        parts.push({ geom: g, mat: M.tileRidge });
      }
      const tip = ridge[ridge.length - 1];
      const up = geom.boxM(0.16, 0.55 * sc + 0.2, 0.16); geom.place(up, { x: tip.x, y: tip.y + 0.25, z: tip.z, rx: 0.3 * Math.sin((j * TAU) / 8), rz: -0.3 * Math.cos((j * TAU) / 8) });
      parts.push({ geom: up, mat: M.tileRidge });
      parts.push({ geom: geom.place(new THREE.CylinderGeometry(0.06, 0.15, 0.32, 6), { x: tip.x, y: tip.y - 0.55, z: tip.z }), mat: own.metal });
      parts.push({ geom: geom.place(geom.boxM(0.02, 0.3, 0.02), { x: tip.x, y: tip.y - 0.25, z: tip.z }), mat: own.metal });
    }
    y += T;
  }
  // 塔刹：覆钵、相轮、宝盖、宝珠，顶尖正好到 P.height
  const apex = y + 4.2 - 0.2; // 顶层屋面尖在 y + 4.2
  const F = P.height - apex;
  parts.push({ geom: geom.place(new THREE.SphereGeometry(0.8, 16, 8, 0, TAU, 0, Math.PI / 2), { y: apex - 0.1 }), mat: own.metal });
  parts.push({ geom: geom.place(new THREE.CylinderGeometry(0.11, 0.13, F, 10), { y: apex + F / 2 - 0.3 }), mat: own.metal });
  const ringGap = (F * 0.52) / 7;
  for (let k = 0; k < 7; k++) {
    const rr = lerp(0.62, 0.36, k / 6);
    parts.push({ geom: geom.place(new THREE.CylinderGeometry(rr, rr, 0.14, 16), { y: apex + 0.8 + k * ringGap }), mat: own.metal });
  }
  const yCanopy = apex + 0.8 + 7 * ringGap + 0.1;
  parts.push({ geom: geom.place(new THREE.ConeGeometry(0.85, 0.5, 16), { y: yCanopy }), mat: own.metal });
  parts.push({ geom: geom.place(new THREE.SphereGeometry(0.34, 14, 10), { y: P.height - 1.35 }), mat: own.metal });
  parts.push({ geom: geom.place(new THREE.SphereGeometry(0.24, 14, 10), { y: P.height - 0.75 }), mat: own.metal });
  parts.push({ geom: geom.place(new THREE.ConeGeometry(0.06, 0.5, 8), { y: P.height - 0.25 }), mat: own.metal });

  const g = geom.mergeByMaterial(parts);
  g.name = 'pagoda';
  g.position.set(P.x, 0, P.z);
  group.add(g);
}

// ---------- 远景民居群 ----------
const BD = { W: 10, D: 9, E: 5.5, slope: 0.5 };

function backdropGeoms(geom) {
  const half = BD.D / 2; const R = BD.E + half * BD.slope;
  const box = geom.place(geom.boxM(BD.W, BD.E + 0.6, BD.D), { y: (BD.E - 0.6) / 2 });
  const tri = new THREE.BufferGeometry(); const pos = []; const uv = [];
  for (const sx of [-1, 1]) {
    const x = (sx * BD.W) / 2; const zs = sx > 0 ? [half, -half] : [-half, half];
    pos.push(x, BD.E, zs[0], x, BD.E, zs[1], x, R, 0);
    uv.push(0, BD.E, BD.D, BD.E, half, R);
  }
  tri.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  tri.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  tri.setIndex([0, 1, 2, 3, 4, 5]); tri.computeVertexNormals();
  const wall = mergeGeometries([box, tri]);
  const run = half + 0.6; const rise = run * BD.slope; const len = Math.hypot(run, rise); const ang = Math.atan2(rise, run);
  const roofs = [];
  for (const sz of [1, -1]) {
    roofs.push(geom.place(geom.boxM(BD.W + 0.5, 0.14, len), { y: R + 0.1 - rise / 2, z: (sz * run) / 2, rx: sz * ang }));
  }
  roofs.push(geom.place(geom.boxM(BD.W + 0.6, 0.3, 0.35), { y: R + 0.2 }));
  return { wall, roof: mergeGeometries(roofs) };
}

function backdropLayout(layout) {
  const houses = []; const trees = [];
  for (const rect of layout.backdrop.fillRects) {
    const r = rng(`${ZONE}-${rect.id}`);
    let z = rect.z0 + 1;
    while (true) {
      const d = r.range(8, 11);
      if (z + d > rect.z1 - 1) break;
      let x = rect.x0 + 1;
      while (true) {
        const w = r.range(7, 14);
        if (x + w > rect.x1 - 1.5) break;
        if (!r.chance(0.06)) {
          houses.push({ x: x + w / 2, z: z + d / 2, w, d, e: r.chance(0.2) ? r.range(3.6, 4.3) : r.range(5.4, 6.8),
            yaw: r.range(-0.02, 0.02) + (r.chance(0.5) ? 0 : Math.PI) });
        }
        x += w + (r.chance(0.3) ? 1.2 : 0) + (r.chance(0.08) ? r.range(2.5, 4) : 0); // 弄堂与偶尔的小巷
      }
      z += d + r.range(1.6, 3.2); // 后巷
    }
  }
  // 区块外环带：村落、散户、树团。避开内区、白莲塔四周、河道（rivers[*].rect 两侧各留 3m）；pad = 物件自身半径
  const inner = layout.backdrop.innerRect; const Rout = layout.backdrop.outerRadius; const P = layout.pagoda;
  const RIVER_GAP = 3;
  const free = (x, z, pad = 0) => !(x > inner.x0 - 8 - pad && x < inner.x1 + 8 + pad && z > inner.z0 - 8 - pad && z < inner.z1 + 8 + pad)
    && Math.hypot(x - P.x, z - P.z) > 40 + pad && Math.hypot(x, z) < Rout - 8 - pad
    && !layout.rivers.some(({ rect: R }) => { const g = RIVER_GAP + pad; return x > R.x0 - g && x < R.x1 + g && z > R.z0 - g && z < R.z1 + g; });
  const r = rng(`${ZONE}-ring`);
  const sample = () => { const rho = Math.sqrt(r.range(130 * 130, 435 * 435)); const a = r.range(0, TAU); return [rho * Math.cos(a), rho * Math.sin(a)]; };
  const addHouse = (x, z, yaw, sc = 1) => {
    const w = r.range(7, 13) * sc; const d = r.range(7.5, 10) * sc;
    if (!free(x, z, Math.hypot(w + 0.6, d + 1.2) / 2)) return; // 含屋檐出挑的半对角线
    houses.push({ x, z, w, d, e: r.chance(0.3) ? r.range(3.6, 4.3) : r.range(5.2, 6.6), yaw, far: true });
  };
  const clump = (cx, cz, n, spread) => {
    for (let k = 0; k < n; k++) {
      const x = cx + r.range(-spread, spread); const z = cz + r.range(-spread, spread); const s = r.range(2.6, 4.8);
      if (!free(x, z, s * 1.2)) continue;
      trees.push({ x, y: s * 0.75 + 1.8, z, s });
    }
  };
  for (let c = 0, tries = 0; c < 46 && tries < 2000; tries++) {
    const [cx, cz] = sample();
    if (!free(cx, cz, 10)) continue;
    c++;
    const psi = r.pick([0, Math.PI / 2]) + r.range(-0.35, 0.35); const cs = Math.cos(psi); const sn = Math.sin(psi);
    const rows = r.int(1, 4);
    for (let row = 0; row < rows; row++) {
      const v = (row - (rows - 1) / 2) * r.range(11, 13); const n = r.int(3, 10);
      let u = -n * 5.5;
      for (let k = 0; k < n; k++) {
        const w = r.range(8, 12); u += w / 2;
        if (!r.chance(0.12)) addHouse(cx + u * cs - v * sn, cz + u * sn + v * cs, -psi + (r.chance(0.5) ? 0 : Math.PI) + r.range(-0.03, 0.03));
        u += w / 2 + (r.chance(0.3) ? r.range(1.2, 3) : 0);
      }
    }
    clump(cx + r.range(-30, 30), cz + r.range(-30, 30), r.int(3, 8), 9);
  }
  for (let k = 0; k < 110; k++) { const [x, z] = sample(); addHouse(x, z, r.range(0, TAU), 0.9); }
  for (let k = 0; k < 50; k++) { const [x, z] = sample(); clump(x, z, r.int(3, 10), 12); }
  return { houses, trees };
}

function buildBackdrop(ctx, group, own) {
  const { layout, materials: M, geom } = ctx;
  const { houses, trees } = backdropLayout(layout);
  const { wall, roof } = backdropGeoms(geom);
  const walls = new THREE.InstancedMesh(wall, M.wall, houses.length);
  const roofs = new THREE.InstancedMesh(roof, M.tile, houses.length);
  const r = rng(`${ZONE}-backdrop-color`);
  const m = new THREE.Matrix4(); const q = new THREE.Quaternion(); const yAxis = new V3(0, 1, 0); const c = new THREE.Color();
  houses.forEach((h, i) => {
    m.compose(new V3(h.x, 0, h.z), q.setFromAxisAngle(yAxis, h.yaw), new V3(h.w / BD.W, h.e / BD.E, h.d / BD.D));
    walls.setMatrixAt(i, m); roofs.setMatrixAt(i, m);
    const v = r.range(0.66, 0.92) * (h.far ? 0.8 : 1); walls.setColorAt(i, c.setRGB(v, v * 0.99, v * 0.96));
    const t = r.range(0.75, 1.1); roofs.setColorAt(i, c.setRGB(t, t, t));
  });
  const ico = new THREE.IcosahedronGeometry(1, 1);
  const crowns = new THREE.InstancedMesh(ico, own.farFoliage, trees.length);
  const trunks = new THREE.InstancedMesh(geom.place(cylM(0.18, 0.28, 1, 6, true), { y: 0.5 }), M.bark, trees.length);
  trees.forEach((t, i) => {
    m.compose(new V3(t.x, t.y, t.z), q.setFromAxisAngle(yAxis, r.range(0, TAU)), new V3(t.s, t.s * r.range(0.75, 0.95), t.s));
    crowns.setMatrixAt(i, m);
    m.compose(new V3(t.x, -0.3, t.z), q.identity(), new V3(t.s * 0.4, t.y + 0.3, t.s * 0.4));
    trunks.setMatrixAt(i, m);
    crowns.setColorAt(i, c.copy(r.pick(CAMPHOR_GREENS)).multiplyScalar(r.range(0.7, 1.05)));
  });
  for (const im of [walls, roofs, crowns, trunks]) { im.castShadow = im.receiveShadow = true; im.computeBoundingSphere(); }
  walls.name = 'backdrop-walls'; roofs.name = 'backdrop-roofs'; crowns.name = 'backdrop-trees'; trunks.name = 'backdrop-trunks';
  group.add(walls, roofs, crowns, trunks);
}

// ---------- 本区块材质 ----------
function ownMaterials(M) {
  const std = (name, p) => { const m = new THREE.MeshStandardMaterial(p); m.name = name; return m; };
  const print = canvasTex(1024, 1024, 1, 1, drawBluePrint);
  const weave = canvasTex(256, 256, 0.5, 0.5, drawWeave);
  const cloth = (name, p) => std(name, { roughness: 0.95, side: THREE.DoubleSide, ...p });
  const leafTex = canvasTex(64, 256, 1, 1, drawWillowLeaf, { wrap: false });
  const sprayTex = canvasTex(256, 256, 1, 1, drawCamphorSpray, { wrap: false });
  const own = {
    bamboo: std('bamboo', { map: canvasTex(64, 128, 0.25, 0.45, drawBamboo), roughness: 0.7 }),
    rope: std('rope', { color: 0x3a3024, roughness: 1 }),
    vat: std('vat', { color: 0x3a2a1e, roughness: 0.35, metalness: 0.05 }),
    dye: std('dye', { color: 0x0b1630, roughness: 0.12 }),
    metal: std('pagodaMetal', { color: 0x4a3f30, roughness: 0.45, metalness: 0.7 }),
    cloth: {
      print: cloth('clothPrint', { map: print }),
      indigo: cloth('clothIndigo', { map: weave, color: 0x223a66 }),
      light: cloth('clothLight', { map: weave, color: 0x8ea8c8 }),
      white: cloth('clothWhite', { map: weave, color: 0xe2ddd0 }),
    },
    twig: std('willowTwig', { color: 0x6b6838, roughness: 0.8 }),
    willowLeaf: std('willowLeaf', { map: leafTex, alphaTest: 0.5, vertexColors: true, side: THREE.DoubleSide, roughness: 0.62 }),
    camphorBlob: std('camphorBlob', { vertexColors: true, roughness: 0.85 }),
    camphorCard: std('camphorCard', { map: sprayTex, alphaTest: 0.5, vertexColors: true, side: THREE.DoubleSide, roughness: 0.6 }),
    farFoliage: std('farFoliage', { color: 0xffffff, roughness: 0.9 }),
  };
  own.rope.userData.noShadow = true;
  return own;
}

// ---------- 接口 ----------
export function build(ctx) {
  rng = ctx.rng;
  ctx.scene?.traverse((o) => { if (o.isDirectionalLight && o.castShadow && !sunLight) sunLight = o; });
  const group = new THREE.Group();
  const own = ownMaterials(ctx.materials);
  buildDyeYard(ctx, group, own);
  buildTrees(ctx, group, own);
  buildPagoda(ctx, group, own);
  buildBackdrop(ctx, group, own);
  group.userData.closeups = Object.fromEntries(Object.entries(HERO).map(([id, h]) => [id, { x: h.rest.x, y: h.rest.y, z: h.rest.z }]));
  update(0);
  return group;
}

export function update(t) {
  U.uTime.value = t;
  U.uSunDir.value.copy(sunDirection(t));
  if (sunLight) U.uSunCol.value.copy(sunLight.color).multiplyScalar(sunLight.intensity);
}

// 特写柳枝梢在 t 时刻的世界坐标（与着色器同一公式），供镜头跟拍。id: 'wNW4' | 'wS3'
export function willowTipAt(id, t) {
  const h = HERO[id];
  if (!h) return null;
  const d = willowAt(h.s, h.phase, h.amp, t);
  return { x: h.rest.x + d.x, y: h.rest.y + d.y, z: h.rest.z + d.z };
}
