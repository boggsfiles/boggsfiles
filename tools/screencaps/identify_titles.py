"""identify_titles.py — map generically named DVD rips (B1_t00.mkv …) to episodes.

For each disc folder that has an srt/ subfolder, compare the timing of the MKV's DVD
subtitle packets (first 12 minutes) with each caption file's cue start times. The
right episode lines up within a fraction of a second; wrong ones don't.
Writes manifest lines: season|code|title|path
"""
import subprocess, re, sys, os, json
from pathlib import Path

def sub_times(mkv: Path, seconds=720):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "s:0", "-read_intervals", f"%+{seconds}",
                          "-show_entries", "packet=pts_time", "-of", "csv=p=0", str(mkv)], capture_output=True, text=True).stdout
    return sorted({float(x) for x in out.split() if re.match(r"^[0-9.]+$", x)})

def srt_times(srt: Path, seconds=720):
    t = []
    for m in re.finditer(r"(\d\d):(\d\d):(\d\d),(\d{3}) -->", srt.read_text(encoding="utf-8", errors="replace")):
        s = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) + int(m[4]) / 1000
        if s <= seconds: t.append(s)
    return t

def score(pk, cues, tol=0.6):
    if not pk or not cues: return 0.0
    import bisect
    hit = 0
    for c in cues:
        i = bisect.bisect_left(pk, c - tol)
        if i < len(pk) and pk[i] <= c + tol: hit += 1
    return hit / len(cues)

def main(folders):
    for folder in folders:
        folder = Path(folder); srts = sorted((folder / "srt").glob("*.srt")); mkvs = sorted(folder.glob("*.mkv"))
        if not srts or not mkvs: continue
        cues = {s: srt_times(s) for s in srts}
        for mkv in mkvs:
            pk = sub_times(mkv)
            best = sorted(((score(pk, c), s) for s, c in cues.items()), reverse=True)
            (sc, s), (sc2, _) = best[0], (best[1] if len(best) > 1 else (0, None))
            m = re.match(r"(\d+)X(\d+) (.+)\.srt", s.name)
            print(f"{m[1]}|{m[1]}X{m[2]}|{m[3]}|{mkv}|{sc:.2f}|{sc2:.2f}", flush=True)

if __name__ == "__main__":
    main(sys.argv[1:])
