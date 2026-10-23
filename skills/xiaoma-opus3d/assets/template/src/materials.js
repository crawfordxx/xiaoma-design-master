// 全局材质（子 Agent 只读）。纹理一律用 Canvas 程序化绘制，不加载图片。
// UV 约定：UV 单位是米；每张纹理 repeat = 1 / 纹理覆盖的真实尺寸。完整的例子见 references/examples/wuzhen.md。
import * as THREE from 'three';
import { rng } from './rng.js';

export function canvasTexture(key, w, h, metersW, metersH, draw, { color = true } = {}) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h, rng(`tex-${key}`));
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(1 / metersW, 1 / metersH);
  t.colorSpace = color ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  t.anisotropy = 8;
  return t;
}

export function speckle(ctx, w, h, r, count, alphaMax, colors) {
  for (let i = 0; i < count; i++) {
    ctx.globalAlpha = r.range(0.02, alphaMax);
    ctx.fillStyle = r.pick(colors);
    const s = r.range(1, 3);
    ctx.fillRect(r.range(0, w), r.range(0, h), s, s);
  }
  ctx.globalAlpha = 1;
}

function std(name, params) {
  const m = new THREE.MeshStandardMaterial(params);
  m.name = name;
  return m;
}

export function createMaterials() {
  const M = {
    ground: std('ground', { color: 0x6f6a58, roughness: 1 }),
    // 发光材质：亮度统一由 setGlowLevel 控制，区块里不要自己改 emissiveIntensity
    glow: std('glow', { color: 0x8f1a12, emissive: 0xff2a10, emissiveIntensity: 1, roughness: 0.6 }),
  };
  M.glow.userData.noShadow = true;
  // 发光亮度上限别太高：ACES 会把高亮的饱和色洗成黄白色（红灯笼会变成淡黄）
  M.setGlowLevel = (level) => { M.glow.emissiveIntensity = 0.12 + 1.7 * level; };
  M.setGlowLevel(0.2);
  return M;
}
