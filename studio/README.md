# BEB studio (new format, 2026-11)

English narration, EN + JP subtitles in one band, theme A (light, editorial).
Scenes are HTML/SVG components (`scenes.js`) driven by a deterministic timeline (`engine.js`);
`render.py` films them frame by frame with headless Chromium and muxes Azure narration.

- Preview stills (no narration needed): `python studio/render.py studio/episodes/<slug>/<name>.json --stills 1.5,6,12`
- Full render with voice: GitHub Actions → "Studio render" (needs AZURE_SPEECH_KEY); output on branch `studio-media`.
