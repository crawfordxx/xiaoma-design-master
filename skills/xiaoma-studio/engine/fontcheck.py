#!/usr/bin/env python3
"""网页字体体检：自托管的分片字体（Google Fonts 那种按 unicode-range 拆成上百个 woff2）最容易悄悄坏掉。
    python3 fontcheck.py <fonts.css> [--chars 跨山绘]
查三件事：
  1. 缺文件：@font-face 引用的文件不存在 → 这一片的字全部回落成系统字体。
  2. 字重被冻结：同一个文件被声明给多个字重（400/500/700/900 指向同一个 url），它就必须是可变字体（带 fvar 表）。
     如果是静态字，所有字重都会画成它那一个字重——典型症状是一句话里个别字突然变粗或变细
     （按单个字重分别请求 Google Fonts 再拼起来，就会混进这种静态文件）。
  3. 缺字：--chars 里的字所在的那一片，实际文件里没有这个字形。
需要 fontTools（pip install fonttools brotli）；没装时只查第 1 条。
修法：用一次请求取全部字重（css2?family=Noto+Sans+SC:wght@400;500;700;900），按「字族 + 字形 + unicode-range」对回本地文件名，替换。
"""
import os
import re
import sys

def faces(css):
    for m in re.finditer(r'@font-face\s*{([^}]*)}', css):
        b = m.group(1)
        fam = re.search(r"font-family:\s*['\"]?([^;'\"]+)", b)
        url = re.search(r'url\(([^)]+)\)', b)
        if not fam or not url:
            continue
        w = re.search(r'font-weight:\s*([\d ]+)', b)
        st = re.search(r'font-style:\s*(\w+)', b)
        ur = re.search(r'unicode-range:\s*([^;]+)', b)
        ranges = []
        for r in (ur.group(1).split(',') if ur else []):
            r = r.strip()[2:]
            a, _, c = r.partition('-')
            try:
                ranges.append((int(a, 16), int(c or a, 16)))
            except ValueError:
                pass
        yield {'family': fam.group(1).strip(), 'weight': (w.group(1).strip() if w else '400'), 'style': st.group(1) if st else 'normal',
               'url': url.group(1).strip('\'"'), 'ranges': ranges}

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    css_path = args[0]
    chars = args[args.index('--chars') + 1] if '--chars' in args else ''
    base = os.path.dirname(os.path.abspath(css_path))
    items = list(faces(open(css_path, encoding='utf-8').read()))
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        TTFont = None
        print('未安装 fontTools：只检查文件是否存在（pip install fonttools brotli 后可查字重和缺字）')

    problems = []
    by_file = {}
    for f in items:
        if f['url'].startswith(('http:', 'https:', 'data:')):
            continue
        p = os.path.normpath(os.path.join(base, f['url']))
        by_file.setdefault(p, []).append(f)
    for p, decl in by_file.items():
        if not os.path.exists(p):
            problems.append(f"缺文件：{os.path.relpath(p, base)}（{decl[0]['family']}，{len(decl)} 处声明）")
            continue
        if TTFont is None:
            continue
        font = TTFont(p)
        weights = sorted({d['weight'] for d in decl})
        if len(weights) > 1 and 'fvar' not in font:
            problems.append(f"字重被冻结：{os.path.relpath(p, base)} 是静态 {font['OS/2'].usWeightClass} 字重，却被声明给 {'/'.join(weights)}（{decl[0]['family']}）")
        if chars:
            cmap = font.getBestCmap()
            for ch in chars:
                cp = ord(ch)
                if any(a <= cp <= c for a, c in decl[0]['ranges']) and cp not in cmap:
                    problems.append(f"缺字：「{ch}」应在 {os.path.relpath(p, base)}，文件里没有")
    print(f'{len(items)} 条 @font-face，{len(by_file)} 个本地文件')
    for x in problems:
        print('  - ' + x)
    print('没有发现问题' if not problems else f'{len(problems)} 个问题')
    sys.exit(2 if problems else 0)

if __name__ == '__main__':
    main()
