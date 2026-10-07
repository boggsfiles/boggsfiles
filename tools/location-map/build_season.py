"""Build preview/season-N.html (N=2..5) and preview/iwtb.html from the season data files.
Same page as the Season 1 preview. Not published anywhere; preview only."""
import json, sys, re
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import s2_book, s3_book, s4_book, s5_book, s25_imdb, s25_paper, s25_fan, iwtb
geo = json.loads((HERE / 'geocache.json').read_text())
APPROX = set(json.loads((HERE / 'geo_unverified.json').read_text()))
BOOK = {2: s2_book, 3: s3_book, 4: s4_book, 5: s5_book}
YEARS = {2: '1994–95', 3: '1995–96', 4: '1996–97', 5: '1997–98'}
SRC = {'book': {"label": "production records"}, 'fan': {"label": "public records"}, 'imdb': {"label": "listing"}}

def mk(ep, title, name, addr, city, lat, lon, played, tier, conf, note):
    d = dict(ep=ep, title=title, season=tier, name=name, addr=addr, city=city, lat=lat, lon=lon, conf=conf, src=[SRC[tier]])
    d['as'] = played
    if note: d['note'] = note
    return d

# every row's title must match its episode code (a 4X08 row titled Tunguska once put a Tunguska pin under Paper Hearts)
_TITLES = {}
for _m in (s2_book, s3_book, s4_book, s5_book, s25_paper, s25_fan, s25_imdb):
    for _r in _m.ROWS:
        assert _TITLES.setdefault(_r[0], _r[1]) == _r[1], f'{_m.__name__}: {_r[0]} is titled {_r[1]!r}, elsewhere {_TITLES[_r[0]]!r}'

def season_locs(n):
    pre = f'{n}X'; locs = []
    for ep, title, name, addr, city, played, note, q in BOOK[n].ROWS + s25_paper.ROWS:
        if not ep.startswith(pre): continue
        g = geo.get(q) if q else None
        if not g: continue
        conf = 'low' if q.strip() in ('Langley, BC', 'North Vancouver, BC', 'Kamloops, BC', 'Surrey, BC') else 'high'
        if q in APPROX: note = ((note + ' ') if note else '') + 'Pin placed on the street; the exact building position is approximate.'
        locs.append(mk(ep, title, name, addr, city, g[0], g[1], played, 'book', conf, note))
    for ep, title, name, addr, city, played, note, q in s25_imdb.ROWS:
        if not ep.startswith(pre) or not geo.get(q): continue
        g = geo[q]
        if q in APPROX: note = ((note + ' ') if note else '') + 'Pin placed on the street; the exact building position is approximate.'
        locs.append(mk(ep, title, name, addr, city, g[0], g[1], played, 'imdb', 'med', note))
    for ep, title, name, addr, city, lat, lon, played, conf, note in s25_fan.ROWS:
        if ep.startswith(pre): locs.append(mk(ep, title, name, addr, city, lat, lon, played, 'fan', conf, note))
    # de-duplicate same episode + same place (keep the better-sourced row, merge descriptions)
    out, seen = [], {}
    rank = {'book': 0, 'fan': 1, 'imdb': 2}
    for l in sorted(locs, key=lambda l: rank[l['season']]):
        k = (l['ep'], round(l['lat'], 3), round(l['lon'], 3))
        if k in seen:
            o = seen[k]
            if o['as'].startswith('Scene not') and not l['as'].startswith('Scene not'): o['as'] = l['as']
            continue
        seen[k] = l; out.append(l)
    for l in out: l['order'] = int(l['ep'][2:])
    return out

def page(locs, title, h1, lede, eyebrow, foot):
    t = (HERE / 'vancouver_template.html').read_text()
    t = t.replace('<title>X-Files Vancouver Locations: Season 1</title>', f'<title>{title}</title>')
    t = t.replace('<h1>Vancouver Locations</h1>', f'<h1>{h1}</h1>')
    t = re.sub(r'<p class="lede">.*?</p>', f'<p class="lede">{lede}</p>', t, count=1, flags=re.S)
    t = t.replace('of 24 episodes', 'episodes').replace('Season 1 · 1993–94', eyebrow)
    t = t.replace("a.innerHTML=`<b>${esc(ep.replace('1X',''))}</b>${esc(v.t)}`", "a.innerHTML=`<b>${esc(ep.replace(/^\\dX/,''))}</b>${esc(v.t)}`")
    t = t.replace('__DATA__', json.dumps({'locs': locs, 'footer': foot}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
    t = t.replace('__BASE__', (HERE / 'vancouver_base.json').read_text())
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + t.replace('<div class="wrap">', '</head><body><div class="wrap">', 1) + '</body></html>'

FOOT = ('<h2 style="font:400 1.4rem/1 var(--display);text-transform:uppercase;letter-spacing:.04em;color:var(--paper);margin:0 0 10px">How to read the pins</h2>'
        '<p>Red pins are confirmed from production records: the location managers\' records and the Boggsfiles call sheets. Green pins were identified from the episode itself and public filming records. '
        'Amber pins come from a single listing that gives an address without saying what was shot there. Interiors were mostly built on the stages at North Shore Studios (later Lions Gate Studios), 555 Brooksbank Ave, North Vancouver. Map lines © OpenStreetMap contributors.</p>')
FOOT5 = FOOT + '<p><b style="color:var(--paper)">Outside British Columbia.</b> Emily (5X07) shot its outdoor desert scenes in Tucson, Arizona, with the Old Pima County Courthouse, 115 N. Church Ave, standing in for the San Diego Hall of Justice.</p>'
(HERE / 'preview').mkdir(exist_ok=True)
for n in (2, 3, 4, 5):
    L = season_locs(n)
    lede = f'Season {n} of The X-Files, {YEARS[n]}, pinned to where it was shot in and around Vancouver, British Columbia. Addresses come from production records and public filming listings, checked against the episodes. Click a pin or a location to jump between the map and the list.'
    (HERE / 'preview' / f'season-{n}.html').write_text(page(L, f'X-Files Vancouver Locations: Season {n}', 'Vancouver Locations', lede, f'Season {n} · {YEARS[n]}', FOOT5 if n == 5 else FOOT))
    print(f'season {n}:', len(L), 'locations,', len({l["ep"] for l in L}), 'episodes')
L = [mk('IWTB', 'I Want to Believe', *r[:5], r[5], 'fan', r[6], r[7]) for r in iwtb.ROWS]
for l in L: l['order'] = 0
lede = 'The X-Files: I Want to Believe (2008), shot December 2007 to March 2008 in and around Vancouver and the Pemberton Valley. Several sites are known from filming listings without the scene they were used for.'
(HERE / 'preview' / 'iwtb.html').write_text(page(L, 'X-Files Vancouver Locations: I Want to Believe', 'I Want to Believe', lede, 'Feature film · 2008', FOOT))
print('iwtb:', len(L))
