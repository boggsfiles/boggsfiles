"""Instagram Reel: the cow line from the Season 1 gag reel. 1080x1920.

Chosen because it is ON CAMERA - both of them, in the car, in the rain. The "hell of a series"
line that looked best on paper turns out to play over the wrap-party credit roll, so it would have
been twenty seconds of scrolling crew names.

Short on purpose: Reels under ~15s loop, and a loop counts again.
"""
import subprocess, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
INK=(11,14,13); PAPER=(232,230,220); SIGNAL=(183,56,49); MUTED=(126,137,129)
HERE = Path(__file__).resolve().parent
SRC = Path.home()/"Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels/Gag Reel - Season 1.mp4"
OUT = Path.home()/"Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos/Gag Moments"
OUT.mkdir(parents=True, exist_ok=True)
WORK = HERE/"cow_work"; shutil.rmtree(WORK, ignore_errors=True); WORK.mkdir()
START, END = 345.45, 354.60
VID_Y = 700

def oswald(s,w=600):
    f=ImageFont.truetype(str(HERE/"fonts/Oswald.ttf"),s); f.set_variation_by_axes([w]); return f
def mono(s,w="Regular"): return ImageFont.truetype(str(HERE/f"fonts/DMMono-{w}.ttf"),s)
def tracked(d,x,y,s,f,fill,tr):
    for ch in s: d.text((x,y),ch,font=f,fill=fill); x+=d.textlength(ch,font=f)+tr
    return x
def brand(d,x,y,size):
    f=ImageFont.truetype(str(HERE/"fonts/Oswald.ttf"),size); f.set_variation_by_axes([500]); tr=.16*size
    x=tracked(d,x,y,"BOGGS",f,PAPER,tr); x+=.34*size-tr
    xw=d.textlength("X",font=f); d.text((x,y),"X",font=f,fill=PAPER)
    asc,_=f.getmetrics(); cx,cy=x+xw/2,y+asc*.62; r=1.08*size/2
    d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=SIGNAL,width=max(3,round(size*2/23.2)))
    tracked(d,x+xw+.34*size,y,"FILES",f,PAPER,tr)

VENC=["-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-r",str(FPS),
      "-c:a","aac","-b:a","192k","-ar","48000","-ac","2","-video_track_timescale","30000"]

ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
y=250
for ln in ["“HAVE YOU EVER","HAD ANY DEALINGS","WITH A COW?”"]:
    d.text((72,y),ln,font=oswald(96),fill=PAPER); y+=102
d.text((76,y+18),"Season 1 gag reel  ·  from the DVD master",font=mono(26),fill=MUTED)
brand(d,76,H-330,40)
d.text((76,H-270),"boggsfiles.com/gag-reels",font=mono(26,"Medium"),fill=SIGNAL)
p=WORK/"ov.png"; ov.save(p)

end=Image.new("RGB",(W,H),INK); d=ImageDraw.Draw(end)
brand(d,76,700,58)
y=820
for ln in ["THE WHOLE","SEASON 1","GAG REEL."]: d.text((76,y),ln,font=oswald(108),fill=PAPER); y+=114
d.text((76,y+26),"13 minutes, 36 seconds",font=mono(28),fill=MUTED)
d.text((76,y+76),"boggsfiles.com/gag-reels",font=mono(30,"Medium"),fill=SIGNAL)
pe=WORK/"end.png"; end.save(pe)

dur=round(END-START,2)
clip=WORK/"clip.mp4"
subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-ss",str(START),"-t",str(dur),"-i",str(SRC),
  "-i",str(p),"-filter_complex",
  f"[0:v]yadif=deint=interlaced,scale=1080:810:flags=lanczos,setsar=1,pad={W}:{H}:0:{VID_Y}:color=0x0b0e0d[v];"
  f"[v][1:v]overlay=0:0,fps={FPS},format=yuv420p[out];[0:a]aresample=48000[aud]",
  "-map","[out]","-map","[aud]",*VENC,"-movflags","+faststart",str(clip)],check=True)
tail=WORK/"tail.mp4"
subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-loop","1","-t","2.4","-i",str(pe),
  "-f","lavfi","-t","2.4","-i","anullsrc=r=48000:cl=stereo","-vf",f"fps={FPS},format=yuv420p",
  *VENC,"-movflags","+faststart",str(tail)],check=True)
(WORK/"list.txt").write_text("file 'clip.mp4'\nfile 'tail.mp4'\n")
final=OUT/"Boggsfiles Reel - S1 the cow line.mp4"
subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-f","concat","-safe","0","-i","list.txt",
  "-c","copy","-movflags","+faststart",str(final)],check=True,cwd=WORK)
secs=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(final)],
  capture_output=True,text=True).stdout.strip())
print(f"wrote {final}  ({secs:.1f}s)")
