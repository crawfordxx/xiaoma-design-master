// 打包入口（scripts/build.mjs 打成 dist/scene-embed.js，全局名 Scene3D）
// 两种用法：
//   1. 自动挂载：<div data-scene='{"quality":"auto","time":55}' style="height:600px"></div>
//   2. 手动挂载：const v = await Scene3D.mount(el, { quality: 'medium' }); v.dispose();
import { mount } from './viewer.js';

export { mount };

function autoMount() {
  for (const el of document.querySelectorAll('[data-scene]')) {
    if (el.__scene) continue;
    let opts = {};
    try { opts = JSON.parse(el.dataset.scene || '{}'); } catch (e) { console.error('[scene] data-scene 不是合法 JSON', e); }
    el.__scene = mount(el, opts);
  }
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', autoMount);
else autoMount();
