"""Put the Vancouver location maps into dist/ as real site pages (site header, nav, analytics).
Writes dist/locations/index.html and dist/locations/vancouver/season-1..4/index.html.
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

WORDS = {2: 'Two', 3: 'Three', 4: 'Four'}
for s in (2, 3, 4):
    o = DIST / 'locations' / 'vancouver' / f'season-{s}'; o.mkdir(parents=True, exist_ok=True)
    (o / 'index.html').write_text(site_page(HERE / 'preview' / f'season-{s}.html',
        f'Every Season {s} filming location of The X-Files in Vancouver, pinned on a map with street addresses.',
        f'<a href="/locations/" style="color:inherit;text-decoration:none">Locations</a> · Vancouver · Season {s}'))

# landing page: per-season counts read from the same data the maps use
def season_stats(path):
    locs = json.loads(re.search(r'const DATA = (.*?);\nconst BASE', path.read_text(), re.S).group(1))['locs']
    locs.sort(key=lambda l: l['order'])
    return len({(l['name'], l['addr']) for l in locs}), len({l['ep'] for l in locs}), locs[0]['title'], locs[-1]['title']
ST = {1: season_stats(HERE / 'preview' / 'index.html')}
for s in (2, 3, 4): ST[s] = season_stats(HERE / 'preview' / f'season-{s}.html')
n_places = ST[1][0]
TOT_P = sum(v[0] for v in ST.values()); TOT_E = sum(v[1] for v in ST.values())
def live_card(s, yrs):
    p, e, a, b = ST[s]
    return (f'<a class="file wide" data-mark="{s}" href="/locations/vancouver/season-{s}/"><span class="meta">Vancouver · {yrs}</span><h2>Season {WORDS[s]}</h2>'
            f'<p>{a} to {b}: {p} places across {e} episodes.</p><span class="open">Open the map →</span></a>')
LAND = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Locations: Boggsfiles</title><meta name="description" content="Where The X-Files was filmed: every location pinned on a map, season by season.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Libre+Caslon+Display&family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet"><link rel="stylesheet" href="/assets/collection.css">{HEADLINKS}
<style>.soon{{opacity:.55;pointer-events:none}}.soon .open{{color:#9aa39d}}</style></head><body>{HEADER}<main>
<section class="hero"><div class="shell"><div class="crumb"><a href="/archive/">Archive</a> &nbsp;/&nbsp; Locations</div><h1>Locations</h1>
<p>Where The X-Files was actually filmed, in Vancouver and Los Angeles. Every cemetery, forest road, office tower and front door, pinned on a map with its street address and what it played on screen.</p>
<div class="summary"><div class="stat"><b>{TOT_P}</b><span>Places mapped</span></div><div class="stat"><b>{TOT_E}</b><span>Episodes mapped</span></div><div class="stat"><b>11</b><span>Seasons and two films</span></div></div></div></section>
<div class="shell"><div class="collection">
<a class="file wide" data-mark="1" href="/locations/vancouver/season-1/"><span class="meta">Vancouver · 1993–94</span><h2>Season One</h2><p>The Pilot to The Erlenmeyer Flask: {n_places} places across 24 episodes.</p><span class="open">Open the map →</span></a>
{live_card(2, '1994–95')}
{live_card(3, '1995–96')}
{live_card(4, '1996–97')}
<a class="file soon" data-mark="5" href="#" aria-disabled="true"><span class="meta">Vancouver · 1997–98</span><h2>Season Five</h2><p>Coming soon.</p><span class="open">Coming soon</span></a>
<a class="file soon" data-mark="F" href="#" aria-disabled="true"><span class="meta">Los Angeles · 1997</span><h2>Fight the Future</h2><p>Coming soon.</p><span class="open">Coming soon</span></a>
<a class="file soon" data-mark="6" href="#" aria-disabled="true"><span class="meta">Los Angeles · 1998–99</span><h2>Season Six</h2><p>Coming soon.</p><span class="open">Coming soon</span></a>
<a class="file soon" data-mark="7" href="#" aria-disabled="true"><span class="meta">Los Angeles · 1999–2000</span><h2>Season Seven</h2><p>Coming soon.</p><span class="open">Coming soon</span></a>
<a class="file soon" data-mark="8" href="#" aria-disabled="true"><span class="meta">Los Angeles · 2000–01</span><h2>Season Eight</h2><p>Coming soon.</p><span class="open">Coming soon</span></a>
<a class="file soon" data-mark="9" href="#" aria-disabled="true"><span class="meta">Los Angeles · 2001–02</span><h2>Season Nine</h2><p>Coming soon.</p><span class="open">Coming soon</span></a>
<a class="file soon" data-mark="I" href="#" aria-disabled="true"><span class="meta">Vancouver · 2008</span><h2>I Want to Believe</h2><p>Coming soon.</p><span class="open">Coming soon</span></a>
<a class="file soon" data-mark="10" href="#" aria-disabled="true"><span class="meta">Vancouver · 2016</span><h2>Season Ten</h2><p>Coming soon.</p><span class="open">Coming soon</span></a>
<a class="file soon" data-mark="11" href="#" aria-disabled="true"><span class="meta">Vancouver · 2018</span><h2>Season Eleven</h2><p>Coming soon.</p><span class="open">Coming soon</span></a>
<a class="file" data-mark="L" href="/misc-memorabilia/x-files-location-scouts/"><span class="meta">Location department</span><h2>Location Scouts</h2><p>Fourteen scouting folders from the Los Angeles years, every place identified.</p><span class="open">Open the folders →</span></a>
</div></div></main><footer><div class="shell footer-row">BOGGSFILES · LOCATIONS <span><a href="/">Home</a> · The truth still matters</span></div></footer></body></html>'''
(DIST / 'locations' / 'index.html').write_text(LAND)
print('wrote seasons 1-4 and', DIST / 'locations' / 'index.html', TOT_P, 'places,', TOT_E, 'episodes')
