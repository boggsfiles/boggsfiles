"""series_caps.py — batch screencaps for every episode in manifest.txt.

Per episode (resumable; skips episodes whose index.json exists):
  1. probe aspect (4:3 vs anamorphic 16:9) and pick an output size at native resolution
  2. base pass   : one frame per shot change (0.28) or every 5 s
  3. dense pass  : one frame per shot change (0.15) or every 2 s
  4. face scan on both passes (InsightFace), match against known identities
  5. keep base frames + dense frames where Mulder or Scully is present
  6. drop near-black frames and near-duplicate timestamps, write full/, thumb/, index.json
  7. Mulder/Scully frames that are unusually soft get swapped for a sharper same-shot neighbour (sharp.py)
  8. frames with no detections between identical-tagged neighbours inherit those tags; tag-overrides.json applied (propagate_tags.py)

Usage: facenv/bin/python series_caps.py [--only 1X79] [--season 1] [--limit N]
"""
import sys, os, re, json, shutil, subprocess, argparse, time
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageStat
from sharp import resharpen
from propagate_tags import propagate as propagate_tags, HERE as _PT_HERE

HERE = Path(__file__).resolve().parent
OUT_ROOT = Path.home() / "Movies/XF_screencaps/series"
# Lindsey's rule: Diana Fowley is never tagged anywhere on the site. Do not add her to identities.npz.
IDENT = np.load(HERE / "identities.npz")
NAMES, CENTS = list(IDENT["names"]), IDENT["cents"]
THRESH = 0.40

def ffprobe(path, *entries):
    return subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", ",".join(entries), "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()

def capture(mkv, out, thr, floor, size):
    out.mkdir(parents=True, exist_ok=True)
    vf = f"yadif=deint=interlaced,select='gt(scene,{thr})+isnan(prev_selected_t)+gte(t-prev_selected_t,{floor})',scale={size}:flags=lanczos,setsar=1,settb=1/1000"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(mkv), "-an", "-sn", "-vf", vf, "-enc_time_base", "1/1000", "-fps_mode", "vfr", "-frame_pts", "1", "-q:v", "3", str(out / "%09d.jpg")], check=True)
    return sorted(f for f in os.listdir(out) if f.endswith(".jpg"))

_app = None
def app():
    global _app
    if _app is None:
        from insightface.app import FaceAnalysis
        _app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"]); _app.prepare(ctx_id=0, det_size=(640, 640))
    return _app

BOXES = {}   # (pass, file) -> Mulder/Scully face boxes, for the sharpness pass
def tag_frames(folder, files):
    tags = {}
    for f in files:
        img = cv2.imread(str(folder / f))
        if img is None: continue
        found = set(); boxes = []
        for face in app().get(img):
            if face.det_score < 0.6: continue
            s = face.normed_embedding @ CENTS.T; j = int(s.argmax())
            if s[j] >= THRESH:
                found.add(NAMES[j])
                if NAMES[j] in ("Mulder", "Scully"): boxes.append([float(v) for v in face.bbox])
        if found: tags[f] = sorted(found); BOXES[(folder.name, f)] = boxes
    return tags

def is_black(path):
    im = Image.open(path).convert("L").resize((64, 36)); st = ImageStat.Stat(im)
    return st.mean[0] < 6 and st.stddev[0] < 6

def process(season, code, title, mkv):
    out = OUT_ROOT / f"S{season:02d}" / f"{code} {title}"
    if (out / "index.json").exists(): return "skip"
    t0 = time.time()
    w, h, dar = (ffprobe(mkv, "stream=width,height,display_aspect_ratio").split(",") + ["", ""])[:3]
    size = "853:480" if dar == "16:9" else "720:540"
    work = out / "_work"; shutil.rmtree(work, ignore_errors=True)
    base = capture(mkv, work / "base", 0.28, 5, size)
    dense = capture(mkv, work / "dense", 0.15, 2, size)
    tb = tag_frames(work / "base", base); td = tag_frames(work / "dense", dense)
    keep = {f: ("base", tb.get(f, [])) for f in base}
    for f in dense:
        if {"Mulder", "Scully"} & set(td.get(f, [])) and f not in keep: keep[f] = ("dense", td[f])
    (out / "full").mkdir(parents=True, exist_ok=True); (out / "thumb").mkdir(exist_ok=True)
    index = {}; last = None; dropped = 0
    for f in sorted(keep):
        src = work / keep[f][0] / f; ms = int(f[:-4])
        if is_black(src) or (last is not None and ms - last <= 150): dropped += 1; continue
        shutil.move(str(src), out / "full" / f)
        im = Image.open(out / "full" / f); im.thumbnail((480, 480)); im.save(out / "thumb" / f, quality=82)
        index[f] = keep[f][1]; last = ms
    sharpened = resharpen(mkv, size, out / "full", out / "thumb", index, boxes={f: BOXES.get((keep[f][0], f), []) for f in index}, ident=(NAMES, CENTS, THRESH))
    BOXES.clear()
    json.dump(index, open(out / "index.json", "w"))
    ov = json.load(open(_PT_HERE / "tag-overrides.json")) if (_PT_HERE / "tag-overrides.json").exists() else {}
    propagate_tags(out, ov.get(code))            # fill detection gaps between identical neighbours + hand overrides
    index = json.load(open(out / "index.json"))
    shutil.rmtree(work, ignore_errors=True)
    n = len(index); ms_ = sum(1 for v in index.values() if "Mulder" in v); sc = sum(1 for v in index.values() if "Scully" in v)
    return f"{n} frames (base {len(base)}, dense {len(dense)}, dropped {dropped}, resharpened {len(sharpened)}) Mulder {ms_} Scully {sc} in {time.time()-t0:.0f}s"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only"); ap.add_argument("--season", type=int); ap.add_argument("--limit", type=int); a = ap.parse_args()
    rows = [l.rstrip("\n").split("|") for l in open(HERE / "manifest.txt") if l.strip()]
    done = 0
    for s, code, title, path in rows:
        if a.only and code != a.only: continue
        if a.season and int(s) != a.season: continue
        if a.limit and done >= a.limit: break
        try:
            r = process(int(s), code, title, Path(path))
        except Exception as e:
            r = f"ERROR {e}"
        print(f"{code} {title}: {r}", flush=True)
        if r != "skip": done += 1

if __name__ == "__main__":
    main()
