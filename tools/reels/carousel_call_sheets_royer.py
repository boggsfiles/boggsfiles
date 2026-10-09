"""Instagram carousel (9 slides, 1080x1350): two newly archived call sheets — 3X12 "War of the
Coprophages" (Day 6 of 8, with its crew memo) and 5X01 "Unusual Suspects" (Day 5 of 8).

House style follows carousel_second_unit.py: logo at y=250 under the IG username overlay, DM Mono
eyebrows and captions, and the document IS the slide. The hook is the LIVESTOCK line on the back
page, so slide 1 crops straight to it.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49)
MUTED = (126, 137, 129); LINE = (44, 50, 48)
HERE = Path(__file__).resolve().parent
PAGES = Path.home() / "Sites/boggsfiles/dist/assets/archive-photos/call-sheets"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Carousel - Call sheets (Coprophages)"
OUT.mkdir(parents=True, exist_ok=True)
N = 9

def oswald(size, wght=500):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), size); f.set_variation_by_axes([wght]); return f
def mono(size, w="Regular"): return ImageFont.truetype(str(HERE / f"fonts/DMMono-{w}.ttf"), size)

LOGO_Y = 250
def tracked(d, x, y, s, f, fill, track):
    for ch in s: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
    return x
def brand(d, x=80, y=LOGO_Y, size=52):
    f = oswald(size, 500); track = 0.16 * size
    x = tracked(d, x, y, "BOGGS", f, PAPER, track); x += 0.34 * size - track
    xw = d.textlength("X", font=f); d.text((x, y), "X", font=f, fill=PAPER)
    asc, _ = f.getmetrics(); cx, cy = x + xw / 2, y + asc * 0.62; r = 1.08 * size / 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=SIGNAL, width=max(3, round(size * 2 / 23.2)))
    tracked(d, x + xw + 0.34 * size, y, "FILES", f, PAPER, track)
def footer(d, k):
    d.line((80, H - 124, W - 80, H - 124), fill=LINE, width=2)
    d.text((80, H - 96), "BOGGSFILES.COM", font=mono(25), fill=PAPER)
    d.text((W - 80, H - 94), f"{k:02d} / {N:02d}", font=mono(23), fill=MUTED, anchor="ra")
def wrap(d, s, f, maxw):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
def para(d, x, y, s, f, fill=PAPER, maxw=W - 160, lh=None):
    lh = lh or int(f.size * 1.3)
    for ln in wrap(d, s, f, maxw): d.text((x, y), ln, font=f, fill=fill); y += lh
    return y

def band(slug, y0, y1, width=W - 160):
    """Crop a horizontal band of a page by fraction of its height, scaled to `width`."""
    im = Image.open(PAGES / f"{slug}.webp").convert("RGB")
    c = im.crop((0, int(im.height * y0), im.width, int(im.height * y1)))
    return c.resize((width, round(c.height * width / c.width)), Image.LANCZOS)

def place(img, d, pic, y, x=80):
    img.paste(pic, (x, y))
    d.rectangle((x, y, x + pic.width - 1, y + pic.height - 1), outline=(70, 76, 72), width=2)
    return y + pic.height

k = 0
def new(eyebrow):
    global k; k += 1
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
    brand(d); d.text((80, LOGO_Y + 88), eyebrow, font=mono(23, "Medium"), fill=SIGNAL)
    d.line((80, LOGO_Y + 132, W - 80, LOGO_Y + 132), fill=LINE, width=2)
    return img, d
def done(img, d):
    footer(d, k); img.save(OUT / f"{k:02d}.jpg", quality=93); print("slide", k)

# 1 — the hook: LIVESTOCK
img, d = new("CALL SHEET · 3X12 · BACK PAGE")
y = d.textbbox((80, 430), "A", font=oswald(118, 600))[1]
d.text((80, 418), "COCKROACH", font=oswald(118, 600), fill=PAPER)
d.text((80, 530), "WRANGLER", font=oswald(118, 600), fill=PAPER)
y = place(img, d, band("3x12-back", 0.615, 0.725), 690)
para(d, 80, y + 30, "Under LIVESTOCK, on a Monday in November 1995.", mono(30))
done(img, d)

# 2 — what the document is
img, d = new("WAR OF THE COPROPHAGES · DAY 6 OF 8")
y = place(img, d, band("3x12-front", 0.015, 0.115), 420)
y = para(d, 80, y + 34, "Mon, Nov 27, 1995. Crew call 7:30am, shoot call 8:00am. Sunrise 7:40, sunset 4:19 — nine hours of daylight to work with.", mono(30))
para(d, 80, y + 18, "Stage 2 and Stage 4, North Shore Studios, North Vancouver.", mono(30), MUTED)
done(img, d)

# 3 — the day's scenes
img, d = new("WHAT THEY SHOT THAT DAY")
y = place(img, d, band("3x12-front", 0.095, 0.225), 400)
para(d, 80, y + 30, "Six and five-eighths pages: a hospital bathroom, Mulder's apartment, the drug den, the Eckerle house basement.", mono(30))
done(img, d)

# 4 — cast call times
img, d = new("CAST · WEEKLY AND DAY PLAYERS")
y = place(img, d, band("3x12-front", 0.255, 0.385), 400)
para(d, 80, y + 30, "Duchovny: makeup 7:00, on set 8:00. Everyone else reports to studio.", mono(30))
done(img, d)

# 5 — the crew
img, d = new("BACK PAGE · THE WHOLE COMPANY")
y = place(img, d, band("3x12-back", 0.0, 0.26), 400)
para(d, 80, y + 30, "Every department, every name, every call time — the shape of a 1995 Vancouver crew on one page.", mono(30))
done(img, d)

# 6 — the roach gag in departmental language
img, d = new("SPECIAL EFFECTS · MAKEUP · LIVESTOCK")
y = place(img, d, band("3x12-back", 0.545, 0.76), 400)
para(d, 80, y + 26, "“Dry ice, dung in flask.” “False arms x 2 for roach gag.” “Cockroach (species 2).”", mono(29))
done(img, d)

# 7 — the memo
img, d = new("ATTACHED TO THE CALL SHEET")
y = place(img, d, band("3x12-memo", 0.26, 0.70), 400)
para(d, 80, y + 30, "Three days before, the production coordinator asked the crew to sponsor a family for Christmas. It went out stapled to the call sheet.", mono(29))
done(img, d)

# 8 — Unusual Suspects
img, d = new("UNUSUAL SUSPECTS · DAY 5 OF 8")
y = place(img, d, band("5x01-front", 0.04, 0.175), 420)
y = para(d, 80, y + 34, "Tues, Aug 26, 1997. Robson Square, 800 Robson St, Vancouver — the episode that invented the Lone Gunmen's origin.", mono(30))
para(d, 80, y + 18, "Forecast: rain, wind, 19C, 100% POP.", mono(30), MUTED)
done(img, d)

# 9 — closer
img, d = new("NEW IN THE ARCHIVE")
y = 430
y = para(d, 80, y, "Two call sheets added to the Boggsfiles collection — 63 sheets across 24 episodes.", mono(34), lh=48)
y = para(d, 80, y + 30, "The Coprophages sheet arrived as four scanner passes because the page overran the bed. Front and back are spliced back together and the crew memo is attached, as it was.", mono(29))
d.text((80, y + 44), "Read every page at boggsfiles.com", font=mono(28, "Medium"), fill=SIGNAL)
d.text((80, y + 92), "Scans courtesy of Jeremy Royer · @unknownparish", font=mono(25), fill=PAPER)
done(img, d)

sheet = Image.new("RGB", (5 * 324, 2 * 405), (40, 40, 40))
for i in range(N):
    t = Image.open(OUT / f"{i + 1:02d}.jpg").resize((324, 405)); sheet.paste(t, ((i % 5) * 324, (i // 5) * 405))
sheet.save(OUT / "_review.jpg", quality=85)
print("out:", OUT)
