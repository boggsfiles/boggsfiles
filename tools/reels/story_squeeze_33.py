"""Instagram Story (1080x1920): Squeeze 33rd anniversary, "where were you?".

Deliberately sparse: the bottom third is left empty so a question or poll sticker can go there
without covering anything. Still comes from the xfilesarchive.com Blu-ray gallery, same source as
the site's episode stills.
"""
from pathlib import Path
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1920
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (126, 137, 129); LINE = (44, 50, 48)
HERE = Path(__file__).resolve().parent
CACHE = HERE / "stills_cache/squeeze"; CACHE.mkdir(parents=True, exist_ok=True)
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Story - Squeeze 33"
OUT.mkdir(parents=True, exist_ok=True)
FRAME = 276

def gallery(n):
    p = CACHE / f"SqueezeBR{n}.jpg"
    if not p.exists():
        req = urllib.request.Request(f"https://xfilesarchive.com/gallery/SqueezeBR{n}.jpg",
                                     headers={"User-Agent": "Mozilla/5.0"})
        p.write_bytes(urllib.request.urlopen(req, timeout=30).read())
    return p

def oswald(size, w=500):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), size); f.set_variation_by_axes([w]); return f
def mono(size, w="Regular"): return ImageFont.truetype(str(HERE / f"fonts/DMMono-{w}.ttf"), size)
def tracked(d, x, y, s, f, fill, track):
    for ch in s: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
    return x
def brand(d, x, y, size):
    f = oswald(size, 500); track = 0.16 * size
    x = tracked(d, x, y, "BOGGS", f, PAPER, track); x += 0.34 * size - track
    xw = d.textlength("X", font=f); d.text((x, y), "X", font=f, fill=PAPER)
    asc, _ = f.getmetrics(); cx, cy = x + xw / 2, y + asc * 0.62; r = 1.08 * size / 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=SIGNAL, width=max(3, round(size * 2 / 23.2)))
    tracked(d, x + xw + 0.34 * size, y, "FILES", f, PAPER, track)

img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
brand(d, 80, 250, 46)
d.text((80, 330), "SQUEEZE  ·  SEPTEMBER 24, 1993", font=mono(26, "Medium"), fill=SIGNAL)
d.line((80, 378, W - 80, 378), fill=LINE, width=2)

y = 440
for ln in ["33 YEARS", "AGO TONIGHT."]:
    d.text((80, y), ln, font=oswald(112, 600), fill=PAPER); y += 118

# the still, lifted slightly out of the shadows so it reads on a phone
im = Image.open(gallery(FRAME)).convert("RGB")
im = ImageOps.fit(im, (920, 518), Image.LANCZOS, centering=(0.5, 0.45))
im = ImageOps.autocontrast(im, cutoff=(0, 2))
img.paste(im, (80, 720))
d.rectangle((80, 720, 80 + 919, 720 + 517), outline=LINE, width=2)

d.text((80, 1266), "The first monster of the week.", font=oswald(40, 400), fill=MUTED)
d.text((80, 1322), "Where were you?", font=oswald(58, 600), fill=PAPER)
# DM Mono has no arrow glyph, so draw one rather than render a tofu box
d.text((122, 1404), "tell me below", font=mono(26, "Medium"), fill=SIGNAL)
d.line((92, 1408, 92, 1426), fill=SIGNAL, width=3)
d.polygon([(92, 1433), (84, 1422), (100, 1422)], fill=SIGNAL)

img.save(OUT / "Squeeze 33 - where were you (story).jpg", quality=94, subsampling=0)
print("wrote", OUT / "Squeeze 33 - where were you (story).jpg")
