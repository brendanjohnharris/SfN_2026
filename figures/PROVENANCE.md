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
4. Check, and refresh the repo's preview: `inkscape SfN_2026.svg --export-width=5344 --export-background=white --export-filename=SfN_2026.png`.

## Poster elements

| Poster element(s) | Local file | Original | Made by |
|---|---|---|---|
| `s1-cameras` (col 1, cameras), `s2-baselines` (col 1, baselines) | `figures/src/Fig1_schematic.svg` | `LAB/plots/Fig1_schematic.svg` | `LAB/scripts/Fig1_schematic.jl` |
| `s3-cards` (col 2, spiking cards + covariance, beside the brain) | `figures/src/trial_stack_covariance.svg` | `LAB/plots/trial_stack_covariance.svg` | `LAB/AllenNeuropixelsLab/scripts/trial_stack_covariance.jl` |
| `s3-results` (col 2, decoding), `s4-results` (col 3, phantom oscillations) | `figures/src/Fig3_case_studies.svg` | `LAB/plots/Fig3_case_studies.svg` | `LAB/scripts/Fig3_case_studies.jl` (data: `LAB/scripts/calculations/neuropixels_data.jl`, `phantom_oscillations.jl`) |
| `s3-nugget-left`, `s3-nugget-right` (col 2, noise-baseline box) | `figures/linked/s3-nugget-{left,right}-<sha1>.png` (crops of `figures/src/nugget_construction.png`) | `LAB/_research/neuropixels_nugget/nugget_construction.png` | `LAB/_research/neuropixels_nugget/nugfig.jl` |
| `s3-brain` (col 2, glass brain) | `figures/src/brain.png` | `DDC/WorkingRegime.jl/assets/brain.png`, itself a copy of `GlassBrain.jl/plots/fig1a_crystal_white_nostreams_transparent.png` | `GlassBrain.jl/scripts/fig1a.jl` (GPU) |

### Crops and covers (current values)

| Element | `data-crop` (x y w h) | Cover rects |
|---|---|---|
| `s1-cameras` | `208 30 472 270` | 3, over the source's (c), (d), (e); the poster draws its own (a)–(c) (label (a) nudged 14 px left, as the source's (c) abuts its title) |
| `s2-baselines` | `42 330 630 382` | 5, over (f)–(j) (fill `#f5f5f5` in the grey boxes, white otherwise); the poster draws its own (a)–(e) |
| `s3-results` | `168 16 552 246` | 1, over the source's row title |
| `s4-results` | `163 548 557 252` | 2, over the row title and a stray letter |
| `s3-cards` | `36 13 382 161` | none (the figure's outer whitespace is clipped) |

Each group holds `<g transform="matrix(k,0,0,k,tx,ty)"><image href=... width/height = source size>`
under a `clipPath` rect in poster units; `k = min(slot w / crop w, slot h / crop h)`, the crop is centred in
the slot, and `tx = X0 - crop_x * k`. Cover rect = source letter bbox padded by ~1 unit; the poster label
uses font size `1.026 * letter height * k`, x = letter left, baseline = letter bottom - `0.19 * letter height * k`.
The Fig1 slots are `s1-cameras` 160.5,1053.6,1460x779 and `s2-baselines` 150.5,2421.2,1480x813 (poster units).

### Per-source notes

- **Fig1_schematic** (720 x 731). Generated on karl, by the script above (layout notes in its header).
  The poster uses quadrants (c–e) and (f–j). Current copy rendered 2026-10-07 23:18 from the uncommitted
  working copy of the script (on top of commit `acf6da0`). The CairoMakie warning that `trail` is not supported is benign; the trails render.
- **trial_stack_covariance** (430 x 200). Session 794812542 (the decoding case study's example; 537
  units), three drifting-grating presentations (ids 40938, 40759, 40748: 90°, 0°, 45°), the 120
  most-driven units. The covariance is `cov` of trial-mean rates (centred, as in the analysis).
  Source data are written to `LAB/plots/trial_stack_covariance/`. Set `CANDIDATES = true` to redraw
  the grid used to choose the trials.
- **Fig3_case_studies** (720 x 810). Row 1 is the Neuropixels decoding (`s3-results`), and row 3
  the phantom oscillations (`s4-results`). The headline numbers are in `LAB/plots/Fig3_case_studies/`
  (`panelD_decoding.tsv`, `panelJ_pc1_correlations.tsv`).
- **nugget_construction** (2900 x 840). Made with
  `julia +1.12 -t auto --project=$HOME/code/BaselinePCALab.jl nugfig.jl`. **Its `wsave` path still points
  at a deleted job scratch dir** (`/suphys/bhar9988/.claude/jobs/04413cc2/tmp/`); edit it to
  `_research/neuropixels_nugget/` before rerunning. The poster uses two raster crops of it (PIL
  boxes `left 0,112,960,648` and `right 1930,112,970,648`, as `x,y,w,h` in source pixels), saved as
  `figures/linked/<id>-<first 8 hex of sha1(png bytes)>.png`. To refresh: re-crop with PIL, write
  the new hashed name, and update the two `<image>` hrefs.
- **brain.png** (1600 x 1600 RGBA). Rendered on `nodegpu02` (L40S) with
  `cd ~/code/GlassBrain.jl/scripts && bash fig1a.jl crystal white 1052342277 nostreams transparent`
  (Visual Behavior session 1052342277, six probes), then copied to `WorkingRegime.jl/assets/brain.png`.
  Placed unmirrored via a scaled group (`matrix(0.524836,0,0,0.524836,1830.998,972.909)`), so it
  matches WorkingRegime Fig. 1. GlassBrain.jl was not committed at render time.

### Unplaced files in `figures/src/`

`Fig1_schematics_bpca.svg` (three-matrix pipeline schematic) and `phantom_construction.{svg,png}`
(`LAB/_research/phantom_correlated/`, made by `phfig2.jl`) were copied as candidate schematics;
they are not on the poster. `Fig1_schematic.png` and `Fig3_case_studies.png` are reference rasters
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
