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
| experiment/S/rej_f1 | 46.446 | [44.060, 48.643] |
| experiment/S/gmiou1 | 32.911 | [31.666, 34.150] |
| experiment/S/rr | 41.750 | [39.655, 43.882] |
| experiment/S/auroc | 69.923 | [67.553, 72.341] |
| experiment/U/rej_f1 | 58.974 | [52.080, 65.172] |
| experiment/U/gmiou1 | 41.689 | [35.220, 48.332] |
| experiment/U/rr | 98.655 | [96.982, 100.000] |
| experiment/U/auroc | 51.888 | [43.826, 60.291] |
| experiment/overall/rej_f1 | 47.664 | [45.329, 49.767] |
| experiment/overall/gmiou1 | 33.335 | [32.116, 34.538] |
| experiment/overall/rr | 44.502 | [42.401, 46.593] |
| experiment/S+/frr | 34.889 | [32.831, 36.883] |
| experiment/U+/frr | 97.710 | [94.999, 100.000] |
| experiment/U-/false_acceptance | 0.000 | [0.000, 0.000] |
| experiment/gap/auroc | 18.035 | [9.158, 26.951] |
| experiment/gap/rej_f1 | -12.529 | [-19.162, -5.089] |
| experiment/gap/gmiou1 | -8.779 | [-15.355, -1.982] |
| candidates/S+/coverage | 78.326 | [76.554, 80.208] |
| candidates/S+/gt_recall | 78.326 | [76.554, 80.208] |
| candidates/S+/top1_hit | 36.996 | [35.120, 38.897] |
| candidates/S+/high_count | 2.579 | [2.549, 2.609] |
| candidates/S+/relative_count | 2.603 | [2.574, 2.631] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.498 | [2.434, 2.559] |
| candidates/S-/relative_count | 2.524 | [2.462, 2.585] |
| candidates/U+/coverage | 69.466 | [60.317, 78.512] |
| candidates/U+/gt_recall | 69.466 | [60.317, 78.512] |
| candidates/U+/top1_hit | 30.534 | [21.551, 39.880] |
| candidates/U+/high_count | 2.626 | [2.468, 2.779] |
| candidates/U+/relative_count | 2.664 | [2.510, 2.810] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.652 | [2.487, 2.802] |
| candidates/U-/relative_count | 2.707 | [2.546, 2.843] |
| comparison/seen_change/auroc | 0.000 | [0.000, 0.000] |
| comparison/unseen_net_gain/auroc | 0.000 | [0.000, 0.000] |
| comparison/gap_reduction/auroc | -0.000 | [-0.000, 0.000] |
| comparison/seen_change/rej_f1 | 0.000 | [0.000, 0.000] |
| comparison/unseen_net_gain/rej_f1 | 0.000 | [0.000, 0.000] |
| comparison/gap_reduction/rej_f1 | -0.000 | [-0.000, 0.000] |
| comparison/seen_change/gmiou1 | 0.000 | [0.000, 0.000] |
| comparison/unseen_net_gain/gmiou1 | 0.000 | [0.000, 0.000] |
| comparison/gap_reduction/gmiou1 | -0.000 | [-0.000, 0.000] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
