# Release decisions

Decisions affecting publication and citation, kept here rather than inside the
files they affect.

## 1. The content licence

Version 0.6.3 reserves all rights in `LICENSE-CONTENT`. A later release may adopt
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

## 2. Semantic claim identifiers — resolved in 0.3, extended through 0.6.3

All 67 claims carry permanent semantic identifiers, with the same identifier
used for the corresponding claim in both editions. `validate.py` reports an
identifier present in only one edition and rejects duplicates within either
edition.

## 3. Release tagging

Tag every published edition after deployment so a citation resolves to a fixed
state of the record rather than to whatever `main` happens to say. The current
release tag is `v0.6.3`.

## 4. Audio status in 0.6.3

The published audio consists of two project-level podcasts, one per language:
`assets/audio/method-en.m4a` (18:10) is exclusive to the English edition and
`assets/audio/method-es.m4a` (40:20) is exclusive to the Spanish edition. An
edition must never point to the other language's recording. Neither recording
is an individual reading of the method or of a case study.

Individual article readings in English and Spanish remain planned work. They
must not be advertised, attached to an article or described as verbatim until
the corresponding complete recording has been produced from the current text.
