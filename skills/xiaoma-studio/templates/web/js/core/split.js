// 拆字：[data-split] 的每个直接子元素算一行，行内中文逐字、拉丁文逐词拆开，外面包一层遮罩（overflow:hidden）。
// 入场写法：gsap.from(chars(el), { yPercent: 110, stagger: 0.025, ease: 'power4.out' })——字从遮罩下面升起。
export function splitLines(el) {
  if (el.dataset.splitDone) return el
  const lines = el.children.length ? [...el.children] : [el]
  for (const line of lines) {
    const text = line.textContent
    const wrap = document.createElement('span')
    wrap.className = 'split-line'
    const inner = document.createElement('span')
    inner.style.display = 'inline-block'
    for (const tk of text.match(/[A-Za-z0-9.,'’%+\-]+|\s+|./gu) || []) {
      if (/^\s+$/.test(tk)) { inner.append(document.createTextNode(tk)); continue }
      const s = document.createElement('span')
      s.className = 'split-char'
      s.textContent = tk
      inner.append(s)
    }
    wrap.append(inner)
    if (line === el) { el.textContent = ''; el.append(wrap) } else { line.textContent = ''; line.append(wrap); line.style.display = 'block' }
  }
  el.dataset.splitDone = '1'
  return el
}

export const chars = (el) => [...el.querySelectorAll('.split-char')]
