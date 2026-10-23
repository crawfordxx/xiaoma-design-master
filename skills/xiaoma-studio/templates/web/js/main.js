// 页面入口：平滑滚动 → 入场时间线 → 各版块滚动触发 → 演示台 → 展厅自动演示。
// 动效分三层，别混：入场（只播一次）、滚动触发（进入视口播一次，不倒放）、交互（用户点了才动）。
import { initSmooth, scrollToEl, gsap, ScrollTrigger } from './core/smooth.js'
import { splitLines, chars } from './core/split.js'
import { initCursor, magnetic } from './core/cursor.js'
import { Run, isCancel, typeText } from './core/run.js'
import { initAutopilot } from './core/autopilot.js'

const $ = (s, r = document) => r.querySelector(s)
const $$ = (s, r = document) => [...r.querySelectorAll(s)]
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches

initSmooth()
initCursor()
magnetic($$('.btn--main'))

// ---------- 导航：往下滚收起、往上滚出现；压在 data-theme="dark" 的版块上自动反白 ----------
const nav = $('#nav')
let lastY = 0
ScrollTrigger.create({
  onUpdate: (self) => {
    const y = self.scroll()
    nav.classList.toggle('is-scrolled', y > 40)
    nav.classList.toggle('is-hidden', y > lastY && y > 400)
    lastY = y
  },
})
for (const sec of $$('[data-theme="dark"]')) {
  ScrollTrigger.create({ trigger: sec, start: 'top 44px', end: 'bottom 44px', onToggle: (s) => nav.classList.toggle('is-dark', s.isActive) })
}

// ---------- 入场：口号逐字从遮罩下升起，其余依次上浮 ----------
const heroTitle = splitLines($('.hero [data-split]'))
if (!reduced) {
  gsap.set(['.hero .kicker', '.hero .lede', '.hero__ctas'], { opacity: 0, y: 30 })
  gsap.timeline({ delay: 0.2 })
    .from(chars(heroTitle), { yPercent: 110, duration: 1.1, stagger: 0.035, ease: 'power4.out' })
    .to(['.hero .kicker', '.hero .lede', '.hero__ctas'], { opacity: 1, y: 0, duration: 1, stagger: 0.1, ease: 'power3.out' }, '-=.7')
}

// ---------- 滚动触发：标题拆字、卡片依次上浮。只播一次，不跟着滚动来回倒放 ----------
if (!reduced) {
  for (const el of $$('.sec [data-split], .sec .title')) {
    const target = el.matches('[data-split]') ? chars(splitLines(el)) : el
    gsap.from(target, { yPercent: el.matches('[data-split]') ? 110 : 0, y: el.matches('[data-split]') ? 0 : 40, opacity: el.matches('[data-split]') ? 1 : 0, duration: 1, stagger: 0.03, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 85%', once: true } })
  }
  for (const group of ['.contrast li', '.cell', '.step']) {
    const els = $$(group)
    if (els.length) gsap.from(els, { y: 60, opacity: 0, duration: 1, stagger: 0.08, ease: 'power3.out', scrollTrigger: { trigger: els[0].parentElement, start: 'top 78%', once: true } })
  }
}

// ---------- 演示台：选条件 → 一步步做 → 出产物。所有等待经 Run，换条件或重来时整条链取消 ----------
for (const group of $$('.chips')) {
  group.addEventListener('click', (e) => {
    const chip = e.target.closest('.chip')
    if (!chip) return
    $$('.chip', group).forEach((c) => c.classList.toggle('is-on', c === chip))
    resetDemo()
  })
}
const agent = $('#agent')
const log = $('[data-log]', agent)
let run = null
let raf = 0
function resetDemo() {
  run?.cancel()
  cancelAnimationFrame(raf)
  log.innerHTML = ''
  $('[data-result]', agent).hidden = true
  $('[data-status]', agent).textContent = '待命'
  $('[data-timer]', agent).textContent = '0.0s'
  agent.classList.remove('beam', 'is-working')
}
// 每一步写成「动词 + 对象 + 结论」，结论里带一个具体数字或名字，才像真的在做事。
// 步骤内容要跟着访客选的条件变——写死的文案一换条件就露馅
const picked = () => $$('.chips').map((g) => $('.chip.is-on', g)?.textContent).filter(Boolean)
const steps = () => [`读取你选的条件：${picked().join('、')}`, '查资料：找到 12 条，3 条标「待核」', '排方案：按条件拆成 3 段', '自查：没有重复、没有冲突', '排版产物，准备导出']
async function playDemo() {
  resetDemo()
  run = new Run()
  const r = run
  const t0 = performance.now()
  const tick = () => { $('[data-timer]', agent).textContent = ((performance.now() - t0) / 1000).toFixed(1) + 's'; raf = requestAnimationFrame(tick) }
  tick()
  agent.classList.add('beam', 'is-working')
  $('[data-status]', agent).textContent = '工作中'
  try {
    for (const text of steps()) {
      const li = document.createElement('li')
      li.innerHTML = '<i></i><span></span>'
      log.append(li)
      await typeText(r, li.querySelector('span'), text, 40)
      await r.wait(500)
      li.classList.add('is-done')
    }
    $('[data-status]', agent).textContent = '完成'
    $('[data-result]', agent).hidden = false
    gsap.from('[data-result]', { y: 20, opacity: 0, duration: 0.8, ease: 'power3.out' })
  } catch (e) {
    if (!isCancel(e)) throw e
  } finally {
    cancelAnimationFrame(raf)
    agent.classList.remove('beam', 'is-working')
  }
}
$('[data-action="run"]').addEventListener('click', playDemo)
$('[data-action="again"]').addEventListener('click', resetDemo)

// ---------- 展厅自动演示：?autoplay=1 打开才启用 ----------
initAutopilot(async (r) => {
  await scrollToEl('#top', { duration: 2 }); await r.wait(4000)
  await scrollToEl('#pain', { duration: 2.2 }); await r.wait(4000)
  await scrollToEl('#demo', { duration: 2.2 }); await playDemo(); await r.wait(5000)
  await scrollToEl('#ability', { duration: 2.2 }); await r.wait(5000)
  await scrollToEl('#steps', { duration: 2.2 }); await r.wait(6000)
  await scrollToEl('#contact', { duration: 2.4 }); await r.wait(6000)
}, { onStop: resetDemo })
