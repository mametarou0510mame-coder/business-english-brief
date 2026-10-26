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
   | Sat | 今週の英単語 総復習 | evergreen: revisit 3 of the week's most useful phrases with new example situations (news-light) |
   | Sun | 場面別の英語 | evergreen: a meeting/email situation (disagreeing politely, asking for deadlines…) tied to a recent story |

   Prefer stories that stay relevant for a week (structural moves, not hour-by-hour market moves).
4. Write each episode per `docs/FORMAT.md`. Quality rules:
   - Facts only from sources you opened. No speculation stated as fact; attribute forecasts ("〜と予測しています").
   - `en` subtitles are your own English, not copied article text. Quote executives only briefly and attribute them.
   - No investment advice, no buy/sell suggestions, no claims about where a stock will go.
   - The "私たちへの意味" scene must contain a genuinely specific angle for people working in Japan, and a counter-view.
   - Vary the visuals: each episode should use at least 5 different templates, and don't open two days in a row with the same template.
   - Phrases must be genuinely useful in meetings/email, at B1–B2 level, and each example sentence must be a realistic Japanese workplace line.
   - Long video title: search-first pattern `「<phrase jp>」は英語で?<phrase en>の使い方|<news ≤20 chars>【ビジネス英語ニュース #NN】`.
   - Each episode also becomes a 5-slide Instagram carousel automatically (engine/carousel.py); keep phrases/examples short enough to fit.
   - Shorts: `news_hook` is the 2-line headline shown on frame 0; `hook` is 2 short lines that make people want the answer; `ig_caption` follows the #01 style
     (question → ✅ phrase → meaning → example → one line of context → 📌 保存 → ▼ YouTube → 7 hashtags).
5. Run `python engine/build.py validate episodes/<id>` for each and **look at** `out/preview_sheet.png` and `out/thumbnail.png`.
   Fix overflowing text, empty-looking frames and awkward line breaks before pushing.
6. Commit all 7 folders in one commit and push to `main`. Commit trailer lines:
   `Co-Authored-By: Claude <noreply@anthropic.com>` and `Claude-Session: <this session's URL>`.
7. Watch the "Build & schedule" workflow run (`gh run list --workflow build.yml`, `gh run view <id> --log-failed`).
   If it fails, read the log, fix, push again (already-uploaded videos are skipped via `state/published.json`).
8. Report to the owner with SendUserMessage in Japanese: the 7 titles with publish times and YouTube Studio links,
   anything you were unsure about, and anything that needs their action.

## Things that need the owner (never do these yourself)

Creating accounts, entering passwords or tokens, changing GitHub secrets, accepting new terms, spending money.
If a token expired (YouTube 400 invalid_grant, Instagram code 190), stop and ask the owner to re-issue it.
