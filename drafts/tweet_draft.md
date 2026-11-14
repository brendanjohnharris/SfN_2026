# Tweet draft (SfN 2026 thread)

Poster LBP076.24, board C25; session Wed 18 Nov 8 am to 12 pm, presenting 11 am to 12 pm.

**1/6**
Unsupervised dimensionality reduction methods are commonly used to infer low-dimensional structure driven by a stimulus from noisy, redundant measurements, such as stimulus-engaged subspaces in population activity. We introduce Baseline PCA! #SfN2026 poster LBP076.24 🧵

**2/6**
Here, redundancy means correlations between neurons that are unrelated to the stimulus, and noise means variability that arises from the measurement process.

**3/6**
Baseline PCA takes two empirical baseline datasets, one capturing redundancy and one capturing noise. For population recordings, our redundancy baseline is spiking in the absence of a stimulus (spontaneous activity), and noise is the variability between adjacent short windows.

**4/6**
With these two ingredients, the error in decoding drifting grating direction from two components drops from 32° with PCA to 9° with Baseline PCA (Allen Neuropixels, 23 sessions).

**5/6**
The same algorithm corrects redundancy in other data too! Phantom oscillations are a known problem for PCA on autocorrelated time series. Baseline PCA recovers a shared chaotic latent from an autocorrelated background (ρ = 0.88 for bPCA vs 0.06 for PCA).

**6/6**
In many cases these baselines are readily available! Where do you see redundancy in your data? Come and see me at poster LBP076.24 (board C25), Wed 18 Nov, 11 am to 12 pm, to discuss!
