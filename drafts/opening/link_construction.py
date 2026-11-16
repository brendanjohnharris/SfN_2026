"""Link figures/src/construction_poster.svg into SfN_2026.svg and lay out Section 1.

The figure fills the section's height at the right. At the left, a text column holds the intro as
free text (the relink's TEXTS, rewrapped here) over the caption box, which runs to the section foot.
The column takes the narrowest width (a multiple of 10) at which both fit; the figure is redrawn by
make_1f.py's option1f_vertical whenever the slot this leaves changes shape. Run it after
figures/relink_case_studies.py, which rewraps the intro texts in place.

Usage, from the repo root:  python3 drafts/opening/link_construction.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [HERE, os.path.join(ROOT, "figures")]
import make_1f                                  # noqa: E402
import relink_case_studies as R                 # noqa: E402

POSTER = os.path.join(ROOT, "SfN_2026.svg")
FIG = "figures/src/construction_poster.svg"
X0, X1, Y0, Y1 = 103, 1678, 631, 2081       # Section 1's content area (51 inside the white panel)
GUTTER, CAP_GAP = 30, 40                    # column to figure; intro text to caption box
NUDGE = -30                                 # the figure drawn left of its slot: its own left margin is empty
PAD, SIZE, LH = 26, 36, 36 * 1.133          # caption box padding, font size, line height
LH40 = 40 * 1.133                           # the intro's line height
STYLE = f"font-size:{SIZE}px;line-height:1.133;font-family:'Source Sans 3';fill:#100f0d;text-anchor:start"

# Runs of (text, style): "" regular, "b" semibold, "i" italic. Wrapped at run time with the real font.
CAPTION = [
    ("Right:", "i"), (" ", ""), ("(a)", "b"),
    (" Each grating direction activates a subnetwork (colored by direction), on top of a background network "
     "(gray) that is active without any stimulus.\n", ""),
    ("(b)", "b"),
    (" A gray screen drives the background network only, revealing the redundant subspace.\n", ""),
    ("(c)", "b"),
    (" Correcting for the redundant activity reveals stimulus-engaged subnetworks. Baseline PCA measures the "
     "variance in (a) relative to (b), above the spiking noise, whereas PCA on (a) alone returns the largest and "
     "most active subnetwork dominated by redundancy.", ""),
]


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


def lay(s, lw):
    """Intro and caption at column width `lw`; returns the poster and the caption's spare height."""
    y = Y0 + 40 * 0.78
    ind = R.measurer(40)("\u2022 ", "")                                 # hanging indent under the bullet
    for tid, x, step in (("text1195", X0, 0), ("text1197", X0 + ind, 56.7), ("text1204", X0 + ind, 50.66), ("text1207", X0, 56.66)):
        y += step
        s = R.move_text(s, tid, x, y, X0 + lw - x)
        s = R.retext(s, tid, R.TEXTS[tid])
        if tid in ("text1197", "text1204"):
            bid = "s1-icon-red" if tid == "text1197" else "s1-icon-noise"
            s, n = re.subn(r'<text id="%s" x="[\d.]+" y="[\d.]+"' % bid, f'<text id="{bid}" x="{X0}" y="{y:.2f}"', s); assert n == 1
        y += (R.retext.lines - 1) * LH40
    cap_y = y + 40 * 0.3 + CAP_GAP
    lines = R.wrap(CAPTION, lw - 2 * PAD, SIZE)
    need = 2 * PAD + SIZE * 0.78 + (len(lines) - 1) * LH + SIZE * 0.3
    x0, y0 = X0 + PAD, cap_y + PAD + SIZE * 0.78 + max(Y1 - cap_y - need, 0) / 2   # spare split above and below
    body = "".join(tspan_line(line, x0, y0 + i * LH, i) for i, line in enumerate(lines))
    new_text = (f'<text x="{x0:.2f}" y="{y0:.2f}" style="{STYLE};--wrap:{lw - 2 * PAD:.1f}px" xml:space="preserve" id="text1217">'
                f'{body}</text>')
    s, n = re.subn(r'<text x="[\d.]+" y="[\d.]+" style="[^"]*" xml:space="preserve" id="text1217">.*?</text>', new_text, s, count=1, flags=re.S)
    assert n == 1, "text1217 not found"
    s = R.set_box(s, "s1-caption-box", X0, cap_y, lw, Y1 - cap_y)
    lay.lines = len(lines)
    return s, Y1 - cap_y - need


def main():
    s = open(POSTER, encoding="utf-8").read()
    assert "s1-construction" in s, "the one-time cameras-to-construction swap is in git history (2f294a6)"
    s = re.sub(r'<rect [^>]*id="s1-intro-box"/>', "", s)                  # the intro is free text
    s = re.sub(r'<g id="(s1-icon-(?:red|noise))" transform=.*?</g>',     # icons became plain bullets
               lambda m: f'<text id="{m.group(1)}" x="0" y="0" style="font-size:40px;font-family:\'Source Sans 3\';fill:#100f0d">\u2022</text>', s, flags=re.S)
    lw = next(w for w in range(500, 1000, 10) if lay(s, w)[1] >= 0)     # narrowest column that holds the text
    s, spare = lay(s, lw)
    # the figure fills the rest, redrawn if the slot changed shape
    fx = X0 + lw + GUTTER
    slot_w, slot_h = X1 - fx, Y1 - Y0
    fw, fh = (float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', open(os.path.join(ROOT, FIG)).read()).groups())
    if abs(fh * slot_w / fw - slot_h) > 1:
        make_1f.SLOT_W, make_1f.SLOT_H = slot_w, slot_h
        make_1f.option1f_vertical()
        fw, fh = (float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', open(os.path.join(ROOT, FIG)).read()).groups())
    k = slot_w / fw
    s, n = re.subn(r'<rect x="[\d.]+" y="[\d.]+" width="[\d.]+" height="[\d.]+" id="rect275"/>',
                   f'<rect x="{fx:.2f}" y="{Y0:.2f}" width="{slot_w:.2f}" height="{slot_h:.2f}" id="rect275"/>', s); assert n == 1
    s, n = re.subn(r'data-crop="[^"]*">(<g transform=")matrix\([^)]*\)(" id="g795"><image id="s1-construction-src" xlink:href="[^"]*" x="0" y="0" )width="[\d.]+" height="[\d.]+"',
                   rf'data-crop="0 0 {fw:g} {fh:g}">\g<1>matrix({k:.5f},0,0,{k:.5f},{fx + NUDGE},{Y0})\g<2>width="{fw:g}" height="{fh:g}"', s); assert n == 1
    open(POSTER, "w", encoding="utf-8").write(s)
    print(f"section 1: text column {lw}, caption {lay.lines} lines ({spare:.0f} px spare); figure {slot_w} x {slot_h} at k = {k:.3f}")


if __name__ == "__main__":
    main()
