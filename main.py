#!/usr/bin/env python3
"""Copy entry.png to /output/entry.png in 64 KiB chunks and print sha256.

Python 3.13, standard library only, no network.
"""

import hashlib
import os
import sys

CHUNK = 64 * 1024
HERE = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = [os.path.join(HERE, "entry.png"), "/bot/entry.png"]
OUT_DIR = "/output"
OUT_PATH = os.path.join(OUT_DIR, "entry.png")


def main():
    src = None
    for cand in CANDIDATES:
        if os.path.isfile(cand):
            src = cand
            break
    if src is None:
        print("ERROR: no entry.png found beside the script (%s) or at /bot/entry.png"
              % os.path.join(HERE, "entry.png"), file=sys.stderr)
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)

    digest = hashlib.sha256()
    total = 0
    with open(src, "rb") as fin, open(OUT_PATH, "wb") as fout:
        while True:
            buf = fin.read(CHUNK)
            if not buf:
                break
            fout.write(buf)
            digest.update(buf)
            total += len(buf)

    print("source: %s" % src)
    print("bytes: %d" % total)
    print("sha256: %s" % digest.hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
