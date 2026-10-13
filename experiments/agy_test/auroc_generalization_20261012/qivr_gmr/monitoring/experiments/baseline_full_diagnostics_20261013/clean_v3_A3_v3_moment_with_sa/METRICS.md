# Frozen final evaluation

Counts: {'S+': 3218, 'S-': 1036, 'U+': 235, 'U-': 122}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 54.394 | [52.006, 56.683] |
| baseline/S/gmiou1 | 34.764 | [33.419, 36.139] |
| baseline/S/rr | 40.644 | [38.128, 43.021] |
| baseline/S/auroc | 75.707 | [73.655, 77.724] |
| baseline/U/rej_f1 | 14.865 | [6.298, 23.944] |
| baseline/U/gmiou1 | 28.306 | [24.464, 32.040] |
| baseline/U/rr | 7.283 | [4.087, 11.143] |
| baseline/U/auroc | 45.598 | [39.663, 51.650] |
| baseline/overall/rej_f1 | 52.386 | [49.929, 54.697] |
| baseline/overall/gmiou1 | 34.264 | [32.981, 35.576] |
| baseline/overall/rr | 38.061 | [35.719, 40.386] |
| baseline/S+/frr | 30.360 | [28.238, 32.285] |
| baseline/U+/frr | 6.383 | [3.139, 10.214] |
| baseline/U-/false_acceptance | 90.984 | [84.721, 96.396] |
| baseline/gap/auroc | 30.109 | [23.780, 36.394] |
| baseline/gap/rej_f1 | 39.529 | [30.484, 48.279] |
| baseline/gap/gmiou1 | 6.459 | [2.566, 10.522] |
| experiment/S/rej_f1 | 55.506 | [52.472, 58.214] |
| experiment/S/gmiou1 | 35.079 | [33.520, 36.590] |
| experiment/S/rr | 33.498 | [31.201, 35.782] |
| experiment/S/auroc | 75.870 | [73.623, 77.949] |
| experiment/U/rej_f1 | 23.037 | [14.444, 31.639] |
| experiment/U/gmiou1 | 24.373 | [20.396, 28.340] |
| experiment/U/rr | 19.328 | [13.793, 24.932] |
| experiment/U/auroc | 46.191 | [40.531, 52.240] |
| experiment/overall/rej_f1 | 53.167 | [50.306, 55.870] |
| experiment/overall/gmiou1 | 34.250 | [32.783, 35.653] |
| experiment/overall/rr | 32.401 | [30.201, 34.565] |
| experiment/S+/frr | 23.058 | [21.121, 24.884] |
| experiment/U+/frr | 20.000 | [13.460, 26.613] |
| experiment/U-/false_acceptance | 81.967 | [73.950, 89.256] |
| experiment/gap/auroc | 29.678 | [23.414, 35.843] |
| experiment/gap/rej_f1 | 32.469 | [23.270, 41.732] |
| experiment/gap/gmiou1 | 10.706 | [6.482, 14.907] |
| candidates/S+/coverage | 72.685 | [70.729, 74.544] |
| candidates/S+/gt_recall | 72.685 | [70.729, 74.544] |
| candidates/S+/top1_hit | 34.618 | [32.581, 36.756] |
| candidates/S+/high_count | 1.306 | [1.280, 1.332] |
| candidates/S+/relative_count | 1.410 | [1.381, 1.441] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 0.892 | [0.827, 0.964] |
| candidates/S-/relative_count | 2.150 | [1.950, 2.365] |
| candidates/U+/coverage | 71.064 | [63.980, 77.487] |
| candidates/U+/gt_recall | 71.064 | [63.980, 77.487] |
| candidates/U+/top1_hit | 40.851 | [33.333, 47.728] |
| candidates/U+/high_count | 1.243 | [1.172, 1.319] |
| candidates/U+/relative_count | 1.272 | [1.206, 1.344] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 1.139 | [1.050, 1.235] |
| candidates/U-/relative_count | 1.328 | [1.153, 1.602] |
| comparison/seen_change/auroc | 0.162 | [-1.028, 1.312] |
| comparison/unseen_net_gain/auroc | 0.593 | [-4.045, 5.461] |
| comparison/gap_reduction/auroc | 0.431 | [-4.538, 5.467] |
| comparison/seen_change/rej_f1 | 1.112 | [-0.742, 2.757] |
| comparison/unseen_net_gain/rej_f1 | 8.172 | [0.112, 16.313] |
| comparison/gap_reduction/rej_f1 | 7.060 | [-1.034, 15.609] |
| comparison/seen_change/gmiou1 | 0.315 | [-0.907, 1.377] |
| comparison/unseen_net_gain/gmiou1 | -3.932 | [-8.313, 0.308] |
| comparison/gap_reduction/gmiou1 | -4.247 | [-8.718, 0.015] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
