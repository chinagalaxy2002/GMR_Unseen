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
