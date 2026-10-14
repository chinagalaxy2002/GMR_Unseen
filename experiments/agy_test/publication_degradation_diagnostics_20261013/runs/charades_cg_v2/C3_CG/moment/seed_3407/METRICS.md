# Frozen final evaluation

Counts: {'S+': 2684, 'S-': 2684, 'U+': 2990, 'U-': 2990}. Video-cluster bootstrap: 2000; seed 3407. All checkpoints/thresholds use Seen validation only.

| Metric (%) or change (pp) | Point | 95% CI |
|---|---:|---|
| baseline/S/rej_f1 | 63.869 | [62.266, 65.578] |
| baseline/S/gmiou1 | 45.950 | [44.480, 47.489] |
| baseline/S/rr | 64.512 | [62.966, 66.054] |
| baseline/S/auroc | 63.376 | [61.696, 65.090] |
| baseline/U/rej_f1 | 60.100 | [58.577, 61.650] |
| baseline/U/gmiou1 | 41.487 | [40.147, 42.845] |
| baseline/U/rr | 67.642 | [66.017, 69.147] |
| baseline/U/auroc | 55.867 | [54.230, 57.488] |
| baseline/overall/rej_f1 | 61.857 | [60.596, 63.084] |
| baseline/overall/gmiou1 | 43.598 | [42.499, 44.736] |
| baseline/overall/rr | 66.161 | [64.789, 67.367] |
| baseline/S+/frr | 55.887 | [53.589, 58.200] |
| baseline/U+/frr | 64.582 | [62.399, 66.490] |
| baseline/U-/false_acceptance | 29.298 | [27.249, 31.404] |
| baseline/gap/auroc | 7.509 | [5.408, 9.624] |
| baseline/gap/rej_f1 | 3.769 | [1.886, 5.783] |
| baseline/gap/gmiou1 | 4.463 | [2.751, 6.275] |
| experiment/S/rej_f1 | 63.869 | [62.266, 65.578] |
| experiment/S/gmiou1 | 45.950 | [44.480, 47.489] |
| experiment/S/rr | 64.512 | [62.966, 66.054] |
| experiment/S/auroc | 63.376 | [61.696, 65.090] |
| experiment/U/rej_f1 | 60.100 | [58.577, 61.650] |
| experiment/U/gmiou1 | 41.487 | [40.147, 42.845] |
| experiment/U/rr | 67.642 | [66.017, 69.147] |
| experiment/U/auroc | 55.867 | [54.230, 57.488] |
| experiment/overall/rej_f1 | 61.857 | [60.596, 63.084] |
| experiment/overall/gmiou1 | 43.598 | [42.499, 44.736] |
| experiment/overall/rr | 66.161 | [64.789, 67.367] |
| experiment/S+/frr | 55.887 | [53.589, 58.200] |
| experiment/U+/frr | 64.582 | [62.399, 66.490] |
| experiment/U-/false_acceptance | 29.298 | [27.249, 31.404] |
| experiment/gap/auroc | 7.509 | [5.408, 9.624] |
| experiment/gap/rej_f1 | 3.769 | [1.886, 5.783] |
| experiment/gap/gmiou1 | 4.463 | [2.751, 6.275] |
| candidates/S+/coverage | 74.367 | [72.392, 76.251] |
| candidates/S+/gt_recall | 74.367 | [72.392, 76.251] |
| candidates/S+/top1_hit | 40.537 | [38.321, 42.846] |
| candidates/S+/high_count | 1.507 | [1.483, 1.532] |
| candidates/S+/relative_count | 1.656 | [1.636, 1.676] |
| candidates/S-/coverage | undefined | undefined |
| candidates/S-/gt_recall | undefined | undefined |
| candidates/S-/top1_hit | undefined | undefined |
| candidates/S-/high_count | 1.314 | [1.286, 1.341] |
| candidates/S-/relative_count | 1.620 | [1.600, 1.639] |
| candidates/U+/coverage | 69.666 | [67.640, 71.610] |
| candidates/U+/gt_recall | 69.666 | [67.640, 71.610] |
| candidates/U+/top1_hit | 31.204 | [29.346, 33.188] |
| candidates/U+/high_count | 1.661 | [1.640, 1.681] |
| candidates/U+/relative_count | 1.795 | [1.780, 1.810] |
| candidates/U-/coverage | undefined | undefined |
| candidates/U-/gt_recall | undefined | undefined |
| candidates/U-/top1_hit | undefined | undefined |
| candidates/U-/high_count | 1.592 | [1.571, 1.614] |
| candidates/U-/relative_count | 1.785 | [1.769, 1.800] |
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
