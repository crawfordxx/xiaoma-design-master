// 可取消的演示运行：页面上「点一下就自己跑一遍」的演示（Agent 工作台、生成方案、逐步亮起）都用它排时间。
// 所有等待都经 run.wait()；用户换选项、重来、离开时 run.cancel()，正在跑的整条链立刻停，不会和新的一轮打架。
export class Cancelled extends Error {
  constructor() { super('cancelled'); this.name = 'Cancelled' }
}
export const isCancel = (e) => e instanceof Cancelled

export class Run {
  constructor(speed = 1) {
    this.speed = speed
    this.cancelled = false
    this.timers = new Set()
    this.rejects = new Set()
  }
  wait(ms) {
    if (this.cancelled) return Promise.reject(new Cancelled())
    return new Promise((resolve, reject) => {
      const t = setTimeout(() => {
        this.timers.delete(t)
        this.rejects.delete(reject)
        this.cancelled ? reject(new Cancelled()) : resolve()
      }, ms / this.speed)
      this.timers.add(t)
      this.rejects.add(reject)
    })
  }
  check() { if (this.cancelled) throw new Cancelled() }
  cancel() {
    this.cancelled = true
    this.timers.forEach(clearTimeout)
    this.timers.clear()
    this.rejects.forEach((r) => r(new Cancelled()))
    this.rejects.clear()
  }
}

/** 逐字打出文本（Agent 思考、输入框里的需求）。 */
export async function typeText(run, el, text, cps = 28) {
  el.textContent = ''
  for (const ch of text) {
    el.textContent += ch
    await run.wait(1000 / cps)
  }
}

/** 数字从 0 滚到目标值，带千分位；文字用等宽数字（.num）才不抖。 */
export function countUp(el, to, { dur = 1200, dec = 0, pre = '', suf = '' } = {}) {
  const t0 = performance.now()
  const fmt = (v) => pre + v.toLocaleString('zh-CN', { minimumFractionDigits: dec, maximumFractionDigits: dec }) + suf
  return new Promise((resolve) => {
    const tick = (now) => {
      const p = Math.min(1, (now - t0) / dur)
      el.textContent = fmt(to * (1 - Math.pow(1 - p, 3)))
      p < 1 ? requestAnimationFrame(tick) : resolve()
    }
    requestAnimationFrame(tick)
  })
}
