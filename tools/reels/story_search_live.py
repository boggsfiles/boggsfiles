"""Instagram story: the search is live, demonstrated on one word.

A story is not a reel. It gets a few seconds and a thumb hovering over the bottom third, so this
types one short query, shows a real result from each half of the archive -- the line as spoken and
the same beat as written -- and says the thing. Everything sits between the profile chrome at the
top and the reply bar at the bottom, with room left for a link sticker.

Result text and the thumbnail are the live ones from boggsfiles.com, not mock-ups.
"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import reel_search as RS

W, H, FPS = 1080, 1920, 24
INK, PAPER, SIGNAL, MUTED, DIM, LINE = RS.INK, RS.PAPER, RS.SIGNAL, RS.MUTED, RS.DIM, RS.LINE
MARGIN = 76

# Instagram's own furniture: profile row up top, reply bar and sticker room below.
TOP_SAFE, BOTTOM_SAFE = 300, 1500

SC = Path("/private/tmp/claude-501/-Users-lindseyboggs-Sites-boggsfiles/"
          "261dd1eb-8941-4607-87c5-4e3fef009978/scratchpad")
OUT = Path.home() / "Desktop" / "Boggsfiles search story"

QUERY = "bambi"
STATUS = "7 results"
THUMB = SC / "bambi_thumb.jpg"

TRANSCRIPT = ("War of the Coprophages",
              "<mark>Bambi</mark> Berenbaum. May I ask why you're trespassing on government "
              "property? Fox Mulder. I'm a federal agent. <mark>Bambi</mark> Berenbaum. So am I.")
SCRIPT = ("War of the Coprophages 3X12",
          "SCULLY Her name is <mark>Bambi?</mark> MULDER Her parents were both naturalists. "
          "Scully does a slight take to the phone. Who is this <mark>Bambi</mark> woman, and how does")


def frame(typed, show_results):
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    qf = RS.osw(96, 500)
    y = TOP_SAFE + 40

    d.text((MARGIN, y), typed, font=qf, fill=PAPER)
    cx = MARGIN + d.textlength(typed, font=qf) + 12
    d.rectangle([cx, y + 10, cx + 6, y + 96], fill=SIGNAL)
    ink = max(d.textbbox((MARGIN, y), QUERY, font=qf)[3],
              d.textbbox((MARGIN, y), "gjpqy", font=qf)[3])
    y = ink + 24
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=LINE, width=2)
    y += 54

    if not show_results:
        return img

    RS.tracked(d, MARGIN, y, STATUS.upper(), RS.mono(30, "Medium"), DIM, 3.4)
    y += 92

    body = RS.mono(36)
    for n, (group, (title, excerpt)) in enumerate((("Transcripts", TRANSCRIPT),
                                                   ("Scripts", SCRIPT))):
        RS.tracked(d, MARGIN, y, group.upper(), RS.mono(27, "Medium"), DIM, 3.6)
        y += 40
        d.line([(MARGIN, y), (W - MARGIN, y)], fill=(34, 40, 38), width=2)
        y += 44
        x = MARGIN
        if n == 0 and THUMB.exists():
            # the thumbnail the search itself picks: the frame the line is said on
            t = Image.open(THUMB).convert("RGB").resize((232, 174), Image.LANCZOS)
            img.paste(t, (MARGIN, y + 4))
            d.rectangle([MARGIN - 1, y + 3, MARGIN + 232, y + 178], outline=(34, 40, 38))
            x = MARGIN + 258
        d.text((x, y), title, font=RS.osw(54, 500), fill=PAPER)
        lines = RS.wrap(d, RS.runs(excerpt), body, W - x - MARGIN)[:4]
        y = RS.draw_runs(d, x, y + 72, lines, body, 52) + 54
    return img


def end_card():
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    y = TOP_SAFE + 180
    for text, colour in (("SEARCH", PAPER), ("IS LIVE.", SIGNAL)):
        d.text((MARGIN, y), text, font=RS.osw(170, 600), fill=colour)
        y += 192
    d.line([(MARGIN, y + 54), (W - MARGIN, y + 54)], fill=LINE, width=2)
    d.text((MARGIN, y + 112), "Every page. Every line.", font=RS.osw(62, 300), fill=PAPER)
    # 603 is the number of scripts in the archive, and the figure already announced in the reel
    d.text((MARGIN, y + 196), "232 transcripts · 603 scripts", font=RS.osw(48, 300), fill=MUTED)
    RS.tracked(d, MARGIN, y + 292, "BOGGSFILES.COM", RS.mono(38, "Medium"), SIGNAL, 3.2)
    return img


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

    for i in range(1, len(QUERY) + 1):
        keys.append(n / FPS)
        put(frame(QUERY[:i], False), 3)
    bells.append(n / FPS)
    put(frame(QUERY, False), 10)
    put(frame(QUERY, True), 96)
    put(end_card(), 70)

    seconds = n / FPS
    wav = OUT / "clicks.wav"
    with wave.open(str(wav), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(44100)
        w.writeframes(RS.typewriter(keys, bells, seconds).tobytes())

    mp4 = OUT / "boggsfiles-search-story.mp4"
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(OUT / "%05d.png"),
                    "-i", str(wav), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                    "-c:a", "aac", "-b:a", "160k", "-shortest",
                    "-movflags", "+faststart", str(mp4)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for p in OUT.glob("*.png"):
        p.unlink()
    wav.unlink()
    print(f"  {n} frames, {seconds:.1f}s -> {mp4}")


if __name__ == "__main__":
    build()
