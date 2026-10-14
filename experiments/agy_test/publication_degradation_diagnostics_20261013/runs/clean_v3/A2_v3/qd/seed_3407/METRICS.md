# Frozen final evaluation

Counts: {'S+': 3230, 'S-': 1066, 'U+': 223, 'U-': 92}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 49.148 | [46.615, 51.632] |
| baseline/S/gmiou1 | 33.699 | [32.211, 35.151] |
| baseline/S/rr | 46.229 | [43.810, 48.508] |
| baseline/S/auroc | 72.390 | [69.984, 74.672] |
| baseline/U/rej_f1 | 15.517 | [6.897, 24.114] |
| baseline/U/gmiou1 | 25.641 | [21.967, 29.199] |
| baseline/U/rr | 7.619 | [3.610, 12.378] |
| baseline/U/auroc | 51.046 | [47.647, 54.494] |
| baseline/overall/rej_f1 | 47.917 | [45.402, 50.298] |
| baseline/overall/gmiou1 | 33.148 | [31.705, 34.534] |
| baseline/overall/rr | 43.591 | [41.298, 45.834] |
| baseline/S+/frr | 38.266 | [35.970, 40.606] |
| baseline/U+/frr | 6.726 | [2.666, 11.916] |
| baseline/U-/false_acceptance | 90.217 | [83.501, 96.041] |
| baseline/gap/auroc | 21.344 | [17.179, 25.573] |
| baseline/gap/rej_f1 | 33.631 | [24.868, 42.779] |
| baseline/gap/gmiou1 | 8.058 | [4.184, 11.967] |
| experiment/S/rej_f1 | 55.647 | [53.214, 57.995] |
| experiment/S/gmiou1 | 36.108 | [34.705, 37.552] |
| experiment/S/rr | 40.526 | [38.167, 42.793] |
| experiment/S/auroc | 76.751 | [74.737, 78.607] |
| experiment/U/rej_f1 | 2.151 | [0.000, 7.059] |
| experiment/U/gmiou1 | 21.186 | [17.498, 24.996] |
| experiment/U/rr | 0.317 | [0.000, 1.031] |
| experiment/U/auroc | 53.609 | [48.489, 58.954] |
| experiment/overall/rej_f1 | 53.931 | [51.524, 56.268] |
| experiment/overall/gmiou1 | 35.089 | [33.760, 36.439] |
| experiment/overall/rr | 37.779 | [35.566, 39.983] |
| experiment/S+/frr | 29.721 | [27.650, 31.684] |
| experiment/U+/frr | 0.000 | [0.000, 0.000] |
| experiment/U-/false_acceptance | 98.913 | [96.341, 100.000] |
| experiment/gap/auroc | 23.141 | [17.466, 28.689] |
| experiment/gap/rej_f1 | 53.496 | [48.366, 57.253] |
| experiment/gap/gmiou1 | 14.922 | [10.824, 19.014] |
| candidates/S+/coverage | 78.019 | [76.279, 79.720] |
| candidates/S+/gt_recall | 78.019 | [76.279, 79.720] |
| candidates/S+/top1_hit | 36.006 | [34.030, 37.868] |
| candidates/S+/high_count | 2.703 | [2.677, 2.728] |
| candidates/S+/relative_count | 2.721 | [2.696, 2.745] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.551 | [2.486, 2.613] |
| candidates/S-/relative_count | 2.638 | [2.575, 2.695] |
| candidates/U+/coverage | 79.821 | [73.798, 85.514] |
| candidates/U+/gt_recall | 79.821 | [73.798, 85.514] |
| candidates/U+/top1_hit | 34.978 | [27.569, 42.661] |
| candidates/U+/high_count | 2.915 | [2.864, 2.958] |
| candidates/U+/relative_count | 2.928 | [2.885, 2.966] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.946 | [2.882, 2.990] |
| candidates/U-/relative_count | 2.946 | [2.882, 2.990] |
| comparison/seen_change/auroc | 4.361 | [2.611, 6.213] |
| comparison/unseen_net_gain/auroc | 2.564 | [-2.824, 8.278] |
| comparison/gap_reduction/auroc | -1.797 | [-7.604, 4.141] |
| comparison/seen_change/rej_f1 | 6.498 | [4.708, 8.248] |
| comparison/unseen_net_gain/rej_f1 | -13.367 | [-22.222, -5.310] |
| comparison/gap_reduction/rej_f1 | -19.865 | [-28.927, -11.586] |
| comparison/seen_change/gmiou1 | 2.409 | [1.211, 3.712] |
| comparison/unseen_net_gain/gmiou1 | -4.454 | [-9.149, 0.094] |
| comparison/gap_reduction/gmiou1 | -6.864 | [-11.692, -2.030] |

Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available.
