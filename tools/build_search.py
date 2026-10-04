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


def main() -> None:
    if not DIST.is_dir():
        raise SystemExit("dist/ not found")
    mark_stubs()
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
