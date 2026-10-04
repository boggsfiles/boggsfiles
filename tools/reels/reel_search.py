"""Reel demoing the archive search: three queries, three answers, no title card.

The pitch is not "the site has search". It is what the search reaches, so the queries are lines
a fan already knows by heart -- the dreamsicle, the light cream cheese, Bambi -- and the reel
opens mid-keystroke on one of them rather than on a logo.

Every result is the real thing, pulled from the live index rather than mocked up, which is why
the excerpts carry their own <mark> runs. Frames are drawn rather than screen-recorded so the
type stays crisp at 1080x1920 and the typing can be paced for reading.

The typewriter is synthesised here too: one key per keystroke, placed from the frame plan so the
clicks land exactly on the letters appearing, and a bell when a query finishes.
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
    # The transcript reads "nonfat", so the query does too -- a hyphen on screen
    # beside an unhyphenated quote just looks like one of them is wrong.
    ("nonfat tofutti rice dreamsicle", "1 result", [
        ("Transcripts", "The Unnatural",
         "Fox Mulder. Something you'd like to share with the rest of the class? Dana Scully. "
         "It's not ice cream. It's a <mark>nonfat</mark> <mark>tofutti</mark> <mark>rice</mark> "
         "<mark>dreamsicle.</mark>"),
    ]),
    ("light cream cheese", "1 result", [
        ("Transcripts", "Bad Blood",
         "...and that was half a <mark>cream</mark> <mark>cheese</mark> bagel. It wasn't even "
         "real <mark>cream</mark> <mark>cheese,</mark> it was <mark>light</mark> "
         "<mark>cream</mark> <mark>cheese!</mark>"),
    ]),
    # Pagefind centres its own excerpt on the first dense match, which for "bambi" lands on a
    # flat line of exposition. The window shown here is a different passage from the same single
    # result -- the one where the joke actually is. Scully asks it twice, having ignored the UFO
    # theory in between, and the repeat is the whole gag.
    ("bambi", "1 result", [
        ("Transcripts", "War of the Coprophages",
         "Fox Mulder. <mark>Bambi</mark> also has this theory I've never come acro-- "
         "Dana Scully. Who? Fox Mulder. Dr. Berenbaum. Anyway, her theory is-- "
         "Dana Scully. Her name is <mark>Bambi?</mark> Fox Mulder. Yeah. Both her parents were "
         "naturalists. Her theory is that UFOs are actually nocturnal insect swarms... "
         "Dana Scully. Her name is <mark>Bambi?</mark>"),
    ]),
]


# Instagram puts its own controls over roughly the top 150px and bottom 270px of a reel.
SAFE_TOP, SAFE_BOTTOM = 250, 1650
QUERY_TOP = 500          # tall enough that even the two-result scene clears the bottom


def frame(query, status=None, hits=(), caret=True, full=None):
    """Lay the block out first, then centre it in the safe area.

    Drawn from a fixed top, the content sat in the upper quarter of a 1080x1920 frame and the
    rest was dead black, which on a phone looks like a mistake rather than a choice.
    """
    full = full if full is not None else query
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    sf, gf, tf = mono(32, "Medium"), mono(28, "Medium"), osw(72, 500)
    # "non-fat tofutti rice dreamsicle" is 30 characters and ran off the frame at a fixed size,
    # so the query is sized to fit the margins. Measured against the finished string, not the
    # partial one, so the type does not resize while it is being typed.
    qf = osw(104, 500)
    for size in range(104, 51, -4):
        qf = osw(size, 500)
        if d.textlength(full, font=qf) + 24 <= W - MARGIN * 2:
            break
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
                d.rectangle([cx, y + 12, cx + 6, y + qf.size], fill=SIGNAL)
            # Place the rule below the ink, not a fixed distance below the draw origin: at a
            # fixed offset the descender of the g in "light" crossed it. Measured against the
            # finished query plus a descender reference, so the rule does not move while the
            # word is being typed or jump between queries that happen to have no descenders.
            ink = d.textbbox((MARGIN, y), full, font=qf)[3]
            tail = d.textbbox((MARGIN, y), "gjpqy", font=qf)[3]
            y = max(ink, tail) + 26
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
    y = 470
    for n, t in enumerate(["EVERY", "PAGE.", "EVERY", "LINE."]):
        d.text((MARGIN, y), t, font=big, fill=SIGNAL if n == 3 else PAPER)
        y += 166
    d.line([(MARGIN, y + 44), (W - MARGIN, y + 44)], fill=LINE, width=2)
    # Say what it is. Without this the reel shows search working without ever naming it.
    d.text((MARGIN, y + 96), "A search bar,", font=osw(64, 400), fill=PAPER)
    d.text((MARGIN, y + 172), "on every page.", font=osw(64, 400), fill=PAPER)
    d.text((MARGIN, y + 282), "518 pages.", font=osw(54, 300), fill=MUTED)
    tracked(d, MARGIN, y + 362, "AND MORE COMING", mono(36, "Medium"), PAPER, 3.6)
    tracked(d, MARGIN, y + 436, "BOGGSFILES.COM", mono(36, "Medium"), SIGNAL, 3.2)
    return img


def typewriter(keys, bells, seconds, sr=44100):
    """One key per keystroke, placed from the frame plan so the clicks land on the letters.

    Synthesised rather than sampled: a noise transient for the typebar hitting paper, a short
    tuned body, and a low thump for the carriage. Each key is varied slightly, because a loop of
    one identical click sounds like a machine rather than someone typing.
    """
    import numpy as np
    rng = np.random.default_rng(7)
    track = np.zeros(int(seconds * sr) + sr, dtype=float)

    def place(sig, at):
        i = int(at * sr)
        track[i:i + len(sig)] += sig[:max(0, len(track) - i)]

    for t in keys:
        n = int(sr * 0.045)
        x = np.arange(n) / sr
        strike = rng.normal(0, 1, n) * np.exp(-x * 150) * 0.55
        body = np.sin(2 * np.pi * rng.uniform(950, 1500) * x) * np.exp(-x * 95) * 0.28
        thump = np.sin(2 * np.pi * rng.uniform(85, 125) * x) * np.exp(-x * 55) * 0.22
        place((strike + body + thump) * rng.uniform(0.82, 1.0), t)

    for t in bells:
        n = int(sr * 0.7)
        x = np.arange(n) / sr
        ring = sum(np.sin(2 * np.pi * f * x) * a for f, a in ((1760, 1.0), (2640, .45), (3520, .2)))
        place(ring * np.exp(-x * 6.5) * 0.22, t)

    peak = np.abs(track).max()
    if peak:
        track = track / peak * 0.72
    return (track * 32767).astype("<i2")


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()
    n = 0
    keys, bells = [], []

    def put(img, holds):
        nonlocal n
        for _ in range(holds):
            img.save(OUT / f"{n:05d}.png")
            n += 1

    for query, status, hits in SCENES:
        for i in range(1, len(query) + 1):
            if query[i - 1] != " ":          # the space bar is quieter; skip rather than fake it
                keys.append(n / FPS)
            put(frame(query[:i], full=query), 2)
        bells.append(n / FPS)                # typewriter bell as the query lands
        put(frame(query, full=query), 11)
        put(frame(query, status, hits[:1], full=query), 14)
        put(frame(query, status, hits, full=query), 56 if len(hits) > 1 else 62)
    put(end_card(), 74)

    seconds = n / FPS
    wav = OUT / "typewriter.wav"
    import wave
    with wave.open(str(wav), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(44100)
        w.writeframes(typewriter(keys, bells, seconds).tobytes())

    mp4 = OUT / "boggsfiles-search.mp4"
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(OUT / "%05d.png"),
                    "-i", str(wav), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                    "-c:a", "aac", "-b:a", "160k", "-shortest",
                    "-movflags", "+faststart", str(mp4)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for f in OUT.glob("*.png"):
        f.unlink()
    wav.unlink()
    print(f"  {n} frames, {seconds:.1f}s, {len(keys)} keystrokes -> {mp4}")


if __name__ == "__main__":
    build()
