"""Instagram carousel (6 slides, 1080x1350): Squeeze aired Sep 24, 1993. Anniversary post, screencaps from the archive.
Same house style as the Pilot 'Scully had a boyfriend' post: logo from the site's CSS (Oswald 500, .16em
tracking, signal-red circle on the X) at y=250 below the IG username overlay; DM Mono eyebrows and
captions; paper quote panels for SCRIPT vs AIRED, matching the site's comparison layout.
Stills come from the character-tagged screencap archive."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1350
INK = (11, 14, 13); PAPER = (232, 230, 220); PAPER2 = (212, 218, 207); QUOTE_INK = (34, 41, 31)
SIGNAL = (183, 56, 49); MUTED = (126, 137, 129); LINE = (44, 50, 48)
HERE = Path(__file__).resolve().parent
EP = Path.home() / "Movies/XF_screencaps/series/S01/1X02 Squeeze/full"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Carousel - Squeeze 33 years"
OUT.mkdir(parents=True, exist_ok=True)
N = 6; CODE = "1X02"

def oswald(size, wght=500):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), size); f.set_variation_by_axes([wght]); return f
def mono(size, w="Regular"): return ImageFont.truetype(str(HERE / f"fonts/DMMono-{w}.ttf"), size)

LOGO_Y = 250
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
    brand(d); d.text((80, LOGO_Y + 95), eyebrow, font=mono(26, "Medium"), fill=SIGNAL)
    d.line((80, LOGO_Y + 140, W - 80, LOGO_Y + 140), fill=LINE, width=2)
def footer(d, k):
    d.line((80, H - 130, W - 80, H - 130), fill=LINE, width=2)
    d.text((80, H - 100), f"BOGGSFILES.COM  ·  {CODE}", font=mono(26), fill=PAPER)
    d.text((W - 80, H - 98), f"{k:02d} / {N:02d}", font=mono(24), fill=MUTED, anchor="ra")
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
def still(img, frame, box):
    """Paste a screencap, cover-cropped into box=(x,y,w,h), with the site's thin border."""
    x, y, w, h = box; im = Image.open(EP / frame).convert("RGB")
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, 0.3)); img.paste(im, (x, y))
    ImageDraw.Draw(img).rectangle((x, y, x + w - 1, y + h - 1), outline=LINE, width=2)
def panel(img, d, y, label, text, tone, h=None):
    """Paper quote panel like the site's .quote / .quote.aired; returns bottom y."""
    f = mono(25); lines = wrap(d, text, f, W - 160 - 50); ph = h or (70 + len(lines) * 36 + 10)
    bg = PAPER2 if tone == "aired" else PAPER
    d.rectangle((80, y, W - 80, y + ph), fill=bg)
    d.rectangle((80, y, 84, y + ph), fill=(74, 143, 224) if tone == "aired" else SIGNAL)
    d.text((110, y + 22), label, font=mono(20, "Medium"), fill=(90, 96, 88))
    yy = y + 60
    for ln in lines: d.text((110, yy), ln, font=f, fill=QUOTE_INK); yy += 36
    return y + ph

EYE = f"THE X-FILES  ·  SQUEEZE  /  {CODE}  ·  SEPTEMBER 24, 1993"
k = 0
def new():
    global k; k += 1
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img); header(d, EYE); return img, d
def done(img, d):
    footer(d, k); img.save(OUT / f"{k:02d}.png")

img, d = new()
y = 430
for ln in ["33 YEARS", "AGO TONIGHT."]: d.text((80, y), ln, font=oswald(118, 600), fill=PAPER); y += 124
d.text((80, y + 8), "The episode that made the show.", font=oswald(44, 400), fill=MUTED)
still(img, "000981147.jpg", (80, 760, 920, 400))
d.text((80, 1176), "SWIPE", font=mono(24, "Medium"), fill=SIGNAL); ax = 80 + d.textlength("SWIPE", font=mono(24, "Medium")) + 18; d.line((ax, 1191, ax + 40, 1191), fill=SIGNAL, width=3); d.polygon([(ax + 40, 1191), (ax + 28, 1182), (ax + 28, 1200)], fill=SIGNAL)
done(img, d)

SLIDES = [
 ("000521654.jpg", "THE BASEMENT.", "Episode three. The first monster of the week, and the first time the office feels like theirs."),
 ("001598881.jpg", "EUGENE VICTOR TOOMS.", "Five livers every thirty years, since 1903. Mulder and Scully work it out at the window."),
 ("001919935.jpg", "THE NEST.", "66 Exeter Street. Newspaper, bile, and a very patient landlord."),
 ("002293792.jpg", "THE VENT.", "The shot every kid who watched in 1993 still checks the bathroom for."),
 ("001010810.jpg", "STILL THE ONE.", "Written by Glen Morgan and James Wong. Tooms came back in Season 1. So will this. boggsfiles.com/screencaps"),
]
for frame, head, cap in SLIDES:
    img, d = new()
    d.text((80, 430), head, font=oswald(64, 600), fill=PAPER)
    still(img, frame, (80, 520, 920, 560))
    para(d, 80, 1104, cap, mono(24), fill=PAPER, lh=34)
    done(img, d)
print("wrote", k, "slides to", OUT)
