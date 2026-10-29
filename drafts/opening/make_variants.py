"""Variants of Option 1 that make the edges explicit: an edge is a pair of units whose
firing is correlated.  All four are built from one simulated population of 14 units.

Run from this folder:  python3 make_variants.py
Writes option1b-zoom.svg, option1c-raster.svg, option1d-flipbook.svg, option1e-arcs.svg.
"""

import math
import os

import numpy as np

from svgkit import (SVG, BLACK, BLUE, RED, GREEN, GREY, GREY_LIGHT, PANEL, DARK, TEAL, WHITE, DIRS,
                    smooth_noise, hex_mix)
from make_drafts import NODES, draw_network, vtext, lines

HERE = os.path.dirname(os.path.abspath(__file__))

# Population: two spontaneous communities sharing a hub, and a stimulus module ------------------
A = [0, 1, 13, 9, 7]            # community A (slow shared fluctuation S_A)
B = [4, 5, 6, 12]               # community B (slow shared fluctuation S_B)
HUB = 8                         # in both
M = [2, 3, 10, 11]              # module driven by the grating; 2 and 3 also weakly in A
PREF = {2: 0, 3: 45, 10: 90, 11: 135}
ORDER = A + [HUB] + B + M       # row order for matrices
N, T = 14, 240                  # units, time bins (50 ms each: 12 s)
STIM = [(20, 50, 0), (70, 100, 45), (120, 150, 90), (170, 200, 135)]   # (start, stop, direction)


def simulate(rng, stim):
    """Poisson spike counts (N x T) and the rates behind them."""
    SA = smooth_noise(T, rng, cutoff=0.08)
    SB = smooth_noise(T, rng, cutoff=0.08)
    SB = SB - SA * np.dot(SA, SB) / np.dot(SA, SA)      # the two communities fluctuate independently
    SB = (SB - SB.mean()) / SB.std()
    wA = np.zeros(N); wA[A] = 1.0; wA[HUB] = 0.8; wA[2] = 0.45; wA[3] = 0.45
    wB = np.zeros(N); wB[B] = 1.0; wB[HUB] = 0.8
    base = np.full(N, 0.22); base[M] = 0.08
    drive = np.zeros((N, T))
    if stim:
        for (t0, t1, d) in STIM:
            for i in M:
                tun = 1.5 + 1.2 * (1 + math.cos(math.radians(2 * (d - PREF[i])))) / 2
                onset = 1 - np.exp(-(np.arange(t1 - t0)) / 3.0)
                drive[i, t0:t1] = tun * onset
    lograte = 1.15 * (wA[:, None] * SA[None, :] + wB[:, None] * SB[None, :]) + drive
    rate = base[:, None] * np.exp(lograte)
    counts = rng.poisson(rate)
    return dict(counts=counts, rate=rate, SA=SA, SB=SB)


def windowed(counts, win=3):
    k = T // win
    return counts[:, :k * win].reshape(N, k, win).sum(axis=2)


def corr(counts, win=3):
    X = windowed(counts, win).astype(float)
    return np.corrcoef(X)


def edges_from_corr(C, thr, nodes=None):
    out = []
    for i in range(N):
        for j in range(i + 1, N):
            if nodes is not None and (i not in nodes or j not in nodes):
                continue
            if C[i, j] > thr:
                out.append((i, j, 1.5 + 4.5 * (C[i, j] - thr) / (1 - thr)))
    return out


THR = 0.35   # correlation threshold for drawing an edge


# Drawing helpers ------------------------------------------------------------------------------
def draw_raster(s, x, y, w, h, counts, rng, order=ORDER, stim=None, label_units=True, colors=None):
    rows = len(order)
    rh = h / rows
    px = w / T
    s.rect(x, y, w, h, fill=WHITE, stroke=GREY_LIGHT, sw=2)
    if stim:
        for (t0, t1, d) in stim:
            s.rect(x + t0 * px, y - 14, (t1 - t0) * px, 9, fill=DIRS[d], rx=2)
    for r, u in enumerate(order):
        yc = y + r * rh
        col = (colors or {}).get(u, BLACK)
        for t in range(T):
            c = counts[u, t]
            for k in range(min(c, 3)):
                xx = x + (t + (k + 0.5) / max(c, 1)) * px
                s.line(xx, yc + 2, xx, yc + rh - 2, stroke=col, sw=1.6, cap="butt")
        if label_units:
            s.text(x - 8, yc + rh * 0.72, f"{r + 1}", size=15, fill=GREY, anchor="end")
    return rh


def draw_matrix(s, x, y, size, C, order=ORDER, vmax=1.0, groups=True):
    n = len(order)
    c = size / n
    for i, u in enumerate(order):
        for j, v in enumerate(order):
            val = C[u, v]
            t = max(0.0, min(1.0, val / vmax))
            s.rect(x + j * c, y + i * c, c + 0.4, c + 0.4, fill=hex_mix(WHITE, BLUE, t ** 0.8))
    s.rect(x, y, size, size, fill="none", stroke=GREY_LIGHT, sw=2)


def index_of(u):
    return ORDER.index(u)


# =============================================================================
# 1b: the network, with one blue and one green edge exploded into the pair's data
# =============================================================================
def option1b(gray, grat, rng):
    s = SVG()
    s.panel(30, 40, 580, 720)
    s.label(46, 82, "a", "Units that fire together", size=34)
    s.text(46, 114, "an edge joins two units whose rates rise and fall together", size=23, fill=GREY)
    Cg = corr(gray["counts"])
    Cs = corr(grat["counts"])
    blue = edges_from_corr(Cg, THR)
    green = [(i, j, w) for (i, j, w) in edges_from_corr(Cs - Cg, 0.25, nodes=set(M))]
    sc, ox, oy = 1.55, 100, 150
    P = draw_network(s, ox, oy, sc, blue, edge_color=BLUE, node_r=12)
    for i, j, w in green:
        s.line(P[i][0], P[i][1], P[j][0], P[j][1], stroke=GREEN, sw=w * 1.25 * sc)
    for k, (x, y) in enumerate(P):      # redraw nodes above the green edges
        s.circle(x, y, 12 * sc * 0.75, fill=WHITE, stroke=BLACK, sw=3)
    # magnifiers on one blue edge (0-1) and one green edge (10-11)
    bm = ((P[0][0] + P[1][0]) / 2, (P[0][1] + P[1][1]) / 2)
    gm = ((P[10][0] + P[11][0]) / 2, (P[10][1] + P[11][1]) / 2)
    s.circle(*bm, 30, fill="none", stroke=BLUE, sw=5)
    s.circle(*gm, 30, fill="none", stroke=GREEN, sw=5)
    s.line(bm[0] + 30, bm[1], 640, 120, stroke=BLUE, sw=3, dash="8,8")
    s.line(gm[0] + 30, gm[1], 640, 500, stroke=GREEN, sw=3, dash="8,8")
    lines(s, 46, 620, [
        [("Blue", {"fill": BLUE, "weight": 600}), (": correlated with nothing on the screen.", {})],
        [("Green", {"fill": GREEN, "weight": 600}), (": correlation the grating adds.", {})],
        "The recording shows all edges in black.",
        [("PCA keeps the biggest blue cluster; bPCA keeps", {})],
        [("green, after measuring blue and the ", {}), ("noise", {"fill": RED, "weight": 600}), (".", {})],
    ], size=24, dy=28)

    # --- callout (b): the blue pair on the gray screen -------------------------------------
    def callout(y0, letter, title, col, data, u, v, stim, colored):
        s.panel(640, y0, 790, 345)
        s.label(656, y0 + 40, letter, title, size=30, color=col)
        x0, w = 680, 380
        tr_y = [y0 + 120, y0 + 210]
        px = w / T
        if stim:
            for (t0, t1, d) in stim:
                s.rect(x0 + t0 * px, y0 + 66, (t1 - t0) * px, 8, fill=DIRS[d], rx=2)
        for yy, unit, name in zip(tr_y, (u, v), ("unit i", "unit j")):
            r = data["rate"][unit]
            sm = np.convolve(data["counts"][unit], np.ones(7) / 7, mode="same")
            amp = 38 / max(sm.max(), 1e-6)
            pts = [(x0 + t * px, yy + 40 - sm[t] * amp) for t in range(T)]
            s.polyline(pts, stroke=col, sw=2.5)
            s.text(x0 - 8, yy + 30, name, size=20, fill=GREY, anchor="end")
            s.line(x0, yy + 42, x0 + w, yy + 42, stroke=GREY_LIGHT, sw=1.5)
        s.text(x0 + w / 2, y0 + 285, "time (rate in 50-ms bins, smoothed)", size=19, fill=GREY, anchor="middle")
        # scatter of windowed counts
        bx, by, bs = 1120, y0 + 70, 230
        s.rect(bx, by, bs, bs, fill=WHITE, stroke=GREY_LIGHT, sw=2)
        X = windowed(data["counts"], 4)
        xi, xj = X[u], X[v]
        mx = max(xi.max(), xj.max(), 1)
        k = len(xi)
        win_dir = {}
        if stim:
            for widx in range(k):
                t0, t1 = widx * 4, widx * 4 + 4
                for (a0, a1, d) in stim:
                    if t0 >= a0 + 3 and t1 <= a1:
                        win_dir[widx] = d
        for widx in range(k):
            cx = bx + 12 + xi[widx] / mx * (bs - 24) + rng.uniform(-3, 3)
            cy = by + bs - 12 - xj[widx] / mx * (bs - 24) + rng.uniform(-3, 3)
            if colored:
                d = win_dir.get(widx)
                s.circle(cx, cy, 4.2, fill=DIRS[d] if d is not None else GREY_LIGHT, opacity=0.85)
            else:
                s.circle(cx, cy, 4.2, fill=col, opacity=0.75)
        if colored:
            for d in (0, 45, 90, 135):
                idx = [w_ for w_, dd in win_dir.items() if dd == d]
                if idx:
                    s.cross(bx + 12 + xi[idx].mean() / mx * (bs - 24), by + bs - 12 - xj[idx].mean() / mx * (bs - 24),
                            r=9, stroke=DIRS[d], sw=5)
        s.text(bx + bs / 2, by + bs + 28, "rate of unit i", size=19, fill=GREY, anchor="middle")
        vtext(s, bx - 14, by + bs / 2, "rate of unit j", size=19)
        rr = np.corrcoef(xi, xj)[0, 1]
        return rr

    r1 = callout(40, "b", "A blue edge: the pair on the gray screen", BLUE, gray, 0, 1, None, False)
    s.text(1385, 40 + 62, f"r = {r1:.2f}", size=22, fill=BLUE, weight=600, anchor="end")
    r2 = callout(415, "c", "A green edge: the pair during gratings", GREEN, grat, 10, 11, STIM, True)
    s.text(1385, 415 + 62, "colour: grating direction", size=19, fill=GREY, anchor="end")
    s.save(os.path.join(HERE, "option1b-zoom.svg"), "Option 1b: an edge exploded into the pair's data")


# =============================================================================
# 1c: spike raster -> correlation matrix -> network, on the gray screen and during gratings
# =============================================================================
def option1c(gray, grat, rng):
    s = SVG()
    rows = [(40, "a", "Gray screen", gray, None, BLUE, "b", "c"),
            (400, "d", "Drifting gratings", grat, STIM, BLACK, "e", "f")]
    Cg, Cs = corr(gray["counts"]), corr(grat["counts"])
    for (y0, la, title, data, stim, col, lb, lc) in rows:
        s.panel(30, y0, 1120, 340)
        s.label(46, y0 + 40, la, title, size=32, color=col)
        s.text(46, y0 + 70, "spike raster, 14 units", size=22, fill=GREY)
        draw_raster(s, 80, y0 + 100, 440, 210, data["counts"], rng, stim=stim)
        s.text(300, y0 + 334, "time (12 s)", size=20, fill=GREY, anchor="middle")
        vtext(s, 52, y0 + 205, "unit", size=20)
        s.op(560, y0 + 215, "→", size=50)
        C = Cg if data is gray else Cs
        s.label(600, y0 + 40, lb, "Correlation matrix", size=28)
        s.text(600, y0 + 70, "each unit against each unit", size=22, fill=GREY)
        draw_matrix(s, 610, y0 + 100, 210, C)
        s.text(715, y0 + 334, "unit", size=20, fill=GREY, anchor="middle")
        s.op(860, y0 + 215, "→", size=50)
        s.label(895, y0 + 40, lc, "As a network", size=28)
        s.text(895, y0 + 70, f"an edge where r > {THR}", size=22, fill=GREY)
        E = edges_from_corr(C, THR)
        draw_network(s, 905, y0 + 90, 0.86, E, edge_color=col if col != BLACK else BLACK, node_r=10)
    # right column: what the grating adds
    s.panel(1180, 40, 250, 720)
    s.label(1196, 80, "g", "Grating only", size=27, color=GREEN)
    s.text(1196, 108, "edges in (f) but not in (c)", size=20, fill=GREY)
    G = edges_from_corr(Cs - Cg, 0.25, nodes=set(M))
    draw_network(s, 1205, 130, 0.78, G, edge_color=GREEN, node_r=10)
    lines(s, 1196, 400, [
        "A few units that fire",
        "together only when the",
        "grating is on.",
        "",
        [("PCA", {"weight": 600}), (" on (e) finds the big", {})],
        [("block, the ", {}), ("spontaneous", {"fill": BLUE, "weight": 600})],
        "correlations.",
        "",
        [("bPCA", {"weight": 600, "fill": GREEN}), (" measures (b) and", {})],
        [("the ", {}), ("spiking noise", {"fill": RED, "weight": 600}), (", and", {})],
        "finds (g).",
    ], size=22, dy=27)
    s.save(os.path.join(HERE, "option1c-raster.svg"), "Option 1c: raster to correlation matrix to network")


# =============================================================================
# 1d: flipbook: units that light up together get an edge
# =============================================================================
def option1d(grat, rng):
    s = SVG()
    counts = grat["counts"]
    SA, SB = grat["SA"], grat["SB"]
    win = 10
    stim_bins = np.zeros(T, bool)
    for (t0, t1, d) in STIM:
        stim_bins[t0:t1] = True

    def best(sig, exclude, lo=0, hi=T - win):
        cand = [(sig[t:t + win].mean(), t) for t in range(lo, hi) if not stim_bins[t:t + win].any()
                and all(abs(t - e) > 20 for e in exclude)]
        return max(cand)[1]

    f1 = best(SA - SB, [])                 # community A up, B down
    f3 = best(SB - SA, [f1])               # community B up, A down
    f4 = best(SA - SB, [f1, f3])
    f6 = best(SB - SA, [f1, f3, f4])
    f2 = STIM[0][0] + 12
    f5 = STIM[2][0] + 12
    frames = sorted([f1, f2, f3, f4, f5, f6])
    # frames row
    s.text(30, 50, "Six moments of one recording: which units are firing?", size=30, weight=600)
    fw, fy = 205, 70
    fx = [30 + k * 238 for k in range(6)]
    lit_sets = []
    for k, (x, t) in enumerate(zip(fx, frames)):
        s.panel(x, fy, fw, 230)
        dir_here = [d for (t0, t1, d) in STIM if t0 <= t < t1]
        lab = f"t{k + 1}" + ("  grating on" if dir_here else "  gray screen")
        s.text(x + 12, fy + 30, lab, size=21, weight=600, fill=DIRS[dir_here[0]] if dir_here else GREY)
        c = counts[:, t:t + win].sum(axis=1)
        lit = {u for u in range(N) if c[u] >= 4}
        lit_sets.append((lit, bool(dir_here)))
        fill = {u: (GREEN if dir_here else BLUE, 11) for u in lit}
        draw_network(s, x + 12, fy + 44, 0.68, (), node_fill=fill, node_r=9)
    # raster with the frames marked
    rx, ry, rw, rh = 80, 360, 700, 300
    s.text(30, 340, "The whole recording", size=26, weight=600)
    rhh = draw_raster(s, rx, ry, rw, rh, counts, rng, stim=STIM)
    px = rw / T
    for k, (x, t) in enumerate(zip(fx, frames)):
        s.rect(rx + t * px, ry, win * px, rh, fill=GREEN if lit_sets[k][1] else BLUE, extra='opacity="0.18"')
        s.text(rx + (t + win / 2) * px, ry + rh + 24, f"t{k + 1}", size=19, fill=GREY, anchor="middle")
    s.text(rx + rw / 2, ry + rh + 50, "time (12 s)", size=20, fill=GREY, anchor="middle")
    vtext(s, rx - 34, ry + rh / 2, "unit", size=20)
    # accumulated network
    s.panel(820, 330, 610, 430)
    s.text(836, 370, "Units that light up together get an edge", size=27, weight=600)
    Cg_like = np.zeros((N, N))
    for lit, is_stim in lit_sets:
        for i in lit:
            for j in lit:
                if i < j:
                    Cg_like[i, j] += 1
    blue_e, green_e = [], []
    for i in range(N):
        for j in range(i + 1, N):
            n_gray = sum(1 for (lit, st) in lit_sets if not st and i in lit and j in lit)
            n_stim = sum(1 for (lit, st) in lit_sets if st and i in lit and j in lit)
            if n_gray >= 2:
                blue_e.append((i, j, 2 + 2 * n_gray))
            elif n_stim >= 2 and i in M and j in M:
                green_e.append((i, j, 6))
    P = draw_network(s, 845, 395, 1.1, blue_e, edge_color=BLUE, node_r=11)
    for i, j, w in green_e:
        s.line(P[i][0], P[i][1], P[j][0], P[j][1], stroke=GREEN, sw=w * 1.25)
    for (x, y) in P:
        s.circle(x, y, 11 * 1.1 * 0.8, fill=WHITE, stroke=BLACK, sw=3)
    lines(s, 1150, 420, [
        [("Blue", {"fill": BLUE, "weight": 600}), (": together on the", {})],
        "gray screen. PCA's",
        "leading component.",
        "",
        [("Green", {"fill": GREEN, "weight": 600}), (": together only", {})],
        "when the grating is on.",
        "bPCA's leading",
        "component, after it",
        [("measures blue and the ", {})],
        [("spiking noise", {"fill": RED, "weight": 600}), (".", {})],
    ], size=22, dy=27)
    s.save(os.path.join(HERE, "option1d-flipbook.svg"), "Option 1d: units that light up together get an edge")


# =============================================================================
# 1e: arcs over the raster rows: the network drawn on the data
# =============================================================================
def draw_arcs(s, x, ys, edges, color, flip=False):
    """Semicircular arcs joining row centres ys[i], ys[j], bulging left of x."""
    for i, j, w in edges:
        yi, yj = ys[index_of(i)], ys[index_of(j)]
        r = abs(yj - yi) / 2
        sweep = 0 if not flip else 1
        s.path(f"M{x:.1f},{min(yi, yj):.1f} A{r:.1f},{r:.1f} 0 0 {sweep} {x:.1f},{max(yi, yj):.1f}",
               stroke=color, sw=w * 0.9, opacity=0.85)


def option1e(gray, grat, rng):
    s = SVG()
    Cg, Cs = corr(gray["counts"]), corr(grat["counts"])
    panels = [(30, "a", "Gray screen", gray, None, BLUE, edges_from_corr(Cg, THR)),
              (520, "b", "Drifting gratings", grat, STIM, BLACK, edges_from_corr(Cs, THR))]
    rh_all = None
    for (x0, la, title, data, stim, col, E) in panels:
        s.panel(x0, 40, 460, 720)
        s.label(x0 + 16, 82, la, title, size=32, color=col)
        s.text(x0 + 16, 112, "spikes of 14 units, with arcs joining", size=21, fill=GREY)
        s.text(x0 + 16, 138, f"pairs whose rates are correlated (r > {THR})", size=21, fill=GREY)
        rx, ry, rw, rh = x0 + 175, 180, 265, 480
        rhh = draw_raster(s, rx, ry, rw, rh, data["counts"], rng, stim=stim, label_units=False)
        ys = [ry + k * rhh + rhh / 2 for k in range(N)]
        draw_arcs(s, rx - 4, ys, E, col)
        s.text(rx + rw / 2, ry + rh + 28, "time (12 s)", size=20, fill=GREY, anchor="middle")
    # (c): the arcs alone, blue and green
    s.panel(1010, 40, 420, 720)
    s.label(1026, 82, "c", "Edges only", size=32)
    s.text(1026, 112, "the network, with the raster removed", size=21, fill=GREY)
    ry, rh = 180, 480
    rhh = rh / N
    ys = [ry + k * rhh + rhh / 2 for k in range(N)]
    xa = 1200
    s.line(xa, ry, xa, ry + rh, stroke=GREY_LIGHT, sw=2)
    for k in range(N):
        s.circle(xa, ys[k], 7, fill=WHITE, stroke=BLACK, sw=2.5)
    draw_arcs(s, xa - 8, ys, edges_from_corr(Cg, THR), BLUE)
    draw_arcs(s, xa + 8, ys, edges_from_corr(Cs - Cg, 0.25, nodes=set(M)), GREEN, flip=True)
    lines(s, 1250, 230, [
        [("Blue", {"fill": BLUE, "weight": 600}), (": present with", {})],
        "nothing on the screen.",
        "",
        [("Green", {"fill": GREEN, "weight": 600}), (": added by", {})],
        "the grating.",
        "",
        "PCA ranks by total",
        "variance and returns",
        "the blue cluster.",
        "",
        [("bPCA", {"weight": 600, "fill": GREEN}), (" measures blue", {})],
        [("and the ", {}), ("noise", {"fill": RED, "weight": 600}), (", and", {})],
        "returns green.",
    ], size=21, dy=26)
    s.save(os.path.join(HERE, "option1e-arcs.svg"), "Option 1e: arcs over the raster")


if __name__ == "__main__":
    rng = np.random.default_rng(2026)
    gray = simulate(rng, stim=False)
    grat = simulate(rng, stim=True)
    option1b(gray, grat, rng)
    option1c(gray, grat, rng)
    option1d(grat, rng)
    option1e(gray, grat, rng)
    print("wrote variants to", HERE)
