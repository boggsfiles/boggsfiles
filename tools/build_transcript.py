#!/usr/bin/env python3
"""Build a speaker-labelled transcript dataset from DVD SRT captions."""

from __future__ import annotations

import argparse
from collections import Counter
import html
import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path


NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
    "eighteen": "18", "nineteen": "19", "twenty": "20",
}

SPEAKER_NAMES = {
    "MILES": "Detective Miles",
    "DETECTIVE MILES": "Detective Miles",
    "JOHN TRUITT": "John Truitt",
    "ASSISTANT CORONER": "Assistant Coroner",
    "SCULLY": "Dana Scully",
    "SCULLY ON TAPE RECORDER": "Dana Scully (recorded)",
    "MULDER": "Fox Mulder",
    "SCOTT BLEVINS": "Scott Blevins",
    "THIRD MAN": "FBI Official",
    "PILOT": "Airline Pilot",
    "JAY NEMMAN": "Dr. Jay Nemman",
    "THERESA NEMMAN": "Theresa Nemman",
    "GLASS": "Dr. Glass",
    "DR. GLASS": "Dr. Glass",
    "PEGGY O'DELL": "Peggy O'Dell",
    "NURSE": "Nurse",
    "WORKER": "Cemetery Worker",
    "TRUCK DRIVER": "Truck Driver",
    "DEPUTY": "Deputy",
    "FIREMAN": "Firefighter",
    "BILLY MILES": "Billy Miles",
    "HEITZ WERBER": "Dr. Heitz Werber",
    "MULDR": "Fox Mulder",
    "SCULLY VOICE OVER": "Dana Scully (voice-over)",
    "SCULLY WHISPERS": "Dana Scully",
    "TOMSON": "Detective Thompson",
    "DORLAND": "Robert Dorland",
    "DORLUND": "Robert Dorland",
    "MR. DORLAND": "Robert Dorland",
    "MR DORLAND": "Robert Dorland",
    "COS COMPUTER": "COS Computer",
    "COMPUTER": "COS Computer",
    "COMPUTER VOICE": "COS Computer",
    "MICHELL": "Michelle Generoo",
    "MICHELLE": "Michelle Generoo",
    "MICHELLE GENEROO": "Michelle Generoo",
    "GENEROO": "Michelle Generoo",
    "EMT1": "Paramedic 1",
    "EMT2": "Paramedic 2",
    "MCGRATH": "Section Chief McGrath",
    "SECTION CHIEF MCGRATH": "Section Chief McGrath",
    "MRS WRIGHT": "Mrs. Wright",
    "DR KENDRICK ON TAPE": "Dr. Sally Kendrick (recorded)",
    "SALLY KENDRICK ON TAPE": "Dr. Sally Kendrick (recorded)",
    "DEEP THROAT VOICE OVER": "Deep Throat (voice-over)",
    "CINDY VOICE OVER": "Cindy Reardon (voice-over)",
    "CINDY": "Cindy Reardon",
    "TEENA": "Teena Simmons",
    "TEENA AND CINDY": "Teena Simmons & Cindy Reardon",
    "TEENA OR CINDY": "Teena Simmons or Cindy Reardon",
    "L'IVELY": "Cecil L'Ively",
    "BOGGS": "Luther Lee Boggs",
    "MAGGIE": "Margaret Scully",
    "MARTY (WOMAN)": "Marty",
    "MAN'S VOICE": "Man's Voice",
    "DASILVA": "Nancy Da Silva",
    "BELT": "Colonel Marcus Aurelius Belt",
    "YOUNG BELT": "Young Marcus Belt",
    "YOUNG BELT IN SPACE": "Young Marcus Belt",
    "MULDER AND SCULLY": "Fox Mulder & Dana Scully",
    "FLORIDA MC": "Florida Mission Control",
    "SHUTTLE LC": "Shuttle Launch Control",
    "OTC": "Orbiter Crew",
    "SHUTTLE": "Orbiter Crew",
    "HOUSTON": "Houston Mission Control",
    "CURLY HOUSTON": "Houston Mission Control",
    "MRS REARDON": "Mrs. Reardon",
    "TRUCK DRIVER'S WIFE": "Truck Driver's Wife",
    "GREEN": "Phoebe Green",
    "PHOEBE": "Phoebe Green",
    "MARSDEN": "Sir Malcolm Marsden",
    "MALCOLM MARSDEN": "Sir Malcolm Marsden",
    "LIZ": "Liz Hawley",
    "ELIZABETH": "Liz Hawley",
    "SISTER ABBY": "Sister Abigail",
    "JERRY": "Jerry Lamana",
    "LAMANA": "Jerry Lamana",
    "MAX": "Max Fenig",
    "HENDERSON": "Colonel Calvin Henderson",
    "WRIGHT": "Deputy Wright",
    "CTGG": "NASA Data Technician",
    "TECHMECH GUY": "NASA Technician",
    "CURLY HAIRED TECH": "Houston Technician",
    "HOUSTON TECH": "Houston Technician",
    "FLORIDA": "Florida Mission Control",
    "ALBUQUERQUE": "Albuquerque Ground Control",
    "SOME GUY": "Mission Control Staffer",
    "LULU": "Lula",
    "BIBLE COP": "Undercover Officer",
    "JOE CRANDELL": "Joe Crandall",
    "PURDUE": "Reggie Purdue",
    "BARNETT": "John Barnett",
    "MULDER ON RECORDER": "Fox Mulder (recorded)",
    "JOHN BARNETT ON RECORDER": "John Barnett (recorded)",
    "SCULLY ON MACHINE": "Dana Scully (recorded)",
    "MARGARET SCULLY ON MACHINE": "Margaret Scully (recorded)",
    "KATHY ON MACHINE": "Kathy (recorded)",
    "HARTLEY": "Reverend Hartley",
    "DANIELS": "Sheriff Daniels",
    "LILLIAN": "Lillian Daniels",
    "TSKANY": "Sheriff Tskany",
    "SCULLY'S VOICE": "Dana Scully (voice-over)",
    "ED": "Edward Funsch",
    "MOTOLA": "Matola",
    "MAN ON VOYAGER RECORD": "Kurt Waldheim (recorded)",
    "KURT WALDHEIM ON MESSAGE": "Kurt Waldheim (recorded)",
    "KURT WALDHEIM ON MACHINE": "Kurt Waldheim (recorded)",
    "SCULLY ON TAPE": "Dana Scully (recorded)",
    "SKINNER ON TAPE": "Walter Skinner (recorded)",
    "MULDER ON ANSWERING MACHINE": "Fox Mulder (recorded)",
}

PILOT_MANUAL_SPEAKERS = {
    273: "Dr. Glass",
    274: "Dr. Glass",
    275: "Dr. Glass",
    276: "Peggy O'Dell",
    284: "Dr. Glass",
    286: "Dr. Glass",
    291: "Nurse",
    463: "Emergency Worker",
    477: "Firefighter",
    578: "Nurse",
    665: "Billy Miles",
    666: "Dr. Heitz Werber",
    667: "Billy Miles",
    713: "Fox Mulder",
}

PROPER_CASE = {
    "f.b.i.": "FBI", "f.b.i.'s": "FBI's", "u.f.o.": "UFO", "u.f.o.s": "UFOs",
    "i.d.": "ID", "x-files": "X-Files", "x-file": "X-File",
    "mulder": "Mulder", "scully": "Scully", "dana": "Dana", "fox": "Fox",
    "karen": "Karen", "swenson": "Swenson", "einstein": "Einstein",
    "oxford": "Oxford", "monty": "Monty", "propps": "Propps",
    "july": "July", "england": "England", "congress": "Congress",
    "halloween": "Halloween", "raymond": "Raymond", "heinz": "Heinz",
    "werber": "Werber", "tv": "TV", "d.a.'s": "DA's",
    "ray": "Ray", "soames": "Soames", "billy": "Billy", "miles": "Miles",
    "peggy": "Peggy", "o'dell": "O'Dell", "theresa": "Theresa", "nemman": "Nemman",
    "oregon": "Oregon", "bellefleur": "Bellefleur", "texas": "Texas",
    "shamrock": "Shamrock", "sturgis": "Sturgis", "south dakota": "South Dakota",
    "u.p.s.": "UPS", "n.s.a.": "NSA", "d.c.": "D.C.",
    "robert budahas": "Robert Budahas", "ellens air base": "Ellens Air Base",
    "idaho": "Idaho", "boise": "Boise", "roswell": "Roswell",
    "new mexico": "New Mexico", "green bay": "Green Bay", "lombardi": "Lombardi",
    "tom colton": "Tom Colton", "eugene tooms": "Eugene Tooms",
    "george usher": "George Usher", "frank briggs": "Frank Briggs",
    "baltimore": "Baltimore", "maryland": "Maryland", "exeter": "Exeter",
    "darlene morris": "Darlene Morris", "kevin morris": "Kevin Morris",
    "ruby morris": "Ruby Morris", "sioux city": "Sioux City", "iowa": "Iowa",
    "lake okobogee": "Lake Okobogee", "greg randall": "Greg Randall",
    "leza atsumi": "Leza Atsumi", "brandenburg": "Brandenburg", "nasa": "NASA",
}

PILOT_SCENE_LOCATIONS = {
    1: "Collum National Forest · Northwest Oregon",
    2: "FBI Headquarters · Washington, D.C.",
    3: "Airplane to Oregon",
    4: "Bellefleur, Oregon",
    5: "Coastal Northwest Oregon · March 7, 1992",
    6: "Examination Facility · 10:56 P.M.",
    7: "Scully's Hotel Room",
    8: "Raymon County State Psychiatric Hospital",
    9: "Collum National Forest · Northwest Oregon",
    10: "Scully's Hotel Room",
    11: "Mulder's Hotel Room",
    12: "Rural Highway 133 · Bellefleur, Oregon",
    13: "Hotel",
    14: "Diner",
    15: "Cemetery · 5:07",
    16: "Raymon County State Psychiatric Hospital",
    17: "Collum National Forest · Northwest Oregon",
    18: "FBI Headquarters · March 22, 1992",
    19: "Section Chief Blevins' Office · FBI Headquarters",
    20: "Scully's Apartment",
}


@dataclass
class RefTurn:
    speaker: str
    text: str
    scene: int
    location: str


def clean_markup(value: str) -> str:
    value = html.unescape(value)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()


def is_caption_credit(value: str) -> bool:
    normalized = normalize(value)
    return normalized.startswith("closed captioned") or normalized.startswith("captions inc") or normalized.startswith("captioning made possible")


def is_sound_label(value: str) -> bool:
    value = value.lower()
    terms = (
        "music", "singing", "laugh", "scream", "shout", "yell", "whisper",
        "beep", "ring", "buzz", "hum", "rumbl", "rattl", "whirr", "crack",
        "clatter", "thunder", "gunshot", "explosion", "grunting", "panting",
        "breathing", "sniff", "gasp", "sigh", "winc", "indistinct",
        "conversing", "speaking", "replying", "continues", "static", "yawn",
        "turns on", "car starts", "tv stops", "slow motion", "slow-motion",
        "sirens approaching", "recording", "groan", "scoff", "yelp",
    )
    return any(term in value for term in terms)


def normalize(value: str) -> str:
    value = clean_markup(value).lower().replace("’", "'")
    value = re.sub(r"\b(?:um|uh|er)\b", " ", value)
    value = re.sub(r"[^a-z0-9']+", " ", value)
    words = [NUMBER_WORDS.get(word, word) for word in value.split()]
    return " ".join(words)


ACCEPT_ALL_CAPS_LABELS = False   # Blu-ray SDH tracks label every speaker in caps; set by align_monotonic --keep-case


def known_label(label: str) -> bool:
    """An all-caps caption label counts as a speaker if it is a known name, optionally
    with an 'ON TV' / 'ON PHONE' style suffix."""
    if ACCEPT_ALL_CAPS_LABELS and len(label.split()) <= 4 and not is_sound_label(label):
        return True
    base = re.sub(r"\s+(ON|OVER)\s+(TV|PHONE|LAPTOP|RADIO|P\.A\.|SPEAKER|INTERCOM|VIDEO|TAPE|MONITOR)$", "", label.strip().upper())
    return label.upper() in SPEAKER_NAMES or base in SPEAKER_NAMES


def parse_srt(path: Path, cue_splits: dict | None = None) -> tuple[list[dict], int]:
    cue_splits = cue_splits or {}
    raw = path.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n")
    cues = []
    source_cues = 0
    for block in re.split(r"\n{2,}", raw.strip()):
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            continue
        source_cues += 1
        number = int(lines[0])
        if str(number) in cue_splits:
            for subindex, segment in enumerate(cue_splits[str(number)]):
                cues.append({"number": number, "subindex": subindex,
                             "text": segment["text"],
                             "explicit_speaker": segment.get("speaker", "")})
            continue
        text_lines = [clean_markup(line) for line in lines[2:] if clean_markup(line)]
        text_lines = [line for line in text_lines if not is_caption_credit(line)]
        dashed = len([line for line in text_lines if re.match(r"^-\s+", line)]) > 1
        segments: list[dict] = []
        current: list[str] = []
        current_speaker = ""
        def flush() -> None:
            nonlocal current, current_speaker
            if current:
                segments.append({"text": " ".join(current), "explicit_speaker": current_speaker})
            current = []
            current_speaker = ""
        for line in text_lines:
            label_only = re.match(r"^([A-Za-z][A-Za-z0-9 .'-]+):$", line)
            inline_label = re.match(r"^([A-Za-z][A-Za-z0-9 .'-]+):\s+(.+)$", line)
            bracket_label = re.match(r"^\[\s*([A-Za-z][A-Za-z0-9 #.'-]+)\s*\]$", line)
            bracket_inline = re.match(r"^\[\s*([A-Za-z][A-Za-z0-9 #.'-]+)\s*\]\s+(.+)$", line)
            if dashed and re.match(r"^-\s+", line):
                flush()
                current = [re.sub(r"^-\s+", "", line)]
            elif label_only and (not label_only.group(1).isupper() or known_label(label_only.group(1))):
                flush()
                current_speaker = label_only.group(1)
            elif inline_label and (not inline_label.group(1).isupper() or known_label(inline_label.group(1))):
                flush()
                current_speaker = inline_label.group(1)
                current = [inline_label.group(2)]
            elif bracket_label and not is_sound_label(bracket_label.group(1)):
                flush()
                current_speaker = bracket_label.group(1).strip()
            elif bracket_inline and not is_sound_label(bracket_inline.group(1)):
                flush()
                current_speaker = bracket_inline.group(1).strip()
                current = [bracket_inline.group(2)]
            else:
                current.append(line)
        flush()
        for subindex, segment in enumerate(segments):
            text = segment["text"]
            # Some Season 1 DVD subtitle tracks end with a disc-authoring credit
            # after the episode itself. It is not part of the aired transcript.
            if normalize(text) == "i made this":
                continue
            if text:
                cues.append({"number": number, "subindex": subindex, "text": text,
                             "explicit_speaker": segment["explicit_speaker"]})
    return cues, source_cues


def parse_reference(path: Path) -> list[RefTurn]:
    raw = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    lines = [re.sub(r"\s+", " ", line).strip() for line in raw.splitlines()]
    turns: list[RefTurn] = []
    scene = 0
    location = ""
    current_speaker = ""
    expecting_location = False
    for line in lines:
        if not line:
            continue
        scene_match = re.match(r"^SCENE (\d+)(?:\s+(.+))?$", line)
        if scene_match:
            scene = int(scene_match.group(1))
            location = (scene_match.group(2) or "").replace(";", " · ")
            current_speaker = ""
            expecting_location = not bool(location)
            continue
        if scene == 0:
            continue
        if re.fullmatch(r"[-* ]{8,}", line) or "OPENING CREDITS" in line:
            current_speaker = ""
            continue
        speaker_match = re.match(r"^([A-Z][A-Z0-9 .'-]+):\s*(.*)$", line)
        embedded_speaker = re.search(r"\)\s*([A-Z][A-Z0-9 .'-]+):\s*(.*)$", line)
        if expecting_location:
            if line.startswith("(") or speaker_match:
                location = f"Scene {scene:02d}"
                expecting_location = False
            else:
                location = line.replace(";", " · ")
                expecting_location = False
                continue
        match = speaker_match or embedded_speaker
        if match:
            current_speaker = SPEAKER_NAMES.get(match.group(1), match.group(1).title())
            dialogue = match.group(2).strip()
            if dialogue:
                turns.append(RefTurn(current_speaker, dialogue, scene, location))
            continue
        if line.startswith("("):
            continue
        if current_speaker:
            turns.append(RefTurn(current_speaker, line, scene, location))
    return turns


def similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a in b:
        return 0.99
    if b in a:
        return 0.94
    a_words = a.split()
    b_words = b.split()
    if len(b_words) > len(a_words):
        best = 0.0
        target = len(a_words)
        for width in range(max(1, target - 2), min(len(b_words), target + 4) + 1):
            for start in range(0, len(b_words) - width + 1):
                window = " ".join(b_words[start:start + width])
                best = max(best, SequenceMatcher(None, a, window).ratio())
        return best
    return SequenceMatcher(None, a, b).ratio()


def cue_kind(text: str) -> str:
    stripped = re.sub(r"\([^)]*\)|\[[^]]*\]", "", text)
    stripped = re.sub(r"[♪♫\W_]+", "", stripped, flags=re.UNICODE).strip()
    if not stripped:
        return "sound"
    if re.fullmatch(r"[\[(].*[\])]", text.strip()):
        return "sound"
    return "dialogue"


def cue_override(overrides: dict, cue: dict):
    manual_key = f'{cue["number"]}.{cue.get("subindex", 0)}'
    for key in (manual_key, str(cue["number"]), cue["number"]):
        if key in overrides:
            return overrides[key]
    for key, value in overrides.items():
        match = re.fullmatch(r"(\d+)-(\d+)", str(key))
        if match and int(match.group(1)) <= cue["number"] <= int(match.group(2)):
            return value
    return None


def readable_case(value: str) -> str:
    value = value.strip()
    if not value:
        return value
    if value.startswith("(") and value.endswith(")"):
        return value.lower()
    result = value.lower()
    for source, replacement in sorted(PROPER_CASE.items(), key=lambda item: -len(item[0])):
        boundary = "" if re.search(r"[^a-z0-9]", source) else r"\b"
        result = re.sub(rf"{boundary}{re.escape(source)}{boundary}", replacement, result, flags=re.I)
    result = re.sub(r"\bi\b", "I", result)
    result = re.sub(r"(^|(?<=[.!?]\s))([a-z])", lambda m: m.group(1) + m.group(2).upper(), result)
    return result


def align(cues: list[dict], turns: list[RefTurn], manual_speakers: dict[int, str] | None = None,
          scene_locations: dict[int, str] | None = None,
          scene_overrides: dict[str, dict] | None = None) -> list[dict]:
    manual_speakers = manual_speakers or {}
    scene_locations = scene_locations or {}
    scene_overrides = scene_overrides or {}
    ref_words: list[str] = []
    ref_meta: list[tuple[str, int, str, int]] = []
    for index, turn in enumerate(turns):
        for word in normalize(turn.text).split():
            ref_words.append(word)
            ref_meta.append((turn.speaker, turn.scene, turn.location, index))

    cue_words: list[str] = []
    cue_word_owner: list[int] = []
    display_text: dict[int, str] = {}
    explicit_tags: dict[int, str] = {}
    kinds: dict[int, str] = {}
    for index, cue in enumerate(cues):
        kinds[index] = cue_kind(cue["text"])
        if cue.get("explicit_speaker"):
            explicit_tags[index] = cue["explicit_speaker"]
        display_text[index] = cue["text"]
        if kinds[index] == "dialogue":
            for word in normalize(display_text[index]).split():
                cue_words.append(word)
                cue_word_owner.append(index)

    votes: dict[int, list[tuple[str, int, str, int]]] = {i: [] for i in range(len(cues))}
    matcher = SequenceMatcher(None, ref_words, cue_words, autojunk=False)
    for match in matcher.get_matching_blocks():
        for offset in range(match.size):
            cue_index = cue_word_owner[match.b + offset]
            votes[cue_index].append(ref_meta[match.a + offset])

    sequential_matches: dict[int, tuple[tuple[str, int, str, int], float]] = {}
    reference_cursor = 0
    for index, cue in enumerate(cues):
        if kinds[index] != "dialogue" or not turns:
            continue
        cue_text = normalize(display_text[index])
        start = max(0, reference_cursor - 1)
        stop = min(len(turns), reference_cursor + 29)
        ranked = []
        for ref_i in range(start, stop):
            match_score = similarity(cue_text, normalize(turns[ref_i].text))
            ranked.append((match_score - max(0, ref_i - reference_cursor) * 0.002, match_score, ref_i))
        if ranked:
            _, match_score, ref_i = max(ranked)
            if match_score >= 0.52:
                turn = turns[ref_i]
                sequential_matches[index] = ((turn.speaker, turn.scene, turn.location, ref_i), match_score)
                reference_cursor = max(reference_cursor, ref_i)

    results = []
    previous_dialogue = None
    last_scene = 1
    last_location = "Scene 01"
    next_dialogue_meta: dict[int, tuple[str, int, str, int]] = {}
    next_vote_at: dict[int, int] = {}
    upcoming = None
    upcoming_at = None
    for index in range(len(cues) - 1, -1, -1):
        if votes[index]:
            upcoming = Counter(votes[index]).most_common(1)[0][0]
            upcoming_at = index
        if upcoming:
            next_dialogue_meta[index] = upcoming
            next_vote_at[index] = upcoming_at

    previous_vote_meta: dict[int, tuple[str, int, str, int]] = {}
    previous_vote_at: dict[int, int] = {}
    previous = None
    previous_at = None
    for index in range(len(cues)):
        if votes[index]:
            previous = Counter(votes[index]).most_common(1)[0][0]
            previous_at = index
        if previous:
            previous_vote_meta[index] = previous
            previous_vote_at[index] = previous_at

    for index, cue in enumerate(cues):
        kind = kinds[index]
        if votes[index]:
            chosen, count = Counter(votes[index]).most_common(1)[0]
            speaker, scene, location, ref_index = chosen
            word_count = max(1, len(normalize(display_text[index]).split()))
            score = count / word_count
            previous_dialogue = chosen
        else:
            before = previous_vote_meta.get(index)
            after = next_dialogue_meta.get(index)
            # An unmatched subtitle line normally continues the preceding turn.
            # Prefer that local continuity over interpolating between distant,
            # repeated phrases elsewhere in the reference transcript.
            chosen = previous_dialogue or before or after or ("Unknown Speaker", 1, "Scene 01", 0)
            if kind == "dialogue" and before and after:
                before_ref = before[3]
                after_ref = after[3]
                lo, hi = sorted((before_ref, after_ref))
                candidates = range(max(0, lo - 1), min(len(turns), hi + 2))
                cue_text = normalize(display_text[index])
                ranked = sorted(
                    ((similarity(cue_text, normalize(turns[ref_i].text)), ref_i) for ref_i in candidates),
                    reverse=True,
                )
                if ranked and ranked[0][0] >= 0.42:
                    ref_i = ranked[0][1]
                    turn = turns[ref_i]
                    chosen = (turn.speaker, turn.scene, turn.location, ref_i)
                elif previous_dialogue:
                    chosen = previous_dialogue
                elif before_ref == after_ref:
                    chosen = before
                else:
                    before_at = previous_vote_at[index]
                    after_at = next_vote_at[index]
                    ratio = (index - before_at) / max(1, after_at - before_at)
                    ref_i = round(before_ref + ratio * (after_ref - before_ref))
                    ref_i = max(0, min(len(turns) - 1, ref_i))
                    turn = turns[ref_i]
                    chosen = (turn.speaker, turn.scene, turn.location, ref_i)
            speaker, scene, location, ref_index = chosen
            score = 0.0 if kind == "dialogue" else 1.0

        sequential = sequential_matches.get(index)
        if sequential and (score < 0.58 or sequential[1] >= score + 0.08):
            chosen, score = sequential
            speaker, scene, location, ref_index = chosen

        tag = explicit_tags.get(index)
        if tag:
            canonical = SPEAKER_NAMES.get(tag.upper(), tag.title())
            if tag.lower() == "man" and score >= 0.5:
                canonical = speaker
            elif tag.lower() == "woman" and score >= 0.5:
                canonical = speaker
            speaker = canonical
        speaker = SPEAKER_NAMES.get(speaker.upper(), speaker)
        speaker = cue_override(manual_speakers, cue) or speaker
        scene_override = cue_override(scene_overrides, cue)
        if scene_override:
            scene = int(scene_override["scene"])
            location = scene_override.get("location", f"Scene {scene:02d}")
        location = scene_locations.get(scene, location)
        if kind == "dialogue" and scene < last_scene and not scene_override:
            scene = last_scene
            location = last_location
        if kind == "sound":
            speaker = "Sound"
        else:
            last_scene = scene
            last_location = location
            previous_dialogue = (speaker, scene, location, ref_index)

        results.append({**cue, "text": display_text[index], "speaker": speaker,
                        "scene": scene, "location": location,
                        "score": round(score, 3), "kind": kind,
                        "reference_index": ref_index})
    return results


def group_entries(aligned: list[dict]) -> list[dict]:
    grouped = []
    for item in aligned:
        if (grouped and item["kind"] == "dialogue" and grouped[-1]["kind"] == "dialogue"
                and item["speaker"] == grouped[-1]["speaker"]
                and item["scene"] == grouped[-1]["scene"]):
            grouped[-1]["text"] += " " + item["text"]
            grouped[-1]["score"] = min(grouped[-1]["score"], item["score"])
            grouped[-1]["cue_end"] = item["number"]
        else:
            grouped.append({**item, "cue_start": item["number"], "cue_end": item["number"]})
    for item in grouped:
        item["text"] = readable_case(item["text"])
    return grouped


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("srt", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--episode", required=True)
    parser.add_argument("--code", required=True)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--episode-number", type=int, required=True)
    parser.add_argument("--airdate", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--previous-url", default="/transcripts/")
    parser.add_argument("--previous-title", default="Transcript archive")
    parser.add_argument("--next-url", default="")
    parser.add_argument("--next-title", default="")
    parser.add_argument("--pilot-overrides", action="store_true")
    parser.add_argument("--speaker-overrides", type=Path)
    parser.add_argument("--scene-overrides", type=Path)
    parser.add_argument("--cue-splits", type=Path)
    args = parser.parse_args()
    cue_splits = {}
    if args.cue_splits:
        cue_splits = json.loads(args.cue_splits.read_text(encoding="utf-8"))
    cues, source_cue_count = parse_srt(args.srt, cue_splits)
    turns = parse_reference(args.reference)
    speaker_overrides = {}
    if args.speaker_overrides:
        speaker_overrides = json.loads(args.speaker_overrides.read_text(encoding="utf-8"))
    if args.pilot_overrides:
        speaker_overrides = {**PILOT_MANUAL_SPEAKERS, **speaker_overrides}
    scene_overrides = {}
    if args.scene_overrides:
        scene_overrides = json.loads(args.scene_overrides.read_text(encoding="utf-8"))
    aligned = align(
        cues,
        turns,
        speaker_overrides,
        PILOT_SCENE_LOCATIONS if args.pilot_overrides else {},
        scene_overrides,
    )
    grouped = group_entries(aligned)
    payload = {
        "episode": args.episode,
        "production_code": args.code,
        "season": args.season,
        "episode_number": args.episode_number,
        "airdate": args.airdate,
        "slug": args.slug,
        "previous_url": args.previous_url,
        "previous_title": args.previous_title,
        "next_url": args.next_url,
        "next_title": args.next_title,
        "source_cues": source_cue_count,
        "entries": grouped,
        "review": {
            "low_confidence_cues": [x for x in aligned if x["kind"] == "dialogue" and x["score"] < 0.58],
            "mean_score": round(sum(x["score"] for x in aligned if x["kind"] == "dialogue") /
                                len([x for x in aligned if x["kind"] == "dialogue"]), 3),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
