"""Single Instagram image (1080x1350): what's new on boggsfiles.com this week.

Mirrors the site's own "New in the files" homepage grid - three by three, hairline rules,
signal-red NEW pills - so anyone who taps through recognises the page they land on.
House style shared with the carousels: Oswald for names, DM Mono for the detail lines.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
BEIGE = (228, 226, 216); CARD = (238, 236, 228); INK = (21, 24, 22)
SIGNAL = (155, 51, 46); MUTED = (108, 113, 109); LINE = (195, 196, 188)
HERE = Path(__file__).resolve().parent
OUT = Path.home() / "Desktop" / "IG - whats new on boggsfiles.png"

ITEMS = [  # name, season, descriptor  - same nine cards as the home page
    ("731",             "Season 3", "Shooting Schedule, Blue"),
    ("Terma",           "Season 4", "Shooting Schedule, Blue"),
    ("Christmas Carol", "Season 5", "Shooting Schedule, Pink"),
    ("Kitsunegari",     "Season 5", "Shooting Schedule, Blue"),
    ("Schizogeny",      "Season 5", "Shooting Schedule, Blue"),
    ("Chinga",          "Season 5", "Shooting Schedule, Blue"),
    ("The Unnatural",   "Season 6", "Shooting Schedule"),
    ("Closure",         "Season 7", "Shooting Schedule"),
    ("Hungry",          "Season 7", "Blue partial draft"),
]

def oswald(size, wght=500):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), size); f.set_variation_by_axes([wght]); return f
def mono(size, w="Regular"): return ImageFont.truetype(str(HERE / f"fonts/DMMono-{w}.ttf"), size)

def tracked(d, x, y, s, f, fill, track):
    for ch in s: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
    return x

def brand(d, x, y, size=52):
    """BOGGS(X)FILES - the site logo, red ring around the X."""
    f = oswald(size, 500); track = 0.16 * size
    x = tracked(d, x, y, "BOGGS", f, INK, track); x += 0.34 * size - track
    xw = d.textlength("X", font=f); d.text((x, y), "X", font=f, fill=INK)
    asc, _ = f.getmetrics(); cx, cy = x + xw / 2, y + asc * 0.62; r = 1.08 * size / 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=SIGNAL, width=max(3, round(size * 2 / 23.2)))
    tracked(d, x + xw + 0.34 * size, y, "FILES", f, INK, track)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

img = Image.new("RGB", (W, H), BEIGE); d = ImageDraw.Draw(img)

brand(d, 70, 92)
tracked(d, 72, 196, "RECENTLY CATALOGUED", mono(21, "Medium"), MUTED, 3.2)
d.text((68, 236), "NEW IN THE FILES", font=oswald(92, 300), fill=INK)

# ---- the grid ----
M, TOP = 68, 400
GW = W - 2 * M
CW, CH = GW / 3, 252
ROWS = 3

for i in range(9):                                           # light tiles, hairline edges
    cx, cy = M + (i % 3) * CW, TOP + (i // 3) * CH
    d.rectangle((cx, cy, cx + CW, cy + CH), fill=CARD, outline=LINE, width=2)

f_sub, f_pill = mono(17, "Light"), mono(15, "Medium")

def fitted(d, s, maxw, hi=37, lo=24):
    """Largest Oswald size that keeps a name on one line. Wrapping collided with the
    detail lines underneath, and a card title should never be two lines here."""
    for size in range(hi, lo - 1, -1):
        f = oswald(size, 300)
        if d.textlength(s, font=f) <= maxw: return f
    return oswald(lo, 300)
for i, (name, season, desc) in enumerate(ITEMS):
    cx, cy = M + (i % 3) * CW, TOP + (i // 3) * CH
    px, py = cx + 26, cy + 26
    # NEW pill
    label = "NEW"; tw = d.textlength(label, font=f_pill) + 4 * 3.0
    d.rounded_rectangle((px, py, px + tw + 26, py + 30), radius=15, outline=SIGNAL, width=2)
    tracked(d, px + 14, py + 6, label, f_pill, SIGNAL, 3.0)
    # name (wraps to two lines if needed)
    f_name = fitted(d, name.upper(), CW - 50)
    d.text((px, cy + 92), name.upper(), font=f_name, fill=INK)
    # detail lines
    d.text((px, cy + CH - 64), season, font=f_sub, fill=MUTED)
    for j, ln in enumerate(wrap(d, desc, f_sub, CW - 46)[:2]):
        d.text((px, cy + CH - 42 + j * 21), ln, font=f_sub, fill=MUTED)

# ---- footer ----
fy = TOP + ROWS * CH + 62
d.text((M - 2, fy), "BOGGSFILES.COM", font=oswald(54, 400), fill=INK)
x = tracked(d, M, fy + 74, "FULL ARCHIVE", mono(19, "Light"), MUTED, 2.4)
d.ellipse((x + 12, fy + 84, x + 20, fy + 92), fill=SIGNAL)
tracked(d, x + 32, fy + 74, "FREE TO BROWSE", mono(19, "Light"), MUTED, 2.4)

img.save(OUT)
print(f"saved {OUT}  {img.size[0]}x{img.size[1]}")
