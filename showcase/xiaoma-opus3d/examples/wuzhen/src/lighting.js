// 天空、太阳、环境光、雾、灯笼光。全部只由 t 决定。
import * as THREE from 'three';
import { createSky } from './sky.js';
import { lighting as L, corridors } from './layout.js';
import { clamp01, lerp, smoothstep } from './paths.js';

const DEG = Math.PI / 180;
const ENV_STEP = 0.5; // 环境贴图每 0.5 秒（按 t 量化）重建一次，保证确定性

export function sunDirection(t) {
  const k = clamp01(t / L.duration);
  const e = lerp(L.sunElevationStartDeg, L.sunElevationEndDeg, k) * DEG;
  const b = L.sunBearingDeg * DEG;
  return new THREE.Vector3(Math.sin(b) * Math.cos(e), Math.sin(e), -Math.cos(b) * Math.cos(e));
}

export function createLighting(scene, renderer, M) {
  const sky = createSky();
  scene.add(sky.mesh);

  const sun = new THREE.DirectionalLight(0xffb070, 2.4);
  sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096);
  sun.shadow.bias = -0.0004;
  sun.shadow.normalBias = 0.04;
  scene.add(sun, sun.target);

  const hemi = new THREE.HemisphereLight(0x9fb0c8, 0x40372c, 0.75);
  scene.add(hemi);

  scene.fog = new THREE.FogExp2(0xa89584, 0.0018);

  // 廊棚下每 14m 一盏真实点光源，照亮石板路；其余灯笼只靠自发光 + bloom
  const lanternLights = [];
  for (const c of corridors) {
    for (let x = c.x0 + 6; x < c.x1 - 2; x += 14) {
      const pl = new THREE.PointLight(0xff8a3a, 0, 11, 2);
      pl.position.set(x, 2.4, 6.8); // 与 houses-south 灯笼挂钩同一条线（z=6.8）
      scene.add(pl);
      lanternLights.push(pl);
    }
  }

  // 环境贴图：只拿天空做 PMREM
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene();
  const envSky = createSky();
  envSky.mesh.onBeforeRender = () => {};
  envSky.uniforms.discIntensity.value = 0;
  envScene.add(envSky.mesh);
  let envKey = null; let envRT = null;

  const warm = new THREE.Color(0xffb878); const ember = new THREE.Color(0xff6a2a);
  const hemiWarm = new THREE.Color(0xa7b3c6); const hemiBlue = new THREE.Color(0x7d8db0);

  function update(t, focus = new THREE.Vector3(), shadowSize = 300) {
    const k = clamp01(t / L.duration);
    const dir = sunDirection(t);
    sky.set(dir, k);

    sun.color.copy(warm).lerp(ember, k);
    sun.intensity = lerp(2.6, 1.1, k);
    hemi.color.copy(hemiWarm).lerp(hemiBlue, k);
    hemi.intensity = lerp(1.25, 0.9, k); // 太阳只有几度高，大部分地方在长阴影里，天光要撑住暗部
    scene.fog.color.copy(sky.horizonColor(k, 0.45));
    renderer.toneMappingExposure = lerp(0.85, 0.95, k);

    const lantern = lerp(L.lanternStart, L.lanternEnd, smoothstep(0, 0.9, k));
    M.setLanternLevel(lantern);
    for (const pl of lanternLights) pl.intensity = 9 * lantern;

    // 阴影相机跟着画面焦点走，按纹素对齐防止抖动
    const half = shadowSize / 2;
    const cam = sun.shadow.camera;
    cam.left = -half; cam.right = half; cam.top = half; cam.bottom = -half;
    cam.near = 1; cam.far = 1200;
    cam.updateProjectionMatrix();
    const texel = shadowSize / sun.shadow.mapSize.x;
    const f = focus.clone(); f.x = Math.round(f.x / texel) * texel; f.z = Math.round(f.z / texel) * texel;
    sun.target.position.copy(f);
    sun.position.copy(f).addScaledVector(dir, 500);
    sun.target.updateMatrixWorld();

    const key = Math.floor(t / ENV_STEP);
    if (key !== envKey) {
      envKey = key;
      envSky.set(sunDirection(key * ENV_STEP), clamp01((key * ENV_STEP) / L.duration));
      if (envRT) envRT.dispose();
      envRT = pmrem.fromScene(envScene, 0, 1, 5000);
      scene.environment = envRT.texture;
      scene.environmentIntensity = lerp(0.8, 0.5, k);
    }
  }

  return { sun, hemi, sky, update };
}
