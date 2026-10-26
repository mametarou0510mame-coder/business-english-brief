"""Instagram Graph API (Facebook Login): publish a Reel from a public video URL.

Env: IG_USER_ID, IG_TOKEN. A username guard stops posting from a token for another account.
"""
import json, os, time, urllib.request, urllib.parse, urllib.error

API = "https://graph.facebook.com/v21.0"


def _http(method, url, data=None):
    body = urllib.parse.urlencode(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Instagram API {e.code}: {e.read()[:400]!r}")


def guard(expected_username):
    uid, tok = os.environ["IG_USER_ID"], os.environ["IG_TOKEN"]
    j = _http("GET", f"{API}/{uid}?fields=username&access_token={tok}")
    if not j.get("username"):
        try:
            pg = _http("GET", f"{API}/{uid}?fields=name,instagram_business_account&access_token={tok}")
        except Exception as e:
            pg = {"error": str(e)[:200]}
        raise SystemExit(f"STOP: IG_USER_ID {uid} is not an Instagram account. Looked up as: {pg}. "
                         "If this is the Facebook page, use its instagram_business_account id as IG_USER_ID.")
    if j.get("username", "").lower() != expected_username.lower():
        raise SystemExit(f"STOP: IG token is for @{j.get('username')}, expected @{expected_username}. Nothing was posted.")
    return j["username"]


def publish_reel(video_url, cover_url, caption):
    uid, tok = os.environ["IG_USER_ID"], os.environ["IG_TOKEN"]
    c = _http("POST", f"{API}/{uid}/media", {"media_type": "REELS", "video_url": video_url, "cover_url": cover_url,
                                             "caption": caption, "share_to_feed": "true", "access_token": tok})
    cid = c["id"]
    for _ in range(60):
        st = _http("GET", f"{API}/{cid}?fields=status_code,status&access_token={tok}")
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram processing failed: {st}")
        time.sleep(10)
    else:
        raise RuntimeError("Instagram processing timed out")
    r = _http("POST", f"{API}/{uid}/media_publish", {"creation_id": cid, "access_token": tok})
    mid = r["id"]
    try:
        link = _http("GET", f"{API}/{mid}?fields=permalink&access_token={tok}").get("permalink")
    except Exception:
        link = None
    return mid, link


def _wait(cid, tok, tries=60):
    for _ in range(tries):
        st = _http("GET", f"{API}/{cid}?fields=status_code&access_token={tok}")
        if st.get("status_code") in (None, "FINISHED"):
            return
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram processing failed: {st}")
        time.sleep(5)
    raise RuntimeError("Instagram processing timed out")


def publish_carousel(image_urls, caption):
    uid, tok = os.environ["IG_USER_ID"], os.environ["IG_TOKEN"]
    kids = []
    for u in image_urls[:10]:
        c = _http("POST", f"{API}/{uid}/media", {"image_url": u, "is_carousel_item": "true", "access_token": tok})
        _wait(c["id"], tok)
        kids.append(c["id"])
    c = _http("POST", f"{API}/{uid}/media", {"media_type": "CAROUSEL", "children": ",".join(kids), "caption": caption,
                                             "access_token": tok})
    _wait(c["id"], tok)
    r = _http("POST", f"{API}/{uid}/media_publish", {"creation_id": c["id"], "access_token": tok})
    mid = r["id"]
    try:
        link = _http("GET", f"{API}/{mid}?fields=permalink&access_token={tok}").get("permalink")
    except Exception:
        link = None
    return mid, link
