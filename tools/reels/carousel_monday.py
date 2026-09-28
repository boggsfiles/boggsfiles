"""Manic Monday carousel: the three rare Monday stills, then the episode's own beats.

Slides are 1080x1350. The three publicity stills are enormous (up to 7071x4799) so they are
downscaled, never pushed up; the screencaps that follow are 720x540 and sit in a framed box
rather than being blown out to full bleed, which at that size would show.
"""
import os, glob, json
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
INK=(11,14,13); PAPER=(232,230,220); SIGNAL=(224,121,108); MUTED=(150,158,151); LINE=(44,50,48)
F = "tools/reels/fonts"
RARE = os.path.expanduser("~/Desktop/X-Files/XF rare pics from episodes/Season 6")
CAPS = os.path.expanduser("~/Movies/XF_screencaps/series/S06/6X15 Monday/full")
OUT  = os.path.expanduser("~/Desktop/Manic Monday carousel")
os.makedirs(OUT, exist_ok=True)

def osw(s,w=500):
    f=ImageFont.truetype(f"{F}/Oswald.ttf",s); f.set_variation_by_axes([w]); return f
def mono(s,w="Medium"): return ImageFont.truetype(f"{F}/DMMono-{w}.ttf",s)
def tracked(d,x,y,s,f,fill,tr):
    for ch in s: d.text((x,y),ch,font=f,fill=fill); x+=d.textlength(ch,font=f)+tr

caps = sorted(glob.glob(f"{CAPS}/*.jpg"))
def cap(frac): return caps[int(len(caps)*frac)]

SLIDES = [
    (f"{RARE}/Season 6 Rare 79.jpg", "A BAD DAY", "that keeps getting worse"),
    (f"{RARE}/Season 6 Rare 80.jpg", "AGAIN",     "the bank, every single time"),
    (f"{RARE}/Season 6 Rare 71.jpg", "BEHIND IT", "on set, 1999"),
    (cap(0.02), "6X15",            "Craddock Marine Bank"),
    (cap(0.05), "WAKE UP",         "the waterbed, the leak, the same morning"),
    (cap(0.52), "THE LOOP",        "she is the only one who remembers"),
    (cap(0.76), "BERNARD",         "the man who never gets out"),
    (None,      "MONDAY",          "Season 6 · aired 28 February 1999"),
]

def framed(path, box_w, box_h):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    s = max(box_w/im.width, box_h/im.height)
    im = im.resize((round(im.width*s), round(im.height*s)), Image.LANCZOS)
    if s > 1.15:
        im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=45, threshold=3))
    x=(im.width-box_w)//2; y=int((im.height-box_h)*0.42)
    return im.crop((x,y,x+box_w,y+box_h))

BOX_Y, BOX_H = 250, 810
for i,(path,big,small) in enumerate(SLIDES, 1):
    img=Image.new("RGB",(W,H),INK); d=ImageDraw.Draw(img)
    if path:
        img.paste(framed(path, W, BOX_H),(0,BOX_Y))
        d.line([(0,BOX_Y-1),(W,BOX_Y-1)],fill=LINE); d.line([(0,BOX_Y+BOX_H),(W,BOX_Y+BOX_H)],fill=LINE)
        tracked(d,66,150,"THE X-FILES  ·  MONDAY",mono(22),MUTED,3.4)
        d.text((62,BOX_Y+BOX_H+56),big,font=osw(74,600),fill=PAPER)
        d.text((64,BOX_Y+BOX_H+148),small,font=osw(38,300),fill=MUTED)
    else:
        tracked(d,66,150,"THE X-FILES",mono(22),MUTED,3.4)
        d.text((58,300),"MANIC",font=osw(150,600),fill=PAPER)
        d.text((58,450),"MONDAY",font=osw(150,600),fill=SIGNAL)
        d.line([(66,660),(W-66,660)],fill=LINE,width=2)
        d.text((62,720),"Season 6, episode 15.",font=osw(46,300),fill=PAPER)
        d.text((62,782),"Aired 28 February 1999.",font=osw(46,300),fill=PAPER)
        d.text((62,880),"Three rare publicity stills,",font=osw(40,300),fill=MUTED)
        d.text((62,932),"scanned from the originals.",font=osw(40,300),fill=MUTED)
        tracked(d,66,1180,"BOGGSFILES.COM",mono(24),SIGNAL,2.8)
    img.save(f"{OUT}/{i:02d}.jpg", quality=92)
print(f"  {len(SLIDES)} slides -> {OUT}")
