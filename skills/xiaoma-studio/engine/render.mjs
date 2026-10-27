#!/usr/bin/env node
// xiaoma-studio 渲染器：无头 Chromium 逐帧 seek(t) 截图 → ffmpeg 编码。
//
//   node render.mjs comp.html --out out/video.mp4            整片
//   node render.mjs comp.html --sheet out/sheet.jpg          每拍一帧的拼图（先看它，再出整片）
//   node render.mjs comp.html --stills 0.5,2,4.25 --dir out  指定时刻的静帧
//   node render.mjs deck.html --slides out/slides --pdf out/deck.pdf   幻灯片逐页 PNG / PDF
//   选项：--fps 60  --from 0 --to 8  --subframes 8 --shutter 180（运动模糊） --audio a.wav  --crf 16  --scale 0.5  --chrome <path>
import { spawn } from 'node:child_process';
import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright-core';
import { findChrome } from './chrome.mjs';

const argv = process.argv.slice(2);
const input = argv.find((a) => !a.startsWith('--') && !argv[argv.indexOf(a) - 1]?.startsWith('--'));
const opt = (name, def) => {
  const i = argv.indexOf('--' + name);
  return i < 0 ? def : argv[i + 1];
};
if (!input) {
  console.error('用法: node render.mjs <composition.html> [--out out.mp4 | --sheet sheet.jpg | --stills t1,t2 --dir dir]');
  process.exit(1);
}


function ffmpeg(args, { stdin = false } = {}) {
  const p = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...args], { stdio: [stdin ? 'pipe' : 'ignore', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => p.on('close', (c) => (c === 0 ? res() : rej(new Error('ffmpeg 退出码 ' + c)))));
  return { proc: p, done };
}

async function open(scale) {
  const browser = await chromium.launch({ executablePath: findChrome(opt('chrome')), args: ['--allow-file-access-from-files', '--autoplay-policy=no-user-gesture-required', '--hide-scrollbars'] });
  const page = await browser.newPage({ viewport: { width: 640, height: 360 }, deviceScaleFactor: scale });
  page.on('pageerror', (e) => console.error('[页面错误]', e.message));
  page.on('console', (m) => m.type() === 'error' && console.error('[console]', m.text()));
  const url = pathToFileURL(resolve(input)).href + '?render=1';
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__ms && window.__ms.meta && window.__ms.meta.duration > 0, null, { timeout: 30000 });
  const meta = await page.evaluate(() => window.__ms.meta);
  await page.setViewportSize({ width: meta.width, height: meta.height });
  await page.evaluate(() => window.__ms.seek(0));
  // 改视口后的第一张截图可能拿到旧尺寸下的合成帧（底部一截是顶部内容）：等两帧再截一张丢掉
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  await page.screenshot({ type: 'png' });
  return { browser, page, meta };
}

const seekShot = async (page, t, type = 'png') => {
  await page.evaluate((tt) => window.__ms.seek(tt), t);
  return page.screenshot({ type, ...(type === 'jpeg' ? { quality: 92 } : {}) });
};

async function renderVideo() {
  const scale = +opt('scale', 1);
  const { browser, page, meta } = await open(scale);
  const fps = +opt('fps', meta.fps);
  const sub = Math.max(1, +opt('subframes', 1));
  const shutter = Math.min(360, Math.max(0, +opt('shutter', 180))) / 360;   // 快门角：180° = 曝光半帧
  const from = +opt('from', 0);
  const to = +opt('to', meta.duration);
  const out = resolve(opt('out', 'out/video.mp4'));
  mkdirSync(dirname(out), { recursive: true });
  const audio = opt('audio');
  const crf = opt('crf', '16');
  const frames = Math.round((to - from) * fps);

  // 每帧的 sub 个子帧连续送进去：tmix 在每组最后一个子帧处正好平均完这一组，再只保留这些帧。
  const vf = sub > 1 ? [`tmix=frames=${sub}`, `select=eq(mod(n\\,${sub})\\,${sub - 1})`, `setpts=N/(${fps}*TB)`] : [];
  const args = ['-f', 'image2pipe', '-framerate', String(fps * sub), '-i', '-'];
  if (audio) args.push('-ss', String(from), '-i', resolve(audio));
  if (vf.length) args.push('-vf', vf.join(','));
  args.push('-c:v', 'libx264', '-preset', 'medium', '-crf', crf, '-pix_fmt', 'yuv420p', '-r', String(fps), '-movflags', '+faststart');
  // 截图是 sRGB，标成 BT.709，各平台播放器才不会按 BT.601 解释而偏色
  args.push('-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-x264-params', 'colorprim=bt709:transfer=bt709:colormatrix=bt709');
  if (audio) args.push('-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-shortest');
  args.push(out);
  const { proc, done } = ffmpeg(args, { stdin: true });

  const started = Date.now();
  for (let i = 0; i < frames; i++) {
    for (let s = 0; s < sub; s++) {
      // 子帧以帧时刻为中心，跨度 = 快门角对应的那一段，第 0 帧也有拖影
      const t = Math.max(0, from + (i + ((s + 0.5) / sub - 0.5) * shutter) / fps);
      const buf = await seekShot(page, t);
      if (!proc.stdin.write(buf)) await new Promise((r) => proc.stdin.once('drain', r));
    }
    if (i % fps === 0) process.stdout.write(`\r渲染 ${i}/${frames} 帧  ${((Date.now() - started) / 1000).toFixed(0)}s`);
  }
  proc.stdin.end();
  await done;
  await browser.close();
  console.log(`\n完成 ${out}  (${frames} 帧, ${fps}fps${sub > 1 ? `, ${sub} 子帧运动模糊、快门 ${Math.round(shutter * 360)}°` : ''})`);
}

/** 时刻列表：--every beat（默认，每拍一帧）或 --every 0.5（秒）。 */
function sheetTimes(meta) {
  const every = opt('every', 'beat');
  const step = every === 'beat' ? 60 / meta.bpm : +every;
  const ts = [];
  for (let t = (meta.beatOffset || 0) + step * 0.5; t < meta.duration; t += step) ts.push(+t.toFixed(3));
  const max = +opt('max', 48);
  return ts.length > max ? ts.filter((_, i) => i % Math.ceil(ts.length / max) === 0) : ts;
}

async function renderStills(times, dir, label) {
  const { browser, page, meta } = await open(+opt('scale', 1));
  mkdirSync(dir, { recursive: true });
  const files = [];
  for (const [i, t] of times.entries()) {
    await page.evaluate((tt) => window.__ms.seek(tt), t);
    if (label) {
      await page.evaluate((txt) => {
        let el = document.getElementById('__ms_label');
        if (!el) {
          el = document.createElement('div');
          el.id = '__ms_label';
          el.style.cssText = 'position:fixed;left:0;top:0;z-index:2147483647;background:#000c;color:#ff0;font:bold 28px ui-monospace,monospace;padding:6px 12px';
          document.body.appendChild(el);
        }
        el.textContent = txt;
      }, `${t.toFixed(2)}s · b${(t / (60 / meta.bpm)).toFixed(1)}`);
    }
    const f = join(dir, `${String(i).padStart(3, '0')}.png`);
    writeFileSync(f, await page.screenshot({ type: 'png' }));
    files.push(f);
  }
  await browser.close();
  return { files, meta };
}

async function renderSheet() {
  const out = resolve(opt('sheet'));
  const tmp = join(tmpdir(), 'ms-sheet-' + process.pid);
  const probe = await open(0.25);
  const times = sheetTimes(probe.meta);
  await probe.browser.close();
  const { files, meta } = await renderStills(times, tmp, true);
  const cols = meta.width >= meta.height ? 4 : 6;
  const rows = Math.ceil(files.length / cols);
  const w = meta.width >= meta.height ? 480 : 270;
  mkdirSync(dirname(out), { recursive: true });
  await ffmpeg(['-framerate', '1', '-i', join(tmp, '%03d.png'), '-vf', `scale=${w}:-2,tile=${cols}x${rows}:padding=4:color=white`, '-frames:v', '1', '-q:v', '3', out]).done;
  rmSync(tmp, { recursive: true, force: true });
  console.log(`拼图 ${out}  (${files.length} 帧: ${times.join(', ')})`);
}

/** 幻灯片：每页定格点（window.__ms.marks）各截一张 PNG，可再拼成 PDF。 */
async function renderDeck() {
  const probe = await open(1);
  const marks = await probe.page.evaluate(() => window.__ms.marks || []);
  await probe.browser.close();
  if (!marks.length) throw new Error('页面没有 window.__ms.marks —— 幻灯片请用 MS.deck()');
  const dir = resolve(opt('slides', join(tmpdir(), 'ms-deck-' + process.pid)));
  const { files, meta } = await renderStills(marks, dir, false);
  console.log(`幻灯片 PNG ×${files.length} → ${dir}`);
  const pdf = opt('pdf');
  if (!pdf) return;
  const html = `<!doctype html><style>@page{size:${meta.width}px ${meta.height}px;margin:0}body{margin:0}img{display:block;width:${meta.width}px;height:${meta.height}px;page-break-after:always}</style>` + files.map((f) => `<img src="${pathToFileURL(f).href}">`).join('');
  const page0 = join(dir, '_deck.html');
  writeFileSync(page0, html);
  const browser = await chromium.launch({ executablePath: findChrome(opt('chrome')), args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage();
  await page.goto(pathToFileURL(page0).href, { waitUntil: 'load' });
  mkdirSync(dirname(resolve(pdf)), { recursive: true });
  await page.pdf({ path: resolve(pdf), width: meta.width + 'px', height: meta.height + 'px', printBackground: true });
  await browser.close();
  rmSync(page0);
  console.log(`PDF → ${resolve(pdf)}`);
}

if (opt('sheet')) await renderSheet();
else if (opt('slides') || opt('pdf')) await renderDeck();
else if (opt('stills')) {
  const dir = resolve(opt('dir', 'out/stills'));
  const { files } = await renderStills(opt('stills').split(',').map(Number), dir, false);
  console.log('静帧:\n' + files.join('\n'));
} else await renderVideo();
