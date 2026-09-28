"""Story frames for the section highlights: three per highlight, 1080x1920.

Same house style and safe-area handling as story_start_here.py. Every figure here is read off the
built site (dist/) rather than typed from memory, and every URL is checked to exist before a frame
claiming it is written.
"""
import re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
TOP, BOT = 300, 1620
BAND_TOP, BAND_BOT = TOP + 150, BOT - 90
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49)
MUTED = (132, 142, 134); LINE = (46, 52, 49)
HERE = Path(__file__).resolve().parent
DIST = HERE.parents[1] / "dist"
ROOT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/IG Story - Sections"

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
    """Centre on the ink, not the font metrics: anchor='ma' hangs text off the ascender and reads low."""
    x0, y0, x1, y1 = box
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    d.text((round((x0 + x1) / 2 - (l + r) / 2), round((y0 + y1) / 2 - (t + b) / 2)), text, font=font, fill=fill)

def render(draw_fn, out, n, total, hint=None):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    draw_fn(d)
    img = Image.new("RGB", (W, H), INK)
    bb = layer.getbbox()
    if bb:
        dy = round((BAND_TOP + BAND_BOT) / 2 - (bb[1] + bb[3]) / 2)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.paste(layer, (0, dy)); layer = sh
    img.paste(layer, (0, 0), layer)
    dd = ImageDraw.Draw(img)
    brand(dd); dd.line((90, TOP + 96, W - 90, TOP + 96), fill=LINE, width=2)
    if hint:
        f = mono(26, "Medium"); dd.text((90, BOT - 4), hint, font=f, fill=SIGNAL)
        ax = 90 + dd.textlength(hint, font=f) + 20; ay = BOT + 13
        dd.line((ax, ay, ax + 40, ay), fill=SIGNAL, width=4)
        dd.polygon([(ax + 40, ay), (ax + 28, ay - 9), (ax + 28, ay + 9)], fill=SIGNAL)
    dd.text((W - 90, BOT - 2), f"{n} / {total}", font=mono(24), fill=MUTED, anchor="ra")
    img.save(out)

def title_frame(lines, blurb, size=132):
    def f(d):
        y = 0
        for ln in lines:
            d.text((90, y), ln, font=osw(size, 600), fill=PAPER); y += int(size * 1.06)
        y = para(d, 90, y + 40, blurb, mono(30), fill=MUTED, lh=46)
        d.line((90, y + 48, 250, y + 48), fill=SIGNAL, width=5)
    return f

def stat_frame(head, rows):
    def f(d):
        d.text((90, 0), head, font=osw(92, 600), fill=PAPER)
        y = 150
        for i, (big, small) in enumerate(rows):
            d.text((90, y), big, font=osw(78, 600), fill=SIGNAL)
            yy = para(d, 90, y + 92, small, mono(27), fill=PAPER, lh=40)
            y = yy + 52
            if i != len(rows) - 1:
                d.line((90, y - 28, W - 90, y - 28), fill=LINE, width=2)
    return f

def bullet_frame(lines, items):
    def f(d):
        y = 0
        for ln in lines:
            d.text((90, y), ln, font=osw(92, 600), fill=PAPER); y += 100
        y += 46
        for it in items:
            d.ellipse((92, y + 12, 108, y + 28), fill=SIGNAL)
            y = para(d, 140, y, it, mono(28), fill=PAPER, maxw=W - 240, lh=42) + 34
    return f

def link_frame(lines, blurb, url):
    def f(d):
        y = 0
        for ln in lines:
            d.text((90, y), ln, font=osw(124, 600), fill=PAPER); y += 132
        y = para(d, 90, y + 40, blurb, mono(30), fill=MUTED, lh=46)
        box = (90, y + 70, W - 90, y + 70 + 132)
        d.rectangle(box, outline=SIGNAL, width=4)
        center_in(d, box, url, osw(52, 600), PAPER)
        d.text((90, y + 70 + 186), "Link in bio", font=mono(30, "Medium"), fill=MUTED)
    return f

# --------------------------------------------------------------------------
SECTIONS = [
 ("Scripts", "/scripts/", [
   title_frame(["THE", "SCRIPTS."],
               "Original production drafts, scanned from the paper they were printed on.", 140),
   stat_frame("THE COLLECTION", [
     ("512",   "drafts, Seasons 1 to 11 and both movies"),
     ("EVERY", "revision color: white, blue, pink, yellow, green, goldenrod, salmon"),
     ("SCANS", "the real pages, stamps and all, not retyped")]),
   link_frame(["GO", "READ."], "Browse by season. Every draft opens full size.", "BOGGSFILES.COM"),
 ]),
 ("Vs Screen", "/script-vs-screen/", [
   title_frame(["SCRIPT", "VS.", "SCREEN."],
               "What was written. What changed. What actually made it to air."),
   stat_frame("THE REPORTS", [
     ("6",  "episodes compared line by line"),
     ("67", "findings, cuts, rewrites and shippy moments"),
     ("17", "archived drafts, read against the DVD captions")]),
   link_frame(["READ", "THEM."],
              "Pilot, Deep Throat, Squeeze, Conduit, The Blessing Way, Herrenvolk.",
              "BOGGSFILES.COM"),
 ]),
 ("Gag Reels", "/gag-reels/", [
   title_frame(["GAG", "REELS."], "The takes that fell apart, straight off the DVD masters."),
   bullet_frame(["WHAT'S", "THERE"], [
     "Seasons 1 and 2 are live now",
     "Ten reels in the collection, Seasons 1 to 9 plus Fight the Future",
     "Full length, not clips",
     "More seasons going up through October"]),
   link_frame(["WATCH."], "No account, no ads, nothing to sign up for.", "BOGGSFILES.COM"),
 ]),
 ("Dailies", "/dailies/", [
   title_frame(["DAILIES."],
               "Raw production footage. Slates, resets, the takes nobody was meant to see.", 150),
   stat_frame("THE COLLECTION", [
     ("14",   "episode collections"),
     ("RAW",  "unedited, straight from the source"),
     ("RARE", "fan-preserved, most of it is nowhere else")]),
   link_frame(["GO", "LOOK."], "Streamed from the archive. Nothing to download.", "BOGGSFILES.COM"),
 ]),
 ("Screencaps", "/screencaps/", [
   title_frame(["SCREEN", "CAPS."], "Every shot change in the whole series, frame by frame.", 140),
   stat_frame("THE NUMBERS", [
     ("230,802", "frames, captured from DVD and Blu-ray"),
     ("219",     "titles, every season and both movies"),
     ("TAGGED",  "filter by who is on screen, jump by timecode")]),
   link_frame(["FIND", "A FRAME."], "Click any one for the full-size capture.", "BOGGSFILES.COM"),
 ]),
 ("Documents", "/production-documents/", [
   title_frame(["PRODUCTION", "PAPER."], "The paperwork nobody was supposed to keep.", 108),
   bullet_frame(["WHAT'S", "THERE"], [
     "21 second unit memos, season schedules and prep calendars, 45 pages",
     "Scanned in full color on their original revision stock",
     "Shooting schedules and call sheets",
     "A season mapped out before the episodes had names"]),
   link_frame(["READ", "THEM."], "Browsable page by page, right on the site.", "BOGGSFILES.COM"),
 ]),
]

missing = [u for _, u, _ in SECTIONS if not (DIST / u.strip("/") / "index.html").exists()]
if missing:
    sys.exit(f"refusing to build: no page at {missing}")

for name, url, frames in SECTIONS:
    out = ROOT / name; out.mkdir(parents=True, exist_ok=True)
    for i, fn in enumerate(frames, 1):
        render(fn, out / f"{i:02d}.png", i, len(frames),
               hint="KEEP TAPPING" if i == 1 else None)
    print(f"  {name}: {len(frames)} frames  ->  {url}")
print(f"\nwrote {sum(len(f) for _, _, f in SECTIONS)} frames to {ROOT}")
