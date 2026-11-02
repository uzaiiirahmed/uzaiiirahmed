"""ASCII terminal README assets.

    python .github/scripts/assets.py              -> assets/ (header, link buttons)
    python .github/scripts/assets.py morph out.svg -> the animated profile card: a
        Windows 98 desktop where a DOS prompt runs `launch eye.exe` (a window pops
        up with a 3D ASCII eye) and `open about.txt` (a Notepad window pops up and
        matrix rain paints the name in), then everything closes and replays.
Logos are from Simple Icons (CC0).
"""
import os
import random
import re
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "assets")

USER = "uzaiiirahmed"
PROMPT = "C:\\Users\\uzair>"
W = 851
MONO = "ui-monospace,SFMono-Regular,'Cascadia Mono',Menlo,Consolas,monospace"
BG, DIM, MID, HI = "#0a0505", "#9e1c1c", "#e03434", "#ff5c5c"
FS = 13
CW = FS * 0.6          # forced glyph advance (textLength keeps it exact)
LINE = 22
TYPE = 0.045           # seconds per typed character

LINKS = [("globe", "portfolio", "https://uzair-ahmed.netlify.app"),
         ("linkedin", "linkedin", "https://linkedin.com/in/uzair-ahmed-381149314"),
         ("instagram", "instagram", "https://instagram.com/uzaiiirahmed")]
# "UZAIR AHMED" in the figlet font "colossal"
NAME = [
    '888     8888888888888P       d888888888888888888b.           d8888888    888888b     d88888888888888888888b.  ',
    '888     888      d88P       d88888  888  888   Y88b         d88888888    8888888b   d8888888       888  "Y88b ',
    '888     888     d88P       d88P888  888  888    888        d88P888888    88888888b.d88888888       888    888 ',
    '888     888    d88P       d88P 888  888  888   d88P       d88P 8888888888888888Y88888P8888888888   888    888 ',
    '888     888   d88P       d88P  888  888  8888888P"       d88P  888888    888888 Y888P 888888       888    888 ',
    '888     888  d88P       d88P   888  888  888 T88b       d88P   888888    888888  Y8P  888888       888    888 ',
    'Y88b. .d88P d88P       d8888888888  888  888  T88b     d8888888888888    888888   "   888888       888  .d88P ',
    ' "Y88888P" d8888888888d88P     8888888888888   T88b   d88P     888888    888888       88888888888888888888P"  ',
]
NAME_SHADES = ["#ffd6d6", "#ffb3a3", "#ff8a7a", "#ff5c5c", "#f04a44", "#e03434", "#c42828", "#9e1c1c"]

CLIENT_Y = 25  # top of the window's client area
UI_FONT = "Tahoma,'MS Sans Serif',Verdana,Arial,sans-serif"


def bevel(x, y, w, h, tl, br, tl2=None, br2=None):
    """Win9x 3D edge: light top/left, dark bottom/right, optionally doubled."""
    out = (f'<path d="M{x} {y + h - 1} V{y} H{x + w - 1}" stroke="{tl}"/>'
           f'<path d="M{x} {y + h - .5} H{x + w - .5} V{y}" stroke="{br}"/>')
    if tl2:
        out += bevel(x + 1, y + 1, w - 2, h - 2, tl2, br2)
    return out


def win_frame(W, H, title):
    """Windows 98 window chrome: grey bevelled frame, gradient caption with
    the app icon and a bold title, and the three square caption buttons."""
    tb = CLIENT_Y - 7  # caption height
    bx = lambda x, glyph: (f'<rect x="{x}" y="5" width="16" height="14" fill="#c0c0c0"/>'
                           + bevel(x + .5, 5.5, 16, 14, "#fff", "#000", "#dfdfdf", "#808080") + glyph)
    x_cls, x_max, x_min = W - 22, W - 40, W - 56
    return (f'<g shape-rendering="crispEdges" fill="none" stroke-width="1">'
            f'<rect width="{W}" height="{H}" fill="#c0c0c0"/>'
            + bevel(.5, .5, W, H, "#dfdfdf", "#000", "#fff", "#808080")
            + f'<defs><linearGradient id="cap"><stop offset="0" stop-color="#800000"/>'
            f'<stop offset="1" stop-color="#d04848"/></linearGradient></defs>'
            f'<rect x="3" y="3" width="{W - 6}" height="{tb}" fill="url(#cap)"/>'
            # app icon: a little MS-DOS prompt
            f'<rect x="6" y="5" width="15" height="13" fill="#000" stroke="#c0c0c0"/>'
            f'<rect x="6.5" y="5.5" width="14" height="3" fill="#000080" stroke="none"/>'
            f'<path d="M9 12.5 h2 M12 12.5 h1" stroke="#c0c0c0"/>'
            + bx(x_min, f'<path d="M{x_min + 4} 15.5 h6 M{x_min + 4} 16.5 h6" stroke="#000"/>')
            + bx(x_max, f'<path d="M{x_max + 3.5} 7.5 h9 v7 h-9 Z M{x_max + 3.5} 8.5 h9" stroke="#000"/>')
            + bx(x_cls, f'<path d="M{x_cls + 4} 8 l7 7 M{x_cls + 5} 8 l7 7 M{x_cls + 11} 8 l-7 7 M{x_cls + 12} 8 l-7 7" '
                        f'stroke="#000" shape-rendering="auto"/>')
            # sunken client area
            + bevel(3.5, tb + 5.5, W - 6, H - tb - 8, "#808080", "#fff", "#000", "#dfdfdf")
            + f'<rect x="5" y="{tb + 7}" width="{W - 10}" height="{H - tb - 12}" fill="{BG}"/></g>'
            f'<text x="26" y="16" font-family="{UI_FONT}" font-size="11" font-weight="700" fill="#fff">{title}</text>')


def ascii_name(x, y, fs=10.5):
    w = len(NAME[0]) * fs * .6
    return "".join(f'<text x="{x}" y="{y + j * fs:.1f}" font-size="{fs}" fill="{c}" textLength="{w:.1f}" '
                   f'lengthAdjust="spacing" style="white-space:pre">{row.replace(chr(34), "&quot;")}</text>'
                   for j, (row, c) in enumerate(zip(NAME, NAME_SHADES))), len(NAME) * fs


def icon(name, x, y, size, fill):
    src = open(os.path.join(HERE, "icons", f"{name}.svg"), encoding="utf-8").read()
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    inner = re.sub(r"<title>.*?</title>", "", src.split(">", 1)[1].rsplit("</svg>", 1)[0])
    inner = re.sub(r'\sfill="[^"]*"', "", inner)
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{vb}" fill="{fill}">{inner}</svg>'


class Term:
    """Builds a terminal window whose lines type out one after another."""

    def __init__(self, title, prefix="", start=0.4, period=None, w=W):
        self.p = prefix  # keeps class/id names unique when several windows share one SVG
        self.period = period  # replay the typing every `period` seconds (None: type once)
        self.title, self.body, self.css, self.defs, self.raw = title, [], [], [], []
        self.t, self.y, self.n, self.w = start, 52, 0, w

    def _reveal(self, start, dur, steps):
        k = self.n
        self.n += 1
        if self.period:
            a, b = start / self.period * 100, (start + dur) / self.period * 100
            self.css.append(f"@keyframes {self.p}g{k}{{0%,{a:.3f}%{{transform:scaleX(0);"
                            f"animation-timing-function:steps({steps},start)}}{b:.3f}%,100%{{transform:scaleX(1)}}}}"
                            f".{self.p}r{k}{{transform-box:fill-box;transform-origin:left;"
                            f"animation:{self.p}g{k} {self.period}s infinite}}")
            return k
        self.css.append(f".{self.p}r{k}{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);"
                        f"animation:grow {dur:.2f}s steps({steps},start) {start:.2f}s forwards}}")
        return k

    def type(self, cmd, wait=0.0):
        """A prompt line where the command gets typed (`wait` s after the prompt shows)."""
        x0 = 20
        px = x0 + (len(PROMPT) + 1) * CW
        k = self._reveal(self.t, 0.01, 1)
        self.body.append(f'<g class="{self.p}r{k}"><text x="{x0}" y="{self.y}" fill="{MID}" '
                         f'textLength="{len(PROMPT) * CW:.1f}">{PROMPT}</text></g>')
        dur = max(len(cmd), 1) * TYPE
        k2 = self._reveal(self.t + 0.25 + wait, dur, len(cmd))
        self.defs.append(f'<clipPath id="{self.p}c{k2}"><rect class="{self.p}r{k2}" x="{px}" y="{self.y - FS}" '
                         f'width="{len(cmd) * CW + 1:.1f}" height="{FS + 5}"/></clipPath>')
        self.body.append(f'<text x="{px}" y="{self.y}" fill="{HI}" clip-path="url(#{self.p}c{k2})" '
                         f'textLength="{len(cmd) * CW:.1f}">{cmd}</text>')
        self.t += 0.25 + wait + dur + 0.35
        self.y += LINE

    def out(self, svg, height=LINE, pause=0.25):
        """Output that appears all at once."""
        k = self._reveal(self.t, 0.01, 1)
        self.body.append(f'<g class="{self.p}r{k}">{svg}</g>')
        self.t += pause
        self.y += height

    def embed(self, svg, height, pause=0.3):
        """Nested SVG drawn outside the theme filter (it carries its own)."""
        k = self._reveal(self.t, 0.01, 1)
        self.raw.append(f'<g class="{self.p}r{k}">{svg}</g>')
        self.t += pause
        self.y += height

    def cursor(self):
        x0 = 20
        k = self._reveal(self.t, 0.01, 1)
        cx = x0 + (len(PROMPT) + 1) * CW
        self.body.append(f'<g class="{self.p}r{k}"><text x="{x0}" y="{self.y}" fill="{MID}" '
                         f'textLength="{len(PROMPT) * CW:.1f}">{PROMPT}</text>'
                         f'<text class="blink" x="{cx}" y="{self.y}" fill="{HI}">_</text></g>')
        self.y += LINE

    def svg(self, bottom=14, h=None):
        H, W = h or self.y - LINE + bottom + 8, self.w
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>
svg{{font-size:{FS}px}}text{{font-family:{MONO};white-space:pre}}
@keyframes grow{{to{{transform:scaleX(1)}}}}
.blink{{animation:blink 1s steps(1,end) infinite}}@keyframes blink{{50%{{opacity:0}}}}
{''.join(self.css)}
</style>
<defs><filter id="glow" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="2" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>{''.join(self.defs)}</defs>
<g>{win_frame(W, H, self.title)}
<g filter="url(#glow)">{''.join(self.body)}</g></g>
{''.join(self.raw)}
</svg>"""


def header(prefix="", start=0.4, period=None):
    t = Term(f"MS-DOS Prompt - {USER}", prefix, start, period)
    t.type("whoami")
    name, nh = ascii_name(20, t.y + 4)
    t.out(name, height=nh + 18, pause=0.5)
    t.type("cat about.txt")
    for line in ["&gt; I write code to make pixels come alive.",
                 "&gt; stack: C · C++ · C# · Unity · Unreal · HTML/CSS"]:
        t.out(f'<text x="20" y="{t.y}" fill="{MID}">{line}</text>', pause=0.18)
    t.cursor()
    return t.svg()


GLYPHS = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワン0123456789:.=*+ZXE"


# luminance ramp, darkest -> brightest
RAMP = " .`'^\",:;Il!i~+_-?][}{1)(|tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
SCLERA = ["#1c1414", "#4a3838", "#8c7272", "#c4a8a8", "#ecdcdc"]
IRIS = ["#2e0707", "#7a1414", "#c42828", "#ff5a4a", "#ffb3a3"]
# eye motion keyposes: (time s, yaw, pitch, lid opening, pupil size); frames are
# rendered in between with easing so the look-around glides instead of stepping
KEYS = [(0, 0, 0, 1, .21), (.55, -.42, .05, 1, .2), (.8, -.42, .05, 1, .2),
        (1.3, .38, -.1, 1, .21), (1.45, .38, -.1, .5, .21), (1.53, .34, -.08, .06, .22),
        (1.62, .3, -.06, .55, .22), (1.72, .26, -.05, 1, .22), (2.2, .28, .24, 1, .23),
        (2.6, .28, .24, 1, .23), (3.1, -.3, -.18, 1, .22), (3.45, -.3, -.18, 1, .22),
        (3.6, -.3, -.18, .07, .22), (3.75, -.26, -.15, 1, .22), (4.3, 0, 0, 1, .21)]
FRAME_DT = .085
HOLD0 = .8  # the eye rests on frame 0 between look-arounds

# Desktop timeline, seconds into each CYCLE
CYCLE = 36.0
LAUNCH_AT = 0.4                 # DOS prompt starts typing `launch eye.exe`
EYE_OPEN = 1.75                 # eye.exe window pops up
NOTE_TYPE = EYE_OPEN + 5.0      # prompt types `open about.txt`
NOTE_OPEN = NOTE_TYPE + 1.1     # about.txt pops up; rain paints the name in
BACK = CYCLE - 4.2              # rain wipes the name away again
NOTE_CLOSE, EYE_CLOSE = CYCLE - .9, CYCLE - .5


def _frames():
    out, t = [], 0.0
    while t <= KEYS[-1][0] + 1e-6:
        a = max(k for k in KEYS if k[0] <= t + 1e-9)
        b = min((k for k in KEYS if k[0] > t + 1e-9), default=a, key=lambda k: k[0])
        x = 0 if b is a else (t - a[0]) / (b[0] - a[0])
        x = x * x * (3 - 2 * x)  # smoothstep
        out.append(tuple(a[i] + (b[i] - a[i]) * x for i in range(1, 5)) + (1.0,))
        t += FRAME_DT
    return out


FRAMES = _frames()
LOOK = HOLD0 + len(FRAMES) * FRAME_DT


def _eye_frame(W, H, cw, ch, yaw, pitch, opening, pupil, zoom=1.0):
    """Render one frame of a lit 3D eyeball as ASCII.

    The eyeball is a unit sphere under a key light; the iris is a cap on the
    sphere around the gaze direction (so it foreshortens into an ellipse when
    the eye looks sideways), with fibres, a bright collar and a dark limbal
    ring. Lids cut an almond-shaped opening, cast a shadow and carry lashes.
    Returns rows of [(class, text)] runs.
    """
    import math
    cx, cy, R = W / 2, H / 2, H * .44 * zoom
    L = (-.45, -.55, .70)
    ln = math.sqrt(sum(c * c for c in L))
    L = tuple(c / ln for c in L)
    Hv = (L[0], L[1], L[2] + 1)
    hn = math.sqrt(sum(c * c for c in Hv))
    Hv = tuple(c / hn for c in Hv)
    G = (math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch))
    # basis around the gaze for the fibre angle
    A = (G[2], 0, -G[0])
    an = math.hypot(A[0], A[2]) or 1
    A = (A[0] / an, 0, A[2] / an)
    B = (G[1] * A[2] - G[2] * A[1], G[2] * A[0] - G[0] * A[2], G[0] * A[1] - G[1] * A[0])
    th_i, th_p = .56, min(pupil, .5)  # iris / pupil angular radius
    half_w, up_h, lo_h = 1.32, .7 * opening, .52 * max(opening, .08)

    f_seed = int(yaw * 1000) % 7  # dither shifts a little per frame, like live terminal output

    def h(i, j):  # stable per-cell hash in [0,1)
        return ((i * 73856093) ^ (j * 19349663)) % 1000 / 1000

    rows = []
    for j in range(int(H // ch)):
        runs, cur, txt = [], None, ""
        for i in range(int(W // cw)):
            u = (i * cw + cw / 2 - cx) / R
            v = (j * ch + ch / 2 - cy) / R
            k = max(0.0, 1 - (u / half_w) ** 2)
            y_up = -up_h * k ** .75 - .06 * opening
            y_lo = lo_h * k ** 1.1
            lum, fam = 0.0, "s"
            if y_up < v < y_lo:
                d2 = u * u + v * v
                if d2 < 1:
                    n = (u, v, math.sqrt(1 - d2))
                    diff = max(0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])
                    c = n[0] * G[0] + n[1] * G[1] + n[2] * G[2]
                    ang = math.acos(max(-1, min(1, c)))
                    spec = max(0, n[0] * Hv[0] + n[1] * Hv[1] + n[2] * Hv[2])
                    if ang < th_p:                                   # pupil
                        # stars live at fixed points in the scene; each is drawn as one
                        # glyph in the cell that holds its centre, so as the camera
                        # dives they stream outward as sharp points, not blocks
                        a_, b_ = math.floor(u * 55), math.floor(v * 55)
                        lum = .02
                        if h(a_ + 500, b_ + 500) > .975:
                            si = math.floor((cx + (a_ + .5) / 55 * R) / cw)
                            sj = math.floor((cy + (b_ + .5) / 55 * R) / ch)
                            if si == i and sj == j:
                                lum = .8
                    elif ang < th_i:                                 # iris
                        t = (ang - th_p) / (th_i - th_p)
                        phi = math.atan2(sum(a * b for a, b in zip(n, B)), sum(a * b for a, b in zip(n, A)))
                        fib = .62 + .38 * math.sin(phi * 38 + 2.6 * math.sin(phi * 5) + t * 3)
                        crypt = .85 + .15 * math.sin(phi * 11 + t * 14)
                        base = 1.05 - .45 * t if t > .18 else .7 + 1.9 * t  # collar
                        if t > .86:
                            base *= .35                                  # limbal ring
                        lum = base * fib * crypt * (.6 + .55 * diff)
                        fam = "i"
                    else:                                            # sclera
                        lum = .3 + .38 * diff - .2 * d2
                    # cornea gloss + wet highlight
                    lum += (1.6 if ang < th_i * 1.1 else .6) * spec ** 700 + .1 * spec ** 40
                else:                                                # corner tissue
                    lum = .18
                gap = min(v - y_up, y_lo - v)
                lum *= 1 - .65 * math.exp(-gap / .07)                # occlusion at the lids
                if v - y_up < .22 * opening:                        # upper-lid cast shadow
                    lum *= .45 + .55 * (v - y_up) / (.22 * opening)
            else:                                                    # skin, lid crease, lashes
                above = y_up - v
                lum = .22 - .06 * abs(u) - .08 * abs(v)
                if k < .02:
                    pass
                elif 0 < above < .05:
                    lum = .03                                        # lash line
                elif 0 < above < .26 and abs(u) < half_w * .95:
                    s = u * 7 - above * 5 * (1 if u > 0 else -1)
                    if (s - math.floor(s)) < .3:
                        lum = .04                                    # lashes
                if k > .02 and abs(above - .34 * opening - .1) < .03 and abs(u) < 1.1:
                    lum *= .4                                        # crease
                if k > .02 and 0 < v - y_lo < .045 and abs(u) < half_w * .9:
                    lum = .3                                         # wet lower-lid rim
                re_ = math.hypot(u / 1.55, v / 1.05)
                if re_ > 1:
                    lum *= math.exp(-(re_ - 1) * 3.2)                # vignette
                lum = max(0, lum)
            base_lum = max(0.0, min(1.0, lum)) ** .62  # lift midtones so the shading reads on black
            # dither only the glyph choice (breaks flat bands into texture); colour
            # stays on the smooth value so runs stay long and the file stays small
            lum += (h(i + f_seed, j) - .5) * (.07 if lum > .02 else 0)
            lum = max(0.0, min(1.0, lum)) ** .62
            ch_ = RAMP[min(len(RAMP) - 1, int(lum * len(RAMP)))]
            cls = f"{fam}{min(4, int(base_lum * 5))}"
            if ch_ == " " and cur:
                cls = cur  # a space has no colour: let it join the current run
            if cls != cur and txt:
                runs.append((cur, txt))
                txt = ""
            cur, txt = cls, txt + ch_
        runs.append((cur, txt))
        rows.append(runs)
    return rows


def ascii_eye(W, H, cw=7, ch=11.5):
    """Animated 3D ASCII eye that keeps looking around and blinking from
    EYE_OPEN until EYE_CLOSE, every CYCLE.

    Returns (css, svg).
    """
    from xml.sax.saxutils import escape
    cols = int(W // cw)
    css = [".eye text{font-family:" + MONO + ";font-size:11px;white-space:pre}"]
    css += [f".s{k}{{fill:{c}}}" for k, c in enumerate(SCLERA)]
    css += [f".i{k}{{fill:{c}}}" for k, c in enumerate(IRIS)]
    frames = []
    for f, (yaw, pitch, opening, pupil, zoom) in enumerate(FRAMES):
        rows = _eye_frame(W, H, cw, ch, yaw, pitch, opening, pupil, zoom)
        out = []
        for j, runs in enumerate(rows):
            # the row's most common colour goes on the <text>; only other runs get a tspan
            weight = {}
            for c, t in runs:
                weight[c] = weight.get(c, 0) + len(t.strip())
            main = max(weight, key=weight.get)
            body = "".join(escape(t) if c == main else f'<tspan class="{c}">{escape(t)}</tspan>'
                           for c, t in runs if t)
            reveal = f' class="{main}"'
            out.append(f'<text{reveal} x="0" y="{j * ch + ch * .8:.1f}" textLength="{cols * cw}" '
                       f'lengthAdjust="spacing">{body}</text>')
        # Frames are switched with SMIL display: CSS can't animate display
        # inside an <img>, and hidden-but-displayed frames (opacity, visibility,
        # moved offscreen) still cost nearly a full redraw every frame, while
        # display:none ones cost nothing.
        times, vals, base = ["0"], ["none"], EYE_OPEN
        while base < EYE_CLOSE:
            a = base if f == 0 else base + HOLD0 + f * FRAME_DT
            b = min(base + HOLD0 + (f + 1) * FRAME_DT, EYE_CLOSE)
            if a < b:
                times += [f"{a / CYCLE:.5f}", f"{b / CYCLE:.5f}"]
                vals += ["inline", "none"]
            base += LOOK
        swap = f'keyTimes="{";".join(times)}" values="{";".join(vals)}"'
        frames.append(f'<g display="none"><animate attributeName="display" '
                      f'dur="{CYCLE}s" repeatCount="indefinite" calcMode="discrete" {swap}/>{"".join(out)}</g>')
    return "".join(css), f'<g class="eye">{"".join(frames)}</g>'


def matrix_rain(W, H, start, back, seed=7, cw=14, trail=18):
    """Matrix rain that falls twice per CYCLE. Each column has a dark curtain
    whose edge rides the falling drop: at `start` it retracts behind the drop,
    painting the content into view; at `back` it slides down in front of it,
    wiping the content away again. (Plain rects rather than
    masks: masks over the profile are too slow to redraw every frame.)

    Returns (css, curtains, rain).
    """
    rnd = random.Random(seed)
    css, curtain, rain = [], [], []
    L = trail * cw

    def pc(t):
        return f"{t / CYCLE * 100:.3f}%"
    for i in range(int(W // cw) + 1):
        x = i * cw
        d1, f1 = start + rnd.uniform(0, 1.4), rnd.uniform(2.4, 3.6)  # f: time for the head to travel H + L
        d2, f2 = back + rnd.uniform(0, .7), rnd.uniform(1.8, 2.4)
        r1, r2 = f1 * H / (H + L), f2 * H / (H + L)                # time for the head to reach the bottom
        css.append(f"@keyframes m{i}{{0%,{pc(d1)}{{transform:translateY(0)}}{pc(d1 + f1)},{pc(d2 - .01)}"
                   f"{{transform:translateY({H + L}px)}}{pc(d2)}{{transform:translateY(0)}}"
                   f"{pc(d2 + f2)},100%{{transform:translateY({H + L}px)}}}}"
                   f"@keyframes k{i}{{0%,{pc(d1)}{{transform:translateY(0)}}{pc(d1 + r1)},{pc(d2 - .01)}"
                   f"{{transform:translateY({H}px)}}{pc(d2)}{{transform:translateY(-{H}px)}}"
                   f"{pc(d2 + r2)},100%{{transform:translateY(0)}}}}"
                   f".m{i}{{animation:m{i} {CYCLE}s linear infinite}}.k{i}{{animation:k{i} {CYCLE}s linear infinite}}")
        curtain.append(f'<rect class="k{i}" x="{x}" y="0" width="{cw + .5}" height="{H}"/>')
        chars = "".join(
            f'<tspan x="{x + cw / 2}" y="{-L + (k + 1) * cw}" fill-opacity="{(k + 1) / trail:.2f}"'
            f'{f" fill={chr(34)}#ffd6d6{chr(34)}" if k == trail - 1 else ""}>{rnd.choice(GLYPHS)}</tspan>'
            for k in range(trail))
        rain.append(f'<text class="m{i}" text-anchor="middle">{chars}</text>')
    return "".join(css), "".join(curtain), "".join(rain)


def window(x, y, w, h, title, inner, show=None):
    """A Win98 window at (x, y). With show=(open, close) it pops open and
    vanishes again at those times every CYCLE."""
    svg = f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{win_frame(w, h, title)}{inner}</svg>'
    if not show:
        return svg
    a, b = show
    k = lambda *ts: ";".join(f"{t / CYCLE:.5f}" for t in ts)
    smil = f'dur="{CYCLE}s" repeatCount="indefinite" calcMode="discrete"'
    # Both done in SMIL with discrete steps: CSS can't animate display in an
    # <img>, and an endless CSS transform on the window repaints all of it
    # every frame. The pop grows from the centre in three snaps.
    cx, cy = x + w / 2, y + h / 2
    return (f'<g display="none"><animate attributeName="display" {smil} keyTimes="0;{k(a, b)}" '
            f'values="none;inline;none"/><g transform="translate({cx} {cy})"><g>'
            f'<animateTransform attributeName="transform" type="scale" {smil} '
            f'keyTimes="0;{k(a + .04, a + .08)}" values=".82;.92;1"/>'
            f'<g transform="translate({-cx} {-cy})">{svg}</g></g></g></g>')


def morph():
    """Three overlapping Win98 windows: the DOS prompt, eye.exe and about.txt."""
    css = []
    # 1. DOS prompt (always open)
    tw, th = 500, 250
    t = Term(f"MS-DOS Prompt - {USER}", "t", LAUNCH_AT, CYCLE, w=tw)
    t.type("launch eye.exe")
    t.t = EYE_OPEN  # the prompt comes back as eye.exe starts; the next command waits
    t.type("open about.txt", wait=NOTE_TYPE - EYE_OPEN)
    t.cursor()
    term = re.sub(r"^<svg", '<svg x="0" y="0"', t.svg(h=th).strip())
    # 2. eye.exe
    ex, ey, ew, eh = 331, 110, 520, 290
    cw, ch = ew - 10, eh - CLIENT_Y - 5
    eye_css, eye = ascii_eye(cw, ch)
    eye_win = window(ex, ey, ew, eh, "eye.exe", f'<svg x="5" y="{CLIENT_Y}" width="{cw}" height="{ch}">{eye}</svg>',
                     (EYE_OPEN, EYE_CLOSE))
    css.append(eye_css)
    # 3. about.txt in Notepad, painted in by the rain
    nx, ny, nw, nh = 30, 330, 600, 214
    menu = 18
    top = CLIENT_Y + menu + 2
    cw, ch = nw - 10, nh - top - 5
    name, name_h = ascii_name(0, 0, fs=8)
    text = (f'<g transform="translate({(cw - len(NAME[0]) * 4.8) / 2:.1f} 22)">{name}</g>'
            + "".join(f'<text x="18" y="{22 + name_h + 22 + k * 20}" fill="{MID}">{line}</text>'
                      for k, line in enumerate(["&gt; I write code to make pixels come alive.",
                                                "&gt; stack: C · C++ · C# · Unity · Unreal · HTML/CSS"])))
    rain_css, curtain, rain = matrix_rain(cw, ch, NOTE_OPEN + .15, BACK)
    inner = (f'<rect x="5" y="{CLIENT_Y}" width="{nw - 10}" height="{menu}" fill="#c0c0c0"/>'
             f'<text x="12" y="{CLIENT_Y + 13}" font-family="{UI_FONT}" font-size="11" fill="#000" '
             f'style="white-space:pre">File   Edit   Search   Help</text>'
             f'<svg x="5" y="{top}" width="{cw}" height="{ch}"><rect width="{cw}" height="{ch}" fill="{BG}"/>'
             f'{text}<g fill="{BG}">{curtain}</g><g class="rain" fill="{HI}">{rain}</g></svg>')
    note = window(nx, ny, nw, nh, "about.txt - Notepad", inner, (NOTE_OPEN, NOTE_CLOSE))
    css.append(rain_css)
    H = ny + nh + 2
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<title>{USER} — terminal profile</title>
<style>{"".join(css)}.rain text{{font-family:{MONO};font-size:13px}}
svg{{font-size:{FS}px}}text{{font-family:{MONO};white-space:pre}}</style>
{term}{eye_win}{note}
</svg>"""


def button(name, label):
    w, h = 168, 38
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
<style>text{{font-family:{MONO};font-size:13px}}</style>
<g>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="6" fill="{BG}" stroke="{MID}"/>
<text x="12" y="24" fill="{DIM}">&gt;</text>
{icon(name, 28, 11, 16, HI)}
<text x="52" y="24" fill="{HI}">{label}</text>
<text x="{w - 14}" y="24" fill="{MID}" text-anchor="end">↗</text>
</g></svg>"""


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "morph":
        os.makedirs(os.path.dirname(sys.argv[2]) or ".", exist_ok=True)
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(morph())
        print("wrote " + sys.argv[2])
        return
    os.makedirs(OUT, exist_ok=True)
    files = {"header.svg": header()}
    for name, label, _ in LINKS:
        files[f"btn-{name}.svg"] = button(name, label)
    for fn, content in files.items():
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
            f.write(content)
        print("wrote assets/" + fn)


if __name__ == "__main__":
    main()
