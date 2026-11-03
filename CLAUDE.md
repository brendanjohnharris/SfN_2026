# CLAUDE.md

## Purpose
This document summarizes the SVG optimization procedures carried out so far in this folder, including validation steps and outcomes.

## Timeline of Procedures

### 1) Initial SVG audit and hotspot profiling
- Inspected the poster SVG line-by-line to find high-value minification targets.
- Identified major bloat sources:
  - Hidden Inkscape grid layer.
  - Grid-only clipPath definitions.
  - Very long path vectors (icons/symbols and equation glyphs).
  - Verbose text tspans with long dx arrays.

### 2) Removed hidden editing grid artifacts
- Removed the hidden grid layer:
  - `g` with id `layer-MC7`.
- Removed grid-only clipPaths:
  - `clipPath3812` through `clipPath4012`.
- Preserved functional clip paths (for example `clip-s1-cameras`).

Validation used:
- Searched for removed IDs after edit to confirm no leftovers.
- Confirmed required non-grid clip paths remained present.

### 3) Re-profiled remaining heavy vectors
- Recomputed longest `<path>` lines and mapped them to visual elements.
- Confirmed the largest remaining heavy paths were symbol/icon-heavy, including:
  - `path599`
  - `path1185` (QR)
  - `s5-icon-brain-path3420`
  - `s5-julia-path3543`
  - `path1359` (GitHub)
  - equation glyph paths (`s2-eq-g*`)

### 4) Externalized heavy symbols into separate SVG files
Created these files under `assets/`:
- `assets/symbol-path599.svg`
- `assets/symbol-x.svg`
- `assets/symbol-bluesky.svg`
- `assets/symbol-qr.svg`
- `assets/symbol-brain.svg`
- `assets/symbol-github.svg`
- `assets/symbol-julia.svg`
- `assets/symbol-s2-eq.svg`

### 5) Rewired main poster SVG to linked assets
Replaced inline heavy vectors/groups in `SfN_2026.svg` with `<image xlink:href="assets/...">` links while preserving placement via existing transforms.

Replacements included:
- `path599` -> `assets/symbol-path599.svg`
- `path3133` -> `assets/symbol-x.svg`
- `path3137` -> `assets/symbol-bluesky.svg`
- `path1185` -> `assets/symbol-qr.svg`
- `s5-icon-brain-path3420` -> `assets/symbol-brain.svg`
- `path1359` -> `assets/symbol-github.svg`
- `s5-julia` group -> `assets/symbol-julia.svg`
- `s2-eq` group -> `assets/symbol-s2-eq.svg`

### 6) Completed equation extraction cleanup
- After externalizing `s2-eq`, removed inline equation glyph defs from main SVG:
  - `s2-eq-g0-118` ... `s2-eq-g6-1`
- Kept those defs inside `assets/symbol-s2-eq.svg` only.

### 7) Validation procedures used throughout
- XML/diagnostics check for edited SVG files (no errors reported).
- Presence/absence checks for key IDs and links.
- File-size checks after each major phase.
- Diff stats checks to quantify deletions/additions.

## Size progression observed
- After grid removal phase: main SVG reduced substantially.
- After symbol externalization: main SVG reduced further.
- Main SVG size before SVGO pass in latest state: `51205` bytes.

## Conservative SVGO pass (latest)
A conservative SVGO pass was run with the following plugin set:
- `removeDoctype`
- `removeXMLProcInst`
- `removeComments`
- `removeMetadata`
- `removeEditorsNSData`

Result:
- Main SVG size changed from `51205` bytes to `48878` bytes.

Render-equivalence check performed:
- Rasterized before and after with Inkscape.
- Compared rasters using ImageMagick `compare -metric AE`.
- Output was non-zero:
  - `RENDER_AE=1.35769e+06 (0.0672113)`
  - `RENDER_IDENTICAL=no`

Interpretation:
- This SVGO pass reduced size but did **not** preserve pixel-identical rendering under the validation method used.

### 8) Asset viewBox refit (2026-10-08)
The extracted symbols had hand-guessed viewBoxes, so several rendered wrongly: `path599` (USYD crest) was clipped to its top third, `s5-icon-brain-path3420` was invisible (its content sat at x~4425, outside a -8..8 viewBox), and `s2-eq` lost its trailing *v*. Inkscape also rasterizes an SVG linked through `<image>` at the linked file's intrinsic size (it did so even in PDF export), so the QR (37 px) and equation (125 px) printed blurred.

Fix, applied to every `assets/*.svg`:
- viewBox = measured content bbox (`inkscape --query-all`) plus 2% padding.
- The poster's `<image>` x/y/width/height = that viewBox exactly (identity mapping, so nothing can clip).
- Root `width`/`height` = viewBox x K, with K chosen so the asset rasterizes at ~800 ppi at its printed size.

Validation: full-poster render vs the all-inline git HEAD differs in 0.007% of pixels (edge antialiasing only); every symbol embeds at 800-860 ppi in Inkscape PDF export. This also shows the conservative SVGO pass causes no visible change. Backups are in the session scratchpad.

## Current status snapshot
- `SfN_2026.svg` and `assets/` render equivalently to the inline original.
- Export with `resvg` (`~/.cargo/bin/resvg -w 5344 --background white SfN_2026.svg SfN_2026.png`, run from the repo root): it draws linked SVGs as vectors. Inkscape and `rsvg-convert` rasterize them (Inkscape put the figures at 33-47 ppi). Details in `figures/PROVENANCE.md`.
- Section 3 (2026-10-08): top row is now (a) brain, (b) raster, (c) covariance at equal widths; the noise-baseline box uses the new vector `figures/src/nugget_poster.svg` (karl: `_research/neuropixels_nugget/nugfig_poster.jl`), drawn at Fig3's scale so fonts and strokes match; results relabelled (f)-(h).
- Section 4 (2026-10-08): the dashed schematic placeholder is replaced by `s4-schematic` (`figures/src/phantom_poster.svg`, karl: `_research/phantom_correlated/phfig_poster.jl`): test, redundancy and noise traces with their equations, at k = 2.853.
- Section 1 (2026-11-03): the cameras figure is replaced by `s1-construction` (`figures/src/construction_poster.svg`, 900 x 1050 at scale 1, placed at 110,1050; made by `drafts/opening/make_1f.py`): drifting gratings and the gray screen each driving a sheet of cells, and the stimulus-engaged set below. The caption box moved to the right of the figure; `drafts/opening/link_construction.py` holds the caption text and rewraps it with the installed Source Sans 3. The other opening drafts and their notes are in `drafts/opening/`.
