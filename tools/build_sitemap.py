#!/usr/bin/env python3
"""Write dist/sitemap.xml and dist/robots.txt so Google can find every page.

Lists every built page except redirect stubs (meta refresh) and pages marked noindex, which
Google would only report back as "Page with redirect" or excluded. Run by publish.sh, so the
sitemap always matches what is being published.

Run:  python3 tools/build_sitemap.py
"""
import re
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

DIST = Path(__file__).resolve().parents[1] / "dist"
SITE = "https://" + (DIST / "CNAME").read_text().strip()
REDIRECT = re.compile(r'http-equiv=["\']refresh', re.I)
NOINDEX = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', re.I)

# Only committed pages: publish.sh ships the committed dist/, so a draft page sitting uncommitted
# in the working tree must not be advertised (Google would find it missing and report a 404).
committed = subprocess.run(["git", "ls-files", "-z", "--", "*.html"], cwd=DIST, capture_output=True, text=True, check=True)
urls = []
for page in sorted(DIST / name for name in committed.stdout.split("\0") if name):
    html = page.read_text(encoding="utf-8", errors="ignore")
    if REDIRECT.search(html) or NOINDEX.search(html):
        continue
    path = page.relative_to(DIST).as_posix()
    path = path[: -len("index.html")] if path.endswith("index.html") else path
    urls.append(f"{SITE}/{path}")

(DIST / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{escape(url)}</loc></url>\n" for url in urls)
    + "</urlset>\n",
    encoding="utf-8",
)
(DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
print(f"sitemap: {len(urls)} pages")
