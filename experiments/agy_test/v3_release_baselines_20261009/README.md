# Semantic Existence v3: completed backbone baselines

All 15 settings (5 semantic holdout splits × 3 backbones) completed successfully. Final evaluation finished at 2026-10-10 04:23 Asia/Shanghai. Dataset: [clean v3 release](../../../data/release/semantic_existence_v3_release/README.md). These results supersede initial-v3-snapshot baseline numbers for this clean release; historical DDV and v1/v2 results elsewhere in the repository use different data.

## Results

- [Seen–Unseen degradation and 95% CIs](evaluation/GENERALIZATION_DROP_COMPARISON.md): AUROC, rejection F1 and end-to-end G-mIoU@1 for every split/backbone and complete five-split macros.
- [Original evaluation tables](evaluation/STANDARD_EVALUATION.md): overall rejection F1, rejection rate, S+/U+ false rejection rates, G-mIoU@1 and absolute Unseen AUROC CI.
- [CSV](evaluation/degradation_metrics.csv), [JSON](evaluation/degradation_metrics.json), [bootstrap intervals](evaluation/degradation_bootstrap.json).

Five-split equal-weight macro averages:

| Backbone | Seen AUROC | Unseen AUROC | AUROC Gap (pp) | Seen Rej-F1 | Unseen Rej-F1 | Rej-F1 Gap (pp) | Seen G-mIoU@1 | Unseen G-mIoU@1 | G-mIoU Gap (pp) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Moment-DETR-GMR | 0.7238 | 0.5224 | 20.14 | 50.51% | 22.25% | 28.27 | 34.54% | 25.51% | 9.03 |
| QD-DETR-GMR | 0.7413 | 0.5337 | 20.76 | 51.30% | 30.61% | 20.68 | 34.86% | 28.02% | 6.84 |
| FlashVTG-GMR | 0.7543 | 0.5647 | 18.96 | 53.36% | 37.09% | 16.27 | 41.75% | 34.44% | 7.31 |

Gap = Seen − Unseen; positive means deterioration, negative means improvement. AUROC measures existence-score ranking; Rej-F1 evaluates rejection at the frozen Seen-validation threshold; G-mIoU evaluates rejection and localization jointly. Rejected negatives score 1; rejected positives score 0; accepted queries use each backbone's own first valid native top-1 window. Rej-F1 and G-mIoU depend on class proportions, so a negative gap alone does not establish better semantic generalization. For example, C2 has U+ FRR about 91–98% despite negative rejection/localization gaps.

## Protocol and provenance

Seed 3407, fresh S+/S− training, maximum 100 epochs, early stop after 27 validations without checkpoint improvement. Checkpoints use native Seen-validation localization selection. Decision threshold maximizes balanced accuracy over 91 Seen-validation percentile candidates (5–95), earliest tie; accept if score >= threshold. Moment/QD read native four-decimal sigmoid scores, Flash reads six-decimal logits to avoid probability-rounding saturation. All 4,611 test rows per group are retained. CIs use 2,000 shared-video cluster bootstrap draws, seed 3407, frozen models and thresholds; macros pair draws across groups. These CIs measure test sampling variation, not training-seed variation.

- `RELEASE_VALIDATION.json`, `DATA_AUDIT.json`: dataset validation and snapshot hashes; all 45 group data files match the clean release in this branch.
- `PROTOCOL.json`, `SOURCE_MANIFEST.json`, `native_source/`: fixed recipe and exact training/inference source snapshot.
- `QUEUE_STATUS.json`, `PIPELINE_EXIT.json`, `FINAL_EVALUATION_STATUS.json`: successful completion records.
- `EVALUATOR_PARITY.json`: all eight historical reference metrics matched within 1e-7; historical values are used only for arithmetic verification.
- `groups/<group>/evaluation/<backbone>/`: frozen calibration, standardized test predictions, bootstrap draws and metrics.
- `groups/<group>/runs/<backbone>/test/*.jsonl.gz`: losslessly compressed native test predictions.
- `groups/<group>/frozen_checkpoints/<backbone>/`: checkpoint SHA-256 manifest and compressed best-validation predictions; Flash options are also included.
- `PUBLICATION_MANIFEST.json`: file sizes and SHA-256 checksums.

Weights, video/text features, caches and training console logs are not published. Native predictions are gzip-compressed; decompress them to their original filenames when using the native evaluation scripts. Original filesystem paths in provenance/options describe the training machine and must be adapted for another machine. Training scripts preserve the original local feature setup, including exact-query feature provenance from the initial-v3 manifest; they require prepared features and do not download them automatically. Training-data copies under groups are omitted because their exact clean-release counterparts are already published.

## Recompute degradation tables without retraining

With NumPy installed, from repository root:

```bash
python scripts/summarize_gmr_degradation.py --experiment experiments/agy_test/v3_release_baselines_20261009
```

This recomputes Seen/Unseen rejection and localization metrics and 2,000-draw video-cluster intervals from the included frozen predictions, and retains the published AUROC results. The training/inference scripts are archived for provenance; do not launch the original machine-specific training queue to recompute these tables.
