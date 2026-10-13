# Frozen final evaluation

Counts: {'S+': 2857, 'S-': 983, 'U+': 596, 'U-': 175}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 57.689 | [54.925, 60.330] |
| baseline/S/gmiou1 | 45.200 | [43.660, 46.821] |
| baseline/S/rr | 37.057 | [34.661, 39.397] |
| baseline/S/auroc | 75.302 | [72.902, 77.558] |
| baseline/U/rej_f1 | 44.111 | [38.596, 49.534] |
| baseline/U/gmiou1 | 30.453 | [27.534, 33.292] |
| baseline/U/rr | 37.873 | [33.804, 42.039] |
| baseline/U/auroc | 66.136 | [61.211, 71.204] |
| baseline/overall/rej_f1 | 55.482 | [52.900, 57.984] |
| baseline/overall/gmiou1 | 42.734 | [41.269, 44.263] |
| baseline/overall/rr | 37.194 | [35.049, 39.317] |
| baseline/S+/frr | 25.516 | [23.459, 27.600] |
| baseline/U+/frr | 31.711 | [27.551, 35.944] |
| baseline/U-/false_acceptance | 41.143 | [32.941, 49.432] |
| baseline/gap/auroc | 9.166 | [3.687, 14.239] |
| baseline/gap/rej_f1 | 13.578 | [7.520, 19.451] |
| baseline/gap/gmiou1 | 14.746 | [11.557, 17.950] |
| experiment/S/rej_f1 | 55.721 | [52.898, 58.282] |
| experiment/S/gmiou1 | 44.484 | [42.969, 46.045] |
| experiment/S/rr | 40.859 | [38.449, 43.277] |
| experiment/S/auroc | 75.822 | [73.537, 78.046] |
| experiment/U/rej_f1 | 41.553 | [35.491, 47.186] |
| experiment/U/gmiou1 | 28.925 | [26.082, 31.702] |
| experiment/U/rr | 34.112 | [30.090, 38.210] |
| experiment/U/auroc | 65.414 | [60.502, 70.318] |
| experiment/overall/rej_f1 | 53.645 | [51.076, 56.040] |
| experiment/overall/gmiou1 | 41.882 | [40.494, 43.260] |
| experiment/overall/rr | 39.731 | [37.508, 41.928] |
| experiment/S+/frr | 30.032 | [27.803, 32.102] |
| experiment/U+/frr | 28.859 | [24.824, 32.983] |
| experiment/U-/false_acceptance | 48.000 | [39.766, 56.377] |
| experiment/gap/auroc | 10.408 | [5.205, 15.581] |
| experiment/gap/rej_f1 | 14.168 | [8.012, 20.601] |
| experiment/gap/gmiou1 | 15.559 | [12.464, 18.755] |
| candidates/S+/coverage | 99.895 | [99.717, 100.000] |
| candidates/S+/gt_recall | 99.895 | [99.717, 100.000] |
| candidates/S+/top1_hit | 58.313 | [55.971, 60.497] |
| candidates/S+/high_count | 1.589 | [1.520, 1.658] |
| candidates/S+/relative_count | 5.678 | [5.530, 5.828] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 1.503 | [1.383, 1.622] |
| candidates/S-/relative_count | 6.052 | [5.789, 6.343] |
| candidates/U+/coverage | 99.832 | [99.463, 100.000] |
| candidates/U+/gt_recall | 99.832 | [99.463, 100.000] |
| candidates/U+/top1_hit | 31.879 | [27.674, 36.320] |
| candidates/U+/high_count | 1.154 | [1.035, 1.277] |
| candidates/U+/relative_count | 6.461 | [6.166, 6.760] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 1.171 | [0.994, 1.364] |
| candidates/U-/relative_count | 6.320 | [5.870, 6.800] |
| comparison/seen_change/auroc | 0.520 | [-0.328, 1.346] |
| comparison/unseen_net_gain/auroc | -0.722 | [-2.785, 1.151] |
| comparison/gap_reduction/auroc | -1.241 | [-3.400, 0.889] |
| comparison/seen_change/rej_f1 | -1.968 | [-3.294, -0.546] |
| comparison/unseen_net_gain/rej_f1 | -2.559 | [-5.919, 0.595] |
| comparison/gap_reduction/rej_f1 | -0.591 | [-4.109, 2.793] |
| comparison/seen_change/gmiou1 | -0.716 | [-1.725, 0.304] |
| comparison/unseen_net_gain/gmiou1 | -1.529 | [-3.740, 0.676] |
| comparison/gap_reduction/gmiou1 | -0.813 | [-3.172, 1.585] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
