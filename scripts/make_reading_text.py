#!/usr/bin/env python3
"""Turn each document into a verbatim reading script.

The prose is not rewritten. Markdown that exists only for the eye is converted
into something a voice can say: link text without its URL, tables read as
labelled rows, headings announced. The source list is summarised rather than
read aloud, because reading forty URLs is unlistenable and the written page
already carries them.

    python scripts/make_reading_text.py            # every document, both editions
    python scripts/make_reading_text.py --lang en
    python scripts/make_reading_text.py --lang es --only 04-caribe

Output goes to audio/scripts/<lang>/<name>.txt, which is gitignored: these are
an intermediate, regenerated whenever the prose changes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

OUT = ROOT / "audio" / "scripts"

WORDS = {
    "en": {
        "by": "By", "sources_note": (
            "The full source list, with links to every primary document, is on "
            "the written page."),
        "section": "Section.", "table_row": "Row.",
        "read_note": "This is a verbatim reading of the written study.",
    },
    "es": {
        "by": "Por", "sources_note": (
            "La lista completa de fuentes, con enlaces a cada documento "
            "primario, está en la página escrita."),
        "section": "Sección.", "table_row": "Fila.",
        "read_note": "Esta es una lectura literal del estudio escrito.",
    },
}


def strip_inline(text: str) -> str:
    """Remove markdown that carries no sound, keeping every spoken word."""
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)      # link text only
    text = re.sub(r"<(https?://[^>]+)>", "", text)             # bare URLs
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\{#[A-Za-z0-9_.:-]+\}", "", text)          # claim anchors
    return re.sub(r"[ \t]+", " ", text).strip()


def convert(md: str, lang: str) -> str:
    W = WORDS[lang]
    out: list[str] = []
    rows: list[list[str]] = []
    header: list[str] = []

    def flush_table() -> None:
        nonlocal rows, header
        for row in rows:
            parts = [f"{h}: {c}" for h, c in zip(header, row) if c]
            out.append(f"{W['table_row']} " + ". ".join(parts) + ".")
        rows, header = [], []

    in_sources = False
    for raw in md.splitlines():
        line = raw.rstrip()

        if line.startswith("|"):
            cells = [strip_inline(c) for c in line.strip().strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            if not header:
                header = cells
            else:
                rows.append(cells)
            continue
        if rows or header:
            flush_table()

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            title = strip_inline(heading.group(2))
            in_sources = bool(re.match(r"^(core\s+)?(sources|fuentes)",
                                       title, re.I))
            if in_sources:
                out.append("")
                out.append(W["sources_note"])
                continue
            out.append("")
            out.append(f"{title}." if not title.endswith((".", "?", "!")) else title)
            continue

        if in_sources:
            continue

        if not line.strip():
            out.append("")
            continue
        if re.match(r"^-{3,}$", line.strip()):
            continue

        item = re.match(r"^\s*(?:[-*]|(\d+)\.)\s+(.*)$", line)
        if item:
            body = strip_inline(item.group(2))
            if body and not body.endswith((".", ";", ":", "?", "!")):
                body += "."
            out.append(body)
            continue

        out.append(strip_inline(line))

    flush_table()

    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["en", "es"], help="one edition only")
    ap.add_argument("--only", help="substring of the filename")
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / "site.yaml").read_text(encoding="utf-8"))
    langs = [args.lang] if args.lang else ["en", "es"]
    total = 0

    for lang in langs:
        L = cfg[lang]
        src = ROOT / "content" / (L["dir"] or "en")
        names = [L["method"]["file"]] + [s["file"] for s in L["studies"]]
        for name in names:
            if args.only and args.only not in name:
                continue
            text = convert((src / name).read_text(encoding="utf-8"), lang)
            dest = OUT / lang / (Path(name).stem + ".txt")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
            words = len(text.split())
            # 150 words per minute is a calm, neutral reading pace
            print(f"  {lang}/{dest.name:26} {words:6,} words  "
                  f"~{words // 150}:{words % 150 * 60 // 150:02d}")
            total += words

    print(f"\n{total:,} words total, roughly {total // 150 // 60} h "
          f"{total // 150 % 60} min of narration at 150 wpm")
    print(f"Written to {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
