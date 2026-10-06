"""Instagram profile picture options, built from the mark already on the site.

The site header reads BOGGS(X)FILES with the X inside a red ring, rotated twelve degrees. That
ring is already a circle, which is what Instagram crops to, so the mark barely needs translating.

Everything here is drawn at 1080 and then shown again at 32px, because 32px is where a profile
picture actually lives -- in a comment, in a story ring, next to a reply. A mark that only works
at full size is not a profile picture, it is a logo.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = 1080
INK = (11, 14, 13)
PAPER = (232, 230, 220)
RED = (183, 56, 49)        # the ring colour from site-header.css
SIGNAL = (224, 121, 108)   # the lighter red the reels use
F = Path(__file__).parent / "fonts"
OUT = Path.home() / "Desktop" / "Boggsfiles profile marks"


def osw(size, weight=600):
    f = ImageFont.truetype(str(F / "Oswald.ttf"), size)
    f.set_variation_by_axes([weight])
    return f


def centred(d, cx, cy, text, font, fill):
    """Centre on the ink, not the ascender box -- Oswald sits high otherwise."""
    b = d.textbbox((0, 0), text, font=font)
    d.text((cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2), text, font=font, fill=fill)


def mark(bg, x_colour, ring_colour, ring_w=34, x_size=560, tilt=-12, ring_d=0.60):
    """The circled X. Drawn oversized then rotated and composited, so the ring stays smooth."""
    img = Image.new("RGB", (S, S), bg)
    layer = Image.new("RGBA", (S * 2, S * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = S  # centre of the double-size layer
    r = int(S * ring_d)
    d.ellipse([c - r, c - r, c + r, c + r], outline=ring_colour + (255,), width=ring_w * 2)
    centred(d, c, c, "X", osw(x_size * 2), x_colour + (255,))
    layer = layer.rotate(tilt, resample=Image.BICUBIC, center=(c, c))
    layer = layer.resize((S, S), Image.LANCZOS)
    img.paste(layer, (0, 0), layer)
    return img


def wordmark(bg, fg, ring_colour):
    """The full name, stacked. Reads at feed size; included so the 32px test can kill it."""
    img = Image.new("RGB", (S, S), bg)
    d = ImageDraw.Draw(img)
    centred(d, S // 2, 250, "BOGGS", osw(190, 500), fg)
    centred(d, S // 2, 830, "FILES", osw(190, 500), fg)
    r = 185
    d.ellipse([S // 2 - r, 540 - r, S // 2 + r, 540 + r], outline=ring_colour, width=26)
    centred(d, S // 2, 540, "X", osw(330), fg)
    return img


OPTIONS = [
    ("01-ink-ring", lambda: mark(INK, PAPER, RED),
     "the site mark exactly: cream X, red ring, on ink"),
    ("02-ink-bold", lambda: mark(INK, PAPER, RED, ring_w=48, x_size=620, ring_d=0.56),
     "same, thicker ring and bigger X for small sizes"),
    ("03-paper", lambda: mark(PAPER, INK, RED, ring_w=44, x_size=600, ring_d=0.58),
     "inverted: ink X on cream, red ring"),
    ("04-red-x", lambda: mark(INK, SIGNAL, PAPER, ring_w=40, x_size=600, ring_d=0.58),
     "red X, cream ring on ink"),
    ("05-wordmark", lambda: wordmark(INK, PAPER, RED),
     "the whole name stacked"),
]


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for name, fn, note in OPTIONS:
        img = fn()
        img.save(OUT / f"{name}.png")
        made.append((name, img, note))

    # the contact sheet: full size, the circle crop Instagram applies, and 32px blown back up
    pad, col = 26, 300
    sheet = Image.new("RGB", (pad + len(made) * (col + pad), 760), (38, 38, 38))
    d = ImageDraw.Draw(sheet)
    small = ImageFont.truetype(str(F / "DMMono-Regular.ttf"), 15)
    for i, (name, img, note) in enumerate(made):
        x = pad + i * (col + pad)
        sheet.paste(img.resize((col, col), Image.LANCZOS), (x, pad))
        mask = Image.new("L", (col, col), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, col, col], fill=255)
        circ = Image.new("RGB", (col, col), (38, 38, 38))
        circ.paste(img.resize((col, col), Image.LANCZOS), (0, 0), mask)
        sheet.paste(circ, (x, pad * 2 + col))
        tiny = img.resize((32, 32), Image.LANCZOS)
        m32 = Image.new("L", (32, 32), 0)
        ImageDraw.Draw(m32).ellipse([0, 0, 32, 32], fill=255)
        t = Image.new("RGB", (32, 32), (38, 38, 38))
        t.paste(tiny, (0, 0), m32)
        sheet.paste(t.resize((96, 96), Image.NEAREST), (x + 100, pad * 3 + col * 2))
        d.text((x, pad * 3 + col * 2 + 104), name, font=small, fill=(220, 220, 220))
        d.text((x, pad * 3 + col * 2 + 124), note[:42], font=small, fill=(150, 150, 150))
    d.text((pad, 716), "top: full   middle: circle crop   bottom: 32px, the size it lives at",
           font=small, fill=(150, 150, 150))
    sheet.save(OUT / "_compare.png")
    print(f"  {len(made)} options -> {OUT}")


if __name__ == "__main__":
    build()
