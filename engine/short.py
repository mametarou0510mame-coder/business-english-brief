"""Vertical 1080x1920 shorts, drawn natively for the phone (no cropped 16:9 frames). About 20 seconds.

0s     The first frame already shows the news headline, its big number/word and the quiz promise.
News   The long video's opening narration (h01, h02 if short) with large captions.
Quiz   English phrase (audio) → 2s countdown → English again + Japanese meaning → example (EN, then JP).
End    Phrase + meaning + save prompt + "くわしい解説は本編で", then the video loops.
Audio is cut from the long video's mix beat by beat.
"""
import os, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw
from core import *  # noqa
import render as R

SW, SH = 1080, 1920
END = 1.8
GAP = 0.12
NEWS_MAX = 10.5        # seconds of news narration at most
QUIZ_STEPS = ("1", "2", "3", "4", "5", "7")   # review beats v{k}1..; skips the 3s repeat pause and the final echo


@lru_cache(maxsize=1)
def vbg():
    return make_bg(SW, SH, (0.5, 0.32), 60)


def _parts(ep, tl, spec):
    """[(kind, phase, beat, local_start, local_end)]"""
    hook, card = [], spec["phrase"]
    for b in tl["beats"]:
        if b["scene"] != 0:
            break
        if isinstance(b.get("vis"), dict) and b["vis"].get("t") == "teaser":
            break
        if b["kind"] in ("silent", "pause"):
            continue
        if hook and sum(x["dur"] for x in hook) + b["dur"] > NEWS_MAX:
            break
        hook.append(b)
    quiz = {b["id"][-1]: b for b in tl["beats"] if tl["scenes"][b["scene"]]["visual"] == "review"
            and isinstance(b.get("vis"), dict) and b["vis"].get("card") == card and b["id"].startswith("v")}
    seq = [("news", "news", b) for b in hook] if spec.get("news", True) else []
    seq += [("quiz", s, quiz[s]) for s in QUIZ_STEPS if s in quiz]
    out, t = [], 0.0
    for kind, ph, b in seq:
        d = b["dur"] if b["kind"] != "pause" else min(b["dur"], 2.0)
        out.append((kind, ph, b, t, t + d))
        t += d + GAP
    return out, t - GAP


def _big(ep, hook_beats):
    """The headline element of the long video's first beat (e.g. 完売 / −17.6%), with its colour and kicker."""
    for b in hook_beats:
        v = b.get("vis") or {}
        if v.get("big"):
            return v["big"], C(v.get("color", "gold"), GOLD), (v.get("kicker") or "").upper()
    return "", GOLD, ""


def build(ep, tl, idx, long_mp4, out, preview=None):
    spec = ep["shorts"][idx]
    P = ep["phrases"][spec["phrase"]]
    parts, body = _parts(ep, tl, spec)
    total = body + END
    news_hook = spec.get("news_hook") or [ep["title_card"]["line1"], ep["title_card"]["line2"]]
    big, big_col, kicker = _big(ep, [p[2] for p in parts if p[0] == "news"])
    first_quiz = next((p[3] for p in parts if p[0] == "quiz"), body)
    starts = {p[1]: p[3] for p in parts if p[0] == "quiz"}

    def cur(ts):
        for p in parts:
            if p[3] <= ts < p[4] + GAP:
                return p
        return None

    def phrase_card(d, y0, a, speaking_t=None):
        rr(d, (70, y0, SW - 70, y0 + 300), 34, fill=mix(PANEL, a), outline=mix(GOLD, a * 0.8), width=3)
        f = fit_font("in_bl", 92, P["en"], 780, 50)
        rich_line(d, SW / 2, y0 + 130, P["en"], f, [P["en"]], TEXT, a)
        if speaking_t is not None:
            wave(d, SW / 2, y0 + 240, speaking_t, GOLD, n=11, w=9, gap=9, hmax=40)

    def frame(ts):
        img = vbg().copy()
        d = ImageDraw.Draw(img)
        rr(d, (60, 110, 108, 158), 12, fill=GOLD)
        txt(d, (84, 134), "B", F("in_bl", 32), INK, "mm")
        txt(d, (124, 133), "Business English Brief", F("in_sb", 30), TEXT, "lm")
        p = cur(ts)
        kind = "end" if (p is None or ts >= body) else p[0]
        if kind == "news":
            _, _, b, l0, l1 = p
            tb = ts - l0
            # quiz promise, visible from frame 0
            rr(d, (170, 205, SW - 170, 275), 35, fill=GOLD)
            txt(d, (SW / 2, 240), "最後に英語クイズ。わかるかな?", F("jp_b", 36), INK, "mm")
            txt(d, (SW / 2, 345), "今日のニュース", F("jp_b", 40), GOLD, "mm")
            y = 440
            for ln in news_hook[:2]:
                txt(d, (SW / 2, y), ln, fit_font("jp_bl", 84, ln, 960), TEXT, "mm")
                y += 108
            if big:
                pop = ease(ts / 0.25) if ts < 0.25 else 1.0
                if kicker:
                    spaced(d, (SW / 2, 700), kicker, F("in_sb", 30), MUTED, 8, "m")
                jp = any(ord(c) > 0x3000 for c in big)
                fb = fit_font("jp_bl" if jp else "in_bl", int(240 * (0.92 + 0.08 * pop)), big, 940, 80)
                txt(d, (SW / 2, 850), big, fb, big_col, "mm")
            # captions: Japanese narration large, English below
            a = ease(tb / 0.15)
            fj, fe = F("jp_b", 46), F("in_m", 36)
            y = 1075
            for ln in balance_wrap(wrap_jp, b.get("jp", ""), fj, 960)[:3]:
                txt(d, (SW / 2, y), ln, fj, mix(TEXT, a), "mm")
                y += 66
            y += 14
            for ln in balance_wrap(wrap_en, b.get("en", ""), fe, 940)[:2]:
                rich_line(d, SW / 2, y, ln, fe, b.get("hl"), SOFT, a)
                y += 54
        elif kind == "quiz":
            _, ph, b, l0, l1 = p
            tb = ts - l0
            txt(d, (SW / 2, 260), "QUIZ", F("in_bl", 40), GOLD, "mm")
            q = "この英語、どういう意味?"
            txt(d, (SW / 2, 345), q, fit_font("jp_bl", 66, q, 960), TEXT, "mm")
            a = ease((ts - first_quiz) / 0.25)
            speaking = tb if (b["kind"] == "rv_en" and ph in ("1", "3") and tb < b["dur"]) else None
            phrase_card(d, 470, a, speaking)
            if ph in ("1", "2"):
                prog = 0.0 if ph == "1" else clamp(tb / (l1 - l0))
                ring(d, SW / 2, 1010, 92, prog, GOLD, width=12)
                n = str(max(1, int((l1 - ts) + 0.999))) if ph == "2" else "?"
                txt(d, (SW / 2, 1010), n, F("in_bl", 92), TEXT, "mm")
                txt(d, (SW / 2, 1170), "考えてみよう", F("jp_b", 42), MUTED, "mm")
            else:
                ra = ease((ts - starts.get("3", l0)) / 0.3)
                txt(d, (SW / 2, 880), "意味", F("jp_b", 36), mix(MUTED, ra), "mm")
                txt(d, (SW / 2, 975), P["jp"], fit_font("jp_bl", 84, P["jp"], 940, 44), mix(GOLD, ra), "mm")
                if ph in ("5", "7"):
                    ea = ease((ts - starts.get("5", l0)) / 0.3)
                    rr(d, (70, 1100, SW - 70, 1440), 28, fill=mix(PANEL, ea), outline=mix(LINE, ea), width=2)
                    txt(d, (110, 1145), "例文", F("jp_b", 32), mix(GOLD, ea), "lm")
                    fe = F("in_sb", 44)
                    y = 1215
                    for ln in balance_wrap(wrap_en, P["ex"], fe, 860)[:3]:
                        rich_line(d, SW / 2, y, ln, fe, [P["en"]], TEXT, ea)
                        y += 60
                    ja = ease((ts - starts.get("7", l0)) / 0.3) if ph == "7" else 0.0
                    fj = F("jp_m", 36)
                    for ln in balance_wrap(wrap_jp, P["ex_jp"], fj, 860)[:2]:
                        txt(d, (SW / 2, y + 12), ln, fj, mix(SOFT, ja * ea), "mm")
                        y += 50
        else:
            a = ease((ts - body) / 0.3)
            txt(d, (SW / 2, 345), "今日の英語", F("jp_bl", 60), mix(GOLD, a), "mm")
            phrase_card(d, 470, a)
            txt(d, (SW / 2, 900), P["jp"], fit_font("jp_bl", 80, P["jp"], 940, 44), mix(GOLD, a), "mm")
            txt(d, (SW / 2, 1040), "保存して、次の会議前に見返そう", F("jp_b", 44), mix(TEXT, a), "mm")
            rr(d, (SW / 2 - 320, 1150, SW / 2 + 320, 1240), 45, outline=mix(GOLD, a), width=3)
            txt(d, (SW / 2, 1195), "くわしい解説は本編で", F("jp_b", 40), mix(GOLD, a), "mm")
        d.rectangle((0, SH - 10, int(SW * ts / total), SH), fill=GOLD)
        return img

    if preview is not None:
        return [frame(x) for x in preview], parts

    tmpv = out + ".v.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SW}x{SH}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmpv]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(total * FPS)):
        p.stdin.write(frame(i / FPS).convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    # audio: each spoken beat cut from the long video's mix, placed at its local start
    inputs, filt, k = [], [], 0
    for kind, ph, b, l0, l1 in parts:
        if b["kind"] == "pause":
            continue
        inputs += ["-ss", f"{b['start']:.3f}", "-t", f"{l1 - l0:.3f}", "-i", long_mp4]
        ms = int(l0 * 1000)
        filt.append(f"[{k + 1}:a]afade=t=in:d=0.03,afade=t=out:st={max(0, l1 - l0 - 0.12):.2f}:d=0.12,adelay={ms}|{ms}[a{k}]")
        k += 1
    filt.append("".join(f"[a{i}]" for i in range(k)) + f"amix=inputs={k}:normalize=0,apad[aout]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmpv, *inputs, "-filter_complex", ";".join(filt),
                    "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-t", f"{total:.3f}", "-movflags", "+faststart", out], check=True)
    os.remove(tmpv)
    cover = out.replace(".mp4", ".jpg")
    frame(0.5).convert("RGB").save(cover, quality=90)
    return out, cover
