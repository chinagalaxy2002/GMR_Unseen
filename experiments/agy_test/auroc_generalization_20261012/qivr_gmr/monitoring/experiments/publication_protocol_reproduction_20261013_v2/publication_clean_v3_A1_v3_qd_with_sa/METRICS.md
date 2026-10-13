# Frozen final evaluation

Counts: {'S+': 2857, 'S-': 983, 'U+': 596, 'U-': 175}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 55.515 | [51.730, 59.054] |
| baseline/S/gmiou1 | 39.433 | [37.853, 41.098] |
| baseline/S/rr | 24.219 | [22.319, 26.180] |
| baseline/S/auroc | 72.951 | [70.266, 75.564] |
| baseline/U/rej_f1 | 28.923 | [22.286, 35.594] |
| baseline/U/gmiou1 | 22.806 | [20.496, 25.246] |
| baseline/U/rr | 19.455 | [16.085, 23.183] |
| baseline/U/auroc | 55.862 | [51.043, 60.748] |
| baseline/overall/rej_f1 | 51.653 | [48.154, 54.914] |
| baseline/overall/gmiou1 | 36.653 | [35.197, 38.103] |
| baseline/overall/rr | 23.422 | [21.749, 25.208] |
| baseline/S+/frr | 13.966 | [12.384, 15.633] |
| baseline/U+/frr | 17.282 | [13.764, 21.053] |
| baseline/U-/false_acceptance | 73.143 | [65.475, 80.226] |
| baseline/gap/auroc | 17.089 | [11.661, 22.491] |
| baseline/gap/rej_f1 | 26.592 | [19.158, 34.224] |
| baseline/gap/gmiou1 | 16.627 | [13.780, 19.505] |
| experiment/S/rej_f1 | 55.515 | [51.730, 59.054] |
| experiment/S/gmiou1 | 39.433 | [37.853, 41.098] |
| experiment/S/rr | 24.219 | [22.319, 26.180] |
| experiment/S/auroc | 72.951 | [70.266, 75.564] |
| experiment/U/rej_f1 | 28.923 | [22.286, 35.594] |
| experiment/U/gmiou1 | 22.806 | [20.496, 25.246] |
| experiment/U/rr | 19.455 | [16.085, 23.183] |
| experiment/U/auroc | 55.862 | [51.043, 60.748] |
| experiment/overall/rej_f1 | 51.653 | [48.154, 54.914] |
| experiment/overall/gmiou1 | 36.653 | [35.197, 38.103] |
| experiment/overall/rr | 23.422 | [21.749, 25.208] |
| experiment/S+/frr | 13.966 | [12.384, 15.633] |
| experiment/U+/frr | 17.282 | [13.764, 21.053] |
| experiment/U-/false_acceptance | 73.143 | [65.475, 80.226] |
| experiment/gap/auroc | 17.089 | [11.661, 22.491] |
| experiment/gap/rej_f1 | 26.592 | [19.158, 34.224] |
| experiment/gap/gmiou1 | 16.627 | [13.780, 19.505] |
| candidates/S+/coverage | 89.184 | [87.641, 90.729] |
| candidates/S+/gt_recall | 89.184 | [87.641, 90.729] |
| candidates/S+/top1_hit | 42.142 | [39.908, 44.353] |
| candidates/S+/high_count | 1.307 | [1.277, 1.336] |
| candidates/S+/relative_count | 1.349 | [1.322, 1.378] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 0.869 | [0.801, 0.939] |
| candidates/S-/relative_count | 1.003 | [0.935, 1.073] |
| candidates/U+/coverage | 85.906 | [82.524, 89.055] |
| candidates/U+/gt_recall | 85.906 | [82.524, 89.055] |
| candidates/U+/top1_hit | 24.832 | [20.910, 28.883] |
| candidates/U+/high_count | 1.451 | [1.392, 1.510] |
| candidates/U+/relative_count | 1.488 | [1.432, 1.545] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 1.406 | [1.287, 1.522] |
| candidates/U-/relative_count | 1.423 | [1.307, 1.538] |
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
