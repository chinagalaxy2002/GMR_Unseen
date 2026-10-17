# Seed 2026 E0 → A3 mechanism experiment handoff

Generated: 2026-10-17T19:49:33+08:00

## Executive summary

This run evaluates whether A3 fixes E0 existence false rejection after localization has already found a GT event. It contains one seed only (`2026`), so all differences are paired descriptive evidence rather than multi-seed uncertainty estimates. E0 is selected by Val native pre-NMS mAP; both EventReadout branches are selected independently by Val raw-logit AUROC. Test is opened only after checkpoint freezing.

The matched control isolates the min-neg increment:

```text
E0 selected localizer
├── EventReadout control: ordinary fine-tuning without min-neg
└── public A3: EventReadout + similarity hard-negative / min-neg
```

Both branches use the same seed, E0 checkpoint, initialization, batch order, optimizer, 100-epoch limit and 23-epoch patience. The negative forward uses a forked RNG, preventing its extra dropout draws from shifting A3's main-path random sequence.

## Frozen results

| model | selected / trained epoch | selection | selected Val score | Test AUROC | Test native mAP | Test G@0.4 | Test G@0.5 | Test G@Val-BA |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| E0 | 32 / 55 | Val mAP | 27.73 | 74.30 | 25.43 | 28.10 | N/A | N/A |
| EventReadout control (no min-neg) | 10 / 33 | Val AUROC | 75.36 | 75.95 | 23.80 | 37.40 | 47.21 | 47.44 |
| A3 | 10 / 33 | Val AUROC | 74.95 | 75.46 | 23.80 | 51.89 | 54.45 | 48.22 |

For A3 branches, `localizer_matches_e0` is `True` for A3 and `True` for the no-minneg control. Thus an existence-mechanism comparison is valid only if both remain `True`.

## Main findings

1. **The matched experiment does not show an AUROC benefit from min-neg.** The no-minneg control has Val/Test AUROC `75.36/75.95`, versus `74.95/75.46` for A3. Therefore this seed does not support the claim that min-neg generally improves global positive-negative ranking.
2. **Min-neg mainly changes the operating scale and rejection behavior.** On selected Val, mean positive/negative scores move from `0.6462/0.3920` without min-neg to `0.4405/0.2444` with min-neg. The Test threshold maximizing G-mIoU@1 shifts from `0.98` to `0.53`, while their maxima are nearly unchanged (`54.71` versus `54.68`). The apparent A3 advantage at conventional thresholds is therefore primarily operating-point alignment, not a higher best-achievable G-mIoU envelope.
3. **Min-neg does improve the intended within-video discrimination diagnostic.** Val same-video macro AUROC changes from `61.98` to `63.81`, and pair-weighted AUROC from `56.39` to `57.48`. This is consistent with the mismatched-query objective, even though global AUROC is slightly worse.
4. **A3 relies more strongly on localized hit-slot evidence after min-neg.** For Top-3 hit queries, final-layer attention mass increases from `0.0551` to `0.0917` and causal hit-slot masking Δlogit increases from `0.0951` to `0.1715`. Attention alone is not treated as causal; the masking change supplies the stronger evidence.
5. **This is not a positive-query rescue mechanism at threshold 0.5.** Among `155` Top-3 hit-positive rows, min-neg alone rescues `0` E0 false rejects, while it changes `45` no-minneg accepts into A3 rejects. The supported interpretation is conservative score calibration plus stronger within-video contrast and hit-slot reliance—not recovery of low-scoring localized positives.

Overall verdict: on seed 2026, EventReadout without min-neg gives the better global AUROC, whereas min-neg makes the head substantially more conservative and moves its useful operating threshold toward 0.5. A3's fixed-threshold G-mIoU improvement is real, but it should not be described as a universal ranking gain or as rescuing E0's positive false rejects.

## Why G-mIoU rises at most practical thresholds

G-mIoU averages all 1,036 Test queries. A correctly rejected negative query has empty prediction and empty GT, so its score is exactly 1. A rejected positive query has empty prediction but non-empty GT, so its score is 0. Consequently:

```text
G-mIoU@1 = correctly rejected negative contribution
          + accepted-positive localization contribution
```

There are 492 negatives, so perfect negative rejection alone contributes `492/1036 = 47.49` G-mIoU points. Because the localizer is unchanged, A3's gain is a gate tradeoff: it earns many more negative-query points while sacrificing some positive-query localization points.

| threshold | model | negative recall | positive recall | negative contribution | positive localization contribution | G-mIoU@1 |
|---:|---|---:|---:|---:|---:|---:|
| 0.4 | E0 | 32.72 | 86.76 | 15.54 | 12.56 | 28.10 |
| 0.4 | no-minneg | 54.88 | 75.37 | 26.06 | 11.34 | 37.40 |
| 0.4 | A3 | 92.07 | 46.51 | 43.73 | 8.16 | 51.89 |
| 0.5 | E0 | 70.93 | 61.40 | 33.69 | 9.88 | 43.57 |
| 0.5 | no-minneg | 78.86 | 60.11 | 37.45 | 9.76 | 47.21 |
| 0.5 | A3 | 98.98 | 40.81 | 47.01 | 7.44 | 54.45 |
| 0.6 | E0 | 85.16 | 52.21 | 40.44 | 8.97 | 49.41 |
| 0.6 | no-minneg | 89.63 | 50.00 | 42.57 | 8.72 | 51.29 |
| 0.6 | A3 | 99.80 | 38.05 | 47.39 | 6.99 | 54.38 |

At threshold 0.5, relative to E0, A3 gains `47.01 - 33.69 = 13.32` points from correct negative rejection and loses `9.88 - 7.44 = 2.44` points from positive localization, for a net gain of about `10.88` G-mIoU points. This is why G-mIoU and Rej-F1 improve even though positive recall declines. A3 beats E0 from thresholds 0.03 through 0.73; beyond that, its already-low score scale rejects almost every positive and it becomes worse. The no-minneg control beats E0 across a wider interval because it improves rejection more moderately without suppressing positives as aggressively.

## What is actually being diagnosed

- **E0 path:** masked mean of final video units, concatenated with the query vector, followed by the native existence MLP.
- **A3 path:** newly initialized sequential cross-attention EventReadout over frozen E0 features. The legacy pooled vector is ignored.
- **Max pooling:** not on either actual path in this configuration. Max-owner values are counterfactual representation diagnostics only and cannot support a causal claim.
- **Hit definition:** one of the first `k` native-ranked windows has IoU ≥ 0.5 with any GT window. No GT-based reranking is performed.
- **False reject:** a positive hit query whose existence score is below 0.4 or 0.5.

## Selected-checkpoint mechanism decomposition

Score deltas below are paired on the same `seed × qid`. Counts at threshold 0.5 describe E0 false rejects rescued first by ordinary EventReadout training or only after adding min-neg. Mask Δlogit is the actual readout-logit reduction after hit-window slots are removed.

| localization set | hit-query rows | E0→no-minneg mean score Δ | no-minneg→A3 mean score Δ | rescued by readout | rescued only by min-neg | no-minneg mask Δlogit | A3 mask Δlogit |
|---|---:|---:|---:|---:|---:|---:|---:|
| Top-1 | 108 | -0.0219 | -0.2210 | 5 | 0 | 0.0769 | 0.1566 |
| Top-2 | 126 | -0.0226 | -0.2263 | 5 | 0 | 0.0808 | 0.1631 |
| Top-3 | 155 | -0.0227 | -0.2208 | 7 | 0 | 0.0951 | 0.1715 |

Interpretation rules:

1. A score increase without AUROC or same-video ranking improvement is calibration, not stronger discrimination.
2. Attention mass is routing evidence, not a causal attribution. The hit-slot masking Δlogit is the causal intervention used here.
3. `E0→no-minneg` combines head replacement and ordinary readout training. `no-minneg→A3` is the matched min-neg increment.
4. A min-neg mechanism is credible when it improves negative separation/rescue and the A3 decision remains causally dependent on hit slots.
5. Test confirms Val-discovered behavior; it must not be mined to select a mechanism claim.

## Top-3 queries rescued only after min-neg at threshold 0.5

_None._

## Top-3 persistent false rejects after A3 at threshold 0.5

| qid | video | E0 | no-minneg | A3 | min-neg Δ | A3 hit-slot mask Δlogit |
|---|---|---:|---:|---:|---:|---:|
| 5477 | WC2022_3857289_2_3260s_3410s | 0.3460 | 0.0880 | 0.0810 | -0.0070 | 0.2309 |
| 2786 | WC2022_3857259_2_4520s_4670s | 0.3000 | 0.1080 | 0.0910 | -0.0170 | 0.3132 |
| 2670 | WC2022_3857286_2_4380s_4530s | 0.3590 | 0.2020 | 0.1020 | -0.1000 | 0.1882 |
| 6079 | WC2022_3857292_1_700s_850s | 0.3550 | 0.1130 | 0.1110 | -0.0020 | -0.0555 |
| 3570 | WC2022_3857286_2_2840s_2990s | 0.2650 | 0.2460 | 0.1170 | -0.1290 | 0.0398 |
| 5660 | WC2022_3857287_1_140s_290s | 0.3380 | 0.1700 | 0.1500 | -0.0200 | -0.0186 |
| 4146 | WC2022_3857259_2_4660s_4810s | 0.4040 | 0.3610 | 0.1520 | -0.2090 | 0.0494 |
| 6236 | WC2022_3857284_1_2100s_2250s | 0.4190 | 0.3310 | 0.1580 | -0.1730 | 0.0752 |
| 535 | WC2022_3857264_1_1540s_1690s | 0.4460 | 0.3030 | 0.1730 | -0.1300 | 0.0431 |
| 5007 | WC2022_3857260_2_3260s_3410s | 0.3250 | 0.2840 | 0.1740 | -0.1100 | 0.0369 |

## Diagnostic inventory

### E0 training and evaluation

- `baseline/runs/E0_s2026/diagnostics/optimization.jsonl`: sampled loss, learning rate and pre-clip norm.
- `baseline/runs/E0_s2026/diagnostics/gradients.jsonl`: sampled existence-vs-localization gradient cosine.
- `baseline/runs/E0_s2026/diagnostics/parameter_updates.jsonl`: module-level epoch updates.
- `baseline/runs/E0_s2026/diagnostics/pool_sources/validation/`: true mean-pool contribution and causal ablation for every Val epoch.
- `baseline/runs/E0_s2026/diagnostics/pool_sources/test/`: frozen Test diagnostic.

### EventReadout branches

- `minneg/runs/no_minneg_s2026/monitor/`: matched control training, score and intervention records.
- `minneg/runs/minneg_s2026/monitor/`: A3 training, score and intervention records.
- Each `pool_sources/validation/epoch_*` directory contains Top1/2/3 hits, false-reject flags, actual attention mass, hit-slot masking, hit-only replay, mismatched-text replay, and separately labelled counterfactual max ownership.
- `selection/trace.jsonl`, `selected.json`, and `selection/frozen.json` document Val-only selection and the Test boundary.
- Exact localizer fingerprints are checked every epoch and during Test.

### Paired reports and figures

- `reports/mechanism/selected_three_way.csv`: principal E0/no-minneg/A3 selected-checkpoint table.
- `reports/mechanism/paired_queries.csv`: E0 versus every A3 epoch.
- `reports/mechanism/epoch_summary.csv`: rescue trajectory.
- `reports/mechanism/MECHANISM_RESULTS.json`: machine-readable mechanism summary.
- `reports/mechanism/mechanism_trajectory.png`: A3 rescue and hit-slot causal reliance trajectory.
- `reports/threshold_sweep_per_seed.csv`: every threshold from 0.00 to 1.00.
- `reports/all_threshold_metrics.png` and `.pdf`: single-seed threshold curves for E0, no-minneg and A3.
- Test prediction hashes and invariant AUROCs: `[{"stage": "baseline", "seed": 2026, "predictions_sha256": "5563a45d48468657246e22699a12f315f5cf4e0d9645aae0bb65a3bd0785be2a", "AUROC": 74.30169476327116}, {"stage": "no_minneg", "seed": 2026, "predictions_sha256": "46775002d6ac387a228bfb98b813bfe98fe0c0b4bb5439a25a2a9c96b9e54364", "AUROC": 75.95068896461024}, {"stage": "minneg", "seed": 2026, "predictions_sha256": "72cda955bbb67e7e8599eda0111155b16bd1466612db5fa693d30a9c923b0fa6", "AUROC": 75.45937201099953}]`.

## Reproduction

From `/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction`:

```bash
/home/guoxiangyu/miniconda3/envs/gmr/bin/python -B pipeline.py
```

The pipeline order is E0 → parallel no-minneg/A3 training → frozen tests → paired mechanism report → threshold sweep → this handoff. Configuration is in `baseline/configs/protocol.json` and `minneg/configs/jobs.json`. Runtime state and exact commands are retained in `PIPELINE_STATE.json`; individual stdout/stderr streams are in `logs/`.

## Scientific limitations

- Only seed 2026 is retained; variance and statistical confidence across seeds are unknown.
- E0 and EventReadout use different selection metrics by design: released E0 Val mAP versus requested EventReadout Val AUROC.
- E0→no-minneg does not separate head replacement from subsequent ordinary fine-tuning. It only separates their combined effect from the additional min-neg effect.
- Slot masking is a post-encoder readout intervention. It establishes reliance of the existence head, not how the frozen localizer originally formed the slot representation.
- Threshold-specific rescue depends on the declared operating point; AUROC and all-threshold curves should accompany any threshold claim.

Reference diagnostics implementation: commit `349becb99cdfba2b23630af9126af0a532506113` on `diagnostics/detr-native-26ep-20261014`.
