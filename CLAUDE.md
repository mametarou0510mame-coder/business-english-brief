# Business English Brief — production notes

YouTube @bizenglishbrief / Instagram @businessenglishbrief.
Concept: 「世界のビジネスニュースで、明日の会議の英語を。」 Japanese narration explains one overseas business news story,
English shows as subtitles, and the video ends with a quiz-style review of 3 meeting phrases (English → Japanese).
Audience: Japanese business people 25–44 who need English and general business knowledge.

## How publishing works

1. A weekly Claude task writes 7 episodes (next Monday–Sunday) as `episodes/<YYYY-MM-DD-slug>/episode.json` and pushes to `main`.
2. `.github/workflows/build.yml` narrates them (Azure), renders long video + 2 shorts + thumbnail,
   uploads to YouTube as **scheduled** (long 07:00, shorts 12:00 / 21:00 JST), and queues Instagram reels.
3. `.github/workflows/instagram.yml` posts the reels at 12:00 / 21:00 JST.
4. The owner may check the scheduled videos in YouTube Studio on Sunday and fix or delete them before they go live.

Format spec: `docs/FORMAT.md`. Engine: `engine/`. State: `state/published.json`, `state/ig_queue.json` (written by Actions — don't edit by hand unless fixing).

## Weekly production task (run on Saturday)

0. **PDCA first.** Read `docs/PDCA.md` and `stats/latest.json` (the Stats workflow commits it every Saturday 04:30 JST;
   if it is older than a day, dispatch `stats.yml` and wait). Fill in the "Check" of the running cycle with the real numbers
   (compare only videos ≥3 days old), decide keep/stop/change for each hypothesis, and when a cycle ends write the next
   cycle (≤4 hypotheses, each with one change, one metric, one target). Apply the decisions to this week's episodes.
1. Look at the latest episode number in `episodes/` and continue from it.
2. Research the past week's business news with WebSearch (and WebFetch only on URLs returned by search).
   Open every page you take a number or quote from, and list it in `sources`.
3. Pick 7 stories, one per weekday format:

   | day | series | angle |
   | --- | --- | --- |
   | Mon | Weekly Brief | the biggest business story of the past week |
   | Tue | 決算と数字の英語 | an earnings report and how numbers are said in English |
   | Wed | テックとAI | technology / AI business move |
   | Thu | 経営者の一言を読む | a CEO/CFO statement and its business English |
   | Fri | 海外メディアが報じる日本 | how overseas media covered a Japanese company or the Japanese economy |
   | Sat | 今週の英単語 総復習 | 聞き流し compilation of all of the week's phrases (`build.py compile-week`), ~7–10 min |
   | Sun | 場面別の英語 | evergreen: a meeting/email situation (disagreeing politely, asking for deadlines…) tied to a recent story |

   Prefer stories that stay relevant for a week (structural moves, not hour-by-hour market moves).
   **Reach rule (PDCA H1):** choose stories Japanese viewers already know or care about — famous consumer brands
   (Apple, Amazon, Nintendo, Toyota, Uniqlo, Starbucks…), Japanese companies or the Japanese economy, or the week's biggest
   headline in Japanese media (check Japanese news rankings). Avoid obscure B2B names unless the angle is famous.
   **Saturday** is the listening compilation: run `python engine/build.py compile-week <saturday-date>`, then polish the
   draft (hook, title, 2 quiz shorts on the most useful phrases) instead of writing a 3-phrase review.
4. Write each episode per `docs/FORMAT.md`. Quality rules:
   - Facts only from sources you opened. No speculation stated as fact; attribute forecasts ("〜と予測しています").
   - `en` subtitles are your own English, not copied article text. Quote executives only briefly and attribute them.
   - No investment advice, no buy/sell suggestions, no claims about where a stock will go.
   - The "私たちへの意味" scene must contain a genuinely specific angle for people working in Japan, and a counter-view.
   - Vary the visuals: each episode should use at least 5 different templates, and don't open two days in a row with the same template.
   - Phrases must be genuinely useful in meetings/email, at B1–B2 level, and each example sentence must be a realistic Japanese workplace line.
   - Long video title: search-first pattern `「<phrase jp>」は英語で?<phrase en>の使い方|<news ≤20 chars>【ビジネス英語ニュース #NN】`.
   - Each episode also becomes a 5-slide Instagram carousel automatically (engine/carousel.py); keep phrases/examples short enough to fit.
   - Shorts (PDCA H2 A/B): `shorts[0]` is news-first (`style` omitted); `shorts[1]` is phrase-first with `"style": "quiz"`,
     `"badge": "会議で使う英語|中級"` (level: 初級/中級/上級) and a short title `「<phrase en>」の意味、わかる?|会議の英語 #shorts`.
   - Shorts: `news_hook` is the 2-line headline shown on frame 0; `hook` is 2 short lines that make people want the answer; `ig_caption` follows the #01 style
     (question → ✅ phrase → meaning → example → one line of context → 📌 保存 → ▼ YouTube → 7 hashtags).
5. Run `python engine/build.py validate episodes/<id>` for each and **look at** `out/preview_sheet.png` and `out/thumbnail.png`.
   Fix overflowing text, empty-looking frames and awkward line breaks before pushing.
6. Commit all 7 folders in one commit and push to `main`. Commit trailer lines:
   `Co-Authored-By: Claude <noreply@anthropic.com>` and `Claude-Session: <this session's URL>`.
7. Watch the "Build & schedule" workflow run (`gh run list --workflow build.yml`, `gh run view <id> --log-failed`).
   If it fails, read the log, fix, push again (already-uploaded videos are skipped via `state/published.json`).
8. Report to the owner with SendUserMessage in Japanese (always Japanese): a 3-line PDCA summary (what the numbers said,
   what you changed), then the 7 titles with publish times and YouTube Studio links,
   anything you were unsure about, and anything that needs their action.

## Hot topics: publish now (速報, owner rule 2026-11-07)

A hot story is published **immediately**, not scheduled. A daily Claude task (「BEB 速報チェック」, every day 18:37 JST)
checks for one; the Saturday weekly task applies the same rule while researching.

1. **Is it hot?** All of these must be true:
   - it broke in the last ~24 hours and is at or near the top of Japanese news rankings today
     (Yahoo!ニュース 経済・国内のランキング, NHK, 日経のトップ), or it is the day's biggest global business headline;
   - Japanese viewers already know the company/topic (reach rule H1), and it gives at least one genuinely useful meeting phrase;
   - it is not already covered or scheduled in `episodes/` (check titles and `sources` of the last 7 and next 7 days);
   - it is not a disaster, accident, crime or death story with victims (we don't build lessons on tragedy).
   If nothing qualifies: do nothing — no commit, no notification. When in doubt, it is not hot.
2. **Limits:** at most 1 hot episode per day and 3 per week. Scheduled episodes stay as they are (hot ones are extra;
   never delete or reschedule a scheduled video).
3. **Make it** like a Weekly Brief episode (all quality rules above apply; 3–5 min is fine), with:
   - `series`: `"速報"`, `episode`: next number after the highest in `episodes/`, `id`: `<today>-<slug>`, `date`: the news date;
   - `publish.long` and `publish.shorts[0]`: the current JST time (`YYYY-MM-DDTHH:MM:00+09:00`, not in the future) →
     the engine uploads them as **public now** and queues the reel immediately; `publish.shorts[1]`: +3 hours
     (the H2 quiz short);
   - `thumbnail.badge`: `"速報"` (badge_color `red`); title follows the normal search-first pattern.
4. Validate, look at the preview sheet and thumbnail, commit only that folder, push, and watch "Build & schedule" to the end
   (one episode takes ~20–30 min). The Saturday compilation picks up hot episodes' phrases automatically.
5. Notify the owner (PushNotification, Japanese): the title, why it was hot, the YouTube link.

## Things that need the owner (never do these yourself)

Creating accounts, entering passwords or tokens, changing GitHub secrets, accepting new terms, spending money.
If a token expired (YouTube 400 invalid_grant, Instagram code 190), stop and ask the owner to re-issue it.
