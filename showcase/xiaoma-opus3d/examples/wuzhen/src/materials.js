// 全局材质（子 Agent 只读，不要在区块文件里另起同类材质）。
// 所有纹理都由 Canvas 程序化绘制，不加载任何图片。
// UV 约定见 geom.js：UV 单位是米，下面每张纹理的 repeat = 1 / 纹理覆盖的真实尺寸。
import * as THREE from 'three';
import { rng } from './rng.js';

function canvasTexture(key, w, h, metersW, metersH, draw, { color = true } = {}) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const ctx = c.getContext('2d');
  draw(ctx, w, h, rng(`tex-${key}`));
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(1 / metersW, 1 / metersH);
  t.colorSpace = color ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  t.anisotropy = 8;
  return t;
}

function speckle(ctx, w, h, r, count, alphaMax, colors) {
  for (let i = 0; i < count; i++) {
    ctx.globalAlpha = r.range(0.02, alphaMax);
    ctx.fillStyle = r.pick(colors);
    const s = r.range(1, 3);
    ctx.fillRect(r.range(0, w), r.range(0, h), s, s);
  }
  ctx.globalAlpha = 1;
}

function blotches(ctx, w, h, r, count, rMin, rMax, color, alphaMax) {
  for (let i = 0; i < count; i++) {
    const x = r.range(0, w); const y = r.range(0, h); const rad = r.range(rMin, rMax);
    const g = ctx.createRadialGradient(x, y, 0, x, y, rad);
    g.addColorStop(0, color.replace('A', String(r.range(0.03, alphaMax))));
    g.addColorStop(1, color.replace('A', '0'));
    ctx.fillStyle = g;
    ctx.fillRect(x - rad, y - rad, rad * 2, rad * 2);
  }
}

// 白粉墙：偏暖灰，墙脚 1.2m 有返潮霉斑，上部有雨水垂痕。覆盖 6m(宽) × 8m(高)，v=0 是墙脚
function drawWall(ctx, w, h, r) {
  ctx.fillStyle = '#d6d0c3';
  ctx.fillRect(0, 0, w, h);
  blotches(ctx, w, h, r, 40, 30, 140, 'rgba(150,140,120,A)', 0.12);
  blotches(ctx, w, h, r, 20, 20, 80, 'rgba(235,232,224,A)', 0.25);
  // 雨水垂痕：从上往下的灰色细条
  for (let i = 0; i < 70; i++) {
    const x = r.range(0, w); const len = r.range(h * 0.05, h * 0.45); const y0 = r.range(0, h * 0.4);
    const g = ctx.createLinearGradient(0, y0, 0, y0 + len);
    g.addColorStop(0, `rgba(95,92,85,${r.range(0.06, 0.18)})`);
    g.addColorStop(1, 'rgba(95,92,85,0)');
    ctx.fillStyle = g;
    ctx.fillRect(x, y0, r.range(2, 9), len);
  }
  // 墙脚返潮：底部约 1.2m 发暗发绿，上沿是起伏的不规则线
  ctx.beginPath();
  ctx.moveTo(0, h);
  for (let x = 0; x <= w; x += 8) {
    ctx.lineTo(x, h * (0.83 - 0.035 * Math.sin(x * 0.011) - 0.02 * Math.sin(x * 0.047 + 1.3) - r.range(0, 0.012)));
  }
  ctx.lineTo(w, h);
  ctx.closePath();
  const damp = ctx.createLinearGradient(0, h * 0.78, 0, h);
  damp.addColorStop(0, 'rgba(96,100,82,0.05)');
  damp.addColorStop(0.3, 'rgba(96,100,82,0.32)');
  damp.addColorStop(1, 'rgba(66,70,58,0.7)');
  ctx.fillStyle = damp;
  ctx.fill();
  speckle(ctx, w, h, r, 9000, 0.25, ['#9b9484', '#efece4', '#7c7a6c']);
}

// 黛瓦：蓝灰，每片瓦长 0.3m，宽度对齐 geom.TILE_PITCH(0.4m)。覆盖 2m × 2m
function drawTile(ctx, w, h, r) {
  ctx.fillStyle = '#434a53';
  ctx.fillRect(0, 0, w, h);
  const cols = 5; const rows = Math.round(2 / 0.3);
  const cw = w / cols; const rh = h / rows;
  for (let j = 0; j < rows; j++) {
    for (let i = 0; i < cols * 2; i++) {
      const v = r.range(-14, 14);
      ctx.fillStyle = `rgb(${67 + v},${74 + v},${84 + v})`;
      ctx.fillRect((i * cw) / 2 + 1, j * rh + 1, cw / 2 - 2, rh - 2);
      // 每片瓦下沿一道暗缝
      ctx.fillStyle = 'rgba(20,22,26,0.55)';
      ctx.fillRect((i * cw) / 2, j * rh + rh - 3, cw / 2, 3);
    }
  }
  blotches(ctx, w, h, r, 25, 10, 50, 'rgba(110,118,92,A)', 0.25); // 青苔
  speckle(ctx, w, h, r, 4000, 0.3, ['#2b3036', '#6a727c']);
}

// 栗壳色木板：竖向板缝，0.25m 一块。覆盖 1m × 2m
function drawWood(ctx, w, h, r) {
  ctx.fillStyle = '#4a2f24';
  ctx.fillRect(0, 0, w, h);
  const boards = 4; const bw = w / boards;
  for (let i = 0; i < boards; i++) {
    const v = r.range(-10, 10);
    ctx.fillStyle = `rgb(${74 + v},${47 + v * 0.6},${36 + v * 0.4})`;
    ctx.fillRect(i * bw, 0, bw, h);
    for (let k = 0; k < 14; k++) { // 木纹
      ctx.strokeStyle = `rgba(30,18,12,${r.range(0.08, 0.25)})`;
      ctx.lineWidth = r.range(0.5, 2);
      ctx.beginPath();
      const x = i * bw + r.range(2, bw - 2);
      ctx.moveTo(x, 0);
      for (let y = 0; y <= h; y += 16) ctx.lineTo(x + Math.sin(y * 0.02 + k) * 2, y);
      ctx.stroke();
    }
    ctx.fillStyle = 'rgba(15,8,5,0.8)';
    ctx.fillRect(i * bw, 0, 2, h); // 板缝
  }
  blotches(ctx, w, h, r, 10, 20, 60, 'rgba(120,100,80,A)', 0.12); // 风化发白
}

// 青石板路：1.2m × 0.6m 错缝。覆盖 2.4m × 2.4m
function drawSlab(ctx, w, h, r) {
  ctx.fillStyle = '#2a2c2d';
  ctx.fillRect(0, 0, w, h);
  const rows = 4; const rh = h / rows; const sw = w / 2;
  for (let j = 0; j < rows; j++) {
    const off = j % 2 ? sw / 2 : 0;
    for (let i = -1; i < 3; i++) {
      const v = r.range(-12, 12);
      ctx.fillStyle = `rgb(${104 + v},${108 + v},${110 + v})`;
      ctx.fillRect(i * sw + off + 2, j * rh + 2, sw - 4, rh - 4);
    }
  }
  blotches(ctx, w, h, r, 30, 15, 70, 'rgba(40,44,46,A)', 0.25); // 湿痕
  speckle(ctx, w, h, r, 6000, 0.3, ['#4d5153', '#9a9fa1']);
}

// 驳岸条石：1.2m × 0.4m 错缝，偏暖灰。覆盖 2.4m × 2.4m
function drawEmbankment(ctx, w, h, r) {
  ctx.fillStyle = '#4a463f';
  ctx.fillRect(0, 0, w, h);
  const rows = 6; const rh = h / rows; const sw = w / 2;
  for (let j = 0; j < rows; j++) {
    const off = j % 2 ? sw / 2 : 0;
    for (let i = -1; i < 3; i++) {
      const v = r.range(-14, 14);
      ctx.fillStyle = `rgb(${138 + v},${132 + v},${120 + v})`;
      ctx.fillRect(i * sw + off + 2, j * rh + 2, sw - 4, rh - 4);
    }
  }
  blotches(ctx, w, h, r, 30, 15, 70, 'rgba(70,74,58,A)', 0.3);
  speckle(ctx, w, h, r, 6000, 0.3, ['#5f5a50', '#b2ab9c']);
}

// 室内暖光：顶上一团灯光，往下变暗，有货架横线和货品剪影，避免成为一面均匀发光墙。覆盖 3m × 3m
function drawInterior(ctx, w, h, r) {
  ctx.fillStyle = '#1a0d05';
  ctx.fillRect(0, 0, w, h);
  for (let i = 0; i < 3; i++) { // 几盏灯的光斑
    const x = r.range(0.15, 0.85) * w; const y = r.range(0.1, 0.35) * h; const rad = r.range(0.3, 0.55) * w;
    const g = ctx.createRadialGradient(x, y, 0, x, y, rad);
    g.addColorStop(0, 'rgba(255,214,150,0.95)'); g.addColorStop(0.4, 'rgba(230,140,60,0.55)'); g.addColorStop(1, 'rgba(60,25,8,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  }
  for (let k = 0; k < 4; k++) { // 货架横板 + 货品剪影
    const y = h * (0.35 + k * 0.16);
    ctx.fillStyle = 'rgba(25,12,5,0.85)';
    ctx.fillRect(0, y, w, 5);
    for (let x = r.range(0, 20); x < w; x += r.range(14, 40)) {
      const bw = r.range(8, 22); const bh = r.range(10, 34);
      ctx.fillStyle = `rgba(${r.int(20, 60)},${r.int(10, 30)},5,${r.range(0.5, 0.9)})`;
      ctx.fillRect(x, y - bh, bw, bh);
    }
  }
}

// 蓝印花布：靛蓝底、白色小团花和点线边。覆盖 1m × 1m
function drawCloth(ctx, w, h, r) {
  ctx.fillStyle = '#1d3a6c';
  ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = '#e9ecef';
  const n = 4; const cell = w / n;
  for (let j = 0; j < n; j++) {
    for (let i = 0; i < n; i++) {
      const cx = (i + 0.5) * cell + (j % 2 ? cell / 2 : 0); const cy = (j + 0.5) * cell;
      for (let p = 0; p < 6; p++) { // 六瓣团花
        const a = (p / 6) * Math.PI * 2;
        ctx.beginPath();
        ctx.ellipse(cx + Math.cos(a) * cell * 0.16, cy + Math.sin(a) * cell * 0.16, cell * 0.09, cell * 0.05, a, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.beginPath(); ctx.arc(cx, cy, cell * 0.05, 0, Math.PI * 2); ctx.fill();
    }
  }
  for (let x = 0; x < w; x += 10) { // 点线边
    ctx.beginPath(); ctx.arc(x, 6, 2, 0, Math.PI * 2); ctx.arc(x + 5, h - 6, 2, 0, Math.PI * 2); ctx.fill();
  }
  speckle(ctx, w, h, r, 2500, 0.25, ['#132849', '#3a5a8f']);
}

function std(name, params) {
  const m = new THREE.MeshStandardMaterial(params);
  m.name = name;
  return m;
}

export function createMaterials() {
  const wallMap = canvasTexture('wall', 768, 1024, 6, 8, drawWall);
  const tileMap = canvasTexture('tile', 512, 512, 2, 2, drawTile);
  const woodMap = canvasTexture('wood', 256, 512, 1, 2, drawWood);
  const slabMap = canvasTexture('slab', 512, 512, 2.4, 2.4, drawSlab);
  const bankMap = canvasTexture('bank', 512, 512, 2.4, 2.4, drawEmbankment);
  const clothMap = canvasTexture('cloth', 256, 256, 1, 1, drawCloth);
  const interiorMap = canvasTexture('interior', 256, 256, 3, 3, drawInterior);

  const M = {
    wall: std('wall', { map: wallMap, roughness: 0.92 }),               // 白粉墙
    tile: std('tile', { map: tileMap, roughness: 0.78, metalness: 0.05 }), // 黛瓦屋面
    tileRidge: std('tileRidge', { color: 0x363b42, roughness: 0.7 }),   // 屋脊、瓦当、墙帽
    wood: std('wood', { map: woodMap, roughness: 0.8 }),               // 门板、木立面
    woodDark: std('woodDark', { color: 0x2e1d16, roughness: 0.75 }),   // 梁柱、窗格、檐下
    stoneSlab: std('stoneSlab', { map: slabMap, roughness: 0.62 }),    // 石板街、桥面
    embankment: std('embankment', { map: bankMap, roughness: 0.85 }),  // 驳岸、台基、石柱、拱券
    cloth: std('cloth', { map: clothMap, roughness: 0.95, side: THREE.DoubleSide }), // 蓝印花布
    lantern: std('lantern', { color: 0x8f1a12, emissive: 0xff2a10, emissiveIntensity: 1, roughness: 0.6 }),
    lanternFrame: std('lanternFrame', { color: 0x1c120d, roughness: 0.7 }),
    interiorGlow: std('interiorGlow', { color: 0x1a120c, emissive: 0xffffff, emissiveMap: interiorMap, emissiveIntensity: 1, roughness: 1 }),
    windowGlow: std('windowGlow', { color: 0x1a120c, emissive: 0xffa456, emissiveIntensity: 1, roughness: 1 }), // 亮窗：均匀暖光（窗小，不能用室内贴图）
    darkInterior: std('darkInterior', { color: 0x0c0a09, roughness: 1 }),
    flagCloth: std('flagCloth', { color: 0xe8dcc0, roughness: 0.95, side: THREE.DoubleSide }), // 酒旗/招幌底色
    bark: std('bark', { color: 0x3b3128, roughness: 0.95 }),
    foliageWillow: std('foliageWillow', { color: 0x7d9a50, roughness: 0.85, side: THREE.DoubleSide }),
    foliageCamphor: std('foliageCamphor', { color: 0x3e6536, roughness: 0.85, side: THREE.DoubleSide }),
    earth: std('earth', { color: 0x6f6a58, roughness: 1 }),             // 区块外地面
    field: std('field', { color: 0x5d6b3e, roughness: 1 }),             // 远处田野
  };
  M.lantern.userData.noShadow = true;
  M.interiorGlow.userData.noShadow = true;
  M.windowGlow.userData.noShadow = true;

  // 灯笼与室内灯光亮度（0~1），由 lighting.js 每帧调用
  M.setLanternLevel = (level) => {
    M.lantern.emissiveIntensity = 0.12 + 1.7 * level; // 再高经 ACES 会洗成黄白色，红色出不来
    M.interiorGlow.emissiveIntensity = 0.04 + 2.0 * level * level; // 贴图本身偏暗，强度比纯色时略高
    M.windowGlow.emissiveIntensity = 0.03 + 1.3 * level * level;
  };
  M.setLanternLevel(0.25);
  return M;
}

// 水的基调颜色，供 water.js 使用
export const WATER = { shallow: 0x4d5a52, deep: 0x1d2a2a };
