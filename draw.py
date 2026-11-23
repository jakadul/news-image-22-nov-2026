#!/usr/bin/env python3
"""Render a 1024x1024 newspaper front page to entry.png."""

import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
INK = "#111111"
RED = "#B3121B"
GREY = "#555555"
FONT_DIR = os.environ.get("FONT_DIR", "/root/makefun-tr/practice-1119/fonts/")

_font_cache = {}


def F(name, size):
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    return _font_cache[key]


def serif_bold(size):
    return F("LiberationSerif-Bold.ttf", size)


def serif(size):
    return F("LiberationSerif-Regular.ttf", size)


def sans_bold(size):
    return F("LiberationSans-Bold.ttf", size)


def sans(size):
    return F("LiberationSans-Regular.ttf", size)


img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)


def tw(text, font):
    return d.textlength(text, font=font)


def wrap(text, font, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if tw(trial, font) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(x, y, text, font, maxw, fill=INK, leading=None):
    if leading is None:
        leading = int(font.size * 1.35)
    for line in wrap(text, font, maxw):
        d.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def fit_line(text, font_name, size, maxw, floor=9):
    while size > floor:
        f = F(font_name, size)
        if tw(text, f) <= maxw:
            return f
        size -= 1
    return F(font_name, floor)


# ----------------------------------------------------------------- header
d.rectangle([0, 0, W - 1, 3], fill=RED)
d.rectangle([0, 6, W - 1, 7], fill=INK)

d.text((56, 24), "ONE DAY", font=serif_bold(92), fill=INK)
d.text((56, 126), "SUNDAY 22 NOVEMBER 2026", font=sans_bold(30), fill=INK)

meta_x = 968
meta_lines = ["24 STORIES", "7 REGIONS", "12:00 UTC PRESS TIME"]
my = 122
for line in meta_lines:
    f = sans_bold(15)
    d.text((meta_x - tw(line, f), my), line, font=f, fill=INK)
    my += 21
d.rectangle([meta_x - 132, 118, meta_x - 131, my - 6], fill=GREY)

# ----------------------------------------------------------------- hero
HY = 176
d.text((56, HY), "THE LEAD", font=sans_bold(13), fill=RED)
hero_y = HY + 26
for line in ["COP31 ENDS", "WITH NO DEAL", "AS THE EU WALKS"]:
    d.text((56, hero_y), line, font=serif_bold(44), fill=INK)
    hero_y += 50

hero_y += 14
hero_y = para(56, hero_y, "Two weeks of talks in Antalya closed without an agreement; "
                          "the climate fund left without a figure.",
              serif(19), 540, leading=26)
hero_y += 12
d.text((56, hero_y), "REUTERS", font=sans_bold(13), fill=RED)

# ------------------------------------------------------- drones (right)
DX = 640
dy = HY
d.text((DX, dy), "186 DRONES IN ONE NIGHT", font=sans_bold(13), fill=INK)
dy += 26

mark_y = dy + 10
step = 26
for i in range(12):
    cx = DX + 10 + i * step
    filled = i < 10
    body = RED if filled else RED
    outline = INK if filled else RED
    # rotors
    d.line([cx - 11, mark_y - 8, cx - 3, mark_y - 3], fill=outline, width=2)
    d.line([cx + 3, mark_y - 3, cx + 11, mark_y - 8], fill=outline, width=2)
    # body
    if filled:
        d.ellipse([cx - 7, mark_y - 3, cx + 7, mark_y + 4], fill=body)
    else:
        d.ellipse([cx - 7, mark_y - 3, cx + 7, mark_y + 4], outline=body, width=2)

dy = mark_y + 22
d.text((DX, dy), "161 SHOT DOWN", font=sans_bold(16), fill=INK)
dy += 24
d.text((DX, dy), "25 GOT THROUGH", font=sans_bold(16), fill=RED)
dy += 30
para(DX, dy, "Russia and Ukraine traded drones overnight; Ukraine's air force "
             "says 161 of 186 were intercepted.", sans(13), 320, fill=GREY, leading=18)

# ------------------------------------------------------------ stats strip
SY = 452
d.rectangle([56, SY, W - 56, SY + 1], fill=INK)
d.rectangle([56, SY + 86, W - 56, SY + 87], fill=INK)

cells = [("24", "STORIES ON THIS PAGE"), ("7", "REGIONS"),
         ("14", "MISSING IN KYIV"), ("4", "DEAD AT HATHA")]
cell_w = (W - 112) // 4
for i, (num, label) in enumerate(cells):
    cx = 56 + i * cell_w + (12 if i else 0)
    d.text((cx, SY + 12), num, font=sans_bold(44), fill=INK)
    d.text((cx, SY + 62), label, font=sans(13), fill=GREY)

# ---------------------------------------------------------------- columns
CY = 576
GUT = 24
COL_W = (W - 112 - 3 * GUT) // 4
col_x = [56 + i * (COL_W + GUT) for i in range(4)]

for i in range(1, 4):
    rx = col_x[i] - GUT // 2
    d.rectangle([rx, CY, rx, 872], fill="#DDDDDD")

stories = [
    ("MIDDLE EAST", "Iran says it downed a US MQ-1 over the Strait of Hormuz",
     "Tehran offered talks on a plan to reopen the waterway; Washington did not confirm the loss.",
     "IRNA"),
    ("AFRICA", "A Russian ship is hit by a drone in Benghazi",
     "Libyan officials said the vessel was struck while docking on its way home.",
     "GUARDIAN"),
    ("AMERICAS", "Mexico captures El Chapo Isidro",
     "Fausto Isidro Meza Flores, on the FBI's ten most wanted list, was taken in Sinaloa.",
     "REUTERS"),
    ("ASIA", "Seoul's education minister resigns over AI cheating",
     "The scandal reached the university entrance exams; universities begin a review.",
     "YONHAP"),
]

for i, (tag, head, summ, src) in enumerate(stories):
    x = col_x[i]
    y = CY
    d.text((x, y), tag, font=sans_bold(12), fill=RED)
    y += 22
    for line in wrap(head, serif_bold(21), COL_W):
        d.text((x, y), line, font=serif_bold(21), fill=INK)
        y += 26
    y += 8
    y = para(x, y, summ, sans(14), COL_W, leading=19)
    y += 10
    d.text((x, y), src, font=sans_bold(12), fill=INK)

# ------------------------------------------------------------- UTC timeline
TY = 788
d.rectangle([56, TY, W - 56, TY + 1], fill=INK)
d.text((56, TY + 10), "SUNDAY, IN UTC", font=sans_bold(13), fill=INK)
d.text((56 + tw("SUNDAY, IN UTC", sans_bold(13)) + 10, TY + 11),
       "Five moments that set the day", font=sans(12), fill=GREY)

axis_y = TY + 52
x0, x1 = 104, 934
d.rectangle([x0, axis_y, x1, axis_y + 1], fill="#BBBBBB")

marks = [
    (0.00, "00:40", "KYIV STRIKE", "above"),
    (0.27, "06:10", "HORMUZ CLAIM", "below"),
    (0.55, "09:45", "COP31 OBJECTION", "above"),
    (0.78, "11:20", "EU REJECTS", "below"),
    (0.97, "12:00", "PRESS TIME", "above"),
]
for frac, tm, label, side in marks:
    mx = int(x0 + frac * (x1 - x0))
    d.ellipse([mx - 6, axis_y - 5, mx + 6, axis_y + 7], fill=RED)
    d.ellipse([mx - 2, axis_y - 1, mx + 2, axis_y + 3], fill="white")
    tf = sans_bold(15)
    lf = sans_bold(11)
    ty = axis_y - 30 if side == "above" else axis_y + 14
    d.text((mx - tw(tm, tf) // 2, ty), tm, font=tf, fill=INK)
    d.text((mx - tw(label, lf) // 2, ty + (18 if side == "above" else 16)), label, font=lf, fill=RED)

# ------------------------------------------------------------- bottom band
BY = 890
d.rectangle([56, BY, W - 56, BY + 1], fill=INK)
d.text((56, BY + 10), "ALSO ON SUNDAY", font=sans_bold(13), fill=INK)

briefs = [
    ("UNIFIL hands its posts to the Lebanese army", "AP"),
    ("Leeds beat Chelsea 4-1; Emegha scored", "BBC"),
    ("Settler raids burn cars in the West Bank", "GUARDIAN"),
    ("IMF holds global growth at 3.3%", "IMF"),
    ("Las Vegas GP decided on the final lap", "F1"),
    ("Hong Kong votes in its district election", "RTHK"),
]

BRIEF_W = 300
b_x = [56, 372]
b_y = BY + 32
row_h = 26
for idx, (text, src) in enumerate(briefs):
    col = idx // 3
    row = idx % 3
    x = b_x[col]
    y = b_y + row * row_h
    size = 14
    full = text + " \u00b7 " + src
    font = sans(size)
    while size > 8 and tw(full, font) > BRIEF_W:
        size -= 1
        font = sans(size)
    d.text((x, y), text, font=font, fill=INK)
    sx = x + tw(text, font)
    d.text((sx, y), " \u00b7 ", font=font, fill=GREY)
    sx += tw(" \u00b7 ", font)
    d.text((sx, y), src, font=sans_bold(size), fill=INK)

# ------------------------------------------------------------- date check
BX, BYY, BW, BH = 700, 890, 268, 128
d.rectangle([BX, BYY, BX + BW, BYY + BH], outline=RED, width=2)
d.text((BX + 14, BYY + 12), "DATE CHECK", font=sans_bold(13), fill=RED)
lines = ["Sunday, 22 November 2026", "Week 47 \u00b7 Day 326 of 366",
         "Sunrise London 07:32 UTC", "Sunset London 16:01 UTC"]
ly = BYY + 38
for line in lines:
    d.text((BX + 14, ly), line, font=sans(13), fill=INK)
    ly += 20

# ------------------------------------------------------------------ footer
d.rectangle([56, 1016, W - 56, 1016], fill=GREY)
f = sans_bold(11)
d.text((56, 1002), "ONE DAY \u00b7 24 STORIES \u00b7 7 REGIONS \u00b7 ALL FACTS AS REPORTED",
       font=f, fill=GREY)
d.text((W - 56 - tw("PAGE 01", f), 1002), "PAGE 01", font=f, fill=GREY)

# ------------------------------------------------------------------ output
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
img.save(out)

px = img.load()
last = 0
for y in range(H - 1, -1, -1):
    for x in range(W):
        if px[x, y] != (255, 255, 255):
            last = y
            break
    else:
        continue
    break

print("saved")
print(last)
