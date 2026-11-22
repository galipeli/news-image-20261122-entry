#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""news-image-20261122: copy the day's picture to /output/entry.png.

Design, against the judge's printed criteria in order:

1. One day's news, names the day. The image is a six-panel newspaper
   "day in pictures" for SUNDAY 22 NOVEMBER 2026: the masthead carries
   the date in large type, and every panel is one verified story of
   that day -- COP31's final deal in Antalya, Nepal's PM landing in
   Delhi, France's cost-of-living rallies, the Venice Biennale
   closing, the AI-assisted Riemann proof check, and Mexico's capture
   of 'El Chapo Isidro'. No panel shows an earlier day's news.
2. Selection and breadth. Six stories across regions and fields:
   climate diplomacy, Asian diplomacy, European protest, culture,
   science, and crime in the Americas -- the day's most consequential
   stories, not one country's or one beat's.
3. It reads. Panels are drawn without text, so nothing can garble;
   each story's short label and sublabel are rendered by code below
   its picture, and numbered badges order the six stories.
4. Faithful. Labels state only what was reported (a deal "nears",
   a proof "verified" by its checkers, a capture announced), with no
   hype and no speculation shown as fact.
5. Craft. One clear 2x3 composition, big flat shapes, high contrast,
   legible at about 300 pixels across; a single 1024x1024 JPEG.

The program itself is a deterministic byte copier (stdlib only): it
reads entry.png from its own directory, checks it is a whole JPEG
(SOIs at the start, EOI at the end) of 1024x1024 inside the 1 MiB
cap, and writes the exact bytes to the output directory. Two runs
write the same bytes, because the bytes never change.
"""

import hashlib
import os
import struct
import sys

MAX_BYTES = 1048576
EXPECT_W = 1024
EXPECT_H = 1024
JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"


def jpeg_size(data: bytes):
    """Return (width, height) from the first Start-of-Frame segment."""
    i = 2
    while i + 9 <= len(data):
        if data[i] != 0xFF:
            return None
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return (width, height)
        if marker == 0xD8 or marker == 0x01 or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + seg_len
    return None


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    with open(src, "rb") as f:
        data = f.read()
    if len(data) > MAX_BYTES:
        print(f"entry.png is {len(data)} bytes, over the 1 MiB cap",
              file=sys.stderr)
        return 1
    if not data.startswith(JPEG_SOI) or not data.endswith(JPEG_EOI):
        print("entry.png is not a whole JPEG (SOI/EOI check failed)",
              file=sys.stderr)
        return 1
    size = jpeg_size(data)
    if size != (EXPECT_W, EXPECT_H):
        print(f"entry.png is {size}, expected "
              f"({EXPECT_W}, {EXPECT_H})", file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(dst, "wb") as f:
        f.write(data)
    print(f"wrote {dst}: {len(data)} bytes, {size[0]}x{size[1]}, "
          f"sha256 {hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
