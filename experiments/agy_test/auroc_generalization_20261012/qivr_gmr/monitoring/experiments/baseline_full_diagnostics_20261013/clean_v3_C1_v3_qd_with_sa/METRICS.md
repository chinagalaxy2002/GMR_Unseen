# Frozen final evaluation

Counts: {'S+': 3311, 'S-': 894, 'U+': 142, 'U-': 264}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 51.290 | [49.025, 53.451] |
| baseline/S/gmiou1 | 33.891 | [32.577, 35.114] |
| baseline/S/rr | 41.427 | [39.332, 43.511] |
| baseline/S/auroc | 78.534 | [76.795, 80.294] |
| baseline/U/rej_f1 | 26.300 | [18.342, 34.170] |
| baseline/U/gmiou1 | 24.403 | [20.366, 28.472] |
| baseline/U/rr | 15.517 | [10.670, 20.632] |
| baseline/U/auroc | 57.750 | [52.582, 63.055] |
| baseline/overall/rej_f1 | 48.532 | [46.268, 50.745] |
| baseline/overall/gmiou1 | 33.056 | [31.758, 34.242] |
| baseline/overall/rr | 39.146 | [37.081, 41.202] |
| baseline/S+/frr | 32.196 | [30.112, 34.236] |
| baseline/U+/frr | 14.085 | [7.970, 20.690] |
| baseline/U-/false_acceptance | 83.712 | [77.642, 89.338] |
| baseline/gap/auroc | 20.783 | [14.954, 26.506] |
| baseline/gap/rej_f1 | 24.990 | [16.881, 33.126] |
| baseline/gap/gmiou1 | 9.488 | [5.222, 13.647] |
| experiment/S/rej_f1 | 49.449 | [47.311, 51.471] |
| experiment/S/gmiou1 | 33.137 | [31.911, 34.424] |
| experiment/S/rr | 49.917 | [47.732, 52.033] |
| experiment/S/auroc | 78.426 | [76.746, 80.097] |
| experiment/U/rej_f1 | 60.738 | [53.588, 66.786] |
| experiment/U/gmiou1 | 43.210 | [37.824, 48.504] |
| experiment/U/rr | 48.522 | [41.351, 55.677] |
| experiment/U/auroc | 60.074 | [53.886, 66.002] |
| experiment/overall/rej_f1 | 50.955 | [49.009, 52.861] |
| experiment/overall/gmiou1 | 34.024 | [32.836, 35.287] |
| experiment/overall/rr | 49.794 | [47.616, 51.860] |
| experiment/S+/frr | 41.045 | [38.829, 43.229] |
| experiment/U+/frr | 40.141 | [30.303, 50.000] |
| experiment/U-/false_acceptance | 46.970 | [38.775, 55.557] |
| experiment/gap/auroc | 18.353 | [11.880, 24.951] |
| experiment/gap/rej_f1 | -11.289 | [-17.725, -3.898] |
| experiment/gap/gmiou1 | -10.072 | [-15.559, -4.298] |
| candidates/S+/coverage | 73.331 | [71.420, 75.231] |
| candidates/S+/gt_recall | 73.331 | [71.420, 75.231] |
| candidates/S+/top1_hit | 34.582 | [32.619, 36.520] |
| candidates/S+/high_count | 2.473 | [2.444, 2.503] |
| candidates/S+/relative_count | 2.506 | [2.477, 2.535] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.348 | [2.286, 2.411] |
| candidates/S-/relative_count | 2.508 | [2.451, 2.565] |
| candidates/U+/coverage | 79.577 | [70.779, 87.744] |
| candidates/U+/gt_recall | 79.577 | [70.779, 87.744] |
| candidates/U+/top1_hit | 47.887 | [37.931, 58.001] |
| candidates/U+/high_count | 2.246 | [2.075, 2.421] |
| candidates/U+/relative_count | 2.261 | [2.085, 2.438] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.383 | [2.202, 2.564] |
| candidates/U-/relative_count | 2.413 | [2.231, 2.593] |
| comparison/seen_change/auroc | -0.107 | [-0.940, 0.735] |
| comparison/unseen_net_gain/auroc | 2.323 | [-1.872, 6.157] |
| comparison/gap_reduction/auroc | 2.431 | [-1.782, 6.342] |
| comparison/seen_change/rej_f1 | -1.841 | [-3.005, -0.617] |
| comparison/unseen_net_gain/rej_f1 | 34.438 | [26.624, 42.608] |
| comparison/gap_reduction/rej_f1 | 36.279 | [28.240, 44.419] |
| comparison/seen_change/gmiou1 | -0.754 | [-1.654, 0.124] |
| comparison/unseen_net_gain/gmiou1 | 18.807 | [13.358, 24.049] |
| comparison/gap_reduction/gmiou1 | 19.561 | [14.116, 24.902] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
