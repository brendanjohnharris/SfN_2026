"""Option 1f: the construction, drawn in the house style of the Cosyne 2025, OHBM 2025 and
MiB 2026 posters: oblique plates with a visible edge (the MiB "population bath"), neurons as small
flattened cell glyphs, soft glows for activity, thin semantic-coloured arrows with small heads,
real-looking stimuli and traces, bold panel letters and almost no prose inside the figure.

(a) A line of grating directions feeds a sheet of neurons; each grating drives its own small
    subnetwork (coloured by direction, blended where a cell answers several) and the shared input
    keeps driving the background group (gray), which overlaps them. Co-active cells are linked.
(b) The gray screen: one shared signal fans out to one group of cells (one signal, many copies).
(?) Which links did the grating add?  (c) The stimulus-engaged set.

Run from this folder:  python3 make_1f.py
Writes option1f-construction.svg (the wide draft, 1460 x 780) and the poster figure
../../figures/src/construction_poster.svg (vertical, 900 x 1050 poster units, linked from
SfN_2026.svg as `s1-construction`).
"""

import math
import os

import numpy as np

from svgkit import SVG, BLACK, BLUE, RED, GREEN, GREY, GREY_LIGHT, DARK, WHITE, DIRS, smooth_noise

HERE = os.path.dirname(os.path.abspath(__file__))
POSTER_FIG = os.path.normpath(os.path.join(HERE, "..", "..", "figures", "src", "construction_poster.svg"))

INK = "#282c34"          # outlines: Fathom chernoe, as in the Makie figures
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
    s.add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" style="fill:url(#g{uid});stroke:none"/>')


def cell(s, x, y, fill=CELL, rx=8.5, ry=6.4, sw=1.2):
    """A cell body lying on the sheet: a foreshortened ellipse with an ink outline."""
    s.add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" style="fill:{fill};stroke:{INK};stroke-width:{sw}"/>')


def blend(colors):
    """The mean of some hex colours: a cell in several subnetworks wears all of them."""
    rgb = [[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in colors]
    return "#%02x%02x%02x" % tuple(round(sum(ch) / len(rgb)) for ch in zip(*rgb))


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


def grating(s, cx, cy, size, deg, uid, drift=True, sw=1.6):
    """A drifting-grating patch: a rounded square filled with a sinusoid-like stripe gradient."""
    period = size / 3.2
    s.defs.append(
        f'<linearGradient id="gr{uid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{period:.2f}" y2="0" '
        f'spreadMethod="repeat" gradientTransform="rotate({deg} {cx:.1f} {cy:.1f})">'
        f'<stop offset="0" stop-color="#2a2a2a"/><stop offset="0.5" stop-color="#e9e9e9"/>'
        f'<stop offset="1" stop-color="#2a2a2a"/></linearGradient>')
    h = size / 2
    s.add(f'<rect x="{cx - h:.1f}" y="{cy - h:.1f}" width="{size}" height="{size}" rx="{size * 0.12:.1f}" '
          f'style="fill:url(#gr{uid});stroke:{INK};stroke-width:{sw}"/>')
    if drift:   # a small white arrow for the drift direction (perpendicular to the stripes)
        a = math.radians(deg)
        ex, ey = math.cos(a) * size * 0.28, math.sin(a) * size * 0.28
        thin_arrow(s, cx - ex, cy - ey, cx + ex, cy + ey, WHITE, sw=2.2 * sw / 1.6, head=7 * sw / 1.6, opacity=0.95)


def trace_box(s, x, y, w, h, sig, color, label, sublabel=None, stroke=INK, size=21, subsize=18, sw=2):
    s.rect(x, y, w, h, fill=WHITE, stroke=stroke, sw=1.4, rx=3)
    n = len(sig)
    pts = [(x + 6 + i / (n - 1) * (w - 12), y + h / 2 - v * (h / 2 - 6)) for i, v in enumerate(sig)]
    s.polyline(pts, stroke=color, sw=sw)
    s.text(x + w / 2, y - 8, label, size=size, weight=700, anchor="middle")
    if sublabel:
        s.text(x + w / 2, y + h + subsize + 4, sublabel, size=subsize, fill=GREY, anchor="middle")


def knn_edges(pts, idx, kn=3, wmul=1.0):
    """Link each active cell to its nearest active neighbours (in sheet coordinates)."""
    edges = set()
    for i in idx:
        d = sorted(((math.dist(pts[i], pts[j]), j) for j in idx if j != i))
        for _, j in d[:kn]:
            edges.add(tuple(sorted((i, j))))
    out = []
    for i, j in edges:
        dist = math.dist(pts[i], pts[j])
        out.append((i, j, (3.2 - 1.6 * min(dist / 140, 1)) * wmul))
    return out


def sheet(s, ox, oy, k, cells, active, color, edges, uid, dim_inactive=False, z=1.0):
    """Plate, links, glows and cell glyphs; z scales glyphs and glows. `color` is one colour or a dict
    per active cell (a link takes the blend of its ends). Returns projected positions."""
    col = color.__getitem__ if isinstance(color, dict) else lambda n: color
    plate(s, ox, oy, k, thickness=7 * z)
    P = [proj(u, v, ox, oy, k) for u, v in cells]
    for i, j, w in edges:
        s.line(P[i][0], P[i][1], P[j][0], P[j][1], stroke=blend([col(i), col(j)]), sw=w, opacity=0.85)
    for n in active:
        glow(s, P[n][0], P[n][1], col(n), f"{uid}{n}", rx=24 * z, ry=18 * z)
    for n, (x, y) in enumerate(P):
        if n in active:
            cell(s, x, y, fill=col(n), rx=8.5 * z, ry=6.4 * z, sw=1.3 * z)
        else:
            cell(s, x, y, fill=CELL if not dim_inactive else "#eceef1", rx=8.5 * z, ry=6.4 * z, sw=1.0 * z)
    return P


def population(rng):
    """A jittered grid of 36 cells on the 380 x 230 sheet, the background group, and one small
    subnetwork per grating direction (overlapping each other and the background group)."""
    cells, index = [], {}
    for j in range(5):
        for i in range(7):
            if (i, j) in ((6, 0), (0, 4), (6, 4)):     # leave a few gaps so it is not a lattice
                continue
            u = 28 + i * 54 + rng.uniform(-9, 9)
            v = 24 + j * 46 + rng.uniform(-8, 8)
            index[(i, j)] = len(cells)
            cells.append((u, v))
    # The groups interleave and share cells, so the lit set in (a) reads as one network.
    spont = [index[c] for c in ((2, 1), (3, 1), (4, 0), (4, 2), (5, 1), (5, 3), (3, 3), (4, 4), (6, 2))]
    subnets = {0: [(2, 4), (3, 3), (2, 2)], 45: [(2, 3), (3, 3), (3, 1)], 90: [(1, 2), (2, 2)], 135: [(1, 1), (3, 1)]}
    subnets = {d: [index[c] for c in cs] for d, cs in subnets.items()}       # (3,3), (2,2), (3,1) answer two directions
    stim = sorted(set().union(*subnets.values()))
    pref = {d: m[0] for d, m in subnets.items()}                             # the arrow's target: bottom grating -> lowest cell
    colors = {n: GREY for n in spont}                                        # background network
    for n in stim:
        colors[n] = blend([DIRS[d] for d, m in subnets.items() if n in m])
    return cells, spont, stim, pref, colors


def option1f():
    """The wide draft (1460 x 780) shown on the comparison page."""
    rng = np.random.default_rng(12)
    s = SVG()
    cells, spont, stim, pref, colors = population(rng)
    k = 0.92
    sig = smooth_noise(90, rng, cutoff=0.1)
    sig = sig / np.abs(sig).max()

    # ---- (a) drifting gratings ----------------------------------------------------------------
    s.rich(30, 60, [("(a)", {"weight": 700}), ("  Drifting gratings", {"weight": 700})], size=34)
    ox, oy = 270, 150
    e_a = knn_edges(cells, sorted(set(stim) | set(spont)), 3)        # one co-active network, links crossing the groups
    P = sheet(s, ox, oy, k, cells, set(stim) | set(spont), colors, e_a, "a")
    line = [(92, 330), (128, 268), (162, 210), (194, 156)]
    sizes = [58, 52, 46, 42]
    s.line(72, 366, 212, 126, stroke=INK, sw=1.4, opacity=0.6)
    s.text(150, 112, "grating direction", size=19, fill=GREY, anchor="middle")
    for (d, (gx, gy), sz) in zip((0, 45, 90, 135), line, sizes):
        grating(s, gx, gy, sz, d, f"a{d}")
        s.text(gx - sz / 2 - 8, gy + 7, f"{d}°", size=19, fill=DIRS[d], weight=600, anchor="end")
        tx, ty = P[pref[d]]
        thin_arrow(s, gx + sz / 2 + 4, gy, tx - 11, ty, DIRS[d], sw=2, head=9, bend=-14, opacity=0.9)
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
    P2 = sheet(s, ox2, oy2, k, cells, set(spont), GREY, e_b, "b")
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
    sheet(s, 1080, 330, 0.75, cells, set(stim), colors, e_c, "c", dim_inactive=True)
    s.text(1090, 500, "the links in (a) that are not in (b)", size=20, fill=GREY)
    s.rich(1090, 532, [("bPCA: variance in (a) ", {"fill": GREY}), ("relative to (b)", {"fill": BLUE, "weight": 600}), (",", {"fill": GREY})], size=20)
    s.rich(1090, 560, [("above the ", {"fill": GREY}), ("spiking noise", {"fill": RED, "weight": 600}), (", per direction", {"fill": GREY})], size=20)
    s.save(os.path.join(HERE, "option1f-construction.svg"), "Option 1f: the construction, as sheets of neurons")


SLOT_W, SLOT_H = 755, 1450                 # the poster slot; link_construction.py sets it from the text column


def option1f_vertical(out=POSTER_FIG):
    """The poster figure: (a) and (b) stacked, the extracted network below, with only the essential
    annotations (the caption carries the rest). 720 figure units wide and as tall as the slot's aspect
    asks, with the poster's own type sizes (panel labels 42 px bold, small labels 26-29 px). The sheets
    are drawn less oblique than the wide draft to use the height; the panels are spaced evenly, with
    the "?" arrow centred in the gap below (b)."""
    global SQUASH
    squash0, SQUASH = SQUASH, 0.9
    rng = np.random.default_rng(12)
    W = 720
    H = round(W * SLOT_H / SLOT_W)
    s = SVG(W, H)
    cells, spont, stim, pref, colors = population(rng)
    k, z = 1.0, 1.25                      # sheet scale; glyph and stroke zoom
    TITLE, LAB, SMALL = 42, 29, 26
    e_a = knn_edges(cells, sorted(set(stim) | set(spont)), 3, wmul=1.3)
    e_b = knn_edges(cells, spont, 3, wmul=1.3)
    in_b = {(i, j) for i, j, _ in e_b}
    e_c = [e for e in knn_edges(cells, stim, 2, wmul=1.3) if (e[0], e[1]) not in in_b]
    OX = 250                               # every sheet shares this left edge
    CAP, DROP = 30, 40                     # label cap height, label baseline to sheet top
    SH = SQUASH * SHEET_H + 7 * z          # a sheet's drawn height
    r = SQUASH / squash0                   # the grating stack stretches with the sheet
    oy = 120
    stack_bottom = oy + r * (324 - 120)
    GAP = (H - stack_bottom - 2 * (CAP + DROP + SH)) / 2     # equal gaps between panels

    # ---- (a) drifting gratings ----------------------------------------------------------------
    s.rich(0, 42, [("(a)", {"weight": 700}), ("  Drifting gratings", {"weight": 700})], size=TITLE)
    P = sheet(s, OX, oy, k, cells, set(stim) | set(spont), colors, e_a, "a", z=z)
    line = [(96, oy + r * 166), (134, oy + r * 104), (170, oy + r * 44), (204, oy - r * 14)]
    sizes = [66, 60, 54, 48]
    s.line(74, stack_bottom, 224, oy - r * 46, stroke=INK, sw=1.8, opacity=0.6)
    for (d, (gx, gy), sz) in zip((0, 45, 90, 135), line, sizes):
        grating(s, gx, gy, sz, d, f"a{d}", sw=2.0)
        s.text(gx - sz / 2 - 9, gy + 9, f"{d}°", size=SMALL, fill=DIRS[d], weight=600, anchor="end")
        tx, ty = P[pref[d]]
        thin_arrow(s, gx + sz / 2 + 5, gy, tx - 13, ty, DIRS[d], sw=2.5, head=11, bend=-16, opacity=0.9)

    # ---- (b) gray screen ------------------------------------------------------------------------
    lb = stack_bottom + GAP + CAP
    s.rich(0, lb, [("(b)", {"weight": 700}), ("  Gray screen", {"weight": 700})], size=TITLE)
    oy2 = lb + DROP
    sheet(s, OX, oy2, k, cells, set(spont), GREY, e_b, "b", z=z)
    gx, gy, sz = 150, oy2 + SH / 2 - 20, 64
    s.rect(gx - sz / 2, gy - sz / 2, sz, sz, fill="#9d9d9d", stroke=INK, sw=2.0, rx=8)
    s.text(gx, gy + sz / 2 + 38, "Redundant links", size=LAB, fill=BLUE, weight=700, anchor="middle")   # under the screen

    # ---- the question, centred in the gap ---------------------------------------------------------
    sb = oy2 + SH
    mid = sb + GAP / 2
    thin_arrow(s, 470, mid - 34, 470, mid + 34, INK, sw=2.8, head=15)
    s.text(432, mid + 24, "?", size=66, weight=700, anchor="end")

    # ---- (c) stimulus-engaged -----------------------------------------------------------------
    lc = sb + GAP + CAP
    s.rich(0, lc, [("(c)", {"weight": 700}), ("  Stimulus-engaged", {"weight": 700, "fill": GREEN})], size=TITLE)
    sheet(s, OX, lc + DROP, k, cells, set(stim), colors, e_c, "c", dim_inactive=True, z=z)
    s.save(out, "The construction: gratings, gray screen, and what the grating engaged")
    SQUASH = squash0
    print(f"vertical figure {W} x {H}, panel gap {GAP:.0f}")
    return out


if __name__ == "__main__":
    option1f()
    print("wrote option1f-construction.svg")
    print("wrote", option1f_vertical())
