# Phase 2 action splits: A1, A2_alt, A3

Status on 2026-09-29: all three models completed 100 epochs with seed 3407 on each of the three action splits. A1 holds out `put/take`, A2_alt holds out `drink/pour`, and A3 holds out `run/walk`. All three use the same 1,500 reviewed S− training queries. Their S+ training sets necessarily differ. Checkpoints and existence thresholds were selected using S+/S− validation only. Each test submission contains precisely the qids in its release test file: 5,170 for A1, 4,945 for A2_alt, and 5,293 for A3, with no duplicate or missing qids.

## Four-quadrant test diagnostics

AUROC and PairAcc are unit fractions; the remaining columns are percentages. FRR is the false refusal rate on present U+ queries, RR is rejection of absent U− queries, and raw/gated R@1@0.5 measures U+ localization before/after the seen-calibrated hard existence gate. Matched pairs number 312, 79, and 129 for A1, A2_alt, and A3, respectively.

| Split | Model | Seen AUROC | Unseen AUROC | PairAcc | U+ FRR | U− RR | U+ raw R@1 | U+ gated R@1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A1 | Moment-DETR-GMR | 0.8044 | 0.4973 | 0.5593 | 23.23 | 25.47 | 23.01 | 17.85 |
| A1 | QD-DETR-GMR | 0.7827 | 0.5058 | 0.5721 | 16.13 | 18.23 | 24.52 | 20.65 |
| A1 | FlashVTG-GMR | 0.8158 | 0.5065 | 0.5561 | 19.14 | 20.82 | 29.46 | 23.66 |
| A2_alt | Moment-DETR-GMR | 0.7690 | 0.5511 | 0.6203 | 0.00 | 0.64 | 26.79 | 26.79 |
| A2_alt | QD-DETR-GMR | 0.7442 | 0.4727 | 0.4557 | 0.60 | 0.32 | 31.55 | 31.55 |
| A2_alt | FlashVTG-GMR | 0.7729 | 0.5240 | 0.5063 | 0.00 | 0.96 | 42.86 | 42.86 |
| A3 | Moment-DETR-GMR | 0.7488 | 0.5643 | 0.4690 | 29.17 | 33.00 | 39.58 | 28.12 |
| A3 | QD-DETR-GMR | 0.7334 | 0.4870 | 0.4535 | 30.21 | 31.31 | 44.27 | 33.33 |
| A3 | FlashVTG-GMR | 0.7422 | 0.6139 | 0.5155 | 23.44 | 43.77 | 46.88 | 34.38 |

Seen AUROC exceeds unseen AUROC in all nine runs. That pattern repeats across three action families, although the magnitude and failure mode vary. On A2_alt, all models accept nearly every U−, so low U+ refusal there is coupled with extremely poor unseen-negative rejection. A3 has larger hard-gate losses on U+ localization. Official full-test GMR AUROC, which uses the entire test set, is 69.53/68.73/70.32% for Moment/QD/Flash on A2_alt and 70.66/69.09/71.36% on A3. It must not be substituted for the seen or unseen subgroup AUROC above; the official evaluator also uses different fixed thresholds and gate definitions.

## Identical-query cross-split check

[`analyze_cross_split_status.py`](../../scripts/analyze_cross_split_status.py) matched the same `qid`, video, query, existence label and ground-truth windows where it is unseen in one split and seen in another. The three action releases yield 1,041 unique test qids and 2,082 directed comparisons because each unseen row can have two seen targets. The table shows the mean *seen-model score minus unseen-model score* for two comparisons, separately for truly present and absent queries. The 95% intervals resample test videos with seed 3407; the models themselves each have only one training seed.

| Unseen → seen split | Label | Identical qids | Moment-DETR | QD-DETR | FlashVTG |
| --- | --- | ---: | ---: | ---: | ---: |
| A1 → A2_alt | Present | 449 | +0.083 [0.061, 0.107] | +0.040 [0.023, 0.061] | +0.028 [0.017, 0.041] |
| A1 → A2_alt | Absent | 154 | +0.219 [0.154, 0.288] | +0.119 [0.064, 0.182] | +0.080 [0.047, 0.119] |
| A3 → A2_alt | Present | 177 | +0.086 [0.052, 0.121] | +0.044 [0.006, 0.087] | +0.078 [0.044, 0.118] |
| A3 → A2_alt | Absent | 21 | +0.604 [0.411, 0.773] | +0.266 [−0.005, 0.520] | +0.329 [0.105, 0.564] |

The same-query check holds video and wording fixed within each paired comparison. Scores often rise when an action becomes seen, but they also rise for absent queries, sometimes more. For A2_alt unseen queries, scores barely change when those queries become seen in A1 or A3; the A2_alt model already accepts almost all U−. These observations do not identify a pure causal effect of semantic exposure: each split trains on a different S+ pool, and model scores can have different calibration. The [full five-split report](semantic_existence_multisplit_results.md) adds composition-split test results and the C1↔C2_alt identical-query comparison.

The test metrics were produced with [`finalize_semantic_multisplit_group.sh`](../../scripts/finalize_semantic_multisplit_group.sh) and [`analyze_semantic_existence.py`](../../scripts/analyze_semantic_existence.py). The [exact metric JSON outputs](../semantic_existence_v2_metrics/) and released annotations, split specs and data provenance under [`data/release/semantic_existence_v2/`](../../data/release/semantic_existence_v2/) are in Git. Local checkpoints, query-level predictions, video features and raw videos are not included. The dataset owner's negative review is a global attestation for the exact candidate batch, without per-query review records.
