"""Instagram carousel (8 slides, 1080x1350): the handwritten insert list for 5X06.

One page of source material, so the carousel works by moving through it: the whole sheet first,
then crops of individual lines at a size where the handwriting is the point. Crop boxes are
fractions of the 300dpi render and were each checked by eye before being used here.

House style matches the 2nd Unit and Script vs. Screen posts.
"""
import subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49)
MUTED = (126, 137, 129); LINE = (44, 50, 48)
HERE = Path(__file__).resolve().parent
PDF = (Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/2nd Unit & Production Schedules/Post Modern Prometheus Insert.pdf")
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Carousel - Insert List (5X06)"
OUT.mkdir(parents=True, exist_ok=True)
N = 8

def oswald(size, wght=500):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), size); f.set_variation_by_axes([wght]); return f
def mono(size, w="Regular"): return ImageFont.truetype(str(HERE / f"fonts/DMMono-{w}.ttf"), size)

LOGO_Y = 250
def tracked(d, x, y, s, f, fill, track):
    for ch in s: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
    return x
def brand(d, x=80, y=LOGO_Y, size=52):
    f = oswald(size, 500); t = 0.16 * size
    x = tracked(d, x, y, "BOGGS", f, PAPER, t); x += 0.34 * size - t
    xw = d.textlength("X", font=f); d.text((x, y), "X", font=f, fill=PAPER)
    asc, _ = f.getmetrics(); cx, cy = x + xw / 2, y + asc * 0.62; r = 1.08 * size / 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=SIGNAL, width=max(3, round(size * 2 / 23.2)))
    tracked(d, x + xw + 0.34 * size, y, "FILES", f, PAPER, t)
def wrap(d, s, f, maxw):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
def para(d, x, y, s, f, fill=PAPER, maxw=W - 160, lh=None):
    lh = lh or int(f.size * 1.35)
    for ln in wrap(d, s, f, maxw): d.text((x, y), ln, font=f, fill=fill); y += lh
    return y

# render the page once at 300dpi
with tempfile.TemporaryDirectory() as td:
    subprocess.run(["pdftoppm", "-r", "300", "-jpeg", "-jpegopt", "quality=95", str(PDF), f"{td}/p"], check=True)
    PAGE = Image.open(next(Path(td).glob("p*.jpg"))).convert("RGB").copy()
PW, PH = PAGE.size

def crop(frac):
    x0, y0, x1, y1 = frac
    return PAGE.crop((int(PW*x0), int(PH*y0), int(PW*x1), int(PH*y1)))

def place(img, im, box):
    """Fit a document crop inside a box, centred, with a hairline edge."""
    x, y, bw, bh = box
    im = im.copy(); im.thumbnail((bw, bh), Image.LANCZOS)
    px, py = x + (bw - im.width)//2, y + (bh - im.height)//2
    img.paste(im, (px, py))
    ImageDraw.Draw(img).rectangle((px, py, px+im.width-1, py+im.height-1), outline=(70, 76, 72), width=2)
    return py + im.height

EYE = "PRODUCTION DOCUMENTS  ·  5X06  ·  THE POST-MODERN PROMETHEUS"
k = 0
def new():
    global k; k += 1
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
    brand(d); d.text((80, LOGO_Y + 88), EYE, font=mono(21, "Medium"), fill=SIGNAL)
    d.line((80, LOGO_Y + 132, W - 80, LOGO_Y + 132), fill=LINE, width=2)
    return img, d
def done(img, d):
    d.line((80, H - 124, W - 80, H - 124), fill=LINE, width=2)
    d.text((80, H - 96), "BOGGSFILES.COM", font=mono(25), fill=PAPER)
    d.text((W - 80, H - 94), f"{k:02d} / {N:02d}", font=mono(23), fill=MUTED, anchor="ra")
    img.save(OUT / f"{k:02d}.jpg", quality=94)

BAND_TOP, BAND_BOT = 408, H - 150          # everything between the rule and the footer

def slide(title, blurb, frac, tsize=60):
    """Measure the whole title + blurb + document group, then centre it in the band, so a one line
    crop and a full page both sit level instead of floating in whatever box is left over."""
    img, d = new()
    th = int(tsize * 1.08) * len(title)
    bl = wrap(d, blurb, mono(24), W - 160) if blurb else []
    bh = (18 + 34 * len(bl)) if bl else 0
    im = crop(frac); im.thumbnail((W - 160, BAND_BOT - BAND_TOP - th - bh - 34), Image.LANCZOS)
    total = th + bh + 34 + im.height
    y = BAND_TOP + (BAND_BOT - BAND_TOP - total) // 2
    for ln in title: d.text((80, y), ln, font=oswald(tsize, 600), fill=PAPER); y += int(tsize * 1.08)
    if bl:
        y += 18
        for ln in bl: d.text((80, y), ln, font=mono(24), fill=MUTED); y += 34
    y += 34
    px = 80 + (W - 160 - im.width) // 2
    img.paste(im, (px, y))
    d.rectangle((px, y, px + im.width - 1, y + im.height - 1), outline=(70, 76, 72), width=2)
    done(img, d)

# 01 - the whole sheet
img, d = new()
y = 400
for ln in ["SOMEBODY WROTE", "THIS BY HAND."]: d.text((80, y), ln, font=oswald(62, 600), fill=PAPER); y += 68
d.text((80, y + 14), "On set. In 1997. On goldenrod paper.", font=mono(24), fill=MUTED)
top = y + 64
page = PAGE.copy(); page.thumbnail((W - 160, H - 176 - top), Image.LANCZOS)
px = 80 + (W - 160 - page.width) // 2
img.paste(page, (px, top))
d.rectangle((px, top, px + page.width - 1, top + page.height - 1), outline=(70, 76, 72), width=2)
d.text((80, H - 150), "SWIPE", font=mono(23, "Medium"), fill=SIGNAL)
ax = 80 + d.textlength("SWIPE", font=mono(23, "Medium")) + 16
d.line((ax, H - 139, ax + 34, H - 139), fill=SIGNAL, width=3)
d.polygon([(ax + 34, H - 139), (ax + 24, H - 147), (ax + 24, H - 131)], fill=SIGNAL)
done(img, d)

# 02 - what it is
slide(["A SCRIPT", "SUPERVISOR'S", "INSERT LIST."],
      "Every close-up the main unit still owed, written down as they went. "
      "Nobody keeps these. They get used up and thrown out.",
      (.06, .015, .99, .11), tsize=56)

# 03 - the animals
slide(["THE CELLAR", "SHOPPING LIST."],
      "Scene 60. One line per animal, in the order they needed them.",
      (.06, .620, .99, .800), tsize=62)

# 04 - goat boy
slide(["“GOAT BOY”", "IS A STAGE", "DIRECTION."],
      "Scene 1, exterior Berkowitz house. CU, close up, GOAT BOY LKS INTO CAR.",
      (.06, .470, .99, .530), tsize=58)

# 05 - the egg
slide(["ONE EGG.", "ON A PLATE."],
      "Scene 47, the diner. (M) means it has to match Mulder's eyeline.",
      (.06, .545, .99, .625), tsize=64)

# 06 - the tape recorder
slide(["PLAY.", "REWIND.", "PLAY."],
      "Scene 31, the Berkowitz living room. The whole action of a shot, in six words.",
      (.06, .365, .99, .460), tsize=70)

# 07 - jerry springer
slide(["AND A TV", "PLAYING", "JERRY SPRINGER."],
      "Last line on the page. Scene 2, Shaineh's bedroom.",
      (.06, .845, .99, .905), tsize=54)

# 08 - closer
img, d = new()
y = 430
for ln in ["23 DOCUMENTS", "LIKE THIS", "ARE ON THE SITE."]: d.text((80, y), ln, font=oswald(74, 600), fill=PAPER); y += 80
y = para(d, 80, y + 28, "Second unit memos, season schedules, prep calendars and insert lists. "
                        "Seasons 5 and 8, scanned in full color on their original stock. "
                        "Free to read, no account.", mono(25), fill=MUTED, lh=36)
_c = crop((.06, .015, .99, .11)); _c.thumbnail((W - 160, H - 210 - (y + 34)), Image.LANCZOS)
_x = 80 + (W - 160 - _c.width)//2
img.paste(_c, (_x, y + 34)); d.rectangle((_x, y + 34, _x + _c.width - 1, y + 33 + _c.height), outline=(70,76,72), width=2)
d.text((80, H - 168), "boggsfiles.com/production-documents", font=mono(26, "Medium"), fill=SIGNAL)
done(img, d)
print(f"wrote {k} slides to {OUT}")
