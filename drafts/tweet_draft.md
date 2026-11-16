# Tweet draft (SfN 2026 thread)

Poster LBP076.24, board C25; session Wed 18 Nov 8 am to 12 pm, presenting from 9 am.

**1/6**
At #SfN2026? I'll present Baseline PCA, a linear dimensionality reduction method that can, among other things, infer stimulus-engaged subspaces in population activity from noisy, redundant measurements. Poster board C25 on Wed 18, from 9am 🧵
https://github.com/brendanjohnharris/SfN_2026
[image: poster PNG]

**2/6**
By redundancy, we mean neuron-to-neuron correlations that are unrelated to the stimulus. Noise is variability that arises from the measurement process.

**3/6**
Baseline PCA takes two empirical baseline datasets, one capturing redundancy and one capturing noise. For population recordings, our redundancy baseline is spiking in the absence of a stimulus (spontaneous activity), and noise is the variability between adjacent short windows.

**4/6**
With these two baselines, the error in decoding drifting grating direction from two components drops from 32° with PCA to 9° with Baseline PCA (Allen Neuropixels Visual Coding data).

**5/6**
But redundancy and noise appear in all kinds of data! Phantom oscillations are a known artifact of PCA on autocorrelated time series. Baseline PCA suppresses these phantoms, recovering a shared chaotic latent from an autocorrelated background where PCA gives sinusoids.

**6/6**
Do you have redundancy in your high-dimensional measurements? In many cases, the baseline data to correct for this are already available! Come by poster board C25 on Wed 18 Nov, from 9am, to discuss!
