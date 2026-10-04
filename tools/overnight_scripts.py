#!/usr/bin/env python3
"""Finish the scripts job: wait for the OCR, build the pages, reindex, verify, publish.

Written to run while Lindsey is asleep, so it refuses rather than guesses. Every gate below has
to pass before anything is published; if one fails it stops, leaves the working tree alone and
says why, and the morning is a five minute fix instead of a rollback.

    python3 tools/overnight_scripts.py            # wait, build, verify, publish
    python3 tools/overnight_scripts.py --dry-run  # everything except the publish
"""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OCR = Path.home() / "Desktop" / "XF script OCR"
EXPECTED = 603                 # episode script PDFs the OCR run was given
MIN_SHARE = float(os.environ.get("SCRIPTS_MIN_SHARE", 0.95))   # a few stragglers are fine,
                               # a third of it missing is not. Overridable so the gates
                               # can be rehearsed before the real run.
MAX_WAIT_H = 3.0
REPORT = Path.home() / "Desktop" / "scripts overnight report.txt"

log_lines = []


def log(msg):
    stamp = time.strftime("%H:%M:%S")
    line = f"[{stamp}] {msg}"
    print(line, flush=True)
    log_lines.append(line)


def run(cmd, **kw):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)
    if r.returncode:
        raise RuntimeError(f"{' '.join(cmd[:3])} failed:\n{r.stdout[-1500:]}{r.stderr[-1500:]}")
    return r.stdout


def ocr_done():
    return len([f for f in OCR.rglob("*.txt") if f.stat().st_size > 0]) if OCR.is_dir() else 0


def wait_for_ocr():
    deadline = time.time() + MAX_WAIT_H * 3600
    while True:
        n = ocr_done()
        share = n / EXPECTED
        if share >= MIN_SHARE:
            log(f"OCR {n}/{EXPECTED} ({share:.0%}) - enough to build")
            return n
        if time.time() > deadline:
            log(f"OCR only {n}/{EXPECTED} ({share:.0%}) after {MAX_WAIT_H}h of waiting")
            return n
        log(f"OCR {n}/{EXPECTED} ({share:.0%}) - waiting")
        time.sleep(300)


def main():
    dry = "--dry-run" in sys.argv
    try:
        done = wait_for_ocr()
        if done / EXPECTED < MIN_SHARE:
            raise RuntimeError(
                f"stopping: only {done} of {EXPECTED} scripts were read. Nothing published. "
                f"Restart the OCR with  python3 tools/ocr_scripts.py  and run this again.")

        log("building script pages")
        out = run([sys.executable, "tools/build_script_text.py"])
        log("  " + out.strip().splitlines()[-1])
        pages = len(list((ROOT / "dist" / "script-text").glob("*/index.html")))

        log("rebuilding the search index")
        out = run([sys.executable, "tools/build_search.py"])
        log("  " + out.strip().splitlines()[-1])

        # --- gates ---------------------------------------------------------------------------
        checks = []
        checks.append(("script pages built", pages, pages >= EXPECTED * MIN_SHARE))
        idx = ROOT / "dist" / "pagefind" / "pagefind.js"
        checks.append(("search index present", idx.exists(), idx.exists()))
        noindex = sum("noindex" in p.read_text(encoding="utf-8", errors="replace")
                      for p in list((ROOT / "dist" / "script-text").glob("*/index.html"))[:40])
        checks.append(("noindex on script pages", f"{noindex}/40 sampled", noindex == 40))
        size_mb = sum(f.stat().st_size for f in (ROOT / "dist").rglob("*") if f.is_file()) / 1e6
        checks.append(("dist size under 600 MB", f"{size_mb:.0f} MB", size_mb < 600))

        for name, value, ok in checks:
            log(f"  {'PASS' if ok else 'FAIL'}  {name}: {value}")
        if not all(ok for _, _, ok in checks):
            raise RuntimeError("a check failed - nothing was published")

        if dry:
            log("dry run: stopping before commit and publish")
            return

        log("committing")
        run(["git", "add", "-A", "dist", "tools"])
        msg = (f"Scripts: {pages} of them, searchable\n\n"
               f"Machine-read text of the scanned episode scripts, built so the site search can "
               f"reach inside them. Every page is noindex: this search reads them, Google does "
               f"not. The body is weighted below dialogue so a common word still returns the "
               f"episode it was said in before it returns four hundred script pages.\n\n"
               f"Built overnight from {done} OCR'd scripts.\n\n"
               f"Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>")
        run(["git", "commit", "-q", "-m", msg])
        log("publishing")
        run(["./publish.sh"], shell=False)
        log("published")
    except Exception as e:
        log(f"STOPPED: {e}")
    finally:
        REPORT.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        print(f"\nreport -> {REPORT}")


if __name__ == "__main__":
    main()
