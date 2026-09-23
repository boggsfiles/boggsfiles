#!/usr/bin/env python3
"""Where the video Worker lives. One place, because both builders bake it into every page.

Why this is its own file: `*.workers.dev` is blocked wholesale in some countries (Russia among
them) because those subdomains are widely used to build circumvention proxies. The page, the
fonts and the poster all load fine there; only the video fails, silently. Serving the very same
Worker from a subdomain of boggsfiles.com avoids that, since the block is on the workers.dev
domain rather than on Cloudflare itself.

To switch: point media.boggsfiles.com at the Worker (Cloudflare dashboard > Workers > the worker >
Settings > Domains & Routes > Add custom domain), set USE_CUSTOM_DOMAIN = True below, then
    python3 tools/build_gag_reels.py && python3 tools/build_dailies.py
    git commit && ./publish.sh
Switching back is the same edit in reverse, so a failed DNS move costs one line.
"""

CUSTOM_DOMAIN = "https://media.boggsfiles.com"
WORKERS_DEV  = "https://boggsfiles-dailies.boggsfiles.workers.dev"

# Flip to True once media.boggsfiles.com resolves and serves the Worker.
USE_CUSTOM_DOMAIN = False

WORKER = CUSTOM_DOMAIN if USE_CUSTOM_DOMAIN else WORKERS_DEV
