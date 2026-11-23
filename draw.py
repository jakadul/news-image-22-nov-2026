#!/usr/bin/env python3
"""Draw a 1024x1024 one-day news digest for SUNDAY 22 NOVEMBER 2026 (Pillow only)."""

import os

from PIL import Image, ImageDraw, ImageFont

FONT_DIR = os.environ.get("FONT_DIR", "/root/makefun-tr/practice-1119/fonts/")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

W = H = 1024
BG = (247, 245, 240)
INK = (24, 24, 24)
MUTED = (110, 108, 102)
LINE = (210, 206, 196)
RED = (178, 34, 34)
GREEN = (34, 120, 60)
ORANGE = (200, 110, 20)
CARD = (255, 253, 248)

STORIES = [
    (1, "EUROPE", "CONFIRMED", "COP31 ends with no deal as the EU rejects the final text",
     "Two weeks of talks closed in Antalya without an agreement; the climate fund was left without a figure.", "Reuters"),
    (2, "EUROPE", "CONFIRMED", "Fourteen missing after a drone strike on the Kyiv region",
     "Overnight attack damaged homes outside the capital; rescue work continued into the afternoon.", "AP"),
    (3, "MIDDLE EAST", "CLAIM", "Iran says it downed a US MQ-1 near the Strait of Hormuz",
     "Tehran offered talks on a two-day plan to reopen the waterway; Washington did not confirm the loss.", "IRNA"),
    (4, "AFRICA", "REPORTED", "Russian ship hit in Benghazi by a suspected Ukrainian drone",
     "Libyan officials said the vessel was struck while docking on its way back to Russia.", "Guardian"),
    (5, "AMERICAS", "CONFIRMED", "Mexico captures El Chapo Isidro",
     "Fausto Isidro Meza Flores, one of the FBI's ten most wanted, was taken in Sinaloa.", "Reuters"),
    (6, "ASIA", "CONFIRMED", "South Korea's education minister resigns over AI cheating",
     "The scandal engulfed university entrance exams.", "Yonhap"),
    (7, "MIDDLE EAST", "CONFIRMED", "UNIFIL begins handing its posts to the Lebanese army",
     "The mission started transferring positions in the south as its mandate ends.", "AP"),
    (8, "EUROPE", "CONFIRMED", "Leeds come from behind to beat Chelsea 4-1",
     "Emegha scored on his full debut for Chelsea; City drew 1-1 with Fulham.", "BBC"),
    (9, "MIDDLE EAST", "CONFIRMED", "Fire at Iraq's Hartha power station kills at least four",
     "Thirty-five were injured north of Basra; civil defence brought the blaze under control.", "INA"),
    (10, "MIDDLE EAST", "REPORTED", "Settler attacks on West Bank villages draw condemnation",
     "Dozens raided communities overnight, burning cars and homes.", "Guardian"),
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

REGIONS = [("Europe", 6), ("Middle East", 5), ("Asia", 5), ("Americas", 4),
           ("Africa", 2), ("Oceania", 1), ("World", 1)]

TIMELINE = [
    (0.04, "00:40", "Kyiv strike"),
    (0.27, "06:10", "Hormuz"),
    (0.50, "09:45", "COP31 objection"),
    (0.72, "11:20", "EU rejects"),
    (0.95, "12:00", "Press time"),
]

NUMBERS = [
    ("24", "stories on this page"),
    ("7", "regions covered"),
    ("186", "drones in the exchanges"),
    ("161", "of them intercepted"),
    ("14", "missing in Kyiv region"),
    ("14", "Iranian tankers readied"),
    ("4", "dead at Hartha station"),
    ("0", "deal at COP31"),
]

PINS = [(180, 250, "1"), (500, 235, "2"), (540, 330, "3"), (500, 430, "4"),
        (235, 500, "5"), (770, 330, "6"), (545, 400, "7"), (205, 300, "8"),
        (560, 380, "9"), (520, 415, "10"), (730, 450, "11"), (330, 370, "12"),
        (350, 470, "13")]


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def status_color(label):
    return {"CONFIRMED": GREEN, "CLAIM": RED, "REPORTED": ORANGE}[label]


def text(draw, xy, s, f, fill=INK, anchor="la"):
    draw.text(xy, s, font=f, fill=fill, anchor=anchor)


def pill(draw, xy, label, f, fg, outline):
    x, y = xy
    w = draw.textlength(label, font=f) + 18
    h = 20
    draw.rounded_rectangle([x, y, x + w, y + h], radius=9, outline=outline, width=2)
    text(draw, (x + w / 2, y + h / 2), label, f, fg, "mm")
    return w


def card(draw, num, region, status, head, detail, source, box, small=False):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=10, fill=CARD, outline=LINE, width=2)
    pad = 12
    f_num = font("LiberationSans-Bold.ttf", 13)
    f_lab = font("LiberationSans-Bold.ttf", 9)
    f_head = font("LiberationSans-Bold.ttf", 12 if small else 14)
    f_body = font("LiberationSans-Regular.ttf", 10 if small else 11)
    f_src = font("LiberationSans-Regular.ttf", 9)

    text(draw, (x0 + pad, y0 + pad), str(num), f_num, RED)
    text(draw, (x0 + pad + 24, y0 + pad + 2), region, f_lab, MUTED)
    pill(draw, (x1 - pad - draw.textlength(status, font=f_lab) - 14, y0 + pad - 1),
         status, f_lab, status_color(status), status_color(status))

    lines = wrap(draw, head, f_head, x1 - x0 - 2 * pad)
    ty = y0 + pad + 24
    for ln in lines:
        text(draw, (x0 + pad, ty), ln, f_head)
        ty += 16
    lines = wrap(draw, detail, f_body, x1 - x0 - 2 * pad)
    for ln in lines[:2]:
        text(draw, (x0 + pad, ty), ln, f_body, MUTED)
        ty += 14
    draw.line([x0 + pad, y1 - 22, x1 - pad, y1 - 22], fill=LINE, width=1)
    text(draw, (x0 + pad, y1 - 18), "Source: " + source, f_src, MUTED)


def wrap(draw, s, f, maxw):
    words = s.split()
    lines, cur = [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def icon(draw, kind, x, y):
    if kind == "globe":
        draw.ellipse([x, y, x + 22, y + 22], outline=INK, width=2)
        draw.line([x + 11, y, x + 11, y + 22], fill=INK, width=1)
        draw.line([x, y + 11, x + 22, y + 11], fill=INK, width=1)
    elif kind == "drone":
        draw.rectangle([x + 6, y + 8, x + 16, y + 14], outline=INK, width=2)
        draw.line([x, y, x + 8, y + 8], fill=INK, width=2)
        draw.line([x + 22, y, x + 14, y + 8], fill=INK, width=2)
    elif kind == "handshake":
        draw.line([x, y + 14, x + 8, y + 6], fill=INK, width=2)
        draw.line([x + 8, y + 6, x + 14, y + 12], fill=INK, width=2)
        draw.line([x + 14, y + 12, x + 22, y + 4], fill=INK, width=2)
    elif kind == "ship":
        draw.line([x, y + 14, x + 22, y + 14], fill=INK, width=2)
        draw.polygon([(x + 4, y + 14), (x + 18, y + 14), (x + 15, y + 20), (x + 7, y + 20)], outline=INK)
        draw.rectangle([x + 9, y + 4, x + 13, y + 14], outline=INK)
    elif kind == "ball":
        draw.ellipse([x, y, x + 20, y + 20], outline=INK, width=2)
        draw.line([x + 10, y, x + 10, y + 20], fill=INK, width=1)
    elif kind == "cap":
        draw.arc([x, y + 4, x + 22, y + 20], 180, 360, fill=INK, width=2)
        draw.line([x, y + 12, x + 22, y + 12], fill=INK, width=2)
    elif kind == "flame":
        draw.polygon([(x + 11, y), (x + 18, y + 12), (x + 11, y + 20), (x + 4, y + 12)], outline=INK)
    elif kind == "flag":
        draw.line([x + 4, y, x + 4, y + 20], fill=INK, width=2)
        draw.polygon([(x + 4, y + 2), (x + 20, y + 5), (x + 4, y + 10)], outline=INK)


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    f_date = font("LiberationSerif-Bold.ttf", 40)
    f_side = font("LiberationSans-Regular.ttf", 11)
    f_sec = font("LiberationSans-Bold.ttf", 14)
    f_small = font("LiberationSans-Regular.ttf", 10)
    f_foot = font("LiberationSans-Regular.ttf", 10)

    # Header
    text(draw, (40, 28), "SUNDAY 22 NOVEMBER 2026", f_date)
    sx = 40 + draw.textlength("SUNDAY 22 NOVEMBER 2026", font=f_date) + 24
    for i, s in enumerate(["24 STORIES · 7 REGIONS", "ALL FROM THIS ONE DAY", "PRESS TIME 12:00 UTC"]):
        text(draw, (sx, 40 + i * 17), s, f_side, MUTED)

    # Region pills
    px = 40
    for name, count in REGIONS:
        label = "%s %d" % (name, count)
        w = draw.textlength(label, font=f_small) + 20
        draw.rounded_rectangle([px, 92, px + w, 92 + 24], radius=12, outline=INK, width=2)
        text(draw, (px + w / 2, 92 + 12), label, f_small, INK, "mm")
        px += w + 10

    # Timeline
    ty = 138
    draw.line([40, ty, W - 40, ty], fill=INK, width=2)
    for frac, t, label in TIMELINE:
        x = 40 + frac * (W - 80)
        draw.ellipse([x - 5, ty - 5, x + 5, ty + 5], fill=RED)
        text(draw, (x, ty - 22), t, f_small, INK, "mm")
        text(draw, (x, ty + 10), label, f_small, MUTED, "mm")

    # Lead cards (3 columns)
    ly, lh = 172, 110
    gap = 12
    cw = (W - 80 - 2 * gap) // 3
    for i in range(3):
        n, region, status, head, detail, src = STORIES[i]
        card(draw, n, region, status, head, detail, src,
             (40 + i * (cw + gap), ly, 40 + i * (cw + gap) + cw, ly + lh))

    # Sidebar + two rows of five smaller cards
    side_w = 130
    grid_x0, grid_y = 40, 296
    grid_w = W - 80 - side_w - 12
    cw2 = (grid_w - 4 * gap) // 5
    ch2 = 118
    icon_kinds = ["globe", "drone", "handshake", "ship", "ball", "cap", "flame", "flag"]
    for i in range(3, 13):
        col = (i - 3) % 5
        row = (i - 3) // 5
        box = (grid_x0 + col * (cw2 + gap), grid_y + row * (ch2 + 10),
               grid_x0 + col * (cw2 + gap) + cw2, grid_y + row * (ch2 + 10) + ch2)
        card(draw, *STORIES[i], box, small=True)
        icon(draw, icon_kinds[i % len(icon_kinds)], box[0] + 12, box[1] + 30)

    # Sidebar
    sx0, sy0 = grid_x0 + grid_w + 12, grid_y
    draw.rounded_rectangle([sx0, sy0, W - 40, sy0 + 2 * ch2 + 10], radius=10,
                           fill=CARD, outline=LINE, width=2)
    text(draw, (sx0 + 12, sy0 + 12), "THE DAY IN NUMBERS", font("LiberationSans-Bold.ttf", 12), RED)
    ny = sy0 + 38
    for num, lab in NUMBERS:
        text(draw, (sx0 + 12, ny), num, font("LiberationSans-Bold.ttf", 18))
        text(draw, (sx0 + 46, ny + 6), lab, font("LiberationSans-Regular.ttf", 9), MUTED)
        ny += 24

    # Briefs (3 columns)
    by = grid_y + 2 * ch2 + 30
    text(draw, (40, by), "ALSO ON SUNDAY 22 NOVEMBER", f_sec)
    by += 26
    colw = (W - 80 - 2 * gap) // 3
    for idx, (n, region, txt, src) in enumerate(BRIEFS):
        col, row = idx // 4, idx % 4
        x = 40 + col * (colw + gap)
        y = by + row * 42
        text(draw, (x, y), str(n), font("LiberationSans-Bold.ttf", 11), RED)
        text(draw, (x + 24, y), region, font("LiberationSans-Bold.ttf", 8), MUTED)
        for j, ln in enumerate(wrap(draw, txt, f_small, colw - 30)[:2]):
            text(draw, (x + 24, y + 12 + j * 12), ln, f_small, INK)
        text(draw, (x + 24, y + 12 + 24), src, font("LiberationSans-Regular.ttf", 8), MUTED)

    # Map + date check
    my = by + 4 * 42 + 14
    text(draw, (40, my), "WHERE IT HAPPENED", f_sec)
    mx0, my0, mx1, my1 = 40, my + 24, 700, my + 226
    draw.rounded_rectangle([mx0, my0, mx1, my1], radius=10, fill=(238, 236, 228), outline=LINE, width=2)
    # schematic continents
    draw.ellipse([mx0 + 20, my0 + 30, mx0 + 130, my0 + 130], outline=(150, 146, 136), width=2)
    draw.ellipse([mx0 + 60, my0 + 150, mx0 + 150, my0 + 210], outline=(150, 146, 136), width=2)
    draw.ellipse([mx0 + 190, my0 + 20, mx0 + 300, my0 + 110], outline=(150, 146, 136), width=2)
    draw.ellipse([mx0 + 320, my0 + 60, mx0 + 430, my0 + 190], outline=(150, 146, 136), width=2)
    draw.ellipse([mx0 + 460, my0 + 30, mx0 + 600, my0 + 110], outline=(150, 146, 136), width=2)
    draw.ellipse([mx0 + 500, my0 + 140, mx0 + 600, my0 + 200], outline=(150, 146, 136), width=2)
    for px_, py_, label in PINS:
        cx, cy = mx0 + px_ * 0.55, my0 + py_ * 0.35
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED)
        text(draw, (cx, cy), label, font("LiberationSans-Bold.ttf", 9), (255, 255, 255), "mm")

    # Date check box
    dx0 = mx1 + 14
    draw.rounded_rectangle([dx0, my0, W - 40, my1], radius=10, fill=CARD, outline=RED, width=3)
    text(draw, (dx0 + 14, my0 + 14), "DATE CHECK", font("LiberationSans-Bold.ttf", 14), RED)
    text(draw, (dx0 + 14, my0 + 40), "Sunday, 22 November 2026",
         font("LiberationSans-Bold.ttf", 12))
    text(draw, (dx0 + 14, my0 + 62), "Week 47 · Day 326 of 366", f_small, MUTED)
    text(draw, (dx0 + 14, my0 + 84), "Sunrise London 07:32 UTC", f_small, MUTED)
    text(draw, (dx0 + 14, my0 + 102), "Sunset London 16:01 UTC", f_small, MUTED)
    text(draw, (dx0 + 14, my0 + 124), "Moon: waxing gibbous", f_small, MUTED)

    # Footer
    foot_y = H - 34
    draw.line([40, foot_y - 10, W - 40, foot_y - 10], fill=LINE, width=1)
    text(draw, (40, foot_y), "ONE DAY · 24 STORIES · 7 REGIONS · ALL FACTS AS REPORTED", f_foot, MUTED)
    text(draw, (W - 40, foot_y), "PAGE 01", f_foot, MUTED, "ra")

    img.save(OUT)
    print("saved %s (%dx%d)" % (OUT, img.width, img.height))
    px = img.load()
    last = 0
    for y in range(H):
        for x in range(0, W, 4):
            r, g, b = px[x, y]
            if r < 240 or g < 240 or b < 240:
                last = y
                break
    print("last non-white row: %d" % last)


if __name__ == "__main__":
    main()
