"""Instagram carousel (10 slides, 1080x1350): the 2nd Unit & Production Schedules section.

House style as the Script vs. Screen posts: logo in Oswald 500 with the signal-red circle on the X
at y=250 (below the IG username overlay), DM Mono eyebrows and captions.

Difference from those posts: the document IS the slide. Each page is placed nearly full bleed with
its own paper color showing, because the color is the revision. No quote panels, no screencaps.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1350
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49)
MUTED = (126, 137, 129); LINE = (44, 50, 48)
HERE = Path(__file__).resolve().parent
PAGES = Path.home() / "Sites/boggsfiles/dist/assets/archive-photos/second-unit"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Carousel - 2nd Unit & Schedules"
OUT.mkdir(parents=True, exist_ok=True)
N = 10

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

def doc(img, slug, box, focus=0.0):
    """Place a page image, cropped from the top by default: the letterhead is the good part."""
    x, y, bw, bh = box
    im = Image.open(PAGES / f"{slug}.webp").convert("RGB")
    s = bw / im.width
    im = im.resize((bw, round(im.height * s)), Image.LANCZOS)
    if im.height > bh:
        top = int((im.height - bh) * focus)
        im = im.crop((0, top, bw, top + bh))
    else:
        bh = im.height
    img.paste(im, (x, y))
    ImageDraw.Draw(img).rectangle((x, y, x + bw - 1, y + bh - 1), outline=(70, 76, 72), width=2)
    return y + bh

k = 0
def new(eyebrow):
    global k; k += 1
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
    brand(d); d.text((80, LOGO_Y + 88), eyebrow, font=mono(23, "Medium"), fill=SIGNAL)
    d.line((80, LOGO_Y + 132, W - 80, LOGO_Y + 132), fill=LINE, width=2)
    return img, d
def done(img, d):
    footer(d, k); img.save(OUT / f"{k:02d}.jpg", quality=93)

EYE = "PRODUCTION DOCUMENTS  ·  NEW ON THE ARCHIVE"

def slide(eyebrow, title, body, slug, focus=0.0, tsize=60):
    img, d = new(eyebrow)
    y = 420
    for ln in title: d.text((80, y), ln, font=oswald(tsize, 600), fill=PAPER); y += int(tsize * 1.09)
    y += 18
    y = para(d, 80, y, body, mono(24), fill=MUTED, lh=35) + 26
    doc(img, slug, (80, y, W - 160, H - 170 - y), focus)
    done(img, d)

# 01 - the hook: paperwork nobody keeps
img, d = new(EYE)
y = 420
for ln in ["NOBODY", "KEEPS THIS", "PAPERWORK."]: d.text((80, y), ln, font=oswald(104, 600), fill=PAPER); y += 110
y = para(d, 80, y + 18, "21 second unit memos, season schedules and prep calendars. "
                        "Superseded in days, then thrown out. These survived.", mono(25), fill=MUTED, lh=36)
doc(img, "01-redux-01", (80, y + 28, W - 160, H - 210 - y))
d.text((80, H - 168), "SWIPE", font=mono(23, "Medium"), fill=SIGNAL)
ax = 80 + d.textlength("SWIPE", font=mono(23, "Medium")) + 16
d.line((ax, H - 155, ax + 36, H - 155), fill=SIGNAL, width=3)
d.polygon([(ax + 36, H - 155), (ax + 25, H - 163), (ax + 25, H - 147)], fill=SIGNAL)
done(img, d)

# 02 - the Directors Schedule, the find
slide(EYE, ["A SEASON BEFORE", "IT HAD NAMES."],
      "Fifth Season Directors Schedule, revised 20 August 1997. Every episode has a director and a "
      "start date. Most of them do not have a title yet.",
      "20-directors-pink-01", focus=0.0, tsize=56)

# 03 - the handwriting, close
img, d = new(EYE)
d.text((80, 420), "SO SOMEBODY", font=oswald(60, 600), fill=PAPER)
d.text((80, 486), "WROTE THEM IN.", font=oswald(60, 600), fill=PAPER)
y = para(d, 80, 578, "Episodes 3 and 4, in blue pen: Redux II, Detour. Below them the title column "
                     "just stops. Directors booked for episodes nobody had written.", mono(24), fill=MUTED, lh=35)
im = Image.open(PAGES / "20-directors-pink-01.webp").convert("RGB")
cw, ch = im.width, im.height
crop = im.crop((int(cw*.05), int(ch*.14), int(cw*.62), int(ch*.36)))
crop = crop.resize((W - 160, round(crop.height * (W - 160) / crop.width)), Image.LANCZOS)
img.paste(crop, (80, y + 34)); d.rectangle((80, y + 34, W - 81, y + 33 + crop.height), outline=(70,76,72), width=2)
done(img, d)

# 04 - Scully & Doggett not available
img, d = new(EYE)
d.text((80, 420), "“SCULLY & DOGGETT", font=oswald(52, 600), fill=PAPER)
d.text((80, 478), "NOT AVAILABLE.”", font=oswald(52, 600), fill=PAPER)
y = para(d, 80, 566, "A tech scout for episode 8ABX09, headed “UNTITLED” because it did not have a "
                     "name yet. It became Surekill.", mono(24), fill=MUTED, lh=35)
im = Image.open(PAGES / "32-surekill-scout-01.webp").convert("RGB")
crop = im.crop((0, 0, im.width, int(im.height * .30)))
crop = crop.resize((W - 160, round(crop.height * (W - 160) / crop.width)), Image.LANCZOS)
img.paste(crop, (80, y + 34)); d.rectangle((80, y + 34, W - 81, y + 33 + crop.height), outline=(70,76,72), width=2)
done(img, d)

# 05 - the color is the revision
slide(EYE, ["THE COLOR IS", "THE REVISION."],
      "Salmon, goldenrod, yellow, green. Every rewrite moved to the next color, so a department "
      "could tell at a glance whether it was holding the current schedule.",
      "07-three-goldenrod-01", focus=0.0, tsize=58)

# 06 - green memo on letterhead
slide(EYE, ["10 OCTOBER 1997."],
      "A memo on green stock about days 11 and 12 of Detour, copied to Goodwin, Finn, French and "
      "Dowler. The only page here on X-F Productions letterhead.",
      "02-detour-memo-01", focus=0.0, tsize=62)

# 07 - three episodes at once
slide(EYE, ["THREE EPISODES,", "ONE SECOND UNIT."],
      "Detour, Christmas Carol and Emily, all running at the same time. Issued 31 October 1997 by "
      "Brett Dowler, and superseded four days later.",
      "05-three-yellow-01", focus=0.0, tsize=56)

# 08 - the inserts themselves
slide(EYE, ["WHAT SECOND", "UNIT SHOOTS."],
      "Emily, remaining inserts: Scully's hand lifting the cross from the sand. Her feet in the sand. "
      "Mulder's POV of the cross. Signed “Kevin”.",
      "10-emily-inserts-02", focus=0.0, tsize=58)

# 09 - the prep calendar
slide(EYE, ["A MONTH, TO", "THE MINUTE."],
      "November 2000 prep calendar, marked “as of 7:20 PM”. Set decoration, an underwater photography "
      "meeting, a location scout, the start of principal photography, Thanksgiving.",
      "30-prep-nov-2000-01", focus=0.12, tsize=58)

# 10 - closer
img, d = new(EYE)
y = 420
for ln in ["ALL 45 PAGES", "ARE ON THE", "ARCHIVE."]: d.text((80, y), ln, font=oswald(100, 600), fill=PAPER); y += 106
y = para(d, 80, y + 26, "21 documents, Seasons 5 and 8, scanned in full color. Free to read, "
                        "no account, no paywall.", mono(25), fill=MUTED, lh=36)
doc(img, "22-s8-goldenrod-01", (80, y + 30, W - 160, H - 230 - y))
d.text((80, H - 178), "boggsfiles.com/production-documents", font=mono(26, "Medium"), fill=SIGNAL)
done(img, d)
print("wrote", k, "slides to", OUT)
