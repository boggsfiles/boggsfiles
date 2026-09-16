#!/usr/bin/env python3
"""build_revival_transcripts.py [codes...]  — align Season 10/11 transcripts from the prepped OCR.

Inputs per episode in ~/Movies/XF_transcript_prep/S<season>/<code>/: subs_clean.srt, reference.txt
Outputs: tools/transcript-data/<slug>.json (via align_monotonic.py), honouring
tools/transcript-overrides/<slug>-reviewed.json when present.
"""
import subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREP = Path.home() / "Movies/XF_transcript_prep"

# code, slug, title, airdate, extra proper nouns (kept capitalised in dialogue)
EPISODES = [
    (10, 1, "10X01", "my-struggle", "My Struggle", "January 24, 2016", "Tad,O'Malley,Sveta,Skinner,Roswell,Kimmel,Obama,Garner,Aurora,Nurse,Snowden,Manning,Assange,Ehrlich"),
    (10, 2, "10X02", "founders-mutation", "Founder's Mutation", "January 25, 2016", "Sanjay,Goldman,Jackie,Kyle,Molly,Gupta,Skinner,William,Agnes,Mary,Nugenics,Rebecca,Rogers"),
    (10, 3, "10X03", "mulder-and-scully-meet-the-were-monster", "Mulder and Scully Meet the Were-Monster", "February 1, 2016", "Guy,Mann,Pasha,Rumanovitch,Annabelle,Daggoo,Oregon,Kumail,Nanjiani,Fort,Shawnee"),
    (10, 4, "10X04", "home-again", "Home Again", "February 8, 2016", "Trashman,Dross,Taillie,Cutler,Huff,Fitzpatrick,Landry,Budd,Colquitt,Philadelphia,Margaret,William,Charlie,Bill"),
    (10, 5, "10X05", "babylon", "Babylon", "February 15, 2016", "Einstein,Miller,Noora,Brem,Shiraz,Texas,Skinner,Babel,Mezuzah,Vortex"),
    (10, 6, "10X06", "my-struggle-ii", "My Struggle II", "February 22, 2016", "Tad,O'Malley,Einstein,Miller,Reyes,Monica,Sandeep,Rubell,Skinner,Spartan,Spartanburg"),
    (11, 1, "11X01", "my-struggle-iii", "My Struggle III", "January 3, 2018", "Skinner,Spender,Jeffrey,Reyes,Monica,Sophia,Erika,Price,Mr. Y,Tad,O'Malley,Spartanburg,William,Kersh"),
    (11, 2, "11X02", "this", "This", "January 10, 2018", "Langly,Skinner,Erika,Price,Hamby,Colquitt,Deep Throat,Purlieu,Titanpointe,Arlington,Karah,Hamby"),
    (11, 3, "11X03", "plus-one", "Plus One", "January 17, 2018", "Judy,Chucky,Poundstone,Cavalier,Peggy,Vickie,Russel,Arkie,Seibert,Hangman"),
    (11, 4, "11X04", "the-lost-art-of-forehead-sweat", "The Lost Art of Forehead Sweat", "January 24, 2018", "Reggie,Murgatroid,Dr. They,Martin,Buddy,Pangborn,Mandela,Mengele,Skinner,Twilight Zone,Lost Martian,Kersh"),
    (11, 5, "11X05", "ghouli", "Ghouli", "January 31, 2018", "Brianna,Sarah,Costa,Paulsen,Green,Jackson,Van De Kamp,Scholz,Norfolk,Skinner,Ghouli,William"),
    (11, 6, "11X06", "kitten", "Kitten", "February 7, 2018", "Skinner,Davey,John James,Kitten,Stenzler,Kersh,Mud Lick,Kentucky,Glasses,Hillbilly,Ed,Vietnam"),
    (11, 7, "11X07", "rm9sbg93zxjz", "Rm9sbG93ZXJz", "February 28, 2018", "Forowa,Whipz,Bigly,Gydz,Queequeg,Zuma,Skinner"),
    (11, 8, "11X08", "familiar", "Familiar", "March 7, 2018", "Strong,Anna,Wentworth,Eggers,Diana,Andrew,Melvin,Emily,Sean,Eastwood,Connecticut,Bibbletiggles,Chuckleteeth"),
    (11, 9, "11X09", "nothing-lasts-forever", "Nothing Lasts Forever", "March 14, 2018", "Barbara,Beaumont,Luvenis,Juliet,Olivia,Bocanegra,Kayla,Dave,Bronx,Father"),
    (11, 10, "11X10", "my-struggle-iv", "My Struggle IV", "March 21, 2018", "William,Skinner,Kersh,Maddy,Reyes,Monica,Tad,O'Malley,Brianna,Sarah,Spender,Jeffrey,Norfolk,Spartanburg"),
]
LABELS = "MULDER=Fox Mulder,SCULLY=Dana Scully,SKINNER=Walter Skinner,KERSH=Alvin Kersh,SVETA=Sveta,GARNER=Garner,MR. O'MALLEY=Tad O'Malley,TAD O'MALLEY=Tad O'Malley,O'MALLEY=Tad O'Malley,NURSE=Nurse,SURGEON=Surgeon,JIMMY KIMMEL=Jimmy Kimmel,OLD MAN=Old Man,CIGARETTE SMOKING MAN=Cigarette-Smoking Man,CSM=Cigarette-Smoking Man,REYES=Monica Reyes,MONICA=Monica Reyes,EINSTEIN=Agent Einstein,MILLER=Agent Miller,AGENT EINSTEIN=Agent Einstein,AGENT MILLER=Agent Miller,WILLIAM=William,JACKSON=Jackson Van De Kamp,SPENDER=Jeffrey Spender,LANGLY=Richard Langly,REGGIE=Reggie Something,GUY=Guy Mann,WONG=Wong,WOMAN=Woman,MAN=Man,GIRL=Girl,BOY=Boy,ANNOUNCER=Announcer,REPORTER=Reporter,NARRATOR=Narrator,DR. THEY=Dr. They,TRASHMAN=Trashman,PRICE=Erika Price,ERIKA PRICE=Erika Price,MR. Y=Mr. Y,DAVEY=Davey James,BARBARA=Barbara Beaumont,LUVENIS=Dr. Luvenis,JUDY=Judy Poundstone,CHUCKY=Chucky Poundstone"
COMMON = "Mulder,Scully,Fox,Dana,FBI,X-Files,Cigarette-Smoking Man,Smoking Man,William,Washington,D.C.,Virginia,America,American,God,Jesus,Christ,Oregon,Texas,Skinner"

def main():
    only = set(sys.argv[1:])
    for i, (season, num, code, slug, title, airdate, proper) in enumerate(EPISODES):
        if only and code not in only: continue
        prev = EPISODES[i - 1] if i else None
        nxt = EPISODES[i + 1] if i + 1 < len(EPISODES) else None
        if prev and prev[0] != season: prev = None
        if nxt and nxt[0] != season: nxt = None
        p = PREP / f"S{season}" / code
        cmd = [sys.executable, str(HERE / "align_monotonic.py"), str(p / "subs_clean.srt"), str(p / "reference.txt"),
               str(HERE / "transcript-data" / f"{slug}.json"), "--episode", title, "--code", f"{season - 9}AYW{num:02d}",
               "--airdate", airdate, "--slug", slug, "--season", str(season), "--episode-number", str(num),
               "--proper", COMMON + "," + proper, "--keep-case", "--labels", LABELS]
        if prev: cmd += ["--previous-url", f"/transcripts/season-{season}/{prev[3]}/", "--previous-title", prev[4]]
        else: cmd += ["--previous-url", f"/transcripts/season-{season}/", "--previous-title", f"Season {season}"]
        if nxt: cmd += ["--next-url", f"/transcripts/season-{season}/{nxt[3]}/", "--next-title", nxt[4]]
        rev = HERE / "transcript-overrides" / f"{slug}-reviewed.json"
        if rev.exists(): cmd += ["--reviewed", str(rev)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(f"{code} {title}: {r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[-300:]}")

if __name__ == "__main__":
    main()
