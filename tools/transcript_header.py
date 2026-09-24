"""Shared transcript header matching the main Boggsfiles homepage."""

from analytics import TAG as _GA

ASSETS = ('<link rel="stylesheet" href="/assets/site-header.css?v=3">'
          '<script src="/assets/site-header.js" defer></script>' + _GA)

_TRANSCRIPT_HEADER = '''<header class="bf-header"><div class="bf-inner"><a class="bf-brand" href="/" aria-label="Boggsfiles home">BOGGS<span class="bf-brand-x">X</span>FILES</a><nav class="bf-navlinks" id="bf-primary-navigation" aria-label="Primary"><a href="/archive/">Archive</a><a href="/scripts/">Scripts</a><a href="/transcripts/" aria-current="page">Transcripts</a><a href="/screencaps/">Screencaps</a><a href="/script-vs-screen/">Script vs. Screen</a><a href="/dailies/">Dailies</a><a href="/gag-reels/">Gag Reels</a><a href="/memorabilia/">Memorabilia</a><a href="/resources/">Resources</a></nav><button class="bf-menu" type="button" aria-label="Open navigation" aria-controls="bf-primary-navigation" aria-expanded="false">☰</button></div></header>'''


def site_header(active: str = "", *, home: bool = False) -> str:
    markup = _TRANSCRIPT_HEADER.replace(' aria-current="page"', '')
    if active:
        markup = markup.replace('>' + active + '</a>', ' aria-current="page">' + active + '</a>')
    if home:
        markup = markup.replace('class="bf-header"', 'class="bf-header bf-header-home"')
    return markup

HEADER = site_header("Transcripts")
