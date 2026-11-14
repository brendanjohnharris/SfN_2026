# Figure provenance

Where every graphic in `SfN_2026.svg` comes from, and how to refresh it. Paths on karl are given
relative to `karl:~/code` (= `/import/taiji1/bhar9988/code`, also reachable as `/suphys/bhar9988/code`).
`LAB` = `BaselinePCALab.jl`.

## Refreshing figures

1. Regenerate on karl if the generating script has changed since its output (compare mtimes:
   `ls -l --time-style=long-iso LAB/scripts/<script>.jl LAB/plots/<name>.svg`). Most scripts are not
   executable; run them as `cd ~/code/BaselinePCALab.jl && julia +1.12 -t auto --project=. scripts/<script>.jl`.
2. `figures/fetch_figures.sh -n` lists which local copies differ from karl; `figures/fetch_figures.sh`
   copies them all into `figures/src/`.
3. Linked SVGs update in the poster automatically, but each slot shows a hand-set crop of the source
   (the group's `data-crop="x y w h"`, in source-figure units), sometimes with white `*-cover-N` rects
   hiding the source's own panel letters. If the source layout moved, re-derive the crop and covers,
   then re-render the poster and look (step 4).
4. Check, and refresh the repo's preview: `resvg -w 5344 --background white SfN_2026.svg SfN_2026.png`
   (`resvg` 0.49, from `cargo install resvg`, in `~/.cargo/bin`; the GitHub binary needs glibc 2.35, newer than
   karl's). Use `-w 16700` for a 300 dpi print raster. It needs Source Sans 3 on the font path: on karl the TeX
   Live copy is linked at `~/.local/share/fonts/sourcesans`.
   Do not export with Inkscape or `rsvg-convert`: both rasterize every SVG linked through `<image>`
   (Inkscape at the linked file's own pixel size, which put the figures at 33-47 ppi), whereas `resvg`
   draws them as vectors. Render from the repo root, or the relative links will not resolve.

## Poster elements

| Poster element(s) | Local file | Original | Made by |
|---|---|---|---|
| `s1-construction` (col 1, gratings / gray screen / stimulus-engaged sheets) | `figures/src/construction_poster.svg` | made in this repo | `drafts/opening/make_1f.py` (`option1f_vertical`), linked by `drafts/opening/link_construction.py` |
| `s2-baselines` (col 1, baselines (a)-(c); the eigenspectra (i), (j) were dropped on 2026-11-06) | `figures/src/Fig1_schematic.svg` | `LAB/plots/Fig1_schematic.svg` | `LAB/scripts/Fig1_schematic.jl`; cropped by `figures/relink_case_studies.py` |
| `s3-raster`, `s3-cov` (col 2, panels (b) and (c), beside the brain) | `figures/src/trial_stack_covariance.svg` | `LAB/plots/trial_stack_covariance.svg` | `LAB/AllenNeuropixelsLab/scripts/trial_stack_covariance.jl` |
| `s3-results` (col 2, decoding) | `figures/src/Fig3_case_studies.svg` | `LAB/plots/Fig3_case_studies.svg` | `LAB/scripts/Fig3_case_studies.jl` (data: `LAB/scripts/calculations/neuropixels_data.jl` at 10% contrast); placed by `figures/relink_case_studies.py` |
| `s4-results` (col 3, phantom results: traces beside the principal value spectrum, caption in a full-width box below) | `figures/src/phantom_results_poster.svg` (+ `_layout.tsv`) | `LAB/_research/phantom_correlated/phantom_results_poster.svg` | `LAB/_research/phantom_correlated/phfig_results_poster.jl`, from `LAB/plots/Fig3_case_studies/panel{J,K}_*.tsv` and `data/phantom_oscillations.jld2` |
| `s3-noise` (col 2, noise-baseline box, panels (d) and (e)) | `figures/src/noise_poster.svg` (+ `_layout.tsv`) | `LAB/_research/neuropixels_nugget/noise_poster.svg` | `LAB/_research/neuropixels_nugget/noisefig_poster.jl` (no source data) |
| `s4-schematic` (col 3, test / redundancy / noise baselines, above the results) | `figures/src/phantom_poster.svg` | `LAB/_research/phantom_correlated/phantom_poster.svg` | `LAB/_research/phantom_correlated/phfig_poster.jl` (source data in `phantom_poster/`) |
| `s3-brain` (col 2, glass brain) | `figures/src/brain.png` | `DDC/WorkingRegime.jl/assets/brain.png`, itself a copy of `GlassBrain.jl/plots/fig1a_crystal_white_nostreams_transparent.png` | `GlassBrain.jl/scripts/fig1a.jl` (GPU) |

### Crops and covers (current values)

| Element | `data-crop` (x y w h) | Cover rects |
|---|---|---|
| `s1-construction` | `0 0 900 1050` (the whole file, at scale 1, placed at 110,1050) | none; the figure carries its own (a)–(c) |
| `s2-baselines` | `50.75 315 439.5 321` (tight to the panel boxes of the 720 x 665 Fig1) | 3, over (f)–(h) (each in its panel's tint); the poster draws its own (a)–(c); since 2026-11-08 at the left of the section at k = 2.12, beside the conditions box (equations `assets/symbol-s2-cond-*.svg` from `figures/make_s2_equations.py`), with the cPCA box and the solution chain (noise-corrected generalized eigenvalue problem, then symmetric orthogonalization; `assets/symbol-s2-eq.svg`, same script) across the bottom (`layout_s2` in `figures/relink_case_studies.py`) |
| `s3-results` | `172 14 541 215` | 1, over the row's panel titles |
| `s4-results` | whole file (667 x 268) at 3666,1700, k = 2.36 | none; the poster's (a), (b) follow `phantom_results_poster_layout.tsv`, the caption box sits 25 below the figure |
| `s3-noise` | whole file (535 x 189) at 1909.5,1724.8, k = 2.853 | none; the poster's (d), (e) follow `noise_poster_layout.tsv` |
| `s3-raster` | `37.75 14.75 183.75 143.75` | none |
| `s3-cov` | `263.75 22 152.25 151` | none |

Section 4 is at k = 2.36 (`K4` in `relink_case_studies.py`), schematic and results alike.
Each group holds `<g transform="matrix(k,0,0,k,tx,ty)"><image href=... width/height = source size>`
under a `clipPath` rect in poster units; `k = min(slot w / crop w, slot h / crop h)`, the crop is centred in
the slot, and `tx = X0 - crop_x * k`. Cover rect = source letter bbox padded by ~1 unit; the poster label
uses font size `1.026 * letter height * k`, x = letter left, baseline = letter bottom - `0.19 * letter height * k`.
The Fig1 slots are `s1-cameras` 160.5,1053.6,1460x779 and `s2-baselines` 150.5,2421.2,1480x813 (poster units).

### Per-source notes

- **construction_poster** (900 x 1050, poster units). Drawn by `drafts/opening/make_1f.py`
  (`python3 make_1f.py` from `drafts/opening/`; the same script writes the wide draft
  `drafts/opening/option1f-construction.svg`). A 36-cell population on an oblique sheet (shear 0.3,
  foreshortening 0.72), with a nine-cell background group (gray) and one two- or three-cell
  subnetwork per grating direction (coloured as in Section 3; a cell in two subnetworks gets the mean
  colour, and three of them also belong to the background group); links join each active cell to its
  nearest active neighbours, in the blend of their ends. Memberships are grid coordinates in
  `population()`. Since 2026-11-06 the gray-screen sheet is gray too, the shared-input traces and their tags are
  gone, and the only annotations are the panel titles, the direction labels, "Redundant links"
  (blue) and a bare "?" arrow; the caption carries the rest. The Section 1 caption box sits to the right of the figure
  (`s1-caption-box`, 1040,1050, 638 x 1050); `drafts/opening/link_construction.py` made the swap from
  the cameras figure and holds the caption text. Fonts: Source Sans 3, panel labels 42 px.
- **Fig1_schematic** (720 x 665 since the 2026-10-31 render, pulled 2026-11-08; was 720 x 731). Panels (f) and (g) are now tinted in their baselines' colours. Generated on karl, by the script above (layout notes in its header).
  The poster uses quadrant (f–j) in Section 2; quadrant (c–e), the cameras, was the Section 1 figure
  until 2026-11-03 (`s1-cameras`, crop `208 30 472 270`, three cover rects). Current copy rendered 2026-10-07 23:18 from the uncommitted
  working copy of the script (on top of commit `acf6da0`). The CairoMakie warning that `trail` is not supported is benign; the trails render.
- **Section 3 layout.** Every figure in column 2 is drawn at Fig3's scale, k = 2.853 poster units per
  figure unit, so fonts and strokes agree across panels. Row 1 is (a) brain, (b) raster, (c) covariance,
  each ~520 units wide with 42 px semibold `(x) Title` labels (`s3-row-label-*`); the brain is scaled so
  its content box (`141,209,1364,1067` px of brain.png) is 517 units wide. The noise box holds (d), (e)
  (`s3-noise-label-*`) and the results are (f)-(h). The layout was set by a one-off script; re-derive
  positions from the element coordinates if anything moves.
- **noise_poster** (535 x 189, transparent background; replaced `nugget_poster` on 2026-11-06 when the
  noise floor became `spontaneous_noise`). A schematic, not data: one synthetic smooth series (random
  sinusoids plus small white fluctuations, `Xoshiro(3)`, black) with an 80 ms window marked; below it the
  window zoomed, so the trend (dashed) is flat and only the fluctuations around it remain, in red; and an
  arrow from them to a cartoon diagonal-dominant covariance across units at the right. Sized to its
  poster slot at k = 2.853 and styled with Fig3's theme, the noise elements in bermejo. Writes
  `noise_poster_layout.tsv` (axis boxes, figure units, y down) for the poster's letters. The caption's
  median floor fraction (0.232, example session) comes from the earlier data-driven version. Run as
  `julia +1.13 -t auto --project=. _research/neuropixels_nugget/noisefig_poster.jl` (~1 min).
- **phantom_results_poster** (667 x 407, transparent). Fig3's row 2 redrawn for the column: the three
  traces (`panelJ_recovered_latent.tsv`, plain lines rather than Fig3's `kinetic!`) across the top, the
  held-out eigenspectra (`panelK_eigenspectra.tsv`, medians) over the loading attribution
  (`panelL_loadings.tsv`) at the right (52% of the width), and an empty bottom-left cell that the poster
  fills with the caption box. ρ values from `phantom_oscillations.jld2`. Writes
  `phantom_results_poster_layout.tsv`. Run as
  `julia +1.13 -t auto --project=. _research/phantom_correlated/phfig_results_poster.jl` (~1 min).
- **phantom_poster** (660 x 239, transparent). Fills the `s4-schematic` slot (1545 x 560) at k = 2.36,
  Section 4's scale. It rebuilds the case study's representative draw (seed 49, asserted equal to the saved
  `X6` and `c_true`) by evaluating `scripts/calculations/phantom_oscillations.jl` up to its "Representative
  realization" block in a fresh module, then replays that function's RNG stream to recover the pieces it
  sums (the 1/f backgrounds and the couplings), so it follows any change to the simulation. It draws the
  first second of series 1 in two rows sharing one amplitude scale. Top, the generative pieces: the chaotic
  latent s(t), the 1/f background b_i(t) and the instrument artefact g_i c(t). Bottom, what bPCA is given:
  the test data x_i, an IAAFT surrogate (redundancy, poster blue `#3f6fd1`) and the calibration record
  x_i^cal = g'_i c (noise: the artefact through a fresh coupling, no subject). Source data:
  `phantom_poster/series1.tsv`. Run as `julia +1.13 -t auto --project=. _research/phantom_correlated/phfig_poster.jl` (~1.5 min).
- **trial_stack_covariance** (430 x 200). Session 794812542 (the decoding case study's example; 537
  units), three drifting-grating presentations (ids 40938, 40759, 40748: 90°, 0°, 45°), the 120
  most-driven units. The covariance is `cov` of trial-mean rates (centred, as in the analysis).
  Source data are written to `LAB/plots/trial_stack_covariance/`. Set `CANDIDATES = true` to redraw
  the grid used to choose the trials.
- **Fig3_case_studies** (720 x 730 since 2026-10-31; rows neuropixels / phantom / genomics). Row 1 is
  the Neuropixels decoding (`s3-results`: panels (b)-(d), the brain schematic (a) being the poster's own);
  row 2 (phantom) is not cropped but redrawn as `phantom_results_poster`. Its row bubbles are tinted, so
  the crop carries a faint tinted rectangle. The headline numbers are in
  `LAB/plots/Fig3_case_studies/` (`panelD_decoding.tsv`, `panelJ_pc1_correlations.tsv`). The ids on the
  poster are relinked by `figures/relink_case_studies.py`, which also rewrites the Section 3 and 4 text
  (numbers at its top) and wraps it with the installed Source Sans 3.
- **nugget_construction** (2900 x 840). No longer on the poster (replaced by `nugget_poster`); the
  `figures/linked/s3-nugget-*` crops are unused. Made with
  `julia +1.12 -t auto --project=$HOME/code/BaselinePCALab.jl nugfig.jl`. **Its `wsave` path still points
  at a deleted job scratch dir** (`/suphys/bhar9988/.claude/jobs/04413cc2/tmp/`); edit it to
  `_research/neuropixels_nugget/` before rerunning. The poster uses two raster crops of it (PIL
  boxes `left 0,112,960,648` and `right 1930,112,970,648`, as `x,y,w,h` in source pixels), saved as
  `figures/linked/<id>-<first 8 hex of sha1(png bytes)>.png`. To refresh: re-crop with PIL, write
  the new hashed name, and update the two `<image>` hrefs.
- **brain.png** (1600 x 1600 RGBA). Rendered on `nodegpu02` (L40S) with
  `cd ~/code/GlassBrain.jl/scripts && bash fig1a.jl crystal white 1052342277 nostreams transparent`
  (Visual Behavior session 1052342277, six probes), then copied to `WorkingRegime.jl/assets/brain.png`.
  Placed unmirrored via a scaled group (see Section 3 layout above), so it matches WorkingRegime Fig. 1. GlassBrain.jl was not committed at render time.

### Unplaced files in `figures/src/`

`Fig1_schematics_bpca.svg` (three-matrix pipeline schematic) and `phantom_construction.{svg,png}`
(`LAB/_research/phantom_correlated/`, made by `phfig2.jl`) were copied as candidate schematics;
they are not on the poster (section 4 uses `phantom_poster` instead). `Fig1_schematic.png` and `Fig3_case_studies.png` are reference rasters
(the cover-rect colours were sampled from them).

## Inline vector graphics (no external file)

- **`s2-eq`** (bPCA equation). LaTeX `standalone` with `amsmath,bm,xcolor`; colours
  `rb = #3F6FD1`, `nb = #F93D53`; body
  `\left(\Sigma^2-\textcolor{nb}{\Sigma^2_n}\right)\bm{v}=\lambda\left(\textcolor{rb}{\Sigma^2_r}-\textcolor{nb}{\Sigma^2_n}\right)\bm{v}`.
  Built with `latex s2-eq.tex && dvisvgm --no-fonts --exact-bbox -o s2-eq.svg s2-eq.dvi`, then
  inlined with ids prefixed `s2-eq-`.
- **`qr`**: `qrencode -t SVG -l H -m 0 --svg-path -o - 'https://github.com/brendanjohnharris/SfN_2026'`,
  recoloured `#26282f`.
- **Icons**: `s1-icon-red`, `s1-icon-noise`, `s5-icon-wave` and `s5-icon-pose` are hand-written paths;
  `s5-icon-brain` comes from the COSYNE 2025 template; `icon-email` is hand-drawn; `icon-github` is the
  Simple Icons GitHub mark.

## Not kept

The original build scripts (`build_poster.py`, `edit_header.py` and the linking heredoc) lived in a
session scratchpad and are gone. Their logic is summarised above. The 2026-10-04 poster session
transcript (`~/.claude/projects/-home-brendan-Documents-SfN-2026/dd149d25-*.jsonl`) holds them in
full if they need rebuilding.
