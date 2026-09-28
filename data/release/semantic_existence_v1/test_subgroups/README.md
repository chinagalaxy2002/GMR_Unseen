# Semantic Existence v1 test subgroups

Views contain only U+/U− test rows and preserve the released JSONL records and order. `unseen_action.jsonl` (open/close) and `unseen_composition.jsonl` are disjoint; the 16 pair files include an empty `dress__front.jsonl` because all three reviewed candidates were QC-excluded.

`counts.csv` lists group sizes. `metrics.csv` contains strict GMR, semantic-seen reference, and localization-only results for Moment-DETR, QD-DETR, and FlashVTG. Blank cells mean the metric is undefined or unavailable (for example, no U− or no existence head). `matched_pair_metrics.csv` groups the 535 matched pairs by the **positive query action**; all pairs are from unseen_action, so there is no composition PairAcc. FRR/RR and hard-gated R@1 use each GMR checkpoint’s seen-validation threshold. Per-pair AUC with tiny or one-sided groups should not be over-interpreted.
