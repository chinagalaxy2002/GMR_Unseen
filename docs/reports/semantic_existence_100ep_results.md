# Semantic Existence v1：新种子 100 轮实验结果

2026-09-27，项目根目录 `/home/guoxiangyu/paper/Openword/generalized-moment-retrieval`。完整协议、首轮结果和入口见 [`SEMANTIC_EXISTENCE_HANDOFF.md`](../SEMANTIC_EXISTENCE_HANDOFF.md)。本轮三个模型均从头用新种子 **3407** 训练整整 **100 epoch**，早停关闭；训练只用 S+/S−，checkpoint 与 existence 阈值只由 862 条 seen 验证样本确定。三个 `tmux` 任务的 `exit_code` 均为 `0`，Moment/QD 各有 100 条训练日志，Flash 有 100 条训练日志。正式 test 均完整覆盖 4,510 个 qid，最佳验证预测均完整覆盖 862 个 qid；所有 test 预测都含 existence 分数和 raw 窗口分数。

## 训练收敛检查

| 模型 | 前 30 轮内最佳 seen 验证指标 | 完整 100 轮最佳 | 第 100 轮 | 最佳 checkpoint 轮次 |
| --- | ---: | ---: | ---: | ---: |
| Moment-DETR-GMR | mAP 23.74 | mAP 23.74 | mAP 21.84 | 11 |
| QD-DETR-GMR | mAP 23.90 | mAP 24.71 | mAP 22.43 | 66 |
| FlashVTG-GMR | (R@1, IoU .5/.7) 平均 43.88 | 同指标 44.60 | 同指标 42.65 | 60 |

这是**同一种子内部**的验证曲线比较。Moment 的最佳 checkpoint 早于第 30 轮；QD 延长训练使验证 mAP 增加 0.81 个百分点，Flash 的选模指标增加 0.72 个百分点。后两者的晚期最佳轮次说明 30 轮上限可能略早，但验证改进较小，且第 100 轮表现低于最佳轮次。与首轮跨种子对比不能单独识别“训练轮数”的因果作用。

## 正式测试：seen 验证阈值的诊断

FRR 为正例错误拒绝率，RR 为负例拒绝率；raw/拒绝后 R@1 使用同一 checkpoint，拒绝后指标在 existence 分数低于 seen 验证阈值时按空集处理。这是诊断用硬拒绝，和官方评测默认阈值分开。

| 模型 | 阈值 | Seen AUROC | Unseen AUROC | S+ FRR | S− RR | U+ FRR | U− RR | U+ raw → 拒绝后 R@1@0.5 | Matched-U PairAcc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Moment-DETR-GMR | 0.8908 | 0.8665 | 0.5701 | 24.50% | 79.39% | 29.17% | 38.33% | 32.92% → 24.40% | 55.70% |
| QD-DETR-GMR | 0.9960 | 0.8713 | 0.5854 | 23.97% | 83.95% | 63.79% | 80.68% | 30.65% → 11.80% | 48.41% |
| FlashVTG-GMR | 0.9830 | 0.8574 | 0.5588 | 14.64% | 75.00% | 46.42% | 51.53% | 37.34% → 20.32% | 50.75% |

官方完整 test：

| 模型 | Overall AUROC | G-mIoU@1 | mAP |
| --- | ---: | ---: | ---: |
| Moment-DETR-GMR | 69.72% | 26.92% | 23.04% |
| QD-DETR-GMR | 79.22% | 33.48% | 22.29% |
| FlashVTG-GMR | 79.72% | 37.81% | 33.69% |

本轮核心结论：三模型的 unseen AUROC 均比 seen 低约 0.29；同视频 535 对 matched-U 的 PairAcc 仅 48.4%–55.7%。QD-DETR 与 FlashVTG 对 U+ 有明显错误拒绝，Moment-DETR 则仍大量误接受 U−。延长训练并换种子后，这个**存在判断无法稳定迁移到未见语义**的现象没有消失；不能声称所有模型的失败机制相同。由于种子与训练轮数同时改变，首轮和本轮的测试差异不能归因于训练轮数本身。

## 产物

共同前缀：`results/semantic_existence/seed3407_100ep/`。

| 模型 | 最佳 checkpoint | 预测/评测文件 |
| --- | --- | --- |
| Moment | `moment/best.ckpt`（SHA-256 `92731526bdce93d58637c5136508c2cf238f38d350f174e9f63288b1e8c3d90d`） | `moment/best_charades_semantic_existence_val_preds.jsonl`、`moment/test/moment_detr_gmr_test_submission.jsonl`、`moment/diagnostics.json`、`moment/official_test_metrics.json` |
| QD | `qd/best.ckpt`（SHA-256 `0f28c60cb063d0e38f32ff834bea51e670c785222b7f7a0001e94f94a58f82f5`） | `qd/best_charades_semantic_existence_val_preds.jsonl`、`qd/test/qd_detr_gmr_test_submission.jsonl`、`qd/diagnostics.json`、`qd/official_test_metrics.json` |
| Flash | `flash/charadesSTA-video_tef-seen_only_seed3407_100ep-2026-09-27-15-47-28/model_best.ckpt`（SHA-256 `bf9b3a7c5246c43aaf9dcd04bfcf7e208acc652baaf1384141fa2fe293e9a85f`） | `flash/.../best_charadesSTA_val_preds.jsonl`、`flash/test/hl_test_submission.jsonl`、`flash/diagnostics.json`、`flash/official_test_metrics.json` |

训练脚本是 `scripts/run_semantic_existence_100ep_tmux.sh`；三份 `run_metadata.txt` 与 `exit_code` 保留在各模型目录。诊断由 `scripts/analyze_semantic_existence.py` 产生，官方指标由 `eval/eval_main.py` 产生。旧单种子结果仍在 `results/semantic_existence/moment_detr_gmr/`、`qd_detr_gmr/` 和 `flash_vtg_gmr/...resume_fixed.../`，未被覆盖。
