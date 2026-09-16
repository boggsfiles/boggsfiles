#!/usr/bin/env python3
"""script_to_reference.py <script.txt> <reference.txt> [--names NAME=Canonical,...]

Turn a shooting-script text dump (pdftotext or tesseract OCR, indentation not required)
into the SCENE / SPEAKER: reference format that build_transcript.parse_reference reads.

Heuristics (modern Fox scripts, Seasons 10-11):
  * scene heading: optional number, INT./EXT., location            -> "SCENE n Location"
  * character cue: short ALL-CAPS line, optional (CONT'D)/(V.O.)     -> new speaker
  * dialogue: mixed-case lines after a cue, wrapped narrow (<= 45 chars);
    a long line, an ALL-CAPS line, a page header, a transition or a blank ends the speech
  * parentheticals and page furniture (CONTINUED, page numbers, revision headers) are dropped
"""
import re, sys, collections
from pathlib import Path

FURNITURE = re.compile(r"^(\(?\s*CONTINUED\s*:?\)?(\s*\(\d+\))?|\d+\.?|X-Files \d+.*|THE X-FILES.*|.*\(\d\d/\d\d/\d\d\)\s*\d*\.?|OMITTED|ACT (ONE|TWO|THREE|FOUR|FIVE)|TEASER|END OF (ACT|TEASER|SHOW|EPISODE).*|GO TO MAIN TITLES|MAIN TITLES|FADE (IN|OUT).*|CUT TO.*|SMASH CUT.*|DISSOLVE.*|INTERCUT.*|BLACK\.?|TITLE:.*)$", re.I)
NOT_CUE = re.compile(r"\b(INT|EXT|CUT|CONTINUED|OMITTED|DAY|NIGHT|LATER|CONTINUOUS|CAMERA|ANGLE|CLOSE|WIDE|PAGE|POV|SHOT|VIEW|INSERT|BACK TO|SAME|MOMENTS|ON |THE END|FLASHBACK|FB\d|TITLE|TEASER|ACT)\b")
SCENE = re.compile(r"^[A-Z0-9]{0,4}[\s.,°]*\.?\s*(INT|EXT|INT/EXT|EXT/INT|I/E)[.\s/]+(.+?)\s*$")

def capsy(s):
    L = [c for c in s if c.isalpha()]
    return bool(L) and sum(c.isupper() for c in L) / len(L) > 0.7

def convert(text, names):
    lines = text.replace("\x0c", "\n").splitlines()
    out, scene, speaker, buf = [], 0, None, []
    def flush():
        nonlocal buf
        if speaker and buf: out.append(f"{speaker}: {' '.join(buf)}")
        buf = []
    for raw in lines:
        s = raw.strip()
        s = re.sub(r"^[^A-Za-z0-9(\[]+", "", s).strip()                 # leading OCR junk
        s = re.sub(r"\s*\*+\s*$", "", s)                                  # revision asterisks
        if not s or FURNITURE.match(s):
            flush(); speaker = None; continue
        m = SCENE.match(s)
        if m and capsy(s):
            flush(); speaker = None; scene += 1
            loc = re.sub(r"\s+\(?[A-Z]*\d+\)?\s*$", "", m.group(2)).strip(" -—«&.")
            loc = re.sub(r"\s*\((FB\d*|FLASHBACK)\)", "", loc)
            out.append(f"\nSCENE {scene} {(m.group(1).rstrip('.') + '. ' + loc).title()}"); continue
        base = re.sub(r"\s*\([A-Z.'’\s/0-9]*\)?\s*$", "", s)          # strip (CONT'D) / (V.O.) / (O.S.), even unclosed
        base = re.sub(r"[‘’~«»:é&\-\s\d]+$", "", base).strip()
        toks = base.split(); name = []
        for t in toks:                                                      # leading run of ALL-CAPS name tokens
            if re.fullmatch(r"[A-Z][A-Z0-9.'’#/&-]*|&", t): name.append(t)
            else: break
        junk = toks[len(name):]
        if (name and len(name) <= 4 and len(" ".join(name)) <= 30 and all(len(j) <= 3 for j in junk) and len(junk) <= 2
                and not NOT_CUE.search(" ".join(name)) and not " ".join(name).endswith(".")):
            nm = " ".join(name).strip(".,").replace("’", "'")
            flush(); speaker = names.get(nm, nm); continue
        if speaker:
            if s.startswith("(") and s.endswith(")"): continue
            if capsy(s) or len(s) > 45: flush(); speaker = None; continue
            buf.append(s)
    flush()
    return out, scene

def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    names = {}
    if "--names" in sys.argv:
        for pair in sys.argv[sys.argv.index("--names") + 1].split(","):
            if "=" in pair: k, v = pair.split("=", 1); names[k.strip()] = v.strip()
    out, scene = convert(src.read_text(encoding="utf-8", errors="replace"), names)
    dst.write_text("\n".join(out) + "\n")
    c = collections.Counter(l.split(":")[0] for l in out if ":" in l and not l.startswith("SCENE"))
    print(f"{src.parent.name}: scenes {scene}, turns {sum(c.values())}; " + ", ".join(f"{k} {v}" for k, v in c.most_common(12)))

if __name__ == "__main__":
    main()
