# Seen–Unseen degradation: AUROC, Rej-F1 and G-mIoU@1

Completed settings: 8/15. Gap = Seen − Unseen; positive means deterioration, negative means improvement. All gaps use percentage points (pp). Rej-F1 and G-mIoU are percentages; AUROC is 0–1. Thresholds and checkpoints are selected on Seen validation only and remain fixed for both subsets.

| Split | Backbone | Seen AUROC | Unseen AUROC | AUROC Gap (pp) | Seen Rej-F1 | Unseen Rej-F1 | Rej-F1 Gap (pp) | Seen G-mIoU@1 | Unseen G-mIoU@1 | G-mIoU Gap (pp) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A1_v3 | FlashVTG-GMR | 0.7813 | 0.6814 | +9.99 | 71.17% | 65.48% | +5.69 | 54.43% | 45.18% | +9.25 |
| A1_v3 | Moment-DETR-GMR | 0.7278 | 0.6487 | +7.91 | 67.98% | 63.52% | +4.46 | 48.12% | 42.01% | +6.10 |
| A1_v3 | QD-DETR-GMR | 0.5352 | 0.5186 | +1.66 | 63.65% | 60.94% | +2.71 | 44.19% | 40.79% | +3.41 |
| A2_v3 | Moment-DETR-GMR | 0.7349 | 0.6665 | +6.84 | 67.23% | 65.12% | +2.11 | 47.45% | 42.09% | +5.36 |
| A2_v3 | QD-DETR-GMR | 0.5684 | 0.5127 | +5.57 | 51.63% | 60.43% | -8.80 | 32.15% | 39.57% | -7.42 |
| A3_v3 | Moment-DETR-GMR | 0.7265 | 0.6421 | +8.44 | 64.33% | 57.14% | +7.19 | 44.37% | 41.01% | +3.36 |
| A3_v3 | QD-DETR-GMR | 0.5351 | 0.5585 | -2.34 | 40.39% | 28.96% | +11.43 | 28.84% | 26.14% | +2.71 |
| C1_v3 | Moment-DETR-GMR | 0.7308 | 0.6264 | +10.45 | 65.88% | 57.19% | +8.68 | 46.35% | 42.99% | +3.35 |

| Split / Backbone | Overall Rej-F1 | Overall RR | S+ FRR | U+ FRR | Overall G-mIoU@1 | Seen rows (+) | Unseen rows (+) |
|---|---:|---:|---:|---:|---:|---:|---:|
| A1_v3 / FlashVTG-GMR | 70.08% | 55.79% | 32.31% | 62.08% | 52.87% | 5739 (2857) | 1167 (596) |
| A1_v3 / Moment-DETR-GMR | 67.16% | 58.07% | 39.76% | 61.74% | 47.09% | 5739 (2857) | 1167 (596) |
| A1_v3 / QD-DETR-GMR | 63.19% | 78.32% | 75.04% | 78.02% | 43.62% | 5739 (2857) | 1167 (596) |
| A2_v3 / Moment-DETR-GMR | 67.09% | 51.45% | 34.80% | 35.43% | 47.09% | 6443 (3230) | 463 (223) |
| A2_v3 / QD-DETR-GMR | 52.38% | 45.11% | 38.61% | 66.37% | 32.65% | 6443 (3230) | 463 (223) |
| A3_v3 / Moment-DETR-GMR | 63.77% | 43.64% | 27.04% | 34.89% | 44.12% | 6393 (3218) | 513 (235) |
| A3_v3 / QD-DETR-GMR | 39.63% | 29.73% | 28.81% | 14.89% | 28.64% | 6393 (3218) | 513 (235) |
| C1_v3 / Moment-DETR-GMR | 65.15% | 46.10% | 29.69% | 27.46% | 46.11% | 6406 (3311) | 500 (142) |

95% CI uses 2,000 paired video-cluster bootstrap draws (seed 3407). Valid draw counts are recorded per metric; undefined F1 draws are omitted.

| Split / Backbone | AUROC Gap 95% CI (pp) | Rej-F1 Gap 95% CI (pp) | G-mIoU Gap 95% CI (pp) |
|---|---:|---:|---:|
| A1_v3 / FlashVTG-GMR | [+6.91, +13.03] | [+2.68, +8.89] | [+6.25, +12.32] |
| A1_v3 / Moment-DETR-GMR | [+4.73, +11.10] | [+1.23, +7.64] | [+3.08, +9.05] |
| A1_v3 / QD-DETR-GMR | [-1.87, +5.09] | [-0.41, +5.88] | [+0.38, +6.45] |
| A2_v3 / Moment-DETR-GMR | [+2.02, +11.44] | [-2.79, +7.59] | [+0.61, +10.07] |
| A2_v3 / QD-DETR-GMR | [+0.68, +10.61] | [-13.68, -3.73] | [-11.96, -2.85] |
| A3_v3 / Moment-DETR-GMR | [+3.84, +13.00] | [+1.97, +12.35] | [-0.83, +7.17] |
| A3_v3 / QD-DETR-GMR | [-7.54, +3.27] | [+5.24, +17.72] | [-0.95, +6.36] |
| C1_v3 / Moment-DETR-GMR | [+5.29, +15.09] | [+1.84, +15.70] | [-2.41, +8.63] |

Seen metrics use S+/S−; Unseen metrics use U+/U−. Rej-F1 = 2TN/(2TN+FP+FN), with rejection as positive. G-mIoU includes positives and negatives: accepted queries use native top-1 set IoU; rejected negatives score 1, rejected positives score 0. Different class proportions between subsets affect Rej-F1 and G-mIoU; these gaps describe the released test subsets rather than controlling for prevalence. Negative gaps are preserved, not forced into a deterioration claim. Formal MACRO rows require all five groups; counts in MACRO rows are group averages, not distinct-query totals.

The original requested branch tables and AUROC bootstrap intervals remain in [STANDARD_EVALUATION.md](STANDARD_EVALUATION.md). All Seen/Unseen absolute and gap CIs for Rej-F1 and G-mIoU are in degradation_bootstrap.json.
