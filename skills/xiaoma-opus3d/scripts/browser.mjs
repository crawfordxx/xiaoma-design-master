// 共用的无头浏览器启动：Playwright 自带的 Chromium + Metal 后端（才能用上 GPU）
import { chromium } from 'playwright';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

function findChrome() {
  if (process.env.CHROME) return process.env.CHROME;
  const base = path.join(os.homedir(), 'Library/Caches/ms-playwright');
  const dirs = fs.readdirSync(base).filter((d) => /^chromium-\d+$/.test(d)).sort().reverse();
  for (const d of dirs) {
    const app = path.join(base, d, 'chrome-mac-arm64');
    if (!fs.existsSync(app)) continue;
    const bundle = fs.readdirSync(app).find((f) => f.endsWith('.app'));
    if (bundle) {
      const macos = path.join(app, bundle, 'Contents/MacOS');
      return path.join(macos, fs.readdirSync(macos)[0]);
    }
  }
  return undefined; // 交给 Playwright 自己找
}

export function launch() {
  return chromium.launch({
    headless: true,
    executablePath: findChrome(),
    args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-unsafe-webgpu'],
  });
}
