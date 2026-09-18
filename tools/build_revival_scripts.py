#!/usr/bin/env python3
"""Season 10 and 11 script pages (Google Drive view links, same layout as Seasons 1–9).

The PDFs live in the Boggsfiles Google Drive with "anyone with the link" viewing and downloading
disabled. Card photos are screencap frames (kept distinct from the transcript still and the
screencap cover for the same episode). Run: python3 tools/build_revival_scripts.py
"""
from __future__ import annotations
import html, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from transcript_header import ASSETS, site_header
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]; DIST = ROOT / "dist"
CAPS = Path.home() / "Movies/XF_screencaps/series"
D = "https://drive.google.com/file/d/{}/view?usp=sharing"

SEASONS = {
    10: ("Season 10", "2016", "/x-files-scripts-by-season/season-9/", "Season 9", "/x-files-scripts-by-season/season-11/", "Season 11", [
        ("My Struggle", "1AYW01", "10X01", [("Green Rev", "1jm7TkYbWFLOozkp-fsQq6HdLce6jdMMg")]),
        ("Founder's Mutation", "1AYW05", "10X02", [("Green", "1sWrNwP6Rw_a3t9Ab2M0ZXkfya-UmwMfY")]),
        ("Mulder & Scully Meet the Were-Monster", "1AYW03", "10X03", [("Blue", "1vwDjQ3fkFvHVu7-nBy0BUn_lb_CPPxto")]),
        ("Home Again", "1AYW02", "10X04", [("Pink", "1xk0FDwtn0w4QUvEetvNZQSzNgp533sR3")]),
        ("Babylon", "1AYW04", "10X05", [("Goldenrod", "1UxLalkpdOidV7Y_q6erSOa3y7DbyB7MZ")]),
        ("My Struggle II", "1AYW06", "10X06", [("Pink", "1tneiRt-0heWWxfxTxd56rDDONnEUM0uq")]),
        ("Unproduced Season 10 Script", "", None, [("Chris Carter's on-set copy", "108gSzD3pmJr6l_narzX2fJkvFYYXvskC")]),
    ]),
    11: ("Season 11", "2018", "/x-files-scripts-by-season/season-10/", "Season 10", None, None, [
        ("My Struggle III", "2AYW01", "11X01", [("White Production Draft", "1NS0m7n582kPeW7Uo9rYh9EkL6ndwbOcL")]),
        ("This", "2AYW02", "11X02", [("Writer's Draft", "1AQOwAytAPLcd4W_qCUGz9zY8yMcT1SI5"), ("Production Draft", "1idJ2dRpdBmzU0kGR_XeXgNJ_jUU2hkHQ")]),
        ("Plus One", "2AYW03", "11X03", [("Production Draft", "19QNW7NmYgx8XJ-Gxq0bnYFcYy53zXEWg")]),
        ("The Lost Art of Forehead Sweat", "2AYW04", "11X04", [("Writer's Draft", "1WntKE9ZefQ9JO5w5KzPAK7wA3Dc39iUC")]),
        ("Ghouli", "2AYW05", "11X05", [("Blue", "1jSSFdm29yAzEGwwNbK79E1huPxw3D-GD"), ("Green Collated", "1OEyS4wUQ-AxTfeb_9QtB3WuzIcUYIPUf")]),
        ("Kitten", "2AYW06", "11X06", [("Green", "1c2p4nldozTAggO6HzO3tSuVepmVGurcx")]),
        ("Rm9sbG93ZXJz", "2AYW07", "11X07", [("Green", "1yyl_SogwKX8ya1wkWjoIcCYK8JQRcVwD")]),
        ("Nothing Lasts Forever", "2AYW08", "11X09", [("Goldenrod", "107xCWxYj19VDZPnYCUxUKLHEE44kCwp1")]),
        ("Familiar", "2AYW09", "11X08", [("Yellow", "1sCCw_r-w23FbPfJD8M6Fy26C3i2NS5AO")]),
        ("My Struggle IV", "2AYW10", "11X10", [("Production Draft · signed by Chris Carter", "1rXTiH-zUdmRiIaOIQXw6Bo5CBXViq0yi")]),
    ]),
}

def card_photo(season: int, n: int, code: str | None) -> str:
    """756×756 webp from the episode's screencaps (frame at ~1/3, Mulder or Scully tagged); falls back to the season image."""
    dest = DIST / "assets/archive-photos" / f"scripts-season-{season}-{n:02d}.webp"
    if dest.exists(): return f"/assets/archive-photos/{dest.name}"
    ep = next((p for p in (CAPS / f"S{season}").glob(f"{code} *")), None) if code else None
    if ep and (ep / "index.json").exists():
        idx = json.load(open(ep / "index.json")); fr = sorted(f for f, t in idx.items() if {"Mulder", "Scully"} & set(t)) or sorted(idx)
        f = fr[len(fr) // 3]; im = Image.open(ep / "full" / f).convert("RGB")
        w, h = im.size; s = min(w, h); im = im.crop(((w - s) // 2, 0, (w - s) // 2 + s, s)).resize((756, 756), Image.LANCZOS)
        im.save(dest, "WEBP", quality=82); return f"/assets/archive-photos/{dest.name}"
    return f"/assets/transcript-stills/{'my-struggle' if season == 10 else 'my-struggle-iii'}.jpg"

def page(season: int) -> str:
    title, year, prev_href, prev_label, next_href, next_label, eps = SEASONS[season]
    arts = []
    for n, (name, prod, code, drafts) in enumerate(eps, 1):
        links = "".join(f'<a class="draft" href="{D.format(fid)}" target="_blank" rel="noopener">{html.escape(label)} ↗</a>' for label, fid in drafts)
        head = f"{html.escape(name)} {prod}".strip()
        arts.append(f'<article class="episode"><div class="episode-image" style="background-image:url(\'{card_photo(season, n, code)}\')"></div><div class="episode-body"><span class="episode-no">File {n:02d}</span><h2>{head}</h2><div class="drafts">{links}</div></div></article>')
    def link(cls, href, label, arrow):
        if not href: return ""
        inner = f'<span aria-hidden="true">{arrow}</span><b>{label}</b>' if cls == "season-prev" else f'<b>{label}</b><span aria-hidden="true">{arrow}</span>'
        return f'<a class="season-link {cls}" href="{href}" aria-label="Go to {label}">{inner}</a>'
    nav = link("season-prev", prev_href, prev_label, "←") + link("season-next", next_href, next_label, "→")
    n_files = sum(len(d) for *_, d in eps)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} - Boggsfiles</title>'
            f'<meta name="description" content="Browse {title} in the Boggsfiles X-Files archive."><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Libre+Caslon+Display&family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet"><link rel="stylesheet" href="/assets/archive-detail.css?v=3">{ASSETS}</head>'
            f'<body>{site_header("Scripts")}<main><section class="archive-hero"><div class="shell"><div class="crumb"><a href="/scripts/">Scripts</a> &nbsp;/&nbsp; {title}</div><h1>{title}</h1>'
            f'<p>Production drafts and collated revisions from the {year} revival, preserved for close reading and comparison.</p><div class="archive-meta"><span>{n_files} script files</span><span>Original scans</span><span>Opens in Google Drive</span></div></div></section>'
            f'<div class="shell"><div class="archive-grid">{"".join(arts)}</div></div><nav class="season-rail" aria-label="Season navigation">{nav}</nav><nav class="season-nav-bottom" aria-label="Season navigation">{nav}</nav></main>'
            f'<footer><div class="shell footer-row">BOGGSFILES · THE X-FILES ARCHIVE <span><a href="/">Home</a> · <a href="/scripts/">Back to Scripts</a></span></div></footer></body></html>')

def main():
    for season in (10, 11):
        out = DIST / f"x-files-scripts-by-season/season-{season}/index.html"; out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(season), encoding="utf-8"); print("built", out)
    # Scripts landing: two new season cards after I Want to Believe; Season 9 gets a "next" link
    p = DIST / "scripts/index.html"; s = p.read_text()
    if 'data-season="10"' not in s:
        cards = ('<a class="season" data-season="10" href="/x-files-scripts-by-season/season-10"><span class="meta">SEASON 10 · 2016</span><h2>Season Ten</h2><span class="open">Open case files →</span></a>'
                 '<a class="season" data-season="11" href="/x-files-scripts-by-season/season-11"><span class="meta">SEASON 11 · 2018</span><h2>Season Eleven</h2><span class="open">Open case files →</span></a>')
        s = s.replace('<span class="open">Open case files →</span></a></div><section class="special">', '<span class="open">Open case files →</span></a>' + cards + '</div><section class="special">', 1)
        p.write_text(s); print("landing updated")
    p = DIST / "x-files-scripts-by-season/season-9/index.html"; s = p.read_text()
    if "season-10" not in s:
        nxt = '<a class="season-link season-next" href="/x-files-scripts-by-season/season-10/" aria-label="Go to Season 10"><b>Season 10</b><span aria-hidden="true">→</span></a>'
        s = s.replace('<b>Season 8</b></a></nav>', '<b>Season 8</b></a>' + nxt + '</nav>')
        p.write_text(s); print("season 9 nav updated")

if __name__ == "__main__":
    main()
