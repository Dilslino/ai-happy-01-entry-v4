#!/usr/bin/env python3
"""ai-happy-01 V4 entrypoint.

Takes the bundled JPEG sitting next to this file, checks that it is a
well-formed JPEG inside the size limits, and copies it verbatim into
the output directory as entry.png. Standard library only; no network
access, no randomness, fully deterministic.
"""

import os
import sys

SOURCE = "image.jpg"
DEST = "entry.png"
BYTE_LIMIT = 1 << 20
SIDE_LIMIT = 1024

# Markers that carry a frame header (the start-of-frame family).
FRAME_MARKERS = frozenset({
    0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
    0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
})


def die(reason):
    print("error: " + reason, file=sys.stderr)
    raise SystemExit(1)


def frame_size(payload):
    """Return (width, height) from the first SOF segment in payload."""
    if payload[:2] != b"\xff\xd8":
        die("input is not a JPEG (no SOI marker)")
    cursor = 2
    total = len(payload)
    # Walk the marker stream. Consecutive 0xFF bytes are padding, so
    # collapse them before reading the tag that follows.
    while cursor < total:
        if payload[cursor] != 0xFF:
            die("broken JPEG marker stream")
        while cursor < total and payload[cursor] == 0xFF:
            cursor += 1
        if cursor >= total:
            break
        tag = payload[cursor]
        cursor += 1
        if tag == 0xD8 or tag == 0x01 or 0xD0 <= tag <= 0xD7:
            continue
        if tag == 0xD9 or tag == 0xDA:
            break
        if cursor + 2 > total:
            die("JPEG segment cut short")
        span = (payload[cursor] << 8) | payload[cursor + 1]
        if span < 2 or cursor + span > total:
            die("JPEG segment cut short")
        if tag in FRAME_MARKERS:
            if span < 7:
                die("SOF segment too short")
            tall = (payload[cursor + 3] << 8) | payload[cursor + 4]
            wide = (payload[cursor + 5] << 8) | payload[cursor + 6]
            return wide, tall
        cursor += span
    die("no SOF marker found in JPEG")


def run():
    folder = os.path.dirname(os.path.abspath(__file__))
    origin = os.path.join(folder, SOURCE)
    try:
        with open(origin, "rb") as handle:
            blob = handle.read()
    except OSError as exc:
        die("cannot read %s: %s" % (SOURCE, exc))
    if len(blob) > BYTE_LIMIT:
        die("input exceeds 1 MiB")
    if blob[:2] != b"\xff\xd8":
        die("input is not a JPEG (no SOI marker)")
    if blob[-2:] != b"\xff\xd9":
        die("input is not a JPEG (no EOI marker)")
    width, height = frame_size(blob)
    if width > SIDE_LIMIT or height > SIDE_LIMIT:
        die("image side exceeds 1024 px")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    target = os.path.join(outdir, DEST)
    with open(target, "wb") as handle:
        handle.write(blob)
    print("%s: %dx%d, %d bytes" % (SOURCE, width, height, len(blob)))


if __name__ == "__main__":
    run()
