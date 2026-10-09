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

## mAP：五划分宏平均

正例原生定位，mAP@[0.50:0.05:0.95]；尚未施加存在拒绝阈值。Seen=S+，Unseen=U+。Gap 为 Seen−Unseen，负数表示 Unseen 更高。

| Backbone Model | Seen mAP | Unseen mAP | mAP Gap (pp) | All mAP | mAP@0.50 | mAP@0.75 |
|---|---:|---:|---:|---:|---:|---:|
| Moment-DETR-GMR | 25.40% | 24.03% | +1.37 | 25.10% | 50.75% | 21.25% |
| QD-DETR-GMR | 25.75% | 26.28% | -0.53 | 25.53% | 51.26% | 21.89% |
| FlashVTG-GMR | 38.34% | 29.60% | +8.74 | 37.44% | 63.28% | 36.69% |

## 拒绝与端到端定位：五划分宏平均

| Backbone Model | Rej-F1 | RR | S+ FRR | U+ FRR | G-mIoU@1 |
|---|---:|---:|---:|---:|---:|
| Moment-DETR-GMR | 56.44% | 47.86% | 37.29% | 39.27% | 37.32% |
| QD-DETR-GMR | 57.65% | 44.72% | 33.79% | 32.84% | 37.17% |
| FlashVTG-GMR | 58.18% | 41.59% | 28.83% | 44.81% | 43.29% |

## Seen / Unseen G-mIoU：五划分宏平均

| Backbone Model | Seen G-mIoU@1 | Unseen G-mIoU@1 | G-mIoU Gap (pp) | All G-mIoU@1 |
|---|---:|---:|---:|---:|
| Moment-DETR-GMR | 38.21% | 30.95% | +7.26 | 37.32% |
| QD-DETR-GMR | 38.34% | 29.00% | +9.34 | 37.17% |
| FlashVTG-GMR | 44.57% | 32.81% | +11.75 | 43.29% |

## 每个划分的完整 mAP 结果

| Evaluation Variant | Seen mAP | Unseen mAP | mAP Gap (pp) | All mAP | mAP@0.50 | mAP@0.75 |
|---|---:|---:|---:|---:|---:|---:|
| A1_v3 / Moment-DETR-GMR | 24.93% | 15.73% | +9.20 | 23.28% | 48.29% | 19.07% |
| A1_v3 / QD-DETR-GMR | 27.57% | 16.62% | +10.95 | 25.60% | 51.55% | 21.65% |
| A1_v3 / FlashVTG-GMR | 40.58% | 23.34% | +17.24 | 37.49% | 62.89% | 37.06% |
| A2_v3 / Moment-DETR-GMR | 23.93% | 21.68% | +2.26 | 23.79% | 49.08% | 19.93% |
| A2_v3 / QD-DETR-GMR | 26.48% | 27.27% | -0.78 | 26.53% | 52.71% | 22.94% |
| A2_v3 / FlashVTG-GMR | 37.67% | 30.02% | +7.66 | 37.18% | 62.80% | 36.50% |
| A3_v3 / Moment-DETR-GMR | 25.65% | 28.18% | -2.53 | 25.82% | 51.88% | 21.75% |
| A3_v3 / QD-DETR-GMR | 24.63% | 30.39% | -5.76 | 25.03% | 49.82% | 21.50% |
| A3_v3 / FlashVTG-GMR | 37.81% | 33.95% | +3.87 | 37.55% | 63.68% | 36.49% |
| C1_v3 / Moment-DETR-GMR | 27.54% | 33.78% | -6.24 | 27.85% | 53.29% | 25.06% |
| C1_v3 / QD-DETR-GMR | 24.36% | 37.77% | -13.40 | 25.03% | 50.18% | 21.55% |
| C1_v3 / FlashVTG-GMR | 37.49% | 33.28% | +4.21 | 37.28% | 63.50% | 36.39% |
| C2_v3 / Moment-DETR-GMR | 24.95% | 20.77% | +4.18 | 24.79% | 51.20% | 20.46% |
| C2_v3 / QD-DETR-GMR | 25.69% | 19.33% | +6.36 | 25.44% | 52.02% | 21.79% |
| C2_v3 / FlashVTG-GMR | 38.14% | 27.42% | +10.72 | 37.71% | 63.51% | 37.00% |
| MACRO / Moment-DETR-GMR | 25.40% | 24.03% | +1.37 | 25.10% | 50.75% | 21.25% |
| MACRO / QD-DETR-GMR | 25.75% | 26.28% | -0.53 | 25.53% | 51.26% | 21.89% |
| MACRO / FlashVTG-GMR | 38.34% | 29.60% | +8.74 | 37.44% | 63.28% | 36.69% |

## 每个划分的完整拒绝与 G-mIoU 结果

| Evaluation Variant | Rej-F1 | RR | S+ FRR | U+ FRR | G-mIoU@1 |
|---|---:|---:|---:|---:|---:|
| A1_v3 / Moment-DETR-GMR | 55.72% | 43.11% | 33.31% | 28.99% | 36.33% |
| A1_v3 / QD-DETR-GMR | 55.96% | 41.29% | 32.82% | 19.97% | 36.19% |
| A1_v3 / FlashVTG-GMR | 57.63% | 37.05% | 23.92% | 31.56% | 43.23% |
| A2_v3 / Moment-DETR-GMR | 55.91% | 55.87% | 46.36% | 36.16% | 36.78% |
| A2_v3 / QD-DETR-GMR | 57.92% | 43.55% | 33.70% | 4.46% | 37.20% |
| A2_v3 / FlashVTG-GMR | 57.25% | 36.11% | 25.77% | 6.25% | 42.76% |
| A3_v3 / Moment-DETR-GMR | 58.50% | 45.21% | 34.24% | 18.99% | 38.94% |
| A3_v3 / QD-DETR-GMR | 59.19% | 43.85% | 32.32% | 19.41% | 37.97% |
| A3_v3 / FlashVTG-GMR | 58.70% | 48.29% | 36.07% | 38.40% | 43.57% |
| C1_v3 / Moment-DETR-GMR | 53.40% | 46.09% | 37.91% | 18.02% | 36.05% |
| C1_v3 / QD-DETR-GMR | 56.20% | 46.03% | 35.94% | 23.26% | 36.90% |
| C1_v3 / FlashVTG-GMR | 56.89% | 40.61% | 28.10% | 52.91% | 42.47% |
| C2_v3 / Moment-DETR-GMR | 58.66% | 49.03% | 34.64% | 94.20% | 38.50% |
| C2_v3 / QD-DETR-GMR | 58.97% | 48.87% | 34.16% | 97.10% | 37.56% |
| C2_v3 / FlashVTG-GMR | 60.42% | 45.91% | 30.28% | 94.93% | 44.39% |
| MACRO / Moment-DETR-GMR | 56.44% | 47.86% | 37.29% | 39.27% | 37.32% |
| MACRO / QD-DETR-GMR | 57.65% | 44.72% | 33.79% | 32.84% | 37.17% |
| MACRO / FlashVTG-GMR | 58.18% | 41.59% | 28.83% | 44.81% | 43.29% |

## 每个划分的 Seen / Unseen G-mIoU

| Evaluation Variant | Seen G-mIoU@1 | Unseen G-mIoU@1 | G-mIoU Gap (pp) | All G-mIoU@1 |
|---|---:|---:|---:|---:|
| A1_v3 / Moment-DETR-GMR | 38.94% | 25.70% | +13.24 | 36.33% |
| A1_v3 / QD-DETR-GMR | 39.77% | 21.63% | +18.14 | 36.19% |
| A1_v3 / FlashVTG-GMR | 46.66% | 29.27% | +17.39 | 43.23% |
| A2_v3 / Moment-DETR-GMR | 37.35% | 29.95% | +7.41 | 36.78% |
| A2_v3 / QD-DETR-GMR | 38.54% | 21.37% | +17.17 | 37.20% |
| A2_v3 / FlashVTG-GMR | 44.57% | 21.35% | +23.22 | 42.76% |
| A3_v3 / Moment-DETR-GMR | 39.58% | 31.07% | +8.51 | 38.94% |
| A3_v3 / QD-DETR-GMR | 38.84% | 27.36% | +11.48 | 37.97% |
| A3_v3 / FlashVTG-GMR | 44.78% | 28.85% | +15.93 | 43.57% |
| C1_v3 / Moment-DETR-GMR | 36.71% | 29.11% | +7.60 | 36.05% |
| C1_v3 / QD-DETR-GMR | 37.07% | 35.12% | +1.96 | 36.90% |
| C1_v3 / FlashVTG-GMR | 42.21% | 45.29% | -3.09 | 42.47% |
| C2_v3 / Moment-DETR-GMR | 38.48% | 38.92% | -0.44 | 38.50% |
| C2_v3 / QD-DETR-GMR | 37.47% | 39.51% | -2.05 | 37.56% |
| C2_v3 / FlashVTG-GMR | 44.63% | 39.31% | +5.32 | 44.39% |
| MACRO / Moment-DETR-GMR | 38.21% | 30.95% | +7.26 | 37.32% |
| MACRO / QD-DETR-GMR | 38.34% | 29.00% | +9.34 | 37.17% |
| MACRO / FlashVTG-GMR | 44.57% | 32.81% | +11.75 | 43.29% |

全部数值对应初始实验快照（每组 Test=4,999），不是当前审核版（每组 Test=4,622）的重训结果。

mAP 与 G-mIoU 的定义不同：mAP 统计正例的原生候选定位质量；G-mIoU 统计阈值后包括正负例的集合输出质量。已有 AUROC/Gap CI 使用 500 次固定模型的视频聚类抽样；新补算 mAP 和修正窗口 G-mIoU 未计算 CI。

[mAP 与定位详细 JSON](baseline_localization_metrics.json)；[计算口径](localization_protocol.json)。
