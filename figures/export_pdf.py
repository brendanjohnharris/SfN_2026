"""Write SfN_2026.pdf, fully vector.

Inkscape rasterizes an SVG linked through <image> at the file's intrinsic size (34-79 ppi here), so this
inlines every linked SVG as a nested <svg> (ids prefixed per copy, relative links made absolute) into a
temporary copy of the poster, then exports that copy with Inkscape. Raster images stay embedded as they are.

Usage, from the repo root:  python3 -I figures/export_pdf.py [path/to/inkscape]
"""
import itertools
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
POSTER, OUT = os.path.join(ROOT, "SfN_2026.svg"), os.path.join(ROOT, "SfN_2026.pdf")
INKSCAPE = sys.argv[1] if len(sys.argv) > 1 else "inkscape"
HREF = r"""((?:xlink:)?href)=(["'])(?!data:|#|https?:|/)([^"']+)\2"""   # a relative link (dvisvgm quotes with ')


def attrs(tag):
    return {k: v for k, _, v in re.findall(r"""([\w:-]+)=(["'])(.*?)\2""", tag)}


def absolutize(text, base):
    return re.sub(HREF, lambda m: f'{m.group(1)}="{os.path.normpath(os.path.join(base, m.group(3)))}"', text)


def inline(path, prefix):
    """The viewBox and body of the SVG at `path`, its ids prefixed so copies cannot collide."""
    src = re.sub(r"<\?xml.*?\?>|<!DOCTYPE[^>]*>|<!--.*?-->", "", open(path, encoding="utf-8").read(), flags=re.S)
    m = re.search(r"<svg\b([^>]*)>(.*)</svg>\s*$", src, re.S)
    root, body = attrs(m.group(1)), m.group(2)
    assert "<style" not in body, f"{path}: CSS selectors would need prefixing too"
    body = re.sub(r"""\bid=(["'])([^"']+)\1""", rf'id="{prefix}\2"', body)
    body = re.sub(r"url\(#([^)]+)\)", rf"url(#{prefix}\1)", body)
    body = re.sub(r"""((?:xlink:)?href)=(["'])#([^"']+)\2""", rf'\1="#{prefix}\3"', body)
    vb = root.get("viewBox") or f"0 0 {float(root['width'].rstrip('ptx'))} {float(root['height'].rstrip('ptx'))}"
    return vb, absolutize(body, os.path.dirname(path))


def main():
    s = open(POSTER, encoding="utf-8").read()
    n = itertools.count()

    def repl(m):
        a = attrs(m.group(0))
        vb, body = inline(os.path.join(ROOT, a["xlink:href"]), f"i{next(n)}-")
        svg = (f'<svg x="{a.get("x", "0")}" y="{a.get("y", "0")}" width="{a["width"]}" height="{a["height"]}" viewBox="{vb}" '
               f'preserveAspectRatio="{a.get("preserveAspectRatio", "xMidYMid meet")}" overflow="hidden">{body}</svg>')
        keep = " ".join(f'{k}="{a[k]}"' for k in ("transform", "style", "opacity", "clip-path") if k in a)
        return f"<g {keep}>{svg}</g>" if keep else svg

    s = re.sub(r'<image\b[^>]*xlink:href="[^"]+\.svg"[^>]*/>', repl, s)
    s = absolutize(s, ROOT)                                       # the poster's own raster links
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf-8") as f:
        f.write(s)
    try:
        subprocess.run([INKSCAPE, f.name, "--export-type=pdf", f"--export-filename={OUT}"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        os.remove(f.name)
    print(f"inlined {next(n)} linked SVGs; wrote {OUT} ({os.path.getsize(OUT) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
