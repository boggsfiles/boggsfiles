"""One story frame for the Conduit Script vs. Screen report, 1080x1920.

A single finding, not a summary. The report has twelve, but a story frame gets about three
seconds, so it carries the one that needs no context: the line that loses her name between the
page and the broadcast.

Laid out for the story safe area, y 300..1620, and the link box at the bottom is sized to sit
under a link sticker.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
TOP, BOT = 300, 1620
INK = (11, 14, 13); PAPER = (232, 230, 220); PAPER2 = (212, 218, 207)
QUOTE_INK = (34, 41, 31); SIGNAL = (183, 56, 49); MUTED = (132, 142, 134); LINE = (46, 52, 49)
HERE = Path(__file__).resolve().parent
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/IG Story - Conduit"
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
    x0, y0, x1, y1 = box
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    d.text((round((x0 + x1) / 2 - (l + r) / 2), round((y0 + y1) / 2 - (t + b) / 2)), text, font=font, fill=fill)
def panel(img, d, y, label, text, tone):
    f = mono(29); lines = wrap(d, text, f, W - 180 - 60); ph = 84 + len(lines) * 42 + 14
    d.rectangle((90, y, W - 90, y + ph), fill=PAPER2 if tone == "aired" else PAPER)
    d.rectangle((90, y, 96, y + ph), fill=(74, 143, 224) if tone == "aired" else SIGNAL)
    d.text((126, y + 26), label, font=mono(22, "Medium"), fill=(90, 96, 88))
    yy = y + 72
    for ln in lines: d.text((126, yy), ln, font=f, fill=QUOTE_INK); yy += 42
    return y + ph

img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
brand(d)
d.text((90, TOP + 92), "SCRIPT VS. SCREEN  ·  CONDUIT  ·  1X03", font=mono(24, "Medium"), fill=SIGNAL)
d.line((90, TOP + 140, W - 90, TOP + 140), fill=LINE, width=2)

y = 520
d.text((90, y), "HE SAID", font=osw(112, 600), fill=PAPER); y += 118
d.text((90, y), "HER NAME.", font=osw(112, 600), fill=PAPER); y += 118
d.text((90, y), "THE EDIT TOOK IT.", font=osw(72, 600), fill=SIGNAL); y += 118

y = panel(img, d, y + 34, "SCRIPT  ·  2ND BLUE, SCENE 42",
          "“I’m still walking into that room, Scully.”", "script")
y = panel(img, d, y + 16, "AIRED  ·  DVD CAPTIONS",
          "“You know, I’m still walking into that room… every day of my life.”", "aired")

y = para(d, 90, y + 34, "He tells her about closing his eyes before walking into his childhood "
                        "bedroom, hoping Samantha would be there. The beat survives. The direct "
                        "address does not.", mono(27), fill=MUTED, lh=40)

box = (90, y + 46, W - 90, y + 46 + 120)
d.rectangle(box, outline=SIGNAL, width=4)
center_in(d, box, "READ ALL 12 FINDINGS", osw(46, 600), PAPER)
# both on one baseline, clear of the reply bar
foot_y = min(box[3] + 34, BOT - 40)
d.text((90, foot_y), "Conduit aired 33 years ago this Thursday.", font=mono(25), fill=MUTED)
d.text((W - 90, foot_y + 1), "boggsfiles.com", font=mono(25), fill=MUTED, anchor="ra")
img.save(OUT / "conduit-vs-screen.png")
print("wrote", OUT / "conduit-vs-screen.png")
