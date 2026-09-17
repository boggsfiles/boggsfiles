"""Reel: Seasons 1-9 gag reels, Mulder/Scully-only clips, 1080x1920, < 90 s. Clip audio kept (on-set sound)."""
import subprocess, os, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (126, 137, 129); LINE = (44, 50, 48)
HERE = Path(__file__).resolve().parent
SRC = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels"
OUTDIR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos"
WORK = Path("gag_work"); shutil.rmtree(WORK, ignore_errors=True); WORK.mkdir()
import numpy as np, wave
SR = 48000
def drone(path, dur, seed=7, fade_in=0.6, fade_out=0.8):
    """Original synthesized X-Files-ish drone bed for the title cards (no licensed music)."""
    t = np.arange(int(dur * SR)) / SR; rng = np.random.default_rng(seed)
    def tone(f, amp, lfo=0.0, rate=0.1): return amp * (1 + lfo * np.sin(2 * np.pi * rate * t)) * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
    bed = tone(55, 0.30, 0.25, 0.07) + tone(55.4, 0.22, 0.25, 0.05) + tone(110, 0.10, 0.4, 0.11) + tone(58.27, 0.08, 0.5, 0.03) + tone(233.1, 0.025, 0.6, 0.13)
    noise = rng.normal(0, 1, len(t)); b = np.zeros_like(noise); acc = 0.0
    for k in range(0, len(noise), 4800):
        seg = noise[k:k + 4800]; out = np.empty_like(seg)
        for j, v in enumerate(seg): acc += 0.015 * (v - acc); out[j] = acc
        b[k:k + 4800] = out
    bed += 0.9 * b / (np.abs(b).max() + 1e-9) * 0.12 * (1 + 0.5 * np.sin(2 * np.pi * 0.045 * t))
    fi, fo = int(fade_in * SR), int(fade_out * SR); bed[:fi] *= np.linspace(0, 1, fi); bed[-fo:] *= np.linspace(1, 0, fo)
    bed = bed / (np.abs(bed).max() + 1e-9) * 0.4; pcm = (bed * 32767).astype("<i2")
    with wave.open(str(path), "wb") as wf: wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(np.repeat(pcm, 2).tobytes())

def oswald(size, wght=500):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), size); f.set_variation_by_axes([wght]); return f
def mono(size, w="Regular"): return ImageFont.truetype(str(HERE / f"fonts/DMMono-{w}.ttf"), size)
LOGO_Y = 200
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
    brand(d); d.text((80, LOGO_Y + 95), eyebrow, font=mono(26, "Medium"), fill=SIGNAL); d.line((80, LOGO_Y + 140, W - 80, LOGO_Y + 140), fill=LINE, width=2)
def footer(d):
    d.line((80, H - 330, W - 80, H - 330), fill=LINE, width=2)
    d.text((80, H - 300), "COMING SOON  ·  boggsfiles.com", font=mono(30), fill=PAPER)

def card(name, eyebrow, big, sub, seconds, bed, offset=0.0):
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img); header(d, eyebrow)
    y = 620
    for ln in big: d.text((76, y), ln, font=oswald(140, 600), fill=PAPER); y += 148
    y += 30
    for s in sub: d.text((80, y), s, font=mono(32), fill=MUTED); y += 48
    footer(d); p = WORK / f"{name}.png"; img.save(p)
    seg = WORK / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-loop", "1", "-t", str(seconds), "-i", str(p), "-ss", str(offset), "-t", str(seconds), "-i", str(bed),
                    "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", str(seg)], check=True)
    return seg

VID_Y = 555   # 1080x810 video, vertically centred
def clip(name, season, start, dur, label):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    header(d, f"GAG REEL  ·  SEASON {season}"); footer(d)
    d.text((80, VID_Y + 810 + 30), label, font=mono(26), fill=MUTED)
    d.text((80, VID_Y - 50), "FROM THE DVD MASTER  ·  NOT A TAPE DUB", font=mono(22, "Medium"), fill=SIGNAL)
    p = WORK / f"{name}_ov.png"; ov.save(p); seg = WORK / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", str(next(SRC.glob(f"Gag Reel - Season {season}*.mp4"))), "-i", str(p),
                    "-filter_complex", f"[0:v]yadif=deint=interlaced,scale=1080:810:flags=lanczos,setsar=1,pad={W}:{H}:0:{VID_Y}:color=0x0b0e0d[v];[v][1:v]overlay=0:0,fps={FPS}[out]",
                    "-map", "[out]", "-map", "0:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(seg)], check=True)
    return seg

segs = []
open_bed = WORK / "open.wav"; drone(open_bed, 2.4 + 2.8 + 3.4)          # one continuous bed across the three opening cards
segs.append(card("c1", "THE X-FILES  ·  BOGGSFILES", ["COMING", "SOON..."], [], 2.4, open_bed, 0.0))
segs.append(card("c2", "THE X-FILES  ·  BOGGSFILES", ["WHAT'S BETTER", "THAN X-FILES", "GAG REELS?"], [], 2.8, open_bed, 2.4))
segs.append(card("c3", "THE X-FILES  ·  BOGGSFILES", ["ONES YOU CAN", "ACTUALLY SEE."], ["Every copy online is a fuzzy tape dub.", "These come straight from the DVD masters."], 3.4, open_bed, 5.2))
CLIPS = [(1, 268, 5, "Mulder + Scully"), (2, 440, 5, "Mulder"), (3, 455, 5, "Mulder + Scully"), (4, 120, 5, "Mulder + Scully"), (5, 216, 5, "Mulder + Scully"),
         (6, 142.7, 5, "Mulder + Scully"), (9, 450, 5, "Scully"), (1, 380, 4.4, "Mulder + Scully"), (3, 310, 5, "Scully"), (7, 276, 6, "Scully"),
         (9, 258, 17.3, "Mulder + Scully")]   # last: flub, "go again", full take through "into the woods tonight", "Yes!"
for i, (season, start, dur, label) in enumerate(CLIPS):
    segs.append(clip(f"k{i:02d}", season, start, dur, label))
drone(WORK / "close.wav", 3.6, seed=11, fade_in=0.3, fade_out=1.2)
segs.append(card("c9", "THE X-FILES  ·  BOGGSFILES", ["SEASONS 1–9.", "EVERY", "GAG REEL."], ["Straight from the masters.", "Coming soon to boggsfiles.com"], 3.6, WORK / "close.wav"))

lst = WORK / "list.txt"; lst.write_text("".join(f"file '{s.resolve()}'\n" for s in segs))
out = OUTDIR / "Boggsfiles Reel - Gag Reels Coming Soon.mp4"
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
print(out, subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)], capture_output=True, text=True).stdout.strip(), "s")
