"""Azure Speech narration: one trimmed WAV per beat in <episode>/audio/<id>.wav.

Env: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION (default japaneast).
Voices come from channel.json (voices.jp / voices.en). Existing files are reused.
"""
import os, sys, time, subprocess, urllib.request, urllib.error
from xml.sax.saxutils import escape

FREE_TIER_INTERVAL = 3.2  # F0: 20 requests / 60 s


def synth(ssml, key, region):
    url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    for attempt in range(8):
        req = urllib.request.Request(url, data=ssml.encode("utf-8"), method="POST", headers={
            "Ocp-Apim-Subscription-Key": key, "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3", "User-Agent": "beb-tts"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503):
                time.sleep(10 * (attempt + 1))
                continue
            raise RuntimeError(f"Azure TTS {e.code}: {e.read()[:200]!r}")
        except urllib.error.URLError:
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("Azure TTS: too many retries")


def ssml_for(line, voices):
    voice = voices["en"] if line["voice"] == "EN" else voices["jp"]
    lang = voice[:5]
    rate = "-8%" if line.get("slow") else ("0%" if line["voice"] == "EN" else "+4%")
    return (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{lang}">'
            f'<voice name="{voice}"><prosody rate="{rate}">{escape(line["text"])}</prosody></voice></speak>')


def trim(src, dst):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.06,areverse,"
                    "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse",
                    "-ar", "48000", "-ac", "1", dst], check=True)


def run(ep_dir, lines, voices):
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION") or "japaneast"
    adir = os.path.join(ep_dir, "audio")
    os.makedirs(adir, exist_ok=True)
    todo = [l for l in lines if not os.path.exists(os.path.join(adir, l["id"] + ".wav"))]
    if todo and not key:
        print(f"[tts] AZURE_SPEECH_KEY not set; {len(todo)} clips will use estimated timing", file=sys.stderr)
        return False
    for i, l in enumerate(todo):
        t0 = time.time()
        mp3 = os.path.join(adir, l["id"] + ".mp3")
        with open(mp3, "wb") as f:
            f.write(synth(ssml_for(l, voices), key, region))
        trim(mp3, os.path.join(adir, l["id"] + ".wav"))
        os.remove(mp3)
        print(f"[tts] {i + 1}/{len(todo)} {l['id']}", flush=True)
        wait = FREE_TIER_INTERVAL - (time.time() - t0)
        if wait > 0:
            time.sleep(wait)
    return True
