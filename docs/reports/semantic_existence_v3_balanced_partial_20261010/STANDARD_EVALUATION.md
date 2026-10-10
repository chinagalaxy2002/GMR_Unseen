# Balanced Semantic Existence v3 baseline evaluation

Completed settings: 8/15. Seed 3407; fresh Seen-only training; native Seen-validation checkpoint selection; threshold maximizes BA over 91 Seen-validation percentiles (5–95), earliest tie. AUROC 0–1; gap in pp. Absolute Unseen AUROC 95% CI: 2,000 video-cluster bootstrap draws, seed 3407; fixed checkpoint and threshold. Macro is equal-weight over all five groups, with shared-video draws. Gains/change/reduction are undefined for standalone baselines and shown as —.

| Evaluation Variant | Seen AUROC | Unseen AUROC | Performance Gap | Unseen Net Gain | 95% CI (Bootstrap) | Seen Change | Gap Reduction |
|---|---:|---:|---:|---:|---|---:|---:|
| A1_v3 / Moment-DETR-GMR / Baseline | 0.7278 | 0.6487 | 7.91 | — | [0.6182, 0.6787] absolute | — | — |
| A1_v3 / QD-DETR-GMR / Baseline | 0.5352 | 0.5186 | 1.66 | — | [0.4883, 0.5514] absolute | — | — |
| A1_v3 / FlashVTG-GMR / Baseline | 0.7813 | 0.6814 | 9.99 | — | [0.6524, 0.7105] absolute | — | — |
| A2_v3 / Moment-DETR-GMR / Baseline | 0.7349 | 0.6665 | 6.84 | — | [0.6227, 0.7122] absolute | — | — |
| A2_v3 / QD-DETR-GMR / Baseline | 0.5684 | 0.5127 | 5.57 | — | [0.4642, 0.5601] absolute | — | — |
| A3_v3 / Moment-DETR-GMR / Baseline | 0.7265 | 0.6421 | 8.44 | — | [0.5977, 0.6859] absolute | — | — |
| A3_v3 / QD-DETR-GMR / Baseline | 0.5351 | 0.5585 | -2.34 | — | [0.5038, 0.6086] absolute | — | — |
| C1_v3 / Moment-DETR-GMR / Baseline | 0.7308 | 0.6264 | 10.45 | — | [0.5841, 0.6742] absolute | — | — |

| Backbone Model | Evaluation Branch | Actual Rejection F1 (Rej-F1) | Overall Rejection Rate (RR) | S+ False Rejection Rate (S+ FRR) | U+ False Rejection Rate (U+ FRR) | End-to-end Localization (G-mIoU@1) |
|---|---|---:|---:|---:|---:|---:|
| Moment-DETR-GMR | A1_v3 / Baseline | 67.16% | 58.07% | 39.76% | 61.74% | 47.09% |
| QD-DETR-GMR | A1_v3 / Baseline | 63.19% | 78.32% | 75.04% | 78.02% | 43.62% |
| FlashVTG-GMR | A1_v3 / Baseline | 70.08% | 55.79% | 32.31% | 62.08% | 52.87% |
| Moment-DETR-GMR | A2_v3 / Baseline | 67.09% | 51.45% | 34.80% | 35.43% | 47.09% |
| QD-DETR-GMR | A2_v3 / Baseline | 52.38% | 45.11% | 38.61% | 66.37% | 32.65% |
| Moment-DETR-GMR | A3_v3 / Baseline | 63.77% | 43.64% | 27.04% | 34.89% | 44.12% |
| QD-DETR-GMR | A3_v3 / Baseline | 39.63% | 29.73% | 28.81% | 14.89% | 28.64% |
| Moment-DETR-GMR | C1_v3 / Baseline | 65.15% | 46.10% | 29.69% | 27.46% | 46.11% |

Rej-F1 = 2TN/(2TN+FP+FN), treating rejection as positive. G-mIoU@1 uses the first valid native submitted window (no duration-bound skip), max IoU / number of GT windows; rejected negatives score 1, rejected positives score 0. Each backbone supplies its own localization. See DATA_AUDIT.json, SOURCE_MANIFEST.json, PROTOCOL.json and per-setting calibration, predictions and bootstrap artifacts.


Seen/Unseen Rej-F1 and G-mIoU@1 gaps: [GENERALIZATION_DROP_COMPARISON.md](GENERALIZATION_DROP_COMPARISON.md).