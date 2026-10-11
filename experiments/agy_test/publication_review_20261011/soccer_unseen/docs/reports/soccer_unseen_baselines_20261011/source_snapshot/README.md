# Soccer-GMR-Unseen v1 baseline experiments

数据：`data/release/soccer_gmr_unseen_v1`。五个划分 A1/A2/A3/C1/C2_soccer，各训练 Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR，共 15 组。

后台入口：`background_pipeline.py`。依次执行数据验证、特征提取、覆盖检查、训练、测试和退化汇总。单个视频提取异常时记录视频、关联 qid 和异常堆栈后跳过，继续处理剩余视频，不复用旧特征。`FEATURE_ERRORS_*.json` 保存异常；全部处理结束后 `FEATURE_COVERAGE.json` 汇总缺失。按用户授权，缺失或损坏特征对应的查询从实验标注副本统一排除，随后自动启动训练；原发布数据保留。`FEATURE_EXCLUSIONS.json` 保存原因与 qid，`EXPERIMENT_DATA_COUNTS.json` 和各组 `FEATURE_FILTERING.json` 保存过滤后的实际样本数；三个 backbone 使用同一冻结副本。`BACKGROUND_STATUS.json` 记录当前阶段，`background.log` 保存总日志。

正在运行的提取流程通过 `continue_after_features.py` 完成自动训练衔接，无需重启提取 worker。`AUTOTRAIN_STATUS.json` 记录衔接状态；等待期间每分钟采样 GPU 温度、功率、利用率和显存，保存为 `GPU_TELEMETRY.jsonl`。

特征使用 CLIP ViT-B/32 和 SlowFast 8x8 R50 K400，每 2 秒一段。原始特征只在复现探针的两种模态均满足形状一致、平均余弦相似度至少 0.98 时复用；否则统一重新提取全部视频。文本按完整查询重新编码，相同文本共享特征。全部特征仅写入本实验目录，不改动原文件。

训练仅使用 S+/S−，从头训练，seed=3407，最多 100 epoch，early stopping patience=26。checkpoint 与拒绝阈值仅由 Seen validation 决定。Moment/QD 使用 Soccer 原生配置，batch size 分别为 8/16；Flash batch size=8。采用上一批 baseline 的训练轮次与评测流程，两个 GPU 排队执行。

最终结果位于 `evaluation/STANDARD_EVALUATION.md` 与 `evaluation/GENERALIZATION_DROP_COMPARISON.md`，同时保存 CSV/JSON、预测、冻结 checkpoint、阈值和 2,000 次视频簇 bootstrap。分别报告 Seen/Unseen AUROC、Rej-F1、G-mIoU@1 与 Seen−Unseen gap，保留负 gap；另报整体 Rej-F1、RR、S+/U+ FRR、整体 G-mIoU@1。五个划分全部完成后才计算该 backbone 的五划分 macro。独立 baseline 的相对收益记为未定义。

Rej-F1 和 G-mIoU@1 受子集正负比例影响，不能将其 gap 单独解释为纯粹的语义泛化损失。视频簇 bootstrap 按数据集的视频片段 ID 聚类，不代表整场比赛独立性。

视频特征提取使用 12 个 worker，两张 RTX 3090 各 6 个；可通过 `SOCCER_FEATURE_WORKERS` 调整（1–12）。SlowFast 单次推理 batch size 仍为 4。完整视频列表按 worker 数互斥分片，断点恢复时跳过已完成特征。

进度文件：`FEATURE_WORKER_*.json`、`QUEUE_STATUS.json`；异常见 `FEATURE_ERRORS_*.json` 和对应的 `*.log`。提取结束前不应将任务标记为已开始模型训练。
