# Soccer-GMR-Unseen v1 baseline evaluation

Completed settings: 15/15. Seed 3407; fresh Seen-only training; native Seen-validation checkpoint selection; threshold maximizes BA over 91 Seen-validation percentiles (5–95), earliest tie. AUROC 0–1; gap in pp. Absolute Unseen AUROC 95% CI: 2,000 video-cluster bootstrap draws, seed 3407; fixed checkpoint and threshold. Macro is equal-weight over all five groups, with shared-video draws. Gains/change/reduction are undefined for standalone baselines and shown as —.

| Evaluation Variant | Seen AUROC | Unseen AUROC | Performance Gap | Unseen Net Gain | 95% CI (Bootstrap) | Seen Change | Gap Reduction |
|---|---:|---:|---:|---:|---|---:|---:|
| A1_soccer / Moment-DETR-GMR / Baseline | 0.7795 | 0.6680 | 11.16 | — | [0.6103, 0.7267] absolute | — | — |
| A1_soccer / QD-DETR-GMR / Baseline | 0.7560 | 0.6516 | 10.44 | — | [0.5902, 0.7099] absolute | — | — |
| A1_soccer / FlashVTG-GMR / Baseline | 0.7766 | 0.6786 | 9.80 | — | [0.6230, 0.7328] absolute | — | — |
| A2_soccer / Moment-DETR-GMR / Baseline | 0.7676 | 0.5429 | 22.47 | — | [0.4763, 0.6071] absolute | — | — |
| A2_soccer / QD-DETR-GMR / Baseline | 0.7037 | 0.6508 | 5.29 | — | [0.5857, 0.7125] absolute | — | — |
| A2_soccer / FlashVTG-GMR / Baseline | 0.7664 | 0.5908 | 17.56 | — | [0.5163, 0.6602] absolute | — | — |
| A3_soccer / Moment-DETR-GMR / Baseline | 0.7733 | 0.6214 | 15.19 | — | [0.5610, 0.6809] absolute | — | — |
| A3_soccer / QD-DETR-GMR / Baseline | 0.7106 | 0.6484 | 6.23 | — | [0.5922, 0.7050] absolute | — | — |
| A3_soccer / FlashVTG-GMR / Baseline | 0.7700 | 0.5914 | 17.85 | — | [0.5375, 0.6455] absolute | — | — |
| C1_soccer / Moment-DETR-GMR / Baseline | 0.7717 | 0.5964 | 17.53 | — | [0.5222, 0.6637] absolute | — | — |
| C1_soccer / QD-DETR-GMR / Baseline | 0.7287 | 0.5839 | 14.48 | — | [0.5156, 0.6473] absolute | — | — |
| C1_soccer / FlashVTG-GMR / Baseline | 0.7756 | 0.6131 | 16.24 | — | [0.5432, 0.6818] absolute | — | — |
| C2_soccer / Moment-DETR-GMR / Baseline | 0.7679 | 0.5211 | 24.67 | — | [0.4342, 0.6101] absolute | — | — |
| C2_soccer / QD-DETR-GMR / Baseline | 0.7116 | 0.4498 | 26.18 | — | [0.3714, 0.5317] absolute | — | — |
| C2_soccer / FlashVTG-GMR / Baseline | 0.7725 | 0.5646 | 20.79 | — | [0.4913, 0.6426] absolute | — | — |
| MACRO / Moment-DETR-GMR / Baseline | 0.7720 | 0.5900 | 18.20 | — | [0.5567, 0.6203] absolute | — | — |
| MACRO / QD-DETR-GMR / Baseline | 0.7221 | 0.5969 | 12.52 | — | [0.5627, 0.6305] absolute | — | — |
| MACRO / FlashVTG-GMR / Baseline | 0.7722 | 0.6077 | 16.45 | — | [0.5780, 0.6386] absolute | — | — |

| Backbone Model | Evaluation Branch | Actual Rejection F1 (Rej-F1) | Overall Rejection Rate (RR) | S+ False Rejection Rate (S+ FRR) | U+ False Rejection Rate (U+ FRR) | End-to-end Localization (G-mIoU@1) |
|---|---|---:|---:|---:|---:|---:|
| Moment-DETR-GMR | A1_soccer / Baseline | 76.68% | 68.65% | 46.44% | 57.38% | 51.38% |
| QD-DETR-GMR | A1_soccer / Baseline | 69.54% | 53.96% | 34.52% | 44.26% | 43.12% |
| FlashVTG-GMR | A1_soccer / Baseline | 77.03% | 69.59% | 46.68% | 62.30% | 53.38% |
| Moment-DETR-GMR | A2_soccer / Baseline | 73.08% | 62.02% | 40.29% | 66.36% | 47.09% |
| QD-DETR-GMR | A2_soccer / Baseline | 71.04% | 60.68% | 42.94% | 53.27% | 43.16% |
| FlashVTG-GMR | A2_soccer / Baseline | 79.05% | 76.18% | 52.83% | 72.90% | 56.51% |
| Moment-DETR-GMR | A3_soccer / Baseline | 77.36% | 70.67% | 46.78% | 68.75% | 52.70% |
| QD-DETR-GMR | A3_soccer / Baseline | 75.84% | 72.77% | 52.97% | 69.53% | 50.35% |
| FlashVTG-GMR | A3_soccer / Baseline | 71.03% | 56.16% | 34.78% | 52.34% | 45.86% |
| Moment-DETR-GMR | C1_soccer / Baseline | 77.71% | 73.89% | 50.90% | 79.80% | 53.66% |
| QD-DETR-GMR | C1_soccer / Baseline | 76.00% | 72.37% | 49.82% | 92.93% | 50.32% |
| FlashVTG-GMR | C1_soccer / Baseline | 71.00% | 54.32% | 31.06% | 62.63% | 45.37% |
| Moment-DETR-GMR | C2_soccer / Baseline | 74.75% | 66.05% | 44.15% | 79.45% | 49.28% |
| QD-DETR-GMR | C2_soccer / Baseline | 73.88% | 68.61% | 48.09% | 98.63% | 47.49% |
| FlashVTG-GMR | C2_soccer / Baseline | 69.37% | 52.31% | 30.36% | 69.86% | 43.75% |
| Moment-DETR-GMR | MACRO / Baseline | 75.91% | 68.26% | 45.71% | 70.35% | 50.82% |
| QD-DETR-GMR | MACRO / Baseline | 73.26% | 65.68% | 45.67% | 71.72% | 46.89% |
| FlashVTG-GMR | MACRO / Baseline | 73.50% | 61.71% | 39.14% | 64.01% | 48.98% |

Rej-F1 = 2TN/(2TN+FP+FN), treating rejection as positive. G-mIoU@1 uses the first valid native submitted window (no duration-bound skip), max IoU / number of GT windows; rejected negatives score 1, rejected positives score 0. Each backbone supplies its own localization. See DATA_AUDIT.json, SOURCE_MANIFEST.json, PROTOCOL.json and per-setting calibration, predictions and bootstrap artifacts.


All tables use frozen experiment annotations after missing/invalid-feature exclusions. See FEATURE_EXCLUSIONS.json, EXPERIMENT_DATA_COUNTS.json and per-group FEATURE_FILTERING.json for excluded queries and actual denominators. Original release annotations are preserved.

Seen/Unseen Rej-F1 and G-mIoU@1 gaps: [GENERALIZATION_DROP_COMPARISON.md](GENERALIZATION_DROP_COMPARISON.md).