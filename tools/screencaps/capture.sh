#!/bin/zsh
# capture.sh <input.mkv> <outdir> [scene_threshold] [floor_seconds] [crop] [start] [duration]
# One full-res JPEG at every shot change, plus one every <floor_seconds> minimum.
# Filenames are the movie timecode in milliseconds: full/000603823.jpg == 0:10:03.823
set -e
IN="$1"; OUT="$2"; TH="${3:-0.28}"; FLOOR="${4:-5}"; CROP="${5:-}"; SS="${6:-0}"; DUR="${7:-}"
mkdir -p "$OUT/full" "$OUT/thumb"
INOPTS=(-ss "$SS"); [[ -n "$DUR" ]] && INOPTS+=(-t "$DUR")
CROPF=""; [[ -n "$CROP" ]] && CROPF="crop=${CROP},"
ffmpeg -nostdin -hide_banner -loglevel error -stats "${INOPTS[@]}" -i "$IN" -an -sn \
  -vf "${CROPF}select='gt(scene,${TH})+isnan(prev_selected_t)+gte(t-prev_selected_t,${FLOOR})',setpts=PTS+${SS}/TB,settb=1/1000" \
  -enc_time_base 1/1000 -fps_mode vfr -frame_pts 1 -q:v 2 "$OUT/full/%09d.jpg"
for f in "$OUT"/full/*.jpg; do sips -Z 480 "$f" --out "$OUT/thumb/$(basename "$f")" >/dev/null; done
echo "frames: $(ls "$OUT/full" | wc -l | tr -d ' ')"
