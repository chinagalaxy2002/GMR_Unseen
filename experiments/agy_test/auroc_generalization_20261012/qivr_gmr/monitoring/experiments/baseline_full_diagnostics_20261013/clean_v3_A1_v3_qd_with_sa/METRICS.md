# Frozen final evaluation

Counts: {'S+': 2857, 'S-': 983, 'U+': 596, 'U-': 175}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 55.515 | [51.730, 59.054] |
| baseline/S/gmiou1 | 39.433 | [37.853, 41.098] |
| baseline/S/rr | 24.219 | [22.319, 26.180] |
| baseline/S/auroc | 72.951 | [70.266, 75.564] |
| baseline/U/rej_f1 | 28.923 | [22.286, 35.594] |
| baseline/U/gmiou1 | 22.806 | [20.496, 25.246] |
| baseline/U/rr | 19.455 | [16.085, 23.183] |
| baseline/U/auroc | 55.862 | [51.043, 60.748] |
| baseline/overall/rej_f1 | 51.653 | [48.154, 54.914] |
| baseline/overall/gmiou1 | 36.653 | [35.197, 38.103] |
| baseline/overall/rr | 23.422 | [21.749, 25.208] |
| baseline/S+/frr | 13.966 | [12.384, 15.633] |
| baseline/U+/frr | 17.282 | [13.764, 21.053] |
| baseline/U-/false_acceptance | 73.143 | [65.475, 80.226] |
| baseline/gap/auroc | 17.089 | [11.661, 22.491] |
| baseline/gap/rej_f1 | 26.592 | [19.158, 34.224] |
| baseline/gap/gmiou1 | 16.627 | [13.780, 19.505] |
| experiment/S/rej_f1 | 55.311 | [52.922, 57.668] |
| experiment/S/gmiou1 | 36.931 | [35.440, 38.447] |
| experiment/S/rr | 44.271 | [41.711, 46.716] |
| experiment/S/auroc | 77.067 | [75.114, 78.995] |
| experiment/U/rej_f1 | 39.709 | [33.673, 45.690] |
| experiment/U/gmiou1 | 25.271 | [22.651, 27.924] |
| experiment/U/rr | 30.869 | [26.640, 34.691] |
| experiment/U/auroc | 64.451 | [59.668, 69.170] |
| experiment/overall/rej_f1 | 53.230 | [50.954, 55.552] |
| experiment/overall/gmiou1 | 34.982 | [33.667, 36.332] |
| experiment/overall/rr | 42.030 | [39.631, 44.236] |
| experiment/S+/frr | 33.532 | [31.167, 35.756] |
| experiment/U+/frr | 26.174 | [21.931, 30.259] |
| experiment/U-/false_acceptance | 53.143 | [44.311, 61.668] |
| experiment/gap/auroc | 12.616 | [7.493, 17.834] |
| experiment/gap/rej_f1 | 15.602 | [9.327, 22.439] |
| experiment/gap/gmiou1 | 11.660 | [8.466, 14.657] |
| candidates/S+/coverage | 70.879 | [68.730, 72.964] |
| candidates/S+/gt_recall | 70.879 | [68.730, 72.964] |
| candidates/S+/top1_hit | 37.557 | [35.489, 39.620] |
| candidates/S+/high_count | 2.472 | [2.438, 2.507] |
| candidates/S+/relative_count | 2.515 | [2.481, 2.549] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.136 | [2.036, 2.239] |
| candidates/S-/relative_count | 2.434 | [2.362, 2.505] |
| candidates/U+/coverage | 59.732 | [55.245, 64.014] |
| candidates/U+/gt_recall | 59.732 | [55.245, 64.014] |
| candidates/U+/top1_hit | 22.148 | [18.531, 25.791] |
| candidates/U+/high_count | 2.678 | [2.612, 2.738] |
| candidates/U+/relative_count | 2.706 | [2.642, 2.765] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.691 | [2.576, 2.798] |
| candidates/U-/relative_count | 2.766 | [2.662, 2.859] |
| comparison/seen_change/auroc | 4.116 | [1.956, 6.285] |
| comparison/unseen_net_gain/auroc | 8.588 | [3.698, 13.505] |
| comparison/gap_reduction/auroc | 4.472 | [-0.948, 9.743] |
| comparison/seen_change/rej_f1 | -0.204 | [-3.140, 2.804] |
| comparison/unseen_net_gain/rej_f1 | 10.786 | [3.941, 17.947] |
| comparison/gap_reduction/rej_f1 | 10.990 | [3.436, 18.542] |
| comparison/seen_change/gmiou1 | -2.502 | [-4.129, -0.920] |
| comparison/unseen_net_gain/gmiou1 | 2.465 | [-0.575, 5.488] |
| comparison/gap_reduction/gmiou1 | 4.966 | [1.649, 8.255] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
