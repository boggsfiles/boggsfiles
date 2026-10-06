import json,re,time,urllib.parse,urllib.request
c=json.load(open('geocache.json'))
bad=[]
for q,v in list(c.items()):
    if not v or (len(v)>2 and str(v[2]).startswith('manual')): continue
    m=re.match(r'(\d+)\s',q)
    if not m: continue
    u='https://nominatim.openstreetmap.org/search?format=json&limit=1&addressdetails=1&countrycodes=ca&q='+urllib.parse.quote(q)
    try: d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'boggsfiles-map/1.0'}),timeout=20))
    except Exception: d=[]
    time.sleep(1.1)
    hn=(d[0].get('address',{}).get('house_number','') if d else '')
    if m.group(1) not in hn.replace(' ','').split(';')+[hn]:
        bad.append(q); print('NO HOUSE MATCH:',q,'->',hn or '(street only)',flush=True)
json.dump(bad,open('geo_unverified.json','w'),indent=0)
print(len(bad),'without a house-number match')
