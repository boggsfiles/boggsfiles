#!/bin/bash
# Publish the Season 2 gag reel. Runs from launchd, so it must not depend on the Claude app
# being open. Idempotent: if season-2 is already live it exits without doing anything.
set -euo pipefail
cd /Users/lindseyboggs/Sites/boggsfiles
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
LOG=/Users/lindseyboggs/Desktop/"gag-s2-publish.log"
exec >>"$LOG" 2>&1
echo "===== $(date '+%F %T %Z') ====="

if grep -q '^LIVE = \["season-1", "season-2"\]' tools/build_gag_reels.py; then
  echo "already flipped live; nothing to do"; exit 0
fi

sed -i '' 's/^LIVE = \["season-1"\]$/LIVE = ["season-1", "season-2"]/' tools/build_gag_reels.py
python3 tools/build_gag_reels.py

# refuse to publish a page that would render stretched or without a video source
grep -q 'object-fit:fill' dist/gag-reels/season-2/index.html || { echo "FAIL: missing object-fit:fill"; exit 1; }
grep -q 'Gag Reel - Season 2.mp4' dist/gag-reels/season-2/index.html || { echo "FAIL: no video key"; exit 1; }

git add dist tools/build_gag_reels.py
git commit -m "Gag Reels: Season 2 goes live"
./publish.sh
git push origin main

for i in $(seq 1 15); do
  sleep 12
  if curl -s "https://www.boggsfiles.com/gag-reels/season-2/?cb=$RANDOM" | grep -q 'object-fit:fill'; then
    echo "LIVE after about $((i*12))s"; exit 0
  fi
done
echo "pushed, but not seen live yet after 3 minutes - check GitHub Pages"
