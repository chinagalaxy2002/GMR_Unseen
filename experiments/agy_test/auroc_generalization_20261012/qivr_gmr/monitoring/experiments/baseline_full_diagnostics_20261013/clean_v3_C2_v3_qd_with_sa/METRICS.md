# Frozen final evaluation

Counts: {'S+': 3322, 'S-': 1066, 'U+': 131, 'U-': 92}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 46.446 | [44.060, 48.643] |
| baseline/S/gmiou1 | 32.911 | [31.666, 34.150] |
| baseline/S/rr | 41.750 | [39.655, 43.882] |
| baseline/S/auroc | 69.923 | [67.553, 72.341] |
| baseline/U/rej_f1 | 58.974 | [52.080, 65.172] |
| baseline/U/gmiou1 | 41.689 | [35.220, 48.332] |
| baseline/U/rr | 98.655 | [96.982, 100.000] |
| baseline/U/auroc | 51.888 | [43.826, 60.291] |
| baseline/overall/rej_f1 | 47.664 | [45.329, 49.767] |
| baseline/overall/gmiou1 | 33.335 | [32.116, 34.538] |
| baseline/overall/rr | 44.502 | [42.401, 46.593] |
| baseline/S+/frr | 34.889 | [32.831, 36.883] |
| baseline/U+/frr | 97.710 | [94.999, 100.000] |
| baseline/U-/false_acceptance | 0.000 | [0.000, 0.000] |
| baseline/gap/auroc | 18.035 | [9.158, 26.951] |
| baseline/gap/rej_f1 | -12.529 | [-19.162, -5.089] |
| baseline/gap/gmiou1 | -8.779 | [-15.355, -1.982] |
| experiment/S/rej_f1 | 46.585 | [44.246, 48.939] |
| experiment/S/gmiou1 | 30.808 | [29.602, 32.019] |
| experiment/S/rr | 40.770 | [38.568, 42.817] |
| experiment/S/auroc | 68.257 | [65.789, 70.886] |
| experiment/U/rej_f1 | 58.974 | [52.080, 65.172] |
| experiment/U/gmiou1 | 41.811 | [35.381, 48.398] |
| experiment/U/rr | 98.655 | [96.982, 100.000] |
| experiment/U/auroc | 60.081 | [51.973, 67.833] |
| experiment/overall/rej_f1 | 47.805 | [45.570, 50.045] |
| experiment/overall/gmiou1 | 31.340 | [30.131, 32.523] |
| experiment/overall/rr | 43.570 | [41.366, 45.594] |
| experiment/S+/frr | 33.835 | [31.699, 35.796] |
| experiment/U+/frr | 97.710 | [94.999, 100.000] |
| experiment/U-/false_acceptance | 0.000 | [0.000, 0.000] |
| experiment/gap/auroc | 8.176 | [-0.205, 17.042] |
| experiment/gap/rej_f1 | -12.389 | [-19.022, -5.177] |
| experiment/gap/gmiou1 | -11.004 | [-17.546, -4.193] |
| candidates/S+/coverage | 76.189 | [74.326, 77.991] |
| candidates/S+/gt_recall | 76.189 | [74.326, 77.991] |
| candidates/S+/top1_hit | 33.865 | [31.972, 35.678] |
| candidates/S+/high_count | 2.749 | [2.729, 2.769] |
| candidates/S+/relative_count | 2.768 | [2.748, 2.787] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.693 | [2.643, 2.742] |
| candidates/S-/relative_count | 2.733 | [2.686, 2.779] |
| candidates/U+/coverage | 57.252 | [47.015, 67.191] |
| candidates/U+/gt_recall | 57.252 | [47.015, 67.191] |
| candidates/U+/top1_hit | 24.427 | [15.739, 32.880] |
| candidates/U+/high_count | 2.748 | [2.634, 2.857] |
| candidates/U+/relative_count | 2.779 | [2.669, 2.880] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.793 | [2.671, 2.901] |
| candidates/U-/relative_count | 2.826 | [2.711, 2.925] |
| comparison/seen_change/auroc | -1.666 | [-2.859, -0.434] |
| comparison/unseen_net_gain/auroc | 8.194 | [-1.785, 17.485] |
| comparison/gap_reduction/auroc | 9.859 | [-0.118, 19.335] |
| comparison/seen_change/rej_f1 | 0.139 | [-1.145, 1.482] |
| comparison/unseen_net_gain/rej_f1 | 0.000 | [0.000, 0.000] |
| comparison/gap_reduction/rej_f1 | -0.139 | [-1.482, 1.145] |
| comparison/seen_change/gmiou1 | -2.103 | [-3.020, -1.144] |
| comparison/unseen_net_gain/gmiou1 | 0.122 | [0.000, 0.316] |
| comparison/gap_reduction/gmiou1 | 2.225 | [1.223, 3.199] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
