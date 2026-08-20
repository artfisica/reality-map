#!/usr/bin/env python3
"""Draw assets/social.png, the 1200x630 preview card.

The mosaic on the card is the real ledger, not decoration: one tile per claim,
in ledger order, coloured by evidence class. Re-run after the ledger changes.

    python scripts/make_social.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

import build  # noqa: E402

W, H = 1200, 630
DEEP = (20, 23, 27)
INK = (236, 234, 223)
MUTED = (155, 160, 153)
COLOURS = {
    "record": (111, 195, 220), "court": (166, 172, 246), "finding": (237, 166, 208),
    "position": (226, 182, 101), "inference": (242, 156, 112), "forecast": (169, 187, 201),
    "unknown": (120, 120, 120),
}


CACHE = ROOT / ".fontcache"


def as_ttf(woff2: Path) -> Path | None:
    """The site ships woff2, which Pillow cannot read. Convert once and cache."""
    ttf = CACHE / (woff2.stem + ".ttf")
    if ttf.exists():
        return ttf
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return None
    try:
        CACHE.mkdir(exist_ok=True)
        f = TTFont(str(woff2))
        f.flavor = None
        f.save(str(ttf))
        return ttf
    except Exception:
        return None


def font(stem: str, size: int, weight: int | None = None):
    woff2 = ROOT / "assets" / "fonts" / f"{stem}.woff2"
    if woff2.exists():
        ttf = as_ttf(woff2)
        if ttf:
            try:
                f = ImageFont.truetype(str(ttf), size)
                if weight is not None:
                    try:
                        f.set_variation_by_axes([weight])
                    except Exception:
                        pass
                return f
            except OSError:
                pass
    for fallback in ("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(fallback).exists():
            return ImageFont.truetype(fallback, size)
    return ImageFont.load_default(size)


def main() -> int:
    cfg = yaml.safe_load((ROOT / "site.yaml").read_text(encoding="utf-8"))
    L = cfg["en"]
    src = ROOT / "content" / "en"
    _, sections, _, _ = build.parse_ledger(
        src / L["ledger"]["file"], L["evidence_classes"], cfg["site"]["match_order"])

    img = Image.new("RGB", (W, H), DEEP)
    d = ImageDraw.Draw(img)

    title = font("newsreader-latin-wght-normal", 82, weight=600)
    small = font("ibm-plex-sans-latin-wght-normal", 24, weight=400)

    x, y = 72, 92
    for line in L.get("title_lines") or [L["title"]]:
        d.text((x, y), line, font=title, fill=INK)
        y += 86

    d.text((x, y + 18), L["tagline"], font=small, fill=MUTED)

    # the mosaic, one tile per claim
    size, gap, group_gap = 22, 5, 22
    tx, ty = x, H - 190
    for sec in sections:
        for c in sec["claims"]:
            if tx + size > W - 72:
                tx, ty = x, ty + size + gap
            d.rectangle([tx, ty, tx + size, ty + size],
                        fill=COLOURS.get(c.class_id, COLOURS["unknown"]))
            tx += size + gap
        tx += group_gap

    total = sum(len(s["claims"]) for s in sections)
    d.text((x, H - 92), f'{total} claims \u00b7 {len(sections)} files \u00b7 '
                        f'{L["edition"]}', font=small, fill=MUTED)
    d.text((x, H - 56), cfg["site"]["author"], font=small, fill=MUTED)

    out = ROOT / "assets" / "social.png"
    img.save(out, optimize=True)
    print(f"Wrote {out} ({total} claims)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
