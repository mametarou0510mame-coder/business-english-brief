"""Daily publishing for studio episodes (owner rule 2026-11-24: per day 1 long, 1 YouTube short, 1 reel, 1 carousel).

usage: python studio/publish.py --what long|short|reel|carousel [--slug <slug>] --media <dir with studio-media checkout>
Queue: studio/queue.json (slugs in publish order). State: studio/published.json.
- long:     first queued slug whose media is ready and whose long is not out yet
- short / reel / carousel: first slug whose long is out and that item is not out yet
Instagram media is served from GitHub Pages (`media` branch, path studio/<slug>/...): the workflow copies it there first."""
import argparse, json, os, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "engine"))
import youtube as Y
import instagram as I

CH = json.load(open(os.path.join(ROOT, "channel.json"), encoding="utf-8"))
STATE, QUEUE = os.path.join(HERE, "published.json"), os.path.join(HERE, "queue.json")
DISCLAIMER = "※数字はすべて出典を確認したものです。英語ナレーションはAI音声です。特定の銘柄の売買を勧めるものではありません。"


def load(p, d):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d


def save(st):
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def chapters(tl):
    out, seen = [], set()
    for s in tl["scenes"]:
        name = (s.get("chapter") or "").strip()
        if name and name not in seen:
            seen.add(name)
            t = int(s["start"])
            out.append(f"{t // 60}:{t % 60:02d} {name.title()}")
    if out:
        out[0] = "0:00 " + out[0].split(" ", 1)[1]
    return out


def ready(media, slug):
    need = ["episode.mp4", "short.mp4", "carousel/c1.jpg"]
    return all(os.path.exists(os.path.join(media, slug, n)) for n in need)


def wait_url(url, tries=30):
    for _ in range(tries):
        try:
            urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=20)
            return True
        except Exception:
            time.sleep(20)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--what", required=True, choices=["long", "short", "reel", "carousel", "pick"])
    ap.add_argument("--slug")
    ap.add_argument("--media", required=True)
    a = ap.parse_args()
    st, q = load(STATE, {}), load(QUEUE, [])
    key = {"long": "long", "short": "short", "reel": "ig_reel", "carousel": "ig_carousel"}
    if a.slug:
        slug = a.slug
    else:
        cands = [s for s in q if not st.get(s, {}).get(key.get(a.what, "long"))]
        if a.what in ("long", "pick"):
            cands = [s for s in cands if ready(a.media, s)]
        else:
            cands = [s for s in cands if st.get(s, {}).get("long")]
        if not cands:
            print(f"::notice title=publish::nothing to publish for {a.what}")
            return
        slug = cands[0]
    if a.what == "pick":
        print(slug)
        return
    ep = json.load(open(os.path.join(HERE, "episodes", slug, "episode.json"), encoding="utf-8"))
    pub, rec = ep["publish"], st.setdefault(slug, {})
    base = f"{CH['pages_base']}/studio/{slug}"
    if a.what in ("long", "short"):
        tok = Y.token()
        Y.guard(tok, CH["youtube_channel_id"])
    if a.what == "long":
        tlp = os.path.join(a.media, slug, "episode_timeline.json")
        L = [pub["summary"], "", "■ 今日の英語"] + [f"・{e}:{j}" for e, j in pub["phrases"]]
        if os.path.exists(tlp):
            L += ["", "■ チャプター"] + chapters(json.load(open(tlp, encoding="utf-8")))
        L += ["", "■ 出典"] + [f"・{t} {u}" for t, u in pub["sources"]] + ["", DISCLAIMER, "", "#ビジネス英語 #英語リスニング #世界経済"]
        vid = Y.upload(tok, os.path.join(a.media, slug, "episode.mp4"),
                       {"title": pub["title"], "description": "\n".join(L), "tags": pub["tags"], "audio_lang": "en"})
        rec["long"] = vid
        save(st)
        print(f"::notice title=publish::long {slug} https://youtu.be/{vid}")
        try:
            Y.set_thumbnail(tok, vid, os.path.join(ROOT, pub["thumb"]))
        except Exception as e:
            print("::warning::thumbnail failed:", str(e)[:200])
    elif a.what == "short":
        sh = pub["short"]
        desc = f"{pub['summary']}\n\n▶ 本編: https://youtu.be/{rec['long']}\n\n#ビジネス英語 #英語リスニング #shorts"
        sid = Y.upload(tok, os.path.join(a.media, slug, "short.mp4"), {"title": sh["title"], "description": desc, "tags": pub["tags"], "audio_lang": "en"})
        rec["short"] = sid
        save(st)
        print(f"::notice title=publish::short {slug} https://youtu.be/{sid}")
    elif a.what == "reel":
        url = f"{base}/short.mp4"
        if not wait_url(url):
            raise SystemExit(f"media not reachable: {url}")
        mid, link = I.publish_reel(url, f"{base}/short.jpg", pub["short"]["ig_caption"])
        rec["ig_reel"] = link or mid
        save(st)
        print(f"::notice title=publish::reel {slug} {rec['ig_reel']}")
    elif a.what == "carousel":
        n = len([f for f in os.listdir(os.path.join(a.media, slug, "carousel")) if f.endswith(".jpg")])
        urls = [f"{base}/carousel/c{i}.jpg" for i in range(1, n + 1)]
        if not wait_url(urls[-1]):
            raise SystemExit(f"media not reachable: {urls[-1]}")
        mid, link = I.publish_carousel(urls, pub["carousel_caption"])
        rec["ig_carousel"] = link or mid
        save(st)
        print(f"::notice title=publish::carousel {slug} {rec['ig_carousel']}")


if __name__ == "__main__":
    main()
