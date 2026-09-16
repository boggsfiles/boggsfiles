#!/usr/bin/env python3
"""Monotonic transcript aligner.

Walks the subtitle cues and the speaker-labelled reference *in order*, so a
line can only match reference dialogue near the current position. This avoids
the scene-jumping of the global aligner in build_transcript.py. Intended for
long, script-derived references (feature films).

Usage: align_monotonic.py srt reference out.json --episode ... (same flags as build_transcript.py)
Optional: --overrides overrides.json  {"<cue>.<sub>": "Speaker", "<a>-<b>": "Speaker"}
          --proper "Word,Other Word"  extra proper nouns to keep capitalised
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
import build_transcript as bt

for _label, _name in {"WHITNEY": "Dakota Whitney", "DRUMMY": "Mosley Drummy", "FATHER JOE": "Father Joe", "FBI AGENT": "FBI Agent",
                      "MRS. FEARON": "Margaret Fearon", "MR. FEARON": "Blair Fearon", "MAN": "Man", "MAN 1": "Man", "MAN 2": "Man",
                      "DRIVER": "Driver", "COP": "Police Officer", "SKINNER": "Walter Skinner", "YBARRA": "Father Ybarra"}.items():
    bt.SPEAKER_NAMES.setdefault(_label, _name)

WINDOW_BACK, WINDOW_FWD = 2, 14
MATCH, WEAK = 0.60, 0.42

SDH_LABELS = {"mulder": "Fox Mulder", "scully": "Dana Scully", "skinner": "Walter Skinner",
              "whitney": "Dakota Whitney", "drummy": "Mosley Drummy", "father joe": "Father Joe", "fbi agent": "FBI Agent",
              "mrs. fearon": "Margaret Fearon", "mr. fearon": "Blair Fearon", "ybarra": "Father Ybarra", "father ybarra": "Father Ybarra",
              "cop": "Police Officer", "driver": "Driver", "man 1": "Man", "man 2": "Man", "man #1": "Man", "man #2": "Man", "man #3": "Man",
              "kurtzweil": "Dr. Alvin Kurtzweil", "cassidy": "Jana Cassidy", "byers": "John Fitzgerald Byers",
              "frohike": "Melvin Frohike", "langly": "Richard Langly"}


def label_to_speaker(label: str) -> str:
    key = re.sub(r"\s+", " ", label.strip().lower())
    key = re.sub(r"\s*(on phone|on tv|on laptop|on radio|on p\.a\.|on speaker|on intercom|on video|on tape|on monitor|over radio|over phone)$", "", key)
    if key in SDH_LABELS:
        return SDH_LABELS[key]
    return re.sub(r"(^|[\s\-/.])([a-z])", lambda m: m.group(1) + m.group(2).upper(), label.strip().lower())


def sim2(a: str, b: str) -> float:
    """Similarity that refuses to credit tiny fragments (e.g. "go") inside long lines."""
    if not a or not b:
        return 0.0
    wa, wb = len(a.split()), len(b.split())
    if wa < 3 or wb < 3:
        if a == b:
            return 1.0
        if min(wa, wb) >= 2 and (a in b or b in a) and min(len(a), len(b)) / max(len(a), len(b)) >= 0.5:
            return 0.9
        return 0.0
    if (a in b or b in a) and min(len(a), len(b)) / max(len(a), len(b)) < 0.35:
        from difflib import SequenceMatcher
        return SequenceMatcher(None, a, b).ratio()
    return bt.similarity(a, b)


def align(cues, turns, overrides):
    """Banded DP alignment: each dialogue cue is matched to at most one reference turn,
    in order; turns may be skipped. Matches need similarity >= MATCH to count."""
    dlg = [i for i, c in enumerate(cues) if bt.cue_kind(c["text"]) == "dialogue"]
    n, m = len(dlg), len(turns)
    tnorm = [bt.normalize(t.text) for t in turns]
    cnorm = [bt.normalize(cues[i]["text"]) for i in dlg]
    BAND = 60
    # similarity matrix within the band
    sim = {}
    for a in range(n):
        est = int(a * m / max(1, n))
        for j in range(max(0, est - BAND), min(m, est + BAND)):
            words = len(cnorm[a].split())
            s = sim2(cnorm[a], tnorm[j]) if words else 0.0
            if s >= MATCH:
                sim[(a, j)] = s
    # DP over (a, j): best score aligning first a cues with first j turns
    import functools
    NEG = -1e9
    best = [dict() for _ in range(n + 1)]
    best[0][0] = 0.0
    back = {}
    for a in range(n):
        est = int(a * m / max(1, n))
        js = range(max(0, est - BAND - 1), min(m, est + BAND) + 1)
        for j in js:
            cur = best[a].get(j)
            if cur is None:
                continue
            # skip this cue (no match)
            if best[a + 1].get(j, NEG) < cur - 0.05:
                best[a + 1][j] = cur - 0.05; back[(a + 1, j)] = (a, j, None)
            # skip a turn
            if j + 1 <= m and best[a].get(j + 1, NEG) < cur - 0.02:
                best[a][j + 1] = cur - 0.02; back[(a, j + 1)] = (a, j, None)
            # match cue a with turn j (and advance), or match and stay on j so a
            # script speech split across several subtitle cues can absorb them all
            s = sim.get((a, j))
            if s is not None:
                if j + 1 <= m and best[a + 1].get(j + 1, NEG) < cur + s:
                    best[a + 1][j + 1] = cur + s; back[(a + 1, j + 1)] = (a, j, s)
                if best[a + 1].get(j, NEG) < cur + s - 0.01:
                    best[a + 1][j] = cur + s - 0.01; back[(a + 1, j)] = (a, j, s)
    # pick the best end state
    j_end = max(best[n], key=lambda j: best[n][j])
    matched = {}
    a, j = n, j_end
    while (a, j) in back:
        pa, pj, s = back[(a, j)]
        if s is not None:
            matched[dlg[pa]] = (pj, s)
        a, j = pa, pj
    # assign speakers / scenes
    out = []; scene_seq = 0; scene_key = None; location = "Scene 01"; recent = []
    tnorm_all = [bt.normalize(t.text) for t in turns]
    last_turn = 0
    for idx, cue in enumerate(cues):
        kind = bt.cue_kind(cue["text"])
        if kind == "sound":
            out.append({**cue, "speaker": "Sound", "scene": max(scene_seq, 1), "location": location,
                        "kind": "sound", "score": 1.0, "part": 0})
            continue
        forced = bt.cue_override(overrides, cue)
        speaker, score = None, 0.0
        if idx in matched:
            j, s = matched[idx]; turn = turns[j]; last_turn = j
            if turn.scene != scene_key:
                scene_key = turn.scene; scene_seq += 1
                location = turn.location or f"Scene {scene_seq:02d}"; recent = []
            speaker, score = turn.speaker, s
        # continuation: SDH captions start a continued sentence in lowercase, and a cue with no
        # closing punctuation carries on in the next cue -- same speaker in both cases
        prev = next((o for o in reversed(out) if o["kind"] == "dialogue"), None)
        txt = cue["text"].strip()
        lower_start = bool(re.match(r"^[\(\[]?[a-z]", txt)) and not re.match(r"^(i|i'm|i'd|i'll|i've)\b", txt)
        open_prev = bool(prev) and not re.search(r"[.?!…\"”)\]]\s*$|--\s*$|—\s*$", prev["text"].strip())
        if prev and (lower_start or (open_prev and (idx not in matched or score < 0.8))) and not forced \
                and not cue.get("explicit_speaker") and prev["number"] >= cue["number"] - 1:
            speaker, score = prev["speaker"], 0.7
        if forced:
            speaker, score = forced, 1.0
        elif cue.get("explicit_speaker") and not bt.is_sound_label(cue["explicit_speaker"]):
            speaker, score = label_to_speaker(cue["explicit_speaker"]), 1.0
        if speaker is None and scene_key is not None:
            # scene-local fallback: the shooting draft often reorders or rewords lines
            cand = [(sim2(bt.normalize(cue["text"]), tnorm_all[j]), j) for j in range(len(turns)) if turns[j].scene == scene_key]
            if cand:
                sbest, jbest = max(cand)
                if sbest >= 0.5:
                    speaker, score = turns[jbest].speaker, round(sbest * 0.9, 2)
        if speaker is None:
            distinct = []
            for sp in reversed(recent):
                if sp not in distinct:
                    distinct.append(sp)
                if len(distinct) == 2:
                    break
            if len(distinct) == 2:
                speaker, score = distinct[1], 0.3
            elif distinct:
                speaker, score = distinct[0], 0.25
            else:
                speaker, score = "Unidentified speaker", 0.0
        recent.append(speaker)
        out.append({**cue, "speaker": speaker, "scene": max(scene_seq, 1), "location": location,
                    "kind": "dialogue", "score": round(score, 2), "part": 0})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("srt", type=Path); ap.add_argument("reference", type=Path); ap.add_argument("output", type=Path)
    for flag in ("--episode", "--code", "--airdate", "--slug"):
        ap.add_argument(flag, required=True)
    ap.add_argument("--season", type=int, default=0); ap.add_argument("--episode-number", type=int, default=1)
    ap.add_argument("--previous-url", default="/transcripts/"); ap.add_argument("--previous-title", default="Transcript archive")
    ap.add_argument("--next-url", default=""); ap.add_argument("--next-title", default="")
    ap.add_argument("--overrides", type=Path); ap.add_argument("--proper", default="")
    ap.add_argument("--reviewed", type=Path, help="reviewed JSON with 'speakers' and 'scenes' (cue -> location)")
    ap.add_argument("--movie", action="store_true"); ap.add_argument("--year", default="")
    ap.add_argument("--keep-case", action="store_true", help="captions are already mixed-case (Blu-ray SDH): don't lowercase and re-capitalise")
    ap.add_argument("--labels", default="", help="extra SDH speaker labels: 'GARNER=Garner,MR. O'MALLEY=Tad O'Malley'")
    a = ap.parse_args()
    for pair in [p for p in a.labels.split(",") if "=" in p]:
        k, v = pair.split("=", 1); bt.SPEAKER_NAMES[k.strip().upper()] = v.strip(); SDH_LABELS[k.strip().lower()] = v.strip()
    if a.keep_case:
        def _keep(value: str) -> str:
            value = re.sub(r"\s+", " ", value.strip())
            value = re.sub(r"\bi\b", "I", value)
            return re.sub(r"(^|(?<=[.!?]\s))([a-z])", lambda m: m.group(1) + m.group(2).upper(), value)
        bt.readable_case = _keep
        bt.ACCEPT_ALL_CAPS_LABELS = True
    for word in [w.strip() for w in a.proper.split(",") if w.strip()]:
        bt.PROPER_CASE[word.lower()] = word
    overrides = json.loads(a.overrides.read_text()) if a.overrides else {}
    scene_breaks = {}
    if a.reviewed:
        rev = json.loads(a.reviewed.read_text())
        overrides.update(rev.get("speakers", {}))
        scene_breaks = {int(k): v for k, v in rev.get("scenes", {}).items()}
    splits = rev.get("splits", {}) if a.reviewed else {}
    cues, source_cues = bt.parse_srt(a.srt, splits)
    # reviewed "text": cue number -> corrected caption text (OCR one-offs); "drop": cue numbers to remove
    fixes = rev.get("text", {}) if a.reviewed else {}
    drop = set(int(k) for k in rev.get("drop", [])) if a.reviewed else set()
    for c in cues:
        if str(c["number"]) in fixes and c.get("subindex", 0) == 0: c["text"] = fixes[str(c["number"])]
    cues = [c for c in cues if c["number"] not in drop]
    turns = bt.parse_reference(a.reference)
    aligned = align(cues, turns, overrides)
    if scene_breaks:
        # reviewed scene list replaces the script-derived scenes: a break applies
        # to the first cue at or after its cue number
        keys = sorted(scene_breaks); k = 0; seq = 0; loc = "Scene 01"
        for item in aligned:
            while k < len(keys) and keys[k] <= item["number"]:
                seq += 1; loc = scene_breaks[keys[k]]; k += 1
            item["scene"], item["location"] = max(seq, 1), loc
    entries = bt.group_entries(aligned)
    data = {"episode": a.episode, "season": a.season, "episode_number": a.episode_number,
            "production_code": a.code, "airdate": a.airdate, "slug": a.slug, "source_cues": source_cues,
            "previous_title": a.previous_title, "previous_url": a.previous_url,
            "next_title": a.next_title, "next_url": a.next_url, "movie": a.movie, "year": a.year,
            "entries": entries}
    a.output.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    low = [e for e in entries if e["kind"] == "dialogue" and e["score"] < 0.45]
    print(f"entries {len(entries)}  scenes {entries[-1]['scene']}  low-confidence {len(low)}")


if __name__ == "__main__":
    main()
