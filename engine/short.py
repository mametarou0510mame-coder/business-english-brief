"""Vertical 1080x1920 shorts cut from the review section of the long video."""
import os, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw
from core import *  # noqa
import render as R

SW, SH = 1080, 1920
END = 2.2


@lru_cache(maxsize=1)
def vbg():
    return make_bg(SW, SH, (0.2, 0.15), 60)


@lru_cache(maxsize=1)
def edge():
    m = Image.new("L", (1080, 492), 255)
    dm = ImageDraw.Draw(m)
    for i in range(60):
        dm.rectangle((i, i, 1079 - i, 491 - i), outline=int(255 * i / 60))
    return m


def build(ep, tl, idx, long_mp4, out):
    spec = ep["shorts"][idx]
    card = spec["phrase"]
    ids = [b for b in tl["beats"] if isinstance(b.get("vis"), dict) and b["vis"].get("card") == card and tl["scenes"][b["scene"]]["visual"] == "review"]
    t0 = ids[0]["start"]
    body = ids[-1]["start"] + ids[-1]["dur"] + 0.3 - t0
    total = body + END
    P = ep["phrases"][card]

    def frame(ts):
        img = vbg().copy()
        d = ImageDraw.Draw(img)
        rr(d, (60, 120, 112, 172), 12, fill=GOLD)
        txt(d, (86, 147), "B", F("in_bl", 34), INK, "mm")
        txt(d, (128, 146), "Business English Brief", F("in_sb", 32), TEXT, "lm")
        txt(d, (SW / 2, 285), spec.get("kicker", "この英語、意味わかる?"), F("jp_b", 44), GOLD, "mm")
        y = 395
        for ln in spec["hook"][:2]:
            txt(d, (SW / 2, y), ln, fit_font("jp_bl", 86, ln, 980), TEXT, "mm")
            y += 112
        if ts < body:
            src = R.frame(ep, tl, t0 + ts)
            img.paste(src.crop((170, 120, 1750, 840)).resize((1080, 492), Image.LANCZOS), (0, 650), edge())
            d = ImageDraw.Draw(img)
        else:
            p = ease((ts - body) / 0.4)
            rr(d, (70, 690, SW - 70, 1110), 30, fill=mix(PANEL, p), outline=mix(LINE, p), width=2)
            f = fit_font("in_b", 62, P["en"], 880)
            rich_line(d, SW / 2, 820, P["en"], f, [P["en"]], TEXT, p)
            txt(d, (SW / 2, 930), P["jp"], fit_font("jp_b", 50, P["jp"], 900), mix(GOLD, p), "mm")
            txt(d, (SW / 2, 1030), "保存して、次の会議前に見返そう", F("jp_m", 34), mix(MUTED, p), "mm")
        txt(d, (SW / 2, 1220), spec.get("ctx", ""), fit_font("jp_m", 34, spec.get("ctx", ""), 980), MUTED, "mm")
        rr(d, (SW / 2 - 300, 1290, SW / 2 + 300, 1370), 40, outline=GOLD, width=3)
        txt(d, (SW / 2, 1330), "ニュースの解説は本編で", F("jp_b", 36), GOLD, "mm")
        d.rectangle((0, SH - 8, int(SW * ts / total), SH), fill=GOLD)
        return img

    tmpv = out + ".v.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SW}x{SH}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmpv]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(total * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmpv, "-ss", f"{t0:.3f}", "-t", f"{total:.3f}", "-i", long_mp4,
                    "-map", "0:v", "-map", "1:a", "-af", f"afade=t=in:d=0.05,afade=t=out:st={body - 0.2:.2f}:d=0.4,apad",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", out], check=True)
    os.remove(tmpv)
    cover = out.replace(".mp4", ".jpg")
    frame(min(body * 0.5, body - 1)).convert("RGB").save(cover, quality=90)
    return out, cover
