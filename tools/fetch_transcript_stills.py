#!/usr/bin/env python3
"""Fetch selected episode screen captures for the transcript gallery."""

from pathlib import Path
import io
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image


STILLS = {
    "pilot": "PilotBR217.jpg",
    "deep-throat": "DeepThroatBR23.jpg",
    "squeeze": "SqueezeBR20.jpg",
    "conduit": "ConduitBR262.jpg",
    "jersey-devil": "TheJerseyDevilBR21.jpg",
    "shadows": "ShadowsBR54.jpg",
    "ghost-in-the-machine": "GhostInTheMachineBR27.jpg",
    "ice": "IceBR216.jpg",
    "space": "SpaceBR167.jpg",
    "fallen-angel": "FallenAngelBR26.jpg",
    "eve": "EveBR94.jpg",
    "fire": "FireBR157.jpg",
    "beyond-the-sea": "BeyondTheSeaBR237.jpg",
    "gender-bender": "GenderBenderBR49.jpg",
    "lazarus": "LazarusBR01.jpg",
    "young-at-heart": "YoungAtHeartBR01.jpg",
    "ebe": "EBEBR44.jpg",
    "miracle-man": "MiracleManBR271.jpg",
    "shapes": "ShapesBR179.jpg",
    "darkness-falls": "DarknessFallsBR267.jpg",
}


def main() -> None:
    destination = Path("dist/assets/transcript-stills")
    destination.mkdir(parents=True, exist_ok=True)
    sources = {}
    headers = {"User-Agent": "Mozilla/5.0"}
    def fetch(item):
        slug, filename = item
        url = f"https://xfilesarchive.com/gallery/{filename}"
        request = urllib.request.Request(url, headers=headers)
        payload = urllib.request.urlopen(request, timeout=30).read()
        return slug, url, payload

    with ThreadPoolExecutor(max_workers=10) as pool:
      downloaded = list(pool.map(fetch, STILLS.items()))
    for slug, url, payload in downloaded:
        image = Image.open(io.BytesIO(payload)).convert("RGB")
        if image.width > 1280:
            image.thumbnail((1280, 1280))
        image.save(destination / f"{slug}.webp", "WEBP", quality=84, method=6)
        sources[slug] = url
    Path("tools/transcript-still-sources.json").write_text(
        json.dumps(sources, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
