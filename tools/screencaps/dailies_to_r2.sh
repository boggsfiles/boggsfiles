#!/bin/zsh
# Upload the iCloud "Dailies" folder to R2 one file at a time, downloading and re-evicting
# each file so the local disk stays free. Safe to re-run: files already on R2 are skipped.
set -u
SRC="$HOME/Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/Dailies"
DEST="r2:boggsfiles-media/dailies"
LOG="$HOME/Movies/XF_screencaps/dailies_upload.log"
cd "$SRC" || exit 1
find . -type f ! -name ".*" | sort | while IFS= read -r f; do
  rel="${f#./}"; logical=$(stat -f %z "$f"); ondisk=$(( $(du -k "$f" | cut -f1) * 1024 ))
  was_evicted=0
  if (( ondisk < logical - 1048576 )); then
    was_evicted=1; brctl download "$f" >/dev/null 2>&1
    # wait for the download to finish (up to 30 min per file)
    for i in $(seq 1 360); do ondisk=$(( $(du -k "$f" | cut -f1) * 1024 )); (( ondisk >= logical - 1048576 )) && break; sleep 5; done
    if (( ondisk < logical - 1048576 )); then echo "TIMEOUT downloading: $rel" >> "$LOG"; continue; fi
  fi
  if rclone copyto "$f" "$DEST/$rel" --s3-no-check-bucket --s3-upload-concurrency 8 --s3-chunk-size 64M -q; then
    echo "uploaded ($(( logical / 1048576 )) MB): $rel" >> "$LOG"
  else
    echo "FAILED: $rel" >> "$LOG"
  fi
  (( was_evicted )) && brctl evict "$f" >/dev/null 2>&1
done
echo "dailies upload finished $(date)" >> "$LOG"
