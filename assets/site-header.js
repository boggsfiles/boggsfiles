// Count opens of archive files hosted on Google Drive. GA can't see inside Drive, so record the
// click on our side instead, named by episode and draft rather than an opaque Drive URL.
document.addEventListener('click', (event) => {
  const link = event.target.closest('a[href*="drive.google.com"], a[href*="docs.google.com"]');
  if (!link || typeof gtag !== 'function') return;
  const tidy = (text) => (text || '').replace(/[↗→]/g, '').replace(/\s+/g, ' ').trim();
  const card = link.closest('.episode');
  const heading = card && card.querySelector('h2');
  const version = tidy(link.textContent);
  const title = heading ? tidy(heading.textContent) : tidy(link.getAttribute('aria-label')).replace(/^Open /, '') || version;
  gtag('event', 'open_file', {
    file_title: title,
    file_version: heading ? version : '',
    file_label: heading ? `${title} · ${version}` : title,
    link_url: link.href,
  });
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
