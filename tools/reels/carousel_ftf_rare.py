"""Instagram carousel (10 slides, 1080x1350): "Antarctica was a green screen" — Fight the Future production
photos that the rarity pass found nowhere else online. Portrait scans run full-bleed (cropped 2:3 -> 4:5);
landscape scans sit on ink with a caption. Same brand block as carousel_screencaps_s1_5.py."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (150, 160, 152)
HERE = Path(__file__).resolve().parent
SRC = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Jesse X-Files/FTF"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Carousel - FTF rare photos"
OUT.mkdir(parents=True, exist_ok=True)

def oswald(size, wght=500):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), size); f.set_variation_by_axes([wght]); return f
def mono(size, w="Regular"): return ImageFont.truetype(str(HERE / f"fonts/DMMono-{w}.ttf"), size)
def tracked(d, x, y, s, f, fill, track):
    for ch in s: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
    return x
def brand(d, x, y, size=58):
    f = oswald(size, 500); track = 0.16 * size
    x = tracked(d, x, y, "BOGGS", f, PAPER, track); x += 0.34 * size - track
    xw = d.textlength("X", font=f); d.text((x, y), "X", font=f, fill=PAPER)
    asc, _ = f.getmetrics(); cx, cy = x + xw / 2, y + asc * 0.62; r = 1.08 * size / 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=SIGNAL, width=max(3, round(size * 2 / 23.2)))
    tracked(d, x + xw + 0.34 * size, y, "FILES", f, PAPER, track)
def wrap(d, s, f, maxw):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
def gradient(im, top, bottom, alpha=215, curve=1.4):
    """darken from `top` (transparent) to `bottom` (alpha) so captions read over the photo"""
    g = Image.new("L", (1, bottom - top)); g.putdata([int(alpha * (i / (bottom - top)) ** curve) for i in range(bottom - top)])
    g = g.resize((W, bottom - top)); layer = Image.new("RGB", (W, bottom - top), INK)
    im.paste(layer, (0, top), g)
def cover_fit(im, w, h):
    s = max(w / im.width, h / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2; return im.crop((x, y, x + w, y + h))
def load(name):
    im = Image.open(SRC / f"{name}.jpg").convert("RGB")
    return im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2)) if max(im.size) > 3000 else im

SLIDES = [  # (file, caption) — portrait files go full-bleed, landscape on ink
    ("FTF2373", None),   # cover
    ("FTF2392", "The Antarctic ice shelf: a soundstage, a green wall, traffic cones and a lot of salt."),
    ("FTF2319", "Fog machine running, green screen edge in frame. The wind and the ice came later."),
    ("FTF2682", "The alien suit on a break between takes."),
    ("FTF2746", "Same suit, in the ice, as shot."),
    ("FTFC6710", "The cryopods inside the ship."),
    ("FTF1941", "Mulder rappels into the ship."),
    ("AFTF1925", "Scully in the pod, inside the ship."),
    ("FTF0347", "Steadicam on the Dallas street."),
    ("FTF1613", None),   # closer
]
N = len(SLIDES)

def footer(d, k):
    brand(d, 80, H - 118, 34)
    d.text((W - 80, H - 106), f"{k} / {N}", font=mono(24), fill=MUTED, anchor="ra")

for k, (name, cap) in enumerate(SLIDES, 1):
    im = load(name); portrait = im.height > im.width
    canvas = Image.new("RGB", (W, H), INK)
    if k == 1:
        canvas = cover_fit(im, W, H); gradient(canvas, 420, H, 250, 1.0); d = ImageDraw.Draw(canvas)
        d.text((80, 760), "ANTARCTICA,", font=oswald(150, 600), fill=PAPER)
        d.text((80, 900), "1998", font=oswald(150, 600), fill=PAPER)
        d.text((80, 1110), "FIGHT THE FUTURE · 10 PRODUCTION PHOTOS", font=mono(28, "Medium"), fill=SIGNAL)
        footer(d, k)
    elif k == N:
        canvas = cover_fit(im, W, H); gradient(canvas, 520, H, 250, 1.0); d = ImageDraw.Draw(canvas)
        y = 830
        for ln in wrap(d, "Ten rare photos from the 1998 production, most of them never published.", mono(34), W - 160):
            d.text((80, y), ln, font=mono(34), fill=PAPER); y += 46
        d.text((80, y + 30), "More of the archive at boggsfiles.com", font=mono(28, "Medium"), fill=SIGNAL)
        footer(d, k)
    elif portrait:
        canvas = cover_fit(im, W, H); gradient(canvas, 760, H, 250, 0.9); d = ImageDraw.Draw(canvas)
        y = 1070 - 46 * (len(wrap(d, cap, mono(32), W - 160)) - 1)
        for ln in wrap(d, cap, mono(32), W - 160): d.text((80, y), ln, font=mono(32), fill=PAPER); y += 46
        footer(d, k)
    else:
        ph = round(im.height * (W / im.width)); pic = im.resize((W, ph), Image.LANCZOS)
        top = (H - ph) // 2 - 90; canvas.paste(pic, (0, top)); d = ImageDraw.Draw(canvas)
        y = top + ph + 56
        for ln in wrap(d, cap, mono(32), W - 160): d.text((80, y), ln, font=mono(32), fill=PAPER); y += 46
        footer(d, k)
    canvas.save(OUT / f"{k:02d}.jpg", quality=93, subsampling=0)
    print("slide", k, name)

# review sheet
sheet = Image.new("RGB", (5 * 324, 2 * 405), (40, 40, 40))
for k in range(N):
    t = Image.open(OUT / f"{k + 1:02d}.jpg").resize((324, 405)); sheet.paste(t, ((k % 5) * 324, (k // 5) * 405))
sheet.save(OUT / "_review.jpg", quality=85)
print("out:", OUT)
