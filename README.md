# GMR Baseline AUROC 退化诊断

当前运行：baseline 诊断（不含 QIVR）；每卡最多 2 个运行任务，CG/clean_v3 优先，Soccer 最后运行。暂停的 Soccer 保留原进程状态。


最新已完成任务更新：**2026-10-13T12:49:45.586159+08:00**，已完成 **14/55** 项。新增完成：`charades_cg_v2_C3_CG_qd_with_sa`, `clean_v3_A2_v3_flash_native`, `soccer_A3_soccer_moment_with_sa`。[完整原始记录](https://github.com/chinagalaxy2002/GMR_Unseen/releases/tag/diagnostics-baseline-auroc-completed-20261013-124945) · [更新清单](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013/updates/20261013-124945/MANIFEST.json)。


最新已完成任务更新：**2026-10-13T10:15:33.714689+08:00**，已完成 **11/55** 项。新增完成：`clean_v3_A1_v3_moment_with_sa`。[完整原始记录](https://github.com/chinagalaxy2002/GMR_Unseen/releases/tag/diagnostics-baseline-auroc-completed-20261013-101533) · [更新清单](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013/updates/20261013-101533/MANIFEST.json)。


本分支保存 Moment-DETR-GMR、QD-DETR-GMR 和 FlashVTG-GMR 的诊断脚本、实验协议及训练记录。

最新训练记录快照：**2026-10-13 08:57:24（Asia/Shanghai）**。小型文本日志、配置、逐 epoch 统计和冻结评估结果保留原始目录；完整 JSONL、NPZ 与 bootstrap 数组见 [原始记录归档](https://github.com/chinagalaxy2002/GMR_Unseen/releases/tag/diagnostics-baseline-auroc-records-20261013-085724)。不包含 checkpoint、模型缓存、特征、视频、凭据或重复源码副本。

[下载与恢复说明](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013/RECORDS_README.md) · [原始路径与 SHA256 清单](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013/RECORDS_MANIFEST.json) · [完整统计表](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013/analysis/numeric_statistics_20261013_084613/STATISTICS.md)

`DIAGNOSTIC_SNAPSHOT.json` 记录此前 00:34 的轻量快照；本次上传以 `RECORDS_MANIFEST.json` 为准。训练队列持续运行，上传内容为时间快照。各 split/backbone 分别保存 Seen/Unseen AUROC、Rej-F1、G-mIoU 与 bootstrap CI；已完成五划分宏平均数量为 0。

## 实验范围

| 数据集 | 划分 | 原生 baseline | DETR no-SA 配对 |
|---|---|---:|---:|
| clean_v3 | A1/A2/A3/C1/C2_v3 | 15 | 10 |
| Charades-CG v2 | C3_CG | 3 | 2 |
| Soccer | A1/A2/A3/C1/C2_soccer | 15 | 10 |
| 合计 | 11 个划分、3 个骨干 | **33** | **22** |

每项 fresh initialization、seed 3407、100 epochs；两张 GPU 每卡最多两个训练进程，优先跨数据集／骨干。正式队列不含 QIVR。所有模型参数参与训练，输入 CLIP／SlowFast／文本为预提取特征。

## 研究问题

- 正样本存在分数下移，还是负样本分数上移？原始 logit、概率、舍入和错排分别怎样变化？
- 正确片段是否被定位？top-1、oracle coverage 与存在判别是否脱节？
- DETR query 获得多少真实 GT 匹配，归属是否频繁变化，是否出现重复或相似表征？
- 池化由哪些槽位／时序单元贡献，逐单元移除后存在分数怎样变化？
- 定位、foreground classification 与 existence 的梯度是否冲突？
- 去 decoder self-attention 后增加的是正确覆盖，还是负样本伪响应？

Flash 的定位来自多尺度时序候选，存在头使用查询表征和池化视频表征；它没有 DETR decoder query 或 Hungarian 槽位。跨骨干分析必须保留这一差异。梯度冲突、LOO 与 Gap 分解为诊断证据，不能单独证明因果。

## 协议与报告

仅使用 S+/S− 训练与 Seen validation 选择／校准。选择 Seen validation AUROC 最大的 checkpoint，并列取最早；阈值在 Seen validation 上最大化 BA。冻结 checkpoint／阈值后才评估 Unseen。

**与历史结果的差异：**历史 baseline 按 Seen localization 选择 checkpoint，本轮按 Seen AUROC 选择，固定跑满 100 epochs。因此历史对照差异不能称作新算法收益，也不能称作完全相同选择协议的复现。

最终每个 split／backbone 分别报告 S/U AUROC、实际 Rej-F1、G-mIoU@1 及 signed Gap，overall Rej-F1／RR／G-mIoU、S+/U+ FRR、样本计数及 2,000 次 video-cluster bootstrap CI。SA 对照给 paired CI；Rej-F1／G-mIoU 的 Gap 依赖子集类比例。五划分 macro 仅在五个划分全部完成后成立。

昂贵梯度／逐层／LOO 诊断采用首 batch＋每 50 steps；固定 Seen probe 和全量 Seen validation 每 epoch 记录。完整原始记录保存在同仓库 Release 附件，分支内保存可直接浏览的文本记录与校验清单。

## 文档和脚本

| 入口 | 内容 |
|---|---|
| [交接文档](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/HANDOFF_20261013_BASELINE_FULL_DIAGNOSTICS.md) | 进程、协议、监控、验证与后续工作 |
| [监控说明](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/FULL_BASELINE_MONITORING.md) | 字段、频率与解释限制 |
| [队列配置](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013/SUITE.json) | 55 项配置 |
| [训练状态快照](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013/STATUS.json) | 上传时的队列状态，不是在线状态 |
| [Seen 汇总](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013/FULL_MONITORING.md) | 最近完整 Seen 验证摘要 |
| [调度脚本](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/decoder_suite.py) | 两卡、每卡两个进程 |
| [DETR runner](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/run_decoder_experiment.py) | Moment/QD with/no-SA |
| [Flash runner](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/run_flash_monitor_experiment.py) | Flash 原生时序诊断 |
| [机制监控](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/src/auroc_mechanism_monitor.py) | 分数／LOO／梯度／损失拆分 |
| [槽位监控](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/src/decoder_slot_monitor.py) | DETR query 与 attention |
| [DETR 验证](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/FULL_MONITOR_TEST_RESULTS.json) | 四种组合逐位输出／梯度／RNG 一致、原生损失精确拆分 |
| [Flash 验证](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/FLASH_FULL_MONITOR_TEST_RESULTS.json) | 同类检查通过；16 条历史 Seen logit 差异≤2e-6、set-IoU 一致 |

脚本所需的模型／数据集源码和注册表随分支提供。特征、历史 checkpoint 和数据输入需在本机准备，不能只 clone 后直接运行训练。DETR 的本机环境为 gmr（Torch 2.6.0+cu124），Flash 为 univtg（Torch 2.0.1+cu118）。Flash 使用 SlowFast→CLIP 特征顺序和原生 logit score；DETR 为 CLIP→SlowFast 和原生概率 score，BCE 与概率另存。

服务器当前队列继续运行，不要重复 launch。文档中的原始数据目录和 PID 是服务器上下文；GitHub 仅提供归档快照。本次上传的逐文件范围见 RECORDS_MANIFEST.json。
