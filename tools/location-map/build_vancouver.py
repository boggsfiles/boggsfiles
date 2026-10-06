"""Build the Season 1 Vancouver locations map as a standalone preview page (preview/index.html).
Not wired into dist/ and not published; that step waits for sign-off."""
import json
from pathlib import Path
from s1_sources import ROWS
from s1_fan import ROLE, DROP, EXTRA
HERE=Path(__file__).resolve().parent
geo=json.loads((HERE/'geocache.json').read_text())
APPROX=set(json.loads((HERE/'geo_unverified.json').read_text()))
extra=json.loads((HERE/'s1_extra.json').read_text()) if (HERE/'s1_extra.json').exists() else []
ORDER=['1X79']+[f'1X{n:02d}' for n in range(1,24)]
SRC={'fan':{"label":"public records"},'book':{"label":"production records"},'imdb':{"label":"listing"},'wiki':{"label":"public records"}}
locs=[]
for ep,title,name,addr,city,played,srcs,conf,note,q in ROWS:
    if (ep,name) in DROP: continue
    if (ep,name) in ROLE: played,conf=ROLE[(ep,name)]; srcs=srcs+['fan']
    g=geo.get(q)
    if not g: print('NO GEO',q); continue
    d=dict(ep=ep,title=title,order=ORDER.index(ep),season='book' if 'book' in srcs else 'imdb',name=name,addr=addr,city=city,lat=g[0],lon=g[1],conf=conf,src=[SRC[s] for s in srcs])
    d['as']=played
    if q in APPROX: note=((note+' ') if note else '')+'Pin placed on the street; the exact building position is approximate.'
    if note: d['note']=note
    locs.append(d)
for ep,title,name,addr,city,lat,lon,played,srcs,conf,note in EXTRA:
    d=dict(ep=ep,title=title,order=ORDER.index(ep),season='book' if 'book' in srcs else ('fan' if 'fan' in srcs else 'imdb'),name=name,addr=addr,city=city,lat=lat,lon=lon,conf=conf,src=[SRC[s] for s in srcs])
    d['as']=played
    if note: d['note']=note
    locs.append(d)
for l in locs:
    if l['season']=='imdb' and any(x['label'].startswith('Fan') for x in l['src']): l['season']='fan'
footer=(HERE/'vancouver_footer.html').read_text() if (HERE/'vancouver_footer.html').exists() else ''
t=(HERE/'vancouver_template.html').read_text()
t=t.replace('__DATA__',json.dumps({'locs':locs,'footer':footer},ensure_ascii=False,separators=(',',':')).replace('</','<\\/')).replace('__BASE__',(HERE/'vancouver_base.json').read_text())
(HERE/'preview').mkdir(exist_ok=True)
out="<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"+t.replace('<div class="wrap">','</head><body><div class="wrap">',1)+"</body></html>"
(HERE/'preview'/'index.html').write_text(out)
print(len(locs),'rows;',len({l['ep'] for l in locs}),'episodes;',len(out)//1024,'KB')
