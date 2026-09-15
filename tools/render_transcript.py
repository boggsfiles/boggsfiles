#!/usr/bin/env python3
"""Render a Boggsfiles transcript page from a prepared JSON dataset."""

from __future__ import annotations

import argparse
import html
import json
from collections import defaultdict
from pathlib import Path
from transcript_header import HEADER, ASSETS
from browse_navigation import navigation, ASSET as NAV_ASSET


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render(data: dict) -> str:
    episode = data["episode"]
    season = int(data["season"])
    episode_number = int(data.get("episode_number", 1))
    season_episode_total = 20 if season == 9 else 21 if season == 8 else 22 if season in (6,7) else 20 if season == 5 else 25 if season == 2 else 24
    production_code = data["production_code"]
    airdate = data.get("airdate", "September 10, 1993")
    previous_url = data.get("previous_url", "/transcripts/")
    previous_title = data.get("previous_title", "Transcript archive")
    next_url = data.get("next_url", "")
    next_title = data.get("next_title", "")
    scenes: dict[int, list[dict]] = defaultdict(list)
    for entry in data["entries"]:
        scenes[int(entry["scene"])].append(entry)

    scene_html = []
    for scene_number, entries in sorted(scenes.items()):
        location = entries[0]["location"]
        rows = []
        for entry in entries:
            text = esc(entry["text"])
            if entry["kind"] == "sound":
                rows.append(
                    f'<div class="transcript-entry sound" data-search="sound {text.lower()}">'
                    f'<p>{text}</p></div>'
                )
            else:
                speaker = esc(entry["speaker"])
                search = esc(f'{entry["speaker"]} {entry["text"]}'.lower())
                rows.append(
                    f'<article class="transcript-entry dialogue" data-search="{search}">'
                    f'<h3>{speaker}</h3><p>{text}</p></article>'
                )
        scene_html.append(
            f'<section class="scene" id="scene-{scene_number}">'
            f'<div class="scene-head"><span>Scene {scene_number:02d}</span><h2>{esc(location)}</h2></div>'
            f'<div class="scene-dialogue">{"".join(rows)}</div></section>'
        )

    entry_count = sum(1 for entry in data["entries"] if entry["kind"] == "dialogue")
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{esc(episode)} Transcript - Boggsfiles</title>
  <meta name="description" content="Read the character-labelled transcript for The X-Files {esc(episode)}, prepared from the official DVD subtitles.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Libre+Caslon+Display&family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/transcript.css">
{ASSETS}{NAV_ASSET}</head>
<body>
  {HEADER}
  <main>
    <section class="transcript-hero"><div class="shell"><div class="crumb"><a href="/transcripts/">Transcripts</a> <span>/</span> <a href="/transcripts/season-{season}/">Season {season}</a> <span>/</span> {esc(episode)}</div><div class="hero-grid"><div><div class="eyebrow">Season {season} · Episode {('19–20' if season == 9 and episode_number == 19 else episode_number)}</div><h1>{esc(episode)}</h1><p>Character-labelled dialogue prepared from the official DVD subtitle track.</p></div><div class="episode-file"><span>Production code</span><b>{esc(production_code)}</b><small>Original airdate · {esc(airdate)}</small></div></div></div></section>
    <div class="search-rail"><div class="shell search-inner"><label for="transcript-search">Search this transcript</label><div class="search-box"><input id="transcript-search" type="search" placeholder="Search dialogue or character…" autocomplete="off"><span aria-hidden="true">⌕</span></div><div id="search-count" aria-live="polite">{entry_count} dialogue entries</div></div></div>
    <div class="shell transcript-layout">
      <aside class="episode-notes"><div class="note-block"><span>File</span><b>{('19–20' if season == 9 and episode_number == 19 else f'{episode_number:02d}')} / {season_episode_total}</b></div><div class="note-block"><span>Source</span><b>Season {season} DVD subtitles</b></div><div class="note-block"><span>Format</span><b>Dialogue + speaker identification</b></div><p>No timestamps are displayed. Sound descriptions from the subtitle track are retained in italics.</p></aside>
      <div class="transcript-body">{''.join(scene_html)}<div id="no-results" hidden><b>No matching dialogue</b><p>Try another character, phrase, or keyword.</p></div></div>
    </div>
    <section class="method"><div class="shell"><span>About this transcript</span><p>The dialogue comes from the official DVD subtitle track supplied by Boggsfiles. Speaker and scene attribution was cross-checked against character-labelled reference material. Subtitle wording is preserved while capitalization and spacing are standardized for easier reading.</p></div></section>
    {navigation((previous_url,previous_title) if previous_url else None,(next_url,next_title) if next_url else None,"Transcript navigation")}
  </main>
  <footer><div class="shell footer-row">BOGGSFILES · TRANSCRIPT ARCHIVE <span><a href="/">Home</a> · <a href="/transcripts/">All transcripts</a></span></div></footer>
  <script>
    const input = document.getElementById('transcript-search');
    const entries = [...document.querySelectorAll('.transcript-entry')];
    const scenes = [...document.querySelectorAll('.scene')];
    const count = document.getElementById('search-count');
    const empty = document.getElementById('no-results');
    input.addEventListener('input', () => {{
      const query = input.value.trim().toLowerCase();
      let visibleDialogue = 0;
      entries.forEach(entry => {{
        const show = !query || entry.dataset.search.includes(query);
        entry.hidden = !show;
        if (show && entry.classList.contains('dialogue')) visibleDialogue++;
      }});
      scenes.forEach(scene => {{ scene.hidden = !scene.querySelector('.transcript-entry:not([hidden])'); }});
      empty.hidden = entries.some(entry => !entry.hidden);
      count.textContent = query ? `${{visibleDialogue}} matching dialogue ${{visibleDialogue === 1 ? 'entry' : 'entries'}}` : '{entry_count} dialogue entries';
    }});
  </script>
</body>
</html>'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()
