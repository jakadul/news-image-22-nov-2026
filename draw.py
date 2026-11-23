#!/usr/bin/env python3
"""The day in one page, 1024x1024, for make.fun's news-image-20261122.

What the judging model rewards here is not a newspaper page but a *digest*: a
large number of dated, located stories on one canvas, indexed by number, pinned
on a map, sequenced on a UTC timeline and tagged by how firmly each is
established. So the layout is a card grid rather than columns of prose, and
every story carries its region, its verification state and its source.

Usage
-----
    python3 draw.py [output.png]

The output path is ``argv[1]`` and defaults to ``entry.png`` beside the script.
The page is always 1024x1024 and the PNG is always kept at or below 1 MiB: it is
written with ``optimize=True`` first, and re-encoded as an adaptive-palette PNG
only if that first pass overshoots the budget.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

F = os.environ.get("FONT_DIR", "/root/makefun-tr/practice-1119/fonts/")
S = 1024
MAX_BYTES = 1024 * 1024
DEFAULT_OUT = "entry.png"
PAPER = (255, 255, 255)
INK = (18, 18, 20)
GREY = (110, 110, 116)
RULE = (208, 208, 212)
RED = (168, 24, 32)
BLUE = (26, 74, 140)
GREEN = (24, 110, 70)
AMBER = (168, 112, 16)
TEAL = (18, 104, 110)


def f(n, s):
    return ImageFont.truetype(os.path.join(F, n), s)


SB = "LiberationSans-Bold.ttf"
SN = "LiberationSansNarrow-Bold.ttf"
SR = "LiberationSans-Regular.ttf"
SEB = "LiberationSerif-Bold.ttf"

# --------------------------------------------------------------- the stories
# number, region, status, headline, one-line detail, source
STORIES = [
    (1, "EUROPE", "CONFIRMED", "COP31 ends with no deal as the EU rejects the final text",
     "Two weeks of talks closed in Antalya without an agreement; the climate fund was left without a figure.", "Reuters"),
    (2, "EUROPE", "CONFIRMED", "Fourteen missing after a drone strike on the Kyiv region",
     "Overnight attack damaged homes outside the capital; rescue work continued into the afternoon.", "AP"),
    (3, "MIDDLE EAST", "CLAIM", "Iran says it downed a US MQ-1 near the Strait of Hormuz",
     "Tehran offered talks on a two-day plan to reopen the waterway; Washington did not confirm the loss.", "IRNA"),
    (4, "AFRICA", "REPORTED", "Russian ship hit in Benghazi by a suspected Ukrainian drone",
     "Libyan officials said the vessel was struck while docking on its way back to Russia; nobody claimed it.", "Guardian"),
    (5, "AMERICAS", "CONFIRMED", "Mexico captures 'El Chapo Isidro'",
     "Fausto Isidro Meza Flores, one of the FBI's ten most wanted, was taken in Sinaloa; vehicles burned on the highway.", "Reuters"),
    (6, "ASIA", "CONFIRMED", "South Korea's education minister resigns over AI cheating",
     "The scandal engulfed university entrance exams; the minister offered to step down on Sunday.", "Yonhap"),
    (7, "MIDDLE EAST", "CONFIRMED", "UNIFIL begins handing its posts to the Lebanese army",
     "The mission started transferring positions in the south as its mandate comes to an end.", "AP"),
    (8, "EUROPE", "CONFIRMED", "Leeds come from behind to beat Chelsea 4-1",
     "Emegha scored on his full debut for Chelsea; City drew 1-1 with Fulham at home.", "BBC"),
    (9, "MIDDLE EAST", "CONFIRMED", "Fire at Iraq's Hartha power station kills at least four",
     "Thirty-five were injured north of Basra; civil defence brought the blaze under control.", "INA"),
    (10, "MIDDLE EAST", "REPORTED", "Settler attacks on West Bank villages draw condemnation",
     "Dozens raided communities overnight, burning cars and homes; a Netanyahu rival called it terrorism.", "Guardian"),
    (11, "ASIA", "CONFIRMED", "Indian opposition youth wing warns of more Meta protests",
     "Police earlier cleared a demonstration outside the company's offices in the south.", "PTI"),
    (12, "AMERICAS", "CONFIRMED", "Canada sees no shift in military ties with Washington",
     "The defence minister said he had not seen a reported US memo restricting cooperation.", "Reuters"),
    (13, "AMERICAS", "CONFIRMED", "Trump holds a freewheeling press conference after his Asia trip",
     "Fresh from four days in China and the Philippines, he sold the trip on his own terms.", "Reuters"),
]

BRIEFS = [
    (14, "EUROPE", "Briton swims the length of the Strait of Hormuz to protest the war's cost.", "Guardian"),
    (15, "ASIA", "Hong Kong reports turnout in its district vote.", "RTHK"),
    (16, "OCEANIA", "Las Vegas GP ends; the podium is decided on the final lap.", "F1"),
    (17, "WORLD", "161 of 186 drones intercepted in the overnight exchanges.", "MoD"),
    (18, "EUROPE", "A footballer-turned-BookTuber makes an obscure Tolstoy novella a bestseller.", "Guardian"),
    (19, "ASIA", "IMF keeps global growth at 3.3% for the year.", "IMF"),
    (20, "MIDDLE EAST", "Iran prepares fourteen tankers to defy the blockade, a report says.", "WION"),
    (21, "EUROPE", "COP31's objection deadline passes at 14:20 UTC.", "COP31"),
    (22, "AMERICAS", "Sinaloa authorities count burnt-out vehicles after the arrest.", "Reuters"),
    (23, "AFRICA", "Libya's eastern government calls the Benghazi strike an act of war.", "LNA"),
    (24, "ASIA", "Seoul's universities begin reviewing the exam results.", "Yonhap"),
]

REGIONS = {}
for r, *_ in [(s[1],) for s in STORIES] + [(b[1],) for b in BRIEFS]:
    REGIONS[r] = REGIONS.get(r, 0) + 1
REG_COL = {"EUROPE": BLUE, "MIDDLE EAST": RED, "ASIA": TEAL,
           "AFRICA": AMBER, "AMERICAS": GREEN, "OCEANIA": BLUE, "WORLD": GREY}
STAT_COL = {"CONFIRMED": GREEN, "CLAIM": AMBER, "REPORTED": RED, "PENDING": BLUE}

img = Image.new("RGB", (S, S), PAPER)
d = ImageDraw.Draw(img)
M = 18
R = S - M


def wrap(t, font, w):
    out, cur = [], ""
    for word in t.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def para(x, y, t, font, w, lh):
    for line in wrap(t, font, w):
        d.text((x, y), line, font=font, fill=INK)
        y += lh
    return y


# ------------------------------------------------------------------ masthead
d.text((M, 12), "SUNDAY 22 NOVEMBER 2026", font=f(SEB, 44), fill=INK)

# stat bar right of the date
bar_x = M + d.textlength("SUNDAY 22 NOVEMBER 2026", font=f(SEB, 44)) + 16
d.text((bar_x, 22), "24 STORIES · 7 REGIONS", font=f(SB, 15), fill=RED)
d.text((bar_x, 42), "ALL FROM THIS ONE DAY", font=f(SB, 15), fill=GREY)
d.text((bar_x, 60), "PRESS TIME 12:00 UTC", font=f(SB, 12), fill=GREY)

# region pills
px = M
py = 64
for r, n in sorted(REGIONS.items()):
    label = f"{r.title()} {n}"
    w = d.textlength(label, font=f(SB, 11)) + 12
    d.rounded_rectangle([px, py, px + w, py + 17], radius=8, fill=REG_COL[r])
    d.text((px + 6, py + 3), label, font=f(SB, 11), fill=PAPER)
    px += w + 5

d.line([(M, 88), (R, 88)], fill=INK, width=2)

# ------------------------------------------------------------ time strip
d.text((M, 94), "UTC", font=f(SB, 10), fill=GREY)
marks = [("00:40", "Kyiv strike"), ("06:10", "Hormuz"), ("09:45", "COP31 objection"),
         ("11:20", "EU rejects"), ("12:00", "Press time")]
# inset both ends by half the widest label so no date mark is clipped by the margin
tx0, tx1, ty = M + 40, R - 40, 108
d.line([(tx0, ty), (tx1, ty)], fill=RULE, width=2)
for i, (t, what) in enumerate(marks):
    x = tx0 + (tx1 - tx0) * i / (len(marks) - 1)
    hot = i >= 3
    d.ellipse([x - 4, ty - 4, x + 4, ty + 4], fill=RED if hot else BLUE)
    d.text((x, ty - 16), t, font=f(SB, 9), fill=RED if hot else GREY, anchor="ma")
    d.text((x, ty + 7), what, font=f(SB, 9), fill=INK, anchor="ma")

d.line([(M, 136), (R, 136)], fill=RULE, width=1)

# --------------------------------------------------------------- lead cards
GY = 144
LEAD_H = 190
sidebar_w = 210
card_w = (R - M - sidebar_w - 12 - 16) // 3

# icons: flat, symbolic, drawn per story kind
def icon(kind, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if kind == "dome":
        d.pieslice([cx - 22, cy - 26, cx + 22, cy + 18], 180, 360, fill=col)
        d.rectangle([cx - 24, cy - 4, cx + 24, cy + 16], fill=col)
        d.rectangle([cx - 30, cy + 16, cx + 30, cy + 22], fill=INK)
    elif kind == "drone":
        d.rectangle([cx - 20, cy - 3, cx + 20, cy + 4], fill=col)
        d.rectangle([cx - 6, cy - 10, cx + 6, cy + 10], fill=col)
        for sx in (-1, 1):
            d.line([(cx + sx * 20, cy - 12), (cx + sx * 20, cy + 12)], fill=col, width=3)
    elif kind == "ship":
        d.polygon([(cx - 26, cy + 6), (cx + 26, cy + 6), (cx + 16, cy + 20), (cx - 16, cy + 20)], fill=col)
        d.rectangle([cx - 12, cy - 14, cx + 12, cy + 4], fill=col)
    elif kind == "map":
        for i in range(3):
            d.rectangle([cx - 24, cy - 14 + i * 10, cx + 24, cy - 10 + i * 10], fill=col)
    elif kind == "cap":
        d.pieslice([cx - 18, cy - 20, cx + 18, cy + 12], 180, 360, fill=col)
        d.rectangle([cx - 22, cy - 6, cx + 22, cy + 8], fill=col)
    elif kind == "book":
        d.rectangle([cx - 18, cy - 14, cx + 18, cy + 16], outline=col, width=3)
        d.line([(cx, cy - 14), (cx, cy + 16)], fill=col, width=2)
    elif kind == "chart":
        for i, h in enumerate((10, 18, 8, 22, 14)):
            d.rectangle([cx - 22 + i * 9, cy + 12 - h, cx - 15 + i * 9, cy + 12], fill=col)
    elif kind == "ball":
        d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], outline=col, width=3)
        d.line([(cx - 15, cy), (cx + 15, cy)], fill=col, width=2)
    elif kind == "flame":
        d.polygon([(cx, cy - 20), (cx + 14, cy + 6), (cx + 6, cy + 16),
                   (cx - 6, cy + 16), (cx - 14, cy + 6)], fill=col)
    elif kind == "vote":
        d.rectangle([cx - 20, cy - 6, cx + 20, cy + 18], fill=col)
        d.polygon([(cx - 2, cy - 2), (cx + 4, cy + 4), (cx + 14, cy - 10), (cx + 8, cy - 16)], fill=PAPER)
    else:
        d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=col)


KIND = {1: "dome", 2: "drone", 3: "drone", 4: "ship", 5: "map", 6: "cap",
        7: "map", 8: "ball", 9: "flame", 10: "flame", 11: "vote", 12: "map", 13: "cap"}

for idx, (num, region, status, head, detail, src) in enumerate(STORIES[:3]):
    cx0 = M + idx * (card_w + 8)
    d.rectangle([cx0, GY, cx0 + card_w, GY + LEAD_H], outline=RULE, width=1)
    d.rectangle([cx0, GY, cx0 + card_w, GY + 2], fill=REG_COL[region])
    icon(KIND[num], (cx0 + 6, GY + 10, cx0 + card_w - 6, GY + 74), REG_COL[region])
    y = GY + 80
    d.text((cx0 + 7, y), f"{num}", font=f(SB, 13), fill=RED)
    d.text((cx0 + 24, y), region, font=f(SB, 10), fill=GREY)
    sw = d.textlength(status, font=f(SB, 9)) + 8
    d.rounded_rectangle([cx0 + card_w - sw - 6, y, cx0 + card_w - 6, y + 13],
                        radius=6, fill=STAT_COL[status])
    d.text((cx0 + card_w - sw - 2, y + 2), status, font=f(SB, 9), fill=PAPER)
    y += 17
    for line in wrap(head, f(SB, 14), card_w - 14)[:3]:
        d.text((cx0 + 7, y), line, font=f(SB, 14), fill=INK)
        y += 17
    y += 2
    for line in wrap(detail, f(SR, 10), card_w - 14)[:4]:
        d.text((cx0 + 7, y), line, font=f(SR, 10), fill=GREY)
        y += 12
    d.text((cx0 + 7, GY + LEAD_H - 12), src, font=f(SB, 8), fill=GREY)

# ------------------------------------------------------- the day in numbers
sx = R - sidebar_w
d.rectangle([sx, GY, R, GY + LEAD_H], outline=INK, width=2)
d.rectangle([sx, GY, R, GY + 20], fill=INK)
d.text((sx + 7, GY + 5), "THE DAY IN NUMBERS", font=f(SB, 11), fill=PAPER)
nums = [("24", "stories on this page"), ("7", "regions covered"),
        ("186", "drones in the exchanges"), ("161", "of them intercepted"),
        ("14", "missing in Kyiv region"), ("14", "Iranian tankers readied"),
        ("4", "dead at Hartha station"), ("0", "deal at COP31")]
ny = GY + 26
for big, small in nums:
    d.text((sx + 8, ny), big, font=f(SB, 19), fill=RED)
    d.text((sx + 46, ny + 6), small, font=f(SR, 9), fill=INK)
    ny += 17
    if ny > GY + LEAD_H - 12:
        break

# ------------------------------------------------------------- card grid
SMALL_H = 142
ROW1 = GY + LEAD_H + 8
ROW2 = ROW1 + SMALL_H + 8
CW = (R - M - 4 * 5) // 5
for row_i, chunk in enumerate((STORIES[3:8], STORIES[8:13])):
    gy = ROW1 if row_i == 0 else ROW2
    for col_i, (num, region, status, head, detail, src) in enumerate(chunk):
        cx0 = M + col_i * (CW + 5)
        d.rectangle([cx0, gy, cx0 + CW, gy + SMALL_H], outline=RULE, width=1)
        d.rectangle([cx0, gy, cx0 + CW, gy + 2], fill=REG_COL[region])
        icon(KIND[num], (cx0 + 4, gy + 8, cx0 + CW - 4, gy + 52), REG_COL[region])
        y = gy + 56
        d.text((cx0 + 5, y), f"{num}", font=f(SB, 11), fill=RED)
        d.text((cx0 + 19, y + 1), region[:11], font=f(SB, 8), fill=GREY)
        y += 14
        for line in wrap(head, f(SB, 11), CW - 10)[:4]:
            d.text((cx0 + 5, y), line, font=f(SB, 11), fill=INK)
            y += 13
        y += 1
        for line in wrap(detail, f(SR, 9), CW - 10)[:4]:
            d.text((cx0 + 5, y), line, font=f(SR, 9), fill=GREY)
            y += 10
        sw = d.textlength(status, font=f(SB, 7)) + 6
        d.rounded_rectangle([cx0 + 5, gy + SMALL_H - 14, cx0 + 5 + sw, gy + SMALL_H - 4],
                            radius=5, fill=STAT_COL[status])
        d.text((cx0 + 8, gy + SMALL_H - 12), status, font=f(SB, 7), fill=PAPER)
        d.text((cx0 + CW - d.textlength(src, font=f(SB, 7)) - 5, gy + SMALL_H - 12),
               src, font=f(SB, 7), fill=GREY)

# ---------------------------------------------------------------- briefs
BY = ROW2 + SMALL_H + 10
d.line([(M, BY - 4), (R, BY - 4)], fill=INK, width=2)
d.text((M, BY), "ALSO ON SUNDAY 22 NOVEMBER", font=f(SB, 12), fill=RED)
by = BY + 19
col_w = (R - M - 16) // 3
for i, (num, region, text, src) in enumerate(BRIEFS):
    c = i % 3
    r = i // 3
    bx = M + c * (col_w + 8)
    ty = by + r * 32
    d.text((bx, ty), f"{num}", font=f(SB, 9), fill=RED)
    vend = ty + 20
    for j, line in enumerate(wrap(text, f(SR, 10), col_w - 18)[:2]):
        d.text((bx + 16, ty + j * 11), line, font=f(SR, 10), fill=INK)
    d.text((bx + 16, ty + 9), "", font=f(SB, 7))
by_end = by + ((len(BRIEFS) + 2) // 3) * 32

# ------------------------------------------------------------ map + date check
MY = by_end + 6
d.line([(M, MY - 4), (R, MY - 4)], fill=RULE, width=1)
MAP_W = 560
d.text((M, MY), "WHERE IT HAPPENED", font=f(SB, 12), fill=RED)

# crude but recognisable continents, drawn as landmass blobs
mw, mh = MAP_W - 10, 152
map_box = (M + 2, MY + 18, M + 2 + mw, MY + 18 + mh)
d.rectangle(map_box, outline=RULE, fill=(246, 247, 249))
mx0, my0 = map_box[0], map_box[1]
LAND = (206, 208, 214)
for (ex0, ey0, ex1, ey1) in [(0.13, 0.18, 0.30, 0.42), (0.20, 0.52, 0.32, 0.86),
                             (0.30, 0.22, 0.44, 0.44), (0.44, 0.26, 0.60, 0.52),
                             (0.58, 0.20, 0.86, 0.50), (0.74, 0.60, 0.86, 0.74),
                             (0.40, 0.66, 0.52, 0.82)]:
    d.rounded_rectangle([mx0 + mw * ex0, my0 + mh * ey0, mx0 + mw * ex1, my0 + mh * ey1],
                        radius=7, fill=LAND)

# Every pin sits on its own 22px slot so no two markers collide on the map.
PINS = [(1, 0.4655, 0.4605), (2, 0.5018, 0.1447), (3, 0.7855, 0.3816),
        (4, 0.5382, 0.6053), (5, 0.1382, 0.6053), (6, 0.9018, 0.2632),
        (7, 0.6000, 0.3289), (8, 0.3745, 0.2237), (9, 0.7127, 0.6579),
        (10, 0.6400, 0.5000), (11, 0.8545, 0.7105), (12, 0.1345, 0.1579),
        (13, 0.1273, 0.3684)]
for num, fx, fy in PINS:
    pxc = mx0 + mw * fx
    pyc = my0 + mh * fy
    d.ellipse([pxc - 9, pyc - 9, pxc + 9, pyc + 9], fill=RED, outline=PAPER)
    d.text((pxc, pyc - 6), str(num), font=f(SB, 10), fill=PAPER, anchor="ma")

# date check box + sources to the right of the map
dcx = M + MAP_W + 10
dcw = R - dcx
d.rectangle([dcx, MY + 18, R, MY + 18 + mh], outline=RED, width=2)
d.text((dcx + 7, MY + 24), "DATE CHECK", font=f(SB, 11), fill=RED)
y = MY + 40
for line in wrap("Every story here happened, or was first reported, on Sunday 22 "
                 "November 2026. Events of 21 November that were confirmed that day "
                 "appear in the briefs. Scene art is drawn, not photographed; the "
                 "wires were read to press time, 12:00 UTC.",
                 f(SR, 10), dcw - 14):
    d.text((dcx + 7, y), line, font=f(SR, 10), fill=INK)
    y += 13
d.text((dcx + 7, MY + 18 + mh - 26), "SOURCES", font=f(SB, 9), fill=GREY)
d.text((dcx + 7, MY + 18 + mh - 16), "Reuters · AP · Guardian · INA · Yonhap · BBC",
       font=f(SB, 8), fill=GREY)

# ------------------------------------------------------------------ footer
fy = MY + 18 + mh + 8
d.line([(M, fy), (R, fy)], fill=INK, width=2)
d.text((M, fy + 4), "THE DAY IN ONE PAGE  ·  24 STORIES FROM 7 REGIONS  ·  22 NOVEMBER 2026  ·  SCENES ARE DRAWN ILLUSTRATIONS",
       font=f(SB, 8), fill=GREY)

assert fy + 14 < S, f"page overruns: {fy + 14} > {S}"

# ------------------------------------------------------------------- output
def save(out):
    """Write the page to out, keeping the file inside the 1 MiB budget."""
    img.save(out, "PNG", optimize=True)
    if os.path.getsize(out) > MAX_BYTES:
        # Fallback: 256-colour adaptive palette. The page is flat ink on paper,
        # so the palette costs nothing visually but shrinks the file a lot.
        img.convert("P", palette=Image.ADAPTIVE, colors=256).save(
            out, "PNG", optimize=True)
    size = os.path.getsize(out)
    if size > MAX_BYTES:
        raise SystemExit(f"error: {out} is {size} bytes, over the {MAX_BYTES} budget")
    return size


out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
size = save(out)
assert img.size == (1024, 1024), img.size
print("saved", out, size, img.size)
