// 展厅 / 大屏自动演示：只在用 ?autoplay=1 打开时启用（记在本次会话），普通访客永远不会被自动滚动。
// 无人操作 idle 秒后按页面脚本自动滚动、自动点演示；任何触摸、点击、按键、滚轮立即交还控制。
// ?idle=20 改等待秒数，?autoplay=0 退出。
import { Run, isCancel } from './run.js'

const KEY = 'xiaoma-kiosk'

export function kioskMode(params = new URLSearchParams(location.search)) {
  try {
    if (params.get('autoplay') === '0') sessionStorage.removeItem(KEY)
    else if (params.get('autoplay') === '1' || params.has('idle')) sessionStorage.setItem(KEY, '1')
    return sessionStorage.getItem(KEY) === '1'
  } catch {
    return params.get('autoplay') === '1'
  }
}

/**
 * @param {(run: Run) => Promise<void>} script 一轮演示：滚到各节、点演示、等它跑完
 * @param {{ idle?: number, onStop?: () => void }} opt
 */
export function initAutopilot(script, { idle = 45, onStop } = {}) {
  if (!kioskMode()) return
  const params = new URLSearchParams(location.search)
  const idleMs = (Number(params.get('idle')) || idle) * 1000
  const badge = Object.assign(document.createElement('div'), { className: 'autopilot-badge', innerHTML: '<i></i><span>自动演示中 · 触摸任意位置接管</span>' })
  document.body.append(badge)
  let run = null
  let timer = 0
  const stop = () => {
    if (run) { run.cancel(); run = null; badge.classList.remove('is-on'); onStop?.() }
    clearTimeout(timer)
    timer = setTimeout(start, idleMs)
  }
  const start = async () => {
    run = new Run()
    badge.classList.add('is-on')
    try { for (;;) await script(run) } catch (e) { if (!isCancel(e)) console.error(e) }
  }
  for (const ev of ['pointerdown', 'keydown', 'wheel', 'touchstart']) addEventListener(ev, stop, { passive: true })
  timer = setTimeout(start, params.get('autoplay') === '1' ? 1500 : idleMs)
}
