"""Reel: Seasons 10 & 11 are on boggsfiles.com — 1080x1920, ~30 s. Blu-ray clips (muted) + site screenshots + drone bed."""
import subprocess, os, shutil, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, wave

W, H, FPS = 1080, 1920, 30
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (126, 137, 129); LINE = (44, 50, 48)
HERE = Path(__file__).resolve().parent
BR = Path("/Volumes/XFiles Archive/Blu-ray rips")
OUTDIR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos"
WORK = Path("s1011_work"); shutil.rmtree(WORK, ignore_errors=True); WORK.mkdir()
SR = 48000

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
def footer(d, text="boggsfiles.com"):
    d.line((80, H - 330, W - 80, H - 330), fill=LINE, width=2); d.text((80, H - 300), text, font=mono(30), fill=PAPER)

def drone(path, dur, seed=7, fade_in=0.6, fade_out=1.5):
    t = np.arange(int(dur * SR)) / SR; rng = np.random.default_rng(seed)
    def tone(f, amp, lfo=0.0, rate=0.1): return amp * (1 + lfo * np.sin(2 * np.pi * rate * t)) * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
    bed = tone(55, 0.30, 0.25, 0.07) + tone(55.4, 0.22, 0.25, 0.05) + tone(110, 0.10, 0.4, 0.11) + tone(58.27, 0.08, 0.5, 0.03) + tone(233.1, 0.025, 0.6, 0.13)
    noise = rng.normal(0, 1, len(t)); b = np.zeros_like(noise); acc = 0.0
    for k in range(0, len(noise), 4800):
        seg = noise[k:k + 4800]; out = np.empty_like(seg)
        for j, v in enumerate(seg): acc += 0.015 * (v - acc); out[j] = acc
        b[k:k + 4800] = out
    bed += 0.9 * b / (np.abs(b).max() + 1e-9) * 0.12 * (1 + 0.5 * np.sin(2 * np.pi * 0.045 * t))
    # a slow pulse every 2.4 s so the cuts feel paced
    bed *= 1 + 0.18 * np.clip(np.sin(2 * np.pi * t / 2.4), 0, 1) ** 8
    fi, fo = int(fade_in * SR), int(fade_out * SR); bed[:fi] *= np.linspace(0, 1, fi); bed[-fo:] *= np.linspace(1, 0, fo)
    bed = bed / (np.abs(bed).max() + 1e-9) * 0.42; pcm = (bed * 32767).astype("<i2")
    with wave.open(str(path), "wb") as wf: wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(np.repeat(pcm, 2).tobytes())

def enc(inp_args, seg, dur, extra_vf=""):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *inp_args, "-t", str(dur), "-an", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(seg)], check=True)

def card(name, eyebrow, big, sub, seconds, big_size=140, y0=620):
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img); header(d, eyebrow); y = y0
    for ln in big: d.text((76, y), ln, font=oswald(big_size, 600), fill=PAPER); y += int(big_size * 1.06)
    y += 30
    for s in sub: d.text((80, y), s, font=mono(32), fill=MUTED); y += 48
    footer(d); p = WORK / f"{name}.png"; img.save(p); seg = WORK / f"{name}.mp4"
    enc(["-loop", "1", "-i", str(p)], seg, seconds); return seg

VID_Y = 660   # 1080x608 letterboxed clip, vertically centred
def clip(name, mkv, start, dur, eyebrow, label):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); header(d, eyebrow); footer(d)
    d.text((80, VID_Y - 50), "FROM THE BLU-RAY  ·  1920 × 1080", font=mono(22, "Medium"), fill=SIGNAL)
    d.text((80, VID_Y + 608 + 30), label, font=mono(26), fill=MUTED)
    p = WORK / f"{name}_ov.png"; ov.save(p); seg = WORK / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", str(mkv), "-i", str(p),
                    "-filter_complex", f"[0:v]scale=1080:608:flags=lanczos,setsar=1,pad={W}:{H}:0:{VID_Y}:color=0x0b0e0d[v];[v][1:v]overlay=0:0,fps={FPS}[out]",
                    "-map", "[out]", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(seg)], check=True)
    return seg

def site(name, shot, eyebrow, big, sub, seconds, pan=700):
    """Phone-width site screenshot (1080x2400) shown at 62% inside a bordered frame, panning down slowly."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); header(d, eyebrow)
    d.text((76, 400), big, font=oswald(88, 600), fill=PAPER); d.text((80, 505), sub, font=mono(26), fill=MUTED)
    fx, fy, fw, fh = 150, 590, 780, 900
    d.rectangle((fx - 6, fy - 6, fx + fw + 6, fy + fh + 6), outline=LINE, width=3)
    footer(d); p = WORK / f"{name}_ov.png"; ov.save(p); seg = WORK / f"{name}.mp4"
    # slide a window down the tall screenshot (crop, not zoompan — zoompan rescales the whole image into the window)
    wh = int(fh * 1080 / fw)   # window height at source width, keeps the aspect exact
    vf = (f"[0:v]scale=1080:-2:flags=lanczos,crop=1080:{wh}:0:'min({pan}*t/{seconds},ih-{wh})',scale={fw}:{fh}:flags=lanczos,"
          f"pad={W}:{H}:{fx}:{fy}:color=0x0b0e0d[v];[v][1:v]overlay=0:0[out]")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(shot), "-i", str(p), "-filter_complex", vf, "-map", "[out]", "-t", str(seconds),
                    "-an", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(seg)], check=True)
    return seg

segs = []
segs.append(card("c1", "THE X-FILES  ·  BOGGSFILES", ["SEASONS", "10 & 11."], ["Finally."], 2.4, big_size=170, y0=640))
segs.append(card("c2", "THE X-FILES  ·  BOGGSFILES", ["NOW ON", "THE ARCHIVE."], ["Screencaps in full 1080p", "Every episode transcribed", "Production scripts — all 16 episodes"], 3.0))
CLIPS = [(BR / "XFILES_S10_D1/mkv/10X03 Mulder and Scully Meet the Were-Monster.mkv", 7*60+44, "Mulder & Scully Meet the Were-Monster"),
         (BR / "XFILES_S10_D2/mkv/10X06 My Struggle II.mkv", 17*60+33, "My Struggle II"),
         (BR / "XFILES_S11_D1/mkv/11X03 Plus One.mkv", 33*60+43, "Plus One"),
         (BR / "XFILES_S11_D2/mkv/11X05 Ghouli.mkv", 2611.5, "Ghouli"),
         (BR / "XFILES_S11_D3/mkv/11X10 My Struggle IV.mkv", 2519, "My Struggle IV")]
for i, (mkv, t, label) in enumerate(CLIPS):
    segs.append(clip(f"k{i}", mkv, t, 2.4, "SCREENCAPS  ·  SEASONS 10–11", label))
SHOTS = HERE / "site_shots"
segs.append(site("s1", SHOTS / "gallery.png", "SCREENCAPS", "EVERY SHOT.", "Tagged by character. Searchable by timecode.", 3.4))
segs.append(site("s2", SHOTS / "transcript.png", "TRANSCRIPTS", "EVERY LINE.", "From the Blu-ray subtitle tracks, character-labelled.", 3.4))
segs.append(site("s3", SHOTS / "scripts.png", "SCRIPTS", "EVERY DRAFT.", "Production drafts and collated revisions.", 3.0))
segs.append(site("s4", SHOTS / "script_s10_page.png", "SCRIPTS  ·  SEASON 10", "MY STRUGGLE.", "Green revision · August 2015", 3.0, pan=120))
segs.append(site("s5", SHOTS / "script_s11_page.png", "SCRIPTS  ·  SEASON 11", "MY STRUGGLE IV.", "Production draft · signed by Chris Carter", 3.0, pan=120))
segs.append(card("c9", "THE X-FILES  ·  BOGGSFILES", ["SEASONS 1–11.", "ALL OF IT."], ["Scripts · Transcripts · Screencaps · Dailies", "boggsfiles.com"], 3.6, big_size=130))

lst = WORK / "list.txt"; lst.write_text("".join(f"file '{s.resolve()}'\n" for s in segs))
video = WORK / "video.mp4"
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(video)], check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout)
drone(WORK / "bed.wav", dur)
out = OUTDIR / "Boggsfiles Reel - Seasons 10 and 11.mp4"
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(video), "-i", str(WORK / "bed.wav"), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
silent = OUTDIR / "Boggsfiles Reel - Seasons 10 and 11 (no audio).mp4"
shutil.copy(video, silent)
print(out, round(dur, 1), "s")
