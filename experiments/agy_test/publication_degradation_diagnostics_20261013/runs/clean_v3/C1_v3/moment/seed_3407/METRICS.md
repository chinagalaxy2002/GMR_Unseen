# Frozen final evaluation

Counts: {'S+': 3311, 'S-': 894, 'U+': 142, 'U-': 264}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 42.700 | [40.167, 45.030] |
| baseline/S/gmiou1 | 32.580 | [31.311, 33.851] |
| baseline/S/rr | 37.218 | [35.059, 39.223] |
| baseline/S/auroc | 68.146 | [66.337, 69.867] |
| baseline/U/rej_f1 | 0.749 | [0.000, 2.490] |
| baseline/U/gmiou1 | 15.333 | [12.813, 17.976] |
| baseline/U/rr | 0.739 | [0.000, 2.083] |
| baseline/U/auroc | 51.175 | [46.930, 55.316] |
| baseline/overall/rej_f1 | 38.591 | [35.978, 41.034] |
| baseline/overall/gmiou1 | 31.061 | [29.837, 32.254] |
| baseline/overall/rr | 34.006 | [32.009, 36.022] |
| baseline/S+/frr | 31.410 | [29.413, 33.293] |
| baseline/U+/frr | 1.408 | [0.000, 3.659] |
| baseline/U-/false_acceptance | 99.621 | [98.718, 100.000] |
| baseline/gap/auroc | 16.971 | [12.482, 21.467] |
| baseline/gap/rej_f1 | 41.951 | [39.099, 44.648] |
| baseline/gap/gmiou1 | 17.247 | [14.375, 19.986] |
| experiment/S/rej_f1 | 42.700 | [40.167, 45.030] |
| experiment/S/gmiou1 | 32.580 | [31.311, 33.851] |
| experiment/S/rr | 37.218 | [35.059, 39.223] |
| experiment/S/auroc | 68.146 | [66.337, 69.867] |
| experiment/U/rej_f1 | 0.749 | [0.000, 2.490] |
| experiment/U/gmiou1 | 15.333 | [12.813, 17.976] |
| experiment/U/rr | 0.739 | [0.000, 2.083] |
| experiment/U/auroc | 51.175 | [46.930, 55.316] |
| experiment/overall/rej_f1 | 38.591 | [35.978, 41.034] |
| experiment/overall/gmiou1 | 31.061 | [29.837, 32.254] |
| experiment/overall/rr | 34.006 | [32.009, 36.022] |
| experiment/S+/frr | 31.410 | [29.413, 33.293] |
| experiment/U+/frr | 1.408 | [0.000, 3.659] |
| experiment/U-/false_acceptance | 99.621 | [98.718, 100.000] |
| experiment/gap/auroc | 16.971 | [12.482, 21.467] |
| experiment/gap/rej_f1 | 41.951 | [39.099, 44.648] |
| experiment/gap/gmiou1 | 17.247 | [14.375, 19.986] |
| candidates/S+/coverage | 70.855 | [68.925, 72.670] |
| candidates/S+/gt_recall | 70.855 | [68.925, 72.670] |
| candidates/S+/top1_hit | 36.303 | [34.301, 38.132] |
| candidates/S+/high_count | 2.706 | [2.685, 2.726] |
| candidates/S+/relative_count | 2.724 | [2.704, 2.744] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.701 | [2.660, 2.741] |
| candidates/S-/relative_count | 2.720 | [2.682, 2.757] |
| candidates/U+/coverage | 77.465 | [68.840, 85.402] |
| candidates/U+/gt_recall | 77.465 | [68.840, 85.402] |
| candidates/U+/top1_hit | 49.296 | [39.454, 59.158] |
| candidates/U+/high_count | 2.493 | [2.356, 2.633] |
| candidates/U+/relative_count | 2.528 | [2.396, 2.659] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.564 | [2.394, 2.722] |
| candidates/U-/relative_count | 2.576 | [2.405, 2.731] |
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
