/* The Civilian Geopolitical Reality Map
   Everything here is progressive enhancement. With JavaScript switched off the
   full text, the full ledger and every source link still work. */

(function () {
  'use strict';

  /* --- reading mode ------------------------------------------------------ */

  var root = document.documentElement;
  var btn = document.querySelector('[data-mode-toggle]');

  function currentMode() {
    if (root.dataset.mode) return root.dataset.mode;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function syncLabel() {
    if (!btn) return;
    var label = btn.querySelector('[data-mode-label]');
    var next = currentMode() === 'dark' ? btn.dataset.light : btn.dataset.dark;
    if (label) label.textContent = next;
    btn.setAttribute('aria-label', next);
  }

  if (btn) {
    syncLabel();
    btn.addEventListener('click', function () {
      var next = currentMode() === 'dark' ? 'light' : 'dark';
      root.dataset.mode = next;
      try { localStorage.setItem('rm-mode', next); } catch (e) {}
      syncLabel();
    });
  }

  /* --- section tracking in the table of contents ------------------------- */

  var tocLinks = Array.prototype.slice.call(document.querySelectorAll('.toc__list a'));
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var byId = {};
    var targets = [];
    tocLinks.forEach(function (a) {
      var el = document.getElementById(decodeURIComponent(a.hash.slice(1)));
      if (el) { byId[el.id] = a; targets.push(el); }
    });
    var visible = new Set();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) visible.add(entry.target.id);
        else visible.delete(entry.target.id);
      });
      var first = targets.filter(function (t) { return visible.has(t.id); })[0];
      tocLinks.forEach(function (a) { a.classList.remove('is-current'); });
      if (first && byId[first.id]) byId[first.id].classList.add('is-current');
    }, { rootMargin: '-72px 0px -70% 0px' });
    targets.forEach(function (t) { io.observe(t); });
  }

  /* --- ledger: search and evidence-class filters ------------------------- */

  var controls = document.querySelector('[data-controls]');
  if (!controls) return;

  var search = controls.querySelector('[data-search]');
  var filters = Array.prototype.slice.call(controls.querySelectorAll('.filter'));
  var status = controls.querySelector('[data-status]');
  var claims = Array.prototype.slice.call(document.querySelectorAll('.claim'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('[data-section]'));
  var empty = document.querySelector('[data-noresults]');
  var resetBtn = empty ? empty.querySelector('[data-reset]') : null;
  var active = new Set();

  function apply() {
    var q = (search && search.value || '').trim().toLowerCase();
    var shown = 0;

    claims.forEach(function (claim) {
      var okClass = active.size === 0 || active.has(claim.dataset.class);
      var okText = !q || claim.dataset.text.indexOf(q) !== -1;
      var show = okClass && okText;
      claim.hidden = !show;
      if (show) shown++;
    });

    sections.forEach(function (section) {
      var any = section.querySelector('.claim:not([hidden])');
      section.hidden = !any;
    });

    if (status) {
      status.textContent = (status.dataset.tpl || '{n} / {m}')
        .replace('{n}', shown).replace('{m}', claims.length);
    }
    if (empty) empty.hidden = shown !== 0;
  }

  filters.forEach(function (f) {
    f.addEventListener('click', function () {
      var id = f.dataset.class;
      if (active.has(id)) { active.delete(id); f.setAttribute('aria-pressed', 'false'); }
      else { active.add(id); f.setAttribute('aria-pressed', 'true'); }
      apply();
    });
  });

  if (search) {
    search.addEventListener('input', apply);
    search.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') { search.value = ''; apply(); }
    });
  }

  function reset() {
    active.clear();
    filters.forEach(function (f) { f.setAttribute('aria-pressed', 'false'); });
    if (search) search.value = '';
    apply();
  }
  if (resetBtn) resetBtn.addEventListener('click', reset);

  /* Links from a study page arrive as /ledger/#class=finding */
  function fromHash() {
    var hash = window.location.hash.slice(1);
    if (hash.indexOf('class=') !== 0) return;
    var id = hash.slice(6);
    var match = filters.filter(function (f) { return f.dataset.class === id; })[0];
    if (!match) return;
    active.add(id);
    match.setAttribute('aria-pressed', 'true');
    apply();
    controls.scrollIntoView({ block: 'start' });
  }
  fromHash();
  window.addEventListener('hashchange', fromHash);
})();
