# BEB studio — the current format (owner decisions 2026-11-24)

**Format:** one world business phenomenon explained in **English narration** (Kokoro AI voice), with **one subtitle band**:
English (large, one sentence) above Japanese (small). Keyword highlighted yellow in both. Nothing is drawn over the subtitle band
(y ≥ 860 is reserved). Look = **theme A** (light paper, black/red/navy). About 3–5 minutes.
Per episode: 1 long video, 1 short (vertical, also posted as the Instagram reel), 1 Instagram carousel, 1 thumbnail.

**Cadence:** per day 1 long (07:00 JST), 1 YouTube short + 1 reel (12:00), 1 carousel (21:00) — `studio-publish.yml`
posts the next item from `queue.json`. Production keeps **up to 7 days of stock**, making **at most 2 episodes per day**.

## Files of an episode (`studio/episodes/<slug>/`)
- `episode.json` — scenes, beats, `publish` (title, summary, phrases, sources, tags, thumb, short title + ig_caption,
  carousel_caption) and `carousel` (cover, num, numSub, phrases, src). Model: `studio/episodes/ai-power/episode.json`.
- `short.json` — vertical short (≈20–35 s): `"portrait": {"head": "<div class='q'>問い<b>強調</b></div><div class='e'>phrase</div>"}`,
  one or two scenes from the long video + a `cta` scene. Model: `ai-power/short.json`.
- `studio/thumb/<slug>.html` → `<slug>.jpg` (1280×720, model `thumb/ai-power.html`: big Japanese title, one red number, phrase pill, one illustration).

## Beats
`{"en", "jp", "hl": [en_keyword, jp_keyword]}`. Optional `"hold": seconds` = silent beat (no narration).
English: B1–B2, short sentences (≤ 18 words), your own words. Japanese: natural, short, one line if possible.

## Scene components (`vis.type`) — `scenes.js`
Generic (prefer these): `bigstat` (kicker, value, decimals, prefix, suffix, tag, sub, src, art: datacenter|none, num_at, tag_at),
`bars` (title, title_jp, items[{label, value, display, color}], note, at[]), `line` (title, points[{label, value}], display, note, min),
`cards` (title, items[{title, jp, value, note, color}], at[]), `flow` (title, items[{title, jp, color}], at[]),
`map` (title, markers[{label, jp, lat, lon, color}], arcs[[i, j]], at[], arc_at[]), `versus` (title, left/right{title, jp, value, color}),
`units` (n, icon: home|person|car, unit, left{label, sub}), `quote` (text, jp, by), `phrases` (items[{en, jp, ex, ex_jp, key}] with beats
step intro/say/think(hold)/ex), `outro` (items), `cta` (en, jp, btn).
Topic-specific (from ai-power): `hook`, `growth`, `rack`, `capex`, `bottleneck`, `scramble`, `japan`, `efficiency`.
`at[i]` = beat index at which item i appears (default: item i on beat i). Colors: red, navy, green, amber, muted or hex.
You may add a new component for a topic (append to scenes.js, never change existing ones' behaviour).

## Commands
- Stills (no voice needed): `python studio/render.py studio/episodes/<slug>/episode.json --stills 2,8,15` → `<name>_still_*.jpg`
- Carousel: `python studio/carousel.py studio/episodes/<slug>/episode.json /tmp/car`
- Thumbnail: render the html with Playwright (see how ai-power.jpg was made: `#t` screenshot, jpeg q92) and commit the jpg.
- Full render with voice (GitHub Actions): dispatch `studio.yml` with `episode=studio/episodes/<slug>/episode.json` and again with
  `short.json` → branch `studio-media/<slug>/` gets episode.mp4, episode_timeline.json, carousel/, short.mp4, short.jpg.
- Then append `<slug>` to `studio/queue.json` (only after both renders succeeded).
