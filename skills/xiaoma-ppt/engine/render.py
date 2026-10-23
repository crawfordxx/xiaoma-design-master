"""pptx → 每页 JPG + 拼图。用法：
    python3 render.py deck.pptx --out out/render [--dpi 80] [--sheet]

本机没有模板字体时（例如 macOS/Linux 上没有微软雅黑），只在「渲染副本」里把字体换成本机已有的同类字体，
交付的 pptx 不受影响。需要 LibreOffice（soffice）和 poppler（pdftoppm）。
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

from PIL import Image, ImageDraw, ImageFont

SANS = ["Microsoft YaHei", "微软雅黑", "PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", "Noto Sans SC",
        "Source Han Sans CN", "Source Han Sans SC", "思源黑体 CN", "WenQuanYi Micro Hei", "Heiti SC"]
SERIF = ["Source Han Serif SC", "Source Han Serif CN", "思源宋体", "Noto Serif CJK SC", "Noto Serif SC",
         "宋体-简", "Songti SC", "STSong", "SimSun", "宋体"]  # macOS 上 LibreOffice 只认「宋体-简」这个名字


def installed_fonts():
    try:
        out = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True, timeout=30).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    fams = set()
    for line in out.splitlines():
        for f in line.split(","):
            fams.add(f.strip().replace("\\", ""))
    return fams


def pick(cands, have):
    for c in cands:
        if c in have:
            return c
    return None


def font_map(xml_texts, have):
    """模板里用到、本机没有的字体 → 本机同类字体"""
    used = set()
    for x in xml_texts:
        used |= set(re.findall(r'typeface="([^"+@][^"]*)"', x))
    m = {}
    for f in used:
        if f in have:
            continue
        serif = re.search(r"宋|明|Serif|Song|Ming|Kai|楷", f, re.I)
        sub = pick(SERIF if serif else SANS, have)
        if sub and sub != f:
            m[f] = sub
    return m


def soffice_bin():
    for b in ("soffice", "libreoffice", "/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        if shutil.which(b) or os.path.exists(b):
            return shutil.which(b) or b
    sys.exit("找不到 LibreOffice（soffice）。macOS: brew install --cask libreoffice；Ubuntu: apt install libreoffice")


def to_pdf(pptx, workdir):
    profile = tempfile.mkdtemp(prefix="lo-")  # 独立配置目录，避免和正在运行的 LibreOffice 冲突
    cmd = [soffice_bin(), f"-env:UserInstallation=file://{profile}", "--headless",
           "--convert-to", "pdf", "--outdir", workdir, pptx]
    try:
        subprocess.run(cmd, capture_output=True, timeout=600)
    except subprocess.TimeoutExpired:
        sys.exit("LibreOffice 转换超过 10 分钟，已放弃")
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    pdf = os.path.join(workdir, os.path.splitext(os.path.basename(pptx))[0] + ".pdf")
    if not os.path.exists(pdf):
        sys.exit("LibreOffice 转 PDF 失败")
    return pdf


def render(pptx, out, dpi=80):
    """返回按页排序的 JPG 路径列表"""
    soffice_bin()
    if not shutil.which("pdftoppm"):
        sys.exit("找不到 pdftoppm（poppler）。macOS: brew install poppler；Ubuntu: apt install poppler-utils")
    os.makedirs(out, exist_ok=True)
    for f in glob.glob(os.path.join(out, "s-*.jpg")):
        os.remove(f)
    tmp = tempfile.mkdtemp(prefix="xmppt-")
    copy = os.path.join(tmp, "deck.pptx")
    have = installed_fonts()
    if have is None:
        print("没有 fc-list，跳过预览字体替换（缺字体时预览可能和 PowerPoint 不同）", file=sys.stderr)
    with zipfile.ZipFile(pptx) as zin:
        names = zin.namelist()
        xmls = {n: zin.read(n).decode("utf-8", "ignore") for n in names if n.endswith(".xml")}
        fmap = font_map(xmls.values(), have) if have else {}
        with zipfile.ZipFile(copy, "w", zipfile.ZIP_DEFLATED) as zout:
            for n in names:
                if n in xmls and fmap:
                    x = xmls[n]
                    for a, b in fmap.items():
                        x = x.replace(f'typeface="{a}"', f'typeface="{b}"')
                    zout.writestr(n, x.encode("utf-8"))
                else:
                    zout.writestr(n, zin.read(n))
    pdf = to_pdf(copy, tmp)
    subprocess.run(["pdftoppm", "-jpeg", "-r", str(dpi), pdf, os.path.join(out, "s")], check=True)
    files = sorted(glob.glob(os.path.join(out, "s-*.jpg")), key=lambda f: int(re.findall(r"(\d+)\.jpg$", f)[0]))
    shutil.copy(pdf, os.path.join(out, "deck.pdf"))
    shutil.rmtree(tmp, ignore_errors=True)
    if fmap:
        subs = sorted(set(fmap.values()))
        print(f"渲染副本替换了 {len(fmap)} 个本机没有的字体 → {'/'.join(subs)}（只影响预览，不影响交付文件）")
    return files


def label_font(size):
    for p in ("/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc",
              "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def sheet(files, path, cols=3, labels=None, width=560):
    """拼图：每格左上角标页码（和可选的标签）"""
    ims = [Image.open(f).convert("RGB") for f in files]
    if not ims:
        return None
    h = round(width * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    gap = 12
    canvas = Image.new("RGB", (cols * width + (cols + 1) * gap, rows * h + (rows + 1) * gap), (40, 40, 44))
    d = ImageDraw.Draw(canvas)
    font = label_font(20)
    for i, im in enumerate(ims):
        x, y = gap + (i % cols) * (width + gap), gap + (i // cols) * (h + gap)
        canvas.paste(im.resize((width, h), Image.LANCZOS), (x, y))
        tag = f"{i + 1}" + (f" · {labels[i]}" if labels and i < len(labels) and labels[i] else "")
        tw = d.textlength(tag, font=font)
        lx, ly = x + width - tw - 16, y + h - 30  # 标在右下角，不挡模板左上角的编号/logo
        d.rectangle([lx, ly, x + width, y + h], fill=(0, 0, 0))
        d.text((lx + 8, ly + 3), tag, fill=(255, 255, 255), font=font)
    canvas.save(path, quality=86)
    return path


def sheets(files, out, per=9, cols=3, labels=None):
    paths = []
    for g in range(0, len(files), per):
        p = os.path.join(out, f"sheet-{g // per + 1}.jpg")
        sheet(files[g:g + per], p, cols, labels[g:g + per] if labels else None)
        paths.append(p)
    return paths


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx")
    ap.add_argument("--out", default="out/render")
    ap.add_argument("--dpi", type=int, default=80)
    a = ap.parse_args()
    files = render(a.pptx, a.out, a.dpi)
    for p in sheets(files, a.out):
        print("拼图", p)
    print(f"共 {len(files)} 页 → {a.out}")


if __name__ == "__main__":
    main()
