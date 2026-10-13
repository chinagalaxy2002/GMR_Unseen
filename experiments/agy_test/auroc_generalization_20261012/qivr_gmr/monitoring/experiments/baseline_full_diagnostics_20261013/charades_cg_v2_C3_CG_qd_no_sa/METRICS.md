# Frozen final evaluation

Counts: {'S+': 2684, 'S-': 2684, 'U+': 2990, 'U-': 2990}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 57.415 | [55.640, 59.304] |
| baseline/S/gmiou1 | 39.442 | [37.931, 41.153] |
| baseline/S/rr | 67.325 | [65.720, 69.022] |
| baseline/S/auroc | 50.498 | [48.574, 52.536] |
| baseline/U/rej_f1 | 57.576 | [55.980, 59.099] |
| baseline/U/gmiou1 | 38.109 | [36.736, 39.479] |
| baseline/U/rr | 66.990 | [65.445, 68.557] |
| baseline/U/auroc | 49.836 | [48.223, 51.495] |
| baseline/overall/rej_f1 | 57.500 | [56.160, 58.811] |
| baseline/overall/gmiou1 | 38.740 | [37.596, 39.906] |
| baseline/overall/rr | 67.148 | [65.847, 68.476] |
| baseline/S+/frr | 67.288 | [65.017, 69.633] |
| baseline/U+/frr | 66.622 | [64.636, 68.682] |
| baseline/U-/false_acceptance | 32.642 | [30.572, 34.711] |
| baseline/gap/auroc | 0.661 | [-1.552, 3.132] |
| baseline/gap/rej_f1 | -0.161 | [-2.215, 2.114] |
| baseline/gap/gmiou1 | 1.333 | [-0.450, 3.254] |
| experiment/S/rej_f1 | 23.923 | [21.962, 25.832] |
| experiment/S/gmiou1 | 17.804 | [16.890, 18.723] |
| experiment/S/rr | 15.723 | [14.769, 16.736] |
| experiment/S/auroc | 50.041 | [48.629, 51.402] |
| experiment/U/rej_f1 | 17.702 | [15.918, 19.380] |
| experiment/U/gmiou1 | 15.009 | [14.162, 15.771] |
| experiment/U/rr | 10.836 | [10.028, 11.652] |
| experiment/U/auroc | 49.916 | [48.713, 50.999] |
| experiment/overall/rej_f1 | 20.765 | [19.492, 22.062] |
| experiment/overall/gmiou1 | 16.331 | [15.694, 16.911] |
| experiment/overall/rr | 13.148 | [12.532, 13.786] |
| experiment/S+/frr | 15.723 | [14.380, 17.103] |
| experiment/U+/frr | 10.903 | [9.812, 12.124] |
| experiment/U-/false_acceptance | 89.231 | [88.092, 90.403] |
| experiment/gap/auroc | 0.125 | [-1.659, 1.941] |
| experiment/gap/rej_f1 | 6.221 | [3.664, 8.899] |
| experiment/gap/gmiou1 | 2.795 | [1.549, 4.035] |
| candidates/S+/coverage | 92.996 | [91.809, 94.099] |
| candidates/S+/gt_recall | 92.996 | [91.809, 94.099] |
| candidates/S+/top1_hit | 20.082 | [18.356, 21.774] |
| candidates/S+/high_count | 0.000 | [0.000, 0.000] |
| candidates/S+/relative_count | 10.000 | [10.000, 10.000] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 0.000 | [0.000, 0.000] |
| candidates/S-/relative_count | 9.997 | [9.990, 10.000] |
| candidates/U+/coverage | 89.599 | [88.256, 90.934] |
| candidates/U+/gt_recall | 89.599 | [88.256, 90.934] |
| candidates/U+/top1_hit | 19.532 | [17.878, 21.142] |
| candidates/U+/high_count | 0.000 | [0.000, 0.000] |
| candidates/U+/relative_count | 10.000 | [10.000, 10.000] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 0.000 | [0.000, 0.000] |
| candidates/U-/relative_count | 10.000 | [10.000, 10.000] |
| comparison/seen_change/auroc | -0.457 | [-2.972, 1.789] |
| comparison/unseen_net_gain/auroc | 0.080 | [-1.950, 1.953] |
| comparison/gap_reduction/auroc | 0.536 | [-2.291, 3.567] |
| comparison/seen_change/rej_f1 | -33.492 | [-36.205, -30.964] |
| comparison/unseen_net_gain/rej_f1 | -39.874 | [-42.251, -37.503] |
| comparison/gap_reduction/rej_f1 | -6.382 | [-9.734, -3.046] |
| comparison/seen_change/gmiou1 | -21.638 | [-23.582, -19.765] |
| comparison/unseen_net_gain/gmiou1 | -23.101 | [-24.826, -21.421] |
| comparison/gap_reduction/gmiou1 | -1.462 | [-3.734, 0.899] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
