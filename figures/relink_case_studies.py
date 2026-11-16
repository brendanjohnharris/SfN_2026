"""Relink the Section 3 and 4 figures of SfN_2026.svg after the October 2026 case-study changes.

Fig3_case_studies.svg is now 720 x 730 with rows neuropixels / phantom / genomics, the Neuropixels
noise baseline is `spontaneous_noise` (successive differences of 10 ms counts) rather than the
autocovariance nugget, and the phantom noise baseline is a calibration recording rather than a
second reading. This script re-crops Fig3 row 1 for `s3-results` (panels b-d, poster-side clip as
before), places the redrawn Section 4 results and caption, relinks the regenerated `noise_poster.svg` and `phantom_poster.svg`, and rewrites
the affected text, wrapped with the installed Source Sans 3. Idempotent: it matches markup by id.

Section 4's results below the schematic are a poster-specific redraw of Fig3's row 2
(`phantom_results_poster.svg`, from `LAB/_research/phantom_correlated/phfig_results_poster.jl`): the
traces across the top, the spectra over the loadings at the right, and the caption in the empty cell at
the bottom left; the Section 3 noise box is `noise_poster.svg`. Both scripts write a `*_layout.tsv` of
axis boxes, which places the poster's panel letters and the caption. Section 2's crop of Fig1 drops its
eigenspectra panels (i), (j).

Usage, from the repo root:  python3 figures/relink_case_studies.py
"""

import os
import re

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
POSTER = os.path.join(ROOT, "SfN_2026.svg")
FIG3 = "figures/src/Fig3_case_studies.svg"
FIG3_W, FIG3_H = 720, 730
NOISE_FIG, NOISE_W, NOISE_H = "figures/src/noise_poster.svg", 535, 189
NOISE_LAYOUT = "figures/src/noise_poster_layout.tsv"               # axis boxes, figure units (y down)
PHANTOM_FIG, PHANTOM_W, PHANTOM_H = "figures/src/phantom_poster.svg", 660, 239
RESULTS_FIG = "figures/src/phantom_results_poster.svg"
RESULTS_LAYOUT = "figures/src/phantom_results_poster_layout.tsv"
S2_CROP = (50.75, 315.0, 439.5, 321.0)    # Fig1's (f)-(h) panel boxes, tight (the 720 x 665 Fig1 of 2026-10-31); its (i)-(j) eigenspectra are dropped
# Relative to the crop's top-left, in Fig1 units: the poster's (a)-(c) letters (x, baseline) and the covers over
# Fig1's own (f)-(h) letters (x, y, w, h, the panel's tint).
S2_LETTERS = {"a": (13.86, 29.33), "b": (163.16, 29.33), "c": (312.36, 29.33)}
S2_LETTER_SIZE = 15.7
S2_COVERS = [(12.9, 15.95, 16.9, 17.4, "#f8faff"), (162.2, 15.95, 20.2, 17.4, "#fff5f6"), (311.4, 15.95, 21.0, 17.4, "#f4f4f5")]
# Section 2 layout (2026-11-08): the figure and the equation box side by side, equal heights, the "why not
# cPCA" box across the bottom; k is the largest scale that keeps the equation column readable (S2_MIN_W)
# and everything inside the section, and the spare height is split into three equal gaps (intro to row,
# row to box, box to the section's foot).
S2_X0, S2_X1 = 103.0, 1678.0                                      # content edges (the section's white box, less margins)
S2_FOOT = 3742.0                                                  # the section's white box, bottom edge
S2_GAP, S2_VGAP, S2_BAR = 40.0, 20.0, 68.0                       # column gap, min box gap, title bar height
S2_MIN_W = 600.0                                                  # narrowest equation column (about 30 characters)
EQ_K = 4.6                                   # equation scale (poster units per pt): ~46 px glyphs, a notch over the 40 px text
# The equation box: the three bPCA conditions of the manuscript (BaselinePCA.tex, main.tex Methods), each
# under a label naming the panel that draws it. Equations from figures/make_s2_equations.py.
S2_LEAD = [("bPCA finds the family of projections ", ""), ("P", "i"), (" that meet three conditions:", "")]
S2_CONDS = [("r", [("(a) ", "b"), ("Redundancy baseline", "rb"), (" becomes white", "")]),
            ("n", [("(b) ", "b"), ("Noise baseline", "nb"), (" collapses", "")]),
            ("t", [("(c) ", "b"), ("Test data", "b"), (" become diagonal", "")])]
# The box below: the contrastive methods, then bPCA's solution (assets/symbol-s2-eq.svg, from make_s2_equations.py).
S2_WHY = [("Earlier contrastive methods can be thought of as comparing the test data with a single baseline [3, 4]:", "")]
S2_BULLETS = [("sub", "\u2212", [("Subtractive methods", "b"), (" such as cPCA subtract two covariances, but require hyperparameter tuning", "")]),
              ("div", "\u00f7", [("Ratio methods", "b"), (" such as ρPCA divide two covariances, amplifying directions dominated "
                                  "by noise", "")])]
S2_BPCA = [("bPCA subtracts noise covariance, whitens corrected redundancy, then orthogonalizes the test data:", "")]
S2_EIG = [("Eigenvalues are test variance above the noise floor, in units of the redundancy baseline (negative "
           "eigenvalues are dropped: +); PCA, cPCA and ρPCA are thus limiting cases.", "")]
# Texts with no other home in this script (Sections 1, 2, 3, 4, 5), set here so the poster text has one source.
S2_INTRO = [("bPCA compares the test data against two baselines:", "")]
S2_BASES = [("r", "#6ea0f9", [("Redundancy baseline", "b"), (": the system measured with the constraint of interest removed", "")]),
            ("n", "#f93d53", [("Noise baseline", "b"), (": the variance due to the measurement process alone", "")])]
BUL_PITCH = 48.66                         # bullet line pitch, as in Section 3
TEXTS = {
    "text1195": [("Stimuli confine neural population activity to ", ""), ("low-dimensional subspaces", "b"),
                 (", usually inferred with ", ""), ("principal component analysis", "b"), (" (PCA) [1]. But recordings also "
                 "carry ", ""), ("nuisance covariance", "b"), (" that is present even without a stimulus:", "")],
    "text1197": [("Redundancy", "b"), (": neurons co-fluctuate during spontaneous activity [2]", "")],
    "text1204": [("Noise", "b"), (": rates estimated from spike counts in finite trials carry measurement error", "")],
    "text1207": [("Since PCA ranks directions by total variance, its leading components mix stimulus-engaged structure "
                  "with redundancy and noise.", "")],
    "text1258": [("Test data", "b"), (": trial-mean firing rates during gratings", "")],
    "text1260": [("Redundancy baseline", "b"), (": spontaneous activity, partitioned into trial-length windows", "")],
    "text1295": [("Redundancy baseline", "b"), (": phase-randomized (IAAFT) surrogates [7], which preserve autocorrelation "
                  "but scramble the shared latent", "")],
    "text1312": [("Baseline PCA", "b"), (" separates the structure imposed by a constraint of interest from ", ""),
                 ("redundancy", "b"), (" and ", ""), ("noise", "b"),
                 (", using empirical baselines that characterize the measurement process.", "")],
}
REFS = [
    [("Cunningham & Yu, ", ""), ("Dimensionality reduction for large-scale neural recordings", "i"), (", Nature Neuroscience (2014).", "")],
    [("Stringer et al., ", ""), ("Spontaneous behaviors drive multidimensional, brainwide activity", "i"), (", Science (2019).", "")],
    [("Abid et al., ", ""), ("Exploring patterns enriched in a dataset with contrastive principal component analysis", "i"),
     (", Nature Communications (2018).", "")],
    [("Carilli et al., ", ""), ("The Rayleigh quotient and contrastive principal component analysis I", "i"), (", bioRxiv (2025).", "")],
    [("Siegle et al., ", ""), ("Survey of spiking in the mouse visual system reveals functional hierarchy", "i"), (", Nature (2021).", "")],
    [("Shinn, ", ""), ("Phantom oscillations in principal component analysis", "i"), (", PNAS (2023).", "")],
    [("Schreiber & Schmitz, ", ""), ("Surrogate time series", "i"), (", Physica D (2000).", "")],
]
REF_IDS = ["text1339", "text1342", "text1345", "text1348", "text1351", "text1354", "text-ref7"]
REF_COLS = ((3666.0, 3), (4473.5, 4))     # column x and how many refs it holds
REF_Y0, REF_LH, REF_GAP = 3415.44, 29.3 * 1.27, 6.05
TITLES = {"tspan1220": "bPCA corrects for redundancy and noise", "tspan1251": "Other contrastive methods",
          "tspan1316": "Other applications"}   # s2-subtitle, s2-whynot-title, s5-beyond-title
PAD, CAP_SIZE = 26, 36                    # caption box padding and font size (poster convention)
K3 = 2.853261                 # Section 3's scale (poster units per Fig3 unit), unchanged
K4 = 2.36                     # Section 4's scale (the schematic and the redrawn results)
SLOT_S3 = (1885.00, 2475.86, 1575.00, 701.90)   # the Section 3 results slot (the old clip rect)
SLOT_S4 = (3666.00, 1700.00, 1575.00, 960.00)   # the Section 4 region below the schematic (ends 1624), clear of the Summary bar (2717)
LABEL = "font-size:42px;line-height:1.133;font-family:'Source Sans 3';fill:#100f0d;text-anchor:start;font-weight:600"

# Fig3 crops (x y w h, figure units), measured from a 2.5 px/unit render: inside each row's bubble border.
CROP_S3 = (172, 14, 541, 215)             # row 1, (b) PCA, (c) bPCA, (d) decoding
COVER_S3 = (172, 14, 541, 29.3)           # the row's panel titles (axes start at y = 44)
EDGE_S3 = (709, 14, 4, 215)               # the panel's rounded right edge
TINT_S3 = "#f6f9f9"                       # Fig3's panel tint: covers in it make the crop one even panel
TITLE_BASE_S3 = 37.5                      # source title baseline (figure units) for the poster's own labels

# Numbers from the refreshed outputs (LAB/plots/Fig3_case_studies/*.tsv, data/*.jld2, noisefig_poster.jl's log).
PCA_K2, BPCA_K2, CHANCE = 31.5, 8.9, 56.25      # decoding error at k = 2 (mean over 23 sessions) and chance
CALLOUT = [[("PCA", "#f93d53", 31.5, 15.86), ("cPCA", "#ffa829", 24.53, 14.57)],   # k = 2 error, mean ± SD over
           [("ρPCA", "#6ea0f9", 12.82, 9.92), ("bPCA", "#88bd69", 8.9, 7.65)]]      # sessions (curves_allvis); PCA_COLORS
R_TRACE_PCA, R_TRACE_BPCA = 0.06, 0.88          # PC1 against the latent, the representative draw
MC_CPCA, MC_RHOPCA = 0.067, 0.053               # median PC1 |cor| over 100 draws, given Sr (data/phantom_oscillations.jld2 mc_pc1_*)
NSIM = 100
NOISE_FRAC = 23                                  # median noise floor / trial-mean variance, %, example session


def measurer(size):
    """Text width in px at `size`, with Source Sans 3 when installed (else a 0.5 em estimate)."""
    try:
        from PIL import ImageFont
        fonts = {}
        for kind, pat in (("", "SourceSans3-Regular"), ("b", "SourceSans3-Semibold"), ("i", "SourceSans3-RegularIt")):
            paths = [os.path.join(r, f) for d in ("~/.fonts", "~/.local/share/fonts", "/usr/share/fonts")
                     for r, _, fs in os.walk(os.path.expanduser(d), followlinks=True) for f in fs if f == f"{pat}.otf"]
            fonts[kind] = ImageFont.truetype(paths[0], size)
        return lambda txt, kind: fonts[FACE.get(kind, kind)].getlength(txt)
    except Exception:
        print("  (Source Sans 3 not found: widths estimated)")
        return lambda txt, kind: 0.5 * size * len(txt)


RUN_STYLE = {"b": "font-weight:600", "i": "font-style:italic",          # run kinds: "" regular, "b" semibold, "i" italic,
             "rb": "font-weight:600;fill:#6ea0f9", "nb": "font-weight:600;fill:#f93d53"}   # "rb"/"nb" redundancy/noise colours
FACE = {"rb": "b", "nb": "b"}                                            # the face each kind is measured in


def wrap(runs, width, size):
    """Greedy word wrap of styled runs ("" regular, "b" semibold, "i" italic) into lines of tokens."""
    w = measurer(size)
    tokens = [(part, kind) for text, kind in runs for part in re.split(r"([^\S\u00a0]+)", text) if part]   # NBSP binds
    lines, cur, cur_w = [], [], 0.0
    for tok, kind in tokens:
        if "\n" in tok:                                 # forced break: a new subcaption
            while cur and cur[-1][0].isspace():
                cur.pop()
            lines.append(cur); cur, cur_w = [], 0.0
            continue
        tw = w(tok, kind)
        if tok.isspace() and "\u00a0" not in tok:
            cur.append((tok, kind)); cur_w += tw
            continue
        if cur and cur_w + tw > width:
            while cur and cur[-1][0].isspace():
                cur.pop()
            lines.append(cur); cur, cur_w = [], 0.0
        cur.append((tok, kind)); cur_w += tw
    if cur:
        lines.append(cur)
    return lines


def retext(s, tid, runs, max_lines=None):
    """Rewrite text element `tid` with `runs`, rewrapped to its own wrap width (--wrap), font size and position."""
    m = re.search(r'<text x="([\d.]+)" y="([\d.]+)" style="([^"]*)" xml:space="preserve" id="%s">.*?</text>' % tid, s, re.S)
    assert m, f"{tid} not found"
    x, y, style = float(m.group(1)), float(m.group(2)), m.group(3)
    size = float(re.search(r"font-size:([\d.]+)px", style).group(1))
    inl = re.search(r"--wrap:([\d.]+)px", style)
    width = float(inl.group(1)) if inl else 1e9
    lh = float(re.search(r"line-height:([\d.]+)", style).group(1))
    lines = wrap(runs, width, size)
    if max_lines is not None:
        assert len(lines) <= max_lines, f"{tid}: {len(lines)} lines, box holds {max_lines}"
    body = []
    for i, line in enumerate(lines):
        parts = []
        for txt, kind in line:
            txt = txt.replace("&", "&amp;").replace("<", "&lt;")         # XML text
            parts.append(f'<tspan style="{RUN_STYLE[kind]}">{txt}</tspan>' if kind in RUN_STYLE else txt)
        body.append(f'<tspan x="{x:g}" y="{y + i * size * lh:.4f}" id="{tid}-l{i}">{"".join(parts)}</tspan>')
    new = f'<text x="{x:.2f}" y="{y:.2f}" style="{style}" xml:space="preserve" id="{tid}">{"".join(body)}</text>'
    print(f"  {tid}: {len(lines)} line(s)")
    retext.lines = len(lines)
    return s[: m.start()] + new + s[m.end():]


def layout(path):
    """Axis boxes written by a poster figure script: {panel: (x, y, w, h)} in figure units, y down."""
    rows = [l.split("\t") for l in open(os.path.join(ROOT, path)).read().strip().split("\n")[1:]]
    return {r[0]: tuple(float(v) for v in r[1:5]) for r in rows}


def move_text(s, tid, x, y, width):
    """Reposition text element `tid` and set its wrap width (--wrap; not inline-size, which Inkscape reflows) before `retext` rewraps it."""
    m = re.search(r'<text x="[\d.]+" y="[\d.]+" style="([^"]*)" xml:space="preserve" id="%s">' % tid, s)
    assert m, f"{tid} not found"
    style = re.sub(r"--wrap:[\d.]+px", f"--wrap:{width:.1f}px", m.group(1))
    return s[: m.start()] + f'<text x="{x:.2f}" y="{y:.2f}" style="{style}" xml:space="preserve" id="{tid}">' + s[m.end():]


def place(crop, slot, k, halign="center", valign="center"):
    """Transform (tx, ty) putting `crop` (figure units) at scale k inside `slot` (poster units); and the placed rect."""
    cx, cy, cw, ch = crop
    sx, sy, sw, sh = slot
    W, H = cw * k, ch * k
    x0 = sx + {"left": 0, "center": (sw - W) / 2, "right": sw - W}[halign]
    y0 = sy + {"top": 0, "center": (sh - H) / 2, "bottom": sh - H}[valign]
    return x0 - cx * k, y0 - cy * k, (x0, y0, W, H)


def cover(gid, n, rect, fill="#ffffff"):
    x, y, w, h = rect
    return f'<rect id="{gid}-cover-{n}" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" style="fill:{fill};stroke:none"/>'


def group(gid, inner_id, src, crop, k, tx, ty, covers, clip=True):
    cx, cy, cw, ch = crop
    clipattr = f' clip-path="url(#clip-{gid})"' if clip else ""
    return (f'<g id="{gid}"{clipattr} data-src="{src}" data-crop="{cx:g} {cy:g} {cw:g} {ch:g}">'
            f'<g transform="matrix({k:g},0,0,{k:g},{tx:.3f},{ty:.3f})" id="{inner_id}">'
            f'<image id="{gid}-src" xlink:href="{src}" x="0" y="0" width="{FIG3_W}" height="{FIG3_H}" preserveAspectRatio="none"/>'
            f'{"".join(covers)}</g></g>')


def clip_def(cid, rect, rect_id):
    x, y, w, h = rect
    return f'<clipPath id="{cid}" clipPathUnits="userSpaceOnUse"><rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" id="{rect_id}"/></clipPath>'


def set_label(s, lid, x, y):
    s, n = re.subn(r'<text x="[\d.]+" y="[\d.]+" style="[^"]*" xml:space="preserve" id="%s">' % lid,
                   f'<text x="{x:.2f}" y="{y:.2f}" style="{LABEL}" xml:space="preserve" id="{lid}">', s)
    assert n == 1, f"{lid} not found"
    return s


def text_runs(s, tid):
    """The plain text of element `tid`, as one regular run."""
    body = re.search(r'id="%s">(.*?)</text>' % tid, s, re.S).group(1)
    return [(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip(), "")]


def set_box(s, rid, x, y, w, h):
    s, n = re.subn(r'<rect x="[\d.]+" y="[\d.]+" width="[\d.]+" height="[\d.]+" (style="[^"]*" id="%s"/>)' % rid,
                   lambda m: f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" {m.group(1)}', s)
    assert n == 1, f"{rid} not found"
    return s


def svg_box(path):
    """viewBox (x, y, w, h) of an asset: the baseline is y = 0."""
    return tuple(float(v) for v in re.search(r"""viewBox=['"]([^'"]+)['"]""", open(os.path.join(ROOT, path)).read(3000)).group(1).split())


def place_eq(s, iid, href, x, baseline):
    """Put asset `href` with its left edge at x and its baseline at `baseline`, at scale EQ_K; adds the element if missing."""
    vx, vy, vw, vh = svg_box(href)
    el = (f'<image id="{iid}" xlink:href="{href}" x="{vx:g}" y="{vy:g}" width="{vw:g}" height="{vh:g}" preserveAspectRatio="none" '
          f'transform="matrix({EQ_K:g},0,0,{EQ_K:g},{x - vx * EQ_K:.3f},{baseline:.3f})"/>')
    s, n = re.subn(r'<image id="%s" [^>]*/>' % iid, el, s)
    if n == 0:                                   # first run: after the equation-box text
        i = s.index("</text>", s.index('id="text1226"')) + len("</text>")
        s = s[:i] + el + s[i:]
    return s


def swatch(s, rid, x, baseline, colour, before=None):
    """A bullet swatch (30 px, Section 3's style) with its top 23 px above `baseline`; created before text `before`."""
    rect = f'<rect x="{x:.2f}" y="{baseline - 23:.2f}" width="30.00" height="30.00" style="fill:{colour};stroke:none" id="{rid}" rx="4"/>'
    s, n = re.subn(r'<rect [^>]*id="%s" rx="4"/>' % rid, rect, s)
    if n == 0:
        i = re.search(r'<text [^>]*id="%s">' % before, s).start()
        s = s[:i] + rect + s[i:]
    return s


def add_text(s, tid, like):
    """A copy of text element `like` (empty) with id `tid`, unless `tid` exists."""
    if f'id="{tid}"' in s:
        return s
    m = re.search(r'<text x="[\d.]+" y="[\d.]+" style="([^"]*)" xml:space="preserve" id="%s">.*?</text>' % like, s, re.S)
    return s[: m.end()] + f'<text x="0" y="0" style="{m.group(1)}" xml:space="preserve" id="{tid}"></text>' + s[m.end():]


def layout_s2(s):
    """Section 2: figure left and the conditions box right at equal heights, the eigenvalue box across the bottom."""
    s = retext(s, "text1225", S2_INTRO)
    y = float(re.search(r'<text x="[\d.]+" y="([\d.]+)" [^>]*id="text1225">', s).group(1)) + (retext.lines - 1) * 40 * 1.133
    for key, colour, runs in S2_BASES:              # swatch and text placed as Section 3's bullets
        y += BUL_PITCH
        tid = f"s2-base-{key}"
        s = add_text(s, tid, "text1225")
        s = move_text(s, tid, S2_X0 + 54, y, S2_X1 - S2_X0 - 54)
        s = retext(s, tid, runs)
        s = swatch(s, f"s2-swatch-{key}", S2_X0 + 4, y, colour, before=tid)
        y += (retext.lines - 1) * 40 * 1.133
    for key, _ in S2_CONDS:
        s = add_text(s, f"s2-cond-{key}-text", "text1226")
    WS = 36                                         # the box's body size, as in the Section 3 noise box
    s = re.sub(r'(style="font-size:)[\d.]+px([^"]*" xml:space="preserve" id="text1252")', rf"\g<1>{WS}px\2", s)
    lhw = WS * 1.133
    for key, _, _ in S2_BULLETS:
        s = add_text(s, f"s2-why-{key}-text", "text1252")
        s = add_text(s, f"s2-why-{key}-icon", "text1252")
    s = add_text(s, "s2-why-bpca-text", "text1252")
    BUL, GAP_B = 60, 8                              # bullet text indent; extra space between paragraphs
    lh40 = 40 * 1.133
    cw, ch = S2_CROP[2], S2_CROP[3]
    full = S2_X1 - S2_X0
    cond = {key: svg_box(f"assets/symbol-s2-cond-{key}.svg") for key, _ in S2_CONDS}
    gev = svg_box("assets/symbol-s2-eq.svg")
    asc = lambda vb: -vb[1] * EQ_K                  # height above the baseline
    desc = lambda vb: (vb[1] + vb[3]) * EQ_K        # depth below it
    GAP_EQ, GAP_COND = 10, 22                       # label to its equation; one condition to the next

    def column(k):                                  # conditions column (x, inner width, content height) at scale k
        x = S2_X0 + cw * k + S2_GAP
        inner = S2_X1 - x - 2 * PAD
        h = PAD + len(wrap(S2_LEAD, inner, 40)) * lh40 + GAP_COND
        for key, runs in S2_CONDS:
            h += len(wrap(runs, inner, 40)) * lh40 + GAP_EQ + asc(cond[key]) + desc(cond[key]) + GAP_COND
        return x, inner, h - GAP_COND + PAD

    inner_w = full - 2 * PAD
    why_h = (S2_BAR + PAD + len(wrap(S2_WHY, inner_w, WS)) * lhw
             + sum(len(wrap(runs, inner_w - BUL, WS)) * lhw + GAP_B for _, _, runs in S2_BULLETS)
             + lhw + len(wrap(S2_BPCA, inner_w, WS)) * lhw + GAP_B + 20 + asc(gev) + desc(gev) + 20
             + len(wrap(S2_EIG, inner_w, WS)) * lhw + PAD)
    intro_foot = y + 10                             # last baseline plus descent
    avail = S2_FOOT - intro_foot - 3 * S2_VGAP      # intro, row, box and the section foot, at least S2_VGAP apart
    k = next(k / 100 for k in range(330, 150, -1)
             if S2_X1 - column(k / 100)[0] >= S2_MIN_W and column(k / 100)[2] <= ch * k / 100
             and ch * k / 100 + why_h <= avail)
    x, inner, col_h = column(k)
    row_h = ch * k
    gap = (S2_FOOT - intro_foot - row_h - why_h) / 3
    fy = intro_foot + gap

    # figure: left
    src = re.search(r'<image id="s2-baselines-src" xlink:href="([^"]+)"', s).group(1)
    vw, vh = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', open(os.path.join(ROOT, src)).read(2000)).groups()
    s, n = re.subn(r'(<image id="s2-baselines-src" [^>]*?)width="[\d.]+" height="[\d.]+"', rf'\g<1>width="{vw}" height="{vh}"', s)
    assert n == 1                                   # the linked size follows the figure (Fig1 went 731 -> 665 tall)
    m = re.search(r'<g transform="matrix\([^)]*\)" id="g913">', s)
    tx, ty = S2_X0 - S2_CROP[0] * k, fy - S2_CROP[1] * k
    s = s[: m.start()] + f'<g transform="matrix({k:g},0,0,{k:g},{tx:.3f},{ty:.3f})" id="g913">' + s[m.end():]
    s, n = re.subn(r'<clipPath id="clip-s2-baselines" clipPathUnits="userSpaceOnUse"><rect [^>]*id="([^"]+)"/></clipPath>',
                   lambda mm: clip_def("clip-s2-baselines", (S2_X0, fy, cw * k, row_h), mm.group(1)), s)
    assert n == 1
    for l, (du, dv) in S2_LETTERS.items():
        lid = f"s2-baselines-label-{l}"
        mm = re.search(r'<text x="[\d.]+" y="[\d.]+" style="font-size:[\d.]+px([^"]*)" xml:space="preserve" id="%s">' % lid, s)
        s = s[: mm.start()] + (f'<text x="{S2_X0 + du * k:.2f}" y="{fy + dv * k:.2f}" style="font-size:{S2_LETTER_SIZE * k:.2f}px{mm.group(1)}" '
                               f'xml:space="preserve" id="{lid}">') + s[mm.end():]
    for i, (du, dv, w, h, fill) in enumerate(S2_COVERS):
        s, n = re.subn(r'<rect id="s2-baselines-cover-%d"[^>]*/>' % i,
                       f'<rect id="s2-baselines-cover-{i}" x="{S2_CROP[0] + du:.2f}" y="{S2_CROP[1] + dv:.2f}" width="{w:g}" height="{h:g}" style="fill:{fill};stroke:none"/>', s)
        assert n == 1

    # conditions box: the figure's height, its content centred vertically; equations indented under the label text
    s = set_box(s, "s2-eq-box", x, fy, S2_X1 - x, row_h)
    y = fy + (row_h - col_h) / 2 + PAD
    s = move_text(s, "text1226", x + PAD, y + 0.78 * 40, inner)
    s = retext(s, "text1226", S2_LEAD)
    y += retext.lines * lh40 + GAP_COND
    indent = measurer(40)("(a) ", "b")
    for key, runs in S2_CONDS:
        tid = f"s2-cond-{key}-text"
        s = move_text(s, tid, x + PAD, y + 0.78 * 40, inner)
        s = retext(s, tid, runs)
        y += retext.lines * lh40 + GAP_EQ + asc(cond[key])
        s = place_eq(s, f"s2-cond-{key}", f"assets/symbol-s2-cond-{key}.svg", x + PAD + indent, y)
        y += desc(cond[key]) + GAP_COND

    # eigenvalue box: full width, below the row; the generalized eigenvalue problem centred between its texts
    wy = fy + row_h + gap
    s = set_box(s, "s2-whynot-bar", S2_X0, wy, full, S2_BAR)
    s = set_box(s, "s2-whynot-box", S2_X0, wy + S2_BAR, full, why_h - S2_BAR)
    s, n = re.subn(r'<text x="[\d.]+" y="[\d.]+" (style="[^"]*" xml:space="preserve" id="s2-whynot-title">)',
                   rf'<text x="{S2_X0 + PAD:.2f}" y="{wy + 47:.2f}" \g<1>', s)
    assert n == 1
    y = wy + S2_BAR + PAD
    s = move_text(s, "text1252", S2_X0 + PAD, y + 0.78 * WS, inner_w)
    s = retext(s, "text1252", S2_WHY)
    y += retext.lines * lhw + GAP_B
    for key, glyph, runs in S2_BULLETS:             # the operator as the bullet: minus for subtractive, division for ratio
        s = move_text(s, f"s2-why-{key}-icon", S2_X0 + PAD + 8, y + 0.78 * WS + 5, BUL)   # +5: the larger glyph onto the text's x-height
        s = re.sub(r'(style="font-size:)[\d.]+px([^"]*" xml:space="preserve" id="s2-why-%s-icon")' % key, r"\g<1>52px\2", s)
        s = retext(s, f"s2-why-{key}-icon", [(glyph, "b")])
        s = move_text(s, f"s2-why-{key}-text", S2_X0 + PAD + BUL, y + 0.78 * WS, inner_w - BUL)
        s = retext(s, f"s2-why-{key}-text", runs)
        y += retext.lines * lhw + GAP_B
    y += lhw                                        # a blank line between the earlier methods and bPCA
    s = move_text(s, "s2-why-bpca-text", S2_X0 + PAD, y + 0.78 * WS, inner_w)
    s = retext(s, "s2-why-bpca-text", S2_BPCA)
    y += retext.lines * lhw + 20 + asc(gev)
    s = place_eq(s, "s2-eq", "assets/symbol-s2-eq.svg", S2_X0 + PAD + (inner_w - gev[2] * EQ_K) / 2, y)
    y += desc(gev) + 20
    s = re.sub(r'(<text x="[\d.]+" y="[\d.]+" style=")[^"]*(" xml:space="preserve" id="text1250">)',
               lambda mm: mm.group(1) + re.search(r'style="([^"]*)" xml:space="preserve" id="text1252"', s).group(1) + mm.group(2), s)
    s = move_text(s, "text1250", S2_X0 + PAD, y + 0.78 * WS, inner_w)
    s = retext(s, "text1250", S2_EIG)
    print(f"  s2 layout: k = {k:.2f}, figure {cw * k:.0f} x {row_h:.0f}, column {S2_X1 - x:.0f} wide, gaps {gap:.0f}")
    return s


def main():
    s = open(POSTER, encoding="utf-8").read()

    # ── Section 2: Fig1's (i), (j) dropped; layout_s2 places (f)-(h) and moves the letters with them ──
    s, n = re.subn(r'(<g id="s2-baselines" clip-path="url\(#clip-s2-baselines\)" data-src="[^"]*" data-crop=")[^"]*"',
                   rf'\g<1>{S2_CROP[0]:g} {S2_CROP[1]:g} {S2_CROP[2]:g} {S2_CROP[3]:g}"', s)
    assert n == 1, "s2-baselines not found"
    if "s2-baselines-label-d" in s:   # first run: drop (d), (e) and the covers over their source letters
        s, n = re.subn(r'<text [^>]*id="s2-baselines-label-[de]">.*?</text>', "", s, flags=re.S)
        assert n == 2
        s, n = re.subn(r'<rect id="s2-baselines-cover-[34]"[^>]*/>', "", s)
        assert n == 2
    s = layout_s2(s)

    # ── Section 3 results: row 1 of the new Fig3 in the old slot, at the old scale; the clip hugs the crop ──
    tx, ty, placed = place(CROP_S3, SLOT_S3, K3)
    s, n = re.subn(r'<clipPath id="clip-s3-results" clipPathUnits="userSpaceOnUse"><rect [^>]*id="([^"]+)"/></clipPath>',
                   lambda m: clip_def("clip-s3-results", placed, m.group(1)), s)
    assert n == 1, "clip-s3-results not found"
    g = group("s3-results", "g1031", FIG3, CROP_S3, K3, tx, ty, [cover("s3-results", 0, COVER_S3, TINT_S3), cover("s3-results", 1, EDGE_S3, TINT_S3)])
    s, n = re.subn(r'<g id="s3-results" .*?</g></g>', g, s, count=1, flags=re.S)
    assert n == 1
    for lid in ("s3-results-label-a", "s3-results-label-b", "s3-results-label-c"):
        x = float(re.search(r'<text x="([\d.]+)" y="[\d.]+" style="[^"]*" xml:space="preserve" id="%s">' % lid, s).group(1))
        s = set_label(s, lid, x, ty + TITLE_BASE_S3 * K3)

    # ── Section 4 results: the redrawn figure ((a) traces, (b) spectrum, side by side), the caption in a
    # full-width box below ──
    RESULTS_W, RESULTS_H = svg_box(RESULTS_FIG)[2:]
    s = re.sub(r'<clipPath id="clip-s4-(results|traces)" .*?</clipPath>', "", s, flags=re.S)   # no poster-side clips here
    x4, y4 = SLOT_S4[0], SLOT_S4[1]
    g = (f'<g id="s4-results" data-src="{RESULTS_FIG}"><g transform="matrix({K4:g},0,0,{K4:g},{x4:.2f},{y4:.2f})" id="g1178">'
         f'<image id="s4-results-src" xlink:href="{RESULTS_FIG}" x="0" y="0" width="{RESULTS_W:g}" height="{RESULTS_H:g}" preserveAspectRatio="none"/></g></g>')
    s, n = re.subn(r'(<g id="s4-traces" .*?</g></g>)?<g id="s4-results" .*?</g></g>(<rect id="s4-results-cover-[1-4]"[^>]*/>)*(<g id="s4-traces" .*?</g></g>)?',
                   g, s, count=1, flags=re.S)
    assert n == 1
    L4 = layout(RESULTS_LAYOUT)
    def at(panel, dx=0, dy=-8):   # a label's left and baseline: above the axis, past its y label by dx (figure units)
        bx, by, bw, bh = L4[panel]
        return x4 + (bx + dx) * K4, y4 + by * K4 + dy
    s = set_label(s, "s4-results-label-a", *at("traces", 0, -30))
    s = set_label(s, "s4-results-label-b", *at("eigenspectra", -28, -30))
    s = re.sub(r'<text [^>]*id="s4-results-label-c">.*?</text>', "", s, flags=re.S)     # (c) loadings: dropped
    s, n = re.subn(r'(<tspan id="tspan1181">)[^<]*', r"\g<1> Principal value spectrum", s); assert n == 1
    bx, by, bw = x4, y4 + RESULTS_H * K4 + 25, SLOT_S4[2]
    s = move_text(s, "text1305", bx + PAD, by + PAD + CAP_SIZE * 0.78, bw - 2 * PAD)

    # ── Section 4 schematic: regenerated at K4 (660 x 239), same slot ──
    s, n = re.subn(r'<g id="s4-schematic" transform="matrix\([^)]*\)" data-src="[^"]*"><image id="s4-schematic-src" x="0" y="0" width="[\d.]+" height="[\d.]+" preserveAspectRatio="none" xlink:href="[^"]*"/></g>',
                   f'<g id="s4-schematic" transform="matrix({K4:g},0,0,{K4:g},3680.34,1059.67)" data-src="{PHANTOM_FIG}"><image id="s4-schematic-src" x="0" y="0" width="{PHANTOM_W}" height="{PHANTOM_H}" preserveAspectRatio="none" xlink:href="{PHANTOM_FIG}"/></g>', s)
    assert n == 1, "s4-schematic not found"

    # ── Section 3 noise box: nugget_poster -> noise_poster (same size and scale) ──
    s, n = re.subn(r'<g id="s3-noise" transform="([^"]*)" data-src="[^"]*"><image id="s3-noise-src" x="0" y="0" width="[\d.]+" height="[\d.]+" preserveAspectRatio="none" xlink:href="[^"]*"/></g>',
                   lambda mm: f'<g id="s3-noise" transform="{mm.group(1)}" data-src="{NOISE_FIG}"><image id="s3-noise-src" x="0" y="0" width="{NOISE_W}" height="{NOISE_H}" preserveAspectRatio="none" xlink:href="{NOISE_FIG}"/></g>', s)
    assert n == 1, "s3-noise not found"
    s, n = re.subn(r'(<tspan id="s3-noise-label-d-t">)[^<]*(</tspan>)', r"\g<1>(d)\g<2>", s)
    assert n == 1
    s, n = re.subn(r'(<tspan id="s3-noise-label-e-t">)[^<]*(</tspan>)', r"\g<1>(e) Noise covariance\g<2>", s)
    assert n == 1
    mm = re.search(r'<g id="s3-noise" transform="matrix\(([\d.]+),0,0,[\d.]+,([\d.]+),([\d.]+)\)"', s)
    k3n, x3n = float(mm.group(1)), float(mm.group(2))
    L3 = layout(NOISE_LAYOUT)
    for lid, panel, dx in (("s3-noise-label-d", "series", -8), ("s3-noise-label-e", "covariance", -8)):
        y_old = float(re.search(r'<text x="[\d.]+" y="([\d.]+)" style="[^"]*" xml:space="preserve" id="%s">' % lid, s).group(1))
        s = set_label(s, lid, x3n + (L3[panel][0] + dx) * k3n, y_old)

    # ── Text ──
    print("text:")
    s = retext(s, "text1256", [
        ("We decoded the direction of drifting gratings (0°, 45°, 90° or 135°, 10% contrast; 75 trials each) "
         "from Neuropixels recordings of mouse visual cortex (Allen Visual Coding, Functional Connectivity "
         "set [5]; 23 sessions; 18 male, 5 female mice), pooling all visual cortical units.", "")], max_lines=3)
    d = (4 - retext.lines) * 40 * 1.133             # height saved against the original 4-line box
    s = set_box(s, "s3-intro-box", 1885, 640, 1575, 228.62 - d)
    for i, (tid, colour) in enumerate((("text1258", "#100f0d"), ("text1260", "#6ea0f9"), ("text1262", "#f93d53"))):
        y = 926.62 + i * BUL_PITCH - d / 2
        s = move_text(s, tid, 1943, y, 1505)
        s = swatch(s, f"s3-swatch-{i}", 1893, y, colour)
    s = retext(s, "text1262", [("Noise baseline", "b"),
        (": counting noise of firing rates, from spontaneous spikes (below)", "")], max_lines=1)
    noise_cap = [("(d)", "b"),
        (" Noise dominates fast fluctuations, so short windows can be used to estimate the noise covariance.\n", ""),
        ("(e)", "b"),
        (" We measure noise covariance from spontaneous spikes in 10 ms bins, scaled up to a trial-mean rate, which "
         f"has a median of {NOISE_FRAC}% of units' trial-mean variance.", "")]
    nb = [float(v) for v in re.search(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" [^>]*id="s3-noise-box"', s).groups()]
    M, P = 12, 16                                   # the caption's white box: inset in the grey box; text padding
    if 'id="s3-noise-capbox"' not in s:
        s = re.sub(r'(<text [^>]*id="text1267")', r'<rect x="0" y="0" width="0" height="0" style="fill:#ffffff;stroke:none" id="s3-noise-capbox"/>\1', s, count=1)
    ch = 2 * P + 36 * 0.78 + (len(wrap(noise_cap, nb[2] - 2 * M - 2 * P, 36)) - 1) * 36 * 1.133 + 36 * 0.3
    cy = nb[1] + nb[3] - M - ch                     # at the foot of the grey box
    s = set_box(s, "s3-noise-capbox", nb[0] + M, cy, nb[2] - 2 * M, ch)
    s = move_text(s, "text1267", nb[0] + M + P, cy + P + 36 * 0.78, nb[2] - 2 * M - 2 * P)
    s = retext(s, "text1267", noise_cap, max_lines=4)
    s3_cap = [("Above:", "i"), (" ", ""), ("(f)", "b"),
        (" Trial-mean responses of an example session (537 units) on its two leading PCA components; colors mark "
         "grating direction and crosses the class means.\n", ""),
        ("(g)", "b"), (" The same session on its two leading bPCA components.\n", ""),
        ("(h)", "b"), (" Error in decoding direction from the top ", ""), ("k", "i"),
        (" components (linear discriminant classifier, 5-fold cross-validation repeated 8 times; mean ± SD across "
         "23 sessions; dashed line: chance).", "")]
    n_cap = len(wrap(s3_cap, 962, 36))
    cap_h = max(371.12, 3246.56 + (n_cap - 1) * 36 * 1.133 + 29.58 - 3197.76)
    s = set_box(s, "s3-caption-box", 1885, 3197.76, 1010, cap_h)
    text_h = 36 * 0.78 + (n_cap - 1) * 36 * 1.133 + 36 * 0.3
    s = move_text(s, "text1277", 1909, 3197.76 + (cap_h - text_h) / 2 + 36 * 0.78, 962)   # centred in its box
    s = retext(s, "text1277", s3_cap)
    s = set_box(s, "s3-callout-box", 2923, 3197.76, 537, cap_h)
    s = add_text(s, "s3-callout-detail2", "s3-callout-detail")
    for row, tid in zip(CALLOUT, ("s3-callout-detail", "s3-callout-detail2")):     # two methods per row
        inner = "".join(f'<tspan style="font-weight:600;fill:{c}">{m}</tspan><tspan> {round(mu)} ± {round(sd)}°{"   " if i == 0 else ""}</tspan>'
                        for i, (m, c, mu, sd) in enumerate(row))
        s, n = re.subn(r'(<text )x="[\d.]+"( y="[\d.]+" [^>]*id="%s">).*?(</text>)' % tid, rf'\g<1>x="3191.50"\g<2>{inner}\g<3>', s, flags=re.S)
        assert n == 1
    for cid, off in (("head", 62), ("num", 175), ("detail", 245), ("detail2", 293), ("chance", 343)):   # the callout, centred in its box
        s, n = re.subn(r'(<text x="[\d.]+" y=")[\d.]+(" [^>]*id="s3-callout-%s">)' % cid,
                       rf"\g<1>{3197.76 + off + (cap_h - 371.12) / 2:.2f}\g<2>", s)
        assert n == 1
    s = move_text(s, "text1287", 1889, 3197.76 + cap_h + 62, 1567)
    assert 3197.76 + cap_h + 62 + 40 * 1.133 + 10 < 3742, "Section 3 closing text overruns the section"
    pca, bpca = round(PCA_K2), round(BPCA_K2)
    s, n = re.subn(r'(<tspan id="tspan1279">)[^<]*(</tspan>)', rf"\g<1>{pca}° → {bpca}°\g<2>", s); assert n == 1
    s, n = re.subn(r'(<tspan id="tspan1284">)[^<]*(</tspan>)', rf"\g<1>chance {round(CHANCE)}°\g<2>", s); assert n == 1
    s = retext(s, "text1287", [("With spontaneous activity as the redundancy baseline, ", ""),
        ("bPCA concentrates stimulus information into its leading components", "b"),
        (f", cutting the mean two-component error by {round(PCA_K2 - BPCA_K2)}°.", "")], max_lines=2)
    for tid, runs in TEXTS.items():
        s = retext(s, tid, runs)
    # authors on two lines, the block (with the affiliation) centred on the crest as before
    s, n = re.subn(r'(<text x="408.00" y=")[\d.]+(" [^>]*id="authors">).*?</text>',
                   r'\g<1>163.50\g<2><tspan x="408" y="163.50" id="tspan1184">Brendan Harris</tspan>'
                   r'<tspan x="408" y="235.50" id="tspan1184b">Ben Fulcher</tspan></text>', s, flags=re.S); assert n == 1
    s, n = re.subn(r'(<text x="408.00" y=")[\d.]+(" [^>]*id="affiliation">)', r"\g<1>315.50\g<2>", s); assert n == 1
    s = re.sub(r'<text [^>]*id="s5-code">.*?</text>', "", s, flags=re.S)             # the code line and Julia logo: cut
    s = re.sub(r'<g [^>]*id="s5-julia">.*?</g>', "", s, flags=re.S)
    s = add_text(s, "s5-closing", "text1317")                       # closing line, under the last bullet's 2 lines
    s = move_text(s, "s5-closing", 4418, 2968.67 + 45.32 + 47, 801)
    s = retext(s, "s5-closing", [("bPCA is a practical algorithm to correct for redundancy and noise across multiple fields.", "")], max_lines=2)
    for tid, txt in TITLES.items():
        s, n = re.subn(r'(<tspan id="%s">)[^<]*(</tspan>)' % tid, rf"\g<1>{txt}\g<2>", s); assert n == 1
    # header: contact details, one per line under the title bar, filling the white panel (to y = 397)
    CT, CS, CP = 46, 38, 64                              # title size, contact size, line pitch
    BAR, f = round(CT * 1.35), CS / 27                   # f: icon scale relative to the original 27 px rows
    s = re.sub(r'<text id="takehome-[1-4]"[^>]*>.*?</text>', "", s, flags=re.S)
    s = re.sub(r'<rect id="takehome-card-\d"[^>]*/>', "", s)
    s, n = re.subn(r'(<rect id="takehome-bar" x="4052" y="52" width="802" height=")[\d.]+"', rf'\g<1>{BAR}"', s); assert n == 1
    s, n = re.subn(r'(<rect id="takehome-box" x="4052" y="52" width="802" height=")[\d.]+"', r'\g<1>345"', s); assert n == 1
    s, n = re.subn(r'<text id="takehome-title" x="[\d.]+" y="[\d.]+" style="font-size:[\d.]+px',
                   f'<text id="takehome-title" x="4070" y="{52 + BAR / 2 + 0.33 * CT:.1f}" style="font-size:{CT}px', s); assert n == 1
    s, n = re.subn(r'(<text id="takehome-title"[^>]*><tspan>)[^<]*(</tspan>)', r"\g<1>Contact details\g<2>", s); assert n == 1
    mid = (52 + BAR + 397) / 2
    for i, (tid, icon) in enumerate((("contact-email", "icon-email"), ("contact-x", "path3133"),
                                     ("contact-github", "icon-github"), ("contact-bluesky", "path3137"))):
        cy, cx = mid + (i - 1.5) * CP, 4095                # icon centre; text x-height centred on it
        s, n = re.subn(r'(<text id="%s" x=")[\d.]+(" y=")[\d.]+(" style="font-size:)[\d.]+px' % tid,
                       rf'\g<1>4138\g<2>{cy + 0.33 * CS:.1f}\g<3>{CS}px', s); assert n == 1
        if icon.startswith("icon-"):                     # 24-unit symbols at scale 1.5
            a = 1.5 * f
            s, n = re.subn(r'<g id="%s" transform="matrix\([^)]*\)">' % icon,
                           f'<g id="{icon}" transform="matrix({a:.4f},0,0,{a:.4f},{cx - 12 * a:.2f},{cy - 12 * a:.2f})">', s); assert n == 1
        else:                                            # y-flipped images: local centre (u, v)
            u, v = {"path3133": (8.76, -9.62), "path3137": (8.795, -11.83)}[icon]
            b_ = 1.3333333 * f
            s, n = re.subn(r'(<image id="%s" [^>]*transform=")matrix\([^)]*\)"' % icon,
                           rf'\g<1>matrix({b_:.5f},0,0,{-b_:.5f},{cx - b_ * u:.3f},{cy + b_ * v:.3f})"', s); assert n == 1
    s = retext(s, "text1315", [("In mouse visual cortex, ", ""), ("two bPCA components", "b"),
        (f" decoded grating direction with {bpca}° error, against {pca}° for PCA.", "")], max_lines=3)
    s = retext(s, "text1293", [
        ("Temporal autocorrelation pervades neural and behavioral time series, and PCA of autocorrelated "
         "signals returns smooth, sinusoid-like components (phantom oscillations) [6]. We simulated 200 signals "
         "that share a weak, chaotic latent, on top of independent 1/f background activity and a shared "
         "instrument artifact.", "")], max_lines=4)
    s = retext(s, "text1297", [("Noise baseline", "b"),
        (": a calibration recording of the instrument only", "")], max_lines=1)
    s = retext(s, "text1305", [("(a)", "b"),
        (f" The leading PCA component is a slow phantom oscillation (ρ\u00a0=\u00a0{R_TRACE_PCA:.2f} with the latent), "
         f"whereas the leading bPCA component recovers the latent (ρ\u00a0=\u00a0{R_TRACE_BPCA:.2f}). Given the same redundancy "
         f"baseline, cPCA (ρ\u00a0=\u00a0{MC_CPCA:.2f}) and ρPCA (ρ\u00a0=\u00a0{MC_RHOPCA:.2f}) also fail (medians over {NSIM} simulations).\n", ""),
        ("(b)", "b"),
        (f" Held-out eigenvalues (medians across {NSIM} simulations): the two leading PCA eigenvalues are nearly "
         "equal, as for phantom oscillations, whereas the bPCA eigenvalues fall to the baseline level of one "
         "(dashed) by the third component.", "")])
    bh = 2 * PAD + CAP_SIZE * 0.78 + (retext.lines - 1) * CAP_SIZE * 1.133 + CAP_SIZE * 0.3
    assert by + bh < 2649.37 - 25, f"Section 4 caption runs into the Summary bar ({by + bh:.0f})"
    s, n = re.subn(r'<rect x="[\d.]+" y="[\d.]+" width="[\d.]+" height="[\d.]+" style="fill:#eef1f2;stroke:none" id="s4-caption-box"/>',
                   f'<rect x="{bx:.2f}" y="{by:.2f}" width="{bw:.2f}" height="{bh:.2f}" style="fill:#eef1f2;stroke:none" id="s4-caption-box"/>', s)
    assert n == 1, "s4-caption-box not found"

    s = add_text(s, "text-ref7", "text1354")
    refs = iter(enumerate(zip(REF_IDS, REFS), 1))
    for x, n in REF_COLS:
        y = REF_Y0
        for _ in range(n):
            i, (tid, runs) = next(refs)
            s = move_text(s, tid, x, y, 767.5)
            s = retext(s, tid, [(f"{i}. ", "")] + runs)
            y += retext.lines * REF_LH + REF_GAP
        assert y < 3730, "references overrun their box"

    s = s.replace("font-family:Arial;", "font-family:'Source Sans 3';")   # dark-bar titles: no Arial on karl, resvg drew nothing
    open(POSTER, "w", encoding="utf-8").write(s)
    print(f"s2: crop {S2_CROP}; s3-results: crop {CROP_S3} at k = {K3}; s4: {RESULTS_FIG} at k = {K4}")


if __name__ == "__main__":
    main()
