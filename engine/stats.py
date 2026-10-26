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
            out["youtube"].append(row)
            print(f"YT {kind:6} {row['views']:>6} views {row['likes']:>3} likes {row['privacy']} | {row['title']}")
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
