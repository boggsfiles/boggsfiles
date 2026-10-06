import json,re,time,math,urllib.parse,urllib.request
c=json.load(open('geocache.json')); bad=json.load(open('geo_unverified.json'))
def dist(a,b): return math.hypot((a[0]-b[0])*111,(a[1]-b[1])*111*math.cos(math.radians(49.2)))
moved=[];kept=[];nohit=[]
for q in bad:
    num=re.match(r'(\d+)',q).group(1)
    u='https://photon.komoot.io/api/?limit=3&lat=49.25&lon=-123.0&q='+urllib.parse.quote(q)
    try: d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'boggsfiles-map/1.0'}),timeout=20))
    except Exception as e: nohit.append(q); continue
    time.sleep(0.6)
    hit=None
    for f in d.get('features',[]):
        p=f['properties']
        if p.get('housenumber','').split('-')[0]==num or p.get('housenumber')==num:
            hit=(f['geometry']['coordinates'][1],f['geometry']['coordinates'][0],p.get('street',''),p.get('city','')); break
    if not hit: nohit.append(q); continue
    old=c[q]; dd=dist(old,hit)
    if dd>0.25:
        c[q]=[round(hit[0],5),round(hit[1],5),'photon']; moved.append((q,round(dd,2),hit[2],hit[3]))
    else: kept.append(q)
json.dump(c,open('geocache.json','w'),indent=0)
print('MOVED',len(moved)); [print(' ',m) for m in moved]
print('CONFIRMED',len(kept)); print('NO HOUSE-NUMBER HIT',len(nohit)); [print(' ',q) for q in nohit]
