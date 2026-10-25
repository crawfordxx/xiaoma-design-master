"""字幕与字卡：解析 on_screen_text / dialogue，按类型排版成透明 PNG（不依赖 libass / drawtext）。

on_screen_text 常把内容和制作备注写在一起：「内容（备注）」。备注只用来判类型，绝不上屏。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DISCLAIMER = re.compile(r"虚构|纯属|演绎|AI\s*生成|人工智能生成")
TIME_LIKE = re.compile(r"\d\s*[:：]\s*\d|\d+\s*[年月日号点时]|凌晨|清晨|深夜|傍晚|午夜|[前后]\s*$|\d+\s*(?:天|小时|分钟|年)[前后]")
PARTS = re.compile(r"\s*／\s*|\s+/\s+")
PAREN = re.compile(r"[（(]([^）)]*)[）)]")
ARROW = re.compile(r"\s*(?:→|->|⇒)\s*")


@dataclass(frozen=True)
class Card:
    kind: str            # name / screen / title / time / caption
    text: str
    start: float = 0.0   # 在本镜内出现的比例区间
    end: float = 1.0


@dataclass(frozen=True)
class Overlay:
    png: Path
    x: int
    y: int
    t0: float
    t1: float


def line_text(raw: str | None) -> str:
    """「周野：“……”」→ 台词正文；去掉说话人、引号和括号里的表演提示。"""
    text = raw or ""
    m = re.match(r"^\s*[^：:“\"]{1,12}[：:]\s*(.+)$", text, re.S)
    text = m.group(1) if m else text
    text = PAREN.sub("", text)
    return text.strip().strip('"“”「」').strip()


def _kind_from_notes(notes: str) -> str:
    if "名牌" in notes or "人名条" in notes:
        return "name"
    if any(k in notes for k in ("屏幕", "手机", "界面", "屏")):
        return "screen"
    if any(k in notes for k in ("片名", "字卡", "标题", "时间卡", "地点卡")):
        return "title"
    return "caption"


def _sequence(cards: list[Card]) -> list[Card]:
    """同一镜多张卡依次出现，不叠在一起。"""
    n = len(cards)
    return [Card(c.kind, c.text, i / n, (i + 1) / n) for i, c in enumerate(cards)]


def parse_ost(raw: str | None) -> tuple[list[Card], list[str]]:
    """返回 (上屏的卡, 被丢掉的内容)。被丢掉的是制作备注和虚构声明（声明只做角标）。"""
    raw = (raw or "").strip()
    if not raw:
        return [], []
    notes = PAREN.findall(raw)
    dropped = [f"备注：{n}" for n in notes]
    content = PAREN.sub("", raw).strip()
    kind = _kind_from_notes(" ".join(notes))
    parts = [p.strip() for p in PARTS.split(content) if p.strip()]
    kept = []
    for p in parts:
        if DISCLAIMER.search(p):
            dropped.append(f"声明并入角标：{p}")
        else:
            kept.append(p)
    if not kept:
        return [], dropped
    if kind == "name":
        return [Card("name", " · ".join(kept))], dropped
    if kind == "screen":
        states = [s for s in ARROW.split("\n".join(kept)) if s.strip()]
        return _sequence([Card("screen", s.strip()) for s in states]), dropped
    cards = []
    for p in kept:
        if kind in ("title", "caption") and TIME_LIKE.search(p) and len(p) <= 16:
            cards.append(Card("time", p))
        else:
            cards.append(Card("title" if kind == "title" else "caption", p))
    return (_sequence(cards) if len(cards) > 1 else cards), dropped


# ---------- 排版 ----------

class Typesetter:
    """按输出画幅排版。尺寸以短边 720 为基准等比放大。"""

    def __init__(self, font_path: str, width: int, height: int):
        self.font_path, self.W, self.H = font_path, width, height
        self.k = min(width, height) / 720

    def font(self, size: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(self.font_path, max(10, int(size * self.k)))

    def _wrap(self, text: str, font: ImageFont.FreeTypeFont, max_w: float) -> list[str]:
        lines = []
        for para in text.split("\n"):
            cur = ""
            for ch in para:
                if cur and font.getlength(cur + ch) > max_w:
                    lines.append(cur)
                    cur = ch
                else:
                    cur += ch
            lines.append(cur)
        return lines

    def text_png(self, text: str, size: float, max_w: float, box: bool,
                 fill: str = "white", box_fill: tuple = (0, 0, 0, 150)) -> Image.Image:
        font = self.font(size)
        lines = self._wrap(text, font, max_w)
        fs = font.size
        lh = int(fs * 1.35)
        pad = int(fs * 0.5)
        w = int(max(font.getlength(ln) for ln in lines)) + pad * 2
        im = Image.new("RGBA", (w, lh * len(lines) + pad), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if box:
            d.rounded_rectangle((0, 0, w - 1, im.height - 1), int(fs * 0.3), fill=box_fill)
        for i, ln in enumerate(lines):
            x = (w - font.getlength(ln)) / 2
            d.text((x, pad // 2 + i * lh), ln, font=font, fill=fill,
                   stroke_width=0 if box else max(2, fs // 12), stroke_fill="black")
        return im

    def vertical_png(self, text: str, size: float) -> Image.Image:
        font = self.font(size)
        chars = [c for c in text if c not in " ·|"]
        fs = font.size
        pad = int(fs * 0.35)
        im = Image.new("RGBA", (fs + pad * 2, int(len(chars) * fs * 1.15) + pad * 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), 6, fill=(0, 0, 0, 120))
        for i, c in enumerate(chars):
            d.text((pad, pad + i * fs * 1.15), c, font=font, fill="white")
        return im

    def screen_png(self, text: str, box_px: tuple[int, int, int, int]) -> Image.Image:
        """贴进屏幕区域：铺一层亮屏底色盖住模型可能画出的乱码，深色字按区域自动缩放。"""
        _, _, bw, bh = box_px
        im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, bw - 1, bh - 1), max(4, bw // 16), fill=(238, 242, 245, 235))
        size = bh / self.k * 0.5
        while size > 8:
            font = self.font(size)
            lines = self._wrap(text, font, bw * 0.86)
            lh = font.size * 1.3
            if lh * len(lines) <= bh * 0.86:
                break
            size *= 0.9
        y0 = (bh - lh * len(lines)) / 2
        for i, ln in enumerate(lines):
            d.text(((bw - font.getlength(ln)) / 2, y0 + i * lh), ln, font=font, fill=(25, 28, 32, 255))
        return im

    # ----- 定位 -----
    def place(self, card: Card, screen_box: tuple[int, int, int, int] | None) -> list[tuple[Image.Image, int, int]]:
        W, H = self.W, self.H
        if card.kind == "name":
            name, *rest = re.split(r"\s*[·|｜]\s*", card.text, maxsplit=1)
            role = rest[0] if rest else ""
            col = self.vertical_png(name, 34)
            x, y = int(W - col.width - W * 0.06), int(H * 0.18)
            out = [(col, x, y)]
            if role.strip():
                tag = self.text_png(role.strip(), 20, W * 0.3, box=True)
                out.append((tag, int(W - tag.width - W * 0.06), y + col.height + 8))
            return out
        if card.kind == "screen":
            if screen_box:
                return [(self.screen_png(card.text, screen_box), screen_box[0], screen_box[1])]
            im = self.text_png(card.text, 30, W * 0.6, box=True, box_fill=(12, 14, 18, 200))
            return [(im, (W - im.width) // 2, int(H * 0.42 - im.height / 2))]
        if card.kind == "title":
            im = self.text_png(card.text, 46, W * 0.8, box=False)
            return [(im, (W - im.width) // 2, (H - im.height) // 2)]
        if card.kind == "time":
            im = self.text_png(card.text, 26, W * 0.5, box=True)
            return [(im, int(W * 0.05), int(H * 0.07))]
        im = self.text_png(card.text, 30, W * 0.86, box=True)
        return [(im, (W - im.width) // 2, int(H * 0.08))]

    def subtitle(self, text: str) -> tuple[Image.Image, int, int]:
        im = self.text_png(text, 34, self.W * 0.86, box=False)
        return im, (self.W - im.width) // 2, int(self.H - im.height - self.H * 0.07)

    def label(self, text: str) -> tuple[Image.Image, int, int]:
        im = self.text_png(text, 18, self.W * 0.5, box=True)
        return im, self.W - im.width - 12, 12


def map_screen_box(box: list[float] | None, src_w: int, src_h: int, W: int, H: int) -> tuple[int, int, int, int] | None:
    """shot.screen_box = [x, y, w, h]（相对片段原画面的 0–1 比例）→ 输出画面像素（经过等比放大 + 居中裁切）。"""
    if not box or len(box) != 4 or not src_w or not src_h:
        return None
    s = max(W / src_w, H / src_h)
    ox, oy = (src_w * s - W) / 2, (src_h * s - H) / 2
    x, y = box[0] * src_w * s - ox, box[1] * src_h * s - oy
    w, h = box[2] * src_w * s, box[3] * src_h * s
    x0, y0 = max(0, int(x)), max(0, int(y))
    x1, y1 = min(W, int(x + w)), min(H, int(y + h))
    if x1 - x0 < 8 or y1 - y0 < 8:
        return None
    return x0, y0, x1 - x0, y1 - y0
