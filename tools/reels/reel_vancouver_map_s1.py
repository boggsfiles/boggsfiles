"""Instagram Reel (1080x1920, 30 fps, ~28 s): the Season 1 Vancouver locations map, hyped.
Opens on the map with no pins, then pins drop in episode by episode while the counter climbs,
intercut with sharp location stills (Real-ESRGAN upscales in hd_frames/). Ends on the address list
scrolling and a "now live" card. Audio is the house synthesized drone bed only, so the licensed
song can be added in Instagram. Same brand block as the other reels."""
import os, json, math, shutil, subprocess, wave
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys; sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "location-map"))
from s1_sources import ROWS
from s1_fan import EXTRA, DROP

W, H, FPS = 1080, 1920, 30
INK = (11, 14, 13); PAPER = (232, 230, 220); SIGNAL = (183, 56, 49); MUTED = (126, 137, 129); LINE = (44, 50, 48)
PANEL = (17, 22, 20); ROAD = (52, 64, 58); ROAD2 = (36, 44, 40); COAST = (127, 167, 180)
HERE = Path(__file__).resolve().parent
OUTDIR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Music Videos"
WORK = Path("vanmap_work"); shutil.rmtree(WORK, ignore_errors=True); WORK.mkdir()
FR = WORK / "frames"; FR.mkdir()

def oswald(size, wght=500):
    f = ImageFont.truetype(str(HERE / "fonts/Oswald.ttf"), size); f.set_variation_by_axes([wght]); return f
def mono(size, w="Regular"): return ImageFont.truetype(str(HERE / f"fonts/DMMono-{w}.ttf"), size)
def tracked(d, x, y, s, f, fill, track):
    for ch in s: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
    return x
def brand(d, x=80, y=150, size=58):
    f = oswald(size, 500); track = 0.16 * size
    x = tracked(d, x, y, "BOGGS", f, PAPER, track); x += 0.34 * size - track
    xw = d.textlength("X", font=f); d.text((x, y), "X", font=f, fill=PAPER)
    asc, _ = f.getmetrics(); cx, cy = x + xw / 2, y + asc * 0.62; r = 1.08 * size / 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=SIGNAL, width=max(3, round(size * 2 / 23.2)))
    tracked(d, x + xw + 0.34 * size, y, "FILES", f, PAPER, track)
FOOT_Y = 1500
def footer(d):
    d.line((80, FOOT_Y, W - 80, FOOT_Y), fill=LINE, width=2)
    d.text((80, FOOT_Y + 26), "boggsfiles.com/locations", font=mono(30), fill=PAPER)
    d.text((W - 80, FOOT_Y + 30), "THE VANCOUVER MAP", font=mono(22), fill=MUTED, anchor="ra")
def ease(t): return t * t * (3 - 2 * t)
def wrap(d, s, f, maxw):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
n = 0
def save(img):
    global n; img.save(FR / f"f{n:05d}.png"); n += 1
def fade(img, a):
    a = max(0.0, min(1.0, a)); return img if a >= 1 else Image.blend(Image.new("RGB", (W, H), INK), img, ease(a))

# ---------- data: pins in episode order ----------
geo = json.loads((HERE.parent / "location-map" / "geocache.json").read_text())
ORDER = ['1X79'] + [f'1X{i:02d}' for i in range(1, 24)]
pins = []
for ep, title, name, addr, city, played, srcs, conf, note, q in ROWS:
    if (ep, name) in DROP or not geo.get(q): continue
    pins.append((ORDER.index(ep), ep, title, name, addr, city, geo[q][0], geo[q][1], 'book' in srcs))
for ep, title, name, addr, city, lat, lon, played, srcs, conf, note in EXTRA:
    pins.append((ORDER.index(ep), ep, title, name, addr, city, lat, lon, 'book' in srcs))
pins.sort(key=lambda p: p[0]); N_PLACES = len({(p[3], p[4]) for p in pins})

# ---------- map ----------
BASE = json.loads((HERE / "vancouver_base.json").read_text())
MW, MH = 1080, 900
lon0, lon1, lat0, lat1 = -123.32, -122.55, 48.99, 49.44
kx = math.cos(math.radians(49.2)); sc = min(MW / ((lon1 - lon0) * kx), MH / (lat1 - lat0))
cx, cy = (lon0 + lon1) / 2, (lat0 + lat1) / 2
def P(lon, lat): return (MW / 2 + (lon - cx) * kx * sc, MH / 2 - (lat - cy) * sc)
def basemap():
    SS = 2; im = Image.new("RGB", (MW * SS, MH * SS), PANEL); d = ImageDraw.Draw(im)
    def lines(key, fill, width):
        for ln in BASE[key]:
            pts = [(x * SS, y * SS) for x, y in (P(a, b) for a, b in ln)]
            if any(-60 < x < MW * SS + 60 and -60 < y < MH * SS + 60 for x, y in pts): d.line(pts, fill=fill, width=width * SS, joint="curve")
    lines("rd", ROAD2, 1); lines("mw", ROAD, 2); lines("water", COAST, 2); lines("coast", COAST, 2)
    im = im.resize((MW, MH), Image.LANCZOS); d = ImageDraw.Draw(im)
    for name, lon, lat in [("VANCOUVER", -123.118, 49.262), ("NORTH VANCOUVER", -123.072, 49.335), ("WEST VANCOUVER", -123.215, 49.345), ("BURNABY", -122.972, 49.243),
                           ("RICHMOND", -123.13, 49.165), ("COQUITLAM", -122.80, 49.283), ("SURREY", -122.82, 49.12), ("DELTA", -123.03, 49.085), ("LANGLEY", -122.62, 49.09), ("WHITE ROCK", -122.80, 49.02), ("MAPLE RIDGE", -122.60, 49.22)]:
        x, y = P(lon, lat); f = oswald(22, 400); tw = sum(d.textlength(c, font=f) + 3 for c in name)
        tracked(d, x - tw / 2, y, name, f, MUTED, 3)
    return im
MAP = basemap()
def map_frame(k_pins, pulse=None, counter=None, ep_label=None, kicker="EVERY LOCATION. SEASON ONE."):
    """k_pins pins drawn; `pulse` = (index, 0..1) ring animation on the newest pin. Counter sits above the map."""
    MY = 560
    img = Image.new("RGB", (W, H), INK); img.paste(MAP, (0, MY)); d = ImageDraw.Draw(img)
    brand(d); d.text((80, 240), kicker, font=mono(28, "Medium"), fill=SIGNAL)
    if counter is not None:
        d.text((80, 290), f"{counter}", font=oswald(150, 600), fill=PAPER)
        d.text((80 + d.textlength(f"{counter}", font=oswald(150, 600)) + 24, 368), "LOCATIONS", font=mono(34, "Medium"), fill=MUTED)
    if ep_label: d.text((80, 490), ep_label, font=mono(28, "Medium"), fill=PAPER)
    d.line((0, MY, W, MY), fill=LINE, width=2); d.line((0, MY + MH, W, MY + MH), fill=LINE, width=2)
    for i, p in enumerate(pins[:k_pins]):
        x, y = P(p[7], p[6]); y += MY; c = SIGNAL if p[8] else (92, 194, 166)
        if MY < y < MY + MH: d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=c, outline=PANEL, width=2)
    if pulse:
        i, t = pulse; p = pins[i]; x, y = P(p[7], p[6]); y += MY; r = 10 + 40 * t
        if MY < y < MY + MH: d.ellipse((x - r, y - r, x + r, y + r), outline=(SIGNAL if p[8] else (92, 194, 166)), width=max(1, int(4 * (1 - t))))
    footer(d); return img

def still(ep, name, kicker, caption, seconds):
    hd = HERE / "hd_frames" / f"{ep[:4]}_{name}.png"
    im = Image.open(hd).convert("RGB") if hd.exists() else Image.open(Path.home() / "Movies/XF_screencaps/series/S01" / ep / "full" / f"{name}.jpg").convert("RGB")
    total = int(seconds * FPS); fr = int(0.3 * FPS)
    for i in range(total):
        z = 1.0 + 0.04 * ease(i / max(1, total - 1))           # slow push-in
        pw = int(W * z); ph = int(pw * 3 / 4); pic = im.resize((pw, ph), Image.LANCZOS).crop(((pw - W) // 2, (ph - 810) // 2, (pw - W) // 2 + W, (ph - 810) // 2 + 810))
        img = Image.new("RGB", (W, H), INK); img.paste(pic, (0, 330)); d = ImageDraw.Draw(img)
        brand(d); d.text((80, 240), kicker, font=mono(28, "Medium"), fill=SIGNAL)
        y = 330 + 810 + 50
        for ln in wrap(d, caption, oswald(64, 500), W - 160): d.text((80, y), ln, font=oswald(64, 500), fill=PAPER); y += 74
        footer(d); save(fade(img, min(i / fr, (total - 1 - i) / fr)))

def card(lines, sub, seconds, kicker=""):
    base = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(base); brand(d)
    if kicker: d.text((80, 240), kicker, font=mono(28, "Medium"), fill=SIGNAL)
    y = 400
    for ln in lines: d.text((76, y), ln, font=oswald(150, 600), fill=PAPER); y += 158
    y += 40
    for s in sub:
        for ln in wrap(d, s, mono(34), W - 160): d.text((80, y), ln, font=mono(34), fill=MUTED); y += 48
        y += 16
    footer(d); total = int(seconds * FPS); fr = int(0.35 * FPS)
    for i in range(total): save(fade(base, min(i / fr, (total - 1 - i) / fr)))


# ---------- site demo (phone captures of the preview page, in vanmap_demo/) ----------
DEMO = HERE / "vanmap_demo"
def phone(page, caption, kicker="THE MAP · BOGGSFILES.COM"):
    """A 1080x1920 page capture inset as a phone, caption above it, everything clear of Instagram's bottom overlay."""
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
    brand(d); d.text((80, 240), kicker, font=mono(28, "Medium"), fill=SIGNAL)
    d.text((80, 300), caption, font=oswald(56, 500), fill=PAPER)
    pw, ph = 600, 1066; pic = page.resize((pw, ph), Image.LANCZOS)
    mask = Image.new("L", (pw, ph), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw - 1, ph - 1), radius=48, fill=255)
    x, y = (W - pw) // 2, 410; img.paste(pic, (x, y), mask)
    d.rounded_rectangle((x - 6, y - 6, x + pw + 6, y + ph + 6), radius=54, outline=LINE, width=6)
    return img
def demo_hold(name, caption, seconds, fade_in=0.3):
    base = Image.open(DEMO / f"{name}.png").convert("RGB"); total = int(seconds * FPS); fr = int(fade_in * FPS)
    for i in range(total): save(fade(phone(base, caption), (i / fr) if i < fr else 1))
def demo_scroll(y0, y1, caption, seconds):
    tall = Image.open(DEMO / "tall.png").convert("RGB"); total = int(seconds * FPS)
    for i in range(total):
        yy = int(y0 + (y1 - y0) * ease(i / max(1, total - 1)))
        save(phone(tall.crop((0, yy, 1080, yy + 1920)), caption))
def demo_xfade(a, b, caption, seconds):
    A = phone(Image.open(DEMO / f"{a}.png").convert("RGB"), caption); B = phone(Image.open(DEMO / f"{b}.png").convert("RGB"), caption)
    total = int(seconds * FPS)
    for i in range(total): save(Image.blend(A, B, ease(i / max(1, total - 1))))

# ---------- sequence ----------
# 1. empty map, 2.2 s
total = int(2.2 * FPS)
for i in range(total): save(fade(map_frame(0, counter=0, ep_label="PILOT · 1993"), i / int(0.5 * FPS)))
# 2. pins drop in, episode by episode, 9 s; counter climbs
drop_total = int(7.0 * FPS); per = drop_total / len(pins); placed = 0
for i in range(drop_total):
    k = min(len(pins), int(i / per) + 1); p = pins[k - 1]
    t = (i - (k - 1) * per) / per
    seen = len({(q[3], q[4]) for q in pins[:k]})
    save(map_frame(k, pulse=(k - 1, min(1, t)), counter=seen, ep_label=f"{p[1].replace('1X', '')} · {p[2].upper()}"))
# 3. hold the full map
for i in range(int(1.6 * FPS)): save(map_frame(len(pins), counter=N_PLACES, ep_label="24 EPISODES · 1993–94"))
# 3b. site demo
demo_scroll(0, 1900, "Scroll the map.", 1.6)
demo_xfade("s1", "s2", "Tap any pin.", 0.5); demo_hold("s2", "Tap any pin.", 1.3, 0)
demo_xfade("s2", "s3", "Every address. Google Maps link.", 0.5); demo_hold("s3", "Every address. Google Maps link.", 1.3, 0)
demo_xfade("s3", "s4", "Jump to any episode.", 0.5); demo_hold("s4", "Jump to any episode.", 1.3, 0)
demo_xfade("s4", "s5", "Tap a location, the map zooms in.", 0.5); demo_hold("s5", "Tap a location, the map zooms in.", 1.4, 0)
demo_xfade("s5", "s6", "All 24 episodes.", 0.5); demo_hold("s6", "All 24 episodes.", 1.1, 0)
# 4. stills
still("1X01 Deep Throat", "002521469", "DEEP THROAT · 1X01", "The motel is in Tsawwassen.", 2.3)
still("1X23 The Erlenmeyer Flask", "001876908", "THE ERLENMEYER FLASK · 1X23", "The warehouse is on Pandora Street.", 2.3)
still("1X19 Darkness Falls", "001093175", "DARKNESS FALLS · 1X19", "The forest is in North Vancouver.", 2.3)
still("1X21 Born Again", "001648046", "BORN AGAIN · 1X21", "Every one, with the street address.", 2.3)
# 5. closing cards
card(["EVERY", "LOCATION.", "SEASON", "ONE."], [f"{N_PLACES} places. 24 episodes. One map.", "Now live at boggsfiles.com"], 3.2, "THE X-FILES IN VANCOUVER")
card(["THE", "TRUTH", "IS OUT", "THERE."], ["And now you know where.", "boggsfiles.com · The Vancouver Map"], 2.8)

# ---------- drone bed (original, synthesized) ----------
SR = 48000; dur = n / FPS; t = np.arange(int(dur * SR)) / SR; rng = np.random.default_rng(7)
def tone(f, amp, lfo=0.0, rate=0.1): return amp * (1 + lfo * np.sin(2 * np.pi * rate * t)) * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
bed = tone(55, 0.30, 0.25, 0.07) + tone(55.4, 0.22, 0.25, 0.05) + tone(110, 0.10, 0.4, 0.11) + tone(58.27, 0.08, 0.5, 0.03) + tone(233.1, 0.025, 0.6, 0.13)
fi, fo = int(1.0 * SR), int(2.0 * SR); bed[:fi] *= np.linspace(0, 1, fi); bed[-fo:] *= np.linspace(1, 0, fo)
bed = bed / (np.abs(bed).max() + 1e-9) * 0.3; pcm = (bed * 32767).astype("<i2")
with wave.open(str(WORK / "drone.wav"), "wb") as wf: wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(np.repeat(pcm, 2).tobytes())

out = OUTDIR / "Boggsfiles Reel - Vancouver Map S1.mp4"
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(FR / "f%05d.png"), "-i", str(WORK / "drone.wav"),
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
print(f"{n} frames, {dur:.1f}s ->", out)
