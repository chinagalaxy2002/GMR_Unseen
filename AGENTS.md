# Repository Guidelines

## Project Structure & Module Organization

- `models/` implements Moment-DETR-GMR, QD-DETR-GMR, and FlashVTG-GMR; `training/` contains their datasets, training, and inference entry points.
- `configs/` holds model, dataset, and feature configurations. `scripts/` provides training launchers, dataset construction, validation, and analysis tools.
- `data/release/semantic_existence_v1/` and `semantic_existence_v2/` contain versioned Charades-derived annotations; `data/label/` contains the separate Soccer-GMR benchmark.
- `eval/` contains benchmark evaluation utilities. Root `test_*.py` files are exploratory diagnostics.
- `experiments/` stores experiment-specific code and reports; `docs/` contains research plans, handoffs, and published metrics. `assets/` contains presentation assets. Local features and checkpoints belong in `features/` and `results/`.

## Build, Test, and Development Commands

Run commands from the repository root:

```bash
python -m pip install -r requirements.txt
python scripts/validate_release.py
bash scripts/train_semantic_existence_qd_detr.sh
bash scripts/infer_semantic_existence_qd_detr.sh
```

These install core dependencies, validate the v1 release, train QD-DETR-GMR, and run its inference workflow. Set `CLIP_FEAT_DIR`, `SLOWFAST_FEAT_DIR`, and `TEXT_FEAT_DIR` to prepared feature directories before training. Inspect launcher defaults and set a fresh `RESULTS_DIR` because training enables overwrite. Dataset construction additionally uses `requirements-dataset.txt`; FlashVTG has `requirements-flash-vtg.txt`. There is no compilation step.

## Coding Style & Naming Conventions

Use four-space Python indentation, `snake_case` functions and variables, and `PascalCase` classes. Follow surrounding code and preserve JSONL field names such as `qid`, `vid`, and `relevant_windows`. Use descriptive script names such as `validate_release.py`. Shell launchers should use `set -euo pipefail` and configurable paths. No shared formatter or linter configuration is established.

## Testing Guidelines

No centralized test framework or coverage threshold is established. Run the relevant dataset validator for annotation changes and a small training/inference smoke check for model changes. Verify positive and empty-window examples. Exploratory `test_*.py` scripts may require extra dependencies, local predictions, or machine-specific paths; inspect them before running.

## Commit & Pull Request Guidelines

Recent commits use imperative descriptions such as “Clarify core research question at start of README.” Keep commits focused. PRs should describe the change, affected models/splits, validation commands, and resulting metrics; link relevant issues or experiment reports. Include screenshots for website changes.

## Research Protocol & Artifacts

Train strict unseen experiments on S+/S− only. Select checkpoints, thresholds, and hyperparameters using seen validation only. Preserve release manifests and checksums; document intentional dataset revisions. Keep videos, features, credentials, and checkpoints out of commits, following `.gitignore`. Record seeds and configuration when reporting results.

## Required Generalization Reporting

For all subsequent GMR experiments, summarize AUROC, actual rejection F1 (Rej-F1), and end-to-end G-mIoU@1 separately on Seen (S+/S−) and Unseen (U+/U−), with Performance Gap = Seen − Unseen in percentage points. Preserve negative gaps as improvements. Also report overall Rej-F1, overall rejection rate, S+ and U+ false rejection rates, and overall G-mIoU@1. Include subset positive/negative counts and video-cluster bootstrap 95% CIs, with frozen Seen-validation checkpoints and thresholds. Rej-F1 and G-mIoU depend on subset class proportions; explain this limitation when interpreting their gaps.

For comparisons against the same-split, same-backbone baseline, report Unseen Net Gain, Seen Change, and Gap Reduction for all three metrics, with paired bootstrap intervals; standalone baseline relative changes are undefined. Report each split and backbone separately; formal five-split macro averages require all five completed splits. Mark incomplete runs and partial summaries explicitly. Save Markdown tables, CSV/JSON metrics, frozen predictions, calibration metadata, and bootstrap artifacts. `scripts/summarize_gmr_degradation.py` provides the Seen/Unseen rejection and localization summary for standardized `predictions.npz` outputs.
