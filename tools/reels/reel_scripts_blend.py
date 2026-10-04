"""Scripts teaser, opening on the search that already works.

The argument is a turn: a line of dialogue is findable today, and the line printed above it in
the script is not. So the reel opens exactly like the search reel -- same typing, same typewriter,
the dreamsicle -- and then shows the page that search cannot reach.

Everything shown is real: the search result comes from the live index, the pages are the actual
scans, and the count is the count.
"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import reel_search as RS                 # the search frames, verbatim from the published reel
import reel_scripts_teaser as RT         # the page, counter and card frames

W, H, FPS = RS.W, RS.H, RS.FPS
OUT = Path.home() / "Desktop" / "Boggsfiles scripts teaser"

QUERY = "nonfat tofutti rice dreamsicle"
HIT = [("Transcripts", "The Unnatural",
        "Fox Mulder. Something you'd like to share with the rest of the class? Dana Scully. "
        "It's not ice cream. It's a <mark>nonfat</mark> <mark>tofutti</mark> <mark>rice</mark> "
        "<mark>dreamsicle.</mark>")]

PAGES = [
    ("02-12.jpg", "Season 1 · 1X02", "“He’s hit a nerve.”"),
    ("04-20.jpg", "Season 6 · 6ABX03", "Still headed “Untitled”"),
    ("03-01.jpg", "Season 6 · 6ABX04", "Dreamland, production draft"),
]


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()
    n = 0
    keys, bells = [], []

    def put(img, holds):
        nonlocal n
        for _ in range(holds):
            img.save(OUT / f"{n:05d}.png")
            n += 1

    # --- 1. the search that already works -------------------------------------------------
    for i in range(1, len(QUERY) + 1):
        if QUERY[i - 1] != " ":
            keys.append(n / FPS)
        put(RS.frame(QUERY[:i], full=QUERY), 2)
    bells.append(n / FPS)
    put(RS.frame(QUERY, full=QUERY), 10)
    put(RS.frame(QUERY, "1 result", HIT, full=QUERY), 14)
    put(RS.frame(QUERY, "1 result", HIT, full=QUERY), 46)

    # --- 2. the turn ------------------------------------------------------------------------
    put(RT.card([("THAT’S WHAT", RS.PAPER, 96), ("THEY SAID.", RS.PAPER, 96)],
                tail="Now the page it was printed on."), 40)

    # --- 3. what the script holds that the episode never did --------------------------------
    for f, kicker, cap in PAGES:
        put(RT.page_frame(RT.SRC / f, kicker, cap), 32)

    put(RT.card([("THAT’S WHAT", RS.PAPER, 96), ("THE SCRIPT", RS.PAPER, 96),
                 ("SAYS.", RS.SIGNAL, 96)]), 40)

    # --- 4. the number, climbing ------------------------------------------------------------
    put(RT.count_frame(RT.SCRIPTS, "scripts"), 26)
    steps = 24
    for k in range(1, steps + 1):
        keys.append(n / FPS)
        put(RT.count_frame(int(RT.PAGES * (k / steps) ** 0.65), "pages"), 2)
    keys.append(n / FPS)
    put(RT.count_frame(RT.PAGES, "pages", "every one of them a scan"), 40)

    # --- 5. the promise ---------------------------------------------------------------------
    put(RT.card([("NOT ONE WORD", RS.PAPER, 100), ("OF IT", RS.PAPER, 100),
                 ("SEARCHABLE.", RS.SIGNAL, 100)], tail="Until tomorrow."), 50)
    put(RT.card([("TOMORROW", RS.SIGNAL, 150)],
                tail="603 scripts. 35,565 pages.", link=True), 60)

    seconds = n / FPS
    wav = OUT / "clicks.wav"
    with wave.open(str(wav), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(44100)
        w.writeframes(RS.typewriter(keys, bells, seconds).tobytes())

    mp4 = OUT / "boggsfiles-scripts-teaser.mp4"
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(OUT / "%05d.png"),
                    "-i", str(wav), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                    "-c:a", "aac", "-b:a", "160k", "-shortest",
                    "-movflags", "+faststart", str(mp4)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for p in OUT.glob("*.png"):
        p.unlink()
    wav.unlink()
    print(f"  {n} frames, {seconds:.1f}s, {len(keys)} clicks -> {mp4}")


if __name__ == "__main__":
    build()
