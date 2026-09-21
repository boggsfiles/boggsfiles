"""One-off gag moment from the Fight the Future gag reel (letterboxed source)."""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (126, 137, 129)
HERE = Path(__file__).resolve().parent
SRC = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels/Gag Reel - Fight the Future.mp4"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Gag Moments"
WORK = Path("ftf_work")
def oswald(size, wght=600):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), size); f.set_variation_by_axes([wght]); return f
def mono(size, w="Regular"): return ImageFont.truetype(str(HERE / f"fonts/DMMono-{w}.ttf"), size)
def tracked(d, x, y, s, f, fill, track):
    for ch in s: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
    return x
def brand(d, x, y, size):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), size); f.set_variation_by_axes([500]); track = 0.16 * size
    x = tracked(d, x, y, "BOGGS", f, PAPER, track); x += 0.34 * size - track
    xw = d.textlength("X", font=f); d.text((x, y), "X", font=f, fill=PAPER)
    asc, _ = f.getmetrics(); cx, cy = x + xw / 2, y + asc * 0.62; r = 1.08 * size / 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=SIGNAL, width=max(3, round(size * 2 / 23.2)))
    tracked(d, x + xw + 0.34 * size, y, "FILES", f, PAPER, track)

# source active picture: crop=708:392:6:86 (1.81:1) -> 1080x598
CROP = "crop=708:392:6:86"; VH = 598; VID_Y = 760
def moment(name, start, dur, hook, label):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); y = 300
    for ln in hook: d.text((72, y), ln, font=oswald(104), fill=PAPER); y += 110
    d.text((76, VID_Y + VH + 28), label, font=mono(24, "Medium"), fill=MUTED)
    brand(d, 76, H - 330, 40); d.text((76, H - 270), "full reels coming to boggsfiles.com", font=mono(26), fill=MUTED)
    p = WORK / f"{name}_ov.png"; ov.save(p)
    end = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(end); brand(d, 76, 860, 64)
    d.text((76, 960), "GAG REELS  ·  SEASONS 1–9 + THE MOVIE  ·  COMING SOON", font=mono(28, "Medium"), fill=SIGNAL); d.text((76, 1010), "boggsfiles.com", font=mono(30), fill=PAPER)
    pe = WORK / f"{name}_end.png"; end.save(pe)
    out = OUT / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", str(SRC), "-i", str(p), "-loop", "1", "-t", "1.6", "-i", str(pe),
                    "-filter_complex",
                    f"[0:v]yadif=deint=interlaced,{CROP},scale=1080:{VH}:flags=lanczos,setsar=1,pad={W}:{H}:0:{VID_Y}:color=0x0b0e0d[v];[v][1:v]overlay=0:0,fps={FPS},format=yuv420p[a];"
                    f"[2:v]fps={FPS},format=yuv420p[b];[a][b]concat=n=2:v=1:a=0[out];"
                    f"[0:a]aresample=48000,apad=pad_dur=1.6,afade=t=out:st={dur}:d=1.2[aud]",
                    "-map", "[out]", "-map", "[aud]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", "1.5", "-i", str(out), "-frames:v", "1", "-vf", "scale=540:-1", str(WORK / f"{name}_preview.png")], check=True)
    print(out.name, dur + 1.6, "s")

moment("06 I don't believe this", 508.8, 4.3, ["\"I DON'T", "F***ING", "BELIEVE THIS.\""], "GAG REEL  ·  FIGHT THE FUTURE  ·  1998")
