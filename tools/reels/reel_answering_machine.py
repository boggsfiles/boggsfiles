"""Reel for the Agua Mala answering-machine wild track: the sound is the artifact.

Three beats cut from the one recording -- take 1 with the words arriving as he says them, the
mixer's slate, then take 3 under the closing lines. The waveform is drawn from the audio itself
and fills as it plays; the half of the message that is not in the episode fills in the signal
colour, so the cut is visible before anyone reads a word.

Stills are the archive's own DVD captures of the scene the message plays over (the empty
apartment, then the machine on the desk), copied from the screencap archive. The only sound that is not on the recording is the beep before
the end card; set BEEP = False to drop it.
"""
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 24
SR = 44100
INK = (11, 14, 13)
PAPER = (232, 230, 220)
SIGNAL = (224, 121, 108)
MUTED = (139, 147, 140)
DIM = (107, 116, 109)
LINE = (44, 50, 48)

HERE = Path(__file__).parent
F = HERE / "fonts"
STILLS = HERE / "stills_cache" / "agua-mala"
AUDIO = Path.home() / "Desktop" / "Fox Mulder Outgoing Message.m4a"
OUT = Path.home() / "Desktop" / "Boggsfiles answering machine reel"

MARGIN = 72
BEEP = True

# (source in, source out, gain) -- the slate is off-mic and needs lifting to be heard at all
TAKE1 = (1.45, 8.35, 1.0)
SLATE = (14.55, 17.35, 2.6)
TAKE3 = (26.95, 33.75, 1.15)

# source-time word starts for take 1; the second sentence is the one the episode drops
AIRED = [("Hi,", 1.64), ("this", 2.08), ("is", 2.14), ("Fox", 2.28), ("Mulder.", 2.52),
         ("You", 3.02), ("can", 3.08), ("leave", 3.16), ("me", 3.30), ("a", 3.40),
         ("message", 3.50), ("after", 3.72), ("the", 4.04), ("beep.", 4.18)]
CUT = [("If", 4.56), ("this", 4.62), ("is", 4.78), ("you,", 4.90), ("Scully,", 5.22),
       ("call", 5.60), ("me", 5.72), ("on", 5.84), ("my", 5.94), ("cell", 6.12),
       ("phone.", 6.28), ("\nI", 6.90), ("think", 7.22), ("you", 7.36), ("know", 7.46),
       ("the", 7.58), ("number.", 7.72)]
SLATE_WORDS = [("“This", 14.78), ("will", 15.00), ("be", 15.08), ("take", 15.18),
               ("two,", 15.36), ("channel", 15.64), ("two.”", 15.82)]
CUT_AT_3 = 29.82  # where the dropped sentence starts in take 3


def osw(size, weight=500):
    f = ImageFont.truetype(str(F / "Oswald.ttf"), size)
    f.set_variation_by_axes([weight])
    return f


def mono(size, cut="Medium"):
    return ImageFont.truetype(str(F / f"DMMono-{cut}.ttf"), size)


def tracked(d, x, y, s, f, fill, tr):
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tr


def tracked_width(d, s, f, tr):
    return sum(d.textlength(ch, font=f) + tr for ch in s) - tr


def load_audio():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(AUDIO), "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def cut(src, seg):
    a, b, gain = seg
    x = src[int(a * SR):int(b * SR)].copy() * gain
    fade = int(SR * 0.012)
    ramp = np.linspace(0, 1, fade)
    x[:fade] *= ramp
    x[-fade:] *= ramp[::-1]
    return x


def envelope(x, bars):
    n = len(x) // bars
    e = np.array([np.sqrt((x[i * n:(i + 1) * n] ** 2).mean()) for i in range(bars)])
    e = e / (e.max() or 1)
    return np.clip(e ** 0.6, 0.06, 1)


def still(name, focus, top):
    """Scene frame, lifted a little for phone screens, plus the crop that keeps the subject in."""
    im = Image.open(STILLS / name).convert("RGB")
    im = im.point(lambda v: round(255 * (v / 255) ** 0.72))
    return im, focus, top


IMG_Y, IMG_H = 452, 566
BARS, BAR_W, BAR_GAP = 78, 8, 4
WAVE_Y, WAVE_H = 1118, 84


def base(d, img, picture, zoom, left, right):
    tracked(d, MARGIN, 196, "THE X-FILES  ·  PRODUCTION SOUND", mono(24), DIM, 3.4)
    d.text((MARGIN, 248), "MULDER’S ANSWERING MACHINE", font=osw(74, 600), fill=PAPER)
    d.text((MARGIN, 350), "The half that never aired.", font=osw(46, 300), fill=SIGNAL)

    im, (fx, fy), _ = picture
    box_w, box_h = W - 2 * MARGIN, IMG_H
    rh = im.height / zoom  # the box is narrower than 16:9, so height is the limit
    rw = rh * box_w / box_h
    l = (im.width - rw) * fx
    t = (im.height - rh) * fy
    crop = im.resize((box_w, box_h), Image.BICUBIC, box=(l, t, l + rw, t + rh))
    img.paste(crop, (MARGIN, IMG_Y))
    d.rectangle([MARGIN - 1, IMG_Y - 1, MARGIN + box_w, IMG_Y + box_h], outline=LINE)

    y = IMG_Y + IMG_H + 26
    tracked(d, MARGIN, y, left, mono(24), MUTED, 3.0)
    f = mono(24)
    tracked(d, W - MARGIN - tracked_width(d, right, f, 3.0), y, right, f, MUTED, 3.0)


def waveform(d, env, progress, cut_from=None):
    """Bars fill as the audio plays; anything past `cut_from` (0..1) fills in the signal colour."""
    mid = WAVE_Y + WAVE_H // 2
    for i, e in enumerate(env):
        x = MARGIN + i * (BAR_W + BAR_GAP)
        h = max(3, round(e * WAVE_H / 2))
        at = (i + 0.5) / len(env)
        if at > progress:
            colour = LINE
        elif cut_from is not None and at >= cut_from:
            colour = SIGNAL
        else:
            colour = PAPER
        d.rectangle([x, mid - h, x + BAR_W - 1, mid + h], fill=colour)


def layout(d, words, font, y, line_h):
    """Wrap once so words never move, then return each word's position."""
    space = d.textlength(" ", font=font)
    x, out = MARGIN, []
    for w, t in words:
        forced = w.startswith("\n")  # break at the sentence rather than orphan its first word
        w = w.lstrip("\n")
        ww = d.textlength(w, font=font)
        if forced or (x + ww > W - MARGIN and x > MARGIN):
            x, y = MARGIN, y + line_h
        out.append((w, t, x, y))
        x += ww + space
    return out, y + line_h


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    src = load_audio()
    a1, a2, a3 = cut(src, TAKE1), cut(src, SLATE), cut(src, TAKE3)
    t1, t2, t3 = len(a1) / SR, len(a2) / SR, len(a3) / SR
    e1, e2, e3 = envelope(a1, BARS), envelope(a2, BARS), envelope(a3, BARS)

    beep_len, hold = (0.42, 2.3) if BEEP else (0.0, 2.3)
    tail = np.zeros(int(hold * SR))
    if BEEP:
        x = np.arange(int(beep_len * SR)) / SR
        tone = np.sin(2 * np.pi * 1000 * x) * 0.11
        edge = int(SR * 0.008)
        tone[:edge] *= np.linspace(0, 1, edge)
        tone[-edge:] *= np.linspace(1, 0, edge)
        tail[int(0.12 * SR):int(0.12 * SR) + len(tone)] += tone
    track = np.concatenate([a1, a2, a3, tail])
    speech_peak = np.abs(np.concatenate([a1, a3])).max()
    track = np.clip(track / speech_peak * 0.89, -1, 1)

    wav = OUT / "mix.wav"
    with wave.open(str(wav), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((track * 32767).astype("<i2").tobytes())

    machine = still("machine-000226763.jpg", (0.18, 1.0), None)
    room = still("apartment-000216753.jpg", (0.55, 0.3), None)

    scratch = ImageDraw.Draw(Image.new("RGB", (W, H)))
    cap = osw(54, 400)
    aired, y_after = layout(scratch, AIRED, cap, 1296, 70)
    dropped, _ = layout(scratch, CUT, cap, y_after + 78, 70)
    y_cut_label = y_after + 30
    slate, _ = layout(scratch, SLATE_WORDS, osw(58, 300), 1300, 76)
    cut_frac_1 = (CUT[0][1] - TAKE1[0]) / t1
    cut_frac_3 = (CUT_AT_3 - TAKE3[0]) / t3

    total = t1 + t2 + t3 + hold
    frames = round(total * FPS)
    mp4 = OUT / "boggsfiles-answering-machine.mp4"
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-framerate", str(FPS), "-i", "-", "-i", str(wav), "-map_metadata", "-1",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", str(mp4)],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for n in range(frames):
        t = n / FPS
        img = Image.new("RGB", (W, H), INK)
        d = ImageDraw.Draw(img)

        if t < t1:
            src_t = TAKE1[0] + t
            base(d, img, machine, 1.0 + 0.07 * t / t1, "AGUA MALA  ·  6X14", "TAKE 1 OF 3")
            waveform(d, e1, t / t1, cut_from=cut_frac_1)
            tracked(d, MARGIN, 1250, "IN THE EPISODE", mono(24), MUTED, 3.0)
            for w, at, x, y in aired:
                if src_t >= at - 0.04:
                    d.text((x, y), w, font=cap, fill=PAPER)
            if src_t >= CUT[0][1] - 0.04:
                tracked(d, MARGIN, y_cut_label, "NOT IN THE EPISODE", mono(24), SIGNAL, 3.0)
            for w, at, x, y in dropped:
                if src_t >= at - 0.04:
                    d.text((x, y), w, font=cap, fill=SIGNAL)

        elif t < t1 + t2:
            u = t - t1
            src_t = SLATE[0] + u
            base(d, img, room, 1.0 + 0.05 * u / t2, "AGUA MALA  ·  6X14", "THE SLATE")
            waveform(d, e2, u / t2)
            tracked(d, MARGIN, 1250, "THE SOUND MIXER", mono(24), MUTED, 3.0)
            for w, at, x, y in slate:
                if src_t >= at - 0.04:
                    d.text((x, y), w, font=osw(58, 300), fill=MUTED)

        elif t < t1 + t2 + t3 + (0.12 if BEEP else 0):
            u = min(t - t1 - t2, t3)
            src_t = TAKE3[0] + u
            base(d, img, machine, 1.07 + 0.06 * u / t3, "AGUA MALA  ·  6X14", "TAKE 3 OF 3")
            waveform(d, e3, u / t3, cut_from=cut_frac_3)
            d.text((MARGIN, 1262), "THREE TAKES.", font=osw(96, 600), fill=PAPER)
            if src_t >= CUT_AT_3 - 0.1:
                d.text((MARGIN, 1386), "ONE SENTENCE", font=osw(96, 600), fill=PAPER)
                d.text((MARGIN, 1510), "MADE IT TO AIR.", font=osw(96, 600), fill=SIGNAL)

        else:
            tracked(d, MARGIN, 196, "THE X-FILES  ·  PRODUCTION SOUND", mono(24), DIM, 3.4)
            d.text((MARGIN, 700), "HEAR THE", font=osw(132, 600), fill=PAPER)
            d.text((MARGIN, 860), "WHOLE THING", font=osw(132, 600), fill=PAPER)
            d.line([(MARGIN, 1076), (W - MARGIN, 1076)], fill=LINE, width=2)
            d.text((MARGIN, 1116), "Three takes and a slate. Agua Mala, 1999.",
                   font=osw(46, 300), fill=MUTED)
            tracked(d, MARGIN, 1260, "BOGGSFILES.COM", mono(36), SIGNAL, 3.2)

        enc.stdin.write(img.tobytes())

    enc.stdin.close()
    enc.wait()
    wav.unlink()
    print(f"  {frames} frames, {total:.1f}s -> {mp4}")


if __name__ == "__main__":
    build()
