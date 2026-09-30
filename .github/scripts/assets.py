"""Static terminal-theme README assets (header, stack, link buttons).

These don't depend on live data, so run this once after editing and commit
the output in assets/:  python .github/scripts/assets.py
All-in-one window (needs the day's snake):
    python .github/scripts/assets.py combined dist/commit-snake.svg dist/profile.svg
Icons in icons/ are from Simple Icons (CC0) and Devicon (MIT).
"""
import os
import re
import sys

from snake import DOTS, round_swap, theme_swap

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

    def __init__(self, title, prefix=""):
        self.p = prefix  # keeps class/id names unique when several windows share one SVG
        self.title, self.body, self.css, self.defs, self.raw = title, [], [], [], []
        self.t, self.y, self.n = 0.4, 56, 0

    def _reveal(self, start, dur, steps):
        k = self.n
        self.n += 1
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
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>{''.join(self.defs)}{theme_swap()}</defs>
<g filter="url(#theme)"><rect width="{W}" height="{H}" rx="12" fill="{BG}"/>
<rect width="{W}" height="26" rx="12" fill="{BAR}"/><rect y="14" width="{W}" height="12" fill="{BAR}"/>
<text x="{W / 2}" y="17" font-size="11" fill="#8a5f5f" text-anchor="middle">{self.title}</text>
<g filter="url(#glow)">{''.join(self.body)}</g></g>
{''.join(self.raw)}{DOTS}
</svg>"""


def header(prefix=""):
    t = Term(f"{USER} — zsh", prefix)
    t.type("whoami")
    t.out(f'<text x="18" y="{t.y + 26}" font-size="44" font-weight="800" fill="{HI}" letter-spacing="3">'
          f'UZAIR AHMED</text>', height=LINE * 2 + 12, pause=0.5)
    t.type("cat about.txt")
    for line in ["&gt; I write code to make pixels come alive.",
                 "&gt; stack: C · C++ · C# · Unity · Unreal · HTML/CSS"]:
        t.out(f'<text x="20" y="{t.y}" fill="{MID}">{line}</text>', pause=0.18)
    t.cursor()
    return t.svg()


def stack(prefix=""):
    t = Term(f"{USER} — ~/stack", prefix)
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


def morph(snake_svg):
    """Header, snake and stack as three windows that merge into one terminal
    and split apart again every round (in step with the red/green swap)."""
    gap = 10
    parts, y, seams = [], 0, []
    for i, svg in enumerate([header("h"), snake_svg, stack("s")]):
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
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<title>{USER} — terminal profile</title>
<defs>{theme_swap()}</defs>
{''.join(parts)}
<g opacity="0" filter="url(#theme)">{round_swap("opacity", "0", "1")}{fill}</g>
</svg>"""


def button(name, label):
    w, h = 168, 38
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
<style>text{{font-family:{MONO};font-size:13px}}</style>
<defs>{theme_swap()}</defs><g filter="url(#theme)">
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
