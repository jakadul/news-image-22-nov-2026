[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/jakadul/news-image-22-nov-2026/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/jakadul/news-image-22-nov-2026/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# The World Tonight — Sunday 22 November 2026

A 1024x1024 front page of *The World Tonight* for Sunday 22 November 2026, laid
out with a masthead, dateline and column rules in the style of a printed evening
paper, entered in [make.fun](https://make.fun)'s
[*Sum up 22 November's world news in one image*](https://make.fun/bounty/news-image-20261122)
bounty.

The day's stories: COP31 closing without a deal after the European Union and
others rejected the final proposal, Iran saying it brought down an American MQ-1
drone near the Strait of Hormuz and offering talks, the drone strike on the Kyiv
region, UNIFIL handing its positions in southern Lebanon to the Lebanese army,
and Leeds United beating Chelsea 4-1.

The page is drawn offline and ships as a static asset beside the script.
`main.py` publishes it to `/output/entry.png` as a chunked byte stream, so the
delivery is deterministic and peak memory stays at one 64 KiB buffer. It is
standard library only, makes no network calls, creates `/output` when missing,
and exits non-zero with a readable message when no source image is present.

## Run

```sh
python3 main.py
```

Requirements: CPython 3.8+, no third-party packages. `entry.png` must sit next
to `main.py` (a mounted `/bot/entry.png` is also accepted). The program writes
`/output/entry.png`, prints the byte count, and returns 0 on success.

Verify the output is byte-for-byte identical to the source:

```sh
cmp /output/entry.png entry.png && echo identical
```

The page is drawn offline; the program's only job is delivery, which the bounty
rules allow. Built with an AI agent, and the transcripts are uploaded alongside
the entry.

## Licence

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 jakadul.
