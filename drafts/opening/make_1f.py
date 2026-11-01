"""Option 1f: the construction, drawn in the house style of the Cosyne 2025, OHBM 2025 and
MiB 2026 posters: oblique plates with a visible edge (the MiB "population bath"), neurons as small
flattened cell glyphs, soft glows for activity, thin semantic-coloured arrows with small heads,
real-looking stimuli and traces, bold panel letters and almost no prose inside the figure.

(a) A line of grating directions feeds a sheet of neurons; each grating drives a different cell
    and the shared input keeps driving its own group. Co-active cells are linked.
(b) The gray screen: one shared signal fans out to one group of cells (one signal, many copies).
(?) Which links did the grating add?  (c) The stimulus-engaged set.

Run from this folder:  python3 make_1f.py
"""

import math
import os

import numpy as np

from svgkit import SVG, BLACK, BLUE, RED, GREEN, GREY, GREY_LIGHT, DARK, WHITE, DIRS, smooth_noise

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#2b2f36"          # outlines, as in the Makie figures
PLATE = "#f3f4f6"        # sheet face
PLATE_EDGE = "#b9bec5"   # sheet thickness
CELL = "#e4e7ea"         # resting cell fill
SHEAR, SQUASH = 0.3, 0.72
SHEET_W, SHEET_H = 380, 230


def proj(u, v, ox, oy, k):
    return ox + k * (u + SHEAR * v), oy + k * SQUASH * v


def plate(s, ox, oy, k, thickness=7):
    """An oblique sheet with a visible edge, like the population bath in the MiB 2026 poster."""
    corners = [(0, 0), (SHEET_W, 0), (SHEET_W, SHEET_H), (0, SHEET_H)]
    top = [proj(u, v, ox, oy, k) for u, v in corners]
    side = [(x, y + thickness) for x, y in top]
    d_side = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in side) + " Z"
    s.path(d_side, stroke=PLATE_EDGE, sw=1.5, fill=PLATE_EDGE)
    d_top = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in top) + " Z"
    s.path(d_top, stroke="#9aa0a6", sw=1.5, fill=PLATE)
    return top


def glow(s, x, y, color, uid, rx=24, ry=18):
    s.defs.append(f'<radialGradient id="g{uid}"><stop offset="0" stop-color="{color}" stop-opacity="0.38"/>'
                  f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
    s.add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx}" ry="{ry}" style="fill:url(#g{uid});stroke:none"/>')


def cell(s, x, y, fill=CELL, rx=8.5, ry=6.4, sw=1.2):
    """A cell body lying on the sheet: a foreshortened ellipse with an ink outline."""
    s.add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx}" ry="{ry}" style="fill:{fill};stroke:{INK};stroke-width:{sw}"/>')


def thin_arrow(s, x1, y1, x2, y2, color, sw=1.8, head=9, bend=0.0, opacity=0.9):
    """A thin, lightly curved arrow with a small head, as in the hierarchy schematics."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    cx, cy = (x1 + x2) / 2 + nx * bend, (y1 + y2) / 2 + ny * bend
    s.path(f"M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}", stroke=color, sw=sw, opacity=opacity)
    ang = math.atan2(y2 - cy, x2 - cx)
    p1 = (x2 - head * math.cos(ang - 0.4), y2 - head * math.sin(ang - 0.4))
    p2 = (x2 - head * math.cos(ang + 0.4), y2 - head * math.sin(ang + 0.4))
    s.add(f'<path d="M{x2:.1f},{y2:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} Z" '
          f'style="fill:{color};stroke:none;opacity:{opacity}"/>')


def grating(s, cx, cy, size, deg, uid, drift=True):
    """A drifting-grating patch: a rounded square filled with a sinusoid-like stripe gradient."""
    period = size / 3.2
    s.defs.append(
        f'<linearGradient id="gr{uid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{period:.2f}" y2="0" '
        f'spreadMethod="repeat" gradientTransform="rotate({deg} {cx:.1f} {cy:.1f})">'
        f'<stop offset="0" stop-color="#2a2a2a"/><stop offset="0.5" stop-color="#e9e9e9"/>'
        f'<stop offset="1" stop-color="#2a2a2a"/></linearGradient>')
    h = size / 2
    s.add(f'<rect x="{cx - h:.1f}" y="{cy - h:.1f}" width="{size}" height="{size}" rx="{size * 0.12:.1f}" '
          f'style="fill:url(#gr{uid});stroke:{INK};stroke-width:1.6"/>')
    if drift:   # a small white arrow for the drift direction (perpendicular to the stripes)
        a = math.radians(deg)
        ex, ey = math.cos(a) * size * 0.28, math.sin(a) * size * 0.28
        thin_arrow(s, cx - ex, cy - ey, cx + ex, cy + ey, WHITE, sw=2.2, head=7, opacity=0.95)


def trace_box(s, x, y, w, h, sig, color, label, sublabel=None, stroke=INK):
    s.rect(x, y, w, h, fill=WHITE, stroke=stroke, sw=1.4, rx=3)
    n = len(sig)
    pts = [(x + 6 + i / (n - 1) * (w - 12), y + h / 2 - v * (h / 2 - 6)) for i, v in enumerate(sig)]
    s.polyline(pts, stroke=color, sw=2)
    s.text(x + w / 2, y - 8, label, size=21, weight=700, anchor="middle")
    if sublabel:
        s.text(x + w / 2, y + h + 22, sublabel, size=18, fill=GREY, anchor="middle")


def knn_edges(pts, idx, kn=3):
    """Link each active cell to its nearest active neighbours (in sheet coordinates)."""
    edges = set()
    for i in idx:
        d = sorted(((math.dist(pts[i], pts[j]), j) for j in idx if j != i))
        for _, j in d[:kn]:
            edges.add(tuple(sorted((i, j))))
    out = []
    for i, j in edges:
        dist = math.dist(pts[i], pts[j])
        out.append((i, j, 3.2 - 1.6 * min(dist / 140, 1)))
    return out


def sheet(s, ox, oy, k, cells, active, color, edges, uid, dim_inactive=False):
    """Plate, links, glows and cell glyphs. Returns projected cell positions."""
    plate(s, ox, oy, k)
    P = [proj(u, v, ox, oy, k) for u, v in cells]
    for i, j, w in edges:
        s.line(P[i][0], P[i][1], P[j][0], P[j][1], stroke=color, sw=w, opacity=0.85)
    for n in active:
        glow(s, P[n][0], P[n][1], color, f"{uid}{n}")
    for n, (x, y) in enumerate(P):
        if n in active:
            cell(s, x, y, fill=color, sw=1.3)
        else:
            cell(s, x, y, fill=CELL if not dim_inactive else "#eceef1", sw=1.0)
    return P


def option1f():
    rng = np.random.default_rng(12)
    s = SVG()
    # ---- the population: a jittered grid of 36 cells on a 380 x 230 sheet -----------------------
    cells, index = [], {}
    for j in range(5):
        for i in range(7):
            if (i, j) in ((6, 0), (0, 4), (6, 4)):     # leave a few gaps so it is not a lattice
                continue
            u = 28 + i * 54 + rng.uniform(-9, 9)
            v = 24 + j * 46 + rng.uniform(-8, 8)
            index[(i, j)] = len(cells)
            cells.append((u, v))
    # The two groups interleave and share two cells, so the lit set in (a) reads as one network.
    spont = [index[c] for c in ((2, 1), (3, 1), (4, 0), (4, 2), (5, 1), (5, 3), (3, 3), (4, 4), (6, 2))]
    stim = [index[c] for c in ((1, 2), (2, 2), (2, 4), (3, 1), (3, 3))]      # (3,1) and (3,3) are in both
    pref = {0: index[(2, 4)], 45: index[(3, 3)], 90: index[(2, 2)], 135: index[(3, 1)]}   # bottom grating -> lowest cell
    k = 0.92
    sig = smooth_noise(90, rng, cutoff=0.1)
    sig = sig / np.abs(sig).max()

    # ---- (a) drifting gratings ----------------------------------------------------------------
    s.rich(30, 60, [("(a)", {"weight": 700}), ("  Drifting gratings", {"weight": 700})], size=34)
    ox, oy = 270, 150
    e_a = knn_edges(cells, sorted(set(stim) | set(spont)), 3)        # one co-active network, links crossing the groups
    P = sheet(s, ox, oy, k, cells, set(stim) | set(spont), DARK, e_a, "a")
    # the line of directions: four patches receding along a slanted line
    line = [(92, 330), (128, 268), (162, 210), (194, 156)]
    sizes = [58, 52, 46, 42]
    s.line(72, 366, 212, 126, stroke=INK, sw=1.4, opacity=0.6)
    s.text(150, 112, "grating direction", size=19, fill=GREY, anchor="middle")
    for (d, (gx, gy), sz) in zip((0, 45, 90, 135), line, sizes):
        grating(s, gx, gy, sz, d, f"a{d}")
        s.text(gx - sz / 2 - 8, gy + 7, f"{d}°", size=19, fill=DIRS[d], weight=600, anchor="end")
        tx, ty = P[pref[d]]
        thin_arrow(s, gx + sz / 2 + 4, gy, tx - 11, ty, DIRS[d], sw=2, head=9, bend=-14, opacity=0.9)
    # the shared input, still present
    bx, by = 775, 150
    trace_box(s, bx, by, 120, 46, sig, "#8e96a3", "shared input", None, stroke=GREY_LIGHT)
    s.text(bx + 60, by + 66, "still present", size=18, fill=GREY, anchor="middle")
    for n in spont:
        thin_arrow(s, bx + 8, by + 44, P[n][0] + 8, P[n][1] - 7, "#8e96a3", sw=1.2, head=6, bend=-8, opacity=0.5)
    s.text(430, 346, "co-active cells, linked", size=20, fill=GREY)

    # ---- (b) gray screen ------------------------------------------------------------------------
    s.rich(30, 430, [("(b)", {"weight": 700}), ("  Gray screen", {"weight": 700})], size=34)
    ox2, oy2 = 270, 500
    e_b = knn_edges(cells, spont, 3)
    P2 = sheet(s, ox2, oy2, k, cells, set(spont), BLUE, e_b, "b")
    gx, gy, sz = 140, 560, 56
    s.rect(gx - sz / 2, gy - sz / 2, sz, sz, fill="#9d9d9d", stroke=INK, sw=1.6, rx=7)
    s.text(gx, gy + sz / 2 + 26, "gray screen", size=19, fill=GREY, anchor="middle")
    bx, by = 775, 500
    trace_box(s, bx, by, 120, 46, sig, BLUE, "shared input", "arousal, running")
    s.text(bx + 60, by + 90, "one signal,", size=18, fill=BLUE, weight=600, anchor="middle")
    s.text(bx + 60, by + 110, "many cells", size=18, fill=BLUE, weight=600, anchor="middle")
    for n in spont:
        thin_arrow(s, bx + 8, by + 44, P2[n][0] + 8, P2[n][1] - 7, BLUE, sw=1.4, head=7, bend=-8, opacity=0.8)
    s.rich(430, 696, [("redundant", {"fill": BLUE, "weight": 700}), (" links: a subset of the cells in (a)", {"fill": GREY})], size=20)

    # ---- the question ---------------------------------------------------------------------------
    s.line(940, 250, 972, 395, stroke=INK, sw=1.6)
    s.line(940, 610, 972, 415, stroke=INK, sw=1.6)
    thin_arrow(s, 972, 405, 1025, 405, INK, sw=2.2, head=12)
    s.text(1000, 378, "?", size=56, weight=700, anchor="middle")
    s.text(984, 440, "which links did", size=18, fill=GREY)
    s.text(984, 462, "the grating add?", size=18, fill=GREY)

    # ---- (c) stimulus-engaged -----------------------------------------------------------------
    s.rich(1080, 292, [("(c)", {"weight": 700}), ("  Stimulus-engaged", {"weight": 700, "fill": GREEN})], size=34)
    in_b = {(i, j) for i, j, _ in knn_edges(cells, spont, 3)}
    e_c = [e for e in knn_edges(cells, stim, 2) if (e[0], e[1]) not in in_b]   # links in (a) that are not in (b)
    sheet(s, 1080, 330, 0.75, cells, set(stim), GREEN, e_c, "c", dim_inactive=True)
    s.text(1090, 500, "the links in (a) that are not in (b)", size=20, fill=GREY)
    s.rich(1090, 532, [("bPCA: variance in (a) ", {"fill": GREY}), ("relative to (b)", {"fill": BLUE, "weight": 600}), (",", {"fill": GREY})], size=20)
    s.rich(1090, 560, [("above the ", {"fill": GREY}), ("spiking noise", {"fill": RED, "weight": 600}), (", per direction", {"fill": GREY})], size=20)
    s.save(os.path.join(HERE, "option1f-construction.svg"), "Option 1f: the construction, as sheets of neurons")


if __name__ == "__main__":
    option1f()
    print("wrote option1f-construction.svg")
