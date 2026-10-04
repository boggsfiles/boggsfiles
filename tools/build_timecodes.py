#!/usr/bin/env python3
"""Give every line of dialogue the frame it was said on.

The pieces were already here and not joined up. Each transcript entry carries the subtitle cue
number it came from; the .srt files hold the timecode for that cue; and the screencap galleries
are keyed by timecode, because a frame id is simply milliseconds. So cue number -> timecode ->
nearest frame, and a search result can show the moment instead of an arbitrary still.

Writes dist/transcripts/<season>/<slug>/frames.json, a small lookup the search fetches only for
results it is about to display:

    [["its not ice cream its a nonfat tofutti", 373759], ...]

Episodes without captions or without a gallery are skipped; those keep the episode-level
thumbnail, which is still right about which episode it is.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DATA = ROOT / "tools" / "transcript-data"
CAPS = Path.home() / "Movies" / "XF Captions by Episode"
KEY_LEN = 46          # enough of a line to identify it inside an excerpt, short enough to ship


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", s.lower())).strip()


def srt_times(path):
    """cue number -> start time in milliseconds."""
    out = {}
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8", errors="replace")):
        m = re.match(r"\s*(\d+)\s*\n(\d\d):(\d\d):(\d\d)[,.](\d+)\s*-->", block)
        if m:
            h, mi, s, ms = map(int, m.group(2, 3, 4, 5))
            out[int(m.group(1))] = ((h * 3600 + mi * 60 + s) * 1000) + ms
    return out


def frames_of(slug_path):
    """The gallery's frame ids, which are themselves timecodes."""
    page = DIST / slug_path / "index.html"
    if not page.exists():
        return []
    html = page.read_text(encoding="utf-8")
    i = html.find("FRAMES")
    if i < 0:
        return []
    return sorted(int(x) for x in re.findall(r'"(\d{6,})"', html[i:html.find("</script>", i)]))


def find_srt(meta, index):
    title, code = norm(meta.get("episode", "")), norm(meta.get("production_code", ""))
    for key, path in index.items():
        if title and title in key:
            return path
    for key, path in index.items():
        if code and code in key:
            return path
    return None


def nearest(frames, t):
    # frames are sorted; a plain scan is fast enough at this size and keeps the intent obvious
    best = min(frames, key=lambda f: abs(f - t))
    return best


def main():
    if not CAPS.is_dir():
        raise SystemExit(f"no captions at {CAPS}")
    index = {norm(p.stem): p for p in CAPS.rglob("*.srt")}
    built = skipped_caps = skipped_gallery = 0
    lines = 0
    for jf in sorted(DATA.glob("*.json")):
        meta = json.loads(jf.read_text(encoding="utf-8"))
        slug, season = meta.get("slug"), meta.get("season")
        if not slug:
            continue
        srt = find_srt(meta, index)
        if not srt:
            skipped_caps += 1
            continue
        times = srt_times(srt)
        # The cue numbering has to line up or every lookup is silently off by a scene.
        if meta.get("source_cues") and abs(len(times) - meta["source_cues"]) > 2:
            skipped_caps += 1
            continue
        tdir = f"transcripts/season-{season}/{slug}" if season else f"transcripts/{slug}"
        if not (DIST / tdir).is_dir():
            tdir = f"transcripts/movies/{slug}"
            if not (DIST / tdir).is_dir():
                continue
        gallery = frames_of(f"screencaps/season-{season}/{slug}") or frames_of(f"screencaps/{slug}")
        if not gallery:
            skipped_gallery += 1
            continue
        rows = []
        for e in meta.get("entries", []):
            t = times.get(e.get("number"))
            key = norm(e.get("text", ""))[:KEY_LEN]
            if t is None or len(key) < 12:
                continue
            rows.append([key, nearest(gallery, t)])
        if not rows:
            continue
        (DIST / tdir / "frames.json").write_text(
            json.dumps(rows, separators=(",", ":")), encoding="utf-8")
        built += 1
        lines += len(rows)
    print(f"wrote frames.json for {built} episodes, {lines:,} lines "
          f"(skipped {skipped_caps} without usable captions, {skipped_gallery} without a gallery)")


if __name__ == "__main__":
    main()
