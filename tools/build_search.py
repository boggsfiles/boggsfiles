#!/usr/bin/env python3
"""Build the site-wide search index into dist/pagefind/.

Pagefind reads the finished HTML in dist/ and writes a sharded index beside it, so search runs
entirely in the visitor's browser and needs no server -- which is the whole constraint here,
because the site is static on GitHub Pages.

Sharding is the reason this is affordable. The site holds ~5.9 MB of text, 94% of it transcripts;
a single index would be far too much to hand every visitor. Pagefind splits it so a search pulls
roughly 100-200 KB.

Excluded from the index:
  * the five redirect stubs, which would otherwise appear as duplicate results
  * the header, footer and nav, which repeat on all 518 pages and drown real matches

Run after the page builders and before ./publish.sh:  python3 tools/build_search.py
"""
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUT = DIST / "pagefind"

# These five pages are <meta http-equiv="refresh"> stubs kept so old links still resolve.
# They carry no content and must not become search results.
REDIRECT_STUBS = [
    "x-files-scripts/index.html",
    "x-files-scripts-by-season/index.html",
    "x-files-dailies/index.html",
    "misc-memorabilia/index.html",
    "got-something-to-share/index.html",
    "x-files-dailies/agua-mala-answering-machine/index.html",
]

# Repeated furniture, plus the breadcrumb, which otherwise opens every transcript excerpt
# with "Transcripts / Season 1 / ..." instead of the line that actually matched.
BOILERPLATE = ["header", "footer", "nav", ".bf-header", ".browse-link", ".footer-row",
               ".crumb", ".bf-navlinks"]


def mark_stubs() -> None:
    """Tag the redirect stubs so pagefind skips them.

    Done with pagefind's own data-pagefind-ignore attribute rather than a --glob, because the CLI
    accepts only one glob and the attribute travels with the file. Idempotent, and it refuses to
    run if a stub ever gains real content, which would mean it should be indexed after all.
    """
    for rel in REDIRECT_STUBS:
        f = DIST / rel
        if not f.exists():
            raise SystemExit(f"redirect stub missing, update REDIRECT_STUBS: {rel}")
        html = f.read_text(encoding="utf-8")
        if 'http-equiv="refresh"' not in html:
            raise SystemExit(f"{rel} is no longer a redirect stub; it should be indexed now")
        if "data-pagefind-ignore" in html:
            continue
        if "<body>" not in html:
            raise SystemExit(f"unexpected markup in {rel}")
        f.write_text(html.replace("<body>", "<body data-pagefind-ignore>", 1), encoding="utf-8")
        print(f"  marked redirect stub: {rel}")


# --- result thumbnails -------------------------------------------------------------------------
# Pagefind shows a picture only if the page offers one, and most of these pages do not have an
# <img> a crawler can see: the screencap galleries build their thumbnails in JavaScript after
# load, and the transcripts carry no image at all. The frame ids are in the page though, so a
# real thumbnail URL can be derived and handed to Pagefind as metadata.

R2 = "https://pub-df226d4134944457905024edfc4635fb.r2.dev"
META = re.compile(r'<span data-pagefind-meta="image:[^"]*" hidden></span>')


def frames_of(html_text):
    """The frame ids a screencap gallery will request once its script runs.

    Read to the end of the script block rather than trying to match the array's closing
    bracket: the entries are themselves nested lists, so a non-greedy match stopped at the
    first one and only ever returned a single id.
    """
    i = html_text.find("FRAMES")
    if i < 0:
        return []
    j = html_text.find("</script>", i)
    return re.findall(r'"(\d{6,})"', html_text[i:j if j > 0 else len(html_text)])


def screencap_base(html_text):
    """The gallery's R2 prefix. Skips any /thumb/ URL, which would be a stamp from a previous run."""
    for m in re.finditer(r'(https://pub-[a-z0-9]+\.r2\.dev/screencaps/[^"\')\s]+)', html_text):
        u = m.group(1)
        if "/thumb/" not in u:
            return u.rstrip("/")
    return None


def thumb_for(rel, page_text, body_text, dist):
    """A thumbnail URL for one page, or None if the page has nothing worth showing.

    The gallery frame list and its R2 base live in a <script> after </main>, so the
    screencap and transcript rules read the whole page; the plain <img> fallback stays
    inside the body so it cannot pick up a header logo.
    """
    section = rel.split("/")[0]

    if section == "screencaps":
        base, ids = screencap_base(page_text), frames_of(page_text)
        return f"{base}/thumb/{ids[0]}.jpg" if base and ids else None

    if section == "transcripts":
        # Transcripts hold no image of their own, so borrow the episode's screencap gallery --
        # but never its opening frame. Lindsey's rule is that a transcript still and a screencap
        # cover must never be the same frame, so take one from four tenths of the way in.
        slug = rel.split("/")[1:-1]
        if not slug:                       # /transcripts/ itself is a listing, not an episode
            return None
        for cand in ("screencaps/" + "/".join(slug), "screencaps/" + slug[-1]):
            page = dist / cand / "index.html"
            if page.exists():
                h = page.read_text(encoding="utf-8")
                base, ids = screencap_base(h), frames_of(h)
                if base and len(ids) > 2:
                    return f"{base}/thumb/{ids[int(len(ids) * 0.4)]}.jpg"
        return None

    if section in ("x-files-dailies", "gag-reels"):
        m = re.search(r'poster="([^"]+)"', page_text)
        return html.unescape(m.group(1)) if m else None

    m = re.search(r'<img[^>]+src="([^"]+)"', body_text)
    return html.unescape(m.group(1)) if m else None


def add_thumbnails() -> int:
    """Stamp each page with its thumbnail. Idempotent: the old stamp is replaced, not stacked."""
    done = 0
    for page in DIST.rglob("index.html"):
        rel = str(page.relative_to(DIST))
        text = page.read_text(encoding="utf-8")
        clean = META.sub("", text)        # derive from the page, not from last run's stamp
        body = re.search(r"<main.*?</main>", clean, re.S)
        url = thumb_for(rel, clean, body.group(0) if body else clean, DIST)
        new = clean
        if url:
            stamp = f'<span data-pagefind-meta="image:{html.escape(url, quote=True)}" hidden></span>'
            new = new.replace("</main>", stamp + "</main>", 1)
            done += 1
        if new != text:
            page.write_text(new, encoding="utf-8")
    return done


def main() -> None:
    if not DIST.is_dir():
        raise SystemExit("dist/ not found")
    mark_stubs()
    print(f"  thumbnails on {add_thumbnails()} pages")
    if OUT.exists():
        shutil.rmtree(OUT)          # stale fragments would linger and resurface as dead results

    cmd = ["npx", "-y", "pagefind@latest", "--site", str(DIST),
           "--exclude-selectors", ",".join(BOILERPLATE)]

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    except FileNotFoundError:
        raise SystemExit("npx not found - install Node, then re-run")
    if r.returncode:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit("pagefind failed")

    for line in r.stdout.splitlines():
        if "Indexed" in line or "Finished" in line:
            print(" ", line.strip())

    size = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    frags = len(list((OUT / "fragment").glob("*"))) if (OUT / "fragment").is_dir() else 0
    print(f"wrote {OUT.relative_to(ROOT)}: {size/1e6:.1f} MB, {frags} page fragments")


if __name__ == "__main__":
    main()
