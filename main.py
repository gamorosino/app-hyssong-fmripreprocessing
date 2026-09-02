#!/usr/bin/env python3
"""Post-fMRIPrep nuisance regression and smoothing for a single BOLD run.

Ported from the single-subject/task loop in Hayoung Song's
`preprocess_afterfmriprep.ipynb` (github.com/hyssong/fmripreprocessing),
generalized to run once per brainlife dataset (one BOLD run at a time)
instead of looping over a hardcoded subject/task list.

Steps (unchanged from the source notebook):
  1. Apply the brain mask to the preprocessed EPI (AFNI 3dcalc)
  2. Intensity normalization (FSL fslmaths -inm 10000)
  3. High-pass filter regressors, 128s cutoff (AFNI 1dBport + 1d_tool.py)
  4. Design matrix combining high-pass + fMRIPrep confounds + polort (AFNI 3dDeconvolve)
  5. Nuisance regression with frame censoring (AFNI 3dTproject)
  6. Spatial smoothing (AFNI 3dmerge)
"""
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

# 24 motion parameters + global signal + CSF + white matter, exactly as in
# the source notebook's `variables` list.
CONFOUND_COLUMNS = [
    "trans_x", "trans_y", "trans_z", "rot_x", "rot_y", "rot_z",
    "trans_x_derivative1", "trans_y_derivative1", "trans_z_derivative1",
    "rot_x_derivative1", "rot_y_derivative1", "rot_z_derivative1",
    "trans_x_derivative1_power2", "trans_y_derivative1_power2",
    "trans_z_derivative1_power2", "rot_x_derivative1_power2",
    "rot_y_derivative1_power2", "rot_z_derivative1_power2",
    "trans_x_power2", "trans_y_power2", "trans_z_power2", "rot_x_power2",
    "rot_y_power2", "rot_z_power2", "global_signal", "csf", "white_matter",
]


def run(cmd):
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def main():
    with open("config.json") as f:
        config = json.load(f)

    bold = str(config["bold"])
    mask = str(config["mask"])
    confounds_tsv = str(config["confounds"])
    tr = float(config["tr"])
    fd_thres = float(config.get("fd_thres", 0.5))
    fwhm = float(config.get("fwhm", 5))
    hpass_cutoff = float(config.get("hpass_cutoff", 0.0078))

    out_dir = "preproc_bold"
    os.makedirs(out_dir, exist_ok=True)

    t = pd.read_csv(confounds_tsv, delimiter="\t")

    # ------ quality check: head motion (reported only, matches notebook) ------ #
    fd = t["framewise_displacement"]
    outlier_pct = 100 * np.sum(fd >= fd_thres) / (len(fd) - np.sum(pd.isna(fd)))
    print(f"meanFD: {np.round(np.nanmean(fd), 2)}, %FD>={fd_thres}: {np.round(outlier_pct, 2)}%")

    # ------ outliers (censor) vector ------ #
    outlier_columns = [c for c in t.columns if c.startswith("motion_outlier") or c.startswith("non_steady_state_outlier")]
    outliers = np.zeros((len(t),)) + np.nan
    flagged = np.sum(np.array(t[outlier_columns]), 1) > 0 if outlier_columns else np.zeros(len(t), dtype=bool)
    outliers[flagged] = 0
    outliers[~flagged] = 1
    outliers_1d = os.path.join(out_dir, "outliers.1D")
    pd.DataFrame(outliers).to_csv(outliers_1d, index=False, header=False)

    # ------ confound regressors matrix ------ #
    for col in CONFOUND_COLUMNS:
        if pd.isna(t[col].iloc[0]):
            t.loc[0, col] = t[col].iloc[1]
    regressors = t[CONFOUND_COLUMNS]
    regressors_1d = os.path.join(out_dir, "confounds_regressors.1D")
    regressors.to_csv(regressors_1d, index=False, header=False)

    # ------ 1. mask the preprocessed EPI ------ #
    masked = os.path.join(out_dir, "1_fmriprep_output.nii.gz")
    run(["3dcalc", "-a", bold, "-b", mask, "-expr", "(a*b)", "-prefix", masked])

    # ------ 2. intensity normalization ------ #
    normalized = os.path.join(out_dir, "2_intensity_normalization.nii.gz")
    run(["fslmaths", masked, "-inm", "10000", normalized])

    # ------ 3. high-pass filter regressors ------ #
    # `1d_tool.py -write` here only strips 1dBport's comment lines into a
    # clean numeric table; the container's bundled 1d_tool.py is a Python 2
    # script that crashes under Python 3, so do that reformatting directly.
    hpass_raw = os.path.join(out_dir, "tmp_rm.hpass.1D")
    with open(hpass_raw, "w") as f:
        subprocess.run(
            ["1dBport", "-input", normalized, "-TR", str(tr), "-band", "0", str(hpass_cutoff), "-nozero"],
            check=True, stdout=f,
        )
    hpass_1d = os.path.join(out_dir, "highpass_regressors.1D")
    with open(hpass_raw) as src, open(hpass_1d, "w") as dst:
        for line in src:
            if not line.lstrip().startswith("#") and line.strip():
                dst.write(line)
    os.remove(hpass_raw)

    # ------ 4. combined design matrix ------ #
    xmat = os.path.join(out_dir, "xmat.1D")
    run([
        "3dDeconvolve", "-input", normalized,
        "-ortvec", hpass_1d, "highpass",
        "-ortvec", regressors_1d, "confounds",
        "-polort", "1",
        "-fout", "-tout", "-x1D", xmat,
        "-fitts", "fitts", "-errts", "errts", "-x1D_stop", "-bucket", "stats",
    ])

    # ------ 5. regress out nuisance variables, censoring flagged frames ------ #
    nuisance_regressed = os.path.join(out_dir, "3_nuissance_regressed.nii.gz")
    run([
        "3dTproject", "-polort", "0", "-input", normalized,
        "-ort", xmat,
        "-censor", outliers_1d, "-cenmode", "ZERO",
        "-prefix", nuisance_regressed,
    ])

    # ------ 6. spatial smoothing ------ #
    smoothed = os.path.join(out_dir, "bold.nii.gz")
    run(["3dmerge", "-quiet", "-1blur_fwhm", str(fwhm), "-doall", "-prefix", smoothed, nuisance_regressed])

    print(f"done: {smoothed}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"command failed: {e}", file=sys.stderr)
        sys.exit(1)
