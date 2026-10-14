# Frozen final evaluation

Counts: {'S+': 2857, 'S-': 983, 'U+': 596, 'U-': 175}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 55.515 | [51.730, 59.054] |
| baseline/S/gmiou1 | 39.433 | [37.853, 41.098] |
| baseline/S/rr | 24.219 | [22.319, 26.180] |
| baseline/S/auroc | 72.951 | [70.266, 75.564] |
| baseline/U/rej_f1 | 28.923 | [22.286, 35.594] |
| baseline/U/gmiou1 | 22.806 | [20.496, 25.246] |
| baseline/U/rr | 19.455 | [16.085, 23.183] |
| baseline/U/auroc | 55.862 | [51.043, 60.748] |
| baseline/overall/rej_f1 | 51.653 | [48.154, 54.914] |
| baseline/overall/gmiou1 | 36.653 | [35.197, 38.103] |
| baseline/overall/rr | 23.422 | [21.749, 25.208] |
| baseline/S+/frr | 13.966 | [12.384, 15.633] |
| baseline/U+/frr | 17.282 | [13.764, 21.053] |
| baseline/U-/false_acceptance | 73.143 | [65.475, 80.226] |
| baseline/gap/auroc | 17.089 | [11.661, 22.491] |
| baseline/gap/rej_f1 | 26.592 | [19.158, 34.224] |
| baseline/gap/gmiou1 | 16.627 | [13.780, 19.505] |
| experiment/S/rej_f1 | 57.608 | [54.845, 60.232] |
| experiment/S/gmiou1 | 36.485 | [34.897, 38.082] |
| experiment/S/rr | 30.365 | [28.015, 32.640] |
| experiment/S/auroc | 76.328 | [74.217, 78.421] |
| experiment/U/rej_f1 | 38.298 | [31.893, 44.560] |
| experiment/U/gmiou1 | 20.531 | [18.209, 22.947] |
| experiment/U/rr | 19.974 | [16.516, 23.457] |
| experiment/U/auroc | 67.818 | [63.030, 72.479] |
| experiment/overall/rej_f1 | 55.044 | [52.428, 57.648] |
| experiment/overall/gmiou1 | 33.817 | [32.393, 35.184] |
| experiment/overall/rr | 28.627 | [26.578, 30.617] |
| experiment/S+/frr | 19.146 | [17.269, 20.833] |
| experiment/U+/frr | 15.268 | [12.203, 18.482] |
| experiment/U-/false_acceptance | 64.000 | [56.068, 71.277] |
| experiment/gap/auroc | 8.510 | [3.455, 13.721] |
| experiment/gap/rej_f1 | 19.310 | [12.528, 26.126] |
| experiment/gap/gmiou1 | 15.954 | [13.130, 18.629] |
| candidates/S+/coverage | 88.344 | [86.865, 89.821] |
| candidates/S+/gt_recall | 88.344 | [86.865, 89.821] |
| candidates/S+/top1_hit | 35.352 | [33.262, 37.574] |
| candidates/S+/high_count | 2.535 | [2.501, 2.570] |
| candidates/S+/relative_count | 2.566 | [2.534, 2.602] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.144 | [2.028, 2.260] |
| candidates/S-/relative_count | 2.665 | [2.549, 2.796] |
| candidates/U+/coverage | 81.208 | [77.727, 84.591] |
| candidates/U+/gt_recall | 81.208 | [77.727, 84.591] |
| candidates/U+/top1_hit | 18.456 | [15.120, 21.775] |
| candidates/U+/high_count | 2.721 | [2.660, 2.780] |
| candidates/U+/relative_count | 2.728 | [2.666, 2.786] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.771 | [2.665, 2.865] |
| candidates/U-/relative_count | 2.771 | [2.665, 2.865] |
| comparison/seen_change/auroc | 3.377 | [1.279, 5.510] |
| comparison/unseen_net_gain/auroc | 11.956 | [7.379, 16.584] |
| comparison/gap_reduction/auroc | 8.579 | [3.592, 13.703] |
| comparison/seen_change/rej_f1 | 2.093 | [-0.687, 4.829] |
| comparison/unseen_net_gain/rej_f1 | 9.375 | [2.955, 16.194] |
| comparison/gap_reduction/rej_f1 | 7.282 | [0.572, 14.399] |
| comparison/seen_change/gmiou1 | -2.948 | [-4.513, -1.420] |
| comparison/unseen_net_gain/gmiou1 | -2.276 | [-4.964, 0.511] |
| comparison/gap_reduction/gmiou1 | 0.672 | [-2.424, 3.755] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
