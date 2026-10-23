// 公共几何工具（子 Agent 只读）。
// 约定：所有几何体的 UV 以“米”为单位，材质贴图的 repeat 已按真实尺寸设好，
// 所以同一材质贴在不同大小的物体上，纹理密度一致。
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

// 盒子，UV 按每个面的真实尺寸（米）缩放
export function boxM(w, h, d) {
  const g = new THREE.BoxGeometry(w, h, d);
  const uv = g.attributes.uv;
  const dims = [[d, h], [d, h], [w, d], [w, d], [w, h], [w, h]]; // +x -x +y -y +z -z
  for (let f = 0; f < 6; f++) {
    for (let k = 0; k < 4; k++) {
      const i = f * 4 + k;
      uv.setXY(i, uv.getX(i) * dims[f][0], uv.getY(i) * dims[f][1]);
    }
  }
  return g;
}

// 平面（XY 平面，法线 +Z），UV 以米为单位
export function planeM(w, h, ws = 1, hs = 1) {
  const g = new THREE.PlaneGeometry(w, h, ws, hs);
  const uv = g.attributes.uv;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * w, uv.getY(i) * h);
  return g;
}

// 对几何体施加平移/旋转（欧拉角 XYZ 顺序），返回同一个几何体
export function place(geom, { x = 0, y = 0, z = 0, rx = 0, ry = 0, rz = 0, s = 1 } = {}) {
  const m = new THREE.Matrix4().compose(
    new THREE.Vector3(x, y, z),
    new THREE.Quaternion().setFromEuler(new THREE.Euler(rx, ry, rz)),
    new THREE.Vector3(s, s, s),
  );
  geom.applyMatrix4(m);
  return geom;
}

// 把 [{geom, mat}] 按材质合并成少量网格，减少 draw call。
// 注意：只保留 position/normal/uv，顶点色和自定义属性会被丢掉；需要它们就直接用 mergeGeometries
export function mergeByMaterial(parts, { castShadow = true, receiveShadow = true } = {}) {
  const byMat = new Map();
  for (const { geom, mat } of parts) {
    if (!mat) throw new Error('mergeByMaterial: 缺少材质');
    const g = geom.index ? geom.toNonIndexed() : geom;
    for (const name of Object.keys(g.attributes)) {
      if (!['position', 'normal', 'uv'].includes(name)) g.deleteAttribute(name);
    }
    g.clearGroups();
    if (!byMat.has(mat)) byMat.set(mat, []);
    byMat.get(mat).push(g);
  }
  const group = new THREE.Group();
  for (const [mat, geoms] of byMat) {
    const merged = mergeGeometries(geoms, false);
    if (!merged) throw new Error(`mergeByMaterial: 合并失败（材质 ${mat.name}）`);
    const mesh = new THREE.Mesh(merged, mat);
    mesh.castShadow = castShadow && !mat.userData.noShadow;
    mesh.receiveShadow = receiveShadow;
    group.add(mesh);
  }
  return group;
}

// 一面带瓦垄的屋面坡。局部坐标：屋脊沿 X 轴在 (z=0, y=0)，
// 向 +Z 延伸 run 米、下降 rise 米到檐口。sag = 屋面中段下凹量（举折），
// detail='high' 时网格更密。法线朝上（外侧）。
export const TILE_PITCH = 0.4; // 一沟一垄的宽度（米）
export function tiledRoofSlope({ width, run, rise, sag = 0.2, detail = 'high', tileDepth = 0.05 }) {
  const step = detail === 'high' ? TILE_PITCH / 6 : TILE_PITCH / 3; // 每垄 6 / 3 个采样
  const nx = Math.max(2, Math.ceil(width / step));
  const ns = detail === 'high' ? 10 : 5;
  const slopeLen = Math.hypot(run, rise);
  const ny = run / slopeLen; const nz = rise / slopeLen; // 屋面外法线 (0, ny, nz)
  const pos = []; const uv = []; const idx = [];
  for (let j = 0; j <= ns; j++) {
    const s = j / ns;
    const baseZ = run * s;
    const baseY = -rise * s - sag * Math.sin(Math.PI * s);
    for (let i = 0; i <= nx; i++) {
      const x = -width / 2 + (width * i) / nx;
      const bump = tileDepth * Math.cos((2 * Math.PI * x) / TILE_PITCH);
      pos.push(x, baseY + bump * ny, baseZ + bump * nz);
      uv.push(x + width / 2, (1 - s) * slopeLen);
    }
  }
  const row = nx + 1;
  for (let j = 0; j < ns; j++) {
    for (let i = 0; i < nx; i++) {
      const a = j * row + i; const b = a + 1; const c = a + row; const d = c + 1;
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

// 沿檐口的一排滴水瓦 + 瓦当（近景细节）。局部坐标与 tiledRoofSlope 的檐口对齐：
// 檐口线在 (y=0, z=0)，沿 X 排布，向 +Z 外挑。返回 [{geom, mat}]
export function eaveTiles(width, M) {
  // tiledRoofSlope 的瓦垄在 x = k·TILE_PITCH，瓦沟在 x = (k+½)·TILE_PITCH
  const parts = [];
  const half = width / 2;
  for (let k = Math.ceil(-half / TILE_PITCH); k * TILE_PITCH <= half; k++) {
    const ridgeX = k * TILE_PITCH;
    const cap = new THREE.CylinderGeometry(0.075, 0.075, 0.03, 8, 1); // 瓦当（圆形勾头）
    place(cap, { x: ridgeX, y: 0.03, z: 0.03, rx: Math.PI / 2 });
    parts.push({ geom: cap, mat: M.tileRidge });
    const channelX = ridgeX + TILE_PITCH / 2;
    if (channelX < half) {
      const drip = new THREE.CylinderGeometry(0.07, 0.07, 0.02, 3, 1); // 滴水（三角垂片）
      place(drip, { x: channelX, y: -0.045, z: 0.03, rx: Math.PI / 2, rz: Math.PI });
      parts.push({ geom: drip, mat: M.tile });
    }
  }
  return parts;
}
