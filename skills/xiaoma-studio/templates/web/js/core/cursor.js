// 跟随光标与磁吸按钮。只在精确指针设备上启用；触屏、减弱动态效果时不出现。
// 光标标签：给元素加 data-cursor="开始"，悬停时外圈放大并显示这两个字。标签只写动词，最多 4 个字。
import { gsap } from 'gsap'

const fine = () => matchMedia('(hover: hover) and (pointer: fine)').matches && !matchMedia('(prefers-reduced-motion: reduce)').matches

export function initCursor() {
  if (!fine()) return
  const el = document.createElement('div')
  el.className = 'cursor'
  el.innerHTML = '<div class="cursor__dot"></div><div class="cursor__ring"></div><div class="cursor__label"></div>'
  document.body.append(el)
  const ring = el.querySelector('.cursor__ring')
  const label = el.querySelector('.cursor__label')
  const pos = { x: innerWidth / 2, y: innerHeight / 2 }
  const lag = { ...pos }
  addEventListener('pointermove', (e) => { pos.x = e.clientX; pos.y = e.clientY }, { passive: true })
  gsap.ticker.add(() => {
    lag.x += (pos.x - lag.x) * 0.18
    lag.y += (pos.y - lag.y) * 0.18
    el.style.transform = `translate3d(${pos.x}px, ${pos.y}px, 0)`
    ring.style.transform = `translate3d(${lag.x - pos.x}px, ${lag.y - pos.y}px, 0) translate(-50%, -50%)`
  })
  document.addEventListener('pointerover', (e) => {
    const t = e.target.closest('a, button, [data-cursor]')
    el.classList.toggle('is-hover', !!t)
    label.textContent = t?.dataset.cursor || ''
    el.classList.toggle('has-label', !!t?.dataset.cursor)
  })
}

/** 磁吸：指针靠近时按钮朝指针挪一点，离开弹回。只给主 CTA 用，别全站铺。 */
export function magnetic(els, strength = 0.28) {
  if (!fine()) return
  for (const el of els) {
    const xTo = gsap.quickTo(el, 'x', { duration: 0.6, ease: 'elastic.out(1, 0.4)' })
    const yTo = gsap.quickTo(el, 'y', { duration: 0.6, ease: 'elastic.out(1, 0.4)' })
    el.addEventListener('pointermove', (e) => {
      const r = el.getBoundingClientRect()
      xTo((e.clientX - r.left - r.width / 2) * strength)
      yTo((e.clientY - r.top - r.height / 2) * strength)
    })
    el.addEventListener('pointerleave', () => { xTo(0); yTo(0) })
  }
}
