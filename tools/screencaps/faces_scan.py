"""faces_scan.py <frames_dir> <out.npz>
Detect faces in every JPEG (downscaled to 960px wide for speed), save embeddings + boxes + file names.
"""
import sys, os, glob, numpy as np, cv2
from insightface.app import FaceAnalysis

D, OUT = sys.argv[1], sys.argv[2]
app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))
files = sorted(glob.glob(os.path.join(D, '*.jpg')))
names, embs, boxes, scores = [], [], [], []
for i, f in enumerate(files):
    img = cv2.imread(f)
    h, w = img.shape[:2]
    s = 960 / w
    small = cv2.resize(img, (960, int(h * s)))
    for face in app.get(small):
        if face.det_score < 0.6:
            continue
        names.append(os.path.basename(f))
        embs.append(face.normed_embedding)
        boxes.append(face.bbox / s)
        scores.append(float(face.det_score))
    if i % 200 == 0:
        print(f"{i}/{len(files)} frames, {len(names)} faces", flush=True)
np.savez(OUT, names=np.array(names), embs=np.array(embs), boxes=np.array(boxes), scores=np.array(scores))
print("done:", len(files), "frames,", len(names), "faces ->", OUT)
