#!/usr/bin/env python3
"""Build the production-sound pages: raw location and wild-track audio, filed under Memorabilia.

Same delivery as build_dailies.py and build_gag_reels.py: the audio lives in the PRIVATE R2 bucket
(boggsfiles-private) under production-audio/, and the page asks the boggsfiles-dailies Worker for a
signed link that expires after a few hours, so the raw bucket URL is never exposed.

The waveform is baked in rather than computed in the browser, so it draws before the audio loads
and the page never needs to decode the file itself. Strip the tags from a file before uploading it
(ffmpeg -map_metadata -1 -c copy), so only the audio itself is published.

The still is one of the archive's own DVD captures, copied to dist/assets/production-audio/<slug>.jpg.
Run:  python3 tools/build_production_audio.py   (then commit + ./publish.sh)
"""
from __future__ import annotations
import html, json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from transcript_header import ASSETS, site_header
from media_host import WORKER          # see tools/media_host.py: workers.dev is blocked in some regions

DIST = Path(__file__).resolve().parents[1] / "dist"
MEDIA_PREFIX = "production-audio/"

AIRED = "Hi, this is Fox Mulder. You can leave me a message after the beep."
DROPPED = "If this is you, Scully, call me on my cell phone. I think you know the number."

# slug -> everything the page needs. `takes` are the readings of the message and `dropped` the
# stretch of each that is not in the finished episode; anything outside a take (false start, slate,
# room tone) is drawn grey, because it is neither. `marks` are the jump points, in order:
# (seconds, label, text, whole message?)
RECORDINGS = {
    "agua-mala-answering-machine": {
        "title": "Mulder’s Answering Machine",
        "episode": "Agua Mala", "code": "6ABX14", "season": "Season 6 · Episode 13",
        "key": "agua-mala-answering-machine.m4a",
        "seconds": 36.69,
        "lede": "The outgoing message on Mulder’s machine, as it was recorded: three takes, a false start and the sound mixer’s slate.",
        "intro": [
            "At the top of Act One of Agua Mala the phone rings in Mulder’s empty apartment and his machine picks up, "
            "before Arthur Dales leaves the message about the hurricane. This is the recording made for that machine: "
            "David Duchovny reading the outgoing message three times, with a false start and the sound mixer’s slate in between.",
            "It is a wild track, which means sound recorded on its own with no camera rolling. "
            "Nothing here has been trimmed or cleaned up.",
        ],
        "takes": [(1.4, 8.3), (18.6, 25.8), (27.0, 33.7)],
        "dropped": [(4.5, 8.3), (22.4, 25.8), (29.8, 33.7)],
        "marks": [
            (1.4, "Take 1", None, True),
            (9.5, "False start", "“Hi, this is Fox Mulder.” He stops, and there is a short exchange with the sound mixer.", False),
            (14.6, "Slate", "The sound mixer: “This will be take two, channel two.”", False),
            (18.6, "Take 2", None, True),
            (27.0, "Take 3", None, True),
        ],
        "facts": [
            ("What made it to air",
             "Only the first sentence. It plays about three minutes in, straight after the main titles, "
             "while the camera drifts through the dark apartment under the guest cast credits. "
             "The line to Scully is not in the episode.",
             [("Read the transcript", "/transcripts/season-6/agua-mala/#scene-2")]),
            ("What the script says",
             "The scene is not in the Salmon revision of January 12, 1999, the last full script in the archive. "
             "There, Act One opens in Arthur Dales’s trailer. The only trace of the call is Scully’s line to him later: "
             "“Agent Mulder played me the message you left him.”",
             [("Read the Salmon script", "/script-text/6abx14-agua-mala-salmon/")]),
        ],
        "more": [("Agua Mala screencaps", "/screencaps/season-6/agua-mala/")],
        # 150 bars, 0-100, from the file itself (RMS per slice, lifted so the quiet slate still shows)
        "wave": [9,9,19,9,13,16,10,67,84,86,74,83,71,68,65,74,56,70,49,45,65,70,72,71,59,78,55,34,9,38,44,44,48,20,9,9,9,9,9,9,
                 76,34,90,74,54,22,30,57,77,40,10,53,55,46,14,37,17,13,12,9,20,58,57,51,53,40,19,60,38,45,25,9,10,10,10,10,10,
                 91,86,93,93,87,81,62,66,65,76,48,67,44,10,10,27,46,56,65,66,67,57,61,41,40,39,43,49,21,9,9,9,10,10,30,82,34,
                 100,83,67,66,65,62,55,57,45,41,57,84,62,68,61,95,52,41,45,52,66,36,57,28,9,9,9,8,5,5,5,5,5,5,5,5],
    },
}

STYLE = """<style>
.pa{--cut:#e0796c;max-width:880px}
.pa-player{background:#111614;border:1px solid var(--line);padding:12px}
.pa-player img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;background:#050606}
.pa-controls{display:flex;align-items:center;gap:18px;margin-top:16px}
.pa-play{flex:none;width:58px;height:58px;border-radius:50%;border:1px solid #6b746d;background:transparent;color:var(--paper);display:grid;place-items:center;cursor:pointer;transition:.2s}
.pa-play:hover,.pa-play:focus-visible{background:var(--paper);color:var(--ink);outline:0}
.pa-play .pause,.pa-playing .pa-play .play{display:none}
.pa-playing .pa-play .pause{display:block}
.pa-wave{flex:1;min-width:0;height:76px;display:flex;align-items:center;gap:2px;cursor:pointer;touch-action:none}
.pa-wave:focus-visible{outline:1px solid #6b746d;outline-offset:6px}
.pa-wave i{flex:1;min-width:1px;background:var(--paper);opacity:.26;border-radius:1px}
.pa-wave i.cut{background:var(--cut);opacity:.42}
.pa-wave i.off{background:#7f8982;opacity:.3}
.pa-wave i.on{opacity:1}
.pa-time{flex:none;font:400 .72rem/1 var(--mono);letter-spacing:.06em;color:#9aa39d;white-space:nowrap}
.pa-key{display:flex;gap:22px;flex-wrap:wrap;margin-top:14px;font:400 .68rem/1.4 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:#9aa39d}
.pa-key span:before{content:'';display:inline-block;width:10px;height:10px;margin-right:9px;background:var(--paper);vertical-align:-1px}
.pa-key .cut{color:var(--cut)}
.pa-key .cut:before{background:var(--cut)}
.pa-key .off:before{background:#7f8982}
.pa-error{margin:14px 0 0;font:400 .72rem/1.4 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:#9aa39d}
.pa h2{font:400 clamp(1.7rem,3vw,2.4rem)/1 var(--display);text-transform:uppercase;letter-spacing:.02em;margin:64px 0 22px}
.pa-marks{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}
.pa-marks button{display:grid;grid-template-columns:64px 150px 1fr;gap:18px;width:100%;padding:18px 4px;background:transparent;border:0;border-bottom:1px solid var(--line);color:inherit;font:inherit;text-align:left;cursor:pointer;transition:.2s}
.pa-marks button:hover,.pa-marks button:focus-visible{background:#111614;outline:0}
.pa-marks .t{color:#7f8982;font-size:.8rem}
.pa-marks .l{font:400 1.15rem/1.3 var(--display);text-transform:uppercase;letter-spacing:.05em}
.pa-marks .x{color:#aeb5af}
.pa-marks .x b{font-weight:400;color:var(--paper)}
.pa-marks .x em{font-style:normal;color:var(--cut)}
.pa-facts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.pa-fact{border:1px solid var(--line);padding:26px 28px 28px;display:flex;flex-direction:column;align-items:flex-start}
.pa-fact h3{font:400 1.35rem/1.1 var(--display);text-transform:uppercase;letter-spacing:.04em;margin:0 0 14px}
.pa-fact p{color:#aeb5af;margin:0 0 22px}
.pa-link{margin-top:auto;border:1px solid #4b544e;padding:9px 12px;font-size:.61rem;letter-spacing:.1em;text-transform:uppercase;transition:.2s}
.pa-link:hover{background:var(--paper);color:var(--ink)}
.pa-more{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
@media(max-width:700px){.pa-controls{flex-wrap:wrap;gap:14px 12px}.pa-play{width:50px;height:50px}.pa-time{margin-left:auto}.pa-wave{order:3;flex:0 0 100%;height:64px}.pa-wave i:nth-child(even){display:none}.pa-marks button{grid-template-columns:48px 1fr;gap:6px 14px}.pa-marks .x{grid-column:2}.pa-facts{grid-template-columns:1fr}}
</style>"""

# Signs the link the same way the video loader does, then runs the player: the waveform is the
# seek bar, and each row of the list jumps to its take.
PLAYER_JS = ('<script>(function(){var W=' + repr(WORKER) + ';'
    'var a=document.getElementById("pa-audio"),root=a.closest(".pa-player"),btn=root.querySelector(".pa-play"),'
    'wave=root.querySelector(".pa-wave"),bars=wave.children,time=root.querySelector(".pa-time"),D=parseFloat(a.dataset.seconds),pending=null,retried=false;'
    'function dur(){return isFinite(a.duration)&&a.duration?a.duration:D}'
    'function fmt(s){s=Math.max(0,Math.floor(s));return Math.floor(s/60)+":"+("0"+s%60).slice(-2)}'
    'function paint(){var t=a.currentTime||0,n=Math.round(t/dur()*bars.length);for(var i=0;i<bars.length;i++)bars[i].classList.toggle("on",i<n);'
    'time.textContent=fmt(t)+" / "+fmt(dur());wave.setAttribute("aria-valuenow",Math.round(t));wave.setAttribute("aria-valuetext",fmt(t)+" of "+fmt(dur()))}'
    'function loop(){paint();if(!a.paused)requestAnimationFrame(loop)}'
    'function fail(){root.querySelector(".pa-error").hidden=false}'
    'function sign(resume){fetch(W+"/sign?key="+encodeURIComponent(a.dataset.key)).then(function(r){if(!r.ok)throw r.status;return r.json()})'
    '.then(function(j){var t=a.currentTime,play=!a.paused;a.src=j.url;if(resume){pending=t;if(play)a.play()}}).catch(fail)}'
    'function seek(t,play){t=Math.max(0,Math.min(dur()-.05,t));if(a.readyState>0)a.currentTime=t;else pending=t;paint();if(play)a.play().catch(function(){})}'
    'function at(e){var r=wave.getBoundingClientRect();return (e.clientX-r.left)/r.width*dur()}'
    'a.addEventListener("loadedmetadata",function(){if(pending!==null){a.currentTime=pending;pending=null}paint()});'
    'a.addEventListener("error",function(){if(!retried&&a.src){retried=true;sign(true)}else if(a.src)fail()});'
    'a.addEventListener("play",function(){root.classList.add("pa-playing");btn.setAttribute("aria-label","Pause");loop()});'
    'a.addEventListener("pause",function(){root.classList.remove("pa-playing");btn.setAttribute("aria-label","Play");paint()});'
    'a.addEventListener("timeupdate",paint);a.addEventListener("ended",paint);'
    'btn.addEventListener("click",function(){if(a.paused)a.play().catch(function(){});else a.pause()});'
    'var down=false;wave.addEventListener("pointerdown",function(e){down=true;wave.setPointerCapture(e.pointerId);seek(at(e),false)});'
    'wave.addEventListener("pointermove",function(e){if(down)seek(at(e),false)});'
    'wave.addEventListener("pointerup",function(){down=false});wave.addEventListener("pointercancel",function(){down=false});'
    'wave.addEventListener("keydown",function(e){var t=a.currentTime||0,k=e.key;'
    'if(k==="ArrowRight")seek(t+2,false);else if(k==="ArrowLeft")seek(t-2,false);else if(k==="Home")seek(0,false);else if(k==="End")seek(dur(),false);'
    'else if(k===" "||k==="Enter")btn.click();else return;e.preventDefault()});'
    'document.querySelectorAll("[data-seek]").forEach(function(b){b.addEventListener("click",function(){seek(parseFloat(b.dataset.seek),true);'
    'root.scrollIntoView({behavior:"smooth",block:"nearest"})})});'
    'sign(false);paint()})();</script>')

ICONS = ('<svg class="play" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="currentColor"><path d="M8 5.5v13l11-6.5z"/></svg>'
         '<svg class="pause" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="currentColor"><path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z"/></svg>')


def page(title: str, description: str, body: str) -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)} - Boggsfiles</title><meta name="description" content="{html.escape(description, quote=True)}">'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Libre+Caslon+Display&family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet">'
            f'<link rel="stylesheet" href="/assets/archive-detail.css?v=4">{ASSETS}{STYLE}</head><body>{site_header("Memorabilia")}<main>{body}</main>'
            f'<footer><div class="shell footer-row">BOGGSFILES &middot; PRODUCTION SOUND <span><a href="/">Home</a> &middot; <a href="/memorabilia/">Back to Memorabilia</a></span></div></footer></body></html>')


def write_route(route: str, content: str) -> None:
    dest = DIST / route.strip("/") / "index.html"; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_text(content, encoding="utf-8")


def r2_keys() -> set[str]:
    out = subprocess.run(["rclone", "lsf", "r2:boggsfiles-private/" + MEDIA_PREFIX], capture_output=True, text=True, check=True).stdout
    return set(out.split("\n"))


def clock(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 60}:{s % 60:02d}"


def detail(slug: str, r: dict) -> None:
    e = html.escape
    total, wave = r["seconds"], r["wave"]
    bars = []
    for i, h in enumerate(wave):
        mid = (i + 0.5) / len(wave) * total
        kind = ("cut" if any(a <= mid < b for a, b in r["dropped"]) else
                "" if any(a <= mid < b for a, b in r["takes"]) else "off")
        bars.append(f'<i{f" class={kind}" if kind else ""} style="height:{max(4, h)}%"></i>')
    takes = sum(1 for m in r["marks"] if m[3])
    still = f"/assets/production-audio/{slug}.jpg"
    player = (f'<div class="pa-player"><img src="{still}" alt="The answering machine on Mulder’s desk in {e(r["episode"])}" width="853" height="480">'
              f'<audio id="pa-audio" preload="metadata" data-key="{e(MEDIA_PREFIX + r["key"], quote=True)}" data-seconds="{total}"></audio>'
              f'<div class="pa-controls"><button class="pa-play" type="button" aria-label="Play">{ICONS}</button>'
              f'<div class="pa-wave" role="slider" tabindex="0" aria-label="Position in the recording" aria-valuemin="0" aria-valuemax="{int(total)}" aria-valuenow="0">{"".join(bars)}</div>'
              f'<span class="pa-time">0:00 / {clock(total)}</span></div>'
              f'<div class="pa-key"><span>The sentence that aired</span><span class="cut">The sentence that was cut</span><span class="off">Between takes, not in the episode</span></div>'
              f'<p class="pa-error" hidden>Audio unavailable right now, please try again later.</p>'
              f'<div class="media-caption"><span>{e(r["episode"])} &middot; {e(r["code"])} &middot; production sound</span><span>{clock(total)}</span></div></div>')
    rows = []
    for t, label, text, whole in r["marks"]:
        x = f'<b>{e(AIRED)}</b> <em>{e(DROPPED)}</em>' if whole else e(text)
        rows.append(f'<li><button type="button" data-seek="{t}"><span class="t">{clock(t)}</span><span class="l">{e(label)}</span><span class="x">{x}</span></button></li>')
    facts = []
    for head, text, links in r["facts"]:
        buttons = "".join(f'<a class="pa-link" href="{href}">{e(label)} &rarr;</a>' for label, href in links)
        facts.append(f'<div class="pa-fact"><h3>{e(head)}</h3><p>{e(text)}</p>{buttons}</div>')
    more = "".join(f'<a class="pa-link" href="{href}">{e(label)} &rarr;</a>' for label, href in r["more"])
    body = (f'<section class="archive-hero"><div class="shell"><div class="crumb"><a href="/memorabilia/">Memorabilia</a> &nbsp;/&nbsp; {e(r["episode"])}</div>'
            f'<h1>{e(r["title"])}</h1><p>{e(r["episode"])} &middot; {e(r["code"])} &middot; {e(r["lede"])}</p>'
            f'<div class="archive-meta"><span>{clock(total)}</span><span>{takes} takes</span><span>Production sound</span></div></div></section>'
            f'<div class="shell detail-wrap"><div class="pa">'
            + "".join(f'<p class="detail-copy" style="margin-bottom:22px">{e(p)}</p>' for p in r["intro"])
            + f'<div style="margin-top:40px">{player}</div>'
            f'<h2>On the recording</h2><ol class="pa-marks">{"".join(rows)}</ol>'
            f'<h2>In the episode</h2><div class="pa-facts">{"".join(facts)}</div><div class="pa-more">{more}</div>'
            f'</div></div>{PLAYER_JS}')
    description = f'{r["title"]}: raw production sound from The X-Files episode {r["episode"]} ({r["code"]}). {r["lede"]}'
    write_route(f"misc-memorabilia/{slug}", page(f'{r["title"]} ({r["episode"]})', description, body))
    print(f"Built production sound: {r['title']} ({clock(total)})", flush=True)


def main() -> None:
    keys = r2_keys()
    missing = [r["key"] for r in RECORDINGS.values() if r["key"] not in keys]
    if missing: raise SystemExit("MISSING on R2 under production-audio/: " + "; ".join(missing))
    for slug, r in RECORDINGS.items():
        still = DIST / "assets" / "production-audio" / f"{slug}.jpg"
        if not still.exists(): raise SystemExit(f"still missing: {still}")
        detail(slug, r)


if __name__ == "__main__":
    main()
