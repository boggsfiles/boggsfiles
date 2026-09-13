#!/usr/bin/env python3
"""Build the transcript season index and live episode galleries."""

from pathlib import Path
from transcript_header import HEADER, ASSETS


SEASON_1 = [
    ("pilot", "Pilot", "1X79", "Mulder and Scully’s first investigation, organized scene by scene for research and close reading."),
    ("deep-throat", "Deep Throat", "1X01", "A missing test pilot draws the agents toward Ellens Air Base and a secret informant."),
    ("squeeze", "Squeeze", "1X02", "An impossible murder case brings the agents face to face with Eugene Victor Tooms."),
    ("conduit", "Conduit", "1X03", "A girl’s disappearance forces Mulder to confront the memory of his own sister."),
    ("jersey-devil", "The Jersey Devil", "1X04", "A body in the woods leads Mulder toward a creature beyond Atlantic City."),
    ("shadows", "Shadows", "1X05", "An unseen force appears to protect a grieving secretary from danger."),
    ("ghost-in-the-machine", "Ghost in the Machine", "1X06", "A lethal artificial intelligence turns a high-rise office into a system of traps."),
    ("ice", "Ice", "1X07", "Isolation and suspicion consume an Arctic research team after a discovery in the ice."),
    ("space", "Space", "1X08", "A shuttle mission is threatened by sabotage and an astronaut’s encounter in orbit."),
    ("fallen-angel", "Fallen Angel", "1X09", "A secret military recovery operation draws Mulder to a crash site—and Max Fenig."),
    ("eve", "Eve", "1X10", "Two identical girls and two identical murders expose a genetics experiment."),
    ("fire", "Fire", "1X11", "A dangerous arsonist—and a figure from Mulder’s past—ignite a combustible case."),
    ("beyond-the-sea", "Beyond the Sea", "1X12", "In the midst of grief, Scully confronts a death-row inmate who claims psychic powers."),
    ("gender-bender", "Gender Bender", "1X13", "A series of intimate deaths points toward an isolated community with a secret."),
    ("lazarus", "Lazarus", "1X14", "Scully’s former partner becomes connected to a bank robber after a near-fatal shooting."),
    ("young-at-heart", "Young at Heart", "1X15", "A criminal Mulder helped imprison appears to return years later without having aged."),
    ("ebe", "E.B.E.", "1X16", "A UFO recovery trail pulls Mulder and Scully into a campaign of disinformation."),
    ("miracle-man", "Miracle Man", "1X17", "A young faith healer becomes the center of a series of mysterious deaths."),
    ("shapes", "Shapes", "1X18", "A Montana killing reopens one of the FBI’s earliest unexplained cases."),
    ("darkness-falls", "Darkness Falls", "1X19", "An ancient swarm traps a logging crew—and the agents—in a remote forest."),
    ("tooms", "Tooms", "1X20", "Eugene Victor Tooms returns, placing Scully in danger as Mulder races to stop him."),
    ("born-again", "Born Again", "1X21", "A child’s impossible knowledge connects a murder investigation to a detective’s death."),
    ("roland", "Roland", "1X22", "A laboratory death draws the agents toward a gifted caretaker and a hidden connection."),
    ("the-erlenmeyer-flask", "The Erlenmeyer Flask", "1X23", "Deep Throat leads Mulder and Scully toward evidence that could prove everything."),
]

SEASON_2 = [
    ("little-green-men", "Little Green Men", "2X01", "Separated from the X-Files, Mulder follows a signal to an abandoned observatory in Puerto Rico."),
    ("the-host", "The Host", "2X02", "A body in the sewers leads Mulder to a parasitic creature—and an unexpected ally."),
    ("blood", "Blood", "2X03", "Electronic messages push ordinary residents toward violence in a quiet Pennsylvania town."),
    ("sleepless", "Sleepless", "2X04", "A group of Vietnam veterans who no longer sleep becomes the center of a deadly conspiracy."),
    ("duane-barry", "Duane Barry", "2X05", "A hostage crisis brings Mulder face to face with a man who says he has been abducted."),
    ("ascension", "Ascension", "2X06", "Mulder follows Duane Barry to Skyland Mountain in a desperate search for Scully."),
    ("3", "3", "2X07", "Alone in Los Angeles, Mulder investigates a series of murders linked to a thirst for blood."),
    ("one-breath", "One Breath", "2X08", "Scully returns in critical condition as Mulder searches for answers and a way to help her."),
    ("firewalker", "Firewalker", "2X09", "A volcanic research team's discovery draws Mulder and Scully into a deadly quarantine."),
    ("red-museum", "Red Museum", "2X10", "Strange abductions in a Wisconsin town lead the agents toward a secret experiment."),
    ("excelsis-dei", "Excelsis Dei", "2X11", "An assault at a care home leads Mulder and Scully to investigate its unseen residents."),
    ("aubrey", "Aubrey", "2X12", "A detective's disturbing visions uncover a connection to murders committed decades earlier."),
    ("irresistible", "Irresistible", "2X13", "A grave desecration case brings the agents face to face with a deeply unsettling killer."),
    ("die-hand-die-verletzt", "Die Hand Die Verletzt", "2X14", "A teenager's death exposes a school's secrets and a sinister substitute teacher."),
    ("fresh-bones", "Fresh Bones", "2X15", "Deaths at a refugee camp lead Mulder and Scully into a case of abuse and apparent voodoo."),
    ("colony", "Colony", "2X16", "Identical murder victims and a visitor from Mulder's past draw the agents into a dangerous pursuit."),
    ("end-game", "End Game", "2X17", "A hostage exchange sends Mulder north in pursuit of the alien bounty hunter."),
    ("fearful-symmetry", "Fearful Symmetry", "2X18", "Missing zoo animals and impossible attacks lead the agents to a mysterious pattern."),
    ("dod-kalm", "Død Kalm", "2X19", "Mulder and Scully board a deserted ship whose remaining crew have aged overnight."),
    ("humbug", "Humbug", "2X20", "A murder investigation brings the agents to a Florida community of sideshow performers."),
    ("the-calusari", "The Calusari", "2X21", "A family tragedy draws Mulder and Scully toward a child's unsettling connection to an unseen force."),
    ("f-emasculata", "F. Emasculata", "2X22", "An escaped-prisoner search exposes a deadly outbreak and a concealed experiment."),
    ("soft-light", "Soft Light", "2X23", "A physicist's shadow becomes the focus of a series of unexplained disappearances."),
    ("our-town", "Our Town", "2X24", "A missing inspector leads the agents into a poultry town with a horrifying secret."),
    ("anasazi", "Anasazi", "2X25", "Stolen government records send Mulder and Scully toward a buried discovery in New Mexico."),
]

SEASON_3 = [
    ("the-blessing-way", "The Blessing Way", "3X01", "As Mulder fights to survive, Scully confronts the consequences of the stolen files."),
    ("paper-clip", "Paper Clip", "3X02", "A hidden archive draws Mulder and Scully deeper into the origins of the conspiracy."),
    ("dpo", "D.P.O.", "3X03", "A string of unusual deaths leads the agents to a young man with a dangerous electrical charge."),
    ("clyde-bruckmans-final-repose", "Clyde Bruckman’s Final Repose", "3X04", "A reluctant psychic helps investigate murders while confronting the certainty of death."),
    ("the-list", "The List", "3X05", "An executed prisoner’s promise of revenge haunts the people inside a Florida prison."),
    ("2shy", "2Shy", "3X06", "An online predator leaves a trail of victims with an inexplicable loss of body fat."),
    ("the-walk", "The Walk", "3X07", "A military hospital’s mysterious attacks point toward a wounded veteran’s unseen reach."),
    ("oubliette", "Oubliette", "3X08", "A kidnapped teenager’s ordeal appears to be shared by a woman who escaped a similar captivity."),
    ('nisei', 'Nisei', '3X09', 'An alien autopsy tape leads Mulder to a secret train and Scully to a group of fellow abductees.'),
    ('731', '731', '3X10', 'Mulder is trapped aboard a train while Scully searches for the truth behind a covert experiment.'),
    ('revelations', 'Revelations', '3X11', 'A boy with mysterious wounds puts Scully’s faith at the center of a dangerous case.'),
    ('war-of-the-coprophages', 'War of the Coprophages', '3X12', 'A rash of deaths and reports of killer cockroaches send a small town into panic.'),
    ('syzygy', 'Syzygy', '3X13', 'Two teenage friends and an unusual planetary alignment unsettle a town—and the agents.'),
    ('grotesque', 'Grotesque', '3X14', 'A serial killer’s disturbing drawings pull Mulder deep into an investigation led by his former mentor.'),
    ('piper-maru', 'Piper Maru', '3X15', 'A salvage crew’s radiation exposure reveals a mystery beneath the Pacific.'),
    ('apocrypha', 'Apocrypha', '3X16', 'The search for Krycek connects a recovered vessel, a stolen tape, and the attack on Skinner.'),
    ('pusher', 'Pusher', '3X17', 'A man who can bend others to his will draws Mulder into a deadly contest.'),
    ('teso-dos-bichos', 'Teso Dos Bichos', '3X18', 'Deaths at a museum follow the arrival of an ancient burial urn from Ecuador.'),
    ('hell-money', 'Hell Money', '3X19', 'A series of deaths in San Francisco’s Chinatown exposes a deadly underground lottery.'),
    ('jose-chungs-from-outer-space', 'Jose Chung’s From Outer Space', '3X20', 'A writer interviews Scully about an alien abduction case full of contradictory accounts.'),
    ('avatar', 'Avatar', '3X21', 'Skinner becomes a murder suspect as a mysterious woman haunts his waking life.'),
    ('quagmire', 'Quagmire', '3X22', 'Deaths near a Georgia lake send Mulder and Scully searching for a legendary creature.'),
    ('wetwired', 'Wetwired', '3X23', 'A strange television signal fuels paranoia and threatens Scully’s trust in Mulder.'),
    ('talitha-cumi', 'Talitha Cumi', '3X24', 'A mysterious healer offers answers as Mulder’s mother falls critically ill.'),
]

SEASONS = {1: SEASON_1, 2: SEASON_2, 3: SEASON_3}

HEAD = '''<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Libre+Caslon+Display&family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet">'''



BASE = '''*{box-sizing:border-box}html{background:#08100d;color:#eeeee8}body{margin:0;font:400 15px/1.7 "DM Mono",monospace;background:#08100d}a{color:inherit;text-decoration:none}.shell{width:min(1656px,calc(100% - 56px));margin:auto}header{border-bottom:1px solid #343c38;position:relative;z-index:5;background:#08100d}.shell nav{}.brand{font:500 1.18rem/1 "Oswald",sans-serif;letter-spacing:.08em;white-space:nowrap}.brand .x{display:inline-block;color:#e44238;margin:0 .13em}.links{display:flex;gap:26px;align-items:center;font-size:.58rem;text-transform:uppercase;letter-spacing:.12em}.links a{color:#929c95}.links a:hover,.links .active{color:#eeeee8}header nav{height:82px;display:flex;align-items:center;justify-content:space-between}.eyebrow{color:#e44238;font-size:.6rem;letter-spacing:.19em;text-transform:uppercase}.hero{padding:92px 0 76px;border-bottom:1px solid #343c38}.crumb{font-size:.58rem;text-transform:uppercase;letter-spacing:.12em;color:#818b84;margin-bottom:30px}.crumb a{color:#eeeee8}.hero h1{font:400 clamp(4.4rem,9vw,9.2rem)/.84 "Oswald",sans-serif;text-transform:uppercase;letter-spacing:-.035em;margin:0}.hero p{color:#a2aaa4;max-width:760px;margin:30px 0 0;font-size:.85rem;line-height:1.85}.summary{display:flex;gap:1px;background:#343c38;border:1px solid #343c38;width:max-content;margin-top:48px}.stat{background:#0e1412;padding:19px 26px;min-width:150px}.stat b{display:block;font:400 1.65rem/1 "Oswald",sans-serif}.stat span{display:block;color:#7f8982;font-size:.5rem;letter-spacing:.12em;text-transform:uppercase;margin-top:10px}footer{border-top:1px solid #343c38;margin-top:90px;padding:38px 0;color:#7f8982;font-size:.55rem;letter-spacing:.11em;text-transform:uppercase}.footer-row{display:flex;justify-content:space-between}@media(max-width:920px){.links{display:none}.hero{padding-top:64px}.shell{width:min(100% - 32px,1656px)}}'''


def season_landing() -> str:
    cards=[]
    for season in range(1,10):
        live=season in SEASONS
        count=len(SEASONS.get(season, []))
        image="pilot" if season == 1 else "the-blessing-way" if season == 3 else "little-green-men"
        image_ext="jpg" if season == 3 else "webp"
        cards.append(f'''<a class="season-card {'live' if live else 'soon'}" href="/transcripts/season-{season}/">
          <div class="season-visual"><span>{season:02d}</span>{f'<img src="/assets/transcript-stills/{image}.{image_ext}" alt="Scene from Season {season}">' if live else ''}</div>
          <div class="season-copy"><div><span class="eyebrow">{f'{count} transcripts live' if live else 'Collection pending'}</span><h2>Season {season}</h2></div><b>{'Explore season →' if live else 'Coming soon →'}</b></div></a>''')
    return f'''<!doctype html><html lang="en"><head><title>Transcripts — Boggsfiles</title><meta name="description" content="Browse character-labelled X-Files episode transcripts by season.">{HEAD}<style>{BASE}
    .seasons{{padding:72px 0 0}}.season-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:#343c38;border:1px solid #343c38}}.season-card{{background:#0e1412;min-height:390px;display:flex;flex-direction:column;transition:.2s}}.season-card:hover{{background:#131a17}}.season-visual{{height:235px;position:relative;overflow:hidden;background:#111714}}.season-visual img{{width:100%;height:100%;object-fit:cover;filter:saturate(.78) brightness(.72);transition:.3s}}.season-card:hover img{{transform:scale(1.02)}}.season-visual>span{{position:absolute;right:20px;bottom:-30px;font:500 9rem/1 "Oswald",sans-serif;color:#1b231f;z-index:1}}.season-visual img+span{{display:none}}.season-copy{{padding:28px 30px 32px;display:flex;align-items:end;justify-content:space-between;gap:20px;flex:1}}.season-copy h2{{font:400 2.8rem/1 "Oswald",sans-serif;text-transform:uppercase;margin:8px 0 0}}.season-copy>b{{font-size:.55rem;text-transform:uppercase;letter-spacing:.12em;white-space:nowrap}}.soon{{color:#929c95}}@media(max-width:1000px){{.season-grid{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:620px){{.season-grid{{grid-template-columns:1fr}}.season-copy{{align-items:start;flex-direction:column}}}}
    </style>{ASSETS}</head><body>{HEADER}<main><section class="hero"><div class="shell"><div class="crumb"><a href="/archive/">Archive</a> &nbsp;/&nbsp; Transcripts</div><div class="eyebrow">The aired record</div><h1>Transcripts</h1><p>Character-labelled episode dialogue prepared from the official DVD subtitle tracks, organized by season and designed for searching, reference, and close reading.</p><div class="summary"><div class="stat"><b>9</b><span>Seasons</span></div><div class="stat"><b>{sum(len(episodes) for episodes in SEASONS.values())}</b><span>Transcripts live</span></div><div class="stat"><b>DVD</b><span>Subtitle source</span></div></div></div></section><section class="seasons"><div class="shell"><div class="season-grid">{''.join(cards)}</div></div></section></main><footer><div class="shell footer-row">BOGGSFILES · TRANSCRIPT ARCHIVE <span><a href="/">Home</a> · <a href="/archive/">Archive</a></span></div></footer></body></html>'''


def season_page(season: int, episodes: list[tuple[str, str, str, str]]) -> str:
    cards=[]
    for number,(slug,title,code,description) in enumerate(episodes,1):
        cards.append(f'''<a class="episode-card" href="/transcripts/season-{season}/{slug}/"><img src="/assets/transcript-stills/{slug}.{'jpg' if season > 2 or season == 2 and number > 4 else 'webp'}" alt="Scene from {title}" loading="lazy"><div class="episode-copy"><span>File {number:02d} · {code}</span><h2>{title}</h2><p>{description}</p><b>Read transcript →</b></div></a>''')
    years = "1993–1994" if season == 1 else "1994–1995" if season == 2 else "1995–1996"
    intro = "The beginning of the X-Files—and the beginning of Mulder and Scully." if season == 1 else "The X-Files is closed, but the search continues as Mulder and Scully are pulled back toward the cases that defined them."
    if season == 3:
        intro = "Mulder and Scully pursue the conspiracy and investigate a new collection of unexplained cases."
    total = 25 if season == 2 else 24
    source_index = "first-season-index.html" if season == 1 else "second-season-index.html" if season == 2 else "third-season-index.html"
    return f'''<!doctype html><html lang="en"><head><title>Season {season} Transcripts — Boggsfiles</title><meta name="description" content="Browse character-labelled transcripts for The X-Files Season {season}.">{HEAD}<style>{BASE}
    .episodes{{padding:72px 0 0}}.season-head{{display:flex;justify-content:space-between;align-items:end;margin-bottom:34px}}.season-head h2{{font:400 clamp(3.2rem,6vw,6rem)/.9 "Oswald",sans-serif;text-transform:uppercase;margin:10px 0 0}}.season-head>span{{color:#8c968f;font-size:.62rem;letter-spacing:.12em;text-transform:uppercase}}.episode-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;background:#343c38;border:1px solid #343c38}}.episode-card{{background:#0e1412;display:flex;min-width:0;flex-direction:column;transition:.2s}}.episode-card:hover{{background:#141b18}}.episode-card img{{width:100%;aspect-ratio:16/10;object-fit:cover;filter:saturate(.82) brightness(.79);transition:.25s}}.episode-card:hover img{{filter:saturate(.95) brightness(.9)}}.episode-copy{{padding:25px 25px 28px;display:flex;flex:1;flex-direction:column;min-height:290px}}.episode-copy>span{{color:#e44238;font-size:.53rem;letter-spacing:.14em;text-transform:uppercase}}.episode-copy h2{{font:400 clamp(1.8rem,2.4vw,2.75rem)/.96 "Oswald",sans-serif;text-transform:uppercase;margin:14px 0 15px}}.episode-copy p{{color:#929c95;font-size:.66rem;line-height:1.7;margin:0}}.episode-copy b{{margin-top:auto;padding-top:24px;font-size:.54rem;letter-spacing:.12em;text-transform:uppercase}}.source-note{{color:#747e77;font-size:.55rem;margin-top:22px;text-align:right}}.source-note a{{text-decoration:underline;text-underline-offset:3px}}@media(max-width:1160px){{.episode-grid{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:650px){{.episode-grid{{grid-template-columns:1fr}}.episode-copy{{min-height:240px}}.season-head{{align-items:start;flex-direction:column;gap:18px}}}}
    </style>{ASSETS}</head><body>{HEADER}<main><section class="hero"><div class="shell"><div class="crumb"><a href="/transcripts/">Transcripts</a> &nbsp;/&nbsp; Season {season}</div><div class="eyebrow">{years}</div><h1>Season {season}</h1><p>{intro} Read each episode without timestamps, with dialogue attributed to its speaker and divided into searchable scenes.</p><div class="summary"><div class="stat"><b>{len(episodes)}</b><span>Transcripts live</span></div><div class="stat"><b>{total}</b><span>Episodes total</span></div><div class="stat"><b>{season}X</b><span>Production files</span></div></div></div></section><section class="episodes"><div class="shell"><div class="season-head"><div><div class="eyebrow">Episode files</div><h2>Read Season {season}</h2></div><span>Broadcast order · Four across</span></div><div class="episode-grid">{''.join(cards)}</div><p class="source-note">Episode screen captures: <a href="https://xfilesarchive.com/{source_index}">The X-Files Archive</a>.</p></div></section></main><footer><div class="shell footer-row">BOGGSFILES · TRANSCRIPT ARCHIVE <span><a href="/">Home</a> · <a href="/transcripts/">All seasons</a></span></div></footer></body></html>'''


def placeholder(season: int) -> str:
    return f'''<!doctype html><html lang="en"><head><title>Season {season} Transcripts — Boggsfiles</title>{HEAD}<style>{BASE}.pending{{padding:110px 0 160px}}.pending-box{{border:1px solid #343c38;padding:70px;background:#0e1412}}.pending h1{{font:400 clamp(4rem,9vw,9rem)/.9 "Oswald",sans-serif;text-transform:uppercase;margin:15px 0 25px}}.pending p{{color:#929c95;max-width:620px}}.pending a{{display:inline-block;margin-top:28px;color:#e44238;font-size:.6rem;text-transform:uppercase;letter-spacing:.13em}}@media(max-width:650px){{.pending-box{{padding:42px 28px}}}}</style>{ASSETS}</head><body>{HEADER}<main class="pending"><div class="shell"><div class="pending-box"><div class="eyebrow">Transcript collection</div><h1>Season {season}</h1><p>This season’s character-labelled DVD transcripts are being prepared for the Boggsfiles archive.</p><a href="/transcripts/">← Return to all seasons</a></div></div></main><footer><div class="shell footer-row">BOGGSFILES · TRANSCRIPT ARCHIVE <span><a href="/">Home</a></span></div></footer></body></html>'''


def main() -> None:
    root=Path("dist/transcripts")
    (root/"index.html").write_text(season_landing(),encoding="utf-8")
    for season, episodes in SEASONS.items():
        directory=root/f"season-{season}"
        directory.mkdir(parents=True,exist_ok=True)
        (directory/"index.html").write_text(season_page(season, episodes),encoding="utf-8")
    for season in range(4,10):
        directory=root/f"season-{season}"
        directory.mkdir(parents=True,exist_ok=True)
        (directory/"index.html").write_text(placeholder(season),encoding="utf-8")


if __name__ == "__main__":
    main()
