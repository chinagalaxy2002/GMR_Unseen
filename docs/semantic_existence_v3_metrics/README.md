# Semantic Existence v3 baseline degradation

[完整 baseline 退化报告](../reports/semantic_existence_v3_baseline_results.md) 汇总五个划分、三个 backbone、15 次 seed=3407 训练及五划分宏平均，仅包含原生 baseline。

- [当前审核版数据](../../data/release/semantic_existence_v3/)：每组 Test=4,622，负例重审已应用；正例全量审核进行中。
- [与已有 baseline 对应的实验快照](../../data/release/semantic_existence_v3_baseline_snapshot_20261009/)：每组 Test=4,999，结果来自此快照。
- [JSON 指标](baseline_metrics.json)、[CSV 指标](baseline_metrics.csv)、[Bootstrap CI](baseline_bootstrap_ci.json)、[发布版本说明](publication_info.json)。

| Backbone | Seen AUROC | Unseen AUROC | Gap (pp) |
|---|---:|---:|---:|
| Moment-DETR-GMR | 0.7699 | 0.5854 | 18.46 |
| QD-DETR-GMR | 0.7916 | 0.5498 | 24.18 |
| FlashVTG-GMR | 0.7921 | 0.5313 | 26.07 |

These baseline numbers apply to the initial experiment snapshot. They are not retraining results for the current reviewed release. Bootstrap CIs use 500 fixed-model test-video cluster draws; G-mIoU uses the first valid submitted native window without duration-bound skipping.
