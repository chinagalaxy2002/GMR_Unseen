# Semantic Existence v3 — current reviewed annotations

Revision: `negative-full-audit-20261009-1`. Status: `negative_reaudit_applied_positive_reaudit_in_progress`. Negative re-audit has been applied; positive full semantic audit remains in progress according to this release record.

The master pool contains 15,076 positive qids and 2,869 reviewed negative qids. All 6,976 legacy negative candidates have decisions: keep 2,869, exclude 1,005, quarantine 3,102. Train contains S+/S− only, with one shared video split assignment across groups.

## Groups and current counts

| Group | Held semantics | Train | Val | Seen Val | Test |
|---|---|---:|---:|---:|---:|
| A1_v3 | physical placement / taking | 9,791 | 1,516 | 1,246 | 4,622 |
| A2_v3 | drink / pour | 10,827 | 1,516 | 1,419 | 4,622 |
| A3_v3 | run / walk | 10,783 | 1,516 | 1,418 | 4,622 |
| C1_v3 | sit × bed, chair, couch | 10,845 | 1,516 | 1,358 | 4,622 |
| C2_v3 | open / close × box, cabinet | 10,951 | 1,516 | 1,445 | 4,622 |

## Baseline results and version relationship

[Baseline degradation report](../../../docs/reports/semantic_existence_v3_baseline_results.md) and [baseline metrics](../../../docs/semantic_existence_v3_metrics/) report the existing initial-snapshot experiments. Their exact annotation snapshot is [`../semantic_existence_v3_baseline_snapshot_20261009/`](../semantic_existence_v3_baseline_snapshot_20261009/). Those experiments have 4,999 test queries per group; this current reviewed release has 4,622. Existing results are not results from retraining on this revision.

## Review and lineage

`negative_review_update.json`, `release_info.json` and `review/` record decisions, exclusions, quarantines and corrections. The negative replacement keeps 2,869 of the original 3,585 released negatives and removes 57 excluded and 659 quarantined records. Shared S− training pools contain 1,016 action-axis and 836 composition-axis negatives.

A1 also includes semantic revision `a1-semantic-repair-20261009-1`. Original positive queries, existence labels and windows are preserved by these revisions. Negatives rely on reviewed event distinctions and same-video positive-GT conflict checks under the construction assumption; no per-item video review is claimed.

Each split includes `train.jsonl`, `val.jsonl`, `val_seen.jsonl`, `test.jsonl`, metadata, matched-U pair index and expanded matched-U query records. Actual counts are in `statistics.json` and `semantic_inventory.json`.
