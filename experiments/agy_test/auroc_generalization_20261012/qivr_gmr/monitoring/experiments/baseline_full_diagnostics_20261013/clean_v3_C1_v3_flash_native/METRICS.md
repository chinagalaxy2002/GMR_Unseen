# Frozen final evaluation

Counts: {'S+': 3311, 'S-': 894, 'U+': 142, 'U-': 264}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 51.024 | [48.791, 53.148] |
| baseline/S/gmiou1 | 40.537 | [39.203, 41.862] |
| baseline/S/rr | 42.592 | [40.504, 44.628] |
| baseline/S/auroc | 78.953 | [77.174, 80.673] |
| baseline/U/rej_f1 | 52.857 | [43.478, 60.750] |
| baseline/U/gmiou1 | 38.211 | [31.890, 44.259] |
| baseline/U/rr | 38.424 | [29.411, 47.841] |
| baseline/U/auroc | 60.369 | [55.587, 65.203] |
| baseline/overall/rej_f1 | 51.272 | [49.052, 53.391] |
| baseline/overall/gmiou1 | 40.332 | [38.987, 41.621] |
| baseline/overall/rr | 42.225 | [39.957, 44.374] |
| baseline/S+/frr | 33.404 | [31.235, 35.462] |
| baseline/U+/frr | 31.690 | [22.421, 42.030] |
| baseline/U-/false_acceptance | 57.955 | [47.510, 68.404] |
| baseline/gap/auroc | 18.584 | [13.489, 23.802] |
| baseline/gap/rej_f1 | -1.833 | [-9.824, 7.917] |
| baseline/gap/gmiou1 | 2.326 | [-3.866, 8.855] |
| experiment/S/rej_f1 | 51.236 | [48.936, 53.457] |
| experiment/S/gmiou1 | 39.563 | [38.318, 40.828] |
| experiment/S/rr | 39.358 | [37.296, 41.371] |
| experiment/S/auroc | 78.183 | [76.499, 79.833] |
| experiment/U/rej_f1 | 29.114 | [21.538, 36.975] |
| experiment/U/gmiou1 | 24.980 | [20.844, 29.154] |
| experiment/U/rr | 12.808 | [9.241, 16.749] |
| experiment/U/auroc | 66.325 | [60.180, 72.474] |
| experiment/overall/rej_f1 | 48.796 | [46.498, 50.983] |
| experiment/overall/gmiou1 | 38.279 | [37.055, 39.504] |
| experiment/overall/rr | 37.020 | [35.034, 39.015] |
| experiment/S+/frr | 30.263 | [28.198, 32.247] |
| experiment/U+/frr | 4.225 | [0.847, 8.451] |
| experiment/U-/false_acceptance | 82.576 | [76.743, 87.699] |
| experiment/gap/auroc | 11.858 | [5.142, 18.364] |
| experiment/gap/rej_f1 | 22.122 | [14.240, 30.069] |
| experiment/gap/gmiou1 | 14.583 | [10.314, 18.856] |
| candidates/S+/coverage | 99.909 | [99.756, 100.000] |
| candidates/S+/gt_recall | 99.909 | [99.756, 100.000] |
| candidates/S+/top1_hit | 51.133 | [48.986, 53.238] |
| candidates/S+/high_count | 0.651 | [0.606, 0.694] |
| candidates/S+/relative_count | 11.056 | [10.801, 11.336] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 0.733 | [0.645, 0.821] |
| candidates/S-/relative_count | 11.436 | [10.961, 11.917] |
| candidates/U+/coverage | 99.296 | [97.674, 100.000] |
| candidates/U+/gt_recall | 99.296 | [97.674, 100.000] |
| candidates/U+/top1_hit | 50.704 | [40.306, 61.075] |
| candidates/U+/high_count | 0.599 | [0.429, 0.784] |
| candidates/U+/relative_count | 11.387 | [10.483, 12.445] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 0.462 | [0.327, 0.614] |
| candidates/U-/relative_count | 11.545 | [10.451, 12.748] |
| comparison/seen_change/auroc | -0.769 | [-1.556, 0.034] |
| comparison/unseen_net_gain/auroc | 5.957 | [1.384, 10.317] |
| comparison/gap_reduction/auroc | 6.726 | [1.897, 11.035] |
| comparison/seen_change/rej_f1 | 0.212 | [-1.002, 1.428] |
| comparison/unseen_net_gain/rej_f1 | -23.743 | [-30.901, -16.932] |
| comparison/gap_reduction/rej_f1 | -23.955 | [-30.995, -17.073] |
| comparison/seen_change/gmiou1 | -0.974 | [-1.907, -0.088] |
| comparison/unseen_net_gain/gmiou1 | -13.230 | [-18.482, -8.022] |
| comparison/gap_reduction/gmiou1 | -12.256 | [-17.541, -6.988] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
