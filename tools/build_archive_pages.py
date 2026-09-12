from __future__ import annotations

import html
import http.cookiejar
import io
import re
import time
import urllib.request
import urllib.error
from pathlib import Path

from lxml import html as lhtml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
LEGACY = "https://sites.google.com/view/boggsfiles"
UA = {"User-Agent": "Mozilla/5.0"}

SCRIPT_PAGES = [
    (f"Season {n}", f"season-{n}") for n in range(1, 10)
] + [
    ("Fight the Future", "fight-the-future"),
    ("I Want to Believe", "i-want-to-believe"),
    ("Miscellaneous Script Partials", "misc-script-partials"),
]

DAILIES = [
    ("Aubrey", "aubrey"), ("Ascension", "ascension"),
    ("Paper Hearts", "paper-hearts"),
    ("The Field Where I Died", "the-field-where-i-died"),
    ("Tunguska", "tunguska"), ("Sanguinarium", "sanguinarium"),
    ("Irresistible", "irresistible"), ("Quagmire", "quagmire"),
    ("Musings of a Cigarette Smoking Man", "musings-of-a-cigarette-smoking-man"),
    ("Deep Throat", "deep-throat"), ("Kitsunegari", "kitsunegari"),
    ("Apocrypha", "apocrypha"),
    ("Die Hand Die Verletzt", "die-hand-die-verletzt"),
    ("Born Again", "born-again"),
]

MEMORABILIA = [
    ("X-Files Shooting Schedules", "x-files-shooting-schedules"),
    ("X-Files Call Sheets", "x-files-call-sheets"),
    ("William B. Davis Interview", "william-b-davis-interview"),
    ("Comics", "comics"), ("Oneliners", "oneliners"),
]

BOILERPLATE = (
    "This site will be of plenty of interest", "This site contains copyrighted",
    "The material on this site is distributed", "If you wish to use copyrighted",
    "If you are the writer of any", "Enjoy!!!", "Fair Use Notice",
)


def fetch(path: str):
    page_url = LEGACY + path
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    request = urllib.request.Request(page_url, headers=UA)
    with opener.open(request, timeout=45) as response:
        return lhtml.fromstring(response.read()), opener, page_url


def save_image(opener, page_url: str, source_url: str, key: str) -> str:
    photo_dir = DIST / "assets" / "archive-photos"
    photo_dir.mkdir(parents=True, exist_ok=True)
    destination = photo_dir / f"{key}.webp"
    if not destination.exists():
        for attempt in range(10):
            if attempt:
                cookie_jar = http.cookiejar.CookieJar()
                opener = urllib.request.build_opener(
                    urllib.request.HTTPCookieProcessor(cookie_jar)
                )
                with opener.open(
                    urllib.request.Request(page_url, headers=UA), timeout=45
                ) as response:
                    refreshed = lhtml.fromstring(response.read())
                image_index = int(key.rsplit("-", 1)[-1]) - 1
                if key.startswith("scripts-"):
                    refreshed_cards = script_cards(refreshed)
                    if image_index < len(refreshed_cards):
                        source_url = refreshed_cards[image_index]["image"]
                else:
                    refreshed_images = media_items(refreshed)[1]
                    if image_index < len(refreshed_images):
                        source_url = refreshed_images[image_index]
            request = urllib.request.Request(source_url, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": page_url,
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Sec-Fetch-Dest": "image",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "cross-site",
            })
            try:
                with opener.open(request, timeout=45) as response:
                    image = Image.open(io.BytesIO(response.read())).convert("RGB")
                image.thumbnail((1400, 900), Image.Resampling.LANCZOS)
                image.save(destination, "WEBP", quality=84, method=6)
                break
            except urllib.error.HTTPError:
                if attempt == 9:
                    raise
                time.sleep(min(2 * (attempt + 1), 10))
    return f"/assets/archive-photos/{destination.name}"


def clean(value: str) -> str:
    return " ".join(value.split())


def unique(values):
    seen = set()
    for value in values:
        if value and value not in seen:
            seen.add(value)
            yield value


def nav(active: str = "") -> str:
    links = [
        ("Archive", "/archive/"), ("Scripts", "/scripts/"),
        ("Transcripts", "/transcripts/"),
        ("Script vs. Screen", "/#script-vs-screen"),
        ("Dailies", "/dailies/"), ("Memorabilia", "/memorabilia/"),
        ("Resources", "/resources/"),
    ]
    items = "".join(
        f'<a{(" class=\"active\"" if label == active else "")} href="{url}">{label}</a>'
        for label, url in links
    )
    return f'<header><nav class="shell"><a class="brand" href="/">BOGGS<span class="x">X</span>FILES</a><div class="links">{items}</div></nav></header>'


def page(title: str, body: str, active: str) -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — BoggsFiles</title><meta name="description" content="Browse {html.escape(title)} in the BoggsFiles X-Files archive."><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Libre+Caslon+Display&family=Oswald:wght@300;400;500;600&display=swap" rel="stylesheet"><link rel="stylesheet" href="/assets/archive-detail.css"></head><body>{nav(active)}<main>{body}</main><footer><div class="shell footer-row">BOGGSFILES · THE X-FILES ARCHIVE <span><a href="/">Home</a> · <a href="/{active.lower().replace(' ', '-')}/">Back to {html.escape(active)}</a></span></div></footer></body></html>'''


def write_route(route: str, content: str):
    destination = DIST / route.strip("/") / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def content_blocks(document):
    return document.xpath('//div[contains(@class,"oKdM2c") and contains(@class,"ZZyype")]')


def script_cards(document) -> list[dict]:
    blocks = content_blocks(document)
    last_image = ""
    cards = []
    for block in blocks:
        images = block.xpath('.//img[@src]/@src')
        if images:
            last_image = images[0]
        draft_links = []
        for anchor in block.xpath('.//a[contains(@href,"drive.google.com")]'):
            label = clean(anchor.text_content()) or "Open file"
            draft_links.append((label, anchor.get("href")))
        if not draft_links:
            continue
        paragraphs = [clean(p.text_content()) for p in block.xpath('.//p') if clean(p.text_content())]
        title = paragraphs[0] if paragraphs else "Archived Script"
        cards.append({"title": title, "image": last_image, "links": draft_links})
        last_image = ""
    return cards


def build_script_page(label: str, slug: str):
    document, opener, page_url = fetch(f"/x-files-scripts-by-season/{slug}")
    cards = script_cards(document)
    cards_html = []
    for index, card in enumerate(cards, 1):
        local_image = save_image(opener, page_url, card["image"], f"scripts-{slug}-{index:02d}") if card["image"] else ""
        image_style = f' style="background-image:url(\'{html.escape(local_image, quote=True)}\')"' if local_image else ""
        buttons = "".join(
            f'<a class="draft" href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">{html.escape(name)} ↗</a>'
            for name, url in card["links"]
        )
        cards_html.append(f'<article class="episode"><div class="episode-image"{image_style}></div><div class="episode-body"><span class="episode-no">File {index:02d}</span><h2>{html.escape(card["title"])}</h2><div class="drafts">{buttons}</div></div></article>')
    body = f'''<section class="archive-hero"><div class="shell"><div class="crumb"><a href="/scripts/">Scripts</a> &nbsp;/&nbsp; {html.escape(label)}</div><h1>{html.escape(label)}</h1><p>Original drafts and production revisions, preserved together for close reading and comparison.</p><div class="archive-meta"><span>{len(cards)} episode files</span><span>Original scans</span><span>Opens in Google Drive</span></div></div></section><div class="shell"><div class="archive-grid">{"".join(cards_html)}</div></div>'''
    write_route(f"x-files-scripts-by-season/{slug}", page(label, body, "Scripts"))


def descriptive_text(document) -> list[str]:
    paragraphs = []
    for node in document.xpath('//p'):
        text = clean(node.text_content())
        if len(text) < 24 or any(text.startswith(prefix) for prefix in BOILERPLATE):
            continue
        paragraphs.append(text)
    return list(unique(paragraphs))[:8]


def media_items(document):
    frames = list(unique(document.xpath('//iframe/@data-src | //iframe/@src')))
    attribute_urls = [str(value) for value in document.xpath('//@*')]
    for url in attribute_urls:
        match = re.search(r'https://(?:www\.)?youtube\.com/(?:live|watch\?v=)/?([A-Za-z0-9_-]{6,})', url)
        if match:
            frames.append(f"https://www.youtube.com/embed/{match.group(1)}")
    frames = list(unique(frames))
    images = list(unique(document.xpath('//img[@src]/@src')))
    images = [url for url in images if "googleusercontent.com" in url and "favicon" not in url]
    return frames, images


def resource_links(document, page_label: str):
    resources = []
    for embed in document.xpath('//*[@data-embed-open-url]'):
        url = embed.get("data-embed-open-url") or ""
        labels = embed.xpath('.//span[contains(@class,"pB4Yfc")]/text() | .//*[@aria-label]/@aria-label')
        label = clean(labels[0]) if labels else ""
        if label.startswith("Drive, "):
            label = label[7:]
        if page_label == "X-Files Call Sheets":
            label = label.removesuffix(".pdf").replace("CAll Sheet", "Call Sheet")
        if label and url.startswith("http"):
            resources.append((label, url))
    for anchor in document.xpath('//a[@href]'):
        url = anchor.get("href") or ""
        label = clean(anchor.text_content())
        if not label or url.startswith("#") or "/view/boggsfiles" in url or "forms.gle" in url:
            continue
        if url.startswith("http") and not url.startswith("https://accounts.google"):
            resources.append((label, url))
    known_urls = {url for _, url in resources}
    archive_number = 1
    generic_label = "Comic" if page_label == "Comics" else "Call sheet" if "Call Sheets" in page_label else "Archive file"
    for value in document.xpath('//@*'):
        url = str(value).replace('\\u003d', '=')
        match = re.search(r'https://drive\.google\.com/open\?id=[A-Za-z0-9_-]+', url)
        if match and match.group(0) not in known_urls:
            file_url = match.group(0)
            resources.append((f"{generic_label} {archive_number:03d}", file_url))
            known_urls.add(file_url)
            archive_number += 1
    return list(unique(resources))


def build_detail(label: str, route: str, legacy_path: str, active: str, kind: str):
    document, opener, page_url = fetch(legacy_path)
    frames, images = media_items(document)
    resources = resource_links(document, label)
    paragraphs = descriptive_text(document)
    if label == "X-Files Call Sheets":
        file_labels = [name.removesuffix(".pdf") for name, _ in resources]
        paragraphs = [
            text for text in paragraphs
            if not text.startswith("Here you can study scripts")
            and not any(name.startswith(text + " Call Sheet") for name in file_labels)
        ]
    copy = "".join(f'<p class="detail-copy">{html.escape(text)}</p>' for text in paragraphs)
    media = []
    for src in frames:
        media.append(f'<div class="media"><iframe src="{html.escape(src, quote=True)}" loading="lazy" allow="autoplay; encrypted-media" allowfullscreen title="{html.escape(label)} archive media"></iframe></div>')
    if not frames:
        image_key = re.sub(r"[^a-z0-9]+", "-", route.lower()).strip("-")
        for index, src in enumerate(images[:18], 1):
            local_src = save_image(opener, page_url, src, f"{image_key}-{index:02d}")
            media.append(f'<div class="media"><img src="{html.escape(local_src, quote=True)}" loading="lazy" alt="{html.escape(label)} archive image"></div>')
    resource_html = ""
    if resources:
        rows = "".join(f'<div class="resource"><span>{html.escape(name)}</span><a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">Open source ↗</a></div>' for name, url in resources)
        resource_html = f'<div class="resource-list">{rows}</div>'
    media_html = f'<div class="media-grid">{"".join(media)}</div>' if media else ("" if resources else '<div class="empty-note">This archive entry is preserved in the collection. Additional media will be added as it is prepared for the new site.</div>')
    body = f'''<section class="archive-hero"><div class="shell"><div class="crumb"><a href="/{active.lower()}/">{html.escape(active)}</a> &nbsp;/&nbsp; {html.escape(label)}</div><h1>{html.escape(label)}</h1><p>{html.escape(kind)}</p><div class="archive-meta"><span>Original archive material</span><span>Preserved by Boggsfiles</span></div></div></section><div class="shell detail-wrap">{copy}{media_html}{resource_html}</div>'''
    write_route(route, page(label, body, active))


def main():
    for label, slug in SCRIPT_PAGES:
        build_script_page(label, slug)
        print(f"Built scripts: {label}", flush=True)
    for label, slug in DAILIES:
        build_detail(label, f"x-files-dailies/{slug}", f"/x-files-dailies/{slug}", "Dailies", "Rare production dailies and alternate footage from The X-Files.")
        print(f"Built dailies: {label}", flush=True)
    for label, slug in MEMORABILIA:
        build_detail(label, f"misc-memorabilia/{slug}", f"/misc-memorabilia/{slug}", "Memorabilia", "Original documents, interviews, and artifacts from the Boggsfiles collection.")
        print(f"Built memorabilia: {label}", flush=True)


if __name__ == "__main__":
    main()
