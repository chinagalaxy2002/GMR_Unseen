# Semantic Existence v3 Balanced baseline experiments

![原 GMR README 的 GMR Adapter 总体方法图](../../../assets/adapter10.png)

*原 [GMR](https://github.com/dymm9977/generalized-moment-retrieval) 方法图：存在判断决定返回定位结果或空集。*

GMR 同时判断事件是否存在并定位其时间窗。我们关注：**训练未见的动作或组合下，存在判断与定位能否共同泛化？** 本实验保留 Clean v3 的语义划分，跨视频补齐负例后重新训练三个骨干；三模型的五划分宏平均 AUROC 仍从 Seen 到 Unseen 下降 **3.52–10.98 pp**，QD 的 U+ 误拒率为 **71.86%**。这些结果表明，在另一种负例构造下仍需同时考察存在判断、真实事件误拒与端到端定位。

Dataset: `data/release/semantic_existence_v3_balanced`. Independent fresh training for five groups × Moment-DETR-GMR, QD-DETR-GMR, FlashVTG-GMR. No warm starts. Seed 3407; maximum 100 epochs, max_es_cnt 26. Checkpoints and rejection thresholds use full Seen validation only; training uses S+/S− only. Native model/optimizer recipe copied from the completed clean-v3 baseline experiments. Three training slots per GPU, two GPUs.

Original clean-v3 data and results are preserved. Added negatives are unverified cross-video pseudo negatives; query features reuse the exact-text donor feature only after SHA256 identity checking, while video features use the target video. Release checksums, validation report, copied split hashes, feature provenance, source hashes and training configuration are retained.

`QUEUE_STATUS.json` shows live training/inference/bootstrap stages. `queue.log` and `groups/<group>/runs/<backbone>/console.log` contain logs. Completion requires `FINAL_EVALUATION_STATUS.json` with `complete: true`.

Results update after each completed evaluation:

- `evaluation/STANDARD_EVALUATION.md`: original branch tables and overall metrics.
- `evaluation/GENERALIZATION_DROP_COMPARISON.md`: Seen/Unseen AUROC, Rej-F1, G-mIoU@1 and all three pp gaps, paired video-cluster bootstrap 95% CIs, subset counts, RR and FRR.
- Corresponding CSV/JSON, frozen predictions, per-setting thresholds and 2,000 bootstrap draws.

Formal macros require all five groups. Negative Seen−Unseen gaps remain improvements. Standalone baseline relative gains are undefined. Rej-F1 and G-mIoU depend on class proportions, including residual Seen/Unseen imbalance in the balanced release. The experiment evaluates the pseudo-negative construction and does not assume label verification or improved performance.

Run in the experiment's tmux session with the univtg Python environment; the runner itself selects gmr Python for Moment/QD and univtg Python for Flash.

<!-- FINAL_RESULT_READER_ENTRY -->

## 最终结果索引（2026-10-11）

全部 **15/15** 设置已完成。下表为五划分等权宏平均；单个训练种子，模型与阈值仅使用 Seen 验证确定。

| Backbone | Seen → Unseen AUROC | Seen → Unseen Rej-F1 | Seen → Unseen G-mIoU@1 |
| --- | --- | --- | --- |
| Moment-DETR-GMR | 0.7253 → 0.6466 | 65.88% → 62.11% | 45.99% → 43.16% |
| QD-DETR-GMR | 0.5445 → 0.5093 | 56.87% → 61.40% | 39.01% → 47.17% |
| FlashVTG-GMR | 0.7706 → 0.6608 | 68.04% → 61.68% | 51.48% → 44.85% |

- [完整三项指标、逐划分 Gap、95% CI 与拒绝/误拒率](evaluation/GENERALIZATION_DROP_COMPARISON.md)
- [存在判断与整体拒绝、定位的标准评测表](evaluation/STANDARD_EVALUATION.md)
- [四套数据统一结果与绝对指标置信区间](../../../docs/gmr_baseline_summary_20261011/RESULTS_WITH_CI.md)

Gap = Seen − Unseen（百分点），保留负值。Rej-F1 与 G-mIoU@1 受子集正负比例影响；独立 baseline 的 Unseen Net Gain、Seen Change、Gap Reduction 未定义。
