# Frozen final evaluation

Counts: {'S+': 3230, 'S-': 1066, 'U+': 223, 'U-': 92}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 54.031 | [51.647, 56.279] |
| baseline/S/gmiou1 | 35.314 | [33.971, 36.660] |
| baseline/S/rr | 40.154 | [37.761, 42.518] |
| baseline/S/auroc | 75.445 | [73.572, 77.232] |
| baseline/U/rej_f1 | 2.151 | [0.000, 7.059] |
| baseline/U/gmiou1 | 20.748 | [17.325, 24.203] |
| baseline/U/rr | 0.317 | [0.000, 1.031] |
| baseline/U/auroc | 50.751 | [45.696, 55.589] |
| baseline/overall/rej_f1 | 52.358 | [49.981, 54.636] |
| baseline/overall/gmiou1 | 34.319 | [33.064, 35.605] |
| baseline/overall/rr | 37.432 | [35.120, 39.669] |
| baseline/S+/frr | 30.062 | [28.019, 32.049] |
| baseline/U+/frr | 0.000 | [0.000, 0.000] |
| baseline/U-/false_acceptance | 98.913 | [96.341, 100.000] |
| baseline/gap/auroc | 24.694 | [19.396, 30.124] |
| baseline/gap/rej_f1 | 51.880 | [46.593, 55.689] |
| baseline/gap/gmiou1 | 14.565 | [10.641, 18.203] |
| experiment/S/rej_f1 | 54.031 | [51.647, 56.279] |
| experiment/S/gmiou1 | 35.314 | [33.971, 36.660] |
| experiment/S/rr | 40.154 | [37.761, 42.518] |
| experiment/S/auroc | 75.445 | [73.572, 77.232] |
| experiment/U/rej_f1 | 2.151 | [0.000, 7.059] |
| experiment/U/gmiou1 | 20.748 | [17.325, 24.203] |
| experiment/U/rr | 0.317 | [0.000, 1.031] |
| experiment/U/auroc | 50.751 | [45.696, 55.589] |
| experiment/overall/rej_f1 | 52.358 | [49.981, 54.636] |
| experiment/overall/gmiou1 | 34.319 | [33.064, 35.605] |
| experiment/overall/rr | 37.432 | [35.120, 39.669] |
| experiment/S+/frr | 30.062 | [28.019, 32.049] |
| experiment/U+/frr | 0.000 | [0.000, 0.000] |
| experiment/U-/false_acceptance | 98.913 | [96.341, 100.000] |
| experiment/gap/auroc | 24.694 | [19.396, 30.124] |
| experiment/gap/rej_f1 | 51.880 | [46.593, 55.689] |
| experiment/gap/gmiou1 | 14.565 | [10.641, 18.203] |
| candidates/S+/coverage | 75.542 | [73.480, 77.544] |
| candidates/S+/gt_recall | 75.542 | [73.480, 77.544] |
| candidates/S+/top1_hit | 36.656 | [34.607, 38.600] |
| candidates/S+/high_count | 2.494 | [2.467, 2.523] |
| candidates/S+/relative_count | 2.537 | [2.511, 2.564] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 2.213 | [2.122, 2.305] |
| candidates/S-/relative_count | 2.442 | [2.373, 2.511] |
| candidates/U+/coverage | 85.202 | [79.638, 90.393] |
| candidates/U+/gt_recall | 85.202 | [79.638, 90.393] |
| candidates/U+/top1_hit | 35.426 | [28.240, 42.554] |
| candidates/U+/high_count | 2.812 | [2.750, 2.868] |
| candidates/U+/relative_count | 2.825 | [2.763, 2.881] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 2.826 | [2.727, 2.913] |
| candidates/U-/relative_count | 2.837 | [2.747, 2.918] |
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
