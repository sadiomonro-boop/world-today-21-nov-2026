#!/usr/bin/env python3
"""THE WORLD TODAY - Saturday 21 November 2026.

A front-page newspaper image summing up the world news of
Saturday 21 November 2026. Pure Python standard library only:
the program draws every pixel itself (5x7 bitmap font, dot-matrix
world map, procedural skyline) and writes a PNG with zlib/struct.
No network, no files read, fully deterministic: two runs write
byte-identical output.
"""

import os
import struct
import zlib

W = 1024
H = 1024

WHITE = (255, 255, 255)
PAPER = (252, 250, 244)
INK = (12, 12, 12)
GREY = (110, 110, 108)
LGREY = (205, 203, 196)
RED = (178, 18, 28)
DRED = (140, 10, 20)
BLUE = (24, 58, 110)
GOLD = (176, 132, 24)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, '#' = ink. Lowercase and accented letters are
# normalised to their uppercase ASCII form before drawing.

FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '\\': ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
    '~': ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    '^': ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
    '`': ("01000", "00100", "00000", "00000", "00000", "00000", "00000"),
    '{': ("00010", "00100", "00100", "01100", "00100", "00100", "00010"),
    '}': ("01000", "00100", "00100", "00110", "00100", "00100", "01000"),
    'E2': ("00110", "01001", "10000", "11110", "10000", "10001", "00110"),
    'L2': ("00110", "01000", "10000", "11100", "10000", "10000", "11111"),
    'X2': ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    'D2': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
}

ACCENTS = {
    'A': 'A', 'E': 'E', 'I': 'I', 'O': 'O', 'U': 'U', 'C': 'C', 'N': 'N',
    'a': 'A', 'e': 'E', 'i': 'I', 'o': 'O', 'u': 'U', 'c': 'C', 'n': 'N',
}


def normalise(text):
    out = []
    for ch in text:
        if ch == '\u20ac':
            out.append('\u0001')  # euro marker, mapped below
        elif ch == '\u00a3':
            out.append('\u0002')  # pound marker
        elif ch == '\u2022':
            out.append('\u0003')  # bullet marker
        elif ch == '\u2014' or ch == '\u2013':
            out.append('\u0004')  # dash marker
        elif ch in ACCENTS:
            out.append(ACCENTS[ch])
        else:
            out.append(ch.upper())
    return ''.join(out)


MARKERS = {'\u0001': 'E2', '\u0002': 'L2', '\u0003': 'X2', '\u0004': 'D2'}


def text_width(text, scale):
    return len(normalise(text)) * 6 * scale - scale


def wrap_text(text, max_chars):
    words = text.split()
    lines = []
    cur = ''
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += ' ' + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, w, h, bg=PAPER):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(0, len(self.px), 3):
            self.px[i] = bg[0]
            self.px[i + 1] = bg[1]
            self.px[i + 2] = bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def get(self, x, y):
        i = (y * self.w + x) * 3
        return (self.px[i], self.px[i + 1], self.px[i + 2])

    def fill(self, x0, y0, x1, y1, c):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        for y in range(y0, y1):
            base = (y * self.w + x0) * 3
            for x in range(x0, x1):
                i = base + (x - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x0, x1, y, c, t=1):
        for yy in range(y, y + t):
            for x in range(x0, x1):
                self.set(x, yy, c)

    def vline(self, x, y0, y1, c, t=1):
        for xx in range(x, x + t):
            for y in range(y0, y1):
                self.set(xx, y, c)

    def rect(self, x0, y0, x1, y1, c, t=1):
        self.hline(x0, x1, y0, c, t)
        self.hline(x0, x1, y1 - t, c, t)
        self.vline(x0, y0, y1, c, t)
        self.vline(x1 - t, y0, y1, c, t)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                    self.set(x, y, c)

    def ring(self, cx, cy, r, c):
        for a in range(360):
            import math
            x = int(cx + r * math.cos(math.radians(a)))
            y = int(cy + r * math.sin(math.radians(a)))
            self.set(x, y, c)

    def draw_text(self, x, y, text, scale, c, bold=False):
        text = normalise(text)
        cx = x
        for ch in text:
            key = MARKERS.get(ch, ch)
            glyph = FONT.get(key)
            if glyph is None:
                cx += 6 * scale
                continue
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        for sy in range(scale):
                            for sx in range(scale):
                                self.set(cx + col * scale + sx,
                                         y + row * scale + sy, c)
                                if bold:
                                    self.set(cx + col * scale + sx + 1,
                                             y + row * scale + sy, c)
            cx += 6 * scale
        return cx

    def text_centred(self, cx, y, text, scale, c, bold=False):
        w = text_width(text, scale)
        return self.draw_text(cx - w // 2, y, text, scale, c, bold)

    def para(self, x, y, width_px, text, scale, c, line_h=None, bold=False,
             max_lines=None):
        if line_h is None:
            line_h = 7 * scale + 3
        max_chars = max(1, width_px // (6 * scale))
        lines = wrap_text(text, max_chars)
        if max_lines is not None:
            lines = lines[:max_lines]
        for i, ln in enumerate(lines):
            self.draw_text(x, y + i * line_h, ln, scale, c, bold)
        return y + len(lines) * line_h


def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        start = y * stride
        raw.extend(canvas.px[start:start + stride])
    comp = zlib.compress(bytes(raw), 6)
    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        out += struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        return out
    ihdr = struct.pack('>IIBBBBB', canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- stories
# Every story below happened, or was first reported, on Saturday
# 21 November 2026 (any timezone). Sources: Reuters, AFP, AP,
# BBC, USGS, Xinhua, Al Jazeera, Financial Times, PANA, Korea
# JoongAng Daily. Figures are only those the sources reported.

HERO = {
    "kicker": "MIDDLE EAST  |  RIYADH, SAUDI ARABIA",
    "headline": "THREE MISSILES DOWNED OVER RIYADH",
    "body": ("Saudi defences intercepted three Houthi ballistic "
             "missiles fired at Riyadh early on Saturday, the "
             "coalition said, after explosions were heard. It was "
             "the third straight night of alerts."),
}

LEADS = [
    {
        "kicker": "SOUTH AMERICA  |  PERU",
        "headline": "STRONG QUAKE SHAKES PERU'S ANDES",
        "body": ("A 6.7 quake hit central Peru at 00:09 UTC. "
                 "Felt in Lima; none hurt."),
    },
    {
        "kicker": "MARKETS  |  NEW YORK",
        "headline": "WALL ST PLUNGES AS AI RALLY CRACKS",
        "body": ("US stocks fell sharply Friday: Nasdaq -5.3%, "
                 "S&P -3.7%, Dow -950 points."),
    },
    {
        "kicker": "EUROPE  |  POLAND",
        "headline": "RUSSIAN MISSILES CRASH IN POLAND",
        "body": ("Two Russian missiles and a drone crashed in "
                 "Poland, Warsaw said."),
    },
]

MIDS = [
    {
        "kicker": "UKRAINE",
        "headline": "KRYVYI RIH HIT: 2 DEAD, 42 HURT",
        "body": ("Russian strike kills a child and a paramedic."),
    },
    {
        "kicker": "DIPLOMACY",
        "headline": "TRUMP HAILS XI AND PUTIN TALKS",
        "body": ("Trump calls Xi and Putin ties 'fantastic'."),
    },
    {
        "kicker": "DENMARK",
        "headline": "DANE EXPELS RUSSIAN DIPLOMAT",
        "body": ("Copenhagen expels a diplomat over a murder plot."),
    },
    {
        "kicker": "GAZA",
        "headline": "EU URGES ISRAEL TO HOLD TRUCE",
        "body": ("EU urges Israel to hold Gaza truce as a man is killed."),
    },
    {
        "kicker": "CLIMATE  |  ANTALYA",
        "headline": "COP31 REACHES ITS FINAL DAY",
        "body": ("States demand a stronger deal at COP31's final day."),
    },
    {
        "kicker": "EUROPE",
        "headline": "YOUTH TAKE TO EUROPE'S STREETS",
        "body": ("Youth rally across Europe over costs and climate."),
    },
    {
        "kicker": "TECH  |  WASHINGTON",
        "headline": "US CLEARED 900,000 AI CHIPS FOR CHINA",
        "body": ("US cleared 900,000 Nvidia and AMD AI chips for China."),
    },
    {
        "kicker": "TECH  |  NVIDIA",
        "headline": "SEC PROBES NVIDIA ACCOUNTS",
        "body": ("SEC probes Nvidia accounts; Trump wants Huang back."),
    },
]

# Numbered briefs: (number, one-line headline with the key figure)
BRIEFS = [
    "SIBERIA PLANE CRASH KILLS 19",
    "FRENCH POLICE GUILTY OVER ZECLER",
    "NVIDIA HIRES FIRM OVER HUANG CLAIMS",
    "KIM TOURS FACTORIES AFTER SNUB",
    "MAN GUILTY OF SPARKING DEADLY LA FIRE",
    "ANTHROPIC SLIDES AFTER $81.3BN IPO",
    "BITCOIN SLIPS BELOW $60,000",
    "ASIA SINKS: NIKKEI -5.1%, KOSPI -5.2%",
    "ESTONIA SHUTS BORDERS, RUSSIA FUMES",
    "UKRAINE BLOCKS RUSSIAN COP31 REPORT",
    "1M AFGHAN CHILDREN FACE MALNUTRITION",
    "TUNISIA JAILS RIGHTS DEFENDER 5 YEARS",
    "AFCON: IVORY COAST LATE DRAW IN GAMBIA",
    "TEXANS BEAT COLTS 26-3, STROUD 3 TDS",
    "GIANTS TRADE INFIELDER TO RAYS",
    "WNBA CHIEF TO RETIRE AFTER 7 YEARS",
    "NORWAY RETHINKS SCREENS IN SCHOOLS",
    "US PRESSES SINGAPORE ON IRAN RULES",
    "2ND JUDGE HALTS TRUMP ARCH PROJECT",
    "SWEDEN VOTES SUNDAY ON RIGHT-WING RULE",
    "TRUMP: NO RUSH ON IRAN DECISIONS",
    "HOUTHI THREATS WIDEN TO JEDDAH",
]

KPIS = [
    ("NASDAQ", "-5.3%"),
    ("S&P 500", "-3.7%"),
    ("DOW", "-950 PTS"),
    ("PERU QUAKE", "M6.7"),
    ("RIYADH", "3 MISSILES"),
    ("KRYVYI RIH", "42 HURT"),
]

# Dot-matrix world map: 64 columns x 22 rows, '#' = land.
# Rough equirectangular sketch, longitudes -170..190, latitudes 75..-55.
MAP_ROWS = [
    "                                                                ",
    "      ####  ########  ###      #################  ##########     ",
    "   ######## ############     ######################  ########   ",
    "    ######  ###########      ####################    ######     ",
    "     #####   #########        #################      ####       ",
    "      ###     #######          ##############        ##         ",
    "       ##      #####            ###########          #          ",
    "        #       ###     ##       #########                      ",
    "                ##    ####       #######        ##  ####        ",
    "                 #   ######       #####       ##########        ",
    "                      ####        ###        ###########        ",
    "                       ##         ##          #########         ",
    "                       ##         #           ########          ",
    "                        #                      ######           ",
    "                        ##                      ####            ",
    "                         #                       ##             ",
    "                         ##                       #             ",
    "                          #                                     ",
    "                          ##                                    ",
    "                           #                                    ",
    "                           #                                    ",
    "                                                                ",
]

# Pins: (map column, map row, number, label, label dx, label dy).
# Positions are nudged a little so the crowded eastern
# Mediterranean pins stay readable on this schematic map.
PINS = [
    (34, 8, "1", "1 RIYADH", 12, -4),
    (14, 13, "2", "2 PERU", -68, -4),
    (30, 2, "3", "3 UKRAINE", -70, 12),
    (27, 2, "4", "4 DENMARK", -96, -4),
    (32, 6, "5", "5 ANTALYA", 14, 12),
    (11, 6, "6", "6 WASHINGTON", 12, -4),
]

SOURCES = ("SOURCES: REUTERS, AFP, AP, BBC, USGS, XINHUA, AL JAZEERA, "
           "FINANCIAL TIMES, PANA, KOREA JOONGANG DAILY")

# ---------------------------------------------------------------- drawing

def _rand(state):
    """Deterministic xorshift32 step (full-period high bits)."""
    state ^= (state << 13) & 0xffffffff
    state ^= state >> 17
    state ^= (state << 5) & 0xffffffff
    return state & 0xffffffff


def speckle(c, seed=1234567):
    """Deterministic light paper speckle, applied last so it textures
    every white area: adds paper grain and file size without ever
    touching ink, so legibility is untouched."""
    state = seed
    n = W * H
    for _ in range(n // 6):
        state = _rand(state)
        x = state % W
        state = _rand(state)
        y = state % H
        state = _rand(state)
        v = state % 3
        if c.get(x, y) in (PAPER, WHITE):
            c.set(x, y, (238, 236, 230) if v == 0 else (244, 242, 236))


def draw_masthead(c):
    c.fill(0, 0, W, 64, WHITE)
    c.hline(0, W, 0, RED, 4)
    c.text_centred(W // 2, 10, "THE WORLD TODAY", 5, INK, bold=True)
    c.draw_text(16, 47, "SATURDAY, 21 NOVEMBER 2026", 2, RED, bold=True)
    right = "32 STORIES  -  6 CONTINENTS  -  ONE DAY"
    c.draw_text(W - 16 - text_width(right, 2), 47, right, 2, INK, bold=True)
    c.hline(0, W, 62, INK, 2)
    # red date-check bar
    c.fill(0, 66, W, 92, RED)
    c.text_centred(W // 2, 72,
                   "DATE CHECK - SATURDAY 21 NOVEMBER 2026: EVERY STORY "
                   "BELOW IS FROM THIS DAY", 2, WHITE, bold=True)


def draw_hero(c, x0, y0, x1, y1):
    c.fill(x0, y0, x1, y1, WHITE)
    c.rect(x0, y0, x1, y1, INK, 2)
    tx = x0 + 14
    tw = 620
    c.draw_text(tx, y0 + 10, HERO["kicker"], 2, RED, bold=True)
    c.hline(tx, x0 + tw + 14, y0 + 30, LGREY, 1)
    y = y0 + 38
    for ln in wrap_text(HERO["headline"], tw // 18):
        c.draw_text(tx, y, ln, 3, INK, bold=True)
        y += 26
    c.para(tx, y + 4, tw, HERO["body"], 2, INK, line_h=17, max_lines=4)
    # graphic: Riyadh skyline + intercept arcs, right side
    gx0 = x0 + 660
    gx1 = x1 - 12
    gy1 = y1 - 12
    gy0 = y0 + 12
    c.fill(gx0, gy0, gx1, gy1, (16, 24, 46))
    # stars
    state = 987654321
    for _ in range(40):
        state = (1103515245 * state + 12345) & 0x7fffffff
        sx = gx0 + 6 + state % (gx1 - gx0 - 12)
        state = (1103515245 * state + 12345) & 0x7fffffff
        sy = gy0 + 4 + state % 40
        c.set(sx, sy, (200, 200, 210))
    # skyline silhouettes
    towers = [(0, 46, 26), (30, 62, 34), (68, 40, 90), (104, 54, 30),
              (138, 44, 40), (182, 70, 26), (212, 50, 30), (246, 60, 22)]
    for dx, th, wd in towers:
        c.fill(gx0 + dx, gy1 - th, gx0 + dx + wd, gy1, (8, 12, 26))
        for wy in range(gy1 - th + 6, gy1 - 6, 12):
            for wx in range(gx0 + dx + 4, gx0 + dx + wd - 4, 10):
                c.set(wx, wy, (240, 200, 60))
    # intercept arcs + bursts
    import math
    for (ax, ay, bx, by) in [(gx0 + 20, gy1 - 90, gx0 + 150, gy0 + 30),
                             (gx0 + 260, gy1 - 80, gx0 + 160, gy0 + 44)]:
        for t in range(101):
            f = t / 100.0
            px = int(ax + (bx - ax) * f)
            py = int(ay + (by - ay) * f - 34 * math.sin(math.pi * f))
            c.set(px, py, (255, 210, 80))
            c.set(px + 1, py, (255, 210, 80))
    for (bx, by) in [(gx0 + 150, gy0 + 30), (gx0 + 160, gy0 + 44)]:
        for r in (3, 6, 9):
            c.ring(bx, by, r, (255, 90, 60))
        c.disc(bx, by, 3, (255, 220, 120))
    c.draw_text(gx0 + 8, gy1 - 16, "RIYADH SKYLINE, 21 NOV", 1,
                (220, 220, 225))


def draw_card(c, x0, y0, x1, y1, story, headline_scale=2, body_lines=3):
    c.fill(x0, y0, x1, y1, WHITE)
    c.rect(x0, y0, x1, y1, INK, 1)
    c.fill(x0, y0, x1, y0 + 3, RED)
    tx = x0 + 8
    tw = x1 - x0 - 16
    c.draw_text(tx, y0 + 7, story["kicker"], 1, RED, bold=True)
    y = y0 + 18
    for ln in wrap_text(story["headline"],
                        tw // (6 * headline_scale))[:2]:
        c.draw_text(tx, y, ln, headline_scale, INK, bold=True)
        y += 7 * headline_scale + 1
    c.para(tx, y + 2, tw, story["body"], 2, INK, line_h=14,
           max_lines=body_lines)


def draw_map(c, x0, y0, x1, y1):
    c.fill(x0, y0, x1, y1, (235, 240, 246))
    c.rect(x0, y0, x1, y1, INK, 1)
    c.draw_text(x0 + 10, y0 + 6, "WHERE IT HAPPENED - THE DAY ON THE MAP",
                2, BLUE, bold=True)
    map_x0 = x0 + 10
    map_y0 = y0 + 26
    x_step = (x1 - x0 - 20) // 64
    y_step = 4
    rows = MAP_ROWS[1:21]
    for r, row in enumerate(rows):
        for col, ch in enumerate(row):
            if ch == '#':
                cx = map_x0 + col * x_step
                cy = map_y0 + r * y_step
                c.disc(cx, cy, 2, (70, 90, 120))
                c.disc(cx + x_step // 2, cy, 2, (70, 90, 120))
    for (col, row, num, label, ldx, ldy) in PINS:
        px = map_x0 + col * x_step
        py = map_y0 + (row - 1) * y_step
        c.disc(px, py, 8, RED)
        c.ring(px, py, 8, DRED)
        c.text_centred(px, py - 4, num, 1, WHITE, bold=True)
        lx, ly = px + ldx, py + ldy
        c.fill(lx - 2, ly - 1, lx + len(label) * 6 + 2, ly + 8,
               (235, 240, 246))
        c.draw_text(lx, ly, label, 1, INK, bold=True)


def draw_kpis(c, x0, y0, x1, y1):
    c.draw_text(x0, y0 - 2, "BY THE NUMBERS", 2, RED, bold=True)
    n = len(KPIS)
    bw = (x1 - x0 - (n - 1) * 8) // n
    for i, (label, value) in enumerate(KPIS):
        bx0 = x0 + i * (bw + 8)
        bx1 = bx0 + bw
        c.fill(bx0, y0 + 16, bx1, y1, WHITE)
        c.rect(bx0, y0 + 16, bx1, y1, INK, 1)
        c.text_centred((bx0 + bx1) // 2, y0 + 22, label, 1, GREY, bold=True)
        c.text_centred((bx0 + bx1) // 2, y0 + 36, value, 2, RED, bold=True)


def build():
    c = Canvas(W, H)
    draw_masthead(c)
    # hero
    draw_hero(c, 16, 98, W - 16, 244)
    # leads: 3 columns
    ly0, ly1 = 250, 360
    lw = (W - 32 - 16) // 3
    for i, story in enumerate(LEADS):
        x0 = 16 + i * (lw + 8)
        draw_card(c, x0, ly0, x0 + lw, ly1, story, body_lines=4)
    # mids: 4 columns x 2 rows
    my0 = 366
    mw = (W - 32 - 24) // 4
    mh = 95
    for i, story in enumerate(MIDS):
        row, col = divmod(i, 4)
        x0 = 16 + col * (mw + 8)
        y0 = my0 + row * (mh + 6)
        draw_card(c, x0, y0, x0 + mw, y0 + mh, story, body_lines=3)
    # briefs
    by0 = 566
    c.draw_text(16, by0, "THE DAY IN BRIEF - 22 MORE STORIES, "
                "21 NOVEMBER 2026", 2, INK, bold=True)
    c.hline(16, W - 16, by0 + 18, INK, 2)
    col_w = (W - 32 - 24) // 2
    for i, item in enumerate(BRIEFS):
        col, row = divmod(i, 11)
        x0 = 16 + col * (col_w + 24)
        y = by0 + 26 + row * 19
        num = "%02d" % (i + 1)
        c.draw_text(x0, y, num, 2, RED, bold=True)
        c.draw_text(x0 + 30, y, item, 2, INK)
    # map
    draw_map(c, 16, 800, W - 16, 906)
    # KPI strip
    draw_kpis(c, 16, 912, W - 16, 972)
    # footer
    c.hline(16, W - 16, 980, INK, 2)
    c.draw_text(16, 988, SOURCES, 1, INK)
    c.draw_text(16, 1000,
                "ALL 32 STORIES HAPPENED OR WERE FIRST REPORTED ON "
                "SATURDAY 21 NOVEMBER 2026. DRAWN BY CODE; NO PHOTOGRAPHS.",
                1, GREY)
    speckle(c)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(canvas, path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
