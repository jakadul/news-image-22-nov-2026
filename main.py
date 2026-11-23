#!/usr/bin/env python3
"""Publish the "The World Tonight" front page as /output/entry.png.

The finished newspaper page ships beside this script as ``entry.png``. This
program performs no rendering and no network access: it locates that asset and
streams it byte-for-byte into the writable output directory expected by the
bounty harness.

Design notes
------------
* Standard library only, no third-party imports, CPython 3.8+.
* Deterministic: the source is a fixed file and the copy is a raw byte stream,
  so repeated runs produce identical output.
* The transfer is a chunked read/write loop rather than a whole-file helper, so
  peak memory stays at one buffer regardless of how large the page gets.
* The output directory is created when missing, and a missing source aborts
  with a non-zero exit status and a readable message instead of a traceback.
"""

import sys
from pathlib import Path

SOURCE_CANDIDATES = (
    Path(__file__).resolve().parent / "entry.png",
    Path("/bot/entry.png"),
)
OUTPUT_DIR = Path("/output")
OUTPUT_NAME = "entry.png"
CHUNK_SIZE = 64 * 1024


def locate_source() -> Path:
    """Return the first existing entry.png, preferring the one beside this file."""
    for candidate in SOURCE_CANDIDATES:
        if candidate.is_file():
            return candidate
    tried = ", ".join(str(path) for path in SOURCE_CANDIDATES)
    raise SystemExit(f"error: entry.png not found (looked in: {tried})")


def stream_copy(source: Path, destination: Path) -> int:
    """Copy source to destination in fixed-size chunks and return bytes written."""
    written = 0
    with source.open("rb") as reader, destination.open("wb") as writer:
        while True:
            chunk = reader.read(CHUNK_SIZE)
            if not chunk:
                break
            writer.write(chunk)
            written += len(chunk)
        writer.flush()
    return written


def main() -> int:
    source = locate_source()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT_DIR / OUTPUT_NAME

    written = stream_copy(source, destination)
    expected = source.stat().st_size
    if written != expected:
        raise SystemExit(f"error: short write to {destination} ({written} of {expected} bytes)")

    print(f"wrote {destination} ({written} bytes) from {source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
