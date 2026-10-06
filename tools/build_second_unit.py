#!/usr/bin/env python3
"""Build dist/misc-memorabilia/second-unit-schedules/index.html.

Source PDFs live in iCloud at "X-Files Scripts/2nd Unit & Production Schedules" (25 documents,
75 pages; 21 consolidated 2026-09-28, the two Je Souhaite files split out of one packet 2026-10-03). Page images are written to
dist/assets/archive-photos/second-unit/ as <slug>-<page>.webp plus -thumb.webp, the same way the
Location Scouts section works, so the pages are browsable on the site without a Drive round trip.

Revision colors are taken from what each memo says about itself, never from measuring the scan:
production "salmon" photographs pink and "goldenrod" photographs orange, so measurement disagrees
with the documents. Where a document does not name its own color, none is claimed.

Re-run after adding PDFs. Existing webps are left alone.
"""
import html, os, re, subprocess, tempfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SRC = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/X-Files Scripts/2nd Unit & Production Schedules"
IMG = "/assets/archive-photos/second-unit"
IMGDIR = DIST / IMG.lstrip("/")
OUT = DIST / "misc-memorabilia" / "second-unit-schedules" / "index.html"

# pdf stem, slug, color the document names for itself, date, from, memo no, what it covers
DOCS = [
 # --- Season 5 second unit, in the order they were issued -------------------
 dict(g="unit", pdf="2nd Unit Redux I, Redux II", slug="01-redux",
      color="Salmon", date="Friday, September 12, 1997", who="Kevin Parks", memo="2NDU-5X02-04",
      title="Redux I & Redux II", note="The earliest memo in the set. Second unit schedule for the two-part season opener."),
 dict(g="unit", pdf="2nd Unit Detour Memo + Schedule (Green) 10-10-97", slug="02-detour-memo",
      color="Green", date="October 10, 1997", who="2nd Unit", memo=None,
      title="Detour, days 11 and 12",
      note="A memo on green stock with the schedule attached, copied to B. Goodwin, J.P. Finn, R. French and B. Dowler. The only document here on X-F Productions letterhead."),
 dict(g="unit", pdf="2nd Unit Detour, Christmas Carol Salmon", slug="03-detour-xmas",
      color="3rd Salmon", date="Friday, October 17, 1997", who="Kevin Parks", memo="2NDU-5X02-08",
      title="Detour & Christmas Carol", note="Headed “3rd Salmon”, so the schedule had already been revised onto salmon stock twice before this one."),
 dict(g="unit", pdf="2nd Unit Detour", slug="04-detour-pickups",
      color="Goldenrod", date="Tuesday, October 28, 1997", who="Brett Dowler", memo="2NDU-5X05-03",
      title="Detour pickups and inserts", note="An updated schedule of pickups and inserts for 5X04."),
 dict(g="unit", pdf="2nd Unit Detour, Chrismas Carol, Emily Yellow", slug="05-three-yellow",
      color="Yellow", date="Friday, October 31, 1997", who="Brett Dowler", memo="2NDU-5X05-06",
      title="Detour, Christmas Carol & Emily", note="Three episodes running at once on one second unit."),
 dict(g="unit", pdf="2nd Unit Post Modern Prometheus", slug="06-prometheus",
      color=None, date="Friday, October 31, 1997", who="Kevin Parks", memo="2NDU-5X06",
      title="The Post-Modern Prometheus", note="Issued the same day as the memo above, by the other assistant director. Includes the company move to 2659 Oxford Street for the Berkowitz house."),
 dict(g="unit", pdf="2nd Unit Detour, Chrismas Carol, Emily Goldenrod", slug="07-three-goldenrod",
      color="Goldenrod", date="Tuesday, November 4, 1997", who="Brett Dowler", memo="2NDU-5X06-1",
      title="Detour, Christmas Carol & Emily",
      note="Notes that 5X05 pickups and reshoots are “yet to be fully scheduled”. The longest document in the set at four pages."),
 dict(g="unit", pdf="2nd Unit Detour, Chrismas Carol, Emily", slug="08-three-salmon",
      color="Salmon", date="Wednesday, November 5, 1997", who="Brett Dowler", memo="2NDU-5X06-2",
      title="Detour, Christmas Carol & Emily",
      note="Issued the next day, already revised. Christmas Carol pickups move to 3106 Alberta Street, the Scully family house."),
 dict(g="unit", pdf="2nd Unit Christmas Carol, Kitsunegari, Schizogeny", slug="09-kitsunegari",
      color="Green", date="Tuesday, November 19, 1997", who="Kevin Parks", memo="2NDU-5X07-3",
      title="Christmas Carol, Kitsunegari & Schizogeny", note="A revised schedule covering three episodes."),
 dict(g="unit", pdf="2nd Unit Emily Memo + Insert List (Green) 11-25-97", slug="10-emily-inserts",
      color="Green", date="Tuesday, November 25, 1997", who="Kevin Parks", memo="5X07-INSERTS",
      title="Emily, remaining inserts",
      note="A memo plus the attached insert list, signed “Kevin”. Notes that 5X05 and 5X06 are complete. The inserts are Scully's hand lifting the cross from the sand, her feet in the sand, and Mulder's POV of the cross."),
 dict(g="unit", pdf="2nd Unit Kill Switch Goldenrod", slug="11-kill-switch",
      color="Goldenrod", date="Wednesday, January 14, 1998", who="Kevin Parks", memo="2NDU-5X10-3",
      title="Kill Switch", note="Back after the Christmas hiatus."),
 dict(g="unit", pdf="2nd Unit Chinga, Kill Switch", slug="12-chinga",
      color="Salmon", date="Friday, January 16, 1998", who="Brett Dowler", memo="2NDU-5X11-1",
      title="Chinga & Kill Switch", note="Kill Switch day 12 shoots at the Park Canada RV lot on Nulelum Way, directed by Rob Bowman."),
 dict(g="unit", pdf="2nd Unit Mind's Eye, Travelers, All Souls Yellow", slug="13-minds-eye-yellow",
      color="Yellow", date="Wednesday, March 18, 1998", who="Brett Dowler", memo="2NDU-5X16-1",
      title="Mind's Eye, Travelers & All Souls", note=None),
 dict(g="unit", pdf="2nd Unit Mind's Eye, Travelers, All Souls Goldenrod", slug="14-minds-eye-gold",
      color="Goldenrod", date="Friday, March 20, 1998", who="Brett Dowler", memo="2NDU-5X16-2",
      title="Mind's Eye, Travelers & All Souls",
      note="Two days later, with an updated list of the inserts still outstanding. The last second unit memo in the set."),

 # --- insert lists ----------------------------------------------------------
 dict(g="inserts", pdf="Christmas Carol Insert", slug="15-xmas-inserts",
      color=None, date="Tuesday, November 4, 1997", who=None, memo="5X05",
      title="Christmas Carol, pickups and inserts",
      note="Page two of the pickup and insert list, on goldenrod. Almost every line is a point of "
           "view: Scully comparing photographs, a hypodermic needle with blood in a baggy, two PCR "
           "sheets held to the light, the crucifix in the jewellery box. The header carries a typo "
           "that nobody caught, CHISTMAS CAROL, and the shoot day line reads November 1999 on a "
           "sheet dated November 1997."),
 dict(g="inserts", pdf="Post Modern Prometheus Insert", slug="16-pmp-inserts",
      color=None, date="Undated", who=None, memo="5X06",
      title="The Post-Modern Prometheus, preliminary inserts",
      note="The script supervisor's own list, <b>written out by hand in pen</b> on a blank form. "
           "Inserts are the close ups the main unit still owes, and this is somebody tracking what "
           "is outstanding as the day goes. Scene 60, in the cellar, reads as a shopping list: CS "
           "SANDWICH ON PLATE, CS GOAT, CS HORSE, CS ROOSTER, CS PIG, CS WINDOWS GET SMASHED. Scene "
           "1 is CU GOAT BOY LKS INTO CAR. The circled M and S mark whose eyeline each shot has to "
           "match, so Mulder and Scully are being tracked shot by shot. The last line on the page "
           "is TV PLAYING JERRY SPRINGER."),

 # --- season-wide schedules -------------------------------------------------
 dict(g="season", pdf="Director's Schedule 5th Season Pink", slug="20-directors-pink",
      color="Pink", date="Revised August 20, 1997", who=None, memo=None,
      title="Fifth Season Directors Schedule",
      note="The whole season on one page: show number, writer, director, prep, start and wrap. Episodes 1 and 2 are typed. Episodes 3 and 4 have their titles <b>written in by hand in blue pen</b>, Redux II and Detour, because they had not been named when this was typed. From episode 5 on, the title column is simply empty: directors and dates assigned to episodes that did not exist yet. The sheet heads itself <b>DIRECTORS SCHEDULE</b>, with no apostrophe, and the title here follows the paper."),
 dict(g="season", pdf="Director's Schedule 5th Season Salmon", slug="21-directors-salmon",
      color="Salmon", date="Revised November 14, 1997", who=None, memo=None,
      title="Fifth Season Directors Schedule",
      note="The same document three months later. Worth reading against the Pink: the blanks have started to fill in. Headed <b>DIRECTORS SCHEDULE</b> with no apostrophe, like the Pink."),
 dict(g="season", pdf="Production Schedule Season 8 Goldenrod", slug="22-s8-goldenrod",
      color="Goldenrod", date="Season 8", who=None, memo=None,
      title="Season Eight Production Schedule",
      note="Three pages on 20th Century Fox letterhead: episode number, writer, editor, prep and shoot dates, director and air date, straight through the season, holidays and pre-empted weeks included."),
 dict(g="season", pdf="Production Schedule Season 8 Yellow", slug="23-s8-yellow",
      color="Yellow", date="August 15, 2000", who=None, memo=None,
      title="Season Eight Production Schedule", note="The dated revision of the same schedule."),

 # --- calendars and scouts --------------------------------------------------
 dict(g="prep", pdf="Prep Calendar November 2000", slug="30-prep-nov-2000",
      color="Pink", date="November 2000", who=None, memo="8ABX12",
      title="Prep Calendar, November 2000",
      note="A month laid out as a wall calendar, timed to the minute and marked “as of 7:20 PM”. Set decoration meetings, an underwater photography meeting, a location scout, wardrobe, the start of principal photography, and Thanksgiving."),
 dict(g="prep", pdf="Season 8 Prep Calendar", slug="31-prep-jan-2001",
      color="White", date="January 2001", who=None, memo="8ABX16",
      title="Prep Calendar, January 2001",
      note="Location scout, VFX/SFX/stunt scout of an oil platform, prop meeting, second unit mini scout, casting calls."),
 dict(g="prep", pdf="Surekill Tech Scout Only ", slug="32-surekill-scout",
      color=None, date="Tentative, Thursday October 19, 2000", who=None, memo="8ABX09",
      title="Surekill tech scout",
      note="Headed 8ABX09 “UNTITLED”, before the episode had its name. Under the date it notes that Stage 5 is in use by 8ABX08 and, plainly, that <b>Scully and Doggett are not available</b>. The location list runs down the day scene by scene, with the Herald Examiner building standing in for a Worcester bus station."),
 # --- Je Souhaite, Season 7 -------------------------------------------------
 dict(g="je21", pdf="7ABX21 Je Souhaite Director's Plans", slug="40-je-souhaite-plans",
      color=None, date="April 6, 2000", who="Corey Kaplan and Lauren Polizzi", memo="7ABX21",
      title="Je Souhaite, director's plans",
      note="An art department memo and the fourteen set drawings that answer it, for production "
           "designer Corey Kaplan, drawn by J. Bruce, Harbour and RH/JB. The memo is headed "
           "<b>&ldquo;Untitled&rdquo;</b>: four days before the first day of shooting, Je Souhaite "
           "still had no name. The sets run from the Avalon Carson trailer park and the mobile home "
           "interior on Stage 5 to the U-Stor-It on Pacific Coast Highway, the Elysee Cafe standing "
           "in for the diner, 5th and Spring downtown, the county morgue, Mulder's apartment, "
           "Skinner's office and Mulder's office. Each sheet carries its own scale, and the mobile "
           "home drawing is annotated <b>BOAT NOT ON STAGE. KICKER WALLS TO BE USED.</b>"),
 dict(g="je21", pdf="7ABX21 Je Souhaite Effects Crew Working File", slug="41-je-souhaite-effects",
      color=None, date="April 2000", who=None, memo="7ABX21",
      title="Je Souhaite, effects crew working file",
      note="Bound into the back of the same file, and not an art department document at all. Two "
           "pre-production calendars on green and pink stock, the April 6 tech scout itinerary, a "
           "yellow revised schedule, a pink production meeting pass, a handwritten crew call and the "
           "green final shooting schedule. What ties them together is the handwriting, and the "
           "handwriting belongs to somebody in effects. Beside each stop on the scout is what that "
           "stop needs: <b>2 cobweb guns, dust gun, water truck</b> at the storage facility, "
           "<b>water splash, car hood, car body</b> on Suburban Road, and a flat <b>NOTHING</b> "
           "beside the diner and the city street. The handwritten page is a truck load-out &mdash; "
           "cob webbers, air hoses, a dust gun, a bucket of Fuller's earth, an air compressor, a "
           "mole fogger. The schedule margins keep the day's gags in a running list: <b>trailer "
           "explodes, car window blow, debris fall, rug falls</b>, and later <b>stove knob breaks, "
           "rear panel removes, fire bar, helium heat wave</b>. The same crew is assigned day by day "
           "across every page &mdash; Rick, Lee, Eric, Jeff, Jeff, Ron, Randy. Beside one circled "
           "scene somebody has written <b>DID WE GET THAT?!!</b> Four phone numbers on the tech "
           "scout page are blurred in this scan."),
]

GROUPS = [
 ("unit", "Second unit, Season 5",
  "Fourteen memos issued between September 1997 and March 1998 by the two second unit assistant "
  "directors, Kevin Parks and Brett Dowler. Second unit shoots the pieces the main unit cannot: "
  "inserts, pickups, hands, feet, plates, reshoots. Each memo goes to all departments, on whatever "
  "color the revision had reached that week."),
 ("inserts", "Insert lists",
  "Inserts are the close ups the main unit still owes: the hands, the objects, the things an edit "
  "cuts to. Somebody has to keep track of which ones are outstanding. Two of those lists survived, "
  "and one of them is handwritten."),
 ("season", "Season schedules",
  "Four documents that plan a whole season at once, two from Season 5 and two from Season 8."),
 ("prep", "Prep calendars and scouts",
  "What a production week actually looks like when it is written down."),
 ("je21", "Je Souhaite, Season 7",
  "Two documents from one episode, 7ABX21, written and directed by Vince Gilligan and shot through "
  "April 2000. They arrived bound into a single file and are separated here, because they were kept "
  "by two different people. The first belonged to the art department. The second belonged to "
  "somebody in effects, and it is the more interesting of the two."),
]

HEAD = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>2nd Unit &amp; Production Schedules: Boggsfiles</title><meta name="description" content="Twenty-five documents from inside The X-Files production office: second unit memos, insert lists, season schedules, prep calendars and a Season 7 director&#39;s plans packet, scanned in full color on their original revision stock."><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Libre+Caslon+Display&family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet"><link rel="stylesheet" href="/assets/archive-detail.css?v=4"><link rel="stylesheet" href="/assets/site-header.css?v=3"><script src="/assets/site-header.js" defer></script></head><body><header class="bf-header"><div class="bf-inner"><a class="bf-brand" href="/" aria-label="Boggsfiles home">BOGGS<span class="bf-brand-x">X</span>FILES</a><nav class="bf-navlinks" id="bf-primary-navigation" aria-label="Primary"><a href="/archive/">Archive</a><a href="/scripts/">Scripts</a><a href="/transcripts/">Transcripts</a><a href="/screencaps/">Screencaps</a><a href="/script-vs-screen/">Script vs. Screen</a><a href="/dailies/">Dailies</a><a href="/gag-reels/">Gag Reels</a><a href="/locations/">Locations</a><a href="/memorabilia/" aria-current="page">Memorabilia</a><a href="/resources/">Resources</a></nav><button class="bf-menu" type="button" aria-label="Open navigation" aria-controls="bf-primary-navigation" aria-expanded="false">☰</button></div></header><main>'''
JUMP = """<script>
/* Every document id starts with a digit, and the page sets scroll-behavior:smooth, so the
   browser's own fragment jump gets cancelled by images settling and never lands. Do it
   explicitly and instantly, on load as well as on hashchange, so a contents link and a shared
   link both arrive in the right place. The offset is read from scroll-margin-top. */
(function () {
  function jump() {
    var h = location.hash.slice(1); if (!h) return;
    var el = document.getElementById(h); if (!el) return;
    var top = el.getBoundingClientRect().top + window.pageYOffset
            - (parseFloat(getComputedStyle(el).scrollMarginTop) || 0);
    var root = document.documentElement, prev = root.style.scrollBehavior;
    root.style.scrollBehavior = 'auto';
    window.scrollTo(0, Math.max(0, top));
    root.style.scrollBehavior = prev;
  }
  addEventListener('hashchange', jump);
  /* On a cold load the target moves as images settle, and the scroll can be reset from under
     us, so re-assert it a few times before giving up. */
  addEventListener('load', function () {
    requestAnimationFrame(jump);
    [60, 200, 600, 1200].forEach(function (ms) { setTimeout(jump, ms); });
  });
})();
</script>"""

FOOT = '''</main><footer><div class="shell footer-row">BOGGSFILES · PRODUCTION DOCUMENTS <span><a href="/">Home</a> · <a href="/production-documents/">All production documents</a></span></div></footer></body></html>'''

CSS_EXTRA = '''<style>
.su-swatch{display:inline-block;width:.68em;height:.68em;border-radius:50%;margin-right:.45em;vertical-align:-1px;border:1px solid rgba(0,0,0,.35)}
/* 25 documents at a full-page hero each ran to 21 screens. The hero is cropped to a square
   on its top edge, which is where a document identifies itself, and the index below the
   masthead jumps straight to a section. Scoped here so Location Scouts is unaffected. */
/* a global nav{display:flex} would otherwise turn these sections into flex items */
.su-index{display:block;margin:0 0 6px;padding:4px 0 10px}
.su-index section{display:grid;grid-template-columns:168px minmax(0,1fr);gap:10px 24px;
  padding:13px 0;border-top:1px solid var(--line)}
.su-index section:first-child{border-top:0}
.su-index h4{margin:0;font:400 .6rem/1.5 var(--mono);letter-spacing:.13em;text-transform:uppercase;color:#737d76}
.su-index h4 i{font-style:normal;color:#4e564f;margin-right:5px}
.su-index div{display:flex;flex-wrap:wrap;gap:5px 22px}
.su-index a{color:#c9cfca;text-decoration:none;font-size:.82rem;line-height:1.35}
.su-index a:hover,.su-index a:focus-visible{color:var(--red)}
.su-index a u{text-decoration:none;color:#6c756e;font:400 .56rem/1 var(--mono);
  letter-spacing:.1em;text-transform:uppercase;margin-left:6px}
@media (max-width:640px){.su-index section{grid-template-columns:minmax(0,1fr);gap:7px}}
.scout-tier,.detail-wrap .scout{scroll-margin-top:92px}
.detail-wrap .scout{grid-template-columns:minmax(0,3fr) minmax(0,9fr);gap:24px;margin-top:28px;padding-top:28px;align-items:start}
/* 3/4 is the page proportion of these scans, and contain keeps the document whole: a square
   cover crop cut the bottom off every title page. */
.detail-wrap .scout-hero img{aspect-ratio:3/4;object-fit:contain}
.detail-wrap .scout-tier{margin-top:52px;margin-bottom:52px}
@media (max-width:700px){
  .detail-wrap .scout{grid-template-columns:minmax(0,1fr)}
}
</style>'''

SWATCH = {"Pink": "#f6a8bc", "Salmon": "#f6b48c", "3rd Salmon": "#f6b48c", "Goldenrod": "#efc04a",
          "Yellow": "#f2ec72", "Green": "#a6e2ae", "White": "#f2f1ea"}


def render():
    """PDF pages -> webp, full and thumb. Skips anything already rendered."""
    IMGDIR.mkdir(parents=True, exist_ok=True)
    made = 0
    for d in DOCS:
        pdf = SRC / f"{d['pdf']}.pdf"
        if not pdf.exists():
            raise SystemExit(f"missing source PDF: {pdf}")
        n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(
            ["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
        d["pages"] = n
        if all((IMGDIR / f"{d['slug']}-{i:02d}.webp").exists() for i in range(1, n + 1)):
            continue
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["pdftoppm", "-r", "200", "-jpeg", "-jpegopt", "quality=92",
                            str(pdf), f"{td}/p"], check=True)
            for i, src in enumerate(sorted(Path(td).glob("p*.jpg")), 1):
                im = Image.open(src).convert("RGB")
                full = im.copy(); full.thumbnail((1500, 1500), Image.LANCZOS)
                full.save(IMGDIR / f"{d['slug']}-{i:02d}.webp", "WEBP", quality=82, method=6)
                th = im.copy(); th.thumbnail((430, 430), Image.LANCZOS)
                th.save(IMGDIR / f"{d['slug']}-{i:02d}-thumb.webp", "WEBP", quality=78, method=6)
                made += 1
    print(f"  rendered {made} new page images")


def doc_html(d):
    n = d["pages"]
    meta = []
    if d["color"]:
        meta.append(f'<span class="su-rev"><i class="su-swatch" style="background:{SWATCH[d["color"]]}"></i>{d["color"]}</span>')
    meta.append(html.escape(d["date"]))
    if d["who"]:  meta.append("from " + html.escape(d["who"]))
    if d["memo"]: meta.append(html.escape(d["memo"]))
    meta.append(f'{n} page{"s" if n != 1 else ""}')
    thumbs = "".join(
        f'<a class="scout-page" href="{IMG}/{d["slug"]}-{i:02d}.webp" target="_blank" rel="noopener" '
        f'aria-label="Open page {i} of {html.escape(d["title"])}">'
        f'<img src="{IMG}/{d["slug"]}-{i:02d}-thumb.webp" loading="lazy" alt="{html.escape(d["title"])}, page {i}">'
        f'<span>{i:02d}</span></a>' for i in range(1, n + 1))
    hero = f'{IMG}/{d["slug"]}-01.webp'
    return (f'<article class="scout" id="{d["slug"]}">'
            f'<a class="scout-hero" href="{hero}" target="_blank" rel="noopener">'
            f'<img src="{hero}" loading="lazy" alt="{html.escape(d["title"])}"></a>'
            f'<div class="scout-body"><div class="scout-tab">{" &nbsp;·&nbsp; ".join(meta)}</div>'
            f'<h3>{html.escape(d["title"])}</h3>'
            + (f'<p>{d["note"]}</p>' if d.get("note") else "")
            + f'<details class="scout-pages"><summary>All {n} page{"s" if n != 1 else ""}</summary>'
              f'<div class="scout-grid">{thumbs}</div></details></div></article>')


def build():
    render()
    total = sum(d["pages"] for d in DOCS)
    body = [HEAD, CSS_EXTRA,
      '<section class="archive-hero"><div class="shell">'
      '<div class="crumb"><a href="/production-documents/">Production Documents</a> &nbsp;/&nbsp; 2nd Unit &amp; Production Schedules</div>'
      '<h1>2nd Unit &amp;<br>Production Schedules</h1>'
      '<p>Twenty-five documents from inside the production office: the memos that told every department '
      'where the second unit would be on Thursday, the schedules that mapped whole seasons before the '
      'episodes had names, and the calendars that counted a month down to the minute.</p>'
      f'<div class="archive-meta"><span>{len(DOCS)} documents</span><span>{total} scanned pages</span>'
      '<span>Seasons 5, 7 and 8</span><span>1997&ndash;2001</span></div></div></section>',
      '<div class="shell detail-wrap">',
      '<p class="detail-copy">Second unit is the part of a production almost nobody keeps paperwork from. '
      'It shoots what the main unit cannot: inserts, pickups, hands and feet, plates, reshoots of a scene '
      'that did not cut together. Somebody has to tell every department where it will be and what it needs, '
      'so an assistant director writes a memo, runs it off on whatever color the revision has reached, and '
      'distributes it. Then it is superseded, usually within days, and thrown away. These survived. '
      'Each one is scanned in full color on its original stock, because the color is the revision.</p>',
      '<nav class="su-index" aria-label="Contents">' + "".join(
          f'<section><h4><i>{len([d for d in DOCS if d["g"] == k])}</i> {html.escape(t)}</h4><div>' +
          "".join(f'<a href="#{d["slug"]}">{html.escape(d["title"])}'
                  + (f'<u>{html.escape(d["color"] or d["date"])}</u>'
                     if sum(1 for x in DOCS if x["title"] == d["title"]) > 1 else '')
                  + '</a>' for d in DOCS if d["g"] == k) + '</div></section>'
          for k, t, _ in GROUPS) + '</nav>']
    for key, title, blurb in GROUPS:
        group = [d for d in DOCS if d["g"] == key]
        body.append(f'<section class="scout-tier" id="s-{key}"><div class="schedule-season-head"><h2>{title}</h2>'
                    f'<span>{len(group)} document{"s" if len(group) != 1 else ""}</span></div>'
                    f'<p class="scout-blurb">{blurb}</p>')
        body.extend(doc_html(d) for d in group)
        body.append('</section>')
    body.append('<div class="notice"><strong>Have more of these?</strong>'
                '<p>Second unit memos, call sheets, prep calendars and production schedules were never meant '
                'to be kept. If you have any, they belong in the record.</p>'
                '<a class="button" href="/contribute/">Contribute →</a></div>')
    body.append('</div>'); body.append(JUMP); body.append(FOOT)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(body))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(DOCS)} documents, {total} pages")


if __name__ == "__main__":
    build()
