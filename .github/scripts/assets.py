"""Static terminal-theme README assets (header, stack, link buttons).

These don't depend on live data, so run this once after editing and commit
the output in assets/:  python .github/scripts/assets.py
All-in-one window (needs the day's snake):
    python .github/scripts/assets.py combined dist/commit-snake.svg dist/profile.svg
Icons in icons/ are from Simple Icons (CC0) and Devicon (MIT).
"""
import os
import random
import re
import sys

from snake import DOTS, HOLD, LOOP, round_swap

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "assets")

USER = "uzaiiirahmed"
PROMPT = f"{USER}@github:~$"
W = 851  # matches the snake board width
MONO = "ui-monospace,SFMono-Regular,'Cascadia Mono',Menlo,Consolas,monospace"
BG, BAR, DIM, MID, HI = "#0a0505", "#1a0c0c", "#9e1c1c", "#e03434", "#ff5c5c"
FS = 13
CW = FS * 0.6          # forced glyph advance (textLength keeps it exact)
LINE = 22
TYPE = 0.045           # seconds per typed character

STACK = [("c", "c"), ("cplusplus", "c++"), ("csharp", "c#"), ("css", "css"),
         ("html5", "html"), ("unity", "unity"), ("unrealengine", "unreal")]
LINKS = [("globe", "portfolio", "https://uzair-ahmed.netlify.app"),
         ("linkedin", "linkedin", "https://linkedin.com/in/uzair-ahmed-381149314"),
         ("instagram", "instagram", "https://instagram.com/uzaiiirahmed")]


def icon(name, x, y, size, fill):
    src = open(os.path.join(HERE, "icons", f"{name}.svg"), encoding="utf-8").read()
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    inner = re.sub(r"<title>.*?</title>", "", src.split(">", 1)[1].rsplit("</svg>", 1)[0])
    inner = re.sub(r'\sfill="[^"]*"', "", inner)
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{vb}" fill="{fill}">{inner}</svg>'


class Term:
    """Builds a terminal window whose lines type out one after another."""

    def __init__(self, title, prefix="", start=0.4, period=None):
        self.p = prefix  # keeps class/id names unique when several windows share one SVG
        self.period = period  # replay the typing every `period` seconds (None: type once)
        self.title, self.body, self.css, self.defs, self.raw = title, [], [], [], []
        self.t, self.y, self.n = start, 56, 0

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

    def type(self, cmd):
        """A prompt line where the command gets typed."""
        x0 = 20
        px = x0 + (len(PROMPT) + 1) * CW
        k = self._reveal(self.t, 0.01, 1)
        self.body.append(f'<g class="{self.p}r{k}"><text x="{x0}" y="{self.y}" fill="{MID}" '
                         f'textLength="{len(PROMPT) * CW:.1f}">{PROMPT}</text></g>')
        dur = max(len(cmd), 1) * TYPE
        k2 = self._reveal(self.t + 0.25, dur, len(cmd))
        self.defs.append(f'<clipPath id="{self.p}c{k2}"><rect class="{self.p}r{k2}" x="{px}" y="{self.y - FS}" '
                         f'width="{len(cmd) * CW + 1:.1f}" height="{FS + 5}"/></clipPath>')
        self.body.append(f'<text x="{px}" y="{self.y}" fill="{HI}" clip-path="url(#{self.p}c{k2})" '
                         f'textLength="{len(cmd) * CW:.1f}">{cmd}</text>')
        self.t += 0.25 + dur + 0.35
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
                         f'<rect class="blink" x="{cx}" y="{self.y - FS + 1}" width="{CW:.1f}" height="{FS + 2}" fill="{HI}"/></g>')
        self.y += LINE

    def svg(self, bottom=14):
        H = self.y - LINE + bottom + 8
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>
svg{{font-size:{FS}px}}text{{font-family:{MONO};white-space:pre}}
@keyframes grow{{to{{transform:scaleX(1)}}}}
.blink{{animation:blink 1s steps(1,end) infinite}}@keyframes blink{{50%{{opacity:0}}}}
{''.join(self.css)}
</style>
<defs><filter id="glow" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="2" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>{''.join(self.defs)}</defs>
<g><rect width="{W}" height="{H}" rx="12" fill="{BG}"/>
<rect width="{W}" height="26" rx="12" fill="{BAR}"/><rect y="14" width="{W}" height="12" fill="{BAR}"/>
<text x="{W / 2}" y="17" font-size="11" fill="#8a5f5f" text-anchor="middle">{self.title}</text>
<g filter="url(#glow)">{''.join(self.body)}</g></g>
{''.join(self.raw)}{DOTS}
</svg>"""


def header(prefix="", start=0.4, period=None):
    t = Term(f"{USER} — zsh", prefix, start, period)
    t.type("whoami")
    t.out(f'<text x="18" y="{t.y + 26}" font-size="44" font-weight="800" fill="{HI}" letter-spacing="3">'
          f'UZAIR AHMED</text>', height=LINE * 2 + 12, pause=0.5)
    t.type("cat about.txt")
    for line in ["&gt; I write code to make pixels come alive.",
                 "&gt; stack: C · C++ · C# · Unity · Unreal · HTML/CSS"]:
        t.out(f'<text x="20" y="{t.y}" fill="{MID}">{line}</text>', pause=0.18)
    t.cursor()
    return t.svg()


def stack(prefix="", start=0.4, period=None):
    t = Term(f"{USER} — ~/stack", prefix, start, period)
    t.type("ls ~/stack")
    cols, size = len(STACK), 34
    slot = (W - 40) / cols
    for i, (name, label) in enumerate(STACK):
        cx = 20 + slot * i + slot / 2
        t.out(icon(name, cx - size / 2, t.y - 10, size, HI) +
              f'<text x="{cx}" y="{t.y + size + 8}" fill="{MID}" text-anchor="middle">{label}/</text>',
              height=0, pause=0.12)
    t.y += size + 34
    t.type("./connect.sh")
    return t.svg(bottom=4)


def combined(snake_svg):
    """Header, snake and stack in one terminal window. Needs today's snake."""
    t = Term(f"{USER} — zsh")
    t.type("whoami")
    t.out(f'<text x="18" y="{t.y + 26}" font-size="44" font-weight="800" fill="{HI}" letter-spacing="3">'
          f'UZAIR AHMED</text>', height=LINE * 2 + 12, pause=0.5)
    t.type("cat about.txt")
    for line in ["&gt; I write code to make pixels come alive.",
                 "&gt; stack: C · C++ · C# · Unity · Unreal · HTML/CSS"]:
        t.out(f'<text x="20" y="{t.y}" fill="{MID}">{line}</text>', pause=0.18)
    t.y += 8
    t.type("./snake --eat commits")
    # reuse the snake's board + status line, cropping off its own title bar and prompt
    sw, sh = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', snake_svg).group(1, 2))
    top = 56
    inner = re.sub(r"^<svg[^>]*>", "", snake_svg.strip()).rsplit("</svg>", 1)[0]
    nested = (f'<svg x="0" y="{t.y - 10}" width="{sw}" height="{sh - top}" '
              f'viewBox="0 {top} {sw} {sh - top}">{inner}</svg>')
    t.embed(nested, sh - top + 8)
    t.type("ls ~/stack")
    cols, size = len(STACK), 34
    slot = (W - 40) / cols
    for i, (name, label) in enumerate(STACK):
        cx = 20 + slot * i + slot / 2
        t.out(icon(name, cx - size / 2, t.y - 10, size, HI) +
              f'<text x="{cx}" y="{t.y + size + 8}" fill="{MID}" text-anchor="middle">{label}/</text>',
              height=0, pause=0.12)
    t.y += size + 34
    t.type("./connect.sh")
    return t.svg(bottom=4)


def _nest(svg, y):
    w, h = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).group(1, 2))
    inner = re.sub(r"^<svg[^>]*>", "", svg.strip()).rsplit("</svg>", 1)[0]
    return f'<svg x="0" y="{y}" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{inner}</svg>', h


GLYPHS = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワン0123456789:.=*+ZXE"


# luminance ramp, darkest -> brightest
RAMP = " .`'^\",:;Il!i~+_-?][}{1)(|tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
SCLERA = ["#1c1414", "#4a3838", "#8c7272", "#c4a8a8", "#ecdcdc"]
IRIS = ["#2e0707", "#7a1414", "#c42828", "#ff5a4a", "#ffb3a3"]
# eye motion keyposes: (time s, yaw, pitch, lid opening, pupil size); frames are
# rendered in between with easing so the look-around glides instead of stepping
KEYS = [(0, 0, 0, 1, .21), (.55, -.42, .05, 1, .2), (.8, -.42, .05, 1, .2),
        (1.3, .38, -.1, 1, .21), (1.45, .38, -.1, .5, .21), (1.53, .34, -.08, .06, .22),
        (1.62, .3, -.06, .55, .22), (1.72, .26, -.05, 1, .22), (2.1, 0, 0, 1, .24),
        (2.4, 0, 0, 1, .24)]
# On GitHub the image's clock starts while the page is still parsing it, so the
# first moments are often never painted: the eye holds still for a beat first.
EYE_PAD = 0.6
FRAME_T0, FRAME_DT = .35 + EYE_PAD, .085


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
EYE = FRAME_T0 + len(FRAMES) * FRAME_DT  # the rain starts falling over the eye here
CYCLE = 2 * LOOP                          # eye -> rain -> profile (two snake rounds) -> rain -> eye
BACK = CYCLE - HOLD + 0.3                 # second round's game over: rain covers the profile again


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
    """Animated 3D ASCII eye: looks around and blinks, then stays put while
    the rain wipes it away column by column (it is clipped to the rain
    curtains, see morph). It is back under the curtains for the second shower,
    so the rain uncovers it again. Replays every CYCLE.

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
        start = 0 if f == 0 else FRAME_T0 + f * FRAME_DT
        end = FRAME_T0 + (f + 1) * FRAME_DT if f < len(FRAMES) - 1 else EYE + 6.2  # first shower done
        a, b = start / CYCLE, end / CYCLE
        swap = (f'keyTimes="0;{b:.5f};{BACK / CYCLE:.5f}" values="inline;none;inline"' if f == 0
                else f'keyTimes="0;{a:.5f};{b:.5f}" values="none;inline;none"')
        frames.append(f'<g display="{"inline" if f == 0 else "none"}"><animate attributeName="display" '
                      f'dur="{CYCLE}s" repeatCount="indefinite" calcMode="discrete" {swap}/>{"".join(out)}</g>')
    return "".join(css), f'<g class="eye">{"".join(frames)}</g>'


def matrix_rain(W, H, seed=7, cw=14, trail=18):
    """Matrix rain that falls twice per CYCLE. Each column has a dark curtain
    whose edge rides the falling drop: after the eye it retracts behind the
    drop, painting the profile into view; at BACK it slides down in front of
    it, wiping the profile away for the next eye. (Plain rects rather than
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
        d1, f1 = EYE + rnd.uniform(0, 1.8), rnd.uniform(2.8, 4.2)  # f: time for the head to travel H + L
        d2, f2 = BACK + rnd.uniform(0, .7), rnd.uniform(1.8, 2.4)
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


def morph(snake_svg):
    """Header, snake and stack as three windows that merge into one terminal
    and split apart again every round, framed by the eye + rain loop."""
    gap = 10
    parts, y, seams = [], 0, []
    # (the typing waits for the rain to finish painting)
    for i, svg in enumerate([header("h", EYE + 5.2, CYCLE), snake_svg, stack("s", EYE + 5.5, CYCLE)]):
        nested, h = _nest(svg, y)
        parts.append(nested)
        if i:
            seams.append(y)
        y += h + gap
    H = y - gap
    # Merged look: fill each gap plus the lower window's title bar with terminal
    # background (squaring off the rounded corners) and draw a faint divider.
    fill = "".join(
        f'<rect x="0" y="{sy - gap - 12}" width="{W}" height="{gap + 12 + 26}" fill="{BG}"/>'
        f'<line x1="20" x2="{W - 20}" y1="{sy - gap / 2 + 6}" y2="{sy - gap / 2 + 6}" stroke="{DIM}" '
        f'stroke-opacity=".45" stroke-dasharray="2 5"/>' for sy in seams)
    css, curtain, rain = matrix_rain(W, H)
    eye_css, eye = ascii_eye(W, H)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<title>{USER} — terminal profile</title>
<style>{css}{eye_css}.rain text{{font-family:{MONO};font-size:13px}}</style>
<defs><clipPath id="card"><rect width="{W}" height="{H}" rx="12"/></clipPath>
<clipPath id="wipe">{curtain}</clipPath></defs>
{''.join(parts)}
<g opacity="0">{round_swap("opacity", "0", "1")}{fill}</g>
<g clip-path="url(#card)"><g class="curtain" fill="{BG}">{curtain}</g><g clip-path="url(#wipe)">{eye}</g><g class="rain" fill="{HI}">{rain}</g></g>
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
    if len(sys.argv) == 4 and sys.argv[1] in ("combined", "morph"):
        with open(sys.argv[2], encoding="utf-8") as f:
            svg = (combined if sys.argv[1] == "combined" else morph)(f.read())
        with open(sys.argv[3], "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote " + sys.argv[3])
        return
    os.makedirs(OUT, exist_ok=True)
    files = {"header.svg": header(), "stack.svg": stack()}
    for name, label, _ in LINKS:
        files[f"btn-{name}.svg"] = button(name, label)
    for fn, content in files.items():
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
            f.write(content)
        print("wrote assets/" + fn)


if __name__ == "__main__":
    main()
