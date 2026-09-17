"""gag_scan.py — face-tag the Season 1-5 gag reels at 1 fps and list runs of Mulder / Scully footage.
Writes gag_runs.json: {file: [[start_s, end_s, {"Mulder": n, "Scully": n}], ...]}"""
import subprocess, tempfile, os, json, sys
from pathlib import Path
import numpy as np, cv2
sys.path.insert(0, str(Path.home() / "Sites/boggsfiles/tools/screencaps"))
from insightface.app import FaceAnalysis

IDENT = np.load(Path.home() / "Sites/boggsfiles/tools/screencaps/identities.npz"); NAMES, CENTS = list(IDENT["names"]), IDENT["cents"]
app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"]); app.prepare(ctx_id=0, det_size=(640, 640))
SRC = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels"
import json as _j
out = _j.load(open(Path(__file__).with_name("gag_runs.json"))) if Path(__file__).with_name("gag_runs.json").exists() else {}
for n in [int(a) for a in sys.argv[1:]] or range(1, 6):
    f = next(SRC.glob(f"Gag Reel - Season {n}*.mp4")); tmp = tempfile.mkdtemp()
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(f), "-vf", "yadif,fps=1,scale=640:-2", "-q:v", "3", f"{tmp}/%05d.jpg"], check=True)
    tags = []
    for k in sorted(os.listdir(tmp)):
        found = set()
        for face in app.get(cv2.imread(f"{tmp}/{k}")):
            if face.det_score < 0.65: continue
            s = face.normed_embedding @ CENTS.T; j = int(s.argmax())
            if s[j] >= 0.40 and NAMES[j] in ("Mulder", "Scully"): found.add(NAMES[j])
        tags.append(found)
    # runs: consecutive seconds where Mulder or Scully is present (allow 1-second gaps)
    runs = []; start = None; gap = 0; counts = {"Mulder": 0, "Scully": 0}
    for i, t in enumerate(tags + [set()]):
        if t:
            if start is None: start = i; counts = {"Mulder": 0, "Scully": 0}
            for c in t: counts[c] += 1
            gap = 0
        elif start is not None:
            gap += 1
            if gap > 1:
                if i - gap - start >= 3: runs.append([start, i - gap, counts])
                start = None; gap = 0
    out[f.name] = runs
    print(f.name, len(tags), "s;", len(runs), "runs:", [(a, b, c["Mulder"], c["Scully"]) for a, b, c in runs])
json.dump(out, open(Path(__file__).with_name("gag_runs.json"), "w"), indent=1)
