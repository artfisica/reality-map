# Changelog

Editions are dated and versioned together. When a court rules, a policy changes
or new primary evidence appears, the ledger row is updated first and the change
is recorded here.

## 0.10.0 — 14 October 2026

- Corrected the Iraq comparison with the missing legal transition: Security
  Council Resolution 1956 ended the Development Fund arrangements in 2011,
  Executive Order 13668 ended the special US immunity regime in 2014, and the
  Central Bank of Iraq's audited statements identify the Iraqi-owned successor
  accounts at the New York Fed.
- Added the reported 2026 suspension and conditional restart of Iraqi physical-
  dollar deliveries. The edition treats this as demonstrated leverage over one
  access channel, not confiscation or a freeze of all electronic oil revenue.
- Added the June–July Venezuela earthquake deployment: the Venezuelan request,
  the official nearly 2,000-troop theatre figure, Reuters' report of more than
  900 personnel inside Venezuela, the named airport and port nodes, and the
  documented conclusion of the 621st Air Force element's mission.
- Kept the legal boundaries explicit: later consent to disaster relief did not
  retroactively legalise the January intervention; the record does not establish
  2,000 occupation troops inside Venezuela, permanent US bases or the departure
  of every US military or intelligence element.
- Added **When does custody become control?** to the cover evidence paths. It
  traces the change from the Iraq occupation fund to successor accounts,
  Venezuela's explicit disbursement regime, demonstrated Iraqi access leverage
  and the still-uncompleted Venezuelan gold proposal.
- Added three matched ledger claims in each language, bringing the record to 95
  claims per edition and three bilingual evidence paths.

## 0.9.0 — 14 October 2026

- Added the 30 September letter from the ranking Democrats of four Senate
  committees. It formally challenges the statutory authority for the announced
  US equity and long-term oil-purchase structure and requests the agreements,
  but is not described as a congressional or judicial ruling of illegality.
- Added the 13 October DEA record placing Álvaro Pulido Vargas in US custody
  after coordination with “international partners,” while preserving the
  official record's silence on arrest location, route and legal process.
- Added attributed Bloomberg Línea and *El País* reporting on Pulido's
  Venezuelan citizenship, prior imprisonment near Caracas and delivery by
  Venezuelan actors. These details remain attributed reporting rather than an
  official Venezuelan admission or published surrender order.
- Revised the Canelón assessment. The combined Canelón and Pulido record now
  supports investigating an organised opaque transfer channel, but does not
  prove a common route, who placed Canelón at sea, or a documented mechanism
  capable of overriding Article 69.
- Added four matched ledger claims in each language, bringing the record to 92
  claims per edition.
- Added **Trace the evidence** to both covers. Two question-led paths—the
  Canelón/Pulido transfers and control of Venezuelan oil—show, step by step,
  how later evidence changes the permissible conclusion. Every displayed
  claim, class, source and wording boundary is derived from a stable ledger id.
  Without JavaScript, both complete ordered paths remain visible.
- Extended strict validation to reject missing path claims, repeated steps and
  any divergence between the English and Spanish evidentiary sequences.
- Extended the interface test to exercise path selection, step navigation,
  stable ledger links and the complete no-JavaScript rendering.

## Interface 2026-10-13 — 13 October 2026

An interface release, named by `site.interface_version`. The record is unchanged: 88 matched claims, edition 11 October 2026, tag
`v0.8.0`. This release only changes how the published pages can be read, shared
and searched. Every addition is progressive enhancement; with JavaScript off the
text, the ledger and every source link still work as before. Nothing is loaded
from a third party and nothing leaves the reader's browser.

- Added a site-wide search (the **Search** button, `Ctrl K` or `/`) over
  documents, section headings and all claims in the reader's edition, built
  from `atlas.json` and fetched from this domain only when opened.
- Added **Learn the six** to the cover: a ledger claim shown with its colour
  hidden, the six classes to choose from, and the ledger's own classification
  and note revealed afterwards. Practice, not a test of the record.
- Added a reading-progress rule to every document and a *Continue reading*
  card on the cover that returns to the last document and position. The page
  itself never scrolls the reader without being asked. State is kept in the
  browser under a versioned key, as the audio position is.
- Added *Pass this study on* to every document: copy the link, copy a citation
  that names the edition and version, native share where the device offers it,
  and plain intent links for email, Bluesky, LinkedIn and X that request
  nothing until the reader chooses one.
- The ledger keeps the current search and filters in the URL
  (`/ledger/?q=icc&class=court`), so a view can be handed to someone else, and
  every claim row gains *Copy link*, *Copy citation* and native share.
- Hovering or focusing a mosaic tile on the cover shows the claim, its
  reference and its evidence class in a card instead of a browser tooltip.
- On the map, a pin and its legend entry highlight each other, and the pin
  label now carries the status the record supports.
- A reader returning after the edition has changed sees a one-line notice
  naming the edition they last read and this one, with a link to this file.
- Added `feed.xml`, an Atom feed generated from this changelog, so corrections
  can be followed without a tracker on either side; linked from every page.
  Every timestamp comes from the date in a release heading and every entry id
  is a stable `tag:` URI, so rebuilding the site cannot make the feed look
  newly updated; the deploy workflow builds twice and fails if the feed
  differs.
- `atlas.json` now lists each document's section headings and each claim's
  ledger section.
- Fixed the ledger source link, which nested one anchor inside another.
- Added `site.interface_version`, used to version `atlas.css` and `atlas.js`
  so the interface can change between editions without moving the edition
  version, the citations or the release tag. An interface release is headed
  `Interface YYYY-MM-DD` here; that heading is its permanent feed identifier.
  Sections headed `Unreleased` never enter the feed.
- Added `scripts/test_interface.mjs`, a jsdom smoke test that exercises every
  enhancement against the built pages in both editions. Both workflows run it
  after the link check, so a push to `main` cannot deploy an interface the
  test has not passed.
- The search dialog exposes its state to assistive technology: the input is a
  combobox and the highlighted result is announced through
  `aria-activedescendant`.

## 0.8.0 — 11 October 2026

- Replaced the initial anonymous-source description of the oil arrangement with
  the White House's named NABEP structure: 35 per cent US equity, at-cost
  purchasing, first refusal, board controls and the official 100-year claim.
- Added the published National Assembly support resolution, while preserving the
  distinction between a public political endorsement and the still-unpublished
  PDVSA–NABEP contract, field instruments and renewal clause.
- Added OFAC General License 52C, the separate Chevron, Eni, GE Vernova and
  Continental announcements, failed congressional subpoena vote, partial
  document production and missing KPMG audits.
- Kept the 25- versus 100-year duration conflict unresolved: the former rests on
  an attributed statement by PDVSA's president; the latter remains an official
  White House claim rather than a publicly inspectable contractual clause.
- Added the Canelón transfer with accusation/conviction discipline, the FBI's
  later “at sea” account, Venezuela's nationality-based non-extradition rule and
  the still-missing maritime jurisdictional facts.
- Updated the ICC analysis after the 9 October designation of the Court itself.
  The edition identifies a prospective territorial-jurisdiction gap after
  Venezuela's withdrawal takes effect without claiming present blanket immunity
  or an unproved intention to commit future atrocities.
- Added the Iraq comparison: Iraqi-owned oil receipts have remained in a New
  York Fed account through an architecture originating in 2003, creating a
  durable US financial chokepoint without transferring formal ownership.
- Added the reported but uncompleted proposal to move Venezuelan central-bank
  gold from London to New York, and classified it as attributed reporting.
- Expanded the bilingual ledger from 75 to 88 matched semantic claims and dated
  the complete edition 11 October 2026.

## 0.7.0 — 31 August 2026

- Added the announced US–Venezuela oil arrangement to Studies V and VI in both
  languages: 17 fields, a stated potential of 65 billion barrels, projected
  investment and Venezuelan public revenue, and the unpublished terms AP
  attributed to a US official.
- Kept ownership, control and rhetoric separate. The record now distinguishes
  Venezuela's 25-year sovereignty account from the attributed US account of
  100-year rights, 55 per cent effective output, at-cost purchases and supply
  for the Strategic Petroleum Reserve and military.
- Made the missing contract an evidentiary finding rather than filling its gaps:
  exact rights, operator ownership, constitutional approvals, investment duties
  and the conflicting duration claims remain unresolved.
- Reframed the Study VI conclusion around the use the public record now
  supports: claimed control over Venezuelan oil is being sold as domestic
  energy security and lower gasoline prices during the Iran war and before the
  November elections. The unsupported debt-payment claim remains only as a
  secondary evidentiary boundary.
- Added EIA fuel-price data, the IEA record of the Hormuz supply disruption and
  separately attributed CFR assessments of the failed quick-victory timetable,
  strategic setback and political pressure to reduce oil prices.
- Expanded the bilingual ledger from 67 to 75 matched claims and dated the
  complete edition 31 August 2026.

## 0.6.3 — 23 August 2026

- Corrected the language separation in the audio edition: English pages now
  use only the 18:10 English podcast, while Spanish pages use only the 40:20
  Spanish podcast, *La impunidad de los Estados ante la ley*.
- Added strict validation of language suffixes in configured audio sources so
  an English recording cannot again be published in the Spanish edition, or
  vice versa.
- Preserved the complete 0.6.2 ICC sanctions and Marco Rubio credibility audit.

## 0.6.2 — 23 August 2026

- Documented the 18 August sanctions against ICC President Tomoko Akane and
  Senior Trial Lawyer Abdoulaye Seye, including OFAC's operational measure and
  the State Department's declared campaign to weaken and dismantle the Court.
- Separated the treaty rule in Rome Statute article 12, the United States'
  jurisdictional position, Human Rights Watch's attributed assessment and the
  European Union's declaratory response.
- Added a bilingual audit of Marco Rubio's political credibility based on his
  documented record concerning Donald Trump, immigration reform and election-
  year Supreme Court appointments.
- Kept institutional authority, political credibility and unproved personal
  motive as distinct categories: Rubio's 99–0 confirmation is recorded alongside
  the later evidentiary comparison of his words and acts.
- Corrected the audio model before publication: version 0.6.2 exposes one
  general English-language project podcast in both editions and does not claim
  that individual article readings already exist.
- Removed the three case-study audio assignments and files that had been
  presented as individual episodes (`study-01-es.m4a`, `study-06-en.m4a` and
  `study-06-es.m4a`). The site remains ready to add the real English and Spanish
  article readings when they are produced.
- Synchronised the English and Spanish ledgers at 67 classified claims and
  dated the complete edition 23 August 2026.

## 0.6.1 — 22 August 2026

- Rebuilt the bilingual listening pages as a responsive audio library with a
  clearly separated current episode, full-width controls and readable episode
  cards that scale to the complete study collection.
- Restyled the player embedded in individual studies so it reads as part of the
  article instead of an unformatted block of controls and links.
- Added versioned CSS and JavaScript URLs so GitHub Pages and browsers cannot
  keep serving the pre-audio stylesheet after an interface update.
- Corrected singular episode labels and made all audio-interface ornament
  neutral ink so it cannot be confused with the evidence-class colour system.
- Removed the accidentally committed nested copy of the 0.4 repository and
  made validation reject any future nested repository copy.

- Added the manual's audio episode, the first English entry in the audio
  edition.
- Fixed the listening desk assuming every episode belongs to a case study: the
  manual's episode linked to a page that does not exist, and was labelled as a
  case study.
- Added `scripts/make_reading_text.py` and `scripts/encode_audio.py`.

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
