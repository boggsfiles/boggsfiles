#!/usr/bin/env python3
"""Check that every Google Drive file the site links to opens for a signed-out visitor.

A file that isn't shared "Anyone with the link" sends visitors to a Google sign-in page; a deleted
one gives "not found". Both are reported. Google rate-limits rapid requests (HTTP 429), so this goes
slowly and reports anything it couldn't confirm separately; just re-run it later for those.

Kept out of publish.sh because it takes several minutes and depends on Google's rate limits.

Run:  python3 tools/check_drive_links.py
"""
import re
import subprocess
import time
from pathlib import Path

DIST = Path(__file__).resolve().parents[1] / "dist"
DELAY = 1.5  # seconds between requests; faster than this trips Google's rate limit around 800 requests

files = subprocess.run(["git", "ls-files", "-z", "--", "*.html"], cwd=DIST, capture_output=True, text=True, check=True).stdout
links = sorted({
    url.replace("&amp;", "&")
    for name in files.split("\0") if name
    for url in re.findall(r'https://(?:drive|docs)\.google\.com/[^"\'\s<>]+', (DIST / name).read_text(errors="ignore"))
})
print(f"checking {len(links)} Drive links (about {len(links) * DELAY / 60:.0f} minutes)")

broken, unconfirmed = [], []
for i, url in enumerate(links, 1):
    out = subprocess.run(["curl", "-s", "-L", "--max-redirs", "5", "-o", "/dev/null", "-m", "30",
                          "-w", "%{http_code} %{url_effective}", url], capture_output=True, text=True).stdout
    code, _, final = out.partition(" ")
    if "accounts.google.com" in final:
        broken.append(f"not shared publicly (asks visitors to sign in): {url}")
    elif code in ("404", "410"):
        broken.append(f"file not found: {url}")
    elif code != "200":
        unconfirmed.append(f"HTTP {code}: {url}")
    if i % 100 == 0:
        print(f"  {i}/{len(links)}")
    time.sleep(DELAY)

for line in broken: print("✗", line)
for line in unconfirmed: print("?", line)
print(f"\n{len(links) - len(broken) - len(unconfirmed)} OK, {len(broken)} broken, {len(unconfirmed)} couldn't be confirmed (re-run later)")
raise SystemExit(1 if broken else 0)
