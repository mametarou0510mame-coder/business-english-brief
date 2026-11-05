"""Read-only competitor scan via YouTube Data API: finds Japanese channels for given keywords and summarises
their recent uploads (views, duration, shorts share, top titles). Writes stats/competitors.json and prints a report."""
import json, os, re, sys, statistics as st
sys.path.insert(0, os.path.dirname(__file__))
import youtube as Y

QUERIES = ["ビジネス英語", "ニュース 英語 解説", "英語 ニュース 聞き流し", "会議 英語 フレーズ", "英会話 フレーズ ショート",
           "経済ニュース 解説", "海外ニュース 解説 日本語", "TOEIC 英単語"]


def dur(s):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (3600, 60, 1))) if m else 0


def main():
    tok = Y.token()
    H = {"Authorization": f"Bearer {tok}"}
    get = lambda u: Y._req("GET", u, headers=H)[1]
    chans = {}
    for q in QUERIES:
        from urllib.parse import quote
        j = get(f"{Y.API}/search?part=snippet&type=channel&maxResults=10&regionCode=JP&relevanceLanguage=ja&q={quote(q)}")
        for it in j.get("items", []):
            chans.setdefault(it["snippet"]["channelId"], set()).add(q)
    ids = list(chans)
    info = {}
    for k in range(0, len(ids), 50):
        j = get(f"{Y.API}/channels?part=snippet,statistics,contentDetails&id=" + ",".join(ids[k:k + 50]))
        for it in j.get("items", []):
            info[it["id"]] = it
    rows = []
    for cid, it in info.items():
        subs = int(it["statistics"].get("subscriberCount", 0) or 0)
        if subs < 5000:
            continue
        up = it["contentDetails"]["relatedPlaylists"]["uploads"]
        pl = get(f"{Y.API}/playlistItems?part=contentDetails&maxResults=20&playlistId={up}")
        vids = [x["contentDetails"]["videoId"] for x in pl.get("items", [])]
        if not vids:
            continue
        vj = get(f"{Y.API}/videos?part=snippet,statistics,contentDetails&id=" + ",".join(vids))
        vs = [{"title": v["snippet"]["title"], "views": int(v["statistics"].get("viewCount", 0)), "sec": dur(v["contentDetails"]["duration"]),
               "date": v["snippet"]["publishedAt"][:10]} for v in vj.get("items", [])]
        shorts = [v for v in vs if v["sec"] <= 180]
        longs = [v for v in vs if v["sec"] > 180]
        rows.append({"id": cid, "name": it["snippet"]["title"], "subs": subs, "videos": int(it["statistics"].get("videoCount", 0)),
                     "queries": sorted(chans[cid]), "n": len(vs),
                     "med_long": int(st.median([v["views"] for v in longs])) if longs else None,
                     "med_short": int(st.median([v["views"] for v in shorts])) if shorts else None,
                     "short_share": round(len(shorts) / len(vs), 2), "med_long_min": round(st.median([v["sec"] for v in longs]) / 60, 1) if longs else None,
                     "first": vs[-1]["date"], "last": vs[0]["date"],
                     "top": sorted(vs, key=lambda v: -v["views"])[:3]})
    rows.sort(key=lambda r: -r["subs"])
    os.makedirs("stats", exist_ok=True)
    json.dump(rows, open("stats/competitors.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in rows[:40]:
        print(f"{r['name'][:24]} | subs {r['subs']} | 20本中short {int(r['short_share']*100)}% | 長尺中央値 {r['med_long']}回/{r['med_long_min']}分 | short中央値 {r['med_short']}回 | {r['first']}〜{r['last']}")
        for v in r["top"]:
            print(f"   ▲{v['views']} {v['sec']}s {v['title'][:60]}")


if __name__ == "__main__":
    main()
