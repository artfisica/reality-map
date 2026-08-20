#!/usr/bin/env python3
"""Fail the build if any internal link, asset or anchor does not resolve.

External links are listed but never fetched: the point of this check is that
the atlas never sends a reader to a page of its own that is not there.
"""

import re
import sys
from pathlib import Path
from urllib.parse import urldefrag

OUT = Path(__file__).resolve().parent.parent / "docs"

HREF = re.compile(r'(?:href|src)="([^"]+)"')
ID = re.compile(r'\sid="([^"]+)"')


def main() -> int:
    if not OUT.exists():
        sys.exit("docs/ not found. Run: python build.py")

    pages = sorted(OUT.rglob("*.html"))
    ids = {p: set(ID.findall(p.read_text(encoding="utf-8"))) for p in pages}

    problems, external = [], set()

    for page in pages:
        text = page.read_text(encoding="utf-8")
        for href in HREF.findall(text):
            if href.startswith(("http://", "https://", "mailto:", "data:")):
                external.add(href.split("/")[2] if "//" in href else href)
                continue

            target, fragment = urldefrag(href)

            if not target:  # same page anchor
                if fragment and fragment not in ids[page] and "=" not in fragment:
                    problems.append(f"{page.relative_to(OUT)} -> #{fragment} (no such id)")
                continue

            resolved = (page.parent / target).resolve()
            if resolved.is_dir():
                resolved = resolved / "index.html"
            if not resolved.exists():
                problems.append(f"{page.relative_to(OUT)} -> {href} (missing)")
                continue
            if fragment and resolved.suffix == ".html" and "=" not in fragment:
                if fragment not in ids.get(resolved, set()):
                    problems.append(
                        f"{page.relative_to(OUT)} -> {href} (no such id in target)")

    print(f"{len(pages)} pages, {len(external)} external hosts referenced")
    for host in sorted(external):
        print(f"  {host}")

    if problems:
        print(f"\n{len(problems)} broken internal links:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1

    print("\nAll internal links resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
