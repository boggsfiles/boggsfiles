"""pick_stills.py — choose a transcript-card still per Season 10/11 episode.

Samples a frame every 20 s from the Blu-ray rip, face-tags with the known identities, and keeps
the brightest well-lit frame that shows Mulder AND Scully (falls back to either). Writes
dist/assets/transcript-stills/<slug>.jpg at 1260x709 and a contact sheet for review.
Usage: facenv/bin/python pick_stills.py
"""
import subprocess, sys, os, tempfile
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageStat
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build_revival_transcripts import EPISODES

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "dist/assets/transcript-stills"
IDENT = np.load(HERE / "identities.npz"); NAMES, CENTS = list(IDENT["names"]), IDENT["cents"]
manifest = {l.split("|")[1]: l.rstrip("\n").split("|")[3] for l in open(HERE / "manifest.txt") if l.strip()}

from insightface.app import FaceAnalysis
app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"]); app.prepare(ctx_id=0, det_size=(640, 640))

def faces(img):
    found = {}
    for f in app.get(img):
        if f.det_score < 0.7: continue
        s = f.normed_embedding @ CENTS.T; j = int(s.argmax())
        if s[j] >= 0.42: found[NAMES[j]] = max(found.get(NAMES[j], 0), float(s[j]) * (f.bbox[2] - f.bbox[0]))
    return found

sheet = []
for season, num, code, slug, title, *_ in EPISODES:
    if (OUT / f"{slug}.jpg").exists(): continue
    mkv = manifest[code]; tmp = tempfile.mkdtemp()
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", "120", "-i", mkv, "-an", "-sn", "-vf", "fps=1/20,scale=960:-2", "-q:v", "3", f"{tmp}/%04d.jpg"], check=True)
    best = None
    for f in sorted(os.listdir(tmp)):
        img = cv2.imread(f"{tmp}/{f}"); found = faces(img)
        st = ImageStat.Stat(Image.open(f"{tmp}/{f}").convert("L")); bright = st.mean[0]
        if bright < 40 or bright > 200: continue
        score = (2 if {"Mulder", "Scully"} <= set(found) else 1 if {"Mulder", "Scully"} & set(found) else 0)
        if score == 0: continue
        size = sum(found.get(n, 0) for n in ("Mulder", "Scully"))
        key = (score, min(size, 400), bright)
        if best is None or key > best[0]: best = (key, f)
    if best is None: print(code, "no face frame"); continue
    idx = int(best[1][:-4]); t = 120 + (idx - 1) * 20
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(t), "-i", mkv, "-frames:v", "1", "-vf", "scale=1260:709:flags=lanczos", "-q:v", "4", str(OUT / f"{slug}.jpg")], check=True)
    print(f"{code} {title}: t={t}s {best[0]}")
    im = Image.open(OUT / f"{slug}.jpg"); im.thumbnail((420, 240)); sheet.append(im)
if sheet:
    cols = 4; rows = (len(sheet) + cols - 1) // cols
    S = Image.new("RGB", (cols * 420, rows * 240))
    for i, im in enumerate(sheet): S.paste(im, ((i % cols) * 420, (i // cols) * 240))
    S.save(str(HERE / "stills_sheet.jpg"), quality=80)
