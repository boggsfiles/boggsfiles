"""Teaser for the scripts going searchable: the scans first, then the number, then the date.

Leads with the documents rather than the site, which is the rule and also the better reel -- a
pink revision page is more arresting than a search box. The page count ticks up rather than
appearing, with the same typewriter under it as the search reel, so the two read as a pair.

Page images are pulled from the real PDFs; the count is the real count from the OCR survey.
"""
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 24
INK = (11, 14, 13)
PAPER = (232, 230, 220)
SIGNAL = (224, 121, 108)
MUTED = (139, 147, 140)
DIM = (107, 116, 109)
LINE = (44, 50, 48)

F = Path(__file__).parent / "fonts"
SRC = Path("/private/tmp/claude-501/-Users-lindseyboggs-Sites-boggsfiles/"
           "261dd1eb-8941-4607-87c5-4e3fef009978/scratchpad/pages")
OUT = Path.home() / "Desktop" / "Boggsfiles scripts teaser"

MARGIN = 72
SCRIPTS, PAGES = 603, 35565


def osw(size, weight=500):
    f = ImageFont.truetype(str(F / "Oswald.ttf"), size)
    f.set_variation_by_axes([weight])
    return f


def mono(size, cut="Medium"):
    return ImageFont.truetype(str(F / f"DMMono-{cut}.ttf"), size)


def tracked(d, x, y, s, f, fill, tr):
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tr


def page_frame(path, kicker, caption):
    """One script page, filling the frame, with its own label under it."""
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    im = Image.open(path).convert("RGB")
    box_w, box_h = W - 96, 1330
    s = min(box_w / im.width, box_h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (W - im.width) // 2, 300
    img.paste(im, (x, y))
    d.rectangle([x - 1, y - 1, x + im.width, y + im.height], outline=LINE)
    tracked(d, MARGIN, 190, kicker.upper(), mono(24), DIM, 3.4)
    d.text((MARGIN, y + im.height + 54), caption, font=osw(52, 400), fill=PAPER)
    return img


def count_frame(n, label, sub=None):
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    tracked(d, MARGIN, 190, "THE X-FILES  ·  SCRIPTS", mono(24), DIM, 3.4)
    big = osw(196, 600)
    text = f"{n:,}"
    d.text((MARGIN, 780), text, font=big, fill=PAPER)
    d.text((MARGIN, 1010), label, font=osw(76, 400), fill=SIGNAL)
    if sub:
        d.text((MARGIN, 1130), sub, font=osw(46, 300), fill=MUTED)
    return img


def card(lines, tail=None, link=False):
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    tracked(d, MARGIN, 190, "THE X-FILES  ·  SCRIPTS", mono(24), DIM, 3.4)
    y = 700
    for text, colour, size in lines:
        d.text((MARGIN, y), text, font=osw(size, 600 if size > 90 else 400), fill=colour)
        y += size + 24
    if tail:
        d.line([(MARGIN, y + 40), (W - MARGIN, y + 40)], fill=LINE, width=2)
        d.text((MARGIN, y + 96), tail, font=osw(50, 300), fill=MUTED)
        y += 150
    if link:
        tracked(d, MARGIN, y + 110, "BOGGSFILES.COM", mono(36), SIGNAL, 3.2)
    return img


def typewriter(clicks, seconds, sr=44100):
    """Same keyboard as the search reel, under the counter rather than under typing."""
    rng = np.random.default_rng(11)
    track = np.zeros(int(seconds * sr) + sr)
    for t in clicks:
        n = int(sr * 0.045)
        x = np.arange(n) / sr
        sig = (rng.normal(0, 1, n) * np.exp(-x * 150) * 0.55
               + np.sin(2 * np.pi * rng.uniform(950, 1500) * x) * np.exp(-x * 95) * 0.28
               + np.sin(2 * np.pi * rng.uniform(85, 125) * x) * np.exp(-x * 55) * 0.22)
        i = int(t * sr)
        track[i:i + n] += sig * rng.uniform(0.8, 1.0)
    peak = np.abs(track).max()
    if peak:
        track = track / peak * 0.7
    return (track * 32767).astype("<i2")


PAGES_SHOWN = [
    ("01-01.jpg", "Season 1 · 1X02", "Squeeze, pink revision"),
    # the stage direction on this page is the whole argument for searching a script
    ("02-12.jpg", "Season 1 · 1X02", "“He’s hit a nerve.”"),
    ("03-01.jpg", "Season 6 · 6ABX04", "Dreamland, production draft"),
    ("04-20.jpg", "Season 6 · 6ABX03", "Still headed “Untitled”"),
    ("05-01.jpg", "Season 5 · 5X02", "Redux, goldenrod"),
    ("06-30.jpg", "Season 5 · 5X01", "Unusual Suspects"),
]


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()
    n = 0
    clicks = []

    def put(img, holds):
        nonlocal n
        for _ in range(holds):
            img.save(OUT / f"{n:05d}.png")
            n += 1

    for i, (f, kicker, cap) in enumerate(PAGES_SHOWN):
        put(page_frame(SRC / f, kicker, cap), 34 if i == 0 else 26)

    put(count_frame(SCRIPTS, "scripts"), 30)

    # the page count climbs rather than appearing, one click per step
    steps = 26
    for k in range(1, steps + 1):
        clicks.append(n / FPS)
        value = int(PAGES * (k / steps) ** 0.65)
        put(count_frame(value, "pages"), 2)
    clicks.append(n / FPS)
    put(count_frame(PAGES, "pages", "every one of them a scan"), 44)

    put(card([("NOT ONE WORD", PAPER, 104), ("OF IT", PAPER, 104),
              ("SEARCHABLE.", SIGNAL, 104)], tail="Until tomorrow."), 56)
    put(card([("TOMORROW", SIGNAL, 150)],
             tail="603 scripts. 35,565 pages.", link=True), 62)

    seconds = n / FPS
    wav = OUT / "clicks.wav"
    with wave.open(str(wav), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(44100)
        w.writeframes(typewriter(clicks, seconds).tobytes())

    mp4 = OUT / "boggsfiles-scripts-teaser.mp4"
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
