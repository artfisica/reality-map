#!/usr/bin/env python3
"""Check the atlas for publication-integrity defects before it goes out.

Severities:
    error  always fails
    warn   fails only with --strict, which is what CI uses
    note   informational, never fails

Run:
    python scripts/validate.py            # local, tolerant
    python scripts/validate.py --strict   # what the pull-request check runs
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

import build  # noqa: E402

REPORT: list[tuple[str, str]] = []


def say(severity: str, message: str) -> None:
    REPORT.append((severity, message))


def check_edition(cfg: dict, code: str) -> dict:  # noqa: C901
    L = cfg[code]
    src = ROOT / "content" / (L["dir"] or "en")
    order = cfg["site"]["match_order"]

    _, sections, _, problems = build.parse_ledger(
        src / L["ledger"]["file"], L["evidence_classes"], order)
    for severity, message in problems:
        say(severity if severity != "note" else "note", f"[{code}] {message}")

    claims = [c for s in sections for c in s["claims"]]
    have = {s["title"] for s in sections}

    # every ledger section named in the configuration must exist
    named = set()
    for study in L["studies"]:
        for name in study.get("ledger_sections", []):
            named.add(name)
            if name not in have:
                say("error", f'[{code}] site.yaml points study "{study["slug"]}" at '
                             f'ledger section "{name}", which the ledger does not contain')
    for title in have - named:
        say("warn", f'[{code}] ledger section "{title}" is not attached to any study, '
                    f"so its claims have no route back to the prose")

    # duplicate anchors would make bookmarks ambiguous
    seen: dict[str, str] = {}
    for c in claims:
        if c.cid in seen:
            say("error", f"[{code}] two claims share the anchor {c.cid}: "
                         f'"{seen[c.cid][:48]}" and "{c.claim_text[:48]}"')
        seen[c.cid] = c.claim_text

    # An evidentiary source with no link cannot be checked by a reader, unless
    # it deliberately names several documents rather than one.
    aggregates = [re.compile(p, re.I)
                  for p in cfg["site"].get("aggregate_patterns", {}).get(code, [])]
    for c in claims:
        if c.source_url:
            continue
        plain = re.sub(r"<[^>]+>", "", c.source_html).strip()
        if any(p.search(plain) for p in aggregates):
            say("note", f'[{code}] {c.ref} is a declared aggregate reference: "{plain}"')
        else:
            say("warn", f'[{code}] {c.ref} has no source link: "{plain[:60]}". '
                        f"Give it a URL, or add the phrase to "
                        f"site.aggregate_patterns if it names several documents.")

    unnamed = [c.ref for c in claims if not c.semantic]
    if unnamed:
        say("note", f"[{code}] {len(unnamed)} of {len(claims)} claims use a derived "
                    f"anchor rather than a semantic id")

    # documents: sources numbered 1..n with no gaps
    files = [L["method"]["file"]] + [s["file"] for s in L["studies"]]
    for name in files:
        doc = build.parse_doc(src / name, "x", 1, "")
        numbers = [s.n for s in doc.sources]
        if numbers and numbers != list(range(1, len(numbers) + 1)):
            say("error", f"[{code}] {name} source numbering is {numbers}, "
                         f"expected 1 to {len(numbers)}")
        for s in doc.sources:
            if not s.url:
                say("warn", f"[{code}] {name} source {s.n:02d} has no URL")

    # the byline spelling, which is easy to lose in translation and export
    want = cfg["site"].get("author_must_read")
    if want:
        stripped = want.replace("\u00e1", "a").replace("\u00e9", "e")
        for path in sorted(src.glob("*.md")):
            body = path.read_text(encoding="utf-8")
            if stripped != want and stripped in body:
                say("error", f'[{code}] {path.name} spells the author as '
                             f'"{stripped}"; it must read "{want}"')

    # the version and date a document declares must match the edition
    edition_bits = [b for b in re.split(r"[\s,]+", L["edition"]) if b]
    for path in sorted(src.glob("*.md")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:8])
        line = re.search(r"^\*\*(?:Version|Versi\u00f3n|Edition|Edici\u00f3n)[^*]*\*\*$",
                         head, re.M)
        declared = re.search(r"\b\d+\.\d+\b", line.group(0)) if line else None
        if declared and declared.group(0) != L["version"]:
            say("error", f'[{code}] {path.name} declares version '
                         f'{declared.group(0)}, the edition is {L["version"]}')
        if edition_bits and not all(b in head for b in edition_bits[:1] + edition_bits[-1:]):
            say("warn", f'[{code}] {path.name} does not carry the edition date '
                        f'"{L["edition"]}"')

    # every map marker must have geometry behind it
    import json as _json
    geo = _json.loads((ROOT / "assets" / "map.json").read_text(encoding="utf-8"))
    for place in L.get("map", {}).get("places", []):
        if place["id"] not in geo["points"]:
            say("error", f'[{code}] map place "{place["id"]}" has no projected '
                         f"point. Add it to scripts/make_map.mjs and re-run it.")

    # prohibited terminology
    for term in cfg["site"].get("prohibited", {}).get(code, []):
        pattern = re.compile(rf"\b{re.escape(term)}\b", re.I)
        for path in sorted(src.glob("*.md")):
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if pattern.search(line):
                    say("error", f'[{code}] prohibited term "{term}" in '
                                 f"{path.name} line {i}")

    return {"claims": claims, "sections": sections}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("--verbose", action="store_true", help="list every note")
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / "site.yaml").read_text(encoding="utf-8"))
    editions = {code: check_edition(cfg, code) for code in ("en", "es")}

    # the two editions are the same atlas and must carry the same record
    counts = {code: len(data["claims"]) for code, data in editions.items()}
    if len(set(counts.values())) != 1:
        say("error", f"the editions disagree on the record: "
                     + ", ".join(f"{k} has {v} claims" for k, v in counts.items())
                     + ". Synchronise the ledgers before publishing.")

    # semantic ids should name the same claim in both editions
    ids = {code: {c.cid for c in data["claims"] if c.semantic}
           for code, data in editions.items()}
    if ids["en"] or ids["es"]:
        only_en, only_es = ids["en"] - ids["es"], ids["es"] - ids["en"]
        for i in sorted(only_en):
            say("warn", f"semantic id {i} exists in English but not Spanish")
        for i in sorted(only_es):
            say("warn", f"semantic id {i} exists in Spanish but not English")

    map_ids = {code: [p["id"] for p in cfg[code].get("map", {}).get("places", [])]
               for code in ("en", "es")}
    if map_ids["en"] != map_ids["es"]:
        say("error", "the two editions list different map places, so the map "
                     "would show a different atlas in each language")

    files = {code: len(data["sections"]) for code, data in editions.items()}
    if len(set(files.values())) != 1:
        say("warn", "the editions have different numbers of ledger files: "
                    + ", ".join(f"{k}={v}" for k, v in files.items()))

    for code in ("en", "es"):
        if cfg[code]["version"] != cfg["en"]["version"]:
            say("warn", f"edition versions differ: en {cfg['en']['version']} vs "
                        f"{code} {cfg[code]['version']}")

    errors = [m for s, m in REPORT if s == "error"]
    warns = [m for s, m in REPORT if s == "warn"]
    notes = [m for s, m in REPORT if s == "note"]

    for label, items in (("ERROR", errors), ("WARN", warns), ("NOTE", notes)):
        if not items:
            continue
        print(f"\n{label} ({len(items)})")
        shown = items if (label != "NOTE" or args.verbose) else items[:8]
        for item in shown:
            print(f"  {item}")
        if len(shown) < len(items):
            print(f"  ... and {len(items) - len(shown)} more, use --verbose")

    print(f"\n{counts['en']} English claims, {counts['es']} Spanish claims")
    if errors:
        print("\nValidation failed.")
        return 1
    if warns and args.strict:
        print("\nValidation failed under --strict.")
        return 1
    print("\nValidation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
