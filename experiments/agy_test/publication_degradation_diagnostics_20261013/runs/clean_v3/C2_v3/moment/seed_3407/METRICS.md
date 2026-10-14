# Frozen final evaluation

Counts: {'S+': 3322, 'S-': 1066, 'U+': 131, 'U-': 92}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 45.070 | [42.421, 47.638] |
| baseline/S/gmiou1 | 32.244 | [31.006, 33.500] |
| baseline/S/rr | 32.338 | [30.215, 34.457] |
| baseline/S/auroc | 67.597 | [65.099, 70.242] |
| baseline/U/rej_f1 | 56.106 | [49.410, 62.421] |
| baseline/U/gmiou1 | 39.395 | [33.380, 45.642] |
| baseline/U/rr | 94.619 | [91.165, 97.510] |
| baseline/U/auroc | 49.262 | [41.495, 57.220] |
| baseline/overall/rej_f1 | 46.270 | [43.801, 48.735] |
| baseline/overall/gmiou1 | 32.590 | [31.387, 33.849] |
| baseline/overall/rr | 35.350 | [33.148, 37.432] |
| baseline/S+/frr | 25.858 | [23.798, 27.854] |
| baseline/U+/frr | 96.183 | [92.465, 99.187] |
| baseline/U-/false_acceptance | 7.609 | [2.353, 13.581] |
| baseline/gap/auroc | 18.335 | [10.020, 26.788] |
| baseline/gap/rej_f1 | -11.035 | [-17.921, -3.562] |
| baseline/gap/gmiou1 | -7.151 | [-13.428, -0.818] |
| experiment/S/rej_f1 | 43.681 | [41.121, 46.154] |
| experiment/S/gmiou1 | 32.213 | [30.943, 33.453] |
| experiment/S/rr | 37.375 | [35.235, 39.554] |
| experiment/S/auroc | 63.541 | [60.963, 66.186] |
| experiment/U/rej_f1 | 58.824 | [51.850, 65.132] |
| experiment/U/gmiou1 | 41.260 | [34.751, 47.930] |
| experiment/U/rr | 95.964 | [91.983, 98.696] |
| experiment/U/auroc | 56.107 | [48.743, 63.977] |
| experiment/overall/rej_f1 | 45.219 | [42.818, 47.622] |
| experiment/overall/gmiou1 | 32.651 | [31.428, 33.876] |
| experiment/overall/rr | 40.208 | [38.065, 42.401] |
| experiment/S+/frr | 31.577 | [29.526, 33.556] |
| experiment/U+/frr | 94.656 | [89.582, 98.438] |
| experiment/U-/false_acceptance | 2.174 | [0.000, 5.635] |
| experiment/gap/auroc | 7.434 | [-0.778, 15.509] |
| experiment/gap/rej_f1 | -15.143 | [-21.983, -7.844] |
| experiment/gap/gmiou1 | -9.047 | [-15.690, -2.355] |
| candidates/S+/coverage | 75.406 | [73.485, 77.211] |
| candidates/S+/gt_recall | 75.406 | [73.485, 77.211] |
| candidates/S+/top1_hit | 37.327 | [35.375, 39.228] |
| candidates/S+/high_count | 2.595 | [2.569, 2.623] |
| candidates/S+/relative_count | 2.629 | [2.603, 2.654] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.531 | [2.473, 2.590] |
| candidates/S-/relative_count | 2.581 | [2.526, 2.639] |
| candidates/U+/coverage | 70.229 | [60.991, 79.231] |
| candidates/U+/gt_recall | 70.229 | [60.991, 79.231] |
| candidates/U+/top1_hit | 32.061 | [23.021, 41.008] |
| candidates/U+/high_count | 2.649 | [2.521, 2.770] |
| candidates/U+/relative_count | 2.679 | [2.560, 2.795] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.685 | [2.544, 2.817] |
| candidates/U-/relative_count | 2.761 | [2.640, 2.872] |
| comparison/seen_change/auroc | -4.056 | [-5.280, -2.823] |
| comparison/unseen_net_gain/auroc | 6.845 | [0.212, 13.379] |
| comparison/gap_reduction/auroc | 10.901 | [4.311, 17.624] |
| comparison/seen_change/rej_f1 | -1.390 | [-2.863, 0.029] |
| comparison/unseen_net_gain/rej_f1 | 2.718 | [-0.001, 5.783] |
| comparison/gap_reduction/rej_f1 | 4.108 | [1.019, 7.497] |
| comparison/seen_change/gmiou1 | -0.030 | [-1.008, 0.903] |
| comparison/unseen_net_gain/gmiou1 | 1.866 | [-1.426, 5.224] |
| comparison/gap_reduction/gmiou1 | 1.896 | [-1.533, 5.271] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
