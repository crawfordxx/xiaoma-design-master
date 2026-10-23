// 交互模型：把场景挂到任意容器里，鼠标/触摸拖动旋转、滚轮/双指缩放、右键/双指平移。
// 用法：const viewer = await mount(document.getElementById('scene'), { quality: 'auto', time: 55 });
//       viewer.dispose();
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import * as layout from './layout.js';
import { createScene, QUALITY_ORDER } from './scene.js';

const DEFAULTS = {
  quality: 'auto',   // auto | high | medium | low；auto 会在帧率不够时自动降档
  time: 55,          // 光照时刻（0~70）：0 日落前，70 华灯初上
  view: { pos: [95, 55, 85], target: [-10, 0, -5], fov: 45 }, // 初始视角
  minDistance: 1.5,
  maxDistance: 420,
  hint: true,        // 显示操作提示
};
const SLOW_FRAME_MS = 25; // 平均帧时间超过它（约 40fps 以下）就降一档

function isMobile() {
  return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent) || (navigator.maxTouchPoints > 1 && window.innerWidth < 900);
}

// 相机最低高度：河道上方贴水面，其他地方不低于地面
function floorAt(x, z) {
  const wet = layout.rivers.some((r) => x > r.rect.x0 && x < r.rect.x1 && z > r.rect.z0 && z < r.rect.z1);
  return wet ? layout.LEVELS.water + 0.25 : layout.LEVELS.ground + 0.4;
}

function overlay(container, text, style) {
  const el = document.createElement('div');
  el.textContent = text;
  Object.assign(el.style, {
    position: 'absolute', pointerEvents: 'none', color: '#f3e9da', font: '13px/1.4 "PingFang SC", system-ui, sans-serif',
    textShadow: '0 1px 3px rgba(0,0,0,.8)', transition: 'opacity .6s', ...style,
  });
  container.appendChild(el);
  return el;
}

export async function mount(container, options = {}) {
  const o = { ...DEFAULTS, ...options };
  if (getComputedStyle(container).position === 'static') container.style.position = 'relative';
  const loading = overlay(container, '乌镇 · 加载中…', { inset: '0', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '15px', background: '#1b1a22' });

  let tier = o.quality === 'auto' ? (isMobile() ? 'low' : 'high') : o.quality;
  const rect = container.getBoundingClientRect();
  const S = await createScene({ container, width: rect.width || 800, height: rect.height || 450, quality: tier });
  if (S.status.errors.length) console.warn('[wuzhen] 部分区块加载失败：', S.status.errors);
  S.renderer.domElement.style.touchAction = 'none'; // 手势交给 OrbitControls，不让页面滚动抢走

  const camera = S.persp;
  camera.fov = o.view.fov;
  camera.position.set(...o.view.pos);
  const controls = new OrbitControls(camera, S.renderer.domElement);
  controls.target.set(...o.view.target);
  Object.assign(controls, {
    enableDamping: true, dampingFactor: 0.08, screenSpacePanning: false, zoomToCursor: true,
    minDistance: o.minDistance, maxDistance: o.maxDistance, maxPolarAngle: THREE.MathUtils.degToRad(88),
  });
  controls.update();

  // 焦点不许拖出场景，相机不许钻到地下或水下
  const margin = 40; const E = layout.EXTENT;
  function constrain() {
    const t = controls.target;
    t.x = THREE.MathUtils.clamp(t.x, E.x0 - margin, E.x1 + margin);
    t.z = THREE.MathUtils.clamp(t.z, E.z0 - margin, E.z1 + margin);
    t.y = THREE.MathUtils.clamp(t.y, layout.LEVELS.water, 30);
    const floor = floorAt(camera.position.x, camera.position.z);
    if (camera.position.y < floor) camera.position.y = floor;
  }

  const hint = o.hint ? overlay(container, isMobile() ? '单指旋转 · 双指缩放 / 平移' : '左键拖动旋转 · 滚轮缩放 · 右键拖动平移', { left: '12px', bottom: '10px' }) : null;
  controls.addEventListener('start', () => { if (hint) hint.style.opacity = '0'; }, { once: true });

  const ro = new ResizeObserver(([entry]) => {
    const { width, height } = entry.contentRect;
    if (width > 0 && height > 0) S.setSize(width, height);
  });
  ro.observe(container);

  // 看不见时（滚出屏幕、切到后台标签页）停止渲染
  let visible = true;
  const io = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; });
  io.observe(container);

  // 自动降档：连续 90 帧的平均帧时间太长就降一档（只降不升，避免来回跳）
  const frameTimes = [];
  function adapt(dt) {
    if (o.quality !== 'auto' || dt > 250) return; // 切回标签页时的大间隔不算
    frameTimes.push(dt);
    if (frameTimes.length < 90) return;
    const avg = frameTimes.reduce((a, b) => a + b, 0) / frameTimes.length;
    frameTimes.length = 0;
    const i = QUALITY_ORDER.indexOf(tier);
    if (avg > SLOW_FRAME_MS && i < QUALITY_ORDER.length - 1) {
      tier = QUALITY_ORDER[i + 1];
      S.setQuality(tier);
      console.info(`[wuzhen] 平均帧时间 ${avg.toFixed(1)}ms，画质降到 ${tier}`);
    }
  }

  const start = performance.now(); let last = start; let raf = 0; let frames = 0;
  function loop(now) {
    raf = requestAnimationFrame(loop);
    if (!visible || document.hidden) { last = now; return; }
    adapt(now - last); last = now;
    controls.update();
    constrain();
    S.render({ lightT: o.time, animT: (now - start) / 1000, view: { camera, target: controls.target } });
    if (++frames === 2) loading.style.opacity = '0'; // 前两帧会编译着色器，画出来之后再撤掉加载层
  }
  raf = requestAnimationFrame(loop);

  return {
    get quality() { return tier; },
    setQuality(name) { tier = name; o.quality = name; S.setQuality(name); },
    controls, camera, scene: S.scene, status: S.status,
    dispose() {
      cancelAnimationFrame(raf); ro.disconnect(); io.disconnect(); controls.dispose(); S.dispose();
      loading.remove(); hint?.remove();
    },
  };
}
