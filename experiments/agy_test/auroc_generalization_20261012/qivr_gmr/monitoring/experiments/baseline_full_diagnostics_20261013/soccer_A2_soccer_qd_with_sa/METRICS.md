# Frozen final evaluation

Counts: {'S+': 829, 'S-': 1128, 'U+': 107, 'U-': 169}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 70.450 | [67.875, 72.680] |
| baseline/S/gmiou1 | 42.299 | [39.363, 45.047] |
| baseline/S/rr | 59.428 | [56.004, 62.668] |
| baseline/S/auroc | 70.374 | [68.215, 72.201] |
| baseline/U/rej_f1 | 74.792 | [69.669, 79.507] |
| baseline/U/gmiou1 | 49.287 | [43.129, 55.817] |
| baseline/U/rr | 69.565 | [63.636, 75.352] |
| baseline/U/auroc | 65.080 | [58.565, 71.249] |
| baseline/overall/rej_f1 | 71.041 | [68.612, 73.151] |
| baseline/overall/gmiou1 | 43.163 | [40.288, 45.783] |
| baseline/overall/rr | 60.681 | [57.232, 63.899] |
| baseline/S+/frr | 42.943 | [39.298, 46.659] |
| baseline/U+/frr | 53.271 | [45.000, 62.105] |
| baseline/U-/false_acceptance | 20.118 | [14.197, 26.144] |
| baseline/gap/auroc | 5.294 | [-1.477, 12.118] |
| baseline/gap/rej_f1 | -4.343 | [-9.395, 0.817] |
| baseline/gap/gmiou1 | -6.988 | [-13.512, -0.887] |
| experiment/S/rej_f1 | 74.290 | [72.153, 76.191] |
| experiment/S/gmiou1 | 47.563 | [44.801, 50.182] |
| experiment/S/rr | 68.370 | [65.344, 71.161] |
| experiment/S/auroc | 71.001 | [69.086, 72.796] |
| experiment/U/rej_f1 | 79.803 | [75.377, 83.929] |
| experiment/U/gmiou1 | 59.290 | [52.925, 66.077] |
| experiment/U/rr | 85.870 | [81.588, 89.884] |
| experiment/U/auroc | 65.902 | [59.323, 71.924] |
| experiment/overall/rej_f1 | 75.070 | [73.123, 76.807] |
| experiment/overall/gmiou1 | 49.012 | [46.365, 51.481] |
| experiment/overall/rr | 70.533 | [67.584, 73.133] |
| experiment/S+/frr | 50.905 | [47.697, 54.355] |
| experiment/U+/frr | 70.093 | [63.462, 76.925] |
| experiment/U-/false_acceptance | 4.142 | [1.351, 7.472] |
| experiment/gap/auroc | 5.099 | [-1.440, 12.074] |
| experiment/gap/rej_f1 | -5.513 | [-10.249, -0.629] |
| experiment/gap/gmiou1 | -11.727 | [-18.582, -5.019] |
| candidates/S+/coverage | 35.344 | [31.162, 39.546] |
| candidates/S+/gt_recall | 22.274 | [19.486, 25.027] |
| candidates/S+/top1_hit | 2.895 | [1.756, 4.182] |
| candidates/S+/high_count | 2.982 | [2.802, 3.164] |
| candidates/S+/relative_count | 9.417 | [9.385, 9.448] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 0.160 | [0.090, 0.241] |
| candidates/S-/relative_count | 9.574 | [9.538, 9.608] |
| candidates/U+/coverage | 40.187 | [29.058, 51.852] |
| candidates/U+/gt_recall | 27.336 | [19.468, 35.920] |
| candidates/U+/top1_hit | 2.804 | [0.000, 6.195] |
| candidates/U+/high_count | 2.271 | [1.761, 2.743] |
| candidates/U+/relative_count | 9.467 | [9.375, 9.562] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 0.000 | [0.000, 0.000] |
| candidates/U-/relative_count | 9.645 | [9.569, 9.720] |
| comparison/seen_change/auroc | 0.627 | [-0.817, 2.055] |
| comparison/unseen_net_gain/auroc | 0.821 | [-2.993, 4.478] |
| comparison/gap_reduction/auroc | 0.194 | [-3.927, 4.071] |
| comparison/seen_change/rej_f1 | 3.841 | [2.189, 5.598] |
| comparison/unseen_net_gain/rej_f1 | 5.011 | [1.579, 8.602] |
| comparison/gap_reduction/rej_f1 | 1.170 | [-2.553, 4.933] |
| comparison/seen_change/gmiou1 | 5.264 | [3.699, 6.902] |
| comparison/unseen_net_gain/gmiou1 | 10.003 | [6.588, 13.586] |
| comparison/gap_reduction/gmiou1 | 4.739 | [1.191, 8.284] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
