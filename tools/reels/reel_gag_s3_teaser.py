"""Teaser reel for the Season 3 gag reel, 1080x1920.

Structure: corpsing first as the hook, then the Queequeg memorial gag, which is the only bit of
this reel that plays with the sound off. No intro title card, per house rule; the card is at the
end only.

Aspect: the masters are 720x480 with SAR 1:1 and DAR 3:2, i.e. 4:3 content stored stretched, which
is why the site plays them with object-fit:fill. Every clip is squeezed back to 640x480 before it
is scaled up, or everyone is 12% too wide.

Every clip below was frame-differenced to confirm it does not cross a hard cut. The explosion at
11:20 was cut from the running order: every window inside it trips the detector, and a blooming
fireball changes the whole frame, so an edit cannot be told from the explosion itself.
"""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
VID_W, VID_H = 1080, 810                 # 4:3 corrected, full bleed width
VID_Y = (H - VID_H) // 2
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (132, 142, 134)
HERE = Path(__file__).resolve().parent
SRC = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels/Gag Reel - Season 3.mp4"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Reel - Gag Reel S3 teaser"
OUT.mkdir(parents=True, exist_ok=True)
TMP = Path("/private/tmp/claude-501/-Users-lindseyboggs-Sites-boggsfiles/261dd1eb-8941-4607-87c5-4e3fef009978/scratchpad/gag3")

# verified clean by frame differencing
CLIPS = [(494.0, 498.0),   # Mulder cracking up
         (478.5, 482.0),   # both of them going
         (657.3, 661.2),   # "In Memory Of QUEEQUEG"
         (663.3, 666.8),   # "No Dog Will Ever Replace You"
         (669.3, 672.0)]   # a completely different dog

def osw(s, w=600):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), s); f.set_variation_by_axes([w]); return f
def mono(s, w="Medium"): return ImageFont.truetype(str(HERE / f"fonts/DMMono-{w}.ttf"), s)
def tracked(d, x, y, s, f, fill, track):
    for ch in s: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
    return x
def brand(d, x, y, size=46):
    f = osw(size, 500); t = 0.16 * size
    x = tracked(d, x, y, "BOGGS", f, PAPER, t); x += 0.34 * size - t
    xw = d.textlength("X", font=f); d.text((x, y), "X", font=f, fill=PAPER)
    asc, _ = f.getmetrics(); cx, cy = x + xw / 2, y + asc * 0.62; r = 1.08 * size / 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=SIGNAL, width=4)
    tracked(d, x + xw + 0.34 * size, y, "FILES", f, PAPER, t)

# ---- overlay that sits over the whole body, clear of the video band -------
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
brand(d, 80, VID_Y - 190)
d.text((80, VID_Y - 118), "GAG REEL  ·  SEASON 3  ·  1995–96", font=mono(26), fill=SIGNAL)
d.text((80, VID_Y + VID_H + 76), "THE FULL REEL IS ON THE SITE", font=mono(28), fill=PAPER)
d.text((80, VID_Y + VID_H + 126), "boggsfiles.com/gag-reels", font=mono(26), fill=MUTED)
ov.save(TMP / "overlay.png")

# ---- end card -------------------------------------------------------------
ec = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(ec)
brand(d, 80, 560, 52)
y = 700
for ln in ["SEASON 3", "GAG REEL."]:
    d.text((80, y), ln, font=osw(128, 600), fill=PAPER); y += 138
d.text((80, y + 30), "Eleven minutes, uncut, from the DVD master.", font=mono(30), fill=MUTED)
d.text((80, y + 76), "Free. No account.", font=mono(30), fill=MUTED)
box = (80, y + 160, W - 80, y + 160 + 130)
d.rectangle(box, outline=SIGNAL, width=4)
t = "BOGGSFILES.COM"; f = osw(54, 600)
l, tp, r, b = d.textbbox((0, 0), t, font=f)
d.text((round((box[0]+box[2])/2 - (l+r)/2), round((box[1]+box[3])/2 - (tp+b)/2)), t, font=f, fill=PAPER)
ec.save(TMP / "endcard.png")

# ---- body: trim, un-stretch, stack, overlay -------------------------------
parts, amix = [], []
for i, (a, b) in enumerate(CLIPS):
    parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,scale=640:480,setsar=1,"
                 f"scale={VID_W}:{VID_H}:flags=lanczos[v{i}]")
    amix.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}]")
concat = "".join(f"[v{i}][a{i}]" for i in range(len(CLIPS))) + f"concat=n={len(CLIPS)}:v=1:a=1[vc][ac]"
fc = ";".join(parts + amix) + ";" + concat + \
     f";color=c=0x0b0e0d:s={W}x{H}:d=30[bg];[bg][vc]overlay=0:{VID_Y}:shortest=1[stacked]" \
     f";[stacked][1:v]overlay=0:0[vout]"
body = TMP / "body.mp4"
subprocess.run(["ffmpeg","-v","error","-y","-i",str(SRC),"-i",str(TMP/"overlay.png"),
                "-filter_complex",fc,"-map","[vout]","-map","[ac]",
                "-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p","-r","30",
                "-c:a","aac","-b:a","192k","-ar","48000", str(body)], check=True)

# ---- end card as 3s of video, then join -----------------------------------
tail = TMP / "tail.mp4"
subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-t","3","-i",str(TMP/"endcard.png"),
                "-f","lavfi","-t","3","-i","anullsrc=channel_layout=stereo:sample_rate=48000",
                "-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p","-r","30",
                "-c:a","aac","-b:a","192k", str(tail)], check=True)
lst = TMP / "join.txt"; lst.write_text(f"file '{body}'\nfile '{tail}'\n")
final = OUT / "gag-reel-s3-teaser.mp4"
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",str(lst),
                "-c","copy", str(final)], check=True)

dur = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",
                      str(final)], capture_output=True, text=True).stdout.strip()
print(f"wrote {final}")
print(f"  {float(dur):.1f}s, {final.stat().st_size/1e6:.1f} MB, {W}x{H}")
