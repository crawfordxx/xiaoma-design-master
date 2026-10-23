#!/usr/bin/env node
// 不用看图也能做的自检（给不能读图的模型，也给能读图的模型做第二道保险）。
//   node lint.mjs comp.html [--samples 24]
// 1. 确定性：同一批时刻先顺序渲染、再打乱顺序渲染，像素不同 = 有帧间状态（残留层、只在某个镜头里清理的元素）。
// 2. 对比度：每个可见文字元素与其背后底色的对比度 < 3:1（WCAG 大字标准）即报，抓「亮底白字」。
// 3. 重叠：两个可见文字块相交面积超过较小者的 25% 即报，抓「上一个镜头的标题没退场」。
// 装饰性元信息（.hud / .meta / [data-decor] 内的字）不查对比度与重叠。
import { existsSync, readdirSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright-core';

const argv = process.argv.slice(2);
const input = argv.find((a) => !a.startsWith('--'));
const opt = (n, d) => { const i = argv.indexOf('--' + n); return i < 0 ? d : argv[i + 1]; };
if (!input) { console.error('用法: node lint.mjs <composition.html> [--samples 24]'); process.exit(1); }

function findChrome() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const cache = join(homedir(), process.platform === 'darwin' ? 'Library/Caches/ms-playwright' : '.cache/ms-playwright');
  const c = [];
  if (existsSync(cache)) for (const d of readdirSync(cache).sort().reverse()) {
    if (d.startsWith('chromium_headless_shell-')) c.push(join(cache, d, 'chrome-headless-shell-mac-arm64/chrome-headless-shell'), join(cache, d, 'chrome-headless-shell-mac-x64/chrome-headless-shell'), join(cache, d, 'chrome-headless-shell-linux64/chrome-headless-shell'));
    if (d.startsWith('chromium-')) c.push(join(cache, d, 'chrome-mac-arm64/Chromium.app/Contents/MacOS/Chromium'), join(cache, d, 'chrome-linux/chrome'));
  }
  c.push('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium');
  const hit = c.find((p) => existsSync(p));
  if (!hit) throw new Error('找不到 Chromium/Chrome，设置 CHROME_PATH');
  return hit;
}

const browser = await chromium.launch({ executablePath: findChrome(), args: ['--allow-file-access-from-files'] });
const page = await browser.newPage({ viewport: { width: 640, height: 360 } });
page.on('pageerror', (e) => console.error('[页面错误]', e.message));
await page.goto(pathToFileURL(resolve(input)).href + '?render=1', { waitUntil: 'load' });
await page.waitForFunction(() => window.__ms?.meta?.duration > 0, null, { timeout: 30000 });
const meta = await page.evaluate(() => window.__ms.meta);
await page.setViewportSize({ width: meta.width, height: meta.height });

const N = +opt('samples', 24);
const marks = await page.evaluate(() => window.__ms.marks || null);
const times = marks || Array.from({ length: N }, (_, i) => +(((i + 0.5) / N) * meta.duration).toFixed(3));
const shot = async (t) => { await page.evaluate((x) => window.__ms.seek(x), t); return page.screenshot({ type: 'png' }); };

// ---------- 1. 确定性 ----------
const forward = new Map();
for (const t of times) forward.set(t, await shot(t));
const shuffled = [...times].sort((a, b) => ((a * 7919) % 1) - ((b * 7919) % 1)).reverse();
const bad = [];
for (const t of shuffled) {
  const b = await shot(t);
  const a = forward.get(t);
  if (!a.equals(b)) {
    const diff = await page.evaluate(async ([x, y]) => {   // 在页面里解码比较，得到差异像素占比
      const load = (s) => new Promise((r) => { const i = new Image(); i.onload = () => r(i); i.src = 'data:image/png;base64,' + s; });
      const [ia, ib] = await Promise.all([load(x), load(y)]);
      const w = 320, h = Math.round(ia.height * 320 / ia.width);
      const c = new OffscreenCanvas(w, h), g = c.getContext('2d');
      g.drawImage(ia, 0, 0, w, h); const da = g.getImageData(0, 0, w, h).data;
      g.drawImage(ib, 0, 0, w, h); const db = g.getImageData(0, 0, w, h).data;
      let n = 0; for (let i = 0; i < da.length; i += 4) if (Math.abs(da[i] - db[i]) + Math.abs(da[i + 1] - db[i + 1]) + Math.abs(da[i + 2] - db[i + 2]) > 24) n++;
      return n / (w * h);
    }, [a.toString('base64'), b.toString('base64')]);
    if (diff > 0.002) bad.push(`${t}s(${(diff * 100).toFixed(1)}%)`);
  }
}
console.log(bad.length ? `✗ 确定性：${bad.length} 个时刻乱序渲染结果不同 → 有帧间状态：${bad.slice(0, 12).join(' ')}` : '✓ 确定性：乱序渲染与顺序渲染一致');

// ---------- 2 + 3. 对比度与重叠 ----------
// 对比度按真实像素算：先读出每个文字块的位置和颜色，再把文字设为透明截图，取文字框内背景的平均亮度。
const lowC = new Map(), overlaps = new Map();
const HIDE = '#stage, #stage * { color: transparent !important; -webkit-text-stroke-color: transparent !important; text-shadow: none !important; }';
for (const t of times) {
  await page.evaluate((x) => window.__ms.seek(x), t);
  const r = await page.evaluate(() => {
    const parse = (s) => { const m = s.match(/[\d.]+/g); return m ? m.map(Number) : [0, 0, 0, 0]; };
    const effOpacity = (el) => { let o = 1; for (let e = el; e && e !== document.documentElement; e = e.parentElement) { const s = getComputedStyle(e); if (s.display === 'none' || s.visibility === 'hidden') return 0; o *= +s.opacity; } return o; };
    const items = [];
    const walker = document.createTreeWalker(document.getElementById('stage') || document.body, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const n = walker.currentNode, txt = n.textContent.trim();
      if (txt.length < 2) continue;
      const el = n.parentElement;
      if (el.closest('#ms-bar,#__ms_label,.hud,.meta,[data-decor]')) continue;   // 装饰性元信息允许很淡
      if (effOpacity(el) < 0.6) continue;
      const s = getComputedStyle(el);
      const fg = parse(s.color);
      if (fg.length === 4 && fg[3] < 0.5) continue;           // 透明字（渐变填字等）跳过
      const range = document.createRange(); range.selectNodeContents(n);
      const rb = range.getBoundingClientRect(), eb = el.getBoundingClientRect();
      // 字体的 ascent/descent 会让文字框超出行框；和元素框取交集，避免大数字「压住」下方的单位
      const box = { left: Math.max(rb.left, eb.left), top: Math.max(rb.top, eb.top), right: Math.min(rb.right, eb.right), bottom: Math.min(rb.bottom, eb.bottom) };
      box.width = box.right - box.left; box.height = box.bottom - box.top;
      if (box.width < 4 || box.height < 4 || box.right < 0 || box.bottom < 0 || box.left > innerWidth || box.top > innerHeight) continue;
      items.push({ txt: txt.slice(0, 16), fg, size: parseFloat(s.fontSize), box: [box.left, box.top, box.right, box.bottom], el: el.closest('[id]')?.id || el.className || el.tagName });
    }
    return items;
  });
  if (!r.length) continue;
  const tag = await page.addStyleTag({ content: HIDE });
  const bgShot = (await page.screenshot({ type: 'png' })).toString('base64');
  await tag.evaluate((n) => n.remove());
  const res = await page.evaluate(async ([png, items]) => {
    const img = await new Promise((ok) => { const i = new Image(); i.onload = () => ok(i); i.src = 'data:image/png;base64,' + png; });
    const c = new OffscreenCanvas(img.width, img.height), g = c.getContext('2d'); g.drawImage(img, 0, 0);
    const k = img.width / innerWidth;
    const lum = ([r, gg, b]) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(r) + 0.7152 * f(gg) + 0.0722 * f(b); };
    return items.map((it) => {
      const [x0, y0, x1, y1] = it.box.map((v) => Math.round(v * k));
      const w = Math.max(1, Math.min(img.width, x1) - Math.max(0, x0)), h = Math.max(1, Math.min(img.height, y1) - Math.max(0, y0));
      const d = g.getImageData(Math.max(0, x0), Math.max(0, y0), w, h).data;
      let sum = 0, n = 0;
      for (let i = 0; i < d.length; i += 16) { sum += lum([d[i], d[i + 1], d[i + 2]]); n++; }
      const Lb = sum / n, Lf = lum(it.fg);
      return { ...it, contrast: (Math.max(Lb, Lf) + 0.05) / (Math.min(Lb, Lf) + 0.05) };
    });
  }, [bgShot, r]);
  for (const it of res) {
    const need = it.size >= 24 ? 3 : 2;            // 大字 3:1；小号元信息放宽到 2:1
    if (it.contrast < need) lowC.set(it.txt, `${it.txt}（${it.contrast.toFixed(1)}:1 @${t}s）`);
  }
  for (let i = 0; i < res.length; i++) for (let j = i + 1; j < res.length; j++) {
    const [a, b] = [res[i].box, res[j].box];
    const ix = Math.min(a[2], b[2]) - Math.max(a[0], b[0]), iy = Math.min(a[3], b[3]) - Math.max(a[1], b[1]);
    if (ix <= 0 || iy <= 0 || res[i].el === res[j].el) continue;
    const small = Math.min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]));
    if (ix * iy > 0.25 * small) overlaps.set(res[i].txt + '|' + res[j].txt, `「${res[i].txt}」×「${res[j].txt}」@${t}s`);
  }
}
console.log(lowC.size ? `✗ 对比度：${lowC.size} 处文字对比度 < 3:1 → ${[...lowC.values()].slice(0, 10).join('；')}` : '✓ 对比度：可见文字均 ≥ 3:1');
console.log(overlaps.size ? `✗ 重叠：${overlaps.size} 对文字互相压住 → ${[...overlaps.values()].slice(0, 10).join('；')}` : '✓ 重叠：没有互相压住的文字');
console.log('说明：canvas 里画的字不在检查范围内；渐变填色的字会跳过；对比度取文字框内背景像素的平均亮度。');
await browser.close();
process.exit(bad.length || lowC.size || overlaps.size ? 2 : 0);
