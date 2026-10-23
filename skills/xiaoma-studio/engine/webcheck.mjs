#!/usr/bin/env node
// 网页体检：多个宽度逐版块截图 + 不用看图也能查的问题。给官网、落地页、展厅大屏页用。
//   node webcheck.mjs <url> [--widths 390,1024,1280,1440,1920] [--height 900] [--out out/webcheck] [--wait 4000]
// 页面要先用本地服务起起来（vite dev / preview、任何静态服务都行），file:// 下字体和模块常常加载不了。
// 查的东西：
//   1. 横向溢出：页面比视口宽（手机上出现左右晃）。
//   2. 导航溢出：.nav / header 的内容比自身宽（加了导航项以后最常见）。
//   3. 文字出界：可见文字超出视口右边，且不在可横向滚动的容器里。
//   4. 请求失败：4xx / 5xx / 网络错误，尤其是字体子集和图片（缺一个字体子集 = 一批字回落成系统字体）。
//   5. 坏图：<img> 加载完 naturalWidth 为 0。
//   6. 控制台报错。
// 截图：每个宽度、每个顶层版块（main > section、带 id 的 section）各一张，外加 report.html 一页看全。
import { existsSync, mkdirSync, readdirSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, resolve } from 'node:path';
import { chromium } from 'playwright-core';

const argv = process.argv.slice(2);
const url = argv.find((a) => !a.startsWith('--') && !/^\d/.test(a));
const opt = (n, d) => { const i = argv.indexOf('--' + n); return i < 0 ? d : argv[i + 1]; };
if (!url) { console.error('用法: node webcheck.mjs <url> [--widths 390,1024,1280,1440,1920] [--height 900] [--out out/webcheck] [--wait 4000]'); process.exit(1); }
const widths = opt('widths', '390,1024,1280,1440,1920').split(',').map(Number);
const height = Number(opt('height', 900));
const wait = Number(opt('wait', 4000));
const out = resolve(opt('out', 'out/webcheck'));
mkdirSync(out, { recursive: true });

function findChrome() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const cache = join(homedir(), process.platform === 'darwin' ? 'Library/Caches/ms-playwright' : '.cache/ms-playwright');
  const c = [];
  if (existsSync(cache)) for (const d of readdirSync(cache).sort().reverse()) {
    if (d.startsWith('chromium-')) c.push(join(cache, d, 'chrome-mac-arm64/Chromium.app/Contents/MacOS/Chromium'), join(cache, d, 'chrome-mac/Chromium.app/Contents/MacOS/Chromium'), join(cache, d, 'chrome-linux/chrome'));
    if (d.startsWith('chromium_headless_shell-')) c.push(join(cache, d, 'chrome-headless-shell-mac-arm64/chrome-headless-shell'), join(cache, d, 'chrome-headless-shell-linux64/chrome-headless-shell'));
  }
  c.push('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium');
  const hit = c.find((p) => existsSync(p));
  if (!hit) throw new Error('找不到 Chromium/Chrome，设置 CHROME_PATH');
  return hit;
}

// 在页面里跑：找出所有问题（不依赖截图）
function inspect() {
  const vw = innerWidth;
  const issues = [];
  const de = document.documentElement;
  if (de.scrollWidth > vw + 1) issues.push(`横向溢出：页面宽 ${de.scrollWidth}px > 视口 ${vw}px`);
  for (const n of document.querySelectorAll('.nav, body > header')) {
    if (n.scrollWidth > n.clientWidth + 1) issues.push(`导航溢出：${n.className || n.tagName} 内容 ${n.scrollWidth}px > ${n.clientWidth}px`);
  }
  const scrollable = (el) => { for (let p = el.parentElement; p; p = p.parentElement) { const s = getComputedStyle(p); if (/(auto|scroll|hidden|clip)/.test(s.overflowX) && p !== document.body && p !== de) return true; } return false; };
  const seen = new Set();
  for (const el of document.querySelectorAll('h1,h2,h3,h4,p,li,a,button,span,b,em,strong,label')) {
    if (!el.childNodes.length || ![...el.childNodes].some((c) => c.nodeType === 3 && c.textContent.trim())) continue;
    const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    if (!r.width || s.visibility === 'hidden' || Number(s.opacity) === 0 || s.display === 'none') continue;
    if (r.right > vw + 1 && !scrollable(el)) {
      const t = el.textContent.trim().slice(0, 20);
      if (!seen.has(t)) { seen.add(t); issues.push(`文字出界：「${t}」右边到 ${Math.round(r.right)}px`); }
    }
  }
  for (const img of document.images) if (img.complete && img.naturalWidth === 0 && img.getAttribute('src')) issues.push(`坏图：${img.getAttribute('src')}`);
  return issues;
}

const browser = await chromium.launch({ executablePath: findChrome(), args: ['--hide-scrollbars', '--autoplay-policy=no-user-gesture-required'] });
const report = [];
let problems = 0;
for (const w of widths) {
  const page = await browser.newPage({ viewport: { width: w, height: w <= 600 ? Math.max(height, 844) : height } });
  const failed = []; const errors = [];
  page.on('requestfailed', (r) => failed.push(`${r.failure()?.errorText || '失败'} ${r.url()}`));
  page.on('response', (r) => { if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`); });
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(wait);
  // 先从头滚到底一遍，触发懒加载和「进入视口才播一次」的动画
  await page.evaluate(async () => { for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight * 0.6) { scrollTo(0, y); await new Promise((r) => setTimeout(r, 120)); } scrollTo(0, 0); });
  await page.waitForTimeout(800);
  const sections = await page.evaluate(() => {
    const list = [...document.querySelectorAll('main > section, body > section, section[id]')].filter((s, i, a) => a.indexOf(s) === i && !a.some((o) => o !== s && o.contains(s)));
    return list.map((s, i) => ({ i, id: s.id || `s${i + 1}`, top: s.getBoundingClientRect().top + scrollY }));
  });
  const shots = [];
  for (const s of sections.length ? sections : [{ i: 0, id: 'page', top: 0 }]) {
    await page.evaluate((y) => { window.lenis?.scrollTo?.(y, { immediate: true }); scrollTo(0, y); }, s.top);
    await page.waitForTimeout(1200);
    const file = `${w}-${String(s.i + 1).padStart(2, '0')}-${s.id}.png`;
    await page.screenshot({ path: join(out, file) });
    shots.push(file);
  }
  await page.evaluate(() => scrollTo(0, 0));
  const issues = [...(await page.evaluate(inspect)), ...[...new Set(failed)].map((f) => `请求失败：${f}`), ...[...new Set(errors)].map((e) => `控制台报错：${e.slice(0, 200)}`)];
  problems += issues.length;
  report.push({ w, shots, issues });
  console.log(`\n== ${w}px：${shots.length} 张截图，${issues.length ? issues.length + ' 个问题' : '没有发现问题'}`);
  for (const i of issues) console.log('  - ' + i);
  await page.close();
}
await browser.close();

const esc = (s) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[c]);
writeFileSync(join(out, 'report.html'), `<!doctype html><meta charset="utf-8"><title>webcheck</title>
<style>body{font:14px system-ui;margin:24px;background:#111;color:#eee}h2{margin:32px 0 8px}ul{color:#ffb547}.row{display:flex;gap:12px;overflow-x:auto}.row img{height:320px;border:1px solid #333}</style>
<h1>${esc(url)}</h1>${report.map((r) => `<h2>${r.w}px</h2>${r.issues.length ? `<ul>${r.issues.map((i) => `<li>${esc(i)}</li>`).join('')}</ul>` : '<p>没有发现问题</p>'}<div class="row">${r.shots.map((s) => `<a href="${s}"><img src="${s}" title="${s}"></a>`).join('')}</div>`).join('')}`);
console.log(`\n截图与汇总：${join(out, 'report.html')}`);
process.exit(problems ? 2 : 0);
