"""1280x720 YouTube thumbnail from episode['thumbnail'].

Fields: big (e.g. "5%"), big_color, under (large JP word under the number), badge (pill text),
badge_color, question (JP line), pill (English phrase on gold), bottom (JP line, gold).
"""
from PIL import ImageDraw
from core import *  # noqa


def build(ep, out):
    th = ep["thumbnail"]
    W_, H_ = 1280, 720
    img = make_bg(W_, H_, (0.15, 0.2), 48)
    d = ImageDraw.Draw(img)
    big = str(th["big"])
    f = fit_font("in_bl" if big.isascii() else "jp_bl", 360 if len(big) <= 3 else 260, big, 600)
    d.text((70, 330), big, font=f, fill=C(th.get("big_color", "red")), anchor="lm")
    if th.get("crack", True) and big.isascii():
        d.line([(90, 230), (230, 300), (290, 280), (390, 380), (450, 360), (600, 460)], fill=BG, width=14)
    if th.get("under"):
        d.text((80, 560), th["under"], font=fit_font("jp_bl", 92, th["under"], 560), fill=TEXT, anchor="lm")
    x = 700
    if th.get("badge"):
        d.rounded_rectangle((x - 10, 120, x + 520, 190), radius=14, fill=C(th.get("badge_color", "green")))
        d.text((x + 255, 156), th["badge"], font=fit_font("jp_bl", 46, th["badge"], 500), fill=INK, anchor="mm")
    if th.get("question"):
        d.text((x + 255, 280), th["question"], font=fit_font("jp_bl", 76, th["question"], 540), fill=TEXT, anchor="mm")
    if th.get("pill"):
        s = th["pill"]
        fp = fit_font("in_xb" if s.isascii() else "jp_bl", 70, s, 500)
        wv = tw(fp, s)
        d.rounded_rectangle((x + 255 - wv / 2 - 22, 360, x + 255 + wv / 2 + 22, 460), radius=18, fill=GOLD)
        d.text((x + 255, 408), s, font=fp, fill=INK, anchor="mm")
    if th.get("bottom"):
        d.text((x + 255, 520), th["bottom"], font=fit_font("jp_b", 46, th["bottom"], 540), fill=GOLD, anchor="mm")
    d.rounded_rectangle((40, 640, 92, 692), radius=10, fill=GOLD)
    d.text((66, 667), "B", font=F("in_bl", 36), fill=INK, anchor="mm")
    d.text((106, 666), f"Business English Brief  {ep['episode']}", font=F("in_sb", 28), fill=MUTED, anchor="lm")
    img.save(out, optimize=True)
    return out
