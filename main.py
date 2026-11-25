#!/usr/bin/env python3
"""Entry point for news-image-20261125 (program/v1).

The front page image is committed in this repository as entry.png.
This program copies it byte-for-byte to the output location the
grader expects, then checks the copy is a real PNG inside the
competition's size gate. Standard library only, no network.
"""
import os
import shutil
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576  # 1 MiB: the kit's size gate for entry.png


def die(message):
    print("error: %s" % message, file=sys.stderr)
    return 1


def check_png(path):
    """Return an error string, or None when path is a PNG under the gate."""
    with open(path, "rb") as handle:
        magic = handle.read(len(PNG_MAGIC))
    if magic != PNG_MAGIC:
        return "not a PNG (bad magic bytes)"
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        return "too large: %d bytes, gate is %d" % (size, MAX_BYTES)
    return None


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(base, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    dest = os.path.join(out_dir, "entry.png")

    if not os.path.isfile(source):
        return die("entry.png not found next to main.py: %s" % source)

    problem = check_png(source)
    if problem is not None:
        return die("committed entry.png is unusable: %s" % problem)

    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(source, dest)

    problem = check_png(dest)
    if problem is not None:
        return die("copied output is unusable: %s" % problem)

    print("wrote %s (%d bytes, valid PNG)" % (dest, os.path.getsize(dest)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
