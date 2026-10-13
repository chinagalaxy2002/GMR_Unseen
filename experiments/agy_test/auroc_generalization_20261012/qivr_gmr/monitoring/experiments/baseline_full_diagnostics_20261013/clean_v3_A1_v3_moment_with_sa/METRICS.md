# Frozen final evaluation

Counts: {'S+': 2857, 'S-': 983, 'U+': 596, 'U-': 175}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 56.375 | [53.699, 58.929] |
| baseline/S/gmiou1 | 37.786 | [36.225, 39.279] |
| baseline/S/rr | 35.469 | [32.955, 37.895] |
| baseline/S/auroc | 74.990 | [72.927, 76.992] |
| baseline/U/rej_f1 | 37.356 | [30.405, 43.990] |
| baseline/U/gmiou1 | 23.763 | [21.107, 26.228] |
| baseline/U/rr | 22.438 | [18.742, 26.115] |
| baseline/U/auroc | 64.392 | [59.315, 69.032] |
| baseline/overall/rej_f1 | 53.918 | [51.352, 56.442] |
| baseline/overall/gmiou1 | 35.441 | [34.059, 36.784] |
| baseline/overall/rr | 33.290 | [31.055, 35.473] |
| baseline/S+/frr | 24.536 | [22.367, 26.567] |
| baseline/U+/frr | 18.121 | [14.497, 21.828] |
| baseline/U-/false_acceptance | 62.857 | [54.877, 70.811] |
| baseline/gap/auroc | 10.598 | [5.558, 15.873] |
| baseline/gap/rej_f1 | 19.019 | [12.094, 26.341] |
| baseline/gap/gmiou1 | 14.022 | [11.176, 17.098] |
| experiment/S/rej_f1 | 56.646 | [54.136, 59.101] |
| experiment/S/gmiou1 | 38.319 | [36.872, 39.788] |
| experiment/S/rr | 38.854 | [36.409, 41.297] |
| experiment/S/auroc | 75.728 | [73.703, 77.710] |
| experiment/U/rej_f1 | 41.089 | [34.957, 47.091] |
| experiment/U/gmiou1 | 25.207 | [22.665, 27.656] |
| experiment/U/rr | 29.702 | [25.826, 33.686] |
| experiment/U/auroc | 64.125 | [59.134, 68.922] |
| experiment/overall/rej_f1 | 54.463 | [52.131, 56.866] |
| experiment/overall/gmiou1 | 36.127 | [34.826, 37.495] |
| experiment/overall/rr | 37.324 | [35.132, 39.570] |
| experiment/S+/frr | 27.686 | [25.535, 29.727] |
| experiment/U+/frr | 24.497 | [20.713, 28.521] |
| experiment/U-/false_acceptance | 52.571 | [44.509, 60.656] |
| experiment/gap/auroc | 11.603 | [6.523, 16.851] |
| experiment/gap/rej_f1 | 15.557 | [9.092, 22.171] |
| experiment/gap/gmiou1 | 13.112 | [10.239, 16.179] |
| candidates/S+/coverage | 72.104 | [69.939, 74.142] |
| candidates/S+/gt_recall | 72.104 | [69.939, 74.142] |
| candidates/S+/top1_hit | 40.637 | [38.515, 42.692] |
| candidates/S+/high_count | 2.082 | [2.046, 2.118] |
| candidates/S+/relative_count | 2.138 | [2.102, 2.173] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 1.759 | [1.673, 1.850] |
| candidates/S-/relative_count | 2.066 | [1.971, 2.172] |
| candidates/U+/coverage | 60.067 | [55.897, 64.623] |
| candidates/U+/gt_recall | 60.067 | [55.897, 64.623] |
| candidates/U+/top1_hit | 24.161 | [20.473, 27.749] |
| candidates/U+/high_count | 2.267 | [2.202, 2.332] |
| candidates/U+/relative_count | 2.312 | [2.248, 2.379] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.217 | [2.103, 2.331] |
| candidates/U-/relative_count | 2.297 | [2.183, 2.410] |
| comparison/seen_change/auroc | 0.737 | [0.022, 1.442] |
| comparison/unseen_net_gain/auroc | -0.267 | [-2.545, 1.952] |
| comparison/gap_reduction/auroc | -1.005 | [-3.336, 1.286] |
| comparison/seen_change/rej_f1 | 0.271 | [-1.017, 1.644] |
| comparison/unseen_net_gain/rej_f1 | 3.733 | [-0.554, 8.598] |
| comparison/gap_reduction/rej_f1 | 3.462 | [-1.013, 8.431] |
| comparison/seen_change/gmiou1 | 0.534 | [-0.343, 1.520] |
| comparison/unseen_net_gain/gmiou1 | 1.444 | [-0.402, 3.249] |
| comparison/gap_reduction/gmiou1 | 0.910 | [-1.129, 3.015] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
