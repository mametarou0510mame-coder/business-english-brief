"""Instagram carousel (1080x1350, 5 slides): a save-worthy summary of the episode's 3 phrases.

1 cover   : 会議で使える英語3つ + the news headline + its big number/word
2-4       : one phrase each — English, meaning, workplace example (EN/JP)
5         : key words + "保存して、会議の前に見返そう" + YouTube pointer
"""
import os
from PIL import ImageDraw
from core import *  # noqa

W, H = 1080, 1350


def _base(n, total):
    img = make_bg(W, H, (0.5, 0.25), 60).convert("RGB")
    d = ImageDraw.Draw(img)
    rr(d, (60, 60, 108, 108), 12, fill=GOLD)
    txt(d, (84, 84), "B", F("in_bl", 32), INK, "mm")
    txt(d, (124, 83), "Business English Brief", F("in_sb", 30), TEXT, "lm")
    txt(d, (W - 60, 83), f"{n}/{total}", F("in_sb", 30), MUTED, "rm")
    return img, d


def _big(ep):
    for sc in ep["scenes"][:1]:
        for b in sc["beats"]:
            v = b.get("vis") or {}
            if v.get("big"):
                return v["big"], C(v.get("color", "gold"), GOLD)
    return "", GOLD


def build(ep, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    ph = ep["phrases"][:3]
    total = len(ph) + 2
    paths = []

    img, d = _base(1, total)
    txt(d, (W / 2, 250), "会議で使える英語", F("jp_bl", 92), TEXT, "mm")
    txt(d, (W / 2, 370), f"{len(ph)}つ", F("jp_bl", 120), GOLD, "mm")
    big, col = _big(ep)
    if big:
        jp = any(ord(c) > 0x3000 for c in big)
        txt(d, (W / 2, 640), big, fit_font("jp_bl" if jp else "in_bl", 230, big, 900, 80), col, "mm")
    y = 850
    for ln in (ep["title_card"]["line1"], ep["title_card"]["line2"]):
        txt(d, (W / 2, y), ln, fit_font("jp_b", 54, ln, 940, 30), SOFT, "mm")
        y += 80
    rr(d, (W / 2 - 330, 1130, W / 2 + 330, 1220), 45, fill=GOLD)
    txt(d, (W / 2, 1175), "スワイプして答えを見る →", F("jp_b", 40), INK, "mm")
    paths.append(img)

    for i, p in enumerate(ph):
        img, d = _base(i + 2, total)
        txt(d, (W / 2, 210), f"PHRASE {i + 1}", F("in_bl", 40), GOLD, "mm")
        rr(d, (60, 270, W - 60, 560), 34, fill=PANEL, outline=GOLD, width=3)
        f = fit_font("in_bl", 96, p["en"], 820, 48)
        rich_line(d, W / 2, 415, p["en"], f, [p["en"]], TEXT, 1.0)
        txt(d, (W / 2, 640), "意味", F("jp_b", 34), MUTED, "mm")
        txt(d, (W / 2, 730), p["jp"], fit_font("jp_bl", 80, p["jp"], 940, 40), GOLD, "mm")
        rr(d, (60, 840, W - 60, 1240), 28, fill=PANEL, outline=LINE, width=2)
        txt(d, (100, 890), "例文", F("jp_b", 34), GOLD, "lm")
        fe = F("in_sb", 46)
        y = 970
        for ln in balance_wrap(wrap_en, p["ex"], fe, 880)[:3]:
            rich_line(d, W / 2, y, ln, fe, [p["en"]], TEXT, 1.0)
            y += 64
        fj = F("jp_m", 38)
        for ln in balance_wrap(wrap_jp, p["ex_jp"], fj, 880)[:2]:
            txt(d, (W / 2, y + 16), ln, fj, SOFT, "mm")
            y += 54
        paths.append(img)

    img, d = _base(total, total)
    txt(d, (W / 2, 220), "あわせて覚えたい単語", F("jp_bl", 64), TEXT, "mm")
    y = 340
    for w in ep.get("words", [])[:3]:
        rr(d, (90, y, W - 90, y + 140), 26, fill=PANEL, outline=LINE, width=2)
        txt(d, (140, y + 70), w["en"], fit_font("in_b", 52, w["en"], 440, 30), TEXT, "lm")
        txt(d, (W - 140, y + 70), w["jp"], fit_font("jp_b", 44, w["jp"], 400, 26), GOLD, "rm")
        y += 170
    txt(d, (W / 2, 930), "保存して、会議の前に見返そう", F("jp_bl", 56), GOLD, "mm")
    txt(d, (W / 2, 1030), "ニュースの解説と音声は", F("jp_m", 40), SOFT, "mm")
    txt(d, (W / 2, 1090), "プロフィールのYouTubeから", F("jp_m", 40), SOFT, "mm")
    rr(d, (W / 2 - 300, 1160, W / 2 + 300, 1240), 40, outline=GOLD, width=3)
    txt(d, (W / 2, 1200), "@businessenglishbrief", F("in_sb", 38), GOLD, "mm")
    paths.append(img)

    files = []
    for i, im in enumerate(paths):
        fp = os.path.join(out_dir, f"c{i + 1}.jpg")
        im.save(fp, quality=92)
        files.append(fp)
    return files


def caption(ep):
    ph = ep["phrases"][:3]
    lines = [f"「{ph[0]['jp']}」、英語で言えますか?", "", "📰 今日のニュース", ep["youtube"]["summary"], "",
             "このニュースから、会議で使える英語を3つ。"]
    for i, p in enumerate(ph):
        lines += ["", f"{i + 1}️⃣ {p['en']}", p["jp"], f"例:{p['ex']}"]
    lines += ["", "📌 保存して、次の会議の前に見返そう", "▼ ニュースの解説と音声はプロフィールのYouTubeから", "",
              "#ビジネス英語 #英語学習 #英会話 #ニュース英語 #社会人の勉強 #会議英語 #英語フレーズ"]
    return "\n".join(lines)
