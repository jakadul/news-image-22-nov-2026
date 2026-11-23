#!/usr/bin/env python3
"""Digest-page renderer for the 22 Nov 2026 news image.

Everything on the sheet is drawn with Pillow from flat vector primitives:
no bitmaps, no photography. The layout is a dense one-page news digest --
a masthead, seven region chips, a UTC timeline, thirteen lead/grid cards,
an "in numbers" side panel, eleven short briefs, a world map with numbered
pins, a date-check / sources block, and a footer strip.

Fonts are pulled from FONT_DIR (default below). The rendered PNG is always
1024x1024 and is kept at or under 1 MiB.

Usage:
    python3 draw.py [output.png]
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------- config
FONT_DIR = os.environ.get("FONT_DIR", "/root/makefun-tr/practice-1119/fonts/")
SIZE = 1024                 # canvas is a perfect square
BYTES_CAP = 1024 * 1024     # hard file budget
OUT_DEFAULT = "entry.png"
M = 18                      # outer margin

# Palette: paper, ink, and the small set of signal colours.
PAPER   = (255, 255, 255)
INK     = (18, 18, 20)
GREY    = (110, 110, 116)
HAIR    = (208, 208, 212)
RED     = (168, 24, 32)
BLUE    = (26, 74, 140)
GREEN   = (24, 110, 70)
AMBER   = (168, 112, 16)
TEAL    = (18, 104, 110)
LAND    = (206, 208, 214)
MAPBG   = (246, 247, 249)

F_BOLD   = "LiberationSans-Bold.ttf"
F_NARROW = "LiberationSansNarrow-Bold.ttf"
F_REG    = "LiberationSans-Regular.ttf"
F_SERIF  = "LiberationSerif-Bold.ttf"

REGION_TINT = {
    "EUROPE": BLUE, "MIDDLE EAST": RED, "ASIA": TEAL, "AFRICA": AMBER,
    "AMERICAS": GREEN, "OCEANIA": BLUE, "WORLD": GREY,
}
STATUS_TINT = {"CONFIRMED": GREEN, "CLAIM": AMBER, "REPORTED": RED, "PENDING": BLUE}

# ---------------------------------------------------------------------- content
# (num, region, status, headline, one-line detail, source)
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

# (num, region, one-liner, source)
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

TIMELINE = [("00:40", "Kyiv strike"), ("06:10", "Hormuz"),
            ("09:45", "COP31 objection"), ("11:20", "EU rejects"), ("12:00", "Press time")]

NUMBERS = [("24", "stories on this page"), ("7", "regions covered"),
           ("186", "drones in the exchanges"), ("161", "of them intercepted"),
           ("14", "missing in Kyiv region"), ("14", "Iranian tankers readied"),
           ("4", "dead at Hartha station"), ("0", "deal at COP31")]

# (num, fx, fy) -- fractional pin positions on the map, 13 of them.
PINS = [(1, 0.4655, 0.4605), (2, 0.5018, 0.1447), (3, 0.7855, 0.3816),
        (4, 0.5382, 0.6053), (5, 0.1382, 0.6053), (6, 0.9018, 0.2632),
        (7, 0.6000, 0.3289), (8, 0.3745, 0.2237), (9, 0.7127, 0.6579),
        (10, 0.6400, 0.5000), (11, 0.8545, 0.7105), (12, 0.1345, 0.1579),
        (13, 0.1273, 0.3684)]

# Landmass blobs as fractional (x0, y0, x1, y1) boxes over the map rect.
LANDBOX = [(0.13, 0.18, 0.30, 0.42), (0.20, 0.52, 0.32, 0.86),
           (0.30, 0.22, 0.44, 0.44), (0.44, 0.26, 0.60, 0.52),
           (0.58, 0.20, 0.86, 0.50), (0.74, 0.60, 0.86, 0.74),
           (0.40, 0.66, 0.52, 0.82)]

# One small glyph per lead story, keyed by its number.
GLYPH = {1: "dome", 2: "drone", 3: "drone", 4: "ship", 5: "map", 6: "cap",
         7: "map", 8: "ball", 9: "flame", 10: "flame", 11: "vote",
         12: "map", 13: "cap"}

REGION_COUNT = {}
for _, region, *_ in STORIES:
    REGION_COUNT[region] = REGION_COUNT.get(region, 0) + 1
for _, region, *_ in BRIEFS:
    REGION_COUNT[region] = REGION_COUNT.get(region, 0) + 1

MIDDLE_NOTE = ("Every story here happened, or was first reported, on Sunday 22 "
               "November 2026. Events of 21 November that were confirmed that day "
               "appear in the briefs. Scene art is drawn, not photographed; the "
               "wires were read to press time, 12:00 UTC.")
SOURCE_LINE = "Reuters \u00b7 AP \u00b7 Guardian \u00b7 INA \u00b7 Yonhap \u00b7 BBC"
FOOTER_LINE = ("THE DAY IN ONE PAGE  \u00b7  24 STORIES FROM 7 REGIONS  \u00b7  "
               "22 NOVEMBER 2026  \u00b7  SCENES ARE DRAWN ILLUSTRATIONS")


def face(name, size):
    """Load a TrueType face from FONT_DIR at the requested size."""
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


class Page:
    """A 1024x1024 canvas plus the drawing helpers the layout is built from."""

    def __init__(self):
        self.im = Image.new("RGB", (SIZE, SIZE), PAPER)
        self.d = ImageDraw.Draw(self.im)
        self.bottom = M   # running max of the lowest y any content reaches

    # -- text ---------------------------------------------------------------
    def wrap(self, text, font, width):
        """Word-wrap text to a pixel width, returning a list of lines."""
        lines, cur = [], ""
        for word in text.split():
            probe = (cur + " " + word).strip()
            if self.d.textlength(probe, font=font) <= width:
                cur = probe
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def paragraph(self, x, y, text, font, width, leading, max_lines=None, fill=INK):
        """Draw wrapped text; return the y just below the last line."""
        rows = self.wrap(text, font, width)
        if max_lines:
            rows = rows[:max_lines]
        for row in rows:
            self.d.text((x, y), row, font=font, fill=fill)
            y += leading
        return y

    def rule(self, y, x0=None, x1=None, color=HAIR, weight=1):
        x0 = M if x0 is None else x0
        x1 = SIZE - M if x1 is None else x1
        self.d.line([(x0, y), (x1, y)], fill=color, width=weight)
        self.bottom = max(self.bottom, y + weight)

    # -- glyphs -------------------------------------------------------------
    def glyph(self, kind, box, color):
        d = self.d
        x0, y0, x1, y1 = box
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if kind == "dome":
            d.pieslice([cx - 22, cy - 26, cx + 22, cy + 18], 180, 360, fill=color)
            d.rectangle([cx - 24, cy - 4, cx + 24, cy + 16], fill=color)
            d.rectangle([cx - 30, cy + 16, cx + 30, cy + 22], fill=INK)
        elif kind == "drone":
            d.rectangle([cx - 20, cy - 3, cx + 20, cy + 4], fill=color)
            d.rectangle([cx - 6, cy - 10, cx + 6, cy + 10], fill=color)
            for side in (-1, 1):
                d.line([(cx + side * 20, cy - 12), (cx + side * 20, cy + 12)],
                       fill=color, width=3)
        elif kind == "ship":
            d.polygon([(cx - 26, cy + 6), (cx + 26, cy + 6),
                       (cx + 16, cy + 20), (cx - 16, cy + 20)], fill=color)
            d.rectangle([cx - 12, cy - 14, cx + 12, cy + 4], fill=color)
        elif kind == "map":
            for i in range(3):
                d.rectangle([cx - 24, cy - 14 + i * 10, cx + 24, cy - 10 + i * 10],
                            fill=color)
        elif kind == "cap":
            d.pieslice([cx - 18, cy - 20, cx + 18, cy + 12], 180, 360, fill=color)
            d.rectangle([cx - 22, cy - 6, cx + 22, cy + 8], fill=color)
        elif kind == "book":
            d.rectangle([cx - 18, cy - 14, cx + 18, cy + 16], outline=color, width=3)
            d.line([(cx, cy - 14), (cx, cy + 16)], fill=color, width=2)
        elif kind == "ball":
            d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], outline=color, width=3)
            d.line([(cx - 15, cy), (cx + 15, cy)], fill=color, width=2)
        elif kind == "flame":
            d.polygon([(cx, cy - 20), (cx + 14, cy + 6), (cx + 6, cy + 16),
                       (cx - 6, cy + 16), (cx - 14, cy + 6)], fill=color)
        elif kind == "vote":
            d.rectangle([cx - 20, cy - 6, cx + 20, cy + 18], fill=color)
            d.polygon([(cx - 2, cy - 2), (cx + 4, cy + 4), (cx + 14, cy - 10),
                       (cx + 8, cy - 16)], fill=PAPER)
        else:
            d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=color)

    # -- sections -----------------------------------------------------------
    def masthead(self):
        d = self.d
        d.text((M, 12), "SUNDAY 22 NOVEMBER 2026", font=face(F_SERIF, 44), fill=INK)
        bx = M + d.textlength("SUNDAY 22 NOVEMBER 2026", font=face(F_SERIF, 44)) + 16
        d.text((bx, 22), "24 STORIES \u00b7 7 REGIONS", font=face(F_BOLD, 15), fill=RED)
        d.text((bx, 42), "ALL FROM THIS ONE DAY", font=face(F_BOLD, 15), fill=GREY)
        d.text((bx, 60), "PRESS TIME 12:00 UTC", font=face(F_BOLD, 12), fill=GREY)
        self.bottom = max(self.bottom, 88)

    def region_chips(self):
        d = self.d
        x, y = M, 64
        for region in sorted(REGION_COUNT):
            label = f"{region.title()} {REGION_COUNT[region]}"
            w = d.textlength(label, font=face(F_BOLD, 11)) + 12
            d.rounded_rectangle([x, y, x + w, y + 17], radius=8,
                                fill=REGION_TINT[region])
            d.text((x + 6, y + 3), label, font=face(F_BOLD, 11), fill=PAPER)
            x += w + 5
        self.bottom = max(self.bottom, y + 17)

    def timeline(self):
        d = self.d
        d.text((M, 94), "UTC", font=face(F_BOLD, 10), fill=GREY)
        left, right, y = M + 40, SIZE - M - 40, 112
        d.line([(left, y), (right, y)], fill=HAIR, width=2)
        for i, (stamp, what) in enumerate(TIMELINE):
            x = left + (right - left) * i / (len(TIMELINE) - 1)
            hot = i >= 3
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=RED if hot else BLUE)
            d.text((x, y - 16), stamp, font=face(F_BOLD, 9),
                   fill=RED if hot else GREY, anchor="ma")
            d.text((x, y + 7), what, font=face(F_BOLD, 9), fill=INK, anchor="ma")
        self.bottom = max(self.bottom, y + 18)

    def status_chip(self, x, y, status, size=9):
        d = self.d
        w = d.textlength(status, font=face(F_BOLD, size)) + 8
        d.rounded_rectangle([x - w, y, x, y + size + 4], radius=5,
                            fill=STATUS_TINT[status])
        d.text((x - w + 4, y + 2), status, font=face(F_BOLD, size), fill=PAPER)

    def lead_cards(self, gy, height, side_w):
        d = self.d
        gap = 8
        card_w = (SIZE - 2 * M - side_w - 12 - gap * 2) // 3
        for idx, (num, region, status, head, detail, src) in enumerate(STORIES[:3]):
            x = M + idx * (card_w + gap)
            d.rectangle([x, gy, x + card_w, gy + height], outline=HAIR, width=1)
            d.rectangle([x, gy, x + card_w, gy + 2], fill=REGION_TINT[region])
            self.glyph(GLYPH[num], (x + 6, gy + 10, x + card_w - 6, gy + 74),
                       REGION_TINT[region])
            y = gy + 80
            d.text((x + 7, y), str(num), font=face(F_BOLD, 13), fill=RED)
            d.text((x + 24, y), region, font=face(F_BOLD, 10), fill=GREY)
            self.status_chip(x + card_w - 6, y, status, 9)
            y += 17
            y = self.paragraph(x + 7, y, head, face(F_BOLD, 14), card_w - 14,
                               17, max_lines=3, fill=INK)
            y += 2
            y = self.paragraph(x + 7, y, detail, face(F_REG, 10), card_w - 14,
                               12, max_lines=4, fill=GREY)
            d.text((x + 7, gy + height - 12), src, font=face(F_BOLD, 8), fill=GREY)
        self.bottom = max(self.bottom, gy + height)

    def numbers_panel(self, gy, height, side_w):
        d = self.d
        x = SIZE - M - side_w
        d.rectangle([x, gy, x + side_w, gy + height], outline=INK, width=2)
        d.rectangle([x, gy, x + side_w, gy + 20], fill=INK)
        d.text((x + 7, gy + 5), "THE DAY IN NUMBERS", font=face(F_BOLD, 11), fill=PAPER)
        y = gy + 26
        for big, small in NUMBERS:
            d.text((x + 8, y), big, font=face(F_BOLD, 19), fill=RED)
            d.text((x + 46, y + 6), small, font=face(F_REG, 9), fill=INK)
            y += 17
            if y > gy + height - 12:
                break
        self.bottom = max(self.bottom, gy + height)

    def story_grid(self, top, small_h):
        d = self.d
        gap = 5
        cw = (SIZE - 2 * M - 4 * gap) // 5
        chunks = (STORIES[3:8], STORIES[8:13])
        for row_i, chunk in enumerate(chunks):
            gy = top + row_i * (small_h + gap)
            for col_i, (num, region, status, head, detail, src) in enumerate(chunk):
                x = M + col_i * (cw + gap)
                d.rectangle([x, gy, x + cw, gy + small_h], outline=HAIR, width=1)
                d.rectangle([x, gy, x + cw, gy + 2], fill=REGION_TINT[region])
                self.glyph(GLYPH[num], (x + 4, gy + 8, x + cw - 4, gy + 52),
                           REGION_TINT[region])
                y = gy + 56
                d.text((x + 5, y), str(num), font=face(F_BOLD, 11), fill=RED)
                d.text((x + 19, y + 1), region[:11], font=face(F_BOLD, 8), fill=GREY)
                y += 14
                y = self.paragraph(x + 5, y, head, face(F_BOLD, 11), cw - 10,
                                   13, max_lines=4, fill=INK)
                y += 1
                y = self.paragraph(x + 5, y, detail, face(F_REG, 9), cw - 10,
                                   10, max_lines=4, fill=GREY)
                sw = d.textlength(status, font=face(F_BOLD, 7)) + 6
                d.rounded_rectangle([x + 5, gy + small_h - 14, x + 5 + sw,
                                     gy + small_h - 4], radius=5,
                                    fill=STATUS_TINT[status])
                d.text((x + 8, gy + small_h - 12), status, font=face(F_BOLD, 7), fill=PAPER)
                d.text((x + cw - d.textlength(src, font=face(F_BOLD, 7)) - 5,
                        gy + small_h - 12), src, font=face(F_BOLD, 7), fill=GREY)
        rows = len(chunks)
        self.bottom = max(self.bottom, top + rows * small_h + (rows - 1) * gap)

    def briefs(self, top):
        d = self.d
        self.rule(top - 4, color=INK, weight=2)
        d.text((M, top), "ALSO ON SUNDAY 22 NOVEMBER", font=face(F_BOLD, 12), fill=RED)
        by = top + 19
        col_w = (SIZE - 2 * M - 2 * 8) // 3
        rows = (len(BRIEFS) + 2) // 3
        for i, (num, region, text, src) in enumerate(BRIEFS):
            c, r = i % 3, i // 3
            bx = M + c * (col_w + 8)
            ty = by + r * 32
            d.text((bx, ty), str(num), font=face(F_BOLD, 9), fill=RED)
            self.paragraph(bx + 16, ty, text, face(F_REG, 10), col_w - 18,
                           11, max_lines=2, fill=INK)
        self.bottom = max(self.bottom, by + rows * 32)
        return by + rows * 32

    def map_panel(self, top):
        d = self.d
        self.rule(top - 4, color=HAIR, weight=1)
        d.text((M, top), "WHERE IT HAPPENED", font=face(F_BOLD, 12), fill=RED)
        mw, mh = 550, 152
        x0, y0 = M + 2, top + 18
        d.rectangle([x0, y0, x0 + mw, y0 + mh], outline=HAIR, fill=MAPBG)
        for (ex0, ey0, ex1, ey1) in LANDBOX:
            d.rounded_rectangle([x0 + mw * ex0, y0 + mh * ey0,
                                 x0 + mw * ex1, y0 + mh * ey1], radius=7, fill=LAND)
        for num, fx, fy in PINS:
            px, py = x0 + mw * fx, y0 + mh * fy
            d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED, outline=PAPER)
            d.text((px, py - 6), str(num), font=face(F_BOLD, 10), fill=PAPER, anchor="ma")
        self.bottom = max(self.bottom, y0 + mh)
        return x0, y0, mw, mh

    def date_check(self, x0, y0, mh):
        d = self.d
        left = x0 + 550 + 10
        right = SIZE - M
        width = right - left
        d.rectangle([left, y0, right, y0 + mh], outline=RED, width=2)
        d.text((left + 7, y0 + 6), "DATE CHECK", font=face(F_BOLD, 11), fill=RED)
        y = self.paragraph(left + 7, y0 + 24, MIDDLE_NOTE, face(F_REG, 10),
                           width - 14, 13, fill=INK)
        d.text((left + 7, y0 + mh - 26), "SOURCES", font=face(F_BOLD, 9), fill=GREY)
        d.text((left + 7, y0 + mh - 16), SOURCE_LINE, font=face(F_BOLD, 8), fill=GREY)

    def footer(self, y):
        d = self.d
        self.rule(y, color=INK, weight=2)
        d.text((M, y + 4), FOOTER_LINE, font=face(F_BOLD, 8), fill=GREY)
        self.bottom = max(self.bottom, y + 12)


def render():
    page = Page()
    page.masthead()
    page.region_chips()
    page.rule(88, color=INK, weight=2)
    page.timeline()
    page.rule(138, color=HAIR, weight=1)

    gy, lead_h, side_w = 146, 192, 210
    page.lead_cards(gy, lead_h, side_w)
    page.numbers_panel(gy, lead_h, side_w)

    grid_top = gy + lead_h + 8
    page.story_grid(grid_top, small_h=142)

    briefs_top = grid_top + 2 * 142 + 8 + 12
    by_end = page.briefs(briefs_top)

    map_top = by_end + 8
    x0, y0, mw, mh = page.map_panel(map_top)
    page.date_check(x0, y0, mh)

    page.footer(y0 + mh + 8)
    return page


def measure_bottom(im):
    """Find the last pixel row that differs from the paper colour."""
    px = im.convert("RGB").load()
    for y in range(SIZE - 1, -1, -1):
        for x in range(0, SIZE, 4):
            if px[x, y] != PAPER:
                return y
    return 0


def save(im, path):
    """Write the page, staying inside the byte budget."""
    im.save(path, "PNG", optimize=True)
    if os.path.getsize(path) > BYTES_CAP:
        im.convert("P", palette=Image.ADAPTIVE, colors=256).save(path, "PNG", optimize=True)
    size = os.path.getsize(path)
    if size > BYTES_CAP:
        raise SystemExit(f"error: {path} is {size} bytes, over the {BYTES_CAP} cap")
    return size


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else OUT_DEFAULT
    page = render()
    assert page.im.size == (SIZE, SIZE), page.im.size
    size = save(page.im, out)
    bottom = measure_bottom(page.im)
    print(f"saved {out} {size} bytes {page.im.size} bottom_row={bottom}")


if __name__ == "__main__":
    main()
