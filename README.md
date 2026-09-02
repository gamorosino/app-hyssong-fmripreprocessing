# hyssong-fmripreprocessing

Post-fMRIPrep nuisance regression and smoothing (AFNI/FSL), ported from Hayoung Song's fmripreprocessing notebook

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

## Inputs

- `bold` (neuro/func/task)
- `mask` (neuro/mask)
- `confounds` (neuro/regressors)

## Outputs

- `preproc_bold` (neuro/func/task) -- Brain-masked, intensity-normalized, nuisance-regressed (24 motion parameters + WM + CSF + global signal + high-pass), and spatially smoothed BOLD, ready for functional-connectivity analyses.

## Usage

Brainlife.io: run via `braise-app-run`/`braise-app-pipeline` (once registered
with `braise-app-create`), or the web UI.

Locally (outside brainlife): copy `config.json.example` to `config.json`,
fill in real file paths, then run `./main` from this directory. `main` pulls
its own container (`singularity exec docker://...`) -- no local install of
the underlying tool needed, only Singularity itself.

Entrypoint: `main.py`

## Authors

- Gabriele Amorosino <g.amorosino@gmail.com>

## License

MIT, see `LICENSE`.
