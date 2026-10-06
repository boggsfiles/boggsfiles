import json,time,urllib.parse,urllib.request,os
from s1_sources import ROWS
cache=json.load(open('geocache.json')) if os.path.exists('geocache.json') else {}
for r in ROWS:
    q=r[9]
    if q in cache: continue
    u='https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=ca&q='+urllib.parse.quote(q)
    try:
        d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'boggsfiles-map/1.0'}),timeout=20))
        cache[q]=[round(float(d[0]['lat']),5),round(float(d[0]['lon']),5),d[0]['display_name'][:70]] if d else None
    except Exception as e: cache[q]=None; print('ERR',q,e)
    time.sleep(1.1)
json.dump(cache,open('geocache.json','w'),indent=0)
miss=[q for q,v in cache.items() if not v]; print(len(cache),'cached;',len(miss),'missing'); print('\n'.join(miss))
