#!/bin/zsh
# Publish the site: push dist/ as the gh-pages branch and point GitHub Pages at it.
set -e
cd "$(dirname "$0")"
python3 tools/add_analytics.py   # safety net: idempotent, catches any page a builder missed
git branch -f gh-pages "$(git subtree split --prefix dist -q)"
git push -f origin gh-pages
gh api -X PUT repos/boggsfiles/boggsfiles/pages -f build_type=legacy -f "source[branch]=gh-pages" -f "source[path]=/" >/dev/null 2>&1 \
  || gh api -X POST repos/boggsfiles/boggsfiles/pages -f build_type=legacy -f "source[branch]=gh-pages" -f "source[path]=/" >/dev/null
gh api -X PUT repos/boggsfiles/boggsfiles/pages -f cname=www.boggsfiles.com >/dev/null || true
echo "Published. Pages status:"
gh api repos/boggsfiles/boggsfiles/pages | grep -oE '"(html_url|cname|status)":"?[^,"]*'
