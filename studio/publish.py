"""Publish a studio episode now: YouTube long (public) + thumbnail, YouTube short (public), Instagram reel.

usage: python studio/publish.py studio/episodes/<slug>/episode.json <media_dir>
media_dir holds <slug>/episode.mp4 and <slug>/short.mp4 (from the studio-media branch).
State: studio/published.json (skips what is already done)."""
import json, os, sys, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "engine"))
import youtube as Y
import instagram as I

CH = json.load(open(os.path.join(ROOT, "channel.json"), encoding="utf-8"))
STATE = os.path.join(HERE, "published.json")
DISCLAIMER = "※数字はすべて出典を確認したものです。英語ナレーションはAI音声です。特定の銘柄の売買を勧めるものではありません。"


def chapters(tl):
    out, seen = [], set()
    for s in tl["scenes"]:
        name = (s.get("chapter") or "").strip()
        if not name or name in seen:
            continue
        seen.add(name)
        t = int(s["start"])
        out.append(f"{t // 60}:{t % 60:02d} {name.title()}")
    if out and not out[0].startswith("0:00"):
        out[0] = "0:00 " + out[0].split(" ", 1)[1]
    return out


def main():
    ep_path, media = sys.argv[1], sys.argv[2]
    slug = os.path.basename(os.path.dirname(ep_path))
    ep = json.load(open(ep_path, encoding="utf-8"))
    pub = ep["publish"]
    tlp = os.path.join(media, slug, "episode_timeline.json")
    tl = json.load(open(tlp, encoding="utf-8")) if os.path.exists(tlp) else None
    st = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    rec = st.setdefault(slug, {})
    tok = Y.token()
    Y.guard(tok, CH["youtube_channel_id"])
    if not rec.get("long"):
        L = [pub["summary"], "", "■ 今日の英語"] + [f"・{a}:{b}" for a, b in pub["phrases"]]
        if tl:
            L += ["", "■ チャプター"] + chapters(tl)
        L += ["", "■ 出典"] + [f"・{a} {u}" for a, u in pub["sources"]] + ["", DISCLAIMER, "", "#ビジネス英語 #英語リスニング #世界経済"]
        vid = Y.upload(tok, os.path.join(media, slug, "episode.mp4"),
                       {"title": pub["title"], "description": "\n".join(L), "tags": pub["tags"], "audio_lang": "en", "lang": "ja"})
        rec["long"] = vid
        json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"::notice title=publish::long https://youtu.be/{vid}")
        try:
            Y.set_thumbnail(tok, vid, os.path.join(ROOT, pub["thumb"]))
        except Exception as e:
            print("::warning::thumbnail failed:", str(e)[:200])
    sh = pub.get("short")
    if sh and not rec.get("short"):
        desc = f"{pub['summary']}\n\n▶ 本編: https://youtu.be/{rec['long']}\n\n#ビジネス英語 #英語リスニング #shorts"
        sid = Y.upload(tok, os.path.join(media, slug, sh["file"]), {"title": sh["title"], "description": desc, "tags": pub["tags"], "audio_lang": "en"})
        rec["short"] = sid
        json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"::notice title=publish::short https://youtu.be/{sid}")
    if sh and not rec.get("ig") and os.environ.get("IG_TOKEN"):
        base = f"{CH['pages_base']}/studio/{slug}"
        url, cover = f"{base}/short.mp4", f"{base}/short.jpg"
        import urllib.request
        for _ in range(30):
            try:
                urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=20)
                break
            except Exception:
                time.sleep(20)
        mid, link = I.publish_reel(url, cover, sh["ig_caption"])
        rec["ig"] = link or mid
        json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"::notice title=publish::instagram {rec['ig']}")


if __name__ == "__main__":
    main()
