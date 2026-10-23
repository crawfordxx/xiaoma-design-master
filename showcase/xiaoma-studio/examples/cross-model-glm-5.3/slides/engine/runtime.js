/* motion-studio runtime —— 每一帧都是时间 t 的纯函数。
 *
 * 渲染合约（render contract）：
 *   - 画面只由 MS.render(fn) 注册的 fn(t) 决定；同一个 t 永远画出同一帧。
 *   - 禁止 CSS transition / animation、setTimeout、在渲染里用 requestAnimationFrame。
 *   - 禁止帧间状态；随机只用 MS.rng(seed) / MS.hash(i)，不要用 Math.random()。
 *   - 渲染器调用 window.__ms.seek(t)，预览模式下本文件自己用时钟驱动 seek。
 */
(function () {
  'use strict';

  const params = new URLSearchParams(location.search);
  const RENDER = params.has('render');

  const cfg = { width: 1920, height: 1080, fps: 30, duration: 10, bpm: 120, beatOffset: 0, background: '#000' };
  let renderFn = () => {};
  const pending = [];

  // ---------- 数学 ----------
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, p) => a + (b - a) * p;
  const invLerp = (a, b, x) => clamp((x - a) / (b - a));
  const mix = (a, b, p) => (Array.isArray(a) ? a.map((v, i) => lerp(v, b[i], p)) : lerp(a, b, p));

  const ease = {
    linear: (p) => p,
    inQuad: (p) => p * p,
    outQuad: (p) => 1 - (1 - p) * (1 - p),
    inOutQuad: (p) => (p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2),
    inCubic: (p) => p * p * p,
    outCubic: (p) => 1 - Math.pow(1 - p, 3),
    inOutCubic: (p) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
    outQuart: (p) => 1 - Math.pow(1 - p, 4),
    inOutQuart: (p) => (p < 0.5 ? 8 * p ** 4 : 1 - Math.pow(-2 * p + 2, 4) / 2),
    inExpo: (p) => (p === 0 ? 0 : Math.pow(2, 10 * p - 10)),
    outExpo: (p) => (p === 1 ? 1 : 1 - Math.pow(2, -10 * p)),
    inOutExpo: (p) => (p === 0 ? 0 : p === 1 ? 1 : p < 0.5 ? Math.pow(2, 20 * p - 10) / 2 : (2 - Math.pow(2, -20 * p + 10)) / 2),
    inBack: (p) => 2.70158 * p * p * p - 1.70158 * p * p,
    outBack: (p) => 1 + 2.70158 * Math.pow(p - 1, 3) + 1.70158 * Math.pow(p - 1, 2),
    inOutBack: (p) => {
      const c = 1.70158 * 1.525;
      return p < 0.5 ? (Math.pow(2 * p, 2) * ((c + 1) * 2 * p - c)) / 2 : (Math.pow(2 * p - 2, 2) * ((c + 1) * (p * 2 - 2) + c) + 2) / 2;
    },
    outElastic: (p) => (p === 0 || p === 1 ? p : Math.pow(2, -10 * p) * Math.sin((p * 10 - 0.75) * ((2 * Math.PI) / 3)) + 1),
  };

  /** t 在 [start, end] 内的进度，经过缓动，区间外夹到 0/1。 */
  const prog = (t, start, end, e = ease.inOutCubic) => e(invLerp(start, end, t));

  /** 阻尼弹簧的闭式解：t0 时刻从 0 弹向 1，可以过冲。没有帧间状态。 */
  function spring(t, t0, { stiffness = 170, damping = 22, mass = 1 } = {}) {
    const x = t - t0;
    if (x <= 0) return 0;
    const w0 = Math.sqrt(stiffness / mass);
    const zeta = damping / (2 * Math.sqrt(stiffness * mass));
    if (zeta < 1) {
      const wd = w0 * Math.sqrt(1 - zeta * zeta);
      return 1 - Math.exp(-zeta * w0 * x) * (Math.cos(wd * x) + ((zeta * w0) / wd) * Math.sin(wd * x));
    }
    return 1 - Math.exp(-w0 * x) * (1 + w0 * x);
  }

  /** 一个值经历多次变化：每次变化各自一个弹簧，叠加求和，所以仍是 t 的纯函数。
   *  changes: [[t0, value], ...]，按时间升序。 */
  function springTo(t, initial, changes, opts) {
    let v = initial;
    let prev = initial;
    for (const [t0, target] of changes) {
      v += (target - prev) * spring(t, t0, opts);
      prev = target;
    }
    return v;
  }

  // ---------- 确定性随机 ----------
  function rng(seed = 1) {
    let a = seed >>> 0;
    return function mulberry32() {
      a = (a + 0x6d2b79f5) >>> 0;
      let r = Math.imul(a ^ (a >>> 15), 1 | a);
      r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
      return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
    };
  }
  const hash = (i, seed = 0) => rng((i * 2654435761) ^ (seed * 97531))();
  /** 平滑一维噪声，[-1, 1]。用于漂移、手绘抖动。 */
  function noise(x, seed = 0) {
    const i = Math.floor(x);
    const f = x - i;
    const u = f * f * (3 - 2 * f);
    return lerp(hash(i, seed) * 2 - 1, hash(i + 1, seed) * 2 - 1, u);
  }

  // ---------- 节拍 ----------
  const beatLen = () => 60 / cfg.bpm;
  const beat = (n) => cfg.beatOffset + n * beatLen();
  const beatOf = (t) => (t - cfg.beatOffset) / beatLen();
  /** 每拍一次的脉冲：拍点处 1，按 decay 秒衰减到 0。 */
  const pulse = (t, decay = 0.25) => {
    const b = beatOf(t);
    if (b < 0) return 0;
    return Math.exp(-((b - Math.floor(b)) * beatLen()) / decay);
  };

  // ---------- 镜头 ----------
  /** shots: [[start, fn], ...]，fn(t, localT, dur)。返回当前镜头下标。 */
  function shots(t, list, total = cfg.duration) {
    let idx = 0;
    for (let i = 0; i < list.length; i++) if (t >= list[i][0]) idx = i;
    const start = list[idx][0];
    const end = idx + 1 < list.length ? list[idx + 1][0] : total;
    list[idx][1](t, t - start, end - start);
    return idx;
  }

  // ---------- DOM ----------
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  /** 一次写入多项样式。transform 等用字符串；数值不加单位。 */
  function css(el, styles) {
    if (!el) return;
    for (const k in styles) el.style[k] = styles[k];
  }
  /** 按 t 显隐：不在区间内直接 display:none，省掉多余绘制。 */
  const show = (el, visible) => css(el, { display: visible ? '' : 'none' });

  // ---------- 文字 ----------
  /** 把元素拆成逐字/逐词 span（只拆一次，结果缓存在元素上）。中文默认逐字。 */
  function split(el, mode = 'chars') {
    if (el.__msSplit) return el.__msSplit;
    const text = el.textContent;
    el.textContent = '';
    const parts = mode === 'words' ? text.split(/(\s+)/) : [...text];
    const spans = [];
    for (const p of parts) {
      if (/^\s+$/.test(p)) {
        el.appendChild(document.createTextNode(p));
        continue;
      }
      const s = document.createElement('span');
      s.textContent = p;
      s.style.display = 'inline-block';
      s.style.whiteSpace = 'pre';
      el.appendChild(s);
      spans.push(s);
    }
    el.__msSplit = spans;
    return spans;
  }

  /** 逐字出现。style: 'rise'（从遮罩线下升起）| 'fade'（字幕式淡入）| 'blur'。 */
  function reveal(el, t, start, { stagger = 0.03, dur = 0.5, mode = 'chars', style = 'rise', e = ease.outCubic, out = null } = {}) {
    const spans = split(el, mode);
    spans.forEach((s, i) => {
      const p = prog(t, start + i * stagger, start + i * stagger + dur, e);
      const q = out ? prog(t, out + i * stagger * 0.5, out + i * stagger * 0.5 + dur * 0.6, ease.inCubic) : 0;
      const v = p * (1 - q);
      if (style === 'rise') css(s, { transform: `translateY(${(1 - p) * 110 + q * -60}%)`, opacity: v > 0 ? 1 : 0 });
      else if (style === 'blur') css(s, { opacity: v, filter: `blur(${(1 - v) * 12}px)` });
      else css(s, { opacity: v });
    });
  }

  /** 打字机：返回 t 时刻应显示的子串。cps = 每秒字数。 */
  const typewriter = (str, t, start, cps = 18) => [...str].slice(0, Math.max(0, Math.floor((t - start) * cps))).join('');

  /** 数字滚动，带千分位。 */
  function counter(t, start, end, from, to, { decimals = 0, e = ease.outExpo, sep = ',' } = {}) {
    const v = lerp(from, to, prog(t, start, end, e));
    const [i, d] = v.toFixed(decimals).split('.');
    return i.replace(/\B(?=(\d{3})+(?!\d))/g, sep) + (d ? '.' + d : '');
  }

  // ---------- Canvas ----------
  function canvas(el) {
    const c = typeof el === 'string' ? $(el) : el;
    if (!c.__ms) {
      const w = c.clientWidth || cfg.width;
      const h = c.clientHeight || cfg.height;
      c.width = Math.round(w * devicePixelRatio);
      c.height = Math.round(h * devicePixelRatio);
      const ctx = c.getContext('2d');
      ctx.scale(devicePixelRatio, devicePixelRatio);
      c.__ms = { ctx, w, h };
    }
    const { ctx, w, h } = c.__ms;
    ctx.clearRect(0, 0, w, h);
    return c.__ms;
  }

  /** 沿路径按进度描边：path 为 [[x,y],...]，p 为 0..1。 */
  function drawPath(ctx, pts, p) {
    if (pts.length < 2 || p <= 0) return;
    const segs = [];
    let total = 0;
    for (let i = 1; i < pts.length; i++) {
      const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
      segs.push(d);
      total += d;
    }
    let left = total * clamp(p);
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length && left > 0; i++) {
      const k = Math.min(1, left / segs[i - 1]);
      ctx.lineTo(lerp(pts[i - 1][0], pts[i][0], k), lerp(pts[i - 1][1], pts[i][1], k));
      left -= segs[i - 1];
    }
    ctx.stroke();
  }

  // ---------- 素材就绪 ----------
  /** 注册一个需要在首帧前完成的 Promise（字体、图片、数据）。 */
  const ready = (promise) => pending.push(promise);

  /** 视频素材：按 t 精确 seek，等 'seeked' 再画。建议先用 ffmpeg -g 1 全帧内编码。 */
  function videoAt(video, time) {
    if (Math.abs(video.currentTime - time) < 1 / 120) return Promise.resolve();
    return new Promise((res) => {
      video.addEventListener('seeked', res, { once: true });
      video.currentTime = time;
    });
  }

  async function settle() {
    await Promise.all(pending);
    if (document.fonts) await document.fonts.ready;
    await Promise.all($$('img').map((img) => (img.complete ? img.decode().catch(() => {}) : new Promise((r) => (img.onload = img.onerror = r)))));
  }

  // ---------- seek：渲染器与预览器共用的唯一入口 ----------
  let settled = null;
  async function seek(t) {
    if (!settled) settled = settle();
    await settled;
    const tt = clamp(t, 0, cfg.duration);
    const r = renderFn(tt);
    if (r && typeof r.then === 'function') await r;
    document.documentElement.style.setProperty('--ms-frame', String(Math.round(tt * cfg.fps)));
  }

  function setup(opts) {
    Object.assign(cfg, opts);
    const root = document.documentElement;
    root.style.setProperty('--ms-w', cfg.width + 'px');
    root.style.setProperty('--ms-h', cfg.height + 'px');
    document.body.style.background = cfg.background;
  }

  function render(fn) {
    renderFn = fn;
    window.__ms.meta = { ...cfg };
    if (RENDER) seek(0);
    else startPreview();
  }

  // ---------- 预览器（仅预览模式；渲染时完全不加载） ----------
  function startPreview() {
    const stage = $('#stage');
    const fit = () => {
      const s = Math.min(innerWidth / cfg.width, (innerHeight - 56) / cfg.height);
      if (stage) css(stage, { transform: `scale(${s})`, transformOrigin: '0 0', position: 'absolute', left: (innerWidth - cfg.width * s) / 2 + 'px', top: '0px' });
    };
    fit();
    addEventListener('resize', fit);

    const bar = document.createElement('div');
    bar.innerHTML = `<button id="ms-play">▶</button><input id="ms-scrub" type="range" min="0" max="${cfg.duration}" step="${1 / cfg.fps}" value="0"><span id="ms-time"></span>`;
    css(bar, { position: 'fixed', left: '0', right: '0', bottom: '0', height: '48px', display: 'flex', gap: '12px', alignItems: 'center', padding: '0 16px', background: '#111', color: '#ddd', font: '12px ui-monospace, monospace', zIndex: 99999 });
    document.body.appendChild(bar);
    const scrub = $('#ms-scrub');
    css(scrub, { flex: '1' });
    const timeEl = $('#ms-time');
    let playing = false;
    let t0 = 0;
    let base = 0;
    const draw = async (t) => {
      await seek(t);
      scrub.value = t;
      timeEl.textContent = `${t.toFixed(2)}s · beat ${beatOf(t).toFixed(1)} · f${Math.round(t * cfg.fps)}`;
    };
    const loop = (now) => {
      if (!playing) return;
      let t = base + (now - t0) / 1000;
      if (t > cfg.duration) {
        base = 0;
        t0 = now;
        t = 0;
      }
      draw(t).then(() => requestAnimationFrame(loop));
    };
    const toggle = () => {
      playing = !playing;
      $('#ms-play').textContent = playing ? '❚❚' : '▶';
      if (playing) {
        base = +scrub.value >= cfg.duration ? 0 : +scrub.value;
        t0 = performance.now();
        requestAnimationFrame(loop);
      }
    };
    $('#ms-play').onclick = toggle;
    scrub.oninput = () => {
      playing = false;
      $('#ms-play').textContent = '▶';
      draw(+scrub.value);
    };
    addEventListener('keydown', (e) => {
      if (e.code === 'Space') { e.preventDefault(); toggle(); }
      if (e.code === 'ArrowRight' || e.code === 'ArrowLeft') {
        playing = false;
        const step = e.shiftKey ? beatLen() : 1 / cfg.fps;
        draw(clamp(+scrub.value + (e.code === 'ArrowRight' ? step : -step), 0, cfg.duration));
      }
    });
    draw(+(params.get('t') || 0));
  }

  window.__ms = { seek, meta: cfg };
  window.MS = {
    RENDER, cfg, setup, render, ready, seek,
    clamp, lerp, invLerp, mix, ease, prog, spring, springTo,
    rng, hash, noise,
    beat, beatOf, beatLen, pulse, shots,
    $, $$, css, show,
    split, reveal, typewriter, counter,
    canvas, drawPath, videoAt,
  };
})();
