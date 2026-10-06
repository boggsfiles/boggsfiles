"""Instagram carousel (5 slides, 1080x1350): "coming soon" tease for the Season 1 Vancouver locations map.
Same house style as carousel_location_scouts.py (ink ground, Oswald display, DM Mono captions, brand block
in the footer). Frames are Season 1 screencaps from the capture archive; slide 3 is drawn from
vancouver_base.json (coastline and main roads from OpenStreetMap) with no pins on it yet."""
import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (150, 160, 152)
PANEL = (17, 22, 20); ROAD = (52, 64, 58); ROAD2 = (36, 44, 40); COAST = (127, 167, 180)
HERE = Path(__file__).resolve().parent
CAPS = Path.home() / "Movies/XF_screencaps/series/S01"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Carousel - Vancouver map coming soon"
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
    g = Image.new("L", (1, bottom - top)); g.putdata([int(alpha * (i / (bottom - top)) ** curve) for i in range(bottom - top)])
    g = g.resize((W, bottom - top)); layer = Image.new("RGB", (W, bottom - top), INK)
    im.paste(layer, (0, top), g)
def cover_fit(im, w, h, ax=0.5, ay=0.5):
    s = max(w / im.width, h / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = round((im.width - w) * ax); y = round((im.height - h) * ay); return im.crop((x, y, x + w, y + h))
HD = HERE / "hd_frames"   # Real-ESRGAN x4 upscales of the DVD captures (tools/sr/sr.py), 2880x2160
def frame(ep, name):
    hd = HD / f"{ep[:4]}_{name}.png"
    if hd.exists(): return Image.open(hd).convert("RGB")
    im = Image.open(CAPS / ep / "full" / f"{name}.jpg").convert("RGB")
    return im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=70, threshold=2))

N = 5
def footer(d, k):
    brand(d, 80, H - 118, 34)
    d.text((W - 80, H - 106), f"{k} / {N}", font=mono(24), fill=MUTED, anchor="ra")

def vancouver_map(w, h):
    """Coast and main roads only, centred on Burrard Inlet. Deliberately no pins."""
    base = json.loads((HERE / "vancouver_base.json").read_text())
    lon0, lon1, lat0, lat1 = -123.30, -122.62, 49.10, 49.42
    kx = math.cos(math.radians(49.26)); s = max(w / ((lon1 - lon0) * kx), h / (lat1 - lat0))
    cx, cy = (lon0 + lon1) / 2, (lat0 + lat1) / 2
    P = lambda p: (w / 2 + (p[0] - cx) * kx * s, h / 2 - (p[1] - cy) * s)
    SS = 2; im = Image.new("RGB", (w * SS, h * SS), PANEL); d = ImageDraw.Draw(im)
    def lines(key, fill, width):
        for ln in base[key]:
            pts = [(x * SS, y * SS) for x, y in map(P, ln)]
            if any(-50 < x < w * SS + 50 and -50 < y < h * SS + 50 for x, y in pts): d.line(pts, fill=fill, width=width * SS, joint="curve")
    lines("rd", ROAD2, 1); lines("mw", ROAD, 2); lines("water", COAST, 2); lines("coast", COAST, 2)
    im = im.resize((w, h), Image.LANCZOS); d = ImageDraw.Draw(im)
    for name, lon, lat in [("VANCOUVER", -123.118, 49.262), ("NORTH VANCOUVER", -123.072, 49.335), ("WEST VANCOUVER", -123.215, 49.345),
                           ("BURNABY", -122.972, 49.243), ("RICHMOND", -123.118, 49.165), ("NEW WESTMINSTER", -122.905, 49.203),
                           ("COQUITLAM", -122.80, 49.283), ("SURREY", -122.80, 49.135)]:
        x, y = P((lon, lat)); f = oswald(22, 400); tw = sum(d.textlength(c, font=f) + 3 for c in name)
        tracked(d, x - tw / 2, y, name, f, MUTED, 3)
    return im

# ---------- 1: the map, no pins yet
c = Image.new("RGB", (W, H), INK); mh = 640; c.paste(vancouver_map(W, mh), (0, 250)); d = ImageDraw.Draw(c)
d.text((80, 168), "COMING SOON", font=mono(30, "Medium"), fill=SIGNAL)
d.line((0, 250, W, 250), fill=(44, 50, 48), width=2); d.line((0, 250 + mh, W, 250 + mh), fill=(44, 50, 48), width=2)
d.text((80, 250 + mh + 36), "EVERY LOCATION.", font=oswald(108, 600), fill=PAPER)
d.text((80, 250 + mh + 140), "SEASON ONE.", font=oswald(108, 600), fill=PAPER)
d.text((80, 250 + mh + 278), "THE X-FILES IN VANCOUVER · MAPPED", font=mono(28, "Medium"), fill=PAPER)
footer(d, 1); c.save(OUT / "01.jpg", quality=95, subsampling=0)

# ---------- 2: Deep Throat, motel door
c = Image.new("RGB", (W, H), INK); ph = 700
c.paste(frame("1X01 Deep Throat", "002521469").resize((W, 810), Image.LANCZOS).crop((0, 55, W, 55 + ph)), (0, 250)); d = ImageDraw.Draw(c)
d.text((80, 168), "DEEP THROAT · 1X01", font=mono(28, "Medium"), fill=SIGNAL)
y = 250 + ph + 54
for ln in wrap(d, "The caption says Idaho. The motel is in Tsawwassen. So is almost everything else in Season 1: 24 episodes shot in and around Vancouver.", mono(32), W - 160):
    d.text((80, y), ln, font=mono(32), fill=PAPER); y += 46
footer(d, 2); c.save(OUT / "02.jpg", quality=95, subsampling=0)

# ---------- 3: E.B.E., downtown street
c = Image.new("RGB", (W, H), INK); ph = 700
c.paste(frame("1X23 The Erlenmeyer Flask", "001876908").resize((W, 810), Image.LANCZOS).crop((0, 55, W, 55 + ph)), (0, 250)); d = ImageDraw.Draw(c)
d.text((80, 168), "THE ERLENMEYER FLASK · 1X23", font=mono(28, "Medium"), fill=SIGNAL)
y = 250 + ph + 54
for ln in wrap(d, "We went through the location managers' own records, episode by episode, and pinned every street, cemetery, office tower and front door.", mono(32), W - 160):
    d.text((80, y), ln, font=mono(32), fill=PAPER); y += 46
footer(d, 3); c.save(OUT / "03.jpg", quality=95, subsampling=0)

# ---------- 4: Darkness Falls
c = Image.new("RGB", (W, H), INK); ph = 700
c.paste(frame("1X19 Darkness Falls", "001093175").resize((W, 810), Image.LANCZOS).crop((0, 55, W, 55 + ph)), (0, 250)); d = ImageDraw.Draw(c)
d.text((80, 168), "DARKNESS FALLS · 1X19", font=mono(28, "Medium"), fill=SIGNAL)
y = 250 + ph + 54
for ln in wrap(d, "From the Pilot to The Erlenmeyer Flask. With the street address, and what each place played on screen.", mono(32), W - 160):
    d.text((80, y), ln, font=mono(32), fill=PAPER); y += 46
footer(d, 4); c.save(OUT / "04.jpg", quality=95, subsampling=0)

# ---------- 5: closer, Born Again
c = Image.new("RGB", (W, H), INK); ph = 620
c.paste(frame("1X21 Born Again", "001648046").resize((W, 810), Image.LANCZOS).crop((0, 60, W, 60 + ph)), (0, 250)); d = ImageDraw.Draw(c)
d.text((80, 168), "BORN AGAIN · 1X21", font=mono(28, "Medium"), fill=SIGNAL)
d.text((80, 250 + ph + 36), "THE VANCOUVER MAP", font=oswald(88, 600), fill=PAPER)
d.text((80, 250 + ph + 122), "SEASON ONE", font=oswald(88, 600), fill=PAPER)
d.text((80, 250 + ph + 246), "Coming soon to boggsfiles.com", font=mono(32), fill=PAPER)
d.text((80, 250 + ph + 296), "FOLLOW SO YOU DON'T MISS IT", font=mono(28, "Medium"), fill=SIGNAL)
footer(d, 5); c.save(OUT / "05.jpg", quality=95, subsampling=0)

sheet = Image.new("RGB", (5 * 324, 405), (40, 40, 40))
for k in range(N):
    sheet.paste(Image.open(OUT / f"{k + 1:02d}.jpg").resize((324, 405)), (k * 324, 0))
sheet.save(OUT / "_review.jpg", quality=85)
print("out:", OUT)
