/* The Civilian Geopolitical Reality Map
   Everything here is progressive enhancement. With JavaScript switched off the
   full text, the full ledger and every source link still work. */

(function () {
  'use strict';

  /* --- shared: configuration, storage, the atlas index ------------------- */

  var CFG = {};
  try {
    var cfgEl = document.getElementById('rm-config');
    if (cfgEl) CFG = JSON.parse(cfgEl.textContent);
  } catch (e) { CFG = {}; }
  var S = CFG.strings || {};
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function fmt(tpl, vars) {
    return String(tpl || '').replace(/\{(\w+)\}/g, function (m, k) {
      return vars && k in vars ? vars[k] : m;
    });
  }
  function load(key) {
    try { var v = localStorage.getItem(key); return v ? JSON.parse(v) : null; }
    catch (e) { return null; }
  }
  function save(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) {}
  }
  function drop(key) { try { localStorage.removeItem(key); } catch (e) {} }
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }
  function inField(target) {
    if (!target) return false;
    var tag = (target.tagName || '').toLowerCase();
    return tag === 'input' || tag === 'textarea' || tag === 'select' || target.isContentEditable;
  }
  function classById(id) {
    var list = CFG.classes || [];
    for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
    return null;
  }
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = el('textarea'); ta.value = text;
      ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.top = '-9999px';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); resolve(); } catch (e) { reject(e); }
      document.body.removeChild(ta);
    });
  }

  /* The index of both editions is built once at publish time (atlas.json)
     and fetched from this domain only when a feature needs it. */
  var atlasPromise = null;
  function atlas() {
    if (atlasPromise) return atlasPromise;
    if (!CFG.atlas || !window.fetch) return Promise.reject(new Error('no index'));
    atlasPromise = fetch(CFG.atlas, { credentials: 'omit' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) {
        var editions = data.editions || [];
        for (var i = 0; i < editions.length; i++) {
          if (editions[i].lang === CFG.lang) return editions[i];
        }
        throw new Error('edition missing');
      });
    atlasPromise.catch(function () { atlasPromise = null; });
    return atlasPromise;
  }

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

  /* --- audio companion: keep the listener's place between reading pages -- */

  var companion = document.querySelector('[data-audio-companion]');
  if (companion) {
    var audio = companion.querySelector('[data-audio]');
    var audioStatus = companion.querySelector('[data-audio-status]');
    var audioKey = companion.dataset.audioKey;
    var lastStoredSecond = -1;

    function clock(seconds) {
      var whole = Math.max(0, Math.floor(seconds));
      var minutes = Math.floor(whole / 60);
      var remainder = String(whole % 60);
      return minutes + ':' + (remainder.length < 2 ? '0' : '') + remainder;
    }

    function savedPosition() {
      try { return Number(localStorage.getItem(audioKey)) || 0; }
      catch (e) { return 0; }
    }

    function storePosition() {
      if (!audio || !audioKey || !Number.isFinite(audio.currentTime)) return;
      var second = Math.floor(audio.currentTime);
      if (second === lastStoredSecond) return;
      lastStoredSecond = second;
      try { localStorage.setItem(audioKey, String(audio.currentTime)); } catch (e) {}
    }

    if (audio) {
      audio.addEventListener('loadedmetadata', function () {
        var saved = savedPosition();
        if (saved > 5 && saved < audio.duration - 5) {
          audio.currentTime = saved;
          if (audioStatus) {
            audioStatus.textContent = companion.dataset.resume.replace('{time}', clock(saved));
          }
        }
      });
      audio.addEventListener('play', function () { companion.dataset.playing = 'true'; });
      audio.addEventListener('pause', function () {
        companion.dataset.playing = 'false';
        storePosition();
      });
      audio.addEventListener('timeupdate', storePosition);
      audio.addEventListener('ended', function () {
        companion.dataset.playing = 'false';
        try { localStorage.removeItem(audioKey); } catch (e) {}
        if (audioStatus) audioStatus.textContent = companion.dataset.complete;
      });
      window.addEventListener('pagehide', storePosition);
    }
  }

  /* --- audio library: one desk, sequential study episodes --------------- */

  var library = document.querySelector('[data-audio-library]');
  if (library) {
    var libraryAudio = library.querySelector('[data-library-audio]');
    var episodeButtons = Array.prototype.slice.call(library.querySelectorAll('[data-episode]'));
    var libraryTitle = library.querySelector('[data-library-title]');
    var libraryKind = library.querySelector('[data-library-kind]');
    var libraryCoverKind = library.querySelector('[data-library-cover-kind]');
    var libraryNumber = library.querySelector('[data-library-number]');
    var libraryDuration = library.querySelector('[data-library-duration]');
    var libraryDescription = library.querySelector('[data-library-description]');
    var libraryStatus = library.querySelector('[data-library-status]');
    var libraryArticle = library.querySelector('[data-library-article]');
    var libraryDownload = library.querySelector('[data-library-download]');
    var selected = 0;
    var libraryLastSecond = -1;
    var playWhenReady = false;

    function libraryClock(seconds) {
      var whole = Math.max(0, Math.floor(seconds));
      var minutes = Math.floor(whole / 60);
      var remainder = String(whole % 60);
      return minutes + ':' + (remainder.length < 2 ? '0' : '') + remainder;
    }

    function librarySaved() {
      try { return Number(localStorage.getItem(library.dataset.audioKey)) || 0; }
      catch (e) { return 0; }
    }

    function storeLibraryPosition() {
      if (!libraryAudio || !Number.isFinite(libraryAudio.currentTime)) return;
      var second = Math.floor(libraryAudio.currentTime);
      if (second === libraryLastSecond) return;
      libraryLastSecond = second;
      try { localStorage.setItem(library.dataset.audioKey, String(libraryAudio.currentTime)); }
      catch (e) {}
    }

    function chooseEpisode(index, shouldPlay) {
      var button = episodeButtons[index];
      if (!button || !libraryAudio) return;
      storeLibraryPosition();
      selected = index;
      libraryLastSecond = -1;
      playWhenReady = shouldPlay;
      library.dataset.audioKey = button.dataset.key;
      libraryAudio.src = button.dataset.src;
      libraryAudio.load();
      if (libraryTitle) libraryTitle.textContent = button.dataset.title;
      if (libraryKind) {
        libraryKind.textContent = button.dataset.kind + ' · ' + button.dataset.duration;
      }
      if (libraryCoverKind) libraryCoverKind.textContent = button.dataset.kind;
      if (libraryNumber) libraryNumber.textContent = button.dataset.number;
      if (libraryDuration) libraryDuration.textContent = button.dataset.duration;
      if (libraryDescription) libraryDescription.textContent = button.dataset.description;
      if (libraryArticle) libraryArticle.href = button.dataset.article;
      if (libraryDownload) libraryDownload.href = button.dataset.src;
      if (libraryStatus) libraryStatus.textContent = library.dataset.ready;
      episodeButtons.forEach(function (item, itemIndex) {
        item.setAttribute('aria-current', itemIndex === index ? 'true' : 'false');
        var card = item.closest('.episode-card');
        if (card) card.classList.toggle('is-current', itemIndex === index);
      });
    }

    if (libraryAudio && episodeButtons.length) {
      libraryAudio.addEventListener('loadedmetadata', function () {
        var saved = librarySaved();
        if (saved > 5 && saved < libraryAudio.duration - 5) {
          libraryAudio.currentTime = saved;
          if (libraryStatus) {
            libraryStatus.textContent = library.dataset.resume
              .replace('{time}', libraryClock(saved));
          }
        }
        if (playWhenReady) {
          playWhenReady = false;
          libraryAudio.play().catch(function () {});
        }
      });
      libraryAudio.addEventListener('play', function () { library.dataset.playing = 'true'; });
      libraryAudio.addEventListener('pause', function () {
        library.dataset.playing = 'false';
        storeLibraryPosition();
      });
      libraryAudio.addEventListener('timeupdate', storeLibraryPosition);
      libraryAudio.addEventListener('ended', function () {
        try { localStorage.removeItem(library.dataset.audioKey); } catch (e) {}
        if (selected + 1 < episodeButtons.length) chooseEpisode(selected + 1, true);
        else {
          library.dataset.playing = 'false';
          if (libraryStatus) libraryStatus.textContent = library.dataset.complete;
        }
      });
      episodeButtons.forEach(function (button, index) {
        button.addEventListener('click', function () { chooseEpisode(index, true); });
      });
      window.addEventListener('pagehide', storeLibraryPosition);
    }
  }

  /* --- a revised record: tell a returning reader ------------------------- */

  (function () {
    if (!CFG.version || !CFG.lang) return;
    var key = 'rm-seen:' + CFG.lang;
    var seen = load(key);
    if (!seen) { save(key, CFG.version); return; }
    if (seen === CFG.version) return;
    var main = document.getElementById('main');
    if (!main) return;
    var box = el('aside', 'revised');
    box.setAttribute('role', 'status');
    var text = el('p', 'revised__text', fmt(S.new_edition, { old: seen, new: CFG.version }) + ' ');
    var link = el('a', 'revised__link', S.new_edition_link);
    link.href = CFG.changelog || '#'; link.rel = 'noopener';
    text.appendChild(link);
    var close = el('button', 'revised__close', S.dismiss);
    close.type = 'button';
    function done() { save(key, CFG.version); box.remove(); }
    close.addEventListener('click', done);
    link.addEventListener('click', function () { save(key, CFG.version); });
    box.appendChild(text); box.appendChild(close);
    main.insertBefore(box, main.firstChild);
  })();

  /* --- reading progress: a thin rule, and your place on the home page ---- */

  (function () {
    var docKey = document.body.dataset.doc;
    if (!docKey) return;
    var article = document.querySelector('.doc') || document.body;
    var bar = el('div', 'progress');
    bar.setAttribute('role', 'progressbar');
    bar.setAttribute('aria-label', S.progress_label || 'Reading progress');
    bar.setAttribute('aria-valuemin', '0'); bar.setAttribute('aria-valuemax', '100');
    var fill = el('span', 'progress__fill');
    bar.appendChild(fill);
    document.body.appendChild(bar);

    var storeKey = 'rm-read:' + docKey + ':' + CFG.version;
    var ticking = false, lastPct = -1, lastSaved = -1;

    function pct() {
      var rect = article.getBoundingClientRect();
      var top = rect.top + window.scrollY;
      var span = Math.max(1, article.offsetHeight - window.innerHeight);
      var p = (window.scrollY - top) / span * 100;
      return Math.max(0, Math.min(100, Math.round(p)));
    }
    function remember(p) {
      var record = { doc: docKey, lang: CFG.lang, version: CFG.version, pct: p,
                     url: window.location.pathname, title: CFG.title, at: Date.now() };
      save(storeKey, record);
      if (p >= 4 && p <= 96) save('rm-last:' + CFG.lang, record);
      else {
        var last = load('rm-last:' + CFG.lang);
        if (last && last.doc === docKey) drop('rm-last:' + CFG.lang);
      }
    }
    function update() {
      ticking = false;
      var p = pct();
      if (p === lastPct) return;
      lastPct = p;
      fill.style.transform = 'scaleX(' + (p / 100) + ')';
      bar.setAttribute('aria-valuenow', String(p));
      if (Math.abs(p - lastSaved) >= 2) { lastSaved = p; remember(p); }
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; window.requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', update);
    window.addEventListener('pagehide', function () { remember(pct()); });

    /* The position is remembered for the Continue reading card on the cover;
       the page itself never moves the reader without being asked. */
    update();
  })();

  (function () {
    var slot = document.querySelector('[data-continue]');
    if (!slot) return;
    var last = load('rm-last:' + CFG.lang);
    if (!last || !last.url || last.version !== CFG.version) return;
    var head = el('p', 'eyebrow', S.continue_h);
    var link = el('a', 'continue__link');
    link.href = last.url;
    link.appendChild(el('span', 'continue__title', last.title));
    link.appendChild(el('span', 'continue__pct', fmt(S.continue_pct, { pct: last.pct })));
    var dismiss = el('button', 'continue__dismiss', S.continue_dismiss);
    dismiss.type = 'button';
    dismiss.addEventListener('click', function () { drop('rm-last:' + CFG.lang); slot.hidden = true; });
    var track = el('span', 'continue__track');
    var fill = el('span', 'continue__fill');
    fill.style.width = last.pct + '%';
    track.appendChild(fill);
    slot.appendChild(head); slot.appendChild(link); slot.appendChild(track); slot.appendChild(dismiss);
    slot.hidden = false;
  })();

  /* --- pass it on: copy, native share and a citation on every study ------ */

  (function () {
    var share = document.querySelector('[data-share]');
    if (!share) return;
    var row = share.querySelector('[data-share-row]');
    var status = share.querySelector('[data-share-status]');
    var url = CFG.canonical || window.location.href;
    function say(msg) {
      if (!status) return;
      status.textContent = msg;
      window.clearTimeout(say.t);
      say.t = window.setTimeout(function () { status.textContent = ''; }, 2400);
    }
    function button(label, onClick) {
      var b = el('button', 'share__btn share__btn--js', label);
      b.type = 'button'; b.addEventListener('click', onClick);
      return b;
    }
    var first = row.firstChild;
    row.insertBefore(button(S.copy_link, function () {
      copyText(url).then(function () { say(S.copied); });
    }), first);
    row.insertBefore(button(S.copy_citation, function () {
      copyText(fmt(S.citation, { author: CFG.author, title: CFG.title, site: CFG.site,
                                 edition: CFG.edition, version: CFG.version, url: url }))
        .then(function () { say(S.citation_copied); });
    }), first);
    if (navigator.share) {
      row.insertBefore(button(S.share, function () {
        navigator.share({ title: CFG.title + ' \u2014 ' + CFG.short, url: url }).catch(function () {});
      }), first);
    }
  })();

  /* --- the mosaic: read a tile without leaving the cover ----------------- */

  (function () {
    var tiles = Array.prototype.slice.call(document.querySelectorAll('.mosaic .tile'));
    if (!tiles.length) return;
    var card = el('div', 'tilecard');
    card.setAttribute('role', 'tooltip');
    card.hidden = true;
    var ref = el('span', 'tilecard__ref');
    var cls = el('span', 'tilecard__class');
    var txt = el('p', 'tilecard__text');
    card.appendChild(ref); card.appendChild(cls); card.appendChild(txt);
    document.body.appendChild(card);
    var hideTimer;

    function show(tile) {
      window.clearTimeout(hideTimer);
      var parts = (tile.getAttribute('aria-label') || '').split(' \u00b7 ');
      if (parts.length < 3) return;
      ref.textContent = parts[0];
      cls.textContent = parts[1];
      cls.className = 'tilecard__class';
      var match = /tile--([a-z]+)/.exec(tile.className);
      if (match) cls.classList.add('stamp--' + match[1]);
      txt.textContent = parts.slice(2).join(' \u00b7 ');
      card.hidden = false;
      var r = tile.getBoundingClientRect();
      var w = card.offsetWidth, h = card.offsetHeight;
      var left = Math.max(8, Math.min(window.innerWidth - w - 8, r.left + r.width / 2 - w / 2));
      var top = r.top - h - 10;
      if (top < 8) top = r.bottom + 10;
      card.style.left = left + 'px';
      card.style.top = (top + window.scrollY) + 'px';
    }
    function hide() { hideTimer = window.setTimeout(function () { card.hidden = true; }, 60); }
    tiles.forEach(function (tile) {
      tile.dataset.title = tile.getAttribute('title') || '';
      tile.removeAttribute('title');
      tile.addEventListener('mouseenter', function () { show(tile); });
      tile.addEventListener('focus', function () { show(tile); });
      tile.addEventListener('mouseleave', hide);
      tile.addEventListener('blur', hide);
    });
    window.addEventListener('scroll', function () { card.hidden = true; }, { passive: true });
  })();

  /* --- the map: pins and legend point at each other ---------------------- */

  (function () {
    var pins = Array.prototype.slice.call(document.querySelectorAll('.map-pin[data-numeral]'));
    var groups = Array.prototype.slice.call(document.querySelectorAll('.legend__group[data-numeral]'));
    if (!pins.length || !groups.length) return;
    function mark(numeral, on) {
      pins.concat(groups).forEach(function (node) {
        if (node.dataset.numeral === numeral) node.classList.toggle('is-hot', on);
      });
    }
    pins.concat(groups).forEach(function (node) {
      var n = node.dataset.numeral;
      node.addEventListener('mouseenter', function () { mark(n, true); });
      node.addEventListener('mouseleave', function () { mark(n, false); });
      node.addEventListener('focusin', function () { mark(n, true); });
      node.addEventListener('focusout', function () { mark(n, false); });
    });
  })();

  /* --- learn the six: a ledger claim with its colour hidden -------------- */

  (function () {
    var box = document.querySelector('[data-trainer]');
    if (!box) return;
    var refEl = box.querySelector('[data-trainer-ref]');
    var claimEl = box.querySelector('[data-trainer-claim]');
    var choices = Array.prototype.slice.call(box.querySelectorAll('[data-choice]'));
    var result = box.querySelector('[data-trainer-result]');
    var verdict = box.querySelector('[data-trainer-verdict]');
    var answer = box.querySelector('[data-trainer-answer]');
    var note = box.querySelector('[data-trainer-note]');
    var open = box.querySelector('[data-trainer-open]');
    var source = box.querySelector('[data-trainer-source]');
    var next = box.querySelector('[data-trainer-next]');
    var score = box.querySelector('[data-trainer-score]');
    var claims = [], deck = [], current = null, right = 0, total = 0, answered = false;

    function shuffle(list) {
      for (var i = list.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var t = list[i]; list[i] = list[j]; list[j] = t;
      }
      return list;
    }
    function draw() {
      if (!deck.length) deck = shuffle(claims.slice());
      current = deck.pop();
      answered = false;
      refEl.textContent = current.ref + ' \u00b7 ' + current.file;
      claimEl.textContent = current.claim;
      result.hidden = true;
      choices.forEach(function (c) {
        c.disabled = false;
        c.classList.remove('is-right', 'is-wrong', 'is-answer');
        c.setAttribute('aria-pressed', 'false');
      });
      next.textContent = S.trainer_next;
      box.classList.add('is-live');
    }
    function reveal(choice) {
      if (answered || !current) return;
      answered = true; total++;
      var ok = choice.dataset.choice === current['class'];
      if (ok) right++;
      var cls = classById(current['class']) || { name: current.classification, note: '' };
      choices.forEach(function (c) {
        c.disabled = true;
        if (c === choice) {
          c.classList.add(ok ? 'is-right' : 'is-wrong');
          c.setAttribute('aria-pressed', 'true');
        }
        if (c.dataset.choice === current['class']) c.classList.add('is-answer');
      });
      verdict.textContent = ok ? S.trainer_right : S.trainer_wrong;
      verdict.className = 'trainer__verdict ' + (ok ? 'is-right' : 'is-wrong');
      answer.textContent = cls.full || cls.name;
      answer.className = 'stamp stamp--' + current['class'];
      note.textContent = cls.note || '';
      open.href = CFG.ledger + '#' + current.id;
      if (current.source) { source.href = current.source; source.hidden = false; }
      else source.hidden = true;
      result.hidden = false;
      score.textContent = fmt(S.trainer_score, { right: right, total: total });
    }
    choices.forEach(function (c) { c.addEventListener('click', function () { reveal(c); }); });
    next.addEventListener('click', draw);

    atlas().then(function (edition) {
      claims = (edition.claims || []).filter(function (c) { return classById(c['class']); });
      if (claims.length < 6) return;
      box.hidden = false;
    }).catch(function () {});
  })();

  /* --- search the atlas: documents, sections and claims, one dialog ------ */

  (function () {
    var openers = Array.prototype.slice.call(document.querySelectorAll('[data-search-open]'));
    if (!CFG.atlas || !window.fetch || typeof HTMLDialogElement === 'undefined') return;
    openers.forEach(function (b) { b.hidden = false; });

    var dialog = null, input = null, list = null, hint = null, index = null, cursor = -1, rows = [];

    function build() {
      dialog = el('dialog', 'palette');
      dialog.setAttribute('aria-label', S.search_h || 'Search');
      var box = el('div', 'palette__box');
      var head = el('div', 'palette__head');
      head.appendChild(el('p', 'eyebrow', S.search_h));
      var close = el('button', 'palette__close', S.search_close);
      close.type = 'button';
      close.addEventListener('click', function () { dialog.close(); });
      head.appendChild(close);
      input = el('input', 'palette__input');
      input.type = 'search'; input.setAttribute('autocomplete', 'off');
      input.placeholder = S.search_placeholder || '';
      input.setAttribute('role', 'combobox');
      input.setAttribute('aria-autocomplete', 'list');
      input.setAttribute('aria-expanded', 'true');
      input.setAttribute('aria-controls', 'palette-results');
      hint = el('p', 'palette__hint', fmt(S.search_hint, { n: '\u2026' }));
      list = el('ol', 'palette__list'); list.id = 'palette-results';
      list.setAttribute('role', 'listbox');
      box.appendChild(head); box.appendChild(input); box.appendChild(hint); box.appendChild(list);
      dialog.appendChild(box);
      document.body.appendChild(dialog);
      dialog.addEventListener('click', function (ev) { if (ev.target === dialog) dialog.close(); });
      input.addEventListener('input', render);
      input.addEventListener('keydown', function (ev) {
        if (ev.key === 'ArrowDown') { ev.preventDefault(); move(1); }
        else if (ev.key === 'ArrowUp') { ev.preventDefault(); move(-1); }
        else if (ev.key === 'Enter') {
          var a = rows[cursor] || rows[0];
          if (a) { ev.preventDefault(); a.click(); }
        }
      });
    }

    function buildIndex(edition) {
      var items = [];
      var root = CFG.root || '';
      (edition.documents || []).forEach(function (d) {
        var kind = d.kind === 'method' ? '' : (d.numeral ? d.numeral + ' \u00b7 ' : '');
        items.push({ group: 'documents', title: kind + d.title, sub: '', href: root + d.url,
                     text: (d.title + ' ' + (d.numeral || '')).toLowerCase() });
        (d.headings || []).forEach(function (h) {
          items.push({ group: 'sections', title: h.text, sub: d.title, href: root + d.url + '#' + h.id,
                       text: (h.text + ' ' + d.title).toLowerCase() });
        });
      });
      (edition.claims || []).forEach(function (c) {
        items.push({ group: 'claims', title: c.claim, sub: c.ref + ' \u00b7 ' + c.classification,
                     cls: c['class'], href: root + edition.ledger + '#' + c.id,
                     text: (c.claim + ' ' + c.ref + ' ' + c.id + ' ' + c.classification + ' ' + c.file).toLowerCase() });
      });
      hint.textContent = fmt(S.search_hint, { n: (edition.claims || []).length });
      return items;
    }

    function matches(item, terms) {
      for (var i = 0; i < terms.length; i++) if (item.text.indexOf(terms[i]) === -1) return false;
      return true;
    }

    function render() {
      rows = []; cursor = -1;
      input.removeAttribute('aria-activedescendant');
      list.textContent = '';
      if (!index) return;
      var q = input.value.trim().toLowerCase();
      var terms = q.split(/\s+/).filter(Boolean);
      var groups = [['documents', S.search_documents, 6], ['sections', S.search_sections, 6], ['claims', S.search_claims, 10]];
      var any = false;
      groups.forEach(function (g) {
        var hits = index.filter(function (it) { return it.group === g[0] && (!terms.length ? g[0] === 'documents' : matches(it, terms)); }).slice(0, g[2]);
        if (!hits.length) return;
        any = true;
        var li = el('li', 'palette__group');
        li.appendChild(el('p', 'palette__label', g[1]));
        var ol = el('ol', 'palette__items');
        hits.forEach(function (it) {
          var item = el('li', 'palette__item');
          var a = el('a', 'palette__link'); a.href = it.href; a.setAttribute('role', 'option');
          a.id = 'palette-opt-' + rows.length; a.setAttribute('aria-selected', 'false');
          if (it.cls) {
            var sw = el('span', 'palette__swatch stamp--' + it.cls); sw.setAttribute('aria-hidden', 'true');
            a.appendChild(sw);
          }
          a.appendChild(el('span', 'palette__title', it.title));
          if (it.sub) a.appendChild(el('span', 'palette__sub', it.sub));
          item.appendChild(a); ol.appendChild(item); rows.push(a);
        });
        li.appendChild(ol); list.appendChild(li);
      });
      if (!any) {
        var empty = el('li', 'palette__empty', S.search_empty + ' ');
        var a = el('a', 'palette__link palette__link--inline', S.search_open_ledger);
        a.href = CFG.ledger + (q ? '?q=' + encodeURIComponent(q) : '');
        a.setAttribute('role', 'option'); a.id = 'palette-opt-0'; a.setAttribute('aria-selected', 'false');
        empty.appendChild(a); list.appendChild(empty); rows.push(a);
      }
    }
    function move(delta) {
      if (!rows.length) return;
      if (cursor >= 0) {
        rows[cursor].classList.remove('is-cursor');
        rows[cursor].setAttribute('aria-selected', 'false');
      }
      cursor = (cursor + delta + rows.length) % rows.length;
      rows[cursor].classList.add('is-cursor');
      rows[cursor].setAttribute('aria-selected', 'true');
      input.setAttribute('aria-activedescendant', rows[cursor].id);
      rows[cursor].scrollIntoView({ block: 'nearest' });
    }
    function open() {
      if (!dialog) build();
      if (!dialog.open) dialog.showModal();
      input.value = ''; render(); input.focus();
      if (!index) {
        atlas().then(function (edition) { index = buildIndex(edition); render(); })
          .catch(function () { hint.textContent = S.search_empty; });
      }
    }
    openers.forEach(function (b) { b.addEventListener('click', open); });
    document.addEventListener('keydown', function (ev) {
      if ((ev.ctrlKey || ev.metaKey) && !ev.altKey && (ev.key === 'k' || ev.key === 'K')) {
        ev.preventDefault(); open();
      } else if (ev.key === '/' && !inField(ev.target) && !document.querySelector('[data-controls]')) {
        ev.preventDefault(); open();
      }
    });
  })();

  /* --- keyboard: step through the series with the arrow keys ------------- */

  document.addEventListener('keydown', function (ev) {
    if (ev.altKey || ev.ctrlKey || ev.metaKey || ev.shiftKey || inField(ev.target)) return;
    var open = document.querySelector('dialog[open]');
    if (open) return;
    var target = null;
    if (ev.key === 'ArrowRight') target = document.querySelector('.series__next');
    if (ev.key === 'ArrowLeft') target = document.querySelector('.series__prev');
    if (target) window.location.href = target.href;
  });

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

  /* Keep the current search and filters in the URL so a reader can hand
     another person exactly the view they are looking at. */
  function syncUrl() {
    if (!window.history || !window.history.replaceState) return;
    var params = new URLSearchParams();
    var q = (search && search.value || '').trim();
    if (q) params.set('q', q);
    if (active.size) params.set('class', Array.from(active).join(','));
    var qs = params.toString();
    window.history.replaceState(null, '', window.location.pathname + (qs ? '?' + qs : '') + window.location.hash);
  }

  function apply() {
    var q = (search && search.value || '').trim().toLowerCase();
    var shown = 0;
    syncUrl();

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
  function fromQuery() {
    var params = new URLSearchParams(window.location.search);
    var q = params.get('q'), cls = params.get('class');
    if (!q && !cls) return;
    if (q && search) search.value = q;
    (cls || '').split(',').forEach(function (id) {
      var match = filters.filter(function (f) { return f.dataset.class === id; })[0];
      if (match) { active.add(id); match.setAttribute('aria-pressed', 'true'); }
    });
    apply();
    if (!window.location.hash) controls.scrollIntoView({ block: 'start' });
  }
  fromQuery();
  fromHash();
  window.addEventListener('hashchange', fromHash);

  /* Every claim can be copied as a permanent link or a citation. */
  var canonical = (CFG.canonical || window.location.href).split('#')[0].split('?')[0];
  claims.forEach(function (claim) {
    var meta = claim.querySelector('.claim__meta');
    if (!meta) return;
    var actions = el('span', 'claim__actions');
    var live = el('span', 'claim__copied');
    live.setAttribute('aria-live', 'polite');
    var link = canonical + '#' + claim.id;
    function flash(msg) {
      live.textContent = msg;
      window.setTimeout(function () { live.textContent = ''; }, 2000);
    }
    var copy = el('button', 'claim__action', S.copy_link);
    copy.type = 'button';
    copy.addEventListener('click', function () { copyText(link).then(function () { flash(S.copied); }); });
    var cite = el('button', 'claim__action', S.copy_citation);
    cite.type = 'button';
    cite.addEventListener('click', function () {
      copyText(fmt(S.claim_citation, { author: CFG.author, site: CFG.site, ref: claim.dataset.ref,
                                       id: claim.id, edition: CFG.edition, version: CFG.version, url: link }))
        .then(function () { flash(S.citation_copied); });
    });
    actions.appendChild(copy); actions.appendChild(cite);
    if (navigator.share) {
      var shareBtn = el('button', 'claim__action', S.share);
      shareBtn.type = 'button';
      var text = claim.querySelector('.claim__text');
      shareBtn.addEventListener('click', function () {
        navigator.share({ title: claim.dataset.ref + ' \u00b7 ' + CFG.short,
                          text: text ? text.textContent : '', url: link }).catch(function () {});
      });
      actions.appendChild(shareBtn);
    }
    actions.appendChild(live);
    meta.appendChild(actions);
  });

  document.addEventListener('keydown', function (ev) {
    if (ev.key === '/' && !inField(ev.target) && search && !document.querySelector('dialog[open]')) {
      ev.preventDefault(); search.focus(); search.select();
    }
  });
})();
