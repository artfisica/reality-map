#!/usr/bin/env python3
"""Build The Civilian Geopolitical Reality Map into a bilingual static site.

The markdown in content/ is canonical and is never rewritten. Everything the
site shows about evidence classes, claim counts and cross references is derived
from those files at build time, so the published apparatus cannot drift from
the text.

Usage:
    python build.py            # build into docs/
    python build.py --serve    # build, then serve docs/ on :8000
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

try:
    import markdown
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("Missing dependencies. Run: pip install -r requirements.txt")

from markdown.extensions.toc import slugify

ROOT = Path(__file__).parent.resolve()
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
OUT = ROOT / "docs"
WPM = 230


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------


@dataclass
class Source:
    n: int
    text_html: str
    url: str
    issuer: str
    domain: str


@dataclass
class Claim:
    cid: str
    semantic: bool
    ref: str
    section: str
    section_slug: str
    class_id: str
    classification: str
    claim_html: str
    claim_text: str
    source_html: str
    source_url: str
    permitted_html: str
    avoid_html: str


@dataclass
class Doc:
    slug: str
    title: str
    subtitle: str
    author: str
    dateline: str
    standfirst: str
    body_html: str
    toc: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    sources_note: str = ""
    auth_heading: str = ""
    auth_refs: list = field(default_factory=list)
    words: int = 0
    numeral: str = ""
    ledger_sections: list = field(default_factory=list)
    url: str = ""
    depth: int = 1

    @property
    def minutes(self) -> int:
        return max(1, round(self.words / WPM))


def make_md() -> markdown.Markdown:
    return markdown.Markdown(
        extensions=["tables", "attr_list", "toc", "sane_lists"],
        extension_configs={"toc": {"permalink": False, "toc_depth": "2-3"}},
    )


def inline(text: str) -> str:
    out = make_md().convert(text.strip())
    out = re.sub(r"^<p>|</p>$", "", out.strip())
    return out.replace("</p>\n<p>", "<br>")


def e(text: str) -> str:
    return html.escape(str(text), quote=True)


def t(ui: dict, key: str, **kw) -> str:
    value = ui.get(key, key)
    for k, v in kw.items():
        value = value.replace("{" + k + "}", str(v))
    return value


def parse_reference(rest: str, n: int) -> Source:
    url = ""
    link = re.search(r"<(https?://[^>\s]+)>\s*$", rest) or \
        re.search(r"(https?://\S+)\s*$", rest)
    if link:
        url = link.group(1)
        rest = rest[: link.start()].rstrip().rstrip(":").rstrip()
    issuer = re.split(r",|\u2014| \u2013 ", rest)[0].strip(" *_")
    return Source(n, inline(rest), url, issuer,
                  urlsplit(url).netloc.replace("www.", "") if url else "")


def split_sources(body: str) -> tuple[str, list[Source], str, str, list[Source]]:
    """Return (body, sources, note, authorial_heading, authorial_refs).

    Authorial context is a separate H3 block after the numbered sources. It is
    the author writing in his own voice, not a document of record, so it is
    parsed and rendered separately rather than folded into the source list.
    """
    m = None
    for m in re.finditer(r"^##\s+(?:Core\s+|Fuentes\s+)?(?:Sources|Fuentes)"
                         r"(?:\s+(?:principales|centrales))?\s*$", body, re.M | re.I):
        pass
    if not m:
        return body, [], "", "", []

    head = re.sub(r"\n-{3,}\s*$", "\n", body[: m.start()].rstrip()) + "\n"
    tail = body[m.end():]

    auth_h, auth_md = "", ""
    a = re.search(r"^###\s+(.+?)\s*$", tail, re.M)
    if a:
        auth_h, auth_md = a.group(1), tail[a.end():]
        tail = tail[: a.start()]

    sources, note = [], []
    for raw in tail.splitlines():
        line = raw.strip()
        if not line:
            continue
        item = re.match(r"^(\d+)\.\s+(.*)$", line)
        if item:
            sources.append(parse_reference(item.group(2), int(item.group(1))))
        else:
            note.append(line)

    auth = []
    for raw in auth_md.splitlines():
        line = raw.strip()
        item = re.match(r"^(?:[-*]|\d+\.)\s+(.*)$", line)
        if item:
            auth.append(parse_reference(item.group(1), len(auth) + 1))

    return (head, sources, inline(" ".join(note)) if note else "", auth_h, auth)


def parse_doc(path: Path, slug: str, depth: int, url: str) -> Doc:
    raw = path.read_text(encoding="utf-8")

    title = ""
    m = re.match(r"^#\s+(.+?)\s*$", raw, re.M)
    if m:
        title = m.group(1)
        raw = raw[: m.start()] + raw[m.end():]

    subtitle = ""
    m = re.match(r"^\s*##\s+(.+?)\s*$", raw, re.M)
    if m and m.start() < 200:
        subtitle = m.group(1)
        raw = raw[: m.start()] + raw[m.end():]

    author = dateline = ""
    byline = re.match(r"^\s*((?:\*\*[^\n]+\*\*\s*\n?)+)", raw)
    if byline:
        for line in byline.group(1).strip().splitlines():
            value = line.strip().strip("*").strip()
            low = value.lower()
            if low.startswith(("by ", "por ", "author:", "autor:")):
                author = re.sub(r"^(by|por|author:|autor:)\s*", "", value, flags=re.I)
            elif value:
                dateline = re.sub(r"^(edition|edici[oó]n):\s*", "", value, flags=re.I)
        raw = raw[byline.end():]

    standfirst = ""
    lead = re.match(r"^\s*\*([^*][^\n]*(?:\n[^\n]+)*?)\*\s*\n", raw)
    if lead:
        standfirst = inline(lead.group(1))
        raw = raw[lead.end():]

    body_md, sources, note, auth_h, auth = split_sources(raw)
    words = len(re.findall(r"\b[\w'\u2019\u00c0-\u017f-]+\b", body_md))

    md = make_md()
    body = md.convert(body_md.strip())
    body = body.replace("<table>", '<div class="table-scroll"><table>')
    body = body.replace("</table>", "</table></div>")
    body = re.sub(r'<a href="(https?://[^"]+)"',
                  r'<a class="exlink" target="_blank" rel="noopener noreferrer" href="\1"',
                  body)
    body = re.sub(r"(<h2[^>]*>)", r'<div class="sec-rule"></div>\1', body, count=0)

    return Doc(slug=slug, title=title, subtitle=subtitle, author=author,
               dateline=dateline, standfirst=standfirst, body_html=body,
               toc=md.toc_tokens, sources=sources, sources_note=note,
               auth_heading=auth_h, auth_refs=auth,
               words=words, url=url, depth=depth)


def classify(classification: str, classes: list[dict], order: list[str]) -> str:
    """Map a Classification cell to an evidence class, or return "" if unknown.

    There is deliberately no default. An unrecognised classification used to
    fall through to "record", which silently promoted an unmapped category to a
    verified event. Unknown classifications now stop the build instead.
    """
    low = classification.lower()
    by_id = {c["id"]: c for c in classes}
    for cid in order:
        for token in by_id.get(cid, {}).get("match") or []:
            if token in low:
                return cid
    return ""


def parse_ledger(path: Path, classes: list[dict], order: list[str]):
    raw = path.read_text(encoding="utf-8")
    problems: list[tuple[str, str]] = []
    sections: list[dict] = []
    intro_md = re.sub(r"^#\s+.*$", "", re.split(r"^##\s+.+?\s*$", raw, flags=re.M)[0],
                      flags=re.M)
    outro_md = ""

    parts = re.split(r"^##\s+(.+?)\s*$", raw, flags=re.M)
    seq = 0
    first = True
    for i in range(1, len(parts), 2):
        heading, block = parts[i], parts[i + 1]
        rows = [r for r in block.splitlines() if r.strip().startswith("|")]
        header = [c.strip() for c in rows[0].strip().strip("|").split("|")] if rows else []

        if len(rows) < 3 or len(header) != 5:
            # Framing, not a claims file. The very first heading repeats the
            # document subtitle, so it is dropped; later ones are kept.
            target = "outro" if sections else "intro"
            text = block if (first and target == "intro") else f"\n## {heading}\n{block}"
            if target == "intro":
                intro_md += text
            else:
                outro_md += text
            first = False
            continue

        first = False
        slug = slugify(heading, "-")
        claims, last_url = [], ""
        for row in rows[2:]:
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) != 5:
                problems.append(("error", f"{heading}: a claim row has {len(cells)} "
                                          f"cells, expected 5 -> {row.strip()[:80]}"))
                continue
            claim, classification, source, permitted, avoid = cells
            seq += 1

            # A stable anchor. An explicit {#SEMANTIC-ID} in the claim cell wins;
            # otherwise the anchor is derived from the claim text, so inserting a
            # row never renumbers the ones below it.
            cid = ""
            explicit = re.search(r"\{#([A-Za-z0-9_.:-]+)\}\s*$", claim)
            if explicit:
                cid = explicit.group(1)
                claim = claim[: explicit.start()].rstrip()
            plain = re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", claim.lower())).strip()
            if not cid:
                cid = "q" + hashlib.sha1(plain.encode("utf-8")).hexdigest()[:7]

            class_id = classify(classification, classes, order)
            if not class_id:
                problems.append(("error", f"{heading}: unknown classification "
                                          f"\u201c{classification}\u201d "
                                          f"(claim {seq}). Add a match token in "
                                          f"site.yaml or correct the cell."))
                class_id = "unknown"

            url = ""
            link = re.search(r"\((https?://[^)]+)\)", source)
            if link:
                url = last_url = link.group(1)
            elif re.match(r"^(same|mism[ao]|el mismo|la misma)\b", source.strip(), re.I):
                url = last_url

            claims.append(Claim(
                cid=cid, semantic=bool(explicit),
                ref=f"C{seq:02d}", section=heading, section_slug=slug,
                class_id=class_id, classification=classification,
                claim_html=inline(claim), claim_text=re.sub(r"<[^>]+>", "", inline(claim)),
                source_html=inline(source), source_url=url,
                permitted_html=inline(permitted), avoid_html=inline(avoid)))
        sections.append({"title": heading, "slug": slug, "claims": claims})

    intro_md = re.sub(r"^\*\*.*\*\*\s*$", "", intro_md, flags=re.M)
    intro = make_md().convert(intro_md.strip())
    intro = intro.replace("<table>", '<div class="table-scroll"><table>')
    intro = intro.replace("</table>", "</table></div>")
    outro = make_md().convert(outro_md.strip()) if outro_md.strip() else ""
    return intro, sections, outro, problems


# --------------------------------------------------------------------------
# components
# --------------------------------------------------------------------------


def stamp(cls: dict, count=None, href="", mini=False) -> str:
    tag = "a" if href else "span"
    attrs = f' href="{href}"' if href else ""
    label = cls["full"] if count is None else f'{count} \u00b7 {cls["full"]}'
    name = "" if mini else f'<span class="stamp__name">{e(cls["name"])}</span>'
    num = f'<span class="stamp__n">{count}</span>' if count is not None else ""
    klass = "stamp stamp--" + cls["id"] + (" stamp--mini" if mini else "")
    return (f'<{tag} class="{klass}"{attrs} title="{e(label)}" aria-label="{e(label)}">'
            f'{name}{num}</{tag}>')


def evidence_bar(counts: dict, classes: list[dict], total: int) -> str:
    if not total:
        return ""
    segs = []
    for cls in classes:
        n = counts.get(cls["id"], 0)
        if not n:
            continue
        segs.append(f'<span class="bar__seg bar--{cls["id"]}" '
                    f'style="flex:{n}" title="{e(str(n) + " " + cls["full"])}"></span>')
    return f'<span class="bar" role="img" aria-hidden="true">{"".join(segs)}</span>'


def mosaic(sections: list[dict], ledger_url: str, classes: list[dict]) -> str:
    by_id = {c["id"]: c for c in classes}
    groups = []
    for sec in sections:
        tiles = []
        for c in sec["claims"]:
            label = f'{c.ref} \u00b7 {by_id[c.class_id]["full"]} \u00b7 {c.claim_text}'
            tiles.append(f'<a class="tile tile--{c.class_id}" href="{ledger_url}#{c.cid}" '
                         f'title="{e(label)}" aria-label="{e(label)}"></a>')
        groups.append(f'<span class="mosaic__g" title="{e(sec["title"])}">'
                      f'{"".join(tiles)}</span>')
    return f'<div class="mosaic">{"".join(groups)}</div>'


def toc_html(tokens: list, label: str) -> str:
    if not tokens:
        return ""
    items = "".join(f'<li><a href="#{x["id"]}">{x["name"]}</a></li>' for x in tokens)
    return (f'<aside class="toc" aria-label="{e(label)}">'
            f'<p class="toc__label">{e(label)}</p>'
            f'<ol class="toc__list">{items}</ol></aside>')


def sources_html(doc: Doc, ui: dict) -> str:
    if not doc.sources:
        return ""
    items = []
    for s in doc.sources:
        link = (f'<a class="source__url" target="_blank" rel="noopener noreferrer" '
                f'href="{e(s.url)}">{e(s.domain)} <span aria-hidden="true">&#8250;</span></a>'
                if s.url else "")
        items.append(f'<li class="source" id="source-{s.n}">'
                     f'<span class="source__n">{s.n:02d}</span>'
                     f'<span class="source__body">{s.text_html}{link}</span></li>')
    note = f'<p class="sources__note">{doc.sources_note}</p>' if doc.sources_note else ""

    auth = ""
    if doc.auth_refs:
        rows = []
        for s2 in doc.auth_refs:
            link = (f'<a class="source__url" target="_blank" rel="noopener noreferrer" '
                    f'href="{e(s2.url)}">{e(s2.domain)} <span aria-hidden="true">&#8250;</span></a>'
                    if s2.url else "")
            rows.append(f'<li class="source source--auth">'
                        f'<span class="source__n" aria-hidden="true">&#8226;</span>'
                        f'<span class="source__body">{s2.text_html}{link}</span></li>')
        auth = (f'<section class="authorial" id="authorial">'
                f'<h3 class="authorial__h">{e(doc.auth_heading)}</h3>'
                f'<p class="authorial__lede">{e(t(ui, "authorial_lede"))}</p>'
                f'<ul class="sources__list">{"".join(rows)}</ul></section>')

    return (f'<section class="sources" id="sources"><h2 class="sources__h">'
            f'{e(t(ui, "sources_h"))}</h2><p class="sources__lede">{e(t(ui, "sources_lede"))}</p>'
            f'<ol class="sources__list">{"".join(items)}</ol>{note}{auth}</section>')


def issuers(doc: Doc, ui: dict) -> str:
    if not doc.sources:
        return ""
    seen, chips = set(), []
    for s in doc.sources:
        key = s.issuer.lower()
        if key and key not in seen:
            seen.add(key)
            chips.append(f"<li>{e(s.issuer)}</li>")
    return (f'<div class="issuers"><p class="issuers__label">{e(t(ui, "documented_from"))}</p>'
            f'<ul class="issuers__list">{"".join(chips)}</ul></div>')


def chrome(L: dict, alt: dict, prefix: str, active: str, alt_url: str) -> str:
    ui = L["ui"]
    base = prefix + (L["dir"] + "/" if L["dir"] else "")
    items = [("method", L["method"]["label"], f'{base}{L["method"]["slug"]}/')]
    for s in L["studies"]:
        items.append((s["slug"], s["numeral"], f'{base}{L["studies_dir"]}/{s["slug"]}/'))
    items.append(("map", L["map"]["label"], f'{base}{L["map"]["slug"]}/'))
    items.append(("ledger", L["ledger"]["label"], f'{base}{L["ledger"]["slug"]}/'))

    links = ""
    for slug, label, href in items:
        on = slug == active
        cur = ' aria-current="page"' if on else ""
        links += (f'<a class="nav__link{" is-active" if on else ""}" href="{href}"{cur}>'
                  f"{e(label)}</a>")

    return f"""<nav class="nav" aria-label="{e(L['short'])}">
  <a class="nav__home{' is-active' if active == 'home' else ''}" href="{base}">
    <span class="nav__mark" aria-hidden="true"></span><span>{e(L['short'])}</span></a>
  <div class="nav__links">{links}</div>
  <a class="nav__lang" href="{alt_url}" lang="{alt['code']}" hreflang="{alt['code']}">{e(alt['label'])}</a>
  <button class="nav__mode" type="button" data-mode-toggle
    data-dark="{e(t(ui, 'mode_dark'))}" data-light="{e(t(ui, 'mode_light'))}"
    aria-label="{e(t(ui, 'mode_dark'))}"><span data-mode-label>{e(t(ui, 'mode_dark'))}</span></button>
</nav>"""


def shell(L: dict, alt: dict, *, title: str, description: str, depth: int, body: str,
          active: str = "", page: str = "", alt_url: str = "", path: str = "",
          alt_path: str = "") -> str:
    prefix = "../" * depth
    ui = L["ui"]
    lang_base = prefix + (L["dir"] + "/" if L["dir"] else "")
    ai_href = f'{lang_base}{L["method"]["slug"]}/#{t(ui, "ai_anchor")}'
    site_base = L["base_url"].rstrip("/")
    canonical = f'{site_base}/{path.lstrip("/")}'
    alt_abs = f'{site_base}/{alt_path.lstrip("/")}'

    full = title if title == L["title"] else f'{title} \u00b7 {L["short"]}'
    return f"""<!DOCTYPE html>
<html lang="{L['code']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full)}</title>
<meta name="description" content="{e(description)}">
<meta name="author" content="{e(L.get('author', 'Arturo Sanchez Pineda'))}">
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{e(L['title'])}">
<meta property="og:locale" content="{L['code']}">
<meta property="og:image" content="{site_base}/assets/social.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="{L['code']}" href="{canonical}">
<link rel="alternate" hreflang="{alt['code']}" href="{alt_abs}">
<link rel="alternate" hreflang="x-default" href="{site_base}/">
<link rel="stylesheet" href="{prefix}assets/atlas.css">
<link rel="icon" href="{prefix}assets/mark.svg" type="image/svg+xml">
<script>(function(){{try{{var m=localStorage.getItem('rm-mode');if(m)document.documentElement.dataset.mode=m;}}catch(e){{}}}})();</script>
</head>
<body class="{page}">
<a class="skip" href="#main">{e(t(ui, 'skip'))}</a>
{chrome(L, alt, prefix, active, alt_url)}
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="foot__grid">
    <div><p class="foot__title">{e(L['title'])}</p>
      <p class="foot__meta">{e(L['edition'])} \u00b7 v{e(L['version'])}</p></div>
    <div><p class="foot__meta">{e(t(ui, 'foot_1'))}</p>
      <p class="foot__meta">{e(t(ui, 'foot_2'))}</p>
      <p class="foot__meta"><a class="foot__link" href="{ai_href}">{e(t(ui, 'foot_ai'))}</a></p></div>
  </div>
  <p class="foot__rule">&copy; {date.today().year} {e(L.get('author', 'Arturo Sanchez Pineda'))}</p>
</footer>
<script src="{prefix}assets/atlas.js" defer></script>
</body>
</html>"""


def render_map(L, alt, geo, alt_url, path, alt_path):
    """The atlas located. Markers say where a study looks, never what a place is.

    Nothing here is coloured. On the rest of the site colour means evidence
    class; a filled territory would be colour asserting a legal conclusion, so
    the map stays monochrome and puts the status in words instead.
    """
    M, ui = L["map"], L["ui"]
    depth = 2 if L["dir"] else 1
    prefix = "../" * depth
    base = prefix + (L["dir"] + "/" if L["dir"] else "")
    by_numeral = {study["numeral"]: study["slug"] for study in L["studies"]}
    vb_x, vb_y, vb_w, vb_h = (float(value) for value in geo["viewBox"].split())

    pins, rows, groups = [], [], {}
    for place in M["places"]:
        x, y = geo["points"][place["id"]]
        # Markers are HTML overlays so their labels remain legible when the SVG
        # contracts on a phone. Offsets are CSS pixels, not geographic units:
        # they separate dense clusters without changing the basemap geometry.
        dx, dy = place.get("offset", (0, 0))
        px = (x - vb_x) / vb_w * 100
        py = (y - vb_y) / vb_h * 100
        href = f'{base}{L["studies_dir"]}/{by_numeral[place["numeral"]]}/'
        label = f'{place["numeral"]} \u00b7 {place["name"]}'
        pins.append(
            f'<a class="map-pin" href="{href}" aria-label="{e(label)}" '
            f'data-label="{e(place["name"])}" style="--map-x:{px:.3f}%;'
            f'--map-y:{py:.3f}%;--map-dx:{dx}px;--map-dy:{dy}px">'
            f'<span aria-hidden="true">{e(place["numeral"])}</span></a>')
        groups.setdefault(place["numeral"], []).append(place)

    for numeral, places in groups.items():
        items = "".join(
            f'<li class="place"><span class="place__n">{e(p["name"])}</span>'
            f'<span class="place__s">{e(p["status"])}</span></li>' for p in places)
        rows.append(
            f'<div class="legend__group">'
            f'<a class="legend__study" href="{base}{L["studies_dir"]}/{by_numeral[numeral]}/">'
            f'<span class="legend__num">{e(numeral)}</span>'
            f'<span>{e(t(ui, "case_study"))} {e(numeral)}</span></a>'
            f'<ul class="places">{items}</ul></div>')

    body = f"""
<article class="mappage">
  <header class="doc__head">
    <p class="eyebrow">{e(M['eyebrow'])}</p>
    <h1 class="doc__title">{e(M['title'])}</h1>
    <p class="doc__subtitle">{e(M['subtitle'])}</p>
  </header>
  <p class="lede mappage__lede">{e(M['lede'])}</p>
  <figure class="atlasmap">
    <div class="atlasmap__stage">
      <svg viewBox="{geo['viewBox']}" role="img" xmlns="http://www.w3.org/2000/svg">
        <title>{e(M['title'])}</title>
        <desc>{e(M['lede'])}</desc>
        <path class="sphere" fill="#ffffff" stroke="#767676" d="{geo['sphere']}"/>
        <path class="grat" fill="none" stroke="#c4c4c4" d="{geo['graticule']}"/>
        <path class="land" fill="#e8e8e8" stroke="#9a9a9a" d="{geo['land']}"/>
      </svg>
      <div class="map-pins">{"".join(pins)}</div>
    </div>
    <figcaption class="note">{e(M['note'])}</figcaption>
  </figure>
  <div class="legend">{"".join(rows)}</div>
</article>"""
    return shell(L, alt, title=M["title"], description=M["lede"][:180], depth=depth,
                 body=body, active="map", page="page-map", alt_url=alt_url,
                 path=path, alt_path=alt_path)


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------


def render_home(L, alt, method, studies, sections, claims, standfirst, alt_url, depth,
                path, alt_path):
    ui, classes = L["ui"], L["evidence_classes"]
    counts = {c["id"]: 0 for c in classes}
    for c in claims:
        if c.class_id in counts:
            counts[c.class_id] += 1

    key = "".join(
        f'<li class="key__row">{stamp(c, counts[c["id"]], href=f"{L["ledger"]["slug"]}/#class={c["id"]}")}'
        f'<p class="key__note">{e(c["note"])}</p></li>' for c in classes)

    entries = []
    docs = [("00", method, f'{L["method"]["slug"]}/', t(ui, "the_method"))]
    docs += [(d.numeral, d, f'{L["studies_dir"]}/{d.slug}/',
              f'{t(ui, "case_study")} {d.numeral}') for d in studies]
    for numeral, doc, href, kind in docs:
        mine = [c for c in claims if c.section in (doc.ledger_sections or [])]
        cnt = {}
        for c in mine:
            cnt[c.class_id] = cnt.get(c.class_id, 0) + 1
        entries.append(f"""<li class="entry">
  <a class="entry__link" href="{href}">
    <span class="entry__num" aria-hidden="true">{e(numeral)}</span>
    <span class="entry__main">
      <span class="entry__kind">{e(kind)}</span>
      <span class="entry__title">{e(doc.title)}</span>
      <span class="entry__sub">{e(doc.subtitle)}</span>
      {evidence_bar(cnt, classes, len(mine))}
    </span>
    <span class="entry__meta"><span>{doc.minutes} {e(t(ui, "min_read"))}</span>
      <span>{len(doc.sources)} {e(t(ui, "sources"))}</span>
      {f'<span>{len(mine)} {e(t(ui, "claims"))}</span>' if mine else ''}</span>
  </a></li>""")

    body = f"""
<header class="cover">
  <div class="cover__in">
    <p class="cover__stamp"><span>{e(L['edition'])}</span><span>v{e(L['version'])}</span></p>
    <h1 class="cover__title">{"".join(f"<span>{e(w)}</span>" for w in L.get('title_lines') or L['title'].split(' ', 2))}</h1>
    <p class="cover__tagline">{e(L['tagline'])}</p>
    <div class="cover__mosaic">
      {mosaic(sections, L["ledger"]["slug"] + "/", classes)}
      <p class="cover__caption">{e(t(ui, 'mosaic_caption'))}</p>
    </div>
    <p class="cover__by">{e(L.get('author', 'Arturo Sanchez Pineda'))}</p>
  </div>
</header>

<section class="position">
  <p class="eyebrow">{e(t(ui, 'position_label'))}</p>
  <div class="position__text">{standfirst}</div>
</section>

<section class="key">
  <div class="key__head">
    <h2 class="h-lg">{e(t(ui, 'key_h'))}</h2>
    <p class="lede">{e(t(ui, 'key_lede', n=len(claims)))}</p>
  </div>
  <ol class="key__list">{key}</ol>
  <p class="note">{e(t(ui, 'bar_note'))}</p>
  <a class="cta" href="{L['ledger']['slug']}/">{e(t(ui, 'open_ledger'))}
    <span aria-hidden="true">&#8250;</span></a>
</section>

<section class="register">
  <div class="register__head">
    <h2 class="h-lg">{e(t(ui, 'register_h'))}</h2>
    <p class="lede">{e(t(ui, 'register_lede'))}</p>
  </div>
  <ol class="register__list">{"".join(entries)}</ol>
</section>

<section class="ways">
  <h2 class="h-sm">{e(t(ui, 'ways_h'))}</h2>
  <div class="ways__grid">
    <a class="way" href="{L['method']['slug']}/"><span class="way__k">{e(t(ui, 'way1_k'))}</span>
      <span class="way__d">{e(t(ui, 'way1_d'))}</span></a>
    <a class="way" href="{L['studies_dir']}/{studies[4].slug}/"><span class="way__k">{e(t(ui, 'way2_k'))}</span>
      <span class="way__d">{e(t(ui, 'way2_d'))}</span></a>
    <a class="way" href="{L['ledger']['slug']}/"><span class="way__k">{e(t(ui, 'way3_k'))}</span>
      <span class="way__d">{e(t(ui, 'way3_d', n=len(claims), f=len(sections)))}</span></a>
    <a class="way" href="{L['map']['slug']}/"><span class="way__k">{e(t(ui, 'way4_k'))}</span>
      <span class="way__d">{e(t(ui, 'way4_d'))}</span></a>
  </div>
</section>
"""
    return shell(L, alt, title=L["title"], description=L["description"], depth=depth,
                 body=body, active="home", page="page-home", alt_url=alt_url,
                 path=path, alt_path=alt_path)


def render_method_map(L: dict) -> str:
    """Render the method as a compact, bilingual operational map."""
    maps = {
        "en": {
            "eyebrow": "The method at a glance",
            "title": "From official language to observable conduct",
            "lede": ("Classify the claim, compare declared order with the forces "
                     "that predict conduct, measure the response, apply the five "
                     "tests and turn the result into civilian preparation."),
            "gate": "Classify every claim",
            "classes": "fact · position · finding · court rule · allegation · inference · risk",
            "declared": "Declared order",
            "observed": "What predicts conduct",
            "layers_label": "02 · Six-layer power map",
            "distance": "The distance between them is the object of study",
            "layers": [
                ("01", "Rule", "What does law require?"),
                ("02", "Declaration", "What principle is invoked?"),
                ("03", "Interest", "What objective is protected?"),
                ("04", "Dependency", "What limits freedom of action?"),
                ("05", "Instrument", "What tool is used or withheld?"),
                ("06", "Cost", "Who benefits; who absorbs it?"),
            ],
            "gradient": "Enforcement gradient",
            "gradient_href": "#3-the-enforcement-gradient",
            "steps": ["Concern", "Humanitarian aid", "Evidence", "Suspension",
                      "Individual measures", "Arms restrictions", "Isolation",
                      "Collective action"],
            "tests_label": "Five tests",
            "tests": [
                ("04", "Protected ally", "#4-the-protected-ally-test"),
                ("05", "Colonial continuity", "#5-the-colonial-continuity-test"),
                ("06", "Intervention lifecycle", "#6-the-intervention-lifecycle"),
                ("07", "Target construction", "#7-the-target-construction-test"),
                ("08", "Sovereignty under coercion", "#8-sovereignty-under-coercion"),
            ],
            "protocol_label": "Civilian operating protocol",
            "protocol": [
                ("Build an evidence file", "#build-an-evidence-file"),
                ("Map practical dependencies", "#map-practical-dependencies"),
                ("Read institutional behaviour", "#read-institutional-behaviour"),
                ("Maintain intellectual discipline", "#maintain-intellectual-discipline"),
            ],
            "result": "Do not confuse a declared right with effective protection.",
            "layer_href": "#2-the-six-layer-power-map",
            "gate_href": "#1-the-discipline-of-naming-facts",
        },
        "es": {
            "eyebrow": "El método, en una mirada",
            "title": "Del lenguaje oficial a la conducta observable",
            "lede": ("Clasifique la afirmación, compare el orden declarado con las "
                     "fuerzas que predicen la conducta, mida la respuesta, aplique las "
                     "cinco pruebas y traduzca el resultado en preparación civil."),
            "gate": "Clasifique cada afirmación",
            "classes": "hecho · posición · conclusión · decisión judicial · alegación · inferencia · riesgo",
            "declared": "Orden declarado",
            "observed": "Lo que predice la conducta",
            "layers_label": "02 · Mapa de poder en seis capas",
            "distance": "La distancia entre ambos es el objeto de estudio",
            "layers": [
                ("01", "Norma", "¿Qué exige el derecho?"),
                ("02", "Declaración", "¿Qué principio se invoca?"),
                ("03", "Interés", "¿Qué objetivo se protege?"),
                ("04", "Dependencia", "¿Qué limita el margen de acción?"),
                ("05", "Instrumento", "¿Qué herramienta se usa o se retiene?"),
                ("06", "Costo", "¿Quién gana; quién lo absorbe?"),
            ],
            "gradient": "Escala de respuesta estatal",
            "gradient_href": "#3-la-escala-de-respuesta-estatal",
            "steps": ["Preocupación", "Ayuda humanitaria", "Pruebas e investigación",
                      "Suspensión", "Medidas individuales", "Restricción de armas",
                      "Aislamiento", "Acción colectiva"],
            "tests_label": "Cinco pruebas",
            "tests": [
                ("04", "Aliado protegido", "#4-la-prueba-del-aliado-protegido"),
                ("05", "Continuidad colonial", "#5-la-prueba-de-continuidad-colonial"),
                ("06", "Ciclo de intervención", "#6-el-ciclo-de-vida-de-una-intervencion"),
                ("07", "Construcción del objetivo", "#7-la-prueba-de-construccion-del-objetivo"),
                ("08", "Soberanía bajo coerción", "#8-soberania-bajo-coercion"),
            ],
            "protocol_label": "Protocolo operativo civil",
            "protocol": [
                ("Construya un expediente", "#construya-un-expediente"),
                ("Dibuje sus dependencias", "#dibuje-sus-dependencias-practicas"),
                ("Lea la conducta institucional", "#lea-la-conducta-institucional"),
                ("Mantenga disciplina intelectual", "#mantenga-disciplina-intelectual"),
            ],
            "result": "No confunda un derecho reconocido con una protección efectiva.",
            "layer_href": "#2-el-mapa-de-poder-en-seis-capas",
            "gate_href": "#1-la-disciplina-de-nombrar-los-hechos",
        },
    }
    M = maps[L["code"]]

    def layer(item):
        n, name, question = item
        return (f'<a class="methodmap__layer" href="{M["layer_href"]}">'
                f'<span class="methodmap__n">{n}</span>'
                f'<span><strong>{e(name)}</strong><small>{e(question)}</small></span></a>')

    declared = "".join(layer(x) for x in M["layers"][:2])
    observed = "".join(layer(x) for x in M["layers"][2:])
    steps = "".join(f'<li><span>{i:02d}</span>{e(label)}</li>'
                    for i, label in enumerate(M["steps"], 1))
    tests = "".join(
        f'<a href="{href}"><span>{n}</span><strong>{e(label)}</strong></a>'
        for n, label, href in M["tests"])
    protocol = "".join(
        f'<a href="{href}"><span>{i:02d}</span>{e(label)}</a>'
        for i, (label, href) in enumerate(M["protocol"], 1))

    return f"""
<section class="methodmap on-deep" aria-labelledby="methodmap-title">
  <header class="methodmap__head">
    <p class="eyebrow">{e(M['eyebrow'])}</p>
    <h2 id="methodmap-title">{e(M['title'])}</h2>
    <p>{e(M['lede'])}</p>
  </header>
  <a class="methodmap__gate" href="{M['gate_href']}">
    <span class="methodmap__section">01</span>
    <strong>{e(M['gate'])}</strong>
    <small>{e(M['classes'])}</small>
  </a>
  <div class="methodmap__arrow" aria-hidden="true">&#8595;</div>
  <p class="methodmap__layers-label">{e(M['layers_label'])}</p>
  <div class="methodmap__layers">
    <section aria-label="{e(M['declared'])}">
      <p>{e(M['declared'])}</p>{declared}
    </section>
    <div class="methodmap__distance"><span>{e(M['distance'])}</span></div>
    <section aria-label="{e(M['observed'])}">
      <p>{e(M['observed'])}</p>{observed}
    </section>
  </div>
  <div class="methodmap__arrow" aria-hidden="true">&#8595;</div>
  <a class="methodmap__gradient" href="{M['gradient_href']}">
    <span class="methodmap__section">03</span><strong>{e(M['gradient'])}</strong>
    <ol>{steps}</ol>
  </a>
  <div class="methodmap__arrow methodmap__arrow--branch" aria-hidden="true">&#8595;</div>
  <section class="methodmap__tests" aria-label="{e(M['tests_label'])}">
    <p>{e(M['tests_label'])}</p><div>{tests}</div>
  </section>
  <div class="methodmap__arrow" aria-hidden="true">&#8595;</div>
  <section class="methodmap__protocol" aria-label="{e(M['protocol_label'])}">
    <p><span>09</span>{e(M['protocol_label'])}</p><div>{protocol}</div>
  </section>
  <p class="methodmap__result">{e(M['result'])}</p>
</section>"""


def render_doc(L, alt, doc, claims, kind, prev, nxt, alt_url, alt_path):
    ui, classes = L["ui"], L["evidence_classes"]
    prefix = "../" * doc.depth
    mine = [c for c in claims if c.section in (doc.ledger_sections or [])]

    evidence = ""
    if mine:
        cnt = {}
        for c in mine:
            cnt[c.class_id] = cnt.get(c.class_id, 0) + 1
        chips = "".join(stamp(cls, cnt[cls["id"]],
                              href=f'{prefix}{L["dir"] + "/" if L["dir"] else ""}'
                                   f'{L["ledger"]["slug"]}/#class={cls["id"]}')
                        for cls in classes if cls["id"] in cnt)
        evidence = f"""<div class="evidence">
  <p class="eyebrow">{e(t(ui, 'evidence_here'))}</p>
  {evidence_bar(cnt, classes, len(mine))}
  <div class="evidence__chips">{chips}</div>
  <p class="note">{e(t(ui, 'bar_note'))}</p>
  <a class="evidence__link" href="{prefix}{L['dir'] + '/' if L['dir'] else ''}{L['ledger']['slug']}/#{mine[0].section_slug}">
    {e(t(ui, 'see_all', n=len(mine)))} <span aria-hidden="true">&#8250;</span></a>
</div>"""

    series = ""
    parts = []
    if prev:
        parts.append(f'<a class="series__prev" href="{prefix}{prev[0]}">'
                     f'<span class="series__dir">{e(t(ui, "previous"))}</span>'
                     f'<span class="series__t">{e(prev[1])}</span></a>')
    if nxt:
        parts.append(f'<a class="series__next" href="{prefix}{nxt[0]}">'
                     f'<span class="series__dir">{e(t(ui, "next"))}</span>'
                     f'<span class="series__t">{e(nxt[1])}</span></a>')
    if parts:
        series = f'<nav class="series">{"".join(parts)}</nav>'

    numeral = doc.numeral or "00"
    eyebrow = t(ui, "the_method") if kind == "method" else \
        f'{t(ui, "case_study")} {doc.numeral}'
    stand = f'<div class="doc__standfirst">{doc.standfirst}</div>' if doc.standfirst else ""
    method_map = render_method_map(L) if kind == "method" else ""

    body = f"""
<article class="doc">
  <header class="doc__head">
    <span class="doc__numeral" aria-hidden="true">{e(numeral)}</span>
    <p class="eyebrow">{e(eyebrow)}</p>
    <h1 class="doc__title">{e(doc.title)}</h1>
    <p class="doc__subtitle">{e(doc.subtitle)}</p>
    <div class="doc__meta"><span>{e(doc.author or L.get('author', ''))}</span>
      <span>{e(doc.dateline)}</span>
      <span>{doc.minutes} {e(t(ui, 'min_read'))}</span>
      <span>{len(doc.sources)} {e(t(ui, 'sources'))}</span></div>
    {stand}
  </header>
  {issuers(doc, ui)}
  {evidence}
  {method_map}
  <div class="doc__layout">
    {toc_html(doc.toc, t(ui, 'in_this_document'))}
    <div class="prose">{doc.body_html}</div>
  </div>
  {sources_html(doc, ui)}
  {series}
</article>"""
    return shell(L, alt, title=doc.title, description=doc.subtitle or L["description"],
                 depth=doc.depth, body=body,
                 active="method" if kind == "method" else doc.slug,
                 page="page-doc", alt_url=alt_url, path=doc.url, alt_path=alt_path)


def render_ledger(L, alt, intro, sections, outro, claims, section_study, alt_url,
                  path, alt_path):
    ui, classes = L["ui"], L["evidence_classes"]
    by_id = {c["id"]: c for c in classes}
    by_id["unknown"] = {"id": "unknown", "name": "Unmapped", "full": "Unmapped classification"}
    counts = {c["id"]: 0 for c in classes}
    for c in claims:
        if c.class_id in counts:
            counts[c.class_id] += 1
    depth = 2 if L["dir"] else 1
    prefix = "../" * depth

    filters = "".join(
        f'<button class="filter filter--{c["id"]}" type="button" data-class="{c["id"]}" '
        f'aria-pressed="false"><span>{e(c["name"])}</span>'
        f'<span class="filter__n">{counts[c["id"]]}</span></button>'
        for c in classes if counts[c["id"]])

    blocks = []
    for sec in sections:
        rows = []
        for c in sec["claims"]:
            src = (f'<a class="claim__source" target="_blank" rel="noopener noreferrer" '
                   f'href="{e(c.source_url)}">{c.source_html} '
                   f'<span aria-hidden="true">&#8250;</span></a>' if c.source_url
                   else f'<span class="claim__source">{c.source_html}</span>')
            rows.append(f"""<li class="claim" id="{c.cid}" data-class="{c.class_id}"
     data-text="{e((c.claim_text + ' ' + c.classification).lower())}">
  <div class="claim__top"><a class="claim__ref" href="#{c.cid}"
      title="{e(c.cid)}">{c.ref}</a>
    <p class="claim__text">{c.claim_html}</p></div>
  <div class="claim__body">
    <div class="claim__meta">{stamp(by_id[c.class_id])}
      <span class="claim__raw">{e(c.classification)}</span>{src}</div>
    <div class="wording wording--ok"><p class="wording__label">{e(t(ui, 'permitted'))}</p>
      <p class="wording__text">{c.permitted_html}</p></div>
    <div class="wording wording--no"><p class="wording__label">{e(t(ui, 'avoid'))}</p>
      <p class="wording__text">{c.avoid_html}</p></div>
  </div></li>""")
        back = ""
        if sec["title"] in section_study:
            slug, numeral, title = section_study[sec["title"]]
            back = (f'<a class="file__study" href="{prefix}{L["dir"] + "/" if L["dir"] else ""}'
                    f'{L["studies_dir"]}/{slug}/">'
                    f'{e(t(ui, "supports_study", numeral=numeral))}: {e(title)} '
                    f'<span aria-hidden="true">&#8250;</span></a>')
        blocks.append(f"""<section class="file" id="{sec['slug']}" data-section>
  <div class="file__head"><h2 class="file__h">{e(sec['title'])}</h2>
    <span class="file__n">{len(sec['claims'])}</span></div>
  {back}
  <ol class="claims">{"".join(rows)}</ol></section>""")

    body = f"""
<article class="ledger">
  <header class="doc__head">
    <p class="eyebrow">{e(L['ledger']['eyebrow'])}</p>
    <h1 class="doc__title">{e(L['ledger']['title'])}</h1>
    <p class="doc__subtitle">{e(L['ledger']['subtitle'])}</p>
    <div class="doc__meta"><span>{e(L.get('author', ''))}</span><span>{e(L['edition'])}</span>
      <span>{len(claims)} {e(t(ui, 'claims'))}</span>
      <span>{len(sections)} {e(t(ui, 'files'))}</span></div>
  </header>
  <div class="ledger__intro prose">{intro}</div>
  <div class="controls" data-controls>
    <div class="controls__search"><label class="eyebrow" for="q">{e(t(ui, 'search'))}</label>
      <input id="q" type="search" autocomplete="off" data-search></div>
    <div><p class="eyebrow">{e(t(ui, 'filter_by'))}</p>
      <div class="filters">{filters}</div></div>
    <p class="controls__status" data-status aria-live="polite"
       data-tpl="{e(t(ui, 'n_of_m'))}">{len(claims)} {e(t(ui, 'claims'))}</p>
  </div>
  <div class="files">{"".join(blocks)}</div>
  <p class="noresults" data-noresults hidden>{e(t(ui, 'no_results'))}
    <button type="button" data-reset>{e(t(ui, 'clear'))}</button></p>
  <div class="ledger__outro prose">{outro}</div>
</article>"""
    return shell(L, alt, title=L["ledger"]["title"],
                 description=L["ledger"]["subtitle"], depth=depth, body=body,
                 active="ledger", page="page-ledger", alt_url=alt_url,
                 path=path, alt_path=alt_path)


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_lang(cfg, code: str) -> dict:
    L = dict(cfg[code])
    L["author"] = cfg["site"]["author"]
    L["base_url"] = cfg["site"]["base_url"]
    alt = dict(cfg[L["other"]])
    base = (L["dir"] + "/") if L["dir"] else ""
    abase = (alt["dir"] + "/") if alt["dir"] else ""
    classes = L["evidence_classes"]
    src = CONTENT / (L["dir"] or "en")

    depth_base = 1 if L["dir"] else 0
    method = parse_doc(src / L["method"]["file"], L["method"]["slug"],
                       depth_base + 1, f'{base}{L["method"]["slug"]}/')
    studies = []
    for s in L["studies"]:
        d = parse_doc(src / s["file"], s["slug"], depth_base + 2,
                      f'{base}{L["studies_dir"]}/{s["slug"]}/')
        d.numeral, d.ledger_sections = s["numeral"], s.get("ledger_sections", [])
        d.title = re.sub(r"^(Case Study|Estudio de caso)\s+[IVXLC]+\s*[:\u2014.-]\s*",
                         "", d.title)
        studies.append(d)

    intro, sections, outro, problems = parse_ledger(
        src / L["ledger"]["file"], classes, cfg["site"]["match_order"])
    claims = [c for sec in sections for c in sec["claims"]]

    section_study = {}
    for cfg_s, doc in zip(L["studies"], studies):
        for name in cfg_s.get("ledger_sections", []):
            section_study[name] = (doc.slug, doc.numeral, doc.title)

    standfirst = ""
    want = L["method"].get("standfirst_from", "")
    if want:
        raw = (src / L["method"]["file"]).read_text(encoding="utf-8")
        pat = re.sub(r"['\u2019]", lambda _: "['\u2019]", re.escape(want))
        pat = re.sub(r"[oO]", "[oO\u00f3\u00d3]", pat)
        m = re.search(rf"^##\s+{pat}\s*$(.*?)^##\s", raw, re.M | re.S)
        if m:
            paras = [p.strip() for p in m.group(1).strip().split("\n\n") if p.strip()]
            standfirst = make_md().convert("\n\n".join(paras[:2]))

    alt_home = f"{'../' * depth_base}{abase}" if depth_base else abase
    write(OUT / base / "index.html",
          render_home(L, alt, method, studies, sections, claims, standfirst,
                      alt_home or "./", depth_base, base, abase))

    order = [(f'{base}{L["method"]["slug"]}/', method.title)]
    order += [(f'{base}{L["studies_dir"]}/{d.slug}/', d.title) for d in studies]
    order += [(f'{base}{L["ledger"]["slug"]}/', L["ledger"]["title"])]

    def alt_for(depth, path):
        return "../" * depth + path

    write(OUT / base / L["method"]["slug"] / "index.html",
          render_doc(L, alt, method, claims, "method", None, order[1],
                     alt_for(method.depth, f'{abase}{alt["method"]["slug"]}/'),
                     f'{abase}{alt["method"]["slug"]}/'))
    for i, doc in enumerate(studies, start=1):
        aslug = alt["studies"][i - 1]["slug"]
        write(OUT / base / L["studies_dir"] / doc.slug / "index.html",
              render_doc(L, alt, doc, claims, "study", order[i - 1], order[i + 1],
                         alt_for(doc.depth, f'{abase}{alt["studies_dir"]}/{aslug}/'),
                         f'{abase}{alt["studies_dir"]}/{aslug}/'))
    geo = json.loads((ASSETS / "map.json").read_text(encoding="utf-8"))
    mdepth = depth_base + 1
    write(OUT / base / L["map"]["slug"] / "index.html",
          render_map(L, alt, geo,
                     alt_for(mdepth, f'{abase}{alt["map"]["slug"]}/'),
                     f'{base}{L["map"]["slug"]}/',
                     f'{abase}{alt["map"]["slug"]}/'))

    ldepth = depth_base + 1
    write(OUT / base / L["ledger"]["slug"] / "index.html",
          render_ledger(L, alt, intro, sections, outro, claims, section_study,
                        alt_for(ldepth, f'{abase}{alt["ledger"]["slug"]}/'),
                        f'{base}{L["ledger"]["slug"]}/',
                        f'{abase}{alt["ledger"]["slug"]}/'))

    return {"lang": code, "problems": problems, "documents": [
        {"slug": d.slug, "title": d.title, "url": d.url, "words": d.words,
         "sources": [{"n": s.n, "issuer": s.issuer, "url": s.url} for s in d.sources]}
        for d in [method] + studies],
        "claims": [{"id": c.cid, "semantic_id": c.semantic, "ref": c.ref,
                    "file": c.section, "class": c.class_id,
                    "classification": c.classification, "claim": c.claim_text,
                    "source": c.source_url} for c in claims],
        "urls": [base or ""] + [u for u, _ in order]
                + [f'{base}{L["map"]["slug"]}/']}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true")
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / "site.yaml").read_text(encoding="utf-8"))
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    data = {"built": date.today().isoformat(),
            "author": cfg["site"]["author"], "editions": []}
    urls = []
    for code in ("en", "es"):
        result = build_lang(cfg, code)
        urls += result.pop("urls")
        data["editions"].append(result)

    # Generate before copying assets so the deployed card and source asset are
    # byte-for-byte identical. Failure must stop the build; otherwise a stale
    # claim count could be published despite a successful page build.
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "scripts" / "make_social.py")],
                   check=True)

    shutil.copytree(ASSETS, OUT / "assets")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    write(OUT / "atlas.json", json.dumps(data, indent=2, ensure_ascii=False))

    base = cfg["site"]["base_url"].rstrip("/")
    write(OUT / "sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{base}/{u}</loc></url>\n" for u in urls)
          + "</urlset>\n")
    write(OUT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")

    n_claims = sum(len(ed["claims"]) for ed in data["editions"])
    print(f"Built {len(list(OUT.rglob('*.html')))} pages in 2 editions, "
          f"{n_claims} claims -> {OUT}")

    errors, notes = [], []
    for ed in data["editions"]:
        for severity, message in ed.pop("problems", []):
            (errors if severity == "error" else notes).append(f'[{ed["lang"]}] {message}')

    unnamed = sum(1 for ed in data["editions"]
                  for c in ed["claims"] if not c["semantic_id"])
    if unnamed:
        print(f"\n{unnamed} claims still use a derived anchor rather than a "
              f"semantic id. Add one by ending the claim cell with "
              f"{{#VEN-EO14373}}. Derived anchors are stable across "
              f"insertions but change if the claim text is rewritten.")

    if errors:
        print(f"\n{len(errors)} errors:", file=sys.stderr)
        for line in errors:
            print(f"  {line}", file=sys.stderr)
        return 1

    if args.serve:
        import http.server, os, socketserver
        os.chdir(OUT)
        with socketserver.TCPServer(("", 8000), http.server.SimpleHTTPRequestHandler) as s:
            print("http://localhost:8000")
            s.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
