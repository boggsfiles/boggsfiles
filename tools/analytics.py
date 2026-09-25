#!/usr/bin/env python3
"""The Google Analytics tag, in one place.

Imported by transcript_header.ASSETS so every page a builder emits carries it, and by
add_analytics.py which back-fills pages already sitting in dist/. Keeping the snippet in a single
constant means the two can never disagree about which property is being measured.

Property: Boggsfiles  ·  measurement G-RZJWTDMN98
The earlier G-08L5YBPPTP was a dead property: Google served 404 for its gtag config,
where it returns a 200 stub even for IDs it has never seen.
"""

MEASUREMENT_ID = "G-RZJWTDMN98"

TAG = (
    f'<script async src="https://www.googletagmanager.com/gtag/js?id={MEASUREMENT_ID}"></script>'
    "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}"
    f"gtag('js',new Date());gtag('config','{MEASUREMENT_ID}');</script>"
)
