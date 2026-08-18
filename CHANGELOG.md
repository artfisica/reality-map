# Changelog

Editions are dated and versioned together. When a court rules, a policy changes
or new primary evidence appears, the ledger row is updated first and the change
is recorded here.

## 0.3 — 17 August 2026

- Spanish edition published alongside English, at `/es/`.
- Added the graphic method map on both method pages: the classification gate,
  the six-layer power map, the response scale, the five tests and the civilian
  protocol, each linked to the section it summarises.
- Added the world map at `/map/` and `/es/mapa/`: ten mapped locations across five
  studies, drawn in Equal Earth so areas are comparable, as one borderless
  landmass so it takes no position on any disputed boundary, and monochrome so
  colour keeps meaning evidence class and nothing else. Markers locate where a
  study looks; each place's legal status is stated in words, not encoded in the
  drawing.
- Kept geographic markers legible on small screens with fixed-size HTML labels,
  separated dense clusters with documented pixel offsets, and fitted the SVG to
  the complete Equal Earth sphere so its outline is not clipped.
- Added a bilingual authorship and generative-AI disclosure to the method,
  summarized it in the README and linked it from every page footer. It separates
  Arturo Sánchez Pineda's originating ideas and final responsibility from the
  research, editorial, bilingual, coding and visual assistance provided by AI.
- Clarified in the first person that Arturo wrote the study and the prompts used
  to direct AI searches for possible references, while preserving a precise
  account of the drafting and technical assistance AI provided.
- Added French Guiana's exclusion from Schengen under Article 138 and separated
  it from the Spain-specific visa and departure-control regime governing Ceuta
  and Melilla; synchronized the analysis, ledgers and map labels in both languages.
- Restored the map page's missing horizontal content wrapper so its heading,
  introduction, geographic drawing, projection note and legend align within the
  same responsive measure as the rest of the site.
- Linked the author credit on the cover, document metadata and footer to Arturo
  Sánchez Pineda's LinkedIn profile using a single site-level URL and `rel="me"`.
- Case studies reordered: the Caribbean killings become IV, Venezuela becomes V.
- Claim anchors are now stable. They no longer come from row order, so adding a
  claim does not renumber the ones below it or break an existing citation.
- An unrecognised classification now fails the build instead of silently
  becoming a record.
- Authorial context is parsed and displayed as its own section, distinct from
  the numbered sources.
- The source description now names the kinds of source actually present,
  including attributed investigative reporting.
- Added `scripts/validate.py` and a pull-request check. It also verifies the
  byline spelling, that each document declares the edition's version and date,
  and that semantic claim ids match across the two editions.
- Prohibited Spanish terminology narrowed to the nouns `licitud` and
  `ilicitud`. The adjectives stay available, because "uso ilícito de la fuerza"
  is legally precise.
- Aggregate source references are declared in `site.aggregate_patterns` and
  reported as notes rather than warnings.
- The social card is regenerated on every build, so it cannot report a stale
  claim count.
- The content licence reserves all rights and no longer carries editorial
  instructions; open questions moved to `DECISIONS.md`.
- Synchronized the definitive fourteen-document corpus, including the
  authorial method derived from *Miedo* and *Dolor*, the Caribbean-to-Venezuela
  chronology, Executive Order 14373, the BBC investigation and the analysis of
  de facto tutelage.
- Both editions now contain the same 46 claims in the same case-study order.
- Every claim has a permanent semantic identifier shared by its English and
  Spanish versions.
- Added the English `documentary fact` evidence match used by the Executive
  Order 14373 claim.

## 0.2 — 17 August 2026

- Spanish drafts of the manual and the five case studies.

## 0.1 — 16 August 2026

- First edition: the manual, five case studies and the ledger, in English.
