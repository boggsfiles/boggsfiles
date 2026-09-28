"""The "Start Here" highlight: five story frames, 1080x1920.

Same house style as the highlight covers and the carousels. Laid out for the story safe area:
Instagram covers roughly the top 250px with the account row and the bottom 240px with the reply
bar, so nothing important goes outside y 300..1620.

Figures are deliberately rounded where the collection is still growing, because a highlight is
evergreen and exact counts go stale. "Every episode" is used where the set is actually complete.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
TOP, BOT = 300, 1620
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49)
MUTED = (132, 142, 134); LINE = (46, 52, 49)
HERE = Path(__file__).resolve().parent
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/IG Story - Start Here"
OUT.mkdir(parents=True, exist_ok=True)

def osw(s, w=600):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), s); f.set_variation_by_axes([w]); return f
def mono(s, w="Regular"): return ImageFont.truetype(str(HERE / f"fonts/DMMono-{w}.ttf"), s)

def tracked(d, x, y, s, f, fill, track):
    for ch in s: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
    return x
def brand(d, x=90, y=TOP, size=46):
    f = osw(size, 500); t = 0.16 * size
    x = tracked(d, x, y, "BOGGS", f, PAPER, t); x += 0.34 * size - t
    xw = d.textlength("X", font=f); d.text((x, y), "X", font=f, fill=PAPER)
    asc, _ = f.getmetrics(); cx, cy = x + xw / 2, y + asc * 0.62; r = 1.08 * size / 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=SIGNAL, width=4)
    tracked(d, x + xw + 0.34 * size, y, "FILES", f, PAPER, t)
def wrap(d, s, f, maxw):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
def para(d, x, y, s, f, fill=PAPER, maxw=W - 180, lh=None):
    lh = lh or int(f.size * 1.42)
    for ln in wrap(d, s, f, maxw): d.text((x, y), ln, font=f, fill=fill); y += lh
    return y

def center_in(d, box, text, font, fill):
    """Centre text on its actual ink, not its font metrics: anchor="ma" hangs it off the
    ascender, which includes the empty space above the caps and reads as sitting low."""
    x0, y0, x1, y1 = box
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    d.text((round((x0 + x1) / 2 - (l + r) / 2), round((y0 + y1) / 2 - (t + b) / 2)),
           text, font=font, fill=fill)

k = 0
BAND_TOP, BAND_BOT = TOP + 150, BOT - 90     # where a frame's content is allowed to live

def frame():
    """Content is drawn onto a transparent layer so it can be centred once its height is known."""
    global k; k += 1
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return layer, ImageDraw.Draw(layer)

def done(layer, d, hint=None):
    img = Image.new("RGB", (W, H), INK)
    bbox = layer.getbbox()
    if bbox:
        dy = round((BAND_TOP + BAND_BOT) / 2 - (bbox[1] + bbox[3]) / 2)
        shifted = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        shifted.paste(layer, (0, dy))
        layer = shifted
    img.paste(layer, (0, 0), layer)
    dd = ImageDraw.Draw(img)
    brand(dd); dd.line((90, TOP + 96, W - 90, TOP + 96), fill=LINE, width=2)
    if hint:
        f = mono(26, "Medium")
        dd.text((90, BOT - 4), hint, font=f, fill=SIGNAL)
        ax = 90 + dd.textlength(hint, font=f) + 20; ay = BOT + 13
        dd.line((ax, ay, ax + 40, ay), fill=SIGNAL, width=4)
        dd.polygon([(ax + 40, ay), (ax + 28, ay - 9), (ax + 28, ay + 9)], fill=SIGNAL)
    dd.text((W - 90, BOT - 2), f"{k} / 5", font=mono(24), fill=MUTED, anchor="ra")
    img.save(OUT / f"{k:02d}.png")

# 1 — what this is
img, d = frame()
y = 470
for ln in ["AN", "X-FILES", "ARCHIVE."]:
    d.text((90, y), ln, font=osw(146, 600), fill=PAPER); y += 152
y = para(d, 90, y + 44, "Rare scripts, transcripts, screencaps, gag reels and production paperwork. "
                        "Collected over thirty years.", mono(30), fill=MUTED, lh=46)
d.line((90, y + 52, 250, y + 52), fill=SIGNAL, width=5)
done(img, d, "KEEP TAPPING")

# 2 — the scale
img, d = frame()
d.text((90, 470), "WHAT'S IN IT", font=osw(96, 600), fill=PAPER)
rows = [("500+",     "script drafts, seasons 1 to 11"),
        ("EVERY",    "episode, transcribed from the discs"),
        ("230,000+", "screencaps, frame by frame"),
        ("21",       "production documents, newly added")]
y = 640
for big, small in rows:
    d.text((90, y), big, font=osw(82, 600), fill=SIGNAL)
    d.text((90, y + 96), small, font=mono(27), fill=PAPER)
    y += 190
    if (big, small) != rows[-1]:
        d.line((90, y - 46, W - 90, y - 46), fill=LINE, width=2)
done(img, d)

# 3 — the rarer things
img, d = frame()
d.text((90, 470), "AND THE", font=osw(96, 600), fill=PAPER)
d.text((90, 566), "RARE STUFF", font=osw(96, 600), fill=PAPER)
items = ["Gag reels, straight off the masters",
         "Dailies from 14 episodes",
         "Script vs. Screen: every line that changed between the page and the broadcast",
         "Location scout folders from the Los Angeles years",
         "Second unit memos on their original revision paper"]
y = 728
for it in items:
    d.ellipse((92, y + 12, 108, y + 28), fill=SIGNAL)
    y = para(d, 140, y, it, mono(28), fill=PAPER, maxw=W - 240, lh=42) + 34
done(img, d)

# 4 — the price
img, d = frame()
y = 520
for ln in ["FREE.", "NO ACCOUNT.", "NO PAYWALL."]:
    d.text((90, y), ln, font=osw(128, 600), fill=PAPER); y += 138
y = para(d, 90, y + 56, "Nothing here is for sale and nothing is behind a login. "
                        "It is an archive, not a shop.", mono(30), fill=MUTED, lh=46)
d.line((90, y + 56, 250, y + 56), fill=SIGNAL, width=5)
done(img, d)

# 5 — the link
img, d = frame()
y = 500
for ln in ["START", "READING."]:
    d.text((90, y), ln, font=osw(150, 600), fill=PAPER); y += 158
y = para(d, 90, y + 44, "Everything above is one tap away. New files go up most weeks.",
         mono(30), fill=MUTED, lh=46)
box_y = y + 80
BOX = (90, box_y, W - 90, box_y + 132)
d.rectangle(BOX, outline=SIGNAL, width=4)
center_in(d, BOX, "BOGGSFILES.COM", osw(58, 600), PAPER)
d.text((90, box_y + 186), "Link in bio", font=mono(30, "Medium"), fill=MUTED)
done(img, d)

print(f"wrote {k} frames to {OUT}")
