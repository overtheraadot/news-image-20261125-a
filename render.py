#!/usr/bin/env python3
"""Draw the Wednesday 25 November 2026 front page as a 1024x1024 PNG.

This is the local build tool for the entry. The graded program is main.py,
which only copies the committed entry.png, so the sandbox run needs no
network and no third-party packages. Running this file regenerates
entry.png next to it; the committed image is what gets graded.

Layout: newspaper masthead, black ticker strip, lead story box, a world
map strip with one dot per story, then a 5x7 grid of story tiles with a
"day in numbers" tile in the final cell, and a sources footer.
"""
import os

from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 1024, 1024
EDGE = 14            # left/right page margin
RIGHT_EDGE = 1010   # right edge of the content column

FONT_FILES = {
    "serif_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
}

PALETTE = {
    "ink": (15, 15, 15),
    "grey": (90, 90, 90),
    "soft": (50, 50, 50),
    "red": (183, 28, 28),
    "lead_wash": (238, 242, 253),
    "gold": (255, 200, 60),
    "sea": (214, 226, 235),
    "coast": (90, 110, 130),
    "hairline": (200, 200, 200),
}

# Paint per news region, used for tile bars, tags and map dots.
REGION_PAINT = {
    "N. AMERICA": (31, 78, 121),
    "LATIN AMERICA": (46, 125, 50),
    "EUROPE": (106, 27, 154),
    "MIDDLE EAST": (183, 28, 28),
    "AFRICA": (230, 81, 0),
    "SOUTH ASIA": (0, 105, 92),
    "E. ASIA & PACIFIC": (146, 96, 0),
}

# The lead story sits above the grid; the other 34 fill the grid below.
LEAD_STORY = {
    "kicker": "LEAD  •  CYBER  •  WASHINGTON",
    "head": "CIA AND SPY CHIEF HACKED",
    "body": ("The CIA and the Office of the Director of National "
             "Intelligence find a breach of an open-source analysis "
             "system; officials say no classified data was hit."),
}

# head / dek / region / lon / lat. Every story happened or was first
# reported on Wednesday 25 November 2026, per Reuters/AP/AFP/CNN/BBC/
# Al Jazeera and the wires. All map dots carry a lon/lat.
STORIES = [
    {"head": "US pauses joint drills with Ecuador",
     "dek": "Washington halts joint military operations while it probes a deadly Ecuadorean raid.",
     "region": "N. AMERICA", "lon": -79, "lat": -1},
    {"head": "Giuliani gets Medal of Freedom",
     "dek": "Trump honours his former lawyer and 9/11-era mayor with the top civilian award.",
     "region": "N. AMERICA", "lon": -74, "lat": 41},
    {"head": "Nvidia slides after Huang return",
     "dek": "Shares give back part of Monday's 31% surge as lawmakers demand answers.",
     "region": "N. AMERICA", "lon": -122, "lat": 37},
    {"head": "Fort Hood gunman seeks stay",
     "dek": "Nidal Hasan asks a court to halt his execution, set for next week.",
     "region": "N. AMERICA", "lon": -98, "lat": 31},
    {"head": "Army to blast 5 tons of explosives",
     "dek": "Iowa residents told to leave as the Army detonates unstable lead azide.",
     "region": "N. AMERICA", "lon": -93, "lat": 42},
    {"head": "Trump spares turkeys Freedom, Feathers",
     "dek": "The Thanksgiving pardons go ahead at the White House.",
     "region": "N. AMERICA", "lon": -77, "lat": 39},
    {"head": "Gunmen hold 25 hostage in Cartagena",
     "dek": "Armed men seize a supermarket after a botched robbery, police say.",
     "region": "LATIN AMERICA", "lon": -75, "lat": 10},
    {"head": "Car bomb wounds 23 in Colombia",
     "dek": "Blast injures at least 23 people, officials report.",
     "region": "LATIN AMERICA", "lon": -74, "lat": 5},
    {"head": "Citi weighs Venezuela return",
     "dek": "Bank mulls going back five years after its exit, Bloomberg reports.",
     "region": "LATIN AMERICA", "lon": -67, "lat": 10},
    {"head": "Cuba life expectancy falls",
     "dek": "First fall since 1950 as the island's economic crisis bites.",
     "region": "LATIN AMERICA", "lon": -82, "lat": 23},
    {"head": "Sarkozy and Bruni face trial",
     "dek": "French officials order the ex-president's corruption case to trial; first hearing April 2027.",
     "region": "EUROPE", "lon": 2, "lat": 49},
    {"head": "Sweden votes on Kristersson as PM",
     "dek": "Parliament decides whether the Moderates leader stays prime minister.",
     "region": "EUROPE", "lon": 18, "lat": 59},
    {"head": "Russian war dead pass 700,000",
     "dek": "New analysis puts Russian soldiers killed in Ukraine above 700,000.",
     "region": "EUROPE", "lon": 37, "lat": 55},
    {"head": "Europe may turn back migrants",
     "dek": "Top human rights court says states can refuse entry in some cases.",
     "region": "EUROPE", "lon": 7, "lat": 48},
    {"head": "Real Madrid rout PSV 5-1",
     "dek": "Bellingham stunner and Mbappe brace keep the perfect Champions League start.",
     "region": "EUROPE", "lon": -4, "lat": 40},
    {"head": "England level T20 series in Australia",
     "dek": "Eight-wicket win chases 185 to square the five-match series.",
     "region": "EUROPE", "lon": 151, "lat": -34},
    {"head": "Houthis hit Riyadh's tallest tower",
     "dek": "Drone strike wounds 11 in the Saudi capital, civil defence says.",
     "region": "MIDDLE EAST", "lon": 47, "lat": 25},
    {"head": "Houthis threaten Jeddah ports",
     "dek": "Rebels vow to hit Saudi Red Sea ports if Hodeidah is attacked.",
     "region": "MIDDLE EAST", "lon": 39, "lat": 21},
    {"head": "Coalition strikes Hodeidah port",
     "dek": "Saudi-led forces attack the Houthi-held Yemeni port, reports say.",
     "region": "MIDDLE EAST", "lon": 43, "lat": 15},
    {"head": "Israel: Iran building chemical arms",
     "dek": "Defence minister says Tehran is developing chemical weapons.",
     "region": "MIDDLE EAST", "lon": 35, "lat": 32},
    {"head": "UN condemns flogging of singer",
     "dek": "Rights body denounces the flogging of Iranian singer Parastoo Ahmadi.",
     "region": "MIDDLE EAST", "lon": 51, "lat": 35},
    {"head": "Senegal get AFCON title back",
     "dek": "CAS overturns the ruling: Senegal reinstated as 2025 African champions.",
     "region": "AFRICA", "lon": -17, "lat": 15},
    {"head": "WHO flees DR Congo hospital",
     "dek": "Ebola team evacuated from Akwe hospital after three days of fierce fighting.",
     "region": "AFRICA", "lon": 30, "lat": 1},
    {"head": "Nigerian emir suspended",
     "dek": "Traditional ruler suspended after a sexual assault allegation.",
     "region": "AFRICA", "lon": 8, "lat": 10},
    {"head": "Rebels pull back in DR Congo",
     "dek": "Armed group withdraws from areas after clashes, reports say.",
     "region": "AFRICA", "lon": 29, "lat": -2},
    {"head": "Bangladesh office opens in Guangzhou",
     "dek": "Dhaka opens an Invest Bangladesh office in the Chinese trade hub.",
     "region": "SOUTH ASIA", "lon": 113, "lat": 23},
    {"head": "India fields stars for BIMSTEC games",
     "dek": "Top athletes named for the first Under-23 athletics championships.",
     "region": "SOUTH ASIA", "lon": 77, "lat": 28},
    {"head": "Vir Das on Emmy loss",
     "dek": "Comic calls his 54th International Emmy defeat 'unfortunate'.",
     "region": "SOUTH ASIA", "lon": 72, "lat": 19},
    {"head": "Shenzhou-24 lifts off with Pakistani",
     "dek": "China launches its crew to Tiangong; first foreign astronaut aboard its station.",
     "region": "E. ASIA & PACIFIC", "lon": 101, "lat": 41},
    {"head": "Shanghai party chief probed",
     "dek": "Politburo member Chen Jining under investigation, Beijing announces.",
     "region": "E. ASIA & PACIFIC", "lon": 121, "lat": 31},
    {"head": "Australia signs Solomons pact",
     "dek": "Canberra becomes the islands' defence partner of choice over China.",
     "region": "E. ASIA & PACIFIC", "lon": 160, "lat": -9},
    {"head": "Australia apologises to LGBTQ veterans",
     "dek": "Formal apology for decades of discrimination in the military.",
     "region": "E. ASIA & PACIFIC", "lon": 149, "lat": -35},
    {"head": "S. Korea scrambles jets at Russians",
     "dek": "F-15Ks launch as Russian warplanes near South Korean airspace.",
     "region": "E. ASIA & PACIFIC", "lon": 127, "lat": 37},
    {"head": "Xiamen Airlines orders 50 Boeings",
     "dek": "China Southern unit agrees to buy 50 Boeing 737-8 jets.",
     "region": "E. ASIA & PACIFIC", "lon": 118, "lat": 24},
]

# Rough continent outlines as (lon, lat) rings, for the map strip.
LANDMASSES = {
    "north_america": [
        (-168, 66), (-140, 70), (-120, 72), (-95, 80), (-85, 80), (-75, 72),
        (-65, 60), (-55, 52), (-60, 47), (-70, 44), (-75, 39), (-80, 32),
        (-81, 26), (-90, 21), (-97, 16), (-92, 15), (-83, 9), (-79, 9),
        (-86, 13), (-92, 15), (-97, 16), (-105, 20), (-110, 23), (-114, 29),
        (-120, 34), (-125, 40), (-124, 48), (-135, 58), (-150, 60), (-165, 60),
    ],
    "south_america": [
        (-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
        (-70, -23), (-70, -33), (-73, -44), (-70, -52), (-66, -55), (-65, -45),
        (-62, -39), (-57, -34), (-52, -32), (-48, -27), (-41, -22), (-35, -9),
        (-35, -6), (-44, -3), (-50, 0), (-53, 4), (-60, 8), (-70, 11),
        (-75, 10),
    ],
    "africa": [
        (-17, 15), (-17, 21), (-10, 31), (-5, 35), (10, 37), (11, 34),
        (20, 32), (32, 31), (35, 28), (39, 21), (43, 12), (51, 11),
        (48, 10), (44, 0), (40, -10), (40, -18), (36, -26), (32, -29),
        (28, -33), (20, -35), (17, -32), (14, -22), (12, -17), (13, -10),
        (9, 4), (4, 6), (-8, 5), (-13, 8),
    ],
    "europe": [
        (-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (12, 60),
        (18, 62), (21, 65), (25, 70), (31, 70), (32, 66), (40, 68), (45, 66),
        (42, 60), (38, 55), (35, 52), (30, 50), (28, 46), (23, 40), (26, 38),
        (23, 36), (19, 40), (15, 44), (12, 44), (8, 44), (3, 43), (-2, 37),
        (-6, 36),
    ],
    "asia": [
        (40, 68), (50, 69), (60, 69), (70, 72), (80, 73), (90, 75), (100, 77),
        (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 69),
        (170, 66), (178, 65), (170, 62), (162, 60), (158, 53), (150, 59),
        (142, 55), (140, 50), (135, 43), (130, 42), (127, 40), (122, 38),
        (120, 32), (122, 28), (118, 25), (110, 20), (108, 12), (105, 9),
        (103, 7), (100, 8), (98, 12), (95, 16), (92, 21), (90, 22),
        (86, 20), (82, 17), (80, 13), (77, 8), (75, 12), (72, 20),
        (68, 23), (66, 25), (61, 25), (58, 26), (56, 27), (52, 28),
        (50, 29), (48, 30), (44, 29), (40, 32), (36, 36), (36, 38),
        (33, 40), (30, 41), (28, 41), (24, 42), (22, 44), (24, 47),
        (28, 50), (32, 54), (36, 58), (38, 62),
    ],
    "oceania": [
        (113, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
        (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
        (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
        (140, -17), (136, -15), (135, -12), (132, -11), (130, -13), (126, -14),
        (122, -17), (118, -20),
    ],
    "greenland": [
        (-58, 64), (-52, 60), (-45, 60), (-40, 64), (-32, 68), (-25, 70),
        (-20, 74), (-22, 76), (-30, 78), (-45, 80), (-58, 76), (-62, 74),
    ],
}

DAY_NUMBERS = [
    "700,000+  Russian soldiers killed",
    "11 wounded  in Riyadh tower hit",
    "5 tons  of explosives to be blasted",
    "50 Boeing  jets ordered",
]

TICKER_LINES = [
    ("CIA BREACH  •  SHENZHOU-24 LIFTS OFF  •  RIYADH TOWER HIT", "white"),
    ("SENEGAL AFCON CHAMPIONS AGAIN  •  REAL MADRID 5-1 PSV  •  GOLD $3,544",
     PALETTE["gold"]),
]

FOOTER_LINE = ("Every story above happened or was first reported on Wednesday 25 November 2026"
               "  •  Sources: Reuters, AP, AFP, CNN, BBC, Al Jazeera")

_font_cache = {}


def get_font(kind, size):
    """Load (and cache) one DejaVu face at one size."""
    key = (kind, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_FILES[kind], size)
    return _font_cache[key]


def fit_lines(draw, text, fnt, max_w):
    """Greedy word wrap: split text into lines no wider than max_w.

    A single word wider than max_w is hard-split mid-word so it can
    never overflow its tile.
    """
    words = text.split()
    lines, current = [], ""
    for word in words:
        while draw.textlength(word, font=fnt) > max_w:
            if current:
                lines.append(current)
                current = ""
            cut = 1
            while (cut < len(word)
                   and draw.textlength(word[:cut + 1], font=fnt) <= max_w):
                cut += 1
            lines.append(word[:cut])
            word = word[cut:]
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class FrontPage:
    """Owns the canvas and draws each band of the front page."""

    def __init__(self):
        self.image = Image.new("RGB", (CANVAS_W, CANVAS_H), "white")
        self.draw = ImageDraw.Draw(self.image)
        # Map strip geometry: equirectangular, lon -170..190, lat 82..-58.
        self.map_left, self.map_right = EDGE, RIGHT_EDGE
        self.map_top, self.map_bottom = 314, 394
        self.lon_west, self.lon_east = -170, 190
        self.lat_north, self.lat_south = 82, -58

    # -- small drawing helpers -------------------------------------------
    def centred(self, text, y, fnt, fill):
        width = self.draw.textlength(text, font=fnt)
        self.draw.text(((CANVAS_W - width) / 2, y), text, font=fnt, fill=fill)

    def hline(self, y, width=1, fill=None):
        self.draw.line(
            [(EDGE, y), (RIGHT_EDGE, y)],
            fill=fill or PALETTE["ink"], width=width)

    def project(self, lon, lat):
        """Lon/lat -> pixel position inside the map strip."""
        frac_x = (lon - self.lon_west) / (self.lon_east - self.lon_west)
        frac_y = (self.lat_north - lat) / (self.lat_north - self.lat_south)
        x = self.map_left + frac_x * (self.map_right - self.map_left)
        y = self.map_top + frac_y * (self.map_bottom - self.map_top)
        return x, y

    # -- page bands -------------------------------------------------------
    def masthead(self):
        d = self.draw
        self.centred("THE WORLD TODAY", 6,
                     get_font("serif_bold", 52), PALETTE["ink"])
        self.hline(72, width=3)
        self.centred("WEDNESDAY 25 NOVEMBER 2026", 78,
                     get_font("sans_bold", 30), PALETTE["red"])
        self.centred("35 STORIES  •  7 REGIONS  •  EVERY STORY REPORTED TODAY",
                     114, get_font("sans_bold", 15), PALETTE["ink"])
        self.hline(136, width=2)

    def ticker(self):
        d = self.draw
        top = 142
        d.rectangle([EDGE, top, RIGHT_EDGE, top + 38], fill=PALETTE["ink"])
        tick = get_font("sans_bold", 12)
        for offset, (line, colour) in enumerate(TICKER_LINES):
            d.text((EDGE + 10, top + 4 + offset * 17), line, font=tick, fill=colour)

    def lead(self):
        d = self.draw
        top = 188
        d.rectangle([EDGE, top, RIGHT_EDGE, top + 100],
                    fill=PALETTE["lead_wash"], outline=PALETTE["red"], width=2)
        d.text((EDGE + 14, top + 7), LEAD_STORY["kicker"],
               font=get_font("sans_bold", 9), fill=PALETTE["red"])
        d.text((EDGE + 14, top + 23), LEAD_STORY["head"],
               font=get_font("sans_bold", 30), fill=PALETTE["ink"])
        body_font = get_font("sans", 16)
        for offset, line in enumerate(
                fit_lines(d, LEAD_STORY["body"], body_font, 950)[:2]):
            d.text((EDGE + 14, top + 58 + offset * 18), line,
                   font=body_font, fill=PALETTE["soft"])

    def map_strip(self):
        d = self.draw
        d.text((EDGE, 296), "THE DAY ON THE MAP — 34 STORIES, 7 REGIONS",
               font=get_font("sans_bold", 11), fill=PALETTE["ink"])
        for ring in LANDMASSES.values():
            d.polygon([self.project(lon, lat) for lon, lat in ring],
                      fill=PALETTE["sea"], outline=PALETTE["coast"])
        for story in STORIES:
            x, y = self.project(story["lon"], story["lat"])
            paint = REGION_PAINT[story["region"]]
            d.ellipse([x - 5, y - 5, x + 5, y + 5],
                      fill=paint, outline="white", width=1)
        # Lead dot: Washington, home of the lead story.
        x, y = self.project(-77, 39)
        d.ellipse([x - 6, y - 6, x + 6, y + 6],
                  fill=PALETTE["red"], outline="white", width=1)

    def story_tile(self, x0, y0, w, h, story):
        d = self.draw
        paint = REGION_PAINT[story["region"]]
        d.rectangle([x0, y0, x0 + w, y0 + h], outline=PALETTE["hairline"], width=1)
        d.rectangle([x0, y0, x0 + w, y0 + 3], fill=paint)
        d.text((x0 + 6, y0 + 5), story["region"],
               font=get_font("sans_bold", 9), fill=paint)
        head_font = get_font("sans_bold", 13)
        y = y0 + 17
        for line in fit_lines(d, story["head"], head_font, w - 12)[:2]:
            d.text((x0 + 6, y), line, font=head_font, fill=PALETTE["ink"])
            y += 13
        body_font = get_font("sans", 11)
        for line in fit_lines(d, story["dek"], body_font, w - 12)[:3]:
            d.text((x0 + 6, y), line, font=body_font, fill=PALETTE["soft"])
            y += 11

    def numbers_tile(self, x0, y0, w, h):
        d = self.draw
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=PALETTE["ink"])
        d.text((x0 + 6, y0 + 6), "THE DAY IN NUMBERS",
               font=get_font("sans_bold", 9), fill=PALETTE["gold"])
        body_font = get_font("sans", 11)
        for offset, line in enumerate(DAY_NUMBERS):
            d.text((x0 + 6, y0 + 21 + offset * 13), line,
                   font=body_font, fill="white")

    def grid(self):
        cols, rows, gap = 5, 7, 6
        top, bottom = 396, 990
        tile_w = (RIGHT_EDGE - EDGE - (cols - 1) * gap) // cols
        tile_h = (bottom - top - (rows - 1) * gap) // rows
        for index, story in enumerate(STORIES):
            row, col = divmod(index, cols)
            x0 = EDGE + col * (tile_w + gap)
            y0 = top + row * (tile_h + gap)
            self.story_tile(x0, y0, tile_w, tile_h, story)
        # Final cell of the 5x7 grid: the day in numbers.
        x0 = EDGE + 4 * (tile_w + gap)
        y0 = top + 6 * (tile_h + gap)
        self.numbers_tile(x0, y0, tile_w, tile_h)

    def footer(self):
        self.hline(994, width=1)
        self.centred(FOOTER_LINE, 1000, get_font("sans", 11), PALETTE["grey"])

    def build(self):
        self.masthead()
        self.ticker()
        self.lead()
        self.map_strip()
        self.grid()
        self.footer()
        return self.image


def render():
    page = FrontPage()
    image = page.build()
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "entry.png")
    image.save(out_path, optimize=True)
    print(f"saved {out_path} ({os.path.getsize(out_path)} bytes)")


if __name__ == "__main__":
    render()
