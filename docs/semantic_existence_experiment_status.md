# Semantic Existence v1：主要实验方案与进度

## 2026-09-28 12:29 CST 完成状态

E0/E1 与补充的 QD-DETR 定位-only 对照均完成，结果见 [`semantic_existence_localization_controls.md`](semantic_existence_localization_controls.md)。E2–E5 的三个 GMR backbone 训练、raw/拒绝后诊断早已完成；E7 text-only 诊断及 matched-U 不确定性分析完成。E6 的 Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR 三组 semantic-seen reference 也完成 100 epoch、完整 test 和官方评分，结果见 [`semantic_existence_semantic_seen_reference_results.md`](semantic_existence_semantic_seen_reference_results.md)。因此当前方案的已安排实验**全部完成**；没有启动新增多种子实验。

E6 把 held-out 正例加回后，U+ FRR 降到 2.50%–3.63%，但 U− 拒绝率也降到 2.64%–4.33%。QD matched-U PairAcc 从 48.41% 提高到 70.37%，其 seen 阈值下的 U− 拒绝仍只有 4.33%。这一参考实验不能作为严格 unseen baseline。

## 2026-09-28 01:31 CST 状态

三组定位-only 对照（Moment-DETR、QD-DETR、FlashVTG）均完成 100 epoch 训练、测试与自动评分，四个 `exit_code` 均为 `0`。主结果和按视频聚类的定位损失区间见 [`semantic_existence_localization_controls.md`](semantic_existence_localization_controls.md)。其中 test U+ 的 plain → GMR raw → seen 阈值硬拒绝 R@1@IoU 0.5 分别为 Moment 35.07% → 32.92% → 24.40%、QD 34.85% → 30.65% → 11.80%、Flash 44.27% → 37.34% → 20.32%。

按用户“训练完成即可继续”的最新指示，取消原定 02:54:44 CST 的 E6 启动队列，并于 **01:31:20 CST** 并行启动三组单种子 semantic-seen reference。Moment/QD 共用 GPU 0，Flash 使用 GPU 1。三个训练进程均已进入运行；完成后将由 [`finalize_semantic_seen_references.sh`](../scripts/finalize_semantic_seen_references.sh) 自动执行完整 test 推理和评分。E6 仍属于**运行中**，结果不能提前引用。实际启动时间记在 `results/semantic_existence/semantic_seen_reference_seed3407_100ep/schedule_metadata.txt`。

## 2026-09-27 20:26 CST 后续实验更新

> 2026-09-27 21:57 CST 状态：Moment-DETR 定位-only 对照训练与测试结束，`exit_code=0`；QD-DETR 与 FlashVTG 定位-only 对照仍在运行。E6 三 backbone 定时任务尚未启动。Moment-DETR 定位-only 在 test S+/U+ 的 R@1@IoU 0.5 分别为 34.93%/35.07%；同 seed GMR checkpoint 的原始窗口分别为 31.58%/32.92%。完整对照见 `results/semantic_existence/localization_only_seed3407_100ep/moment/localization_comparison.json`。

已启动单种子（3407）的三个定位-only 对照：Moment-DETR、QD-DETR、FlashVTG。每个模型仅用 6,851 条 S+ 训练、只用 694 条 val S+ 选模，最终仅在 2,090 条 test S+ 与 881 条 test U+ 上计算定位指标。训练上限为 100 epoch，不早停，采用与 seed 3407 GMR 主实验相同的视频/文本特征和相应 backbone 配置；Moment/QD 顺序使用 GPU 0，Flash 使用 GPU 1。入口为 [`run_semantic_localization_controls.sh`](../scripts/run_semantic_localization_controls.sh)，结果目录为 `results/semantic_existence/localization_only_seed3407_100ep/`。训练完成后由 [`watch_semantic_localization_controls.sh`](../scripts/watch_semantic_localization_controls.sh) 自动调用 [`finalize_semantic_localization_controls.sh`](../scripts/finalize_semantic_localization_controls.sh) 评分。当前属于**运行中**，不可作为已完成结果引用；没有启动额外种子。

E6 semantic-seen reference 已在 2026-09-27 21:57 CST 定时：**2026-09-28 02:54:44 CST** 同时启动 Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR，单种子 3407、100 epoch，不早停。它们把 `removed_train_holdouts.jsonl` 的 2,679 条原训练正例加回原有 8,317 条训练样本，共 10,996 条；validation 仍只用 862 条 seen 样本，test 仍是原 4,510 条。训练沿用 [`run_semantic_existence_100ep_tmux.sh`](../scripts/run_semantic_existence_100ep_tmux.sh) 的三模型并行配置，由 [`schedule_semantic_seen_references.sh`](../scripts/schedule_semantic_seen_references.sh) 定时启动，完成后由 [`finalize_semantic_seen_references.sh`](../scripts/finalize_semantic_seen_references.sh) 自动推理与评分。定时元数据和结果目录为 `results/semantic_existence/semantic_seen_reference_seed3407_100ep/`；原先单独为 FlashVTG 设置的“定位结束即启动”队列已取消。E6 **有意让 held-out 语义进入训练**，只能作泄漏语义参考，不能算严格 unseen baseline。与严格 GMR 相比，它同时增加了训练正例数量，因此结果不是单独识别语义新颖性效应的因果估计。

启动时曾生成一个误含 300 条 U+ 的 val 视图，但在首次验证前即停止，未产生可用 checkpoint；该未完成启动的日志留在 `localization_only_seed3407_100ep_aborted_val_leak/`，用于审计。之后已改为仅 694 条 S+ 的 val 视图并重新从头训练。

对已完成的 seed 3407 GMR checkpoint 另做了 matched-U 不确定性分析，输出为 `results/semantic_existence/seed3407_100ep/matched_pair_uncertainty.json`。535 对上的 PairAcc（95% 配对 bootstrap 区间）分别为 Moment 55.70%（51.50%–59.81%）、QD 48.41%（44.39%–52.43%）、Flash 50.75%（46.82%–54.58%）。Moment 的非平局配对符号检验双侧 p=0.0093，QD p=0.4730，Flash p=0.7426。Flash/QD 的预测分数经过输出精度舍入，分别有 81/38 个平局；因此符号检验剔除平局，PairAcc 则将平局计为 0.5。

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
