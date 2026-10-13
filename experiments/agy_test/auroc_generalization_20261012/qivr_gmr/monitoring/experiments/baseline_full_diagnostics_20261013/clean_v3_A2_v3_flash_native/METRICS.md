# Frozen final evaluation

Counts: {'S+': 3230, 'S-': 1066, 'U+': 223, 'U-': 92}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 55.608 | [53.175, 58.069] |
| baseline/S/gmiou1 | 41.880 | [40.515, 43.391] |
| baseline/S/rr | 39.735 | [37.452, 42.013] |
| baseline/S/auroc | 77.065 | [75.117, 79.022] |
| baseline/U/rej_f1 | 2.151 | [0.000, 7.059] |
| baseline/U/gmiou1 | 29.590 | [25.818, 33.346] |
| baseline/U/rr | 0.317 | [0.000, 1.031] |
| baseline/U/auroc | 53.173 | [48.423, 57.966] |
| baseline/overall/rej_f1 | 53.873 | [51.399, 56.355] |
| baseline/overall/gmiou1 | 41.040 | [39.727, 42.461] |
| baseline/overall/rr | 37.042 | [34.768, 39.223] |
| baseline/S+/frr | 28.978 | [26.916, 30.979] |
| baseline/U+/frr | 0.000 | [0.000, 0.000] |
| baseline/U-/false_acceptance | 98.913 | [96.341, 100.000] |
| baseline/gap/auroc | 23.892 | [18.487, 29.265] |
| baseline/gap/rej_f1 | 53.457 | [48.218, 57.353] |
| baseline/gap/gmiou1 | 12.289 | [8.189, 16.268] |
| experiment/S/rej_f1 | 54.656 | [52.291, 56.839] |
| experiment/S/gmiou1 | 40.239 | [38.840, 41.608] |
| experiment/S/rr | 43.925 | [41.517, 46.288] |
| experiment/S/auroc | 78.549 | [76.736, 80.284] |
| experiment/U/rej_f1 | 2.151 | [0.000, 7.059] |
| experiment/U/gmiou1 | 27.609 | [24.194, 31.232] |
| experiment/U/rr | 0.317 | [0.000, 1.031] |
| experiment/U/auroc | 62.161 | [55.694, 68.469] |
| experiment/overall/rej_f1 | 53.053 | [50.675, 55.333] |
| experiment/overall/gmiou1 | 39.377 | [38.066, 40.686] |
| experiment/overall/rr | 40.946 | [38.596, 43.232] |
| experiment/S+/frr | 33.437 | [31.175, 35.565] |
| experiment/U+/frr | 0.000 | [0.000, 0.000] |
| experiment/U-/false_acceptance | 98.913 | [96.341, 100.000] |
| experiment/gap/auroc | 16.387 | [9.565, 23.003] |
| experiment/gap/rej_f1 | 52.506 | [47.241, 56.298] |
| experiment/gap/gmiou1 | 12.630 | [8.767, 16.393] |
| candidates/S+/coverage | 99.907 | [99.749, 100.000] |
| candidates/S+/gt_recall | 99.907 | [99.749, 100.000] |
| candidates/S+/top1_hit | 50.929 | [48.699, 53.030] |
| candidates/S+/high_count | 0.345 | [0.313, 0.380] |
| candidates/S+/relative_count | 12.218 | [11.884, 12.553] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 0.375 | [0.315, 0.438] |
| candidates/S-/relative_count | 12.160 | [11.586, 12.749] |
| candidates/U+/coverage | 100.000 | [100.000, 100.000] |
| candidates/U+/gt_recall | 100.000 | [100.000, 100.000] |
| candidates/U+/top1_hit | 43.498 | [36.000, 51.030] |
| candidates/U+/high_count | 0.112 | [0.038, 0.206] |
| candidates/U+/relative_count | 16.390 | [15.411, 17.427] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 0.087 | [0.000, 0.230] |
| candidates/U-/relative_count | 16.402 | [15.069, 17.713] |
| comparison/seen_change/auroc | 1.483 | [0.635, 2.356] |
| comparison/unseen_net_gain/auroc | 8.988 | [3.662, 14.273] |
| comparison/gap_reduction/auroc | 7.505 | [2.156, 12.742] |
| comparison/seen_change/rej_f1 | -0.951 | [-2.112, 0.225] |
| comparison/unseen_net_gain/rej_f1 | 0.000 | [0.000, 0.000] |
| comparison/gap_reduction/rej_f1 | 0.951 | [-0.225, 2.112] |
| comparison/seen_change/gmiou1 | -1.640 | [-2.620, -0.675] |
| comparison/unseen_net_gain/gmiou1 | -1.981 | [-5.412, 1.667] |
| comparison/gap_reduction/gmiou1 | -0.341 | [-3.978, 3.370] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
