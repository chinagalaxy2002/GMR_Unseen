# Frozen DETR Result Tables

All rows use seed 3407, native Seen-localization checkpoint selection, a maximum of 26 completed epochs and Seen-only threshold calibration. Units are percentages and percentage-point gaps. Negative gaps are retained.

| Dataset/split | Backbone | Selected epoch | AUROC Seen / Unseen / gap | Rej-F1 Seen / Unseen / gap | G-mIoU@1 Seen / Unseen / gap |
| --- | --- | --- | --- | --- | --- |
| charades_cg_v2/C3_CG | moment | 14 | 63.38 / 55.87 / 7.51 | 63.87 / 60.10 / 3.77 | 45.95 / 41.49 / 4.46 |
| charades_cg_v2/C3_CG | qd | 17 | 50.27 / 49.49 / 0.78 | 30.41 / 23.93 / 6.47 | 24.25 / 18.83 / 5.42 |
| clean_v3/A1_v3 | moment | 18 | 74.99 / 64.39 / 10.60 | 56.38 / 37.36 / 19.02 | 37.79 / 23.76 / 14.02 |
| clean_v3/A1_v3 | qd | 14 | 76.33 / 67.82 / 8.51 | 57.61 / 38.30 / 19.31 | 36.48 / 20.53 / 15.95 |
| clean_v3/A2_v3 | moment | 15 | 75.45 / 50.75 / 24.69 | 54.03 / 2.15 / 51.88 | 35.31 / 20.75 / 14.57 |
| clean_v3/A2_v3 | qd | 12 | 76.75 / 53.61 / 23.14 | 55.65 / 2.15 / 53.50 | 36.11 / 21.19 / 14.92 |
| clean_v3/A3_v3 | moment | 11 | 75.71 / 45.60 / 30.11 | 54.39 / 14.86 / 39.53 | 34.76 / 28.31 / 6.46 |
| clean_v3/A3_v3 | qd | 26 | 76.57 / 51.93 / 24.64 | 54.65 / 25.00 / 29.65 | 33.92 / 28.21 / 5.71 |
| clean_v3/C1_v3 | moment | 5 | 68.15 / 51.18 / 16.97 | 42.70 / 0.75 / 41.95 | 32.58 / 15.33 / 17.25 |
| clean_v3/C1_v3 | qd | 19 | 78.53 / 57.75 / 20.78 | 51.29 / 26.30 / 24.99 | 33.89 / 24.40 / 9.49 |
| clean_v3/C2_v3 | moment | 7 | 63.54 / 56.11 / 7.43 | 43.68 / 58.82 / -15.14 | 32.21 / 41.26 / -9.05 |
| clean_v3/C2_v3 | qd | 21 | 69.92 / 51.89 / 18.03 | 46.45 / 58.97 / -12.53 | 32.91 / 41.69 / -8.78 |

## Completed Clean five-split macro

Each split has equal weight. Intervals use the same target-video cluster draws across splits to retain cross-split dependence.

| Backbone | Metric | Seen [95% CI] | Unseen [95% CI] | Gap [95% CI] |
| --- | --- | --- | --- | --- |
| moment | auroc | 71.57 [70.21, 72.84] | 53.60 [51.28, 56.07] | 17.96 [15.39, 20.44] |
| moment | rej_f1 | 50.24 [48.43, 51.95] | 22.79 [20.00, 25.54] | 27.45 [24.69, 30.28] |
| moment | gmiou1 | 34.53 [33.46, 35.58] | 25.88 [24.10, 27.66] | 8.65 [6.76, 10.50] |
| qd | auroc | 75.62 [74.30, 76.86] | 56.60 [54.07, 59.27] | 19.02 [16.21, 21.60] |
| qd | rej_f1 | 53.13 [51.35, 54.84] | 30.14 [26.83, 33.16] | 22.98 [19.61, 26.58] |
| qd | gmiou1 | 34.66 [33.62, 35.70] | 27.20 [25.26, 29.12] | 7.46 [5.43, 9.54] |

## Overall operating-point records and subset sizes

| Dataset/split | Backbone | S+ / S- / U+ / U- | Overall Rej-F1 | Overall RR | S+ FRR | U+ FRR | U- false acceptance | Overall G-mIoU |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| charades_cg_v2/C3_CG | moment | 2684 / 2684 / 2990 / 2990 | 61.86 | 66.16 | 55.89 | 64.58 | 29.30 | 43.60 |
| charades_cg_v2/C3_CG | qd | 2684 / 2684 / 2990 / 2990 | 27.13 | 17.82 | 20.12 | 14.65 | 84.41 | 21.39 |
| clean_v3/A1_v3 | moment | 2857 / 983 / 596 / 175 | 53.92 | 33.29 | 24.54 | 18.12 | 62.86 | 35.44 |
| clean_v3/A1_v3 | qd | 2857 / 983 / 596 / 175 | 55.04 | 28.63 | 19.15 | 15.27 | 64.00 | 33.82 |
| clean_v3/A2_v3 | moment | 3230 / 1066 / 223 / 92 | 52.36 | 37.43 | 30.06 | 0.00 | 98.91 | 34.32 |
| clean_v3/A2_v3 | qd | 3230 / 1066 / 223 / 92 | 53.93 | 37.78 | 29.72 | 0.00 | 98.91 | 35.09 |
| clean_v3/A3_v3 | moment | 3218 / 1036 / 235 / 122 | 52.39 | 38.06 | 30.36 | 6.38 | 90.98 | 34.26 |
| clean_v3/A3_v3 | qd | 3218 / 1036 / 235 / 122 | 52.85 | 37.76 | 29.30 | 13.62 | 81.97 | 33.48 |
| clean_v3/C1_v3 | moment | 3311 / 894 / 142 / 264 | 38.59 | 34.01 | 31.41 | 1.41 | 99.62 | 31.06 |
| clean_v3/C1_v3 | qd | 3311 / 894 / 142 / 264 | 48.53 | 39.15 | 32.20 | 14.08 | 83.71 | 33.06 |
| clean_v3/C2_v3 | moment | 3322 / 1066 / 131 / 92 | 45.22 | 40.21 | 31.58 | 94.66 | 2.17 | 32.65 |
| clean_v3/C2_v3 | qd | 3322 / 1066 / 131 / 92 | 47.66 | 44.50 | 34.89 | 97.71 | 0.00 | 33.34 |

## Interpretation boundaries

Rej-F1 and G-mIoU depend on subset class proportions. Reference differences describe 26-epoch reproduction deviations rather than algorithmic gains. AUROC shadow checkpoints are compared on Seen validation only. Pooling components, gradient conflicts and score-distribution decompositions are diagnostic associations rather than causal estimates. Full confidence intervals and paired changes for all three metrics are in `DETR_METRICS_WITH_CI.csv` and `DETR_ANALYSIS.json`.
