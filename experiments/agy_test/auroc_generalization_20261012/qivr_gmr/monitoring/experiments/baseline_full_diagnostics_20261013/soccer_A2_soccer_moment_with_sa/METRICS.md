# Frozen final evaluation

Counts: {'S+': 829, 'S-': 1128, 'U+': 107, 'U-': 169}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 73.639 | [71.632, 75.456] |
| baseline/S/gmiou1 | 46.998 | [44.653, 49.174] |
| baseline/S/rr | 60.603 | [57.472, 63.391] |
| baseline/S/auroc | 76.763 | [74.933, 78.438] |
| baseline/U/rej_f1 | 69.565 | [63.998, 74.501] |
| baseline/U/gmiou1 | 47.724 | [41.569, 53.721] |
| baseline/U/rr | 72.101 | [67.112, 77.018] |
| baseline/U/auroc | 54.289 | [47.628, 60.711] |
| baseline/overall/rej_f1 | 73.080 | [71.098, 74.857] |
| baseline/overall/gmiou1 | 47.088 | [44.761, 49.250] |
| baseline/overall/rr | 62.024 | [59.023, 64.657] |
| baseline/S+/frr | 40.290 | [36.848, 43.671] |
| baseline/U+/frr | 66.355 | [59.166, 73.451] |
| baseline/U-/false_acceptance | 24.260 | [17.838, 31.056] |
| baseline/gap/auroc | 22.474 | [15.945, 29.451] |
| baseline/gap/rej_f1 | 4.074 | [-0.955, 9.609] |
| baseline/gap/gmiou1 | -0.726 | [-6.826, 5.176] |
| experiment/S/rej_f1 | 72.895 | [70.539, 74.910] |
| experiment/S/gmiou1 | 45.096 | [42.413, 47.581] |
| experiment/S/rr | 58.866 | [55.444, 62.008] |
| experiment/S/auroc | 76.283 | [74.505, 77.963] |
| experiment/U/rej_f1 | 76.440 | [71.618, 81.068] |
| experiment/U/gmiou1 | 53.178 | [46.694, 59.967] |
| experiment/U/rr | 77.174 | [71.875, 82.311] |
| experiment/U/auroc | 56.346 | [49.018, 63.004] |
| experiment/overall/rej_f1 | 73.403 | [71.168, 75.288] |
| experiment/overall/gmiou1 | 46.095 | [43.316, 48.550] |
| experiment/overall/rr | 61.129 | [57.742, 64.237] |
| experiment/S+/frr | 38.721 | [35.271, 42.358] |
| experiment/U+/frr | 62.617 | [54.783, 70.193] |
| experiment/U-/false_acceptance | 13.609 | [8.333, 19.513] |
| experiment/gap/auroc | 19.938 | [12.599, 27.523] |
| experiment/gap/rej_f1 | -3.545 | [-8.521, 1.519] |
| experiment/gap/gmiou1 | -8.082 | [-14.939, -1.520] |
| candidates/S+/coverage | 58.866 | [55.459, 62.543] |
| candidates/S+/gt_recall | 40.460 | [37.734, 43.428] |
| candidates/S+/top1_hit | 16.767 | [13.753, 19.663] |
| candidates/S+/high_count | 3.948 | [3.760, 4.136] |
| candidates/S+/relative_count | 5.861 | [5.691, 6.043] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 1.689 | [1.551, 1.835] |
| candidates/S-/relative_count | 5.209 | [5.005, 5.406] |
| candidates/U+/coverage | 46.729 | [36.272, 56.364] |
| candidates/U+/gt_recall | 34.969 | [26.967, 43.273] |
| candidates/U+/top1_hit | 5.607 | [0.826, 11.570] |
| candidates/U+/high_count | 2.551 | [2.086, 2.970] |
| candidates/U+/relative_count | 5.636 | [5.230, 6.051] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 1.059 | [0.827, 1.290] |
| candidates/U-/relative_count | 5.651 | [5.314, 5.967] |
| comparison/seen_change/auroc | -0.479 | [-1.530, 0.619] |
| comparison/unseen_net_gain/auroc | 2.057 | [-3.777, 7.686] |
| comparison/gap_reduction/auroc | 2.537 | [-3.509, 8.501] |
| comparison/seen_change/rej_f1 | -0.744 | [-2.285, 0.711] |
| comparison/unseen_net_gain/rej_f1 | 6.875 | [3.018, 11.147] |
| comparison/gap_reduction/rej_f1 | 7.619 | [3.471, 12.057] |
| comparison/seen_change/gmiou1 | -1.902 | [-3.392, -0.495] |
| comparison/unseen_net_gain/gmiou1 | 5.454 | [1.404, 9.803] |
| comparison/gap_reduction/gmiou1 | 7.356 | [3.018, 11.802] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
