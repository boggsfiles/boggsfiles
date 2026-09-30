#!/usr/bin/env python3
"""Pick and render a poster frame for every gag reel.

The <video> elements on the gag reel pages point at gag-reel-posters/<slug>.jpg in the
boggsfiles-media bucket. Only season-1 ever had one; without a poster the player shows whatever
its first frame happens to be.

There is no face detection on this machine, so frames are scored on exposure, colour and detail,
which is enough to avoid the two failure modes that matter: black frames and flat grey ones. The
chosen frames are contact-sheeted afterwards so a bad pick can be swapped by hand.

Masters are 720x480 with DAR 3:2, i.e. 4:3 stored stretched, so posters render at 1280x960 to
match the season-1 poster already in the bucket.
"""
import subprocess, tempfile
from pathlib import Path
import numpy as np
from PIL import Image

GR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels"
OUT = Path("/private/tmp/claude-501/-Users-lindseyboggs-Sites-boggsfiles/261dd1eb-8941-4607-87c5-4e3fef009978/scratchpad/posters")
OUT.mkdir(parents=True, exist_ok=True)
REELS = {
    "season-1": "Gag Reel - Season 1.mp4", "season-2": "Gag Reel - Season 2.mp4",
    "season-3": "Gag Reel - Season 3.mp4", "season-4": "Gag Reel - Season 4.mp4",
    "season-5": "Gag Reel - Season 5.mp4", "season-6": "Gag Reel - Season 6.mp4",
    "season-7": "Gag Reel - Season 7.mp4", "season-8": "Gag Reel - Season 8.mp4",
    "season-9": "Gag Reel - Season 9 (with Chris Carter tribute).mp4",
    "fight-the-future": "Gag Reel - Fight the Future.mp4",
}
STEP = 6          # seconds between candidates
HEAD, TAIL = 25, 0.94   # skip the studio slate, and the credits at the end

def dur(p):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                                 "-of","csv=p=0",str(p)], capture_output=True, text=True).stdout)

def skin_fraction(a):
    """Rough lit-skin mask. No face detector on this machine, but "a decent amount of lit skin in
    frame" is a good enough proxy for "somebody's face is in this shot"."""
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    mx = a.max(2); mn = a.min(2)
    m = ((r > 95) & (g > 40) & (b > 20) & ((mx - mn) > 15) &
         (np.abs(r - g) > 15) & (r > g) & (r > b))
    return float(m.mean())

def score(a):
    """Well exposed, with a face in it if possible. Black frames and flat greys score zero."""
    g = a.mean(2)
    mean = g.mean()
    if mean < 45 or mean > 175: return 0.0
    detail = g.std()
    colour = float(np.abs(a[:, :, 0] - a[:, :, 1]).mean() + np.abs(a[:, :, 1] - a[:, :, 2]).mean())
    centre = g[g.shape[0]//4:3*g.shape[0]//4, g.shape[1]//4:3*g.shape[1]//4].std()
    skin = skin_fraction(a)
    if skin < 0.02: return 0.0            # no person in frame, not a poster
    return detail * 0.7 + colour * 0.8 + centre * 0.5 + skin * 900

picks = {}
for slug, name in REELS.items():
    src = GR / "published" / name
    if not src.exists(): src = GR / name
    total = dur(src)
    with tempfile.TemporaryDirectory() as td:
        # Candidates are extracted at final size and scored directly, so there is no index-to-
        # timestamp mapping to get wrong. An earlier version scored small frames and then re-seeked
        # by computed time, and the frame it scored was not the frame it saved.
        subprocess.run(["ffmpeg","-v","error","-ss",str(HEAD),"-to",str(total*TAIL),"-i",str(src),
                        "-vf",f"fps=1/{STEP},scale=1280:960:flags=lanczos","-q:v","2",
                        f"{td}/c%04d.jpg"], check=True)
        cands = sorted(Path(td).glob("c*.jpg"))
        best, bf = -1.0, None
        for f in cands:
            a = np.array(Image.open(f).convert("RGB")).astype(float)
            sc = score(a)
            if sc > best: best, bf = sc, f
        if bf is None:                       # nothing passed the gates, take the brightest
            bf = max(cands, key=lambda f: np.array(Image.open(f).convert("L")).mean())
            best = 0.0
        dest = OUT / f"{slug}.jpg"
        dest.write_bytes(bf.read_bytes())
    a = np.array(Image.open(dest).convert("RGB")).astype(float)
    at = HEAD + (cands.index(bf)) * STEP
    picks[slug] = at
    print(f"  {slug:18} ~{int(at)//60}:{int(at)%60:02d}  score {best:4.0f}  "
          f"luma {a.mean():5.1f}  skin {skin_fraction(a)*100:4.1f}%"
          + ("   <-- CHECK" if a.mean() < 45 else ""))
print(f"\n{len(picks)} posters -> {OUT}")
