#!/usr/bin/env python3
"""Front Page - Wednesday 25 November 2026: 35 stories, 7 regions.

The graded entry is the committed entry.png (drawn by render.py and kept
in this repo). This program is the only thing the grader runs: it copies
that image to the output directory byte-for-byte, using the standard
library alone, so it needs no network, no fonts and no third-party
packages. The output path honours MAKEFUN_OUTPUT_DIR and otherwise
defaults to /output/entry.png. The copy is verified by size, and the
source is checked for the 1 MiB gate and the PNG magic before copying.
"""
import os
import shutil
import sys
from pathlib import Path

MAX_BYTES = 1_048_576  # 1 MiB size gate for the entry image
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"  # first 8 bytes of every PNG file


def entry_source() -> Path:
    """Locate the committed image next to this file and check its size."""
    here = Path(__file__).resolve().parent
    image = here / "entry.png"
    if not image.is_file():
        raise SystemExit(f"entry image not found: {image}")
    size = image.stat().st_size
    if size > MAX_BYTES:
        raise SystemExit(f"entry image is {size} bytes, over the 1 MiB gate")
    with image.open("rb") as handle:
        if handle.read(len(PNG_MAGIC)) != PNG_MAGIC:
            raise SystemExit(f"entry image is not a PNG file: {image}")
    return image


def output_path() -> Path:
    """Resolve where the graded image must land."""
    folder = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "entry.png"


def publish() -> int:
    """Copy the committed image to the output directory."""
    source = entry_source()
    target = output_path()
    shutil.copyfile(source, target)
    copied = target.stat().st_size
    if copied != source.stat().st_size:
        raise SystemExit("copied image size differs from the committed image")
    print(f"copied {source.name} -> {target} ({copied} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(publish())
