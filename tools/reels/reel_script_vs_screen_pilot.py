"""Script vs. Screen — Pilot. 1080x1920 Instagram Reel.
Real script pages (Goldenrod / First Draft scans) with the key lines highlighted,
answered by the aired footage. Logo rendered from the site's CSS (Oswald 500, .16em tracking,
signal-red circle on the X). Fonts: Oswald + DM Mono (the site's web fonts)."""
import os, subprocess, shutil, math
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

W, H, FPS = 1080, 1920, 30
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (126, 137, 129); LINE = (44, 50, 48)
V = "/Users/lindseyboggs/Movies/Season 1 XF Transcripts/XFDISC1/B1_t00.mkv"

def oswald(size, wght=500):
    f = ImageFont.truetype("fonts/Oswald.ttf", size); f.set_variation_by_axes([wght]); return f
def mono(size, w="Regular"): return ImageFont.truetype(f"fonts/DMMono-{w}.ttf", size)

OUT = "frames"; shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
n = 0
audio_clips = []   # (start_seconds, wav)
def save(img):
    global n; img.save(f"{OUT}/f{n:05d}.png"); n += 1
def ease(t): return t * t * (3 - 2 * t)

# ---------- logo, matching .bf-brand ----------
def tracked(d, x, y, s, f, fill, track):
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
    return x
def brand(d, x=80, y=110, size=58):
    f = oswald(size, 500); track = 0.16 * size
    x = tracked(d, x, y, "BOGGS", f, PAPER, track)
    x += 0.34 * size - track                     # margin: 0 .34em (letter-spacing 0 on the X)
    xw = d.textlength("X", font=f)
    d.text((x, y), "X", font=f, fill=PAPER)
    asc, desc = f.getmetrics(); cx = x + xw / 2; cy = y + asc * 0.62
    r = 1.08 * size / 2; bw = max(3, round(size * 2 / 23.2))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=SIGNAL, width=bw)
    x += xw + 0.34 * size
    tracked(d, x, y, "FILES", f, PAPER, track)
def header(d, eyebrow):
    brand(d)
    d.text((80, 205), eyebrow, font=mono(26, "Medium"), fill=SIGNAL)
    d.line((80, 250, W - 80, 250), fill=LINE, width=2)
def footer(d):
    d.line((80, H - 150, W - 80, H - 150), fill=LINE, width=2)
    d.text((80, H - 122), "boggsfiles.com/script-vs-screen", font=mono(30), fill=PAPER)
    d.text((W - 80, H - 118), "TRUTH STILL MATTERS", font=mono(22), fill=MUTED, anchor="ra")

def wrap(d, s, f, maxw):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines
def para(d, x, y, s, f, fill=PAPER, maxw=W - 160, lh=None):
    lh = lh or int(f.size * 1.22)
    for ln in wrap(d, s, f, maxw): d.text((x, y), ln, font=f, fill=fill); y += lh
    return y

def fade(img, a):
    a = max(0.0, min(1.0, a))
    return img if a >= 1 else Image.blend(Image.new("RGB", (W, H), INK), img, ease(a))

# ---------- script page panel ----------
def page_panel(src, box, hl, w=980, h=620, zoom=1.0):
    """Crop a scanned page, tint to site paper, highlight key lines, return w x h image."""
    im = Image.open(src).convert("L")
    x0, y0, x1, y1 = box
    if zoom != 1.0:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; bw, bh = (x1 - x0) / zoom, (y1 - y0) / zoom
        x0, y0, x1, y1 = cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2
    crop = im.crop((int(x0), int(y0), int(x1), int(y1)))
    crop = ImageOps.colorize(crop, black=(24, 22, 20), white=PAPER).convert("RGBA")
    if hl:
        ov = Image.new("RGBA", crop.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        hx0, hy0, hx1, hy1 = hl
        od.rectangle((hx0 - x0, hy0 - y0, hx1 - x0, hy1 - y0), fill=SIGNAL + (70,))
        crop = Image.alpha_composite(crop, ov)
    return crop.convert("RGB").resize((w, h), Image.LANCZOS)

def clip_frames(name, start, dur):
    d = f"clip_{name}"
    if not os.path.isdir(d):
        os.makedirs(d)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", start, "-t", str(dur), "-i", V, "-an",
                        "-vf", "yadif=deint=all,scale=980:735:flags=lanczos", "-r", str(FPS), f"{d}/%05d.png"], check=True)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", start, "-t", str(dur), "-i", V, "-vn",
                        "-ac", "2", "-ar", "48000", f"{d}/audio.wav"], check=True)
    return d, sorted(f for f in os.listdir(d) if f.endswith(".png"))

def title_card(eyebrow, big, sub, seconds, first=False):
    base = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(base); header(d, eyebrow)
    y = 620
    for ln in big:
        d.text((76, y), ln, font=oswald(150, 600), fill=PAPER); y += 158
    y += 36
    for s in sub:
        y = para(d, 80, y, s, mono(32), fill=MUTED, lh=46) + 14
    footer(d)
    total = int(seconds * FPS); fr = int(0.4 * FPS)
    for i in range(total):
        a = min(i / fr, (total - 1 - i) / fr) if fr else 1
        save(fade(base, a))

def compare(eyebrow, page, box, hl, page_label, page_caption, clip, clip_label, clip_caption, hold=3.0, page2=None):
    """Page appears alone (hold seconds) with its caption; then the footage plays beneath it."""
    global n
    # -- page alone, slow zoom in on the page (panel 980x760)
    total = int(hold * FPS); fr = int(0.4 * FPS)
    for i in range(total):
        z = 1.0 + 0.03 * ease(i / max(1, total - 1))
        img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img); header(d, eyebrow)
        d.text((80, 292), page_label, font=mono(24, "Medium"), fill=SIGNAL)
        pnl = page_panel(page, box, hl, w=980, h=760, zoom=z); img.paste(pnl, (50, 330))
        d.rectangle((50, 330, 1030, 1090), outline=LINE, width=2)
        y = para(d, 80, 1140, page_caption, oswald(54, 500), lh=64)
        d.polygon([(82, y + 44), (106, y + 44), (94, y + 62)], fill=MUTED)
        d.text((124, y + 40), "ON SCREEN", font=mono(26, "Medium"), fill=MUTED)
        footer(d)
        save(fade(img, i / fr if i < fr else 1))
    # -- footage beneath the page
    cd, frames = clip_frames(clip[0], clip[1], clip[2])
    audio_clips.append((n / FPS, f"{cd}/audio.wav"))
    if page2: pnl = page_panel(page2[0], page2[1], page2[2], w=980, h=380)
    else:
        bw = box[2] - box[0]; cy = (hl[1] + hl[3]) / 2; bh = bw / (980 / 380)
        pnl = page_panel(page, (box[0], cy - bh / 2, box[2], cy + bh / 2), hl, w=980, h=380)
    ctotal = len(frames); label2 = page2[3] if page2 else page_label
    for i, f in enumerate(frames):
        img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img); header(d, eyebrow)
        d.text((80, 292), label2, font=mono(24, "Medium"), fill=SIGNAL)
        img.paste(pnl, (50, 330)); d.rectangle((50, 330, 1030, 710), outline=LINE, width=2)
        d.text((80, 750), clip_label, font=mono(24, "Medium"), fill=SIGNAL)
        vf = Image.open(f"{cd}/{f}"); img.paste(vf, (50, 790)); d.rectangle((50, 790, 1030, 1525), outline=LINE, width=2)
        para(d, 80, 1560, clip_caption, oswald(44, 500), lh=54)
        footer(d)
        a = min(1, (ctotal - 1 - i) / fr) if i > ctotal - fr else 1
        save(fade(img, a))

EYE = "SCRIPT VS. SCREEN  ·  1X79 PILOT  ·  1993"
# 1. opener
title_card(EYE, ["WHAT CHANGED", "BETWEEN THE", "PAGE AND", "THE SCREEN?"],
           ["Three archived drafts of the Pilot, read against the aired episode.",
            "White · Blue · Goldenrod. Here are three things that moved."], 3.2)

# 2. Quantico classroom (cut)
compare(EYE, "hi_class-03.pgm", (200, 1275, 1660, 2407), (200, 1755, 1660, 1985),
        "ON THE PAGE  ·  GOLDENROD DRAFT  ·  APRIL 2, 1993",
        "Scully is introduced mid-lecture at Quantico, teaching the physiology of electrocution.",
        ("class", "00:02:26.0", 7.5), "ON SCREEN  ·  AIRED SEPTEMBER 10, 1993",
        "The lecture was never filmed. She walks into FBI Headquarters instead.")

# 3. Mosquito bites (stage direction vs. aired)
compare(EYE, "hi_mosq-33.pgm", (180, 1213, 1720, 2407), (180, 1675, 1720, 1805),
        "ON THE PAGE  ·  GOLDENROD DRAFT  ·  SCENE 62",
        "The stage direction: Mulder runs one hand gently down to the base of her spine.",
        ("mosq", "00:26:51.5", 9.5), "ON SCREEN  ·  “MOSQUITO BITES.”",
        "What aired is the candle, the marks, and the hug. Same words, different scene.")

# 4. Produce section (cut, then restored)
compare(EYE, "hi_fd51-51.pgm", (300, 870, 1500, 1800), (300, 1110, 1500, 1215),
        "ON THE PAGE  ·  FIRST DRAFT  ·  DECEMBER 17, 1992",
        "The Orderly gets a joke: not my ward, not my aisle of the produce section.",
        ("nurse", "00:37:44.6", 9.6), "ON SCREEN  ·  RESTORED, ALMOST WORD FOR WORD",
        "Cut from Blue. Gone from Goldenrod. Back on screen, and given to the Nurse.",
        page2=("hi_gold48-48.pgm", (250, 690, 1380, 1128), (250, 862, 1380, 955), "GOLDENROD DRAFT  ·  APRIL 2, 1993  ·  THE JOKE IS GONE"))

# 5. closer
title_card(EYE, ["THE FULL", "REPORT IS", "ON THE", "ARCHIVE."],
           ["Draft history, deleted scenes, and every line that changed.",
            "boggsfiles.com  ·  Script vs. Screen"], 3.4)


# ---------- drone bed (original, synthesized): full under titles/pages, ducked under aired dialogue ----------
import numpy as np, wave
SR = 48000; dur = n / FPS; t = np.arange(int(dur * SR)) / SR
rng = np.random.default_rng(7)
def tone(f, amp, lfo=0.0, rate=0.1): return amp * (1 + lfo * np.sin(2 * np.pi * rate * t)) * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
bed = tone(55, 0.30, 0.25, 0.07) + tone(55.4, 0.22, 0.25, 0.05) + tone(110, 0.10, 0.4, 0.11) + tone(58.27, 0.08, 0.5, 0.03) + tone(233.1, 0.025, 0.6, 0.13)
noise = rng.normal(0, 1, len(t)); b = np.zeros_like(noise); acc = 0.0
for k in range(0, len(noise), 4800):                      # cheap one-pole low-pass, block-wise
    seg = noise[k:k + 4800]; out = np.empty_like(seg)
    for j, v in enumerate(seg): acc += 0.015 * (v - acc); out[j] = acc
    b[k:k + 4800] = out
bed += 0.9 * b / (np.abs(b).max() + 1e-9) * 0.12 * (1 + 0.5 * np.sin(2 * np.pi * 0.045 * t))
env = np.ones_like(t)
for start, wav in audio_clips:
    with wave.open(wav) as wf: cdur = wf.getnframes() / wf.getframerate()
    a, z = int(start * SR), int((start + cdur) * SR); r = int(0.6 * SR)
    env[a + r:z - r] = 0.22
    env[a:a + r] = np.linspace(1, 0.22, r); env[z - r:z] = np.linspace(0.22, 1, r)
fr = int(1.2 * SR); env[:fr] *= np.linspace(0, 1, fr); env[-int(2.0 * SR):] *= np.linspace(1, 0, int(2.0 * SR))
bed = bed * env; bed = bed / (np.abs(bed).max() + 1e-9) * 0.35
pcm = (bed * 32767).astype("<i2")
with wave.open("drone.wav", "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(np.repeat(pcm, 2).tobytes())
audio_clips.append((0.0, "drone.wav"))

# ---------- encode ----------
dur = n / FPS
cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{OUT}/f%05d.png",
       "-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
for _, wav in audio_clips: cmd += ["-i", wav]
fc = "".join(f"[{i + 2}:a]adelay={int(s * 1000)}|{int(s * 1000)},afade=t=in:d=0.25,afade=t=out:st={max(0, 0):.2f}:d=0[a{i}];" for i, (s, _) in enumerate(audio_clips))
fc = "".join(f"[{i + 2}:a]afade=t=in:d=0.3,adelay={int(s * 1000)}|{int(s * 1000)}[a{i}];" for i, (s, _) in enumerate(audio_clips))
fc += "[1:a]" + "".join(f"[a{i}]" for i in range(len(audio_clips))) + f"amix=inputs={len(audio_clips) + 1}:normalize=0:duration=first[aout]"
cmd += ["-filter_complex", fc, "-map", "0:v", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "reel_svs_pilot.mp4"]
subprocess.run(cmd, check=True)
print(f"{n} frames, {dur:.1f}s")
