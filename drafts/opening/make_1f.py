"""Option 1f: the network opening that carries the construction, on oblique planes.

(a) The grating manifold (a line of directions) feeds the network and lights a set of units,
    whose links strengthen.  (b) The gray screen pumps the network through one shared input and
    lights a different set, visibly a subset of (a)'s.  The spontaneous set is drawn as redundant:
    one signal, copied by many units.  (?) How to keep only what the grating engaged.

Run from this folder:  python3 make_1f.py
"""

import math
import os

import numpy as np

from svgkit import SVG, BLACK, BLUE, RED, GREEN, GREY, GREY_LIGHT, PANEL, DARK, WHITE, DIRS, smooth_noise

HERE = os.path.dirname(os.path.abspath(__file__))

# Units in plane coordinates (u, v) on a 360 x 240 sheet: the grating-driven group at the left
# (nearest the stimulus), the spontaneous group at the right (nearest the shared input), bystanders between.
NODES = [(230, 40), (300, 30), (210, 110), (280, 90), (240, 170), (310, 150), (340, 80),     # 0-6 spontaneous
         (40, 40), (100, 70), (60, 140), (120, 190),                                          # 7-10 grating-driven
         (160, 20), (180, 215), (330, 215), (30, 225), (180, 120)]                            # 11-15 bystanders
SPONT = [0, 1, 2, 3, 4, 5, 6]
STIM = [7, 8, 9, 10]
TUNED = {0: 7, 45: 8, 90: 9, 135: 10}          # direction -> the unit it drives most
SPONT_EDGES = [(0, 1, 4), (0, 2, 3), (0, 3, 3), (1, 3, 4), (1, 6, 3), (3, 6, 4), (2, 3, 3), (2, 4, 3),
               (3, 5, 4), (4, 5, 3), (5, 6, 3), (3, 4, 2)]
STIM_EDGES = [(7, 8, 5), (7, 9, 4), (8, 9, 5), (8, 10, 4), (9, 10, 5), (7, 10, 3)]
SHEAR, SQUASH = 0.5, 0.6     # oblique projection of the sheet: x += SHEAR * v, y = SQUASH * v


def project(u, v, ox, oy, k):
    return ox + k * (u + SHEAR * v), oy + k * SQUASH * v


def plane(s, ox, oy, k, fill="#e3e6e9"):
    c = [project(u, v, ox, oy, k) for (u, v) in ((0, 0), (360, 0), (360, 240), (0, 240))]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in c) + " Z"
    s.path(d, stroke="#c9ccd1", sw=2, fill=fill)


def network(s, ox, oy, k, edges, edge_color, lit, fill_color, node_r=11):
    plane(s, ox, oy, k)
    P = [project(u, v, ox, oy, k) for u, v in NODES]
    for i, j, w in edges:
        s.line(P[i][0], P[i][1], P[j][0], P[j][1], stroke=edge_color, sw=w * 1.3)
    for n, (x, y) in enumerate(P):
        on = n in lit
        s.circle(x, y, node_r, fill=fill_color if on else WHITE, stroke=BLACK if on else GREY, sw=3 if on else 2.5)
    return P


def grating_icon(s, cx, cy, r, deg, uid):
    """A circular patch of stripes at the given orientation (what the mouse saw)."""
    s.defs.append(f'<clipPath id="clip{uid}"><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}"/></clipPath>')
    s.add(f'<g clip-path="url(#clip{uid})" transform="rotate({deg} {cx:.1f} {cy:.1f})">')
    s.rect(cx - r, cy - r, 2 * r, 2 * r, fill="#6c6f75")
    n = 7
    for i in range(n):
        x = cx - r + (i + 0.5) * 2 * r / n
        s.rect(x - r / n * 0.5, cy - r, r / n, 2 * r, fill="#f2f3f4")
    s.add('</g>')
    s.circle(cx, cy, r, fill="none", stroke=BLACK, sw=2.5)


def curved_arrow(s, x1, y1, x2, y2, stroke, sw=3, bend=40, head=14, opacity=1.0):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    cx, cy = mx - dy / L * bend, my + dx / L * bend
    s.path(f"M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}", stroke=stroke, sw=sw, opacity=opacity)
    ang = math.atan2(y2 - cy, x2 - cx)
    p1 = (x2 - head * math.cos(ang - 0.45), y2 - head * math.sin(ang - 0.45))
    p2 = (x2 - head * math.cos(ang + 0.45), y2 - head * math.sin(ang + 0.45))
    s.add(f'<path d="M{x2:.1f},{y2:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} Z" '
          f'style="fill:{stroke};stroke:none;opacity:{opacity}"/>')


def wiggle(s, x, y, w, h, sig, color, sw=2.5, opacity=1.0):
    n = len(sig)
    pts = [(x + i / (n - 1) * w, y - v * h / 2) for i, v in enumerate(sig)]
    s.polyline(pts, stroke=color, sw=sw, opacity=opacity)


def option1f():
    rng = np.random.default_rng(3)
    s = SVG()
    sig = smooth_noise(60, rng, cutoff=0.12)
    sig = sig / np.abs(sig).max()
    k = 0.9
    PX, PW = 30, 800                       # left panels

    # ---- (a) drifting gratings ---------------------------------------------------------------
    s.panel(PX, 40, PW, 345)
    s.label(46, 82, "a", "Drifting gratings", size=34)
    s.text(46, 112, "the stimulus set is a line of directions; each unit it drives reads a different point on it",
           size=22, fill=GREY)
    mx = 110
    s.path(f"M{mx},150 C{mx + 20},195 {mx - 20},280 {mx},335", stroke=BLACK, sw=3)
    s.text(mx, 140, "direction", size=21, fill=GREY, anchor="middle")
    ys = {0: 170, 45: 218, 90: 266, 135: 314}
    ox, oy = 250, 165
    P = network(s, ox, oy, k, SPONT_EDGES + STIM_EDGES, BLACK, set(SPONT) | set(STIM), DARK)
    for d, yy in ys.items():
        t = (yy - 150) / 185
        xx = mx + 20 * math.sin(2 * math.pi * t) * 0.75
        grating_icon(s, xx, yy, 16, d, f"a{d}")
        s.text(xx - 24, yy + 7, f"{d}°", size=20, fill=DIRS[d], weight=600, anchor="end")
        tx, ty = P[TUNED[d]]
        curved_arrow(s, xx + 19, yy, tx - 13, ty, DIRS[d], sw=3, bend=-18 if d < 90 else 18)
    # the shared input continues during the stimulus (faint, same place as in b)
    bx, by = 690, 150
    s.rect(bx, by, 130, 46, fill=WHITE, stroke=GREY_LIGHT, sw=2, rx=10)
    wiggle(s, bx + 10, by + 23, 110, 30, sig, BLUE, opacity=0.5)
    s.text(bx + 65, by + 66, "shared input", size=17, fill=GREY, anchor="middle")
    s.text(bx + 65, by + 86, "continues", size=17, fill=GREY, anchor="middle")
    for n in SPONT:
        curved_arrow(s, bx + 10, by + 40, P[n][0] + 10, P[n][1] - 10, BLUE, sw=1.5, bend=-10, head=8, opacity=0.35)
    s.rich(46, 365, [("Units that fire together get stronger links. ", {"weight": 600}),
                     ("Eleven units light up.", {"fill": GREY})], size=22)

    # ---- (b) gray screen -------------------------------------------------------------------
    s.panel(PX, 400, PW, 345)
    s.label(46, 442, "b", "Gray screen", size=34)
    s.text(46, 472, "no stimulus, yet one shared signal (arousal, running) pumps a group of units", size=22, fill=GREY)
    s.circle(mx, 600, 17, fill="#a8abb0", stroke=BLACK, sw=2.5)
    s.text(mx, 640, "gray", size=19, fill=GREY, anchor="middle")
    s.text(mx, 662, "screen", size=19, fill=GREY, anchor="middle")
    ox2, oy2 = 250, 525
    P2 = network(s, ox2, oy2, k, SPONT_EDGES, BLUE, set(SPONT), BLUE)
    bx, by = 690, 512
    s.rect(bx, by, 130, 46, fill=WHITE, stroke=BLUE, sw=2.5, rx=10)
    wiggle(s, bx + 10, by + 23, 110, 30, sig, BLUE)
    s.text(bx + 65, by - 8, "shared input", size=20, fill=BLUE, weight=600, anchor="middle")
    for n in SPONT:
        curved_arrow(s, bx + 10, by + 40, P2[n][0] + 10, P2[n][1] - 10, BLUE, sw=2, bend=-10, head=9, opacity=0.8)
    # the redundancy cue: peripheral lit units each show a copy of the same signal
    for n, (dx, dy) in ((0, (-44, -30)), (2, (-50, 4)), (4, (-18, 28)), (5, (8, 28)), (6, (12, -28))):
        x, y = P2[n]
        s.rect(x + dx - 4, y + dy - 10, 40, 20, fill=WHITE, stroke=GREY_LIGHT, sw=1, rx=5)
        wiggle(s, x + dx, y + dy, 32, 12, sig, BLUE, sw=1.5)
    s.rich(46, 725, [("Seven units light up, all copying one signal: ", {"weight": 600}),
                     ("redundant", {"fill": BLUE, "weight": 700}), (" links. ", {"weight": 600}),
                     ("A subset of the units in (a).", {"fill": GREY})], size=22)

    # ---- the question ------------------------------------------------------------------------
    s.line(PX + PW, 212, 880, 398, stroke=BLACK, sw=3)
    s.line(PX + PW, 572, 880, 412, stroke=BLACK, sw=3)
    s.arrow(880, 405, 1000, 405, stroke=BLACK, sw=4, head=18)
    s.text(940, 372, "?", size=64, weight=700, anchor="middle")
    s.text(940, 445, "(a) − (b)", size=24, fill=GREY, anchor="middle")

    # ---- (c) what the grating engaged --------------------------------------------------------
    s.panel(1010, 150, 420, 510)
    s.label(1026, 192, "c", "What the grating engaged", size=30, color=GREEN)
    s.text(1026, 222, "the units and links in (a) that are not in (b)", size=20, fill=GREY)
    network(s, 1030, 262, 0.78, STIM_EDGES, GREEN, set(STIM), GREEN)
    s.text(1026, 470, "Subtracting the pictures is the idea.", size=21)
    s.text(1026, 498, "Baseline PCA does it to covariance:", size=21)
    s.rich(1026, 526, [("variance in (a) ", {}), ("relative to (b)", {"fill": BLUE, "weight": 600}), (",", {})], size=21)
    s.rich(1026, 554, [("above the ", {}), ("spiking noise", {"fill": RED, "weight": 600}), (",", {})], size=21)
    s.text(1026, 582, "one direction at a time.", size=21)
    s.text(1026, 630, "PCA on (a) alone returns the biggest", size=19, fill=GREY)
    s.text(1026, 654, "cluster, which is the redundant one.", size=19, fill=GREY)
    s.save(os.path.join(HERE, "option1f-construction.svg"), "Option 1f: the construction, as networks")


if __name__ == "__main__":
    option1f()
    print("wrote option1f-construction.svg")
