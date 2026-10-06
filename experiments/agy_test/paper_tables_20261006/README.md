# Paper tables: independent candidate verifier

This directory evaluates the latest frozen **independent_candidate_transfer_suite** experiment. It does not combine metrics from previous DDV or SDCV experiments.

## Files

- `PAPER_TABLES.md`: degradation, full Table-2-style metrics for All / Seen / Unseen queries, fixed-threshold supplements, and FlashVTG ablations.
- `paper_tables.tex`: tables for a paper using `booktabs` and `graphicx`.
- `paper_metrics.json`: aggregated metrics, subset counts, and individual split / seed results.
- `per_split_seed_metrics.csv`: complete operating thresholds and metrics.
- `input_manifest.json`: hashes of inputs read during recomputation.
- `build_tables.py`, `recompute.log`: reproducible metric computation and its log.

## Recompute

```bash
/home/guoxiangyu/miniconda3/envs/univtg/bin/python \
  experiments/agy_test/paper_tables_20261006/build_tables.py
```

No training is performed. The script reads existing predictions and replays validation checkpoints on CPU where needed to select ablation thresholds using only Seen validation labels.

## Protocol

Five semantic-existence splits of Charades-STA are averaged equally. Full verifier results average per-seed metrics over seeds 3407, 42, and 2024, rather than ensembling predictions. Baselines use the existing backbone existence probabilities. Mechanism A uses each target backbone's own published candidate windows. Temporal localization metrics use positive queries without existence gating; G-mIoU applies the rejection gate.

The main operating points use Seen-validation Youden J with the original experiment's 100-point threshold grid. Separate tables use the original GMR paper's fixed threshold 0.4. This is a **Table-2-style evaluation on a different dataset**, not a reproduction of the paper's Soccer-GMR Table 2.

All metrics are percentages. Gap differences are percentage points. Multi-moment recall is reported as unavailable when no positive queries have multiple annotated moments. Confidence intervals for gap reduction come from the completed independent paired video-cluster audit; they condition on the three fixed training seeds.
