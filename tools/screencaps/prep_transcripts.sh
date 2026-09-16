#!/bin/zsh
# prep_transcripts.sh <season>  — OCR Blu-ray SDH subtitles and scanned scripts for a season.
# Outputs to ~/Movies/XF_transcript_prep/S<season>/<code>/{subs.srt, script.txt}
set -u; setopt nullglob
S="$1"; OUT="$HOME/Movies/XF_transcript_prep/S$S"; mkdir -p "$OUT"
TOOLS="$HOME/Sites/boggsfiles/tools/screencaps"; PY="$TOOLS/facenv/bin/python"
SCRIPTS="$HOME/Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/XF Season $S"
LOG="$OUT/prep.log"
grep "^$S|" "$TOOLS/manifest.txt" | while IFS='|' read -r season code title mkv; do
  d="$OUT/$code"; mkdir -p "$d"
  if [ ! -s "$d/subs.srt" ]; then
    # pick the English PGS track with the most packets (the SDH one)
    best=""; bestn=0
    for idx in $(ffprobe -v error -select_streams s -show_entries stream=index:stream_tags=language -of csv=p=0 "$mkv" | awk -F, '$2=="eng"{print $1}'); do
      n=$(ffprobe -v error -select_streams "$idx" -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "$mkv" 2>/dev/null | head -1)
      (( ${n:-0} > bestn )) && { bestn=$n; best=$idx; }
    done
    if [ -n "$best" ]; then
      ffmpeg -nostdin -v error -y -i "$mkv" -map 0:$best -c copy "$d/subs.sup" && "$PY" "$TOOLS/pgs2srt.py" "$d/subs.sup" "$d/subs.srt" 4 >>"$LOG" 2>&1 && rm -f "$d/subs.sup"
      echo "$code subs: $(grep -c '^[0-9]*$' "$d/subs.srt") cues (track $best, $bestn packets)" >> "$LOG"
    else echo "$code subs: NO ENGLISH TRACK" >> "$LOG"; fi
  fi
  if [ ! -s "$d/script.txt" ]; then
    pdf="$SCRIPTS/$(awk -F'|' -v c="$code" '$1==c{print $2}' "$TOOLS/script_pdfs.txt")"
    if [ -n "$pdf" ]; then
      if [ "$(pdftotext -layout "$pdf" - 2>/dev/null | wc -w)" -gt 3000 ]; then pdftotext -layout "$pdf" "$d/script.txt"; echo "$code script: text layer ($pdf)" >> "$LOG"
      else
        mkdir -p "$d/pages"; pdftoppm -r 200 -gray "$pdf" "$d/pages/p" >/dev/null 2>&1
        : > "$d/script.txt"; for p in "$d"/pages/p-*.pgm; do tesseract "$p" - -l eng --psm 6 2>/dev/null >> "$d/script.txt"; printf '\f' >> "$d/script.txt"; done
        rm -rf "$d/pages"; echo "$code script: OCR $(wc -w < "$d/script.txt") words ($pdf)" >> "$LOG"
      fi
    else echo "$code script: NO PDF FOUND for '$title'" >> "$LOG"; fi
  fi
done
echo "season $S prep finished $(date)" >> "$LOG"
