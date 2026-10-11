# Seen–Unseen degradation: AUROC, Rej-F1 and G-mIoU@1

Completed settings: 15/15. Gap = Seen − Unseen; positive means deterioration, negative means improvement. All gaps use percentage points (pp). Rej-F1 and G-mIoU are percentages; AUROC is 0–1. Thresholds and checkpoints are selected on Seen validation only and remain fixed for both subsets.

| Split | Backbone | Seen AUROC | Unseen AUROC | AUROC Gap (pp) | Seen Rej-F1 | Unseen Rej-F1 | Rej-F1 Gap (pp) | Seen G-mIoU@1 | Unseen G-mIoU@1 | G-mIoU Gap (pp) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A1_soccer | FlashVTG-GMR | 0.7766 | 0.6786 | +9.80 | 76.64% | 79.10% | -2.46 | 52.83% | 56.77% | -3.94 |
| A1_soccer | Moment-DETR-GMR | 0.7795 | 0.6680 | +11.16 | 76.29% | 78.80% | -2.51 | 50.66% | 55.81% | -5.15 |
| A1_soccer | QD-DETR-GMR | 0.7560 | 0.6516 | +10.44 | 70.14% | 66.12% | +4.01 | 43.54% | 40.55% | +2.99 |
| A2_soccer | FlashVTG-GMR | 0.7664 | 0.5908 | +17.56 | 78.89% | 80.10% | -1.21 | 55.92% | 60.73% | -4.81 |
| A2_soccer | Moment-DETR-GMR | 0.7676 | 0.5429 | +22.47 | 73.64% | 69.57% | +4.07 | 47.00% | 47.72% | -0.73 |
| A2_soccer | QD-DETR-GMR | 0.7037 | 0.6508 | +5.29 | 70.45% | 74.79% | -4.34 | 42.30% | 49.29% | -6.99 |
| A3_soccer | FlashVTG-GMR | 0.7700 | 0.5914 | +17.85 | 72.37% | 61.24% | +11.13 | 47.36% | 35.14% | +12.22 |
| A3_soccer | Moment-DETR-GMR | 0.7733 | 0.6214 | +15.19 | 77.83% | 74.19% | +3.63 | 52.96% | 50.84% | +2.12 |
| A3_soccer | QD-DETR-GMR | 0.7106 | 0.6484 | +6.23 | 75.91% | 75.33% | +0.58 | 50.04% | 52.61% | -2.57 |
| C1_soccer | FlashVTG-GMR | 0.7756 | 0.6131 | +16.24 | 70.44% | 74.19% | -3.75 | 44.19% | 53.86% | -9.67 |
| C1_soccer | Moment-DETR-GMR | 0.7717 | 0.5964 | +17.53 | 78.31% | 73.87% | +4.44 | 53.50% | 54.80% | -1.30 |
| C1_soccer | QD-DETR-GMR | 0.7287 | 0.5839 | +14.48 | 75.95% | 76.35% | -0.40 | 48.96% | 60.15% | -11.19 |
| C2_soccer | FlashVTG-GMR | 0.7725 | 0.5646 | +20.79 | 69.49% | 68.51% | +0.97 | 43.37% | 47.40% | -4.04 |
| C2_soccer | Moment-DETR-GMR | 0.7679 | 0.5211 | +24.67 | 74.78% | 74.52% | +0.25 | 48.62% | 55.54% | -6.92 |
| C2_soccer | QD-DETR-GMR | 0.7116 | 0.4498 | +26.18 | 73.15% | 79.08% | -5.94 | 45.64% | 65.09% | -19.45 |
| MACRO | Moment-DETR-GMR | 0.7720 | 0.5900 | +18.20 | 76.17% | 74.19% | +1.98 | 50.55% | 52.94% | -2.39 |
| MACRO | QD-DETR-GMR | 0.7221 | 0.5969 | +12.52 | 73.12% | 74.34% | -1.22 | 46.10% | 53.54% | -7.44 |
| MACRO | FlashVTG-GMR | 0.7722 | 0.6077 | +16.45 | 73.56% | 72.63% | +0.94 | 48.73% | 50.78% | -2.05 |

| Split / Backbone | Overall Rej-F1 | Overall RR | S+ FRR | U+ FRR | Overall G-mIoU@1 | Seen rows (+) | Unseen rows (+) |
|---|---:|---:|---:|---:|---:|---:|---:|
| A1_soccer / FlashVTG-GMR | 77.03% | 69.59% | 46.68% | 62.30% | 53.38% | 1918 (814) | 315 (122) |
| A1_soccer / Moment-DETR-GMR | 76.68% | 68.65% | 46.44% | 57.38% | 51.38% | 1918 (814) | 315 (122) |
| A1_soccer / QD-DETR-GMR | 69.54% | 53.96% | 34.52% | 44.26% | 43.12% | 1918 (814) | 315 (122) |
| A2_soccer / FlashVTG-GMR | 79.05% | 76.18% | 52.83% | 72.90% | 56.51% | 1957 (829) | 276 (107) |
| A2_soccer / Moment-DETR-GMR | 73.08% | 62.02% | 40.29% | 66.36% | 47.09% | 1957 (829) | 276 (107) |
| A2_soccer / QD-DETR-GMR | 71.04% | 60.68% | 42.94% | 53.27% | 43.16% | 1957 (829) | 276 (107) |
| A3_soccer / FlashVTG-GMR | 71.03% | 56.16% | 34.78% | 52.34% | 45.86% | 1959 (808) | 274 (128) |
| A3_soccer / Moment-DETR-GMR | 77.36% | 70.67% | 46.78% | 68.75% | 52.70% | 1959 (808) | 274 (128) |
| A3_soccer / QD-DETR-GMR | 75.84% | 72.77% | 52.97% | 69.53% | 50.35% | 1959 (808) | 274 (128) |
| C1_soccer / FlashVTG-GMR | 71.00% | 54.32% | 31.06% | 62.63% | 45.37% | 1962 (837) | 271 (99) |
| C1_soccer / Moment-DETR-GMR | 77.71% | 73.89% | 50.90% | 79.80% | 53.66% | 1962 (837) | 271 (99) |
| C1_soccer / QD-DETR-GMR | 76.00% | 72.37% | 49.82% | 92.93% | 50.32% | 1962 (837) | 271 (99) |
| C2_soccer / FlashVTG-GMR | 69.37% | 52.31% | 30.36% | 69.86% | 43.75% | 2021 (863) | 212 (73) |
| C2_soccer / Moment-DETR-GMR | 74.75% | 66.05% | 44.15% | 79.45% | 49.28% | 2021 (863) | 212 (73) |
| C2_soccer / QD-DETR-GMR | 73.88% | 68.61% | 48.09% | 98.63% | 47.49% | 2021 (863) | 212 (73) |
| MACRO / Moment-DETR-GMR | 75.91% | 68.26% | 45.71% | 70.35% | 50.82% | 1963.4 (830.2) | 269.6 (105.8) |
| MACRO / QD-DETR-GMR | 73.26% | 65.68% | 45.67% | 71.72% | 46.89% | 1963.4 (830.2) | 269.6 (105.8) |
| MACRO / FlashVTG-GMR | 73.50% | 61.71% | 39.14% | 64.01% | 48.98% | 1963.4 (830.2) | 269.6 (105.8) |

95% CI uses 2,000 paired video-cluster bootstrap draws (seed 3407). Valid draw counts are recorded per metric; undefined F1 draws are omitted.

| Split / Backbone | AUROC Gap 95% CI (pp) | Rej-F1 Gap 95% CI (pp) | G-mIoU Gap 95% CI (pp) |
|---|---:|---:|---:|
| A1_soccer / FlashVTG-GMR | [+4.20, +15.90] | [-7.07, +2.32] | [-10.60, +2.37] |
| A1_soccer / Moment-DETR-GMR | [+4.97, +17.07] | [-6.89, +2.13] | [-11.56, +1.19] |
| A1_soccer / QD-DETR-GMR | [+4.18, +16.58] | [-1.56, +9.95] | [-2.97, +8.65] |
| A2_soccer / FlashVTG-GMR | [+10.03, +25.37] | [-5.66, +3.22] | [-11.53, +1.53] |
| A2_soccer / Moment-DETR-GMR | [+15.95, +29.45] | [-0.95, +9.61] | [-6.83, +5.18] |
| A2_soccer / QD-DETR-GMR | [-1.48, +12.12] | [-9.39, +0.82] | [-13.51, -0.89] |
| A3_soccer / FlashVTG-GMR | [+11.91, +23.69] | [+5.13, +17.21] | [+6.25, +17.83] |
| A3_soccer / Moment-DETR-GMR | [+8.74, +21.97] | [-0.94, +8.52] | [-4.42, +8.49] |
| A3_soccer / QD-DETR-GMR | [+0.06, +12.64] | [-4.14, +5.34] | [-9.10, +3.72] |
| C1_soccer / FlashVTG-GMR | [+9.14, +23.64] | [-9.49, +2.41] | [-16.23, -2.89] |
| C1_soccer / Moment-DETR-GMR | [+10.02, +25.33] | [-0.84, +10.24] | [-8.19, +5.63] |
| C1_soccer / QD-DETR-GMR | [+7.19, +21.83] | [-5.12, +4.62] | [-17.33, -4.78] |
| C2_soccer / FlashVTG-GMR | [+12.59, +28.15] | [-5.45, +7.71] | [-11.20, +3.25] |
| C2_soccer / Moment-DETR-GMR | [+15.69, +33.26] | [-5.48, +5.89] | [-13.89, -0.26] |
| C2_soccer / QD-DETR-GMR | [+17.66, +34.34] | [-11.17, -0.71] | [-26.18, -12.81] |
| MACRO / Moment-DETR-GMR | [+15.06, +21.41] | [-0.11, +4.20] | [-5.14, +0.42] |
| MACRO / QD-DETR-GMR | [+8.99, +15.99] | [-3.50, +1.20] | [-10.18, -4.67] |
| MACRO / FlashVTG-GMR | [+12.91, +19.53] | [-1.62, +3.57] | [-4.99, +0.99] |

Seen metrics use S+/S−; Unseen metrics use U+/U−. Rej-F1 = 2TN/(2TN+FP+FN), with rejection as positive. G-mIoU includes positives and negatives: accepted queries use native top-1 set IoU; rejected negatives score 1, rejected positives score 0. Different class proportions between subsets affect Rej-F1 and G-mIoU; these gaps describe the released test subsets rather than controlling for prevalence. Negative gaps are preserved, not forced into a deterioration claim. Formal MACRO rows require all five groups; counts in MACRO rows are group averages, not distinct-query totals.

The original requested branch tables and AUROC bootstrap intervals remain in [STANDARD_EVALUATION.md](STANDARD_EVALUATION.md). All Seen/Unseen absolute and gap CIs for Rej-F1 and G-mIoU are in degradation_bootstrap.json.
