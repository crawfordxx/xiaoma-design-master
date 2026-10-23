// 场景核心：建渲染器、后期、光照和全部区块，提供 render() / setSize() / setQuality()。
// main.js（截图测试）和 viewer.js（交互模型）都建立在它上面。
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import * as layout from './layout.js';
import { rng } from './rng.js';
import { createMaterials } from './materials.js';
import * as shared from './shared.js'; // 项目公共生成器
import * as geom from './geom.js';
import * as paths from './paths.js';
import { createLighting } from './lighting.js';
import { ZONE_MODULES, DEFAULT_ZONES } from './zones/index.js';

// 画质档位。reflection = 水面反射分辨率相对画面的比例（0 = 关闭反射）
export const QUALITY = {
  high: { pixelRatio: 2, samples: 4, shadow: 4096, bloom: true, reflection: 0.5 },
  medium: { pixelRatio: 1.5, samples: 2, shadow: 2048, bloom: true, reflection: 0.35 },
  low: { pixelRatio: 1, samples: 0, shadow: 1024, bloom: false, reflection: 0 },
};
export const QUALITY_ORDER = ['high', 'medium', 'low'];

// 安全网：bloom 之前把 NaN/Inf 像素清零。否则任何一个 shader 出一个坏像素，bloom 会把它扩散成整帧黑屏
const NanGuardShader = {
  uniforms: { tDiffuse: { value: null } },
  vertexShader: 'varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  // 按位模式判断（指数位全 1 = Inf/NaN）：Metal 的快速数学会把 isnan 和 c != c 优化掉
  fragmentShader: `uniform sampler2D tDiffuse; varying vec2 vUv;
    bool bad(float x) { return (floatBitsToUint(x) & 0x7f800000u) == 0x7f800000u || abs(x) > 65000.0; }
    void main() { vec4 c = texture2D(tDiffuse, vUv);
      gl_FragColor = (bad(c.r) || bad(c.g) || bad(c.b)) ? vec4(0.0, 0.0, 0.0, 1.0) : c; }`,
};

/**
 * @param {object} o
 * @param {HTMLElement} o.container  画布挂到哪里
 * @param {number} o.width  CSS 像素宽
 * @param {number} o.height CSS 像素高
 * @param {string[]} [o.zones]  要加载的区块，默认全部正式区块
 * @param {string} [o.quality]  high | medium | low
 * @param {number} [o.pixelRatio] 设备像素比上限（截图测试传 1，保证输出尺寸固定）
 * @param {boolean} [o.preserveDrawingBuffer] 截图测试需要
 */
export async function createScene(o) {
  const status = { ready: false, errors: [], zones: {} };
  let width = o.width; let height = o.height;
  const dpr = o.pixelRatio ?? (typeof window !== 'undefined' ? window.devicePixelRatio : 1);

  const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: Boolean(o.preserveDrawingBuffer), powerPreference: 'high-performance' });
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.domElement.style.display = 'block';
  o.container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const persp = new THREE.PerspectiveCamera(45, width / height, 0.05, 6000);
  const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 2000);
  const materials = createMaterials();
  const lighting = createLighting(scene, renderer, materials);

  // 区块会在 build 时读画面尺寸（比如水面反射），所以先把尺寸设好
  let quality = QUALITY[o.quality ?? 'high'];
  renderer.setPixelRatio(Math.min(dpr, quality.pixelRatio));
  renderer.setSize(width, height); // 第三个参数默认 true：同时设 CSS 尺寸，否则高像素比屏幕上画布会按物理像素撑出容器

  const ctx = { THREE, scene, renderer, layout, materials, rng, shared, geom, paths };
  const updaters = [];
  for (const z of o.zones ?? DEFAULT_ZONES) {
    const t0 = performance.now();
    try {
      const mod = ZONE_MODULES[z];
      if (!mod) throw new Error(`没有这个区块：${z}`);
      const group = await mod.build(ctx);
      if (!(group instanceof THREE.Object3D)) throw new Error('build(ctx) 必须返回 THREE.Object3D');
      group.name = z;
      scene.add(group);
      if (mod.update) updaters.push({ z, fn: mod.update });
      status.zones[z] = { ok: true, ms: Math.round(performance.now() - t0) };
    } catch (e) {
      console.error(`[zone ${z}]`, e);
      status.errors.push(`${z}: ${e.message}`);
      status.zones[z] = { ok: false, error: e.message };
    }
  }

  // 水面反射：按画质调分辨率；关闭时跳过反射渲染，并把 shader 的 uReflect 置 0
  const reflectors = [];
  scene.traverse((obj) => { if (obj.isReflector) reflectors.push(obj); });
  let reflectOn = true;
  for (const r of reflectors) {
    const inner = r.onBeforeRender;
    r.onBeforeRender = (...args) => {
      if (reflectOn) inner(...args);
      else if (r.material.uniforms?.uReflect) r.material.uniforms.uReflect.value = 0;
    };
  }

  const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType, samples: quality.samples }));
  const renderPass = new RenderPass(scene, persp);
  const bloom = new UnrealBloomPass(new THREE.Vector2(width, height), 0.55, 0.5, 0.88);
  composer.addPass(renderPass);
  composer.addPass(new ShaderPass(NanGuardShader));
  composer.addPass(bloom);
  composer.addPass(new OutputPass());

  const FOG_DENSITY = scene.fog.density;

  function applyQuality() {
    renderer.setPixelRatio(Math.min(dpr, quality.pixelRatio));
    renderer.setSize(width, height); // 第三个参数默认 true：同时设 CSS 尺寸，否则高像素比屏幕上画布会按物理像素撑出容器
    composer.setPixelRatio(renderer.getPixelRatio());
    composer.setSize(width, height);
    for (const rt of [composer.renderTarget1, composer.renderTarget2]) {
      if (rt.samples !== quality.samples) { rt.samples = quality.samples; rt.dispose(); }
    }
    bloom.enabled = quality.bloom;
    const sun = lighting.sun;
    if (sun.shadow.mapSize.x !== quality.shadow) {
      sun.shadow.mapSize.set(quality.shadow, quality.shadow);
      sun.shadow.map?.dispose();
      sun.shadow.map = null;
    }
    reflectOn = quality.reflection > 0;
    const buf = renderer.getDrawingBufferSize(new THREE.Vector2());
    for (const r of reflectors) {
      const s = Math.max(quality.reflection, 0.1);
      r.getRenderTarget().setSize(Math.round(buf.x * s), Math.round(buf.y * s));
    }
  }
  applyQuality();

  // view: { pos, target, fov } 或 { ortho: true, rect } 或 { camera, target }（交互模式直接给相机）
  function applyView(view) {
    if (view.camera) {
      const dist = view.camera.position.distanceTo(view.target);
      return { camera: view.camera, focus: view.target, shadowSize: THREE.MathUtils.clamp(dist * 1.6, 24, 320) };
    }
    if (view.ortho) {
      const r = view.rect ?? layout.EXTENT; const aspect = width / height;
      const cx = (r.x0 + r.x1) / 2; const cz = (r.z0 + r.z1) / 2;
      const halfW = Math.max((r.x1 - r.x0) / 2, ((r.z1 - r.z0) / 2) * aspect);
      const halfH = halfW / aspect;
      Object.assign(ortho, { left: -halfW, right: halfW, top: halfH, bottom: -halfH });
      ortho.position.set(cx, 150, cz);
      ortho.up.set(0, 0, -1); // 北在上
      ortho.lookAt(cx, 0, cz);
      ortho.updateProjectionMatrix();
      return { camera: ortho, focus: new THREE.Vector3(cx, 0, cz), shadowSize: 2 * Math.max(halfW, halfH) + 20, noFog: true };
    }
    persp.fov = view.fov ?? 45;
    persp.position.set(...view.pos);
    persp.up.set(0, 1, 0);
    const target = new THREE.Vector3(...view.target);
    persp.lookAt(target);
    persp.updateProjectionMatrix();
    const dist = persp.position.distanceTo(target);
    return { camera: persp, focus: target, shadowSize: THREE.MathUtils.clamp(dist * 1.6, 24, 320) };
  }

  // lightT：光照时刻（决定太阳高度、灯笼亮度）；animT：动画时刻（船、布、柳条、水波）
  function render({ lightT, animT, view }) {
    const { camera, focus, shadowSize, noFog } = applyView(view);
    lighting.update(lightT, focus, shadowSize);
    scene.fog.density = noFog ? 0 : FOG_DENSITY;
    if (noFog) renderer.toneMappingExposure *= 2.5; // 俯视对位图提亮，只为看清位置
    for (const { z, fn } of updaters) {
      try { fn(animT); } catch (e) { status.errors.push(`${z}.update: ${e.message}`); }
    }
    renderPass.camera = camera;
    composer.render();
  }

  function setSize(w, h) {
    width = Math.max(1, Math.round(w)); height = Math.max(1, Math.round(h));
    persp.aspect = width / height;
    persp.updateProjectionMatrix();
    applyQuality();
  }

  function setQuality(name) {
    if (!QUALITY[name]) throw new Error(`没有这个画质档位：${name}`);
    quality = QUALITY[name];
    applyQuality();
  }

  function dispose() {
    renderer.dispose();
    renderer.domElement.remove();
  }

  status.ready = true;
  return { renderer, scene, persp, ortho, composer, materials, lighting, status, render, setSize, setQuality, dispose, get size() { return { width, height }; } };
}
