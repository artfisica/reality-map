# Changelog

Editions are dated and versioned together. When a court rules, a policy changes
or new primary evidence appears, the ledger row is updated first and the change
is recorded here.

## 0.6 — 22 August 2026

- Corrected the audio model introduced in 0.5: the recordings are long-form
  companions to particular studies, not generic narrations of the entire atlas.
- Added `/listen/` and `/es/escuchar/` as the single bilingual listening desk,
  with a shared player, sequential playback, per-episode resume positions,
  article links and direct downloads.
- Assigned *How superpowers export their deadliest costs* and *Cómo las
  potencias exportan su costo humano* to Case Study VI.
- Added the 40:20 Spanish Case Study I episode, *La impunidad de los Estados
  ante la ley*.
- Replaced the repeated whole-site player with an audio-library invitation on
  each homepage and an episode player only where that study has a recording.
- Optimized the new 77.9 MB source recording to a 20.4 MB mono AAC web asset
  without cutting its content.
- Extended validation to check each study-level episode independently and
  added the listening pages to navigation, alternate-language links and the
  sitemap.

## 0.5 — 21 August 2026

- Added a complete English and Spanish audio companion to the home page, method
  and every study, so a reader can listen while moving through the written
  record.
- Added cross-page playback-position recovery in the browser, separately
  versioned for each language; no playback information leaves the device.
- Encoded the supplied recordings as locally hosted, mono AAC files optimized
  for spoken voice, reducing their combined size from about 98 MB to about
  26 MB without cutting their content.
- Added explicit interface language stating that the audio is a conversational
  guide and that the written studies and claim ledger remain authoritative.
- Added Open Graph audio metadata, accessible fallback/download links, responsive
  player styling, reduced-motion behavior and print exclusion.
- Extended strict validation to reject a missing or empty configured recording.

## 0.4 — 20 August 2026

- Added Case Study VI in English and Spanish: debt, humanitarian abandonment,
  fiscal externalisation and control over Venezuelan resource revenue.
- Separated the US$40 trillion gross-debt fact from debt held by the public,
  annual deficit and net interest; added CBO’s 2026–2036 baseline.
- Documented the termination of 83 per cent of USAID-managed programmes while
  preserving the distinction between programme count and budget share.
- Added the 2025 USAID-specific and 2026 global-aid mortality studies as
  counterfactual forecasts, never as observed or inevitable death counts.
- Added field evidence from Nepal and operational assessments from the UN,
  WFP and UNHCR showing how funding withdrawal removes health, protection and
  food systems in practice.
- Added the legal boundary between voluntary contributions, assessed UN dues,
  conflict-specific humanitarian-access duties and the duty to prevent
  genocide.
- Added the fiscal-externalisation test to the manual: debt creates pressure,
  but governments select which lives and programmes absorb it.
- Distinguished the established US control over specified Venezuelan resource
  revenues from the unsupported claim that those revenues are being used to
  service US debt; added transaction-level indicators that would change the
  classification.
- Added the September 2024 exploding-device attacks in Lebanon and Syria, with
  Amnesty International’s conditional legal assessment and the UN human-rights
  chief’s demand for an independent investigation.
- Expanded the geographic map to eleven locations and six studies by adding
  Washington, D.C., as the decision point for the new study.
- Synchronized both editions at 59 semantically matched claims and updated the
  edition metadata to 20 August 2026.

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
- Harmonised Arturo's physicist-and-engineer description and the Spanish
  «te lo dije» phrase, repeated the name of the Spanish response scale where it
  is applied, and reduced duplicated method exposition in Study I.
- Added a bilingual method, sources and AI-assistance link to every standalone
  study page, and split the densest sentences in Study III without altering its
  findings or source record.
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
