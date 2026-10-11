# Seen–Unseen degradation: AUROC, Rej-F1 and G-mIoU@1

Completed settings: 15/15. Gap = Seen − Unseen; positive means deterioration, negative means improvement. All gaps use percentage points (pp). Rej-F1 and G-mIoU are percentages; AUROC is 0–1. Thresholds and checkpoints are selected on Seen validation only and remain fixed for both subsets.

| Split | Backbone | Seen AUROC | Unseen AUROC | AUROC Gap (pp) | Seen Rej-F1 | Unseen Rej-F1 | Rej-F1 Gap (pp) | Seen G-mIoU@1 | Unseen G-mIoU@1 | G-mIoU Gap (pp) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A1_v3 | FlashVTG-GMR | 0.7813 | 0.6814 | +9.99 | 71.17% | 65.48% | +5.69 | 54.43% | 45.18% | +9.25 |
| A1_v3 | Moment-DETR-GMR | 0.7278 | 0.6487 | +7.91 | 67.98% | 63.52% | +4.46 | 48.12% | 42.01% | +6.10 |
| A1_v3 | QD-DETR-GMR | 0.5352 | 0.5186 | +1.66 | 63.65% | 60.94% | +2.71 | 44.19% | 40.79% | +3.41 |
| A2_v3 | FlashVTG-GMR | 0.7907 | 0.6933 | +9.73 | 70.55% | 64.56% | +6.00 | 53.18% | 45.97% | +7.21 |
| A2_v3 | Moment-DETR-GMR | 0.7349 | 0.6665 | +6.84 | 67.23% | 65.12% | +2.11 | 47.45% | 42.09% | +5.36 |
| A2_v3 | QD-DETR-GMR | 0.5684 | 0.5127 | +5.57 | 51.63% | 60.43% | -8.80 | 32.15% | 39.57% | -7.42 |
| A3_v3 | FlashVTG-GMR | 0.7823 | 0.6489 | +13.34 | 69.36% | 59.59% | +9.77 | 51.90% | 44.78% | +7.12 |
| A3_v3 | Moment-DETR-GMR | 0.7265 | 0.6421 | +8.44 | 64.33% | 57.14% | +7.19 | 44.37% | 41.01% | +3.36 |
| A3_v3 | QD-DETR-GMR | 0.5351 | 0.5585 | -2.34 | 40.39% | 28.96% | +11.43 | 28.84% | 26.14% | +2.71 |
| C1_v3 | FlashVTG-GMR | 0.7626 | 0.6165 | +14.61 | 64.63% | 51.06% | +13.58 | 48.95% | 37.76% | +11.19 |
| C1_v3 | Moment-DETR-GMR | 0.7308 | 0.6264 | +10.45 | 65.88% | 57.19% | +8.68 | 46.35% | 42.99% | +3.35 |
| C1_v3 | QD-DETR-GMR | 0.5151 | 0.4688 | +4.63 | 65.18% | 83.45% | -18.27 | 46.67% | 71.60% | -24.93 |
| C2_v3 | FlashVTG-GMR | 0.7361 | 0.6639 | +7.22 | 64.46% | 67.72% | -3.26 | 48.93% | 50.56% | -1.63 |
| C2_v3 | Moment-DETR-GMR | 0.7063 | 0.6493 | +5.70 | 63.96% | 67.59% | -3.63 | 43.67% | 47.71% | -4.03 |
| C2_v3 | QD-DETR-GMR | 0.5685 | 0.4877 | +8.07 | 63.51% | 73.21% | -9.70 | 43.20% | 57.74% | -14.54 |
| MACRO | Moment-DETR-GMR | 0.7253 | 0.6466 | +7.87 | 65.88% | 62.11% | +3.76 | 45.99% | 43.16% | +2.83 |
| MACRO | QD-DETR-GMR | 0.5445 | 0.5093 | +3.52 | 56.87% | 61.40% | -4.53 | 39.01% | 47.17% | -8.16 |
| MACRO | FlashVTG-GMR | 0.7706 | 0.6608 | +10.98 | 68.04% | 61.68% | +6.36 | 51.48% | 44.85% | +6.63 |

| Split / Backbone | Overall Rej-F1 | Overall RR | S+ FRR | U+ FRR | Overall G-mIoU@1 | Seen rows (+) | Unseen rows (+) |
|---|---:|---:|---:|---:|---:|---:|---:|
| A1_v3 / FlashVTG-GMR | 70.08% | 55.79% | 32.31% | 62.08% | 52.87% | 5739 (2857) | 1167 (596) |
| A1_v3 / Moment-DETR-GMR | 67.16% | 58.07% | 39.76% | 61.74% | 47.09% | 5739 (2857) | 1167 (596) |
| A1_v3 / QD-DETR-GMR | 63.19% | 78.32% | 75.04% | 78.02% | 43.62% | 5739 (2857) | 1167 (596) |
| A2_v3 / FlashVTG-GMR | 70.13% | 47.78% | 26.35% | 36.32% | 52.70% | 6443 (3230) | 463 (223) |
| A2_v3 / Moment-DETR-GMR | 67.09% | 51.45% | 34.80% | 35.43% | 47.09% | 6443 (3230) | 463 (223) |
| A2_v3 / QD-DETR-GMR | 52.38% | 45.11% | 38.61% | 66.37% | 32.65% | 6443 (3230) | 463 (223) |
| A3_v3 / FlashVTG-GMR | 68.62% | 43.35% | 22.25% | 28.09% | 51.38% | 6393 (3218) | 513 (235) |
| A3_v3 / Moment-DETR-GMR | 63.77% | 43.64% | 27.04% | 34.89% | 44.12% | 6393 (3218) | 513 (235) |
| A3_v3 / QD-DETR-GMR | 39.63% | 29.73% | 28.81% | 14.89% | 28.64% | 6393 (3218) | 513 (235) |
| C1_v3 / FlashVTG-GMR | 63.47% | 37.75% | 19.75% | 21.13% | 48.14% | 6406 (3311) | 500 (142) |
| C1_v3 / Moment-DETR-GMR | 65.15% | 46.10% | 29.69% | 27.46% | 46.11% | 6406 (3311) | 500 (142) |
| C1_v3 / QD-DETR-GMR | 66.78% | 91.98% | 88.67% | 100.00% | 48.47% | 6406 (3311) | 500 (142) |
| C2_v3 / FlashVTG-GMR | 64.66% | 41.28% | 22.34% | 54.20% | 49.00% | 6596 (3322) | 310 (131) |
| C2_v3 / Moment-DETR-GMR | 64.16% | 47.32% | 31.67% | 45.80% | 43.86% | 6596 (3322) | 310 (131) |
| C2_v3 / QD-DETR-GMR | 64.07% | 72.59% | 65.32% | 100.00% | 43.85% | 6596 (3322) | 310 (131) |
| MACRO / Moment-DETR-GMR | 65.46% | 49.32% | 32.59% | 41.07% | 45.65% | 6315.4 (3187.6) | 590.6 (265.4) |
| MACRO / QD-DETR-GMR | 57.21% | 63.54% | 59.29% | 71.86% | 39.45% | 6315.4 (3187.6) | 590.6 (265.4) |
| MACRO / FlashVTG-GMR | 67.39% | 45.19% | 24.60% | 40.36% | 50.82% | 6315.4 (3187.6) | 590.6 (265.4) |

95% CI uses 2,000 paired video-cluster bootstrap draws (seed 3407). Valid draw counts are recorded per metric; undefined F1 draws are omitted.

| Split / Backbone | AUROC Gap 95% CI (pp) | Rej-F1 Gap 95% CI (pp) | G-mIoU Gap 95% CI (pp) |
|---|---:|---:|---:|
| A1_v3 / FlashVTG-GMR | [+6.91, +13.03] | [+2.68, +8.89] | [+6.25, +12.32] |
| A1_v3 / Moment-DETR-GMR | [+4.73, +11.10] | [+1.23, +7.64] | [+3.08, +9.05] |
| A1_v3 / QD-DETR-GMR | [-1.87, +5.09] | [-0.41, +5.88] | [+0.38, +6.45] |
| A2_v3 / FlashVTG-GMR | [+5.00, +14.33] | [+0.80, +11.59] | [+2.64, +11.79] |
| A2_v3 / Moment-DETR-GMR | [+2.02, +11.44] | [-2.79, +7.59] | [+0.61, +10.07] |
| A2_v3 / QD-DETR-GMR | [+0.68, +10.61] | [-13.68, -3.73] | [-11.96, -2.85] |
| A3_v3 / FlashVTG-GMR | [+8.63, +18.16] | [+4.27, +15.38] | [+3.01, +11.22] |
| A3_v3 / Moment-DETR-GMR | [+3.84, +13.00] | [+1.97, +12.35] | [-0.83, +7.17] |
| A3_v3 / QD-DETR-GMR | [-7.54, +3.27] | [+5.24, +17.72] | [-0.95, +6.36] |
| C1_v3 / FlashVTG-GMR | [+9.59, +19.32] | [+5.99, +21.08] | [+5.32, +16.15] |
| C1_v3 / Moment-DETR-GMR | [+5.29, +15.09] | [+1.84, +15.70] | [-2.41, +8.63] |
| C1_v3 / QD-DETR-GMR | [+0.25, +9.20] | [-20.61, -16.00] | [-28.20, -21.92] |
| C2_v3 / FlashVTG-GMR | [+0.65, +14.28] | [-9.06, +2.74] | [-7.52, +3.76] |
| C2_v3 / Moment-DETR-GMR | [-1.28, +12.75] | [-9.39, +2.41] | [-9.86, +1.63] |
| C2_v3 / QD-DETR-GMR | [+1.29, +14.95] | [-14.52, -4.98] | [-20.80, -8.86] |
| MACRO / Moment-DETR-GMR | [+5.67, +10.11] | [+1.54, +6.08] | [+0.80, +4.75] |
| MACRO / QD-DETR-GMR | [+1.11, +6.05] | [-6.42, -2.61] | [-9.88, -6.42] |
| MACRO / FlashVTG-GMR | [+8.87, +13.19] | [+3.90, +8.76] | [+4.55, +8.49] |

Seen metrics use S+/S−; Unseen metrics use U+/U−. Rej-F1 = 2TN/(2TN+FP+FN), with rejection as positive. G-mIoU includes positives and negatives: accepted queries use native top-1 set IoU; rejected negatives score 1, rejected positives score 0. Different class proportions between subsets affect Rej-F1 and G-mIoU; these gaps describe the released test subsets rather than controlling for prevalence. Negative gaps are preserved, not forced into a deterioration claim. Formal MACRO rows require all five groups; counts in MACRO rows are group averages, not distinct-query totals.

The original requested branch tables and AUROC bootstrap intervals remain in [STANDARD_EVALUATION.md](STANDARD_EVALUATION.md). All Seen/Unseen absolute and gap CIs for Rej-F1 and G-mIoU are in degradation_bootstrap.json.
