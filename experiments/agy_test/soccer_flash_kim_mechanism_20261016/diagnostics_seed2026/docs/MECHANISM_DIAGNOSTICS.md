# E0 → A3 mechanism diagnostics

## Question

Why does A3 improve existence detection when E0 can already localize a ground-truth event but assigns the query a low existence score?

The analysis is paired by `seed × qid`. Diagnostics never enter the loss, checkpoint selection, early stopping, or threshold selection. E0 is selected by Val native pre-NMS mAP, matching the released baseline protocol. Task A and A3 are selected by Val raw-logit AUROC. Test is evaluated only after the selected checkpoint is frozen.

## Architectural fact

Neither experiment uses max pooling on its actual decision path under the Soccer-Flash configuration.

- E0 uses masked **mean pooling**, concatenates pooled video and query features, then applies an MLP.
- A3 replaces the E0 existence MLP with a newly initialized sequential cross-attention `EventReadout`. It inherits and freezes the selected E0 localizer. The legacy pooled vector is ignored.
- Max-pool owner dimensions are retained only as a labelled counterfactual representation diagnostic. They must not be interpreted as causal attribution.

## Recorded evidence

For every Val epoch and the frozen Test checkpoint:

1. The first three native ranked localization windows are matched to GT at IoU ≥ 0.5.
2. Positive queries are marked as false rejects at thresholds 0.4 and 0.5.
3. E0 records the actual mean-pool contribution of slots covered by hit windows, dominant feature dimensions, and the logit drop after removing their additive contribution.
4. A3 records per-layer cross-attention mass on slots covered by hit windows, the logit drop after masking those slots from the readout, the hit-only logit, and a mismatched-text intervention.
5. Both models record counterfactual max-owner dimensions, explicitly marked non-causal.
6. Training records every-step loss/gradient norm, sampled objective-gradient interactions, per-epoch parameter updates, score distributions, same-video ranking, selection traces, RNG state, and immutable-localizer checks.

## Mechanism tests

The automatic paired report separates four outcomes for E0 hit-positive queries: rescued by A3, persistently rejected, persistently accepted, and regressed. A mechanism claim requires all of the following:

- rescued queries receive more actual A3 attention on hit slots than persistent rejects;
- masking hit slots causes a larger A3 logit drop for rescued queries;
- the pattern is consistent across seeds and visible before looking at Test;
- the gain is not explained only by a global score shift or threshold calibration;
- localization fingerprints remain unchanged.

The reduced run keeps seed 2026 only. Outputs are written to `reports/mechanism/paired_queries.csv`, `epoch_summary.csv`, `MECHANISM_RESULTS.json`, and `mechanism_trajectory.png` after it completes.

An exact `EventReadout control (no min-neg)` uses the same readout, seed, E0 checkpoint, data order, optimizer, 100-epoch budget, 23-epoch patience, and Val-AUROC selection. It is a new ablation, not the public A3. Public A3 enables similarity hard-negative/min-neg. The hard-negative forward is RNG-forked so its additional dropout draws do not shift the main-path dropout sequence. `selected_three_way.csv` decomposes E0 → control and control → A3 at their frozen checkpoints.
