"""Instagram carousel (7 slides, 1080x1350): Script vs. Screen, Conduit (1X03), for the Oct 1 anniversary.

Same house style as the Squeeze and Deep Throat posts: logo from the site's CSS (Oswald 500, .16em
tracking, signal-red circle on the X) at y=250 below the IG username overlay; DM Mono eyebrows and
captions; paper quote panels for SCRIPT vs AIRED, matching the site's comparison layout.

Conduit is the quiet one: it aired unusually close to its shooting draft, so the hook is the absence
of change rather than a cut scene. Four of the seven slides carry caption-confirmed findings.

Stills come from the xfilesarchive.com Blu-ray gallery (about 1290x726), the same source the site's
episode stills use, NOT from ~/Movies/XF_screencaps (720x540, which upscales badly at this size).
BR262 and BR302 are deliberately skipped: they are already the site's transcript still and
Script vs. Screen card for this episode.
"""
from pathlib import Path
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1350
INK = (11, 14, 13); PAPER = (232, 230, 220); PAPER2 = (212, 218, 207); QUOTE_INK = (34, 41, 31)
SIGNAL = (183, 56, 49); MUTED = (126, 137, 129); LINE = (44, 50, 48)
HERE = Path(__file__).resolve().parent
CACHE = HERE / "stills_cache/conduit"; CACHE.mkdir(parents=True, exist_ok=True)
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Carousel - Script vs Screen (Conduit)"
OUT.mkdir(parents=True, exist_ok=True)
N = 7; CODE = "1X03"

def gallery(n):
    """ConduitBR<n>.jpg from the Blu-ray gallery, cached locally. The host needs a browser User-Agent."""
    p = CACHE / f"ConduitBR{n}.jpg"
    if not p.exists():
        req = urllib.request.Request(f"https://xfilesarchive.com/gallery/ConduitBR{n}.jpg",
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
    brand(d); d.text((80, LOGO_Y + 95), eyebrow, font=mono(24, "Medium"), fill=SIGNAL)
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

EYE = f"THE X-FILES  ·  CONDUIT  /  {CODE}  ·  OCTOBER 1, 1993"
TOP, BOTTOM = 430, H - 150          # header rule sits at 390, footer rule at H-130
k = 0
def new():
    global k; k += 1
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img); header(d, EYE); return img, d
def done(img, d):
    footer(d, k); img.save(OUT / f"{k:02d}.png")

def panel_h(d, text):
    return 70 + len(wrap(d, text, mono(25), W - 160 - 50)) * 36 + 10
def note_h(d, text):
    return len(wrap(d, text, mono(23), W - 160)) * 32

def slide(title, still_n, panels, note, tsize=62, centering=(0.5, 0.3)):
    """Title block, then a still sized to whatever the panels and closing note leave over."""
    img, d = new()
    y = TOP
    for ln in title: d.text((80, y), ln, font=oswald(tsize, 600), fill=PAPER); y += int(tsize * 1.09)
    y += 24
    below = sum(panel_h(d, t) for _, t in panels) + 12 * (len(panels) - 1) + 18 + note_h(d, note)
    still(img, still_n, (80, y, 920, BOTTOM - below - y - 22), centering=centering)
    y = BOTTOM - below
    for i, (label, text) in enumerate(panels):
        y = panel(img, d, y, label, text, "aired" if label.startswith("AIRED") else "script")
        y += 12
    para(d, 80, y + 6, note, mono(23), fill=MUTED, lh=32)
    done(img, d)

# 1 - hook: the absence of change is the story
img, d = new()
y = TOP
for ln in ["ALMOST", "NOTHING", "CHANGED."]: d.text((80, y), ln, font=oswald(112, 600), fill=PAPER); y += 118
y = para(d, 80, y + 14, "Which is why the few things that did are worth reading.",
         oswald(36, 400), fill=MUTED, lh=44)
still(img, 44, (80, y + 30, 920, BOTTOM - 64 - (y + 30)))
d.text((80, BOTTOM - 40), "SWIPE FOR THE EVIDENCE", font=mono(24, "Medium"), fill=SIGNAL)
ax = 80 + d.textlength("SWIPE FOR THE EVIDENCE", font=mono(24, "Medium")) + 18
d.line((ax, BOTTOM - 25, ax + 40, BOTTOM - 25), fill=SIGNAL, width=3)
d.polygon([(ax + 40, BOTTOM - 25), (ax + 28, BOTTOM - 34), (ax + 28, BOTTOM - 16)], fill=SIGNAL)
done(img, d)

# 2 - Ruby's father is only ever named on screen
slide(["HE HAS A NAME", "ONLY ON SCREEN."], 80,
      [("SCRIPT  ·  BOTH DRAFTS, IDENTICAL",
        "“I know what you’re thinking, but Ruby’s father had nothing to do with this.”"),
       ("AIRED  ·  DVD CAPTIONS", "“Charles had nothing to do with this.”")],
      "Ruby’s father is never named on the page. Not in either draft.")

# 3 - the bar is renamed in spoken dialogue
slide(["THE BAR GOT", "RENAMED FOR AIR."], 140,
      [("SCRIPT  ·  BOTH DRAFTS",
        "“All he ever did since we knew him was pour beer over at the Boar’s Head.”"),
       ("AIRED  ·  DVD CAPTIONS",
        "“All he ever did since we met him was pour beer at the Pennsylvania Pub.”")],
      "Not just the neon sign. The swap is in the spoken line.")

# 4 - the Blevins cut: she says the parallel out loud
slide(["SHE SAYS IT", "OUT LOUD. CUT."], 46,
      [("SCRIPT ONLY  ·  BLEVINS’ OFFICE, SCENE 5",
        "SCULLY: “Of course. A young boy. A missing sister. An alien abduction scenario.”")],
      "Two exchanges vanish from the middle of this scene. The captions prove it: the lines on "
      "either side join with a 0.07 second gap, so nothing was spoken in between.",
      centering=(0.5, 0.35))

# 5 - the Danny call is rewritten
slide(["THE REDSKINS", "JOKE NEVER AIRED."], 30,
      [("SCRIPT  ·  BOTH DRAFTS",
        "“Look, I got Redskins season tickets. Pick a game.” (winces) “The Giants? You’re killing me here, Danny.”"),
       ("AIRED  ·  DVD CAPTIONS",
        "“I know a friend who knows a friend who knows a friend who can get you a ticket to a Redskins game.”")],
      "Whole exchange rewritten. No tickets, no Giants tease.")

# 6 - the line loses her name
slide(["HE SAID HER NAME.", "THE EDIT TOOK IT."], 244,
      [("SCRIPT  ·  SCENE 42", "“I’m still walking into that room, Scully.”"),
       ("AIRED  ·  DVD CAPTIONS",
        "“You know, I’m still walking into that room... every day of my life.”")],
      "The beat survives. The direct address does not.", tsize=56)

# 7 - closer
img, d = new()
y = TOP
for ln in ["THE FULL", "REPORT IS ON", "THE ARCHIVE."]: d.text((80, y), ln, font=oswald(112, 600), fill=PAPER); y += 118
y = para(d, 80, y + 30, "Two drafts, twelve findings, every line that moved.", mono(28), fill=MUTED, lh=40)
still(img, 190, (80, y + 34, 920, BOTTOM - 64 - (y + 34)), centering=(0.5, 0.52))
d.text((80, BOTTOM - 40), "boggsfiles.com/script-vs-screen", font=mono(28, "Medium"), fill=SIGNAL)
done(img, d)
print("wrote", k, "slides to", OUT)
