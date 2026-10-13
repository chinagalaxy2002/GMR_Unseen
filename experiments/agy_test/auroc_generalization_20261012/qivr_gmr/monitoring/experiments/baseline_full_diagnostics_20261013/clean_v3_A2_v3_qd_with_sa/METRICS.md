# Frozen final evaluation

Counts: {'S+': 3230, 'S-': 1066, 'U+': 223, 'U-': 92}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 49.148 | [46.615, 51.632] |
| baseline/S/gmiou1 | 33.699 | [32.211, 35.151] |
| baseline/S/rr | 46.229 | [43.810, 48.508] |
| baseline/S/auroc | 72.390 | [69.984, 74.672] |
| baseline/U/rej_f1 | 15.517 | [6.897, 24.114] |
| baseline/U/gmiou1 | 25.641 | [21.967, 29.199] |
| baseline/U/rr | 7.619 | [3.610, 12.378] |
| baseline/U/auroc | 51.046 | [47.647, 54.494] |
| baseline/overall/rej_f1 | 47.917 | [45.402, 50.298] |
| baseline/overall/gmiou1 | 33.148 | [31.705, 34.534] |
| baseline/overall/rr | 43.591 | [41.298, 45.834] |
| baseline/S+/frr | 38.266 | [35.970, 40.606] |
| baseline/U+/frr | 6.726 | [2.666, 11.916] |
| baseline/U-/false_acceptance | 90.217 | [83.501, 96.041] |
| baseline/gap/auroc | 21.344 | [17.179, 25.573] |
| baseline/gap/rej_f1 | 33.631 | [24.868, 42.779] |
| baseline/gap/gmiou1 | 8.058 | [4.184, 11.967] |
| experiment/S/rej_f1 | 54.925 | [52.516, 57.059] |
| experiment/S/gmiou1 | 35.265 | [33.807, 36.711] |
| experiment/S/rr | 43.250 | [40.806, 45.621] |
| experiment/S/auroc | 77.105 | [75.180, 78.950] |
| experiment/U/rej_f1 | 2.151 | [0.000, 7.059] |
| experiment/U/gmiou1 | 20.654 | [16.774, 24.507] |
| experiment/U/rr | 0.317 | [0.000, 1.031] |
| experiment/U/auroc | 54.355 | [48.899, 59.441] |
| experiment/overall/rej_f1 | 53.298 | [50.915, 55.492] |
| experiment/overall/gmiou1 | 34.267 | [32.866, 35.674] |
| experiment/overall/rr | 40.317 | [37.982, 42.577] |
| experiment/S+/frr | 32.663 | [30.448, 34.652] |
| experiment/U+/frr | 0.000 | [0.000, 0.000] |
| experiment/U-/false_acceptance | 98.913 | [96.341, 100.000] |
| experiment/gap/auroc | 22.750 | [17.104, 28.476] |
| experiment/gap/rej_f1 | 52.774 | [47.629, 56.521] |
| experiment/gap/gmiou1 | 14.611 | [10.450, 18.708] |
| candidates/S+/coverage | 73.189 | [71.285, 74.961] |
| candidates/S+/gt_recall | 73.189 | [71.285, 74.961] |
| candidates/S+/top1_hit | 34.675 | [32.727, 36.687] |
| candidates/S+/high_count | 2.653 | [2.624, 2.683] |
| candidates/S+/relative_count | 2.687 | [2.661, 2.715] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.272 | [2.171, 2.375] |
| candidates/S-/relative_count | 2.544 | [2.477, 2.613] |
| candidates/U+/coverage | 72.646 | [65.071, 79.621] |
| candidates/U+/gt_recall | 72.646 | [65.071, 79.621] |
| candidates/U+/top1_hit | 30.045 | [23.036, 37.620] |
| candidates/U+/high_count | 2.928 | [2.884, 2.966] |
| candidates/U+/relative_count | 2.946 | [2.907, 2.978] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.946 | [2.882, 2.990] |
| candidates/U-/relative_count | 2.957 | [2.897, 3.000] |
| comparison/seen_change/auroc | 4.715 | [2.857, 6.531] |
| comparison/unseen_net_gain/auroc | 3.310 | [-1.609, 8.540] |
| comparison/gap_reduction/auroc | -1.405 | [-6.482, 4.145] |
| comparison/seen_change/rej_f1 | 5.777 | [4.109, 7.560] |
| comparison/unseen_net_gain/rej_f1 | -13.367 | [-22.222, -5.310] |
| comparison/gap_reduction/rej_f1 | -19.143 | [-28.121, -10.825] |
| comparison/seen_change/gmiou1 | 1.567 | [0.410, 2.818] |
| comparison/unseen_net_gain/gmiou1 | -4.986 | [-9.724, 0.026] |
| comparison/gap_reduction/gmiou1 | -6.553 | [-11.507, -1.427] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
