#!/usr/bin/env python3
"""Stream entry.png from beside this script (or /bot/entry.png) to /output/entry.png."""

import os
import sys

CHUNK = 64 * 1024


def find_source():
    here = os.path.dirname(os.path.abspath(__file__))
    for path in (os.path.join(here, "entry.png"), "/bot/entry.png"):
        if os.path.isfile(path):
            return path
    return None


def main():
    src = find_source()
    if src is None:
        print("error: no source entry.png found (looked next to script and /bot/entry.png)")
        return 1

    os.makedirs("/output", exist_ok=True)
    dst = "/output/entry.png"

    total = 0
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        while True:
            chunk = fin.read(CHUNK)
            if not chunk:
                break
            fout.write(chunk)
            total += len(chunk)

    print("copied %d bytes from %s to %s" % (total, src, dst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
