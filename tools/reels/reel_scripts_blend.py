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
    # The same beat the search just found, on the page it was printed on -- and Mulder's line
    # is not the line that aired. Script: "Did you bring enough ice cream for all the kids in
    # the class?" On screen: "Something you'd like to share with the rest of the class?"
    ("07-12.jpg", "Season 6 · 6ABX20", "He says it differently on the page"),
    ("02-12.jpg", "Season 1 · 1X02", "“He’s hit a nerve.”"),
    ("04-20.jpg", "Season 6 · 6ABX03", "Still headed “Untitled”"),
]


def end_card():
    """The sign-off. "And more coming" because the archive is never finished."""
    img = Image.new("RGB", (W, H), RS.INK)
    d = ImageDraw.Draw(img)
    RS.tracked(d, RT.MARGIN, 190, "THE X-FILES  \u00b7  SCRIPTS", RT.mono(24), RS.DIM, 3.4)
    d.text((RT.MARGIN, 700), "TOMORROW", font=RT.osw(150, 600), fill=RS.SIGNAL)
    d.line([(RT.MARGIN, 918), (W - RT.MARGIN, 918)], fill=RS.LINE, width=2)
    d.text((RT.MARGIN, 974), "603 scripts. 35,565 pages.", font=RT.osw(50, 300), fill=RS.MUTED)
    RS.tracked(d, RT.MARGIN, 1066, "AND MORE COMING", RT.mono(36), RS.PAPER, 3.6)
    RS.tracked(d, RT.MARGIN, 1146, "BOGGSFILES.COM", RT.mono(36), RS.SIGNAL, 3.2)
    return img


def search_beat(put, keys, bells, n_of, query, status, hits, hold):
    """Type a query, ring the bell, show the result. Returns nothing; appends to the click track."""
    for i in range(1, len(query) + 1):
        if query[i - 1] != " ":
            keys.append(n_of() / FPS)
        put(RS.frame(query[:i], full=query), 2)
    bells.append(n_of() / FPS)
    put(RS.frame(query, full=query), 8)
    put(RS.frame(query, status, hits, full=query), 12)
    put(RS.frame(query, status, hits, full=query), hold)


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

    def n_of():
        return n

    # --- 1. the search, and the page the line was printed on --------------------------------
    search_beat(put, keys, bells, n_of, QUERY, "1 result", HIT, 42)
    put(RT.card([("THAT\u2019S WHAT", RS.PAPER, 96), ("THEY SAID.", RS.PAPER, 96)],
                tail="Now the page it was printed on."), 36)
    put(RT.page_frame(RT.SRC / PAGES[0][0], PAGES[0][1], PAGES[0][2]), 40)

    # --- 2. two more that already work, so the gap is obvious when it comes ------------------
    for query, status, hits in (RS.SCENES[1], RS.SCENES[2]):
        search_beat(put, keys, bells, n_of, query, status, hits, 30)

    put(RT.card([("ALL OF THAT", RS.PAPER, 96), ("IS DIALOGUE.", RS.PAPER, 96)],
                tail="None of it is the script."), 38)

    # --- 3. what only the script holds ------------------------------------------------------
    for f, kicker, cap in PAGES[1:]:
        put(RT.page_frame(RT.SRC / f, kicker, cap), 30)

    put(RT.card([("THAT\u2019S WHAT", RS.PAPER, 96), ("THE SCRIPT", RS.PAPER, 96),
                 ("SAYS.", RS.SIGNAL, 96)]), 36)

    # --- 4. the number, climbing ------------------------------------------------------------
    put(RT.count_frame(RT.SCRIPTS, "scripts"), 24)
    steps = 22
    for k in range(1, steps + 1):
        keys.append(n / FPS)
        put(RT.count_frame(int(RT.PAGES * (k / steps) ** 0.65), "pages"), 2)
    keys.append(n / FPS)
    put(RT.count_frame(RT.PAGES, "pages", "every one of them a scan"), 36)

    # --- 5. the promise ---------------------------------------------------------------------
    put(RT.card([("NOT ONE WORD", RS.PAPER, 100), ("OF IT", RS.PAPER, 100),
                 ("SEARCHABLE.", RS.SIGNAL, 100)], tail="Until tomorrow."), 46)
    put(end_card(), 64)

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
