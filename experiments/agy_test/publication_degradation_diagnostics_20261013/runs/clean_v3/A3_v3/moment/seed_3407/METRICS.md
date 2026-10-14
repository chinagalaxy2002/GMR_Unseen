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
| experiment/S/rej_f1 | 54.394 | [52.006, 56.683] |
| experiment/S/gmiou1 | 34.764 | [33.419, 36.139] |
| experiment/S/rr | 40.644 | [38.128, 43.021] |
| experiment/S/auroc | 75.707 | [73.655, 77.724] |
| experiment/U/rej_f1 | 14.865 | [6.298, 23.944] |
| experiment/U/gmiou1 | 28.306 | [24.464, 32.040] |
| experiment/U/rr | 7.283 | [4.087, 11.143] |
| experiment/U/auroc | 45.598 | [39.663, 51.650] |
| experiment/overall/rej_f1 | 52.386 | [49.929, 54.697] |
| experiment/overall/gmiou1 | 34.264 | [32.981, 35.576] |
| experiment/overall/rr | 38.061 | [35.719, 40.386] |
| experiment/S+/frr | 30.360 | [28.238, 32.285] |
| experiment/U+/frr | 6.383 | [3.139, 10.214] |
| experiment/U-/false_acceptance | 90.984 | [84.721, 96.396] |
| experiment/gap/auroc | 30.109 | [23.780, 36.394] |
| experiment/gap/rej_f1 | 39.529 | [30.484, 48.279] |
| experiment/gap/gmiou1 | 6.459 | [2.566, 10.522] |
| candidates/S+/coverage | 71.659 | [69.597, 73.601] |
| candidates/S+/gt_recall | 71.659 | [69.597, 73.601] |
| candidates/S+/top1_hit | 35.519 | [33.438, 37.449] |
| candidates/S+/high_count | 2.572 | [2.544, 2.601] |
| candidates/S+/relative_count | 2.599 | [2.570, 2.626] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.305 | [2.211, 2.401] |
| candidates/S-/relative_count | 2.513 | [2.443, 2.584] |
| candidates/U+/coverage | 73.617 | [65.815, 80.785] |
| candidates/U+/gt_recall | 73.617 | [65.815, 80.785] |
| candidates/U+/top1_hit | 44.255 | [36.443, 51.837] |
| candidates/U+/high_count | 2.191 | [2.053, 2.328] |
| candidates/U+/relative_count | 2.204 | [2.064, 2.346] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.041 | [1.864, 2.223] |
| candidates/U-/relative_count | 2.057 | [1.876, 2.238] |
| comparison/seen_change/auroc | 0.000 | [0.000, 0.000] |
| comparison/unseen_net_gain/auroc | 0.000 | [0.000, 0.000] |
| comparison/gap_reduction/auroc | -0.000 | [-0.000, 0.000] |
| comparison/seen_change/rej_f1 | 0.000 | [0.000, 0.000] |
| comparison/unseen_net_gain/rej_f1 | 0.000 | [0.000, 0.000] |
| comparison/gap_reduction/rej_f1 | -0.000 | [-0.000, 0.000] |
| comparison/seen_change/gmiou1 | 0.000 | [0.000, 0.000] |
| comparison/unseen_net_gain/gmiou1 | 0.000 | [0.000, 0.000] |
| comparison/gap_reduction/gmiou1 | -0.000 | [-0.000, 0.000] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
