# BEB growth PDCA log

Every Saturday the weekly task reads `stats/latest.json` (written by the Stats workflow at 04:30 JST), fills in the
"Check" of the running cycle, and writes the next cycle's plan here before producing episodes.
Metric definitions: views are lifetime views at snapshot time; compare videos of similar age (≥3 days old).

## Baseline — 2026-11-06 (channel age 2 weeks, 48 videos)

- Channel: 2 subscribers, 4,019 total views. Instagram: 127 followers, 42 posts (was 25 on 10/26).
- Long videos (4 min): almost all 0–7 views. YouTube is not showing them at all (no subscribers, no search traffic yet).
- Shorts: wide spread, 0–896 views. Best: KFC×ペプシ決別 896 / ボルボ 739 / メタ罰金 541 / 折りたたみiPhone 320 /
  「ほぼ予想どおり」299 / 「別の角度から」220. Worst: Salesforce×Braze 0, PHP 1, 日本CPI 0, 11/2週の多く 3–97.
- Pattern: well-known brands + conflict/drama get tested further; obscure B2B names (Braze, PHP, Robinhood) die at 0–80.
  Shorts uploaded in a burst (13 on 10/26) mostly stalled.

## Competitor scan — 2026-11-06 (YouTube API, 20 latest uploads each)

| channel | subs | format | what works |
| --- | --- | --- | --- |
| 猛牛ちゃんねる (TOEIC) | 128k | 100% shorts, 35–55s | one word per short; title「adapt の意味、わかる？｜TOEIC700点」; level tag; median 1.7k |
| ビジネス英語コーチHika | 42k | 45% shorts | short dramas/skits 16–24k; long 13 min interviews |
| HelloEar 1日1フレーズ | 104k | daily long 12 min at 07:00 | numbered daily series (瞬間英作文 292日目), emotional line in title, median 5.8k |
| mochantv | 585k | long 8–28 min | real speeches of famous people (Obama, 南場, Musk) with 英日字幕+解説 |
| Sakura English / ksp | 811k / 217k | long 20–180 min | 聞き流し・リスニング compilations, median 15–53k |
| 日経CNBC / 日テレ / BBC Japan | 227k–3.4M | news | the week's biggest headline (米中間選挙, 日経平均急落) gets 50k–800k |

Takeaways: (1) learning channels win long-form with **10–30 min listening/practice compilations**, not 4-min explainers;
(2) shorts that work are **one item, one question, ≤40 s, very short title with a level tag**; (3) news reach comes
from **the biggest headline Japanese viewers already care about**; (4) consistency and a numbered series build habit.

## Cycle 1 — 2026-11-07 → 2026-11-20

| # | hypothesis | change | metric (videos ≥3 days old) | target |
| --- | --- | --- | --- | --- |
| H1 | Topics Japanese viewers already know get more shorts views | pick stories with famous consumer brands, Japan-related companies, or the week's top headline in Japanese media; avoid obscure B2B names | median short views | 50 → 300 |
| H2 | A phrase-first quiz short (no news intro, ~20 s, title「◯◯ の意味、わかる？」) beats the news-first short | every episode: short1 = news-first (style news), short2 = quiz (style quiz, badge with level) | median views quiz vs news | quiz ≥ 1.5× news |
| H3 | A weekly 聞き流し compilation earns long-form views where 4-min explainers do not | Saturday long = `build.py compile-week` (all phrases of the week, ~7–10 min) | Saturday long views vs weekday long | > 5× weekday median |
| H4 | Instagram grows faster than YouTube for this niche | keep 2 reels + carousel daily | IG followers | 127 → 250 |

Check (fill in on 11/14 and 11/21):

- 11/07 (Do, week 1): applied all four changes to episodes #23–#29 (11/09–11/15).
  H1 topics: 米中間選挙→日経平均6%安, トヨタ決算, ChatGPT vs Google, Apple新CEO, 任天堂スイッチ2 — all household names.
  H2: every episode has short1 = news-first, short2 = quiz (badge 会議で使う英語|中級); Saturday #28 has 2 quiz shorts.
  H3: Saturday #28 is the first `compile-week` listening video (18 phrases, ~8 min). Engine: outro now uses a compact
  grid when an episode has more than 3 phrases. Baseline at start (stats 11/07, videos ≥3 days old):
  median short 33 views, median long 0, IG 130 followers. First Check on 11/14 (only #16–#22 will be ≥3 days old).
- 11/07 ops change (owner): hot topics are published immediately (series 速報, see CLAUDE.md). Track hot vs scheduled
  views separately from 11/14; candidate hypothesis for Cycle 2: "a hot story published the same day gets ≥3× the
  views of a scheduled one".
- 11/07 analytics now readable (YouTube Analytics + IG insights, stats run 11/07 18:28 JST). Baseline (all videos so far):
  traffic = Shorts feed 3,844 views vs YouTube search 106 / channel page 12. Median short: 71–97 views, avg view 11–13 s,
  ~50% viewed. Long: median 2 views, avg 63 s (31%). IG reels: median 23 views / reach 13, saves ≈0, shares 0.
  → Discovery is almost only the Shorts feed; search brings nothing yet, long videos are not found at all.

## Pivot watch: search-first / TOEIC format (owner idea 11/07 — decide at the Cycle 1 end, 11/21)

Owner suggests we may pivot to a format people search for (e.g. TOEIC). Decide on 11/21 with these rules:
- **Pivot signal:** YouTube search stays < 5% of views AND weekday news longs stay at median < 10 views AND the quiz short
  (H2) beats the news short. Then news is not what people come for — the phrase/quiz is.
- **If pivot:** Cycle 2 tests a search-first format while keeping the news as the "example sentence" source:
  (a) quiz shorts titled with a searched tag, e.g. `「<phrase>」の意味、わかる?|TOEIC730点・会議の英語 #shorts`;
  (b) the Saturday long as a searchable list, e.g. `【TOEIC頻出】ビジネス英語◯選|聞き流し`;
  (c) before writing, dispatch `competitors.yml` (already scans 「TOEIC 英単語」) and pick wording from what ranks.
  Metric: search-traffic views and median views of TOEIC-tagged vs untagged quiz shorts.
- **If not:** keep the news concept; revisit at the end of Cycle 2.
