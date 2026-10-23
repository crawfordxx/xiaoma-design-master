/* motion-studio deck —— HTML 幻灯片 = 带暂停点的时间轴。
 * 同一个文件：演讲时方向键逐步推进；导出时按 data-dur 连续播放成视频，或每页一张 PNG/PDF。
 *
 *   <section class="slide" data-dur="6" data-tr="push">
 *     <h1 data-fx="rise" data-in="0.2">标题</h1>
 *     <p data-fx="fade" data-step="1">按一下才出现</p>
 *   </section>
 *
 * data-fx：rise 遮罩升起 | chars 逐字升起 | fade | blur | scale 弹出 | left/right 侧入 | draw SVG 描边 | count 数字滚动(data-to) | type 打字机 | bar 宽度生长(data-to=百分比)
 * data-in：页内秒数；data-step：第 N 次按键后出现（演讲用，导出视频时按 step × data-gap 秒排布）
 * data-tr：进入本页的转场 push（默认）| fade | zoom | flood | wipe
 */
(function () {
  'use strict';
  const { prog, ease, css, $$, spring, clamp, counter, typewriter, reveal } = MS;

  const STEP_GAP = 1.1;   // 导出视频时，每个 step 之间隔多少秒
  const TR = 0.7;         // 转场时长

  function build(opts = {}) {
    const slides = $$('.slide');
    let t = 0;
    const plan = slides.map((el, i) => {
      const gap = +(el.dataset.gap || STEP_GAP);
      const items = [...el.querySelectorAll('[data-fx]')].map((node) => {
        const step = +(node.dataset.step || 0);
        const at = node.dataset.in !== undefined ? +node.dataset.in : 0;
        return { node, fx: node.dataset.fx, step, at: at + step * gap, dur: +(node.dataset.d || 0.7) };
      });
      const steps = [...new Set(items.map((x) => x.step))].sort((a, b) => a - b);
      const lastBuild = Math.max(0, ...items.map((x) => x.at + x.dur));
      const dur = Math.max(+(el.dataset.dur || 0), lastBuild + 1.2, 2);
      const p = { el, i, start: t, dur, items, tr: el.dataset.tr || (i ? 'push' : 'fade'), pauses: steps.map((s) => t + TR + s * gap + 0.85) };
      t += dur;
      return p;
    });
    const total = t;
    MS.setup({ ...opts, duration: total });
    // 暂停点（演讲模式）与每页定格点（导出 PNG/PDF）
    window.__ms.marks = plan.map((p) => +(p.start + p.dur - 0.05).toFixed(3));
    const pauses = plan.flatMap((p) => p.pauses).filter((x) => x < total);

    const at = (p, lt) => {
      for (const it of p.items) apply(it, lt - TR * (p.i ? 1 : 0.4));
    };

    MS.render((now) => {
      const cur = plan.findLast((p) => now >= p.start) || plan[0];
      for (const p of plan) {
        const lt = now - p.start;
        const visible = p === cur || (p.i === cur.i - 1 && now - cur.start < TR);
        css(p.el, { display: visible ? '' : 'none' });
        if (!visible) continue;
        at(p, lt);
        if (p === cur) enter(p, lt);
        else leave(p, now - cur.start, cur.tr);
      }
      const num = document.getElementById('deck-num');
      if (num) num.textContent = `${String(cur.i + 1).padStart(2, '0')} / ${String(plan.length).padStart(2, '0')}`;
      const bar = document.getElementById('deck-progress');
      if (bar) css(bar, { transform: `scaleX(${now / total})` });
    });

    if (!MS.RENDER) presenter(plan, pauses, total);
    return plan;
  }

  function enter(p, lt) {
    const q = prog(lt, 0, TR, ease.outCubic);
    const z = p.i ? 3 : 1;
    if (p.tr === 'fade') css(p.el, { opacity: q, transform: '', clipPath: '', zIndex: z });
    else if (p.tr === 'zoom') css(p.el, { opacity: q, transform: `scale(${1.06 - 0.06 * q})`, clipPath: '', zIndex: z });
    else if (p.tr === 'flood') css(p.el, { opacity: 1, transform: '', clipPath: `circle(${prog(lt, 0, TR, ease.inOutCubic) * 75}% at 50% 50%)`, zIndex: z });
    else if (p.tr === 'wipe') css(p.el, { opacity: 1, transform: '', clipPath: `inset(0 ${100 - prog(lt, 0, TR, ease.inOutQuart) * 100}% 0 0)`, zIndex: z });
    else css(p.el, { opacity: q, transform: `translateY(${(1 - q) * 6}%)`, clipPath: '', zIndex: z });
  }

  function leave(p, lt, tr) {
    const q = prog(lt, 0, TR, ease.inCubic);
    if (tr === 'push') css(p.el, { opacity: 1 - q, transform: `translateY(${-q * 6}%)`, zIndex: 2 });
    else css(p.el, { opacity: tr === 'fade' || tr === 'zoom' ? 1 - q : 1, transform: '', zIndex: 2 });
  }

  function apply({ node, fx, at, dur }, lt) {
    const p = prog(lt, at, at + dur, ease.outCubic);
    switch (fx) {
      case 'rise': css(node, { transform: `translateY(${(1 - p) * 40}px)`, opacity: p, clipPath: `inset(0 0 ${(1 - p) * 100}% 0)` }); break;
      case 'chars': reveal(node, lt, at, { stagger: 0.035, dur: 0.55, style: 'rise', e: ease.outExpo }); break;
      case 'fade': css(node, { opacity: p }); break;
      case 'blur': css(node, { opacity: p, filter: `blur(${(1 - p) * 14}px)` }); break;
      case 'scale': { const s = spring(lt, at, { stiffness: 260, damping: 18 }); css(node, { transform: `scale(${s})`, opacity: clamp(s * 2) }); break; }
      case 'left': css(node, { transform: `translateX(${(1 - p) * -80}px)`, opacity: p }); break;
      case 'right': css(node, { transform: `translateX(${(1 - p) * 80}px)`, opacity: p }); break;
      case 'draw': for (const path of node.querySelectorAll('path,line,polyline,circle,rect')) {
        const len = path.getTotalLength ? path.getTotalLength() : 1000;
        css(path, { strokeDasharray: len, strokeDashoffset: len * (1 - prog(lt, at, at + dur * 2, ease.inOutCubic)) });
      } break;
      case 'count': {
        const to = +node.dataset.to, dec = +(node.dataset.dec || 0);
        node.textContent = (node.dataset.pre || '') + counter(lt, at, at + dur * 2, 0, to, { decimals: dec }) + (node.dataset.suf || '');
        css(node, { opacity: clamp(p * 3) });
        break;
      }
      case 'type': {
        node.__full = node.__full ?? node.textContent;
        node.textContent = typewriter(node.__full, lt, at, +(node.dataset.cps || 28));
        break;
      }
      case 'bar': css(node, { width: `${(+node.dataset.to || 100) * prog(lt, at, at + dur * 1.6, ease.outExpo)}%` }); break;
      default: css(node, { opacity: p });
    }
  }

  /** 演讲模式：→/空格 播到下一个暂停点；← 回到上一个；F 全屏。底部预览条依旧可用。 */
  function presenter(plan, pauses, total) {
    let head = 0;
    let target = null;
    let t0 = 0;
    const go = (to) => {
      target = clamp(to, 0, total);
      const from = head;
      t0 = performance.now();
      const step = (now) => {
        if (target === null) return;
        head = Math.min(target, from + (now - t0) / 1000);
        MS.seek(head);
        const scrub = document.getElementById('ms-scrub');
        if (scrub) scrub.value = head;
        if (head < target) requestAnimationFrame(step);
      };
      if (target < head) { head = target; MS.seek(head); return; }
      requestAnimationFrame(step);
    };
    const next = () => go(pauses.find((x) => x > head + 0.01) ?? total);
    const prev = () => go([...pauses].reverse().find((x) => x < head - 0.01) ?? 0);
    addEventListener('keydown', (e) => {
      if (['ArrowRight', 'ArrowDown', 'PageDown', 'Enter'].includes(e.code) || e.key === ' ') { e.preventDefault(); e.stopImmediatePropagation(); next(); }
      if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(e.code)) { e.preventDefault(); e.stopImmediatePropagation(); prev(); }
      if (e.key === 'f') document.documentElement.requestFullscreen?.();
    }, true);
    addEventListener('click', (e) => { if (!e.target.closest('#ms-scrub,#ms-play')) next(); });
    next();
  }

  MS.deck = build;
})();
