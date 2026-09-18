"""Five single-moment gag reels for Instagram: hook text over the footage from frame one, no intro card,
clip audio kept, 1.6 s logo tag at the end. 1080x1920. Output: iCloud XF Music Videos/Gag Moments/."""
import subprocess, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (126, 137, 129)
HERE = Path(__file__).resolve().parent
SRC = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Gag Moments"; OUT.mkdir(parents=True, exist_ok=True)
WORK = Path("gagm_work"); shutil.rmtree(WORK, ignore_errors=True); WORK.mkdir()

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

VID_Y = 700   # 1080x810 clip; hook text sits above it, inside IG's safe area
def moment(name, season, start, dur, hook, sub):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); y = 250
    for ln in hook: d.text((72, y), ln, font=oswald(104), fill=PAPER); y += 110
    d.text((76, VID_Y + 810 + 28), f"GAG REEL  ·  SEASON {season}  ·  FROM THE DVD MASTER", font=mono(24, "Medium"), fill=MUTED)
    brand(d, 76, H - 330, 40); d.text((76, H - 270), "full reels coming to boggsfiles.com", font=mono(26), fill=MUTED)
    p = WORK / f"{name}_ov.png"; ov.save(p)
    end = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(end); brand(d, 76, 860, 64)
    d.text((76, 960), "GAG REELS  ·  SEASONS 1–9  ·  COMING SOON", font=mono(28, "Medium"), fill=SIGNAL); d.text((76, 1010), "boggsfiles.com", font=mono(30), fill=PAPER)
    pe = WORK / f"{name}_end.png"; end.save(pe)
    src = next(SRC.glob(f"Gag Reel - Season {season}*.mp4")); out = OUT / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", str(src), "-i", str(p), "-loop", "1", "-t", "1.6", "-i", str(pe),
                    "-filter_complex",
                    f"[0:v]yadif=deint=interlaced,scale=1080:810:flags=lanczos,setsar=1,pad={W}:{H}:0:{VID_Y}:color=0x0b0e0d[v];[v][1:v]overlay=0:0,fps={FPS},format=yuv420p[a];"
                    f"[2:v]fps={FPS},format=yuv420p[b];[a][b]concat=n=2:v=1:a=0[out];"
                    f"[0:a]aresample=48000,apad=pad_dur=1.6,afade=t=out:st={dur}:d=1.2[aud]",
                    "-map", "[out]", "-map", "[aud]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-movflags", "+faststart", str(out)], check=True)
    print(out.name, dur + 1.6, "s")

moment("01 Scully loses it", 9, 450, 6, ["SCULLY CANNOT", "GET THROUGH", "THIS TAKE."], "Season 9 gag reel · from the DVD master")
moment("02 Neither of them", 3, 461, 9, ["NEITHER OF THEM", "COULD KEEP IT", "TOGETHER."], "Season 3 gag reel · from the DVD master")
moment("03 Bad Blood energy", 5, 216, 5, ["THIS IS WHAT", "SEASON 5 LOOKED", "LIKE OFF CAMERA."], "Season 5 gag reel · from the DVD master")
moment("04 Mid-surgery", 7, 276, 6, ["SCULLY. MID-SURGERY.", "LOSING IT."], "Season 7 gag reel · from the DVD master")
moment("05 Go again", 9, 258, 17.3, ["\"GO AGAIN.\"", "\"GO AGAIN.\""], "Season 9 gag reel · the full take")
