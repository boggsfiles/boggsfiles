"""Instagram carousel (8 slides, 1080x1350) announcing screencaps for Seasons 1-5 + Fight the Future.
Logo is rendered from the site's CSS (Oswald 500, .16em tracking, red circle on the X) and sits at y=250,
below Instagram's username/avatar overlay. Frames come straight from the capture archive (character-tagged)."""
import os, json, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (126, 137, 129); LINE = (44, 50, 48)
HERE = Path(__file__).resolve().parent
SERIES = Path.home() / "Movies/XF_screencaps/series"
FTF = Path.home() / "Movies/XF_screencaps/Fight the Future (extended)"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Carousel - Screencaps S1-5 + FTF"
OUT.mkdir(parents=True, exist_ok=True)

def oswald(size, wght=500):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), size); f.set_variation_by_axes([wght]); return f
def mono(size, w="Regular"): return ImageFont.truetype(str(HERE / f"fonts/DMMono-{w}.ttf"), size)

LOGO_Y = 250   # below the IG username overlay
def tracked(d, x, y, s, f, fill, track):
    for ch in s: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
    return x
def brand(d, x=80, y=LOGO_Y, size=58):
    f = oswald(size, 500); track = 0.16 * size
    x = tracked(d, x, y, "BOGGS", f, PAPER, track); x += 0.34 * size - track
    xw = d.textlength("X", font=f); d.text((x, y), "X", font=f, fill=PAPER)
    asc, _ = f.getmetrics(); cx, cy = x + xw / 2, y + asc * 0.62; r = 1.08 * size / 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=SIGNAL, width=max(3, round(size * 2 / 23.2)))
    tracked(d, x + xw + 0.34 * size, y, "FILES", f, PAPER, track)
def header(d, eyebrow):
    brand(d); d.text((80, LOGO_Y + 95), eyebrow, font=mono(26, "Medium"), fill=SIGNAL); d.line((80, LOGO_Y + 140, W - 80, LOGO_Y + 140), fill=LINE, width=2)
def footer(d, k):
    d.line((80, H - 130, W - 80, H - 130), fill=LINE, width=2)
    d.text((80, H - 100), "boggsfiles.com/screencaps", font=mono(30), fill=PAPER)
    d.text((W - 80, H - 96), f"{k} / 8", font=mono(24), fill=MUTED, anchor="ra")
def wrap(d, s, f, maxw):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
def para(d, x, y, s, f, fill=PAPER, maxw=W - 160, lh=None):
    lh = lh or int(f.size * 1.22)
    for ln in wrap(d, s, f, maxw): d.text((x, y), ln, font=f, fill=fill); y += lh
    return y
def tc(ms): s = ms // 1000; return f"{s // 60}:{s % 60:02d}"

def episode_dir(code):
    for s in SERIES.iterdir():
        for e in s.iterdir():
            if e.name.startswith(code + " "): return e
def pick(ep, want, n, seed=1, tmin=0):
    """n frames from an episode folder where `want` characters are all tagged, spread across the episode."""
    idx = json.load(open(ep / "index.json"))
    cands = sorted(f for f, tags in idx.items() if set(want) <= set(tags) and int(f[:-4]) >= tmin)
    if len(cands) <= n: return cands
    step = len(cands) / n; random.seed(seed)
    return [cands[int(i * step + random.random() * step * 0.6)] for i in range(n)]
def cell(ep, f, w, h):
    im = Image.open(ep / "full" / f).convert("RGB")
    s = max(w / im.width, h / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))
def grid(img, ep, frames, top, cols=2, gap=8, aspect=0.5625, label=None):
    d = ImageDraw.Draw(img); cw = (W - 160 - gap * (cols - 1)) // cols; ch = round(cw * aspect)
    for i, f in enumerate(frames):
        x = 80 + (i % cols) * (cw + gap); y = top + (i // cols) * (ch + gap)
        img.paste(cell(ep, f, cw, ch), (x, y))
        d.rectangle((x + 8, y + ch - 36, x + 96, y + ch - 8), fill=INK); d.text((x + 16, y + ch - 33), tc(int(f[:-4])), font=mono(18), fill=PAPER)
    return top + ((len(frames) + cols - 1) // cols) * (ch + gap)

def save(img, k, name): img.save(OUT / f"{k:02d} {name}.jpg", quality=92)

# ---- 1. cover
img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img); header(d, "NEW ON THE ARCHIVE")
y = 440
for ln in ["SCREENCAPS.", "SEASONS 1–5.", "EVERY SHOT."]:
    d.text((76, y), ln, font=oswald(130, 600), fill=PAPER); y += 132
y = para(d, 80, y + 30, "127,000 frames from Seasons 1 through 5 and Fight the Future, captured from every shot change and tagged by character.", mono(30), fill=MUTED, lh=44)
d.text((80, y + 24), "SWIPE", font=mono(28, "Medium"), fill=SIGNAL); d.polygon([(190, y + 30), (190, y + 56), (212, y + 43)], fill=SIGNAL)
ep = episode_dir("1X79"); fr = pick(ep, ["Mulder", "Scully"], 5, seed=3, tmin=9 * 60 * 1000)
x = 80
for f in fr: img.paste(cell(ep, f, 184, 104), (x, H - 260)); x += 192
footer(d, 1); save(img, 1, "Cover")

# ---- 2. how it works
img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img); header(d, "HOW IT WORKS")
d.text((76, 420), "TAGGED BY", font=oswald(110, 600), fill=PAPER); d.text((76, 530), "CHARACTER.", font=oswald(110, 600), fill=PAPER)
y = 680
for lab, txt in [("MULDER", "every frame he's in"), ("SCULLY", "every frame she's in"), ("MULDER + SCULLY", "the two-shots"), ("SKINNER · CSM · THE LONE GUNMEN", "and the rest"), ("FOWLEY", "never. not once. don't ask.")]:
    tw = d.textlength(lab, font=mono(24, "Medium")) + 36
    d.rectangle((80, y, 80 + tw, y + 48), fill=SIGNAL); d.text((98, y + 11), lab, font=mono(24, "Medium"), fill=PAPER)
    d.text((100 + tw, y + 11), txt, font=mono(26), fill=MUTED); y += 72
para(d, 80, y + 20, "Plus a timecode range, so you can jump to the exact scene. Dense coverage wherever Mulder or Scully is on screen.", mono(28), fill=PAPER, lh=42)
footer(d, 2); save(img, 2, "How it works")

# ---- 3-7. one slide per season
SEASONS = [(3, "SEASON ONE", "1X79", "Pilot", ["Mulder", "Scully"]), (4, "SEASON TWO", "2X13", "Irresistible", ["Mulder", "Scully"]),
           (5, "SEASON THREE", "3X17", "Pusher", ["Mulder", "Scully"]), (6, "SEASON FOUR", "4X15", "Memento Mori", ["Mulder", "Scully"]),
           (7, "SEASON FIVE", "5X12", "Bad Blood", ["Mulder", "Scully"])]
COUNTS = {"SEASON ONE": "26,152", "SEASON TWO": "25,337", "SEASON THREE": "25,123", "SEASON FOUR": "25,379", "SEASON FIVE": "22,024"}
for k, title, code, epname, want in SEASONS:
    ep = episode_dir(code)
    if ep is None: raise SystemExit(f"missing {code}")
    fr = pick(ep, want, 4, seed=k, tmin=9 * 60 * 1000)
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img); header(d, f"{COUNTS[title]} FRAMES  ·  NOW LIVE")
    d.text((76, 420), title, font=oswald(120, 600), fill=PAPER)
    bottom = grid(img, ep, fr, 570, cols=2)
    d = ImageDraw.Draw(img); d.text((80, bottom + 22), f"From “{epname}”  ·  filter: Mulder + Scully", font=mono(26), fill=MUTED)
    footer(d, k); save(img, k, title.title())

# ---- 8. Fight the Future + closer
idx = json.load(open(FTF / "index.json")); hall = sorted(f for f, t in idx.items() if "Hallway Scene" in t)
fr = [hall[i] for i in [int(i * len(hall) / 4 + len(hall) / 8) for i in range(4)]]
img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img); header(d, "2,892 FRAMES  ·  NOW LIVE")
d.text((76, 420), "FIGHT THE", font=oswald(110, 600), fill=PAPER); d.text((76, 530), "FUTURE.", font=oswald(110, 600), fill=PAPER)
bottom = grid(img, FTF, fr, 670, cols=2, aspect=816 / 1920)
d = ImageDraw.Draw(img); d.text((80, bottom + 22), "Filter: The Hallway Scene  ·  112 frames, one button", font=mono(26), fill=MUTED)
d.text((80, bottom + 90), "SEASONS 6–11 ARE CAPTURING NOW.", font=oswald(44, 500), fill=PAPER)
footer(d, 8); save(img, 8, "Fight the Future")
print("wrote", sorted(os.listdir(OUT)))
