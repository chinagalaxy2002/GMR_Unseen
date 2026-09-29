# Action-split evaluation files

This directory contains the exact machine-readable metric outputs for the three completed phase-2 action splits (A1, A2_alt, A3), each with seed 3407 and 100 training epochs. For every split and model (`moment`, `qd`, `flash`):

- `diagnostics.json` is from `scripts/analyze_semantic_existence.py`; it contains the seen-validation threshold, four-quadrant test diagnostics, seen/unseen AUROC, localization before and after the threshold, and matched-U PairAcc.
- `official_test_metrics.json` is from `eval/eval_main.py` on the same split's full test submission. Its overall AUROC and fixed-threshold metrics use different definitions from the subgroup diagnostics.

`cross_status_action/{moment,qd,flash}.summary.json` contains directed identical-query unseen→seen comparisons produced by `scripts/analyze_cross_split_status.py`. Each row records the split direction, existence label, qid/video counts, mean score change, and video-cluster bootstrap intervals. The associated query-level CSVs remain local because they include full queries and model predictions.

The [result report](../semantic_existence_action_multisplit_results.md) explains the numbers and their limits. Released A1/A2_alt/A3 ground truth is under [`data/release/semantic_existence_v2/`](../../data/release/semantic_existence_v2/). Checkpoints, query-level predictions and media are not included.
