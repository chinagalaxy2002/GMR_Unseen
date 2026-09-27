# Semantic Existence v1：主要实验方案与进度

> 进度快照：2026-09-27 15:40 CST。Moment-DETR-GMR、FlashVTG-GMR 与补充的 QD-DETR-GMR 均已完成单种子训练和完整测试。原始方案见 [`data/release/semantic_existence_v1/plan.md`](../../data/release/semantic_existence_v1/plan.md)。

## 研究问题与实验协议

目标是检验：只在已见语义上学到的时刻定位和存在判断，能否在未见语义中区分目标真的存在（U+）与真的缺席（U−）。本轮先运行主要实验 **E2–E5**，每个模型只用一个种子；定位-only 对照、semantic-seen oracle 与多种子实验暂未运行。

| 阶段 | 数据 | 用途 |
| --- | --- | --- |
| 训练 | `train.jsonl`：S+ 6,851；S− 1,466 | 训练定位与 existence head；没有 U+/U− |
| 选择 checkpoint、校准阈值 | `val_seen.jsonl`：S+ 694；S− 168 | 只使用 seen 验证样本；不查看 val U+/U− |
| 最终测试 | `test.jsonl`：S+ 2,090；S− 592；U+ 881；U− 947 | 四象限结果、官方 GMR 指标 |
| 配对诊断 | `matched_u_pairs.jsonl`：535 对 | 同视频、同来源正例的 U+/U− existence 排序 |

主模型分别是 Moment-DETR-GMR（seed 2023）与 FlashVTG-GMR（seed 2024）。模型的任务特定参数从头在上述训练集学习，没有用完整 Charades-STA 微调过的定位 checkpoint 初始化。视频采用已有的 Charades CLIP + SlowFast 特征，约 1 秒一个特征；原始正句采用已有 CLIP 文本特征，改写负句用同系列 CLIP ViT-B/32 编码。14,345 条发布样本的 query 特征与 5,449 个视频的两类特征均已核对齐全。

每个 GMR checkpoint 保留不经过 existence 判定的候选时刻分数及 existence 分数。诊断阈值由 seen 验证集上最大化 balanced accuracy 确定，再固定用于测试。报告指标包括 S+/U+ 的错误拒绝率、S−/U− 的拒绝率、seen 与 unseen AUROC、U+ 原始 R@1@IoU 0.5、拒绝后 R@1@IoU 0.5，以及 matched-U PairAcc。这里的“拒绝后 R@1”表示低于校准阈值时输出空集，是诊断用的硬拒绝；官方 GMR 指标单独计算，不能与它混用。

## 当前进度

| 实验 | 状态 | 当前产物 |
| --- | --- | --- |
| E2 Moment-DETR-GMR | **完成**。训练到第 12 个 epoch，依据 seen 验证 mAP 连续 8 个 epoch 未提升而早停；最佳 seen 验证 mAP 为 25.66% | [`best.ckpt`](../results/semantic_existence/moment_detr_gmr/best.ckpt)、[`val.log`](../results/semantic_existence/moment_detr_gmr/val.log) |
| E4 Moment-DETR-GMR raw / gated 与四象限测试 | **完成**。完整 test、535 对配对诊断及官方 GMR 指标均已生成 | [`diagnostics.json`](../results/semantic_existence/moment_detr_gmr/diagnostics.json)、[`official_test_metrics.json`](../results/semantic_existence/moment_detr_gmr/official_test_metrics.json) |
| E3 FlashVTG-GMR | **完成**。单种子训练至第 30 个 epoch；最佳 checkpoint 来自第 21 个 epoch（零起始序号 20），依据 seen 验证 R@1@0.5 与 R@1@0.7 的平均值选定 | [`flash_training_resume_fixed.log`](../results/semantic_existence/flash_training_resume_fixed.log)、`results/semantic_existence/flash_vtg_gmr/charadesSTA-video_tef-seen_only_seed2024_resume_fixed-2026-09-27-14-10-34/model_best.ckpt` |
| E5 FlashVTG-GMR raw / gated 与四象限测试 | **完成**。完整 test、535 对配对诊断及官方 GMR 指标均已生成 | `results/semantic_existence/flash_vtg_gmr/charadesSTA-video_tef-seen_only_seed2024_resume_fixed-2026-09-27-14-10-34/diagnostics.json`、同目录 `official_test_metrics.json` |
| 补充 QD-DETR-GMR | **完成**。训练 30 个 epoch；最佳 checkpoint 来自第 27 个 epoch（零起始序号 26），依据 seen 验证 mAP 选定；完整测试已运行 | [`diagnostics.json`](../results/semantic_existence/qd_detr_gmr/diagnostics.json)、[`official_test_metrics.json`](../results/semantic_existence/qd_detr_gmr/official_test_metrics.json) |

FlashVTG 首个 epoch 后遇到当前环境的 AdamW `foreach` 兼容错误；已关闭该优化路径，并从首个 epoch 的完整 checkpoint（模型、优化器、调度器）以**同一种子**继续训练。这是一次训练续跑，不是额外种子。此前一次初始化重试在训练前结束，也未产生独立实验结果。

## 已完成的 Moment-DETR-GMR 结果

校准阈值为 `pred_exist_score = 0.8802`，只由 seen 验证集确定。以下百分比来自测试集：

| 指标 | S+ | S− | U+ | U− |
| --- | ---: | ---: | ---: | ---: |
| 数量 | 2,090 | 592 | 881 | 947 |
| 错误拒绝率 / 负例拒绝率 | 27.42% | 79.73% | 23.04% | 23.86% |
| 原始 R@1@IoU 0.5 | 31.82% | — | 34.62% | — |
| 拒绝后 R@1@IoU 0.5 | 24.11% | — | 27.58% | — |

- Seen AUROC（S+ 对 S−）：**0.8413**；unseen AUROC（U+ 对 U−）：**0.5712**，差 **0.2701**。
- Matched-U PairAcc：**64.49%**，共 535 对。配对排序有信号，但远非可靠区分。
- U+ 与 S+ 的错误拒绝率差：**−4.37 个百分点**。本模型在整体 U+ 上没有出现方案预期的“新语义过度拒绝”。
- 主要失败表现是 **U− 被误判为存在**：U− 平均 existence 分数为 0.905，与 U+ 的 0.904 很接近。按新颖性类型看，882 条 unseen-action U− 仅约 21.4% 被拒绝，65 条 unseen-composition U− 约 56.9% 被拒绝。这是描述性拆分，后者样本较少。
- 官方完整 test 指标：AUROC **67.81%**、G-mIoU@1 **23.55%**、mAP **25.48%**。官方指标使用其自身定义与默认分类阈值，和上面的 seen 校准阈值诊断分开解读。

因此，当前证据支持“seen existence 无法稳定迁移到 unseen existence”，但**不支持**把 Moment-DETR-GMR 的主要问题写成 U+ 过度拒绝。是否有模型依赖的过度拒绝现象，需要等 FlashVTG-GMR 的最终测试结果。

## 三模型测试对比与核查

| 模型 | Seen AUROC | Unseen AUROC | S+ FRR | U+ FRR | U− 拒绝率 | U+ raw → 拒绝后 R@1@0.5 | Matched-U PairAcc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Moment-DETR-GMR | 0.841 | 0.571 | 27.4% | 23.0% | 23.9% | 34.6% → 27.6% | 64.5% |
| FlashVTG-GMR | 0.888 | 0.615 | 15.6% | 50.4% | 64.8% | 37.3% → 18.6% | 49.7% |
| QD-DETR-GMR | 0.861 | 0.592 | 17.6% | 51.9% | 64.1% | 31.0% → 15.2% | 49.1% |

QD-DETR 的训练与测试口径已核对：`best.ckpt` 为零起始第 26 个 epoch，训练仅使用正式 S+/S−，选模仅使用 862 条 seen 验证样本；模型启用 existence head，负例进入训练并贡献 `loss_exist`。最佳验证与测试预测分别完整覆盖 862/4,510 个互异 qid，诊断文件可由统一脚本逐字节复算。其模型包含 QD-DETR 的 query-dependent transformer，而非将 Moment-DETR 结果改名。三模型均未用完整 Charades-STA 的任务微调 checkpoint 初始化。

FlashVTG 和 QD-DETR 都出现明显的 U+ 额外错误拒绝；Moment-DETR 的主要问题则是 U− 误接受。三者共同说明 seen 上学到的 existence 判断不能稳定迁移到未见语义，但不应把所有模型的错误都概括为“过度拒绝”。当前三组训练均结束，因而无需开启 `tmux` 续训；后续可补定位-only 对照 E0/E1，本轮不做多种子。

复现入口：[`prepare_charades_semantic_existence.py`](../scripts/prepare_charades_semantic_existence.py) 准备 seen 验证视图与文本特征；[`analyze_semantic_existence.py`](../scripts/analyze_semantic_existence.py) 计算四象限和 matched-U 指标。原始发布数据及统计见 [`HANDOFF.md`](../../data/release/semantic_existence_v1/HANDOFF.md)。
