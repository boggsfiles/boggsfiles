"""Je Souhaite carousel: why a crew member's annotated schedule is the rare half.

Ten 1080x1350 slides. Every slide is a scan - the document leads, never the site. Crops are
given as fractions of the page so they survive a re-render at another dpi, and each one is
letterboxed in its own paper color rather than cropped to fill, because on these pages the
part that matters is often at the edge.

Source pages are rendered from the two published PDFs, so the tech scout slide carries the
same blurred phone numbers the site does.
"""
import os, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageStat

W, H = 1080, 1350
INK=(11,14,13); PAPER=(232,230,220); SIGNAL=(224,121,108); MUTED=(150,158,151); LINE=(44,50,48)
F = "tools/reels/fonts"
ICL = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/2nd Unit & Production Schedules"
PDFS = {"e": ICL / "7ABX21 Je Souhaite Effects Crew Working File.pdf",
        "p": ICL / "7ABX21 Je Souhaite Director's Plans.pdf"}
OUT = Path.home() / "Desktop/Je Souhaite carousel"
BOX_Y, BOX_H = 250, 810

def osw(s, w=500):
    f = ImageFont.truetype(f"{F}/Oswald.ttf", s); f.set_variation_by_axes([w]); return f
def mono(s, w="Medium"): return ImageFont.truetype(f"{F}/DMMono-{w}.ttf", s)
def tracked(d, x, y, s, f, fill, tr):
    for ch in s: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + tr

# (page key, page no, crop box as fractions of the page or None for the whole page, headline, subline)
SLIDES = [
 ("e",  4, (.60, .704, .99, .768), "DID WE GET THAT?!!", "written in the margin, April 2000"),
 ("p",  1, None,                   "TWO DOCUMENTS",      "bound into one file, kept by two different people"),
 ("p",  2, (.05, .26, .95, .41),   "\u201cUNTITLED\u201d", "four days out, the episode still had no name"),
 ("p",  8, (.02, .05, .98, .72),   "FOURTEEN SETS",      "the Carson trailer park, drawn to scale"),
 ("e",  3, (.33, .475, .99, .600), "2 COBWEB GUNS",      "what each stop on the tech scout needed"),
 ("e",  3, (.22, .630, .98, .805), "NOTHING",            "and what it didn\u2019t"),
 ("e",  7, (.02, .085, .75, .355), "THE TRUCK",          "cob webbers, air hoses, a mole fogger"),
 ("e",  9, (.66, .290, 1.0, .445), "TRAILER EXPLODES",   "the day\u2019s gags, kept in a running list"),
 ("e",  7, (.02, .520, .80, .605), "JEFF, JEFF, ERIC,\nRON, RANDY", "the same names, day after day"),
 (None, 0, None,                   "NOBODY KEEPS THIS",  None),
]

def render_pages():
    """One pdftoppm pass per PDF, at the resolution the crops are taken from."""
    pages = {}
    for key, pdf in PDFS.items():
        td = tempfile.mkdtemp()
        subprocess.run(["pdftoppm", "-r", "200", "-jpeg", "-jpegopt", "quality=95",
                        str(pdf), f"{td}/{key}"], check=True)
        for f in sorted(Path(td).glob(f"{key}-*.jpg")):
            pages[(key, int(f.stem.split("-")[1]))] = f
    return pages

def paper_of(im):
    """The page's own background, taken from a border strip, so letterboxing disappears."""
    w, h = im.size
    edge = Image.new("RGB", (w, 24))
    edge.paste(im.crop((0, 0, w, 12)), (0, 0))
    edge.paste(im.crop((0, h - 12, w, h)), (0, 12))
    return tuple(int(v) for v in ImageStat.Stat(edge).median)

def ink_box(im, box, pad=14):
    """Within a generous region, find what actually has ink on it.

    The stock is yellow, green or white depending on the page, so the threshold is relative
    to that region's own paper rather than fixed. Returns a box in full-page pixels.
    """
    import numpy as np
    x0, y0, x1, y1 = [int(v) for v in box]
    a = np.asarray(im.crop((x0, y0, x1, y1)).convert("L")).astype(int)
    mask = a < int(np.median(a)) - 45
    rows, cols = np.nonzero(mask.any(axis=1))[0], np.nonzero(mask.any(axis=0))[0]
    if not len(rows) or not len(cols):
        return (x0, y0, x1, y1)
    return (x0 + cols[0] - pad, y0 + rows[0] - pad, x0 + cols[-1] + pad, y0 + rows[-1] + pad)


def widen_to(box, page, aspect=2.3):
    """Grow a box about its centre until it is no wider than `aspect`, so a one-line strip
    does not end up as a sliver floating in the band. Clamped to the page."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if w / max(1, h) > aspect:
        need = w / aspect
        cy = (y0 + y1) / 2
        y0, y1 = cy - need / 2, cy + need / 2
    return (max(0, int(x0)), max(0, int(y0)), min(page[0], int(x1)), min(page[1], int(y1)))


def plate(path, box, fit=True):
    """Fit the crop inside the band, letterboxed in the document's own paper color."""
    im = Image.open(path).convert("RGB")
    if box:
        x0, y0, x1, y1 = box
        region = (im.width*x0, im.height*y0, im.width*x1, im.height*y1)
        b = ink_box(im, region) if fit else region
        im = im.crop(widen_to(b, im.size))
    bg = paper_of(im)
    s = min(W / im.width, BOX_H / im.height)
    im = im.resize((max(1, round(im.width*s)), max(1, round(im.height*s))), Image.LANCZOS)
    out = Image.new("RGB", (W, BOX_H), bg)
    out.paste(im, ((W - im.width)//2, (BOX_H - im.height)//2))
    return out


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    pages = render_pages()
    for i, (key, pg, box, big, small) in enumerate(SLIDES, 1):
        img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
        if key:
            img.paste(plate(pages[(key, pg)], box), (0, BOX_Y))
            d.line([(0, BOX_Y-1), (W, BOX_Y-1)], fill=LINE)
            d.line([(0, BOX_Y+BOX_H), (W, BOX_Y+BOX_H)], fill=LINE)
            tracked(d, 66, 150, "THE X-FILES  ·  7ABX21  ·  JE SOUHAITE", mono(22), MUTED, 3.4)
            lines = big.split("\n")
            size = 74 if len(lines) == 1 and len(big) < 20 else 58
            y = BOX_Y + BOX_H + 56
            for ln in lines:
                d.text((62, y), ln, font=osw(size, 600), fill=PAPER); y += size + 10
            if small: d.text((64, y + 24), small, font=osw(36, 300), fill=MUTED)
        else:
            tracked(d, 66, 150, "THE X-FILES", mono(22), MUTED, 3.4)
            d.text((58, 290), "NOBODY", font=osw(140, 600), fill=PAPER)
            d.text((58, 430), "KEEPS", font=osw(140, 600), fill=PAPER)
            d.text((58, 570), "THIS", font=osw(140, 600), fill=SIGNAL)
            d.line([(66, 760), (W-66, 760)], fill=LINE, width=2)
            for n, t in enumerate([
                "The art department’s plans get filed.",
                "A crew member’s marked-up schedule",
                "gets thrown out at wrap.",
                "",
                "This one didn’t. 28 pages, free,",
                "scanned in full color."]):
                d.text((62, 816 + n*58), t, font=osw(42, 300), fill=PAPER if n < 3 else MUTED)
            tracked(d, 66, 1190, "BOGGSFILES.COM", mono(24), SIGNAL, 2.8)
        img.save(OUT / f"{i:02d}.jpg", quality=93)
    print(f"  {len(SLIDES)} slides -> {OUT}")

if __name__ == "__main__":
    build()
