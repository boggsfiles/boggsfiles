#!/usr/bin/env python3
"""Build dist/misc-memorabilia/x-files-location-scouts/index.html.

Source scans live in tools/location-scouts/<NN-slug>/ (see its README.md for
the identification notes); page images are the WebPs in
dist/assets/archive-photos/location-scouts/ (<NN-slug>-<page>.webp and
-thumb.webp). Edit FOLDERS below and re-run.
"""
import glob, html, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
IMG = '/assets/archive-photos/location-scouts'
OUT = os.path.join(DIST, 'misc-memorabilia', 'x-files-location-scouts', 'index.html')

# status: confirmed | inferred | unknown | library
TIERS = [
    ('proof', 'The one with proof',
     'Only one folder ties itself to an episode without any guessing — and it shows the decision being made.'),
    ('scene', 'Scene scouts',
     'Handwritten labels are scene slugs or street names. The place is certain; the episode is not, unless marked.'),
    ('survey', 'Stage surveys, summer 1998',
     'Three rental lots photographed gate-first — guard shacks, main drives, offices — which is how you look at a lot when you are deciding where to base a show. That is what The X-Files was doing the summer it moved from Vancouver. It ended up at Fox. These are the roads not taken.'),
    ('library', 'From the location library',
     'The seller of these folders got them from, in their words, "the person who did set location work for the show and many others." These are the "many others": folders with no scene label, no frame match, or a date outside the show\'s Los Angeles years. They came in the same box, so they are here — marked.'),
]

FOLDERS = [
    dict(slug='09-norton-afb', tier='proof', tab='Norton AFB "Gates"', sub='Gate 3 · Gate 5 · Gate 7 · Mill St Gate · Reverse',
         place='Former Norton Air Force Base, San Bernardino', loc='confirmed', ep='confirmed', episode='Closure (7X11)',
         note='A gate-by-gate survey of the closed base. A yellow Post-it on the Gate 5 flight-line panorama reads <b>"THIS GATE ⇒"</b>: that is the fence Mulder stands at looking into "April Air Force Base." The last page pairs the scout print with the frame. Bare trees and low winter sun agree with a January 2000 scout.',
         hero=10, captions={10: 'Gate 5 — the Post-it', 22: 'Scout print over the frame from "Closure"'}),

    dict(slug='04-bridge', tier='scene', tab='Bridge', place='Malibou Lake entrance bridge, Lake Vista Dr at Mulholland Hwy, Agoura Hills',
         loc='confirmed', ep='unknown',
         note='The stone gate posts at the far end of the panorama read <b>"Malibou Lake."</b> The obvious candidate — the car-off-a-bridge teaser of "Nothing Important Happened Today" — was checked against the frames and ruled out: that bridge is a harbor lift span, not this one.', hero=1),
    dict(slug='03-harbor-building', tier='scene', tab='Harbor Bldg. Los Angeles', sub='N/W exposure',
         place='Harbor (Tidewater Oil) Building, 4201 Wilshire Blvd at Crenshaw', loc='confirmed', ep='unknown',
         note='Claud Beelman, 1958; a Los Angeles Historic-Cultural Monument, still standing. No X-Files credit exists for the address in any public database — possibly scouted and not used.', hero=1),
    dict(slug='02-lindsey-studios', tier='scene', tab='Lindsey Studios', sub='Apt. facade · Courtroom & corridors',
         place='Standing sets on a rental soundstage', loc='inferred', ep='unknown',
         note='The stage ceiling is visible above the courtroom walls — these are sets, not a courthouse. "Redrum," the one Los Angeles-era story built around a courtroom, was checked against the frames and ruled out: its arraignment is in a real courtroom with tall arched windows.', hero=2),
    dict(slug='06-ocean-long-beach', tier='scene', tab='Ocean – Long Beach', sub='#3 P.M.',
         place='Ocean Blvd between Pine Ave and Locust Ave, downtown Long Beach', loc='confirmed', ep='unknown',
         note='The Renaissance hotel sign, "211 E. Ocean," The Breakers, and the Locust and Pine Square street signs are all readable. Two close-ups of a car hood and mirror with the street soft behind are camera-mount tests: a scout for a daytime driving shot, timed to the light.', hero=1,
         captions={4: 'Car-mount angle tests'}),
    dict(slug='12-greyhound-downtown', tier='scene', tab='Grey Hound Bus Terminal – Downtown',
         place='Greyhound Los Angeles terminal, 1716 E. 7th St at Alameda', loc='confirmed', ep='unknown',
         note='The "1716" on the wall is the address. The station closed in 2023.', hero=3),
    dict(slug='14-media-center-burbank', tier='scene', tab='Media Center Burbank CA', sub='Noon',
         place='Downtown Burbank — Media City Center (now Burbank Town Center), IKEA, San Fernando Blvd &amp; First St',
         loc='confirmed', ep='unknown',
         note='About forty prints of the shopping district in hard midday light. "Noon" on the tab is a light note, like Long Beach\'s "3 P.M."', hero=3),
    dict(slug='01-warehouse', tier='scene', tab='Wearhouse', sub='sic',
         place='Unidentified agricultural warehouse, probably Ventura County', loc='unknown', ep='unknown',
         note='Orchard trees, a cracked lot, flat farmland with low hills — a grain-and-bean elevator or packing plant. Reverse image search found nothing; the building may be gone. <b>If you know this building, we want to hear from you.</b>', hero=3),

    dict(slug='05-warner-hollywood', tier='survey', tab='Warner Hollywood Studios', sub='typed label',
         place='The Lot at Formosa, 1041 N. Formosa Ave, West Hollywood', loc='confirmed', ep='none',
         note='The old Pickford-Fairbanks / Goldwyn lot. The sign on the wall dates the visit to before the 1999 sale and rename to "The Lot"; the crape myrtle by the gate is in summer bloom.', hero=1),
    dict(slug='07-sunset-gower', tier='survey', tab='Sunset Gower Studios', sub='typed label',
         place='Sunset Gower Studios, 1438 N. Gower St, Hollywood', loc='confirmed', ep='none',
         note='The old Columbia lot; Ocean Way Recording is in frame across the street. Same gate-and-guard-shack coverage as Warner Hollywood.', hero=1),
    dict(slug='08-ren-mar', tier='survey', tab='Ren Mar Studios',
         place='Ren-Mar Studios, 846 N. Cahuenga Blvd, Hollywood (now Red Studios)', loc='confirmed', ep='none',
         note='The thorough one: about thirty prints, including office suites, dressing rooms, and a dressing-room bath. Whoever shot this was picturing their cast using it. The old Desilu lot.', hero=1),

    dict(slug='10-sierra-madre', tier='library', tab='Sierra Madre', sub='one tab: "Towns · Baldwin Ave &amp; Orange Grove · 1/26/95 · 3:30–5:00 PM"',
         place='Downtown Sierra Madre — Old North Church, Baldwin Ave storefronts, a hair salon', loc='confirmed', ep='library',
         note='The tab is dated <b>January 1995</b>, when the show was still shooting in Vancouver — so this folder belongs to one of the other productions in the same library. Includes a blank Twentieth Century Fox Television parking-license form.', hero=5),
    dict(slug='11-unlabeled', tier='library', tab='(unlabeled)',
         place='A studio backlot alley set, dressed and lit — plus a second copy of the Warehouse panorama', loc='inferred', ep='library',
         note='Thin brick façade panels, taped floor marks, a lamp on a stand, a "New York Street" through the arch. Which lot is not readable from the frames.', hero=3),
    dict(slug='13-unlabeled-2', tier='library', tab='(unlabeled 2)',
         place='Southern California ranch country — Simi Hills / Ventura County terrain', loc='unknown', ep='library',
         note='Not the Arizona desert: dry grass, chaparral and pale sandstone rather than saguaro and red rock. No signage or structure to pin a ranch.', hero=2),
]

CHIP = {
    'confirmed': ('scout-ok', 'Confirmed'),
    'inferred': ('scout-inf', 'Inferred'),
    'unknown': ('scout-no', 'Unknown'),
    'library': ('scout-lib', 'Library'),
}

HEAD = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>X-Files Location Scouts: Boggsfiles</title><meta name="description" content="Fourteen location-scout folders from the Los Angeles years of The X-Files, scanned by Jeremy Royer, with every location identified."><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Libre+Caslon+Display&family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet"><link rel="stylesheet" href="/assets/archive-detail.css"><link rel="stylesheet" href="/assets/site-header.css?v=3"><script src="/assets/site-header.js" defer></script></head><body><header class="bf-header"><div class="bf-inner"><a class="bf-brand" href="/" aria-label="Boggsfiles home">BOGGS<span class="bf-brand-x">X</span>FILES</a><nav class="bf-navlinks" id="bf-primary-navigation" aria-label="Primary"><a href="/archive/">Archive</a><a href="/scripts/">Scripts</a><a href="/transcripts/">Transcripts</a><a href="/screencaps/">Screencaps</a><a href="/script-vs-screen/">Script vs. Screen</a><a href="/dailies/">Dailies</a><a href="/gag-reels/">Gag Reels</a><a href="/memorabilia/" aria-current="page">Memorabilia</a><a href="/resources/">Resources</a></nav><button class="bf-menu" type="button" aria-label="Open navigation" aria-controls="bf-primary-navigation" aria-expanded="false">☰</button></div></header><main>'''

FOOT = '''</main><footer><div class="shell footer-row">BOGGSFILES · MEMORABILIA ARCHIVE <span><a href="/">Home</a> · The truth still matters</span></div></footer></body></html>'''


def pages(slug):
    files = sorted(glob.glob(os.path.join(DIST, IMG.lstrip('/'), f'{slug}-[0-9][0-9].webp')))
    return [os.path.basename(f)[:-5] for f in files]


def folder_html(f, idx):
    pg = pages(f['slug'])
    n = len(pg)
    hero = f'{f["slug"]}-{f.get("hero", 1):02d}'
    loc_cls, loc_txt = CHIP[f['loc']]
    ep = f['ep']
    chips = f'<span class="scout-k">Location</span><span class="scout-chip {loc_cls}">{loc_txt}</span>'
    if ep in CHIP:
        c, t = CHIP[ep]
        chips += f'<span class="scout-k">{"X-Files?" if ep == "library" else "Episode"}</span><span class="scout-chip {c}">{t}</span>'
        if f.get('episode'):
            chips += f'<span class="scout-ep">{html.escape(f["episode"])}</span>'
    sub = f'<small>{f["sub"]}</small>' if f.get('sub') else ''
    caps = f.get('captions', {})
    thumbs = ''.join(
        f'<a class="scout-page" href="{IMG}/{p}.webp" target="_blank" rel="noopener" aria-label="Open page {i + 1} of {f["tab"]}">'
        f'<img src="{IMG}/{p}-thumb.webp" loading="lazy" alt="{html.escape(f["tab"])}, page {i + 1}">'
        f'<span>{i + 1:02d}{(" · " + html.escape(caps[i + 1])) if (i + 1) in caps else ""}</span></a>'
        for i, p in enumerate(pg))
    return (f'<article class="scout" id="{f["slug"]}">'
            f'<a class="scout-hero" href="{IMG}/{hero}.webp" target="_blank" rel="noopener"><img src="{IMG}/{hero}.webp" loading="lazy" alt="{html.escape(f["place"])}"></a>'
            f'<div class="scout-body"><div class="scout-tab">Folder {f["slug"][:2]} · {html.escape(f["tab"])} {sub}</div>'
            f'<h3>{f["place"]}</h3><div class="scout-row">{chips}</div><p>{f["note"]}</p>'
            f'<details class="scout-pages"><summary>All {n} page{"s" if n != 1 else ""}</summary><div class="scout-grid">{thumbs}</div></details>'
            f'</div></article>')


def build():
    total = sum(len(pages(f['slug'])) for f in FOLDERS)
    confirmed = sum(1 for f in FOLDERS if f['loc'] == 'confirmed')
    body = [HEAD,
            '<section class="archive-hero"><div class="shell"><div class="crumb"><a href="/memorabilia/">Memorabilia</a> &nbsp;/&nbsp; X-Files Location Scouts</div>',
            '<h1>Location Scouts</h1>',
            '<p>Fourteen manila folders from the location department of the Los Angeles years — taped-together panoramas, handwritten tabs, one Post-it that made a decision. Every place is identified from what is readable in the scans. Episodes are claimed only where the folder itself proves it.</p>',
            f'<div class="archive-meta"><span>{len(FOLDERS)} folders</span><span>{total} scanned pages</span><span>{confirmed} locations pinned</span><span>Seasons 6–9, 1998–2002</span></div>'
            '<p class="scout-credit">Scans and original folders courtesy of <b>Jeremy Royer</b> · <a href="https://www.instagram.com/unknownparish/" target="_blank" rel="noopener">@unknownparish</a></p></div></section>',
            '<div class="shell detail-wrap">',
            '<p class="detail-copy">Location scouts are how a show finds the world it films in. A location manager drives out, shoots a roll of 4×6 prints, tapes the overlapping ones into panoramas on a folder, and writes the scene name on the tab: "Bridge," "Wearhouse," "Ocean – Long Beach, 3 P.M." Most of what gets scouted is never used, which is what makes these folders rare — they record the choosing, not just the choice. These fourteen came from a single sale; the seller got them from the person who did set location work for the show and many others, which is why a few of them belong to other productions. Scanned and shared by <a href="https://www.instagram.com/unknownparish/" target="_blank" rel="noopener">Jeremy Royer (@unknownparish)</a>, who bought the folders intact and scanned all ninety-one pages.</p>',
            '<div class="scout-legend"><span><i class="scout-chip scout-ok">Confirmed</i> readable in the scan or matched to a frame</span><span><i class="scout-chip scout-inf">Inferred</i> best fit, not proven</span><span><i class="scout-chip scout-no">Unknown</i> nothing to go on</span><span><i class="scout-chip scout-lib">Library</i> likely from another production</span></div>']
    for key, title, blurb in TIERS:
        group = [f for f in FOLDERS if f['tier'] == key]
        body.append(f'<section class="scout-tier"><div class="schedule-season-head"><h2>{title}</h2><span>{len(group)} folder{"s" if len(group) != 1 else ""}</span></div><p class="scout-blurb">{blurb}</p>')
        body.extend(folder_html(f, i) for i, f in enumerate(group))
        body.append('</section>')
    body.append('<div class="notice"><strong>Recognize the warehouse?</strong><p>Folder 01 is the one location nobody has placed. If you know the building — or you have a Los Angeles-era call sheet, which lists every location with its address — it would close the file.</p><a class="button" href="/contribute/">Contribute →</a></div>')
    body.append('</div>')
    body.append(FOOT)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as fh:
        fh.write(''.join(body))
    print(f'wrote {os.path.relpath(OUT, ROOT)}: {len(FOLDERS)} folders, {total} pages')


if __name__ == '__main__':
    build()
