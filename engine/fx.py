"""Motion and CG layer for the long video: living background, camera push, scene transitions,
extruded/shining hero type, and three CG templates (globe, line, network).

Everything is deterministic in t, so parallel renderers produce identical frames.
"""
import math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from core import *  # noqa

PAD = 80   # background is rendered larger and panned


# ---------------------------------------------------------------- living background
@lru_cache(maxsize=1)
def _bg_big():
    img = make_bg(W + 2 * PAD, H + 2 * PAD, (0.22, 0.12), 0)
    d = ImageDraw.Draw(img)
    for x in range(0, W + 2 * PAD, 64):
        d.line((x, 0, x, H + 2 * PAD), fill=(14, 22, 40))
    for y in range(0, H + 2 * PAD, 64):
        d.line((0, y, W + 2 * PAD, y), fill=(14, 22, 40))
    return img


@lru_cache(maxsize=1)
def _orb():
    s = 900
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).ellipse((150, 150, s - 150, s - 150), fill=70)
    return m.filter(ImageFilter.GaussianBlur(120))


_PARTS = [((i * 7919) % 1000 / 1000, (i * 104729) % 1000 / 1000, 0.4 + (i * 31) % 7 / 10, (i * 13) % 5)
          for i in range(70)]


def living_bg(t):
    ox = PAD + math.sin(t * 0.07) * PAD * 0.8
    oy = PAD + math.cos(t * 0.05) * PAD * 0.6
    img = _bg_big().crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    # slow drifting coloured orb
    cx = int(W * (0.75 + 0.12 * math.sin(t * 0.11))) - 450
    cy = int(H * (0.65 + 0.10 * math.cos(t * 0.09))) - 450
    img.paste(Image.new("RGB", (900, 900), (40, 62, 120)), (cx, cy), _orb())
    d = ImageDraw.Draw(img)
    for px, py, sp, k in _PARTS:      # floating particles
        x = (px * W + t * 18 * sp) % W
        y = (py * H - t * 10 * sp) % H
        r = 1.2 + k * 0.6
        tw_ = 0.5 + 0.5 * math.sin(t * (1.3 + k * 0.3) + px * 20)
        c = mix((150, 170, 220), 0.25 + 0.35 * tw_)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    return img


# ---------------------------------------------------------------- camera + transitions
def camera(img, ts, dur):
    """Slow push-in across the scene (max 3.5%), eased."""
    s = 1 + 0.035 * ease_io(clamp(ts / max(dur, 4)))
    if s <= 1.001:
        return img
    w, h = int(W / s), int(H / s)
    x0, y0 = (W - w) // 2, int((H - h) * 0.42)
    return img.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.BILINEAR)


def sweep_in(img, bg, ts, dur=0.55):
    """Scene entrance: content slides in from the right behind a slanted light bar."""
    if ts >= dur:
        return img
    p = ease(ts / dur)
    off = int((1 - p) * 140)
    if off:
        moved = bg.copy()
        moved.paste(img.crop((0, 0, W - off, H)), (off, 0))
        img = Image.blend(bg, moved, clamp(ts / (dur * 0.7)))
    bx = int(lerp(-300, W + 300, ease_io(ts / dur)))
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    for w_, val in ((150, 28), (60, 70), (16, 150), (4, 255)):
        md.polygon([(bx - w_, H), (bx + 300 - w_, 0), (bx + 300 + w_, 0), (bx + w_, H)], fill=val)
    img = img.copy()
    img.paste((255, 214, 120), (0, 0), m)
    return img


# ---------------------------------------------------------------- type
@lru_cache(maxsize=64)
def _mask(s, fname, size):
    f = F(fname, size)
    l, t_, r, b = f.getbbox(s)
    m = Image.new("L", (r - l + 40, b - t_ + 40), 0)
    ImageDraw.Draw(m).text((20 - l, 20 - t_), s, font=f, fill=255)
    return m


def text3d(img, cx, cy, s, fname, size, col, a=1.0, depth=16, shine_t=None):
    """Extruded headline: dark side layers + front face + optional moving shine band."""
    size = int(size)
    m = _mask(s, fname, size)
    x0, y0 = int(cx - m.width / 2), int(cy - m.height / 2)
    side = tuple(int(c * 0.38) for c in col)
    for k in range(depth, 0, -2):
        q = k / depth
        c = tuple(int(lerp(side[i], col[i] * 0.55, 1 - q)) for i in range(3))
        img.paste(mix(c, a), (x0 + k // 2, y0 + k), m)
    # soft glow
    if a > 0.5:
        g = m.resize((max(1, m.width // 4), max(1, m.height // 4))).filter(ImageFilter.GaussianBlur(6)).resize(m.size)
        gk = 0.35 if (max(col) - min(col)) > 60 else 0.08
        g = g.point(lambda v: int(v * gk * a))
        img.paste(col, (x0, y0), g)
    img.paste(mix(col, a), (x0, y0), m)
    if shine_t is not None and 0 <= shine_t <= 1:
        band = Image.new("L", m.size, 0)
        bd = ImageDraw.Draw(band)
        bx = lerp(-m.width * 0.3, m.width * 1.3, shine_t)
        bd.polygon([(bx, m.height), (bx + m.height * 0.5, 0), (bx + m.height * 0.5 + 60, 0), (bx + 60, m.height)], fill=170)
        img.paste((255, 255, 255), (x0, y0), ImageChops.multiply(band, m))
    return m.width


# ---------------------------------------------------------------- CG templates
def _rot(lat, lon, rlon, tilt):
    la, lo = math.radians(lat), math.radians(lon + rlon)
    x, y, z = math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo)
    tl = math.radians(tilt)
    y, z = y * math.cos(tl) - z * math.sin(tl), y * math.sin(tl) + z * math.cos(tl)
    return x, y, z


@lru_cache(maxsize=1)
def _land_pts():
    """(lat, lon) of land cells on a 2.5° grid, from Natural Earth 1:110m land (public domain)."""
    import os
    m = Image.open(os.path.join(os.path.dirname(__file__), "land.png")).convert("L")
    out = []
    lat = 85.0
    while lat > -60:
        step = 2.5 / max(0.25, math.cos(math.radians(lat)))
        lon = -180.0
        while lon < 180:
            px = int((lon + 180) / 360 * (m.width - 1))
            py = int((90 - lat) / 180 * (m.height - 1))
            if m.getpixel((px, py)) > 127:
                out.append((lat, lon))
            lon += step
        lat -= 2.5
    return out


def t_globe(d, v, x):
    """Rotating wireframe globe with glowing city markers and arcs.
    v: {title?, points:[{label, lat, lon, color}], arcs:[[i, j], ...], lon?: centre longitude}"""
    img = x.img
    a = 1.0 if x.cont else ease(x.vt / 0.6)
    cx, cy, R = 700, 470, 300 * (0.9 + 0.1 * a)
    rlon = -v.get("lon", 120) + x.ts * 6
    tilt = v.get("lat", 25)
    # atmosphere
    d.ellipse((cx - R - 30, cy - R - 30, cx + R + 30, cy + R + 30), fill=mix((30, 52, 100), 0.6 * a))
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=mix((16, 28, 56), a), outline=mix(BLUE, 0.8 * a), width=3)
    for lat in range(-60, 90, 30):
        pts, back = [], []
        for lo in range(0, 361, 6):
            X, Y, Z = _rot(lat, lo, rlon, tilt)
            (pts if Z > 0 else back).append((cx + X * R, cy - Y * R, Z))
        for seq, c in ((back, 0.12), (pts, 0.45)):
            for i in range(len(seq) - 1):
                if abs(seq[i][0] - seq[i + 1][0]) < R * 0.3:
                    d.line((seq[i][:2], seq[i + 1][:2]), fill=mix(BLUE, c * a), width=2)
    for lo in range(0, 360, 30):
        prev = None
        for la in range(-90, 91, 6):
            X, Y, Z = _rot(la, lo, rlon, tilt)
            p = (cx + X * R, cy - Y * R)
            if prev:
                d.line((prev[0], p), fill=mix(BLUE, (0.45 if Z > 0 and prev[1] > 0 else 0.12) * a), width=2)
            prev = (p, Z)
    for la_, lo_ in _land_pts():
        X, Y, Z = _rot(la_, lo_, rlon, tilt)
        if Z > 0.02:
            r_ = 2.2 + 1.6 * Z
            px_, py_ = cx + X * R, cy - Y * R
            d.ellipse((px_ - r_, py_ - r_, px_ + r_, py_ + r_), fill=mix((96, 140, 220), (0.35 + 0.55 * Z) * a))
    P = []
    for i, pt in enumerate(v.get("points", [])):
        X, Y, Z = _rot(pt["lat"], pt["lon"], rlon, tilt)
        P.append((cx + X * R, cy - Y * R, Z))
    for k, (i, j) in enumerate(v.get("arcs", [])):
        p = ease((x.vt - 0.6 - k * 0.3) / 1.0)
        if p <= 0:
            continue
        (x1, y1, z1), (x2, y2, z2) = P[i], P[j]
        n = 40
        mx_, my_ = (x1 + x2) / 2, (y1 + y2) / 2 - math.hypot(x2 - x1, y2 - y1) * 0.45
        pts = []
        for s in range(int(n * p) + 1):
            q = s / n
            pts.append(((1 - q) ** 2 * x1 + 2 * (1 - q) * q * mx_ + q * q * x2, (1 - q) ** 2 * y1 + 2 * (1 - q) * q * my_ + q * q * y2))
        if len(pts) > 1:
            d.line(pts, fill=mix(GOLD, 0.35), width=9)
            d.line(pts, fill=GOLD, width=3)
            hx, hy = pts[-1]
            d.ellipse((hx - 7, hy - 7, hx + 7, hy + 7), fill=(255, 240, 200))
    for i, pt in enumerate(v.get("points", [])):
        X, Y, Z = P[i]
        if Z < -0.05:
            continue
        p = ease((x.vt - 0.3 - i * 0.2) / 0.5)
        col = C(pt.get("color", "gold"), GOLD)
        pr = 10 + 26 * ((x.ts * 0.8 + i * 0.3) % 1)
        d.ellipse((X - pr, Y - pr, X + pr, Y + pr), outline=mix(col, p * (1 - (pr - 10) / 26)), width=3)
        d.ellipse((X - 9, Y - 9, X + 9, Y + 9), fill=mix(col, p))
        lab = pt.get("label", "")
        if lab:
            f = F("jp_b" if not lab.isascii() else "in_b", 30)
            wv = tw(f, lab) + 28
            rr(d, (X + 18, Y - 50, X + 18 + wv, Y - 8), 14, fill=mix(PANEL, p), outline=mix(col, p), width=2)
            txt(d, (X + 18 + wv / 2, Y - 29), lab, f, mix(TEXT, p), "mm")
    # side panel
    if v.get("title"):
        p = ease((x.vt - 0.4) / 0.6)
        txt(d, (1150, 300), v["title"], fit_font("jp_bl", 64, v["title"], 700), mix(TEXT, p), "lm")
    yy = 400
    for i, ln in enumerate(v.get("lines", [])):
        p = ease((x.vt - 0.8 - i * 0.35) / 0.5)
        col = C(ln.get("color", "gold"), GOLD)
        d.rectangle((1150, yy - 22, 1158, yy + 22), fill=mix(col, p))
        txt(d, (1180, yy), ln["text"], fit_font("jp_b", 42, ln["text"], 640), mix(TEXT, p), "lm")
        yy += 84


def t_line(d, v, x):
    """Animated line chart with glow, area fill and a live end label.
    v: {title, points:[{label, value}], unit?, color?, display?: end label, note?, mark?: [{i, text}]}"""
    pts = v["points"]
    a = 1.0 if x.cont else ease(x.vt / 0.5)
    col = C(v.get("color", "gold"), GOLD)
    if v.get("title"):
        txt(d, (W / 2, 190), v["title"], fit_font("jp_b", 44, v["title"], 1500), mix(TEXT, a), "mm")
    X0, X1, Y0, Y1 = 260, 1660, 280, 720
    vals = [p_["value"] for p_ in pts]
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.15 or 1
    lo, hi = lo - pad, hi + pad
    for k in range(5):
        y = Y1 - (Y1 - Y0) * k / 4
        d.line((X0, y, X1, y), fill=mix(LINE, a * 0.8), width=1)
    n = len(pts)
    XY = [(X0 + (X1 - X0) * i / max(1, n - 1), Y1 - (Y1 - Y0) * (p_["value"] - lo) / (hi - lo)) for i, p_ in enumerate(pts)]
    for i, p_ in enumerate(pts):
        if i % max(1, n // 6) == 0 or i == n - 1:
            txt(d, (XY[i][0], Y1 + 34), p_["label"], F("jp_m" if not p_["label"].isascii() else "in_m", 26), mix(MUTED, a), "mm")
    p = 1.0 if x.cont else ease_io((x.vt - 0.3) / 1.8)
    m = p * (n - 1)
    k = int(m)
    draw = XY[:k + 1]
    if k < n - 1:
        q = m - k
        draw.append((lerp(XY[k][0], XY[k + 1][0], q), lerp(XY[k][1], XY[k + 1][1], q)))
    if len(draw) > 1:
        poly = draw + [(draw[-1][0], Y1), (draw[0][0], Y1)]
        layer = Image.new("L", (W, H), 0)
        ImageDraw.Draw(layer).polygon(poly, fill=60)
        x.img.paste(col, (0, 0), layer)
        d.line(draw, fill=mix(col, 0.35), width=14, joint="curve")
        d.line(draw, fill=col, width=5, joint="curve")
        ex, ey = draw[-1]
        pr = 12 + 6 * math.sin(x.vt * 6)
        d.ellipse((ex - pr, ey - pr, ex + pr, ey + pr), fill=mix(col, 0.4))
        d.ellipse((ex - 8, ey - 8, ex + 8, ey + 8), fill=(255, 255, 255))
        if p >= 0.999 and v.get("display"):
            q = ease((x.vt - 2.1) / 0.4) if not x.cont else 1
            lab = v["display"]
            f = F("in_bl" if lab.isascii() else "jp_bl", 46)
            wv = tw(f, lab) + 40
            bx = min(ex - wv / 2, X1 - wv)
            rr(d, (bx, ey - 100, bx + wv, ey - 34), 20, fill=mix(col, q))
            txt(d, (bx + wv / 2, ey - 67), lab, f, mix(INK, q, mix(col, q)), "mm")
    for mk in v.get("mark", []):
        i = mk["i"]
        if m >= i:
            q = ease((m - i) / 0.6)
            mx_, my_ = XY[i]
            d.line((mx_, my_ + 16, mx_, Y1), fill=mix(MUTED, q * 0.7), width=2)
            txt(d, (mx_, my_ - 40), mk["text"], fit_font("jp_b", 32, mk["text"], 420), mix(SOFT, q), "mm")
    if v.get("note"):
        txt(d, (W / 2, 800), v["note"], F("jp_m", 28), mix(MUTED, a), "mm")


def t_network(d, v, x):
    """Hub-and-spoke network with packets flowing along the links.
    v: {center: {label, sub?}, nodes:[{label, color?}], title?, inward?: bool}"""
    a = 1.0 if x.cont else ease(x.vt / 0.5)
    cx, cy = W / 2, 500
    nodes = v["nodes"]
    n = len(nodes)
    R = 330
    pos = []
    for i in range(n):
        ang = -math.pi / 2 + 2 * math.pi * i / n + 0.12 * math.sin(x.ts * 0.3)
        pos.append((cx + math.cos(ang) * R * 1.35, cy + math.sin(ang) * R * 0.7))
    for i, (px, py) in enumerate(pos):
        p = 1.0 if x.cont else ease((x.vt - 0.3 - i * 0.15) / 0.5)
        if p <= 0:
            continue
        ex, ey = lerp(cx, px, p), lerp(cy, py, p)
        col = C(nodes[i].get("color", "blue"), BLUE)
        d.line((cx, cy, ex, ey), fill=mix(col, 0.25 * a), width=8)
        d.line((cx, cy, ex, ey), fill=mix(col, 0.7 * a), width=2)
        for k in range(3):
            q = (x.ts * 0.45 + k / 3 + i * 0.17) % 1
            if v.get("inward", True):
                q = 1 - q
            qx, qy = lerp(cx, ex, q), lerp(cy, ey, q)
            d.ellipse((qx - 6, qy - 6, qx + 6, qy + 6), fill=mix((255, 240, 200), p))
    for i, (px, py) in enumerate(pos):
        p = 1.0 if x.cont else ease((x.vt - 0.6 - i * 0.15) / 0.5)
        col = C(nodes[i].get("color", "blue"), BLUE)
        lab = nodes[i]["label"]
        f = fit_font("jp_b" if not lab.isascii() else "in_b", 34, lab, 300)
        wv = max(tw(f, lab) + 50, 160)
        rr(d, (px - wv / 2, py - 40, px + wv / 2, py + 40), 40, fill=mix(PANEL, p), outline=mix(col, p), width=3)
        txt(d, (px, py), lab, f, mix(TEXT, p), "mm")
    c = v["center"]
    pr = 120 + 8 * math.sin(x.ts * 2)
    d.ellipse((cx - pr - 30, cy - pr - 30, cx + pr + 30, cy + pr + 30), fill=mix((60, 50, 20), 0.5 * a))
    d.ellipse((cx - 120, cy - 120, cx + 120, cy + 120), fill=mix(GOLD, a))
    txt(d, (cx, cy - (14 if c.get("sub") else 0)), c["label"], fit_font("in_bl" if c["label"].isascii() else "jp_bl", 46, c["label"], 210),
        mix(INK, a, mix(GOLD, a)), "mm")
    if c.get("sub"):
        txt(d, (cx, cy + 36), c["sub"], fit_font("jp_b", 28, c["sub"], 200), mix(INK, a, mix(GOLD, a)), "mm")
    if v.get("title"):
        txt(d, (W / 2, 160), v["title"], fit_font("jp_b", 40, v["title"], 1500), mix(TEXT, a), "mm")


CG = {"globe": t_globe, "line": t_line, "network": t_network}
