#!/usr/bin/env python3
"""Deliver the "The World Tonight" front page to /output/entry.png.

The newspaper page is drawn offline and shipped as ``entry.png`` next to this
file; this program does no rendering and no network access. It only copies that
read-only asset (mounted at /bot by the harness) into the writable output
directory, which is exactly what the bounty rules permit.

The copy is a plain byte-for-byte stream copy, so two runs always produce
identical files.
"""

import shutil
from pathlib import Path

SOURCE_NAMES = ("entry.png", "/bot/entry.png")


def find_source() -> Path:
    """Return the first existing entry.png, preferring the one beside this file."""
    here = Path(__file__).resolve().parent
    for name in SOURCE_NAMES:
        candidate = here / name if not name.startswith("/") else Path(name)
        if candidate.is_file():
            return candidate
    raise SystemExit("entry.png not found")


def main() -> None:
    source = find_source()
    output_dir = Path("/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, output_dir / "entry.png")


if __name__ == "__main__":
    main()
