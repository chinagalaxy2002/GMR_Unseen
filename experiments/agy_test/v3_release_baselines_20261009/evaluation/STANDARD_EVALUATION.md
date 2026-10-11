# Clean Semantic Existence v3 baseline evaluation

Completed settings: 15/15. Seed 3407; fresh Seen-only training; native Seen-validation checkpoint selection; threshold maximizes BA over 91 Seen-validation percentiles (5–95), earliest tie. AUROC 0–1; gap in pp. Absolute Unseen AUROC 95% CI: 2,000 video-cluster bootstrap draws, seed 3407; fixed checkpoint and threshold. Macro is equal-weight over all five groups, with shared-video draws. Gains/change/reduction are undefined for standalone baselines and shown as —.

| Evaluation Variant | Seen AUROC | Unseen AUROC | Performance Gap | Unseen Net Gain | 95% CI (Bootstrap) | Seen Change | Gap Reduction |
|---|---:|---:|---:|---:|---|---:|---:|
| A1_v3 / Moment-DETR-GMR / Baseline | 0.7499 | 0.6439 | 10.60 | — | [0.5931, 0.6903] absolute | — | — |
| A1_v3 / QD-DETR-GMR / Baseline | 0.7295 | 0.5586 | 17.09 | — | [0.5104, 0.6075] absolute | — | — |
| A1_v3 / FlashVTG-GMR / Baseline | 0.7530 | 0.6614 | 9.17 | — | [0.6121, 0.7120] absolute | — | — |
| A2_v3 / Moment-DETR-GMR / Baseline | 0.7545 | 0.5075 | 24.69 | — | [0.4570, 0.5559] absolute | — | — |
| A2_v3 / QD-DETR-GMR / Baseline | 0.7239 | 0.5105 | 21.34 | — | [0.4765, 0.5449] absolute | — | — |
| A2_v3 / FlashVTG-GMR / Baseline | 0.7707 | 0.5317 | 23.89 | — | [0.4842, 0.5797] absolute | — | — |
| A3_v3 / Moment-DETR-GMR / Baseline | 0.7571 | 0.4560 | 30.11 | — | [0.3966, 0.5165] absolute | — | — |
| A3_v3 / QD-DETR-GMR / Baseline | 0.7685 | 0.5029 | 26.56 | — | [0.4475, 0.5586] absolute | — | — |
| A3_v3 / FlashVTG-GMR / Baseline | 0.7720 | 0.4650 | 30.70 | — | [0.4065, 0.5225] absolute | — | — |
| C1_v3 / Moment-DETR-GMR / Baseline | 0.6815 | 0.5118 | 16.97 | — | [0.4693, 0.5532] absolute | — | — |
| C1_v3 / QD-DETR-GMR / Baseline | 0.7853 | 0.5775 | 20.78 | — | [0.5258, 0.6305] absolute | — | — |
| C1_v3 / FlashVTG-GMR / Baseline | 0.7895 | 0.6037 | 18.58 | — | [0.5559, 0.6520] absolute | — | — |
| C2_v3 / Moment-DETR-GMR / Baseline | 0.6760 | 0.4926 | 18.33 | — | [0.4149, 0.5722] absolute | — | — |
| C2_v3 / QD-DETR-GMR / Baseline | 0.6992 | 0.5189 | 18.03 | — | [0.4383, 0.6029] absolute | — | — |
| C2_v3 / FlashVTG-GMR / Baseline | 0.6862 | 0.5618 | 12.44 | — | [0.4759, 0.6481] absolute | — | — |
| MACRO / Moment-DETR-GMR / Baseline | 0.7238 | 0.5224 | 20.14 | — | [0.4980, 0.5475] absolute | — | — |
| MACRO / QD-DETR-GMR / Baseline | 0.7413 | 0.5337 | 20.76 | — | [0.5095, 0.5586] absolute | — | — |
| MACRO / FlashVTG-GMR / Baseline | 0.7543 | 0.5647 | 18.96 | — | [0.5394, 0.5906] absolute | — | — |

| Backbone Model | Evaluation Branch | Actual Rejection F1 (Rej-F1) | Overall Rejection Rate (RR) | S+ False Rejection Rate (S+ FRR) | U+ False Rejection Rate (U+ FRR) | End-to-end Localization (G-mIoU@1) |
|---|---|---:|---:|---:|---:|---:|
| Moment-DETR-GMR | A1_v3 / Baseline | 53.92% | 33.29% | 24.54% | 18.12% | 35.44% |
| QD-DETR-GMR | A1_v3 / Baseline | 51.65% | 23.42% | 13.97% | 17.28% | 36.65% |
| FlashVTG-GMR | A1_v3 / Baseline | 55.48% | 37.19% | 25.52% | 31.71% | 42.73% |
| Moment-DETR-GMR | A2_v3 / Baseline | 52.36% | 37.43% | 30.06% | 0.00% | 34.32% |
| QD-DETR-GMR | A2_v3 / Baseline | 47.92% | 43.59% | 38.27% | 6.73% | 33.15% |
| FlashVTG-GMR | A2_v3 / Baseline | 53.87% | 37.04% | 28.98% | 0.00% | 41.04% |
| Moment-DETR-GMR | A3_v3 / Baseline | 52.39% | 38.06% | 30.36% | 6.38% | 34.26% |
| QD-DETR-GMR | A3_v3 / Baseline | 52.05% | 39.38% | 30.76% | 22.13% | 33.70% |
| FlashVTG-GMR | A3_v3 / Baseline | 54.21% | 34.66% | 25.05% | 19.15% | 42.12% |
| Moment-DETR-GMR | C1_v3 / Baseline | 38.59% | 34.01% | 31.41% | 1.41% | 31.06% |
| QD-DETR-GMR | C1_v3 / Baseline | 48.53% | 39.15% | 32.20% | 14.08% | 33.06% |
| FlashVTG-GMR | C1_v3 / Baseline | 51.27% | 42.23% | 33.40% | 31.69% | 40.33% |
| Moment-DETR-GMR | C2_v3 / Baseline | 46.27% | 35.35% | 25.86% | 96.18% | 32.59% |
| QD-DETR-GMR | C2_v3 / Baseline | 47.66% | 44.50% | 34.89% | 97.71% | 33.34% |
| FlashVTG-GMR | C2_v3 / Baseline | 47.47% | 44.61% | 35.37% | 90.84% | 38.31% |
| Moment-DETR-GMR | MACRO / Baseline | 48.70% | 35.63% | 28.45% | 24.42% | 33.53% |
| QD-DETR-GMR | MACRO / Baseline | 49.56% | 38.01% | 30.02% | 31.59% | 33.98% |
| FlashVTG-GMR | MACRO / Baseline | 52.46% | 39.15% | 29.66% | 34.68% | 40.91% |

Rej-F1 = 2TN/(2TN+FP+FN), treating rejection as positive. G-mIoU@1 uses the first valid native submitted window (no duration-bound skip), max IoU / number of GT windows; rejected negatives score 1, rejected positives score 0. Each backbone supplies its own localization. See DATA_AUDIT.json, SOURCE_MANIFEST.json, PROTOCOL.json and per-setting calibration, predictions and bootstrap artifacts.
