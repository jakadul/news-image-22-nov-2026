#!/usr/bin/env python3
"""One-day news poster, 1024x1024, Pillow only.

Vertical budget (px):
    0   - 130   navy header band
    130 - 196   stats strip (6 cells, thin rules)
    196 - 226   region pill bar (7 pills)
    226 - 264   navy timeline bar (6 marks)
    264 - 274   gutter
    274 - 470   three lead cards (74px illustration panel each)
    470 - 482   gutter
    482 - 740   4x3 grid of twelve small cards + tall numbers panel
    740 - 752   gutter
    752 - 950   map panel (300 wide) + date-check box
    950 - 962   gutter
    962 - 984   navy footer band (22px)
    984 - 1024  cream margin
"""

import os
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
W = H = 1024
M = 20                              # outer margin
CREAM = (250, 246, 236)             # #FAF6EC ground
NAVY = (18, 32, 58)                 # #12203A panels
RED = (200, 16, 46)                 # #C8102E accents
WHITE = (255, 255, 255)
INK = (34, 34, 34)                  # body text
GREY = (86, 86, 86)                 # was (140,140,140) -> darkened for 600px legibility
DUSTY = (226, 178, 194)             # dusty pink
PALE_BLUE = (176, 198, 222)
RULE = (214, 206, 192)
PINK_BOX = (250, 228, 232)

REGIONS = {
    "EUROPE": (46, 109, 180),
    "MIDDLE EAST": (200, 16, 46),
    "ASIA": (30, 138, 95),
    "AFRICA": (224, 138, 22),
    "AMERICAS": (123, 75, 168),
    "OCEANIA": (18, 140, 140),
    "WORLD": (58, 58, 58),
}
BADGES = {"CONFIRMED": (30, 138, 95), "REPORTED": (224, 138, 22),
          "CLAIM": (200, 16, 46), "PENDING": (110, 110, 110)}

FONT_DIR = os.environ.get("FONT_DIR", "/root/makefun-tr/practice-1119/fonts/")
_cache = {}


def F(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    return _cache[key]


def serif(size):
    return F("LiberationSerif-Bold.ttf", size)


def bold(size):
    return F("LiberationSans-Bold.ttf", size)


def body(size):
    return F("LiberationSans-Regular.ttf", size)


# ---------------------------------------------------------------- helpers
def wrap(text, font, maxw):
    """Greedy word wrap measured with textlength. Returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if font.getlength(trial) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def wrap_n(text, font, maxw, n):
    """Wrap to at most n lines; shrink the font size until it fits."""
    size = font.size
    while size > 4:
        f = font.__class__(os.path.join(FONT_DIR, font.path.split(os.sep)[-1]), size) \
            if False else _font_like(font, size)
        lines = wrap(text, f, maxw)
        if len(lines) <= n:
            return lines, f
        size -= 1
    return lines, f


def _font_like(font, size):
    # recover the family file from the cached name
    for (name, sz), f in _cache.items():
        if f is font:
            return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    return font


def fit(text, font, maxw):
    """Shrink one line until it fits maxw."""
    size = font.size
    f = font
    while f.getlength(text) > maxw and size > 5:
        size -= 1
        f = _font_like(font, size)
    return text, f


def pill(d, x, y, label, fill, fnt, fg=WHITE, padx=6, h=None):
    """Draw a filled rounded label centred on its own box. Returns width."""
    tw = fnt.getlength(label)
    h = h or fnt.size + 6
    w = tw + padx * 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=h / 2, fill=fill)
    ty = y + (h - fnt.size) / 2 - fnt.size * 0.18
    d.text((x + padx, ty), label, font=fnt, fill=fg)
    return w


def badge(d, x, y, kind, fnt):
    """Status badge: coloured rounded box, white caps text. Returns (w,h)."""
    label = kind
    tw = fnt.getlength(label)
    h = fnt.size + 5
    w = tw + 10
    d.rounded_rectangle([x, y, x + w, y + h], radius=2,
                        fill=BADGES.get(kind, GREY))
    d.text((x + 5, y + (h - fnt.size) / 2 - fnt.size * 0.2), label,
           font=fnt, fill=WHITE)
    return w, h


def rule(d, x0, y, x1, col=RULE):
    d.line([x0, y, x1, y], fill=col, width=1)


# ---------------------------------------------------------------- artwork
def scene_skyline(d, box):
    """Flat navy city skyline, lit windows, drone dots."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(12, 23, 44))
    # moon
    d.ellipse([x0 + w - 26, y0 + 8, x0 + w - 14, y0 + 20], fill=(232, 214, 150))
    towers = [(0.02, 0.62, 0.11), (0.13, 0.40, 0.08), (0.21, 0.55, 0.10),
              (0.31, 0.30, 0.07), (0.38, 0.48, 0.12), (0.50, 0.60, 0.09),
              (0.59, 0.38, 0.08), (0.67, 0.52, 0.11), (0.78, 0.34, 0.07),
              (0.85, 0.58, 0.12)]
    for fx, fh, fw in towers:
        bx0 = x0 + fx * w
        bx1 = bx0 + fw * w
        by0 = y1 - fh * h
        d.rectangle([bx0, by0, bx1, y1], fill=(28, 44, 72))
        # windows
        cols = max(2, int(fw * w / 7))
        rows = max(2, int((y1 - by0) / 8))
        for c in range(cols):
            for r in range(rows):
                if (c * 3 + r * 5) % 4 == 0:
                    wx = bx0 + 3 + c * ((bx1 - bx0 - 4) / cols)
                    wy = by0 + 4 + r * ((y1 - by0 - 6) / rows)
                    d.rectangle([wx, wy, wx + 2, wy + 2], fill=(246, 206, 120))
    # drone dots with thin trails
    for dx, dy in [(0.18, 0.16), (0.42, 0.10), (0.62, 0.20), (0.80, 0.12)]:
        px, py = x0 + dx * w, y0 + dy * h
        d.line([px - 8, py + 4, px, py], fill=(200, 16, 46), width=1)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(230, 70, 90))
    d.line([x0, y1, x1, y1], fill=(60, 82, 118), width=1)


def scene_drones(d, box):
    """Drones with rotors over damaged buildings."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(12, 23, 44))
    # damaged blocks
    for fx, fw, fh in [(0.04, 0.20, 0.34), (0.30, 0.16, 0.46), (0.52, 0.24, 0.28)]:
        bx0 = x0 + fx * w
        bx1 = bx0 + fw * w
        by0 = y1 - fh * h
        d.rectangle([bx0, by0, bx1, y1], fill=(30, 46, 74))
        d.polygon([(bx0, by0), (bx0 + fw * w * 0.4, by0 + 6),
                   (bx1, by0 - 2), (bx1, by0 + 3), (bx0, by0 + 5)],
                  fill=(12, 23, 44))
        for c in range(2):
            wx = bx0 + 5 + c * 11
            d.rectangle([wx, by0 + 10, wx + 4, by0 + 14], fill=(246, 176, 110))
    # smoke
    for sx, sy, r in [(0.44, 0.30, 9), (0.48, 0.22, 7), (0.52, 0.16, 5)]:
        d.ellipse([x0 + sx * w - r, y0 + sy * h - r,
                   x0 + sx * w + r, y0 + sy * h + r], fill=(58, 72, 98))
    # three drones
    for dx, dy in [(0.20, 0.22), (0.56, 0.34), (0.78, 0.18)]:
        cx, cy = x0 + dx * w, y0 + dy * h
        d.rectangle([cx - 5, cy - 2, cx + 5, cy + 2], fill=(214, 224, 236))
        d.line([cx - 12, cy - 6, cx - 3, cy - 2], fill=(176, 198, 222), width=1)
        d.line([cx + 3, cy - 2, cx + 12, cy - 6], fill=(176, 198, 222), width=1)
        d.ellipse([cx - 15, cy - 8, cx - 9, cy - 4], fill=(200, 16, 46))
        d.ellipse([cx + 9, cy - 8, cx + 15, cy - 4], fill=(200, 16, 46))
        d.line([cx, cy + 2, cx, cy + 7], fill=(200, 16, 46), width=1)
    d.line([x0, y1, x1, y1], fill=(60, 82, 118), width=1)


def scene_radar(d, box):
    """Concentric radar arcs with a red sweep line."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(12, 23, 44))
    cx, cy = x0 + w * 0.5, y1 - 4
    for r in (14, 26, 38, 50):
        d.arc([cx - r, cy - r, cx + r, cy + r], 180, 360,
              fill=(52, 82, 122), width=1)
    for ang in (205, 250, 295, 340):
        import math
        a = math.radians(ang)
        d.line([cx, cy, cx + 50 * math.cos(a), cy + 50 * math.sin(a)],
               fill=(38, 60, 96), width=1)
    import math
    a = math.radians(232)
    d.line([cx, cy, cx + 52 * math.cos(a), cy + 52 * math.sin(a)],
           fill=(200, 16, 46), width=2)
    for ang, r in ((212, 30), (268, 41), (318, 24)):
        b = math.radians(ang)
        px, py = cx + r * math.cos(b), cy + r * math.sin(b)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(246, 206, 120))
    d.line([x0, y1, x1, y1], fill=(60, 82, 118), width=1)


def scene_map(d, box, pins):
    """Eight outlined elliptical landmasses on navy + numbered red pins."""
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=(12, 23, 44))
    land = [
        (0.12, 0.20, 0.16, 0.10), (0.30, 0.44, 0.10, 0.14),
        (0.52, 0.22, 0.13, 0.09), (0.58, 0.48, 0.09, 0.12),
        (0.74, 0.66, 0.14, 0.08), (0.78, 0.24, 0.12, 0.07),
        (0.40, 0.74, 0.10, 0.06), (0.22, 0.58, 0.07, 0.09),
    ]
    for cx, cy, rx, ry in land:
        bx = x0 + cx * (x1 - x0)
        by = y0 + cy * (y1 - y0)
        rw = rx * (x1 - x0)
        rh = ry * (y1 - y0)
        d.ellipse([bx - rw, by - rh, bx + rw, by + rh],
                  fill=(24, 40, 66), outline=(72, 98, 136), width=1)
    f = bold(6)
    for i, (px, py) in enumerate(pins, start=1):
        cx = x0 + px * (x1 - x0)
        cy = y0 + py * (y1 - y0)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED,
                  outline=(255, 200, 205), width=1)
        num = str(i)
        tw = f.getlength(num)
        d.text((cx - tw / 2, cy - 4), num, font=f, fill=WHITE)


# ---------------------------------------------------------------- draw
def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    CW = W - 2 * M                      # content width

    # ---------- 1. header band 0-130
    d.rectangle([0, 0, W, 130], fill=NAVY)
    # right column reserved first so the masthead can never run under it
    pt_label = "PRESS TIME"
    pt_time = "09:45 UTC"
    pt_w = max(bold(9).getlength(pt_label), bold(28).getlength(pt_time))
    pt_x = W - M - pt_w
    mast, mastf = fit("ONE DAY  ·  SUNDAY 22 NOVEMBER 2026", serif(46),
                      pt_x - M - 18)
    d.text((M, 24), mast, font=mastf, fill=WHITE)
    d.text((M, 84), "THE WORLD TONIGHT  ·  38 STORIES  ·  7 REGIONS  ·  "
                    "ALL FROM THIS ONE DAY", font=bold(12), fill=DUSTY)
    d.text((W - M - bold(9).getlength(pt_label), 30), pt_label,
           font=bold(9), fill=PALE_BLUE)
    d.text((W - M - bold(28).getlength(pt_time), 46), pt_time,
           font=bold(28), fill=WHITE)
    d.rectangle([0, 130, W, 133], fill=RED)

    # ---------- 2. stats strip 130-196
    stats = [("186", "DRONES IN ONE NIGHT"), ("7", "REGIONS"),
             ("38", "STORIES"), ("161", "SHOT DOWN"),
             ("14", "TRAPPED IN DYMER"), ("24", "DEAD OFF NIGERIA")]
    cellw = CW / 6
    ytop, ybot = 138, 192
    for i, (num, lab) in enumerate(stats):
        cx0 = M + i * cellw
        nf = bold(30)
        d.text((cx0 + 4, ytop), num, font=nf, fill=RED)
        lines, lf = wrap_n(lab, bold(8), cellw - 12, 2)
        ly = ytop + 34
        for ln in lines:
            d.text((cx0 + 4, ly), ln, font=lf, fill=GREY)
            ly += 10
        if i:
            d.line([cx0, ytop + 2, cx0, ybot - 4], fill=RULE, width=1)
    rule(d, M, 196, W - M)

    # ---------- 3. region pill bar 196-226
    pill_counts = [("EUROPE", 9), ("MIDDLE EAST", 7), ("ASIA", 8),
                   ("AFRICA", 5), ("AMERICAS", 5), ("OCEANIA", 3),
                   ("WORLD", 1)]
    pf = bold(9)
    x = M
    for name, cnt in pill_counts:
        label = "%s %d" % (name, cnt)
        pw = pill(d, x, 200, label, REGIONS[name], pf, padx=7, h=17)
        x += pw + 4

    # ---------- 4. navy timeline bar 226-264
    d.rectangle([M, 228, W - M, 262], fill=NAVY)
    marks = [("00:40", "KYIV STRIKE"), ("03:00", "COP31 DEADLINE"),
             ("06:00", "186 DRONES"), ("06:00", "VEGAS GP ENDS"),
             ("09:00", "HK TURNOUT"), ("09:45", "PRESS TIME")]
    mf, cf = bold(8), bold(7)
    span = (CW - 40) / (len(marks) - 1)
    for i, (tm, cap) in enumerate(marks):
        mx = M + 20 + i * span
        d.line([mx, 236, mx, 254], fill=PALE_BLUE, width=1)
        d.ellipse([mx - 2, 241, mx + 2, 245], fill=RED)
        tw = mf.getlength(tm)
        d.text((mx - tw / 2, 228 + 2), tm, font=mf, fill=WHITE)
        cap, cf2 = fit(cap, cf, span - 8)
        cw2 = cf2.getlength(cap)
        d.text((mx - cw2 / 2, 253), cap, font=cf2, fill=PALE_BLUE)

    # ---------- 5. lead cards 274-470
    leads = [
        ("ANTALYA, TÜRKIYE", "WORLD", "PENDING",
         "COP31 closes with no deal as the EU walks out",
         "Two weeks of talks ended without a figure for the climate fund.",
         "Reuters", scene_skyline),
        ("DYMER, KYIV REGION", "EUROPE", "CONFIRMED",
         "186 drones at Ukraine; 14 may be trapped",
         "161 shot down or jammed. A drone collapsed part of an apartment block.",
         "Ukraine Air Force", scene_drones),
        ("RIFFA, BAHRAIN", "MIDDLE EAST", "CLAIM",
         "Iran claims hits on US radar sites",
         "The attacks were intercepted and caused no casualties, Bahrain says.",
         "IRGC", scene_radar),
    ]
    gap = 12
    cw = (CW - 2 * gap) / 3
    cy0, cy1 = 274, 470
    for i, (place, reg, status, head, summ, src, scene) in enumerate(leads, 1):
        x0 = M + (i - 1) * (cw + gap)
        x1 = x0 + cw
        d.rectangle([x0, cy0, x1, cy1], fill=WHITE, outline=RULE, width=1)
        d.rectangle([x0, cy0, x1, cy0 + 4], fill=REGIONS[reg])
        # illustration panel
        ib = [x0 + 6, cy0 + 8, x1 - 6, cy0 + 8 + 74]
        scene(d, ib)
        # badge over illustration
        badge(d, x0 + 12, cy0 + 14, status, bold(6))
        # number
        d.text((x1 - 20, cy0 + 10), str(i), font=bold(15), fill=RED)
        # place
        pl, plf = fit(place, bold(8), cw - 34)
        d.text((x0 + 6, cy0 + 88), pl, font=plf, fill=REGIONS[reg])
        # headline, max 3 lines
        hl, hf = wrap_n(head, bold(13), cw - 12, 3)
        hy = cy0 + 99
        for ln in hl:
            d.text((x0 + 6, hy), ln, font=hf, fill=INK)
            hy += hf.size + 3
        # summary, max 3 lines
        sl, sf = wrap_n(summ, body(8), cw - 12, 3)
        sy = cy1 - 46
        for ln in sl:
            d.text((x0 + 6, sy), ln, font=sf, fill=INK)
            sy += sf.size + 2
        # source
        sr, srf = fit(src, bold(7), cw - 12)
        d.text((x0 + 6, cy1 - 11), sr, font=srf, fill=GREY)

    # ---------- 6. grid of twelve + numbers panel 482-740
    smalls = [
        ("SERANG, INDONESIA", "ASIA", "CONFIRMED",
         "Candy factory fire kills three, 39 missing", "Reuters"),
        ("GAZA CITY", "MIDDLE EAST", "REPORTED",
         "Israeli fire kills four; three in a food truck", "Al Jazeera"),
        ("KHARTOUM", "AFRICA", "REPORTED",
         "Drones strike homes near the capital", "AFP"),
        ("SOUTHERN NIGERIA", "AFRICA", "CONFIRMED",
         "Mourners' boat capsizes; 24 dead, 24 saved", "AP"),
        ("VATICAN CITY", "EUROPE", "CONFIRMED",
         "Pope Leo XIV hosts 1,300 poor guests", "Vatican News"),
        ("HONG KONG", "ASIA", "CONFIRMED",
         "Record turnout in the committee polls", "HK Government"),
        ("LAS VEGAS", "AMERICAS", "CONFIRMED",
         "Verstappen wins by 0.639s; his 75th", "F1 and AP"),
        ("WELLINGTON", "OCEANIA", "CONFIRMED",
         "India declare on a record 720/9", "Cricbuzz"),
        ("SEOUL", "ASIA", "CONFIRMED",
         "Education minister resigns over AI cheating", "Yonhap"),
        ("BRASILIA", "AMERICAS", "REPORTED",
         "Bolsonaro still in intensive care", "Reuters"),
        ("TEHRAN", "MIDDLE EAST", "CONFIRMED",
         "Rolling power cuts, up to two hours a day", "AFP"),
        ("MANILA", "ASIA", "CONFIRMED",
         "Storm strands 1,500 travellers", "AFP"),
    ]
    numbers = [("186", "drones at Ukraine"), ("161", "downed or jammed"),
               ("14", "trapped, Dymer"), ("98.37%", "Hong Kong turnout"),
               ("720/9", "India record total"), ("24", "dead, capsize"),
               ("3", "dead at factory fire"), ("4", "dead at Hartha"),
               ("3.3%", "IMF growth")]

    panw = 210
    gx0, gx1 = M, W - M - panw - gap
    gy0, gy1 = 482, 740
    gcw = (gx1 - gx0 - 2 * 8) / 3
    gch = (gy1 - gy0 - 3 * 8) / 4
    for i, (place, reg, status, head, src) in enumerate(smalls):
        r, c = divmod(i, 3)
        x0 = gx0 + c * (gcw + 8)
        y0 = gy0 + r * (gch + 8)
        x1, y1 = x0 + gcw, y0 + gch
        d.rectangle([x0, y0, x1, y1], fill=WHITE, outline=RULE, width=1)
        d.rectangle([x0, y0, x0 + 3, y1], fill=REGIONS[reg])
        badge(d, x0 + 7, y0 + 5, status, bold(6))
        d.text((x1 - 12, y0 + 4), str(i + 4), font=bold(9), fill=RED)
        pl, plf = fit(place, bold(6), gcw - 26)
        d.text((x0 + 7, y0 + 15), pl, font=plf, fill=REGIONS[reg])
        hl, hf = wrap_n(head, bold(8), gcw - 12, 3)
        hy = y0 + 24
        for ln in hl:
            d.text((x0 + 7, hy), ln, font=hf, fill=INK)
            hy += hf.size + 1
        sr, srf = fit(src, bold(5), gcw - 12)
        d.text((x0 + 7, y1 - 9), sr, font=srf, fill=GREY)

    # numbers panel
    px0 = W - M - panw
    d.rectangle([px0, gy0, W - M, gy1], fill=NAVY)
    d.text((px0 + 10, gy0 + 8), "THE DAY IN NUMBERS", font=bold(9), fill=DUSTY)
    d.line([px0 + 10, gy0 + 22, W - M - 10, gy0 + 22], fill=(52, 74, 108))
    ny = gy0 + 30
    for val, lab in numbers:
        d.text((px0 + 10, ny), val, font=bold(13), fill=WHITE)
        lf = body(7)
        ls, lf2 = fit(lab, lf, panw - 20)
        d.text((px0 + 10, ny + 14), ls, font=lf2, fill=PALE_BLUE)
        ny += 25

    # ---------- 7. map panel 752-950 (300 wide)
    my0, my1 = 752, 950
    mx0, mx1 = M, M + 300
    d.rectangle([mx0, my0, mx1, my1], fill=NAVY)
    d.text((mx0 + 10, my0 + 8), "WHERE IT HAPPENED", font=bold(9), fill=DUSTY)
    pins = [
        (0.36, 0.34), (0.56, 0.42), (0.60, 0.54), (0.52, 0.66),
        (0.50, 0.30), (0.76, 0.44), (0.22, 0.42), (0.82, 0.72),
        (0.78, 0.34), (0.30, 0.62), (0.62, 0.36), (0.80, 0.50),
        (0.46, 0.52), (0.26, 0.34), (0.68, 0.58),
    ]
    scene_map(d, [mx0 + 8, my0 + 24, mx1 - 8, my1 - 8], pins)

    # ---------- 8. date-check box beside it
    bx0 = mx1 + 12
    bx1 = W - M
    d.rectangle([bx0, my0, bx1, my1], fill=PINK_BOX, outline=RED, width=2)
    d.text((bx0 + 10, my0 + 9), "DATE CHECK", font=bold(10), fill=RED)
    bodytxt = ("Every story here happened, or was first reported, on Sunday "
               "22 November 2026 UTC up to the 09:45 press time. Nothing is "
               "carried over from an earlier day.")
    bl, bf = wrap_n(bodytxt, body(8), bx1 - bx0 - 20, 3)
    by = my0 + 26
    for ln in bl:
        d.text((bx0 + 10, by), ln, font=bf, fill=INK)
        by += bf.size + 2
    by += 6
    d.text((bx0 + 10, by), "DELIBERATELY LEFT OUT", font=bold(8), fill=RED)
    by += 13
    bullets = ["Peru earthquake — Fri 20 Nov",
               "El Chapo Isidro arrest — Sat 21 Nov",
               "Kryvyi Rih missile — Sat 21 Nov",
               "Myanmar genocide ruling — Thu 19 Nov",
               "Copa Sudamericana final — Sat 21 Nov",
               "NWSL final — Sat 21 Nov",
               "Nvidia SEC probe — Fri 20 Nov",
               "Hodeidah strikes — 20 and 21 Nov"]
    for b in bullets:
        d.ellipse([bx0 + 11, by + 2, bx0 + 15, by + 6], fill=RED)
        d.text((bx0 + 20, by), b, font=body(7), fill=INK)
        by += 11

    # ---------- 9. navy footer 962-984
    d.rectangle([0, 962, W, 984], fill=NAVY)
    ft = ("ONE DAY  ·  38 STORIES  ·  7 REGIONS  ·  SCENES ARE DRAWN "
          "ILLUSTRATIONS  ·  WIRES READ TO 09:45 UTC")
    ff, ff2 = fit(ft, bold(7), W - 2 * M - 70)
    d.text((M, 969), ft, font=ff2, fill=PALE_BLUE)
    pg = "PAGE 01"
    d.text((W - M - bold(7).getlength(pg), 969), pg, font=bold(7), fill=WHITE)

    # ---------- save + report
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out)
    px = img.load()
    last = 0
    for y in range(H - 1, -1, -1):
        row_has = False
        for x in range(W):
            if px[x, y] != (250, 246, 236):
                row_has = True
                break
        if row_has:
            last = y
            break
    print("saved")
    print(last)


if __name__ == "__main__":
    main()
