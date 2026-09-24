#!/usr/bin/env python3
"""Back-fill the analytics tag into pages already built in dist/.

Idempotent: a page that already has the tag is skipped, so this is safe to re-run and safe to use
alongside builders that now emit the tag themselves. Inserts immediately before </head> so the tag
loads before the page body, which is what Google's snippet expects.

Run:  python3 tools/add_analytics.py      (then commit + ./publish.sh)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from analytics import TAG, MEASUREMENT_ID

DIST = Path(__file__).resolve().parents[1] / "dist"
added = skipped = nohead = 0
for f in sorted(DIST.rglob("*.html")):
    t = f.read_text(encoding="utf-8")
    if MEASUREMENT_ID in t: skipped += 1; continue
    if "</head>" not in t: nohead += 1; print("  no </head>:", f.relative_to(DIST)); continue
    f.write_text(t.replace("</head>", TAG + "</head>", 1), encoding="utf-8"); added += 1
print(f"tagged {added} pages, {skipped} already had it, {nohead} had no </head>")
