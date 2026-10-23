#!/usr/bin/env node
// 新建一个自包含的项目目录：复制模板 + 运行时文件，项目可以整体搬走。
//   node engine/init.mjs <目录> [video|slides|web]
import { cpSync, existsSync, mkdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const [dir, kind = 'video'] = process.argv.slice(2);
if (!dir || !['video', 'slides', 'web'].includes(kind)) {
  console.error('用法: node engine/init.mjs <目录> [video|slides|web]');
  process.exit(1);
}
const out = resolve(dir);
// 网页：复制 Vite 骨架（不带 node_modules / dist），规则见 references/web.md
if (kind === 'web') {
  if (existsSync(join(out, 'index.html'))) { console.log('目录里已有 index.html，未覆盖'); process.exit(0); }
  cpSync(join(here, '..', 'templates', 'web'), out, { recursive: true, filter: (p) => !/[\\/](node_modules|dist)([\\/]|$)/.test(p) });
  console.log(`已创建 ${out}
  开发：cd ${out} && npm install && npm run dev
  体检：node ${join(here, 'webcheck.mjs')} http://localhost:5173/ --widths 390,1024,1280,1440,1920
  字体：python3 ${join(here, 'fontcheck.py')} <fonts.css> --chars <页面上的标题文字>`);
  process.exit(0);
}
mkdirSync(join(out, 'engine'), { recursive: true });
mkdirSync(join(out, 'out'), { recursive: true });
for (const f of ['runtime.js', 'deck.js', 'base.css', 'themes.css']) cpSync(join(here, f), join(out, 'engine', f));
const target = join(out, 'index.html');
if (existsSync(target)) console.log('index.html 已存在，未覆盖');
else cpSync(join(here, '..', 'templates', kind, 'index.html'), target);
if (!existsSync(join(out, 'STORYBOARD.md'))) cpSync(join(here, '..', 'templates', 'STORYBOARD.md'), join(out, 'STORYBOARD.md'));
console.log(`已创建 ${out}
  预览：浏览器打开 ${join(out, 'index.html')}
  拼图：node ${join(here, 'render.mjs')} ${target} --sheet ${join(out, 'out/sheet.jpg')}
  出片：node ${join(here, 'render.mjs')} ${target} --out ${join(out, 'out/video.mp4')} --audio ${join(out, 'out/audio.wav')}`);
