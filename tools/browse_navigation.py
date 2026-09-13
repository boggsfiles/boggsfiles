"""Shared previous/next navigation matching the script season arrows."""
from html import escape
ASSET = '<link rel="stylesheet" href="/assets/browse-navigation.css?v=3">'
def navigation(previous=None, following=None, label="Episode navigation"):
    links=[]
    for direction,item in (("prev",previous),("next",following)):
        if not item: continue
        url,title=item
        arrow="←" if direction=="prev" else "→"
        content=f'<span aria-hidden="true">{arrow}</span><b>{escape(title)}</b>'
        links.append(f'<a class="browse-link browse-{direction}" href="{escape(url,quote=True)}" aria-label="{ "Previous" if direction=="prev" else "Next" }: {escape(title,quote=True)}">{content}</a>')
    items="".join(links)
    return f'<nav class="browse-rail" aria-label="{label}">{items}</nav><nav class="browse-bottom" aria-label="{label}">{items}</nav>' if items else ''
