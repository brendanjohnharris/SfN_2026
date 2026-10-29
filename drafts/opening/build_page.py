"""Assemble a single HTML page that shows the five opening drafts with their notes.

Usage: python3 build_page.py OUT.html   (run from this folder; reads the option*.svg files)
"""

import re
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def inline_svg(name):
    svg = open(os.path.join(HERE, name)).read()
    svg = re.sub(r'<\?xml[^>]*>', '', svg)
    svg = re.sub(r'\swidth="[\d.]+"\sheight="[\d.]+"', ' class="fig" role="img"', svg, count=1)
    return svg


OPTIONS = [
    dict(
        n=1, file="option1-networks.svg", frame="Network view",
        pitch="Your recording is two networks on top of each other",
        reads=[
            "Panel (a) is a network: dots are units, a line means “these two fire together”. It is labelled <em>gray screen</em>, so these links have nothing to do with the stimulus: shared inputs, arousal, running.",
            "Panel (b) is a smaller, tighter network in green: the links the grating adds. Two of its units also sit in the blue ring, so the same neurons carry both networks.",
            "Panel (c) has no lines, only red halos: spiking noise is private to each unit. It links nothing but blurs everything.",
            "Panel (d) is the sum, drawn in black on purpose: in the recording nothing says which line came from which network.",
            "Panel (e): PCA sees only (d) and ranks directions by total variance, so its leading component is the largest co-fluctuation, the spontaneous network.",
            "Panel (f): Baseline PCA has measured (a) and (c), subtracts the noise, measures variance relative to the spontaneous network, and returns the green module.",
        ],
        lead="A population recording is a network: units that fire together are linked. Most links are there with nothing on the screen (shared inputs, arousal, running), and every unit also carries its own spiking noise. The stimulus adds a smaller network on top. PCA ranks directions by total variance, so it returns the biggest network first: the spontaneous one.",
        caption="(a) On a gray screen, units already co-fluctuate: the spontaneous network. (b) A grating engages a smaller set of units, some of which also belong to the spontaneous network. (c) Finite spike counts add private noise to every unit. (d) The recording is the sum, and the three parts look alike. (e) PCA ranks directions by total variance, so its leading component is the largest co-fluctuation, the spontaneous network. (f) Baseline PCA measures (a) and (c) directly, and ranks what the grating adds beyond them.",
        handoff="“The spontaneous network” becomes the <b class=\"blue\">redundancy baseline</b>; “the spiking noise” becomes the <b class=\"red\">noise baseline</b>. Section 2 then opens: “bPCA compares the test data with a redundancy baseline (the spontaneous network, recorded on the gray screen) and a noise baseline (the spiking noise).”",
        strengths=[
            "The most distinctive picture of the five; “functional connectivity” is a frame neuroscientists already hold.",
            "Makes the real difficulty visible: the same units carry both networks. Panel (d) in black says “indistinguishable” without a word.",
            "Colouring units by loading in (e) and (f) is exactly what a component is, so the figure also teaches what bPCA returns.",
        ],
        risks=[
            "A network implies pairwise links; a component is a pattern of loadings. A reader may think bPCA is a connectivity method. Say “co-fluctuation network” once, and colour nodes rather than edges.",
            "Six panels is dense for the slot: at poster size the sentences in (e) and (f) should move to the caption box.",
        ],
    ),
    dict(
        n=2, file="option2-stateSpace.svg", frame="Population-coding geometry",
        pitch="The largest axis of variance is rarely the stimulus",
        reads=[
            "Panel (a) plots one unit's rate against another's during the gray screen. Everyone has drawn this plot (the noise-correlation scatter). The tilt says the units rise and fall together without a stimulus.",
            "Panel (b) is the same plot during gratings, coloured by direction. The tilt remains, and the four directions are displaced <em>across</em> it because the two units prefer different directions. PC1 (teal) runs along the tilt: the largest axis, along which the colours overlap completely.",
            "Panel (c) lays the two covariance ellipses on top of each other. The black ellipse (gratings) sticks out beyond the blue one (gray screen) in one direction only, across the tilt: bPC1. The red disc is the spiking noise both ellipses contain; it is subtracted before they are compared.",
        ],
        lead="Plot two units against each other and they rise and fall together even on a gray screen: shared inputs, arousal and running give the population a large axis of variance that has nothing to do with the stimulus. A grating adds variance along a different axis, where the units' tuning differs. PCA takes the largest axis. Baseline PCA takes the axis where the stimulus adds variance beyond the gray screen, above the spiking noise.",
        caption="(a) Firing rates of two units during spontaneous activity: the cloud is tilted because the units co-fluctuate. (b) During drifting gratings the tilt remains and the four directions (colours; crosses mark class means) separate across it. PCA takes the largest axis, PC1, along which the directions overlap. (c) Baseline PCA compares the two covariance ellipses after subtracting the spiking noise (red), and takes the axis where the gratings add variance beyond the gray screen: bPC1, along which the directions separate. In a population this happens in hundreds of dimensions at once (Section 3).",
        handoff="The blue ellipse is the <b class=\"blue\">redundancy baseline</b> Σ²ᵣ, the red disc the <b class=\"red\">noise baseline</b> Σ²ₙ; an eigenvalue is how far the black ellipse sticks out beyond the blue, in units of the blue, after both lose the red. This is already Section 2's panel (c), which could then shrink.",
        strengths=[
            "The most familiar picture in population coding: nothing to translate.",
            "The decoding numbers (31° to 9°) sit inside the figure, and the panels preview Section 3's (f)–(h), so the poster reads as one story.",
            "The red disc explains the noise baseline by itself: a direction as thin as the disc in both ellipses would blow up if you divided by the baseline alone.",
        ],
        risks=[
            "It is the two-neuron cartoon every method paper uses, so it is the least surprising.",
            "“Redundancy” still needs one line of translation in Section 2 (here it is only “co-fluctuation”).",
            "It assumes the spontaneous covariance persists during the stimulus; Section 2(e) covers quenching (λ < 1).",
        ],
    ),
    dict(
        n=3, file="option3-dFF.svg", frame="Imaging arithmetic",
        pitch="Baseline-correct the covariance, not just the fluorescence",
        reads=[
            "Top row: a stimulus frame F, the baseline frame F₀, the dark frame with the shutter closed, and ΔF/F, which shows only the responding cells. Every imager does this before looking at anything else.",
            "The formula under it is the one they know: ΔF/F = (F − F₀) / (F₀ − dark). The dark frame leaves both terms before the ratio.",
            "Bottom row: the same three objects for covariance. Σ² during gratings has a shared block plus a tuned sub-block; Σ²ᵣ on the gray screen has the shared block only; Σ²ₙ, the spiking noise, is a diagonal. The result is a spectrum, λ − 1 per direction, zero except where the stimulus adds covariance.",
            "The formula under it is the same formula with the symbols swapped: λ − 1 = (Σ² − Σ²ᵣ) / (Σ²ᵣ − Σ²ₙ), one direction at a time. That is what the generalized eigenvalue problem in Section 2 computes.",
        ],
        lead="No imager reports raw fluorescence: F is read relative to a baseline F₀, after the camera's dark frame is subtracted. PCA reports raw variance. Baseline PCA reads the variance of each direction the same way: relative to spontaneous activity (the baseline), after subtracting spiking noise (the dark frame). Directions where the stimulus adds nothing come out at zero, like a cell that did not respond.",
        caption="Top: ΔF/F compares a stimulus frame F with a baseline frame F₀ after removing the dark frame; only responding cells remain. Bottom: Baseline PCA compares the covariance during gratings, Σ², with the covariance on the gray screen, Σ²ᵣ, after removing the spiking-noise covariance Σ²ₙ. The eigenvalue λ − 1 of a direction is its ΔF/F, so only stimulus-engaged directions remain.",
        handoff="F₀ is the <b class=\"blue\">redundancy baseline</b>, the dark frame the <b class=\"red\">noise baseline</b>, and λ − 1 is ΔF/F. “λ > 1 marks directions to which the constraint adds variance” becomes “ΔF/F > 0”. The equation box can carry the gloss “λ − 1 is ΔF/F for covariance”.",
        strengths=[
            "The parallel is exact, not a metaphor: nothing has to be unlearned later.",
            "Instant for imagers, familiar to electrophysiologists (baseline subtraction, normalisation).",
            "The only option that makes the noise baseline obvious on its own: everyone knows why the dark frame is subtracted. It also makes λ readable (λ = 1 is “same as baseline”).",
        ],
        risks=[
            "“One direction at a time” carries the subtlety: ΔF/F is pixel-wise, bPCA is an eigenproblem. A careful reader will ask which directions.",
            "It does not show why PCA fails on its own: there is no largest-axis picture. Pairs well with Option 2.",
        ],
    ),
    dict(
        n=4, file="option4-control.svg", frame="Experimental logic",
        pitch="PCA has no control condition. Your recording already contains two.",
        reads=[
            "A session timeline, like the stimulus-epoch strip of the Allen protocol: a gratings block (one stripe per trial) and a gray-screen block.",
            "Three cards are pulled out of it. Test data: the gratings. Control 1: the gray screen, the same units with no stimulus. Control 2: the spike-count noise, the same units read at 10 ms so that rate changes cancel in successive differences and only counting noise remains.",
            "Below: PCA uses the first card only. Baseline PCA uses all three and reports λ, the variance above the noise in units of the gray screen.",
        ],
        lead="No experiment is reported without a control, but PCA has none: every direction of variance counts as structure, including the co-fluctuations that are there with nothing on the screen and the noise in every spike count. Baseline PCA adds two controls that your recording already contains: the gray-screen epoch, which keeps the shared inputs but removes the stimulus, and the spike-count noise, which keeps the measurement but removes the activity.",
        caption="One Neuropixels session provides all three inputs. Test data: trial-mean rates during gratings. Control 1 (redundancy baseline): the same units on the gray screen, cut into trial-length windows. Control 2 (noise baseline): the counting noise of each unit's rate, from differences of 10-ms spike counts, in which rate fluctuations cancel. PCA uses the test data only; Baseline PCA reports, for each direction, the test variance above the noise in units of the control.",
        handoff="Control 1 is the <b class=\"blue\">redundancy baseline</b>, control 2 the <b class=\"red\">noise baseline</b>. “Control” stays useful later: the IAAFT surrogate is the control for phantom oscillations (Section 4) and the second reading is its noise control.",
        strengths=[
            "Speaks to an experimentalist's reflex (where is the control?) and sells feasibility: no new experiment, the baselines are already in the session.",
            "Doubles as the methods strip for Section 3, whose Test / Redundancy / Noise list could shrink.",
            "The 10-ms differencing story, which otherwise arrives late in the nugget box, appears up front.",
        ],
        risks=[
            "The least visual option: it shows what bPCA takes in, not why PCA fails.",
            "“Control” may suggest subtracting means rather than comparing covariances.",
            "Works best as a strip beneath another figure, or as the header of Section 3.",
        ],
    ),
    dict(
        n=5, file="option5-ongoing.svg", frame="Time-domain superposition",
        pitch="Evoked responses ride on ongoing activity that is larger than they are",
        reads=[
            "Panel (a): six raw traces across one trial with grating onset marked. They all wobble together, slowly, and some show a small step at onset. This is the Arieli (1996) and Stringer (2019) picture: ongoing activity is large and shared.",
            "Panel (b) separates the traces into ongoing (blue; one waveform, scaled per unit), evoked (green; stimulus-locked, different per unit) and spiking noise (red). The grey badges say where the variance is: mostly ongoing.",
            "Panel (c): the leading component of PCA is the ongoing waveform; the leading component of Baseline PCA is the evoked one.",
        ],
        lead="Ongoing activity is not silence: large fluctuations shared across the population continue through every trial [Arieli 1996; Stringer 2019], and a stimulus adds a smaller, structured response on top. PCA ranks directions by variance, so its leading components follow the ongoing activity. Baseline PCA measures the ongoing activity when no stimulus is shown, and the spiking noise, and ranks what the stimulus adds.",
        caption="(a) Six units in one trial: the slow fluctuations are shared, the responses at grating onset are small and differ between units. (b) The three parts: ongoing activity (shared; most of the variance), evoked response (stimulus-locked), spiking noise (private). (c) PCA's leading component follows the ongoing activity; Baseline PCA's follows the evoked response.",
        handoff="Ongoing activity is the <b class=\"blue\">redundancy baseline</b>, spiking noise the <b class=\"red\">noise baseline</b>. It also previews Section 4: autocorrelated background activity is what produces phantom oscillations.",
        strengths=[
            "The premise is already believed (nobody at SfN doubts that ongoing activity is large), so the argument is short.",
            "The only option in the time domain, which is how most people picture their data; it bridges to Section 4.",
        ],
        risks=[
            "Section 3's test data are trial-mean rates, not time courses, so this is an intuition, not the analysis. Label (a) “one trial of many” or say so in the caption.",
            "Because the premise is familiar, the figure is the least surprising of the five.",
        ],
    ),
]

VARIANTS_INTRO = """The network in Option 1 is drawn by hand, so nothing in it says what a line <em>is</em>. These four variants keep the whole-system view but build the network from spiking data, so the reader can see that an edge joins two units whose firing rates rise and fall together. All four come from one simulated population: 14 units, 12 s at 50 ms bins, Poisson spikes. Units 1–10 belong to two spontaneous groups that share a hub unit, each group driven by its own slow fluctuation (arousal, running). Units 11–14 are a module tuned to grating direction; two of them also lean weakly on the first group, so the same neurons carry both. Correlations are Pearson r between rates in 150 ms windows, and an edge is drawn where r &gt; 0.35."""

VARIANTS = [
    dict(
        n="1b", file="option1b-zoom.svg", frame="An edge, exploded into the pair's data",
        pitch="An edge is two units whose rates rise and fall together",
        reads=[
            "Panel (a) is the network in its true colours: two blue groups (correlated with nothing on the screen) and a green module (correlation the grating adds). A magnifier sits on one blue edge and one green edge.",
            "Panel (b) opens the blue edge. The two units' rates over 12 s of gray screen bump at the same moments, and their rates in 200 ms windows, plotted against each other, make a tilted cloud: r = 0.88. That is all an edge is.",
            "Panel (c) opens the green edge. During gratings the two units burst under the stimulus bars, and the scatter, coloured by direction, pulls the four directions apart; windows with no grating (grey) sit near the origin. A green edge is covariance the grating creates, and it carries the direction.",
        ],
        lead="Draw a line between any two units whose firing rates rise and fall together, and a population recording becomes a network. Most of its lines are there with nothing on the screen: shared inputs, arousal, running. The grating adds a few more, among the units it drives. PCA, which ranks directions by total variance, returns the biggest cluster of lines, which is not the stimulus.",
        caption="(a) Units linked when their rates are correlated: blue on the gray screen, green only during gratings. (b) One blue edge: the pair's rates on the gray screen and their joint distribution (r = 0.88). (c) One green edge: the pair's rates during gratings, and their joint distribution coloured by direction (crosses: class means; grey: no grating). The recording draws every edge in black. bPCA measures the blue network and the spiking noise, and ranks what the grating adds.",
        handoff="Panel (b) is the <b class=\"blue\">redundancy baseline</b> seen for one pair; the ellipse of (c) beyond the ellipse of (b) is what bPCA ranks; the <b class=\"red\">noise baseline</b> is the jitter of each dot that would remain if the rates were held fixed. Panel (c) is also Section 3's panel (g) for two units.",
        strengths=[
            "Answers “what is an edge?” with the plot every electrophysiologist uses.",
            "Merges Option 1 (the whole system) with Option 2 (one pair); the green scatter previews the decoding result.",
        ],
        risks=[
            "The busiest of the network variants: two callouts compete with the network, and at poster scale they need the full slot height.",
            "The magnified pairs must be chosen so their traces look clean.",
        ],
    ),
    dict(
        n="1c", file="option1c-raster.svg", frame="Spike raster, correlation matrix, network",
        pitch="Correlations that are there with nothing on the screen",
        reads=[
            "Panel (a) is a raster of 14 units on the gray screen. Dense vertical bands show groups of units firing together, at moments that have nothing to do with a stimulus.",
            "Panel (b) is the correlation matrix of their rates. The two bands become two blocks (units 1–6 and 6–10, sharing unit 6).",
            "Panel (c) draws the matrix as a network: an edge wherever r > 0.35. Two clusters, and that is everything the matrix said.",
            "Panels (d)–(f) repeat this during gratings. The bands are still there, units 11–14 now burst at every grating, the matrix gains a third block, and the network gains a clique, drawn in black like every other edge because the recording does not label them.",
            "Panel (g) keeps only the edges of (f) that are not in (c): the few units that fire together only when the grating is on.",
        ],
        lead="Correlate every unit with every other unit and a recording becomes a matrix, and the matrix a network. On a gray screen the matrix already has blocks: groups of units that rise and fall together under shared inputs, arousal and running. A grating adds one block more. PCA diagonalises the whole matrix, so its leading components are the biggest blocks, which were there without the stimulus.",
        caption="(a)–(c) Gray screen: spike raster, correlation matrix of the rates, and the matrix as a network (edge where r > 0.35). (d)–(f) The same during drifting gratings (bars: direction). (g) Edges present in (f) but not in (c). PCA on (e) returns the large blocks, the spontaneous correlations. bPCA measures (b) and the spiking noise, and returns (g).",
        handoff="Matrix (b) <em>is</em> the <b class=\"blue\">redundancy baseline</b> Σ²ᵣ and matrix (e) is Σ²; nothing is renamed. The <b class=\"red\">noise baseline</b> is what each unit's diagonal entry holds beyond the trend of its neighbouring lags (Section 3's nugget), so Section 3's noise box follows naturally.",
        strengths=[
            "Nothing is metaphorical: the raster is the data, the matrix is the covariance PCA and bPCA actually consume, the network is only the matrix thresholded.",
            "The block structure explains “redundancy” even to a physicist. Panel (g) is the stimulus-engaged subspace as a picture.",
        ],
        risks=[
            "Seven panels. For matrix-literate readers the network adds little over the matrix.",
            "Rasters print badly when small: at poster scale the bins must stay at least a point wide.",
        ],
    ),
    dict(
        n="1d", file="option1d-flipbook.svg", frame="Flipbook: units that light up together get an edge",
        pitch="Fire together, wire together, even with nothing on the screen",
        reads=[
            "Six snapshots of the same 14 units at six moments of one recording; a filled dot is a unit firing in that half second. At the gray-screen moments one group lights up together, or the other. At the grating moments a different group of four lights up.",
            "The raster underneath shows where the six moments sit, so the snapshots are visibly taken from the data.",
            "On the right, every pair that lit up together in two or more gray-screen moments gets a blue edge; pairs that lit up together only during gratings get a green one. The network is assembled in front of the reader.",
        ],
        lead="Watch a population for a few seconds and the same groups of units keep lighting up together, with nothing on the screen. Link every pair that does, and you have a network that owes nothing to the stimulus. A grating lights up one more group. PCA ranks directions by total variance, so its leading component is the group that lights up most, not the one the grating drives.",
        caption="Top: six moments of one recording (filled: units firing in that 0.5 s; green frames fall during a grating). Bottom left: the recording, with the six moments marked. Bottom right: pairs that lit up together at two or more gray-screen moments (blue) and pairs that lit up together only during gratings (green). bPCA measures the blue network and the spiking noise, and returns green.",
        handoff="The blue network, assembled from gray-screen moments, is the <b class=\"blue\">redundancy baseline</b>; the green edges are what bPCA ranks; the <b class=\"red\">noise baseline</b> is a dot that flickers on alone.",
        strengths=[
            "The most self-explanatory of all the drafts: a passer-by can rebuild the network from the frames, and “together, repeatedly” is exactly what the covariance of binned counts measures.",
            "The Hebbian slogan is a hook every neuroscientist knows, and the twist (the wiring is there without a stimulus) is the message.",
        ],
        risks=[
            "“Wire together” may suggest synaptic plasticity; say “edge”, not “wire”, in the body text.",
            "The lit sets are Poisson-noisy, which is realistic, but a passer-by may count mismatches. Six frames plus a raster is wide; it fits the slot only with small frames.",
        ],
    ),
    dict(
        n="1e", file="option1e-arcs.svg", frame="Arcs over the raster",
        pitch="The network, drawn on the data",
        reads=[
            "Panels (a) and (b) are the two rasters of 1c, but the network is drawn directly on them: an arc joins two rows whose rates are correlated. On the gray screen the arcs form two bundles.",
            "During gratings the bundles stay and new arcs appear among the four bottom rows.",
            "Panel (c) removes the raster and keeps the arcs: blue for the gray screen, green for what the grating added.",
        ],
        lead="As 1c: correlate every unit with every other unit and the recording becomes a network. On a gray screen it already has two bundles of arcs; the grating adds a third.",
        caption="(a) Gray screen: spikes of 14 units, with an arc joining each pair whose rates are correlated (r > 0.35). (b) The same during drifting gratings. (c) The arcs alone: present on the gray screen (blue) and added by the grating (green). PCA returns the blue bundles; bPCA measures them and the spiking noise, and returns green.",
        handoff="The blue arcs are the <b class=\"blue\">redundancy baseline</b>, the green arcs what bPCA ranks, and the <b class=\"red\">noise baseline</b> the counting jitter in every row.",
        strengths=[
            "One picture holds the data and the network, and it is compact enough to share the slot with text.",
            "“Same rows, more arcs” is obvious at a glance.",
        ],
        risks=[
            "Arc diagrams are less familiar than node-link drawings.",
            "Chance correlations produce stray long arcs (one in (a)) that need pruning or a word of explanation.",
        ],
    ),
]

TABLE = [
    ("1 Networks", "“functional connectivity”", "the recording is two networks plus noise; PCA picks the bigger", "spontaneous network / spiking noise", "high", "reads as a connectivity method"),
    ("1b Zoom", "“an edge is a correlation”", "the whole system, and one pair opened up", "pair scatter on gray screen / dot jitter", "medium", "busy"),
    ("1c Raster to network", "“that's my raster”", "gray screen already has blocks; the grating adds one", "matrix (b) is Σ²ᵣ", "medium", "seven panels"),
    ("1d Flipbook", "“fire together, wire together”", "units that light up together get an edge, stimulus or not", "blue network / lone flicker", "high", "slogan suggests plasticity"),
    ("1e Arcs", "“network on the raster”", "same rows, more arcs", "blue arcs / noise", "medium", "unfamiliar drawing"),
    ("2 State space", "“noise-correlation scatter”", "PC1 is the shared gain; the stimulus is across it", "blue ellipse / red disc", "low", "the standard cartoon"),
    ("3 ΔF/F", "“that's ΔF/F”", "λ − 1 is ΔF/F for covariance", "F₀ / dark frame", "medium", "does not show why PCA fails"),
    ("4 Control", "“where is the control?”", "the baselines are already in the session", "control 1 / control 2", "low", "not a picture of the problem"),
    ("5 Ongoing", "“Arieli, Stringer”", "evoked rides on ongoing; PCA follows ongoing", "ongoing activity / spiking noise", "medium", "time domain is not the analysis"),
]

CSS = """
<style>
/* Layout: one reading column, 72ch wide, with full-bleed figure cards; the poster's own palette as tokens. */
:root {
  --bg: #f7f8f9; --fg: #100f0d; --muted: #5f656d; --panel: #ffffff; --line: #d9dde2;
  --blue: #3f6fd1; --red: #e0283f; --green: #4f8a32; --dark: #26282f; --chip: #eef1f2;
  --display: 'Source Sans 3', 'Segoe UI', Helvetica, Arial, sans-serif;
  --body: 'Source Sans 3', 'Segoe UI', Helvetica, Arial, sans-serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #16181c; --fg: #eceef1; --muted: #a3a9b2; --panel: #1f2227; --line: #343940;
  --blue: #7ea1ea; --red: #ff6b7c; --green: #8fc46b; --dark: #0f1114; --chip: #272b31; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #16181c; --fg: #eceef1; --muted: #a3a9b2; --panel: #1f2227; --line: #343940;
  --blue: #7ea1ea; --red: #ff6b7c; --green: #8fc46b; --dark: #0f1114; --chip: #272b31; color-scheme: dark }
body { background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 17px; line-height: 1.5;
  padding-block: 32px 64px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.wrap { max-width: 1100px; margin: 0 auto; }
.col { max-width: 72ch; }
h1, h2, h3 { font-family: var(--display); text-wrap: balance; line-height: 1.15; margin: 0; }
h1 { font-size: clamp(2rem, 5vw, 3rem); font-weight: 700; letter-spacing: -0.01em; }
h2 { font-size: clamp(1.4rem, 3vw, 1.9rem); font-weight: 700; }
h3 { font-size: 1.05rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }
p { margin: 0; }
.eyebrow { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 600; }
header { display: grid; gap: 14px; padding-block: 8px 28px; border-bottom: 1px solid var(--line); margin-bottom: 36px; }
nav { display: flex; flex-wrap: wrap; gap: 8px; }
nav a { text-decoration: none; color: var(--fg); background: var(--chip); border-radius: 999px; padding: 6px 14px; font-size: 0.95rem; font-weight: 600; }
nav a:hover, nav a:focus-visible { outline: 2px solid var(--blue); outline-offset: 1px; }
nav a.sub { font-weight: 400; }
section.variant { padding-left: 16px; border-left: 3px solid var(--line); }
.jobs { display: grid; gap: 8px; padding-left: 1.3em; margin: 0; }
section.option { display: grid; gap: 22px; padding-block: 36px; border-bottom: 1px solid var(--line); }
.head { display: grid; gap: 6px; }
.frame { color: var(--muted); font-weight: 600; }
figure { margin: 0; background: #ffffff; border: 1px solid var(--line); border-radius: 12px; padding: 12px; overflow-x: auto; }
figure .fig { width: 100%; height: auto; display: block; min-width: 640px; }
figcaption { font-size: 0.92rem; color: #5f656d; margin-top: 8px; }
.two { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 28px; }
.two > div { min-width: 0; display: grid; gap: 10px; align-content: start; }
ol.reads { padding-left: 1.3em; margin: 0; display: grid; gap: 8px; }
blockquote { margin: 0; padding: 10px 14px; border-left: 3px solid var(--blue); background: var(--chip); border-radius: 0 8px 8px 0; }
blockquote.cap { border-left-color: var(--muted); font-size: 0.97rem; }
ul.sr { padding-left: 1.2em; margin: 0; display: grid; gap: 6px; }
.blue { color: var(--blue); } .red { color: var(--red); } .green { color: var(--green); }
table { border-collapse: collapse; width: 100%; font-size: 0.95rem; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { color: var(--muted); font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
.tablewrap { overflow-x: auto; }
.rec { display: grid; gap: 14px; padding-block: 36px; }
.rec ul { padding-left: 1.2em; margin: 0; display: grid; gap: 6px; }
footer { color: var(--muted); font-size: 0.9rem; padding-top: 28px; border-top: 1px solid var(--line); }
code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.9em; background: var(--chip); padding: 1px 5px; border-radius: 4px; }
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
</style>
"""


def section(o, variant=False):
    reads = "".join(f"<li>{r}</li>" for r in o["reads"])
    strengths = "".join(f"<li>{r}</li>" for r in o["strengths"])
    risks = "".join(f"<li>{r}</li>" for r in o["risks"])
    eyebrow = f"Variant {o['n']} of Option 1 \u00b7 {o['frame']}" if variant else f"Option {o['n']} \u00b7 {o['frame']}"
    return f"""
<section class="option{' variant' if variant else ''}" id="option-{o['n']}">
  <div class="head">
    <span class="eyebrow">{eyebrow}</span>
    <h2>{o['pitch']}</h2>
    <p class="frame">Proposed subtitle for the Section 1 header bar.</p>
  </div>
  <figure>{inline_svg(o['file'])}<figcaption>Draft at the Section 1 figure size (1460 × 780 poster units). Source: <code>drafts/opening/{o['file']}</code>.</figcaption></figure>
  <div class="two">
    <div>
      <h3>How a neuroscientist reads it</h3>
      <ol class="reads">{reads}</ol>
    </div>
    <div>
      <h3>Lead text (replaces the intro box)</h3>
      <blockquote>{o['lead']}</blockquote>
      <h3>Caption</h3>
      <blockquote class="cap">{o['caption']}</blockquote>
      <h3>Hand-off to Section 2</h3>
      <p>{o['handoff']}</p>
    </div>
  </div>
  <div class="two">
    <div><h3>Strengths</h3><ul class="sr">{strengths}</ul></div>
    <div><h3>Risks</h3><ul class="sr">{risks}</ul></div>
  </div>
</section>"""


def main(out):
    rows = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in TABLE)
    nav = "".join(f'<a href="#option-{o["n"]}">{o["n"]}. {o["frame"]}</a>' for o in OPTIONS[:1])
    nav += "".join(f'<a href="#option-{v["n"]}" class="sub">{v["n"]}. {v["frame"]}</a>' for v in VARIANTS)
    nav += "".join(f'<a href="#option-{o["n"]}">{o["n"]}. {o["frame"]}</a>' for o in OPTIONS[1:])
    body_sections = (section(OPTIONS[0])
                     + f'<section class="rec" id="variants"><h2>Option 1, made explicit</h2><p class="col">{VARIANTS_INTRO}</p></section>'
                     + "".join(section(v, variant=True) for v in VARIANTS)
                     + "".join(section(o) for o in OPTIONS[1:]))
    html = f"""<title>Five Poster Openings</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,300;0,400;0,600;0,700;1,400&display=swap">
{CSS}
<div class="wrap">
<header>
  <span class="eyebrow">SfN 2026 poster · Section 1 · workshop</span>
  <h1>Five ways to open the poster</h1>
  <div class="col" style="display:grid;gap:10px">
    <p>A neuroscientist gives the first column about thirty seconds. In that time it has to do three things:</p>
    <ol class="jobs">
      <li>Make them feel the problem in their own terms: the leading principal components of a population recording are usually not the stimulus.</li>
      <li>Name the two nuisance sources in words they already use. The paper calls them <em>redundancy</em> (neurons co-fluctuate without a stimulus) and <em>noise</em> (spike counts are finite). Neither word is what a neuroscientist would say first.</li>
      <li>Set up the two baselines, so that Section 2's <span class="blue"><b>redundancy baseline</b></span> and <span class="red"><b>noise baseline</b></span> land as names for things the reader has already seen.</li>
    </ol>
    <p>The current opening (two balls in a stadium, filmed by cameras) is a clean thought experiment, but it costs the reader four translations before the point lands: balls are neurons, cameras are recorded units, the rod is the stimulus, the seven redundant cameras are shared inputs. Each option below draws the problem directly in neural data, and comes with a subtitle for the header bar, a lead paragraph, a caption, and the sentence that hands over to Section 2.</p>
  </div>
  <nav>{nav}</nav>
</header>
{body_sections}
<section class="rec" id="compare">
  <h2>Side by side</h2>
  <div class="tablewrap"><table>
    <thead><tr><th>Option</th><th>First thought</th><th>Teaches in ten seconds</th><th>Section 2 words set up as</th><th>Visual novelty</th><th>Main risk</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
</section>
<section class="rec" id="recommendation">
  <h2>Recommendation</h2>
  <div class="col" style="display:grid;gap:12px">
    <p>Use <b>Option 2 as the figure</b>, with <b>Option 4 reduced to a one-line strip</b> under it saying where the three inputs come from. It is the picture neuroscientists already use to think about population coding, so there is nothing to translate; it previews Section 3's panels (f)–(h), so the poster reads as one story from column 1 to column 2; and the headline numbers (31° to 9°) can sit in the opening. Then borrow Option 3's gloss for Section 2's equation (“λ − 1 is ΔF/F for covariance, one direction at a time”), the quickest way to make the eigenvalue mean something.</p>
    <p>If the whole-system view matters more, take the network family. Among its variants, <b>1c</b> is the safest (every element is a real analysis object, and its matrices are literally Σ²ᵣ and Σ²), <b>1d</b> is the most memorable and the only one that teaches what an edge means without a scatter plot or a matrix, <b>1b</b> is the best bridge to the state-space picture, and <b>1e</b> is the most compact. If the opening is to be a network, use <b>1d</b> as the figure, with its slogan as the header subtitle, and reuse 1c's matrices (b) and (e) beside Section 2's equation, where they become Σ²ᵣ and Σ² without renaming. Keep Option 2's panel (c) in Section 2, where it already lives, so the two-neuron geometry still appears once.</p>
    <p>By audience: mostly systems electrophysiology, Option 2; mostly imaging, Option 3; a crowd that asks “do I need new data?”, Option 4; neighbours presenting spontaneous activity, Option 5.</p>
    <p>Hybrids that fit the slot:</p>
    <ul>
      <li><b>2 + 4</b>: Option 2's three panels, plus Option 4's timeline as a 120-unit strip beneath them.</li>
      <li><b>1 + 2</b>: Option 1's panels (a), (b), (d) as a top strip (what the recording contains), Option 2's panel (c) beside them (what each method does with it).</li>
      <li><b>2 + 3</b>: Option 2 as the figure, Option 3's two formulas as the gloss beside Section 2's equation.</li>
    </ul>
  </div>
</section>
<footer>
  <p>Drafts live in <code>drafts/opening/</code> of the SfN_2026 repository (branch <code>claude/sfn-2026-poster-opening-dei5wp</code>): the SVGs, PNG previews, the generator <code>make_drafts.py</code>, and <code>README.md</code> with these notes. At poster scale the sentences inside the drawings should move to the caption box; only labels of 34 px and up stay in the figure.</p>
</footer>
</div>
"""
    with open(out, "w") as f:
        f.write(html)
    print("wrote", out, len(html), "bytes")


if __name__ == "__main__":
    main(sys.argv[1])
