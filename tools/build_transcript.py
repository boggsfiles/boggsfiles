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
}

MANUAL_SPEAKERS = {
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
}

SCENE_LOCATIONS = {
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


def normalize(value: str) -> str:
    value = clean_markup(value).lower().replace("’", "'")
    value = re.sub(r"\b(?:um|uh|er)\b", " ", value)
    value = re.sub(r"[^a-z0-9']+", " ", value)
    words = [NUMBER_WORDS.get(word, word) for word in value.split()]
    return " ".join(words)


def parse_srt(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n")
    cues = []
    for block in re.split(r"\n{2,}", raw.strip()):
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            continue
        text = clean_markup(" ".join(lines[2:]))
        if text:
            cues.append({"number": int(lines[0]), "text": text})
    return cues


def parse_reference(path: Path) -> list[RefTurn]:
    raw = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n{2,}", raw) if p.strip()]
    turns: list[RefTurn] = []
    scene = 0
    location = ""
    current_speaker = ""
    expecting_location = False
    for paragraph in paragraphs:
        scene_match = re.match(r"^SCENE (\d+)(?:\s+(.+))?$", paragraph)
        if scene_match:
            scene = int(scene_match.group(1))
            location = (scene_match.group(2) or "").replace(";", " · ")
            current_speaker = ""
            expecting_location = not bool(location)
            continue
        if scene == 0:
            continue
        if expecting_location and not paragraph.startswith("("):
            location = paragraph.replace(";", " · ")
            expecting_location = False
            continue
        if paragraph.startswith("("):
            continue
        match = re.match(r"^([A]+)", paragraph)
        match = re.match(r"^([A-Z][A-Z0-9 .'-]+):\s*(.*)$", paragraph)
        if match:
            current_speaker = SPEAKER_NAMES.get(match.group(1), match.group(1).title())
            dialogue = match.group(2).strip()
            if dialogue:
                turns.append(RefTurn(current_speaker, dialogue, scene, location))
            continue
        if current_speaker:
            turns.append(RefTurn(current_speaker, paragraph, scene, location))
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
    stripped = re.sub(r"\([^)]*\)", "", text).strip()
    if not stripped:
        return "sound"
    if re.fullmatch(r"[\[(].*[\])]", text.strip()):
        return "sound"
    return "dialogue"


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


def align(cues: list[dict], turns: list[RefTurn]) -> list[dict]:
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
        explicit = re.match(r"^(Man|Woman|Mulder|Scully|Doctor|Nurse|Billy|Pilot):\s*(.*)$", cue["text"], re.I)
        if explicit:
            explicit_tags[index] = explicit.group(1).lower()
            display_text[index] = explicit.group(2).strip()
        else:
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

    results = []
    previous_dialogue = None
    next_dialogue_meta: dict[int, tuple[str, int, str, int]] = {}
    upcoming = None
    for index in range(len(cues) - 1, -1, -1):
        if votes[index]:
            upcoming = Counter(votes[index]).most_common(1)[0][0]
        if upcoming:
            next_dialogue_meta[index] = upcoming

    for index, cue in enumerate(cues):
        kind = kinds[index]
        if votes[index]:
            chosen, count = Counter(votes[index]).most_common(1)[0]
            speaker, scene, location, ref_index = chosen
            word_count = max(1, len(normalize(display_text[index]).split()))
            score = count / word_count
            previous_dialogue = chosen
        else:
            chosen = previous_dialogue or next_dialogue_meta.get(index) or (
                "Unknown Speaker", 1, "Collum National Forest, Northwest Oregon", 0)
            speaker, scene, location, ref_index = chosen
            score = 0.0 if kind == "dialogue" else 1.0

        tag = explicit_tags.get(index)
        if tag == "mulder":
            speaker = "Fox Mulder"
        elif tag == "scully":
            speaker = "Dana Scully"
        elif tag == "man" and score < 0.5:
            speaker = "Unidentified Man"
        elif tag == "woman" and score < 0.5:
            speaker = "Unidentified Woman"
        elif tag == "doctor":
            speaker = "Dr. Glass"
        elif tag == "nurse":
            speaker = "Nurse"
        elif tag == "billy":
            speaker = "Billy Miles"
        elif tag == "pilot":
            speaker = "Airline Pilot"
        speaker = MANUAL_SPEAKERS.get(cue["number"], speaker)
        if cue["number"] == 463:
            scene = 12
        location = SCENE_LOCATIONS.get(scene, location)
        if kind == "sound":
            speaker = "Sound"

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
    args = parser.parse_args()
    cues = parse_srt(args.srt)
    turns = parse_reference(args.reference)
    aligned = align(cues, turns)
    grouped = group_entries(aligned)
    payload = {
        "episode": "Pilot",
        "production_code": "1X79",
        "season": 1,
        "source_cues": len(cues),
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
