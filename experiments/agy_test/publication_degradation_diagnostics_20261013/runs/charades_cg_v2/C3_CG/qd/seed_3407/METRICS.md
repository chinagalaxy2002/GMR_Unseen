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
| experiment/S/rej_f1 | 30.405 | [28.269, 32.491] |
| experiment/S/gmiou1 | 24.247 | [23.169, 25.370] |
| experiment/S/rr | 20.827 | [19.578, 22.118] |
| experiment/S/auroc | 50.267 | [48.665, 52.015] |
| experiment/U/rej_f1 | 23.934 | [22.019, 25.834] |
| experiment/U/gmiou1 | 18.826 | [17.927, 19.672] |
| experiment/U/rr | 15.117 | [14.107, 16.077] |
| experiment/U/auroc | 49.486 | [47.816, 51.065] |
| experiment/overall/rej_f1 | 27.131 | [25.585, 28.640] |
| experiment/overall/gmiou1 | 21.390 | [20.682, 22.127] |
| experiment/overall/rr | 17.818 | [16.948, 18.664] |
| experiment/S+/frr | 20.119 | [18.405, 21.793] |
| experiment/U+/frr | 14.649 | [13.276, 15.975] |
| experiment/U-/false_acceptance | 84.415 | [83.033, 85.796] |
| experiment/gap/auroc | 0.780 | [-1.350, 2.909] |
| experiment/gap/rej_f1 | 6.471 | [3.882, 9.111] |
| experiment/gap/gmiou1 | 5.421 | [4.169, 6.774] |
| candidates/S+/coverage | 88.525 | [87.144, 89.779] |
| candidates/S+/gt_recall | 88.525 | [87.144, 89.779] |
| candidates/S+/top1_hit | 38.823 | [36.627, 40.901] |
| candidates/S+/high_count | 2.344 | [2.306, 2.383] |
| candidates/S+/relative_count | 2.423 | [2.387, 2.460] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.324 | [2.286, 2.360] |
| candidates/S-/relative_count | 2.413 | [2.377, 2.449] |
| candidates/U+/coverage | 87.291 | [85.930, 88.504] |
| candidates/U+/gt_recall | 87.291 | [85.930, 88.504] |
| candidates/U+/top1_hit | 27.358 | [25.619, 29.224] |
| candidates/U+/high_count | 2.599 | [2.569, 2.628] |
| candidates/U+/relative_count | 2.677 | [2.648, 2.706] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.613 | [2.583, 2.643] |
| candidates/U-/relative_count | 2.675 | [2.647, 2.702] |
| comparison/seen_change/auroc | -0.231 | [-2.550, 2.088] |
| comparison/unseen_net_gain/auroc | -0.350 | [-2.352, 1.556] |
| comparison/gap_reduction/auroc | -0.119 | [-2.878, 2.783] |
| comparison/seen_change/rej_f1 | -27.010 | [-29.541, -24.577] |
| comparison/unseen_net_gain/rej_f1 | -33.641 | [-35.948, -31.287] |
| comparison/gap_reduction/rej_f1 | -6.631 | [-9.625, -3.553] |
| comparison/seen_change/gmiou1 | -15.195 | [-17.099, -13.468] |
| comparison/unseen_net_gain/gmiou1 | -19.283 | [-20.970, -17.696] |
| comparison/gap_reduction/gmiou1 | -4.088 | [-6.231, -1.810] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
