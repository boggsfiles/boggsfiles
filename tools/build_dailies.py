#!/usr/bin/env python3
"""Build the Dailies detail pages with native <video> players served from Cloudflare R2.

Replaces the Sprout Video embeds. Files live in the R2 bucket under dailies/<episode folder>/…;
DAILIES maps each page to its R2 keys in viewing order. Captions come from the file names.
Run:  python3 tools/build_dailies.py   (then commit + ./publish.sh)
"""
from __future__ import annotations
import html, re, subprocess, sys, urllib.parse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from transcript_header import ASSETS, site_header

DIST = Path(__file__).resolve().parents[1] / "dist"

def page(title: str, body: str, active: str) -> str:   # same shell as build_archive_pages.page (that module needs lxml)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)} - Boggsfiles</title><meta name="description" content="Browse {html.escape(title)} in the Boggsfiles X-Files archive.">'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Libre+Caslon+Display&family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet">'
            f'<link rel="stylesheet" href="/assets/archive-detail.css?v=3">{ASSETS}</head><body>{site_header(active)}<main>{body}</main>'
            f'<footer><div class="shell footer-row">BOGGSFILES · THE X-FILES ARCHIVE <span><a href="/">Home</a> · <a href="/{active.lower()}/">Back to {html.escape(active)}</a></span></div></footer></body></html>')

def write_route(route: str, content: str) -> None:
    dest = DIST / route.strip("/") / "index.html"; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_text(content, encoding="utf-8")

MEDIA_BASE = "https://pub-df226d4134944457905024edfc4635fb.r2.dev/dailies/"
POSTER_BASE = "https://pub-df226d4134944457905024edfc4635fb.r2.dev/dailies-posters/"   # <slug>-<nn>.jpg, one frame ~45 s into each file
INTRO = ("Dailies are the raw, unedited footage recorded during a day of filming. They often include slates, repeated takes, "
         "alternate performances, and material that never appears in the finished episode. The production team reviewed them "
         "to evaluate performances, coverage, focus, sound, and continuity before the episode was edited.")

# slug -> (title, [(caption, r2 key), ...]) — order is viewing order
DAILIES = {
    "deep-throat": ("Deep Throat", [("Reel 1", "Deep Throat/DEEP THROAT DAILIES 1.mp4"), ("Reel 2", "Deep Throat/DEEP THROAT DAILIES 2.mp4")]),
    "born-again": ("Born Again", [("Dailies", "Born Again/Born Again Dailies.mp4")]),
    "ascension": ("Ascension", [(f"Reel {n}", f"Ascension Dailies/Ascension Dailie {n}.mp4") for n in range(1, 6)]),
    "aubrey": ("Aubrey", [("Reel 1", "Aubrey Dailies/Aubrey Dailie 1.mp4")] + [(f"Reel {n}", f"Aubrey Dailies/Aubrey dailie {n}.mp4") for n in range(2, 6)]),
    "irresistible": ("Irresistible", [("2X13 dailies", "Irresistable/_XF 2X13 IRRESISTIBLE DAILIES.mp4")]),
    "die-hand-die-verletzt": ("Die Hand Die Verletzt", [("Dailies", "Die Hand/Die Hand Dailies.mp4")]),
    "apocrypha": ("Apocrypha", [("Dailies", "Apocrypha/Apocrypha.mp4")]),
    "quagmire": ("Quagmire", [("3X22 dailies · reel 1", "Quagmire/XF 3X22 QUAGMIRE _1 DAILIES.mp4"), ("Reel 2", "Quagmire/Quagmire 2.mp4")]),
    "the-field-where-i-died": ("The Field Where I Died", [
        ("Part 1 · Gillian Anderson", "The Field Where I Died/The field where I died (GA) - part 1.mp4"),
        ("Part 2 · Gillian Anderson, David Duchovny & Kristen Cloke", "The Field Where I Died/The field where I died (GA, DD & KC) - part 2.mp4"),
        ("Part 3 · Gillian Anderson, David Duchovny & Mitch Pileggi", "The Field Where I Died/The field where I died (GA, DD & MP) - part 3.mp4"),
        ("Part 4 · Gillian Anderson, David Duchovny & Mitch Pileggi", "The Field Where I Died/The field where I died (GA, DD & MP) - part 4.mp4"),
        ("2nd unit · part 1", "The Field Where I Died/The field where I died 2nd unit - part 1.mp4"),
        ("2nd unit · part 2", "The Field Where I Died/The field where I died 2nd unit - part 2.mp4"),
        ("2nd unit · part 3", "The Field Where I Died/The field where I died 2nd unit - part 3.mp4")]),
    "sanguinarium": ("Sanguinarium", [
        ("Part 1 · Richard Beymer", "Sanguinarium Dailies/Sanguinarium (Richard Beymer) - part 1.mp4"),
        ("Part 2 · David Duchovny & Gillian Anderson", "Sanguinarium Dailies/Sanguinarium (DD & GA) - part 2.mp4"),
        ("Reel 3", "Sanguinarium Dailies/sanguinarium~1 DONE.mp4"),
        ("Reel 4", "Sanguinarium Dailies/sanguinarium (2)~1 DONE.mp4"),
        ("Reel 5", "Sanguinarium Dailies/sanguinarium (3)~1 DONE.mp4"),
        ("Reel 6", "Sanguinarium Dailies/sanguinarium 8~1 DONE.mp4"),
        ("Reel 7", "Sanguinarium Dailies/sanguinarium 10~1 DONE.mp4"),
        ("Field reel", "Sanguinarium Dailies/sanguinarium-field~1 DONE.mp4"),
        ("2nd unit · part 1", "Sanguinarium Dailies/Sanguinarium 2nd unit - part 1.mp4")]),
    "musings-of-a-cigarette-smoking-man": ("Musings of a Cigarette Smoking Man", [
        ("Part 1 · William B. Davis", "Musings of a CSM/Musings of a CSM (WBD) - part 1.mp4"),
        ("Reel 2", "Musings of a CSM/musings~1.mp4"), ("Reel 3", "Musings of a CSM/musings (2)~1.mp4"),
        ("Reel 4", "Musings of a CSM/musings (3)~1.mp4"), ("Reel 5", "Musings of a CSM/musings (4)~1.mp4"),
        ("Reel 6", "Musings of a CSM/musings (5)~1.mp4")]),
    "tunguska": ("Tunguska", [
        ("Part 1 · Mitch Pileggi & William B. Davis", "Tunguska Dailies/Tunguska (MP & WBD) - part 1.mp4"),
        ("Part 2 · David Duchovny & Nicholas Lea", "Tunguska Dailies/Tunguska (DD & NL) - part 2.mp4"),
        ("Part 3 · William B. Davis & John Neville", "Tunguska Dailies/Tunguska (WBD & JN) - part 3.mp4"),
        ("Part 4 · David Duchovny & Nicholas Lea", "Tunguska Dailies/Tunguska (DD & NL) - part 4.mp4"),
        ("Part 5 · David Duchovny, Nicholas Lea & Mitch Pileggi", "Tunguska Dailies/Tunguska (DD, NL & MP) - part 5.mp4"),
        ("Part 6 · David Duchovny", "Tunguska Dailies/Tunguska (DD) - part 6.mp4"),
        ("2nd unit · part 1", "Tunguska Dailies/Tunguska 2nd unit - part 1.mp4")]),
    "paper-hearts": ("Paper Hearts", [
        ("Part 1 · David Duchovny & Gillian Anderson", "Paper Hearts Dailies/Paper Hearts (DD & GA) - part 1.mp4"),
        ("Part 2 · David Duchovny & Rebecca Toolan", "Paper Hearts Dailies/Paper Hearts (DD & Rebecca Toolan) - part 2.mp4"),
        ("Part 3 · David Duchovny & Tom Noonan", "Paper Hearts Dailies/Paper Hearts (DD & Tom Noonan) - part 3.mp4"),
        ("Part 4 · Tom Noonan", "Paper Hearts Dailies/Paper Hearts (Tom Noonan) - part 4.mp4"),
        ("Part 5 · David Duchovny, Gillian Anderson & Byrne Piven", "Paper Hearts Dailies/Paper Hearts (DD, GA & Byrne Piven) - part 5.mp4"),
        ("Part 6 · David Duchovny, Gillian Anderson & Mitch Pileggi", "Paper Hearts Dailies/Paper Hearts (DD, GA & MP) - part 6.mp4"),
        ("Part 7 · David Duchovny & Gillian Anderson", "Paper Hearts Dailies/Paper Hearts (DD & GA) - part 7.mp4"),
        ("Part 8 · David Duchovny & Vanessa Morley", "Paper Hearts Dailies/Paper Hearts (DD & Vanessa Morley) - part 8.mp4"),
        ("Part 9 · David Duchovny & Gillian Anderson", "Paper Hearts Dailies/Paper Hearts (DD & GA) - part 9.mp4"),
        ("Part 10 · David Duchovny, Tom Noonan & Vanessa Morley", "Paper Hearts Dailies/Paper Hearts (DD, TN, VM) - part 10.mp4"),
        ("Part 11 · David Duchovny, Tom Noonan & Vanessa Morley", "Paper Hearts Dailies/Paper Hearts (DD, TN, VM) - part 11.mp4"),
        ("Part 12 · David Duchovny, Gillian Anderson, Mitch Pileggi & Tom Noonan", "Paper Hearts Dailies/Paper Hearts (DD, GA, MP, TN) - part 12.mp4"),
        ("2nd unit · part 1", "Paper Hearts Dailies/Paper Hearts 2nd unit - part 1.mp4"),
        ("2nd unit · part 2", "Paper Hearts Dailies/Paper Hearts 2nd unit - part 2.mp4"),
        ("2nd unit · part 3", "Paper Hearts Dailies/Paper Hearts 2nd unit - part 3.mp4"),
        ("4X08 full dailies reel", "Paper Hearts Dailies/_4X08 PAPER HEARTS DAILIES.mp4")]),
    "kitsunegari": ("Kitsunegari", [("Dailies", "Kitsunegari/Kitsunegari Dailies.mp4")]),
}

def r2_sizes() -> dict[str, int]:
    out = subprocess.run(["rclone", "lsl", "r2:boggsfiles-media/dailies/"], capture_output=True, text=True, check=True).stdout
    sizes = {}
    for line in out.splitlines():
        parts = line.split(None, 3)
        if len(parts) == 4: sizes[parts[3]] = int(parts[0])
    return sizes

def fmt_size(n: int) -> str:
    return f"{n / 1e9:.1f} GB" if n >= 1e9 else f"{n / 1e6:.0f} MB"

def main() -> None:
    sizes = r2_sizes(); missing = []
    for slug, (title, items) in DAILIES.items():
        media = []
        for i, (caption, key) in enumerate(items, 1):
            if key not in sizes: missing.append(key); continue
            url = MEDIA_BASE + urllib.parse.quote(key)
            media.append(f'<div class="media"><video controls preload="metadata" playsinline poster="{POSTER_BASE}{slug}-{i:02d}.jpg" src="{html.escape(url, quote=True)}" title="{html.escape(title)} — {html.escape(caption)}"></video>'
                         f'<div class="media-caption"><span>{i:02d} · {html.escape(caption)}</span><a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">{fmt_size(sizes[key])} ↗</a></div></div>')
        n = len(media); count = f"{n} video file" + ("" if n == 1 else "s")
        body = (f'<section class="archive-hero"><div class="shell"><div class="crumb"><a href="/dailies/">Dailies</a> &nbsp;/&nbsp; {html.escape(title)}</div>'
                f'<h1>{html.escape(title)}</h1><p>Rare production dailies and alternate footage from The X-Files.</p>'
                f'<div class="archive-meta"><span>{count}</span><span>Original archive material</span><span>Preserved by Boggsfiles</span></div></div></section>'
                f'<div class="shell detail-wrap"><p class="detail-copy">{html.escape(INTRO)}</p><div class="media-grid">{"".join(media)}</div></div>')
        write_route(f"x-files-dailies/{slug}", page(title, body, "Dailies"))
        print(f"Built dailies: {title} ({n})", flush=True)
    if missing: raise SystemExit("MISSING on R2: " + "; ".join(missing))

if __name__ == "__main__":
    main()
