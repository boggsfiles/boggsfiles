/* Site-wide search.
 *
 * Pagefind does the index work; this file is the front of it. Five things here are deliberate:
 *
 *  1. A line typed the way it was said is looked up word for word first. Those results are
 *     listed on their own, in episode order, above the looser matches. If the line is not in the
 *     archive as typed, the dialog says so instead of presenting loose matches as the answer.
 *
 *  2. Results are grouped by what they are. "Squeeze" is legitimately a transcript, a screencap
 *     gallery and a set of script drafts, and a flat list buries that. Each collection is asked
 *     for its own best results, so 60 script drafts cannot crowd the episode out of the list.
 *
 *  3. Every row says what it is: the collection, and for an episode its season, episode number
 *     and production code. A script row names its draft and the page of the scan. The index
 *     carries that description for each page (tools/build_search.py writes it).
 *
 *  4. There is a relevance floor. Pagefind falls back to fuzzy matching, so a typo like "zzzzqq"
 *     still returns a page. A result has to actually contain the typed words, in its title
 *     or its excerpt, or it is dropped - better to say nothing than to answer confidently wrong.
 *
 *  5. A transcript hit hands off to the dialogue filter already on that page. The link carries
 *     ?q=, and on arrival we fill #transcript-search and fire its input event, so the reader lands
 *     on the matching lines rather than at the top of a 50,000-word page.
 */
(() => {
  window.__bfSearchBuild = 6;   // read this to confirm which build is actually running

  // The words on screen, in one place so they are easy to change.
  const TEXT = {
    exact: 'Word for word',
    close: 'Close matches',
    notExact: 'Didn’t find that word for word. Here’s what’s close.',
    nothing: 'Didn’t find that word for word, or anything close.',
    more: 'Show more',
  };

  // Collections, in the order they are listed. tools/build_search.py has the same list.
  const ORDER = ['Transcripts', 'Script vs. Screen', 'Screencaps', 'Scripts', 'Dailies',
                 'Gag Reels', 'Documents', 'Rare 35mm', 'Locations', 'Pages'];
  const FIRST = { Transcripts: 6 };   // rows a collection shows before "Show more"
  const FIRST_OTHER = 4;
  const MORE = 20;                    // rows each "Show more" adds

  const strip = (html) => (html || '').replace(/<[^>]*>/g, '');
  const tokens = (q) => q.toLowerCase().match(/[\p{L}\p{N}]{3,}/gu) || [];
  const clean = (w) => w.replace(/[^\p{L}\p{N}]/gu, '').toLowerCase();

  /* What was typed, made comparable with what is on the page. Phones type curly apostrophes and
   * the subtitles use straight ones; quotation marks would end the quoted search early. */
  const tidy = (q) => q.replace(/[‘’ʼ′`]/g, "'")
    .replace(/["“”„«»]/g, ' ').replace(/\s+/g, ' ').trim();
  const wordsOf = (q) => tidy(q).split(' ').map(clean).filter(Boolean);

  /* The relevance floor.
   *
   * Pagefind reaches rather than returning nothing: searching "xyzzyplugh" matched the single
   * letter X in "Brand X", and "zzzzqq" matched "zz". But it also stems and fuzzes usefully --
   * "bees" legitimately matches "bee" - so an exact-string test threw away 200 good results.
   *
   * The rule that separates the two: the word Pagefind matched has to share a real prefix with
   * the word that was typed, and be of comparable length. One letter of a ten-letter query is
   * not a match; "bee" for "bees" is. */
  const shared = (a, b) => { let i = 0; while (i < a.length && i < b.length && a[i] === b[i]) i++; return i; };
  const near = (m, w) => shared(m, w) >= Math.min(w.length, 3) && Math.abs(m.length - w.length) <= 3;
  const marksOf = (hit) => [...(hit.raw || '').matchAll(/<mark>(.*?)<\/mark>/g)]
    .map((m) => clean(strip(m[1]))).filter(Boolean);
  const matched = (hit, words) => {
    if (!words.length) return true;
    const marks = marksOf(hit);
    const title = hit.title.toLowerCase();
    return words.some((w) => title.includes(w) || marks.some((m) => near(m, w)));
  };

  /* The floor for a line of several words.
   *
   * Every transcript contains "not", "be" and "the", so a line from another show still came
   * back with results built out of its small words. What makes a close match close is the words
   * that carry the line: they have to turn up together, in the one passage Pagefind excerpts.
   * A line made only of small words ("to be or not to be") has no close match worth showing. */
  const SMALL = new Set(('a an and are as at be been but by can cant could did didnt do does dont for from get go '
    + 'going got had has have he her here him his how i if im in is isnt it its ive just know let like me my no not '
    + 'now of oh on one or our out she so some than that thats the their them then there theres these they this '
    + 'to too up us was we well were what when where which who why will with wont would yes you your youre').split(' '));
  const carrying = (words) => [...new Set(words.filter((w) => w.length >= 3 && !SMALL.has(w)))];
  const covers = (hit, words, weighty) => {
    const marks = marksOf(hit);
    const title = clean(hit.title);
    const got = (list) => list.filter((w) => title.includes(w) || marks.some((m) => near(m, w))).length;
    const most = (n) => (n <= 3 ? n : Math.ceil(n * 0.75));
    const all = [...new Set(words)];
    // the words that carry the line, and most of the line as a whole
    return got(weighty) >= most(weighty.length) && got(all) >= most(all.length);
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

  async function momentFrame(url, excerpt, line, phrase) {
    if (!/^\/transcripts\//.test(url)) return null;
    if (!frameCache.has(url)) {
      frameCache.set(url, fetch(url + 'frames.json')
        .then((r) => (r.ok ? r.json() : null)).catch(() => null));
    }
    const rows = await frameCache.get(url);
    if (!rows) return null;
    // A word-for-word hit knows which line it is: take the caption that starts nearest before
    // the matched words, not the longest caption anywhere in the excerpt.
    const at = line && phrase ? line.indexOf(phrase) : -1;
    if (at >= 0) {
      let best = null;
      for (const [key, frame] of rows) {
        const i = line.indexOf(key);
        if (i >= 0 && i <= at && (!best || i > best[0] || (i === best[0] && key.length > best[1].length))) best = [i, key, frame];
      }
      if (best) return best[2];
    }
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
    // A title-only hit ("bad blood" on Bad Blood) matches no line of dialogue. Landing on an empty
    // filter reads as a broken page, so drop the query and show the whole transcript instead.
    const empty = document.getElementById('no-results');
    if (empty && !empty.hidden) {
      input.value = '';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      history.replaceState(null, '', location.pathname + location.hash);
      return;
    }
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
  let names = [];           // every page's name, to tell when someone typed a title

  // filters() fetches the list of collections and page names; without it a search reports no counts.
  const load = () => (loading ||= import('/pagefind/pagefind.js')
    .then(async (m) => { await m.init(); names = Object.keys((await m.filters()).name || {}); pagefind = m; })
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

  /* --- one result -------------------------------------------------------------------------- */

  // The index puts this lone mark between a speaker and their line, so a quoted search cannot
  // run from one into the other ("Fox Mulder: It's me." is not "Mulder, it's me"). It is not for
  // reading, so it never reaches the screen. Script text carries a "[page 12]" marker at the top
  // of each page of the scan, which is how a row can say which page to open.
  const BREAK = '¦';
  const squash = (s) => s.replace(/[^\p{L}\p{N}]/gu, '').toLowerCase();
  const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const pageMark = (w, i) => (w[i] === '[page' && /^\d+\]$/.test(w[i + 1] || ''))
    || (w[i - 1] === '[page' && /^\d+\]$/.test(w[i]));
  const scanPage = (url, w, at) => {
    if (!/^\/script-text\//.test(url)) return '';
    for (let i = Math.min(at, w.length - 2); i >= 0; i--) {
      if (w[i] === '[page' && /^\d+\]$/.test(w[i + 1])) return 'scan page ' + parseInt(w[i + 1], 10);
    }
    return '';
  };

  /* Where the typed words stand on the page exactly as typed, as [first word, last word].
   *
   * Pagefind's quoted search is nearly that, but it also accepts another form of a word: "I
   * wanted to believe" comes back for "I want to believe". That is close, not word for word,
   * so each result is checked against the page text before it is listed as word for word. */
  const exactSpot = (w, locations, target) => {
    for (const a of locations) {
      let text = '';
      for (let b = a; b < w.length && text.length < target.length; b++) {
        // "Clyde Bruckman" is in "Clyde Bruckman's Final Repose": a possessive on the last word still counts
        if (text + squash(w[b].replace(/['’]s(?=[^\p{L}\p{N}]*$)/u, '')) === target) return [a, b];
        text += squash(w[b]);
        if (text === target) return [a, b];
      }
    }
    return null;
  };

  // target: the typed words run together, when this result came from the quoted search
  const toHit = (d, target) => {
    const w = (d.content || '').trim().split(/\s+/);
    const raw = d.excerpt || '';
    const hit = { url: d.url.replace(/index\.html$/, ''), title: d.meta?.title || d.url,
      image: d.meta && d.meta.image, raw, exact: false, said: '', line: '' };
    const spot = target ? exactSpot(w, d.locations || [], target) : null;
    let at = d.locations?.[0] ?? 0;
    if (spot) {
      // Our own excerpt, cut around the words themselves, so the line is always in view and
      // lit as one phrase.
      const [a, b] = spot;
      const read = (from, to) => {
        const out = [];
        for (let i = Math.max(0, from); i < Math.min(w.length, to); i++) {
          if (w[i] !== BREAK && !pageMark(w, i)) out.push(w[i]);
        }
        return esc(out.join(' '));
      };
      hit.exact = true;
      hit.excerpt = read(a - 10, a) + ' <mark>' + read(a, b + 1) + '</mark> ' + read(b + 1, b + 15);
      // the words as they stand on the page, and the line they sit in
      hit.said = w.slice(a, b + 1).join(' ').replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, '');
      let from = a; while (from > 0 && a - from < 80 && w[from - 1] !== BREAK) from--;
      let to = b + 1; while (to < w.length && to - b < 80 && w[to] !== BREAK) to++;
      hit.line = plain(w.slice(from, to).join(' '));
      at = a;
    } else {
      // Pagefind's excerpt, with the marks taken out and a run of matched words joined into
      // one highlight.
      hit.excerpt = raw.replace(/\s*¦\s*/g, ' ').replace(/\[page \d+\]\s*/g, '')
        .replace(/<\/mark>(\s*)<mark>/g, '$1');
      // which match the excerpt shows, to name the right page of a script
      const shown = strip(raw).trim().split(/\s+/);
      const lead = strip(raw.split('<mark>')[0]).trim().split(/\s+/).filter(Boolean).length;
      for (const loc of d.locations || []) {
        if (w[loc - lead] === shown[0] && w[loc] === shown[lead]) { at = loc; break; }
      }
    }
    hit.what = [d.meta?.what, scanPage(hit.url, w, at)].filter(Boolean).join(' · ');
    return hit;
  };

  const row = (h, group, query) => {
    const a = document.createElement('a');
    a.className = 'bf-search-hit';
    // Transcript pages carry the query through so their own dialogue filter picks it up. A
    // word-for-word hit passes the words as the page has them ("Mulder, it's me"), because that
    // filter compares punctuation too and "mulder its me" would find nothing.
    const carry = h.exact && h.said ? h.said : query;
    a.href = group.name === 'Transcripts' ? h.url + '?q=' + encodeURIComponent(carry) : h.url;
    // The thumbnail is stamped on at index time (see tools/build_search.py); a transcript
    // borrows a frame from its episode's gallery, never that gallery's opening frame.
    // An imageless hit still reserves the column, so the text keeps one left edge down
    // the list. The spacer draws nothing -- an empty bordered box would read as a hole.
    a.innerHTML = (h.image ? '<img alt="" loading="lazy">' : '<i class="bf-hit-gap"></i>')
      + '<div class="bf-hit-text"><b></b><span class="bf-hit-what"></span><span>' + h.excerpt + '</span></div>';
    if (h.image) {
      const im = a.querySelector('img');
      im.src = h.image;
      // then, if this is a line of dialogue, swap in the frame it was said on
      momentFrame(h.url, h.excerpt, h.exact && h.line, h.exact && plain(h.said)).then((f) => {
        if (f) im.src = h.image.replace(/\/thumb\/\d+\.jpg$/,
          '/thumb/' + String(f).padStart(9, '0') + '.jpg');
      });
      // A frame that 404s is swapped for the spacer, not removed: removing it collapsed
      // the row and that one result sat further left than every other.
      im.addEventListener('error', () => im.replaceWith(
        Object.assign(document.createElement('i'), {className: 'bf-hit-gap'})));
    }
    a.querySelector('b').textContent = h.title;
    const what = a.querySelector('.bf-hit-what');
    if (h.what) what.textContent = h.what; else what.remove();
    return a;
  };

  /* --- one collection's results ------------------------------------------------------------
   *
   * Pagefind hands back every match as a cheap id; the text of a result is a separate small
   * file each. So a collection loads only the rows it is about to show, and "Show more" loads
   * the next few. `keep` is the test a row has to pass to be shown: the relevance floor for a
   * loose match, the page-text check for a word-for-word one. A row that fails is set aside. */
  const collection = (name, found, keep, more = {}) => ({
    name, found, keep, next: 0, ready: [], aside: [], shown: 0, counted: false, ...more });

  async function take(group, want, rounds) {
    while (group.ready.length < want && group.next < group.found.length && rounds-- > 0) {
      const batch = group.found.slice(group.next, group.next + Math.max(want, 6));
      group.next += batch.length;
      const data = await Promise.all(batch.map((r) => r.data()));
      data.map((d, i) => toHit(d, batch[i].target || group.target))
        .forEach((h) => (group.keep(h) ? group.ready : group.aside).push(h));
    }
    return group.ready.splice(0, want);
  }

  // How many results the collection is known to hold: everything offered, less what failed the test.
  const size = (g) => g.found.length - g.aside.length;

  const section = (group, hits, query, mine) => {
    const box = document.createElement('section');
    box.className = 'bf-search-group';
    const h2 = document.createElement('h2');
    h2.textContent = group.name;
    const count = group.counted ? h2.appendChild(document.createElement('i')) : null;
    box.appendChild(h2);
    hits.forEach((h) => box.appendChild(row(h, group, query)));
    group.shown = hits.length;
    const left = () => (group.counted ? size(group) - group.shown : group.ready.length + group.found.length - group.next);
    const more = document.createElement('button');
    more.type = 'button';
    more.className = 'bf-search-more';
    const label = () => {
      if (count) count.textContent = size(group);
      more.textContent = TEXT.more + (group.counted ? ' · ' + left() + ' left' : '');
    };
    label();
    more.addEventListener('click', async () => {
      more.disabled = true;
      const next = await take(group, MORE, 3);
      if (mine !== seq) return;
      const rows = next.map((h) => row(h, group, query));
      rows.forEach((r) => box.insertBefore(r, more));
      group.shown += rows.length;
      more.disabled = false;
      label();
      if (left() <= 0 || !rows.length) more.remove();
      (rows[0] || input).focus();
    });
    if (left() > 0) box.appendChild(more);
    return box;
  };

  const part = (label, count) => {
    const h = Object.assign(document.createElement('h2'), { className: 'bf-search-part', textContent: label });
    if (count) h.appendChild(Object.assign(document.createElement('i'), { textContent: count }));
    return h;
  };
  const note = (text) => Object.assign(document.createElement('p'), { className: 'bf-search-note', textContent: text });

  /* --- a search ---------------------------------------------------------------------------- */
  const run = async (typed) => {
    const mine = ++seq;
    const query = tidy(typed);
    hint.hidden = !!query;
    if (!query) { results.textContent = ''; status.textContent = ''; return; }
    try { await load(); } catch { status.textContent = 'Search is unavailable right now.'; return; }

    const words = wordsOf(query);
    const isLine = words.length >= 2;
    const weighty = carrying(words);
    const first = (g) => FIRST[g.name] || FIRST_OTHER;
    const kindsIn = (found) => {
      const counts = found.filters?.kind;
      if (!counts) return found.results.length ? [''] : [];      // an index without collections: one list
      return ORDER.filter((k) => counts[k] > 0);
    };
    const ask = (q, kind, sorted) => pagefind.search(q, {
      ...(kind ? { filters: { kind } } : {}), ...(sorted ? { sort: { order: 'asc' } } : {}) });

    // 1. Word for word: the quoted search, each collection in episode order.
    const exactGroups = [];
    const exactIds = new Set();
    if (isLine) {
      const quoted = '"' + query + '"';
      const all = await pagefind.search(quoted);
      if (mine !== seq) return;
      all.results.forEach((r) => exactIds.add(r.id));
      // A page called what was typed leads its collection, ahead of episode order: "Bad Blood"
      // should open with Bad Blood, not with the first episode where someone says it.
      const phrase = ' ' + words.join(' ');
      const titled = names.filter((n) => (' ' + n).includes(phrase)).slice(0, 40);
      for (const kind of kindsIn(all)) {
        let found = (await ask(quoted, kind, true)).results;
        if (kind && titled.length) {
          const lead = (await pagefind.search(quoted, { filters: { kind, name: { any: titled } }, sort: { order: 'asc' } })).results;
          const ids = new Set(lead.map((r) => r.id));
          found = [...lead, ...found.filter((r) => !ids.has(r.id))];
        }
        if (found.length) exactGroups.push(collection(kind || 'Results', found, (h) => h.exact, { counted: true, target: words.join('') }));
      }
      if (mine !== seq) return;
    }
    const exactRows = await Promise.all(exactGroups.map((g) => take(g, first(g), 2)));
    if (mine !== seq) return;

    // 2. A line remembered almost right is usually right for a stretch: "the truth is out here"
    // has "the truth is out" in it. When nothing is word for word, look for the line with a word
    // or two off either end. Those lead the close matches, in episode order.
    const stretches = new Map();      // collection -> results, each carrying the stretch it matched
    if (isLine && words.length >= 3 && !exactRows.some((rows) => rows.length)) {
      for (let len = words.length - 1; len >= Math.max(2, words.length - 2) && !stretches.size; len--) {
        for (let i = 0; i + len <= words.length; i++) {
          const piece = words.slice(i, i + len);
          if (!carrying(piece).length && len < 4) continue;     // "it is me" on its own says nothing
          const quoted = '"' + piece.join(' ') + '"';
          for (const kind of kindsIn(await pagefind.search(quoted))) {
            const list = stretches.get(kind) || stretches.set(kind, []).get(kind);
            const have = new Set(list.map((r) => r.id));
            (await ask(quoted, kind, true)).results.forEach((r) => {
              if (!have.has(r.id)) list.push(Object.assign(r, { target: piece.join('') }));
            });
          }
          if (mine !== seq) return;
        }
      }
    }

    // 3. Everything else that matches, each collection by relevance, minus what is already above.
    const closeGroups = [];
    const floor = isLine ? (h) => h.exact || covers(h, words, weighty) : (h) => matched(h, tokens(query));
    const loose = new Map();
    if (!isLine || weighty.length) {
      const all = await pagefind.search(query);
      if (mine !== seq) return;
      for (const kind of kindsIn(all)) {
        loose.set(kind, (await ask(query, kind, false)).results.filter((r) => !exactIds.has(r.id)));
      }
      if (mine !== seq) return;
    }
    for (const kind of new Set([...stretches.keys(), ...loose.keys()])) {
      const lead = stretches.get(kind) || [];
      const ids = new Set(lead.map((r) => r.id));
      const found = [...lead, ...(loose.get(kind) || []).filter((r) => !ids.has(r.id))];
      if (found.length) closeGroups.push(collection(kind || 'Results', found, floor, { counted: !isLine }));
    }
    // A result the quoted search offered that is not word for word on the page ("I wanted to
    // believe") is the closest match there is: it opens its collection's close matches.
    exactGroups.forEach((g) => {
      if (!g.aside.length) return;
      let twin = closeGroups.find((c) => c.name === g.name);
      if (!twin) closeGroups.push(twin = collection(g.name, [], () => true));
      twin.ready.unshift(...g.aside);
    });
    closeGroups.sort((a, b) => ORDER.indexOf(a.name) - ORDER.indexOf(b.name));
    const closeRows = await Promise.all(closeGroups.map((g) => take(g, first(g), 2)));
    if (mine !== seq) return;

    // 4. Draw. A collection where nothing passed its test is dropped, not shown empty.
    const exactShown = exactGroups.map((g, i) => [g, exactRows[i]]).filter(([, rows]) => rows.length);
    const closeShown = closeGroups.map((g, i) => [g, closeRows[i]]).filter(([, rows]) => rows.length);
    // Half a line is never found word for word. Hold "didn't find that" for a beat, so it is
    // said once the typing stops and not flashed between every two keystrokes.
    if (isLine && !exactShown.length) {
      await new Promise((r) => setTimeout(r, 400));
      if (mine !== seq) return;
    }
    results.textContent = '';
    if (!exactShown.length && !closeShown.length) {
      status.textContent = isLine ? '' : 'No results for “' + query + '”';
      if (isLine) results.appendChild(note(TEXT.nothing));
      return;
    }
    if (isLine) {
      // the count sits beside the heading, so the status line above has nothing to add
      status.textContent = '';
      if (exactShown.length) results.appendChild(part(TEXT.exact, exactShown.reduce((n, [g]) => n + size(g), 0)));
      else results.appendChild(note(TEXT.notExact));
      exactShown.forEach(([g, rows]) => results.appendChild(section(g, rows, query, mine)));
      if (closeShown.length) results.appendChild(part(TEXT.close));
    } else {
      const total = closeShown.reduce((n, [g]) => n + size(g), 0);
      status.textContent = total + (total === 1 ? ' result' : ' results');
    }
    closeShown.forEach(([g, rows]) => results.appendChild(section(g, rows, query, mine)));
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
    const hits = [...panel.querySelectorAll('.bf-search-hit, .bf-search-more')];
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
