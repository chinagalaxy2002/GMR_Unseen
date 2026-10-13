# Frozen final evaluation

Counts: {'S+': 814, 'S-': 1104, 'U+': 122, 'U-': 193}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 70.136 | [67.629, 72.313] |
| baseline/S/gmiou1 | 43.540 | [40.946, 45.935] |
| baseline/S/rr | 53.650 | [50.322, 56.685] |
| baseline/S/auroc | 75.604 | [73.629, 77.391] |
| baseline/U/rej_f1 | 66.125 | [60.481, 71.505] |
| baseline/U/gmiou1 | 40.554 | [34.970, 46.236] |
| baseline/U/rr | 55.873 | [50.000, 61.892] |
| baseline/U/auroc | 65.164 | [59.019, 70.993] |
| baseline/overall/rej_f1 | 69.544 | [67.133, 71.652] |
| baseline/overall/gmiou1 | 43.119 | [40.654, 45.444] |
| baseline/overall/rr | 53.963 | [50.656, 57.087] |
| baseline/S+/frr | 34.521 | [30.973, 37.998] |
| baseline/U+/frr | 44.262 | [35.642, 53.333] |
| baseline/U-/false_acceptance | 36.788 | [29.902, 43.752] |
| baseline/gap/auroc | 10.440 | [4.182, 16.584] |
| baseline/gap/rej_f1 | 4.011 | [-1.559, 9.947] |
| baseline/gap/gmiou1 | 2.986 | [-2.972, 8.654] |
| experiment/S/rej_f1 | 73.185 | [70.967, 75.011] |
| experiment/S/gmiou1 | 45.553 | [42.860, 47.910] |
| experiment/S/rr | 64.546 | [61.649, 67.275] |
| experiment/S/auroc | 70.427 | [68.214, 72.296] |
| experiment/U/rej_f1 | 79.482 | [75.329, 83.300] |
| experiment/U/gmiou1 | 58.800 | [52.765, 64.820] |
| experiment/U/rr | 85.714 | [82.214, 89.145] |
| experiment/U/auroc | 60.388 | [54.408, 66.352] |
| experiment/overall/rej_f1 | 74.225 | [72.260, 75.779] |
| experiment/overall/gmiou1 | 47.421 | [44.890, 49.573] |
| experiment/overall/rr | 67.532 | [64.854, 69.963] |
| experiment/S+/frr | 46.806 | [43.483, 50.373] |
| experiment/U+/frr | 70.492 | [65.152, 75.941] |
| experiment/U-/false_acceptance | 4.663 | [1.869, 7.870] |
| experiment/gap/auroc | 10.038 | [3.439, 16.401] |
| experiment/gap/rej_f1 | -6.296 | [-10.945, -1.643] |
| experiment/gap/gmiou1 | -13.247 | [-20.267, -6.801] |
| candidates/S+/coverage | 49.140 | [45.211, 52.949] |
| candidates/S+/gt_recall | 33.546 | [30.746, 36.338] |
| candidates/S+/top1_hit | 6.265 | [3.861, 8.833] |
| candidates/S+/high_count | 2.775 | [2.607, 2.938] |
| candidates/S+/relative_count | 9.362 | [9.334, 9.392] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 0.000 | [0.000, 0.000] |
| candidates/S-/relative_count | 9.551 | [9.523, 9.580] |
| candidates/U+/coverage | 54.098 | [45.744, 62.812] |
| candidates/U+/gt_recall | 39.071 | [32.086, 46.220] |
| candidates/U+/top1_hit | 9.016 | [2.999, 15.835] |
| candidates/U+/high_count | 2.434 | [1.960, 2.850] |
| candidates/U+/relative_count | 9.459 | [9.375, 9.545] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 0.000 | [0.000, 0.000] |
| candidates/U-/relative_count | 9.699 | [9.634, 9.765] |
| comparison/seen_change/auroc | -5.178 | [-6.943, -3.459] |
| comparison/unseen_net_gain/auroc | -4.776 | [-9.649, 0.169] |
| comparison/gap_reduction/auroc | 0.402 | [-5.020, 5.661] |
| comparison/seen_change/rej_f1 | 3.049 | [0.952, 5.201] |
| comparison/unseen_net_gain/rej_f1 | 13.357 | [8.348, 18.853] |
| comparison/gap_reduction/rej_f1 | 10.308 | [5.209, 15.702] |
| comparison/seen_change/gmiou1 | 2.013 | [0.032, 3.920] |
| comparison/unseen_net_gain/gmiou1 | 18.245 | [13.211, 23.524] |
| comparison/gap_reduction/gmiou1 | 16.232 | [11.070, 21.682] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
