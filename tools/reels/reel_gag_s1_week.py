"""Season 1 gag reel, split into one moment a day for a week. Same look as reel_gag_moments.py."""
import subprocess, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (126, 137, 129)
HERE = Path(__file__).resolve().parent
SRC = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels/Gag Reel - Season 1.mp4"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Gag Moments/Season 1 week"; OUT.mkdir(parents=True, exist_ok=True)
WORK = Path("gag1_work/build"); shutil.rmtree(WORK, ignore_errors=True); WORK.mkdir(parents=True)
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
VID_Y = 700
def moment(name, start, dur, hook, label, end_line="GAG REELS  ·  SEASONS 1–9 + THE MOVIE  ·  COMING SOON"):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); y = 250
    for ln in hook: d.text((72, y), ln, font=oswald(104), fill=PAPER); y += 110
    d.text((76, VID_Y + 810 + 28), label, font=mono(24, "Medium"), fill=MUTED)
    brand(d, 76, H - 330, 40); d.text((76, H - 270), "full reels coming to boggsfiles.com", font=mono(26), fill=MUTED)
    p = WORK / f"{name}_ov.png"; ov.save(p)
    end = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(end); brand(d, 76, 860, 64)
    d.text((76, 960), end_line, font=mono(28, "Medium"), fill=SIGNAL); d.text((76, 1010), "boggsfiles.com", font=mono(30), fill=PAPER)
    pe = WORK / f"{name}_end.png"; end.save(pe)
    out = OUT / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", str(SRC), "-i", str(p), "-loop", "1", "-t", "1.6", "-i", str(pe),
                    "-filter_complex",
                    f"[0:v]yadif=deint=interlaced,scale=1080:810:flags=lanczos,setsar=1,pad={W}:{H}:0:{VID_Y}:color=0x0b0e0d[v];[v][1:v]overlay=0:0,fps={FPS},format=yuv420p[a];"
                    f"[2:v]fps={FPS},format=yuv420p[b];[a][b]concat=n=2:v=1:a=0[out];"
                    f"[0:a]aresample=48000,apad=pad_dur=1.6,afade=t=out:st={dur:.2f}:d=1.2[aud]",
                    "-map", "[out]", "-map", "[aud]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(min(2.5, dur / 2)), "-i", str(out), "-frames:v", "1", "-vf", "scale=300:-1", str(WORK / f"{name}.png")], check=True)
    print(name, dur + 1.6, "s")

L = "GAG REEL  ·  SEASON 1  ·  FROM THE DVD MASTER"
def shot(name, a, b, hook, **kw): moment(name, a, round(b - a - 0.04, 2), hook, L, **kw)
shot("Mon - Mulder take one", 130.35, 145.08, ["MULDER.", "TAKE ONE.", "NOT HAPPENING."])
shot("Tue - Scully in the rain", 221.79, 247.98, ["SCULLY.", "IN THE RAIN.", "GONE."])
shot("Wed - Rain take two", 262.33, 291.22, ["SAME SCENE.", "NEXT TAKE.", "STILL GONE."])
shot("Thu - Mulder blue shirt", 291.22, 304.90, ["MULDER.", "ONE LINE.", "COULD NOT."])
shot("Fri - Parked car", 384.65, 395.33, ["MULDER.", "PARKED CAR.", "DONE FOR."])
shot("Sat - Elevator", 412.08, 427.09, ["STUCK IN", "AN ELEVATOR.", "NOBODY IS OKAY."])
shot("Sun - Last gag", 757.99, 772.51, ["THE LAST GAG", "OF SEASON 1."], end_line="SEASON 1 GAG REEL  ·  FULL REEL NEXT WEEK")
shot("Alt - Doorway", 364.06, 373.61, ["MULDER. SCULLY.", "DOORWAY.", "ONE OF THEM BREAKS."])
shot("Alt - Rainy car", 348.01, 357.46, ["SCULLY. MULDER.", "RAINY CAR.", "NEITHER OF THEM."])
