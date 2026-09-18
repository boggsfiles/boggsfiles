#!/usr/bin/env python3
"""Build the Screencaps section.

Images live on Cloudflare R2 (MEDIA_BASE), not in the repo. Each title's frames are
uploaded to  screencaps/<season-slug>/<episode-slug>/{full,thumb}/  by sync_media();
this script writes the pages:
  /screencaps/                         landing (films + seasons)
  /screencaps/season-N/                episode cards for one season
  /screencaps/season-N/<slug>/         gallery (filters, timecode range)
  /screencaps/fight-the-future/        film gallery

Titles come from tools/screencaps/manifest.txt plus the two films; an episode appears
as soon as its capture folder has an index.json.
"""
from __future__ import annotations
import html, json, os, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from transcript_header import site_header, ASSETS
from build_transcript_indexes import HEAD, BASE, SEASONS
from browse_navigation import navigation, ASSET as NAV_ASSET

ROOT = Path(__file__).resolve().parent.parent
HEADER = site_header("Screencaps")
MEDIA_BASE = "https://pub-df226d4134944457905024edfc4635fb.r2.dev"
CAPS_ROOT = Path.home() / "Movies/XF_screencaps"
BUCKET = "r2:boggsfiles-media"

SEASON_YEARS = {1: "1993–1994", 2: "1994–1995", 3: "1995–1996", 4: "1996–1997", 5: "1997–1998", 6: "1998–1999",
                7: "1999–2000", 8: "2000–2001", 9: "2001–2002", 10: "2016", 11: "2018"}
SEASON_TOTAL = {1: 24, 2: 25, 3: 24, 4: 24, 5: 20, 6: 22, 7: 22, 8: 21, 9: 20, 10: 6, 11: 10}
SEASON_IMAGE = {1: "pilot.webp", 2: "little-green-men.webp", 3: "the-blessing-way.jpg", 4: "herrenvolk.jpg", 5: "redux.jpg",
                6: "the-beginning.jpg", 7: "the-sixth-extinction.jpg", 8: "within.jpg", 9: "nothing-important-happened-today.jpg",
                10: "my-struggle.jpg", 11: "plus-one.jpg"}
CHARACTER_FILTERS = ["Mulder", "Scully", "Mulder + Scully", "Skinner", "CSM", "Well-Manicured Man", "The Lone Gunmen"]
GROUPS = {"Mulder + Scully": ["Mulder", "Scully"], "The Lone Gunmen": ["Byers", "Frohike", "Langly"], "The Hallway Scene": ["Hallway Scene"]}

FILMS = [
    {"slug": "fight-the-future", "title": "Fight the Future", "kind": "Feature film", "year": "1998", "aspect": "1920/816",
     "source": CAPS_ROOT / "Fight the Future (extended)", "still": "/assets/transcript-stills/fight-the-future.jpg",
     "blurb": "Every shot change from the extended cut, with dense coverage wherever Mulder or Scully is on screen.",
     "filters": ["Mulder", "Scully", "Mulder + Scully", "The Hallway Scene", "Skinner", "CSM", "Well-Manicured Man", "Kurtzweil",
                 "The Lone Gunmen", "Cassidy", "Michaud", "Bronschweig", "Strughold", "Syndicate", "Barmaid", "Stevie"], "media": "Blu-ray"},
    {"slug": "i-want-to-believe", "title": "I Want to Believe", "kind": "Feature film", "year": "2008", "aspect": "16/9",
     "source": None, "still": "/assets/transcript-stills/i-want-to-believe.jpg", "blurb": "From the DVD · in preparation", "filters": [], "media": "DVD"},
]


def esc(v) -> str:
    return html.escape(str(v), quote=True)


def slugify(title: str) -> str:
    s = title.lower().replace("&", "and"); s = re.sub(r"[’'.]", "", s); s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def slug_table() -> dict[str, tuple[str, str]]:
    """code -> (slug, title) from the transcript tables, so URLs match across sections."""
    out = {}
    for season, eps in SEASONS.items():
        for slug, title, code, _ in eps:
            m = re.match(r"(\d+)(?:ABX|X)(\d+)", code)
            if m: out[f"{int(m[1])}X{int(m[2]):02d}"] = (slug, title)
    return out


def episodes() -> list[dict]:
    table = slug_table(); rows = []
    for line in (ROOT / "tools/screencaps/manifest.txt").read_text().splitlines():
        if not line.strip(): continue
        season, code, title, path = line.split("|")
        m = re.match(r"(\d+)X(\d+)", code); key = f"{int(m[1])}X{int(m[2]):02d}"
        slug = table.get(key, (slugify(title), title))[0]
        src = CAPS_ROOT / "series" / f"S{int(season):02d}" / f"{code} {title}"
        live = (src / "index.json").exists()
        dar = "16/9" if int(season) >= 5 else "4/3"
        rows.append({"season": int(season), "code": code, "title": title, "slug": slug, "source": src, "live": live, "aspect": dar,
                     "media": "Blu-ray" if int(season) >= 10 else "DVD", "num": 0 if code == "1X79" else int(m[2])})   # Pilot (1X79) airs first
    return rows


def tc(ms: int) -> str:
    s = ms // 1000
    return f"{s // 3600}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def gallery_page(t: dict, crumb: str, filters: list[str], up_url: str, nav_prev, nav_next) -> str:
    index = json.load(open(t["source"] / "index.json"))
    frames = sorted(index)
    present = {x for v in index.values() for x in v}
    def ok(f):
        need = GROUPS.get(f, [f]); return all(n in present for n in need)
    buttons = "".join(f'<button type="button" data-f="{esc(f)}">{esc(f)}</button>' for f in ["All"] + [f for f in filters if ok(f)])
    data = [[f[:-4], index[f]] for f in frames]
    media = f"{MEDIA_BASE}/screencaps/{t['path']}/"
    last = tc(int(frames[-1][:-4])) if frames else "0:00:00"
    return f'''<!doctype html><html lang="en"><head><title>{esc(t["title"])} Screencaps - Boggsfiles</title><meta name="description" content="{esc(t["title"])} screencaps, tagged by character and searchable by time.">{HEAD}<style>{BASE}
    .caps{{padding:40px 0 80px}}.cap-toolbar{{position:sticky;top:0;z-index:4;background:#08100d;border-bottom:1px solid #343c38;padding:14px 0}}.cap-toolbar .shell{{display:flex;gap:10px;align-items:center;flex-wrap:wrap}}.cap-toolbar b{{font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;color:#8c968f;margin-right:6px;white-space:nowrap}}.cap-toolbar button{{background:#0e1412;border:1px solid #343c38;color:#eeeee8;padding:7px 12px;font:400 .62rem/1 "DM Mono",monospace;letter-spacing:.08em;text-transform:uppercase;cursor:pointer;transition:.15s}}.cap-toolbar button:hover{{background:#151b18}}.cap-toolbar button.on{{background:#b4312d;border-color:#b4312d}}.cap-toolbar input{{background:#0e1412;border:1px solid #343c38;color:#eeeee8;padding:7px 10px;font:400 .68rem "DM Mono",monospace;width:96px}}.cap-count{{margin-left:auto;font-size:.62rem;letter-spacing:.1em;color:#8c968f;text-transform:uppercase}}
    .cap-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;background:#343c38;border:1px solid #343c38;margin-top:28px}}.cap{{position:relative;display:block;background:#0e1412;min-width:0}}.cap img{{width:100%;display:block;aspect-ratio:{t["aspect"]};object-fit:cover;filter:saturate(.9) brightness(.86);transition:.2s}}.cap:hover img{{filter:none}}.cap span{{position:absolute;left:8px;bottom:8px;background:rgba(8,16,13,.82);padding:3px 7px;font-size:.58rem;letter-spacing:.08em;font-variant-numeric:tabular-nums}}.cap em{{position:absolute;right:8px;bottom:8px;background:rgba(180,49,45,.9);padding:3px 7px;font-size:.52rem;letter-spacing:.08em;text-transform:uppercase;font-style:normal;max-width:60%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
    .cap-empty{{padding:80px 0;text-align:center;color:#8c968f}}.cap-more{{display:block;margin:28px auto 0;background:#0e1412;border:1px solid #343c38;color:#eeeee8;padding:14px 28px;font:400 .62rem "DM Mono",monospace;letter-spacing:.14em;text-transform:uppercase;cursor:pointer}}.cap-more[hidden]{{display:none}}
    @media(max-width:1160px){{.cap-grid{{grid-template-columns:repeat(3,1fr)}}}}@media(max-width:700px){{.cap-grid{{grid-template-columns:repeat(2,1fr)}}.cap-count{{margin-left:0;width:100%}}}}
    </style>{ASSETS}{NAV_ASSET}</head><body>{HEADER}<main>
    <section class="hero"><div class="shell"><div class="crumb">{crumb}</div><div class="eyebrow">{esc(t["kind"])} · {esc(t["year"])}</div><h1>{esc(t["title"])}</h1><p>{esc(t["blurb"])} Filter by who is on screen, or jump to a stretch by timecode. Click any frame for the full-size capture.</p><div class="summary"><div class="stat"><b>{len(frames):,}</b><span>Frames</span></div><div class="stat"><b>{len(present)}</b><span>Tags</span></div><div class="stat"><b>{esc(t["media"])}</b><span>Source</span></div></div></div></section>
    <div class="cap-toolbar"><div class="shell"><b>Show</b>{buttons}<label style="margin-left:8px"><b>From</b><input id="cap-a" placeholder="0:00:00"></label><label><b>To</b><input id="cap-b" placeholder="{last}"></label><span class="cap-count" id="cap-count"></span></div></div>
    <section class="caps"><div class="shell"><div class="cap-grid" id="cap-grid"></div><div class="cap-empty" id="cap-empty" hidden>No frames match that filter.</div><button class="cap-more" id="cap-more" type="button">Show more frames</button></div></section>
    {navigation(nav_prev, nav_next, "Screencap navigation")}
    </main><footer><div class="shell footer-row">BOGGSFILES · SCREENCAP ARCHIVE <span><a href="/">Home</a> · <a href="{esc(up_url)}">Back</a> · <a href="/screencaps/">All screencaps</a></span></div></footer>
    <script>
    const FRAMES={json.dumps(data, separators=(",", ":"))};const GROUPS={json.dumps(GROUPS)};const BASE={json.dumps(media)};
    const grid=document.getElementById('cap-grid'),count=document.getElementById('cap-count'),empty=document.getElementById('cap-empty'),more=document.getElementById('cap-more');
    const tc=ms=>{{const s=Math.floor(ms/1000);return `${{Math.floor(s/3600)}}:${{String(Math.floor(s%3600/60)).padStart(2,'0')}}:${{String(s%60).padStart(2,'0')}}`}};
    const parse=v=>{{if(!v.trim())return null;const x=v.split(':').map(Number).reverse();return ((x[2]||0)*3600+(x[1]||0)*60+(x[0]||0))*1000}};
    let who='All',shown=0,list=[];const PAGE=240;
    function matches(tags){{if(who==='All')return true;const need=GROUPS[who]||[who];return need.every(n=>tags.includes(n))}}
    function refresh(){{const a=parse(document.getElementById('cap-a').value)??0,b=parse(document.getElementById('cap-b').value)??Infinity;
      list=FRAMES.filter(([id,tags])=>{{const ms=+id;return ms>=a&&ms<=b&&matches(tags)}});grid.innerHTML='';shown=0;renderMore();
      count.textContent=list.length.toLocaleString()+' frames';empty.hidden=list.length>0}}
    function renderMore(){{const slice=list.slice(shown,shown+PAGE);const frag=document.createDocumentFragment();
      for(const [id,tags] of slice){{const a=document.createElement('a');a.className='cap';a.href=BASE+'full/'+id+'.jpg';a.target='_blank';a.rel='noopener';
        const lab=tags.filter(x=>x!=='Hallway Scene');a.innerHTML=`<img loading="lazy" src="${{BASE}}thumb/${{id}}.jpg" alt="Frame at ${{tc(+id)}}"><span>${{tc(+id)}}</span>${{lab.length?`<em>${{lab.join(', ')}}</em>`:''}}`;frag.appendChild(a)}}
      grid.appendChild(frag);shown+=slice.length;more.hidden=shown>=list.length}}
    document.querySelectorAll('.cap-toolbar button').forEach(btn=>btn.addEventListener('click',()=>{{who=btn.dataset.f;document.querySelectorAll('.cap-toolbar button').forEach(x=>x.classList.toggle('on',x===btn));refresh()}}));
    document.querySelector('.cap-toolbar button').classList.add('on');
    document.getElementById('cap-a').addEventListener('input',refresh);document.getElementById('cap-b').addEventListener('input',refresh);more.addEventListener('click',renderMore);refresh();
    </script></body></html>'''


CARD_CSS = '''.episodes{padding:72px 0 0}.season-head{display:flex;justify-content:space-between;align-items:end;margin-bottom:34px}.season-head h2{font:400 clamp(3.2rem,6vw,6rem)/.9 "Oswald",sans-serif;text-transform:uppercase;margin:10px 0 0}.season-head>span{color:#8c968f;font-size:.62rem;letter-spacing:.12em;text-transform:uppercase}.episode-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;background:#343c38;border:1px solid #343c38}.episode-card{background:#0e1412;display:flex;min-width:0;flex-direction:column;transition:.2s}.episode-card:hover{background:#141b18}.episode-card img{width:100%;aspect-ratio:16/10;object-fit:cover;filter:saturate(.82) brightness(.79);transition:.25s}.episode-card:hover img{filter:saturate(.95) brightness(.9)}.episode-copy{padding:25px 25px 28px;display:flex;flex:1;flex-direction:column;min-height:250px}.episode-copy>span{color:#e44238;font-size:.53rem;letter-spacing:.14em;text-transform:uppercase}.episode-copy h2{font:400 clamp(1.8rem,2.4vw,2.75rem)/.96 "Oswald",sans-serif;text-transform:uppercase;margin:14px 0 15px}.episode-copy p{color:#929c95;font-size:.66rem;line-height:1.7;margin:0}.episode-copy b{margin-top:auto;padding-top:24px;font-size:.54rem;letter-spacing:.12em;text-transform:uppercase}.episode-card.pending{color:#929c95}.episode-card.pending img{filter:saturate(.3) brightness(.45)}.episode-card.pending:hover{background:#0e1412}.episode-card.pending:hover img{filter:saturate(.3) brightness(.45)}.episode-card.pending h2{color:#b9c0bb}@media(max-width:1160px){.episode-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:650px){.episode-grid{grid-template-columns:1fr}.season-head{align-items:start;flex-direction:column;gap:18px}}'''


def card(href, img, kind, title, note, live) -> str:
    inner = f'<img src="{esc(img)}" alt="{esc(title)}" loading="lazy"><div class="episode-copy"><span>{esc(kind)}</span><h2>{esc(title)}</h2><p>{esc(note)}</p><b>{"Browse frames →" if live else "Coming soon"}</b></div>'
    return f'<a class="episode-card" href="{esc(href)}">{inner}</a>' if live else f'<article class="episode-card pending">{inner}</article>'


def page(title, crumb, eyebrow, h1, intro, stats, head_eyebrow, head_h2, head_note, cards, nav_html="") -> str:
    return f'''<!doctype html><html lang="en"><head><title>{esc(title)} - Boggsfiles</title><meta name="description" content="{esc(intro)}">{HEAD}<style>{BASE}
    {CARD_CSS}
    </style>{ASSETS}{NAV_ASSET}</head><body>{HEADER}<main><section class="hero"><div class="shell"><div class="crumb">{crumb}</div><div class="eyebrow">{esc(eyebrow)}</div><h1>{esc(h1)}</h1><p>{esc(intro)}</p><div class="summary">{stats}</div></div></section>
    <section class="episodes"><div class="shell"><div class="season-head"><div><div class="eyebrow">{esc(head_eyebrow)}</div><h2>{esc(head_h2)}</h2></div><span>{esc(head_note)}</span></div><div class="episode-grid">{cards}</div></div></section>{nav_html}</main><footer><div class="shell footer-row">BOGGSFILES · SCREENCAP ARCHIVE <span><a href="/">Home</a> · <a href="/screencaps/">All screencaps</a></span></div></footer></body></html>'''


def stat(b, s): return f'<div class="stat"><b>{b}</b><span>{s}</span></div>'


COVER_OVERRIDES = json.loads((ROOT / "tools/screencaps/cover-overrides.json").read_text()) if (ROOT / "tools/screencaps/cover-overrides.json").exists() else {}

def cover_for(ep: dict) -> str:
    if ep["code"] in COVER_OVERRIDES: return f"{MEDIA_BASE}/screencaps/{ep['path']}/thumb/{COVER_OVERRIDES[ep['code']]}"   # hand-picked by Lindsey
    index = json.load(open(ep["source"] / "index.json")); frames = sorted(index)
    both = [f for f in frames if {"Mulder", "Scully"} <= set(index[f])] or [f for f in frames if index[f]] or frames
    return f"{MEDIA_BASE}/screencaps/{ep['path']}/thumb/{both[len(both) // 2]}"


def sync_media(items: list[dict]) -> None:
    """Upload any live title whose frames aren't on R2 yet (rclone copy is incremental)."""
    for t in items:
        if not t.get("source") or not (t["source"] / "index.json").exists(): continue
        marker = t["source"] / ".uploaded"
        if marker.exists(): continue
        for sub in ("full", "thumb"):
            subprocess.run(["rclone", "copy", str(t["source"] / sub), f"{BUCKET}/screencaps/{t['path']}/{sub}", "--transfers", "32", "--checkers", "32", "--s3-no-check-bucket", "-q"], check=True)
        marker.write_text("ok"); print("uploaded", t["path"], flush=True)


def main() -> None:
    out = ROOT / "dist/screencaps"; out.mkdir(exist_ok=True)
    films = [dict(f, path=f["slug"]) for f in FILMS]
    eps = [dict(e, path=f"season-{e['season']}/{e['slug']}") for e in episodes()]
    sync_media([f for f in films if f["source"]] + eps)

    # film galleries
    for f in films:
        if not f["source"]: continue
        (out / f["slug"]).mkdir(exist_ok=True)
        crumb = f'<a href="/screencaps/">Screencaps</a> &nbsp;/&nbsp; {esc(f["title"])}'
        (out / f["slug"] / "index.html").write_text(gallery_page(f, crumb, f["filters"], "/screencaps/", None, None), encoding="utf-8")

    # season pages + episode galleries
    seasons_live = {}
    for s in range(1, 12):
        rows = sorted([e for e in eps if e["season"] == s], key=lambda e: e["num"])
        for i, e in enumerate(rows, 1): e["num"] = i          # display number = position in the season (Pilot = 1)
        live = [e for e in rows if e["live"]]
        seasons_live[s] = len(live)
        if not rows: continue
        sdir = out / f"season-{s}"; sdir.mkdir(exist_ok=True)
        for i, e in enumerate(live):
            e_dir = sdir / e["slug"]; e_dir.mkdir(exist_ok=True)
            t = {**e, "kind": f"Season {s} · Episode {e['num']}", "year": e["code"], "blurb": f"Every shot change, with dense coverage wherever Mulder or Scully is on screen. Prepared from the Season {s} {e['media']}."}
            crumb = f'<a href="/screencaps/">Screencaps</a> &nbsp;/&nbsp; <a href="/screencaps/season-{s}/">Season {s}</a> &nbsp;/&nbsp; {esc(e["title"])}'
            prev = (f"/screencaps/season-{s}/{live[i-1]['slug']}/", live[i-1]["title"]) if i > 0 else (f"/screencaps/season-{s}/", f"Season {s}")
            nxt = (f"/screencaps/season-{s}/{live[i+1]['slug']}/", live[i+1]["title"]) if i + 1 < len(live) else None
            (e_dir / "index.html").write_text(gallery_page(t, crumb, CHARACTER_FILTERS, f"/screencaps/season-{s}/", prev, nxt), encoding="utf-8")
        cards = "".join(card(f"/screencaps/season-{s}/{e['slug']}/", cover_for(e) if e["live"] else f"/assets/transcript-stills/{SEASON_IMAGE[s]}",
                             f"File {e['num']:02d} · {e['code']}", e["title"], (f"{len(json.load(open(e['source'] / 'index.json'))):,} frames · {e['media']}" if e["live"] else "In preparation"), e["live"]) for e in rows)
        crumb = f'<a href="/screencaps/">Screencaps</a> &nbsp;/&nbsp; Season {s}'
        nav = navigation((f"/screencaps/season-{s-1}/", f"Season {s-1}") if s > 1 else None, (f"/screencaps/season-{s+1}/", f"Season {s+1}") if s < 11 else None, "Season navigation")
        (sdir / "index.html").write_text(page(f"Season {s} Screencaps", crumb, SEASON_YEARS[s], f"Season {s}", f"Frame-by-frame captures for Season {s}, tagged by who is on screen and searchable by timecode.",
                                              stat(len(live), "Episodes live") + stat(SEASON_TOTAL[s], "Episodes total") + stat(rows[0]["media"], "Source"),
                                              "Episode files", f"Season {s} frames", "Broadcast order · Four across", cards, nav), encoding="utf-8")

    # landing
    total_frames = sum(len(json.load(open(e["source"] / "index.json"))) for e in eps if e["live"]) + sum(len(json.load(open(f["source"] / "index.json"))) for f in films if f["source"])
    def film_card(f):
        return card(f"/screencaps/{f['slug']}/", f["still"], f"{f['kind']} · {f['year']}", f["title"], (f"{len(json.load(open(f['source'] / 'index.json'))):,} frames · {f['media']}" if f["source"] else f["blurb"]), bool(f["source"]))
    def season_card(s):
        return card(f"/screencaps/season-{s}/", f"/assets/transcript-stills/{SEASON_IMAGE[s]}", SEASON_YEARS[s], f"Season {s}",
                    (f"{seasons_live[s]} of {SEASON_TOTAL[s]} episodes live · {'Blu-ray' if s >= 10 else 'DVD'}" if seasons_live[s] else f"{SEASON_TOTAL[s]} episodes · in preparation"), seasons_live[s] > 0)
    # release order: Fight the Future after Season 5, I Want to Believe after Season 9
    cards = ""
    for s in range(1, 12):
        cards += season_card(s)
        if s == 5: cards += film_card(films[0])
        if s == 9: cards += film_card(films[1])
    live_titles = sum(1 for f in films if f["source"]) + sum(seasons_live.values())
    (out / "index.html").write_text(page("Screencaps", '<a href="/archive/">Archive</a> &nbsp;/&nbsp; Screencaps', "Frame by frame", "Screencaps",
                                         "Captures taken at every shot change, tagged by who is on screen and searchable by timecode — Blu-ray for the films and Seasons 10–11, DVD for Seasons 1–9. Episodes go live as they are processed.",
                                         stat(live_titles, "Titles live") + stat(f"{total_frames:,}", "Frames") + stat("DVD · Blu-ray", "Sources"),
                                         "The collection", "Films and seasons", "Release order", cards), encoding="utf-8")
    print(f"screencaps: {live_titles} titles live, {total_frames:,} frames")


if __name__ == "__main__":
    main()
