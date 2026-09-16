#!/usr/bin/env python3
"""clean_ocr_srt.py <in.srt> <out.srt>  — fix the recurring tesseract mistakes in Blu-ray PGS OCR.

Only touches patterns that are never real English ("|" and "/" as words, "lf", "fo", "ts"...),
so it is safe to run on every episode. Anything ambiguous is left for review.
"""
import re, sys
from pathlib import Path

WORD_FIXES = {"|": "I", "/": "I", "!": "I", "l": "I", "lf": "if", "lt": "it", "ln": "in", "ls": "is", "Lt": "It", "Lf": "If", "Ln": "In", "Ls": "Is",
              "il": "I'll", "Il": "I'll", "Lsaw": "I saw", "Lam": "I am", "aman": "a man", "S50": "So", "S0": "So", "didnt": "didn't", "ocully": "Scully", "ina": "in a", "ofthe": "of the", "inthe": "in the", "tothe": "to the",
              "fo": "to", "ts": "is", "|--": "I--", "|!": "I!", "/|": "I", "Iittle": "little", "l'm": "I'm", "l'll": "I'll", "l've": "I've", "l'd": "I'd",
              "Ocully": "Scully", "Ihe": "The", "Ihat": "That", "Ihis": "This", "Ihere": "There", "Ihey": "They"}

def fix_line(line: str) -> str:
    if "-->" in line or re.fullmatch(r"\d+\s*", line): return line
    # bracketed sound cues where "[" / "]" were read as "I" or "|": "IGASPS]" -> "[GASPS]"
    line = re.sub(r"(?<![A-Za-z])[I|]([A-Z][A-Z ,'-]{2,})\]", r"[\1]", line)
    line = re.sub(r"\[([A-Z][A-Z ,'-]{2,})[I|](?![A-Za-z])", r"[\1]", line)
    out = []
    for tok in re.split(r"(\s+)", line):
        core = tok.strip(".,?;:\"“”‘’()")
        if not core: out.append(tok); continue
        lead = tok[:len(tok) - len(tok.lstrip(".,?\"“‘("))]; trail = tok[len(lead) + len(core):]
        if core in WORD_FIXES and not (core == "!" and trail == ""):
            # "!" alone followed by punctuation is still an exclamation ("Hey !")
            core = WORD_FIXES[core]
        else:
            core = re.sub(r"^[|/]('(?:m|ll|ve|d|s))$", r"I\1", core)           # |'m  /'ll
            core = re.sub(r"^[|/](?=t['’]?s$|f$|t$)", "I", core)                  # /t's /f /t -> It's If It
            core = re.sub(r"^[|/](?=[a-z])", "l", core)                           # /earn /aw /ater -> learn law later
            core = re.sub(r"(?<=[a-z])\|(?=[a-z])", "l", core)                  # he|p -> help
        out.append(lead + core + trail)
    line = "".join(out)
    line = re.sub(r"(?<=[A-Za-z]) I(?=[a-z]{2,}\b)", " l", line) if False else line
    line = re.sub(r"\bI ts\b", "Is", line)
    line = re.sub(r"(?<![\w])! (?=[a-z']|I\b)", "I ", line)                       # ", ! could" -> ", I could"
    line = re.sub(r"(?<=[a-z,]) Is (?=[a-z])", " is ", line)
    line = re.sub(r"(?<=[a-z,]) (Know|Knows|Knew|Sure|Just|Call)\b", lambda m: " " + m.group(1).lower(), line)                     # OCR capital I in mid-sentence "is"
    line = re.sub(r"^([^A-Za-z0-9]*)([a-z])", lambda m: m.group(1) + m.group(2).upper(), line) if not re.match(r"^[a-z]", line) else line
    line = re.sub(r"([.?!]\s+)([a-z])(?=[a-z]* )", lambda m: m.group(1) + m.group(2).upper(), line)
    return line

def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
    fixed = [fix_line(l) for l in lines]
    changed = sum(1 for a, b in zip(lines, fixed) if a != b)
    dst.write_text("\n".join(fixed) + "\n")
    print(f"{src.parent.name}: {changed} lines fixed")

if __name__ == "__main__":
    main()
