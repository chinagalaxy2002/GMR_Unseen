# Frozen final evaluation

Counts: {'S+': 3230, 'S-': 1066, 'U+': 223, 'U-': 92}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 54.031 | [51.647, 56.279] |
| baseline/S/gmiou1 | 35.314 | [33.971, 36.660] |
| baseline/S/rr | 40.154 | [37.761, 42.518] |
| baseline/S/auroc | 75.445 | [73.572, 77.232] |
| baseline/U/rej_f1 | 2.151 | [0.000, 7.059] |
| baseline/U/gmiou1 | 20.748 | [17.325, 24.203] |
| baseline/U/rr | 0.317 | [0.000, 1.031] |
| baseline/U/auroc | 50.751 | [45.696, 55.589] |
| baseline/overall/rej_f1 | 52.358 | [49.981, 54.636] |
| baseline/overall/gmiou1 | 34.319 | [33.064, 35.605] |
| baseline/overall/rr | 37.432 | [35.120, 39.669] |
| baseline/S+/frr | 30.062 | [28.019, 32.049] |
| baseline/U+/frr | 0.000 | [0.000, 0.000] |
| baseline/U-/false_acceptance | 98.913 | [96.341, 100.000] |
| baseline/gap/auroc | 24.694 | [19.396, 30.124] |
| baseline/gap/rej_f1 | 51.880 | [46.593, 55.689] |
| baseline/gap/gmiou1 | 14.565 | [10.641, 18.203] |
| experiment/S/rej_f1 | 53.928 | [51.525, 56.143] |
| experiment/S/gmiou1 | 34.841 | [33.459, 36.284] |
| experiment/S/rr | 43.040 | [40.618, 45.403] |
| experiment/S/auroc | 76.268 | [74.395, 78.003] |
| experiment/U/rej_f1 | 2.151 | [0.000, 7.059] |
| experiment/U/gmiou1 | 20.964 | [17.099, 24.832] |
| experiment/U/rr | 0.317 | [0.000, 1.031] |
| experiment/U/auroc | 54.263 | [49.031, 59.714] |
| experiment/overall/rej_f1 | 52.327 | [49.915, 54.540] |
| experiment/overall/gmiou1 | 33.893 | [32.574, 35.248] |
| experiment/overall/rr | 40.121 | [37.801, 42.408] |
| experiment/S+/frr | 32.910 | [30.730, 34.958] |
| experiment/U+/frr | 0.000 | [0.000, 0.000] |
| experiment/U-/false_acceptance | 98.913 | [96.341, 100.000] |
| experiment/gap/auroc | 22.005 | [16.237, 27.677] |
| experiment/gap/rej_f1 | 51.777 | [46.629, 55.609] |
| experiment/gap/gmiou1 | 13.877 | [9.641, 17.943] |
| candidates/S+/coverage | 79.040 | [77.364, 80.768] |
| candidates/S+/gt_recall | 79.040 | [77.364, 80.768] |
| candidates/S+/top1_hit | 35.201 | [33.118, 37.167] |
| candidates/S+/high_count | 2.472 | [2.444, 2.502] |
| candidates/S+/relative_count | 2.518 | [2.490, 2.547] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.168 | [2.079, 2.259] |
| candidates/S-/relative_count | 2.393 | [2.323, 2.462] |
| candidates/U+/coverage | 83.857 | [77.871, 89.083] |
| candidates/U+/gt_recall | 83.857 | [77.871, 89.083] |
| candidates/U+/top1_hit | 32.287 | [24.774, 40.164] |
| candidates/U+/high_count | 2.767 | [2.681, 2.844] |
| candidates/U+/relative_count | 2.780 | [2.697, 2.854] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.837 | [2.701, 2.943] |
| candidates/U-/relative_count | 2.859 | [2.727, 2.955] |
| comparison/seen_change/auroc | 0.823 | [0.261, 1.391] |
| comparison/unseen_net_gain/auroc | 3.512 | [-1.012, 8.083] |
| comparison/gap_reduction/auroc | 2.689 | [-1.858, 7.252] |
| comparison/seen_change/rej_f1 | -0.103 | [-0.991, 0.801] |
| comparison/unseen_net_gain/rej_f1 | 0.000 | [0.000, 0.000] |
| comparison/gap_reduction/rej_f1 | 0.103 | [-0.801, 0.991] |
| comparison/seen_change/gmiou1 | -0.473 | [-1.242, 0.311] |
| comparison/unseen_net_gain/gmiou1 | 0.216 | [-3.006, 3.571] |
| comparison/gap_reduction/gmiou1 | 0.689 | [-2.594, 4.061] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
