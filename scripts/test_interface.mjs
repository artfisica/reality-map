// Smoke test for assets/atlas.js against the built site in docs/.
// Runs every enhancement in a DOM (jsdom) with the real pages and the real
// atlas.json, so a change to build.py, site.yaml or the script cannot ship a
// control that throws. Needs `python build.py` first.
//   npm ci && npm run test:interface
import { JSDOM } from 'jsdom';
import fs from 'node:fs';
import assert from 'node:assert/strict';

const docs = new URL('../docs/', import.meta.url).pathname;
const base = 'https://artfisica.github.io/reality-map/';
const atlas = JSON.parse(fs.readFileSync(docs + 'atlas.json', 'utf8'));
const js = fs.readFileSync(docs + 'assets/atlas.js', 'utf8');
const tick = (ms = 30) => new Promise((r) => setTimeout(r, ms));

function config(path) {
  return JSON.parse(/id="rm-config">(.*?)<\/script>/s.exec(fs.readFileSync(docs + path, 'utf8'))[1]);
}

async function page(path, url, seed = {}, before = null) {
  const html = fs.readFileSync(docs + path, 'utf8')
    .replace(/<script src="[^"]*atlas\.js[^"]*" defer><\/script>/, '');
  const dom = new JSDOM(html, { url, runScripts: 'outside-only', pretendToBeVisual: true });
  const w = dom.window;
  w.matchMedia = () => ({ matches: false, addEventListener() {} });
  w.fetch = async () => ({ ok: true, status: 200, json: async () => atlas });
  w.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); this.open = true; };
  w.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.open = false; };
  w.requestAnimationFrame = (cb) => setTimeout(cb, 0);
  w.scrollTo = () => {};
  w.HTMLElement.prototype.scrollIntoView = () => {};
  w.navigator.clipboard = { writeText: async () => {} };
  for (const [k, v] of Object.entries(seed)) w.localStorage.setItem(k, JSON.stringify(v));
  if (before) before(w);
  const errors = [];
  w.addEventListener('error', (e) => errors.push(e.message));
  w.eval(js);
  await tick(50);
  assert.deepEqual(errors, [], `${path}: script errors`);
  return w;
}

let failures = 0;
async function test(name, fn) {
  try { await fn(); console.log('ok   ' + name); }
  catch (e) { failures++; console.log('FAIL ' + name + '\n     ' + e.message); }
}

for (const [lang, home, study, ledger, map] of [
  ['en', 'index.html', 'studies/venezuela/', 'ledger/', 'map/'],
  ['es', 'es/index.html', 'es/estudios/venezuela/', 'es/registro/', 'es/mapa/'],
]) {
  const prefix = lang === 'es' ? 'es/' : '';
  await test(`${lang} home: evidence paths, trainer, search palette, mosaic card`, async () => {
    const staticPage = new JSDOM(fs.readFileSync(docs + home, 'utf8')).window.document;
    assert.equal(staticPage.querySelectorAll('[data-path-panel]').length, 2);
    assert.ok(staticPage.querySelectorAll('[data-path-step]').length >= 14);
    assert.equal(staticPage.querySelectorAll('[data-path-step][hidden]').length, 0,
      'every evidence step remains visible without JavaScript');
    const w = await page(home, base + prefix);
    const d = w.document;
    assert.equal(d.querySelector('[data-search-open]').hidden, false);
    const paths = d.querySelector('[data-evidence-paths]');
    assert.ok(paths.classList.contains('is-enhanced'));
    assert.equal(paths.querySelectorAll('[data-path-tab]').length, 2);
    assert.equal(paths.querySelectorAll('[data-path-panel]:not([hidden])').length, 1);
    let activePath = paths.querySelector('[data-path-panel]:not([hidden])');
    assert.equal(activePath.querySelectorAll('[data-path-step]:not([hidden])').length, 1);
    const firstClaim = activePath.querySelector('[data-path-step]:not([hidden]) .path__claim').textContent;
    activePath.querySelector('[data-path-next]').click();
    assert.notEqual(activePath.querySelector('[data-path-step]:not([hidden]) .path__claim').textContent, firstClaim);
    assert.match(activePath.querySelector('[data-path-status]').textContent, /2/);
    paths.querySelectorAll('[data-path-tab]')[1].click();
    activePath = paths.querySelector('[data-path-panel]:not([hidden])');
    assert.equal(activePath.dataset.pathPanel, 'oil-control');
    assert.match(activePath.querySelector('.path__ledger').href, /#[A-Z0-9-]+$/);
    assert.ok(d.querySelector('.trainer.wrap'), 'trainer uses shared page width');
    assert.equal(d.querySelector('[data-trainer]').hidden, false);
    d.querySelector('[data-trainer-next]').click();
    assert.ok(d.querySelector('[data-trainer-claim]').textContent.length > 20);
    d.querySelector('[data-choice="record"]').click();
    assert.ok(d.querySelector('[data-trainer-answer]').className.includes('stamp--'));
    assert.match(d.querySelector('[data-trainer-open]').href, /#[A-Z0-9-]+$/);
    d.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'k', ctrlKey: true, bubbles: true }));
    await tick();
    assert.ok(d.querySelector('dialog[open]'), 'palette opens');
    const input = d.querySelector('.palette__input');
    input.value = 'icc'; input.dispatchEvent(new w.Event('input'));
    assert.ok(d.querySelectorAll('.palette__link').length > 2, 'palette has results');
    assert.equal(input.getAttribute('role'), 'combobox');
    input.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));
    const active = input.getAttribute('aria-activedescendant');
    assert.ok(active, 'active option exposed');
    assert.equal(d.getElementById(active).getAttribute('aria-selected'), 'true');
    const tile = d.querySelector('.mosaic .tile');
    tile.dispatchEvent(new w.Event('mouseenter'));
    assert.equal(d.querySelector('.tilecard').hidden, false);
  });
  await test(`${lang} home: continue reading and revised-record notice`, async () => {
    const cfg = config(home);
    const w = await page(home, base + prefix, {
      ['rm-last:' + lang]: { doc: `${lang}:venezuela`, lang, version: cfg.version, pct: 42, url: '/x/', title: 'T' },
      ['rm-seen:' + lang]: '0.0.1',
    });
    const d = w.document;
    assert.equal(d.querySelector('[data-continue]').hidden, false);
    assert.ok(d.querySelector('.revised'), 'revised notice shown');
    d.querySelector('.revised__close').click();
    assert.equal(JSON.parse(w.localStorage.getItem('rm-seen:' + lang)), cfg.version);
  });
  await test(`${lang} study: progress rule and share bar`, async () => {
    const cfg = config(study + 'index.html');
    let scrolled = false;
    const w = await page(study + 'index.html', base + study,
      { [`rm-read:${cfg.doc}:${cfg.version}`]: { doc: cfg.doc, lang, version: cfg.version, pct: 50, url: '/x/', title: 'T' } },
      (win) => { win.scrollTo = () => { scrolled = true; }; win.scroll = win.scrollTo; });
    const d = w.document;
    assert.ok(d.querySelector('.progress[role="progressbar"]'));
    assert.equal(scrolled, false, 'the page must not move the reader on its own');
    const btns = [...d.querySelectorAll('.share__btn')];
    assert.ok(btns.length >= 6, 'share buttons present');
    d.querySelector('.share__btn--js').click();
    await tick();
    assert.ok(d.querySelector('[data-share-status]').textContent.length > 0);
  });
  await test(`${lang} ledger: URL-synced filters, claim actions, no nested anchors`, async () => {
    const w = await page(ledger + 'index.html', base + ledger + '?q=icc&class=court');
    const d = w.document;
    assert.deepEqual([...d.querySelectorAll('.filter[aria-pressed="true"]')].map((f) => f.dataset.class), ['court']);
    assert.ok(d.querySelectorAll('.claim:not([hidden])').length < 88);
    const q = d.querySelector('[data-search]');
    q.value = 'tribunal'; q.dispatchEvent(new w.Event('input'));
    assert.match(w.location.search, /q=tribunal/);
    assert.ok(d.querySelector('.claim .claim__actions button'));
    assert.equal(d.querySelectorAll('a a').length, 0, 'anchors must not nest');
  });
  await test(`${lang} map: pins and legend highlight each other`, async () => {
    const w = await page(map + 'index.html', base + map);
    const d = w.document;
    d.querySelector('.map-pin').dispatchEvent(new w.Event('mouseenter'));
    assert.equal(d.querySelectorAll('.legend__group.is-hot').length, 1);
  });
}

await test('feed: every entry keyed to a release, none to a draft', async () => {
  const feed = fs.readFileSync(docs + 'feed.xml', 'utf8');
  const ids = [...feed.matchAll(/<id>(.*?)<\/id>/g)].map((m) => m[1]).slice(1);
  assert.ok(ids.length > 3, 'feed has entries');
  for (const id of ids) assert.match(id, /\/changelog\/(\d+(\.\d+)+|interface-\d{4}-\d{2}-\d{2})$/, id);
  assert.ok(!/<updated>\d{4}-\d{2}-\d{2}T(?!00:00:00Z)/.test(feed), 'timestamps come from headings, not the clock');
});

if (failures) { console.log(`${failures} failing`); process.exit(1); }
console.log('Interface smoke test passed.');
