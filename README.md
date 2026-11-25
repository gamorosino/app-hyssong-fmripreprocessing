<h1 align="center">hyssong-fmripreprocessing</h1>

<p align="center">
  Denoises an fMRIPrep-preprocessed BOLD run with AFNI and FSL: brain masking, intensity normalization, nuisance regression (24 motion, WM, CSF, global signal, high-pass) with frame censoring, and spatial smoothing.
</p>

<p align="center">
  <a href="https://github.com/brainlife/abcd-spec"><img src="https://img.shields.io/badge/ABCD_Spec-v1.1-green.svg" alt="ABCD Spec v1.1"></a>
  <a href="https://doi.org/10.25663/brainlife.app.958"><img src="https://img.shields.io/badge/Brainlife-brainlife.app.958-blue.svg" alt="Run on brainlife.io"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-see_LICENSE-lightgrey.svg" alt="License"></a>
</p>

## At a glance

<!-- brainlife-app:begin (generated from the App manifest; edit the manifest, not this block) -->

> **Denoises an fMRIPrep-preprocessed BOLD run with AFNI and FSL: brain masking, intensity normalization, nuisance regression (24 motion, WM, CSF, global signal, high-pass) with frame censoring, and spatial smoothing.**

Port of Hayoung Song's post-fMRIPrep notebook: masks the BOLD with the fMRIPrep brain mask (3dcalc), scales intensities (fslmaths -inm 10000), builds high-pass and confound regressors (1dBport, 3dDeconvolve), regresses them out while censoring frames flagged by fMRIPrep motion-outlier columns (3dTproject), and smooths with 3dmerge. Use it to prepare task or rest BOLD for functional-connectivity analyses. Inputs must come from the same fMRIPrep run; tr must be set, and fd_thres is only used to report the percentage of high-motion frames.

| | |
|---|---|
| **Inputs** | `neuro/func/task` · `neuro/mask` · `neuro/regressors` |
| **Outputs** | `neuro/func/task` |
| **Container** | `nipreps/fmriprep@sha256:102db5fe8b0a34298f2eb2fd5962ad99ff0a948d258cbf08736fcc1b845cad9f` |
| **Resources** | 4 GB memory · 1 h walltime |
| **Run it** | [doi.org/10.25663/brainlife.app.958](https://doi.org/10.25663/brainlife.app.958) |

#### Inputs

| Input | Datatype | Required | Description |
|---|---|---|---|
| `bold` | `neuro/func/task` | yes | fMRIPrep-preprocessed BOLD (space-MNI152NLin2009cAsym, desc-preproc) |
| `mask` | `neuro/mask` (func) | yes | Brain mask matching the BOLD input (from fMRIPrep) |
| `confounds` | `neuro/regressors` | yes | fMRIPrep confounds regressors.tsv for the same BOLD run |

#### Outputs

| Output | Datatype | Description |
|---|---|---|
| `preproc_bold` | `neuro/func/task` | Brain-masked, intensity-normalized, nuisance-regressed (24 motion parameters + WM + CSF + global signal + high-pass), and spatially smoothed BOLD, ready for functional-connectivity analyses. |

<details>
<summary><b>Parameters</b> (4)</summary>

| Parameter | Type | Default | Description |
|---|---|---|---|
| `tr` | number |  | Repetition time (seconds) of the BOLD acquisition |
| `fd_thres` | number | `0.5` | Framewise displacement threshold (mm) used to flag/censor high-motion frames |
| `fwhm` | number | `5` | Full-width half-max (mm) of the spatial smoothing kernel applied at the end |
| `hpass_cutoff` | number | `0.0078` | High-pass filter cutoff frequency in Hz (default 0.0078 Hz corresponds to a 128s period) |

</details>

<!-- brainlife-app:end -->

## Running the App

### On brainlife.io

Open the App at [doi.org/10.25663/brainlife.app.958](https://doi.org/10.25663/brainlife.app.958), choose `neuro/func/task`, `neuro/mask`, `neuro/regressors` from your project, set the parameters and press **Execute**. The results are saved to your project as `neuro/func/task`.

### Locally

You need [Singularity/Apptainer](https://apptainer.org/) (the App runs in `nipreps/fmriprep@sha256:102db5fe8b0a34298f2eb2fd5962ad99ff0a948d258cbf08736fcc1b845cad9f`), [`jq`](https://jqlang.github.io/jq/).

1. Clone this repository.
2. Create `config.json` with the paths to your inputs and the parameters:

   ```json
   {
       "bold": "/path/to/bold/bold",
       "mask": "/path/to/mask/mask",
       "confounds": "/path/to/confounds/confounds",
       "tr": "",
       "fd_thres": 0.5,
       "fwhm": 5,
       "hpass_cutoff": 0.0078
   }
   ```

3. Run `./main`.

## Troubleshooting

- **no output produced**: Check that the BOLD, mask and confounds come from the same fMRIPrep run and that tr is set.

## Origin

Ported from the single-subject/task loop in `preprocess_afterfmriprep.ipynb`
(https://github.com/hyssong/fmripreprocessing), by Hayoung Song
(hyssong@uchicago.edu). The original notebook is included here as
`original_preprocess_afterfmriprep.ipynb` for reference; `main.py` runs the
same six processing steps once per brainlife dataset (one BOLD run at a
time) instead of looping over a hardcoded subject/task list.

Runs inside the existing `nipreps/fmriprep:20.2.3` container (also referenced
by the original repo's `fmriprepscript.sbatch`), which already bundles AFNI
and FSL -- no new image was built for this app.

## Citing

If you use this App, please cite it, the software it builds on and brainlife.io:

- hyssong-fmripreprocessing. brainlife.io App. [doi:10.25663/brainlife.app.958](https://doi.org/10.25663/brainlife.app.958)
- Jenkinson et al. FSL. *NeuroImage* 62:782-790 (2012). [doi:10.1016/j.neuroimage.2011.09.015](https://doi.org/10.1016/j.neuroimage.2011.09.015)
- Cox. AFNI: Software for Analysis and Visualization of Functional Magnetic Resonance Neuroimages. *Computers and Biomedical Research* 29:162-173 (1996). [doi:10.1006/cbmr.1996.0014](https://doi.org/10.1006/cbmr.1996.0014)
- Esteban et al. fMRIPrep: a robust preprocessing pipeline for functional MRI. *Nature Methods* 16:111-116 (2018). [doi:10.1038/s41592-018-0235-4](https://doi.org/10.1038/s41592-018-0235-4)
- Hayashi S, Caron BA, Heinsfeld AS, et al. brainlife.io: a decentralized and open-source cloud platform to support neuroscience research. *Nature Methods* 21:809–813 (2024). [doi:10.1038/s41592-024-02237-2](https://doi.org/10.1038/s41592-024-02237-2)
- Avesani P, McPherson B, Hayashi S, et al. The open diffusion data derivatives, brain data upcycling via integrated publishing of derivatives and reproducible open cloud services. *Scientific Data* 6:69 (2019). [doi:10.1038/s41597-019-0073-y](https://doi.org/10.1038/s41597-019-0073-y)

## Authors

- Gabriele Amorosino

## License

See [LICENSE](LICENSE).
