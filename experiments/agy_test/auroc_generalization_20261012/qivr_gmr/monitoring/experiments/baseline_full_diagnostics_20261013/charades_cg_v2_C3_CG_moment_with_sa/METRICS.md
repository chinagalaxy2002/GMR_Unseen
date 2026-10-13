# Frozen final evaluation

Counts: {'S+': 2684, 'S-': 2684, 'U+': 2990, 'U-': 2990}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 63.869 | [62.266, 65.578] |
| baseline/S/gmiou1 | 45.950 | [44.480, 47.489] |
| baseline/S/rr | 64.512 | [62.966, 66.054] |
| baseline/S/auroc | 63.376 | [61.696, 65.090] |
| baseline/U/rej_f1 | 60.100 | [58.577, 61.650] |
| baseline/U/gmiou1 | 41.487 | [40.147, 42.845] |
| baseline/U/rr | 67.642 | [66.017, 69.147] |
| baseline/U/auroc | 55.867 | [54.230, 57.488] |
| baseline/overall/rej_f1 | 61.857 | [60.596, 63.084] |
| baseline/overall/gmiou1 | 43.598 | [42.499, 44.736] |
| baseline/overall/rr | 66.161 | [64.789, 67.367] |
| baseline/S+/frr | 55.887 | [53.589, 58.200] |
| baseline/U+/frr | 64.582 | [62.399, 66.490] |
| baseline/U-/false_acceptance | 29.298 | [27.249, 31.404] |
| baseline/gap/auroc | 7.509 | [5.408, 9.624] |
| baseline/gap/rej_f1 | 3.769 | [1.886, 5.783] |
| baseline/gap/gmiou1 | 4.463 | [2.751, 6.275] |
| experiment/S/rej_f1 | 66.759 | [65.065, 68.449] |
| experiment/S/gmiou1 | 45.879 | [44.558, 47.316] |
| experiment/S/rr | 44.374 | [42.823, 45.941] |
| experiment/S/auroc | 75.123 | [73.611, 76.669] |
| experiment/U/rej_f1 | 59.258 | [57.533, 61.130] |
| experiment/U/gmiou1 | 38.184 | [36.972, 39.476] |
| experiment/U/rr | 40.585 | [39.077, 42.007] |
| experiment/U/auroc | 68.460 | [66.984, 70.111] |
| experiment/overall/rej_f1 | 62.883 | [61.556, 64.238] |
| experiment/overall/gmiou1 | 41.824 | [40.871, 42.830] |
| experiment/overall/rr | 42.378 | [41.215, 43.444] |
| experiment/S+/frr | 25.745 | [23.819, 27.620] |
| experiment/U+/frr | 27.492 | [25.548, 29.385] |
| experiment/U-/false_acceptance | 46.321 | [44.210, 48.390] |
| experiment/gap/auroc | 6.662 | [4.526, 8.714] |
| experiment/gap/rej_f1 | 7.501 | [5.265, 9.657] |
| experiment/gap/gmiou1 | 7.694 | [5.976, 9.399] |
| candidates/S+/coverage | 76.416 | [74.550, 78.235] |
| candidates/S+/gt_recall | 76.416 | [74.550, 78.235] |
| candidates/S+/top1_hit | 39.456 | [37.380, 41.566] |
| candidates/S+/high_count | 1.039 | [1.008, 1.072] |
| candidates/S+/relative_count | 1.659 | [1.582, 1.738] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 0.553 | [0.521, 0.586] |
| candidates/S-/relative_count | 3.041 | [2.907, 3.181] |
| candidates/U+/coverage | 70.268 | [68.366, 72.222] |
| candidates/U+/gt_recall | 70.268 | [68.366, 72.222] |
| candidates/U+/top1_hit | 29.431 | [27.602, 31.363] |
| candidates/U+/high_count | 1.081 | [1.049, 1.112] |
| candidates/U+/relative_count | 1.708 | [1.645, 1.774] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 0.721 | [0.687, 0.753] |
| candidates/U-/relative_count | 2.532 | [2.423, 2.643] |
| comparison/seen_change/auroc | 11.746 | [9.950, 13.568] |
| comparison/unseen_net_gain/auroc | 12.593 | [10.579, 14.583] |
| comparison/gap_reduction/auroc | 0.847 | [-1.582, 3.421] |
| comparison/seen_change/rej_f1 | 2.890 | [1.132, 4.722] |
| comparison/unseen_net_gain/rej_f1 | -0.842 | [-2.809, 1.151] |
| comparison/gap_reduction/rej_f1 | -3.732 | [-6.205, -1.265] |
| comparison/seen_change/gmiou1 | -0.071 | [-1.527, 1.422] |
| comparison/unseen_net_gain/gmiou1 | -3.303 | [-4.801, -1.793] |
| comparison/gap_reduction/gmiou1 | -3.232 | [-5.130, -1.288] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
