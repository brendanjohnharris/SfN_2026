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
- Section 1 (2026-11-03): the cameras figure is replaced by `s1-construction` (`figures/src/construction_poster.svg`, 900 x 1050 at scale 1, placed at 110,1050; made by `drafts/opening/make_1f.py`): drifting gratings and the gray screen each driving a sheet of cells, and the stimulus-engaged set below (2026-11-06: subnetworks coloured by direction, blended where shared, background network gray; shared-input traces and most tags removed). The caption box moved to the right of the figure; `drafts/opening/link_construction.py` holds the caption text and rewraps it with the installed Source Sans 3. The other opening drafts and their notes are in `drafts/opening/`.
- Sections 3 and 4 (2026-11-06): relinked to the late-October case studies by `figures/relink_case_studies.py` (rerun it after refetching `Fig3_case_studies.svg`; it holds the crops, the Section 4 scale k = 2.36 and the quoted numbers). Neuropixels: 10% contrast gratings, Gaussian feature gate, noise baseline = `spontaneous_noise` (half the covariance of successive differences of 10 ms spontaneous counts), shown in the noise box by `figures/src/noise_poster.svg` (`_research/neuropixels_nugget/noisefig_poster.jl`); decoding 32° to 9°, chance 56°. Phantom: noise baseline = a calibration recording (artefact through fresh couplings, no subject), schematic `figures/src/phantom_poster.svg` regenerated at k = 2.36 (660 x 239); held-out eigenspectra; bPC1 r = 0.88, loadings r = 0.94 / 0.04; results are two crops of Fig3 row 2 (`s4-traces`, `s4-results`).
- Sections 2-4 (2026-11-06, second pass): Section 2 shows only Fig1's (a)-(c) (the dilution/ablation eigenspectra are cropped out). The Section 3 noise box is a synthetic schematic: smooth series, a window zoomed to show fast fluctuations around the trend, and a cartoon diagonal-dominant covariance (no data). Section 4's results are a poster-specific redraw (`figures/src/phantom_results_poster.svg`, `_research/phantom_correlated/phfig_results_poster.jl`): traces across the top at 1700-1945, eigenspectra over loadings at the right, the caption box in the empty bottom-left cell. Both poster figures write a `*_layout.tsv` that `figures/relink_case_studies.py` uses to place the panel letters and the caption.
- Section 2 (2026-11-08): relaid out by `layout_s2` in `figures/relink_case_studies.py`: Fig1's (a)-(c), cropped tight to the panel boxes, at the left (k = 2.12) and the equation box beside it at the same height; the "Why not contrastive PCA?" box (now 40 px, like the other dark-bar boxes) across the bottom; the spare height split into three equal gaps. The four dark-bar titles were set in Arial, which karl lacks, so resvg drew them blank; the script now sets them in Source Sans 3. Fig1 was refreshed the same day to karl's 2026-10-31 render (720 x 665, tinted (f)/(g); `plots/` is gitignored, so GitHub has only `scripts/Fig1_schematic.jl`); the crop, letters and covers are crop-relative constants in the script (`S2_CROP`, `S2_LETTERS`, `S2_COVERS`), and the linked size follows the file's viewBox. The relink is idempotent (a second run changes nothing), so rerun it on the current poster, then `drafts/opening/link_construction.py`, then resvg.
- Section 2 (2026-11-08, later): the box beside the figure now shows the manuscript's three bPCA conditions (BaselinePCA.tex `origin/main`, main.tex Methods: redundancy baseline white, noise baseline zero, test data diagonal), each labelled with the panel that draws it; the equations are `assets/symbol-s2-cond-{r,n,t}.svg`, rendered by `figures/make_s2_equations.py` (LaTeX + dvisvgm). The generalized eigenvalue problem (`assets/symbol-s2-eq.svg`) moved to the full-width "Why not contrastive PCA?" box, between the ratio-methods text and the eigenvalue reading. Box texts are constants in `figures/relink_case_studies.py` (`S2_LEAD`, `S2_CONDS`, `S2_WHY`, `S2_EIG`).
- Section 2 (2026-11-08, last): the "Why not contrastive PCA?" box now shows bPCA's solution as a two-step chain (main.tex Methods): the noise-corrected generalized eigenvalue problem, then the symmetric orthogonalization P = V (V^T Σ² V)^{-1/2} σ̂₊. `assets/symbol-s2-eq.svg` is now rendered by `figures/make_s2_equations.py` (key `eq`) instead of being the hand-extracted original; the box prose was shortened to fit (gaps 56).
- Captions (2026-11-08): rewritten to match the current figures. Section 1 (`link_construction.py`): subnetworks over a gray background network, gray screen = redundant links, (c) what remains. Section 4 (`relink_case_studies.py`): chaotic latent, ρ as in the figure, bPCA eigenvalues at baseline by component 3, no "Above:". Summary `text1315` is now set by the relink from the decoding numbers.
- Text pass (2026-11-08): Brendan's edits to the emailed markdown (`.claude/docs/SfN_2026_poster_text.md`) applied. Texts that lived only in the SVG (`text1204`, `text1207`, `text1225`, `text1260`, `text1295`, `text1312`, the Section 2 subtitle and box title) are now set by `figures/relink_case_studies.py` (`TEXTS`, `TITLES`, `S2_INTRO`), so the poster text has one source; Section 1's caption stays in `link_construction.py`. Section 2 tightened to k = 2.02, gaps 21.
- Section 2 (2026-11-08, bullets): the "Other contrastive methods" box lists subtractive and ratio methods as bullets with − and ÷ as their icons (`S2_BULLETS`), the box body now at 36 px like the Section 3 noise box. `layout_s2` now measures the available height from the intro's actual foot (it used a fixed top edge, stale once the intro grew); minimum gap 20, condition spacing 10/22; k = 1.92.
- Caption pass (2026-11-08): each subcaption ((a), (b), ...) starts a new line in every caption box; a `\n` inside a run forces the break (`wrap` in both `relink_case_studies.py` and `link_construction.py`). The Section 2 intro is a lead line plus one swatch bullet per baseline (`S2_BASES`, Section 3's swatch style; k = 1.82, gaps 29). Section 3: intro and closing text one line shorter (the intro box hugs its text, bullets moved up half the saving), the results caption and callout boxes size to the caption. The noise box drops the "Zoom" title and the top trace's background and baseline (`noisefig_poster.jl`), and its label is just "(d)". Reference 7 (Cunningham & Yu 2014) added, cited in Section 1 for PCA on population activity. `retext` now escapes `&`/`<` and reads each element's line height (the references use 1.27).
- References (2026-11-08): numbered by first citation in reading order (Cunningham & Yu 1, Stringer 2, Abid 3, Carilli 4, Siegle 5, Shinn 6, Schreiber & Schmitz 7); the list is `REFS` in `relink_case_studies.py`, laid out in two columns (3 + 4) by line count. Section 3's noise figure (`noisefig_poster.jl`) redrawn in the house style of the MiB 2026 / OHBM 2025 / Cosyne 2025 posters (GitHub repos): framed axes with ticks and units, plain inset zoom box, bold black arrow, colorbar on the matrix.
- Later (2026-11-09): noise-figure arrow redrawn (symmetric arc, shaft ends at a 9 px triangular head); the zoomed trace plots every 2nd sample (`ZOOM_STEP`); "The recording links all co-active cells." cut from the Section 1 caption; the header's take-home box is titled "Summary" (set by the relink).
- Header Summary box (2026-11-09): Brendan's new four bullets (`TAKEHOME` in `relink_case_studies.py`), set at 26 px with hanging indents (6 lines); the box height follows the text.
- Summary box (2026-11-09, later): the first two points in side-by-side white cards, the other two as bullets below.
- Summary box (2026-11-09, last): "PCA" bold in the first card, "Population recordings" and "Time series" bold in the bullets, 10 px bottom padding; the contact rows (texts and icons) moved down 10 px (`CDY`) to keep the gap.
- Noise figure (2026-11-09): the zoomed trace is sampled every 0.5 ms (`ZOOM_DT`, 8x the earlier 4 ms), on its own grid with the trend linearly interpolated and fresh noise drawn after the covariance, so the rest of the figure is unchanged.
- Fathom colours (2026-11-09): every figure now uses Fathom's palette. The Makie figures already did; `drafts/opening/svgkit.py` (Section 1 figure, via `make_1f.py`), `figures/make_s2_equations.py`, the relink's swatches and coloured runs, the Section 5 keypoint icon and `phfig_poster.jl` moved from the old darker blue `#3f6fd1` and greens to baikal `#6ea0f9`, qinghai `#88bd69`, chernoe `#282c34` (figure ink) and darker(abyad) (the 1/f trace). Grating directions follow Fig3: 0° chernoe, 45° bermejo, 90° ianthina, 135° baikal. Background greys, title bars and the Julia logo are unchanged.
- Later (2026-11-09): Section 4 eigenspectra y label is "CV principal value" (`phfig_results_poster.jl`). The Section 3 callout lists all four methods at k = 2 in two rows (`CALLOUT`: PCA 32 ± 16, cPCA 25 ± 15, ρPCA 13 ± 10, bPCA 9 ± 8°, mean ± SD over 23 sessions from `curves_allvis` in `data/neuropixels_data_contrast=0.1.jld2`, coloured by `PCA_COLORS`); the callout and caption boxes grew to 371 px.
- Noise figure (2026-11-09, later): the zoomed trace has no frame, ticks or y label, only "Time" beneath it; its y limits hug the trace. The zoom guides end in small vertical ticks marking the window's range.
- Section 1 layout (2026-11-09): the construction figure is cropped to its content (720 x 1031, `make_1f.py`) and spaced evenly (`GAP` 75 between panels, labels 40 above their sheets; "Redundant links" under the gray screen, the "?" arrow under sheet (b)); the caption box runs from the figure + 30 out to the intro box edge (818 wide, 14 lines) and is centred on the figure vertically. `link_construction.py` now rewrites the slot size on every run. Section subtitles (`s1`-`s4-subtitle`) are upright.
- Section 1 layout (2026-11-09, rework): text column at the left, the intro as free text (no box) over the caption box, which runs to the section foot (the caption opens "Right:"); the construction figure fills the rest at full height. `link_construction.py` picks the narrowest column (multiple of 10) that holds both, currently 670, and redraws the figure through `make_1f.option1f_vertical` whenever the slot changes shape (now 875 x 1450, drawn 720 x 1193 at k = 1.215, sheets at SQUASH 0.9, equal panel gaps); it wraps with the relink's measured `wrap` (its own font lookup missed Source Sans 3 and wrapped short) and re-lays the intro texts the relink rewraps, so run it after the relink.
- Section 1 subtitle (2026-11-09): "PCA cannot distinguish meaningful structure from redundancy and noise"; too long at 48 px, so all four section subtitles are now 38 px (baselines raised 3.5 px to stay centred in the bars).
- Header glossary (2026-11-09): the header Summary box is now "Glossary": four one-line entries (constraint of interest, test data, redundancy baseline in baikal, noise baseline in bermejo) at 26 px, 12 px apart (`TAKEHOME` in `relink_case_studies.py`); the cards are gone and the box height follows the text (232 px).
- Inkscape compatibility (2026-11-09): the scripts stored each text's wrap width as `inline-size`, which Inkscape (1.4.2) treats as SVG 2 auto-flow and rewraps (lines run together); it is now a custom `--wrap` property that renderers ignore and an Inkscape save keeps. `svgkit.rich` sets `xml:space="preserve"` (Inkscape dropped the space in "(a) Drifting gratings"). resvg output unchanged. Still open: Inkscape's PDF export rasterizes the linked figure SVGs at their intrinsic size (34-79 ppi).
- Later (2026-11-09): the header box is now "Contact details" (46 px title in a 62 px bar, the four contacts one per line at 38 px with their icons, filling the panel to y = 397); the glossary and cards are gone. Section 1's redundancy/noise icons are plain bullets. Section 2's subtractive bullet ends "require hyperparameter tuning"; Section 3's (d) reads "so short windows can be used to estimate the noise covariance". Section 3's results crop now sits on one even panel (the title cover and a right-edge cover are filled with Fig3's tint `#f6f9f9`).
- Section 4 (2026-11-09): the loading-attribution axis is gone; `phfig_results_poster.jl` draws the traces (names above each trace) beside a square "Principal value spectrum" axis (667 x 268), and the caption ((a), (b) only) sits in a full-width box 25 below the figure.
- Later (2026-11-09): Section 4's figure is 667 x 250; trace names and "Time →" use (b)'s x-label size; the (a)/(b) labels sit 30 above the axes. Caption (a) adds the cPCA and ρPCA medians over 100 draws (0.07, 0.05; `MC_CPCA`, `MC_RHOPCA`, from `mc_pc1_*`); it is 6 lines. The "Beyond spikes" box is "Other applications", without the code line or Julia logo. References checked against the publishers' records (all seven correct; ref 7 is the 2000 review, IAAFT itself is Schreiber & Schmitz 1996 PRL).
- Later (2026-11-09): Section 4's traces axis spans the figure's full height (fixed `height`, `tellheight = false`), traces at amplitude 1.3 and linewidth 1.8; (b) markers 9, lines 3. Header authors on two lines ("Brendan Harris" / "Ben Fulcher", set by the relink), the block re-centred on the crest.
- Later (2026-11-09): the noise figure's top rate trace is baikal blue (`noisefig_poster.jl`).
- Later (2026-11-09): "Other applications" ends with a closing line, "bPCA is a practical algorithm to correct for redundancy and noise across multiple fields." (`s5-closing`, 2 lines, set by the relink).
- Later (2026-11-09): the diagonal line joining the grating cards in Section 1 (a) is removed (`make_1f.option1f_vertical`).
- Later (2026-11-09): Section 4 caption (a) quotes each method beside its name: "cPCA (ρ = 0.07) and ρPCA (ρ = 0.05) also fail (medians over 100 simulations)"; the ρ quotes use non-breaking spaces so they never split.
- Later (2026-11-09): US English sweep: "colored" (Section 1 caption), "characterize" (Summary); no other British spellings in the visible text or figure labels.
- PDF export (2026-11-09): `python3 -I figures/export_pdf.py [inkscape]` writes `SfN_2026.pdf` (1414 x 1000 mm, one page): it inlines all 18 linked SVGs as nested `<svg>` (ids prefixed per copy; handles dvisvgm's single-quoted attributes) so Inkscape keeps them vector, and embeds subset Source Sans 3. Only the figures' own rasters remain (229-336 ppi). karl has no Inkscape; the 1.4.2 AppImage was run extracted from the session scratchpad.
- Later (2026-11-09): the grating cards (`make_1f.grating`) use explicit stops at every half period across the card instead of `spreadMethod="repeat"`, which PDF viewers expand inconsistently; resvg output differs by at most 2 grey levels.
- Later (2026-11-14): Section 1 (c) no longer erases the background network (a set difference, i.e. subtraction): its links and cells stay, drawn faint as "at baseline" (`sheet(..., flat=...)` in `make_1f.py`); the arrow from (b) has no label (the "?" is gone).
- Later (2026-11-14): the label under the gray screen in Section 1 (b) reads "Redundant covariance" (two lines; one would reach the sheet).
- Later (2026-11-14): a bold ÷ sits in the gap between Section 1 (a) and (b), centred on the arrow below (b).
- Later (2026-11-15): Section 3 (g) direction labels sit beside their crosses: 0° left, 90° right, 45° above, 135° below (`scatter_ring!(...; place)` in BaselinePCALab `scripts/Fig3_case_studies.jl`, which also widens the bPCA axis right margin to 0.2 so the 90° label fits; the paper figure changes too). Fig3 re-rendered and recopied to `figures/src/`.
- Branches (2026-11-15): `main` is the public branch (README, .gitignore, `SfN_2026.pdf/.png/.svg` only; the SVG self-contained via `figures/standalone_svg.py`); all work happens on `dev`. A local `.git/hooks/pre-push` mirrors the three poster files, README and .gitignore from the pushed `dev` commit onto `main` and pushes `main` whenever `dev` is pushed, so re-export the PDF and PNG before pushing.
- Later (2026-11-16): the "Redundant covariance" label under the gray screen is gone (`make_1f.py`); the Section 1 caption is centred vertically in its box (`link_construction.py`). The Section 3 noise caption sits in a white box at the foot of the grey box (`s3-noise-capbox`, 12 px inset, 16 px padding; set by the relink). Section 2's bPCA sentence is one line ("bPCA subtracts noise covariance, whitens corrected redundancy, then orthogonalizes the test data:") with a blank line above it.
- Later (2026-11-16): the Section 3 results caption (`text1277`) is centred vertically in `s3-caption-box`.
- Later (2026-11-16): Section 1 panel titles start 20% of the figure width in (`LX = 144` in `make_1f.option1f_vertical`, was 0), so (c) sits nearer its sheet.
- Later (2026-11-16): the Section 1 figure crops its empty side margins (`CL, CR = 30, 18` in `make_1f.option1f_vertical`; drawn 672 x 1114), so it places at k = 1.302 (was 1.215) and the panel gaps shrink from 123 to 84.
- Later (2026-11-16): the Section 1 arrow below (b) is as thick as the ÷ bar (shaft 9 figure units, head 26 x 28, solid ink).
- Later (2026-11-16): the Section 3 noise-figure arrow is straight and level with the centre of (e)'s "Unit" ylabel (`noisefig_poster.jl`); figure recopied to `figures/src/`.
- Later (2026-11-16): Section 3 raster cards carry a 4-unit white edge under their frames (`card-halo` paths patched into `figures/src/trial_stack_covariance.svg`; `trial_stack_covariance.jl` draws the same, but `AllenNeuropixelsLab` would not precompile so it was not re-run). Noise figure (3d/3e): straight arrow shortened at both ends, no colorbar or tick numbers on the matrix, panel sizes pinned to the old layout (`COLGAP`, an invisible `Box` where the colorbar was); in the poster the figure and its white caption box are spaced evenly down the grey box (`INK_FOOT` etc. in the relink). The results crop sits on white: the relink writes `figures/src/Fig3_case_studies_poster.svg` (row 1's 5% teal tint zeroed) and the covers are white.
- Later (2026-11-16): Section 4 (a), (b) and their caption share one grey box (`s4-panel-box`, 1632 to 2624), the caption in a white box at its foot (`s4-caption-box`), gaps even. Section 1 intro: "usually inferred (without supervision) using principal component analysis".
- Later (2026-11-16): Section 4 (b) lines 4.5 and markers 15; (a) trace names and "Time →" at 1.3x (b)'s x-label size, trace spacing D = 4.3 (`SCATTERLINES` in `phfig_results_poster.jl`, was 3 and 9).
- Later (2026-11-16): Section 4 (a) trace names sit just above their own trace's peak (`A * maximum(y)`), and the figure has 12 units of left padding so (a) clears the grey box edge (`phfig_results_poster.jl`).
- Later (2026-11-16): `s4-panel-box` is inserted just before `s4-caption-box` (it was drawn over the white caption box, hiding it); the figure sits 12 right and 10 down of its even-gap position; (b) axis background transparent.
- Later (2026-11-16): Section 1 (a) grating cards fan up and to the left, each 22 units clear of the sheet's left edge and parallel to it (`edge` in `make_1f.option1f_vertical`).
- Later (2026-11-16): the four Section 1 grating cards are one size (60).
- Later (2026-11-16): the Section 1 figure is drawn 30 px left of its slot (`NUDGE` in `link_construction.py`).
- Later (2026-11-16): callout heading "Decoding error with 2 PCs" (SVG text only); references centred vertically in their box (`REF_Y0` 3442.44).
- Later (2026-11-16): Section 4 reworked again: no grey box around (a), (b); a grey box behind the schematic traces (`s4-schematic-box`, schematic top -8 to bottom +16); the caption is back in a full-width grey box ending 25 above the Summary bar, with even gaps between the schematic box, the figure and the caption.
- Later (2026-11-16): callout heading semibold, not italic, and its last line "Chance level 56°" (relink); Fig3 (h) legend "Chance level".
- Later (2026-11-16): Fig3 re-rendered (legend "Chance level") and recopied; `FIG3_S3` also drops row 1's outline, and `EDGE_S3` is 8 wide, so no grey marks remain at the crop's right edge.
- Later (2026-11-16): the Section 3 noise figure is centred horizontally in its grey box (`INK_L`, `INK_R` in the relink; 98 px either side).
