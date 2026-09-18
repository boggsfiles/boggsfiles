"""sharp.py — swap motion-blurred Mulder/Scully frames for a sharper neighbour from the same shot.

The capture grabs a frame every 2 s inside long shots, which sometimes lands mid-swing / mid-turn.
For each Mulder/Scully frame that is noticeably softer than the episode's typical frame, decode
±WINDOW s around it, discard candidates that belong to a different shot, and keep the sharpest
candidate if it beats the original by RATIO. The file keeps its timestamp name (≤0.4 s off).
"""
import os, subprocess, tempfile, shutil
from pathlib import Path
import numpy as np, cv2
from PIL import Image

WINDOW = 0.4      # seconds either side
RATIO = 1.3       # candidate's face regions must be this much sharper
SHOT_DIFF = 22    # mean abs pixel diff (64×36 grey) above which it's a different shot
PAD = 0.12        # face box padding (fraction of box size) — the face drifts a little within ±0.4 s
NEW_BRIGHT = 400  # newly-bright pixels (credits text etc.) above which a candidate is rejected
CREDITS = (150_000, 510_000)  # ms window where the opening credits fade in/out over act 1 — leave those frames alone

def sharpness(img, boxes=None):
    """Laplacian variance, averaged over the (padded) face boxes when given — a sharp background
    behind a blurred actor otherwise hides the blur."""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    if not boxes: return cv2.Laplacian(g, cv2.CV_64F).var()
    vals = []
    for x1, y1, x2, y2 in boxes:
        px, py = (x2 - x1) * PAD, (y2 - y1) * PAD
        a, b = max(0, int(x1 - px)), max(0, int(y1 - py)); c, d = min(g.shape[1], int(x2 + px)), min(g.shape[0], int(y2 + py))
        if c - a > 8 and d - b > 8: vals.append(cv2.Laplacian(g[b:d, a:c], cv2.CV_64F).var())
    return float(np.mean(vals)) if vals else cv2.Laplacian(g, cv2.CV_64F).var()

_app = None
def face_boxes(img, names, ident_names, cents, thresh):
    """Boxes of faces in img that match one of `names` (InsightFace, same identities as the capture)."""
    global _app
    if _app is None:
        from insightface.app import FaceAnalysis
        _app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"]); _app.prepare(ctx_id=0, det_size=(640, 640))
    out = []
    for face in _app.get(img):
        if face.det_score < 0.6: continue
        s = face.normed_embedding @ cents.T; j = int(s.argmax())
        if s[j] >= thresh and ident_names[j] in names: out.append([float(v) for v in face.bbox])
    return out

def _small(img): return cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (64, 36), interpolation=cv2.INTER_AREA).astype(np.float32)

def candidates(mkv, ms, size, tmp):
    t0 = max(0.0, ms / 1000 - WINDOW)
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{2 * WINDOW + 0.04:.3f}", "-i", str(mkv), "-an", "-sn",
                        "-vf", f"yadif=deint=interlaced,scale={size}:flags=lanczos,setsar=1", "-q:v", "3", f"{tmp}/%03d.jpg"])
    return sorted(Path(tmp).glob("*.jpg")) if r.returncode == 0 else []   # a failed decode just means "no candidates"

def _iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter + 1e-9)

def better_frame(mkv, size, frame_path, ms, boxes, ident=None, want=("Mulder", "Scully")):
    """Return path of a sharper same-shot candidate (temp file) or None. Caller copies it over.
    Guards: same shot (low-res diff), no new bright overlay (opening credits), and — when ident is given —
    the same faces are still detected in the candidate at the same spot (rejects hand-over-face / turned away)."""
    orig = cv2.imread(str(frame_path))
    if orig is None: return None, None
    s0 = sharpness(orig, boxes); ref = _small(orig); og = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
    tmp = tempfile.mkdtemp(); ranked = []
    for c in candidates(mkv, ms, size, tmp):
        img = cv2.imread(str(c))
        if img is None or img.shape != orig.shape: continue
        if np.abs(_small(img) - ref).mean() > SHOT_DIFF: continue
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if int(((g > 170) & (og < 90)).sum()) > NEW_BRIGHT: continue
        s = sharpness(img, boxes)
        if s > s0 * RATIO: ranked.append((s, c))
    for s, c in sorted(ranked, reverse=True):
        if ident is None: return c, tmp
        found = face_boxes(cv2.imread(str(c)), want, *ident)
        if all(any(_iou(b, f) >= 0.3 for f in found) for b in boxes): return c, tmp
    return None, tmp

def resharpen(mkv, size, full_dir, thumb_dir, index, boxes=None, want=("Mulder", "Scully"), ident=None):
    """Improve blurry Mulder/Scully frames in place. Returns list of replaced filenames.
    boxes: {file: [bbox,...]} from the capture's face pass; frames missing from it are re-detected (needs ident=(names, cents, thresh))."""
    files = [f for f, tags in index.items() if set(want) & set(tags)]
    boxes = dict(boxes or {}); replaced = []
    for f in sorted(files):
        if CREDITS[0] <= int(f[:-4]) <= CREDITS[1]: continue
        if f not in boxes:
            if ident is None: continue
            img = cv2.imread(str(full_dir / f))
            if img is None: continue
            boxes[f] = face_boxes(img, want, *ident)
        if not boxes[f]: continue
        best, tmp = better_frame(mkv, size, full_dir / f, int(f[:-4]), boxes[f], ident, want)
        if best is not None:
            shutil.copy(best, full_dir / f)
            im = Image.open(full_dir / f); im.thumbnail((480, 480)); im.save(thumb_dir / f, quality=82)
            replaced.append(f)
        if tmp: shutil.rmtree(tmp, ignore_errors=True)
    return replaced
