# Seen–Unseen degradation: AUROC, Rej-F1 and G-mIoU@1

Completed settings: 15/15. Gap = Seen − Unseen; positive means deterioration, negative means improvement. All gaps use percentage points (pp). Rej-F1 and G-mIoU are percentages; AUROC is 0–1. Thresholds and checkpoints are selected on Seen validation only and remain fixed for both subsets.

| Split | Backbone | Seen AUROC | Unseen AUROC | AUROC Gap (pp) | Seen Rej-F1 | Unseen Rej-F1 | Rej-F1 Gap (pp) | Seen G-mIoU@1 | Unseen G-mIoU@1 | G-mIoU Gap (pp) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A1_v3 | FlashVTG-GMR | 0.7530 | 0.6614 | +9.17 | 57.69% | 44.11% | +13.58 | 45.20% | 30.45% | +14.75 |
| A1_v3 | Moment-DETR-GMR | 0.7499 | 0.6439 | +10.60 | 56.38% | 37.36% | +19.02 | 37.79% | 23.76% | +14.02 |
| A1_v3 | QD-DETR-GMR | 0.7295 | 0.5586 | +17.09 | 55.51% | 28.92% | +26.59 | 39.43% | 22.81% | +16.63 |
| A2_v3 | FlashVTG-GMR | 0.7707 | 0.5317 | +23.89 | 55.61% | 2.15% | +53.46 | 41.88% | 29.59% | +12.29 |
| A2_v3 | Moment-DETR-GMR | 0.7545 | 0.5075 | +24.69 | 54.03% | 2.15% | +51.88 | 35.31% | 20.75% | +14.57 |
| A2_v3 | QD-DETR-GMR | 0.7239 | 0.5105 | +21.34 | 49.15% | 15.52% | +33.63 | 33.70% | 25.64% | +8.06 |
| A3_v3 | FlashVTG-GMR | 0.7720 | 0.4650 | +30.70 | 56.32% | 26.04% | +30.28 | 43.03% | 31.22% | +11.81 |
| A3_v3 | Moment-DETR-GMR | 0.7571 | 0.4560 | +30.11 | 54.39% | 14.86% | +39.53 | 34.76% | 28.31% | +6.46 |
| A3_v3 | QD-DETR-GMR | 0.7685 | 0.5029 | +26.56 | 54.09% | 23.35% | +30.74 | 34.38% | 25.57% | +8.80 |
| C1_v3 | FlashVTG-GMR | 0.7895 | 0.6037 | +18.58 | 51.02% | 52.86% | -1.83 | 40.54% | 38.21% | +2.33 |
| C1_v3 | Moment-DETR-GMR | 0.6815 | 0.5118 | +16.97 | 42.70% | 0.75% | +41.95 | 32.58% | 15.33% | +17.25 |
| C1_v3 | QD-DETR-GMR | 0.7853 | 0.5775 | +20.78 | 51.29% | 26.30% | +24.99 | 33.89% | 24.40% | +9.49 |
| C2_v3 | FlashVTG-GMR | 0.6862 | 0.5618 | +12.44 | 46.14% | 60.26% | -14.13 | 38.09% | 42.72% | -4.63 |
| C2_v3 | Moment-DETR-GMR | 0.6760 | 0.4926 | +18.33 | 45.07% | 56.11% | -11.04 | 32.24% | 39.39% | -7.15 |
| C2_v3 | QD-DETR-GMR | 0.6992 | 0.5189 | +18.03 | 46.45% | 58.97% | -12.53 | 32.91% | 41.69% | -8.78 |
| MACRO | Moment-DETR-GMR | 0.7238 | 0.5224 | +20.14 | 50.51% | 22.25% | +28.27 | 34.54% | 25.51% | +9.03 |
| MACRO | QD-DETR-GMR | 0.7413 | 0.5337 | +20.76 | 51.30% | 30.61% | +20.68 | 34.86% | 28.02% | +6.84 |
| MACRO | FlashVTG-GMR | 0.7543 | 0.5647 | +18.96 | 53.36% | 37.09% | +16.27 | 41.75% | 34.44% | +7.31 |

| Split / Backbone | Overall Rej-F1 | Overall RR | S+ FRR | U+ FRR | Overall G-mIoU@1 | Seen rows (+) | Unseen rows (+) |
|---|---:|---:|---:|---:|---:|---:|---:|
| A1_v3 / FlashVTG-GMR | 55.48% | 37.19% | 25.52% | 31.71% | 42.73% | 3840 (2857) | 771 (596) |
| A1_v3 / Moment-DETR-GMR | 53.92% | 33.29% | 24.54% | 18.12% | 35.44% | 3840 (2857) | 771 (596) |
| A1_v3 / QD-DETR-GMR | 51.65% | 23.42% | 13.97% | 17.28% | 36.65% | 3840 (2857) | 771 (596) |
| A2_v3 / FlashVTG-GMR | 53.87% | 37.04% | 28.98% | 0.00% | 41.04% | 4296 (3230) | 315 (223) |
| A2_v3 / Moment-DETR-GMR | 52.36% | 37.43% | 30.06% | 0.00% | 34.32% | 4296 (3230) | 315 (223) |
| A2_v3 / QD-DETR-GMR | 47.92% | 43.59% | 38.27% | 6.73% | 33.15% | 4296 (3230) | 315 (223) |
| A3_v3 / FlashVTG-GMR | 54.21% | 34.66% | 25.05% | 19.15% | 42.12% | 4254 (3218) | 357 (235) |
| A3_v3 / Moment-DETR-GMR | 52.39% | 38.06% | 30.36% | 6.38% | 34.26% | 4254 (3218) | 357 (235) |
| A3_v3 / QD-DETR-GMR | 52.05% | 39.38% | 30.76% | 22.13% | 33.70% | 4254 (3218) | 357 (235) |
| C1_v3 / FlashVTG-GMR | 51.27% | 42.23% | 33.40% | 31.69% | 40.33% | 4205 (3311) | 406 (142) |
| C1_v3 / Moment-DETR-GMR | 38.59% | 34.01% | 31.41% | 1.41% | 31.06% | 4205 (3311) | 406 (142) |
| C1_v3 / QD-DETR-GMR | 48.53% | 39.15% | 32.20% | 14.08% | 33.06% | 4205 (3311) | 406 (142) |
| C2_v3 / FlashVTG-GMR | 47.47% | 44.61% | 35.37% | 90.84% | 38.31% | 4388 (3322) | 223 (131) |
| C2_v3 / Moment-DETR-GMR | 46.27% | 35.35% | 25.86% | 96.18% | 32.59% | 4388 (3322) | 223 (131) |
| C2_v3 / QD-DETR-GMR | 47.66% | 44.50% | 34.89% | 97.71% | 33.34% | 4388 (3322) | 223 (131) |
| MACRO / Moment-DETR-GMR | 48.70% | 35.63% | 28.45% | 24.42% | 33.53% | 4196.6 (3187.6) | 414.4 (265.4) |
| MACRO / QD-DETR-GMR | 49.56% | 38.01% | 30.02% | 31.59% | 33.98% | 4196.6 (3187.6) | 414.4 (265.4) |
| MACRO / FlashVTG-GMR | 52.46% | 39.15% | 29.66% | 34.68% | 40.91% | 4196.6 (3187.6) | 414.4 (265.4) |

95% CI uses 2,000 paired video-cluster bootstrap draws (seed 3407). Valid draw counts are recorded per metric; undefined F1 draws are omitted.

| Split / Backbone | AUROC Gap 95% CI (pp) | Rej-F1 Gap 95% CI (pp) | G-mIoU Gap 95% CI (pp) |
|---|---:|---:|---:|
| A1_v3 / FlashVTG-GMR | [+3.69, +14.24] | [+7.52, +19.45] | [+11.56, +17.95] |
| A1_v3 / Moment-DETR-GMR | [+5.56, +15.87] | [+12.09, +26.34] | [+11.18, +17.10] |
| A1_v3 / QD-DETR-GMR | [+11.66, +22.49] | [+19.16, +34.22] | [+13.78, +19.50] |
| A2_v3 / FlashVTG-GMR | [+18.49, +29.26] | [+48.22, +57.35] | [+8.19, +16.27] |
| A2_v3 / Moment-DETR-GMR | [+19.40, +30.12] | [+46.59, +55.69] | [+10.64, +18.20] |
| A2_v3 / QD-DETR-GMR | [+17.18, +25.57] | [+24.87, +42.78] | [+4.18, +11.97] |
| A3_v3 / FlashVTG-GMR | [+24.89, +36.73] | [+21.20, +39.37] | [+7.55, +16.01] |
| A3_v3 / Moment-DETR-GMR | [+23.78, +36.39] | [+30.48, +48.28] | [+2.57, +10.52] |
| A3_v3 / QD-DETR-GMR | [+20.61, +32.57] | [+22.00, +39.90] | [+4.91, +12.95] |
| C1_v3 / FlashVTG-GMR | [+13.49, +23.80] | [-9.82, +7.92] | [-3.87, +8.86] |
| C1_v3 / Moment-DETR-GMR | [+12.48, +21.47] | [+39.10, +44.65] | [+14.38, +19.99] |
| C1_v3 / QD-DETR-GMR | [+14.95, +26.51] | [+16.88, +33.13] | [+5.22, +13.65] |
| C2_v3 / FlashVTG-GMR | [+3.37, +21.73] | [-20.79, -6.89] | [-11.11, +2.05] |
| C2_v3 / Moment-DETR-GMR | [+10.02, +26.79] | [-17.92, -3.56] | [-13.43, -0.82] |
| C2_v3 / QD-DETR-GMR | [+9.16, +26.95] | [-19.16, -5.09] | [-15.35, -1.98] |
| MACRO / Moment-DETR-GMR | [+17.55, +22.56] | [+25.47, +31.15] | [+7.19, +10.88] |
| MACRO / QD-DETR-GMR | [+18.09, +23.36] | [+16.92, +24.74] | [+4.72, +8.97] |
| MACRO / FlashVTG-GMR | [+16.42, +21.51] | [+13.25, +19.84] | [+5.04, +9.68] |

Seen metrics use S+/S−; Unseen metrics use U+/U−. Rej-F1 = 2TN/(2TN+FP+FN), with rejection as positive. G-mIoU includes positives and negatives: accepted queries use native top-1 set IoU; rejected negatives score 1, rejected positives score 0. Different class proportions between subsets affect Rej-F1 and G-mIoU; these gaps describe the released test subsets rather than controlling for prevalence. Negative gaps are preserved, not forced into a deterioration claim. Formal MACRO rows require all five groups; counts in MACRO rows are group averages, not distinct-query totals.

The original requested branch tables and AUROC bootstrap intervals remain in [STANDARD_EVALUATION.md](STANDARD_EVALUATION.md). All Seen/Unseen absolute and gap CIs for Rej-F1 and G-mIoU are in degradation_bootstrap.json.
