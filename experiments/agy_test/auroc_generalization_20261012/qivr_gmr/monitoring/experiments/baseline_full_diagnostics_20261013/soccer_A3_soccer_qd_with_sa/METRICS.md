# Frozen final evaluation

Counts: {'S+': 808, 'S-': 1151, 'U+': 128, 'U-': 146}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 75.914 | [73.781, 77.753] |
| baseline/S/gmiou1 | 50.037 | [47.061, 52.768] |
| baseline/S/rr | 71.159 | [68.132, 74.065] |
| baseline/S/auroc | 71.062 | [69.159, 72.801] |
| baseline/U/rej_f1 | 75.332 | [70.951, 79.524] |
| baseline/U/gmiou1 | 52.608 | [46.870, 58.609] |
| baseline/U/rr | 84.307 | [80.555, 87.866] |
| baseline/U/auroc | 64.836 | [59.216, 70.496] |
| baseline/overall/rej_f1 | 75.838 | [73.911, 77.507] |
| baseline/overall/gmiou1 | 50.353 | [47.660, 52.793] |
| baseline/overall/rr | 72.772 | [69.947, 75.422] |
| baseline/S+/frr | 52.970 | [49.644, 56.207] |
| baseline/U+/frr | 69.531 | [64.583, 75.000] |
| baseline/U-/false_acceptance | 2.740 | [0.633, 5.556] |
| baseline/gap/auroc | 6.226 | [0.059, 12.638] |
| baseline/gap/rej_f1 | 0.582 | [-4.145, 5.341] |
| baseline/gap/gmiou1 | -2.571 | [-9.096, 3.716] |
| experiment/S/rej_f1 | 76.675 | [74.732, 78.348] |
| experiment/S/gmiou1 | 50.715 | [47.863, 53.373] |
| experiment/S/rr | 70.801 | [67.397, 73.857] |
| experiment/S/auroc | 72.599 | [70.685, 74.442] |
| experiment/U/rej_f1 | 73.278 | [68.665, 77.528] |
| experiment/U/gmiou1 | 49.077 | [43.302, 55.087] |
| experiment/U/rr | 79.197 | [74.602, 83.577] |
| experiment/U/auroc | 65.218 | [59.347, 70.786] |
| experiment/overall/rej_f1 | 76.250 | [74.393, 77.841] |
| experiment/overall/gmiou1 | 50.514 | [47.817, 53.049] |
| experiment/overall/rr | 71.832 | [68.549, 74.751] |
| experiment/S+/frr | 51.238 | [47.473, 54.935] |
| experiment/U+/frr | 65.625 | [59.722, 72.358] |
| experiment/U-/false_acceptance | 8.904 | [4.379, 14.396] |
| experiment/gap/auroc | 7.381 | [1.489, 13.735] |
| experiment/gap/rej_f1 | 3.396 | [-1.396, 8.300] |
| experiment/gap/gmiou1 | 1.638 | [-4.832, 7.804] |
| candidates/S+/coverage | 50.743 | [47.343, 54.001] |
| candidates/S+/gt_recall | 33.824 | [31.179, 36.520] |
| candidates/S+/top1_hit | 6.559 | [4.804, 8.486] |
| candidates/S+/high_count | 3.597 | [3.361, 3.834] |
| candidates/S+/relative_count | 9.806 | [9.728, 9.874] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 0.448 | [0.349, 0.565] |
| candidates/S-/relative_count | 9.860 | [9.803, 9.907] |
| candidates/U+/coverage | 48.438 | [39.552, 56.924] |
| candidates/U+/gt_recall | 35.938 | [28.774, 43.177] |
| candidates/U+/top1_hit | 6.250 | [2.272, 11.268] |
| candidates/U+/high_count | 3.000 | [2.447, 3.489] |
| candidates/U+/relative_count | 9.930 | [9.818, 10.000] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 0.281 | [0.122, 0.467] |
| candidates/U-/relative_count | 9.945 | [9.868, 10.000] |
| comparison/seen_change/auroc | 1.537 | [0.344, 2.767] |
| comparison/unseen_net_gain/auroc | 0.383 | [-3.079, 3.860] |
| comparison/gap_reduction/auroc | -1.154 | [-5.103, 2.570] |
| comparison/seen_change/rej_f1 | 0.761 | [-0.543, 2.072] |
| comparison/unseen_net_gain/rej_f1 | -2.053 | [-4.687, 0.119] |
| comparison/gap_reduction/rej_f1 | -2.814 | [-5.854, -0.323] |
| comparison/seen_change/gmiou1 | 0.678 | [-0.750, 2.030] |
| comparison/unseen_net_gain/gmiou1 | -3.531 | [-6.339, -1.225] |
| comparison/gap_reduction/gmiou1 | -4.209 | [-7.367, -1.521] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
