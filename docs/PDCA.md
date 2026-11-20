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

- 11/14 Check (stats 11/14 05:21 JST). Channel 4 subs (was 2), 4,982 total views (4,019 on 11/06). Traffic: Shorts feed 4,600 /
  YouTube search 131 (2.6%) / channel page 23. IG 147 followers (130 on 11/07).
  Only #23, #24 and 速報 #30 are ≥3 days old, so most numbers below are early (age 0–2 days marked).
  - H1 (known topics): shorts ≥3 days of week 2 = 12, 43, 21, 8, 213, 74 → median 32 (baseline 33) — no lift yet.
    Younger: Nintendo 226/134 (age 0), ChatGPT 63/6, Nvidia 速報 37/19, Apple new CEO 9/7. Pattern: the **top headline in
    Japanese media / a Japanese household name** (SoftBank loss, Nintendo) reaches; a famous foreign brand alone does not (Apple 9).
    → KEEP, sharpened: rank candidates by "is it top news in Japan this week" first, brand fame second.
  - H2 (quiz vs news short, same episode): 43/12, 8/21, 74/213, 6/63, 7/9, 19/37, 134/226 → quiz wins 1 of 7, median quiz 19 vs
    news 37 (0.5×; target ≥1.5×). Caveat: the quiz short goes up 9 h later, so it is always younger at snapshot time.
    → KEEP the A/B to the cycle end (11/21), but it is on track to FAIL. Weekly listening #28 has 2 quiz-only shorts (0 so far, age <1 day).
  - H3 (listening long): #28 goes live 11/14 07:00 — no data yet. Weekday longs still median 0–1 view. → KEEP, judge 11/21.
  - H4 (IG 127 → 250): +17 followers/week → ~165 by 11/20, target missed. Reels reach 12–190. → KEEP posting; rethink in Cycle 2.
  - 速報 vs scheduled (same age 1–4 days): 速報 news shorts 213, 37 vs scheduled news shorts 12, 21, 63, 9 → early sign for the
    Cycle 2 candidate hypothesis "hot ≥3× scheduled".
  - Applied to #32–#38 (11/16–11/22): Nvidia CEO resignation (NHK top story), Honda results, Google robots at Mercedes,
    docomo/KDDI/SoftBank CEOs' apologies, yen at 160 — all Japan-known names. Shorts: news-first + quiz A/B unchanged.

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

- 11/21 Check — Cycle 1 end (stats 11/21 05:18 JST). Channel 17 subs (4 on 11/14), 10,559 total views (4,982 on 11/14).
  Traffic: Shorts feed 9,575 / YouTube search 277 (2.6%) / other YT pages 163 / channel page 72. IG 157 followers (147 on 11/14).
  Videos ≥3 days old from #22 on (published 11/08–11/17 UTC): 13 episodes.
  - H1 (known topics, median short 50 → 300): median of all 26 shorts = 82 (baseline 33, ×2.5) — target missed, direction right.
    Top: 「it depends on how you define」921, 「pass on the cost」919, 「a drag on」658, 「weigh on」651, 「work alongside」635, 「as things stand」525.
    Lowest: Apple new CEO 14/11, ChatGPT 66/9, Toyota 22/10. → KEEP as the default topic rule (it's the floor, not the growth lever).
  - H2 (quiz ≥1.5× news): quiz median **162** vs news **66 = 2.5×**; quiz won 8 of 12 pairs, and **all 6 pairs from 11/13 on**
    (919/244, 525/148, 162/90, 658/74, 635/45, 651/50). The early losses were all on 11/09–11/12 when nothing reached.
    → **PASS. Make quiz the standard** for both shorts.
  - H3 (listening long >5× weekday long): #28 = 4 views, avg view 21 s (5%) vs weekday median 1 view. Both ~0; no signal,
    and the 5% retention says people leave in the first 20 s. → STOP as a growth bet (keep the Saturday slot because the
    workflow and CLAUDE.md expect it), CHANGE its packaging in Cycle 2 (H7).
  - H4 (IG 127 → 250): 157 (+10/week). Reels median ~80 views, saves ≈0. → FAIL. Keep posting (it's automatic), no new bet.
  - 速報 vs scheduled news shorts (same age): 213, 54, 50 vs scheduled median 66 — no clear lift once age is equal. Not a hypothesis.
  - **Pivot decision:** all three pivot signals are true (search 2.6% < 5%; weekday longs median 1 < 10; quiz beats news).
    → PIVOT per the rule above: Cycle 2 tests search-first packaging; the news stays as the source of the example sentences.
    (competitors.yml crashed on a video without `duration`; fixed in engine/competitors.py, re-run after the push.)

## Cycle 2 — 2026-11-21 → 2026-12-04 (episodes #42– , 11/23–12/06)

| # | hypothesis | change | metric (videos ≥3 days old) | target |
| --- | --- | --- | --- | --- |
| H5 | Two quiz shorts per episode beat one quiz + one news short | `shorts[0]` is also a quiz (`style: quiz`, another phrase); no news-first short on scheduled episodes (速報 keeps its news short) | median views of `shorts[0]` vs Cycle 1 news-first median 66 | ≥ 150 |
| H6 | A searched tag in the quiz title brings search/browse views | A/B inside each episode: on Mon/Wed/Fri/Sun `shorts[0]` title = `「<en>」の意味、わかる?|TOEIC730点・会議の英語 #shorts`, `shorts[1]` keeps `…|会議の英語 #shorts`; Tue/Thu the other way round; Sat `shorts[0]` tagged | median tagged vs untagged; channel search share | tagged ≥ 1.3× untagged; search 2.6% → 5% |
| H7 | A searchable list title makes the Saturday long findable | Saturday long title `【聞き流し】TOEIC・会議で使えるビジネス英語<N>選|…` (not 「TOEIC頻出」: we can't verify frequency) + a one-line hook so the first phrase starts within ~10 s | Saturday long views at 7 days; avg view % | ≥ 30 views; ≥ 15% |

Check (fill in on 11/28 and 12/05):

- 11/21 (Do): applied H5–H7 to #42–#48 (11/23–11/29). Topics: SMBC/MUFG data leak via KARTE (top Japanese news 11/18–20),
  Walmart Q3, Apple's own AI agent (report), Nadella at DealBook, Japan's October CPI and a December BOJ hike (overseas
  coverage), Saturday listening, Sunday "reporting an outage" (Microsoft Outlook/Teams outage 11/12).
