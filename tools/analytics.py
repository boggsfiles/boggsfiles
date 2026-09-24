#!/usr/bin/env python3
"""The Google Analytics tag, in one place.

Imported by transcript_header.ASSETS so every page a builder emits carries it, and by
add_analytics.py which back-fills pages already sitting in dist/. Keeping the snippet in a single
constant means the two can never disagree about which property is being measured.

Property: boggsfiles.com  ·  stream 8548608558  ·  measurement G-08L5YBPPTP
"""

MEASUREMENT_ID = "G-08L5YBPPTP"

TAG = (
    f'<script async src="https://www.googletagmanager.com/gtag/js?id={MEASUREMENT_ID}"></script>'
    "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}"
    f"gtag('js',new Date());gtag('config','{MEASUREMENT_ID}');</script>"
)
