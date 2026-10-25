"""Shared drawing primitives: palette, fonts, easing, text layout."""
import os
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30

BG = (10, 16, 32)
BG2 = (19, 32, 58)
PANEL = (18, 26, 46)
LINE = (36, 48, 74)
TEXT = (244, 246, 250)
MUTED = (138, 148, 168)
SOFT = (200, 206, 218)
GOLD = (242, 193, 78)
RED = (229, 72, 77)
GREEN = (60, 203, 143)
BLUE = (120, 160, 230)
INK = (10, 16, 32)
DOT = (120, 134, 160)

COLORS = {"red": RED, "gold": GOLD, "green": GREEN, "blue": BLUE, "text": TEXT, "muted": MUTED}


def C(name, default=TEXT):
    if isinstance(name, (list, tuple)):
        return tuple(name)
    return COLORS.get(name or "", default)


_FD = ["/usr/share/fonts/opentype", "/usr/share/fonts/truetype", "/usr/share/fonts"]
_FONT_FILES = {
    "in_r": ["inter/Inter-Regular.otf"],
    "in_m": ["inter/Inter-Medium.otf"],
    "in_sb": ["inter/Inter-SemiBold.otf"],
    "in_b": ["inter/Inter-Bold.otf"],
    "in_xb": ["inter/Inter-ExtraBold.otf", "inter/Inter-Bold.otf"],
    "in_bl": ["inter/InterDisplay-Black.otf", "inter/Inter-Black.otf", "inter/Inter-ExtraBold.otf"],
    "jp_r": ["noto/NotoSansCJK-Regular.ttc"],
    "jp_m": ["noto/NotoSansCJK-Medium.ttc", "noto/NotoSansCJK-Regular.ttc"],
    "jp_b": ["noto/NotoSansCJK-Bold.ttc"],
    "jp_bl": ["noto/NotoSansCJK-Black.ttc", "noto/NotoSansCJK-Bold.ttc"],
}


@lru_cache(maxsize=None)
def _font_path(name):
    for rel in _FONT_FILES[name]:
        for d in _FD:
            p = os.path.join(d, rel)
            if os.path.exists(p):
                return p
    raise FileNotFoundError(f"font {name} not found; install fonts-inter fonts-noto-cjk fonts-noto-cjk-extra")


@lru_cache(maxsize=1024)
def F(name, size):
    return ImageFont.truetype(_font_path(name), int(size), index=0)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(p):
    p = clamp(p)
    return 1 - (1 - p) ** 3


def ease_io(p):
    p = clamp(p)
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


def mix(c, a, base=BG):
    a = clamp(a)
    return tuple(int(base[i] + (c[i] - base[i]) * a) for i in range(3))


def lerp(a, b, p):
    return a + (b - a) * p


def tw(font, s):
    return font.getlength(s)


def txt(d, xy, s, font, fill, anchor="la"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)


def spaced(d, xy, s, font, fill, spacing=4, anchor="l"):
    x, y = xy
    total = sum(tw(font, c) for c in s) + spacing * (len(s) - 1)
    if anchor == "m":
        x -= total / 2
    for c in s:
        d.text((x, y), c, font=font, fill=fill, anchor="lm")
        x += tw(font, c) + spacing
    return total


NO_START = set("、。，．・」』）)!！?？ー")


def wrap_jp(s, font, maxw):
    lines, cur = [], ""
    for ch in s:
        if tw(font, cur + ch) > maxw and cur:
            if ch in NO_START:
                cur += ch
                continue
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def wrap_en(s, font, maxw):
    words, lines, cur = s.split(" "), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(font, t) > maxw and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def balance_wrap(fn, s, font, maxw):
    lines = fn(s, font, maxw)
    if fn is wrap_jp and len(lines) == 2:
        cands = [i + 1 for i, ch in enumerate(s[:-1]) if ch in "、。"]
        cands = [i for i in cands if tw(font, s[:i]) <= maxw and tw(font, s[i:]) <= maxw]
        if cands:
            i = min(cands, key=lambda i: abs(i - len(s) / 2))
            return [s[:i], s[i:]]
    if len(lines) == 2:
        best, lo, hi = lines, maxw * 0.5, maxw
        for _ in range(12):
            mid = (lo + hi) / 2
            l2 = fn(s, font, mid)
            if len(l2) <= 2:
                best, hi = l2, mid
            else:
                lo = mid
        lines = best
    return lines


def fit_font(name, size, s, maxw, minsize=20):
    while size > minsize and tw(F(name, size), s) > maxw:
        size -= 2
    return F(name, size)


def rich_line(d, cx, y, line, font, hls, fill, alpha, hl_alpha=1.0):
    """English line centred at cx with gold highlight boxes around hl substrings."""
    low = line.lower()
    spans = []
    for h in hls or []:
        i = low.find(h.lower())
        if i >= 0:
            spans.append((i, i + len(h)))
    spans.sort()
    merged = []
    for a, b in spans:
        if merged and a < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    segs, pos = [], 0
    for a, b in merged:
        if a > pos:
            segs.append((line[pos:a], False))
        segs.append((line[a:b], True))
        pos = b
    if pos < len(line):
        segs.append((line[pos:], False))
    boxed = hl_alpha > 0.05
    M = 14 if boxed else 0
    widths = [tw(font, s_) + (2 * M if h and boxed else 0) for s_, h in segs]
    x = cx - sum(widths) / 2
    asc, desc = font.getmetrics()
    hh = asc + desc
    for (s_, h), wv in zip(segs, widths):
        if h and boxed:
            d.rounded_rectangle((x + 2, y - hh * 0.52 - 4, x + wv - 2, y + hh * 0.48 + 2), radius=10,
                                fill=mix(GOLD, alpha * hl_alpha))
            col = mix(INK, alpha, mix(GOLD, alpha * hl_alpha)) if hl_alpha > 0.5 else mix(fill, alpha)
            d.text((x + M, y), s_, font=font, fill=col, anchor="lm")
        else:
            d.text((x, y), s_, font=font, fill=mix(fill, alpha), anchor="lm")
        x += wv


def rr(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def make_bg(w, h, glow=(0.2, 0.1), grid=64):
    img = Image.new("RGB", (w, h), BG)
    g = Image.new("L", (w, h), 0)
    gd = ImageDraw.Draw(g)
    cx, cy = glow[0] * w, glow[1] * h
    r = max(w, h) * 0.55
    gd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    g = g.filter(ImageFilter.GaussianBlur(max(w, h) * 0.12))
    img = Image.composite(Image.new("RGB", (w, h), BG2), img, g)
    if grid:
        d = ImageDraw.Draw(img)
        for x in range(0, w, grid):
            d.line((x, 0, x, h), fill=(14, 22, 40))
        for y in range(0, h, grid):
            d.line((0, y, w, y), fill=(14, 22, 40))
    return img


@lru_cache(maxsize=1)
def background():
    return make_bg(W, H, (0.2, 0.1), 64)


def person(d, cx, cy, col, s=1.0):
    r = 9 * s
    d.ellipse((cx - r, cy - 22 * s - r, cx + r, cy - 22 * s + r), fill=col)
    d.rounded_rectangle((cx - 15 * s, cy - 8 * s, cx + 15 * s, cy + 14 * s), radius=int(9 * s), fill=col)


def wave(d, cx, cy, t, col, n=9, w=8, gap=8, hmax=46):
    import math
    x = cx - (n * w + (n - 1) * gap) / 2
    for i in range(n):
        h = 8 + (hmax - 8) * (0.5 + 0.5 * math.sin(t * 9 + i * 0.9)) * (0.6 + 0.4 * math.sin(i * 1.7))
        d.rounded_rectangle((x, cy - h / 2, x + w, cy + h / 2), radius=4, fill=col)
        x += w + gap


def ring(d, cx, cy, r, p, col, width=10, track=LINE):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=track, width=width)
    if p > 0:
        d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * clamp(p), fill=col, width=width)


def multiline(d, x, y, text, font, fill, lh, anchor="lm"):
    for ln in str(text).split("\n"):
        d.text((x, y), ln, font=font, fill=fill, anchor=anchor)
        y += lh
    return y
