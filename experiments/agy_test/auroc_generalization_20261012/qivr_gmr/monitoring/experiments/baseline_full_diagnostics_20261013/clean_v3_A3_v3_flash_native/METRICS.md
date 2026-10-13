# Frozen final evaluation

Counts: {'S+': 3218, 'S-': 1036, 'U+': 235, 'U-': 122}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 56.318 | [53.763, 58.793] |
| baseline/S/gmiou1 | 43.030 | [41.567, 44.537] |
| baseline/S/rr | 35.919 | [33.605, 38.115] |
| baseline/S/auroc | 77.204 | [75.086, 79.318] |
| baseline/U/rej_f1 | 26.042 | [17.142, 34.452] |
| baseline/U/gmiou1 | 31.221 | [27.346, 35.360] |
| baseline/U/rr | 19.608 | [14.203, 25.588] |
| baseline/U/auroc | 46.502 | [40.648, 52.247] |
| baseline/overall/rej_f1 | 54.209 | [51.690, 56.655] |
| baseline/overall/gmiou1 | 42.116 | [40.718, 43.566] |
| baseline/overall/rr | 34.656 | [32.399, 36.823] |
| baseline/S+/frr | 25.047 | [23.088, 26.977] |
| baseline/U+/frr | 19.149 | [13.471, 25.439] |
| baseline/U-/false_acceptance | 79.508 | [70.748, 87.235] |
| baseline/gap/auroc | 30.702 | [24.885, 36.731] |
| baseline/gap/rej_f1 | 30.277 | [21.195, 39.374] |
| baseline/gap/gmiou1 | 11.809 | [7.550, 16.011] |
| experiment/S/rej_f1 | 56.331 | [53.549, 58.931] |
| experiment/S/gmiou1 | 42.454 | [40.947, 43.881] |
| experiment/S/rr | 31.899 | [29.599, 34.124] |
| experiment/S/auroc | 77.750 | [75.712, 79.744] |
| experiment/U/rej_f1 | 12.500 | [4.255, 21.429] |
| experiment/U/gmiou1 | 31.026 | [27.397, 34.812] |
| experiment/U/rr | 6.162 | [3.132, 9.797] |
| experiment/U/auroc | 45.323 | [39.300, 51.379] |
| experiment/overall/rej_f1 | 53.843 | [51.153, 56.473] |
| experiment/overall/gmiou1 | 41.570 | [40.104, 42.935] |
| experiment/overall/rr | 29.907 | [27.698, 32.026] |
| experiment/S+/frr | 21.224 | [19.343, 23.054] |
| experiment/U+/frr | 5.532 | [2.631, 9.260] |
| experiment/U-/false_acceptance | 92.623 | [86.554, 97.674] |
| experiment/gap/auroc | 32.428 | [26.173, 38.659] |
| experiment/gap/rej_f1 | 43.831 | [34.635, 52.658] |
| experiment/gap/gmiou1 | 11.428 | [7.417, 15.402] |
| candidates/S+/coverage | 99.938 | [99.809, 100.000] |
| candidates/S+/gt_recall | 99.938 | [99.809, 100.000] |
| candidates/S+/top1_hit | 53.543 | [51.384, 55.562] |
| candidates/S+/high_count | 0.961 | [0.908, 1.011] |
| candidates/S+/relative_count | 8.347 | [8.123, 8.587] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 0.856 | [0.772, 0.941] |
| candidates/S-/relative_count | 8.630 | [8.191, 9.082] |
| candidates/U+/coverage | 100.000 | [100.000, 100.000] |
| candidates/U+/gt_recall | 100.000 | [100.000, 100.000] |
| candidates/U+/top1_hit | 46.809 | [39.166, 54.668] |
| candidates/U+/high_count | 0.885 | [0.733, 1.051] |
| candidates/U+/relative_count | 7.740 | [7.168, 8.361] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 1.008 | [0.808, 1.235] |
| candidates/U-/relative_count | 7.820 | [6.967, 8.797] |
| comparison/seen_change/auroc | 0.547 | [-0.124, 1.215] |
| comparison/unseen_net_gain/auroc | -1.179 | [-3.513, 1.123] |
| comparison/gap_reduction/auroc | -1.726 | [-4.134, 0.698] |
| comparison/seen_change/rej_f1 | 0.013 | [-1.341, 1.335] |
| comparison/unseen_net_gain/rej_f1 | -13.542 | [-20.480, -7.093] |
| comparison/gap_reduction/rej_f1 | -13.554 | [-20.589, -6.913] |
| comparison/seen_change/gmiou1 | -0.576 | [-1.498, 0.358] |
| comparison/unseen_net_gain/gmiou1 | -0.195 | [-3.546, 2.868] |
| comparison/gap_reduction/gmiou1 | 0.381 | [-3.011, 3.643] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
