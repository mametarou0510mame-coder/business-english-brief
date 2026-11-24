"""BEB studio renderer: HTML/SVG scenes (studio/) -> frames via headless Chromium -> H.264, with English narration.

usage: python studio/render.py studio/episodes/<slug>/<name>.json [--out out.mp4] [--workers 4] [--stills 0.5,3,...]
Narration: Azure (AZURE_SPEECH_KEY / AZURE_SPEECH_REGION) one clip per beat; without a key, durations are estimated
and the video is silent (preview mode).
"""
import argparse, json, os, sys, subprocess, math, wave, shutil, concurrent.futures as cf
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FPS = 30
GAP, HEAD, TAIL = 0.65, 0.6, 1.0


_KP = None


def kokoro_wav(text, voice, speed, path):
    """Kokoro-82M (Apache-2.0, runs on CPU): natural English narration with no quota."""
    global _KP
    import numpy as np, soundfile as sf
    from kokoro import KPipeline
    if _KP is None:
        _KP = KPipeline(lang_code="a" if voice.startswith("a") else "b")
    chunks = [a for _, _, a in _KP(text, voice=voice, speed=speed)]
    tmp = path + ".raw.wav"
    sf.write(tmp, np.concatenate([np.asarray(c) for c in chunks]), 24000)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af",
                    "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse",
                    "-ar", "48000", "-ac", "1", path], check=True)
    os.remove(tmp)


def tts(ep, adir):
    engine = ep.get("tts", "azure")
    key = os.environ.get("AZURE_SPEECH_KEY") if engine == "azure" else None
    use_kokoro = engine == "kokoro" and os.environ.get("STUDIO_TTS") != "off"
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    durs = []
    for si, sc in enumerate(ep["scenes"]):
        for bi, b in enumerate(sc["beats"]):
            if b.get("hold"):
                durs.append(float(b["hold"]))
                continue
            wav = os.path.join(adir, f"{si:02d}_{bi:02d}.wav")
            if use_kokoro and not os.path.exists(wav):
                try:
                    kokoro_wav(b["en"], ep.get("voice", "af_heart"), float(ep.get("speed", 0.92)), wav)
                except ImportError:
                    use_kokoro = False
            if key and not os.path.exists(wav):
                import tts as T
                ssml = (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
                        f'<voice name="{ep.get("voice", "en-US-AvaNeural")}"><prosody rate="{ep.get("rate", "-6%")}">{escape(b["en"])}</prosody></voice></speak>')
                mp3 = T.synth(ssml, key, os.environ.get("AZURE_SPEECH_REGION", "japaneast"))
                tmp = wav + ".mp3"
                open(tmp, "wb").write(mp3)
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af",
                                "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse",
                                "-ar", "48000", "-ac", "1", wav], check=True)
                os.remove(tmp)
                import time; time.sleep(3.2)
            if os.path.exists(wav):
                with wave.open(wav) as w:
                    durs.append(w.getnframes() / w.getframerate())
            else:
                durs.append(len(b["en"].split()) / 2.45 + 0.3)
    return durs


def timeline(ep, durs):
    t, k, scenes = 0.0, 0, []
    for si, sc in enumerate(ep["scenes"]):
        start = t
        t += HEAD
        beats = []
        for bi, b in enumerate(sc["beats"]):
            d = durs[k]; k += 1
            beats.append(dict(b, start=round(t, 3), end=round(t + d, 3), audio=f"{si:02d}_{bi:02d}.wav"))
            t += d + GAP
        t += TAIL - GAP
        scenes.append(dict(sc, start=round(start, 3), end=round(t, 3), beats=beats))
    return {"scenes": scenes, "total": round(t, 3), "portrait": ep.get("portrait")}


def render_part(args):
    tl, a, b, out, stills = args
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text"])
        vw, vh = (1080, 1920) if tl.get("portrait") else (1920, 1080)
        pg = br.new_page(viewport={"width": vw, "height": vh}, device_scale_factor=1)
        pg.goto("file://" + os.path.join(HERE, "index.html"))
        pg.evaluate("document.fonts.ready")
        pg.evaluate("tl => loadTimeline(tl)", tl)
        stage = pg.locator("#stage")
        if stills:
            for t in stills:
                pg.evaluate("t => seek(t)", t)
                stage.screenshot(path=f"{out}_{t:06.2f}.jpg", type="jpeg", quality=92)
            br.close()
            return out
        tmp = out.replace(".mp4", ".part.mp4")
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp],
                              stdin=subprocess.PIPE)
        for f in range(a, b):
            pg.evaluate("t => seek(t)", f / FPS)
            ff.stdin.write(stage.screenshot(type="jpeg", quality=92))
        ff.stdin.close()
        ff.wait()
        br.close()
        if ff.returncode == 0:
            os.replace(tmp, out)
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=max(1, min(8, os.cpu_count() or 2)))
    ap.add_argument("--stills")
    a = ap.parse_args()
    ep = json.load(open(a.episode, encoding="utf-8"))
    base = os.path.splitext(a.episode)[0]
    adir = base + "_audio"
    os.makedirs(adir, exist_ok=True)
    tl = timeline(ep, tts(ep, adir))
    json.dump(tl, open(base + "_timeline.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"total {tl['total']:.1f}s")
    if a.stills:
        ts = [float(x) for x in a.stills.split(",")]
        render_part((tl, 0, 0, base + "_still", ts))
        return
    out = a.out or base + ".mp4"
    n = int(math.ceil(tl["total"] * FPS))
    W = a.workers
    step = int(math.ceil(n / W))
    parts = [(tl, i, min(n, i + step), f"{base}_p{k:02d}.mp4", None) for k, i in enumerate(range(0, n, step))]
    with cf.ProcessPoolExecutor(W) as ex:
        files = list(ex.map(render_part, parts))
    lst = base + "_parts.txt"
    open(lst, "w").write("".join(f"file '{os.path.abspath(f)}'\n" for f in files))
    silent = base + "_silent.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    clips = [(b["start"], os.path.join(adir, b["audio"])) for sc in tl["scenes"] for b in sc["beats"] if os.path.exists(os.path.join(adir, b["audio"]))]
    if clips:
        inp, flt = [], []
        for i, (st, f) in enumerate(clips):
            inp += ["-i", f]
            ms = int(st * 1000)
            flt.append(f"[{i + 1}:a]adelay={ms}|{ms}[a{i}]")
        flt.append("".join(f"[a{i}]" for i in range(len(clips))) + f"amix=inputs={len(clips)}:normalize=0,loudnorm=I=-16:TP=-1.5,apad[aout]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, *inp, "-filter_complex", ";".join(flt), "-map", "0:v", "-map", "[aout]",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out + ".tmp.mp4"], check=True)
        os.replace(out + ".tmp.mp4", out)
    else:
        os.replace(silent, out)
    for f in files:
        os.remove(f)
    print(out)


if __name__ == "__main__":
    main()
