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
| experiment/S/rej_f1 | 68.572 | [66.994, 70.144] |
| experiment/S/gmiou1 | 48.672 | [47.310, 50.090] |
| experiment/S/rr | 50.354 | [48.768, 52.030] |
| experiment/S/auroc | 74.930 | [73.441, 76.567] |
| experiment/U/rej_f1 | 63.225 | [61.670, 64.806] |
| experiment/U/gmiou1 | 42.133 | [40.898, 43.382] |
| experiment/U/rr | 52.040 | [50.526, 53.518] |
| experiment/U/auroc | 67.315 | [65.779, 68.867] |
| experiment/overall/rej_f1 | 65.732 | [64.539, 66.860] |
| experiment/overall/gmiou1 | 45.226 | [44.243, 46.224] |
| experiment/overall/rr | 51.243 | [50.026, 52.387] |
| experiment/S+/frr | 31.893 | [29.688, 34.046] |
| experiment/U+/frr | 39.565 | [37.397, 41.528] |
| experiment/U-/false_acceptance | 35.485 | [33.567, 37.467] |
| experiment/gap/auroc | 7.615 | [5.608, 9.637] |
| experiment/gap/rej_f1 | 5.347 | [3.304, 7.401] |
| experiment/gap/gmiou1 | 6.539 | [4.794, 8.245] |
| candidates/S+/coverage | 72.355 | [70.213, 74.411] |
| candidates/S+/gt_recall | 72.355 | [70.213, 74.411] |
| candidates/S+/top1_hit | 42.139 | [39.809, 44.347] |
| candidates/S+/high_count | 1.065 | [1.033, 1.099] |
| candidates/S+/relative_count | 1.620 | [1.560, 1.688] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 0.575 | [0.541, 0.606] |
| candidates/S-/relative_count | 2.838 | [2.716, 2.968] |
| candidates/U+/coverage | 65.652 | [63.543, 67.693] |
| candidates/U+/gt_recall | 65.652 | [63.543, 67.693] |
| candidates/U+/top1_hit | 32.241 | [30.323, 34.163] |
| candidates/U+/high_count | 1.069 | [1.037, 1.104] |
| candidates/U+/relative_count | 1.710 | [1.655, 1.773] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 0.704 | [0.671, 0.737] |
| candidates/U-/relative_count | 2.362 | [2.265, 2.458] |
| comparison/seen_change/auroc | 11.553 | [9.834, 13.425] |
| comparison/unseen_net_gain/auroc | 11.448 | [9.563, 13.264] |
| comparison/gap_reduction/auroc | -0.105 | [-2.541, 2.405] |
| comparison/seen_change/rej_f1 | 4.704 | [3.071, 6.456] |
| comparison/unseen_net_gain/rej_f1 | 3.126 | [1.389, 4.954] |
| comparison/gap_reduction/rej_f1 | -1.578 | [-3.792, 0.650] |
| comparison/seen_change/gmiou1 | 2.722 | [1.338, 4.191] |
| comparison/unseen_net_gain/gmiou1 | 0.646 | [-0.826, 2.069] |
| comparison/gap_reduction/gmiou1 | -2.076 | [-3.952, -0.236] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
