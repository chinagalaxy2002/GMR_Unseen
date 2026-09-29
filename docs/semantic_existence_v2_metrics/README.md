# Phase 2 evaluation files

This directory contains machine-readable outputs for all five phase-2 splits, each trained with seed 3407 for 100 epochs. For every split and model (`moment`, `qd`, `flash`):

- `diagnostics.json` is from `scripts/analyze_semantic_existence.py`; it contains the seen-validation threshold, four-quadrant test diagnostics, seen/unseen AUROC, localization before and after the threshold, and matched-U PairAcc.
- `official_test_metrics.json` is from `eval/eval_main.py` on the same split's full test submission. Its overall AUROC and fixed-threshold metrics use different definitions from the subgroup diagnostics.

`cross_status_action/` and `cross_status_composition/` contain directed identical-query unseen→seen comparisons produced by `scripts/analyze_cross_split_status.py`. Each summary records split direction, existence label, qid/video counts, mean score change, and video-cluster bootstrap intervals. The associated query-level CSVs remain local because they include full queries and model predictions.

`bootstrap/<split>/<model>.json` gives 2,000-resample, test-video cluster percentile intervals for the core diagnostics. `text_only/<split>.json` records the text-only control. `test_query_distributions.json` summarizes query lengths and action/object distributions by quadrant.

The [five-split result report](../reports/semantic_existence_multisplit_results.md) explains the metrics and their limits. Released ground truth is under [`data/release/semantic_existence_v2/`](../../data/release/semantic_existence_v2/). Checkpoints, query-level predictions and media are not included.
