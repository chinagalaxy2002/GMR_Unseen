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
| experiment/S/rej_f1 | 38.781 | [36.523, 40.939] |
| experiment/S/gmiou1 | 28.487 | [27.259, 29.710] |
| experiment/S/rr | 28.875 | [27.329, 30.319] |
| experiment/S/auroc | 51.659 | [49.987, 53.285] |
| experiment/U/rej_f1 | 46.081 | [44.186, 47.955] |
| experiment/U/gmiou1 | 29.987 | [28.743, 31.251] |
| experiment/U/rr | 41.739 | [40.185, 43.299] |
| experiment/U/auroc | 50.169 | [48.647, 51.746] |
| experiment/overall/rej_f1 | 42.901 | [41.262, 44.460] |
| experiment/overall/gmiou1 | 29.277 | [28.316, 30.228] |
| experiment/overall/rr | 35.654 | [34.371, 36.912] |
| experiment/S+/frr | 27.161 | [25.114, 29.112] |
| experiment/U+/frr | 41.204 | [39.169, 43.168] |
| experiment/U-/false_acceptance | 57.726 | [55.596, 59.852] |
| experiment/gap/auroc | 1.490 | [-0.669, 3.501] |
| experiment/gap/rej_f1 | -7.300 | [-9.934, -4.866] |
| experiment/gap/gmiou1 | -1.500 | [-3.074, 0.012] |
| candidates/S+/coverage | 88.711 | [87.408, 90.038] |
| candidates/S+/gt_recall | 88.711 | [87.408, 90.038] |
| candidates/S+/top1_hit | 33.308 | [31.301, 35.292] |
| candidates/S+/high_count | 2.115 | [2.065, 2.172] |
| candidates/S+/relative_count | 2.126 | [2.073, 2.185] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.137 | [2.091, 2.192] |
| candidates/S-/relative_count | 2.151 | [2.102, 2.210] |
| candidates/U+/coverage | 83.746 | [82.186, 85.250] |
| candidates/U+/gt_recall | 83.746 | [82.186, 85.250] |
| candidates/U+/top1_hit | 25.518 | [23.738, 27.421] |
| candidates/U+/high_count | 2.102 | [2.065, 2.147] |
| candidates/U+/relative_count | 2.109 | [2.070, 2.154] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.119 | [2.077, 2.166] |
| candidates/U-/relative_count | 2.124 | [2.082, 2.171] |
| comparison/seen_change/auroc | 1.162 | [-1.258, 3.578] |
| comparison/unseen_net_gain/auroc | 0.333 | [-1.849, 2.523] |
| comparison/gap_reduction/auroc | -0.829 | [-3.712, 2.341] |
| comparison/seen_change/rej_f1 | -18.634 | [-21.381, -16.189] |
| comparison/unseen_net_gain/rej_f1 | -11.495 | [-13.759, -9.176] |
| comparison/gap_reduction/rej_f1 | 7.139 | [4.298, 10.392] |
| comparison/seen_change/gmiou1 | -10.955 | [-12.882, -9.165] |
| comparison/unseen_net_gain/gmiou1 | -8.122 | [-9.815, -6.354] |
| comparison/gap_reduction/gmiou1 | 2.833 | [0.601, 5.251] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
