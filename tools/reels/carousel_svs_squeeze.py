"""Instagram carousel (7 slides, 1080x1350): Script vs. Screen, Squeeze (1X02), for the Sept 24 anniversary.
Same house style as the Deep Throat post: logo from the site's CSS (Oswald 500, .16em tracking, signal-red
circle on the X) at y=250 below the IG username overlay; DM Mono eyebrows and captions; paper quote panels
for SCRIPT vs AIRED, matching the site's comparison layout.

Stills come from the xfilesarchive.com Blu-ray gallery (about 1290x726), the same source the site's episode
stills use, NOT from ~/Movies/XF_screencaps (720x540, which upscales badly at this size).
"""
from pathlib import Path
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1350
INK = (11, 14, 13); PAPER = (232, 230, 220); PAPER2 = (212, 218, 207); QUOTE_INK = (34, 41, 31)
SIGNAL = (183, 56, 49); MUTED = (126, 137, 129); LINE = (44, 50, 48)
HERE = Path(__file__).resolve().parent
CACHE = HERE / "stills_cache/squeeze"; CACHE.mkdir(parents=True, exist_ok=True)
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Carousel - Script vs Screen (Squeeze)"
OUT.mkdir(parents=True, exist_ok=True)
N = 7; CODE = "1X02"

def gallery(n):
    """SqueezeBR<n>.jpg from the Blu-ray gallery, cached locally. The host needs a browser User-Agent."""
    p = CACHE / f"SqueezeBR{n}.jpg"
    if not p.exists():
        req = urllib.request.Request(f"https://xfilesarchive.com/gallery/SqueezeBR{n}.jpg",
                                     headers={"User-Agent": "Mozilla/5.0"})
        p.write_bytes(urllib.request.urlopen(req, timeout=30).read())
    return p

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
def still(img, n, box, centering=(0.5, 0.3)):
    x, y, w, h = box; im = Image.open(gallery(n)).convert("RGB")
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=centering); img.paste(im, (x, y))
    ImageDraw.Draw(img).rectangle((x, y, x + w - 1, y + h - 1), outline=LINE, width=2)
def panel(img, d, y, label, text, tone, h=None):
    f = mono(25); lines = wrap(d, text, f, W - 160 - 50); ph = h or (70 + len(lines) * 36 + 10)
    d.rectangle((80, y, W - 80, y + ph), fill=PAPER2 if tone == "aired" else PAPER)
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

# 1 - hook
img, d = new()
y = 430
for ln in ["33 YEARS", "AGO TONIGHT."]: d.text((80, y), ln, font=oswald(118, 600), fill=PAPER); y += 124
d.text((80, y + 8), "Four drafts. The last line is in none of them.", font=oswald(40, 400), fill=MUTED)
still(img, 276, (80, 760, 920, 400))
d.text((80, 1176), "SWIPE FOR THE EVIDENCE", font=mono(24, "Medium"), fill=SIGNAL)
ax = 80 + d.textlength("SWIPE FOR THE EVIDENCE", font=mono(24, "Medium")) + 18
d.line((ax, 1191, ax + 40, 1191), fill=SIGNAL, width=3)
d.polygon([(ax + 40, 1191), (ax + 28, 1182), (ax + 28, 1200)], fill=SIGNAL)
done(img, d)

# 2 - the last line
img, d = new()
d.text((80, 430), "THE LINE YOU REMEMBER", font=oswald(58, 600), fill=PAPER)
d.text((80, 496), "IS IN NO DRAFT.", font=oswald(58, 600), fill=PAPER)
y = para(d, 80, 584, "White, Pink, Green and the true final Yellow all close the episode on the same sentence. "
                     "The DVD captions show something else entirely aired.", mono(26), fill=PAPER, lh=38)
y = panel(img, d, y + 20, "SCRIPT  ·  ALL FOUR DRAFTS, IDENTICAL",
          "“I look at him and wonder... what’s next?”", "script")
y = panel(img, d, y + 12, "AIRED  ·  DVD CAPTIONS",
          "“I look at this guy, and I think, ‘It ain’t enough.’”", "aired")
para(d, 80, y + 16, "Written after the last archived draft. At the table read, on set, or in a polish nobody kept.",
     mono(23), fill=MUTED, lh=32)
done(img, d)

# 3 - the necklace scene
img, d = new()
d.text((80, 430), "HE NOTICED", font=oswald(64, 600), fill=PAPER)
d.text((80, 500), "THE NECKLACE.", font=oswald(64, 600), fill=PAPER)
still(img, 164, (80, 596, 920, 350))
y = panel(img, d, 972, "SCRIPT ONLY", "MULDER: The worse the day gets, the faster the necklace twirls.", "script")
para(d, 80, y + 14, "Cut for broadcast, and it was the last scene they ever touched.",
     mono(23), fill=MUTED, lh=32)
done(img, d)

# 4 - Mr. Lee
img, d = new()
d.text((80, 430), "A WHOLE SCENE.", font=oswald(64, 600), fill=PAPER)
d.text((80, 500), "ONE LINE ON AIR.", font=oswald(64, 600), fill=PAPER)
still(img, 212, (80, 596, 920, 350))
y = panel(img, d, 972, "AIRED  ·  DVD CAPTIONS",
          "“Baltimore P.D. checked out Tooms’s apartment. It was a cover.”", "aired")
para(d, 80, y + 14, "Superintendent, empty apartment, phone call. In all four drafts.",
     mono(23), fill=MUTED, lh=32)
done(img, d)

# 5 - Spooky
img, d = new()
d.text((80, 430), "“SPOOKY” WAS", font=oswald(64, 600), fill=PAPER)
d.text((80, 500), "AN ASIDE.", font=oswald(64, 600), fill=PAPER)
still(img, 300, (80, 596, 920, 350))
y = panel(img, d, 972, "SCRIPT  ·  ALL FOUR DRAFTS", "KENNEDY: You got it... (to Kramer) ...Spooky.", "script")
para(d, 80, y + 14, "On air there is no pivot to a partner. It is said straight to his face.",
     mono(23), fill=MUTED, lh=32)
done(img, d)

# 6 - Colton's demotion
img, d = new()
d.text((80, 430), "COLTON NEVER", font=oswald(64, 600), fill=PAPER)
d.text((80, 500), "GOT WHAT HE HAD COMING.", font=oswald(46, 600), fill=PAPER)
still(img, 12, (80, 596, 920, 330))
y = panel(img, d, 952, "SCRIPT ONLY  ·  SCULLY’S CLOSING UPDATE",
          "“He’s been bumped off the Violent Crime Section and reassigned to white collar crime.”", "script")
para(d, 80, y + 14, "In every draft. Cut on the way to broadcast.", mono(23), fill=MUTED, lh=32)
done(img, d)

# 7 - closer
img, d = new()
y = 430
for ln in ["THE FULL", "REPORT IS ON", "THE ARCHIVE."]: d.text((80, y), ln, font=oswald(112, 600), fill=PAPER); y += 118
para(d, 80, y + 34, "Four drafts, fourteen findings, every line that changed.", mono(28), fill=MUTED, lh=40)
still(img, 352, (80, 900, 920, 250))
d.text((80, 1176), "boggsfiles.com/script-vs-screen", font=mono(28, "Medium"), fill=SIGNAL)
done(img, d)
print("wrote", k, "slides to", OUT)
