# Frozen final evaluation

Counts: {'S+': 814, 'S-': 1104, 'U+': 122, 'U-': 193}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 76.294 | [74.400, 78.011] |
| baseline/S/gmiou1 | 50.656 | [48.170, 53.044] |
| baseline/S/rr | 67.362 | [64.264, 70.284] |
| baseline/S/auroc | 77.952 | [76.009, 79.764] |
| baseline/U/rej_f1 | 78.802 | [74.418, 82.714] |
| baseline/U/gmiou1 | 55.806 | [49.747, 61.809] |
| baseline/U/rr | 76.508 | [71.616, 81.293] |
| baseline/U/auroc | 66.797 | [61.031, 72.668] |
| baseline/overall/rej_f1 | 76.678 | [74.941, 78.238] |
| baseline/overall/gmiou1 | 51.383 | [48.981, 53.654] |
| baseline/overall/rr | 68.652 | [65.681, 71.409] |
| baseline/S+/frr | 46.437 | [42.681, 50.126] |
| baseline/U+/frr | 57.377 | [49.635, 64.656] |
| baseline/U-/false_acceptance | 11.399 | [6.896, 16.043] |
| baseline/gap/auroc | 11.156 | [4.971, 17.071] |
| baseline/gap/rej_f1 | -2.508 | [-6.890, 2.127] |
| baseline/gap/gmiou1 | -5.149 | [-11.560, 1.195] |
| experiment/S/rej_f1 | 72.277 | [69.553, 74.575] |
| experiment/S/gmiou1 | 44.339 | [41.627, 46.825] |
| experiment/S/rr | 53.962 | [50.681, 57.025] |
| experiment/S/auroc | 77.565 | [75.530, 79.396] |
| experiment/U/rej_f1 | 76.674 | [72.055, 80.860] |
| experiment/U/gmiou1 | 54.188 | [48.195, 60.273] |
| experiment/U/rr | 76.190 | [71.609, 80.734] |
| experiment/U/auroc | 66.718 | [61.430, 72.482] |
| experiment/overall/rej_f1 | 73.017 | [70.642, 75.019] |
| experiment/overall/gmiou1 | 45.728 | [43.257, 47.986] |
| experiment/overall/rr | 57.098 | [54.076, 60.034] |
| experiment/S+/frr | 32.187 | [28.938, 35.508] |
| experiment/U+/frr | 60.656 | [53.913, 67.228] |
| experiment/U-/false_acceptance | 13.990 | [9.090, 19.419] |
| experiment/gap/auroc | 10.846 | [4.747, 16.248] |
| experiment/gap/rej_f1 | -4.398 | [-9.536, 0.556] |
| experiment/gap/gmiou1 | -9.848 | [-16.520, -3.788] |
| candidates/S+/coverage | 66.708 | [63.020, 70.604] |
| candidates/S+/gt_recall | 49.488 | [46.308, 52.590] |
| candidates/S+/top1_hit | 22.604 | [19.036, 26.140] |
| candidates/S+/high_count | 4.193 | [4.003, 4.390] |
| candidates/S+/relative_count | 5.065 | [4.910, 5.238] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.163 | [2.011, 2.327] |
| candidates/S-/relative_count | 4.219 | [4.045, 4.393] |
| candidates/U+/coverage | 58.197 | [47.872, 67.481] |
| candidates/U+/gt_recall | 43.033 | [34.722, 51.588] |
| candidates/U+/top1_hit | 14.754 | [7.874, 22.430] |
| candidates/U+/high_count | 3.197 | [2.888, 3.511] |
| candidates/U+/relative_count | 4.762 | [4.468, 5.075] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 1.933 | [1.741, 2.130] |
| candidates/U-/relative_count | 3.959 | [3.732, 4.177] |
| comparison/seen_change/auroc | -0.388 | [-1.600, 0.728] |
| comparison/unseen_net_gain/auroc | -0.079 | [-4.639, 4.632] |
| comparison/gap_reduction/auroc | 0.309 | [-4.490, 5.333] |
| comparison/seen_change/rej_f1 | -4.017 | [-5.808, -2.478] |
| comparison/unseen_net_gain/rej_f1 | -2.127 | [-5.697, 1.113] |
| comparison/gap_reduction/rej_f1 | 1.890 | [-1.945, 5.423] |
| comparison/seen_change/gmiou1 | -6.317 | [-7.893, -4.875] |
| comparison/unseen_net_gain/gmiou1 | -1.618 | [-5.386, 1.918] |
| comparison/gap_reduction/gmiou1 | 4.699 | [0.885, 8.341] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
