"""Single Instagram image (1080x1350): what's new on boggsfiles.com.

The first version of this was a grid of text cards, which is just a screenshot of a web page.
The real draw is the paperwork itself - blue mimeograph stock, the X-Files logo, the episode
art, "SHOOTING SCHEDULE" with the revision colour written on by hand. So the covers are the
whole composition, laid out overlapping like documents spread on a desk, and the caption does
the naming instead of labels on the image.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
BEIGE = (226, 224, 213); INK = (21, 24, 22); SIGNAL = (155, 51, 46); MUTED = (112, 117, 112)
HERE = Path(__file__).resolve().parent
ART  = HERE.parents[1] / "dist/assets/archive-photos"
OUT  = Path.home() / "Desktop" / "IG - whats new on boggsfiles.png"

# Ordered for the page, not by season: the three pale covers are spread one per row so the
# blue mimeograph stock carries the whole composition instead of stacking at the top.
COVERS = [
    "misc-memorabilia-x-files-shooting-schedules-64.webp",   # 731            blue
    "misc-memorabilia-x-files-shooting-schedules-18.webp",   # Christmas Carol blue
    "misc-memorabilia-x-files-shooting-schedules-71.webp",   # Closure        b/w
    "misc-memorabilia-x-files-shooting-schedules-65.webp",   # Terma          blue
    "misc-memorabilia-x-files-shooting-schedules-67.webp",   # Chinga         blue
    "misc-memorabilia-x-files-shooting-schedules-70.webp",   # The Unnatural  b/w
    "misc-memorabilia-x-files-shooting-schedules-66.webp",   # Kitsunegari    blue
    "misc-memorabilia-x-files-shooting-schedules-69.webp",   # Schizogeny     blue
    "scripts-misc-script-partials-20.webp",                  # Hungry         aged white
]
TILT = [-2.4, 1.8, -1.2, 2.2, -1.9, 1.4, -2.1, 1.6, -1.5]   # fixed, not random, so reruns match

def oswald(size, wght=400):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), size); f.set_variation_by_axes([wght]); return f
def mono(size, w="Regular"): return ImageFont.truetype(str(HERE / f"fonts/DMMono-{w}.ttf"), size)

def tracked(d, x, y, s, f, fill, track):
    for ch in s: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
    return x

def brand(d, x, y, size=40):
    f = oswald(size, 500); track = 0.16 * size
    x = tracked(d, x, y, "BOGGS", f, INK, track); x += 0.34 * size - track
    xw = d.textlength("X", font=f); d.text((x, y), "X", font=f, fill=INK)
    asc, _ = f.getmetrics(); cx, cy = x + xw / 2, y + asc * 0.62; r = 1.08 * size / 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=SIGNAL, width=max(2, round(size * 2 / 23.2)))
    tracked(d, x + xw + 0.34 * size, y, "FILES", f, INK, track)

img = Image.new("RGB", (W, H), BEIGE)

# ---- the stack ----
CW, CH = 265, 354            # cover size, the scans' own 590x788 proportion
GAPX, GAPY = 28, 12          # every cover fully visible, nothing cropped
x0 = (W - (3 * CW + 2 * GAPX)) // 2
y0 = 145

# The scans are not all the same shape (590x788, 633x900, 590x760...). Scaling every one to
# an identical box would stretch the odd ones, so each is matched on HEIGHT and keeps its own
# width. Rows are then centred, which leaves the small width variation looking like paper
# rather than like a mistake.
loaded = []
for name in COVERS:
    src = Image.open(ART / name).convert("RGB")
    w = max(1, round(CH * src.width / src.height))
    loaded.append(src.resize((w, CH), Image.LANCZOS))

for i, src in enumerate(loaded):
    cw = src.width
    row = [im.width for im in loaded[(i // 3) * 3:(i // 3) * 3 + 3]]
    rx = (W - (sum(row) + 2 * GAPX)) // 2
    sheet = Image.new("RGB", (cw + 8, CH + 8), (250, 250, 247))     # a thin paper border
    sheet.paste(src, (4, 4))
    rot = sheet.rotate(TILT[i], expand=True, resample=Image.BICUBIC, fillcolor=BEIGE)
    mask = Image.new("L", sheet.size, 255).rotate(TILT[i], expand=True, resample=Image.BICUBIC, fillcolor=0)

    px = rx + sum(row[:i % 3]) + (i % 3) * GAPX - (rot.width - cw) // 2
    py = y0 + (i // 3) * (CH + GAPY) - (rot.height - CH) // 2

    shadow = Image.new("RGBA", (rot.width + 40, rot.height + 40), (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 90), (20, 24), mask)
    shadow = shadow.filter(ImageFilter.GaussianBlur(11))
    img.paste(Image.alpha_composite(
        Image.new("RGBA", shadow.size, BEIGE + (255,)), shadow).convert("RGB"),
        (px - 20, py - 20))
    img.paste(rot, (px, py), mask)

d = ImageDraw.Draw(img)

# ---- masthead, over the beige above the stack ----
brand(d, 68, 46)
tracked(d, 70, 106, "RECENTLY CATALOGUED", mono(17, "Medium"), MUTED, 2.8)

# ---- footer band, so the bottom row reads as sitting on a surface ----
d.rectangle((0, H - 110, W, H), fill=INK)
d.text((66, H - 94), "NINE NEW FILES", font=oswald(48, 400), fill=(238, 236, 228))
x = tracked(d, 68, H - 44, "BOGGSFILES.COM", mono(19, "Medium"), (238, 236, 228), 2.6)
d.ellipse((x + 14, H - 38, x + 22, H - 30), fill=SIGNAL)
tracked(d, x + 34, H - 44, "FREE TO BROWSE", mono(19, "Light"), (150, 158, 151), 2.6)

img.save(OUT)
print(f"saved {OUT}  {img.size[0]}x{img.size[1]}")
