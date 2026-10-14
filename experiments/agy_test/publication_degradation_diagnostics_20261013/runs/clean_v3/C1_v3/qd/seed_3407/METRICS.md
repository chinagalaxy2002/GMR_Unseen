# Frozen final evaluation

Counts: {'S+': 3311, 'S-': 894, 'U+': 142, 'U-': 264}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 51.290 | [49.025, 53.451] |
| baseline/S/gmiou1 | 33.891 | [32.577, 35.114] |
| baseline/S/rr | 41.427 | [39.332, 43.511] |
| baseline/S/auroc | 78.534 | [76.795, 80.294] |
| baseline/U/rej_f1 | 26.300 | [18.342, 34.170] |
| baseline/U/gmiou1 | 24.403 | [20.366, 28.472] |
| baseline/U/rr | 15.517 | [10.670, 20.632] |
| baseline/U/auroc | 57.750 | [52.582, 63.055] |
| baseline/overall/rej_f1 | 48.532 | [46.268, 50.745] |
| baseline/overall/gmiou1 | 33.056 | [31.758, 34.242] |
| baseline/overall/rr | 39.146 | [37.081, 41.202] |
| baseline/S+/frr | 32.196 | [30.112, 34.236] |
| baseline/U+/frr | 14.085 | [7.970, 20.690] |
| baseline/U-/false_acceptance | 83.712 | [77.642, 89.338] |
| baseline/gap/auroc | 20.783 | [14.954, 26.506] |
| baseline/gap/rej_f1 | 24.990 | [16.881, 33.126] |
| baseline/gap/gmiou1 | 9.488 | [5.222, 13.647] |
| experiment/S/rej_f1 | 51.290 | [49.025, 53.451] |
| experiment/S/gmiou1 | 33.891 | [32.577, 35.114] |
| experiment/S/rr | 41.427 | [39.332, 43.511] |
| experiment/S/auroc | 78.534 | [76.795, 80.294] |
| experiment/U/rej_f1 | 26.300 | [18.342, 34.170] |
| experiment/U/gmiou1 | 24.403 | [20.366, 28.472] |
| experiment/U/rr | 15.517 | [10.670, 20.632] |
| experiment/U/auroc | 57.750 | [52.582, 63.055] |
| experiment/overall/rej_f1 | 48.532 | [46.268, 50.745] |
| experiment/overall/gmiou1 | 33.056 | [31.758, 34.242] |
| experiment/overall/rr | 39.146 | [37.081, 41.202] |
| experiment/S+/frr | 32.196 | [30.112, 34.236] |
| experiment/U+/frr | 14.085 | [7.970, 20.690] |
| experiment/U-/false_acceptance | 83.712 | [77.642, 89.338] |
| experiment/gap/auroc | 20.783 | [14.954, 26.506] |
| experiment/gap/rej_f1 | 24.990 | [16.881, 33.126] |
| experiment/gap/gmiou1 | 9.488 | [5.222, 13.647] |
| candidates/S+/coverage | 85.986 | [84.565, 87.380] |
| candidates/S+/gt_recall | 85.986 | [84.565, 87.380] |
| candidates/S+/top1_hit | 35.488 | [33.602, 37.456] |
| candidates/S+/high_count | 2.546 | [2.518, 2.574] |
| candidates/S+/relative_count | 2.572 | [2.545, 2.599] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.459 | [2.398, 2.517] |
| candidates/S-/relative_count | 2.504 | [2.444, 2.563] |
| candidates/U+/coverage | 89.437 | [83.673, 94.444] |
| candidates/U+/gt_recall | 89.437 | [83.673, 94.444] |
| candidates/U+/top1_hit | 50.704 | [40.800, 60.626] |
| candidates/U+/high_count | 2.472 | [2.336, 2.604] |
| candidates/U+/relative_count | 2.507 | [2.370, 2.636] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.602 | [2.462, 2.729] |
| candidates/U-/relative_count | 2.617 | [2.482, 2.743] |
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
