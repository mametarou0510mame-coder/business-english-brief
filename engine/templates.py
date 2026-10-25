"""Visual templates for the main area of a 16:9 frame (y ≈ 130–790; subtitles live below).

Each template is fn(d, v, x) where v is the beat's "vis" dict and x is a context with
  vt   seconds since this visual started
  ts   seconds since the scene started
  cont True when the previous beat used the same template (skip shared intro animation)
  ep   the episode dict
Docs for every template and its fields: docs/FORMAT.md
"""
import math
from core import *  # noqa


def _a(x, delay=0.0, dur=0.5):
    return ease((x.vt - delay) / dur)


# ---------------------------------------------------------------- hero
def t_hero(d, v, x):
    a = _a(x)
    if v.get("kicker"):
        spaced(d, (W / 2, 210), v["kicker"].upper(), F("in_b", 30), mix(MUTED, a), 8, "m")
    big = str(v["big"])
    size = 380 if len(big) <= 4 else (260 if len(big) <= 7 else 180)
    s = size * (0.85 + 0.15 * ease(x.vt / 0.6))
    font = fit_font("jp_bl" if not big.isascii() else "in_bl", s, big, 1600)
    txt(d, (W / 2, 470), big, font, mix(C(v.get("color", "red")), a), "mm")
    if v.get("crack"):
        p = ease((x.vt - 0.5) / 0.7)
        pts = [(620, 330), (820, 430), (900, 400), (1040, 520), (1120, 490), (1320, 610)]
        n = int(p * (len(pts) - 1) * 10)
        seg = []
        for i in range(len(pts) - 1):
            for k in range(10):
                if len(seg) <= n:
                    q = k / 10
                    seg.append((lerp(pts[i][0], pts[i + 1][0], q), lerp(pts[i][1], pts[i + 1][1], q)))
        if len(seg) > 1:
            d.line(seg, fill=BG, width=12)
    if v.get("sub"):
        p2 = _a(x, 1.0)
        txt(d, (W / 2, 720), v["sub"], F("jp_b", 44), mix(C(v.get("sub_color", "green")), p2), "mm")


def t_hero_side(d, v, x):
    p = ease(x.vt / 0.6) if not x.cont else 1
    big = str(v["big"])
    xb = lerp(W / 2, 560, p)
    s = lerp(380, 300, p)
    font = fit_font("in_bl" if big.isascii() else "jp_bl", s, big, 700)
    txt(d, (xb, 450), big, font, C(v.get("color", "red")), "mm")
    full = v.get("text", "")
    n = int(clamp((x.vt - 0.4) / 0.9) * len(full))
    f = fit_font("in_xb" if full.isascii() else "jp_bl", 104, full, 980)
    txt(d, (900, 410), full[:n], f, GOLD, "lm")
    if n < len(full) and int(x.vt * 3) % 2 == 0:
        cx = 900 + tw(f, full[:n]) + 8
        d.rectangle((cx, 360, cx + 6, 460), fill=GOLD)
    if v.get("jp"):
        p3 = _a(x, 1.3)
        txt(d, (904, 530), v["jp"], F("jp_m", 48), mix(TEXT, p3), "lm")


def t_teaser(d, v, x):
    a = ease(x.vt / 0.4)
    n = len(x.ep.get("phrases", [])) or 3
    spaced(d, (W / 2, 210), v.get("title", f"TODAY'S {n} PHRASES"), F("in_b", 36), mix(GOLD, a), 6, "m")
    widths = [(320, 260), (380, 180), (240, 120, 260), (300, 200)]
    gap = 150 if n <= 3 else 120
    for i in range(n):
        p = ease((x.vt - 0.25 - i * 0.25) / 0.45)
        y = 300 + i * gap + (1 - p) * 30
        rr(d, (360, y, 1560, y + gap - 38), 20, fill=mix(PANEL, p), outline=mix(LINE, p), width=2)
        cy = y + (gap - 38) / 2
        txt(d, (410, cy), f"0{i + 1}", F("in_bl", 48), mix(GOLD, p), "lm")
        xx = 520
        for wv in widths[i % 4]:
            rr(d, (xx, cy - 16, xx + wv, cy + 16), 10, fill=mix((52, 64, 92), p))
            xx += wv + 22
        txt(d, (1500, cy), "?", F("in_bl", 54), mix(MUTED, p), "mm")
    p = _a(x, 1.2)
    txt(d, (W / 2, 300 + n * gap + 20), v.get("note", "答えは動画の最後に"), F("jp_m", 34), mix(MUTED, p), "mm")


# ---------------------------------------------------------------- numbers
def _count_text(c, p):
    val = c["to"] * ease(p)
    dec = c.get("decimals", 0)
    s = f"{val:,.{dec}f}"
    return f"{c.get('prefix', '')}{s}{c.get('suffix', '')}"


def _panel(d, P, x0, x, delay=0.3):
    """Right-hand stat panel: rows of {kicker, big|count, color, sub}."""
    rows = P if isinstance(P, list) else [P]
    y = 250 if len(rows) > 1 else 300
    for i, r in enumerate(rows):
        a = _a(x, delay + i * 0.9)
        if i:
            d.rectangle((x0, y - 40, x0 + 700, y - 38), fill=mix(LINE, a))
        if r.get("kicker"):
            k = r["kicker"]
            txt(d, (x0, y), k, F("in_b" if k.isascii() else "jp_m", 28 if k.isascii() else 32),
                mix(GOLD if k.isascii() else MUTED, a), "lm")
            y += 80
        big = _count_text(r["count"], (x.vt - delay - i * 0.9) / 1.2) if r.get("count") else str(r.get("big", ""))
        size = r.get("size", 130 if len(rows) == 1 else 104)
        f = fit_font("in_bl" if big.isascii() else "jp_bl", size, big, 800)
        txt(d, (x0, y), big, f, mix(C(r.get("color", "text")), a), "lm")
        y += size * 0.75
        if r.get("sub"):
            txt(d, (x0 + 6, y), r["sub"], F("in_sb" if r["sub"].isascii() else "jp_m", 40), mix(TEXT, a), "lm")
            y += 56
        if r.get("note"):
            txt(d, (x0 + 6, y), r["note"], F("jp_m", 32), mix(MUTED, a), "lm")
            y += 50
        y += 70


def t_people(d, v, x):
    total, hit = v.get("total", 100), v.get("hit", 5)
    cols = 10
    rows = math.ceil(total / cols)
    rng = [(i * 37 + 13) % total for i in range(hit * 3)]
    cut = []
    for r_ in rng:
        if r_ not in cut:
            cut.append(r_)
        if len(cut) == hit:
            break
    cut = set(cut)
    p_cut = 1.0 if x.cont else ease((x.vt - 0.8) / 1.0)
    a_in = 1.0 if x.cont else ease(x.vt / 0.5)
    sy = 54 if rows <= 10 else 540 / rows
    for i in range(total):
        r, c = divmod(i, cols)
        cx, cy = 210 + c * 66, 200 + r * sy
        if i in cut:
            col = tuple(int(lerp(mix(TEXT, a_in * 0.85)[k], mix(RED, 1 - 0.75 * p_cut)[k], clamp(p_cut * 3))) for k in range(3))
        else:
            col = mix(DOT, a_in)
        person(d, cx, cy, col)
    txt(d, (525, 200 + rows * sy + 10), v.get("label", f"{total}人のうち{hit}人"), F("jp_m", 28), mix(MUTED, a_in), "mm")
    if v.get("panel"):
        _panel(d, v["panel"], 1010, x, 0.0 if x.cont else 0.3)


def t_counter(d, v, x):
    a = _a(x)
    if v.get("kicker"):
        k = v["kicker"]
        spaced(d, (W / 2, 230), k.upper(), F("in_b", 32), mix(GOLD, a), 6, "m") if k.isascii() else \
            txt(d, (W / 2, 230), k, F("jp_b", 40), mix(GOLD, a), "mm")
    s = _count_text(v, x.vt / 1.4) if "to" in v else str(v.get("big", ""))
    f = fit_font("in_bl" if s.isascii() else "jp_bl", 220, s, 1600)
    txt(d, (W / 2, 430), s, f, mix(C(v.get("color", "text")), a), "mm")
    p2 = _a(x, 1.0)
    if v.get("sub"):
        txt(d, (W / 2, 600), v["sub"], F("jp_b", 46), mix(TEXT, p2), "mm")
    if v.get("note"):
        txt(d, (W / 2, 680), v["note"], F("jp_m", 34), mix(MUTED, p2), "mm")


def t_bars(d, v, x):
    items = v["items"]
    a = _a(x)
    if v.get("title"):
        txt(d, (W / 2, 200), v["title"], F("jp_b", 44), mix(TEXT, a), "mm")
    mx = max(abs(i["value"]) for i in items) or 1
    n = len(items)
    gap = min(110, 520 / n)
    y0 = 300
    for k, it in enumerate(items):
        p = ease((x.vt - 0.2 - k * 0.15) / 0.8)
        y = y0 + k * gap
        txt(d, (520, y), it["label"], fit_font("jp_b", 36, it["label"], 340), mix(TEXT, a), "rm")
        wv = 900 * abs(it["value"]) / mx * p
        col = C(it.get("color", "gold"))
        rr(d, (560, y - gap * 0.3, 560 + max(wv, 8), y + gap * 0.3), 10, fill=mix(col, a))
        label = it.get("display", f"{it['value']:,}{v.get('unit', '')}")
        txt(d, (580 + wv, y), label, F("in_b" if label.isascii() else "jp_b", 34), mix(TEXT, p), "lm")
    if v.get("note"):
        txt(d, (W / 2, y0 + n * gap + 20), v["note"], F("jp_m", 30), mix(MUTED, _a(x, 1.0)), "mm")


# ---------------------------------------------------------------- comparisons
def t_vs(d, v, x):
    sides = [v["left"], v["right"]]
    for i, s in enumerate(sides):
        col = C(s.get("color", "green" if s.get("up", True) else "red"))
        up = s.get("up", True)
        p = ease((x.vt - i * 0.35) / 0.5)
        x0 = 300 + i * 680
        rr(d, (x0, 200, x0 + 620, 760), 28, fill=mix(PANEL, p), outline=mix(col, p * 0.6), width=3)
        if s.get("en"):
            spaced(d, (x0 + 310, 270), s["en"].upper(), F("in_b", 30), mix(col, p), 6, "m")
        txt(d, (x0 + 310, 340), s.get("label", ""), F("jp_b", 44), mix(TEXT, p), "mm")
        cx, cy = x0 + 310, 500
        dy = -1 if up else 1
        off = 14 * math.sin(x.ts * 2.4) * p
        sg = 1 if up else -1
        d.polygon([(cx - 80, cy + 40 * sg + off * dy), (cx + 80, cy + 40 * sg + off * dy), (cx, cy - 70 * sg + off * dy)],
                  fill=mix(col, p))
        val = s.get("val", "")
        txt(d, (cx, 670), val, fit_font("jp_bl", 64, val, 560), mix(col, p), "mm")
    if v.get("mid"):
        txt(d, (W / 2, 480), v["mid"], F("jp_b", 40), mix(MUTED, _a(x, 0.9)), "mm")


def t_quote(d, v, x):
    a = _a(x)
    rr(d, (220, 190, 1700, 720), 30, fill=mix(PANEL, a), outline=mix(LINE, a), width=2)
    txt(d, (300, 300), "“", F("in_bl", 200), mix(GOLD, a), "lm")
    lines = v["lines"]
    isen = all(l.isascii() for l in lines)
    size = 76 if len(lines) <= 2 else 60
    f = F("in_b" if isen else "jp_b", size)
    y = 450 - (len(lines) - 1) * size * 0.72
    for ln in lines:
        f2 = fit_font("in_b" if isen else "jp_b", size, ln, 1300)
        rich_line(d, 960, y, ln, f2, v.get("hl"), TEXT, a, hl_alpha=ease((x.vt - 0.6) / 0.4))
        y += size * 1.45
    if v.get("by"):
        txt(d, (960, 650), "— " + v["by"], F("jp_r", 28), mix(MUTED, _a(x, 0.5)), "mm")


def t_cards(d, v, x):
    items = v["items"]
    show = v.get("show", len(items))
    n = len(items)
    cw = min(500, (1600 - (n - 1) * 40) / n)
    x_start = (W - (n * cw + (n - 1) * 40)) / 2
    for i in range(show):
        it = items[i]
        new = (i == show - 1) and not (x.cont and v.get("_prev_show", 0) >= show)
        if x.cont and i < v.get("_prev_show", 0):
            p = 1.0
        else:
            p = ease((x.vt - (0 if i == 0 or x.cont else i * 0.45)) / 0.5)
        col = C(it.get("color", "red"))
        x0 = x_start + i * (cw + 40)
        y0 = 190 + (1 - p) * 30
        rr(d, (x0, y0, x0 + cw, y0 + 460), 26, fill=mix(PANEL, p), outline=mix(LINE, p), width=2)
        d.rectangle((x0 + 40, y0 + 46, x0 + 90, y0 + 52), fill=mix(col, p))
        txt(d, (x0 + 40, y0 + 100), it.get("name", ""), fit_font("in_b" if it.get("name", "").isascii() else "jp_b", 38, it.get("name", ""), cw - 70), mix(TEXT, p), "lm")
        big = str(it.get("big", ""))
        txt(d, (x0 + 40, y0 + 230), big, fit_font("jp_bl", 92, big, cw - 70), mix(col, p), "lm")
        if it.get("sub"):
            txt(d, (x0 + 40, y0 + 330), it["sub"], fit_font("jp_b", 40, it["sub"], cw - 70), mix(TEXT, p), "lm")
        if it.get("note"):
            txt(d, (x0 + 40, y0 + 400), it["note"], fit_font("jp_m", 28, it["note"], cw - 70), mix(MUTED, p), "lm")
    if v.get("footer"):
        txt(d, (W / 2, 705), v["footer"], F("jp_m", 32), mix(MUTED, 1 if x.cont else _a(x)), "mm")


def t_points(d, v, x):
    items = v["items"]
    show = v.get("show", len(items))
    n = len(items)
    cw = (1620 - (n - 1) * 40) / n
    for i in range(show):
        it = items[i]
        cur = i + 1 == show
        p = ease(x.vt / 0.5) if cur and not (x.cont and v.get("_prev_show", 0) >= show) else 1.0
        dim = 1.0 if cur else 0.55
        col = C(it.get("color", ["red", "blue", "green", "gold"][i % 4]))
        x0 = 150 + i * (cw + 40)
        y0 = 190 + (1 - p) * 30
        rr(d, (x0, y0, x0 + cw, y0 + 580), 28, fill=mix(PANEL, p),
           outline=mix(col if cur else LINE, p * (0.9 if cur else 1)), width=3 if cur else 2)
        txt(d, (x0 + 44, y0 + 70), it.get("num", f"0{i + 1}"), F("in_bl", 54), mix(col, p * dim), "lm")
        txt(d, (x0 + 44, y0 + 150), it.get("head", ""), F("jp_m", 34), mix(MUTED, p * dim), "lm")
        yy = y0 + 240
        for ln in str(it.get("big", "")).split("\n"):
            txt(d, (x0 + 44, yy), ln, fit_font("jp_bl", 58, ln, cw - 80), mix(TEXT, p * dim), "lm")
            yy += 76
        yy += 30
        for ln in str(it.get("sub", "")).split("\n"):
            txt(d, (x0 + 44, yy), ln, fit_font("jp_r", 30, ln, cw - 80), mix(MUTED, p * dim), "lm")
            yy += 44


def t_flow(d, v, x):
    rows = v["rows"]
    gap = 240 if len(rows) <= 2 else 170
    y_start = 260 if len(rows) <= 2 else 210
    for i, r in enumerate(rows):
        p = ease((x.vt - i * 0.6) / 0.5)
        ok = r.get("ok", True)
        col = GREEN if ok else RED
        y = y_start + i * gap
        h = 150 if len(rows) <= 2 else 120
        rr(d, (200, y, 760, y + h), 22, fill=mix(PANEL, p), outline=mix(col, p * 0.7), width=3)
        txt(d, (480, y + h / 2), r["a"], fit_font("jp_b", 36, r["a"], 520), mix(TEXT, p), "mm")
        d.line((790, y + h / 2, 900, y + h / 2), fill=mix(MUTED, p), width=4)
        d.polygon([(900, y + h / 2 - 15), (930, y + h / 2), (900, y + h / 2 + 15)], fill=mix(MUTED, p))
        mid = r.get("mid", "AI")
        rr(d, (960, y + 20, 1180, y + h - 20), 22, fill=mix(GOLD, p))
        txt(d, (1070, y + h / 2), mid, fit_font("in_bl" if mid.isascii() else "jp_bl", 56, mid, 200), mix(INK, p, mix(GOLD, p)), "mm")
        d.line((1210, y + h / 2, 1310, y + h / 2), fill=mix(MUTED, p), width=4)
        cx, cy = 1380, y + h / 2
        if ok:
            d.line([(cx - 30, cy), (cx - 8, cy + 24), (cx + 32, cy - 26)], fill=mix(col, p), width=12)
        else:
            d.line((cx - 30, cy - 30, cx + 30, cy + 30), fill=mix(col, p), width=12)
            d.line((cx + 30, cy - 30, cx - 30, cy + 30), fill=mix(col, p), width=12)
        txt(d, (1450, cy), r.get("res", ""), fit_font("jp_m", 34, r.get("res", ""), 420), mix(TEXT, p), "lm")


def t_layers(d, v, x):
    a = 1.0 if x.cont else ease(x.vt / 0.5)
    cx, base = 760, 720
    pal = [(43, 58, 92), (52, 80, 122), (62, 106, 154), (72, 126, 176)]
    y = base
    for i, lab in enumerate(v["layers"]):
        p = 1.0 if x.cont else ease((x.vt - i * 0.25) / 0.5)
        h_, wv = 104, 640 - i * 40
        yy = y - h_ + (1 - p) * 40
        col = pal[i % 4]
        if v.get("glow"):
            col = tuple(int(lerp(col[k], col[k] + 40, 0.5 + 0.5 * math.sin(x.ts * 3))) for k in range(3))
        rr(d, (cx - wv / 2, yy, cx + wv / 2, yy + h_ - 6), 18, fill=mix(col, p))
        txt(d, (cx, yy + h_ / 2 - 3), lab, fit_font("jp_b", 34, lab, wv - 40), mix(TEXT, p, mix(col, p)), "mm")
        y -= h_
    top_y = y
    ic = v.get("icing")
    if ic:
        p = 1.0 if (x.cont and v.get("_prev_icing")) else ease_io(x.vt / 0.9)
        off = (1 - p) * -260
        wv = 560
        iy = top_y - 58 + off
        rr(d, (cx - wv / 2 - 10, iy, cx + wv / 2 + 10, iy + 56), 26, fill=GOLD)
        for k, dx in enumerate([-200, -110, -20, 80, 170, 230]):
            hh = 6 + 7 * ((k * 37) % 3)
            d.ellipse((cx + dx - 16, iy + 30, cx + dx + 16, iy + 52 + hh), fill=GOLD)
        lab = ic.get("label", "AI")
        txt(d, (cx, iy + 28), lab, fit_font("in_bl" if lab.isascii() else "jp_bl", 40, lab, 500), INK, "mm")
        q = 1.0 if (x.cont and v.get("_prev_icing")) else ease((x.vt - 0.8) / 0.5)
        d.line((cx + wv / 2 + 30, iy + 28, 1180, iy + 28), fill=mix(GOLD, q), width=3)
        if ic.get("en"):
            txt(d, (1200, iy + 10), ic["en"], fit_font("in_b", 46, ic["en"], 680), mix(GOLD, q), "lm")
        if ic.get("jp"):
            txt(d, (1200, iy + 70), ic["jp"], F("jp_m", 32), mix(TEXT, q), "lm")
        if ic.get("en2"):
            txt(d, (1200, base - 150), ic["en2"], fit_font("in_b", 46, ic["en2"], 680), mix(TEXT, q), "lm")
        if ic.get("jp2"):
            txt(d, (1200, base - 90), ic["jp2"], F("jp_m", 32), mix(MUTED, q), "lm")
    if v.get("footer"):
        q = ease(x.vt / 0.5)
        f = v["footer"]
        txt(d, (1200, base - 20), f, F("in_b" if f.isascii() else "jp_b", 40), mix(GREEN, q), "lm")


def _org_nodes(p):
    nodes, links = [], []
    cx0 = 960
    top = (cx0, lerp(220, 250, p))
    nodes.append(("top", top, 1.0))
    l1x = [cx0 - 360, cx0 + 360]
    l1y = lerp(340, 440, p)
    for xx in l1x:
        nodes.append(("l1", (xx, l1y), 1.0))
        links.append((top, (xx, l1y), 1.0))
    l2x = [cx0 - 540, cx0 - 180, cx0 + 180, cx0 + 540]
    for i, xx in enumerate(l2x):
        nodes.append(("l2", (xx, 460), 1 - p))
        links.append(((l1x[i // 2], l1y), (xx, 460), 1 - p))
    sx = [cx0 - 630 + i * 180 for i in range(8)]
    for i, xx in enumerate(sx):
        nodes.append(("st", (xx, 640), 1.0))
        links.append(((l2x[i // 2], 460), (xx, 640), 1 - p))
        links.append(((l1x[i // 4], l1y), (xx, 640), p))
    return nodes, links


def t_org(d, v, x):
    flat = v.get("flat", False)
    p = 0.0 if not flat else (1.0 if x.cont and v.get("_prev_flat") else ease_io((x.vt - 0.3) / 1.4))
    a = 1.0 if x.cont else ease(x.vt / 0.5)
    nodes, links = _org_nodes(p)
    for s, e, la in links:
        if la > 0.02:
            d.line((s[0], s[1] + 22, e[0], e[1] - 22), fill=mix(LINE, a * la), width=3)
    for kind, (xx, yy), na in nodes:
        if na <= 0.02:
            continue
        if kind == "st":
            person(d, xx, yy + 10, mix((130, 144, 170), a * na), 1.1)
        else:
            col = GOLD if kind == "top" else ((90, 108, 140) if kind == "l1" else (RED if p > 0 else (90, 108, 140)))
            sc = 1 - 0.4 * p if kind == "l2" else 1
            wv, hv = 120 * sc, 44 * sc
            rr(d, (xx - wv / 2, yy - hv / 2, xx + wv / 2, yy + hv / 2), 12, fill=mix(col, a * na))
    f = F("in_b", 26)
    txt(d, (150, 760), "LAYERS", f, mix(MUTED, a), "lm")
    txt(d, (300, 760), str(round(lerp(4, 3, p))), F("in_bl", 56), mix(GOLD if p > 0.5 else TEXT, a), "lm")
    txt(d, (460, 760), "SPAN OF CONTROL", f, mix(MUTED, a), "lm")
    txt(d, (740, 760), str(round(lerp(2, 4, p))), F("in_bl", 56), mix(GOLD if p > 0.5 else TEXT, a), "lm")
    if v.get("label") and flat:
        q = ease((x.vt - 1.6) / 0.5) if not (x.cont and v.get("_prev_flat")) else 1
        rr(d, (1230, 730, 1770, 792), 30, fill=mix(GOLD, q))
        txt(d, (1500, 761), v["label"], fit_font("in_b", 34, v["label"], 500), mix(INK, q, mix(GOLD, q)), "mm")


def t_statement(d, v, x):
    a = _a(x)
    k = v.get("kicker", "")
    if k:
        f = fit_font("in_bl", 120, k, 1600) if k.isascii() else fit_font("jp_bl", 100, k, 1600)
        if k.isascii():
            spaced(d, (W / 2, 330), k, f, mix(GOLD, a), 10, "m")
        else:
            txt(d, (W / 2, 330), k, f, mix(GOLD, a), "mm")
    p = _a(x, 0.4)
    y = 500
    for ln in str(v.get("text", "")).split("\n"):
        txt(d, (W / 2, y), ln, fit_font("jp_b", 56, ln, 1600), mix(TEXT, p), "mm")
        y += 80
    if v.get("sub"):
        txt(d, (W / 2, y + 20), v["sub"], F("jp_m", 34), mix(MUTED, _a(x, 0.8)), "mm")


def t_timeline(d, v, x):
    items = v["items"]
    show = v.get("show", len(items))
    n = len(items)
    y0, y1 = 220, 740
    step = (y1 - y0) / max(1, n - 1) if n > 1 else 0
    d.line((420, y0, 420, y0 + step * (n - 1)), fill=LINE, width=4)
    for i in range(show):
        it = items[i]
        p = 1.0 if (x.cont and i < v.get("_prev_show", 0)) else ease((x.vt - (0 if x.cont else i * 0.35)) / 0.5)
        y = y0 + i * step
        col = C(it.get("color", "gold"))
        d.ellipse((420 - 16, y - 16, 420 + 16, y + 16), fill=mix(col, p))
        txt(d, (380, y), it.get("when", ""), fit_font("jp_b", 34, it.get("when", ""), 300), mix(col, p), "rm")
        txt(d, (470, y), it.get("text", ""), fit_font("jp_m", 38, it.get("text", ""), 1300), mix(TEXT, p), "lm")


TEMPLATES = {
    "hero": t_hero, "hero_side": t_hero_side, "teaser": t_teaser,
    "people": t_people, "counter": t_counter, "bars": t_bars,
    "vs": t_vs, "quote": t_quote, "cards": t_cards, "points": t_points,
    "flow": t_flow, "layers": t_layers, "org": t_org, "statement": t_statement, "timeline": t_timeline,
}
