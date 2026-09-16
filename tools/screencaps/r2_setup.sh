#!/bin/zsh
echo ""
echo "R2 setup — paste each value from the Cloudflare page, then press Return."
echo ""
printf "1) Access Key ID: "; read -r AK
printf "2) Secret Access Key: "; read -r SK
F=~/.config/rclone/rclone.conf
sed -i '' "s|^access_key_id = .*|access_key_id = $AK|; s|^secret_access_key = .*|secret_access_key = $SK|" "$F"
chmod 600 "$F"
echo ""; echo "Saved. Testing the connection..."
if rclone lsd r2:boggsfiles-media >/dev/null 2>&1 || rclone lsf r2:boggsfiles-media --max-depth 1 >/dev/null 2>&1; then echo "✅ Connected to boggsfiles-media. You can close this tab."; else echo "❌ Could not connect — tell Claude and we'll check the values."; fi
