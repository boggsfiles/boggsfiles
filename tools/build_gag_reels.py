#!/usr/bin/env python3
"""Build the Gag Reels landing page and the per-season detail pages.

Same pattern as build_dailies.py: the .mp4 files live in the PRIVATE R2 bucket (boggsfiles-private)
under gag-reels/, and the page asks the boggsfiles-dailies Worker (worker/src/index.js) for a signed
link that expires after a few hours, so the raw bucket URL is never exposed.

Add a season to LIVE once its file is on R2. Everything not in LIVE renders as "Coming soon".
Run:  python3 tools/build_gag_reels.py   (then commit + ./publish.sh)
"""
from __future__ import annotations
import html, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from transcript_header import ASSETS, site_header

DIST = Path(__file__).resolve().parents[1] / "dist"
WORKER = "https://boggsfiles-dailies.boggsfiles.workers.dev"
MEDIA_PREFIX = "gag-reels/"
POSTER_BASE = "https://pub-df226d4134944457905024edfc4635fb.r2.dev/gag-reel-posters/"

LOADER = ('<script>(function(){var W=' + repr(WORKER) + ';'
          'function sign(v,resume){fetch(W+"/sign?key="+encodeURIComponent(v.dataset.key)).then(function(r){if(!r.ok)throw r.status;return r.json()})'
          '.then(function(j){var t=v.currentTime,play=!v.paused;v.src=j.url;if(resume){v.currentTime=t;if(play)v.play()}})'
          '.catch(function(){v.closest(".media").insertAdjacentHTML("beforeend","<p class=media-caption>Video unavailable right now, please try again later.</p>")})}'
          'document.querySelectorAll("video[data-key]").forEach(function(v){sign(v,false);var retried=false;'
          'v.addEventListener("error",function(){if(!retried&&v.src){retried=true;sign(v,true)}})})})();</script>')

# slug -> (card title, years, r2 filename inside gag-reels/)
REELS = {
    "season-1":        ("Season 1", "1993–94", "Gag Reel - Season 1.mp4"),
    "season-2":        ("Season 2", "1994–95", "Gag Reel - Season 2.mp4"),
    "season-3":        ("Season 3", "1995–96", "Gag Reel - Season 3.mp4"),
    "season-4":        ("Season 4", "1996–97", "Gag Reel - Season 4.mp4"),
    "season-5":        ("Season 5", "1997–98", "Gag Reel - Season 5.mp4"),
    "season-6":        ("Season 6", "1998–99", "Gag Reel - Season 6.mp4"),
    "season-7":        ("Season 7", "1999–2000", "Gag Reel - Season 7.mp4"),
    "season-8":        ("Season 8", "2000–01", "Gag Reel - Season 8.mp4"),
    "season-9":        ("Season 9", "2001–02", "Gag Reel - Season 9 (with Chris Carter tribute).mp4"),
    "fight-the-future": ("Fight the Future", "1998", "Gag Reel - Fight the Future.mp4"),
}
MARKS = {"season-1": "1", "season-2": "2", "season-3": "3", "season-4": "4", "season-5": "5",
         "season-6": "6", "season-7": "7", "season-8": "8", "season-9": "9", "fight-the-future": "F"}

LIVE = ["season-1"]

INTRO = ("A gag reel is the blooper tape the crew cuts together for the wrap party at the end of a season. "
         "Flubbed lines, broken takes, corpsing, and the running jokes that only make sense if you were on that set. "
         "These are the full reels, from the DVD masters rather than a tape dub of a tape dub.")

def page(title: str, body: str) -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)} - Boggsfiles</title><meta name="description" content="Watch the {html.escape(title)} in the Boggsfiles X-Files archive.">'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Libre+Caslon+Display&family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet">'
            f'<link rel="stylesheet" href="/assets/archive-detail.css?v=3">{ASSETS}</head><body>{site_header("Gag Reels")}<main>{body}</main>'
            f'<footer><div class="shell footer-row">BOGGSFILES &middot; GAG REELS <span><a href="/">Home</a> &middot; <a href="/gag-reels/">Back to Gag Reels</a></span></div></footer></body></html>')

def write_route(route: str, content: str) -> None:
    dest = DIST / route.strip("/") / "index.html"; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_text(content, encoding="utf-8")

def r2_meta() -> dict[str, int]:
    out = subprocess.run(["rclone", "lsl", "r2:boggsfiles-private/gag-reels/"], capture_output=True, text=True, check=True).stdout
    sizes = {}
    for line in out.splitlines():
        parts = line.split(None, 3)
        if len(parts) == 4: sizes[parts[3]] = int(parts[0])
    return sizes

def duration(key: str) -> str | None:
    src = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels" / key
    if not src.exists(): return None
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                         capture_output=True, text=True)
    if out.returncode: return None
    secs = int(float(out.stdout.strip()))
    return f"{secs // 60}:{secs % 60:02d}"

def fmt_size(n: int) -> str:
    return f"{n / 1e9:.1f} GB" if n >= 1e9 else f"{n / 1e6:.0f} MB"

def detail(slug: str, sizes: dict[str, int]) -> None:
    title, years, key = REELS[slug]
    full = f"The {title} Gag Reel" if slug != "fight-the-future" else "The Fight the Future Gag Reel"
    dur, size = duration(key), sizes.get(key)
    meta = [m for m in (dur, fmt_size(size) if size else None, "From the DVD master") if m]
    player = (f'<div class="media"><video controls controlsList="nodownload noremoteplayback" disablePictureInPicture '
              f'style="object-fit:fill" '   # capture says SAR 1:1 (3:2); the DVD content is 4:3, so squeeze it back

              f'oncontextmenu="return false" preload="metadata" playsinline poster="{POSTER_BASE}{slug}.jpg" '
              f'data-key="{html.escape(MEDIA_PREFIX + key, quote=True)}" title="{html.escape(full)}"></video>'
              f'<div class="media-caption"><span>{html.escape(title)} gag reel</span><span>{html.escape(" · ".join(m for m in (dur, fmt_size(size) if size else "") if m))}</span></div></div>')
    body = (f'<section class="archive-hero"><div class="shell"><div class="crumb"><a href="/gag-reels/">Gag Reels</a> &nbsp;/&nbsp; {html.escape(title)}</div>'
            f'<h1>{html.escape(title)}</h1><p>{html.escape(years)} &middot; the full wrap-party reel, from the DVD master.</p>'
            f'<div class="archive-meta">{"".join(f"<span>{html.escape(m)}</span>" for m in meta)}</div></div></section>'
            f'<div class="shell detail-wrap"><p class="detail-copy">{html.escape(INTRO)}</p><div class="media-grid" style="--card-columns:1;grid-template-columns:1fr">{player}</div></div>{LOADER}')
    write_route(f"gag-reels/{slug}", page(f"{title} Gag Reel", body))
    print(f"Built gag reel page: {title}" + (f" ({dur})" if dur else ""), flush=True)

def landing() -> None:
    cards = []
    for slug, (title, years, _key) in REELS.items():
        mark = MARKS[slug]
        if slug in LIVE:
            cards.append(f'<a class="file" data-mark="{mark}" href="/gag-reels/{slug}/"><span class="meta">Gag reel</span>'
                         f'<h2>{html.escape(title)}</h2><p>{html.escape(years)} &middot; From the DVD master</p>'
                         f'<span class="open">Watch the reel &rarr;</span></a>')
        else:
            cards.append(f'<div class="file file-soon" data-mark="{mark}"><span class="meta">Gag reel</span>'
                         f'<h2>{html.escape(title)}</h2><p>{html.escape(years)} &middot; From the DVD master</p>'
                         f'<span class="open soon">Coming soon</span></div>')
    n = len(LIVE)
    live_line = ("Season 1 is up now. The rest are being prepared and will be posted here as they are ready."
                 if n == 1 else f"{n} reels are up now. The rest are being prepared and will be posted here as they are ready.")
    body = (f'<section class="hero"><div class="shell"><div class="crumb"><a href="/archive/">Archive</a> &nbsp;/&nbsp; Gag Reels</div>'
            f'<h1>Gag Reels</h1><p>Flubs, cracked takes, and the moments the cast couldn’t keep a straight face, preserved from the DVD masters rather than a tape dub of a tape dub.</p>'
            f'<div class="summary"><div class="stat"><b>{len(REELS)}</b><span>Reels</span></div>'
            f'<div class="stat"><b>1–9</b><span>Seasons + Fight the Future</span></div>'
            f'<div class="stat"><b>{n}</b><span>Watch now</span></div></div></div></section>'
            f'<section class="intro"><div class="shell intro-grid"><div><div class="eyebrow">Now playing</div>'
            f'<h2>Ones you can actually see</h2></div><p>Every gag reel from the Season 1–9 DVD sets and the Fight the Future disc, '
            f'captured directly from the discs at full DVD resolution. {live_line}</p></div></section>'
            f'<div class="shell"><div class="collection dailies-grid">{"".join(cards)}</div>'
            f'<div class="notice"><strong>Have a reel we’re missing?</strong><p>Help expand the archive. Contributions can remain anonymous.</p>'
            f'<a class="button" href="/contribute/">Share evidence &rarr;</a></div></div>')
    doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>Gag Reels: Boggsfiles</title>'
           f'<meta name="description" content="X-Files gag reels for Seasons 1–9 and Fight the Future, preserved from the DVD masters. Season 1 is streaming now.">'
           f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
           f'<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Libre+Caslon+Display&family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet">'
           f'<link rel="stylesheet" href="/assets/collection.css">{ASSETS}</head><body>{site_header("Gag Reels")}<main>{body}</main>'
           f'<footer><div class="shell footer-row">BOGGSFILES &middot; GAG REELS <span><a href="/">Home</a></span></div></footer></body></html>')
    write_route("gag-reels", doc)
    print(f"Built gag reels landing ({n} live)", flush=True)

def main() -> None:
    sizes = r2_meta()
    missing = [REELS[s][2] for s in LIVE if REELS[s][2] not in sizes]
    if missing: raise SystemExit("MISSING on R2 under gag-reels/: " + "; ".join(missing))
    for slug in LIVE: detail(slug, sizes)
    landing()

if __name__ == "__main__":
    main()
