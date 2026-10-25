# Business English Brief

世界のビジネスニュースで、明日の会議の英語を。

- YouTube: https://www.youtube.com/@bizenglishbrief
- Instagram: https://www.instagram.com/businessenglishbrief/

This repository builds and schedules the channel's videos automatically. See `CLAUDE.md` for how it works
and `docs/FORMAT.md` for the episode format.

## Secrets (Settings → Secrets and variables → Actions)

`YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`, `IG_USER_ID`, `IG_TOKEN`, `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`

Run **Actions → Check accounts** after changing any of them: it shows which YouTube channel and Instagram account
the secrets belong to, without uploading anything.

## Local use

```
sudo apt-get install ffmpeg fonts-inter fonts-noto-cjk fonts-noto-cjk-extra && pip install pillow
python engine/build.py validate episodes/<id>
AZURE_SPEECH_KEY=... python engine/build.py render episodes/<id>
```
