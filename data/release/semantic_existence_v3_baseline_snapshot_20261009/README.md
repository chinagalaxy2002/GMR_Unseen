# Baseline experiment annotation snapshot — 2026-10-09

This directory preserves the exact initial v3 annotations used by the 15 completed Seen-only baseline training runs. It contains 18,661 unique qids: 15,076 positives and 3,585 negatives. Each group has 4,999 full-test records.

The current reviewed release is in [`../semantic_existence_v3/`](../semantic_existence_v3/). This historical snapshot predates the A1 semantic repair and the negative re-audit replacement. It must not be described as the final reviewed dataset.

Baseline degradation results: [report](../../../docs/reports/semantic_existence_v3_baseline_results.md); [machine-readable metrics](../../../docs/semantic_existence_v3_metrics/).

Only annotations actually needed for training, Seen validation and full-test evaluation are copied here; features, videos, checkpoints and predictions are not included.

| Group | Train | Val | Seen Val | Test |
|---|---:|---:|---:|---:|
| A1_v3 | 10,019 | 1,615 | 1,312 | 4,999 |
| A2_v3 | 11,274 | 1,615 | 1,492 | 4,999 |
| A3_v3 | 11,309 | 1,615 | 1,514 | 4,999 |
| C1_v3 | 11,248 | 1,615 | 1,455 | 4,999 |
| C2_v3 | 11,553 | 1,615 | 1,546 | 4,999 |

See `snapshot_info.json` for partition and video counts.
