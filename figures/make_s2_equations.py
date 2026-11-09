"""Render the Section 2 bPCA conditions to assets/symbol-s2-cond-{r,n,t}.svg, and the solution chain to
assets/symbol-s2-eq.svg (LaTeX -> dvisvgm, glyphs as paths).

The three conditions on the bPCA projection P, as in the manuscript's Methods (BaselinePCA.tex, main.tex):
the redundancy baseline is whitened, the noise baseline collapses, the test data become diagonal; and the
solution, main.tex Methods (redundancy blue, noise red). Each viewBox is the exact bbox plus 2% padding,
with the baseline at y = 0, and the root size is the viewBox x 42 (about 800 ppi as printed), as for the
other assets (CLAUDE.md, step 8).

Usage, from the repo root:  python3 figures/make_s2_equations.py
"""
import os
import re
import subprocess
import tempfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
K = 42
EQS = {
    "r": r"P^{T}\,{\color{redund}\Sigma^2_r}\,P = I",
    "n": r"P^{T}\,{\color{noise}\Sigma^2_n}\,P = \mathbf{0}",
    "t": r"P^{T}\,\Sigma^2\,P = \hat{\sigma}^2_{+}",
    # the solution: noise-corrected generalized eigenvalue problem, then symmetric orthogonalization against the test data
    "eq": r"(\Sigma^2 - {\color{noise}\Sigma^2_n})\,V = ({\color{redund}\Sigma^2_r} - {\color{noise}\Sigma^2_n})\,V\hat{\sigma}^2"
          r"\quad\longrightarrow\quad P = V\,(V^{T}\Sigma^2 V)^{-1/2}\,\hat{\sigma}_{+}",
}
OUT = lambda key: "symbol-s2-eq.svg" if key == "eq" else f"symbol-s2-cond-{key}.svg"
TEX = r"""\documentclass{article}
\usepackage{amsmath,xcolor}
\definecolor{redund}{HTML}{6ea0f9}\definecolor{noise}{HTML}{f93d53}
\pagestyle{empty}
\begin{document}
$\displaystyle %s$
\end{document}
"""

with tempfile.TemporaryDirectory() as tmp:
    for key, eq in EQS.items():
        open(os.path.join(tmp, "eq.tex"), "w").write(TEX % eq)
        subprocess.run(["latex", "-interaction=nonstopmode", "eq.tex"], cwd=tmp, check=True, capture_output=True)
        subprocess.run(["dvisvgm", "--no-fonts", "--exact-bbox", "--bbox=min", "-o", "eq.svg", "eq.dvi"],
                       cwd=tmp, check=True, capture_output=True)
        svg = open(os.path.join(tmp, "eq.svg")).read()
        # dvisvgm places the page origin at the top-left; shift so the baseline is y = 0
        x, y, w, h = (float(v) for v in re.search(r"viewBox='([^']+)'", svg).group(1).split())
        base = float(re.search(r"<use [^>]*y='([\d.\-]+)'", svg).group(1))     # the leading P sits on the baseline
        pad = 0.02 * max(w, h)
        vb = (x - pad, y - base - pad, w + 2 * pad, h + 2 * pad)
        svg = re.sub(r"<g id='page1'>", f"<g id='page1' transform='translate(0,{-base:.6f})'>", svg)
        svg = re.sub(r"viewBox='[^']+'", "viewBox='%.2f %.2f %.2f %.2f'" % vb, svg)
        svg = re.sub(r"(<svg [^>]*?) width='[^']*' height='[^']*'", r"\1", svg)
        svg = svg.replace("<svg ", f'<svg width="{vb[2] * K:.0f}" height="{vb[3] * K:.0f}" ', 1)
        svg = re.sub(r"id='g", f"id='s2c{key}-g", svg).replace("xlink:href='#g", f"xlink:href='#s2c{key}-g")
        out = os.path.join(ROOT, "assets", OUT(key))
        open(out, "w").write(svg)
        print(f"{out}: viewBox {' '.join('%.2f' % v for v in vb)}")
