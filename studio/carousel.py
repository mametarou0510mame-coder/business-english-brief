"""Render the Instagram carousel (1080x1350 JPEGs) for a studio episode from episode.json["carousel"].

usage: python studio/carousel.py studio/episodes/<slug>/episode.json <out_dir>"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ep = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto("file://" + os.path.join(HERE, "carousel.html"))
        pg.evaluate("document.fonts.ready")
        n = pg.evaluate("c => build(c)", ep["carousel"])
        for i in range(1, n + 1):
            pg.locator(f"#s{i}").screenshot(path=os.path.join(out, f"c{i}.jpg"), type="jpeg", quality=92)
        br.close()
    print(n, "slides ->", out)


if __name__ == "__main__":
    main()
