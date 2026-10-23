// 确认无头浏览器拿到的是真 GPU（而不是软件渲染或没有 WebGL2）
import { launch } from './browser.mjs';
const b = await launch(); const p = await b.newPage();
const r = await p.evaluate(() => {
  const gl = document.createElement('canvas').getContext('webgl2');
  if (!gl) return null;
  const ext = gl.getExtension('WEBGL_debug_renderer_info');
  return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'unknown';
});
await b.close();
if (!r) { console.error('✗ 没有 WebGL2：检查 browser.mjs 里的 --use-angle 参数（见 pitfalls.md“环境”）'); process.exit(1); }
const soft = /swiftshader|llvmpipe|software/i.test(r);
console.log(`${soft ? '⚠ 软件渲染，会非常慢' : '✓'} ${r}`);
