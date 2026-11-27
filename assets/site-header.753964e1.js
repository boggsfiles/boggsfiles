// Pictures load from pics.boggsfiles.com. Some internet providers still cannot find that name, so
// a picture that will not load there is asked for once more at the older address, and the player
// posters (which report no error of their own) follow when one test picture fails.
(() => {
  const NEW = 'https://pics.boggsfiles.com/';
  const OLD = 'https://pub-df226d4134944457905024edfc4635fb.r2.dev/';
  const swap = (img) => {
    if (!(img instanceof HTMLImageElement) || !img.src.startsWith(NEW)) return false;
    img.src = OLD + img.src.slice(NEW.length);
    return true;
  };
  // At the window and in the capture phase, so it runs before any handler that gives up on the picture.
  window.addEventListener('error', (e) => { if (swap(e.target)) e.stopImmediatePropagation(); }, true);
  // Pictures that failed before this script ran.
  for (const img of document.images) if (img.complete && img.currentSrc && !img.naturalWidth) swap(img);
  const players = [...document.querySelectorAll('video[poster^="' + NEW + '"]')];
  if (players.length) {
    const test = new Image();
    test.onerror = () => players.forEach((v) => { v.poster = OLD + v.poster.slice(NEW.length); });
    test.src = players[0].poster;
  }
})();

// Count opens of archive files hosted on Google Drive. GA can't see inside Drive, so record the
// click on our side instead, named by episode and draft rather than an opaque Drive URL.
// window.bfDescribeFile is exposed so the site check can audit every link's name before publishing.
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
    if (location.pathname.startsWith('/script-vs-screen/')) {
      // "Revision report · 2X07 · Season 2…" above the title supplies the code, as on the season pages
      const code = text(document, '.hero .eyebrow').match(/\b[0-9A-Z]+X\d+\b/)?.[0];
      return ['Script', [text(document, 'h1'), code].filter(Boolean).join(' '), tidy(link.textContent)];
    }
    // Script text pages: "Quagmire 3X22" with "Pink · machine-read text…" beneath, named to match the season pages
    if (location.pathname.startsWith('/script-text/')) return ['Script', text(document, 'h1'), text(document, 'h1 + p').split(' · ')[0]];
    // Dailies scene rows: "Script, scene 20 · page 14" opens the draft's scan; the link carries the
    // episode and draft it names, so it counts under the same name as the season page button.
    if (link.closest('.media-script')) return ['Script', tidy(link.dataset.fileTitle), tidy(link.dataset.fileVersion)];
    // The mistake form is not an archive file: it is named here, and its clicks are counted on their own below.
    if (link.closest('.bf-fix')) return ['Form', 'Spot a mistake form', ''];
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
    fallback = true;
    return [kind, name, ''];
  };
  let fallback = false;
  let [type, title, version] = describe();
  // Safety net for page layouts added later: a name that can't identify the file on its own
  // ("Open the scan", "28", nothing at all) gets the page's title in front of it.
  // Only for links no rule above recognized: a rule knows its titles, and an episode really is called "3".
  const vague = fallback && (/^#?\d*$/.test(title) || /^(open|view|read|download|see|click)\b/i.test(title));
  if (vague) {
    const page = text(document, 'h1') || tidy(document.title.split(/[:|]/)[0]);
    title = title ? `${page} · ${title}` : page;
  }
  const label = version ? `${title} · ${version}` : title;
  // guessed: no rule above knew this layout. Still sent, but the site check flags it so a rule gets written.
  return { file_type: type, file_title: title, file_version: version, file_label: label, guessed: vague || type === 'File' };
};

// Video plays on every page with a player: dailies, gag reels, the unaired Pilot and the Fox promos
// on the Episodes pages. Uses GA's own video event names (video_start, video_progress,
// video_complete, with video_title, video_provider and video_percent) so they read as video in the
// reports, plus video_watch_time, whose video_seconds_watched feeds the "Video seconds watched"
// custom metric. Progress counts only what was actually played: dragging the slider ahead does not
// add watched time, so it cannot fake a 75% mark. Each milestone is sent once per video per page
// view: the signed-link script can swap the source mid-play when a link expires, and that must not
// count as a second play.
(() => {
  const sent = new WeakMap();
  const watched = new WeakMap();      // seconds actually played, per video
  const pending = new Map();          // seconds played but not yet reported, per video
  const last = new WeakMap();         // playhead at the previous timeupdate
  const MILESTONES = [10, 25, 50, 75];
  const path = location.pathname;
  const provider = path.startsWith('/gag-reels/') ? 'Gag reel'
    : path.startsWith('/episodes/') ? 'Promo'
    : path.includes('/pilot-unaired-cut/') ? 'Unaired Pilot'
    : path.startsWith('/x-files-dailies/') ? 'Dailies' : 'Video';
  const send = (video, name, extra = {}) => {
    if (typeof gtag !== 'function') return;
    gtag('event', name, {
      video_title: video.getAttribute('title') || document.title.split(/[:|]/)[0].trim(),
      video_provider: provider,
      video_duration: Math.round(video.duration) || undefined,
      video_current_time: Math.round(video.currentTime),
      ...extra,
    });
  };
  const once = (video, name, extra = {}) => {
    const done = sent.get(video) || new Set();
    const key = name + (extra.video_percent ?? '');
    if (done.has(key)) return;
    done.add(key); sent.set(video, done);
    send(video, name, extra);
  };
  const flush = (video, beacon) => {
    const secs = Math.round(pending.get(video) || 0);
    if (secs < 1) return;
    pending.set(video, (pending.get(video) || 0) - secs);
    send(video, 'video_watch_time', { video_seconds_watched: secs, ...(beacon ? { transport_type: 'beacon' } : {}) });
  };
  const isVideo = (e) => e.target.matches?.('video');
  // Media events don't bubble, so listen in the capture phase to hear every <video> on the page.
  document.addEventListener('play', (e) => { if (!isVideo(e)) return; last.set(e.target, e.target.currentTime); once(e.target, 'video_start'); }, true);
  document.addEventListener('seeking', (e) => { if (isVideo(e)) last.delete(e.target); }, true);
  document.addEventListener('timeupdate', (e) => {
    const v = e.target;
    if (!isVideo(e) || v.paused) return;
    const prev = last.get(v); last.set(v, v.currentTime);
    if (prev === undefined) return;
    const step = v.currentTime - prev;
    if (step <= 0 || step > 2) return;   // a seek or a source swap, not playback
    watched.set(v, (watched.get(v) || 0) + step);
    pending.set(v, (pending.get(v) || 0) + step);
    if (!v.duration) return;
    const pct = (watched.get(v) / v.duration) * 100;
    for (const m of MILESTONES) if (pct >= m) once(v, 'video_progress', { video_percent: m });
  }, true);
  document.addEventListener('pause', (e) => { if (isVideo(e)) flush(e.target); }, true);
  document.addEventListener('ended', (e) => {
    const v = e.target;
    if (!isVideo(e)) return;
    flush(v);
    if (v.duration && (watched.get(v) || 0) >= v.duration * 0.9) once(v, 'video_complete', { video_percent: 100 });
  }, true);
  // Leaving the page mid-video still counts the time watched.
  const leave = () => { for (const v of pending.keys()) flush(v, true); };
  addEventListener('pagehide', leave);
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') leave(); });
})();

document.addEventListener('click', (event) => {
  const link = event.target.closest('a[href*="drive.google.com"], a[href*="docs.google.com"]');
  if (!link || typeof gtag !== 'function') return;
  if (link.closest('.bf-fix')) return;
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

// Nothing on the site can be downloaded or saved. Pictures, video and
// audio get no right-click menu, no drag and no iPhone long-press save, and a link to a bare image
// file (a full-size screencap, a scout page) opens in a viewer here instead of as the raw file in
// a new tab, where Save As would work. Drive files carry Google's own lock (download, print and copy
// off for viewers), and the site check refuses to publish a link to a raw PDF or video file.
// This stops the menus and buttons; it cannot stop a screenshot.
(() => {
  const IMAGE = /\.(jpe?g|png|webp|gif|avif)(\?|#|$)/i;
  const FILE = /\.(pdf|zip|mp4|m4v|mov|m4a|mp3|wav|docx?)(\?|#|$)/i;
  const style = document.createElement('style');
  style.textContent = `img,video,audio,picture,canvas{-webkit-touch-callout:none;-webkit-user-drag:none;user-select:none}
.bf-viewer{position:fixed;inset:0;z-index:2000;display:flex;align-items:center;justify-content:center;background:rgba(8,10,9,.94);padding:max(16px,env(safe-area-inset-top)) 16px max(16px,env(safe-area-inset-bottom))}
.bf-viewer[hidden]{display:none}
.bf-viewer img{max-width:100%;max-height:100%;object-fit:contain;box-shadow:0 10px 40px rgba(0,0,0,.6)}
.bf-viewer button{position:absolute;border:0;background:rgba(255,255,255,.12);color:#fff;font:600 22px/1 system-ui,sans-serif;width:44px;height:44px;border-radius:50%;cursor:pointer}
.bf-viewer button:hover,.bf-viewer button:focus-visible{background:rgba(255,255,255,.26)}
.bf-viewer .bf-viewer-close{top:max(14px,env(safe-area-inset-top));right:14px}
.bf-viewer .bf-viewer-prev{left:14px;top:50%;transform:translateY(-50%)}
.bf-viewer .bf-viewer-next{right:14px;top:50%;transform:translateY(-50%)}`;
  document.head.appendChild(style);

  const fileLink = (el) => {
    const a = el.closest?.('a[href]');
    const href = a?.getAttribute('href') || '';
    return a && (IMAGE.test(href) || FILE.test(href)) ? a : null;
  };
  const guarded = (el) => el.closest?.('img, video, audio, picture, canvas, source, .bf-viewer') || fileLink(el);
  document.addEventListener('contextmenu', (e) => { if (guarded(e.target)) e.preventDefault(); }, true);
  document.addEventListener('dragstart', (e) => { if (guarded(e.target)) e.preventDefault(); }, true);

  let viewer, picture, links = [], at = 0;
  const show = (i) => {
    at = (i + links.length) % links.length;
    const a = links[at];
    picture.src = a.href;
    picture.alt = a.querySelector('img')?.alt || a.getAttribute('aria-label') || '';
    viewer.querySelectorAll('.bf-viewer-prev, .bf-viewer-next').forEach((b) => { b.hidden = links.length < 2; });
    // Which pictures people open. Link text and Link URL are built-in
    // dimensions in Google Analytics, so Reports > Engagement > Events > view_photo lists them by name.
    if (typeof gtag === 'function') {
      gtag('event', 'view_photo', { link_text: (picture.alt || a.getAttribute('href').split('/').pop()).slice(0, 100),
        link_url: a.href, page_section: location.pathname.split('/')[1] || 'home' });
    }
  };
  const close = () => { viewer.hidden = true; picture.removeAttribute('src'); document.documentElement.style.overflow = ''; links[at]?.focus(); };
  const open = (a) => {
    if (!viewer) {
      viewer = document.createElement('div');
      viewer.className = 'bf-viewer';
      viewer.setAttribute('role', 'dialog');
      viewer.setAttribute('aria-modal', 'true');
      viewer.innerHTML = '<img alt="" draggable="false"><button class="bf-viewer-prev" aria-label="Previous">‹</button>'
        + '<button class="bf-viewer-next" aria-label="Next">›</button><button class="bf-viewer-close" aria-label="Close">×</button>';
      picture = viewer.querySelector('img');
      viewer.addEventListener('click', (e) => {
        if (e.target.closest('.bf-viewer-prev')) show(at - 1);
        else if (e.target.closest('.bf-viewer-next')) show(at + 1);
        else if (e.target === viewer || e.target.closest('.bf-viewer-close')) close();
      });
      document.addEventListener('keydown', (e) => {
        if (viewer.hidden) return;
        if (e.key === 'Escape') close();
        else if (e.key === 'ArrowLeft' && links.length > 1) show(at - 1);
        else if (e.key === 'ArrowRight' && links.length > 1) show(at + 1);
      });
      document.body.appendChild(viewer);
    }
    links = [...document.querySelectorAll('a[href]')].filter((l) => IMAGE.test(l.getAttribute('href')) && !l.closest('.bf-viewer'));
    viewer.hidden = false;
    document.documentElement.style.overflow = 'hidden';
    show(Math.max(0, links.indexOf(a)));
    viewer.querySelector('.bf-viewer-close').focus();
  };
  // Bubble phase, after the page's own handlers: a page with its own in-page viewer (the photo
  // albums) has already called preventDefault and keeps it.
  document.addEventListener('click', (e) => {
    const a = fileLink(e.target);
    if (!a || e.defaultPrevented) return;
    if (!IMAGE.test(a.getAttribute('href'))) return;
    e.preventDefault();
    open(a);
  });
  // A middle click opens the raw file in a new tab without ever firing "click"
  document.addEventListener('auxclick', (e) => { if (fileLink(e.target)) e.preventDefault(); });
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
  css.href = '/assets/site-search.5.css';
  document.head.appendChild(css);
  const js = document.createElement('script');
  js.src = '/assets/site-search.6.js';
  js.defer = true;
  document.head.appendChild(js);
})();

// The same view_photo event for pages with their own picture viewer (.wf-lb: Show Drawings, the wardrobe
// files, Polaroids, Tooms, cast lists and the rest). Watching the viewer catches the first open and every
// arrow or swipe to the next picture, without touching each page's own script (November 17, 2026).
(() => {
  const lb = document.querySelector('.wf-lb');
  if (!lb || typeof MutationObserver !== 'function') return;
  let last = '';
  new MutationObserver(() => {
    if (!lb.classList.contains('on')) { last = ''; return; }
    const m = /url\(["']?(.*?)["']?\)/.exec(lb.style.backgroundImage || '');
    if (!m || m[1] === last) return;
    last = m[1];
    if (typeof gtag !== 'function') return;
    const b = [...document.querySelectorAll('[data-full]')].find((x) => x.dataset.full === last);
    const name = b?.querySelector('img')?.alt || b?.getAttribute('aria-label') || last.split('/').pop();
    gtag('event', 'view_photo', { link_text: name.slice(0, 100), link_url: new URL(last, location.href).href,
      page_section: location.pathname.split('/')[1] || 'home' });
  }).observe(lb, { attributes: true, attributeFilter: ['style', 'class'] });
})();

// Email signup: the homepage band, and one line above the footer on every other page.
// Both post to the same list, with the page the address came from.
(() => {
  const URL_ = 'https://docs.google.com/forms/d/e/1FAIpQLSfwt1rpA04be3ZibGW60Mi_bPDhKcufiBIsteTpsI3zDq2njg/formResponse';
  const path = location.pathname;
  const footer = document.querySelector('body > footer, footer');
  if (footer && path !== '/' && !path.startsWith('/guest') && !document.querySelector('.bf-signup')) {
    const strip = document.createElement('section');
    strip.className = 'bf-signup-strip';
    strip.setAttribute('aria-label', 'Email signup');
    strip.innerHTML = '<div class="bf-signup-inner"><p class="bf-signup-line">Get a note when something new lands in the files.</p>'
      + '<form class="bf-signup" data-source="Footer" novalidate><input type="email" autocomplete="email" placeholder="you@example.com" aria-label="Your email">'
      + '<button type="submit">Sign me up</button></form><p class="bf-signup-msg" role="alert"></p></div>';
    footer.parentNode.insertBefore(strip, footer);
  }
  document.addEventListener('submit', (e) => {
    const form = e.target.closest && e.target.closest('form.bf-signup');
    if (!form) return;
    e.preventDefault();
    const box = form.parentNode, msg = box.querySelector('.bf-signup-msg');
    const email = form.querySelector('input[type=email]').value.trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { if (msg) msg.textContent = "That email doesn't look quite right."; return; }
    const btn = form.querySelector('button'), label = btn.textContent;
    btn.disabled = true; btn.textContent = 'Sending...';
    const from = form.dataset.source === 'Footer' ? 'Footer: ' + path : (form.dataset.source || path);
    fetch(URL_, { method: 'POST', mode: 'no-cors', body: new URLSearchParams({ 'entry.1947244089': email, 'entry.217118568': from }) })
      .then(() => {
        form.hidden = true;
        if (msg) { msg.classList.add('is-done'); msg.textContent = "You're on the list!! \uD83D\uDC7D"; }
        if (typeof gtag === 'function') gtag('event', 'email_signup', { page_section: path.split('/')[1] || 'home' });
      })
      .catch(() => { btn.disabled = false; btn.textContent = label; if (msg) msg.textContent = 'Something went wrong. Try again in a minute.'; });
  });
  document.addEventListener('input', (e) => {
    const form = e.target.closest && e.target.closest('form.bf-signup');
    const msg = form && form.parentNode.querySelector('.bf-signup-msg');
    if (msg && !msg.classList.contains('is-done')) msg.textContent = '';
  });
})();

// "Spot a mistake?": one line above the footer on episode, transcript and location pages. Opens the form in a
// new tab with the page's address already filled in.
(() => {
  const path = location.pathname;
  if (!/^\/(episodes|transcripts|locations)\/./.test(path)) return;
  const before = document.querySelector('.bf-signup-strip') || document.querySelector('body > footer, footer');
  if (!before || document.querySelector('.bf-fix')) return;
  const p = document.createElement('p');
  p.className = 'bf-fix';
  const a = document.createElement('a');
  a.href = 'https://docs.google.com/forms/d/e/1FAIpQLSdc84mXXl-pgo3t5iXSsAPtT5gpUW1Onj9RhsGNZW4Pfvz58w/viewform?usp=pp_url&entry.1878741533='
    + encodeURIComponent('https://www.boggsfiles.com' + path);
  a.target = '_blank';
  a.rel = 'noopener';
  a.textContent = 'Tell the archive';
  p.append('Spot a mistake? ', a);
  before.parentNode.insertBefore(p, before);
  a.addEventListener('click', () => {
    if (typeof gtag === 'function') gtag('event', 'spot_a_mistake', { page_section: path.split('/')[1] });
  });
})();
