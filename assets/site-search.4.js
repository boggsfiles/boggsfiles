/* Site-wide search.
 *
 * Pagefind does the index work; this file is the front of it. Three things here are deliberate:
 *
 *  1. Results are grouped by what they are. "Squeeze" is legitimately a transcript, a screencap
 *     gallery and a Script vs. Screen comparison, and a flat list buries that.
 *
 *  2. There is a relevance floor. Pagefind falls back to fuzzy matching, so a typo like "zzzzqq"
 *     still returns a page. A result has to actually contain one of the typed words, in its title
 *     or its excerpt, or it is dropped - better to say nothing than to answer confidently wrong.
 *
 *  3. A transcript hit hands off to the dialogue filter already on that page. The link carries
 *     ?q=, and on arrival we fill #transcript-search and fire its input event, so the reader lands
 *     on the matching lines rather than at the top of a 50,000-word page.
 */
(() => {
  window.__bfSearchBuild = 4;   // read this to confirm which build is actually running
  const SECTIONS = [
    [/^\/transcripts\//, 'Transcripts'],
    [/^\/script-vs-screen\//, 'Script vs. Screen'],
    [/^\/screencaps\//, 'Screencaps'],
    [/^\/script-text\//, 'Scripts'],   // the OCR'd script text, weighted below dialogue
    [/^\/scripts\//, 'Scripts'],
    [/^\/(x-files-)?dailies\//, 'Dailies'],
    [/^\/gag-reels\//, 'Gag Reels'],
    [/^\/(misc-)?memorabilia\/|^\/production-documents\//, 'Documents'],
  ];
  const ORDER = ['Transcripts', 'Script vs. Screen', 'Screencaps', 'Scripts',
                 'Dailies', 'Gag Reels', 'Documents', 'Pages'];
  const sectionOf = (url) => (SECTIONS.find(([re]) => re.test(url)) || [, 'Pages'])[1];
  const strip = (html) => (html || '').replace(/<[^>]*>/g, '');
  const tokens = (q) => q.toLowerCase().match(/[\p{L}\p{N}]{3,}/gu) || [];

  /* The relevance floor.
   *
   * Pagefind reaches rather than returning nothing: searching "xyzzyplugh" matched the single
   * letter X in "Brand X", and "zzzzqq" matched "zz". But it also stems and fuzzes usefully --
   * "bees" legitimately matches "bee" - so an exact-string test threw away 200 good results.
   *
   * The rule that separates the two: the word Pagefind matched has to share a real prefix with
   * the word that was typed, and be of comparable length. One letter of a ten-letter query is
   * not a match; "bee" for "bees" is. */
  const clean = (w) => w.replace(/[^\p{L}\p{N}]/gu, '').toLowerCase();
  const shared = (a, b) => { let i = 0; while (i < a.length && i < b.length && a[i] === b[i]) i++; return i; };
  const matched = (hit, words) => {
    if (!words.length) return true;
    const marks = [...(hit.excerpt || '').matchAll(/<mark>(.*?)<\/mark>/g)]
      .map((m) => clean(strip(m[1]))).filter(Boolean);
    const title = hit.title.toLowerCase();
    return words.some((w) => title.includes(w) || marks.some((m) =>
      shared(m, w) >= Math.min(w.length, 3) && Math.abs(m.length - w.length) <= 3));
  };



  /* --- the frame a line was actually said on ----------------------------------------------
   *
   * A transcript page gets one thumbnail, but a search is about one line, so the page-level
   * still was arbitrary -- searching "tofutti" returned a man on a bus. Each episode ships a
   * small frames.json mapping the start of a line to the nearest screencap frame, built from
   * the subtitle timecodes. It is fetched only for results about to be shown, and only once
   * per episode. If anything is missing the episode still is left exactly as it was. */
  const frameCache = new Map();
  const plain = (s) => (s || '').replace(/<[^>]*>/g, ' ')
    .toLowerCase().replace(/[^a-z0-9 ]/g, '').replace(/\s+/g, ' ').trim();

  async function momentFrame(url, excerpt) {
    if (!/^\/transcripts\//.test(url)) return null;
    if (!frameCache.has(url)) {
      frameCache.set(url, fetch(url + 'frames.json')
        .then((r) => (r.ok ? r.json() : null)).catch(() => null));
    }
    const rows = await frameCache.get(url);
    if (!rows) return null;
    const hay = plain(excerpt);
    let best = null;
    for (const [key, frame] of rows) {          // longest matching line wins
      if (key.length > (best ? best[0].length : 0) && hay.includes(key)) best = [key, frame];
    }
    return best ? best[1] : null;
  }

  /* --- the handoff, for readers arriving from a search result ------------------------------ */
  const handoff = () => {
    const q = new URLSearchParams(location.search).get('q');
    const input = document.getElementById('transcript-search');
    if (!q || !input) return;
    input.value = q;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.scrollIntoView({ block: 'center' });
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', handoff);
  } else {
    handoff();
  }

  const header = document.querySelector('.bf-header');
  if (!header) return;
  const inner = header.querySelector('.bf-inner') || header;

  /* --- trigger ----------------------------------------------------------------------------- */
  const open = document.createElement('button');
  open.type = 'button';
  open.className = 'bf-search-open';
  open.setAttribute('aria-label', 'Search the archive');
  open.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
    'aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4.2-4.2"/></svg>';
  const menu = inner.querySelector('.bf-menu');
  menu ? inner.insertBefore(open, menu) : inner.appendChild(open);

  /* --- overlay ----------------------------------------------------------------------------- */
  const panel = document.createElement('div');
  panel.className = 'bf-search';
  panel.hidden = true;
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-modal', 'true');
  panel.setAttribute('aria-label', 'Search the archive');
  panel.innerHTML =
    '<div class="bf-search-bar">' +
      '<input type="search" autocomplete="off" spellcheck="false" ' +
        'placeholder="Search episodes, dialogue, documents…" aria-label="Search the archive">' +
      '<button type="button" class="bf-search-close">Esc</button>' +
    '</div>' +
    '<p class="bf-search-status"></p>' +
    '<div class="bf-search-results"></div>' +
    '<p class="bf-search-hint">Searches every page: 232 transcripts, screencaps, scripts, ' +
      'dailies and production documents.</p>';
  document.body.appendChild(panel);

  const input = panel.querySelector('input');
  const status = panel.querySelector('.bf-search-status');
  const results = panel.querySelector('.bf-search-results');
  const hint = panel.querySelector('.bf-search-hint');

  let pagefind = null;      // loaded on first open, not on every page view
  let loading = null;
  let seq = 0;              // guards against a slow query landing after a newer one
  let lastFocus = null;

  const load = () => (loading ||= import('/pagefind/pagefind.js')
    .then(async (m) => { await m.init(); pagefind = m; })
    .catch(() => { loading = null; throw new Error('index unavailable'); }));

  const setOpen = (show) => {
    panel.hidden = !show;
    document.documentElement.style.overflow = show ? 'hidden' : '';
    open.setAttribute('aria-expanded', String(show));
    if (show) {
      lastFocus = document.activeElement;
      load().catch(() => { status.textContent = 'Search is unavailable right now.'; });
      input.focus();
      input.select();
    } else if (lastFocus) {
      lastFocus.focus();
    }
  };

  const render = (query, hits, capped) => {
    results.textContent = '';
    hint.hidden = !!query;
    if (!query) { status.textContent = ''; return; }
    if (!hits.length) {
      status.textContent = 'No results for “' + query + '”';
      return;
    }
    // Say so when the list is truncated, rather than reporting 60 as if it were the total.
    status.textContent = hits.length + (capped ? '+' : '') +
      (hits.length === 1 && !capped ? ' result' : ' results');
    const groups = new Map();
    hits.forEach((h) => {
      const g = sectionOf(h.url);
      (groups.get(g) || groups.set(g, []).get(g)).push(h);
    });
    ORDER.filter((g) => groups.has(g)).forEach((g) => {
      const box = document.createElement('section');
      box.className = 'bf-search-group';
      box.innerHTML = '<h2>' + g + '<i>' + groups.get(g).length + '</i></h2>';
      groups.get(g).forEach((h) => {
        const a = document.createElement('a');
        a.className = 'bf-search-hit';
        // Transcript pages carry the query through so their own dialogue filter picks it up.
        a.href = g === 'Transcripts' ? h.url + '?q=' + encodeURIComponent(query) : h.url;
        // The thumbnail is stamped on at index time (see tools/build_search.py); a transcript
        // borrows a frame from its episode's gallery, never that gallery's opening frame.
        // An imageless hit still reserves the column, so the text keeps one left edge down
        // the list. The spacer draws nothing -- an empty bordered box would read as a hole.
        a.innerHTML = (h.image ? '<img alt="" loading="lazy">' : '<i class="bf-hit-gap"></i>')
          + '<div class="bf-hit-text"><b></b><span>' + h.excerpt + '</span></div>';
        if (h.image) {
          const im = a.querySelector('img');
          im.src = h.image;
          // then, if this is a line of dialogue, swap in the frame it was said on
          momentFrame(h.url, h.excerpt).then((f) => {
            if (f) im.src = h.image.replace(/\/thumb\/\d+\.jpg$/,
              '/thumb/' + String(f).padStart(9, '0') + '.jpg');
          });
          // A frame that 404s is swapped for the spacer, not removed: removing it collapsed
          // the row and that one result sat further left than every other.
          im.addEventListener('error', () => im.replaceWith(
            Object.assign(document.createElement('i'), {className: 'bf-hit-gap'})));
        }
        a.querySelector('b').textContent = h.title;
        box.appendChild(a);
      });
      results.appendChild(box);
    });
  };

  const run = async (query) => {
    const mine = ++seq;
    if (!query) return render('', []);
    try { await load(); } catch { status.textContent = 'Search is unavailable right now.'; return; }
    const found = await pagefind.search(query);
    if (mine !== seq) return;                       // a newer keystroke already won
    const words = tokens(query);
    const CAP = 60;   // enough to fill the panel; loading every fragment would be wasteful
    const data = await Promise.all(found.results.slice(0, CAP).map((r) => r.data()));
    if (mine !== seq) return;
    const hits = data.map((d) => ({
      url: d.url.replace(/index\.html$/, ''),
      title: d.meta?.title || d.url,
      excerpt: d.excerpt || '',
      image: d.meta && d.meta.image,
    })).filter((h) => {
      return matched(h, words);
    });
    render(query, hits, found.results.length > CAP);
  };

  let timer;
  input.addEventListener('input', () => {
    clearTimeout(timer);
    const q = input.value.trim();
    timer = setTimeout(() => run(q), 120);
  });

  /* --- keyboard ---------------------------------------------------------------------------- */
  open.addEventListener('click', () => setOpen(true));
  panel.querySelector('.bf-search-close').addEventListener('click', () => setOpen(false));
  panel.addEventListener('click', (e) => { if (e.target === panel) setOpen(false); });

  document.addEventListener('keydown', (e) => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.isContentEditable;
    if ((e.key === '/' && !typing) || ((e.metaKey || e.ctrlKey) && e.key === 'k')) {
      e.preventDefault();
      setOpen(true);
    } else if (e.key === 'Escape' && !panel.hidden) {
      setOpen(false);
    }
  });

  panel.addEventListener('keydown', (e) => {
    if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
    const hits = [...panel.querySelectorAll('.bf-search-hit')];
    if (!hits.length) return;
    e.preventDefault();
    const at = hits.indexOf(document.activeElement);
    const next = e.key === 'ArrowDown'
      ? (at + 1) % hits.length
      : (at <= 0 ? hits.length - 1 : at - 1);
    hits.forEach((h) => h.classList.remove('is-active'));
    hits[next].classList.add('is-active');
    hits[next].focus();
  });
})();
