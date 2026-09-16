#!/usr/bin/env python3
"""review_dump.py <slug> <code>  — per-cue listing (speaker | text) for hand review."""
import json, sys
from pathlib import Path
slug, code = sys.argv[1], sys.argv[2]; season = code[:2]
e = json.load(open(Path.home() / f"Sites/boggsfiles/tools/transcript-data/{slug}.json"))["entries"]
srt = (Path.home() / f"Movies/XF_transcript_prep/S{season}/{code}/subs_clean.srt").read_text().strip().split("\n\n")
cues = {}
for blk in srt:
    L = blk.split("\n")
    if len(L) >= 3: cues[int(L[0])] = " ".join(L[2:])
sp = {}; scene_at = {}
for x in e:
    for n in range(x["cue_start"], x["cue_end"] + 1): sp.setdefault(n, []).append((x["speaker"], x["score"]))
    scene_at.setdefault(x["cue_start"], (x["scene"], x["location"]))
last = None
for n in sorted(cues):
    if n in scene_at and scene_at[n][0] != last: last = scene_at[n][0]; print(f"\n== {scene_at[n][0]} {scene_at[n][1]}")
    who = "/".join(dict.fromkeys(s for s, _ in sp.get(n, []))) or "-"
    sc = min([c for _, c in sp.get(n, [])] or [0])
    print(f"{n:4d} {who[:16]:16s} {sc:.1f}| {cues[n][:105]}")
