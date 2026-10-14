# Frozen final evaluation

Counts: {'S+': 2857, 'S-': 983, 'U+': 596, 'U-': 175}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 56.375 | [53.699, 58.929] |
| baseline/S/gmiou1 | 37.786 | [36.225, 39.279] |
| baseline/S/rr | 35.469 | [32.955, 37.895] |
| baseline/S/auroc | 74.990 | [72.927, 76.992] |
| baseline/U/rej_f1 | 37.356 | [30.405, 43.990] |
| baseline/U/gmiou1 | 23.763 | [21.107, 26.228] |
| baseline/U/rr | 22.438 | [18.742, 26.115] |
| baseline/U/auroc | 64.392 | [59.315, 69.032] |
| baseline/overall/rej_f1 | 53.918 | [51.352, 56.442] |
| baseline/overall/gmiou1 | 35.441 | [34.059, 36.784] |
| baseline/overall/rr | 33.290 | [31.055, 35.473] |
| baseline/S+/frr | 24.536 | [22.367, 26.567] |
| baseline/U+/frr | 18.121 | [14.497, 21.828] |
| baseline/U-/false_acceptance | 62.857 | [54.877, 70.811] |
| baseline/gap/auroc | 10.598 | [5.558, 15.873] |
| baseline/gap/rej_f1 | 19.019 | [12.094, 26.341] |
| baseline/gap/gmiou1 | 14.022 | [11.176, 17.098] |
| experiment/S/rej_f1 | 56.375 | [53.699, 58.929] |
| experiment/S/gmiou1 | 37.786 | [36.225, 39.279] |
| experiment/S/rr | 35.469 | [32.955, 37.895] |
| experiment/S/auroc | 74.990 | [72.927, 76.992] |
| experiment/U/rej_f1 | 37.356 | [30.405, 43.990] |
| experiment/U/gmiou1 | 23.763 | [21.107, 26.228] |
| experiment/U/rr | 22.438 | [18.742, 26.115] |
| experiment/U/auroc | 64.392 | [59.315, 69.032] |
| experiment/overall/rej_f1 | 53.918 | [51.352, 56.442] |
| experiment/overall/gmiou1 | 35.441 | [34.059, 36.784] |
| experiment/overall/rr | 33.290 | [31.055, 35.473] |
| experiment/S+/frr | 24.536 | [22.367, 26.567] |
| experiment/U+/frr | 18.121 | [14.497, 21.828] |
| experiment/U-/false_acceptance | 62.857 | [54.877, 70.811] |
| experiment/gap/auroc | 10.598 | [5.558, 15.873] |
| experiment/gap/rej_f1 | 19.019 | [12.094, 26.341] |
| experiment/gap/gmiou1 | 14.022 | [11.176, 17.098] |
| candidates/S+/coverage | 77.389 | [75.142, 79.413] |
| candidates/S+/gt_recall | 77.389 | [75.142, 79.413] |
| candidates/S+/top1_hit | 38.397 | [36.171, 40.484] |
| candidates/S+/high_count | 2.354 | [2.322, 2.388] |
| candidates/S+/relative_count | 2.400 | [2.369, 2.434] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.019 | [1.926, 2.116] |
| candidates/S-/relative_count | 2.274 | [2.203, 2.349] |
| candidates/U+/coverage | 67.617 | [63.230, 71.901] |
| candidates/U+/gt_recall | 67.617 | [63.230, 71.901] |
| candidates/U+/top1_hit | 23.490 | [19.621, 27.363] |
| candidates/U+/high_count | 2.540 | [2.476, 2.600] |
| candidates/U+/relative_count | 2.565 | [2.503, 2.624] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.560 | [2.450, 2.669] |
| candidates/U-/relative_count | 2.623 | [2.511, 2.726] |
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
