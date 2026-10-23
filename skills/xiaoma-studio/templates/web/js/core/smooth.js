// 平滑滚动：Lenis 驱动，ScrollTrigger 跟随。所有「滚到某处」都走 scrollToEl，演示脚本才能 await。
import Lenis from 'lenis'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export let lenis = null

export function initSmooth() {
  // 减弱动态效果的用户不加平滑滚动
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return null
  lenis = new Lenis({ lerp: 0.085, wheelMultiplier: 0.9, touchMultiplier: 1.4, smoothWheel: true })
  lenis.on('scroll', ScrollTrigger.update)
  gsap.ticker.add((t) => lenis.raf(t * 1000))
  gsap.ticker.lagSmoothing(0)
  return lenis
}

export function scrollToEl(target, opts = {}) {
  return new Promise((resolve) => {
    if (!lenis) {
      const el = typeof target === 'string' ? document.querySelector(target) : null
      if (el) el.scrollIntoView({ behavior: 'smooth' })
      else if (typeof target === 'number') scrollTo({ top: target, behavior: 'smooth' })
      return setTimeout(resolve, 600)
    }
    lenis.scrollTo(target, { duration: 1.6, easing: (t) => 1 - Math.pow(1 - t, 4), ...opts, onComplete: resolve })
  })
}

export { gsap, ScrollTrigger }
