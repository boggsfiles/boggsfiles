"""Instagram carousel (10 slides, 1080x1350): "The folders that found the locations" — Jeremy Royer's
fourteen X-Files location-scout folders. Scans are landscape panoramas on manila, so they sit on ink
with a caption rather than running full-bleed. Same brand block as carousel_ftf_rare.py, plus a
contributor credit line the other carousels don't need."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (150, 160, 152)
HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "location-scouts"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Carousel - Location scouts"
OUT.mkdir(parents=True, exist_ok=True)
CREDIT = "Scans courtesy of Jeremy Royer · @unknownparish"

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
    g = Image.new("L", (1, bottom - top)); g.putdata([int(alpha * (i / (bottom - top)) ** curve) for i in range(bottom - top)])
    g = g.resize((W, bottom - top)); layer = Image.new("RGB", (W, bottom - top), INK)
    im.paste(layer, (0, top), g)
def cover_fit(im, w, h, anchor=0.5):
    s = max(w / im.width, h / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2; y = round((im.height - h) * anchor); return im.crop((x, y, x + w, y + h))
def load(page):
    im = Image.open(SRC / page[:-3] / "full" / f"{page}.jpg").convert("RGB")
    return im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2)) if max(im.size) > 3000 else im

SLIDES = [  # (page, kicker, caption)
    ("09-norton-afb-10", None, None),  # cover
    ("09-norton-afb-10", "NORTON AFB · GATE 5",
     "A location manager photographed every gate of a closed Air Force base, then stuck a Post-it on one: THIS GATE."),
    ("09-norton-afb-22", "CLOSURE · 7X11",
     "That gate is the fence Mulder stands at in “Closure.” The folder keeps the scout print and the frame together."),
    ("04-bridge-01", "BRIDGE",
     "Tab says BRIDGE. The stone posts at the far end say Malibou Lake — Agoura Hills, still there."),
    ("01-warehouse-01", "WEARHOUSE (SIC)",
     "Orchards, a cracked lot, a grain elevator somewhere in farm country. The one nobody has placed yet."),
    ("06-ocean-long-beach-01", "OCEAN – LONG BEACH · 3 P.M.",
     "The time on the tab is the point: low sun on Ocean Blvd, scouted for a driving shot."),
    ("03-harbor-building-01", "HARBOR BLDG · N/W EXPOSURE",
     "4201 Wilshire at dusk. Scouted, and — as far as anyone can tell — never used."),
    ("05-warner-hollywood-01", "WARNER HOLLYWOOD STUDIOS",
     "Summer 1998: the show is moving from Vancouver and needs stages. Three lots got toured."),
    ("08-ren-mar-01", "REN-MAR STUDIOS",
     "Ren-Mar got the thorough visit — offices, dressing rooms, the shower. They went to Fox instead."),
    ("12-greyhound-downtown-03", None, None),  # closer
]
N = len(SLIDES)

def footer(d, k):
    brand(d, 80, H - 118, 34)
    d.text((W - 80, H - 106), f"{k} / {N}", font=mono(24), fill=MUTED, anchor="ra")

for k, (page, kicker, cap) in enumerate(SLIDES, 1):
    im = load(page)
    canvas = Image.new("RGB", (W, H), INK)
    if k == 1:
        canvas = cover_fit(im, W, H); gradient(canvas, 380, H, 252, 1.0); d = ImageDraw.Draw(canvas)
        d.text((80, 690), "THE FOLDERS", font=oswald(132, 600), fill=PAPER)
        d.text((80, 812), "THAT FOUND", font=oswald(132, 600), fill=PAPER)
        d.text((80, 934), "THE LOCATIONS", font=oswald(132, 600), fill=PAPER)
        d.text((80, 1108), "14 X-FILES SCOUT FOLDERS · 91 PAGES", font=mono(28, "Medium"), fill=SIGNAL)
        d.text((80, 1152), CREDIT, font=mono(24), fill=MUTED)
        footer(d, k)
    elif k == N:
        canvas = cover_fit(im, W, H); gradient(canvas, 300, H, 255, 0.72); d = ImageDraw.Draw(canvas)
        y = 742
        for ln in wrap(d, "Fourteen folders, ninety-one pages, eleven locations pinned to an address. One warehouse still unidentified.", mono(34), W - 160):
            d.text((80, y), ln, font=mono(34), fill=PAPER); y += 46
        d.text((80, y + 34), "All fourteen at boggsfiles.com", font=mono(28, "Medium"), fill=SIGNAL)
        d.text((80, y + 76), CREDIT, font=mono(24), fill=PAPER)
        footer(d, k)
    else:
        ph = round(im.height * (W / im.width)); pic = im.resize((W, ph), Image.LANCZOS)
        if ph > 720:  # tall page: crop to a band, anchored low, so the caption still fits
            pic = cover_fit(im, W, 720, anchor=0.72); ph = 720
        top = 250; canvas.paste(pic, (0, top)); d = ImageDraw.Draw(canvas)
        d.text((80, 168), kicker, font=mono(28, "Medium"), fill=SIGNAL)
        y = top + ph + 54
        for ln in wrap(d, cap, mono(32), W - 160): d.text((80, y), ln, font=mono(32), fill=PAPER); y += 46
        footer(d, k)
    canvas.save(OUT / f"{k:02d}.jpg", quality=93, subsampling=0)
    print("slide", k, page)

sheet = Image.new("RGB", (5 * 324, 2 * 405), (40, 40, 40))
for k in range(N):
    t = Image.open(OUT / f"{k + 1:02d}.jpg").resize((324, 405)); sheet.paste(t, ((k % 5) * 324, (k // 5) * 405))
sheet.save(OUT / "_review.jpg", quality=85)
print("out:", OUT)
