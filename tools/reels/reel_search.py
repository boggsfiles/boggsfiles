"""Reel demoing the archive search: three queries, three answers, no title card.

The pitch is not "the site has search". It is what the search reaches: there is no Flukeman
episode on the site, yet typing his name lands on Scully's one passing line about him in a
different episode entirely. So the reel opens mid-keystroke on that word, not on a logo.

Every result here is the real thing, pulled from the live index rather than mocked up, which is
why the excerpts carry their own <mark> runs. Frames are drawn rather than screen-recorded so the
type stays crisp at 1080x1920 and the typing can be paced for reading.
"""
import html
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 24
INK = (11, 14, 13)
PAPER = (232, 230, 220)
SIGNAL = (224, 121, 108)
MUTED = (139, 147, 140)
DIM = (107, 116, 109)
LINE = (44, 50, 48)

F = Path(__file__).parent / "fonts"
OUT = Path.home() / "Desktop" / "Boggsfiles search reel"

MARGIN = 72
TOP = 300


def osw(size, weight=500):
    f = ImageFont.truetype(str(F / "Oswald.ttf"), size)
    f.set_variation_by_axes([weight])
    return f


def mono(size, cut="Regular"):
    return ImageFont.truetype(str(F / f"DMMono-{cut}.ttf"), size)


def tracked(d, x, y, s, f, fill, tr):
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tr


def runs(excerpt):
    """Excerpt HTML -> [(text, is_match)], so matched words can be colored as the site colors them."""
    out = []
    for part in re.split(r"(<mark>.*?</mark>)", excerpt):
        if not part:
            continue
        m = part.startswith("<mark>")
        out.append((html.unescape(re.sub(r"<[^>]+>", "", part)), m))
    return out


def wrap(d, parts, font, width):
    """Word-wrap across styled runs, keeping each word's match flag with it."""
    words = []
    for text, hit in parts:
        for i, w in enumerate(text.split(" ")):
            if w:
                words.append((w, hit))
    lines, line, x = [], [], 0.0
    space = d.textlength(" ", font=font)
    for w, hit in words:
        adv = d.textlength(w, font=font)
        if line and x + space + adv > width:
            lines.append(line)
            line, x = [], 0.0
        if line:
            x += space
        line.append((w, hit))
        x += adv
    if line:
        lines.append(line)
    return lines


def draw_runs(d, x, y, lines, font, leading):
    space = d.textlength(" ", font=font)
    for ln in lines:
        cx = x
        for i, (w, hit) in enumerate(ln):
            if i:
                cx += space
            d.text((cx, y), w, font=font, fill=SIGNAL if hit else MUTED)
            cx += d.textlength(w, font=font)
        y += leading
    return y


# query, status line, [(group, title, excerpt html)] -- all taken from the live index
SCENES = [
    ("flukeman", "1 result", [
        ("Transcripts", "The Field Where I Died",
         "Scully. Even if I knew for certain... I wouldn't change a day. Well, maybe that "
         "<mark>flukeman</mark> thing. I could have lived without that just fine."),
    ]),
    ("trust no one", "104 results", [
        ("Transcripts", "The Erlenmeyer Flask",
         "Give me the parcel, Scully. Dana Scully. <mark>No!</mark> Mulder. Mulder. "
         "Deep Throat. <mark>Trust...</mark> <mark>Trust...</mark> <mark>No</mark> <mark>one.</mark>"),
        ("Transcripts", "Little Green Men",
         "Deep throat said, <mark>\"trust</mark> <mark>no</mark> <mark>one.\"</mark> "
         "Fox Mulder. I was sent here by <mark>one</mark> of those people."),
    ]),
    ("cobweb guns", "1 result", [
        ("Documents", "2nd Unit &amp; Production Schedules",
         "Beside each stop on the scout is what that stop needs: 2 <mark>cobweb</mark> "
         "<mark>guns,</mark> dust <mark>gun,</mark> water truck at the storage facility."),
    ]),
]


# Instagram puts its own controls over roughly the top 150px and bottom 270px of a reel.
SAFE_TOP, SAFE_BOTTOM = 250, 1650
QUERY_TOP = 500          # tall enough that even the two-result scene clears the bottom


def frame(query, status=None, hits=(), caret=True):
    """Lay the block out first, then centre it in the safe area.

    Drawn from a fixed top, the content sat in the upper quarter of a 1080x1920 frame and the
    rest was dead black, which on a phone looks like a mistake rather than a choice.
    """
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    qf, sf, gf, tf = osw(104, 500), mono(32, "Medium"), mono(28, "Medium"), osw(72, 500)
    body, leading = mono(42), 62
    inner = W - MARGIN * 2

    ops, height = [], 0
    ops.append(("query", query)); height += 196
    if status:
        ops.append(("status", status)); height += 104
    last = None
    for group, title, excerpt in hits:
        if group != last:
            ops.append(("group", group)); height += 94
            last = group
        lines = wrap(d, runs(excerpt), body, inner)
        ops.append(("hit", html.unescape(title), lines))
        height += 104 + leading * len(lines) + 62

    # The query line stays put and only the results move. Centring the whole block made the
    # query jump up the frame the instant results appeared, which read as a glitch.
    y = min(QUERY_TOP, SAFE_BOTTOM - height)
    y = max(SAFE_TOP, y)
    for op in ops:
        if op[0] == "query":
            d.text((MARGIN, y), op[1], font=qf, fill=PAPER)
            if caret:
                cx = MARGIN + d.textlength(op[1], font=qf) + 12
                d.rectangle([cx, y + 12, cx + 6, y + 104], fill=SIGNAL)
            y += 138
            d.line([(MARGIN, y), (W - MARGIN, y)], fill=LINE, width=2)
            y += 58
        elif op[0] == "status":
            tracked(d, MARGIN, y, op[1].upper(), sf, DIM, 3.4)
            y += 104
        elif op[0] == "group":
            tracked(d, MARGIN, y, op[1].upper(), gf, DIM, 3.6)
            y += 44
            d.line([(MARGIN, y), (W - MARGIN, y)], fill=(34, 40, 38), width=2)
            y += 50
        else:
            d.text((MARGIN, y), op[1], font=tf, fill=PAPER)
            y += 104
            y = draw_runs(d, MARGIN, y, op[2], body, leading) + 62
    return img


def end_card():
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    big = osw(150, 600)
    y = 560
    for n, t in enumerate(["EVERY", "PAGE.", "EVERY", "LINE."]):
        d.text((MARGIN, y), t, font=big, fill=SIGNAL if n == 3 else PAPER)
        y += 166
    d.line([(MARGIN, y + 44), (W - MARGIN, y + 44)], fill=LINE, width=2)
    d.text((MARGIN, y + 112), "518 pages. Free.", font=osw(58, 300), fill=MUTED)
    tracked(d, MARGIN, y + 212, "BOGGSFILES.COM", mono(38, "Medium"), SIGNAL, 3.2)
    return img


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()
    n = 0

    def put(img, holds):
        nonlocal n
        for _ in range(holds):
            img.save(OUT / f"{n:05d}.png")
            n += 1

    for query, status, hits in SCENES:
        # type it in, a couple of frames per character, so the word is readable as it forms
        for i in range(1, len(query) + 1):
            put(frame(query[:i]), 3)
        put(frame(query), 10)                      # beat before the answer
        put(frame(query, status, hits[:1]), 14)    # first result
        if len(hits) > 1:
            put(frame(query, status, hits), 56)
        else:
            put(frame(query, status, hits), 62)
    put(end_card(), 72)

    mp4 = OUT / "boggsfiles-search.mp4"
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(OUT / "%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                    "-movflags", "+faststart", str(mp4)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for p in OUT.glob("*.png"):
        p.unlink()
    print(f"  {n} frames, {n/FPS:.1f}s -> {mp4}")


if __name__ == "__main__":
    build()
