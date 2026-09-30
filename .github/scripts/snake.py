"""Contribution snake generator.

Fetches a user's contribution calendar and renders an animated SVG where a
smooth, tapered snake hunts down every contribution cell.

Usage: GITHUB_TOKEN=... python snake.py <user> <out.svg> [theme]
Themes: native, gameboy, glass, terminal
"""
import json
import os
import re
import sys
import urllib.request
from collections import deque

CELL, GAP = 11, 4
PITCH = CELL + GAP
LOOP = 32.0  # seconds per round; speed adapts so every round takes this long
PRE = 1.2    # pause before the snake starts
HOLD = 3.5   # pause after the last commit is eaten
FADE = 1.4   # red <-> green crossfade, starts right after the last commit is eaten

DOTS = ('<circle cx="18" cy="13" r="5" fill="#ff5f57"/><circle cx="34" cy="13" r="5" fill="#febc2e"/>'
        '<circle cx="50" cy="13" r="5" fill="#28c840"/>')


def round_swap(attr, a, b):
    """SMIL animation that flips `attr` between a and b after every round.

    It spans two rounds and starts at load, so every image on the page that
    uses it switches at the same moment (they all loop on LOOP).
    """
    at = LOOP - HOLD + 0.3
    k = [0, at, at + FADE, LOOP + at, LOOP + at + FADE, 2 * LOOP]
    key_times = ";".join(f"{t / (2 * LOOP):.4f}" for t in k)
    return (f'<animate attributeName="{attr}" dur="{2 * LOOP}s" repeatCount="indefinite" calcMode="spline" '
            f'keyTimes="{key_times}" keySplines="0 0 1 1;.4 0 .2 1;0 0 1 1;.4 0 .2 1;0 0 1 1" '
            f'values="{a};{a};{b};{b};{a};{a}"/>')


def palette_vars(svg):
    """Make every palette colour alternate red / green each round.

    Each colour becomes a registered CSS custom property animated on :root;
    its green twin is the same colour with the R and G channels swapped.
    Much cheaper than a colour-matrix filter over the whole image, which has
    to be re-run every frame. Browsers without @property simply stay red.
    Safe to run again on output that already went through it.
    """
    keep = set(re.findall(r"#[0-9a-f]{6}", DOTS))
    svg = re.sub(r'<style id="palette">.*?</style>', "", svg, flags=re.S)

    def var(h):
        return f"var(--c{h[1:].lower()})"

    def fix_tag(m):
        tag = m.group(0)
        decls = []

        def grab(a):
            h = a.group(2).lower()
            if h in keep:
                return a.group(0)
            decls.append(f"{a.group(1)}:{var(h)}")
            return ""
        tag = re.sub(r'\s(fill|stroke)="(#[0-9a-fA-F]{6})"', grab, tag)
        if decls:
            if ' style="' in tag:
                tag = tag.replace(' style="', f' style="{";".join(decls)};', 1)
            else:
                end = "/>" if tag.endswith("/>") else ">"
                tag = tag[:-len(end)] + f' style="{";".join(decls)}"' + end
        return tag

    svg = re.sub(r"<[a-zA-Z][^<>]*>", fix_tag, svg)
    svg = re.sub(r"<style>.*?</style>", lambda m: re.sub(
        r"#[0-9a-fA-F]{6}\b", lambda h: h.group(0) if h.group(0).lower() in keep else var(h.group(0)),
        m.group(0)), svg, flags=re.S)
    reds = sorted(set(re.findall(r"var\(--c([0-9a-f]{6})\)", svg)))

    def green(h):
        return h[2:4] + h[0:2] + h[4:6]
    at = LOOP - HOLD + 0.3
    k = [0, at, at + FADE, LOOP + at, LOOP + at + FADE, 2 * LOOP]
    pc = [f"{t / (2 * LOOP) * 100:.3f}%" for t in k]
    red_set = ";".join(f"--c{h}:#{h}" for h in reds)
    green_set = ";".join(f"--c{h}:#{green(h)}" for h in reds)
    block = ("".join(f"@property --c{h}{{syntax:'&lt;color&gt;';inherits:true;initial-value:#{h}}}" for h in reds)
             + f":root{{animation:palette {2 * LOOP}s infinite}}"
             f"@keyframes palette{{{pc[0]},{pc[1]}{{{red_set}}}{pc[2]},{pc[3]}{{{green_set}}}"
             f"{pc[4]},{pc[5]}{{{red_set}}}}}")
    return re.sub(r"^(<svg[^>]*>)", lambda m: m.group(1) + f'<style id="palette">{block}</style>',
                  svg.strip())


QUERY = """query($login:String!){user(login:$login){contributionsCollection{
contributionCalendar{totalContributions weeks{contributionDays{
contributionCount contributionLevel weekday}}}}}}"""
LEVEL_MAP = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
             "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

MONO = "ui-monospace,SFMono-Regular,'Cascadia Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

# Each theme: board padding, cell colours, snake layers, and chrome (header/footer).
# Snake: body length in cells, stroke width head->tail, colour head->tail.
# The body is a stack of strokes, each shorter/wider than the last, giving a taper.
THEMES = {
    "native": dict(
        pad=(8, 8, 8, 8), bg=None, radius=2,
        cells=["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
        cells_dark=["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
        outline="#0b3d1c", outline_dark="#04130a",
        snake=dict(length=6, w=(11.5, 2.5), colors=("#6ee08a", "#2f8f47")),
        head=dict(r=6.8, fill="#6ee08a", eye="#0b1f12", tongue="#ff5a79"),
        highlight="#ffffff", glow=False, font=SANS,
    ),
    "gameboy": dict(
        pad=(34, 52, 34, 46), bg="#9bbc0f", radius=0, cap="square",
        cells=["#8bac0f", "#6e8e0c", "#306230", "#1f4a1f", "#0f380f"],
        outline="#0f380f",
        snake=dict(length=6, w=(11, 11), colors=("#306230", "#306230"), steps=1),
        head=dict(r=6.5, fill="#0f380f", eye="#9bbc0f", square=True),
        highlight=None, glow=False, font=MONO,
    ),
    "glass": dict(
        pad=(30, 60, 30, 48), bg="#0b1020", radius=3,
        cells=["#ffffff12", "#5b6cff55", "#7b5cff99", "#b45cffcc", "#ff5cc8"],
        outline="#1a0f3a",
        snake=dict(length=6.5, w=(11, 2.5), colors=("#7ff0ff", "#5a4dff")),
        head=dict(r=6.8, fill="#8ff0ff", eye="#0b1020", tongue="#ff5cc8"),
        highlight="#ffffff", glow=True, font=SANS,
    ),
    "terminal": dict(
        pad=(30, 62, 30, 44), bg="#0a0505", radius=1,
        cells=["#1f0d0d", "#5c1414", "#9e1c1c", "#e03434", "#ff5c5c"],
        outline=None,
        trail=dict(n=34, gap=5, size=(6, 1.5), colors=("#ff5c5c", "#4a0f0f"), start=8),
        head=dict(r=0, cursor=True, fill="#ff5c5c"),
        highlight=None, glow=True, font=MONO,
    ),
}


def fetch(user, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        cal = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    cells = {}
    for x, week in enumerate(cal["weeks"]):
        for d in week["contributionDays"]:
            cells[(x, d["weekday"])] = (LEVEL_MAP[d["contributionLevel"]], d["contributionCount"])
    return len(cal["weeks"]), cells, cal["totalContributions"]


def plan_path(width, cells):
    """Greedy BFS: always chase the nearest uneaten cell, then exit right."""
    food = {p for p, (lvl, _) in cells.items() if lvl > 0}
    lo, hi = -4, width + 3

    def bfs(start, goal):
        prev = {start: None}
        q = deque([start])
        while q:
            cur = q.popleft()
            if cur != start and goal(cur):
                out = []
                while cur != start:
                    out.append(cur)
                    cur = prev[cur]
                return out[::-1]
            x, y = cur
            for nxt in ((x + 1, y), (x, y + 1), (x, y - 1), (x - 1, y)):
                if lo <= nxt[0] <= hi and 0 <= nxt[1] <= 6 and nxt not in prev:
                    prev[nxt] = cur
                    q.append(nxt)
        return []

    path, eats = [(lo, 3)], {}
    while food:
        path += bfs(path[-1], lambda p: p in food)
        food.discard(path[-1])
        eats[path[-1]] = len(path) - 1
    path += bfs(path[-1], lambda p: p == (hi, 3))
    return path, eats


def render(user, width, cells, total, theme_name):
    th = THEMES[theme_name]
    path, eats = plan_path(width, cells)
    n = len(path)
    T = LOOP
    STEP = (LOOP - PRE - HOLD) / (n - 1)
    t_of = lambda step: (PRE + step * STEP) / T * 100
    pct = lambda step: f"{t_of(step):.3f}%"
    end = t_of(n - 1)

    pl, pt, pr, pb = th["pad"]
    gw, gh = width * PITCH - GAP, 7 * PITCH - GAP
    W, H = pl + gw + pr, pt + gh + pb
    cx = lambda x: pl + x * PITCH + CELL / 2
    cy = lambda y: pt + y * PITCH + CELL / 2
    ctx = dict(W=W, H=H, pl=pl, pt=pt, gw=gw, gh=gh, user=user, total=total,
               end=end, T=T, font=th["font"])

    css, eat_order = [], sorted(eats.values())

    # -- cells ------------------------------------------------------------------
    cell_svg, pellets = [], []
    for (x, y), (lvl, _) in sorted(cells.items()):
        X, Y = cx(x) - CELL / 2, cy(y) - CELL / 2
        cell_svg.append(f'<rect class="c0" x="{X}" y="{Y}" width="{CELL}" height="{CELL}" rx="{th["radius"]}"/>')
        if lvl:
            i = len(pellets)
            e = eats[(x, y)]
            css.append(f"@keyframes p{i}{{0%,{pct(e - 0.5)}{{transform:scale(1);opacity:1}}"
                       f"{pct(e + 2.5)}{{transform:scale(1.8);opacity:0}}"
                       f"98%{{transform:scale(.2);opacity:0}}100%{{transform:scale(1);opacity:1}}}}"
                       f".p{i}{{animation-name:p{i}}}")
            pellets.append(f'<rect class="p p{i} c{lvl}" x="{X}" y="{Y}" width="{CELL}" '
                           f'height="{CELL}" rx="{th["radius"]}"/>')

    # -- snake body: stroked path revealed by an animated dash ----------------
    d = "M" + " L".join(f"{cx(x)} {cy(y)}" for x, y in path)
    P = (n - 1) * PITCH
    grow_at = [0] + eat_order + [n - 1]
    grow = lambda k: 1 + 1.6 * min(k, len(eat_order)) / max(len(eat_order), 1)

    def body_layer(name, length, stroke_w, color, extra=""):
        frames = []
        for k, step in enumerate(grow_at):
            L = length * PITCH * grow(k - 1 if k else 0)
            h = step * PITCH
            if k == 0:
                frames.append(f"0%,{pct(0)}{{stroke-dasharray:{L:.1f} {P + 999};stroke-dashoffset:{L:.1f}}}")
            else:
                frames.append(f"{pct(step)}{{stroke-dasharray:{L:.1f} {P + 999};stroke-dashoffset:{L - h:.1f}}}")
        css.append(f"@keyframes {name}{{{''.join(frames)}}}.{name}{{animation-name:{name}}}")
        cap = th.get("cap", "round")
        return (f'<path class="b {name}" d="{d}" fill="none" stroke="{color}" stroke-width="{stroke_w}" '
                f'stroke-linecap="{cap}" stroke-linejoin="{"miter" if cap == "square" else "round"}"{extra}/>')

    mix = lambda c1, c2, t: "#" + "".join(
        f"{round(int(c1[i:i + 2], 16) * (1 - t) + int(c2[i:i + 2], 16) * t):02x}" for i in (1, 3, 5))
    body = []
    if "trail" in th:
        # A trail of small blocks each riding the route a little behind the head.
        # Moving small shapes is far cheaper to redraw than re-dashing long strokes.
        tr = th["trail"]
        lag = tr["gap"] / (PITCH / STEP)
        for k in range(1, tr["n"] + 1):
            t = k / tr["n"]
            size = tr["size"][0] + (tr["size"][1] - tr["size"][0]) * t
            seg = (f'<rect class="tr" style="animation-delay:{k * lag:.3f}s" x="{-size / 2:.2f}" '
                   f'y="{-size / 2:.2f}" width="{size:.2f}" height="{size:.2f}" rx="1" '
                   f'fill="{mix(tr["colors"][0], tr["colors"][1], t)}"/>')
            if k > tr["start"]:
                need = round((k - tr["start"]) / (tr["n"] - tr["start"]) * len(eat_order))
                at = pct(eat_order[max(need - 1, 0)])
                css.append(f"@keyframes g{k}{{0%{{opacity:0}}{at},100%{{opacity:1}}}}.g{k}{{animation-name:g{k}}}")
                seg = f'<g class="anim grow g{k}">{seg}</g>'
            body.append(seg)
        body.reverse()
    sn = th.get("snake", dict(length=1, w=(1, 1), colors=("#000000", "#000000")))
    k_n = sn.get("steps", 10) if "snake" in th else 0
    th["layers"] = []
    for i in range(k_n):  # tail (longest, thinnest) first, head last
        t = 1 - i / max(k_n - 1, 1)
        length = sn["length"] * (0.25 + 0.75 * t) if k_n > 1 else sn["length"]
        w = sn["w"][0] + (sn["w"][1] - sn["w"][0]) * t
        th["layers"].append((length, round(w, 2), mix(sn["colors"][0], sn["colors"][1], t)))

    if th.get("outline"):
        for j, (length, sw, _) in enumerate(th["layers"]):
            body.append(body_layer(f"o{j}", length, sw + 2.5, th["outline"]))
    for j, (length, sw, color) in enumerate(th["layers"]):
        body.append(body_layer(f"l{j}", length, sw, color))
    if th.get("highlight"):
        length, sw, _ = th["layers"][-1]
        body.append(body_layer("hl", length * 0.9, sw * 0.28, th["highlight"], ' opacity=".35"'))

    # -- head rides the same path via CSS motion path, so it faces its direction
    hd = th["head"]
    css.append(f"@keyframes hd{{0%,{pct(0)}{{offset-distance:0px}}{pct(n - 1)},100%{{offset-distance:{P}px}}}}")
    if hd.get("cursor"):
        head = f'<rect x="-3" y="-6" width="7" height="12" fill="{hd["fill"]}"/>'
    elif hd.get("square"):
        r = hd["r"]
        head = (f'<rect x="{-r}" y="{-r}" width="{2 * r}" height="{2 * r}" fill="{hd["fill"]}"/>'
                f'<rect x="1" y="-4" width="3" height="3" fill="{hd["eye"]}"/>'
                f'<rect x="1" y="1" width="3" height="3" fill="{hd["eye"]}"/>')
    else:
        r = hd["r"]
        head = (f'<path class="tongue" d="M{r - 1} 0 H{r + 5} M{r + 5} 0 l2.5 -2 M{r + 5} 0 l2.5 2" '
                f'stroke="{hd["tongue"]}" stroke-width="1.3" stroke-linecap="round" fill="none"/>'
                f'<ellipse rx="{r + 1}" ry="{r}" fill="{hd["fill"]}"/>'
                f'<circle cx="2.2" cy="-3.1" r="2" fill="#fff"/><circle cx="2.2" cy="3.1" r="2" fill="#fff"/>'
                f'<circle cx="2.9" cy="-3.1" r="1.1" fill="{hd["eye"]}"/><circle cx="2.9" cy="3.1" r="1.1" fill="{hd["eye"]}"/>')
    head_g = f'<g id="head">{head}</g>'

    # -- score (rolling digits) -------------------------------------------------
    running, score_steps = 0, []
    for step in eat_order:
        pos = next(p for p, s in eats.items() if s == step)
        running += cells[pos][1]
        score_steps.append((step, running))
    ctx["score_steps"], ctx["pct"], ctx["css"] = score_steps, pct, css

    c = th["cells"]
    cell_css = "".join(f".c{i}{{fill:{col}}}" for i, col in enumerate(c))
    if "cells_dark" in th:
        dark = "".join(f".c{i}{{fill:{col}}}" for i, col in enumerate(th["cells_dark"]))
        dark += f"[class*=' o']{{stroke:{th['outline_dark']}}}"
        cell_css += f"@media (prefers-color-scheme:dark){{{dark}}}"

    chrome_defs, back, front = CHROME[theme_name](ctx)

    style = f"""
.p,.b,#head,#snake,.anim{{animation-duration:{T:.2f}s;animation-iteration-count:infinite;animation-fill-mode:both}}
.p{{transform-box:fill-box;transform-origin:center;animation-timing-function:ease-out}}
.b,#head{{animation-timing-function:linear}}
#head,.tr{{offset-path:path('{d}');animation-name:hd;offset-rotate:auto}}
.tr{{animation-duration:{T:.2f}s;animation-iteration-count:infinite;animation-fill-mode:both;animation-timing-function:linear}}
.grow{{animation-timing-function:steps(1,end)}}
#snake{{animation-name:fade}}
.tongue{{animation:tongue .9s steps(1,end) infinite}}
@keyframes tongue{{0%{{opacity:0}}55%{{opacity:1}}}}
@keyframes fade{{0%,{end:.2f}%{{opacity:1}}{end + 1:.2f}%,100%{{opacity:0}}}}
.dg{{animation-timing-function:steps(1,end)}}
text{{font-family:{th['font']}}}
{cell_css}{''.join(css)}"""

    glow = ' filter="url(#glow)"' if th["glow"] else ""
    dots = DOTS if theme_name == "terminal" else ""
    bg = f'<rect width="{W}" height="{H}" rx="12" fill="{th["bg"]}"/>' if th["bg"] else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<title>{user}'s contribution snake</title>
<style>{style}</style>
<defs>
<filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="board"><rect x="{pl - 6}" y="{pt - 6}" width="{gw + 12}" height="{gh + 12}"/></clipPath>
{chrome_defs}
</defs>
<g>{bg}{back}
<g>{''.join(cell_svg)}</g>
<g{"" if "trail" in th else glow}>{''.join(pellets)}</g>
<g id="snake" clip-path="url(#board)"><g{glow}>{''.join(body)}{head_g}</g></g>
{front}
</g>{dots}
</svg>"""


# ---- per-theme chrome ---------------------------------------------------------

def odometer(ctx, x, y, size, fill, digits=5, extra=""):
    pct, css, adv = ctx["pct"], ctx["css"], size * 0.62
    cols = []
    for dgt in range(digits):
        place = 10 ** (digits - 1 - dgt)
        frames, last = ["0%{transform:translateY(0)}"], 0
        for step, s in ctx["score_steps"]:
            v = (s // place) % 10
            if v != last:
                frames.append(f"{pct(step)}{{transform:translateY({-v * size * 1.2:.1f}px)}}")
                last = v
        css.append(f"@keyframes d{dgt}{{{''.join(frames)}}}.d{dgt}{{animation-name:d{dgt}}}")
        nums = "".join(f'<text y="{i * size * 1.2:.1f}">{i}</text>' for i in range(10))
        cols.append(f'<g transform="translate({dgt * adv:.1f},0)"><g class="anim dg d{dgt}">{nums}</g></g>')
    clip = f'<clipPath id="odo"><rect x="-1" y="{-size}" width="{digits * adv + 2:.1f}" height="{size * 1.25:.1f}"/></clipPath>'
    g = f'<g transform="translate({x},{y})" clip-path="url(#odo)" font-size="{size}" fill="{fill}"{extra}>{"".join(cols)}</g>'
    return clip, g


def overlay(ctx, css_name, inner):
    e = ctx["end"]
    ctx["css"].append(f"@keyframes {css_name}{{0%,{e:.2f}%{{opacity:0}}{e + 1.2:.2f}%,98.5%{{opacity:1}}100%{{opacity:0}}}}"
                      f".{css_name}{{animation-name:{css_name}}}")
    return f'<g class="anim {css_name}">{inner}</g>'


def chrome_native(ctx):
    return "", "", ""


def chrome_gameboy(ctx):
    W, H, pl, pt, gw, gh = (ctx[k] for k in ("W", "H", "pl", "pt", "gw", "gh"))
    clip, score = odometer(ctx, W - pl - 5 * 8.1, 32, 13, "#0f380f", extra=' font-weight="700"')
    back = (f'<rect x="{pl - 12}" y="{pt - 12}" width="{gw + 24}" height="{gh + 24}" fill="#8bac0f" '
            f'stroke="#0f380f" stroke-width="3"/>'
            f'<rect x="{pl - 7}" y="{pt - 7}" width="{gw + 14}" height="{gh + 14}" fill="none" '
            f'stroke="#306230" stroke-width="1" stroke-dasharray="2 2"/>'
            f'<text x="{pl - 12}" y="32" font-size="13" font-weight="700" fill="#0f380f" letter-spacing="2">'
            f'{ctx["user"].upper()}</text>'
            f'<text x="{W / 2}" y="32" font-size="13" font-weight="700" fill="#306230" text-anchor="middle" '
            f'letter-spacing="3">- COMMIT SNAKE -</text>'
            f'<text x="{W - pl - 5 * 8.1 - 10}" y="32" font-size="13" font-weight="700" fill="#306230" '
            f'text-anchor="end">SCORE</text>'
            f'<text x="{pl - 12}" y="{H - 16}" font-size="11" font-weight="700" fill="#306230" letter-spacing="2">'
            f'HI {ctx["total"]:05d}</text>'
            f'<text x="{W - pl + 12}" y="{H - 16}" font-size="11" font-weight="700" fill="#306230" '
            f'text-anchor="end" letter-spacing="2">PRESS START</text>')
    over = overlay(ctx, "over", (
        f'<rect x="{W / 2 - 90}" y="{pt + gh / 2 - 22}" width="180" height="40" fill="#9bbc0f" stroke="#0f380f" stroke-width="3"/>'
        f'<text x="{W / 2}" y="{pt + gh / 2 + 4}" font-size="17" font-weight="700" fill="#0f380f" '
        f'text-anchor="middle" letter-spacing="4">GAME OVER</text>'))
    return clip, back, score + over


def chrome_glass(ctx):
    W, H, pl, pt, gw, gh = (ctx[k] for k in ("W", "H", "pl", "pt", "gw", "gh"))
    clip, score = odometer(ctx, W - pl - 5 * 9.9 + 4, 38, 16, "#ffffff", extra=' font-weight="600"')
    defs = (clip +
            '<radialGradient id="a1"><stop offset="0" stop-color="#6d3cff" stop-opacity=".55"/>'
            '<stop offset="1" stop-color="#6d3cff" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="a2"><stop offset="0" stop-color="#00c2ff" stop-opacity=".4"/>'
            '<stop offset="1" stop-color="#00c2ff" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="a3"><stop offset="0" stop-color="#ff3cac" stop-opacity=".35"/>'
            '<stop offset="1" stop-color="#ff3cac" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="card"><rect width="{W}" height="{H}" rx="12"/></clipPath>')
    ctx["css"].append("@keyframes drift{0%,100%{transform:translate(0,0)}50%{transform:translate(60px,14px)}}"
                      ".drift{animation:drift 14s ease-in-out infinite}"
                      ".drift2{animation:drift 18s ease-in-out infinite reverse}")
    back = (f'<g clip-path="url(#card)">'
            f'<ellipse class="drift" cx="{W * .18}" cy="{H * .2}" rx="260" ry="130" fill="url(#a1)"/>'
            f'<ellipse class="drift2" cx="{W * .75}" cy="{H * .9}" rx="300" ry="120" fill="url(#a2)"/>'
            f'<ellipse class="drift" cx="{W * .55}" cy="{H * .05}" rx="200" ry="80" fill="url(#a3)"/></g>'
            f'<rect x="{pl - 12}" y="{pt - 12}" width="{gw + 24}" height="{gh + 24}" rx="10" fill="#ffffff08" '
            f'stroke="#ffffff1f"/>'
            f'<text x="{pl - 12}" y="36" font-size="15" font-weight="600" fill="#fff">{ctx["user"]}</text>'
            f'<text x="{pl - 12}" y="36" dx="{len(ctx["user"]) * 8.6 + 8:.0f}" font-size="13" fill="#ffffff80">'
            f'contribution snake</text>'
            f'<text x="{W - pl - 5 * 9.9 - 4}" y="37" font-size="12" fill="#ffffff80" text-anchor="end" '
            f'letter-spacing="1">COMMITS EATEN</text>'
            f'<text x="{pl - 12}" y="{H - 17}" font-size="11.5" fill="#ffffff66">{ctx["total"]} contributions in the last year</text>'
            f'<text x="{W - pl + 12}" y="{H - 17}" font-size="11.5" fill="#ffffff66" text-anchor="end">'
            f'updated daily</text>')
    over = overlay(ctx, "over", (
        f'<rect x="{W / 2 - 120}" y="{pt + gh / 2 - 20}" width="240" height="38" rx="19" fill="#0b1020cc" stroke="#ffffff33"/>'
        f'<text x="{W / 2}" y="{pt + gh / 2 + 4}" font-size="14" font-weight="600" fill="#fff" '
        f'text-anchor="middle">✦ all {ctx["total"]} commits eaten ✦</text>'))
    return defs, back, score + over


def chrome_terminal(ctx):
    W, H, pl, pt, gw, gh = (ctx[k] for k in ("W", "H", "pl", "pt", "gw", "gh"))
    clip, score = odometer(ctx, 0, 0, 12, "#ff5c5c")
    u = ctx["user"]
    ctx["css"].append("@keyframes cur{50%{opacity:0}}.cur{animation:cur 1s steps(1,end) infinite}")
    prompt = f"{u}@github:~$ ./snake --eat commits"
    back = (f'<rect x="0" y="0" width="{W}" height="26" rx="12" fill="#1a0c0c"/>'
            f'<rect x="0" y="14" width="{W}" height="12" fill="#1a0c0c"/>'
            f'<circle cx="18" cy="13" r="5" fill="#ff5f57"/><circle cx="34" cy="13" r="5" fill="#febc2e"/>'
            f'<circle cx="50" cy="13" r="5" fill="#28c840"/>'
            f'<text x="{W / 2}" y="17" font-size="11" fill="#8a5f5f" text-anchor="middle">{u} — zsh</text>'
            f'<text x="{pl - 10}" y="48" font-size="12" fill="#ff5c5c" filter="url(#glow)">{prompt}</text>')
    status = (f'<text x="{pl - 10}" y="{H - 16}" font-size="12" fill="#e03434">[</text>'
              f'<g transform="translate({pl - 2},{H - 16})">{score}</g>'
              f'<text x="{pl + 34}" y="{H - 16}" font-size="12" fill="#e03434">/{ctx["total"]}] commits consumed</text>'
              f'<text x="{W - pl + 10}" y="{H - 16}" font-size="12" fill="#9e1c1c" text-anchor="end">'
              f'refresh: daily · 0 errors</text>')
    over = overlay(ctx, "over", (
        f'<rect x="{W / 2 - 150}" y="{pt + gh / 2 - 18}" width="300" height="34" fill="#0a0505" stroke="#e03434"/>'
        f'<text x="{W / 2 - 138}" y="{pt + gh / 2 + 4}" font-size="12" fill="#ff5c5c" filter="url(#glow)">'
        f'&gt; process exited (0). all fed.</text>'
        f'<rect class="cur" x="{W / 2 + 108}" y="{pt + gh / 2 - 7}" width="7" height="13" fill="#ff5c5c"/>'))
    return clip, back, status + over


CHROME = {"native": chrome_native, "gameboy": chrome_gameboy,
          "glass": chrome_glass, "terminal": chrome_terminal}


def main():
    user, out = sys.argv[1], sys.argv[2]
    theme = sys.argv[3] if len(sys.argv) > 3 else "terminal"
    width, cells, total = fetch(user, os.environ["GITHUB_TOKEN"])
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        svg = render(user, width, cells, total, theme)
        f.write(palette_vars(svg) if theme == "terminal" else svg)
    print(f"wrote {out} ({theme})")


if __name__ == "__main__":
    main()
