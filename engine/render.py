"""Frame and video rendering for the 16:9 long-form episode."""
import math, os, subprocess
from types import SimpleNamespace
from PIL import Image, ImageDraw
from core import *  # noqa
from templates import TEMPLATES

NO_SUB = {"silent", "pause", "rv_en", "rv_jp"}
ORDER = ["quiz", "count", "reveal", "example", "repeat", "example_jp", "final"]


def chrome(d, ep, tl, t, scene):
    d.rectangle((0, 0, int(W * t / tl["total"]), 5), fill=GOLD)
    rr(d, (60, 44, 104, 88), 10, fill=GOLD)
    txt(d, (82, 67), "B", F("in_bl", 30), INK, "mm")
    txt(d, (122, 58), "Business English Brief", F("in_sb", 24), TEXT, "lm")
    txt(d, (122, 82), "EP " + str(ep["episode"]).lstrip("#"), F("in_m", 16), MUTED, "lm")
    ch = scene.get("chapter")
    if ch:
        f = F("jp_m", 24)
        x = W - 60 - tw(f, ch)
        d.ellipse((x - 26, 60, x - 14, 72), fill=GOLD)
        txt(d, (x, 66), ch, f, MUTED, "lm")


def subtitles(d, b, tb):
    a = ease(tb / 0.18)
    k = b["kind"]
    en, jp = b.get("en", ""), b.get("jp", "")
    fen = F("in_b", 50) if k == "en_insert" else F("in_sb", 44)
    fjp = F("jp_r", 30)
    en_lines = balance_wrap(wrap_en, en, fen, 1560) if en else []
    jp_lines = balance_wrap(wrap_jp, jp, fjp, 1560) if jp else []
    lh_en, lh_jp = 64, 44
    hgt = len(en_lines) * lh_en + len(jp_lines) * lh_jp + 56
    y1 = 1040
    y0 = y1 - hgt
    rr(d, (140, y0, W - 140, y1), 22, fill=mix(PANEL, a))
    if k == "en_insert":
        rr(d, (140, y0, 152, y1), 4, fill=mix(GOLD, a))
    y = y0 + 28 + lh_en / 2
    for ln in en_lines:
        rich_line(d, W / 2, y, ln, fen, b.get("hl"), TEXT, a)
        y += lh_en
    y += 4
    for ln in jp_lines:
        txt(d, (W / 2, y), ln, fjp, mix(SOFT, a), "mm")
        y += lh_jp
    if b.get("star"):
        f = F("jp_b", 26)
        label = "★ あとで復習"
        wv = tw(f, label) + 40
        p = ease((tb - 0.15) / 0.3)
        x1 = W - 160
        rr(d, (x1 - wv, y0 - 58 + (1 - p) * 10, x1, y0 - 12 + (1 - p) * 10), 20, fill=mix(GOLD, p))
        txt(d, (x1 - wv / 2, y0 - 35 + (1 - p) * 10), label, f, mix(INK, p, mix(GOLD, p)), "mm")
    if k == "en_insert":
        rr(d, (180, y0 - 50, 330, y0 - 14), 18, outline=mix(GOLD, a), width=2)
        txt(d, (255, y0 - 32), "ENGLISH AUDIO", F("in_b", 18), mix(GOLD, a), "mm")


def v_title(d, ep, vt):
    tc = ep["title_card"]
    a = ease(vt / 0.6)
    spaced(d, (W / 2, 330), "BUSINESS ENGLISH BRIEF   " + str(ep["episode"]), F("in_b", 30), mix(GOLD, a), 8, "m")
    p = ease((vt - 0.2) / 0.6)
    txt(d, (W / 2, 470 + (1 - p) * 20), tc["line1"], fit_font("jp_bl", 96, tc["line1"], 1700), mix(TEXT, p), "mm")
    p2 = ease((vt - 0.45) / 0.6)
    txt(d, (W / 2, 600 + (1 - p2) * 20), tc["line2"], fit_font("jp_b", 60, tc["line2"], 1700), mix(TEXT, p2), "mm")
    p3 = ease((vt - 0.8) / 0.8)
    wv = 760 * p3
    d.rectangle((W / 2 - wv / 2, 672, W / 2 + wv / 2, 678), fill=GOLD)
    txt(d, (W / 2, 740), ep["date"].replace("-", "."), F("in_m", 28), mix(MUTED, p3), "mm")


def v_review(d, ep, b, vt, ts):
    vis = b.get("vis") or {}
    ph = vis.get("phase", "intro")
    P, WD = ep["phrases"], ep.get("words", [])
    if ph == "intro":
        a = ease(vt / 0.5)
        spaced(d, (W / 2, 300), "REVIEW", F("in_bl", 140), mix(GOLD, a), 14, "m")
        txt(d, (W / 2, 430), "答え合わせ", F("jp_b", 54), mix(TEXT, a), "mm")
        for i in range(len(P)):
            p = ease((vt - 0.3 - i * 0.2) / 0.4)
            xx = 960 + (i - (len(P) - 1) / 2) * 120
            d.ellipse((xx - 14, 546, xx + 14, 574), outline=mix(GOLD, p), width=3)
        txt(d, (W / 2, 660), "まず英語だけを聞いて、意味を考えてみましょう", F("jp_m", 32), mix(MUTED, a), "mm")
        return
    if ph == "words_intro" or "word" in vis:
        cur = vis.get("word", -1)
        a = ease(vt / 0.4) if ph == "words_intro" else 1
        spaced(d, (W / 2, 210), "KEY WORDS", F("in_bl", 64), mix(GOLD, a), 10, "m")
        for i, w in enumerate(WD):
            y0 = 320 + i * 150
            active = i == cur
            done = i < cur or (active and ph == "w_jp")
            p = ease((vt - i * 0.15) / 0.4) if ph == "words_intro" else 1
            rr(d, (340, y0, 1580, y0 + 120), 22, fill=mix(PANEL, p), outline=mix(GOLD if active else LINE, p), width=3 if active else 2)
            shown = i <= cur
            txt(d, (400, y0 + 60), w["en"] if shown else "· · ·", fit_font("in_b", 54, w["en"], 800) if shown else F("in_b", 54),
                mix(TEXT if shown else MUTED, p), "lm")
            if done:
                q = ease(vt / 0.35) if (active and ph == "w_jp") else 1
                txt(d, (1520, y0 + 60), w["jp"], fit_font("jp_b", 46, w["jp"], 500), mix(GOLD, q), "rm")
            elif active:
                wave(d, 1250, y0 + 60, ts, mix(GOLD, 0.6), n=7, w=6, gap=6, hmax=36)
        return
    ci = vis.get("card", 0)
    p_ = P[ci]
    en, jp, ex, exj = p_["en"], p_["jp"], p_["ex"], p_["ex_jp"]
    k = ORDER.index(ph)
    for i in range(len(P)):
        xx = 960 + (i - (len(P) - 1) / 2) * 60
        col = GOLD if i == ci else (MUTED if i < ci else LINE)
        d.ellipse((xx - 9, 141, xx + 9, 159), fill=col)
    txt(d, (W / 2, 196), f"PHRASE {ci + 1} / {len(P)}", F("in_b", 24), MUTED, "mm")
    a = ease(vt / 0.35) if ph == "quiz" else 1
    rr(d, (200, 240, 1720, 820), 34, fill=mix(PANEL, a), outline=mix(LINE, a), width=2)
    f = fit_font("in_b", 84 if len(en) < 26 else 66, en, 1400)
    pulse = 0.85 + 0.15 * math.sin(vt * 8) if ph == "final" else 1.0
    rich_line(d, W / 2, 360, en, f, [en] if ph == "final" else [], TEXT, a * pulse)
    if ph in ("quiz", "count"):
        if ph == "quiz":
            wave(d, W / 2, 470, ts, mix(GOLD, a))
        txt(d, (W / 2, 560 if ph == "quiz" else 600), "意味は?", F("jp_b", 52), mix(MUTED, a), "mm")
        if ph == "count":
            ring(d, W / 2, 470, 60, clamp(vt / 2.0), GOLD)
            txt(d, (W / 2, 472), str(max(1, 2 - int(vt))), F("in_bl", 54), TEXT, "mm")
        return
    q = ease(vt / 0.35) if ph == "reveal" else 1
    txt(d, (W / 2, 470), jp, fit_font("jp_b", 60, jp, 1400), mix(GOLD, q), "mm")
    if k >= ORDER.index("example"):
        d.line((380, 545, 1540, 545), fill=LINE, width=2)
        q = ease(vt / 0.35) if ph == "example" else 1
        fe = F("in_sb", 44)
        y = 610
        for ln in balance_wrap(wrap_en, ex, fe, 1340):
            rich_line(d, W / 2, y, ln, fe, [], TEXT, q, hl_alpha=0.0)
            lo = ln.lower()
            for part in [en.lower()] + en.lower().split(", "):
                i = lo.find(part)
                if i >= 0:
                    x0 = W / 2 - tw(fe, ln) / 2
                    d.rectangle((x0 + tw(fe, ln[:i]), y + 28, x0 + tw(fe, ln[:i + len(part)]), y + 33), fill=mix(GOLD, q))
                    break
            y += 62
        if ph == "repeat":
            ring(d, 1600, 300, 40, clamp(vt / 3.0), GREEN, width=8)
            txt(d, (1600, 300), str(max(1, 3 - int(vt))), F("in_bl", 34), TEXT, "mm")
            rr(d, (W / 2 - 150, 745, W / 2 + 150, 795), 25, fill=GREEN)
            txt(d, (W / 2, 770), "声に出してリピート", F("jp_b", 26), INK, "mm")
        if k >= ORDER.index("example_jp"):
            q = ease(vt / 0.35) if ph == "example_jp" else 1
            txt(d, (W / 2, y + 30), exj, fit_font("jp_r", 32, exj, 1440), mix(SOFT, q), "mm")


def v_outro(d, ep, b, vt):
    v = b.get("vis", 0)
    P = ep["phrases"]
    if v == 0:
        a = ease(vt / 0.5)
        spaced(d, (W / 2, 190), "TODAY'S PHRASES", F("in_bl", 48), mix(GOLD, a), 8, "m")
        for i, p_ in enumerate(P):
            p = ease((vt - 0.2 - i * 0.2) / 0.45)
            y0 = 270 + i * 165
            rr(d, (260, y0, 1660, y0 + 140), 24, fill=mix(PANEL, p), outline=mix(LINE, p), width=2)
            txt(d, (320, y0 + 70), f"0{i + 1}", F("in_bl", 44), mix(GOLD, p), "lm")
            txt(d, (420, y0 + 52), p_["en"], fit_font("in_b", 46, p_["en"], 1180), mix(TEXT, p), "lm")
            txt(d, (420, y0 + 104), p_["jp"], F("jp_m", 30), mix(GOLD, p), "lm")
        txt(d, (1660, 790), "保存して、明日の会議前に見返そう", F("jp_m", 28), mix(MUTED, ease((vt - 1.0) / 0.5)), "rm")
    else:
        hw = ep.get("homework", {"en": "See you tomorrow!"})
        a = ease(vt / 0.5)
        spaced(d, (W / 2, 250), "HOMEWORK", F("in_bl", 44), mix(GOLD, a), 10, "m")
        lines = balance_wrap(wrap_en, hw["en"], F("in_b", 84), 1500)
        y = 445 - (len(lines) - 1) * 55
        for ln in lines:
            rich_line(d, W / 2, y, ln, F("in_b", 84), hw.get("hl", []), TEXT, a)
            y += 110
        txt(d, (W / 2, 620), "英語でコメント欄に書いてみてください", F("jp_m", 38), mix(MUTED, ease((vt - 0.5) / 0.5)), "mm")
        txt(d, (W / 2, 700), "See you tomorrow  —  Business English Brief", F("in_m", 30), mix(MUTED, ease((vt - 1.0) / 0.5)), "mm")


def find(tl, t):
    beats = tl["beats"]
    lo, hi = 0, len(beats) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if beats[mid]["start"] <= t:
            lo = mid
        else:
            hi = mid - 1
    return beats[lo]


def frame(ep, tl, t):
    img = background().copy()
    d = ImageDraw.Draw(img)
    b = find(tl, t)
    sc = tl["scenes"][b["scene"]]
    tb, vt, ts = t - b["start"], t - b["vis_t0"], t - sc["start"]
    vis = sc["visual"]
    if vis == "title":
        v_title(d, ep, vt)
    else:
        chrome(d, ep, tl, t, sc)
        if vis == "review":
            v_review(d, ep, b, vt, ts)
        elif vis == "outro":
            v_outro(d, ep, b, vt)
        else:
            v = b.get("vis")
            if isinstance(v, dict) and v.get("t") in TEMPLATES:
                TEMPLATES[v["t"]](d, v, SimpleNamespace(vt=vt, ts=ts, cont=b.get("cont", False), ep=ep))
        if b["kind"] not in NO_SUB and tb < b["dur"] + 0.01:
            subtitles(d, b, tb)
    if ts < 0.25:
        img = Image.blend(background(), img, ease(ts / 0.25))
    end = sc["end"] - t
    if 0 <= end < 0.5 and b["scene"] < len(tl["scenes"]) - 1:
        img = Image.blend(background(), img, clamp(end / 0.4))
    return img


# ---------------------------------------------------------------- video
def _render_range(ep, tl, f0, f1, path):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        p.stdin.write(frame(ep, tl, fi / FPS).tobytes())
    p.stdin.close()
    p.wait()
    if p.returncode:
        raise RuntimeError("ffmpeg failed")


def build_audio(tl, path):
    clips = [b for b in tl["beats"] if b.get("audio")]
    if not clips:
        return None
    inputs, filt = [], []
    for i, b in enumerate(clips):
        inputs += ["-i", b["audio"]]
        ms = int(b["start"] * 1000)
        filt.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,adelay={ms}|{ms}[a{i}]")
    filt.append("".join(f"[a{i}]" for i in range(len(clips))) +
                f"amix=inputs={len(clips)}:normalize=0,apad=whole_dur={tl['total']},loudnorm=I=-16:TP=-1.5[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
                    "-map", "[out]", "-ac", "2", "-c:a", "aac", "-b:a", "192k", path], check=True)
    return path


def render_video(ep, tl, out, workers=None, start=0, end=None):
    from multiprocessing import Process
    workers = workers or max(1, (os.cpu_count() or 2))
    end = end or tl["total"]
    out = os.path.abspath(out)
    tmp = os.path.join(os.path.dirname(out), "_tmp")
    os.makedirs(tmp, exist_ok=True)
    f0, f1 = int(start * FPS), int(end * FPS)
    step = math.ceil((f1 - f0) / workers)
    parts, procs = [], []
    for w_ in range(workers):
        a, b = f0 + w_ * step, min(f1, f0 + (w_ + 1) * step)
        if a >= b:
            continue
        pth = os.path.join(tmp, f"part{w_}.mp4")
        parts.append(pth)
        pr = Process(target=_render_range, args=(ep, tl, a, b, pth))
        pr.start()
        procs.append(pr)
    for pr in procs:
        pr.join()
        if pr.exitcode:
            raise RuntimeError("render worker failed")
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        f.write("".join(f"file '{p}'\n" for p in parts))
    vid = os.path.join(tmp, "video.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid], check=True)
    aud = build_audio(tl, os.path.join(tmp, "audio.m4a")) if (start == 0 and end == tl["total"]) else None
    if aud:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", aud, "-c:v", "copy", "-c:a", "copy",
                        "-shortest", "-movflags", "+faststart", out], check=True)
    else:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-c", "copy", "-movflags", "+faststart", out], check=True)
    return out
