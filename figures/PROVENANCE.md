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
   (`resvg` 0.48, from `cargo install resvg`, in `~/.cargo/bin`). Use `-w 16700` for a 300 dpi print raster.
   Do not export with Inkscape or `rsvg-convert`: both rasterize every SVG linked through `<image>`
   (Inkscape at the linked file's own pixel size, which put the figures at 33-47 ppi), whereas `resvg`
   draws them as vectors. Render from the repo root, or the relative links will not resolve.

## Poster elements

| Poster element(s) | Local file | Original | Made by |
|---|---|---|---|
| `s1-construction` (col 1, gratings / gray screen / stimulus-engaged sheets) | `figures/src/construction_poster.svg` | made in this repo | `drafts/opening/make_1f.py` (`option1f_vertical`), linked by `drafts/opening/link_construction.py` |
| `s2-baselines` (col 1, baselines) | `figures/src/Fig1_schematic.svg` | `LAB/plots/Fig1_schematic.svg` | `LAB/scripts/Fig1_schematic.jl` |
| `s3-raster`, `s3-cov` (col 2, panels (b) and (c), beside the brain) | `figures/src/trial_stack_covariance.svg` | `LAB/plots/trial_stack_covariance.svg` | `LAB/AllenNeuropixelsLab/scripts/trial_stack_covariance.jl` |
| `s3-results` (col 2, decoding), `s4-results` (col 3, phantom oscillations) | `figures/src/Fig3_case_studies.svg` | `LAB/plots/Fig3_case_studies.svg` | `LAB/scripts/Fig3_case_studies.jl` (data: `LAB/scripts/calculations/neuropixels_data.jl`, `phantom_oscillations.jl`) |
| `s3-noise` (col 2, noise-baseline box, panels (d) and (e)) | `figures/src/nugget_poster.svg` | `LAB/_research/neuropixels_nugget/nugget_poster.svg` | `LAB/_research/neuropixels_nugget/nugfig_poster.jl` (source data in `nugget_poster/`) |
| `s4-schematic` (col 3, test / redundancy / noise baselines, above the results) | `figures/src/phantom_poster.svg` | `LAB/_research/phantom_correlated/phantom_poster.svg` | `LAB/_research/phantom_correlated/phfig_poster.jl` (source data in `phantom_poster/`) |
| `s3-brain` (col 2, glass brain) | `figures/src/brain.png` | `DDC/WorkingRegime.jl/assets/brain.png`, itself a copy of `GlassBrain.jl/plots/fig1a_crystal_white_nostreams_transparent.png` | `GlassBrain.jl/scripts/fig1a.jl` (GPU) |

### Crops and covers (current values)

| Element | `data-crop` (x y w h) | Cover rects |
|---|---|---|
| `s1-construction` | `0 0 900 1050` (the whole file, at scale 1, placed at 110,1050) | none; the figure carries its own (a)–(c) |
| `s2-baselines` | `42 330 630 382` | 5, over (f)–(j) (fill `#f5f5f5` in the grey boxes, white otherwise); the poster draws its own (a)–(e) |
| `s3-results` | `168 16 552 246` | 1, over the source's row title |
| `s4-results` | `163 548 557 252` | 2, over the row title and a stray letter |
| `s3-raster` | `37.75 14.75 183.75 143.75` | none |
| `s3-cov` | `263.75 22 152.25 151` | none |

Each group holds `<g transform="matrix(k,0,0,k,tx,ty)"><image href=... width/height = source size>`
under a `clipPath` rect in poster units; `k = min(slot w / crop w, slot h / crop h)`, the crop is centred in
the slot, and `tx = X0 - crop_x * k`. Cover rect = source letter bbox padded by ~1 unit; the poster label
uses font size `1.026 * letter height * k`, x = letter left, baseline = letter bottom - `0.19 * letter height * k`.
The Fig1 slots are `s1-cameras` 160.5,1053.6,1460x779 and `s2-baselines` 150.5,2421.2,1480x813 (poster units).

### Per-source notes

- **construction_poster** (900 x 1050, poster units). Drawn by `drafts/opening/make_1f.py`
  (`python3 make_1f.py` from `drafts/opening/`; the same script writes the wide draft
  `drafts/opening/option1f-construction.svg`). A 36-cell population on an oblique sheet (shear 0.3,
  foreshortening 0.72), with a nine-cell spontaneous group and a five-cell grating-driven group that
  share two cells; links join each active cell to its nearest active neighbours. Group memberships
  are grid coordinates in `population()`. The Section 1 caption box sits to the right of the figure
  (`s1-caption-box`, 1040,1050, 638 x 1050); `drafts/opening/link_construction.py` made the swap from
  the cameras figure and holds the caption text. Fonts: Source Sans 3, panel labels 42 px.
- **Fig1_schematic** (720 x 731). Generated on karl, by the script above (layout notes in its header).
  The poster uses quadrant (f–j) in Section 2; quadrant (c–e), the cameras, was the Section 1 figure
  until 2026-11-03 (`s1-cameras`, crop `208 30 472 270`, three cover rects). Current copy rendered 2026-10-07 23:18 from the uncommitted
  working copy of the script (on top of commit `acf6da0`). The CairoMakie warning that `trail` is not supported is benign; the trails render.
- **Section 3 layout.** Every figure in column 2 is drawn at Fig3's scale, k = 2.853 poster units per
  figure unit, so fonts and strokes agree across panels. Row 1 is (a) brain, (b) raster, (c) covariance,
  each ~520 units wide with 42 px semibold `(x) Title` labels (`s3-row-label-*`); the brain is scaled so
  its content box (`141,209,1364,1067` px of brain.png) is 517 units wide. The noise box holds (d), (e)
  (`s3-noise-label-*`) and the results are (f)-(h). The layout was set by a one-off script; re-derive
  positions from the element coordinates if anything moves.
- **nugget_poster** (535 x 189, transparent background). Sized to its poster slot at k = 2.853 and
  styled with Fig3's theme and constants (`fathom(:physics)`, markersize 6, linewidth 2), with the noise
  elements in bermejo, the poster's noise-baseline colour. Same session as the decoding example (537
  units); median floor fraction 0.249. Run as `julia +1.12 -t auto --project=. _research/neuropixels_nugget/nugfig_poster.jl` (~2 min).
- **phantom_poster** (542 x 196, transparent). Fills the old `s4-placeholder` slot at k = 2.853. It
  rebuilds the case study's representative draw (seed 94, asserted equal to the saved `X6`) by
  evaluating `scripts/calculations/phantom_oscillations.jl` up to its "Representative realization"
  block in a fresh module, so it follows any change to the simulation. It draws the first second of
  series 1 in two rows sharing one amplitude scale. Top, the generative pieces: the chaotic latent
  s(t), the 1/f background b_i(t) (the reading minus a_i s and the artefact) and the noise floor
  sigma c(t). Bottom, what bPCA is given: the test data (both readings), an IAAFT surrogate
  (redundancy, poster blue `#3f6fd1`) and the reading difference (noise; asserted equal to
  sigma (c1 - c2)). Source data: `phantom_poster/series1.tsv`. Run as
  `julia +1.12 -t auto --project=. _research/phantom_correlated/phfig_poster.jl` (~1.5 min).
- **trial_stack_covariance** (430 x 200). Session 794812542 (the decoding case study's example; 537
  units), three drifting-grating presentations (ids 40938, 40759, 40748: 90°, 0°, 45°), the 120
  most-driven units. The covariance is `cov` of trial-mean rates (centred, as in the analysis).
  Source data are written to `LAB/plots/trial_stack_covariance/`. Set `CANDIDATES = true` to redraw
  the grid used to choose the trials.
- **Fig3_case_studies** (720 x 810). Row 1 is the Neuropixels decoding (`s3-results`), and row 3
  the phantom oscillations (`s4-results`). The headline numbers are in `LAB/plots/Fig3_case_studies/`
  (`panelD_decoding.tsv`, `panelJ_pc1_correlations.tsv`).
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
