#!/usr/bin/env python3
"""Turn the OCR'd scripts into pages the site search can read.

The scripts themselves stay where they are, on Drive. These pages exist so the words inside them
can be found; each one shows the machine-read text and links out to the actual PDF.

Two deliberate choices:

  * Every page carries <meta name="robots" content="noindex">. The search on this site reads them;
    Google does not. Publishing 35,000 pages of someone else's screenplays into Google is a
    different thing from keeping an archive of links, and that was not the deal.

  * The body is weighted below dialogue for Pagefind. A search for "mulder" should not return
    four hundred script pages ahead of the episode he says it in.

Reads  ~/Desktop/XF script OCR/<season>/<name>.txt   (written by tools/ocr_scripts.py)
Writes dist/script-text/<slug>/index.html
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OCR = Path.home() / "Desktop" / "XF script OCR"
OUT = DIST / "script-text"
SEASON_PAGES = DIST / "x-files-scripts-by-season"

sys.path.insert(0, str(Path(__file__).parent))
from transcript_header import ASSETS, site_header

CODE = re.compile(r"\b(\d{1,2}[xX]\d{2}|\d[A-Z]{3}\d{2})\b")


def drive_links():
    """(production code, revision colour) -> Drive URL, read off the season pages."""
    out = {}
    for page in SEASON_PAGES.rglob("index.html"):
        text = page.read_text(encoding="utf-8")
        for block in re.findall(r'<article class="episode".*?</article>', text, re.S):
            h2 = re.search(r"<h2>(.*?)</h2>", block, re.S)
            if not h2:
                continue
            title = html.unescape(re.sub(r"<[^>]+>", "", h2.group(1))).strip()
            m = CODE.search(title)
            if not m:
                continue
            code = m.group(1).upper()
            for url, label in re.findall(r'<a class="draft" href="([^"]+)"[^>]*>(.*?)</a>', block, re.S):
                colour = html.unescape(re.sub(r"<[^>]+>", "", label)).replace("↗", "").strip()
                out[(code, colour.lower())] = html.unescape(url)
            out.setdefault((code, None), title)
    return out


def parse_name(stem):
    """'6ABX03 Triangle (Blue)' -> ('6ABX03', 'Triangle', 'Blue')."""
    m = CODE.search(stem)
    code = m.group(1).upper() if m else None
    paren = re.search(r"\(([^)]+)\)", stem)
    colour = paren.group(1).strip() if paren else None
    title = stem
    if code:
        title = title.replace(m.group(1), "")
    if paren:
        title = title.replace(paren.group(0), "")
    title = re.sub(r"\[[^\]]*\]", "", title)
    return code, re.sub(r"\s+", " ", title).strip(" -–"), colour


def slugify(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


PAGE_BREAK = re.compile(r"^\[page (\d+)\]$", re.M)


def body_html(text):
    """The OCR text, split at the page markers the OCR run wrote in."""
    text = PAGE_BREAK.sub(lambda m: f"\u0000{m.group(1)}\u0000", text)
    parts = text.split("\u0000")
    out = []
    i = 1
    while i < len(parts) - 1:
        num, chunk = parts[i], parts[i + 1]
        body = html.escape(chunk.strip())
        if body:
            out.append(f'<section class="sp"><span class="sp-n">Page {html.escape(num)}</span>'
                       f"<pre>{body}</pre></section>")
        i += 2
    return "".join(out)


CSS = """<style>
.sp{border-top:1px solid var(--line,#2c3230);padding:26px 0;max-width:72ch}
.sp-n{display:block;font:400 .6rem/1.5 "DM Mono",ui-monospace,monospace;letter-spacing:.13em;
 text-transform:uppercase;color:#6b746d;margin-bottom:10px}
.sp pre{margin:0;white-space:pre-wrap;word-break:break-word;font:400 .82rem/1.55 "DM Mono",ui-monospace,monospace;color:#c9cfca}
.sp-note{max-width:70ch;color:#8b938c;font-size:.88rem}
.sp-note b{color:#e8e6dc;font-weight:500}
</style>"""


def page(code, title, colour, url, text):
    label = " ".join(x for x in (title, code) if x)
    rev = f" · {colour}" if colour else ""
    head = (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            # the site's own search reads this page; search engines are asked not to
            f'<meta name="robots" content="noindex,follow">'
            f"<title>{html.escape(label)}{html.escape(rev)} — script text: Boggsfiles</title>"
            f'<meta name="description" content="Machine-read text of the {html.escape(label)} script, '
            f'for searching. The scan itself is on Drive.">'
            f'<link rel="preconnect" href="https://fonts.googleapis.com">'
            f'<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500'
            f'&family=Libre+Caslon+Display&family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet">'
            f'<link rel="stylesheet" href="/assets/archive-detail.css?v=4">{ASSETS}{CSS}</head><body>'
            + site_header("Scripts") + "<main>")
    link = (f'<p class="sp-note"><a class="button" href="{html.escape(url, quote=True)}" '
            f'target="_blank" rel="noopener">Open the scan →</a></p>' if url else "")
    intro = (
        '<p class="sp-note">This is the <b>machine-read text</b> of a scanned script, here so the '
        'words inside it can be searched. It was read by a computer from a photocopy, so expect '
        'wrong letters here and there. <b>The scan is the document</b> — when the two '
        'disagree, the scan is right.</p>')
    return (head + '<section class="archive-hero"><div class="shell">'
            f'<div class="crumb"><a href="/scripts/">Scripts</a> &nbsp;/&nbsp; script text</div>'
            f"<h1>{html.escape(label)}</h1>"
            f'<p>{html.escape(colour or "Script")} · machine-read text for searching.</p>'
            "</div></section>"
            '<div class="shell detail-wrap">' + intro + link
            # weighted below dialogue so a common word does not bury the episode it was said in
            + '<div data-pagefind-weight="0.4">' + body_html(text) + "</div></div>"
            "</main><footer><div class=\"shell footer-row\">BOGGSFILES · SCRIPT TEXT "
            '<span><a href="/">Home</a> · <a href="/scripts/">Scripts</a></span></div>'
            "</footer></body></html>")


def main():
    if not OCR.is_dir():
        raise SystemExit(f"no OCR output at {OCR}")
    links = drive_links()
    OUT.mkdir(parents=True, exist_ok=True)
    made = linked = 0
    seen = set()
    for txt in sorted(OCR.rglob("*.txt")):
        text = txt.read_text(encoding="utf-8", errors="replace")
        if len(text.strip()) < 400:
            continue
        code, title, colour = parse_name(txt.stem)
        slug = slugify(f"{code or ''} {title} {colour or ''}") or slugify(txt.stem)
        if slug in seen:
            slug = slugify(f"{slug}-{txt.parent.name}")
        seen.add(slug)
        url = links.get((code, (colour or "").lower())) if code else None
        if url:
            linked += 1
        dest = OUT / slug
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "index.html").write_text(page(code, title, colour, url, text), encoding="utf-8")
        made += 1
    print(f"wrote dist/script-text: {made} pages, {linked} linked to their scan on Drive")
    return made


if __name__ == "__main__":
    main()
