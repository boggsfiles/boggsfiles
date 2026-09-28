"""Instagram highlight covers for @boggsfiles, 1080x1920 (story size).

Instagram crops a highlight cover to the centre square and then masks it to a circle, so every
cover is laid out inside a circle of diameter 1080 centred at (540, 960). Nothing important goes
outside a 880px safe circle.

The row is judged at about 56 pixels, so the rules are: two words maximum, set as large as the
circle allows, paper on ink. START HERE is inverted so position one reads as the way in.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
CX, CY = W // 2, H // 2
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49)
HERE = Path(__file__).resolve().parent
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/IG Highlight Covers"
OUT.mkdir(parents=True, exist_ok=True)

def osw(size, wght=600):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), size); f.set_variation_by_axes([wght]); return f

# label lines, the title to type into Instagram (<= 10 chars so it never truncates), inverted?
COVERS = [
    (["START", "HERE"],   "Start Here", True),
    (["SCRIPTS"],         "Scripts",    False),
    (["XF", "TRIPS"],     "XF Trips",   False),
    (["VS", "SCREEN"],    "Vs Screen",  False),
    (["GAG", "REELS"],    "Gag Reels",  False),
    (["DAILIES"],         "Dailies",    False),
    (["SCREEN", "CAPS"],  "Screencaps", False),
    (["DOCS"],            "Documents",  False),
    (["ASK", "ME"],       "Ask Me",     False),
    (["10.13"],           "10.13",      False),
    # held back: there is no /photos/ section on the site yet, so this one has nothing to point at.
    (["PHOTOS"],          "Photos (hold)", False),
]

SAFE = 880              # everything lives inside this circle
RING = 960              # the thin rule, still inside the 1080 mask

def fit(draw, lines, maxw, start=300):
    """Largest Oswald size whose longest line fits the safe width."""
    size = start
    while size > 40:
        f = osw(size)
        if max(draw.textlength(l, font=f) for l in lines) <= maxw:
            return f
        size -= 4
    return osw(40)

for i, (lines, title, invert) in enumerate(COVERS, 1):
    bg, fg = (PAPER, INK) if invert else (INK, PAPER)
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    # the ring, and a signal-red arc marking the top of it
    d.ellipse((CX - RING//2, CY - RING//2, CX + RING//2, CY + RING//2),
              outline=(150, 40, 34) if invert else (60, 68, 63), width=4)
    d.arc((CX - RING//2, CY - RING//2, CX + RING//2, CY + RING//2),
          start=-118, end=-62, fill=SIGNAL, width=14)

    # the words, optically centred on the circle
    usable = SAFE - 120
    f = fit(d, lines, usable)
    asc, desc = f.getmetrics()
    lh = int(f.size * 1.0)
    block = lh * len(lines)
    y = CY - block // 2 - int(f.size * 0.10)
    for ln in lines:
        d.text((CX, y), ln, font=f, fill=fg, anchor="ma")
        y += lh

    img.save(OUT / f"{i:02d} {title}.png")

print(f"wrote {len(COVERS)} covers to {OUT}")
