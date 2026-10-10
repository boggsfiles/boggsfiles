// Count opens of archive files hosted on Google Drive. GA can't see inside Drive, so record the
// click on our side instead, named by episode and draft rather than an opaque Drive URL.
// window.bfDescribeFile is exposed so tools/check_site.mjs can audit every link's name before publishing.
window.bfDescribeFile = (link) => {
  const tidy = (text) => (text || '').replace(/[↗→]/g, '').replace(/\s+/g, ' ').trim();
  const text = (root, selector) => tidy(root.querySelector(selector)?.textContent);
  // Each archive page lays its links out differently, so name the file from the card it sits in.
  const describe = () => {
    const script = link.closest('.episode');
    if (script) {
      // The production code moved out of the headline and under the airdate, so read it from
      // there. Without it two episodes are named "3" and "731", which names nothing.
      const named = [text(script, 'h2'), text(script, '.episode-code')].filter(Boolean).join(' ');
      return ['Script', named, tidy(link.textContent)];
    }
    if (location.pathname.startsWith('/script-vs-screen/')) return ['Script', text(document, 'h1'), tidy(link.textContent)];
    // Script text pages: "Quagmire 3X22" with "Pink · machine-read text…" beneath, named to match the season pages
    if (location.pathname.startsWith('/script-text/')) return ['Script', text(document, 'h1'), text(document, 'h1 + p').split(' · ')[0]];
    const callSheet = link.closest('.call-episode');
    if (callSheet) return ['Call sheet', `${text(callSheet, 'h2')} ${text(callSheet, '.call-episode-head span')}`, tidy(link.textContent)];
    if (link.matches('.comic-issue')) return ['Comic', `Comic ${text(link, 'b')}`, ''];
    if (link.matches('.schedule-card')) {
      // Schedule cards: <h2>Redux</h2> over "5X02 · Blue revision" or "1X10 · Shooting Schedule · Blue revision"
      const kind = link.matches('.oneliner-card') ? 'Oneline schedule' : 'Shooting schedule';
      const [code, ...rest] = text(link, '.schedule-code').split(' · ');
      const version = rest.filter((part) => !/schedule/i.test(part)).join(' · ');
      return [kind, `${text(link, 'h2')} ${code} ${kind}`, version];
    }
    if (link.matches('.recent-item')) {
      // Homepage "New" tiles: "Season 3 · Shooting Schedule, Blue" or "Season 7 · Blue partial draft, 7ABX01"
      const [what, detail = ''] = text(link, 'p').replace(/^Season \d+\s*·\s*/, '').split(/,\s*/);
      if (/draft/i.test(what)) return ['Script', text(link, 'h3'), what];
      if (/shooting schedule/i.test(what)) return ['Shooting schedule', `${text(link, 'h3')} Shooting schedule`, detail];
      return ['File', text(link, 'h3'), what];
    }
    const name = tidy(link.getAttribute('aria-label')).replace(/^(Open|View) /, '').replace(/\s*\(opens in a new tab\)$/, '') || tidy(link.textContent);
    const kind = /oneline/i.test(name) ? 'Oneline schedule' : /shooting schedule/i.test(name) ? 'Shooting schedule' : 'File';
    return [kind, name, ''];
  };
  let [type, title, version] = describe();
  // Safety net for page layouts added later: a name that can't identify the file on its own
  // ("Open the scan", "28", nothing at all) gets the page's title in front of it.
  const vague = /^#?\d*$/.test(title) || /^(open|view|read|download|see|click)\b/i.test(title);
  if (vague) {
    const page = text(document, 'h1') || tidy(document.title.split(/[:|]/)[0]);
    title = title ? `${page} · ${title}` : page;
  }
  const label = version ? `${title} · ${version}` : title;
  // guessed: no rule above knew this layout. Still sent, but check_site.mjs flags it so a rule gets written.
  return { file_type: type, file_title: title, file_version: version, file_label: label, guessed: vague || type === 'File' };
};

document.addEventListener('click', (event) => {
  const link = event.target.closest('a[href*="drive.google.com"], a[href*="docs.google.com"]');
  if (!link || typeof gtag !== 'function') return;
  const { guessed, ...file } = window.bfDescribeFile(link);
  gtag('event', 'open_file', { ...file, link_url: link.href });
});

(() => {
  const header = document.querySelector('.bf-header');
  if (!header) return;
  const button = header.querySelector('.bf-menu');
  const navigation = header.querySelector('.bf-navlinks');
  const setOpen = (open) => {
    navigation.classList.toggle('is-open', open);
    button.setAttribute('aria-expanded', String(open));
    button.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  };
  button.addEventListener('click', () => setOpen(button.getAttribute('aria-expanded') !== 'true'));
  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a')) setOpen(false);
  });
  header.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
      setOpen(false);
      button.focus();
    }
  });
})();

// Site-wide search. Loaded from here rather than added to 518 pages and a dozen builders: this
// file is already on every page that has a header. The stylesheet and script are fetched here,
// but the index itself is not touched until someone actually opens the search.
(() => {
  if (!document.querySelector('.bf-header')) return;
  // Versioned in the filename, not a query string: a ?v= bump was served correctly by the
  // origin and still executed stale in the browser, so the name changes when the file does.
  const css = document.createElement('link');
  css.rel = 'stylesheet';
  css.href = '/assets/site-search.4.css';
  document.head.appendChild(css);
  const js = document.createElement('script');
  js.src = '/assets/site-search.4.js';
  js.defer = true;
  document.head.appendChild(js);
})();
