// 找浏览器：render.mjs / lint.mjs / webcheck.mjs 共用。
// 优先级：--chrome / CHROME_PATH > 系统 Chrome > Playwright 缓存里的 Chromium > chrome-headless-shell。
// 系统 Chrome 排在前面，是因为 headless-shell 的 WebGL 走 SwiftShader 软件渲染，Three.js 片又慢又可能和 GPU 出图不一致。
import { existsSync, readdirSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

const SYSTEM = [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
];

function playwrightCache() {
  const cache = process.env.PLAYWRIGHT_BROWSERS_PATH || join(homedir(), process.platform === 'darwin' ? 'Library/Caches/ms-playwright' : '.cache/ms-playwright');
  if (!existsSync(cache)) return [];
  const full = [];
  const shell = [];
  for (const d of readdirSync(cache).sort().reverse()) {
    if (d.startsWith('chromium-')) {
      full.push(join(cache, d, 'chrome-mac-arm64/Chromium.app/Contents/MacOS/Chromium'), join(cache, d, 'chrome-mac/Chromium.app/Contents/MacOS/Chromium'), join(cache, d, 'chrome-linux/chrome'), join(cache, d, 'chrome-linux64/chrome'));
    }
    if (d.startsWith('chromium_headless_shell-')) {
      shell.push(join(cache, d, 'chrome-headless-shell-mac-arm64/chrome-headless-shell'), join(cache, d, 'chrome-headless-shell-mac-x64/chrome-headless-shell'), join(cache, d, 'chrome-headless-shell-linux64/chrome-headless-shell'));
    }
  }
  return [...full, ...shell];
}

/** explicit：命令行 --chrome 的值（可为空）。 */
export function findChrome(explicit) {
  const fromUser = explicit || process.env.CHROME_PATH;
  if (fromUser) return fromUser;
  const hit = [...SYSTEM, ...playwrightCache()].find((p) => existsSync(p));
  if (!hit) throw new Error('找不到 Chrome / Chromium。设置 CHROME_PATH，或运行 npx playwright install chromium');
  return hit;
}
