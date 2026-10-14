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
| experiment/S/rej_f1 | 54.646 | [52.081, 56.994] |
| experiment/S/gmiou1 | 33.924 | [32.417, 35.347] |
| experiment/S/rr | 39.657 | [37.085, 41.994] |
| experiment/S/auroc | 76.566 | [74.560, 78.378] |
| experiment/U/rej_f1 | 25.000 | [15.686, 33.920] |
| experiment/U/gmiou1 | 28.212 | [24.156, 32.082] |
| experiment/U/rr | 15.126 | [10.366, 20.245] |
| experiment/U/auroc | 51.927 | [46.644, 57.539] |
| experiment/overall/rej_f1 | 52.846 | [50.309, 55.152] |
| experiment/overall/gmiou1 | 33.482 | [32.068, 34.815] |
| experiment/overall/rr | 37.758 | [35.397, 40.072] |
| experiment/S+/frr | 29.304 | [27.171, 31.287] |
| experiment/U+/frr | 13.617 | [8.823, 19.070] |
| experiment/U-/false_acceptance | 81.967 | [74.037, 89.287] |
| experiment/gap/auroc | 24.639 | [18.736, 30.446] |
| experiment/gap/rej_f1 | 29.646 | [20.570, 39.006] |
| experiment/gap/gmiou1 | 5.712 | [1.602, 9.866] |
| candidates/S+/coverage | 82.846 | [81.282, 84.411] |
| candidates/S+/gt_recall | 82.846 | [81.282, 84.411] |
| candidates/S+/top1_hit | 33.250 | [31.393, 35.274] |
| candidates/S+/high_count | 2.757 | [2.724, 2.791] |
| candidates/S+/relative_count | 2.852 | [2.820, 2.885] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.408 | [2.301, 2.517] |
| candidates/S-/relative_count | 3.115 | [3.002, 3.236] |
| candidates/U+/coverage | 88.511 | [83.682, 92.920] |
| candidates/U+/gt_recall | 88.511 | [83.682, 92.920] |
| candidates/U+/top1_hit | 41.277 | [33.763, 48.624] |
| candidates/U+/high_count | 2.545 | [2.448, 2.636] |
| candidates/U+/relative_count | 2.613 | [2.517, 2.710] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.557 | [2.419, 2.696] |
| candidates/U-/relative_count | 2.623 | [2.468, 2.777] |
| comparison/seen_change/auroc | -0.280 | [-0.985, 0.367] |
| comparison/unseen_net_gain/auroc | 1.641 | [-1.185, 4.530] |
| comparison/gap_reduction/auroc | 1.921 | [-0.820, 4.971] |
| comparison/seen_change/rej_f1 | 0.558 | [-0.468, 1.595] |
| comparison/unseen_net_gain/rej_f1 | 1.650 | [-5.336, 8.697] |
| comparison/gap_reduction/rej_f1 | 1.091 | [-5.858, 8.274] |
| comparison/seen_change/gmiou1 | -0.453 | [-1.340, 0.378] |
| comparison/unseen_net_gain/gmiou1 | 2.637 | [-0.623, 5.924] |
| comparison/gap_reduction/gmiou1 | 3.090 | [-0.306, 6.523] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
