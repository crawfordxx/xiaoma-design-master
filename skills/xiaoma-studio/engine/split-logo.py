#!/usr/bin/env python3
"""把整页 SVG（pdftocairo -svg 从 .ai / .pdf 转出来的）按矩形裁成独立的 logo 文件。
    python3 split-logo.py 页.svg 输出.svg x y 宽 高 [--keep-bg] [--two-stop]
- 坐标单位是 pt，和 pdftocairo -png -r 72 出的图上的像素一一对应，先出图量好矩形。
- 只保留起点落在矩形内的图形（带 clip-path 的组按裁剪路径的位置判断），以及它们用到的渐变、裁剪路径。
- 默认去掉比矩形还宽的纯色矩形（设计稿上反白版下面垫的整块底色），--keep-bg 保留。
- --two-stop：pdftocairo 把线性渐变展开成 256 个色标，设计稿里的两色线性渐变可以精简成首尾两个，文件小一个数量级。
  精简前先确认是线性的：抽查中间色标是否等于首尾的线性插值。
"""
import re,sys,copy
import xml.etree.ElementTree as ET
NS='http://www.w3.org/2000/svg'; XL='http://www.w3.org/1999/xlink'
ET.register_namespace('',NS); ET.register_namespace('xlink',XL)
CLIPS={}
def first_pt(el):
    cp=el.get('clip-path')
    if cp:
        c=CLIPS.get(cp[5:-1])
        if c is not None: return first_pt(c)
    for p in el.iter('{%s}path'%NS):
        if p.get('transform'): return None
        m=re.match(r'\s*M\s*(-?[\d.]+)\s+(-?[\d.]+)',p.get('d',''))
        if m: return float(m.group(1)),float(m.group(2))
    return None
def refs(el):
    s=ET.tostring(el,encoding='unicode'); return set(re.findall(r'url\(#([^)]+)\)',s))|set(re.findall(r'href="#([^"]+)"',s))
def crop(src,out,x,y,w,h,drop_bg=True,pad=0):
    t=ET.parse(src); root=t.getroot()
    defs=root.find('{%s}defs'%NS)
    CLIPS.clear(); CLIPS.update({d.get('id'):d for d in defs if d.tag=='{%s}clipPath'%NS})
    body=[e for e in list(root) if e.tag!='{%s}defs'%NS]
    keep=[]
    for e in body:
        # 只处理顶层 <g> 里面的元素
        items=list(e) if e.tag=='{%s}g'%NS and not e.get('clip-path') else [e]
        for it in items:
            pt=first_pt(it)
            if pt is None: continue
            if not (x-1<=pt[0]<=x+w+1 and y-1<=pt[1]<=y+h+1): continue
            if drop_bg and it.tag=='{%s}path'%NS and re.fullmatch(r'\s*M [\d.]+ [\d.]+ L [\d.]+ [\d.]+ L [\d.]+ [\d.]+ L [\d.]+ [\d.]+ Z M [\d.]+ [\d.]+ \s*',it.get('d','')):
                xs=[float(v) for v in re.findall(r'[\d.]+',it.get('d'))[0::2]]
                if max(xs)-min(xs)>w+20: continue  # 整块背景色
            keep.append(it)
    need=set()
    for k in keep: need|=refs(k)
    changed=True
    while changed:
        changed=False
        for d in list(defs) if defs is not None else []:
            if d.get('id') in need:
                n=refs(d)-need
                if n: need|=n; changed=True
    new=ET.Element('{%s}svg'%NS,{'width':f'{w+2*pad:g}','height':f'{h+2*pad:g}','viewBox':f'{x-pad:g} {y-pad:g} {w+2*pad:g} {h+2*pad:g}'})
    nd=ET.SubElement(new,'{%s}defs'%NS)
    for d in list(defs) if defs is not None else []:
        if d.get('id') in need: nd.append(d)
    for k in keep: new.append(k)
    ET.ElementTree(new).write(out,encoding='unicode',xml_declaration=False)
def two_stop(path):
    s=open(path,encoding='utf-8').read()
    def f(m):
        st=re.findall(r'<stop[^>]*/>',m.group(2))
        if len(st)<3: return m.group(0)
        last=re.sub(r'offset="[\d.]+"','offset="1"',st[-1])
        return m.group(1)+st[0]+last+m.group(3)
    s=re.sub(r'(<linearGradient[^>]*>)(.*?)(</linearGradient>)',f,s,flags=re.S)
    open(path,'w',encoding='utf-8').write(s)

if __name__=='__main__':
    a=[x for x in sys.argv[1:] if not x.startswith('--')]
    if len(a)<6:
        print(__doc__); sys.exit(1)
    crop(a[0],a[1],*map(float,a[2:6]),drop_bg='--keep-bg' not in sys.argv)
    if '--two-stop' in sys.argv: two_stop(a[1])
    print('已写入',a[1])
