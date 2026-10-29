"""Small SVG helpers shared by the opening-schematic drafts.

Everything is drawn in poster units (the poster's viewBox is 5344 x 3780), so a
draft can be pasted into `SfN_2026.svg` at the Section 1 figure slot
(x 209.6, y 1053.6, 1362 x 779) without rescaling.  Palette and font follow the
poster: Source Sans 3; test = black, redundancy = blue, noise = red, bPCA = green.
"""

import math

import numpy as np

# Poster palette ---------------------------------------------------------------
BLACK = "#100f0d"      # test data / body text
BLUE = "#3f6fd1"       # redundancy baseline
RED = "#f93d53"        # noise baseline
GREEN = "#5e9a3e"      # bPCA
GREEN_LIGHT = "#88bc69"
PURPLE = "#b97ad7"
GREY = "#7a7f87"       # secondary text
GREY_LIGHT = "#c9ccd1"
PANEL = "#eef1f2"      # grey boxes on the poster
DARK = "#26282f"       # header bars
TEAL = "#2a8c85"       # PC1 colour in the cameras figure
ORANGE = "#f0932b"     # PC2 colour in the cameras figure
WHITE = "#ffffff"
DIRS = {0: BLACK, 45: RED, 90: BLUE, 135: PURPLE}   # grating-direction colours, as in Section 3

FONT = "font-family:'Source Sans 3',sans-serif"


class SVG:
    def __init__(self, w=1460, h=780):
        self.w, self.h = w, h
        self.parts = []
        self.defs = []

    # -- primitives ------------------------------------------------------------
    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=0, rx=0, extra=""):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                 f'style="fill:{fill};stroke:{stroke};stroke-width:{sw}" {extra}/>')

    def circle(self, cx, cy, r, fill=BLACK, stroke="none", sw=0, opacity=1.0, extra=""):
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
                 f'style="fill:{fill};stroke:{stroke};stroke-width:{sw};opacity:{opacity}" {extra}/>')

    def ellipse(self, cx, cy, rx, ry, angle=0, fill="none", stroke=BLACK, sw=4, dash=None, opacity=1.0):
        d = f";stroke-dasharray:{dash}" if dash else ""
        self.add(f'<ellipse cx="0" cy="0" rx="{rx:.1f}" ry="{ry:.1f}" '
                 f'transform="translate({cx:.1f},{cy:.1f}) rotate({angle:.1f})" '
                 f'style="fill:{fill};stroke:{stroke};stroke-width:{sw};opacity:{opacity}{d}"/>')

    def line(self, x1, y1, x2, y2, stroke=BLACK, sw=4, dash=None, cap="round", opacity=1.0):
        d = f";stroke-dasharray:{dash}" if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'style="fill:none;stroke:{stroke};stroke-width:{sw};stroke-linecap:{cap};opacity:{opacity}{d}"/>')

    def path(self, d, stroke=BLACK, sw=4, fill="none", dash=None, opacity=1.0, cap="round", join="round"):
        dd = f";stroke-dasharray:{dash}" if dash else ""
        self.add(f'<path d="{d}" style="fill:{fill};stroke:{stroke};stroke-width:{sw};'
                 f'stroke-linecap:{cap};stroke-linejoin:{join};opacity:{opacity}{dd}"/>')

    def polyline(self, pts, **kw):
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.path(d, **kw)

    def text(self, x, y, s, size=34, fill=BLACK, weight=400, anchor="start", italic=False, extra="", opacity=1.0):
        st = "font-style:italic;" if italic else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" style="{FONT};font-size:{size}px;font-weight:{weight};'
                 f'fill:{fill};text-anchor:{anchor};{st}opacity:{opacity}" {extra}>{s}</text>')

    def rich(self, x, y, runs, size=34, anchor="start"):
        """runs: list of (text, {fill, weight, italic, baseline-shift, size})."""
        spans = []
        for s, st in runs:
            style = ";".join(
                f"{k}:{v}" for k, v in {
                    "fill": st.get("fill", BLACK),
                    "font-weight": st.get("weight", 400),
                    "font-style": "italic" if st.get("italic") else "normal",
                    "font-size": f"{st.get('size', size)}px",
                }.items())
            bs = f' baseline-shift="{st["shift"]}"' if "shift" in st else ""
            spans.append(f'<tspan style="{style}"{bs}>{s}</tspan>')
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" style="{FONT};font-size:{size}px;text-anchor:{anchor}">'
                 + "".join(spans) + "</text>")

    def arrow(self, x1, y1, x2, y2, stroke=BLACK, sw=5, head=18, opacity=1.0):
        """Straight arrow with a filled triangular head."""
        ang = math.atan2(y2 - y1, x2 - x1)
        bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
        self.line(x1, y1, bx, by, stroke=stroke, sw=sw, opacity=opacity)
        s = head * 0.6
        p1 = (bx + s * math.sin(ang), by - s * math.cos(ang))
        p2 = (bx - s * math.sin(ang), by + s * math.cos(ang))
        self.add(f'<path d="M{x2:.1f},{y2:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} Z" '
                 f'style="fill:{stroke};stroke:none;opacity:{opacity}"/>')

    def darrow(self, cx, cy, dx, dy, **kw):
        """Double-headed arrow centred on (cx, cy) with half-extent (dx, dy)."""
        self.arrow(cx, cy, cx + dx, cy + dy, **kw)
        self.arrow(cx, cy, cx - dx, cy - dy, **kw)

    def cross(self, cx, cy, r=10, stroke=BLACK, sw=5):
        self.line(cx - r, cy, cx + r, cy, stroke=stroke, sw=sw)
        self.line(cx, cy - r, cx, cy + r, stroke=stroke, sw=sw)

    def tick(self, cx, cy, size=22, stroke=GREEN, sw=6):
        self.path(f"M{cx - size*0.5:.1f},{cy:.1f} L{cx - size*0.1:.1f},{cy + size*0.4:.1f} L{cx + size*0.55:.1f},{cy - size*0.5:.1f}",
                  stroke=stroke, sw=sw)

    def xmark(self, cx, cy, size=20, stroke=RED, sw=6):
        self.line(cx - size/2, cy - size/2, cx + size/2, cy + size/2, stroke=stroke, sw=sw)
        self.line(cx - size/2, cy + size/2, cx + size/2, cy - size/2, stroke=stroke, sw=sw)

    def panel(self, x, y, w, h, fill=PANEL, rx=18):
        self.rect(x, y, w, h, fill=fill, rx=rx)

    def label(self, x, y, letter, title=None, size=40, color=BLACK):
        """Panel label '(a) Title' in the poster's semibold style."""
        runs = [(f"({letter})", {"weight": 700}), ]
        if title:
            runs.append(("  " + title, {"weight": 600, "fill": color}))
        self.rich(x, y, runs, size=size)

    def op(self, x, y, s, size=64, fill=GREY):
        self.text(x, y, s, size=size, fill=fill, weight=300, anchor="middle")

    # -- output ----------------------------------------------------------------
    def save(self, path, title=""):
        body = "\n".join(self.parts)
        defs = ("<defs>\n" + "\n".join(self.defs) + "\n</defs>\n") if self.defs else ""
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
               f'width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">\n'
               f'<title>{title}</title>\n{defs}{body}\n</svg>\n')
        with open(path, "w") as f:
            f.write(svg)


# Geometry helpers ------------------------------------------------------------
def gauss_cloud(n, cx, cy, sx, sy, angle_deg, rng):
    """n points from a 2-D Gaussian with std (sx, sy) rotated by angle_deg, centred at (cx, cy)."""
    a = math.radians(angle_deg)
    u = rng.normal(size=n) * sx
    v = rng.normal(size=n) * sy
    x = cx + u * math.cos(a) - v * math.sin(a)
    y = cy + u * math.sin(a) + v * math.cos(a)
    return x, y


def smooth_noise(n, rng, cutoff=0.08, seed_scale=1.0):
    """Low-pass filtered white noise, unit std: a 'slow shared fluctuation'."""
    w = rng.normal(size=n)
    k = int(1 / cutoff)
    kern = np.exp(-0.5 * (np.arange(-3 * k, 3 * k + 1) / k) ** 2)
    s = np.convolve(w, kern, mode="same")
    s = (s - s.mean()) / s.std()
    return s * seed_scale


def hex_mix(c1, c2, t):
    """Linear mix of two hex colours, t in [0,1] from c1 to c2."""
    a = [int(c1[i:i+2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i+2], 16) for i in (1, 3, 5)]
    m = [round(x + (y - x) * t) for x, y in zip(a, b)]
    return "#%02x%02x%02x" % tuple(m)
