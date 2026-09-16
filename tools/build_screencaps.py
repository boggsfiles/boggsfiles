#!/usr/bin/env python3
"""Build the Screencaps section: /screencaps/ landing and one gallery page per title.

Source folders (from the screencap pipeline) hold full/, thumb/ and index.json (frame -> tags).
Images are copied into dist/assets/screencaps/<slug>/{full,thumb}/ with the full-size JPEGs
re-encoded to keep the published site a reasonable size.
"""
from __future__ import annotations
import json, os, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from transcript_header import site_header, ASSETS
from build_transcript_indexes import HEAD, BASE

ROOT = Path(__file__).resolve().parent.parent
HEADER = site_header("Screencaps")

TITLES = [
    {
        "slug": "fight-the-future", "title": "Fight the Future", "kind": "Feature film", "year": "1998",
        "source": Path.home() / "Movies/XF_screencaps/Fight the Future (extended)",
        "aspect": "1920/816", "note": "Extended cut · Blu-ray · 1920×816",
        "blurb": "Every shot change from the extended cut, with dense coverage wherever Mulder or Scully is on screen.",
        "filters": ["Mulder", "Scully", "Mulder + Scully", "The Hallway Scene", "Skinner", "CSM", "Well-Manicured Man",
                    "Kurtzweil", "The Lone Gunmen", "Cassidy", "Michaud", "Bronschweig", "Strughold", "Syndicate", "Barmaid", "Stevie"],
        "groups": {"Mulder + Scully": ["Mulder", "Scully"], "The Lone Gunmen": ["Byers", "Frohike", "Langly"], "The Hallway Scene": ["Hallway Scene"]},
    },
]


def tc(ms: int) -> str:
    s = ms // 1000
    return f"{s // 3600}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def copy_images(t: dict, dest: Path) -> list[str]:
    (dest / "full").mkdir(parents=True, exist_ok=True); (dest / "thumb").mkdir(parents=True, exist_ok=True)
    frames = sorted(f for f in os.listdir(t["source"] / "full") if f.endswith(".jpg"))
    for f in frames:
        if not (dest / "full" / f).exists():
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(t["source"] / "full" / f), "-q:v", "4", str(dest / "full" / f)], check=True)
        if not (dest / "thumb" / f).exists():
            shutil.copy2(t["source"] / "thumb" / f, dest / "thumb" / f)
    return frames


def gallery_page(t: dict, frames: list[str], index: dict) -> str:
    tags_present = sorted({x for v in index.values() for x in v})
    data = [[f[:-4], index.get(f, [])] for f in frames]
    buttons = "".join(f'<button type="button" data-f="{esc(f)}">{esc(f)}</button>' for f in ["All"] + t["filters"])
    return f'''<!doctype html><html lang="en"><head><title>{esc(t["title"])} Screencaps - Boggsfiles</title><meta name="description" content="{esc(t["title"])} screencaps, tagged by character and searchable by time.">{HEAD}<style>{BASE}
    .caps{{padding:40px 0 80px}}.cap-toolbar{{position:sticky;top:0;z-index:4;background:#08100d;border-bottom:1px solid #343c38;padding:14px 0}}.cap-toolbar .shell{{display:flex;gap:10px;align-items:center;flex-wrap:wrap}}.cap-toolbar b{{font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;color:#8c968f;margin-right:6px;white-space:nowrap}}.cap-toolbar button{{background:#0e1412;border:1px solid #343c38;color:#eeeee8;padding:7px 12px;font:400 .62rem/1 "DM Mono",monospace;letter-spacing:.08em;text-transform:uppercase;cursor:pointer;transition:.15s}}.cap-toolbar button:hover{{background:#151b18}}.cap-toolbar button.on{{background:#b4312d;border-color:#b4312d}}.cap-toolbar input{{background:#0e1412;border:1px solid #343c38;color:#eeeee8;padding:7px 10px;font:400 .68rem "DM Mono",monospace;width:96px}}.cap-count{{margin-left:auto;font-size:.62rem;letter-spacing:.1em;color:#8c968f;text-transform:uppercase}}
    .cap-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;background:#343c38;border:1px solid #343c38;margin-top:28px}}.cap{{position:relative;display:block;background:#0e1412;min-width:0}}.cap img{{width:100%;display:block;aspect-ratio:{t["aspect"]};object-fit:cover;filter:saturate(.9) brightness(.86);transition:.2s}}.cap:hover img{{filter:none}}.cap span{{position:absolute;left:8px;bottom:8px;background:rgba(8,16,13,.82);padding:3px 7px;font-size:.58rem;letter-spacing:.08em;font-variant-numeric:tabular-nums}}.cap em{{position:absolute;right:8px;bottom:8px;background:rgba(180,49,45,.9);padding:3px 7px;font-size:.52rem;letter-spacing:.08em;text-transform:uppercase;font-style:normal;max-width:60%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
    .cap-empty{{padding:80px 0;text-align:center;color:#8c968f}}.cap-more{{display:block;}}.cap-more[hidden]{{display:none}}.cap-more{{margin:28px auto 0;background:#0e1412;border:1px solid #343c38;color:#eeeee8;padding:14px 28px;font:400 .62rem "DM Mono",monospace;letter-spacing:.14em;text-transform:uppercase;cursor:pointer}}
    @media(max-width:1160px){{.cap-grid{{grid-template-columns:repeat(3,1fr)}}}}@media(max-width:700px){{.cap-grid{{grid-template-columns:repeat(2,1fr)}}.cap-count{{margin-left:0;width:100%}}}}
    </style>{ASSETS}</head><body>{HEADER}<main>
    <section class="hero"><div class="shell"><div class="crumb"><a href="/screencaps/">Screencaps</a> &nbsp;/&nbsp; {esc(t["title"])}</div><div class="eyebrow">{esc(t["kind"])} · {esc(t["year"])}</div><h1>{esc(t["title"])}</h1><p>{esc(t["blurb"])} Filter by who is on screen, or jump to a stretch of the film by timecode. Click any frame for the full-size capture.</p><div class="summary"><div class="stat"><b>{len(frames):,}</b><span>Frames</span></div><div class="stat"><b>{len(tags_present)}</b><span>Tags</span></div><div class="stat"><b>Blu-ray</b><span>Source</span></div></div></div></section>
    <div class="cap-toolbar"><div class="shell"><b>Show</b>{buttons}<label style="margin-left:8px"><b>From</b><input id="cap-a" placeholder="0:00:00"></label><label><b>To</b><input id="cap-b" placeholder="2:02:41"></label><span class="cap-count" id="cap-count"></span></div></div>
    <section class="caps"><div class="shell"><div class="cap-grid" id="cap-grid"></div><div class="cap-empty" id="cap-empty" hidden>No frames match that filter.</div><button class="cap-more" id="cap-more" type="button">Show more frames</button></div></section>
    </main><footer><div class="shell footer-row">BOGGSFILES · SCREENCAP ARCHIVE <span><a href="/">Home</a> · <a href="/screencaps/">All screencaps</a></span></div></footer>
    <script>
    const FRAMES={json.dumps(data, separators=(",", ":"))};
    const GROUPS={json.dumps(t["groups"])};
    const BASE="/assets/screencaps/{t["slug"]}/";
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
        a.innerHTML=`<img loading="lazy" src="${{BASE}}thumb/${{id}}.jpg" alt="Frame at ${{tc(+id)}}"><span>${{tc(+id)}}</span>${{tags.length?`<em>${{tags.filter(x=>x!=='Hallway Scene').join(', ')}}</em>`:''}}`;frag.appendChild(a)}}
      grid.appendChild(frag);shown+=slice.length;more.hidden=shown>=list.length}}
    document.querySelectorAll('.cap-toolbar button').forEach(btn=>btn.addEventListener('click',()=>{{who=btn.dataset.f;document.querySelectorAll('.cap-toolbar button').forEach(x=>x.classList.toggle('on',x===btn));refresh()}}));
    document.querySelector('.cap-toolbar button').classList.add('on');
    document.getElementById('cap-a').addEventListener('input',refresh);document.getElementById('cap-b').addEventListener('input',refresh);more.addEventListener('click',renderMore);refresh();
    </script></body></html>'''


def landing(cards: list[dict]) -> str:
    items = "".join(f'''<a class="episode-card" href="/screencaps/{esc(c["slug"])}/"><img src="/assets/screencaps/{esc(c["slug"])}/thumb/{esc(c["cover"])}" alt="Scene from {esc(c["title"])}" loading="lazy"><div class="episode-copy"><span>{esc(c["kind"])} · {esc(c["year"])} · {c["count"]:,} frames</span><h2>{esc(c["title"])}</h2><p>{esc(c["blurb"])}</p><b>Browse frames →</b></div></a>''' for c in cards)
    return f'''<!doctype html><html lang="en"><head><title>Screencaps - Boggsfiles</title><meta name="description" content="High-resolution X-Files screencaps, tagged by character and searchable by time.">{HEAD}<style>{BASE}
    .episodes{{padding:72px 0 0}}.episode-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;background:#343c38;border:1px solid #343c38}}.episode-card{{background:#0e1412;display:flex;min-width:0;flex-direction:column;transition:.2s}}.episode-card:hover{{background:#141b18}}.episode-card img{{width:100%;aspect-ratio:16/10;object-fit:cover;filter:saturate(.82) brightness(.79);transition:.25s}}.episode-card:hover img{{filter:saturate(.95) brightness(.9)}}.episode-copy{{padding:25px 25px 28px;display:flex;flex:1;flex-direction:column;min-height:290px}}.episode-copy>span{{color:#e44238;font-size:.53rem;letter-spacing:.14em;text-transform:uppercase}}.episode-copy h2{{font:400 clamp(1.8rem,2.4vw,2.75rem)/.96 "Oswald",sans-serif;text-transform:uppercase;margin:14px 0 15px}}.episode-copy p{{color:#929c95;font-size:.66rem;line-height:1.7;margin:0}}.episode-copy b{{margin-top:auto;padding-top:24px;font-size:.54rem;letter-spacing:.12em;text-transform:uppercase}}@media(max-width:1160px){{.episode-grid{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:650px){{.episode-grid{{grid-template-columns:1fr}}}}
    </style>{ASSETS}</head><body>{HEADER}<main><section class="hero"><div class="shell"><div class="crumb"><a href="/archive/">Archive</a> &nbsp;/&nbsp; Screencaps</div><div class="eyebrow">Frame by frame</div><h1>Screencaps</h1><p>High-resolution captures taken at every shot change, tagged by who is on screen and searchable by timecode. Prepared from Blu-ray sources, with the full series to follow.</p><div class="summary"><div class="stat"><b>{len(cards)}</b><span>Titles live</span></div><div class="stat"><b>{sum(c["count"] for c in cards):,}</b><span>Frames</span></div><div class="stat"><b>Blu-ray</b><span>Source</span></div></div></div></section>
    <section class="episodes"><div class="shell"><div class="episode-grid">{items}</div></div></section></main><footer><div class="shell footer-row">BOGGSFILES · SCREENCAP ARCHIVE <span><a href="/">Home</a> · <a href="/archive/">Archive</a></span></div></footer></body></html>'''


def esc(v) -> str:
    import html; return html.escape(str(v), quote=True)


def main() -> None:
    cards = []
    for t in TITLES:
        dest = ROOT / "dist/assets/screencaps" / t["slug"]
        frames = copy_images(t, dest)
        index = json.load(open(t["source"] / "index.json"))
        out = ROOT / "dist/screencaps" / t["slug"]; out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(gallery_page(t, frames, index), encoding="utf-8")
        both = [f for f in frames if {"Mulder", "Scully"} <= set(index.get(f, []))]
        cards.append({**t, "count": len(frames), "cover": (both[len(both) // 2] if both else frames[len(frames) // 2])})
        print(t["slug"], len(frames), "frames")
    (ROOT / "dist/screencaps").mkdir(exist_ok=True)
    (ROOT / "dist/screencaps/index.html").write_text(landing(cards), encoding="utf-8")


if __name__ == "__main__":
    main()
