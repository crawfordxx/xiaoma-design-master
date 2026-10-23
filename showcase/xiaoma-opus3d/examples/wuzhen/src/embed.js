// 打包入口（scripts/build.mjs 打成 dist/wuzhen-embed.js，全局名 WuzhenScene）
// 两种用法：
//   1. 自动挂载：<div data-wuzhen='{"quality":"auto","time":55}' style="height:600px"></div>
//   2. 手动挂载：const v = await WuzhenScene.mount(el, { quality: 'medium' }); v.dispose();
import { mount } from './viewer.js';

export { mount };

function autoMount() {
  for (const el of document.querySelectorAll('[data-wuzhen]')) {
    if (el.__wuzhen) continue;
    let opts = {};
    try { opts = JSON.parse(el.dataset.wuzhen || '{}'); } catch (e) { console.error('[wuzhen] data-wuzhen 不是合法 JSON', e); }
    el.__wuzhen = mount(el, opts);
  }
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', autoMount);
else autoMount();
