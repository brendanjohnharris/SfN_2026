"""Draft schematics for five ways of opening the SfN 2026 poster (Section 1).

Run from this folder:  python3 make_drafts.py
Writes option1-networks.svg ... option5-ongoing.svg, each 1460 x 780 poster units
(the Section 1 figure slot is 1362 x 779, so a draft drops in at k ~ 0.93).
Render previews with:  node render.js preview 1 option*.svg
"""

import math
import os

import numpy as np

from svgkit import (SVG, BLACK, BLUE, RED, GREEN, GREEN_LIGHT, PURPLE, GREY, GREY_LIGHT, PANEL, DARK,
                    TEAL, ORANGE, WHITE, DIRS, gauss_cloud, smooth_noise, hex_mix)

HERE = os.path.dirname(os.path.abspath(__file__))


def vtext(s, x, y, txt, size=27, fill=GREY):
    """Vertical (rotated) axis label."""
    s.add(f'<text x="{x:.1f}" y="{y:.1f}" transform="rotate(-90 {x:.1f} {y:.1f})" '
          f'style="font-family:\'Source Sans 3\',sans-serif;font-size:{size}px;fill:{fill};text-anchor:middle">{txt}</text>')


def lines(s, x, y, rows, size=26, dy=None, fill=BLACK):
    """Several lines of text; a row may be a string or a list of (text, style) runs."""
    dy = dy or round(size * 1.3)
    for i, row in enumerate(rows):
        if isinstance(row, str):
            s.text(x, y + i * dy, row, size=size, fill=fill)
        else:
            s.rich(x, y + i * dy, row, size=size)


# =============================================================================
# Option 1: two networks on top of each other (Brendan's idea)
# =============================================================================
NODES = [(60, 70), (135, 38), (212, 62), (252, 132), (232, 212), (152, 252), (72, 232), (30, 150),
         (142, 142), (100, 104), (192, 124), (176, 194), (108, 186), (56, 118)]
# (i, j, weight): the spontaneous network has a hub (node 8) and a ring; the stimulus module is
# {2, 3, 10, 11}, two of whose units also sit in the spontaneous ring.
BLUE_EDGES = [(8, 0, 3), (8, 1, 4), (8, 4, 3), (8, 5, 4), (8, 6, 2), (8, 7, 3), (8, 13, 2), (8, 3, 2),
              (0, 1, 2), (5, 6, 3), (6, 7, 2), (7, 0, 2), (4, 5, 2), (1, 2, 2), (3, 4, 2), (1, 9, 2),
              (9, 13, 2), (0, 13, 3), (12, 7, 2), (12, 8, 2)]
GREEN_EDGES = [(2, 3, 7), (2, 10, 6), (3, 10, 7), (10, 11, 6), (3, 11, 5), (2, 11, 4)]
SPONT_SET = {0, 1, 4, 5, 6, 7, 8, 13, 9, 12, 2, 3}
STIM_SET = {2, 3, 10, 11}


def draw_network(s, ox, oy, scale=1.0, edges=(), node_fill=None, node_r=11, halos=False,
                 edge_color=BLACK, edge_alpha=1.0, node_stroke=BLACK):
    """Draw NODES at (ox, oy) with the given edges. node_fill: dict node -> (colour, radius)."""
    P = [(ox + x * scale, oy + y * scale) for x, y in NODES]
    if halos:
        for (x, y) in P:
            for r, a in ((26, 0.12), (19, 0.2), (13, 0.3)):    # concentric discs read as a fuzzy halo
                s.circle(x, y, r * scale, fill=RED, opacity=a)
    for i, j, w in edges:
        s.line(P[i][0], P[i][1], P[j][0], P[j][1], stroke=edge_color, sw=w * 1.25 * scale, opacity=edge_alpha)
    for k, (x, y) in enumerate(P):
        fill, r = WHITE, node_r
        if node_fill and k in node_fill:
            fill, r = node_fill[k]
        s.circle(x, y, r * scale, fill=fill, stroke=node_stroke, sw=3 * scale)
    return P


def option1():
    s = SVG()
    pw, ph = 330, 350
    xs = [10, 380, 750, 1120]
    y0 = 50
    titles = [("a", "Spontaneous", BLUE, "network on the gray screen"),
              ("b", "Stimulus-engaged", GREEN, "network the grating adds"),
              ("c", "Spiking noise", RED, "private to each unit"),
              ("d", "Your recording", BLACK, "all three look alike")]
    for (x, (let, title, col, sub)) in zip(xs, titles):
        s.panel(x, y0, pw, ph)
        s.label(x + 16, y0 + 42, let, title, size=32, color=col)
        s.text(x + 16, y0 + 74, sub, size=24, fill=GREY)
    for x, op in ((360, "+"), (730, "+"), (1100, "=")):
        s.op(x, y0 + 215, op, size=56)
    net_scale = 0.9
    ny = y0 + 92
    draw_network(s, xs[0] + 38, ny, net_scale, BLUE_EDGES, edge_color=BLUE)
    draw_network(s, xs[1] + 38, ny, net_scale, GREEN_EDGES, edge_color=GREEN)
    draw_network(s, xs[2] + 38, ny, net_scale, (), halos=True)
    merged = {}
    for i, j, w in BLUE_EDGES + GREEN_EDGES:
        key = tuple(sorted((i, j)))
        merged[key] = merged.get(key, 0) + w
    rec_edges = [(i, j, w) for (i, j), w in merged.items()]
    draw_network(s, xs[3] + 38, ny, net_scale, rec_edges, halos=True)

    # --- bottom row: what each method returns -------------------------------
    y1 = 440
    s.panel(10, y1, 700, 320)
    s.panel(740, y1, 710, 320)
    s.label(26, y1 + 42, "e", "PCA sees only (d)", size=32)
    s.label(756, y1 + 42, "f", "Baseline PCA also measures (a) and (c)", size=32)
    load_pca = {k: (TEAL, 13 if k in (8, 1, 5, 0, 13) else 10) for k in SPONT_SET}
    draw_network(s, 30, y1 + 68, 0.78, rec_edges, node_fill=load_pca, edge_color=GREY_LIGHT)
    lines(s, 270, y1 + 105, [
        "Ranks directions by total variance,",
        "so its leading component is the",
        [("largest", {"weight": 600}), (" co-fluctuation, which is the", {})],
        [("spontaneous network", {"fill": BLUE, "weight": 600}), (".", {})],
    ], size=25)
    s.xmark(284, y1 + 250, size=20)
    s.text(308, y1 + 258, "Not the stimulus, and blurred by noise.", size=25, fill=GREY)
    load_b = {k: (GREEN, 13) for k in STIM_SET}
    draw_network(s, 760, y1 + 68, 0.78, rec_edges, node_fill=load_b, edge_color=GREY_LIGHT)
    lines(s, 1000, y1 + 105, [
        [("Subtracts the ", {}), ("noise", {"fill": RED, "weight": 600}), (", then measures", {})],
        [("variance relative to the ", {}), ("spontaneous", {"fill": BLUE, "weight": 600})],
        [("network", {"fill": BLUE, "weight": 600}), (", and ranks what the grating", {})],
        [("adds: the ", {}), ("stimulus-engaged network", {"fill": GREEN, "weight": 600}), (".", {})],
    ], size=25)
    s.tick(1012, y1 + 250, size=22)
    s.text(1040, y1 + 258, "The stimulus, above the noise.", size=25, fill=GREY)
    s.save(os.path.join(HERE, "option1-networks.svg"), "Option 1: two networks on top of each other")


# =============================================================================
# Option 2: two neurons in state space
# =============================================================================
def cov_ellipse(xs, ys, nsd=2.0):
    """Centre, semi-axes and angle (deg) of the nsd-sigma covariance ellipse of a point cloud."""
    C = np.cov(np.vstack([xs, ys]))
    vals, vecs = np.linalg.eigh(C)
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    ang = math.degrees(math.atan2(vecs[1, 0], vecs[0, 0]))
    return float(np.mean(xs)), float(np.mean(ys)), nsd * math.sqrt(vals[0]), nsd * math.sqrt(vals[1]), ang


def option2():
    rng = np.random.default_rng(7)
    s = SVG()
    pw, ph = 440, 680
    xs = [40, 510, 980]
    y0 = 40
    heads = [("a", "Gray screen", BLUE), ("b", "Drifting gratings", BLACK), ("c", "Compare the two", GREEN)]
    for x, (let, t, col) in zip(xs, heads):
        s.panel(x, y0, pw, ph)
        s.label(x + 16, y0 + 44, let, t, size=36, color=col)
    box = 310
    frames = [(x + 80, y0 + 76) for x in xs]
    for (fx, fy) in frames:
        s.rect(fx, fy, box, box, fill=WHITE, stroke=GREY_LIGHT, sw=2)
        s.text(fx + box / 2, fy + box + 34, "Neuron 1 rate", size=26, fill=GREY, anchor="middle")
        vtext(s, fx - 20, fy + box / 2, "Neuron 2 rate", size=26)
    sx, sy = 66, 22          # spontaneous spread along / across the diagonal (SVG px)
    offs = {0: -51, 45: -17, 90: 17, 135: 51}   # class offsets along the anti-diagonal

    def centre(k):
        fx, fy = frames[k]
        return fx + box / 2, fy + box / 2

    # (a) spontaneous cloud + its covariance ellipse
    cx, cy = centre(0)
    px, py = gauss_cloud(140, cx, cy, sx, sy, -45, rng)
    for x, y in zip(px, py):
        s.circle(x, y, 4.5, fill=BLUE, opacity=0.75)
    e = cov_ellipse(px, py)
    s.ellipse(*e, stroke=BLUE, sw=4)
    ty = y0 + 450
    lines(s, xs[0] + 28, ty, [
        "No stimulus, yet the neurons",
        "rise and fall together: shared",
        "inputs, arousal, running.",
        "",
        [("This is the ", {}), ("redundancy baseline", {"fill": BLUE, "weight": 600}), (",", {})],
        "the spontaneous covariance.",
    ], size=26)
    # (b) gratings: the same diagonal spread, offset by direction
    cx, cy = centre(1)
    a = math.radians(45)
    means, allx, ally = {}, [], []
    for d, off in offs.items():
        mx, my = cx + off * math.cos(a), cy + off * math.sin(a)
        means[d] = (mx, my)
        px, py = gauss_cloud(34, mx, my, sx, sy, -45, rng)
        allx += list(px); ally += list(py)
        for x, y in zip(px, py):
            s.circle(x, y, 4.5, fill=DIRS[d], opacity=0.75)
    et = cov_ellipse(np.array(allx), np.array(ally))
    s.ellipse(*et, stroke=BLACK, sw=4)
    for d, (mx, my) in means.items():
        s.cross(mx, my, r=11, stroke=DIRS[d], sw=6)
        s.circle(mx, my, 7, fill=WHITE, stroke=DIRS[d], sw=4)
    L = 140
    s.darrow(cx, cy, L * math.cos(-a), L * math.sin(-a), stroke=TEAL, sw=6, head=22)
    s.text(cx + 92, cy - 112, "PC1", size=30, fill=TEAL, weight=700)
    lx = xs[1] + 28
    s.text(lx, ty, "Grating direction", size=26)
    for i, d in enumerate((0, 45, 90, 135)):
        s.circle(lx + 205 + i * 52, ty - 9, 8, fill=DIRS[d])
        s.text(lx + 205 + i * 52 + 12, ty, f"{d}°", size=23, fill=DIRS[d], weight=600)
    lines(s, lx, ty + 40, [
        [("PCA takes the ", {}), ("largest", {"weight": 600}), (" axis, which", {})],
        "is the shared gain. Along it the",
        "four directions overlap:",
        "decoding error 31°.",
    ], size=26)
    # (c) overlay: blue ellipse vs black ellipse; bPC1 along the anti-diagonal
    cx, cy = centre(2)
    e_sp = (cx, cy, e[2], e[3], e[4])
    e_te = (cx, cy, et[2], et[3], et[4])
    s.ellipse(*e_sp, stroke=BLUE, sw=4, fill=BLUE, opacity=0.18)
    s.ellipse(*e_sp, stroke=BLUE, sw=4)
    s.ellipse(*e_te, stroke=BLACK, sw=4)
    s.circle(cx, cy, 17, fill=RED, opacity=0.35)
    s.circle(cx, cy, 17, fill="none", stroke=RED, sw=3)
    for d, off in offs.items():
        s.cross(cx + off * math.cos(a), cy + off * math.sin(a), r=9, stroke=DIRS[d], sw=5)
    s.darrow(cx, cy, 112 * math.cos(a), 112 * math.sin(a), stroke=GREEN, sw=6, head=22)
    s.text(cx + 66, cy + 140, "bPC1", size=30, fill=GREEN, weight=700)
    s.darrow(cx, cy, 140 * math.cos(-a), 140 * math.sin(-a), stroke=TEAL, sw=4, head=18, opacity=0.5)
    s.text(cx + 92, cy - 112, "PC1", size=26, fill=TEAL, weight=700, opacity=0.6)
    s.text(cx - 140, cy + 120, "noise", size=24, fill=RED, weight=600)
    s.line(cx - 92, cy + 108, cx - 16, cy + 14, stroke=RED, sw=2)
    lines(s, xs[2] + 28, ty, [
        "bPCA takes the axis where the",
        [("gratings add variance ", {}), ("beyond", {"fill": BLUE, "weight": 600})],
        [("the gray screen", {"fill": BLUE, "weight": 600}), (", above the ", {}), ("spiking", {"fill": RED, "weight": 600})],
        [("noise", {"fill": RED, "weight": 600}), (". Along it the directions", {})],
        "separate: decoding error 9°.",
    ], size=26)
    s.save(os.path.join(HERE, "option2-stateSpace.svg"), "Option 2: two neurons in state space")


# =============================================================================
# Option 3: dF/F for covariance
# =============================================================================
CELLS = [(40, 50, 17), (95, 30, 14), (150, 62, 19), (200, 36, 13), (62, 118, 15), (128, 122, 18),
         (190, 112, 14), (36, 180, 13), (98, 190, 17), (165, 176, 16), (205, 200, 12), (120, 70, 11)]
RESPONDING = {2, 5, 9}


def frame_tile(s, x, y, size, mode, rng):
    """A cartoon two-photon field of view. mode: 'F', 'F0', 'dark', 'dff'."""
    k = size / 240.0
    s.rect(x, y, size, size, fill="#141414", rx=10)
    if mode != "dark":
        for i, (cx, cy, r) in enumerate(CELLS):
            hot = i in RESPONDING and mode in ("F", "dff")
            if mode == "dff" and not hot:
                continue
            col = "#c9e6b0" if hot else "#8a8a8a"
            base = 0.95 if hot else 0.55
            cx, cy, r = x + cx * k, y + cy * k, r * k
            s.circle(cx, cy, r + 6 * k, fill=col, opacity=base * 0.25)
            s.circle(cx, cy, r, fill=col, opacity=base)
            s.circle(cx - r * 0.2, cy - r * 0.2, r * 0.45, fill="#141414", opacity=0.55)  # nucleus
    if mode in ("F", "F0", "dark"):
        n = 260 if mode == "dark" else 120
        for _ in range(n):
            px, py = rng.uniform(4, size - 4, 2)
            s.circle(x + px, y + py, rng.uniform(1.2, 2.4), fill="#ffffff", opacity=rng.uniform(0.15, 0.5))


def cov_tile(s, x, y, size, mat, vmax=1.0):
    n = mat.shape[0]
    c = size / n
    for i in range(n):
        for j in range(n):
            v = max(0.0, min(1.0, mat[i, j] / vmax))
            s.rect(x + j * c, y + i * c, c + 0.5, c + 0.5, fill=hex_mix(WHITE, BLUE, v ** 0.8))
    s.rect(x, y, size, size, fill="none", stroke=GREY_LIGHT, sw=2)


def option3():
    rng = np.random.default_rng(11)
    s = SVG()
    T = 200
    xs = [70, 370, 670, 1120]
    # ---- row 1: imaging ------------------------------------------------------
    s.text(70, 46, "Imaging already corrects fluorescence this way", size=33, weight=600)
    ry = 64
    modes = ["F", "F0", "dark", "dff"]
    labels = [("F", "stimulus frame", BLACK), ("F₀", "baseline frame", BLUE), ("dark frame", "shutter closed", RED),
              ("ΔF / F", "only the responding cells", GREEN)]
    for x, m, (t, sub, col) in zip(xs, modes, labels):
        frame_tile(s, x, ry, T, m, rng)
        s.text(x + T / 2, ry + T + 36, t, size=30, weight=700, fill=col, anchor="middle")
        s.text(x + T / 2, ry + T + 66, sub, size=24, fill=GREY, anchor="middle")
    s.op(xs[3] - 85, ry + T / 2 + 18, "→", size=60)
    s.rich(xs[3] + T / 2, ry + T + 106,
           [("ΔF/F = (F − ", {}), ("F₀", {"fill": BLUE, "weight": 600}), (") / (", {}),
            ("F₀", {"fill": BLUE, "weight": 600}), (" − ", {}), ("dark", {"fill": RED, "weight": 600}), (")", {})],
           size=27, anchor="middle")
    # ---- row 2: covariance ---------------------------------------------------
    s.text(70, 424, "Baseline PCA does the same to covariance, direction by direction", size=33, weight=600)
    ry = 442
    n = 10
    base = 0.04 + 0.05 * rng.random((n, n)); base = (base + base.T) / 2
    shared = np.zeros((n, n)); shared[:7, :7] = 0.42
    tuned = np.zeros((n, n)); tuned[3:6, 3:6] = 0.55
    noise = np.eye(n) * 0.35
    rate = np.eye(n) * 0.25
    sig_g = base + shared + tuned + noise + rate
    sig_r = base + shared + noise + rate
    sig_n = noise
    labels = [("Σ²", "during the gratings", BLACK), ("Σ²ᵣ", "on the gray screen", BLUE), ("Σ²ₙ", "spiking noise", RED)]
    for x, M, (t, sub, col) in zip(xs[:3], (sig_g, sig_r, sig_n), labels):
        cov_tile(s, x, ry, T, M, vmax=1.3)
        s.text(x + T / 2, ry + T + 36, t, size=30, weight=700, fill=col, anchor="middle")
        s.text(x + T / 2, ry + T + 66, sub, size=24, fill=GREY, anchor="middle")
    s.op(xs[3] - 85, ry + T / 2 + 18, "→", size=60)
    x = xs[3]
    s.rect(x, ry, T, T, fill=WHITE, stroke=GREY_LIGHT, sw=2)
    vals = [2.6, 0.5, 0.05, -0.05, 0.08, -0.02, 0.04, -0.06]
    zero_y = ry + T - 36
    scale = 50
    s.line(x + 10, zero_y, x + T - 10, zero_y, stroke=GREY, sw=2, dash="6,6")
    bw = (T - 30) / len(vals)
    for k, v in enumerate(vals):
        bx = x + 15 + k * bw + 4
        h = v * scale
        col = GREEN if v > 0.3 else GREY_LIGHT
        s.rect(bx, zero_y - max(h, 0), bw - 8, abs(h), fill=col)
    s.text(x + T / 2, ry + T - 8, "component", size=21, fill=GREY, anchor="middle")
    vtext(s, x - 12, ry + T / 2 - 18, "λ − 1", size=21)
    s.text(x + T / 2, ry + T + 36, "bPCA: λ − 1", size=30, weight=700, fill=GREEN, anchor="middle")
    s.text(x + T / 2, ry + T + 66, "only the stimulus-engaged directions", size=24, fill=GREY, anchor="middle")
    s.rich(xs[3] + T / 2, ry + T + 106,
           [("λ − 1 = (Σ² − ", {}), ("Σ²ᵣ", {"fill": BLUE, "weight": 600}), (") / (", {}),
            ("Σ²ᵣ", {"fill": BLUE, "weight": 600}), (" − ", {}), ("Σ²ₙ", {"fill": RED, "weight": 600}), (")", {})],
           size=27, anchor="middle")
    s.save(os.path.join(HERE, "option3-dFF.svg"), "Option 3: dF/F for covariance")


# =============================================================================
# Option 4: give PCA a control condition
# =============================================================================
def mini_matrix(s, x, y, w, h, rows, cols, rng, kind):
    """Trials x units rate matrix drawn as a small heat map."""
    cw, ch = w / cols, h / rows
    shared = rng.normal(size=rows)[:, None] * rng.uniform(0.4, 1.0, size=cols)[None, :]
    if kind == "test":
        tun = np.zeros((rows, cols))
        for r in range(rows):
            tun[r, :] = np.sin(np.linspace(0, 2 * math.pi, cols) + (r % 4) * math.pi / 2) * 0.9
        M = shared + tun + 0.35 * rng.normal(size=(rows, cols))
    elif kind == "spont":
        M = shared + 0.35 * rng.normal(size=(rows, cols))
    else:
        M = 0.9 * rng.normal(size=(rows, cols))
    M = (M - M.min()) / (M.max() - M.min())
    for r in range(rows):
        for c in range(cols):
            s.rect(x + c * cw, y + r * ch, cw + 0.4, ch + 0.4, fill=hex_mix(WHITE, DARK, M[r, c]))
    s.rect(x, y, w, h, fill="none", stroke=GREY_LIGHT, sw=2)


def option4():
    rng = np.random.default_rng(5)
    s = SVG()
    tx0, tx1, ty, th = 80, 1380, 100, 56
    s.text(80, 62, "One Neuropixels session", size=36, weight=600)
    s.text(1380, 62, "time →", size=28, fill=GREY, anchor="end")
    gx1 = 760
    s.rect(tx0, ty, gx1 - tx0, th, fill=WHITE, stroke=BLACK, sw=3)
    nstripe = 40
    sw_ = (gx1 - tx0 - 6) / nstripe
    for k in range(nstripe):
        d = (0, 45, 90, 135)[rng.integers(0, 4)]
        s.rect(tx0 + 3 + k * sw_, ty + 3, sw_ - 2, th - 6, fill=DIRS[d], extra='opacity="0.85"')
    s.rect(gx1 + 40, ty, tx1 - gx1 - 40, th, fill="#b4b4b4", stroke=BLACK, sw=3)
    s.text((tx0 + gx1) / 2, ty + th + 36, "drifting gratings, 4 directions × 75 trials", size=27, anchor="middle")
    s.text((gx1 + 40 + tx1) / 2, ty + th + 36, "gray screen (spontaneous activity)", size=27, anchor="middle")
    # cards
    cy0, ch_ = 290, 300
    cards = [(80, 400, "Test data", BLACK, ["Trial-mean firing rates", "during the gratings"], "test"),
             (530, 400, "Control 1: redundancy baseline", BLUE,
              ["The same units on the gray screen,", "cut into trial-length windows"], "spont"),
             (980, 400, "Control 2: noise baseline", RED,
              ["Spike-count noise of each unit,", "from 10-ms differences"], "noise")]
    for (cx, cw, title, col, lns, kind) in cards:
        s.panel(cx, cy0, cw, ch_)
        s.rect(cx, cy0, cw, 54, fill=col, rx=18)
        s.rect(cx, cy0 + 30, cw, 24, fill=col)
        s.text(cx + 18, cy0 + 38, title, size=27, weight=600, fill=WHITE)
        for i, ln in enumerate(lns):
            s.text(cx + 18, cy0 + 96 + i * 32, ln, size=25)
        mini_matrix(s, cx + 18, cy0 + 150, cw - 36, 120, 12, 30, rng, kind)
        s.text(cx + 18, cy0 + 292, "trials ↓   units →", size=21, fill=GREY)
    s.arrow(420, ty + th + 50, 280, cy0 - 8, stroke=BLACK, sw=4)
    s.arrow(1040, ty + th + 50, 730, cy0 - 8, stroke=BLUE, sw=4)
    s.arrow(1120, ty + th + 50, 1180, cy0 - 8, stroke=RED, sw=4)
    s.text(1205, 240, "10-ms bins", size=23, fill=RED)
    # bottom: how each method reads the data
    by = 630
    s.rect(80, by, 610, 120, fill=PANEL, rx=18)
    s.rect(730, by, 650, 120, fill=PANEL, rx=18)
    s.rich(100, by + 48, [("PCA", {"weight": 700}), (": the test data only.", {})], size=29)
    s.text(100, by + 90, "Every direction of variance counts as structure.", size=26)
    s.rich(750, by + 48, [("Baseline PCA", {"weight": 700, "fill": GREEN}), (": test relative to both controls.", {})], size=29)
    s.rich(750, by + 90, [("λ = variance above ", {}), ("noise", {"fill": RED, "weight": 600}),
                          (", in units of the ", {}), ("gray screen", {"fill": BLUE, "weight": 600}), (".", {})], size=26)
    s.save(os.path.join(HERE, "option4-control.svg"), "Option 4: give PCA a control condition")


# =============================================================================
# Option 5: evoked responses ride on ongoing activity
# =============================================================================
def option5():
    rng = np.random.default_rng(21)
    s = SVG()
    # panel (a): six neurons, one trial
    s.panel(30, 40, 630, 720)
    s.label(46, 82, "a", "Six neurons, one trial", size=36)
    n = 300
    t = np.linspace(-0.5, 2.0, n)
    S = smooth_noise(n, rng, cutoff=0.05)
    E = np.where(t > 0, (1 - np.exp(-t / 0.08)) * np.exp(-t / 1.1), 0.0) * 1.6
    w = [1.0, 0.8, 1.25, 0.9, 1.1, 0.7]
    a = [1.0, 0.0, 1.2, -0.35, 0.7, 0.25]
    x0, x1 = 150, 630
    xt = lambda tt: x0 + (tt + 0.5) / 2.5 * (x1 - x0)
    on = xt(0)
    s.rect(on, 126, x1 - on, 510, fill="#dfe3e6")
    s.text(on + 8, 116, "grating on", size=24, fill=GREY)
    amp = 24
    for i in range(6):
        yc = 200 + i * 86
        trace = w[i] * S + a[i] * E + 0.22 * rng.normal(size=n)
        pts = [(xt(tt), yc - v * amp) for tt, v in zip(t, trace)]
        s.polyline(pts, stroke=BLACK, sw=3)
        s.text(x0 - 12, yc + 9, f"neuron {i + 1}", size=24, fill=GREY, anchor="end")
    s.line(x0, 655, x1, 655, stroke=GREY, sw=2)
    for tt in (0, 1, 2):
        s.line(xt(tt), 655, xt(tt), 665, stroke=GREY, sw=2)
        s.text(xt(tt), 694, f"{tt} s", size=24, fill=GREY, anchor="middle")
    s.text(x0, 736, "Recorded: the three parts summed.", size=25)
    # panel (b): the three parts
    s.panel(690, 40, 360, 720)
    s.label(706, 82, "b", "What it is made of", size=36)
    bx0, bx1 = 724, 1030
    bxt = lambda tt: bx0 + (tt + 0.5) / 2.5 * (bx1 - bx0)
    rows = [(225, BLUE, "Ongoing, shared by all", "most of the variance"),
            (430, GREEN, "Evoked, stimulus-locked", "a small part"),
            (625, RED, "Spiking noise, private", "the rest")]
    for (yc, col, lab, sub) in rows:
        s.text(bx0, yc - 92, lab, size=26, weight=600, fill=col)
        s.text(bx0, yc - 64, sub, size=23, fill=GREY)
    yc = rows[0][0]
    for i in range(6):
        pts = [(bxt(tt), yc - w[i] * v * amp * 0.7) for tt, v in zip(t, S)]
        s.polyline(pts, stroke=BLUE, sw=2.5, opacity=0.35 if i else 1.0)
    yc = rows[1][0]
    for i in range(6):
        pts = [(bxt(tt), yc + 16 - a[i] * v * amp * 0.7) for tt, v in zip(t, E)]
        s.polyline(pts, stroke=GREEN, sw=2.5, opacity=0.5 if a[i] < 1 else 1.0)
    yc = rows[2][0]
    pts = [(bxt(tt), yc - v * amp * 0.45) for tt, v in zip(t, 0.6 * rng.normal(size=n))]
    s.polyline(pts, stroke=RED, sw=2)
    for yy in (318, 516):
        s.op(bx0 - 10, yy, "+", size=46)
    # panel (c): leading components
    s.panel(1080, 40, 350, 720)
    s.label(1096, 82, "c", "Leading component", size=32)
    cx0, cx1 = 1110, 1400
    cxt = lambda tt: cx0 + (tt + 0.5) / 2.5 * (cx1 - cx0)
    s.text(cx0, 150, "PCA", size=30, weight=700, fill=TEAL)
    pts = [(cxt(tt), 230 - v * amp * 0.8) for tt, v in zip(t, S)]
    s.polyline(pts, stroke=TEAL, sw=3)
    s.xmark(cx0 + 8, 310, size=20)
    s.text(cx0 + 30, 318, "the ongoing activity", size=24)
    s.text(cx0, 420, "Baseline PCA", size=30, weight=700, fill=GREEN)
    pts = [(cxt(tt), 500 - v * amp * 0.8) for tt, v in zip(t, E)]
    s.polyline(pts, stroke=GREEN, sw=3)
    s.tick(cx0 + 10, 585, size=22)
    s.text(cx0 + 34, 593, "the evoked response", size=24)
    lines(s, cx0, 660, ["bPCA measures the ongoing", "activity on the gray screen,", "and the noise from the spikes."],
          size=22, fill=GREY)
    s.save(os.path.join(HERE, "option5-ongoing.svg"), "Option 5: evoked responses ride on ongoing activity")


if __name__ == "__main__":
    option1(); option2(); option3(); option4(); option5()
    print("wrote drafts to", HERE)
