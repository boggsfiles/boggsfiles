#!/usr/bin/env python3
"""OCR the episode scripts so their text can be searched.

977 of the 1,022 script PDFs are pure scans with no text layer, so this rasterises each page and
runs tesseract over it. Measured at about 6.8 seconds a page, which is why it runs across several
processes and is written to be resumable: a file whose .txt already exists is skipped, so the job
can be stopped and restarted without losing hours.

Originals are never touched. Pages are rasterised into a temporary directory that is deleted as
each file finishes, and the text lands in a separate output tree.

    python3 tools/ocr_scripts.py            # run (resumes where it left off)
    python3 tools/ocr_scripts.py --status   # how far along it is
"""
import os
import re
import subprocess
import sys
import tempfile
import time
from multiprocessing import Pool
from pathlib import Path

SRC = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts"
OUT = Path.home() / "Desktop" / "XF script OCR"
SEASONS = re.compile(r"^XF Season \d+$")
DPI = "300"            # the scans are fax-era; below this tesseract starts dropping small type
WORKERS = 6            # of 8 cores, leaving the machine usable


def targets():
    out = []
    for folder in sorted(p for p in SRC.iterdir() if p.is_dir() and SEASONS.match(p.name)):
        for pdf in sorted(folder.rglob("*.pdf")):
            out.append((pdf, OUT / folder.name / (pdf.stem + ".txt")))
    return out


def ocr_one(job):
    pdf, dest = job
    if dest.exists() and dest.stat().st_size > 0:
        return ("skip", pdf.name, 0)
    dest.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    try:
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["pdftoppm", "-r", DPI, "-gray", "-png", str(pdf), f"{td}/p"],
                           check=True, capture_output=True, timeout=3600)
            parts = []
            for n, png in enumerate(sorted(Path(td).glob("p-*.png")), 1):
                r = subprocess.run(["tesseract", str(png), "stdout", "--psm", "6", "-l", "eng"],
                                   capture_output=True, text=True, timeout=300)
                parts.append(f"\n[page {n}]\n" + r.stdout.strip())
            # written only once the whole file is done, so a half-finished file never looks complete
            dest.write_text(f"# {pdf.relative_to(SRC)}\n" + "".join(parts), encoding="utf-8")
        return ("ok", pdf.name, time.time() - t0)
    except Exception as e:
        return ("fail", f"{pdf.name}: {type(e).__name__}", time.time() - t0)


def status():
    jobs = targets()
    done = [d for _, d in jobs if d.exists() and d.stat().st_size > 0]
    chars = sum(d.stat().st_size for d in done)
    print(f"  {len(done)}/{len(jobs)} files  ({len(done)*100//max(1,len(jobs))}%)  "
          f"{chars/1e6:.1f} MB of text so far")


def main():
    if "--status" in sys.argv:
        return status()
    jobs = targets()
    todo = [j for j in jobs if not (j[1].exists() and j[1].stat().st_size > 0)]
    print(f"{len(jobs)} script PDFs, {len(todo)} still to do, {WORKERS} workers", flush=True)
    ok = fail = 0
    t0 = time.time()
    with Pool(WORKERS) as pool:
        for i, (state, name, secs) in enumerate(pool.imap_unordered(ocr_one, todo), 1):
            if state == "fail":
                fail += 1
                print(f"  FAIL {name}", flush=True)
            else:
                ok += 1
            if i % 10 == 0 or state == "fail":
                rate = (time.time() - t0) / i
                print(f"  {i}/{len(todo)}  ok={ok} fail={fail}  "
                      f"~{rate*(len(todo)-i)/3600:.1f}h left", flush=True)
    print(f"done: {ok} ok, {fail} failed, {(time.time()-t0)/3600:.1f}h", flush=True)


if __name__ == "__main__":
    main()
