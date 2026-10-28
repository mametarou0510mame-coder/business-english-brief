# Episode format (`episodes/<id>/episode.json`)

The full working example is `episodes/2026-10-25-amex-ai-cuts/episode.json`. Copy its shape.

The engine adds these scenes automatically, so do **not** write them:
the title card (after the first scene), the review (phrases quiz + key words), and the outro (summary + homework).
Beat ids starting with `v`, `w`, `o`, `t` followed by digits are reserved for them.

## Top level

| key | meaning |
| --- | --- |
| `id` | folder name, `YYYY-MM-DD-slug` (date = publish date) |
| `episode` | `"#02"` … (increment from the latest episode) |
| `date` | news date shown on the title card (`YYYY-MM-DD`) |
| `series` | weekday format name (see CLAUDE.md) |
| `title_card` | `{line1, line2}` big Japanese title lines |
| `publish` | `{long: "YYYY-MM-DDT07:00:00+09:00", shorts: ["…T12:00:00+09:00", "…T21:00:00+09:00"]}` |
| `phrases` | exactly 3 × `{en, jp, ex, ex_jp}`; `ex` must contain `en` verbatim |
| `words` | 3 × `{en, jp}` |
| `homework` | `{en, jp, hl:[word], say}`; `say` = the Japanese narration line |
| `scenes` | content scenes (below) |
| `youtube` | `{title (≤100 chars), summary (2–3 sentences), tags:[…]}` — description is assembled automatically. Title pattern (search-first): `「<phrase jp>」は英語で?<phrase en>の使い方|<news in ≤20 chars>【ビジネス英語ニュース #NN】` |
| `thumbnail` | `{big, big_color, under, badge, badge_color, question, pill, bottom}` (see thumb.py) |
| `shorts` | 1–2 × `{phrase: 0-2, news_hook:[line1, line2], hook:[line1, line2], ctx, title, ig_caption}` — `news_hook` is the 2-line headline on the short's first frame (≤13 chars per line) |
| `sources` | `[{title, url}]` pages you actually opened |
| `readings` | optional `[["表記", "よみ"], …]` pronunciation fixes for the Japanese voice |

## Scenes and beats

```json
{"id": "what", "chapter": "何が起きたか", "beats": [
  {"id": "n01", "kind": "jp", "jp": "日本語ナレーション", "en": "Own English subtitle.",
   "hl": ["phrase to highlight"], "star": true, "vis": {"t": "counter", "...": "..."}}
]}
```

- The first scene is the hook (no `chapter`). Every other content scene has a `chapter` (it becomes a YouTube chapter).
- `kind`: `jp` (Japanese narration, English subtitle on top), `en_insert` (English voice reads `en`; use for the key phrase, 1–2 s),
  `silent` / `pause` with `dur` seconds.
- `en` is **your own English** summarising the line — never copy article sentences. Short quotes of what someone said are fine.
- `star: true` shows "★ あとで復習" — use it on the beats that introduce the 3 phrases.
- A beat with the same `vis` as the previous one keeps the visual; changing a field (e.g. `show`) animates only the new part.
- Japanese line length: 15–60 characters. Write numbers as you want them read, or add `readings`.

## Visual templates (`vis.t`)

| t | fields | use for |
| --- | --- | --- |
| `hero` | kicker, big, color, crack, sub, sub_color | the opening shock number/word |
| `hero_side` | big, color, text (typed English), jp | number + the key English phrase |
| `teaser` | title?, note? | "today's 3 phrases" masked list (hook end) |
| `people` | total, hit, label, panel (object or list of rows: kicker, big or count{to,prefix,suffix,decimals}, color, sub, note, size) | share of people/jobs |
| `counter` | kicker, to/prefix/suffix/decimals or big, color, sub, note | one big counting number |
| `bars` | title, unit, items[{label, value, display?, color?}], note | comparing 2–6 values |
| `vs` | left/right{en, label, val, up, color}, mid | two things moving opposite ways |
| `quote` | lines[], hl[], by | a short quote of what an executive said |
| `cards` | items[{name, big, sub, note, color}], show, footer | 2–3 companies / cases side by side |
| `points` | items[{num?, head, big, sub, color}], show | 2–3 takeaways (use in "私たちへの意味") |
| `flow` | rows[{a, mid, res, ok}] | cause → mechanism → result |
| `layers` | layers[bottom→top], icing{label,en,jp,en2,jp2}, glow, footer | foundations vs. add-ons |
| `org` | flat, label | org chart getting flatter |
| `statement` | kicker, text, sub | section opener ("SO WHAT?") |
| `timeline` | items[{when, text, color}], show | sequence of events / dates |
| `globe` | title, lines[{text, color}], points[{label, lat, lon, color}], arcs[[i, j]], lon (centre longitude), lat (tilt) | rotating CG globe with land dots, glowing markers and flight arcs — cross-border stories |
| `line` | title, points[{label, value}], color, display (end label), mark[{i, text}], note | animated glowing line chart — only with real data points |
| `network` | title, center{label, sub}, nodes[{label, color}], inward | hub-and-spoke network with flowing packets — ecosystems, portfolios, teams |

Colors: `red` (bad/down), `green` (good/up), `gold` (key), `blue`, `text`, `muted`.

## Check before pushing

```
python engine/build.py validate episodes/<id>
```
prints the estimated length and writes `out/preview_sheet.png` and `out/thumbnail.png` — open them and look.
Target length 4–7 minutes (≈1,800–2,800 TTS characters).

Motion (automatic, no fields): living background (drifting grid, orb, particles), slow camera push-in per scene,
light-sweep scene transitions, extruded 3D type with a shine pass on `hero`, `hero_side`, `counter` and the title card.
