#!/usr/bin/env bash
# Pull the current versions of the poster's karl-generated figures into figures/src/.
# See figures/PROVENANCE.md for what each file is, which script makes it, and which poster
# elements use it. This only copies outputs; regenerate on karl first if the script changed.
#
#   figures/fetch_figures.sh            # copy everything
#   figures/fetch_figures.sh -n         # dry run: show which files differ from karl
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/src"

LAB=code/BaselinePCALab.jl                 # relative to karl:~ (= /suphys/bhar9988)
FILES=(                                    # karl path -> figures/src/<basename>
    "$LAB/plots/Fig1_schematic.svg"          # s1-cameras, s2-baselines
    "$LAB/plots/Fig1_schematic.png"
    "$LAB/plots/Fig1_schematics_bpca.svg"
    "$LAB/plots/Fig3_case_studies.svg"       # s3-results, s4-results
    "$LAB/plots/Fig3_case_studies.png"
    "$LAB/plots/trial_stack_covariance.svg"  # s3-cards
    "$LAB/plots/trial_stack_covariance.png"
    "$LAB/_research/neuropixels_nugget/nugget_construction.png"
    "$LAB/_research/neuropixels_nugget/nugget_poster.svg"   # s3-noise
    "$LAB/_research/neuropixels_nugget/nugget_poster.png"
    "$LAB/_research/phantom_correlated/phantom_construction.svg"
    "$LAB/_research/phantom_correlated/phantom_construction.png"
    "$LAB/_research/phantom_correlated/phantom_poster.svg"  # s4-schematic
    "$LAB/_research/phantom_correlated/phantom_poster.png"
)

if [[ ${1:-} == -n ]]; then
    remote=$(ssh karl "md5sum ${FILES[*]}" 2>/dev/null)
    while read -r sum path; do
        f=$(basename "$path")
        [[ -f $f && $(md5sum <"$f" | cut -d' ' -f1) == "$sum" ]] && s=same || s=DIFFERS
        printf '%-8s %s\n' "$s" "$f"
    done <<<"$remote"
    exit
fi

scp -p "${FILES[@]/#/karl:}" . 2>&1 | grep -v -E 'post-quantum|store now|upgraded' || true
ls -l --time-style=long-iso "${FILES[@]##*/}"
