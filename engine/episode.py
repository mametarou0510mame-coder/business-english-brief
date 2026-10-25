"""Load an episode, expand the automatic scenes, and build the timeline."""
import json, os, re, subprocess, copy

GAP = {"jp": 0.35, "en_insert": 0.55, "rv_en": 0.6, "rv_jp": 0.6, "pause": 0.0, "silent": 0.0}
VOICE_OF = {"jp": "JP", "rv_jp": "JP", "en_insert": "EN", "rv_en": "EN"}

READINGS = [("AI", "エーアイ"), ("CFO", "シーエフオー"), ("CEO", "シーイーオー"), ("%", "パーセント")]


def tts_reading(s, extra=None):
    for k, v in (extra or []):
        s = s.replace(k, v)
    s = re.sub(r"(\d),(\d{3})", r"\1\2", s)
    for k, v in READINGS:
        s = s.replace(k, v)
    return s


def load(ep_dir):
    with open(os.path.join(ep_dir, "episode.json"), encoding="utf-8") as f:
        ep = json.load(f)
    ep["_dir"] = ep_dir
    return ep


def expand(ep):
    """Return the full scene list: hook… + title card + content scenes + review + outro."""
    scenes = copy.deepcopy(ep["scenes"])
    # title card after the first (hook) scene
    title = {"id": "title", "visual": "title", "beats": [{"id": "t01", "kind": "silent", "dur": 3.2}]}
    scenes.insert(1, title)
    ph, words = ep["phrases"], ep.get("words", [])
    n = len(ph)
    rv = [{"id": "v00", "kind": "jp", "jp": "それでは、答え合わせです。まず英語だけを聞いて、意味がわかるか試してください。",
           "en": "Review time. Listen to the English first.", "vis": {"phase": "intro"}}]
    for i, p in enumerate(ph):
        k = i + 1
        rv += [
            {"id": f"v{k}1", "kind": "rv_en", "en": p["en"], "vis": {"card": i, "phase": "quiz"}},
            {"id": f"v{k}2", "kind": "pause", "dur": 2.0, "vis": {"card": i, "phase": "count"}},
            {"id": f"v{k}3", "kind": "rv_en", "en": p["en"], "vis": {"card": i, "phase": "reveal"}},
            {"id": f"v{k}4", "kind": "rv_jp", "jp": p["jp"], "vis": {"card": i, "phase": "reveal"}},
            {"id": f"v{k}5", "kind": "rv_en", "en": p["ex"], "vis": {"card": i, "phase": "example"}},
            {"id": f"v{k}6", "kind": "pause", "dur": 3.0, "vis": {"card": i, "phase": "repeat"}},
            {"id": f"v{k}7", "kind": "rv_jp", "jp": p["ex_jp"], "vis": {"card": i, "phase": "example_jp"}},
            {"id": f"v{k}8", "kind": "rv_en", "en": p["en"], "vis": {"card": i, "phase": "final"}},
        ]
    if words:
        rv.append({"id": "v90", "kind": "jp", "jp": "続いて、単語です。", "en": f"Now, {len(words)} key words.",
                   "vis": {"phase": "words_intro"}})
        for i, w in enumerate(words):
            rv += [
                {"id": f"w{i}1", "kind": "rv_en", "en": w["en"], "vis": {"word": i, "phase": "w_en"}},
                {"id": f"w{i}2", "kind": "rv_jp", "jp": w["jp"], "vis": {"word": i, "phase": "w_jp"}},
                {"id": f"w{i}3", "kind": "rv_en", "en": w["en"], "vis": {"word": i, "phase": "w_jp"}},
            ]
    scenes.append({"id": "review", "visual": "review", "chapter": "復習", "beats": rv})
    hw = ep.get("homework", {})
    out = [
        {"id": "o01", "kind": "jp", "jp": f"今日の{n}フレーズ、ぜひ明日の会議で使ってみてください。",
         "en": f"Try these {n} phrases in your next meeting.", "vis": 0},
    ]
    if hw:
        out.append({"id": "o02", "kind": "jp", "jp": hw.get("say", "最後に宿題です。英語で、コメント欄に書いてみてください。"),
                    "en": "Homework: " + hw["en"], "vis": 1})
    out += [{"id": "o03", "kind": "jp", "jp": "ビジネス・イングリッシュ・ブリーフ。また明日お会いしましょう。",
             "en": "See you tomorrow.", "vis": 1},
            {"id": "o04", "kind": "silent", "dur": 2.5, "vis": 1}]
    scenes.append({"id": "outro", "visual": "outro", "chapter": "まとめ", "beats": out})
    return scenes


def audio_len(ep_dir, bid):
    for ext in ("wav", "mp3", "m4a"):
        p = os.path.join(ep_dir, "audio", f"{bid}.{ext}")
        if os.path.exists(p):
            o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                               capture_output=True, text=True).stdout
            return float(o.strip()), p
    return None, None


def estimate(b):
    k = b["kind"]
    if k == "jp":
        n = len(re.sub(r"[、。「」・\s]", "", b["jp"]))
        return n / 6.4 + 0.15 * b["jp"].count("、") + 0.3 * b["jp"].count("。")
    if k in ("en_insert", "rv_en"):
        return max(1.2, len(b["en"].split()) / 2.6 + 0.2)
    if k == "rv_jp":
        return max(1.0, len(b["jp"]) / 6.0)
    return b.get("dur", 1.0)


def timeline(ep):
    scenes_in = expand(ep)
    t, beats, scenes = 0.0, [], []
    for si, sc in enumerate(scenes_in):
        s0 = t
        prev_key, vis_t0, prev_vis = None, t, None
        for b in sc["beats"]:
            L, path = (None, None) if b["kind"] in ("pause", "silent") else audio_len(ep["_dir"], b["id"])
            speech = L if L else estimate(b)
            dur = b["dur"] if b["kind"] in ("pause", "silent") else speech + GAP[b["kind"]]
            vis = b.get("vis")
            key = json.dumps(vis, sort_keys=True, ensure_ascii=False)
            cont = False
            if key != prev_key:
                if isinstance(vis, dict) and isinstance(prev_vis, dict) and vis.get("t") and vis.get("t") == prev_vis.get("t"):
                    cont = True
                    vis = dict(vis, _prev_show=prev_vis.get("show", 0), _prev_icing=bool(prev_vis.get("icing")),
                               _prev_flat=bool(prev_vis.get("flat")))
                vis_t0, prev_key = t, key
                cur_vis, cur_cont = vis, cont
            beats.append(dict(b, vis=cur_vis, cont=cur_cont, scene=si, start=round(t, 3), dur=round(dur, 3),
                              speech=round(speech, 3), vis_t0=round(vis_t0, 3), audio=path, estimated=L is None))
            prev_vis = b.get("vis")
            t += dur
        if si < len(scenes_in) - 1:
            t += 0.5
        scenes.append(dict(id=sc["id"], visual=sc.get("visual", "main"), chapter=sc.get("chapter"), start=s0, end=t))
    return dict(scenes=scenes, beats=beats, total=round(t, 3))


def tts_lines(ep):
    extra = [tuple(x) for x in ep.get("readings", [])]
    out = []
    for sc in expand(ep):
        for b in sc["beats"]:
            k = b["kind"]
            if k not in VOICE_OF:
                continue
            voice = VOICE_OF[k]
            text = b.get("say") or (b["jp"] if voice == "JP" else b["en"])
            if voice == "JP":
                text = tts_reading(text, extra)
            out.append({"id": b["id"], "voice": voice, "text": text, "slow": k == "rv_en"})
    return out


def fmt_ch(s):
    m, r = divmod(int(s), 60)
    return f"{m}:{r:02d}"


def chapters(tl):
    out = []
    for sc in tl["scenes"]:
        if sc["id"] == tl["scenes"][0]["id"]:
            out.append("0:00 オープニング")
        elif sc.get("chapter"):
            out.append(f"{fmt_ch(sc['start'])} {sc['chapter']}")
    return out


def _srt_t(s):
    h, r = divmod(s, 3600)
    m, r = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(r):02d},{int((r % 1) * 1000):03d}"


def srt(tl, lang):
    out, i = [], 1
    for b in tl["beats"]:
        if b["kind"] in ("pause", "silent"):
            continue
        text = (b.get("jp") or b.get("en")) if lang == "ja" else (b.get("en") or b.get("jp"))
        out.append(f"{i}\n{_srt_t(b['start'])} --> {_srt_t(b['start'] + b['speech'] + 0.2)}\n{text}\n")
        i += 1
    return "\n".join(out)


DISCLAIMER = ("※英語字幕は報道内容をもとにした独自の英文です。発言の引用部分は出典の報道によります。\n"
              "※ナレーションはAI音声（Microsoft Azure AI Speech）を使用しています。\n"
              "※特定の銘柄の売買を勧めるものではありません。")


def long_description(ep, tl):
    y = ep["youtube"]
    L = [y["summary"], ""]
    L.append(f"■ 今日の{len(ep['phrases'])}フレーズ")
    for i, p in enumerate(ep["phrases"]):
        L.append(f"{i + 1}. {p['en']}（{p['jp']}）")
    if ep.get("words"):
        L += ["", "■ 単語", " / ".join(f"{w['en']}（{w['jp']}）" for w in ep["words"])]
    if ep.get("homework"):
        L += ["", "■ 宿題", ep["homework"]["en"], ep["homework"].get("jp", "")]
    L += ["", "■ チャプター"] + chapters(tl)
    L += ["", "■ 出典"]
    for s in ep.get("sources", []):
        L += [s["title"], s["url"]]
    L += ["", DISCLAIMER, "", " ".join(y.get("hashtags", ["#ビジネス英語", "#英語学習", "#ニュース英語"]))]
    return "\n".join(L)
