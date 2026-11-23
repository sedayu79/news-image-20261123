#!/usr/bin/env python3
"""THE WORLD TODAY - Monday 23 November 2026 in one image.

A program that draws a dense newspaper front page summing up the world
news of Monday 23 November 2026, and writes it to /output/entry.png
(locally: $MAKEFUN_OUTPUT_DIR/entry.png).

Every story in the image happened, or was first reported, on Monday
23 November 2026 (verified by news search on the day). Events from other
days are listed in the DATE CHECK box instead of in the stories.

Drawn entirely in code with the Python standard library: own PNG
encoder (zlib) and own 5x7 bitmap font. No network, no clock, no
randomness: two runs write byte-identical files.
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette ---------------------------------------------------------
CREAM = (247, 241, 227)   # warm paper
PAPER = (252, 248, 238)   # card paper
INK = (28, 28, 28)
NAVY = (31, 58, 95)       # accent: rules, tags, pins
RED = (176, 58, 46)       # accent 2: numbers, warnings
SAGE = (122, 139, 111)
GOLD = (201, 162, 39)
SEA = (214, 224, 232)
LAND = (222, 210, 178)
LINE = (180, 172, 150)
GRAY = (96, 94, 88)
TEAL = (43, 106, 94)
WHITE = (255, 255, 255)
DARKRED = (140, 40, 30)

# ---- 5x7 bitmap font -------------------------------------------------
# Each glyph is 7 rows of 5 characters; '#' is a set pixel.
FONT = {
    'A': ("..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", ".#.#.", "..#..", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#...", ".#...", "#####", ".#...", ".#...", ".#..."),
    'g': (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", "####.", "#...#", "#...#", "####.", "#....", "#...."),
    'q': (".....", ".####", "#...#", "#...#", ".####", "....#", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "#####", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", "#...#", "#...#", "#...#", ".####", "....#", ".###."),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".....", ".##..", "..#.."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    '|': ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    '\\': ("#....", ".#...", ".#...", "..#..", "...#.", "...#.", "....#"),
}

for _g in FONT.values():
    assert len(_g) == 7 and all(len(_r) == 5 for _r in _g), "bad glyph"


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---- canvas ----------------------------------------------------------
class Canvas:
    def __init__(self):
        self.px = bytearray(W * H * 3)
        for i in range(0, len(self.px), 3):
            self.px[i] = CREAM[0]
            self.px[i + 1] = CREAM[1]
            self.px[i + 2] = CREAM[2]

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def outline(self, x, y, w, h, c):
        self.hline(x, y, w, c)
        self.hline(x, y + h - 1, w, c)
        self.vline(x, y, h, c)
        self.vline(x + w - 1, y, h, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d <= r * r:
                        self.set(xx, yy, c)

    def poly(self, pts, c):
        # scanline fill of a polygon
        if not pts:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    if y1 != y0:
                        xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.set(x, y, c)

    def text(self, x, y, scale, s, c, bold=False):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '#':
                        for dy in range(scale):
                            for dx in range(scale):
                                self.set(cx + col * scale + dx,
                                         y + row * scale + dy, c)
                                if bold and col < 4:
                                    self.set(cx + col * scale + dx + 1,
                                             y + row * scale + dy, c)
            cx += 6 * scale
        return cx

    def text_center(self, x, y, w, scale, s, c, bold=False):
        tw = text_width(s, scale)
        self.text(x + (w - tw) // 2, y, scale, s, c, bold)

    def para(self, x, y, scale, max_width, lines, c, leading=None, bold=False):
        if leading is None:
            leading = 7 * scale + 2
        for ln in lines:
            self.text(x, y, scale, ln, c, bold)
            y += leading
        return y


# ---- the day's news (verified 23 Nov 2026) ---------------------------
# tag kinds: CONFIRMED / CLAIM / FORECAST / REPORTED

TIMELINE = [
    ("03:00", "Dymer flats hit, 11 dead"),
    ("03:09", "Iran claims 78 US drones downed"),
    ("05:05", "India PMI 56.3, factories lead"),
    ("06:00", "Belgium airspace shuts"),
    ("06:27", "Asia tech sell-off deepens"),
    ("07:00", "Modi welcomes Shah in Delhi"),
    ("08:18", "France PMI falls to 46.2"),
    ("16:00", "Zelenskyy: Ukraine sank Merkury"),
]

NUMBERS = [
    ("258", "House seats for Democrats"),
    ("15", "killed in Kyiv region strikes"),
    ("429", "flights cancelled in Belgium"),
    ("78", "US drones Iran claims downed"),
    ("3.3%", "Kospi fall on Monday"),
    ("8", "MoUs signed, India-Nepal"),
]

HEROES = [
    dict(tag="AFRICA - LIBYA", kind="CLAIM", src="REUTERS",
         head="UKRAINE SAYS IT SANK RUSSIAN CORVETTE OFF LIBYA",
         body="Zelenskyy says seven sea drones sank the Merkury, one of "
              "Russia's newest warships, and hit the cargo ship MV Angara. "
              "A Ka-27 helicopter was destroyed too.",
         art="ship"),
    dict(tag="AMERICAS - US", kind="CONFIRMED", src="AP",
         head="DEMOCRATS CLINCH 258 HOUSE SEATS, BIGGEST SINCE 1992",
         body="Chuck Hubbard beats Virginia Foxx in North Carolina. "
              "Democrats gain 44 seats; Republicans fall to 173. "
              "Divided government from January.",
         art="capitol"),
    dict(tag="EUROPE - UKRAINE", kind="CONFIRMED", src="AL JAZEERA",
         head="RUSSIAN STRIKES KILL 15 IN KYIV REGION",
         body="A five-storey block in Dymer collapses, killing at least 11. "
              "A supermarket in Vyshneve is hit. Zelenskyy urges the US "
              "to release Patriot missiles.",
         art="rubble"),
    dict(tag="ASIA - INDIA", kind="CONFIRMED", src="THE HINDU",
         head="MODI AND SHAH RESET INDIA-NEPAL TIES",
         body="Ceremonial welcome in Delhi, 100-minute talks, eight MoUs "
              "signed. Ayodhya-Janakpur train announced; Nepal seeks $2bn "
              "for flood rebuilding.",
         art="flags"),
]

SECONDARY = [
    dict(tag="EUROPE", kind="CONFIRMED", src="REUTERS",
         head="BELGIUM GROUNDS ITSELF FOR A DAY",
         body="Air traffic control joins a national austerity strike; "
              "airspace shut 07:00-21:00, 429 flights hit.",
         art="plane"),
    dict(tag="ASIA", kind="CONFIRMED", src="DOW JONES",
         head="ASIA'S AI SELL-OFF DEEPENS",
         body="Kospi falls 3.3% as chip stocks slide; Seoul readies a "
              "stabilisation fund. Nasdaq 100 nears a bear market.",
         art="chart"),
    dict(tag="MIDDLE EAST", kind="CLAIM", src="PRESS TV",
         head="IRAN CLAIMS 78 US DRONES DOWNED",
         body="IRGC infographic counts 58 MQ-9 Reapers and 20 MQ-1 "
              "Predators. The Pentagon has not confirmed the tally.",
         art="drone"),
    dict(tag="EUROPE", kind="FORECAST", src="BBC",
         head="FIFA TO CONFIRM UK AS 2035 HOST",
         body="England, Scotland, Wales and Northern Ireland to stage the "
              "Women's World Cup: 48 teams, 104 matches, 19 venues.",
         art="ball"),
    dict(tag="ASIA", kind="CONFIRMED", src="REUTERS",
         head="DHAKA: HASINA WILL BE JAILED IF SHE RETURNS",
         body="Minister tells Reuters Bangladesh seeks her extradition "
              "from India as street violence flares.",
         art="court"),
    dict(tag="EUROPE", kind="CONFIRMED", src="REUTERS",
         head="DENMARK TAKES VISA-BAN PLAN TO EU",
         body="After the alleged Russian plot on rapper Kyivstoner, "
              "Copenhagen seeks EU-wide curbs on Russian tourists.",
         art="stamp"),
    dict(tag="ASIA", kind="REPORTED", src="BLOOMBERG",
         head="MSCI RETHINKS INDONESIA DOWNGRADE",
         body="Chief Henry Fernandez talked to President Prabowo in a "
              "call brokered by Ray Dalio, Bloomberg reports.",
         art="bars"),
    dict(tag="EUROPE", kind="CONFIRMED", src="REUTERS",
         head="GERMANY BOOMS AS FRANCE SLUMPS",
         body="German PMI 55.0, best since March 2022; France 46.2, a "
              "six-month low. Eurozone holds at 51.7.",
         art="gauge"),
]

ALSO = [
    "Gulf bourses rise on diplomatic momentum",
    "Brent near $93; Hormuz oil flows slow",
    "India PMI 56.3, factory demand leads",
    "Eurozone PMI 51.7, fifth month of growth",
    "Hedge funds' worst week since Apr 2025",
    "Qatar PM in Washington for Iran talks",
    "Iran parliament repeats 7 conditions",
    "Zelenskyy: release the Patriots",
    "US futures bounce after AI rout",
    "Taiwan's worst week in 30 years",
    "France PMI 46.2, a six-month low",
    "Nvidia down 23% in a week",
    "Dubai Islamic Bank jumps 9% on deal talks",
    "Diesel shortage persists as crude falls",
]

DATE_CHECK = ("Left out on purpose, first reported before Monday: COP31 collapse "
              "(22 Nov); Liverpool 4-0 Man Utd (22 Nov); Thitikul's third LPGA "
              "title (22 Nov); Trump warns of new Iran strikes after New Year "
              "(22 Nov); Common Cents Act signed, penny ends (20 Nov); "
              "Indonesia's MV Star Line seizure disclosed (20 Nov); Sparta II "
              "hit in the Baltic (21 Nov); Denmark's Kyivstoner plot revealed "
              "(20 Nov); California sues OpenAI (22 Nov); Iran's 58th MQ-9 "
              "claim (21 Nov).")

MAP_PINS = [
    (1, "Benghazi", 20.1, 32.1),
    (2, "Washington", -77.0, 38.9),
    (3, "Kyiv", 30.5, 50.4),
    (4, "Delhi", 77.2, 28.6),
    (5, "Brussels", 4.35, 50.85),
    (6, "Seoul", 127.0, 37.5),
    (7, "Hormuz", 56.5, 26.6),
    (8, "London", -0.1, 51.5),
    (9, "Dhaka", 90.4, 23.8),
    (10, "Copenhagen", 12.6, 55.7),
    (11, "Jakarta", 106.8, -6.2),
    (12, "Berlin", 13.4, 52.5),
]

CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 80), (-80, 73),
     (-65, 60), (-55, 47), (-70, 42), (-75, 35), (-80, 32), (-85, 30),
     (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 49),
     (-140, 60), (-165, 60)],
    [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-35, -8), (-40, -20),
     (-48, -28), (-58, -35), (-65, -41), (-70, -54), (-73, -40), (-75, -20),
     (-80, -5)],
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 70), (40, 68),
     (45, 60), (40, 55), (35, 50), (30, 46), (28, 41), (23, 40), (19, 42),
     (12, 44), (8, 44), (3, 42), (0, 39), (-2, 37), (-9, 37)],
    [(-6, 35), (-10, 31), (-17, 15), (-15, 11), (-8, 5), (5, 6), (9, 4),
     (13, -1), (12, -6), (13, -12), (12, -18), (16, -25), (20, -35),
     (28, -33), (33, -26), (36, -18), (40, -11), (42, -1), (46, 5),
     (51, 11), (48, 12), (43, 12), (40, 15), (38, 18), (35, 22), (32, 31),
     (25, 32), (19, 33), (11, 34), (10, 37)],
    [(30, 70), (40, 68), (50, 69), (60, 70), (70, 72), (80, 73), (90, 75),
     (100, 77), (110, 76), (120, 73), (130, 72), (140, 72), (150, 70),
     (158, 66), (162, 60), (158, 55), (150, 60), (142, 55), (140, 45),
     (135, 43), (130, 40), (127, 35), (122, 32), (120, 28), (115, 23),
     (110, 20), (108, 12), (105, 9), (100, 8), (97, 10), (95, 16),
     (92, 21), (90, 22), (87, 22), (85, 19), (80, 15), (77, 8), (75, 10),
     (72, 20), (68, 23), (65, 25), (62, 25), (58, 26), (55, 26),
     (52, 26), (50, 28), (48, 30), (50, 38), (52, 42), (55, 45),
     (50, 50), (48, 55), (45, 58), (42, 62), (40, 66), (35, 68)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
     (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
     (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20)],
]


# ---- small flat illustrations ---------------------------------------
def draw_art(cv, kind, x, y, w, h, fg, bg):
    """Draw a simple flat illustration inside the box (x, y, w, h)."""
    cv.rect(x, y, w, h, bg)
    cx, cy = x + w // 2, y + h // 2
    if kind == "ship":
        # sea + hull + mast + bridge + drone
        cv.rect(x, y + h - 14, w, 14, (120, 160, 190))
        cv.rect(x + 12, cy - 2, w - 24, 16, fg)
        cv.rect(x + 18, cy - 16, 16, 14, PAPER)
        cv.rect(x + w // 2 - 2, cy - 30, 4, 30, INK)
        cv.rect(x + w // 2 - 2, cy - 30, 22, 4, RED)
        cv.circle(x + w - 24, y + 14, 5, RED)
        cv.rect(x + w - 28, y + 18, 8, 2, INK)
    elif kind == "capitol":
        cv.rect(x + 14, y + h - 22, w - 28, 22, fg)
        for i in range(4):
            cv.rect(x + 20 + i * 16, y + 24, 6, h - 46, NAVY)
        cv.rect(x + 14, y + 18, w - 28, 6, NAVY)
        cv.circle(cx, y + 22, 14, NAVY)
        cv.rect(cx - 14, y + 20, 28, 5, NAVY)
        cv.rect(cx - 2, y + 4, 4, 8, RED)
    elif kind == "rubble":
        cv.rect(x + 12, y + 12, 26, h - 30, fg)
        cv.rect(x + 44, y + 22, 26, h - 40, NAVY)
        cv.line(x + 12, y + 26, x + 38, y + 40, RED)
        cv.line(x + 38, y + 18, x + 26, y + 34, RED)
        for i in range(5):
            cv.rect(x + 16 + i * 12, y + h - 12 - (i % 2) * 4, 8, 6, INK)
    elif kind == "flags":
        cv.rect(x + 22, y + 12, 4, h - 24, INK)
        cv.rect(x + 58, y + 12, 4, h - 24, INK)
        cv.rect(x + 26, y + 14, 30, 12, (255, 153, 51))
        cv.rect(x + 26, y + 26, 30, 12, (19, 136, 8))
        cv.rect(x + 62, y + 14, 30, 12, RED)
        cv.rect(x + 62, y + 26, 30, 12, NAVY)
        cv.circle(x + 41, y + 32, 5, NAVY)
    elif kind == "plane":
        cv.rect(x + 8, cy - 4, w - 16, 8, fg)
        cv.rect(x + w // 2 - 6, y + 8, 12, h - 16, fg)
        cv.rect(x + w - 14, cy - 8, 10, 16, NAVY)
    elif kind == "chart":
        cv.line(x + 8, y + h - 10, x + w - 8, y + h - 10, INK)
        cv.line(x + 8, y + 8, x + 8, y + h - 10, INK)
        pts = [(x + 12, y + 14), (x + 26, y + 22), (x + 40, y + 18),
               (x + 54, y + 32), (x + 68, y + 40)]
        for a, b in zip(pts, pts[1:]):
            cv.line(a[0], a[1], b[0], b[1], RED)
            cv.line(a[0], a[1] + 1, b[0], b[1] + 1, RED)
    elif kind == "drone":
        cv.rect(x + 18, cy - 6, w - 36, 12, fg)
        cv.circle(x + 16, cy, 8, INK)
        cv.circle(x + w - 16, cy, 8, INK)
        cv.circle(cx, cy - 2, 8, NAVY)
        cv.rect(cx - 2, cy + 4, 4, 10, RED)
    elif kind == "ball":
        cv.circle(cx, cy, 22, PAPER)
        cv.circle(cx, cy, 22, INK, fill=False)
        cv.circle(cx, cy, 6, INK)
        for px, py in [(cx - 14, cy - 10), (cx + 14, cy - 10),
                       (cx - 16, cy + 10), (cx + 16, cy + 10), (cx, cy - 18)]:
            cv.circle(px, py, 3, INK)
    elif kind == "court":
        cv.rect(x + 12, y + h - 12, w - 24, 6, fg)
        for i in range(3):
            cv.rect(x + 18 + i * 18, y + 16, 6, h - 30, NAVY)
        cv.rect(x + 10, y + 10, w - 20, 8, fg)
    elif kind == "stamp":
        cv.rect(x + 14, y + 10, w - 28, h - 20, PAPER)
        cv.outline(x + 14, y + 10, w - 28, h - 20, INK)
        cv.circle(cx, cy, 14, RED, fill=False)
        cv.circle(cx, cy, 11, RED, fill=False)
        cv.text(x + 24, cy - 3, 1, "EU", RED, bold=True)
    elif kind == "bars":
        for i, bh in enumerate([12, 22, 16, 30, 24]):
            cv.rect(x + 10 + i * 13, y + h - 8 - bh, 9, bh,
                    TEAL if i % 2 == 0 else NAVY)
    elif kind == "gauge":
        cv.line(x + 10, y + h - 12, x + w - 10, y + 12, TEAL)
        cv.line(x + 10, y + h - 12, x + w - 10, y + 12, TEAL)
        cv.line(x + 10, y + 12, x + w - 10, y + h - 12, RED)
        cv.circle(cx, cy, 5, INK)


# ---- page ------------------------------------------------------------
def draw_page(cv):
    MX = 24
    CW = W - 2 * MX  # 976

    # top rules
    cv.hline(0, 0, W, NAVY)
    cv.rect(0, 1, W, 2, RED)

    # --- masthead -----------------------------------------------------
    cv.text(MX, 10, 1, "THE WORLD ON ONE PAGE", RED, bold=True)
    right = "26 STORIES - 6 REGIONS - ONE DAY"
    cv.text(W - MX - text_width(right, 1), 10, 1, right, NAVY, bold=True)
    cv.text_center(0, 24, W, 6, "THE WORLD TODAY", INK, bold=True)
    cv.hline(MX, 76, CW, INK)
    cv.text_center(0, 80, W, 3, "MONDAY 23 NOVEMBER 2026", NAVY, bold=True)
    cv.hline(MX, 104, CW, INK)
    sub = "EUROPE 8 - MIDDLE EAST 7 - ASIA 6 - AMERICAS 3 - AFRICA 1 - GLOBAL 1"
    cv.text_center(0, 108, W, 1, sub, GRAY)

    # --- timeline strip ----------------------------------------------
    y = 124
    cv.rect(MX, y, 96, 14, RED)
    cv.text(MX + 6, y + 4, 1, "THE DAY IN UTC", WHITE, bold=True)
    cell_w = (CW - 96) // 8
    for i, (t, txt) in enumerate(TIMELINE):
        cx0 = MX + 96 + i * cell_w
        cv.text(cx0 + 4, y + 2, 1, t, RED, bold=True)
        lines = wrap_text(txt, 1, cell_w - 8)
        cv.para(cx0 + 4, y + 12, 1, cell_w - 8, lines[:2], INK, leading=9)
        if i:
            cv.vline(cx0, y, 30, LINE)
    y = 160
    cv.hline(MX, y, CW, NAVY)

    # --- numbers strip ------------------------------------------------
    y = 166
    cv.text(MX, y + 8, 1, "THE DAY", NAVY, bold=True)
    cv.text(MX, y + 18, 1, "IN NUMBERS", NAVY, bold=True)
    num_w = (CW - 96) // 6
    for i, (num, label) in enumerate(NUMBERS):
        nx = MX + 96 + i * num_w
        cv.text(nx + 6, y + 2, 3, num, RED, bold=True)
        lines = wrap_text(label, 1, num_w - 10)
        cv.para(nx + 6, y + 26, 1, num_w - 10, lines[:2], GRAY, leading=9)
        if i:
            cv.vline(nx, y, 38, LINE)
    y = 208
    cv.hline(MX, y, CW, NAVY)

    # --- hero stories: 2 x 2 -----------------------------------------
    hy = 216
    hw = (CW - 8) // 2
    hh = 128
    for idx, st in enumerate(HEROES):
        hx = MX + (idx % 2) * (hw + 8)
        hyy = hy + (idx // 2) * (hh + 8)
        cv.rect(hx, hyy, hw, hh, PAPER)
        cv.outline(hx, hyy, hw, hh, LINE)
        cv.rect(hx, hyy, 4, hh, RED if idx % 2 == 0 else NAVY)
        ax, ay, aw, ah = hx + 12, hyy + 10, 108, hh - 20
        draw_art(cv, st["art"], ax, ay, aw, ah, NAVY, (232, 226, 208))
        tx = hx + 132
        tw = hw - 144
        cv.text(tx, hyy + 10, 1, st["tag"], NAVY, bold=True)
        kx = tx + text_width(st["tag"], 1) + 8
        cv.rect(kx, hyy + 9, text_width(st["kind"], 1) + 8, 11,
                RED if st["kind"] == "CLAIM" else TEAL)
        cv.text(kx + 4, hyy + 10, 1, st["kind"], WHITE, bold=True)
        head_lines = wrap_text(st["head"], 2, tw)
        cv.para(tx, hyy + 26, 2, tw, head_lines[:2], INK, leading=16, bold=True)
        body_lines = wrap_text(st["body"], 1, tw)
        cv.para(tx, hyy + 26 + 16 * min(2, len(head_lines)) + 4, 1, tw,
                body_lines[:4], INK, leading=9)
        cv.text(tx, hyy + hh - 14, 1, "Source: " + st["src"], GRAY)

    # --- secondary stories: 4 x 2 -------------------------------------
    sy = hy + 2 * hh + 8 + 10
    sw = (CW - 3 * 8) // 4
    sh = 104
    for idx, st in enumerate(SECONDARY):
        sx = MX + (idx % 4) * (sw + 8)
        syy = sy + (idx // 4) * (sh + 8)
        cv.rect(sx, syy, sw, sh, PAPER)
        cv.outline(sx, syy, sw, sh, LINE)
        cv.rect(sx, syy, sw, 16, NAVY)
        cv.text(sx + 6, syy + 5, 1, st["tag"], WHITE, bold=True)
        kw = text_width(st["kind"], 1) + 8
        cv.rect(sx + sw - kw - 4, syy + 3, kw, 11,
                RED if st["kind"] == "CLAIM" else
                (GOLD if st["kind"] == "FORECAST" else TEAL))
        cv.text(sx + sw - kw, syy + 4, 1, st["kind"], WHITE, bold=True)
        ax, ay, aw, ah = sx + 6, syy + 22, 56, 40
        draw_art(cv, st["art"], ax, ay, aw, ah, NAVY, (232, 226, 208))
        tx = sx + 68
        tw = sw - 74
        head_lines = wrap_text(st["head"], 1, tw)
        cv.para(tx, syy + 22, 1, tw, head_lines[:3], INK, leading=9, bold=True)
        body_lines = wrap_text(st["body"], 1, sw - 12)
        cv.para(sx + 6, syy + 66, 1, sw - 12, body_lines[:2], GRAY, leading=9)
        cv.text(sx + 6, syy + sh - 12, 1, st["src"], GRAY)

    # --- map + also list ----------------------------------------------
    my = sy + 2 * sh + 8 + 10
    mh = 196
    cv.hline(MX, my - 6, CW, NAVY)
    cv.text(MX, my + 2, 2, "WHERE IT HAPPENED", RED, bold=True)
    cv.text(MX + 396, my + 2, 2, "ALSO ON MONDAY 23 NOVEMBER", RED, bold=True)
    map_x, map_y, map_w, map_h = MX, my + 26, 380, 128
    cv.rect(map_x, map_y, map_w, map_h, SEA)
    cv.outline(map_x, map_y, map_w, map_h, LINE)

    def lonlat(lon, lat):
        return (map_x + int((lon + 180) / 360 * map_w),
                map_y + int((90 - lat) / 180 * map_h))

    for cont in CONTINENTS:
        cv.poly([lonlat(lon, lat) for lon, lat in cont], LAND)
    # display offsets so the four north-west Europe pins do not stack
    PIN_DX = {5: (3, -5), 8: (-7, 3), 10: (-3, -8), 12: (7, 5)}
    for num, name, lon, lat in MAP_PINS:
        px, py = lonlat(lon, lat)
        dx, dy = PIN_DX.get(num, (0, 0))
        px, py = px + dx, py + dy
        cv.circle(px, py, 7, RED)
        cv.circle(px, py, 7, WHITE, fill=False)
        lbl = str(num)
        cv.text(px - text_width(lbl, 1) // 2, py - 3, 1, lbl, WHITE, bold=True)
    # map legend
    ly = map_y + map_h + 6
    for i, (num, name, lon, lat) in enumerate(MAP_PINS):
        lx = map_x + (i % 4) * 96
        lyy = ly + (i // 4) * 10
        cv.text(lx, lyy, 1, "%d %s" % (num, name), INK)

    # also list: 2 columns x 7
    ax0 = MX + 396
    col_w = (CW - 396) // 2
    for i, item in enumerate(ALSO):
        col = i // 7
        row = i % 7
        ix = ax0 + col * col_w
        iy = my + 28 + row * 22
        lbl = str(i + 1)
        if len(lbl) == 1:
            cv.circle(ix + 5, iy + 4, 7, TEAL)
            cv.text(ix + 3, iy + 1, 1, lbl, WHITE, bold=True)
        else:
            cv.rect(ix - 2, iy - 3, 16, 14, TEAL)
            cv.text(ix + 1, iy + 1, 1, lbl, WHITE, bold=True)
        lines = wrap_text(item, 1, col_w - 22)
        cv.para(ix + 16, iy, 1, col_w - 22, lines[:2], INK, leading=9)

    # --- date check ----------------------------------------------------
    dy = my + mh + 10
    cv.rect(MX, dy, CW, 52, (250, 238, 226))
    cv.outline(MX, dy, CW, 52, RED)
    cv.rect(MX, dy, 96, 14, RED)
    cv.text(MX + 6, dy + 4, 1, "DATE CHECK", WHITE, bold=True)
    lines = wrap_text(DATE_CHECK, 1, CW - 16)
    cv.para(MX + 8, dy + 18, 1, CW - 16, lines[:3], INK, leading=9)

    # --- legend + footer -----------------------------------------------
    fy = dy + 52 + 8
    cv.hline(MX, fy, CW, NAVY)
    cv.text(MX, fy + 6, 1, "CONFIRMED", TEAL, bold=True)
    cv.text(MX + 62, fy + 6, 1, "on the record", GRAY)
    cv.text(MX + 150, fy + 6, 1, "CLAIM", RED, bold=True)
    cv.text(MX + 190, fy + 6, 1, "one side's account", GRAY)
    cv.text(MX + 320, fy + 6, 1, "FORECAST", GOLD, bold=True)
    cv.text(MX + 378, fy + 6, 1, "expected, not yet happened", GRAY)
    cv.text(MX + 560, fy + 6, 1, "REPORTED", NAVY, bold=True)
    cv.text(MX + 616, fy + 6, 1, "news report", GRAY)
    cv.text(MX, fy + 18, 1,
            "Sources: Reuters, AP, BBC, AFP, Dow Jones, Bloomberg, Al Jazeera, "
            "Press TV, The Hindu.", GRAY)
    cv.text(MX, fy + 28, 1,
            "All stories happened or were first reported on Monday 23 November "
            "2026. See DATE CHECK for events left out.", GRAY)


# ---- PNG encoder -----------------------------------------------------
def png_bytes(cv):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    cv = Canvas()
    draw_page(cv)
    data = png_bytes(cv)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
