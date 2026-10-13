# Frozen final evaluation

Counts: {'S+': 2684, 'S-': 2684, 'U+': 2990, 'U-': 2990}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 70.630 | [69.007, 72.240] |
| baseline/S/gmiou1 | 53.428 | [52.055, 54.816] |
| baseline/S/rr | 43.685 | [42.074, 45.305] |
| baseline/S/auroc | 79.970 | [78.534, 81.343] |
| baseline/U/rej_f1 | 64.236 | [62.507, 65.793] |
| baseline/U/gmiou1 | 44.960 | [43.663, 46.181] |
| baseline/U/rr | 44.030 | [42.573, 45.446] |
| baseline/U/auroc | 72.040 | [70.515, 73.480] |
| baseline/overall/rej_f1 | 67.255 | [66.023, 68.509] |
| baseline/overall/gmiou1 | 48.965 | [47.981, 49.974] |
| baseline/overall/rr | 43.867 | [42.717, 45.004] |
| baseline/S+/frr | 21.200 | [19.371, 22.979] |
| baseline/U+/frr | 27.659 | [25.768, 29.545] |
| baseline/U-/false_acceptance | 39.599 | [37.670, 41.641] |
| baseline/gap/auroc | 7.930 | [6.107, 9.885] |
| baseline/gap/rej_f1 | 6.394 | [4.285, 8.648] |
| baseline/gap/gmiou1 | 8.469 | [6.677, 10.229] |
| experiment/S/rej_f1 | 72.608 | [71.041, 74.111] |
| experiment/S/gmiou1 | 54.792 | [53.459, 56.128] |
| experiment/S/rr | 49.292 | [47.623, 50.965] |
| experiment/S/auroc | 79.522 | [78.065, 80.971] |
| experiment/U/rej_f1 | 65.898 | [64.334, 67.419] |
| experiment/U/gmiou1 | 46.384 | [45.106, 47.615] |
| experiment/U/rr | 50.033 | [48.627, 51.470] |
| experiment/U/auroc | 71.251 | [69.706, 72.719] |
| experiment/overall/rej_f1 | 69.059 | [67.870, 70.228] |
| experiment/overall/gmiou1 | 50.361 | [49.398, 51.351] |
| experiment/overall/rr | 49.683 | [48.505, 50.802] |
| experiment/S+/frr | 26.490 | [24.437, 28.609] |
| experiment/U+/frr | 34.147 | [32.240, 36.167] |
| experiment/U-/false_acceptance | 34.080 | [32.146, 36.063] |
| experiment/gap/auroc | 8.271 | [6.321, 10.148] |
| experiment/gap/rej_f1 | 6.710 | [4.589, 8.679] |
| experiment/gap/gmiou1 | 8.408 | [6.602, 10.091] |
| candidates/S+/coverage | 99.888 | [99.702, 100.000] |
| candidates/S+/gt_recall | 99.888 | [99.702, 100.000] |
| candidates/S+/top1_hit | 55.216 | [52.871, 57.395] |
| candidates/S+/high_count | 1.468 | [1.400, 1.535] |
| candidates/S+/relative_count | 3.722 | [3.645, 3.804] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 0.923 | [0.878, 0.969] |
| candidates/S-/relative_count | 4.147 | [4.044, 4.249] |
| candidates/U+/coverage | 99.866 | [99.695, 100.000] |
| candidates/U+/gt_recall | 99.866 | [99.695, 100.000] |
| candidates/U+/top1_hit | 42.809 | [40.787, 44.828] |
| candidates/U+/high_count | 1.089 | [1.039, 1.140] |
| candidates/U+/relative_count | 3.758 | [3.678, 3.838] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 0.805 | [0.762, 0.852] |
| candidates/U-/relative_count | 4.133 | [4.034, 4.234] |
| comparison/seen_change/auroc | -0.448 | [-1.414, 0.575] |
| comparison/unseen_net_gain/auroc | -0.789 | [-1.909, 0.377] |
| comparison/gap_reduction/auroc | -0.341 | [-1.709, 0.993] |
| comparison/seen_change/rej_f1 | 1.978 | [0.695, 3.233] |
| comparison/unseen_net_gain/rej_f1 | 1.662 | [0.291, 3.168] |
| comparison/gap_reduction/rej_f1 | -0.316 | [-2.079, 1.452] |
| comparison/seen_change/gmiou1 | 1.363 | [0.272, 2.431] |
| comparison/unseen_net_gain/gmiou1 | 1.424 | [0.342, 2.577] |
| comparison/gap_reduction/gmiou1 | 0.061 | [-1.426, 1.547] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
