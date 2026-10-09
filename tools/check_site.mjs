#!/usr/bin/env node
// Check the site before it goes live. publish.sh runs this and refuses to publish if it fails.
//
//   1. Broken links: every href/src on every committed page must point at a committed file.
//      (publish.sh ships the committed dist/, so an uncommitted target would 404 on the live site.)
//   2. Script errors: every page is opened in headless Chrome and any JavaScript error is reported.
//   3. File names in Analytics: every Google Drive link is run through the same naming code the live
//      site uses (window.bfDescribeFile in assets/site-header.js). A link whose name had to be
//      guessed, like the old "Open the scan" or "28", fails the check until a naming rule covers it.
//
// Run:  node tools/check_site.mjs          (add --links-only to skip the browser checks)

import { execFileSync, spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { mkdtempSync, readFileSync, rmSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { extname, join } from 'node:path';

const DIST = new URL('../dist/', import.meta.url).pathname;
const SITE_HOSTS = new Set(['www.boggsfiles.com', 'boggsfiles.com']);
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const linksOnly = process.argv.includes('--links-only');

const committed = new Set(execFileSync('git', ['ls-files', '-z'], { cwd: DIST, encoding: 'utf8' }).split('\0').filter(Boolean));
const pages = [...committed].filter((f) => f.endsWith('.html')).sort();
const exists = (path) => committed.has(path) || committed.has(join(path, 'index.html'));
const urlFor = (file) => '/' + file.replace(/(^|\/)index\.html$/, '$1');
const problems = { 'Broken links': [], 'Script errors': [], 'Drive links with guessed names': [] };

// 1. Broken links -------------------------------------------------------------------------------
for (const file of pages) {
  const html = readFileSync(join(DIST, file), 'utf8').replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '');
  const base = new URL(urlFor(file), 'https://www.boggsfiles.com');
  for (const [, ref] of html.matchAll(/\s(?:href|src)=["']([^"']+)["']/gi)) {
    if (/^(#|mailto:|tel:|data:|javascript:)/i.test(ref)) continue;
    const url = new URL(ref.replace(/&amp;/g, '&'), base);
    if (!SITE_HOSTS.has(url.hostname)) continue;
    const path = decodeURIComponent(url.pathname).replace(/^\//, '');
    if (path && !exists(path.replace(/\/$/, ''))) problems['Broken links'].push(`${urlFor(file)} → ${url.pathname}`);
  }
}

// 2 & 3. Open every page in headless Chrome -----------------------------------------------------
if (!linksOnly) {
  const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml' };
  const server = createServer((req, res) => {
    let path = decodeURIComponent(new URL(req.url, 'http://x').pathname).replace(/^\//, '');
    try { if (!path || statSync(join(DIST, path)).isDirectory()) path = join(path, 'index.html'); } catch {}
    let body;
    try { body = readFileSync(join(DIST, path)); } catch { return res.writeHead(404).end(); }
    res.writeHead(200, { 'content-type': TYPES[extname(path)] || 'application/octet-stream' }).end(body);
  }).listen(0);
  const origin = `http://localhost:${server.address().port}`;

  const profile = mkdtempSync(join(tmpdir(), 'bf-check-'));
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`, '--no-first-run', 'about:blank']);
  const endpoint = await new Promise((resolve, reject) => {
    chrome.stderr.on('data', (d) => { const m = String(d).match(/ws:\/\/\S+/); if (m) resolve(m[0]); });
    chrome.on('exit', () => reject(new Error('Chrome exited before it was ready')));
  });

  const ws = new WebSocket(endpoint);
  await new Promise((r) => ws.addEventListener('open', r, { once: true }));
  let nextId = 0; const pending = new Map(); const listeners = [];
  ws.addEventListener('message', ({ data }) => {
    const msg = JSON.parse(data);
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
    else listeners.forEach((fn) => fn(msg));
  });
  const send = (method, params = {}, sessionId) => new Promise((resolve) => {
    const id = ++nextId; pending.set(id, resolve); ws.send(JSON.stringify({ id, method, params, sessionId }));
  });

  const { result: { targetId } } = await send('Target.createTarget', { url: 'about:blank' });
  const { result: { sessionId } } = await send('Target.attachToTarget', { targetId, flatten: true });
  await send('Page.enable', {}, sessionId);
  await send('Runtime.enable', {}, sessionId);
  await send('Network.enable', {}, sessionId);
  // Keep the check fast and offline from Google: analytics, fonts and Drive previews aren't under test.
  await send('Network.setBlockedURLs', { urls: ['*googletagmanager.com*', '*google-analytics.com*', '*fonts.googleapis.com*', '*fonts.gstatic.com*', '*drive.google.com*', '*docs.google.com*'] }, sessionId);

  let errors = [];
  listeners.push((msg) => {
    if (msg.method === 'Runtime.exceptionThrown') errors.push(msg.params.exceptionDetails.exception?.description?.split('\n')[0] || msg.params.exceptionDetails.text);
  });
  const loaded = () => new Promise((resolve) => {
    const timer = setTimeout(resolve, 8000);
    listeners.push(function onLoad(msg) {
      if (msg.method === 'Page.loadEventFired') { clearTimeout(timer); listeners.splice(listeners.indexOf(onLoad), 1); resolve(); }
    });
  });

  const AUDIT = `JSON.stringify([...document.querySelectorAll('a[href*="drive.google.com"], a[href*="docs.google.com"]')].map((a) =>
    typeof window.bfDescribeFile === 'function' ? window.bfDescribeFile(a) : { guessed: true, file_label: '(site-header.js not loaded)' }))`;

  for (const [i, file] of pages.entries()) {
    errors = [];
    const done = loaded();
    await send('Page.navigate', { url: origin + urlFor(file) }, sessionId);
    await done;
    const html = readFileSync(join(DIST, file), 'utf8');
    if (/drive\.google\.com|docs\.google\.com/.test(html) && !/http-equiv=["']refresh/i.test(html)) {
      const { result } = await send('Runtime.evaluate', { expression: AUDIT, returnByValue: true }, sessionId);
      for (const f of JSON.parse(result.result.value || '[]')) {
        if (f.guessed) problems['Drive links with guessed names'].push(`${urlFor(file)} → "${f.file_label}"`);
      }
    }
    for (const e of new Set(errors)) problems['Script errors'].push(`${urlFor(file)} → ${e}`);
    if ((i + 1) % 200 === 0) process.stdout.write(`  checked ${i + 1}/${pages.length} pages\n`);
  }

  ws.close(); server.close();
  await new Promise((r) => { chrome.once('exit', r); chrome.kill(); });
  rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
}

// Report ----------------------------------------------------------------------------------------
let failed = false;
for (const [name, list] of Object.entries(problems)) {
  const unique = [...new Set(list)];
  if (!unique.length) continue;
  failed = true;
  console.log(`\n✗ ${name} (${unique.length})`);
  unique.slice(0, 40).forEach((line) => console.log('   ' + line));
  if (unique.length > 40) console.log(`   …and ${unique.length - 40} more`);
}
console.log(failed ? '\nSite check FAILED: fix the above before publishing.' : `Site check passed: ${pages.length} pages${linksOnly ? ' (links only)' : ''}.`);
process.exit(failed ? 1 : 0);
