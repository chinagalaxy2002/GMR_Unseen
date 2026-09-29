# Phase 2: five independent semantic holdout splits

All five frozen splits completed 100-epoch training for Moment-DETR-GMR, QD-DETR-GMR and FlashVTG-GMR with seed 3407 and early stopping disabled. Best checkpoints and existence thresholds used S+/S− validation only. Test submissions cover every test qid exactly once. The five annotation releases are checked in under [`data/release/semantic_existence_v2/`](../../data/release/semantic_existence_v2/); checkpoints and query-level predictions remain local.

## Test diagnostics

AUROC and PairAcc are unit fractions. FRR, RR and R@1@0.5 are percentages. PairAcc compares existence scores for same-video, same-source U+/U− pairs. Raw R@1 uses the localization output before hard existence gating; gated R@1 also requires the U+ score to pass its threshold calibrated on seen validation.

| Split | Model | Seen AUROC | Unseen AUROC | PairAcc | U+ FRR | U− RR | U+ raw R@1 | U+ gated R@1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A1 | Moment | 0.8044 | 0.4973 | 0.5593 | 23.23 | 25.47 | 23.01 | 17.85 |
| A1 | QD | 0.7827 | 0.5058 | 0.5721 | 16.13 | 18.23 | 24.52 | 20.65 |
| A1 | Flash | 0.8158 | 0.5065 | 0.5561 | 19.14 | 20.82 | 29.46 | 23.66 |
| A2_alt | Moment | 0.7690 | 0.5511 | 0.6203 | 0.00 | 0.64 | 26.79 | 26.79 |
| A2_alt | QD | 0.7442 | 0.4727 | 0.4557 | 0.60 | 0.32 | 31.55 | 31.55 |
| A2_alt | Flash | 0.7729 | 0.5240 | 0.5063 | 0.00 | 0.96 | 42.86 | 42.86 |
| A3 | Moment | 0.7488 | 0.5643 | 0.4690 | 29.17 | 33.00 | 39.58 | 28.12 |
| A3 | QD | 0.7334 | 0.4870 | 0.4535 | 30.21 | 31.31 | 44.27 | 33.33 |
| A3 | Flash | 0.7422 | 0.6139 | 0.5155 | 23.44 | 43.77 | 46.88 | 34.38 |
| C1 | Moment | 0.7610 | 0.5621 | 0.6285 | 3.70 | 7.78 | 48.77 | 47.53 |
| C1 | QD | 0.7798 | 0.5618 | 0.6354 | 3.09 | 5.56 | 42.59 | 41.98 |
| C1 | Flash | 0.7533 | 0.5479 | 0.5556 | 3.70 | 3.70 | 51.23 | 48.77 |
| C2_alt | Moment | 0.6759 | 0.4687 | 0.7273 | 98.26 | 96.85 | 35.65 | 0.00 |
| C2_alt | QD | 0.6979 | 0.5447 | 0.5303 | 47.83 | 53.94 | 38.26 | 24.35 |
| C2_alt | Flash | 0.6907 | 0.5474 | 0.5455 | 61.74 | 64.57 | 42.61 | 15.65 |

Seen AUROC exceeds unseen AUROC in all 15 runs. The seen–unseen gap ranges from 0.128 to 0.309. A2_alt has near-zero U− rejection across all models, paired with near-zero U+ refusal; this is broad acceptance rather than good unseen existence discrimination. C2_alt Moment-DETR rejects almost all U+ and U− at its seen threshold. C1's raw localization is relatively strong and incurs little gate loss; other groups show larger losses, especially C2_alt.

The following means weight each frozen group equally within its novelty axis; they do not pool queries or treat groups as independent video domains.

| Axis | Model | Mean seen AUROC | Mean unseen AUROC | Mean gap | Mean PairAcc |
| --- | --- | ---: | ---: | ---: | ---: |
| Action (3 groups) | Moment | 0.7741 | 0.5376 | 0.2365 | 0.5495 |
| Action | QD | 0.7534 | 0.4885 | 0.2649 | 0.4938 |
| Action | Flash | 0.7770 | 0.5481 | 0.2289 | 0.5260 |
| Composition (2 groups) | Moment | 0.7185 | 0.5154 | 0.2031 | 0.6779 |
| Composition | QD | 0.7388 | 0.5533 | 0.1856 | 0.5829 |
| Composition | Flash | 0.7220 | 0.5476 | 0.1744 | 0.5505 |

The [action-split report](semantic_existence_action_multisplit_results.md) gives the action-axis table and identical-query analysis. Exact point metrics and official full-test GMR outputs for all groups are in [`semantic_existence_v2_metrics/`](../semantic_existence_v2_metrics/). Official full-test AUROC and fixed-threshold metrics use different definitions from the seen/unseen subgroup diagnostics.

## Video-cluster uncertainty

For each model and split, 2,000 percentile bootstrap replicates resampled test videos with replacement using seed 3407. [`bootstrap/`](../semantic_existence_v2_metrics/bootstrap/) stores 95% intervals for seen and unseen AUROC, U+ FRR, U− RR, matched-pair accuracy, and raw/gated U+ R@1@0.5. These intervals describe test-video sampling uncertainty for a fixed trained model; they do not measure variability across training seeds.

## Same-query unseen-to-seen comparison

We matched the same qid, video, text, label and temporal annotation when a query is unseen in one split and seen in another. For composition splits, the same test items yield 801 directed comparisons: C1→C2_alt has 162 present and 270 absent queries; C2_alt→C1 has 115 present and 254 absent queries. Mean score changes below are *seen-model score minus unseen-model score*; the corresponding video-cluster 95% intervals are in [`cross_status_composition/`](../semantic_existence_v2_metrics/cross_status_composition/).

| Direction | Label | Qids | Moment | QD | Flash |
| --- | --- | ---: | ---: | ---: | ---: |
| C1→C2_alt | Present | 162 | +0.004 | −0.006 | −0.003 |
| C1→C2_alt | Absent | 270 | +0.027 | −0.003 | −0.002 |
| C2_alt→C1 | Present | 115 | +0.283 | +0.191 | +0.128 |
| C2_alt→C1 | Absent | 254 | +0.258 | +0.161 | +0.175 |

When queries from C2_alt become seen in C1, all three models raise scores for both present and absent events. For the reverse direction, score changes are close to zero. This asymmetry is consistent with different learned score calibration and S+ training distributions across splits; it is not an isolated causal estimate of semantic exposure. The action-axis version is reported in the [action-split report](semantic_existence_action_multisplit_results.md).

## Text-only and query-distribution checks

The character 2–4 gram TF-IDF plus class-balanced logistic-regression diagnostic uses only training query text and no video. It checks for residual language cues; high matched-pair accuracy means PairAcc should not be interpreted as pure visual reasoning.

| Split | Text-only all AUROC | Seen AUROC | Unseen AUROC | Matched-pair accuracy |
| --- | ---: | ---: | ---: | ---: |
| A1 | 0.6557 | 0.8220 | 0.5010 | 0.3365 |
| A2_alt | 0.6971 | 0.7522 | 0.4446 | 0.7975 |
| A3 | 0.6768 | 0.7331 | 0.4234 | 0.4961 |
| C1 | 0.7221 | 0.7840 | 0.5967 | 0.6250 |
| C2_alt | 0.7310 | 0.7147 | 0.5885 | 0.8182 |

The composition U+ samples have three distinct objects in C1 and two in C2_alt; object concentration is part of the composition holdout design. A2_alt U+ is also concentrated: 72% use `glass` or `cup`. Query word counts and top action/object frequencies by test quadrant are in [`test_query_distributions.json`](../semantic_existence_v2_metrics/test_query_distributions.json); exact text-only results are under [`text_only/`](../semantic_existence_v2_metrics/text_only/).

## Limits

Each configuration has one seed. Cross-split comparisons use separately trained checkpoints and change S+ training composition; comparisons are associations, even though they hold the test query constant. Semantic gaps are not uniform in size and the models have different failure modes. The composition groups cover a narrow object range. Negative and parser review provenance is a dataset-owner global attestation for the exact reviewed batches, not per-query or dual-review logs. These results support a repeated failure pattern on this Charades-STA benchmark, not a universal claim across video domains.
