# Frozen final evaluation

Counts: {'S+': 808, 'S-': 1151, 'U+': 128, 'U-': 146}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 77.827 | [75.893, 79.503] |
| baseline/S/gmiou1 | 52.957 | [50.343, 55.424] |
| baseline/S/rr | 69.015 | [66.036, 71.719] |
| baseline/S/auroc | 77.333 | [75.394, 79.217] |
| baseline/U/rej_f1 | 74.194 | [69.780, 78.167] |
| baseline/U/gmiou1 | 50.839 | [44.894, 56.763] |
| baseline/U/rr | 82.482 | [78.125, 86.562] |
| baseline/U/auroc | 62.139 | [56.096, 68.089] |
| baseline/overall/rej_f1 | 77.357 | [75.641, 78.888] |
| baseline/overall/gmiou1 | 52.697 | [50.362, 54.869] |
| baseline/overall/rr | 70.667 | [67.897, 73.216] |
| baseline/S+/frr | 46.782 | [43.233, 50.381] |
| baseline/U+/frr | 68.750 | [62.914, 74.809] |
| baseline/U-/false_acceptance | 5.479 | [2.112, 9.524] |
| baseline/gap/auroc | 15.195 | [8.738, 21.968] |
| baseline/gap/rej_f1 | 3.633 | [-0.938, 8.519] |
| baseline/gap/gmiou1 | 2.118 | [-4.424, 8.487] |
| experiment/S/rej_f1 | 76.404 | [74.245, 78.414] |
| experiment/S/gmiou1 | 50.292 | [47.571, 52.937] |
| experiment/S/rr | 63.910 | [60.653, 67.004] |
| experiment/S/auroc | 77.794 | [75.860, 79.614] |
| experiment/U/rej_f1 | 75.200 | [70.917, 79.082] |
| experiment/U/gmiou1 | 51.891 | [46.226, 57.917] |
| experiment/U/rr | 83.577 | [79.756, 87.347] |
| experiment/U/auroc | 62.604 | [56.952, 68.092] |
| experiment/overall/rej_f1 | 76.242 | [74.292, 78.011] |
| experiment/overall/gmiou1 | 50.488 | [47.985, 52.871] |
| experiment/overall/rr | 66.323 | [63.299, 69.110] |
| experiment/S+/frr | 41.337 | [37.802, 44.658] |
| experiment/U+/frr | 68.750 | [63.910, 74.168] |
| experiment/U-/false_acceptance | 3.425 | [0.730, 6.716] |
| experiment/gap/auroc | 15.190 | [9.278, 21.243] |
| experiment/gap/rej_f1 | 1.204 | [-3.380, 5.943] |
| experiment/gap/gmiou1 | -1.599 | [-8.429, 4.843] |
| candidates/S+/coverage | 66.337 | [62.401, 70.203] |
| candidates/S+/gt_recall | 50.080 | [46.657, 53.448] |
| candidates/S+/top1_hit | 24.257 | [21.085, 27.843] |
| candidates/S+/high_count | 3.636 | [3.454, 3.811] |
| candidates/S+/relative_count | 4.421 | [4.250, 4.590] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 1.834 | [1.703, 1.984] |
| candidates/S-/relative_count | 3.726 | [3.585, 3.869] |
| candidates/U+/coverage | 46.094 | [36.789, 55.714] |
| candidates/U+/gt_recall | 30.990 | [23.980, 38.206] |
| candidates/U+/top1_hit | 5.469 | [1.833, 9.434] |
| candidates/U+/high_count | 1.914 | [1.602, 2.190] |
| candidates/U+/relative_count | 4.031 | [3.654, 4.377] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 0.685 | [0.493, 0.882] |
| candidates/U-/relative_count | 3.055 | [2.780, 3.333] |
| comparison/seen_change/auroc | 0.461 | [-0.862, 1.643] |
| comparison/unseen_net_gain/auroc | 0.466 | [-5.421, 6.446] |
| comparison/gap_reduction/auroc | 0.005 | [-6.254, 6.194] |
| comparison/seen_change/rej_f1 | -1.422 | [-2.930, 0.015] |
| comparison/unseen_net_gain/rej_f1 | 1.006 | [-0.707, 3.012] |
| comparison/gap_reduction/rej_f1 | 2.429 | [0.282, 4.848] |
| comparison/seen_change/gmiou1 | -2.665 | [-4.203, -1.056] |
| comparison/unseen_net_gain/gmiou1 | 1.052 | [-0.733, 3.192] |
| comparison/gap_reduction/gmiou1 | 3.717 | [1.523, 6.122] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
