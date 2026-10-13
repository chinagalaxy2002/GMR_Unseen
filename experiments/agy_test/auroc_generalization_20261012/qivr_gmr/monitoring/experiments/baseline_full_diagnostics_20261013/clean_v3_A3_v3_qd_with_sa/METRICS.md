# Frozen final evaluation

Counts: {'S+': 3218, 'S-': 1036, 'U+': 235, 'U-': 122}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 54.087 | [51.524, 56.558] |
| baseline/S/gmiou1 | 34.377 | [32.832, 35.785] |
| baseline/S/rr | 40.926 | [38.554, 43.278] |
| baseline/S/auroc | 76.846 | [74.839, 78.810] |
| baseline/U/rej_f1 | 23.350 | [14.735, 31.887] |
| baseline/U/gmiou1 | 25.574 | [21.837, 29.088] |
| baseline/U/rr | 21.008 | [15.635, 26.791] |
| baseline/U/auroc | 50.286 | [44.746, 55.856] |
| baseline/overall/rej_f1 | 52.051 | [49.528, 54.534] |
| baseline/overall/gmiou1 | 33.695 | [32.271, 35.039] |
| baseline/overall/rr | 39.384 | [37.141, 41.718] |
| baseline/S+/frr | 30.764 | [28.593, 32.945] |
| baseline/U+/frr | 22.128 | [15.925, 28.761] |
| baseline/U-/false_acceptance | 81.148 | [72.725, 88.800] |
| baseline/gap/auroc | 26.560 | [20.612, 32.573] |
| baseline/gap/rej_f1 | 30.737 | [21.996, 39.898] |
| baseline/gap/gmiou1 | 8.803 | [4.907, 12.946] |
| experiment/S/rej_f1 | 55.004 | [52.536, 57.382] |
| experiment/S/gmiou1 | 35.446 | [34.088, 36.771] |
| experiment/S/rr | 40.009 | [37.526, 42.295] |
| experiment/S/auroc | 77.508 | [75.534, 79.291] |
| experiment/U/rej_f1 | 18.286 | [9.814, 27.273] |
| experiment/U/gmiou1 | 27.979 | [24.011, 31.650] |
| experiment/U/rr | 14.846 | [10.028, 20.681] |
| experiment/U/auroc | 46.828 | [41.243, 52.490] |
| experiment/overall/rej_f1 | 52.798 | [50.346, 55.164] |
| experiment/overall/gmiou1 | 34.868 | [33.564, 36.124] |
| experiment/overall/rr | 38.061 | [35.716, 40.339] |
| experiment/S+/frr | 29.490 | [27.354, 31.426] |
| experiment/U+/frr | 15.745 | [10.454, 22.020] |
| experiment/U-/false_acceptance | 86.885 | [79.167, 93.335] |
| experiment/gap/auroc | 30.681 | [24.689, 36.551] |
| experiment/gap/rej_f1 | 36.718 | [27.361, 45.415] |
| experiment/gap/gmiou1 | 7.467 | [3.607, 11.670] |
| candidates/S+/coverage | 66.283 | [64.248, 68.194] |
| candidates/S+/gt_recall | 66.283 | [64.248, 68.194] |
| candidates/S+/top1_hit | 34.587 | [32.644, 36.714] |
| candidates/S+/high_count | 2.508 | [2.477, 2.540] |
| candidates/S+/relative_count | 2.566 | [2.535, 2.599] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.117 | [2.007, 2.229] |
| candidates/S-/relative_count | 2.987 | [2.774, 3.213] |
| candidates/U+/coverage | 71.915 | [64.731, 78.441] |
| candidates/U+/gt_recall | 71.915 | [64.731, 78.441] |
| candidates/U+/top1_hit | 47.234 | [39.548, 54.752] |
| candidates/U+/high_count | 2.226 | [2.092, 2.350] |
| candidates/U+/relative_count | 2.247 | [2.114, 2.374] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 1.918 | [1.738, 2.091] |
| candidates/U-/relative_count | 1.975 | [1.806, 2.144] |
| comparison/seen_change/auroc | 0.662 | [-0.270, 1.581] |
| comparison/unseen_net_gain/auroc | -3.458 | [-7.933, 0.858] |
| comparison/gap_reduction/auroc | -4.121 | [-8.696, 0.295] |
| comparison/seen_change/rej_f1 | 0.917 | [-0.340, 2.078] |
| comparison/unseen_net_gain/rej_f1 | -5.065 | [-11.646, 1.150] |
| comparison/gap_reduction/rej_f1 | -5.981 | [-12.463, 0.226] |
| comparison/seen_change/gmiou1 | 1.069 | [0.027, 2.157] |
| comparison/unseen_net_gain/gmiou1 | 2.405 | [-1.164, 5.880] |
| comparison/gap_reduction/gmiou1 | 1.335 | [-2.309, 5.047] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
