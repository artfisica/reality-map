#!/usr/bin/env python3
"""Encode a recording to the house spec and print its site.yaml entry.

House spec: mono AAC, 40 kbps, 32 kHz, loudness normalised to -16 LUFS, with
the metadata atom moved to the front so playback starts before the file has
finished downloading. Speech at this bitrate stays clean and costs a reader on
a metered connection about a third of what the raw export does.

    python scripts/encode_audio.py raw/study-02-en.m4a --out study-02-en
    python scripts/encode_audio.py raw/*.m4a            # batch
    python scripts/encode_audio.py --check              # audit what is shipped

Requires ffmpeg on PATH.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "assets" / "audio"

BITRATE = "40k"
RATE = "32000"
LOUDNESS = "loudnorm=I=-16:TP=-1.5:LRA=11"


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size,bit_rate:stream=channels,sample_rate",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format", {})
    return {"duration": float(fmt.get("duration", 0)),
            "size": int(fmt.get("size", 0)),
            "bitrate": int(fmt.get("bit_rate", 0) or 0),
            "channels": int(stream.get("channels", 0) or 0),
            "rate": int(stream.get("sample_rate", 0) or 0)}


def clock(seconds: float) -> str:
    total = round(seconds)
    return f"{total // 60}:{total % 60:02d}"


def encode(source: Path, name: str) -> Path:
    dest = AUDIO / f"{name}.m4a"
    dest.parent.mkdir(parents=True, exist_ok=True)
    before = probe(source)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(source),
         "-af", LOUDNESS, "-c:a", "aac", "-b:a", BITRATE,
         "-ar", RATE, "-ac", "1", "-movflags", "+faststart", str(dest)],
        check=True)
    after = probe(dest)
    saved = 100 - (after["size"] * 100 // max(before["size"], 1))
    print(f"  {source.name} -> assets/audio/{dest.name}")
    print(f"    {before['size']/1e6:.1f} MB -> {after['size']/1e6:.1f} MB "
          f"({saved}% smaller), {clock(after['duration'])}")
    print("    site.yaml entry:")
    print(f"""      audio:
        src: assets/audio/{dest.name}
        title: TITLE HERE
        duration: "{clock(after['duration'])}"
        description: >-
          DESCRIPTION HERE""")
    return dest


def check() -> int:
    if not AUDIO.is_dir():
        print("No assets/audio directory.")
        return 0
    files = sorted(AUDIO.glob("*.m4a"))
    if not files:
        print("No episodes yet.")
        return 0
    total_size = total_time = 0
    problems = 0
    print(f"{'file':26} {'size':>8} {'length':>8} {'kbps':>6} {'ch':>3} {'kHz':>6}")
    for path in files:
        info = probe(path)
        total_size += info["size"]
        total_time += info["duration"]
        off = info["channels"] != 1 or info["rate"] > 32000
        problems += off
        print(f"{path.name:26} {info['size']/1e6:7.1f}M {clock(info['duration']):>8} "
              f"{info['bitrate']//1000:6} {info['channels']:3} {info['rate']/1000:6.1f}"
              + ("   <- re-encode" if off else ""))
    print(f"\n{len(files)} episodes, {total_size/1e6:.0f} MB, "
          f"{int(total_time//3600)} h {int(total_time%3600//60)} min")
    if total_size > 300e6:
        print("Over 300 MB in the repository. Consider attaching audio to "
              "GitHub Releases instead of committing it.")
    if problems:
        print(f"{problems} file(s) are not at the house spec.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="*", type=Path)
    ap.add_argument("--out", help="output name, without extension (single input)")
    ap.add_argument("--check", action="store_true", help="audit shipped episodes")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is not on PATH.")
    if args.check or not args.sources:
        return check()
    if args.out and len(args.sources) > 1:
        sys.exit("--out takes a single input.")
    for source in args.sources:
        encode(source, args.out or source.stem)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
