"""Season 1 dailies teasers for Instagram. Hook text over the footage, clip audio kept,
1.6 s end card. 1080x1920. Sources: the 4:3 DV dailies transfers. Output: iCloud XF Music Videos/Dailies Teasers/."""
import subprocess, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (126, 137, 129)
HERE = Path(__file__).resolve().parent
D = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Dailies"
SRC = {"dt1": D / "Deep Throat/DEEP THROAT DAILIES 1.mov", "dt2": D / "Deep Throat/DEEP THROAT DAILIES 2.mov", "ba": D / "Born Again/Born Again Dailies.mp4"}
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Dailies Teasers"; OUT.mkdir(parents=True, exist_ok=True)
WORK = Path("dailies_work/build"); shutil.rmtree(WORK, ignore_errors=True); WORK.mkdir(parents=True)
VH = 810; VID_Y = 700
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

def segment(i, tag, start, dur):
    p = WORK / f"seg{i:02d}.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", str(SRC[tag]),
                    "-vf", f"yadif=deint=all,scale=1080:{VH}:flags=lanczos,setsar=1,fps={FPS}", "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p",
                    "-af", "aresample=48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", str(p)], check=True)
    return p

def reel(name, segs, hook, label, end_line, hook_size=104):
    parts = [segment(i, *s) for i, s in enumerate(segs)]
    lst = WORK / "list.txt"; lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    joined = WORK / "joined.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)], check=True)
    dur = sum(s[2] for s in segs)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); y = 250
    for ln in hook: d.text((72, y), ln, font=oswald(hook_size), fill=PAPER); y += int(hook_size * 1.06)
    d.text((76, VID_Y + VH + 28), label, font=mono(24, "Medium"), fill=MUTED)
    brand(d, 76, H - 330, 40); d.text((76, H - 270), "full dailies coming to boggsfiles.com", font=mono(26), fill=MUTED)
    p = WORK / f"{name}_ov.png"; ov.save(p)
    end = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(end); brand(d, 76, 860, 64)
    d.text((76, 960), end_line, font=mono(28, "Medium"), fill=SIGNAL); d.text((76, 1010), "boggsfiles.com/dailies", font=mono(30), fill=PAPER)
    pe = WORK / f"{name}_end.png"; end.save(pe)
    out = OUT / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(joined), "-i", str(p), "-loop", "1", "-t", "1.6", "-i", str(pe),
                    "-filter_complex",
                    f"[0:v]pad={W}:{H}:0:{VID_Y}:color=0x0b0e0d[v];[v][1:v]overlay=0:0,fps={FPS},format=yuv420p[a];"
                    f"[2:v]fps={FPS},format=yuv420p[b];[a][b]concat=n=2:v=1:a=0[out];"
                    f"[0:a]apad=pad_dur=1.6,afade=t=out:st={dur - 0.2:.2f}:d=1.4[aud]",
                    "-map", "[out]", "-map", "[aud]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(min(3, dur / 2)), "-i", str(out), "-frames:v", "1", "-vf", "scale=360:-1", str(WORK.parent / f"{name}_preview.png")], check=True)
    print(out.name, round(dur + 1.6, 1), "s")

END = "SEASON 1 DAILIES  ·  FULL REELS NEXT WEEK"
reel("01 Unseen since 1993", [("dt1", 139, 33)], ["SEASON 1", "DAILIES.", "UNSEEN", "SINCE 1993."], "DAILIES  ·  1X01 DEEP THROAT  ·  1993", END)
reel("02 What dailies look like", [("ba", 22, 22)], ["THIS IS WHAT", "THE DAILIES", "LOOK LIKE."], "DAILIES  ·  1X21 BORN AGAIN  ·  MARCH 25, 1994", END)
reel("03 Take 2 take 4", [("ba", 956, 15), ("ba", 1036, 15)], ["SAME LINE.", "TAKE TWO.", "TAKE FOUR."], "DAILIES  ·  1X21 BORN AGAIN  ·  SCENE 281", END)
reel("04 Eriks diner", [("dt1", 816, 32)], ["MULDER. SCULLY.", "ERIK'S DINER.", "TAKE ONE."], "DAILIES  ·  1X01 DEEP THROAT  ·  SCENE 27", END)
slates = [("dt1", 140.6, 1.4), ("dt1", 786.6, 1.4), ("dt1", 816.6, 1.4), ("ba", 26.6, 1.4), ("ba", 44.8, 1.4), ("ba", 287.8, 1.4), ("ba", 312.6, 1.4), ("ba", 956.6, 1.4), ("ba", 1036.6, 1.4), ("ba", 1110.6, 1.4), ("dt2", 320.3, 1.4)]
reel("05 Every slate", slates, ["EVERY SLATE.", "FULL SEASON 1", "DAILIES DROP", "NEXT WEEK."], "DAILIES  ·  DEEP THROAT  ·  BORN AGAIN", "SEASON 1 DAILIES  ·  NEXT WEEK", hook_size=96)
