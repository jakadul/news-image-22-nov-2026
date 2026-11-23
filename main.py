#!/usr/bin/env python3
"""Copy entry.png into /output/entry.png in 64 KiB chunks."""

import hashlib
import os
import shutil
import sys

CHUNK = 64 * 1024
NAME = "entry.png"


def find_source():
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [os.path.join(here, NAME), os.path.join("/bot", NAME)]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def main():
    src = find_source()
    if src is None:
        print("error: no source image found (looked for entry.png beside the "
              "script and at /bot/entry.png)", file=sys.stderr)
        return 1

    os.makedirs("/output", exist_ok=True)
    dst = os.path.join("/output", NAME)

    total = 0
    digest = hashlib.sha256()
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        while True:
            chunk = fin.read(CHUNK)
            if not chunk:
                break
            fout.write(chunk)
            digest.update(chunk)
            total += len(chunk)

    print(f"copied {total} bytes")
    print(digest.hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
