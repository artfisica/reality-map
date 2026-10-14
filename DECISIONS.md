# Release decisions

Decisions affecting publication and citation, kept here rather than inside the
files they affect.

## 1. The content licence

Version 0.10.0 reserves all rights in `LICENSE-CONTENT`. A later release may adopt
one of these alternatives:

- **CC BY 4.0.** Anyone may republish, translate or adapt, including
  commercially, with attribution. Maximum reach. You lose control over how the
  argument is recontextualised, which matters for material this contested.
- **CC BY-NC-ND 4.0.** Anyone may share the work whole and unmodified,
  non-commercially, with attribution. Protects the argument against selective
  editing. Blocks derivative translations, which cuts against the purpose of a
  civilian manual.
- **CC BY-SA 4.0.** Anyone may republish and adapt, including translations,
  provided the result carries the same licence. A middle position: it permits
  the translations you would want while keeping adaptations open.

If the licence changes, replace the licence paragraph, record it in
`CHANGELOG.md` and update `CITATION.cff`.

## 2. Semantic claim identifiers — resolved in 0.3, extended through 0.10.0

All 95 claims carry permanent semantic identifiers, with the same identifier
used for the corresponding claim in both editions. `validate.py` reports an
identifier present in only one edition and rejects duplicates within either
edition.

## 3. Release tagging

Tag every published edition after deployment so a citation resolves to a fixed
state of the record rather than to whatever `main` happens to say. The current
release tag is `v0.10.0`.

## 4. Audio status in 0.10.0

The published audio consists of two project-level podcasts, one per language:
`assets/audio/method-en.m4a` (18:10) is exclusive to the English edition and
`assets/audio/method-es.m4a` (40:20) is exclusive to the Spanish edition. An
edition must never point to the other language's recording. Neither recording
is an individual reading of the method or of a case study.

Individual article readings in English and Spanish remain planned work. They
must not be advertised, attached to an article or described as verbatim until
the corresponding complete recording has been produced from the current text.

## 5. Interface changes between editions

The edition version belongs to the record: it is what a citation resolves to
and what the content files declare in their heads, which `validate.py` checks.
Changes that touch only `assets/atlas.css` and `assets/atlas.js` are therefore
versioned separately through `site.interface_version`, which the build appends
to the asset URLs for cache busting. An interface-only release may be published
without a new edition version or tag; its changelog section is headed
`Interface YYYY-MM-DD`, matching `interface_version`, and that heading is its
permanent id in `feed.xml`. A release that changes the record bumps the
edition version as before and may update `interface_version` as well. A
section headed `Unreleased` is a draft and is excluded from the feed, so an
id never changes once published.

## 6. What the interactive layer may and may not do

Every control added in October 2026 is progressive enhancement over complete
pages. The constraints it must keep:

- No third-party request. The share links are plain intents that request
  nothing until the reader chooses a destination; the search index is this
  site's own `atlas.json`.
- No state leaves the browser. Reading position, the last document and the
  edition last seen live in `localStorage` under versioned keys, like the audio
  position before them.
- Colour still means evidence class only. The trainer hides the colour until
  the reader has answered, then shows the ledger's classification; the
  interface itself is ink on paper.
- The trainer never grades the record. It shows the ledger's own
  classification and note; a disagreement is a reason to read the ledger row,
  not a score.
- Evidence paths are views of the ledger, not a parallel record. Their claim
  text, class, source and permitted wording are resolved from stable claim ids
  during the build. Configuration may supply only the question, chronology
  label and explanation of what changed. Strict validation requires the same
  ids in the same order in both languages. With JavaScript disabled, every step
  remains present and readable.
- A browser-side read-aloud (SpeechSynthesis) was considered and not added:
  decision 4 says a recording may be described as a reading only when
  produced from the current text, and a synthetic voice over the live page
  would need its own wording in both editions before it is offered.
