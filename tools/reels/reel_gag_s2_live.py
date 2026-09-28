"""Season 2 gag reel launch Reel, 1080x1920, for the night the page goes live.

Clip choice was verified frame by frame, not from the transcript. The machine transcript
pointed at a promising run around 324s which turns out to be talk-show footage spliced into
the reel, across a shot change - the same trap as the Season 1 elevator overlay. Every clip
here is checked by shot_cuts() before an overlay is allowed near it.

The source is a DVD capture: 720x480 flagged 3:2 but actually 4:3, so it is scaled to a true
4:3 rather than trusting the sample aspect.
"""
import subprocess, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

W, H, FPS = 1080, 1920, 30
INK=(11,14,13); PAPER=(232,230,220); SIGNAL=(224,121,108); MUTED=(150,158,151)
SRC = Path.home()/"Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels/Gag Reel - Season 2.mp4"
WORK = Path(__file__).parent/"gag2_live"; WORK.mkdir(exist_ok=True)
OUT = Path.home()/"Desktop/Gag Reel S2 - IG.mp4"
F = Path(__file__).parent/"fonts"
VID_W, VID_H = W, 810                     # 4:3 letterboxed into the 9:16 frame
VID_Y = 470
VENC = ["-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-r",str(FPS)]

def osw(s,w=500):
    f=ImageFont.truetype(str(F/"Oswald.ttf"),s); f.set_variation_by_axes([w]); return f
def mono(s,w="Medium"): return ImageFont.truetype(str(F/f"DMMono-{w}.ttf"),s)
def tracked(d,x,y,s,f,fill,tr):
    for ch in s: d.text((x,y),ch,font=f,fill=fill); x+=d.textlength(ch,font=f)+tr

def shot_cuts(start, end, thresh=15.0):
    """Cut timestamps inside the clip, found by differencing consecutive frames.

    ffmpeg's own scene detector is useless on this footage: it cleared a clip that crossed two
    hard cuts even with the threshold dropped to 0.10, because the shots either side are dark
    and similar in tone. Comparing actual frames finds them without fuss.
    """
    import glob, tempfile, numpy as np
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["/opt/homebrew/bin/ffmpeg","-v","error","-ss",str(start),"-to",str(end),
            "-i",str(SRC),"-vf","yadif,scale=160:-1","-fps_mode","passthrough",
            f"{td}/%06d.png"],check=True)
        fs=sorted(glob.glob(f"{td}/*.png"))
        ims=[np.asarray(Image.open(f).convert("RGB"),dtype=np.float32) for f in fs]
    step=1/29.97
    return [round(start+i*step,3) for i in range(1,len(ims))
            if float(np.abs(ims[i]-ims[i-1]).mean()) > thresh]

def clip(name, start, end, lines, note, allow_cuts=False):
    cuts = shot_cuts(start, end)
    if cuts and not allow_cuts:
        raise SystemExit(f"{name}: clip spans a shot change at {cuts} - the overlay would sit "
                         f"over a different scene. Trim it or pass allow_cuts=True.")
    ov = Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    y = VID_Y + VID_H + 90
    for ln in lines:
        d.text((66,y),ln,font=osw(62),fill=PAPER+(255,)); y += 74
    if note: tracked(d,68,y+22,note,mono(23,"Light"),MUTED+(255,),2.6)
    p_ov = WORK/f"{name}_ov.png"; ov.save(p_ov)
    out = WORK/f"{name}.mp4"
    subprocess.run(["/opt/homebrew/bin/ffmpeg","-y","-v","error","-ss",str(start),"-to",str(end),
        "-i",str(SRC),"-i",str(p_ov),"-filter_complex",
        f"[0:v]yadif,scale={VID_W}:{VID_H},setsar=1,"
        f"pad={W}:{H}:0:{VID_Y}:color=0x0b0e0d[v];[v][1:v]overlay=0:0,fps={FPS},format=yuv420p[out];"
        f"[0:a]aresample=48000[a]","-map","[out]","-map","[a]",*VENC,
        "-c:a","aac","-b:a","192k",str(out)],check=True)
    print(f"  {name}: {start}-{end} ({end-start:.1f}s) cuts={cuts or 'none'}")
    return out

def card(name, big, small, secs=2.0):
    img=Image.new("RGB",(W,H),INK); d=ImageDraw.Draw(img)
    y=760
    for ln in big: d.text((66,y),ln,font=osw(78,600),fill=PAPER); y+=88
    tracked(d,68,y+40,small,mono(26),SIGNAL,3.0)
    p=WORK/f"{name}.png"; img.save(p)
    out=WORK/f"{name}.mp4"
    subprocess.run(["/opt/homebrew/bin/ffmpeg","-y","-v","error","-loop","1","-t",str(secs),
        "-i",str(p),"-f","lavfi","-t",str(secs),"-i","anullsrc=r=48000:cl=stereo",
        "-vf",f"fps={FPS},format=yuv420p",*VENC,"-c:a","aac","-b:a","192k",str(out)],check=True)
    return out

parts = [
    # No title card: her own numbers say a Reel that opens on a card underperforms one that
    # opens on the clip.
    clip("01_charades", 556.0, 568.8, ["FOUR WORDS."], "Season 2 gag reel"),
    # The praying-gesture shot is only 713.7-714.95. Either side of it are a photo on a table
    # and a pair of gloved hands, and the first cut of this Reel ran straight through both.
    clip("02_fireme",   713.80, 714.87, ["\u201cDON\u2019T FIRE ME.\u201d"], ""),
    card("03_end", ["COMING AT","10:13 ET","TONIGHT"], "BOGGSFILES.COM / GAG-REELS", 2.6),
]
lst = WORK/"list.txt"
lst.write_text("".join(f"file '{p}'\n" for p in parts))
subprocess.run(["/opt/homebrew/bin/ffmpeg","-y","-v","error","-f","concat","-safe","0",
    "-i",str(lst),"-c","copy","-movflags","+faststart",str(OUT)],check=True)
d=subprocess.run(["/opt/homebrew/bin/ffprobe","-v","error","-show_entries","format=duration",
    "-of","default=nw=1:nk=1",str(OUT)],capture_output=True).stdout.decode().strip()
print(f"\n  saved {OUT}  {float(d):.1f}s")
