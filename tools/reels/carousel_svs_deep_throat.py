"""Instagram carousel (8 slides, 1080x1350): Script vs. Screen, Deep Throat (1X01).
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
EP = Path.home() / "Movies/XF_screencaps/series/S01/1X01 Deep Throat/full"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Carousel - Script vs Screen (Deep Throat)"
OUT.mkdir(parents=True, exist_ok=True)
N = 8; CODE = "1X01"

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

EYE = f"THE X-FILES  ·  DEEP THROAT  /  {CODE}"
k = 0
def new():
    global k; k += 1
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img); header(d, EYE); return img, d
def done(img, d):
    footer(d, k); img.save(OUT / f"{k:02d}.png")

# 1 · hook
img, d = new()
y = 430
for ln in ["BLEVINS", "HAD A SCENE."]: d.text((80, y), ln, font=oswald(118, 600), fill=PAPER); y += 124
d.text((80, y + 8), "Deep Throat cut him.", font=oswald(48, 400), fill=MUTED)
still(img, "000157507.jpg", (80, 760, 920, 400))
d.text((80, 1176), "SWIPE FOR THE EVIDENCE", font=mono(24, "Medium"), fill=SIGNAL); ax = 80 + d.textlength("SWIPE FOR THE EVIDENCE", font=mono(24, "Medium")) + 18; d.line((ax, 1191, ax + 40, 1191), fill=SIGNAL, width=3); d.polygon([(ax + 40, 1191), (ax + 28, 1182), (ax + 28, 1200)], fill=SIGNAL)
done(img, d)

# 2 · Blevins
img, d = new()
d.text((80, 430), "A SECTION CHIEF WHO", font=oswald(64, 600), fill=PAPER)
d.text((80, 500), "NEVER SAYS A WORD.", font=oswald(64, 600), fill=PAPER)
y = para(d, 80, 592, "Blevins corners Scully at the microfiche reader and orders her field report to read like wasted Bureau time. He is in the cast list. He is not in the episode. The scene is in all three drafts, word for word.", mono(26), fill=PAPER, lh=38)
y = panel(img, d, y + 22, "SCRIPT  ·  ALL THREE DRAFTS", "“Because Blevins has it out for you already. And it’d make both of us appear pretty stupid if my field report read like some tabloid story.”", "script")
y = panel(img, d, y + 12, "AIRED  ·  DVD CAPTIONS", "“The Bureau has it out for us already and it would make us appear pretty stupid if my field report read like some tabloid story.”", "aired")
done(img, d)

# 3 · happy hour in Paris
img, d = new()
d.text((80, 430), "WRITTEN IN. STILL CUT.", font=oswald(64, 600), fill=PAPER)
still(img, "000164631.jpg", (80, 520, 920, 430))
y = panel(img, d, 972, "SCRIPT  ·  YELLOW", "“It’s two in the afternoon.” / “Yeah, but it’s happy hour in Paris.”", "script")
para(d, 80, y + 14, "Added at the Pink revision. Survived to the shooting draft. Never aired.", mono(23), fill=MUTED, lh=32)
done(img, d)

# 4 · paranormal bouquet
img, d = new()
d.text((80, 430), "NOT IN ANY DRAFT.", font=oswald(64, 600), fill=PAPER)
still(img, "000265365.jpg", (80, 520, 920, 430))
y = panel(img, d, 972, "AIRED ONLY", "“Let’s just say this case has a distinct smell to it. A certain... paranormal bouquet.”", "aired")
para(d, 80, y + 14, "Not in the First Draft, Blue, or Yellow. Written later, or improvised.", mono(23), fill=MUTED, lh=32)
done(img, d)

# 5 · wake up
img, d = new()
d.text((80, 430), "“SCULLY! WAKE UP!", font=oswald(64, 600), fill=PAPER)
d.text((80, 500), "YOU’VE GOT TO SEE THIS!”", font=oswald(64, 600), fill=PAPER)
still(img, "001013446.jpg", (80, 596, 920, 520))
para(d, 80, 1140, "He does not want a witness. He wants her to see it. On the page and on screen.", mono(24), fill=PAPER, lh=34)
done(img, d)

# 6 · military UFO
img, d = new()
d.text((80, 430), "A QUESTION HE", font=oswald(64, 600), fill=PAPER)
d.text((80, 500), "NEVER ASKED ON THE PAGE.", font=oswald(64, 600), fill=PAPER)
still(img, "002631429.jpg", (80, 596, 920, 440))
y = panel(img, d, 1058, "AIRED  ·  NOT IN ANY DRAFT", "“You have to tell me what it was. A military U.F.O.?” Then eight seconds of silence.", "aired")
done(img, d)

# 7 · the report card
img, d = new()
d.text((80, 430), "SHE BACKED HIM UP.", font=oswald(64, 600), fill=PAPER)
d.text((80, 500), "ON THE RECORD.", font=oswald(64, 600), fill=PAPER)
still(img, "002567565.jpg", (80, 596, 920, 440))
y = panel(img, d, 1058, "AIRED  ·  CLOSING TEXT CARD  ·  NOT IN ANY DRAFT", "“Though this agent can corroborate Agent Mulder’s eyewitness account of two unidentified flying objects...”", "aired")
done(img, d)

# 8 · closer
img, d = new()
y = 430
for ln in ["THE FULL", "REPORT IS ON", "THE ARCHIVE."]: d.text((80, y), ln, font=oswald(112, 600), fill=PAPER); y += 118
para(d, 80, y + 34, "Three drafts, eleven findings, every line that changed.", mono(28), fill=MUTED, lh=40)
still(img, "002517465.jpg", (80, 900, 920, 250))
d.text((80, 1176), "boggsfiles.com/script-vs-screen", font=mono(28, "Medium"), fill=SIGNAL)
done(img, d)
print("wrote", k, "slides to", OUT)
