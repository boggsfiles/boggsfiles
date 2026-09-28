"""Transcribe every gag reel (word timestamps) and rank quotable spoken lines.
Output: gag_lines/<reel>.json (segments) and gag_lines/lines.json (ranked candidates)."""
import os, json, subprocess, re, sys
import mlx_whisper
SRC = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Gag Reels")
OUT = os.path.dirname(os.path.abspath(__file__))
MODEL = "mlx-community/whisper-large-v3-turbo"
reels = [f for f in sorted(os.listdir(SRC)) if f.startswith("Gag Reel") and f.endswith(".mp4")]
for f in reels:
    j = os.path.join(OUT, f[:-4] + ".json")
    if os.path.exists(j): continue
    wav = os.path.join(OUT, "tmp.wav")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", os.path.join(SRC, f), "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    print("transcribing", f, flush=True)
    r = mlx_whisper.transcribe(wav, path_or_hf_repo=MODEL, word_timestamps=True, language="en",
                               condition_on_previous_text=False, no_speech_threshold=0.5, logprob_threshold=-1.0)
    json.dump(r, open(j, "w"))
    print("done", f, len(r.get("segments", [])), "segments", flush=True)
os.path.exists(os.path.join(OUT, "tmp.wav")) and os.remove(os.path.join(OUT, "tmp.wav"))
print("ALL DONE", flush=True)
