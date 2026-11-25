#!/usr/bin/env python3
"""Draw the front page for Wednesday 25 November 2026.

Written from scratch for news-image-20261125: a newspaper front
page, 1024x1024, with a lead story, 34 short stories grouped into
seven world regions across three columns, and a small world-map
strip at the foot.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

PAPER = (247, 243, 234)
INK = (18, 18, 18)
NAVY = (16, 32, 64)
GOLD = (212, 175, 55)
RED = (178, 34, 34)
GREY = (90, 90, 90)
RULE = (200, 192, 175)

# (region, colour, [(headline, place), ...])
REGIONS = [
    ("EUROPE", (31, 73, 125), [
        ("Zelenskyy confirms Ukraine sank a Russian ship", "Gulf of Finland / Libya"),
        ("NATO sends AWACS early-warning plane to Poland", "Poland"),
        ("Putin vows retaliation for strikes on Russian refineries", "Moscow"),
        ("Sarkozy and Bruni ordered to trial over Libya case", "Paris"),
        ("EU announces fresh sanctions against Russia", "Brussels"),
        ("Denmark's top court upholds 'ghetto' evictions", "Copenhagen"),
    ]),
    ("MIDDLE EAST", (146, 64, 14), [
        ("Houthis hit Riyadh's tallest tower; 11 wounded", "Riyadh"),
        ("Israel kills Hamas internal security chief in Gaza strike", "Gaza"),
        ("Winter storms flood Gaza camps; food convoy hit, 4 dead", "Gaza City"),
        ("Iran says three tankers hit by mines in Strait of Hormuz", "Strait of Hormuz"),
        ("US Senate votes 51-48 against curbing Trump's Iran war powers", "Washington"),
        ("Houthis push to 60 km from Aden; army says city will hold", "Yemen"),
    ]),
    ("NORTH AMERICA", (21, 101, 92), [
        ("Trump awards Rudy Giuliani the Medal of Freedom", "Washington"),
        ("CIA and ODNI hit by breach of unclassified data", "Washington"),
        ("Nvidia bounce fades: shares fall 6%, Nasdaq down 1.5%", "New York"),
        ("US consumer confidence jumps to near two-year high", "Washington"),
        ("Trump pardons turkeys Freedom and Feathers", "White House"),
        ("Fort Hood gunman Hasan seeks stay of execution", "Texas"),
    ]),
    ("ASIA-PACIFIC", (107, 33, 168), [
        ("Asian stocks tumble on fresh US tariff threats", "Seoul / Taipei"),
        ("China Southern unit orders 50 Boeing 737-8 jets", "Xiamen"),
        ("BJP and Akali Dal announce Punjab alliance for 2027", "Punjab"),
        ("Nepal PM Balendra Shah wraps first state visit to India", "New Delhi"),
        ("Australia inflation runs hot; rate pressure grows", "Sydney"),
        ("England beat Australia by 8 wickets in 2nd T20I", "Cricket"),
    ]),
    ("AFRICA", (120, 85, 5), [
        ("Senegal gets 2025 AFCON title back after CAS ruling", "Dakar"),
        ("Rebel group pulls back from DR Congo areas after clashes", "DR Congo"),
        ("Nigerian emir suspended after sexual assault allegation", "Nigeria"),
        ("Cameroon separatist leader in Norway court on war crimes", "Oslo"),
    ]),
    ("LATIN AMERICA", (34, 139, 34), [
        ("Car bomb in Colombia injures at least 23 people", "Colombia"),
        ("Armed men hold dozens hostage in Cartagena supermarket", "Cartagena"),
        ("Venezuela reports total public debt of $237.5bn", "Caracas"),
    ]),
    ("TECH, SCIENCE & SPORT", (100, 100, 100), [
        ("Microsoft declares 'Code Red' after historic outage", "Redmond"),
        ("One asteroid eclipses another in rare deep-space image", "Didymos"),
        ("Real Madrid hit PSV 5-1: Bellingham stunner, Mbappe brace", "Madrid"),
    ]),
]

TOTAL = sum(len(r[2]) for r in REGIONS)

LEAD_HEAD = "Ukraine sinks Russian ship as war spreads beyond Europe"
LEAD_DECK = ("Kyiv confirms drone strikes on a Russian cargo ship in the Gulf of "
             "Finland and a warship off Libya \u2014 as NATO sends an AWACS plane "
             "to Poland and Europe demands a seat at the peace talks.")

# Three story columns: (x, width, [region indexes in display order]).
COLUMNS = [
    (24, 312, [0, 4]),
    (356, 312, [1, 5, 6]),
    (688, 312, [2, 3]),
]


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap returning lines that fit inside width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_masthead(draw):
    draw.rectangle([0, 0, W, 118], fill=NAVY)
    draw.rectangle([0, 118, W, 122], fill=GOLD)
    draw.text((24, 22), "THE WORLD IN ONE PAGE",
              font=font(46, bold=True), fill=(255, 255, 255))
    draw.text((24, 80), "WEDNESDAY, 25 NOVEMBER 2026",
              font=font(25, bold=True), fill=GOLD)
    side = font(15, bold=True)
    draw.text((W - 24, 26), "%d STORIES" % TOTAL, font=side,
              fill=(255, 255, 255), anchor="ra")
    draw.text((W - 24, 50), "7 WORLD REGIONS", font=side,
              fill=(220, 220, 220), anchor="ra")
    draw.text((W - 24, 74), "ONE DAY'S NEWS", font=side, fill=GOLD, anchor="ra")


def draw_lead(draw):
    draw.rectangle([24, 138, W - 24, 252], outline=RED, width=3)
    draw.rectangle([24, 138, 190, 166], fill=RED)
    draw.text((34, 142), "LEAD STORY", font=font(16, bold=True),
              fill=(255, 255, 255))
    head = font(27, bold=True)
    y = 172
    for line in wrap(draw, LEAD_HEAD, head, W - 72):
        draw.text((36, y), line, font=head, fill=INK)
        y += 32
    deck = font(15)
    for line in wrap(draw, LEAD_DECK, deck, W - 72):
        draw.text((36, y), line, font=deck, fill=(50, 50, 50))
        y += 20


def draw_region(draw, x, y, width, name, colour, stories, start_no):
    """Draw one region block; return (next y, next story number)."""
    draw.rectangle([x, y, x + width, y + 24], fill=colour)
    draw.text((x + 8, y + 3), name, font=font(13, bold=True),
              fill=(255, 255, 255))
    draw.text((x + width - 8, y + 3), str(len(stories)),
              font=font(13, bold=True), fill=(255, 255, 255), anchor="ra")
    y += 28
    num_f = font(12, bold=True)
    head_f = font(12, bold=True)
    no = start_no
    for headline, place in stories:
        draw.text((x, y), "%02d" % no, font=num_f, fill=colour)
        text = "%s \u2014 %s" % (headline, place)
        for line in wrap(draw, text, head_f, width - 30):
            draw.text((x + 30, y), line, font=head_f, fill=INK)
            y += 15
        y += 5
        no += 1
    return y + 2, no


def draw_map(draw):
    """Simplified world map: rough continent blobs with region dots."""
    x0, y0, x1, y1 = 24, 812, W - 24, 978
    draw.rectangle([x0, y0, x1, y1], outline=RULE, width=2)
    draw.text((x0 + 10, y0 + 6), "THE DAY ON THE MAP",
              font=font(14, bold=True), fill=NAVY)
    draw.text((x1 - 10, y0 + 6), "Dots mark where the 34 stories happened",
              font=font(12), fill=GREY, anchor="ra")
    ox, oy, sx, sy = x0 + 40, y0 + 36, 2.55, 1.05  # lon/lat -> pixel

    def pt(lon, lat):
        return (ox + (lon + 170) * sx, oy + (72 - lat) * sy)

    # Rough continent outlines as longitude/latitude polygons.
    continents = [
        [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
         (-80, 62), (-75, 58), (-65, 60), (-60, 55), (-55, 47), (-65, 44),
         (-70, 42), (-75, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 29),
         (-97, 26), (-105, 23), (-110, 24), (-117, 33), (-124, 40),
         (-125, 49), (-130, 55), (-145, 60), (-158, 58), (-168, 66)],
        [(-75, 10), (-80, 8), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
         (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44),
         (-74, -52), (-68, -55), (-65, -45), (-62, -41), (-58, -34),
         (-52, -32), (-48, -28), (-41, -23), (-38, -15), (-35, -8),
         (-41, -3), (-44, 2), (-50, 0), (-52, 5), (-58, 7), (-62, 9),
         (-68, 11), (-72, 12), (-75, 10)],
        [(-10, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (0, 50), (2, 51),
         (5, 53), (8, 55), (10, 57), (12, 56), (18, 56), (21, 55), (24, 58),
         (28, 60), (30, 62), (30, 70), (40, 68), (50, 68), (60, 69),
         (70, 72), (80, 73), (90, 75), (100, 77), (110, 74), (120, 73),
         (130, 71), (140, 72), (150, 70), (160, 69), (170, 66), (178, 65),
         (170, 60), (162, 60), (158, 53), (150, 59), (142, 59), (140, 53),
         (135, 43), (130, 42), (127, 40), (122, 38), (120, 32), (115, 23),
         (110, 20), (108, 12), (105, 9), (100, 8), (98, 12), (95, 16),
         (92, 21), (89, 22), (86, 20), (82, 17), (80, 13), (77, 8),
         (75, 12), (72, 20), (70, 22), (66, 25), (62, 25), (58, 26),
         (56, 27), (52, 27), (50, 29), (48, 30), (44, 29), (40, 31),
         (36, 36), (30, 36), (27, 37), (23, 36), (19, 40), (15, 38),
         (12, 42), (8, 39), (3, 38), (0, 36), (-2, 35), (-6, 35),
         (-10, 37)],
        [(-6, 35), (-10, 31), (-13, 28), (-17, 21), (-17, 15), (-15, 11),
         (-12, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (12, 0),
         (13, -5), (12, -10), (13, -15), (12, -18), (14, -22), (13, -26),
         (16, -29), (19, -34), (25, -34), (28, -33), (32, -29), (35, -24),
         (36, -20), (40, -15), (40, -11), (42, -8), (44, -2), (46, 2),
         (51, 11), (48, 11), (44, 12), (43, 12), (40, 15), (39, 21),
         (38, 24), (35, 28), (33, 31), (30, 31), (25, 32), (20, 32),
         (15, 32), (11, 34), (10, 37), (5, 37), (0, 36), (-6, 35)],
        [(114, -22), (114, -30), (115, -35), (120, -34), (124, -33),
         (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
         (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
         (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
         (132, -12), (130, -13), (126, -14), (122, -17), (118, -20),
         (114, -22)],
    ]
    for poly in continents:
        draw.polygon([pt(lon, lat) for lon, lat in poly],
                     fill=(214, 226, 235), outline=(120, 140, 160))
    dots = [  # (lon, lat, region index)
        (-3, 54, 0), (19, 52, 0), (30, 50, 0), (10, 48, 0),
        (47, 25, 1), (51, 26, 1), (44, 33, 1), (35, 31, 1),
        (-77, 39, 2), (-99, 39, 2), (-87, 42, 2),
        (77, 28, 3), (103, 1, 3), (121, 31, 3), (139, 35, 3),
        (9, 9, 4), (28, -2, 4), (32, -26, 4),
        (-74, 5, 5), (-58, -23, 5), (-66, 10, 5),
    ]
    colours = [r[1] for r in REGIONS]
    for lon, lat, idx in dots:
        cx, cy = pt(lon, lat)
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=colours[idx],
                     outline=(255, 255, 255), width=2)


def draw_footer(draw):
    draw.text((24, 992),
              "Sources: Reuters, AP, BBC, AFP, as reported on 25 November 2026  |  "
              "make.fun  news-image-20261125",
              font=font(12), fill=GREY)


def build(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_lead(draw)
    # Story numbers follow region order, not column order.
    starts = {}
    n = 1
    for region in REGIONS:
        starts[REGIONS.index(region)] = n
        n += len(region[2])
    for x, width, idxs in COLUMNS:
        y = 268
        for idx in idxs:
            name, colour, stories = REGIONS[idx]
            y, _ = draw_region(draw, x, y, width, name, colour, stories,
                               starts[idx])
    draw_map(draw)
    draw_footer(draw)
    img.save(out_path, "PNG", optimize=True)
    return out_path


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(here, "entry.png")
    build(target)
    print("wrote %s (%d bytes)" % (target, os.path.getsize(target)))
