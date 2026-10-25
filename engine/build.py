#!/usr/bin/env python3
"""Business English Brief pipeline.

  python engine/build.py validate episodes/<id>      schema check + preview sheet (no audio needed)
  python engine/build.py render   episodes/<id>      narration (Azure) + long video + shorts + thumbnail
  python engine/build.py publish  episodes/<id> [--dry]   upload to YouTube (scheduled) + queue Instagram
  python engine/build.py pending                     list episode dirs not yet published
  python engine/build.py ig-due [--dry]              post Instagram reels whose time has come
  python engine/build.py check                       show which YouTube channel / IG account the secrets belong to
"""
import json, os, sys, math, shutil, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import episode as E  # noqa

CH = json.load(open(os.path.join(ROOT, "channel.json"), encoding="utf-8"))
STATE = os.path.join(ROOT, "state", "published.json")
QUEUE = os.path.join(ROOT, "state", "ig_queue.json")
MEDIA = os.path.join(ROOT, "_media")
TEMPLATES_OK = {"hero", "hero_side", "teaser", "people", "counter", "bars", "vs", "quote", "cards", "points",
                "flow", "layers", "org", "statement", "timeline"}


def jload(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def jsave(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def now():
    return dt.datetime.now(dt.timezone.utc)


def parse(ts):
    return dt.datetime.fromisoformat(ts)


# ---------------------------------------------------------------- validate
def validate(ep_dir, sheet=True):
    ep = E.load(ep_dir)
    errs = []
    for k in ("id", "episode", "date", "title_card", "phrases", "scenes", "youtube", "thumbnail", "shorts", "sources", "publish"):
        if k not in ep:
            errs.append(f"missing key: {k}")
    for i, p in enumerate(ep.get("phrases", [])):
        for k in ("en", "jp", "ex", "ex_jp"):
            if not p.get(k):
                errs.append(f"phrases[{i}].{k} missing")
        if p.get("en") and p["en"].lower().split(",")[0] not in p.get("ex", "").lower():
            errs.append(f"phrases[{i}].ex should contain the phrase '{p['en']}'")
    ids = set()
    for sc in ep.get("scenes", []):
        for b in sc.get("beats", []):
            if b["id"] in ids:
                errs.append(f"duplicate beat id {b['id']}")
            ids.add(b["id"])
            if b["id"][0] in "vwot" and b["id"][1:].isdigit():
                errs.append(f"beat id {b['id']} is reserved (v.., w.., o.., t..); use another prefix")
            if b["kind"] not in ("jp", "en_insert", "silent", "pause"):
                errs.append(f"{b['id']}: kind must be jp / en_insert / silent / pause")
            v = b.get("vis")
            if v is not None and (not isinstance(v, dict) or v.get("t") not in TEMPLATES_OK):
                errs.append(f"{b['id']}: vis.t must be one of {sorted(TEMPLATES_OK)}")
            if b["kind"] in ("jp", "en_insert") and not (b.get("jp") and b.get("en")):
                errs.append(f"{b['id']}: jp and en are both required")
    if len(ep.get("shorts", [])) < 2:
        errs.append("need 2 shorts")
    for s in ep.get("shorts", []):
        for k in ("phrase", "hook", "ctx", "title", "ig_caption"):
            if k not in s:
                errs.append(f"shorts.{k} missing")
    if len(ep.get("youtube", {}).get("title", "")) > 100:
        errs.append("youtube.title > 100 chars")
    pub = ep.get("publish", {})
    try:
        parse(pub["long"]); [parse(x) for x in pub["shorts"]]
    except Exception as e:
        errs.append(f"publish times invalid: {e}")
    if errs:
        print("INVALID " + ep_dir + "\n  - " + "\n  - ".join(errs))
        return False
    tl = E.timeline(ep)
    print(f"OK {ep_dir}: ~{tl['total']:.0f}s, {len(tl['beats'])} beats, {sum(len(l['text']) for l in E.tts_lines(ep))} TTS chars")
    if sheet:
        from PIL import Image
        import render as R
        picks = [b for b in tl["beats"] if b["kind"] in ("jp", "en_insert") and tl["scenes"][b["scene"]]["visual"] not in ("review", "outro")]
        step = max(1, len(picks) // 12)
        picks = picks[::step][:12]
        thumbs = [R.frame(ep, tl, b["start"] + min(b["dur"] * 0.8, 2.5)).resize((640, 360)) for b in picks]
        cols = 3
        rows = math.ceil(len(thumbs) / cols)
        s = Image.new("RGB", (cols * 648, rows * 368), (255, 255, 255))
        for i, t in enumerate(thumbs):
            s.paste(t, ((i % cols) * 648, (i // cols) * 368))
        os.makedirs(os.path.join(ep_dir, "out"), exist_ok=True)
        s.save(os.path.join(ep_dir, "out", "preview_sheet.png"))
        import thumb
        thumb.build(ep, os.path.join(ep_dir, "out", "thumbnail.png"))
        print("  preview:", os.path.join(ep_dir, "out", "preview_sheet.png"))
    return True


# ---------------------------------------------------------------- render
def render_ep(ep_dir):
    import tts, render as R, short, thumb
    ep = E.load(ep_dir)
    voiced = tts.run(ep_dir, E.tts_lines(ep), CH["voices"])
    tl = E.timeline(ep)
    out = os.path.join(ep_dir, "out")
    os.makedirs(out, exist_ok=True)
    long_mp4 = os.path.join(out, "long.mp4")
    R.render_video(ep, tl, long_mp4)
    for i in range(len(ep["shorts"])):
        short.build(ep, tl, i, long_mp4, os.path.join(out, f"short{i + 1}.mp4"))
    thumb.build(ep, os.path.join(out, "thumbnail.png"))
    with open(os.path.join(out, "description.txt"), "w", encoding="utf-8") as f:
        f.write(E.long_description(ep, tl))
    for lang in ("ja", "en"):
        with open(os.path.join(out, f"subtitles_{lang}.srt"), "w", encoding="utf-8") as f:
            f.write(E.srt(tl, lang))
    jsave(os.path.join(out, "timeline.json"), {"total": tl["total"], "chapters": E.chapters(tl), "voiced": voiced})
    print(f"rendered {ep_dir}: {tl['total']:.0f}s voiced={voiced}")
    return voiced


# ---------------------------------------------------------------- publish
def _when(ts):
    t = parse(ts)
    return None if t <= now() + dt.timedelta(minutes=20) else t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def publish_ep(ep_dir, dry=False):
    import youtube as Y
    ep = E.load(ep_dir)
    state = jload(STATE, {})
    rec = state.get(ep["id"], {})
    out = os.path.join(ep_dir, "out")
    meta = jload(os.path.join(out, "timeline.json"), {})
    if not meta.get("voiced"):
        raise SystemExit("STOP: narration missing (AZURE_SPEECH_KEY not set?). Not publishing a silent video.")
    tags = ep["youtube"].get("tags", [])
    if dry:
        print("[dry] would upload long + shorts for", ep["id"], "publishAt", ep["publish"])
        return
    tok = Y.token()
    title = Y.guard(tok, CH["youtube_channel_id"])
    print("YouTube channel OK:", title)
    if not rec.get("long"):
        desc = open(os.path.join(out, "description.txt"), encoding="utf-8").read()
        vid = Y.upload(tok, os.path.join(out, "long.mp4"),
                       {"title": ep["youtube"]["title"], "description": desc, "tags": tags, "publish_at": _when(ep["publish"]["long"])})
        Y.set_thumbnail(tok, vid, os.path.join(out, "thumbnail.png"))
        rec["long"] = vid
        state[ep["id"]] = rec
        jsave(STATE, state)
        print("long uploaded:", vid)
    long_url = f"https://youtu.be/{rec['long']}"
    rec.setdefault("shorts", [])
    for i, s in enumerate(ep["shorts"]):
        if i < len(rec["shorts"]) and rec["shorts"][i]:
            continue
        P = ep["phrases"][s["phrase"]]
        desc = (s.get("description") or f"{P['en']}（{P['jp']}）\n例文：{P['ex']}") + \
            f"\n\n▼ ニュースの解説は本編で\n{long_url}\n\n出典：" + " / ".join(x["title"] for x in ep["sources"][:2]) + \
            "\n※ナレーションはAI音声（Microsoft Azure AI Speech）を使用しています。\n\n#ビジネス英語 #英語学習 #ニュース英語"
        when = ep["publish"]["shorts"][i]
        sid = Y.upload(tok, os.path.join(out, f"short{i + 1}.mp4"),
                       {"title": s["title"], "description": desc, "tags": tags[:10], "publish_at": _when(when)})
        rec["shorts"] = rec["shorts"][:i] + [sid]
        state[ep["id"]] = rec
        jsave(STATE, state)
        print(f"short{i + 1} uploaded:", sid)
    # Instagram queue + media for GitHub Pages
    q = jload(QUEUE, [])
    have = {(x["ep"], x["n"]) for x in q}
    for i, s in enumerate(ep["shorts"]):
        if (ep["id"], i) in have:
            continue
        dst = os.path.join(MEDIA, ep["id"])
        os.makedirs(dst, exist_ok=True)
        shutil.copy(os.path.join(out, f"short{i + 1}.mp4"), os.path.join(dst, f"s{i + 1}.mp4"))
        shutil.copy(os.path.join(out, f"short{i + 1}.jpg"), os.path.join(dst, f"s{i + 1}.jpg"))
        q.append({"ep": ep["id"], "n": i, "at": ep["publish"]["shorts"][i],
                  "video": f"{CH['pages_base']}/{ep['id']}/s{i + 1}.mp4", "cover": f"{CH['pages_base']}/{ep['id']}/s{i + 1}.jpg",
                  "caption": s["ig_caption"], "status": "pending"})
    jsave(QUEUE, q)
    rec["status"] = "scheduled"
    state[ep["id"]] = rec
    jsave(STATE, state)


def pending():
    state = jload(STATE, {})
    d = os.path.join(ROOT, "episodes")
    for name in sorted(os.listdir(d)):
        p = os.path.join(d, name)
        if not os.path.isdir(p) or not os.path.exists(os.path.join(p, "episode.json")):
            continue
        ep = E.load(p)
        r = state.get(ep["id"], {})
        if ep.get("status") == "published_manually" or r.get("status") == "scheduled":
            continue
        print(os.path.relpath(p, ROOT))


def ig_due(dry=False):
    import instagram as I
    q = jload(QUEUE, [])
    due = [x for x in q if x["status"] == "pending" and parse(x["at"]) <= now() + dt.timedelta(minutes=10)]
    if not due:
        print("nothing due")
        return
    if not dry:
        print("Instagram account OK: @" + I.guard(CH["instagram_username"]))
    for x in due:
        late = now() - parse(x["at"])
        if late > dt.timedelta(hours=6):
            x["status"] = "skipped_late"
            continue
        if dry:
            print("[dry] would post", x["video"])
            continue
        try:
            mid, link = I.publish_reel(x["video"], x["cover"], x["caption"])
            x.update(status="posted", media_id=mid, permalink=link, posted_at=now().isoformat())
            print("posted", link)
        except Exception as e:
            x.update(status="error", error=str(e)[:300])
            print("ERROR", e)
        jsave(QUEUE, q)
    jsave(QUEUE, q)


def media_sync(dst):
    """Copy new shorts into the checked-out `media` branch and drop ones already posted."""
    q = jload(QUEUE, [])
    keep = {x["ep"] for x in q if x["status"] in ("pending", "error")}
    if os.path.isdir(MEDIA):
        for ep_id in os.listdir(MEDIA):
            shutil.copytree(os.path.join(MEDIA, ep_id), os.path.join(dst, ep_id), dirs_exist_ok=True)
    for name in os.listdir(dst):
        p = os.path.join(dst, name)
        if os.path.isdir(p) and not name.startswith(".") and name not in keep:
            shutil.rmtree(p)
    open(os.path.join(dst, ".nojekyll"), "w").close()
    with open(os.path.join(dst, "index.html"), "w") as f:
        f.write("<!doctype html><title>Business English Brief media</title>")
    print("media kept:", sorted(keep))


def check():
    if os.environ.get("YT_REFRESH_TOKEN"):
        import youtube as Y
        cid, title = Y.whoami(Y.token())
        ok = cid == CH["youtube_channel_id"]
        print(f"YouTube: {title} ({cid}) -> {'OK' if ok else 'WRONG CHANNEL'}")
    else:
        print("YouTube: secrets not set")
    if os.environ.get("IG_TOKEN"):
        import instagram as I
        try:
            print("Instagram: @" + I.guard(CH["instagram_username"]) + " -> OK")
        except SystemExit as e:
            print("Instagram:", e)
    else:
        print("Instagram: secrets not set")
    if os.environ.get("AZURE_SPEECH_KEY"):
        import tts
        tts.synth('<speak version="1.0" xml:lang="ja-JP"><voice name="%s">テスト</voice></speak>' % CH["voices"]["jp"],
                  os.environ["AZURE_SPEECH_KEY"], os.environ.get("AZURE_SPEECH_REGION") or "japaneast")
        print("Azure Speech: OK")
    else:
        print("Azure Speech: secrets not set")


if __name__ == "__main__":
    cmd = sys.argv[1]
    dry = "--dry" in sys.argv
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    if cmd == "validate":
        ok = all(validate(a) for a in args)
        sys.exit(0 if ok else 1)
    elif cmd == "render":
        for a in args:
            render_ep(a)
    elif cmd == "publish":
        for a in args:
            publish_ep(a, dry)
    elif cmd == "pending":
        pending()
    elif cmd == "ig-due":
        ig_due(dry)
    elif cmd == "media-sync":
        media_sync(args[0])
    elif cmd == "check":
        check()
