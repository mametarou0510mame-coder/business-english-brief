"""Read-only performance snapshot: YouTube views/likes/comments per video, channel totals, Instagram reel insights.

Writes stats/latest.json and prints one line per item (shown as notices in the Stats workflow)."""
import json, os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    out = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "youtube": [], "instagram": []}
    state = json.load(open(os.path.join(ROOT, "state/published.json"), encoding="utf-8"))
    import youtube as Y
    tok = Y.token()
    H = {"Authorization": f"Bearer {tok}"}
    _, ch = Y._req("GET", f"{Y.API}/channels?part=statistics&mine=true", headers=H)
    st = ch["items"][0]["statistics"]
    out["channel"] = st
    print(f"CHANNEL subs={st.get('subscriberCount')} views={st.get('viewCount')} videos={st.get('videoCount')}")
    ids = []
    for ep, r in state.items():
        if r.get("long"):
            ids.append((ep, "long", r["long"]))
        for i, s in enumerate(r.get("shorts") or []):
            if s:
                ids.append((ep, f"short{i + 1}", s))
    for k in range(0, len(ids), 50):
        chunk = ids[k:k + 50]
        _, j = Y._req("GET", f"{Y.API}/videos?part=statistics,snippet,status,contentDetails&id=" + ",".join(x[2] for x in chunk), headers=H)
        by = {it["id"]: it for it in j.get("items", [])}
        for ep, kind, vid in chunk:
            it = by.get(vid, {})
            s = it.get("statistics", {})
            row = {"ep": ep, "kind": kind, "id": vid, "title": it.get("snippet", {}).get("title"),
                   "privacy": it.get("status", {}).get("privacyStatus"), "published": it.get("snippet", {}).get("publishedAt"),
                   "views": int(s.get("viewCount", 0)), "likes": int(s.get("likeCount", 0)), "comments": int(s.get("commentCount", 0))}
            try:
                epj = json.load(open(os.path.join(ROOT, "episodes", ep, "episode.json"), encoding="utf-8"))
                row["series"] = epj.get("series")
                if kind.startswith("short"):
                    row["style"] = epj["shorts"][int(kind[5:]) - 1].get("style", "news")
            except Exception:
                pass
            out["youtube"].append(row)
            print(f"YT {kind:6} {row['views']:>6} views {row['likes']:>3} likes {row['privacy']} | {row['title']}")
    # YouTube Analytics (needs the yt-analytics.readonly scope on the refresh token; skipped quietly without it)
    try:
        import urllib.parse as up
        end = dt.date.today().isoformat()
        q = {"ids": "channel==MINE", "startDate": "2026-10-20", "endDate": end, "dimensions": "video",
             "metrics": "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained",
             "sort": "-views", "maxResults": "200"}
        _, a_ = Y._req("GET", "https://youtubeanalytics.googleapis.com/v2/reports?" + up.urlencode(q), headers=H)
        cols = [c["name"] for c in a_.get("columnHeaders", [])]
        by = {r[0]: dict(zip(cols, r)) for r in a_.get("rows", [])}
        for row in out["youtube"]:
            if row["id"] in by:
                row["analytics"] = by[row["id"]]
        q2 = dict(q, dimensions="insightTrafficSourceType", metrics="views", sort="-views")
        q2.pop("maxResults")
        _, t_ = Y._req("GET", "https://youtubeanalytics.googleapis.com/v2/reports?" + up.urlencode(q2), headers=H)
        out["traffic"] = t_.get("rows", [])
        print("ANALYTICS traffic:", out["traffic"])
        for row in sorted(out["youtube"], key=lambda r: -r["views"])[:10]:
            an = row.get("analytics")
            if an:
                print(f"ANALYTICS {row['kind']:6} view%={an.get('averageViewPercentage')} avgSec={an.get('averageViewDuration')} subs+={an.get('subscribersGained')} | {row['title'][:40]}")
    except Exception as e:
        print("ANALYTICS unavailable:", str(e)[:160])
    import statistics as stt
    pub = [r for r in out["youtube"] if r["privacy"] == "public"]
    for label, f in (("long", lambda r: r["kind"] == "long"), ("short/news", lambda r: r.get("style") == "news"),
                     ("short/quiz", lambda r: r.get("style") == "quiz")):
        v = [r["views"] for r in pub if f(r)]
        if v:
            print(f"SUMMARY {label}: n={len(v)} median={stt.median(v)} mean={sum(v) / len(v):.0f} max={max(v)}")
    if os.environ.get("IG_TOKEN"):
        import instagram as I
        uid, itok = os.environ["IG_USER_ID"], os.environ["IG_TOKEN"]
        acc = I._http("GET", f"{I.API}/{uid}?fields=followers_count,media_count&access_token={itok}")
        out["ig_account"] = acc
        print(f"IG followers={acc.get('followers_count')} posts={acc.get('media_count')}")
        q = json.load(open(os.path.join(ROOT, "state/ig_queue.json"), encoding="utf-8"))
        for x in q:
            if x.get("status") != "posted":
                continue
            row = {"ep": x["ep"], "permalink": x.get("permalink")}
            for metrics in ("views,reach,saved,shares,total_interactions", "reach,saved,shares"):
                try:
                    j = I._http("GET", f"{I.API}/{x['media_id']}/insights?metric={metrics}&access_token={itok}")
                    row.update({m["name"]: m["values"][0]["value"] for m in j.get("data", [])})
                    break
                except Exception as e:
                    row["error"] = str(e)[:150]
            out["instagram"].append(row)
            print(f"IG {row.get('views', '?'):>6} views reach={row.get('reach', '?')} saved={row.get('saved', '?')} shares={row.get('shares', '?')} | {x['ep']}")
    os.makedirs(os.path.join(ROOT, "stats"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "stats/latest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
