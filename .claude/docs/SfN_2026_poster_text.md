# SfN 2026 poster: text (2026-11-08)

All text on `SfN_2026.svg`, by section in reading order. Edit freely and send it back.

- Leave each `<!-- id -->` line in place; it tells me where the block goes.
- `**bold**` and `*italic*` match the poster's emphasis. Coloured runs (redundancy blue, noise red) are shown as bold.
- Equations are LaTeX (`$$ ... $$`); edit them as LaTeX.
- Text inside the figures is listed at the end. Those labels are drawn by the figure scripts, not the poster.

## Header

<!-- title-0 -->
Inferring stimulus-engaged subspaces from noisy

<!-- title-1 -->
and redundant population activity with Baseline PCA

<!-- authors -->
Brendan Harris, Ben D. Fulcher

<!-- affiliation -->
School of Physics, The University of Sydney

<!-- contact-email -->
brendan.harris@sydney.edu.au

<!-- contact-x -->
@brendanjohnh

<!-- contact-github -->
@brendanjohnharris

<!-- contact-bluesky -->
@brendanjohnharris.bsky.social

<!-- takehome-title -->
Take-home

<!-- takehome-1 -->
• PCA cannot separate structure from redundancy and noise

<!-- takehome-2 -->
• **Baseline PCA** removes both with empirical baselines

<!-- takehome-3 -->
• Population recordings: finds stimulus-engaged subspaces

<!-- takehome-4 -->
• Time series: removes phantom oscillations

## 1. Problem: PCA cannot tell structure from redundancy and noise
<!-- s1-title / s1-subtitle -->

<!-- text1195 -->
Stimuli confine neural population activity to **low-dimensional subspaces**, usually inferred with **principal component analysis** (PCA). But recordings also carry **nuisance covariance** that is present even without a stimulus:

<!-- text1197 -->
**Redundancy**: neurons co-fluctuate during spontaneous activity [4]

<!-- text1204 -->
**Noise**: rates estimated from spike counts in finite trials carry measurement error

<!-- text1207 -->
Since PCA ranks directions by total variance, its leading components mix stimulus-engaged structure with redundancy and noise.

<!-- text1217 -->
*Left:* **(a)** Each grating direction activates a subnetwork (coloured by direction), on top of a background network (gray) that is active without any stimulus. The recording links all co-active cells. **(b)** A gray screen drives the background network only, revealing the redundant subspace. **(c)** Correcting for the redundant activity reveals stimulus-engaged subnetworks. Baseline PCA measures the variance in (a) relative to (b), above the spiking noise, whereas PCA on (a) alone returns the largest and most active subnetwork dominated by redundancy.

## 2. Baseline PCA: bPCA corrects for redundancy and noise
<!-- s2-title / s2-subtitle -->

<!-- text1225 -->
bPCA compares the test data against a **redundancy baseline**, in which the system varies without the constraint of interest, and a **noise baseline** that captures variance due to the measurement process only.

<!-- text1226 -->
bPCA finds the family of projections *P* that meet three conditions:

<!-- s2-baselines-label-a -->
(a)

<!-- s2-baselines-label-b -->
(b)

<!-- s2-baselines-label-c -->
(c)

<!-- s2-cond-r-text -->
**(a) Redundancy baseline** becomes white

<!-- equation, LaTeX -->
$$ P^{T}\,\Sigma^2_r\,P = I $$

<!-- s2-cond-n-text -->
**(b) Noise baseline** collapses

<!-- equation, LaTeX -->
$$ P^{T}\,\Sigma^2_n\,P = \mathbf{0} $$

<!-- s2-cond-t-text -->
**(c) Test data** become diagonal

<!-- equation, LaTeX -->
$$ P^{T}\,\Sigma^2\,P = \hat{\sigma}^2_{+} $$

<!-- s2-whynot-title -->
Other contrastive methods

<!-- text1252 -->
Earlier contrastive methods can be thought of as comparing the test data with a single baseline [2, 3]. Subtractive methods such as cPCA subtract two covariances, but require hyperparameters to find positive semidefinite solutions; ratio methods such as ρPCA divide two covariances, amplifying directions dominated by noise. bPCA subtracts a noise baseline, then orthogonalizes the eigenvectors *V* symmetrically against the test data:

<!-- equation, LaTeX -->
$$ (\Sigma^2 - \Sigma^2_n)\,V = (\Sigma^2_r - \Sigma^2_n)\,V\hat{\sigma}^2 \;\longrightarrow\; P = V\,(V^{T}\Sigma^2 V)^{-1/2}\,\hat{\sigma}_{+} $$

<!-- text1250 -->
Eigenvalues are test variance above the noise floor, in units of the redundancy baseline (negative eigenvalues are dropped: +); PCA, cPCA and ρPCA are thus limiting cases.

## 3. Visual cortex: bPCA recovers grating direction
<!-- s3-title / s3-subtitle -->

<!-- text1256 -->
We decoded the direction of drifting gratings (0°, 45°, 90° or 135°, 10% contrast; 75 trials each) from Neuropixels recordings of mouse visual cortex (Allen Visual Coding, Functional Connectivity set [5]; 23 sessions; 18 male and 5 female mice), pooling all visual cortical units.

<!-- text1258 -->
**Test data**: trial-mean firing rates during gratings

<!-- text1260 -->
**Redundancy baseline**: spontaneous activity, partitioned into trial-length windows

<!-- text1262 -->
**Noise baseline**: counting noise of firing rates, from spontaneous spikes (below)

<!-- s3-row-label-a -->
(a) Recording

<!-- s3-row-label-b -->
(b) Trial responses

<!-- s3-row-label-c -->
(c) Covariance

<!-- s3-noise-title -->
Measuring the noise baseline

<!-- s3-noise-label-d -->
(d) A unit's spontaneous activity

<!-- s3-noise-label-e -->
(e) Noise covariance

<!-- text1267 -->
**(d)** Noise dominates fast fluctuations, so the covariance in short windows can be used as an estimate for noise. **(e)** We measure noise covariance from spontaneous spikes in 10 ms bins, scaled up to a trial-mean rate, which has a median of 23% of units' trial-mean variance.

<!-- s3-results-label-a -->
**(f)** PCA

<!-- s3-results-label-b -->
**(g)** bPCA

<!-- s3-results-label-c -->
**(h)** Direction decoding

<!-- text1277 -->
*Above:* Trial-mean responses of an example session (537 units) projected onto the two leading components of **(f)** PCA and **(g)** bPCA; colors mark grating direction and crosses the class means. **(h)** Error in decoding direction from the top *k* components (linear discriminant classifier, 5-fold cross-validation repeated 8 times; mean ± SD across 23 sessions; dashed line: chance).

<!-- s3-callout-head -->
Decoding error, two components

<!-- s3-callout-num -->
32° → 9°

<!-- s3-callout-detail -->
**PCA** 32 ± 16° **bPCA** 9 ± 8°

<!-- s3-callout-chance -->
chance 56°

<!-- text1287 -->
With spontaneous activity as the redundancy baseline, **bPCA concentrates stimulus information into its leading components**, cutting the two-component decoding error by 23°, on average.

## 4. Phantom oscillations: bPCA recovers hidden signal
<!-- s4-title / s4-subtitle -->

<!-- text1293 -->
Temporal autocorrelation pervades neural and behavioral time series, and PCA of autocorrelated signals returns smooth, sinusoid-like components: phantom oscillations [1]. We simulated 200 signals that share a weak, chaotic latent, on top of independent 1/f background activity and a shared instrument artifact.

<!-- text1295 -->
**Redundancy baseline**: phase-randomized (IAAFT) surrogates [6], which preserve autocorrelation but scramble the shared latent

<!-- text1297 -->
**Noise baseline**: a calibration recording of the instrument only

<!-- s4-results-label-a -->
**(a)** Recovered latent

<!-- s4-results-label-b -->
**(b)** Eigenspectra

<!-- text1305 -->
**(a)** The leading PCA component is a slow phantom oscillation (ρ = 0.06 with the latent), whereas the leading bPCA component recovers the latent (ρ = 0.88). **(b)** Held-out eigenvalues (medians across 100 simulations): the two leading PCA eigenvalues are nearly equal, as for phantom oscillations, whereas the bPCA eigenvalues fall to the baseline level of one (dashed) by the third component. **(c)** Weights of the leading component against the true loadings of the latent (bPCA ρ = 0.94; PCA ρ = 0.04).

<!-- s4-results-label-c -->
**(c)** Loading attribution

## 5. Summary and Beyond spikes

<!-- s5-summary-title -->
Summary

<!-- s5-beyond-title -->
Beyond spikes

<!-- text1312 -->
**Baseline PCA** separates the structure imposed by a constraint of interest from **redundancy** and **noise**, using empirical baselines that characterise the measurement process.

<!-- text1317 -->
Similar nuisance covariance arises across recording modalities:

<!-- text1319 -->
**fMRI**: spatial smoothing

<!-- text1321 -->
**Spike sorting**: duplicated units

<!-- text1333 -->
**Pose estimation**: anatomically coupled keypoints

<!-- text1315 -->
In mouse visual cortex, **two bPCA components** decoded grating direction with 9° error, against 32° for PCA.

<!-- s5-code -->
**Code**: BaselinePCA.jl

## 6. References

<!-- s6-title -->
References

<!-- text1339 -->
1. Shinn, *Phantom oscillations in principal component analysis*, PNAS (2023).

<!-- text1342 -->
2. Abid et al., *Exploring patterns enriched in a dataset with contrastive principal component analysis*, Nature Communications (2018).

<!-- text1345 -->
3. Carilli et al., *The Rayleigh quotient and contrastive principal component analysis I*, bioRxiv (2025).

<!-- text1348 -->
4. Stringer et al., *Spontaneous behaviors drive multidimensional, brainwide activity*, Science (2019).

<!-- text1351 -->
5. Siegle et al., *Survey of spiking in the mouse visual system reveals functional hierarchy*, Nature (2021).

<!-- text1354 -->
6. Schreiber & Schmitz, *Surrogate time series*, Physica D (2000).


## Appendix: text inside the figures

<!-- fig: s1-construction (drafts/opening/make_1f.py) -->
(a) Drifting gratings · 0° · 45° · 90° · 135° · (b) Gray screen · Redundant links · ? · (c) Stimulus-engaged

<!-- fig: s3 noise box (noisefig_poster.jl) -->
Zoom: fluctuations around the trend · Time · Unit · Unit

<!-- fig: s4 schematic (phfig_poster.jl) -->
Chaotic latent, $s(t)$ · 1/f background, $b_i(t)$ · Instrument artifact, $g_i\,c(t)$ · Test data $\Sigma^2$, $x_i = a_i\,s + b_i + g_i\,c$ · Redundancy baseline $\Sigma^2_r$, $\tilde{x}_i = \mathrm{IAAFT}(x_i)$ · Noise baseline $\Sigma^2_n$, $x_i^{\mathrm{cal}} = g_i'\,c$

<!-- fig: s4 results (phfig_results_poster.jl) -->
Chaotic latent · bPC1 ρ = 0.88 · PC1 ρ = 0.06 · Time → · Component · Held-out eigenvalue · True loading $a_i$ · PC1 weight

Section 2 panels (a)-(c) and the Section 3 panels are crops of the manuscript figures (Fig1, Fig3), so their internal labels follow the paper.
