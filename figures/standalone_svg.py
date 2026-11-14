"""Write a self-contained copy of SfN_2026.svg: linked SVGs inlined (as export_pdf.py does), rasters as data URIs.

Usage:  python3 -I figures/standalone_svg.py OUT.svg [ROOT]   (ROOT: the checkout to build from; default this one)
"""
import base64, itertools, mimetypes, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import export_pdf as E

out = sys.argv[1]
root = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else E.ROOT
s = open(os.path.join(root, "SfN_2026.svg"), encoding="utf-8").read()
n = itertools.count()


def repl(m):
    a = E.attrs(m.group(0))
    vb, body = E.inline(os.path.join(root, a["xlink:href"]), f"i{next(n)}-")
    svg = (f'<svg x="{a.get("x", "0")}" y="{a.get("y", "0")}" width="{a["width"]}" height="{a["height"]}" viewBox="{vb}" '
           f'preserveAspectRatio="{a.get("preserveAspectRatio", "xMidYMid meet")}" overflow="hidden">{body}</svg>')
    keep = " ".join(f'{k}="{a[k]}"' for k in ("transform", "style", "opacity", "clip-path") if k in a)
    return f"<g {keep}>{svg}</g>" if keep else svg


def data(m):
    p = m.group(3)
    return f'{m.group(1)}="data:{mimetypes.guess_type(p)[0]};base64,{base64.b64encode(open(p, "rb").read()).decode()}"'


s = re.sub(r'<image\b[^>]*xlink:href="[^"]+\.svg"[^>]*/>', repl, s)
s = E.absolutize(s, root)
s, k = re.subn(r"""((?:xlink:)?href)=(["'])(/[^"']+)\2""", data, s)
assert not re.search(r"""href=["'](?!data:|#|https?:)""", s), "a link is still external"
open(out, "w", encoding="utf-8").write(s)
print(f"inlined {next(n)} SVGs, embedded {k} rasters; {os.path.getsize(out) / 1e6:.1f} MB")
