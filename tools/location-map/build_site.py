"""Put the Vancouver location maps into dist/ as real site pages (site header, nav, analytics).
Writes dist/locations/index.html and dist/locations/vancouver/season-1/index.html.
Does NOT publish: run ./publish.sh separately when the site is ready to go live."""
import re, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
DIST = HERE.parent.parent / 'dist'
NAV = ('<nav class="bf-navlinks" id="bf-primary-navigation" aria-label="Primary"><a href="/archive/">Archive</a><a href="/scripts/">Scripts</a>'
       '<a href="/transcripts/">Transcripts</a><a href="/screencaps/">Screencaps</a><a href="/script-vs-screen/">Script vs. Screen</a>'
       '<a href="/dailies/">Dailies</a><a href="/gag-reels/">Gag Reels</a><a href="/locations/" aria-current="page">Locations</a>'
       '<a href="/memorabilia/">Memorabilia</a><a href="/resources/">Resources</a></nav>')
HEADER = ('<header class="bf-header"><div class="bf-inner"><a class="bf-brand" href="/" aria-label="Boggsfiles home">BOGGS<span class="bf-brand-x">X</span>FILES</a>'
          + NAV + '<button class="bf-menu" type="button" aria-label="Open navigation" aria-controls="bf-primary-navigation" aria-expanded="false">☰</button></div></header>')
HEADLINKS = ('<link rel="stylesheet" href="/assets/site-header.css?v=3"><script src="/assets/site-header.js" defer></script>'
             '<script async src="https://www.googletagmanager.com/gtag/js?id=G-RZJWTDMN98"></script>'
             "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','G-RZJWTDMN98');</script>")
# sticky offsets under the site header (92px desktop, 72px phone); the episode bar and map stack below it
STICKY = ('<style>.jump{top:var(--hdr,92px)!important}.mapbox{top:calc(var(--hdr,92px) + var(--jh,0px) + 12px)!important;'
          'height:calc(100vh - var(--hdr,92px) - var(--jh,0px) - 28px)!important}.season{scroll-margin-top:calc(var(--hdr,92px) + var(--jh,0px) + 12px)!important}'
          '@media (max-width:900px){.mapbox{top:0!important;height:62vh!important}}</style>'
          "<script>(function(){function m(){var h=document.querySelector('.bf-header'),j=document.getElementById('jump'),r=document.documentElement;"
          "if(h)r.style.setProperty('--hdr',h.offsetHeight+'px');if(j)r.style.setProperty('--jh',j.offsetHeight+'px');}"
          "addEventListener('load',m);addEventListener('resize',m);setTimeout(m,300);})();</script>")

def site_page(src, desc, crumb):
    t = src.read_text()
    t = t.replace('<div class="brand">BOGGS<b>X</b>FILES · LOCATION DEPARTMENT · PREVIEW, NOT PUBLISHED</div>', f'<div class="brand">{crumb}</div>')
    t = re.sub(r'<title>(.*?)</title>', lambda m: f'<title>{m.group(1)}: Boggsfiles</title><meta name="description" content="{desc}">', t, count=1)
    t = t.replace('</head>', HEADLINKS + STICKY + '</head>', 1)
    t = t.replace('<body><div class="wrap">', '<body>' + HEADER + '<div class="wrap">', 1)
    t = t.replace('.wrap{padding-inline', 'body{margin:0}.wrap{padding-inline', 1)
    return t

out = DIST / 'locations' / 'vancouver' / 'season-1'; out.mkdir(parents=True, exist_ok=True)
(out / 'index.html').write_text(site_page(HERE / 'preview' / 'index.html',
    'Every Season 1 filming location of The X-Files in Vancouver, pinned on a map with street addresses.',
    '<a href="/locations/" style="color:inherit;text-decoration:none">Locations</a> · Vancouver · Season 1'))

# landing page
d = json.loads(re.search(r'const DATA = (.*?);\nconst BASE', (HERE / 'preview' / 'index.html').read_text(), re.S).group(1))
n_places = len({(l['name'], l['addr']) for l in d['locs']})
LAND = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Locations: Boggsfiles</title><meta name="description" content="Where The X-Files was filmed: every location pinned on a map, season by season.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Libre+Caslon+Display&family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet"><link rel="stylesheet" href="/assets/collection.css">{HEADLINKS}
<style>.soon{{opacity:.55;pointer-events:none}}.soon .open{{color:#9aa39d}}</style></head><body>{HEADER}<main>
<section class="hero"><div class="shell"><div class="crumb"><a href="/archive/">Archive</a> &nbsp;/&nbsp; Locations</div><h1>Locations</h1>
<p>Where The X-Files was actually filmed. Every cemetery, forest road, office tower and front door, pinned on a map with its street address and what it played on screen.</p>
<div class="summary"><div class="stat"><b>{n_places}</b><span>Season 1 places</span></div><div class="stat"><b>24</b><span>Episodes mapped</span></div><div class="stat"><b>B.C.</b><span>Vancouver, 1993–98</span></div></div></div></section>
<div class="shell"><div class="collection">
<a class="file wide" data-mark="1" href="/locations/vancouver/season-1/"><span class="meta">Vancouver · 1993–94</span><h2>Season One</h2><p>The Pilot to The Erlenmeyer Flask: {n_places} places across 24 episodes.</p><span class="open">Open the map →</span></a>
<a class="file soon" data-mark="2" href="#"><span class="meta">Vancouver · 1994–95</span><h2>Season Two</h2><p>Coming soon.</p><span class="open">Coming soon</span></a>
<a class="file soon" data-mark="3" href="#"><span class="meta">Vancouver · 1995–96</span><h2>Season Three</h2><p>Coming soon.</p><span class="open">Coming soon</span></a>
<a class="file soon" data-mark="4" href="#"><span class="meta">Vancouver · 1996–97</span><h2>Season Four</h2><p>Coming soon.</p><span class="open">Coming soon</span></a>
<a class="file soon" data-mark="5" href="#"><span class="meta">Vancouver · 1997–98</span><h2>Season Five</h2><p>Coming soon.</p><span class="open">Coming soon</span></a>
<a class="file" data-mark="L" href="/misc-memorabilia/x-files-location-scouts/"><span class="meta">Location department</span><h2>Location Scouts</h2><p>Fourteen scouting folders from the Los Angeles years, every place identified.</p><span class="open">Open the folders →</span></a>
</div></div></main><footer><div class="shell footer-row">BOGGSFILES · LOCATIONS <span><a href="/">Home</a> · The truth still matters</span></div></footer></body></html>'''
(DIST / 'locations' / 'index.html').write_text(LAND)
print('wrote', out / 'index.html', 'and', DIST / 'locations' / 'index.html', n_places, 'places')
