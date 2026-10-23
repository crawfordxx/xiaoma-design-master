// 逐帧出片：node scripts/render.mjs [--fps 30] [--duration 70] [--from 0] [--to N] [--workers 2] [--force] [--verify]
// 每帧调用 renderFrame(t)，t = 帧号 / fps，画面只由 t 决定；已存在的帧会跳过（可断点续渲）。
// 全部帧齐了以后用 ffmpeg 合成 out/<项目目录名>.mp4。
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { serve } from './serve.mjs';
import { launch } from './browser.mjs';

const args = { fps: 30, duration: 70, from: 0, to: null, workers: 2, force: false, verify: false, w: 1920, h: 1080, out: 'out/frames' };
const argv = process.argv.slice(2);
for (let i = 0; i < argv.length; i++) {
  const k = argv[i].replace(/^--/, '');
  if (k === 'force' || k === 'verify') args[k] = true;
  else if (k in args) { args[k] = k === 'out' ? argv[++i] : Number(argv[++i]); }
  else throw new Error(`未知参数 ${argv[i]}`);
}
const total = Math.round(args.fps * args.duration);
const last = Math.min(args.to ?? total, total);
fs.mkdirSync(args.out, { recursive: true });
const frameFile = (i) => path.join(args.out, `${String(i).padStart(5, '0')}.png`);

const server = await serve(0);
const url = `http://127.0.0.1:${server.address().port}/?w=${args.w}&h=${args.h}`;
const browser = await launch();

async function openPage() {
  const page = await browser.newPage({ viewport: { width: args.w, height: args.h } });
  page.on('pageerror', (e) => console.log(`[pageerror] ${e.message}`));
  page.on('console', (m) => { if (m.type() === 'error') console.log(`[page error] ${m.text()}`); });
  await page.goto(url);
  await page.waitForFunction(() => window.__status?.ready, null, { timeout: 300000 });
  const status = await page.evaluate(() => window.__status);
  if (status.errors.length) throw new Error(`场景加载有错误：${status.errors.join(' | ')}`);
  return page;
}

async function grab(page, t) {
  await page.evaluate((tt) => { window.setView(null); window.renderFrame(tt); }, t);
  return page.locator('canvas').screenshot({ type: 'png' });
}

try {
  if (args.verify) {
    // 确定性检查：同一个 t 在两个独立页面里渲染，像素必须完全一致
    const [a, b] = [await openPage(), await openPage()];
    for (const t of [0, 10.5, 35, 69.9]) {
      await grab(a, t + 1); // 先在 a 上渲染别的时间，确认没有残留状态
      const ha = crypto.createHash('md5').update(await grab(a, t)).digest('hex');
      const hb = crypto.createHash('md5').update(await grab(b, t)).digest('hex');
      console.log(`${ha === hb ? '✓' : '✗'} t=${t}  ${ha} ${hb}`);
    }
  } else {
    const todo = [];
    for (let i = args.from; i < last; i++) if (args.force || !fs.existsSync(frameFile(i))) todo.push(i);
    console.log(`共 ${last - args.from} 帧，待渲染 ${todo.length} 帧，${args.workers} 个并行页面`);
    const t0 = Date.now(); let done = 0;
    await Promise.all(Array.from({ length: args.workers }, async (_, w) => {
      const page = await openPage();
      for (let k = w; k < todo.length; k += args.workers) {
        const i = todo[k];
        fs.writeFileSync(frameFile(i), await grab(page, i / args.fps));
        done++;
        if (done % 60 === 0 || done === todo.length) {
          const per = (Date.now() - t0) / done;
          console.log(`${done}/${todo.length}  ${(per).toFixed(0)}ms/帧  剩余约 ${((todo.length - done) * per / 60000).toFixed(1)} 分钟`);
        }
      }
      await page.close();
    }));
    const complete = Array.from({ length: total }, (_, i) => fs.existsSync(frameFile(i))).every(Boolean);
    if (complete) {
      const mp4 = `out/${path.basename(process.cwd())}.mp4`;
      execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(args.fps), '-i', path.join(args.out, '%05d.png'),
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', mp4], { stdio: 'inherit' });
      console.log(`✓ ${mp4}`);
    } else {
      console.log('帧还没渲染齐，暂不合成视频');
    }
  }
} finally {
  await browser.close();
  server.close();
}
