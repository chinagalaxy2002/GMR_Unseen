# Frozen final evaluation

Counts: {'S+': 3311, 'S-': 894, 'U+': 142, 'U-': 264}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 42.700 | [40.167, 45.030] |
| baseline/S/gmiou1 | 32.580 | [31.311, 33.851] |
| baseline/S/rr | 37.218 | [35.059, 39.223] |
| baseline/S/auroc | 68.146 | [66.337, 69.867] |
| baseline/U/rej_f1 | 0.749 | [0.000, 2.490] |
| baseline/U/gmiou1 | 15.333 | [12.813, 17.976] |
| baseline/U/rr | 0.739 | [0.000, 2.083] |
| baseline/U/auroc | 51.175 | [46.930, 55.316] |
| baseline/overall/rej_f1 | 38.591 | [35.978, 41.034] |
| baseline/overall/gmiou1 | 31.061 | [29.837, 32.254] |
| baseline/overall/rr | 34.006 | [32.009, 36.022] |
| baseline/S+/frr | 31.410 | [29.413, 33.293] |
| baseline/U+/frr | 1.408 | [0.000, 3.659] |
| baseline/U-/false_acceptance | 99.621 | [98.718, 100.000] |
| baseline/gap/auroc | 16.971 | [12.482, 21.467] |
| baseline/gap/rej_f1 | 41.951 | [39.099, 44.648] |
| baseline/gap/gmiou1 | 17.247 | [14.375, 19.986] |
| experiment/S/rej_f1 | 48.776 | [46.637, 50.704] |
| experiment/S/gmiou1 | 32.702 | [31.410, 33.883] |
| experiment/S/rr | 48.656 | [46.352, 51.006] |
| experiment/S/auroc | 77.270 | [75.506, 79.089] |
| experiment/U/rej_f1 | 53.810 | [44.390, 62.103] |
| experiment/U/gmiou1 | 40.085 | [34.218, 46.219] |
| experiment/U/rr | 38.424 | [29.970, 47.143] |
| experiment/U/auroc | 57.825 | [52.857, 62.942] |
| experiment/overall/rej_f1 | 49.405 | [47.283, 51.304] |
| experiment/overall/gmiou1 | 33.352 | [32.119, 34.500] |
| experiment/overall/rr | 47.755 | [45.449, 49.990] |
| experiment/S+/frr | 40.139 | [37.832, 42.406] |
| experiment/U+/frr | 30.282 | [21.019, 40.136] |
| experiment/U-/false_acceptance | 57.197 | [46.581, 67.317] |
| experiment/gap/auroc | 19.445 | [13.774, 25.002] |
| experiment/gap/rej_f1 | -5.034 | [-13.787, 4.619] |
| experiment/gap/gmiou1 | -7.383 | [-13.728, -1.238] |
| candidates/S+/coverage | 69.858 | [67.855, 71.736] |
| candidates/S+/gt_recall | 69.858 | [67.855, 71.736] |
| candidates/S+/top1_hit | 35.035 | [33.213, 36.794] |
| candidates/S+/high_count | 2.209 | [2.181, 2.241] |
| candidates/S+/relative_count | 2.256 | [2.227, 2.287] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.081 | [2.023, 2.137] |
| candidates/S-/relative_count | 2.209 | [2.151, 2.263] |
| candidates/U+/coverage | 76.056 | [66.667, 84.679] |
| candidates/U+/gt_recall | 76.056 | [66.667, 84.679] |
| candidates/U+/top1_hit | 54.930 | [45.112, 64.568] |
| candidates/U+/high_count | 2.092 | [1.968, 2.216] |
| candidates/U+/relative_count | 2.113 | [1.987, 2.237] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.170 | [2.010, 2.332] |
| candidates/U-/relative_count | 2.189 | [2.029, 2.352] |
| comparison/seen_change/auroc | 9.123 | [7.437, 10.878] |
| comparison/unseen_net_gain/auroc | 6.650 | [0.735, 13.276] |
| comparison/gap_reduction/auroc | -2.473 | [-8.690, 4.418] |
| comparison/seen_change/rej_f1 | 6.075 | [3.959, 8.155] |
| comparison/unseen_net_gain/rej_f1 | 53.060 | [43.950, 61.521] |
| comparison/gap_reduction/rej_f1 | 46.985 | [37.542, 55.924] |
| comparison/seen_change/gmiou1 | 0.122 | [-1.144, 1.328] |
| comparison/unseen_net_gain/gmiou1 | 24.752 | [18.132, 31.705] |
| comparison/gap_reduction/gmiou1 | 24.629 | [17.899, 31.674] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
