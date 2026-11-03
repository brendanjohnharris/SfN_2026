"""Link figures/src/construction_poster.svg into SfN_2026.svg as the Section 1 figure.

Replaces the cameras figure (`s1-cameras`, a crop of Fig1_schematic.svg) with the construction
figure, drops the three poster-drawn panel letters (the new figure carries its own), moves the
Section 1 caption box to the right of the figure and rewrites the caption. Re-running it on a
converted poster only refreshes the caption box and text, so edit CAPTION here and rerun.

Usage, from the repo root:  python3 drafts/opening/link_construction.py
"""

import glob
import os
import re

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
POSTER = os.path.join(ROOT, "SfN_2026.svg")
FIG = "figures/src/construction_poster.svg"
FW, FH = 900, 1050            # the figure's size (poster units; it is placed at scale 1)
FX, FY = 110, 1050            # where it sits in the column
CAP_X, CAP_Y, CAP_W = 1040, 1050, 638      # the caption box, to the right of the figure
PAD, SIZE, LH = 26, 36, 36 * 1.133          # box padding, caption font size, line height (poster convention)
STYLE = f"font-size:{SIZE}px;line-height:1.133;font-family:'Source Sans 3';fill:#100f0d;text-anchor:start"

# Runs of (text, style): "" regular, "b" semibold, "i" italic. Wrapped at run time with the real font.
CAPTION = [
    ("Left:", "i"), (" ", ""), ("(a)", "b"),
    (" A line of grating directions feeds a sheet of cells. Each grating drives one cell most "
     "(coloured arrows), and a shared input keeps driving its own group (grey), which overlaps the "
     "driven one. Co-active cells are linked, and the recording does not say which link came from "
     "where. ", ""),
    ("(b)", "b"),
    (" Gray screen: the shared input alone drives one group, one signal fanned to many cells: "
     "redundant links, and a subset of the cells in (a). ", ""),
    ("(c)", "b"),
    (" Which links did the grating add? Subtracting the pictures is the idea. Baseline PCA measures "
     "the variance in (a) relative to (b), above the spiking noise, one direction at a time, whereas "
     "PCA on (a) alone returns the largest cluster, the redundant one.", ""),
]


def measurer():
    """Text width in px at SIZE, with Source Sans 3 when it is installed (else a 0.5 em estimate)."""
    try:
        from PIL import ImageFont
        fonts = {}
        for kind, pat in (("", "SourceSans3-Regular"), ("b", "SourceSans3-Semibold"), ("i", "SourceSans3-It")):
            paths = glob.glob(os.path.expanduser(f"~/.fonts/{pat}.otf")) + glob.glob(f"/usr/share/fonts/**/{pat}.otf", recursive=True)
            fonts[kind] = ImageFont.truetype(paths[0], SIZE)
        return lambda txt, kind: fonts[kind].getlength(txt)
    except Exception:
        return lambda txt, kind: 0.5 * SIZE * len(txt)


def wrap(runs, width):
    """Greedy word wrap of styled runs into lines of [(word-or-space, kind)], measured per run."""
    w = measurer()
    tokens = []
    for text, kind in runs:
        for part in re.split(r"(\s+)", text):
            if part:
                tokens.append((part, kind))
    lines, cur, cur_w = [], [], 0.0
    for tok, kind in tokens:
        tw = w(tok, kind)
        if tok.isspace():
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


def tspan_line(line, x, y, n):
    out = []
    for txt, kind in line:
        if kind == "b":
            out.append(f'<tspan style="font-weight:600">{txt}</tspan>')
        elif kind == "i":
            out.append(f'<tspan style="font-style:italic">{txt}</tspan>')
        else:
            out.append(txt)
    return f'<tspan x="{x}" y="{y:.4f}" id="s1-cap-{n}">{"".join(out)}</tspan>'


def main():
    s = open(POSTER, encoding="utf-8").read()
    if "s1-construction" not in s:
        # 1. the clip rect becomes the new slot
        s, n = re.subn(r'<clipPath id="clip-s1-cameras" clipPathUnits="userSpaceOnUse"><rect x="[\d.]+" y="[\d.]+" width="[\d.]+" height="[\d.]+" id="rect275"/></clipPath>',
                       f'<clipPath id="clip-s1-construction" clipPathUnits="userSpaceOnUse"><rect x="{FX:.2f}" y="{FY:.2f}" width="{FW:.2f}" height="{FH:.2f}" id="rect275"/></clipPath>', s)
        assert n == 1, "clip-s1-cameras not found"
        # 2. the figure group
        group = (f'<g id="s1-construction" clip-path="url(#clip-s1-construction)" data-src="{FIG}" data-crop="0 0 {FW} {FH}">'
                 f'<g transform="matrix(1,0,0,1,{FX},{FY})" id="g795">'
                 f'<image id="s1-construction-src" xlink:href="{FIG}" x="0" y="0" width="{FW}" height="{FH}" preserveAspectRatio="none"/>'
                 f'</g></g>')
        s, n = re.subn(r'<g id="s1-cameras" .*?</g></g>', group, s, count=1, flags=re.S)
        assert n == 1, "s1-cameras group not found"
        # 3. the poster-drawn panel letters of the old figure
        s, n = re.subn(r'<text [^>]*id="s1-cameras-label-[abc]"><tspan id="tspan\d+">\([abc]\)</tspan></text>', '', s)
        assert n == 3, f"expected 3 panel letters, removed {n}"
        print("replaced the cameras figure with", FIG)
    # 4. the caption text, wrapped to the box
    x0, y0 = CAP_X + PAD, CAP_Y + PAD + SIZE * 0.78
    lines = wrap(CAPTION, CAP_W - 2 * PAD)
    body = "".join(tspan_line(line, x0, y0 + i * LH, i) for i, line in enumerate(lines))
    cap_h = 2 * PAD + SIZE * 0.78 + (len(lines) - 1) * LH + SIZE * 0.3
    new_text = (f'<text x="{x0:.2f}" y="{y0:.2f}" style="{STYLE};inline-size:{CAP_W - 2 * PAD:.1f}px" xml:space="preserve" id="text1217">'
                f'{body}</text>')
    s, n = re.subn(r'<text x="[\d.]+" y="[\d.]+" style="[^"]*" xml:space="preserve" id="text1217">.*?</text>', new_text, s, count=1, flags=re.S)
    assert n == 1, "text1217 not found"
    # 5. the caption box hugs the text, to the right of the figure
    s, n = re.subn(r'<rect x="[\d.]+" y="[\d.]+" width="[\d.]+" height="[\d.]+" style="fill:#eef1f2;stroke:none" id="s1-caption-box"/>',
                   f'<rect x="{CAP_X:.2f}" y="{CAP_Y:.2f}" width="{CAP_W:.2f}" height="{cap_h:.2f}" style="fill:#eef1f2;stroke:none" id="s1-caption-box"/>', s)
    assert n == 1, "s1-caption-box not found"
    open(POSTER, "w", encoding="utf-8").write(s)
    print(f"caption: {len(lines)} lines, box {CAP_W} x {cap_h:.0f} at {CAP_X},{CAP_Y}")


if __name__ == "__main__":
    main()
