"""Season 1 gag reel is live on the site. One 1080x1920 Instagram Reel, four moments.

Same look as reel_gag_s1_week.py (that file's clip boundaries are reused here, already vetted).
Each moment is encoded on its own with identical parameters, then stream-copied together with the
title and end cards, so the concat needs no re-encode.
Run:  cd tools/reels && python3 reel_gag_s1_live.py
"""
import subprocess, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (126, 137, 129); LINE = (44, 50, 48)
HERE = Path(__file__).resolve().parent
SRC = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels/Gag Reel - Season 1.mp4"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Gag Moments"
OUT.mkdir(parents=True, exist_ok=True)
WORK = HERE / "gag1_live"; shutil.rmtree(WORK, ignore_errors=True); WORK.mkdir(parents=True)
VID_Y = 700

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

# identical encode parameters everywhere, so the pieces concatenate without a re-encode
VENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-video_track_timescale", "30000"]
LABEL = "GAG REEL  ·  SEASON 1  ·  FROM THE DVD MASTER"

def card(name, lines, sub, tail, seconds):
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
    brand(d, 76, 620, 58)
    y = 760
    for ln in lines: d.text((76, y), ln, font=oswald(112), fill=PAPER); y += 118
    d.text((76, y + 30), sub, font=mono(30, "Medium"), fill=SIGNAL)
    d.text((76, y + 84), tail, font=mono(28), fill=MUTED)
    p = WORK / f"{name}.png"; img.save(p)
    out = WORK / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-loop", "1", "-t", str(seconds), "-i", str(p),
                    "-f", "lavfi", "-t", str(seconds), "-i", "anullsrc=r=48000:cl=stereo",
                    "-vf", f"fps={FPS},format=yuv420p", *VENC, "-movflags", "+faststart", str(out)], check=True)
    return out

def shot_cuts(start, end):
    """Timestamps of shot changes strictly inside [start, end)."""
    import re
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-ss", str(start),
                        "-t", str(round(end - start, 2)), "-i", str(SRC), "-filter_complex",
                        "select='gt(scene,0.25)',metadata=print:file=-", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [start + float(m) for m in re.findall(r"pts_time:([\d.]+)", r.stdout)
            if 0.15 < float(m) < end - start - 0.15]

def moment(name, start, end, hook, note, allow_cuts=False):
    dur = round(end - start, 2)
    cuts = shot_cuts(start, end)
    if cuts and not allow_cuts:
        raise SystemExit(f"{name}: clip spans a shot change at {['%.2f' % c for c in cuts]} - "
                         f"the overlay would sit over a different scene. Trim the clip or pass allow_cuts=True.")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    y = 250
    for ln in hook: d.text((72, y), ln, font=oswald(104), fill=PAPER); y += 110
    d.text((76, y + 16), note, font=mono(28), fill=MUTED)
    d.text((76, VID_Y + 810 + 28), LABEL, font=mono(24, "Medium"), fill=MUTED)
    brand(d, 76, H - 330, 40)
    d.text((76, H - 270), "boggsfiles.com/gag-reels", font=mono(26), fill=SIGNAL)
    p = WORK / f"{name}_ov.png"; ov.save(p)
    out = WORK / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", str(SRC),
                    "-i", str(p), "-filter_complex",
                    f"[0:v]yadif=deint=interlaced,scale=1080:810:flags=lanczos,setsar=1,"
                    f"pad={W}:{H}:0:{VID_Y}:color=0x0b0e0d[v];[v][1:v]overlay=0:0,fps={FPS},format=yuv420p[out];"
                    f"[0:a]aresample=48000[aud]",
                    "-map", "[out]", "-map", "[aud]", *VENC, "-movflags", "+faststart", str(out)], check=True)
    print(f"  {name}: {dur}s", flush=True)
    return out

parts = [card("00_title", ["SEASON 1", "GAG REEL."], "NOW ON THE ARCHIVE", "all 13 minutes, 36 seconds", 1.8)]
parts += [
    moment("01_airspace", 130.35, 145.08, ["ONE WORD.", "THREE TAKES."], "Russian air... maids."),
    moment("02_rain", 221.79, 247.98, ["THE RAIN.", "THE MUD.", "THE LINE."], "Somewhere around take six.", allow_cuts=True),
    moment("03_gobbledygook", 291.22, 304.90, ["IT WAS GOING", "SO WELL."], "“Spouting a gobbledygook... owl.”"),
    # 427.09 is where the elevator shot ends - do not extend past it, the overlay stops being true
    moment("04_elevator", 412.08, 427.09, ["STUCK IN", "AN ELEVATOR."], "Nobody is okay."),
    moment("05_cool", 427.09, 431.93, ["BETRAYING", "THE COOL EXTERIOR."], "\u201cCan I get off my fingers quickly\u2026\u201d"),
]
parts.append(card("06_end", ["WATCH THE", "WHOLE THING."], "boggsfiles.com/gag-reels", "seasons 2–9 + the movie to follow", 2.4))

lst = WORK / "parts.txt"
lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
final = OUT / "Boggsfiles Reel - Season 1 Gag Reel is live.mp4"
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                "-c", "copy", "-movflags", "+faststart", str(final)], check=True, cwd=WORK)
secs = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(final)],
                            capture_output=True, text=True).stdout.strip())
print(f"\nwrote {final}  ({int(secs)//60}:{secs % 60:04.1f})")
