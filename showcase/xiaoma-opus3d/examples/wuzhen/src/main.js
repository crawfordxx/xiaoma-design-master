// 截图测试入口：按 URL 参数建场景，暴露 renderFrame(t) / setView(v) 给 scripts/ 下的截图、接触表、出片脚本。
// URL 参数：zones=terrain,water（默认全部） w/h=分辨率 overlay=1（叠加 layout 轮廓） t=初始时间 quality=high|medium|low
// 交互模型的入口是 viewer.js，不走这里。
import * as THREE from 'three';
import * as layout from './layout.js';
import { createScene } from './scene.js';
import * as director from './cameras.js';

const params = new URLSearchParams(location.search);
const W = Number(params.get('w')) || 1920;
const H = Number(params.get('h')) || 1080;
const zones = params.get('zones') ? params.get('zones').split(',').filter(Boolean) : undefined;

const S = await createScene({
  container: document.body, width: W, height: H, zones,
  quality: params.get('quality') || 'high', pixelRatio: 1, preserveDrawingBuffer: true,
});
window.__status = S.status;
if (params.get('overlay')) S.scene.add(layoutOverlay());

let viewOverride = null;
window.renderFrame = (t) => {
  const view = viewOverride ?? director.shotAt(t);
  S.render({ lightT: t, animT: t, view });
};
// 光照和动画分开的时刻（比如 README 动图：光照固定在一刻，船和布照常动）
window.renderAt = (lightT, animT) => {
  S.render({ lightT, animT, view: viewOverride ?? director.shotAt(lightT) });
};
window.setView = (v) => { viewOverride = v; };
window.layout = layout;
window.__three = { scene: S.scene, renderer: S.renderer, composer: S.composer, materials: S.materials }; // 调试用

window.renderFrame(Number(params.get('t')) || 0);

// 俯视叠图：把 layout 的所有轮廓画在最上层
function layoutOverlay() {
  const pts = []; const y = 30;
  const rect = (r) => {
    const c = [[r.x0, r.z0], [r.x1, r.z0], [r.x1, r.z1], [r.x0, r.z1]];
    for (let i = 0; i < 4; i++) { const a = c[i]; const b = c[(i + 1) % 4]; pts.push(a[0], y, a[1], b[0], y, b[1]); }
  };
  layout.houses.forEach((h) => { rect(h.footprint); const p = layout.pavilionFootprint(h); if (p) rect(p); });
  layout.rivers.forEach((r) => rect(r.rect));
  layout.bridges.forEach((b) => {
    const half = b.width / 2;
    rect(b.axis === 'z' ? { x0: b.at - half, x1: b.at + half, z0: b.from, z1: b.to } : { x0: b.from, x1: b.to, z0: b.at - half, z1: b.at + half });
  });
  layout.corridors.forEach(rect);
  rect(layout.dyeYard.rect);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  const lines = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: 0xff2bd6, depthTest: false, transparent: true, fog: false }));
  lines.renderOrder = 999;
  return lines;
}
