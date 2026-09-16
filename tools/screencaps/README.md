# Screencap pipeline (built 2026-09-15)
- capture.sh <mkv> <outdir> [scene_thr] [floor_s] [crop] — frames at shot changes + every N s; filenames = movie ms.
- faces_scan.py <frames_dir> <out.npz> — InsightFace (buffalo_l) embeddings for every face. Needs venv: python3 -m venv facenv && facenv/bin/pip install onnxruntime opencv-python-headless insightface
- cents.npy — identity centroids from FTF: index 3=Mulder, 0=Scully, 7=Well-Manicured Man, 23=Kurtzweil, 31=CSM, 14=Skinner. Match = cosine > 0.38.
- FTF workflow: base pass (0.28/5s) + dense pass (0.15/2s) -> keep dense frames only where Mulder|Scully detected -> drop near-black + <=150ms duplicates -> index.json tags + index.html gallery.
Output lives in ~/Movies/XF_screencaps/.
