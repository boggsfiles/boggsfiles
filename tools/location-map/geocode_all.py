import json,time,urllib.parse,urllib.request,os,sys
sys.path.insert(0,'.')
import s2_book,s3_book,s4_book,s5_book,s25_imdb
cache=json.load(open('geocache.json')) if os.path.exists('geocache.json') else {}
qs=[r[7] for m in (s2_book,s3_book,s4_book,s5_book,s25_imdb) for r in m.ROWS if r[7]]
todo=[q for q in dict.fromkeys(qs) if q not in cache]
print(len(todo),'to geocode',flush=True)
for q in todo:
    u='https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=ca&q='+urllib.parse.quote(q)
    try:
        d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'boggsfiles-map/1.0'}),timeout=20))
        cache[q]=[round(float(d[0]['lat']),5),round(float(d[0]['lon']),5),d[0]['display_name'][:70]] if d else None
    except Exception as e: cache[q]=None
    time.sleep(1.1)
json.dump(cache,open('geocache.json','w'),indent=0)
miss=[q for q in todo if not cache.get(q)]; print(len(miss),'missing'); print('\n'.join(miss))
