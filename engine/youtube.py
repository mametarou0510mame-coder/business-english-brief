"""YouTube Data API: scheduled uploads with a channel-identity guard.

Env: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
Every upload first checks that the token belongs to channel.json's youtube_channel_id,
so a token issued for another channel (e.g. ツレドキ) can never post here.
"""
import json, os, urllib.request, urllib.parse, urllib.error

API = "https://www.googleapis.com/youtube/v3"
UP = "https://www.googleapis.com/upload/youtube/v3"


def _req(method, url, data=None, headers=None, raw=None):
    h = dict(headers or {})
    body = raw
    if data is not None:
        if h.get("Content-Type") == "application/json":
            body = json.dumps(data).encode()
        else:
            body = urllib.parse.urlencode(data).encode()
            h.setdefault("Content-Type", "application/x-www-form-urlencoded")
    r = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=600) as resp:
            txt = resp.read()
            return resp, (json.loads(txt) if txt and resp.headers.get_content_type() == "application/json" else txt)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"YouTube API {e.code} {url.split('?')[0]}: {e.read()[:400]!r}")


def token():
    _, j = _req("POST", "https://oauth2.googleapis.com/token", {
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"})
    return j["access_token"]


def whoami(tok):
    _, j = _req("GET", f"{API}/channels?part=snippet&mine=true", headers={"Authorization": f"Bearer {tok}"})
    it = (j.get("items") or [{}])[0]
    return it.get("id"), it.get("snippet", {}).get("title")


def guard(tok, expected_id):
    cid, title = whoami(tok)
    if cid != expected_id:
        raise SystemExit(f"STOP: token is for channel {title!r} ({cid}), expected {expected_id}. Nothing was uploaded.")
    return title


def upload(tok, path, meta):
    """meta: title, description, tags, publish_at (ISO with tz) or None for public now."""
    status = {"selfDeclaredMadeForKids": False, "containsSyntheticMedia": False, "embeddable": True}
    if meta.get("publish_at"):
        status.update(privacyStatus="private", publishAt=meta["publish_at"])
    else:
        status["privacyStatus"] = meta.get("privacy", "public")
    body = {"snippet": {"title": meta["title"][:100], "description": meta["description"][:5000],
                        "tags": meta.get("tags", [])[:30], "categoryId": "27",
                        "defaultLanguage": "ja", "defaultAudioLanguage": "ja"},
            "status": status}
    size = os.path.getsize(path)
    resp, _ = _req("POST", f"{UP}/videos?uploadType=resumable&part=snippet,status", body,
                   {"Authorization": f"Bearer {tok}", "Content-Type": "application/json",
                    "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)})
    loc = resp.headers["Location"]
    with open(path, "rb") as f:
        data = f.read()
    _, j = _req("PUT", loc, headers={"Authorization": f"Bearer {tok}", "Content-Type": "video/mp4"}, raw=data)
    if isinstance(j, bytes):
        j = json.loads(j)
    return j["id"]


def set_thumbnail(tok, vid, png):
    with open(png, "rb") as f:
        data = f.read()
    _req("POST", f"{UP}/thumbnails/set?videoId={vid}", headers={"Authorization": f"Bearer {tok}", "Content-Type": "image/png"}, raw=data)


def set_title(tok, vid, title):
    H = {"Authorization": f"Bearer {tok}"}
    _, j = _req("GET", f"{API}/videos?part=snippet&id={vid}", headers=H)
    sn = j["items"][0]["snippet"]
    body = {"id": vid, "snippet": {"title": title[:100], "description": sn.get("description", ""), "tags": sn.get("tags", []),
                                   "categoryId": sn.get("categoryId", "27"), "defaultLanguage": sn.get("defaultLanguage", "ja")}}
    _req("PUT", f"{API}/videos?part=snippet", body, {**H, "Content-Type": "application/json"})
