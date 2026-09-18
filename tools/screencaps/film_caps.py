"""film_caps.py — screencaps for I Want to Believe (extended cut), same pipeline as the episodes.
The DVD is anamorphic 16:9 with the 2.35:1 picture letterboxed (58 px bars top/bottom at 720x480),
so the bars are cropped and the frames come out 853x360 with square pixels.
Usage: facenv/bin/python film_caps.py
"""
from pathlib import Path
import series_caps as sc

MKV = Path("/Volumes/XFiles Archive/Blu-ray rips/X_FILES_I_WANT_TO_BELIEVE/mkv/M2 I Want to Believe (extended).mkv")
OUT = sc.OUT_ROOT.parent / "I Want to Believe (extended)"
SIZE = "853:480,crop=853:360:0:60,scale=853:360"   # scale to square pixels, drop the letterbox, re-state the size for the sharpness pass

if __name__ == "__main__":
    print("M2 I Want to Believe:", sc.process(0, "M2", "I Want to Believe", MKV, out=OUT, size=SIZE), flush=True)
