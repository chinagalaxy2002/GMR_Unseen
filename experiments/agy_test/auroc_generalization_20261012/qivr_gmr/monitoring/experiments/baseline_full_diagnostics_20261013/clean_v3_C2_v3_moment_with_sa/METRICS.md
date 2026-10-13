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
| experiment/S/rej_f1 | 46.154 | [43.672, 48.467] |
| experiment/S/gmiou1 | 31.635 | [30.345, 32.874] |
| experiment/S/rr | 42.662 | [40.316, 44.893] |
| experiment/S/auroc | 68.855 | [66.597, 71.185] |
| experiment/U/rej_f1 | 56.579 | [49.264, 63.045] |
| experiment/U/gmiou1 | 39.365 | [32.764, 45.734] |
| experiment/U/rr | 95.067 | [91.111, 98.298] |
| experiment/U/auroc | 47.756 | [39.158, 56.514] |
| experiment/overall/rej_f1 | 47.131 | [44.840, 49.334] |
| experiment/overall/gmiou1 | 32.009 | [30.768, 33.189] |
| experiment/overall/rr | 45.196 | [42.839, 47.431] |
| experiment/S+/frr | 35.942 | [33.629, 38.150] |
| experiment/U+/frr | 96.183 | [92.623, 99.206] |
| experiment/U-/false_acceptance | 6.522 | [1.075, 14.286] |
| experiment/gap/auroc | 21.099 | [11.967, 30.518] |
| experiment/gap/rej_f1 | -10.425 | [-17.340, -2.707] |
| experiment/gap/gmiou1 | -7.730 | [-14.277, -0.765] |
| candidates/S+/coverage | 75.045 | [73.164, 76.827] |
| candidates/S+/gt_recall | 75.045 | [73.164, 76.827] |
| candidates/S+/top1_hit | 34.919 | [32.999, 36.919] |
| candidates/S+/high_count | 2.282 | [2.251, 2.313] |
| candidates/S+/relative_count | 2.338 | [2.308, 2.369] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.206 | [2.146, 2.268] |
| candidates/S-/relative_count | 2.302 | [2.241, 2.359] |
| candidates/U+/coverage | 76.336 | [67.164, 84.349] |
| candidates/U+/gt_recall | 76.336 | [67.164, 84.349] |
| candidates/U+/top1_hit | 29.008 | [20.000, 38.931] |
| candidates/U+/high_count | 2.183 | [2.050, 2.322] |
| candidates/U+/relative_count | 2.252 | [2.113, 2.388] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.304 | [2.155, 2.458] |
| candidates/U-/relative_count | 2.413 | [2.253, 2.575] |
| comparison/seen_change/auroc | 1.258 | [-0.220, 2.821] |
| comparison/unseen_net_gain/auroc | -1.506 | [-7.614, 4.347] |
| comparison/gap_reduction/auroc | -2.764 | [-8.949, 3.124] |
| comparison/seen_change/rej_f1 | 1.083 | [-0.970, 3.202] |
| comparison/unseen_net_gain/rej_f1 | 0.473 | [-2.185, 3.067] |
| comparison/gap_reduction/rej_f1 | -0.610 | [-3.868, 2.813] |
| comparison/seen_change/gmiou1 | -0.608 | [-1.715, 0.507] |
| comparison/unseen_net_gain/gmiou1 | -0.030 | [-2.786, 2.677] |
| comparison/gap_reduction/gmiou1 | 0.579 | [-2.329, 3.601] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
