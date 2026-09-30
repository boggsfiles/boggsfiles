"""Teaser reel for the Season 3 gag reel, 1080x1920.

Clips chosen by Lindsey. Order runs kinetic -> peak -> warm -> button: David down the hall as the
hook, Gillian and the light, Gillian cursing as the biggest laugh, the two of them going, then
"the truth is out there" last so the show's own tagline sets up the 10/13 card.

The running clip starts at 77.3 rather than 77.0: frame differencing found cuts at 77.1 and 77.2,
so the original in-point opened mid-transition. Every other clip is a single unbroken shot.

Aspect: masters are 720x480, SAR 1:1, DAR 3:2, i.e. 4:3 stored stretched, which is why the site
plays them object-fit:fill. Clips are squeezed back to 640x480 before scaling or everyone is 12%
too wide. 4:3 in a 9:16 frame leaves dead bands, so a blurred, darkened copy of the picture fills
behind it instead of flat black.
"""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
VID_W, VID_H = 1080, 810
VID_Y = (H - VID_H) // 2
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (140, 150, 142)
HERE = Path(__file__).resolve().parent
SRC = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels/Gag Reel - Season 3.mp4"
OUT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Reel - Gag Reel S3 teaser"
OUT.mkdir(parents=True, exist_ok=True)
TMP = Path("/private/tmp/claude-501/-Users-lindseyboggs-Sites-boggsfiles/261dd1eb-8941-4607-87c5-4e3fef009978/scratchpad/gag3")

CLIPS = [(78.0, 84.0),    # David running down the hall (77.0 opened mid-cut; 77.3 opened on an empty corridor)
         (97.0, 100.0),   # Gillian with the light
         (224.0, 234.0),  # Gillian cursing
         (451.0, 455.0),  # both of them going
         (304.0, 313.0)]  # "the truth is out there"

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
def center_in(d, box, text, font, fill):
    x0, y0, x1, y1 = box
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    d.text((round((x0+x1)/2 - (l+r)/2), round((y0+y1)/2 - (t+b)/2)), text, font=font, fill=fill)

# overlay across the body, clear of the picture band
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
brand(d, 80, VID_Y - 196)
d.text((80, VID_Y - 122), "GAG REEL  ·  SEASON 3  ·  1995–96", font=mono(26), fill=SIGNAL)
d.text((80, VID_Y + VID_H + 82), "THE FULL ELEVEN MINUTES IS ON THE SITE", font=mono(27), fill=PAPER)
d.text((80, VID_Y + VID_H + 130), "boggsfiles.com/gag-reels", font=mono(26), fill=MUTED)
ov.save(TMP / "overlay.png")

# end card: the date is the point. Every element is placed from the measured ink box of the one
# above it, because "10.13" in Oswald 300 has an ink bottom 250px below its draw origin and a
# hardcoded rule underneath it lands inside the numerals.
ec = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(ec)
brand(d, 80, 470, 50)

f_head = osw(66, 600)
d.text((80, 600), "THE REST ARRIVE", font=f_head, fill=PAPER)
y = d.textbbox((80, 600), "THE REST ARRIVE", font=f_head)[3] + 34

f_date = osw(300, 600)
d.text((72, y), "10.13", font=f_date, fill=SIGNAL)
y = d.textbbox((72, y), "10.13", font=f_date)[3] + 46      # clear of the glyphs, not through them

d.line((80, y, W - 80, y), fill=(60, 68, 63), width=3)
y += 46

f_body = mono(31)
for ln in ["Seasons 4 to 9, plus Fight the Future.", "Every gag reel ever made, all at once."]:
    d.text((80, y), ln, font=f_body, fill=PAPER); y += 48
y += 58

box = (80, y, W - 80, y + 130)
d.rectangle(box, outline=SIGNAL, width=4)
center_in(d, box, "SAVE THE DATE", osw(58, 600), PAPER)
d.text((80, box[3] + 46), "boggsfiles.com/gag-reels", font=mono(28), fill=MUTED)
ec.save(TMP / "endcard.png")

# body
parts, auds = [], []
for i, (a, b) in enumerate(CLIPS):
    parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,scale=640:480,setsar=1,"
                 f"scale={VID_W}:{VID_H}:flags=lanczos[v{i}]")
    auds.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}]")
cat = "".join(f"[v{i}][a{i}]" for i in range(len(CLIPS))) + f"concat=n={len(CLIPS)}:v=1:a=1[vc][ac]"
fc = ";".join(parts + auds) + ";" + cat + \
     ";[vc]split=2[fg][bgsrc]" \
     f";[bgsrc]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}," \
     "boxblur=28:2,eq=brightness=-0.30:saturation=0.55[bg]" \
     f";[bg][fg]overlay=0:{VID_Y}[stacked];[stacked][1:v]overlay=0:0[vout]"
body = TMP / "body.mp4"
subprocess.run(["ffmpeg","-v","error","-y","-i",str(SRC),"-i",str(TMP/"overlay.png"),
                "-filter_complex",fc,"-map","[vout]","-map","[ac]",
                "-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p","-r","30",
                "-c:a","aac","-b:a","192k","-ar","48000", str(body)], check=True)

tail = TMP / "tail.mp4"
subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-t","4","-i",str(TMP/"endcard.png"),
                "-f","lavfi","-t","4","-i","anullsrc=channel_layout=stereo:sample_rate=48000",
                "-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p","-r","30",
                "-c:a","aac","-b:a","192k", str(tail)], check=True)
lst = TMP / "join.txt"; lst.write_text(f"file '{body}'\nfile '{tail}'\n")
final = OUT / "gag-reel-s3-teaser.mp4"
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",str(lst),
                "-c","copy", str(final)], check=True)
dur = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",
                      str(final)], capture_output=True, text=True).stdout.strip()
print(f"wrote {final}\n  {float(dur):.1f}s, {final.stat().st_size/1e6:.1f} MB, {W}x{H}")
