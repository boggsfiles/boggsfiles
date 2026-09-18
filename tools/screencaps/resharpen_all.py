"""resharpen_all.py — clean-up pass: swap motion-blurred Mulder/Scully frames in already-captured
episodes for a sharper same-shot neighbour (see sharp.py), then push just the changed files to R2.

Resumable: an episode with .resharpened is skipped. Source MKVs are looked up from manifest.txt;
if the local path is gone, the same folder under the external drive's "DVD rips" is tried.

Usage: facenv/bin/python resharpen_all.py [--season N] [--only CODE] [--no-upload]
"""
import sys, json, re, argparse, subprocess, time
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from sharp import resharpen
from build_screencaps import episodes, BUCKET

EXT = Path("/Volumes/XFiles Archive/DVD rips")
IDENT = np.load(HERE / "identities.npz"); ident = (list(IDENT["names"]), IDENT["cents"], 0.40)

def locate(path):
    p = Path(path)
    if p.exists(): return p
    parts = p.parts
    for i, part in enumerate(parts):
        if part in ("XF_discrip",) or part.endswith("XF Transcripts"):
            q = EXT.joinpath(*parts[i:])
            if q.exists(): return q
    return None

def upload(ep, replaced):
    lst = ep["source"] / ".resharpen_files"; lst.write_text("".join(f"{f}\n" for f in replaced))
    for sub in ("full", "thumb"):
        subprocess.run(["rclone", "copy", str(ep["source"] / sub), f"{BUCKET}/screencaps/{ep['path']}/{sub}", "--files-from", str(lst),
                        "--transfers", "16", "--s3-no-check-bucket", "--ignore-times", "-q"], check=True)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--season", type=int); ap.add_argument("--only"); ap.add_argument("--no-upload", action="store_true"); a = ap.parse_args()
    manifest = {l.split("|")[1]: l.rstrip("\n").split("|")[3] for l in open(HERE / "manifest.txt") if l.strip()}
    for ep in episodes():
        ep["path"] = f"season-{ep['season']}/{ep['slug']}"
        if a.season and ep["season"] != a.season: continue
        if a.only and ep["code"] != a.only: continue
        if not ep["live"] or (ep["source"] / ".resharpened").exists(): continue
        mkv = locate(manifest[ep["code"]])
        if mkv is None: print(ep["code"], "source missing", flush=True); continue
        t0 = time.time(); idx = json.load(open(ep["source"] / "index.json"))
        size = "1920:1080" if ep["season"] >= 10 else ("853:480" if ep["aspect"] == "16/9" else "720:540")
        rep = resharpen(mkv, size, ep["source"] / "full", ep["source"] / "thumb", idx, ident=ident)
        if rep and not a.no_upload and (ep["source"] / ".uploaded").exists(): upload(ep, rep)
        json.dump(rep, open(ep["source"] / ".resharpened", "w"))
        print(f"{ep['code']} {ep['title']}: {len(rep)} replaced in {time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
