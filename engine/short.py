"""Vertical 1080x1920 shorts: a news summary (the long video's hook scene) followed by one phrase quiz.

Part 1 "news"  : the hook scene of the long video — its visual (cropped) plus large captions, with its narration.
Part 2 "quiz"  : the review card for spec["phrase"] — English → pause → Japanese → example → repeat.
End card       : the phrase, its meaning, a save prompt.
"""
import os, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw
from core import *  # noqa
import render as R

SW, SH = 1080, 1920
END = 2.2
GAP_BETWEEN = 0.4


@lru_cache(maxsize=1)
def vbg():
    return make_bg(SW, SH, (0.2, 0.15), 60)


@lru_cache(maxsize=1)
def edge(h=492):
    m = Image.new("L", (1080, h), 255)
    dm = ImageDraw.Draw(m)
    for i in range(50):
        dm.rectangle((i, i, 1079 - i, h - 1 - i), outline=int(255 * i / 50))
    return m


def _segments(ep, tl, spec):
    card = spec["phrase"]
    hook_scene = 0
    news = []
    for b in tl["beats"]:
        if b["scene"] != hook_scene or (isinstance(b.get("vis"), dict) and b["vis"].get("t") == "teaser"):
            if news:
                break
            continue
        if b["kind"] != "silent":
            news.append(b)
    quiz = [b for b in tl["beats"] if isinstance(b.get("vis"), dict) and b["vis"].get("card") == card
            and tl["scenes"][b["scene"]]["visual"] == "review"]
    segs = []
    if news and spec.get("news", True):
        segs.append(("news", news[0]["start"], news[-1]["start"] + news[-1]["dur"]))
    segs.append(("quiz", quiz[0]["start"], quiz[-1]["start"] + quiz[-1]["dur"] + 0.3))
    return segs


def _captions(d, b, tb, y0):
    """Large vertical-friendly captions for the news part: English (with highlights) then Japanese."""
    a = ease(tb / 0.18)
    en, jp = b.get("en", ""), b.get("jp", "")
    fen, fjp = F("in_b", 46), F("jp_m", 36)
    y = y0
    for ln in balance_wrap(wrap_en, en, fen, 940)[:3]:
        rich_line(d, SW / 2, y, ln, fen, b.get("hl"), TEXT, a)
        y += 64
    y += 10
    for ln in balance_wrap(wrap_jp, jp, fjp, 940)[:3]:
        txt(d, (SW / 2, y), ln, fjp, mix(SOFT, a), "mm")
        y += 52


def build(ep, tl, idx, long_mp4, out, preview=None):
    spec = ep["shorts"][idx]
    P = ep["phrases"][spec["phrase"]]
    segs = _segments(ep, tl, spec)
    # local timeline: list of (kind, local_start, local_end, src_start)
    parts, t = [], 0.0
    for kind, s0, s1 in segs:
        parts.append((kind, t, t + (s1 - s0), s0))
        t += (s1 - s0) + GAP_BETWEEN
    body = t - GAP_BETWEEN
    total = body + END

    def frame(ts):
        img = vbg().copy()
        d = ImageDraw.Draw(img)
        rr(d, (60, 120, 112, 172), 12, fill=GOLD)
        txt(d, (86, 147), "B", F("in_bl", 34), INK, "mm")
        txt(d, (128, 146), "Business English Brief", F("in_sb", 32), TEXT, "lm")
        cur = None
        for kind, l0, l1, s0 in parts:
            if l0 <= ts < l1 + GAP_BETWEEN:
                cur = (kind, l0, l1, s0)
                break
        if ts >= body or cur is None:
            kind = "end"
        else:
            kind = cur[0]
        if kind == "news":
            txt(d, (SW / 2, 270), spec.get("news_kicker", "今日のニュース"), F("jp_b", 42), GOLD, "mm")
            y = 370
            for ln in spec.get("news_hook") or [ep["title_card"]["line1"], ep["title_card"]["line2"]]:
                txt(d, (SW / 2, y), ln, fit_font("jp_bl", 72, ln, 980), TEXT, "mm")
                y += 96
        else:
            txt(d, (SW / 2, 270), spec.get("kicker", "この英語、意味わかる?"), F("jp_b", 42), GOLD, "mm")
            y = 370
            for ln in spec["hook"][:2]:
                txt(d, (SW / 2, y), ln, fit_font("jp_bl", 80, ln, 980), TEXT, "mm")
                y += 104
        if kind in ("news", "quiz"):
            _, l0, l1, s0 = cur
            src_t = s0 + min(ts - l0, l1 - l0 - 1 / FPS)
            src = R.frame(ep, tl, src_t)
            if kind == "news":
                img.paste(src.crop((0, 120, 1920, 840)).resize((1080, 405), Image.LANCZOS), (0, 650), edge(405))
            else:
                img.paste(src.crop((170, 120, 1750, 840)).resize((1080, 492), Image.LANCZOS), (0, 600), edge())
            d = ImageDraw.Draw(img)
            if kind == "news":
                b = R.find(tl, src_t)
                if b["kind"] not in ("silent", "pause"):
                    _captions(d, b, src_t - b["start"], 1105)
        else:
            p = ease((ts - body) / 0.4)
            rr(d, (70, 640, SW - 70, 1060), 30, fill=mix(PANEL, p), outline=mix(LINE, p), width=2)
            rich_line(d, SW / 2, 770, P["en"], fit_font("in_b", 62, P["en"], 880), [P["en"]], TEXT, p)
            txt(d, (SW / 2, 880), P["jp"], fit_font("jp_b", 50, P["jp"], 900), mix(GOLD, p), "mm")
            txt(d, (SW / 2, 980), "保存して、次の会議前に見返そう", F("jp_m", 34), mix(MUTED, p), "mm")
        if kind != "news":
            txt(d, (SW / 2, 1200), spec.get("ctx", ""), fit_font("jp_m", 34, spec.get("ctx", ""), 980), MUTED, "mm")
        if kind != "news":   # the news part's captions use this space, so the CTA only shows with the quiz and end card
            rr(d, (SW / 2 - 300, 1400, SW / 2 + 300, 1480), 40, outline=GOLD, width=3)
            txt(d, (SW / 2, 1440), "くわしい解説は本編で", F("jp_b", 36), GOLD, "mm")
        d.rectangle((0, SH - 8, int(SW * ts / total), SH), fill=GOLD)
        return img

    if preview is not None:   # list of local times -> return frames without encoding
        return [frame(x) for x in preview], parts

    tmpv = out + ".v.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SW}x{SH}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmpv]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(total * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    # audio: each segment cut from the long video's mix, joined with short gaps
    inputs, filt = [], []
    for k, (kind, l0, l1, s0) in enumerate(parts):
        inputs += ["-ss", f"{s0:.3f}", "-t", f"{l1 - l0:.3f}", "-i", long_mp4]
        ms = int(l0 * 1000)
        filt.append(f"[{k + 1}:a]afade=t=in:d=0.04,afade=t=out:st={max(0, l1 - l0 - 0.25):.2f}:d=0.25,adelay={ms}|{ms}[a{k}]")
    filt.append("".join(f"[a{k}]" for k in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,apad[aout]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmpv, *inputs, "-filter_complex", ";".join(filt),
                    "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-t", f"{total:.3f}", "-movflags", "+faststart", out], check=True)
    os.remove(tmpv)
    cover = out.replace(".mp4", ".jpg")
    frame(min(2.5, body / 3)).convert("RGB").save(cover, quality=90)
    return out, cover
