"""Good Neighbor Day reel: the Season 6 gag reel couch moment, then Arcadia.

Opens on the gag - 142.402 to 150.911 is one continuous shot, checked frame by frame, so the
clip sits safely inside it. Then the episode's neighbourhood beats, closing on the publicity
photo, which is the only high-resolution image in the set and earns the last card.

ffmpeg here has no drawtext filter, so captions are drawn with PIL.
"""
import os, glob, json, shutil, subprocess
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
INK=(11,14,13); PAPER=(232,230,220); SIGNAL=(224,121,108); MUTED=(150,158,151); LINE=(44,50,48)
F = "tools/reels/fonts"
GAG = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels/Gag Reel - Season 6.mp4")
SCR = os.path.expanduser("~/Movies/XF_screencaps/series/S06/6X13 Arcadia/full")
S   = "/private/tmp/claude-501/-Users-lindseyboggs-Sites-boggsfiles/261dd1eb-8941-4607-87c5-4e3fef009978/scratchpad/gnd"
PRESS = f"{S}/press_hires.jpg"
OUT = os.path.expanduser("~/Desktop/Good Neighbor Day.mp4")
FR  = f"{S}/frames"; shutil.rmtree(FR, ignore_errors=True); os.makedirs(FR)

def osw(s,w=500):
    f=ImageFont.truetype(f"{F}/Oswald.ttf",s); f.set_variation_by_axes([w]); return f
def mono(s,w="Medium"): return ImageFont.truetype(f"{F}/DMMono-{w}.ttf",s)
def tracked(d,x,y,s,f,fill,tr):
    for ch in s: d.text((x,y),ch,font=f,fill=fill); x+=d.textlength(ch,font=f)+tr

caps = json.load(open(f"{S}/caps.json"))
PICKS = [1, 2, 19, 7, 22, 25, 41, 30]          # sign, moving in, welcome wagon, door, dinner, dog, neighbour, mailbox

GAG_IN, GAG_LEN = 142.45, 8.35
BOX_H, BOX_Y = 810, 470

# ---- the gag, as a frame sequence ----
seq = f"{S}/gagseq"; shutil.rmtree(seq, ignore_errors=True); os.makedirs(seq)
subprocess.run(["/opt/homebrew/bin/ffmpeg","-y","-v","error","-ss",str(GAG_IN),"-t",str(GAG_LEN),
    "-i",GAG,"-vf",f"yadif,scale={W}:{BOX_H},setsar=1,fps={FPS}",f"{seq}/%05d.png"],check=True)
gag = sorted(glob.glob(f"{seq}/*.png"))
subprocess.run(["/opt/homebrew/bin/ffmpeg","-y","-v","error","-ss",str(GAG_IN),"-t",str(GAG_LEN),
    "-i",GAG,"-vn","-ar","48000","-ac","2",f"{S}/gag.wav"],check=True)

STILL = 1.30
beats = [("gag", None, 0.0, GAG_LEN)]
t = GAG_LEN
for n in PICKS:
    beats.append(("cap", caps[n-1], t, t+STILL)); t += STILL
beats.append(("press", PRESS, t, t+2.9)); t += 2.9
DUR = t

def fit(path, box_h):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    s = max(W/im.width, box_h/im.height)*1.06
    im = im.resize((round(im.width*s), round(im.height*s)), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=45, threshold=3))

cache={}
def ease(x): return x*x*(3-2*x)
f_hook, f_end, f_sub = osw(60), osw(54), mono(24,"Light")

total=int(DUR*FPS)
for i in range(total):
    tt=i/FPS
    kind, ref, a, b = next((x for x in beats if x[2] <= tt < x[3]), beats[-1])
    p=(tt-a)/(b-a)
    fr=Image.new("RGB",(W,H),INK)
    if kind=="gag":
        fr.paste(Image.open(gag[min(len(gag)-1, round((tt-a)*FPS))]).convert("RGB"), (0,BOX_Y))
    elif kind=="cap":
        if ref not in cache: cache[ref]=fit(ref, BOX_H)
        im=cache[ref]; z=1.06-0.06*ease(p)
        cw,ch=round(W/z),round(BOX_H/z)
        cx=(im.width-cw)//2; cy=(im.height-ch)//2
        fr.paste(im.crop((cx,cy,cx+cw,cy+ch)).resize((W,BOX_H),Image.LANCZOS),(0,BOX_Y))
    else:
        PH=1180; PY=330
        if ref not in cache: cache[ref]=fit(ref, PH)
        im=cache[ref]; z=1.05-0.05*ease(p)
        cw,ch=round(W/z),round(PH/z)
        cx=(im.width-cw)//2; cy=int((im.height-ch)*0.30)
        fr.paste(im.crop((cx,cy,cx+cw,cy+ch)).resize((W,PH),Image.LANCZOS),(0,PY))
    d=ImageDraw.Draw(fr)
    top = BOX_Y if kind!="press" else 330
    bot = top + (BOX_H if kind!="press" else 1180)
    d.line([(0,top-1),(W,top-1)],fill=LINE); d.line([(0,bot),(W,bot)],fill=LINE)

    if kind=="gag" and tt<GAG_LEN-0.4:
        al=min(1.0,max(0.0,(tt-0.2)/0.5))*(1.0 if tt<GAG_LEN-1.0 else max(0.0,(GAG_LEN-0.4-tt)/0.6))
        lay=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
        ld.text((66,bot+80),"THEY PLAYED THE",font=f_hook,fill=PAPER+(255,))
        ld.text((66,bot+148),"PERFECT NEIGHBORS.",font=f_hook,fill=PAPER+(255,))
        ld.text((66,bot+236),"BADLY.",font=f_hook,fill=SIGNAL+(255,))
        arr=np.array(lay).astype(np.float32); arr[...,3]*=al
        fr=Image.alpha_composite(fr.convert("RGBA"),Image.fromarray(arr.astype(np.uint8))).convert("RGB")
    elif kind=="press":
        al=min(1.0,(tt-a)/0.5)
        lay=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
        ld.text((66,1590),"HAPPY GOOD",font=f_end,fill=PAPER+(255,))
        ld.text((66,1652),"NEIGHBOR DAY.",font=f_end,fill=SIGNAL+(255,))
        tracked(ld,68,1740,"ARCADIA  ·  6X13  ·  1999",f_sub,MUTED+(255,),2.4)
        arr=np.array(lay).astype(np.float32); arr[...,3]*=al
        fr=Image.alpha_composite(fr.convert("RGBA"),Image.fromarray(arr.astype(np.uint8))).convert("RGB")

    fr.save(f"{FR}/f{i:05d}.png")
    if i%150==0: print(f"    {i}/{total}",flush=True)

print("  encoding...")
subprocess.run(["/opt/homebrew/bin/ffmpeg","-y","-hide_banner","-loglevel","error",
    "-framerate",str(FPS),"-i",f"{FR}/f%05d.png","-i",f"{S}/gag.wav",
    "-c:v","libx264","-profile:v","high","-pix_fmt","yuv420p","-crf","19",
    "-c:a","aac","-b:a","192k","-af",f"apad,atrim=0:{DUR}",
    "-movflags","+faststart",OUT],check=True)
print(f"  saved {OUT}  {DUR:.1f}s")
