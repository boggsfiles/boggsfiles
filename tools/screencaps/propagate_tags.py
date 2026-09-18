"""propagate_tags.py — fill in Mulder/Scully tags the face pass missed inside a shot, plus hand overrides.

Face detection misses profiles, kisses, backs of heads and dark frames. Rule (deliberately strict — a
shot/reverse-shot cut looks the same as in-shot motion to a low-res diff, so "same shot" can't be trusted):
a frame with NO detected faces is given the tags of its neighbours only when the previous and next
frames (each ≤ GAP ms away and visually close) carry the SAME non-empty Mulder/Scully tags. Frames that
already have one of the two names are never given the other. Detected tags are kept in index.orig.json.

tag-overrides.json: {"8X21": [[start_ms, end_ms, ["Mulder", "Scully"]], ...]} — applied last, always wins.

Usage: python3 propagate_tags.py            (all captured episodes; prints changed counts)
       python3 propagate_tags.py 8X21       (one episode)
"""
import json, os, sys, re
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = Path.home() / "Movies/XF_screencaps/series"
NAMES = ("Mulder", "Scully")
GAP = 3200        # ms — neighbour must be this close (dense capture is every 2 s)
SHOT_DIFF = 26    # mean abs diff of 64×36 greys; above this the neighbour is a cutaway, not the same shot

def small(path):
    return np.asarray(Image.open(path).convert("L").resize((64, 36), Image.BILINEAR), dtype=np.float32)

def propagate(ep: Path, overrides=None):
    orig_p = ep / "index.orig.json"; idx_p = ep / "index.json"
    if not orig_p.exists(): orig_p.write_text(idx_p.read_text())
    orig = json.load(open(orig_p)); frames = sorted(orig)
    new = {f: list(t) for f, t in orig.items()}
    ms = [int(f[:-4]) for f in frames]
    for i in range(1, len(frames) - 1):
        f, p, n = frames[i], frames[i - 1], frames[i + 1]
        if orig[f]: continue          # any detected face at all → leave the frame alone
        pt, nt = sorted(set(orig[p]) & set(NAMES)), sorted(set(orig[n]) & set(NAMES))
        if not pt or pt != nt: continue
        if ms[i] - ms[i - 1] > GAP or ms[i + 1] - ms[i] > GAP: continue
        img = small(ep / "thumb" / f)
        if np.abs(img - small(ep / "thumb" / p)).mean() > SHOT_DIFF or np.abs(img - small(ep / "thumb" / n)).mean() > SHOT_DIFF: continue
        for name in pt:
            if name not in new[f]: new[f].append(name)
    for a, b, tags in (overrides or []):
        for f in frames:
            if a <= int(f[:-4]) <= b:
                for t in tags:
                    if t not in new[f]: new[f].append(t)
    for f in new: new[f] = sorted(new[f])
    changed = sum(1 for f in frames if new[f] != orig[f])
    json.dump(new, open(idx_p, "w"))
    return changed, len(frames)

def main():
    ov = json.load(open(HERE / "tag-overrides.json")) if (HERE / "tag-overrides.json").exists() else {}
    only = sys.argv[1] if len(sys.argv) > 1 else None
    total = 0
    for season in sorted(ROOT.iterdir()):
        for ep in sorted(p for p in season.iterdir() if (p / "index.json").exists()):
            code = ep.name.split(" ")[0]
            if only and code != only: continue
            changed, n = propagate(ep, ov.get(code))
            total += changed
            if changed: print(f"{ep.name}: +{changed} of {n}", flush=True)
    print("total frames changed:", total)

if __name__ == "__main__":
    main()
