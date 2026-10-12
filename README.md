# GMR Baseline AUROC 退化诊断

本分支保存 Moment-DETR-GMR、QD-DETR-GMR 和 FlashVTG-GMR 的**诊断脚本、实验协议、交接文档与轻量汇总**，用于研究 Seen→Unseen AUROC 下降的机制。

**归档时间：2026-10-13T00:34:57.242920+08:00。训练尚未完成，当前没有完整冻结测试后的性能结论。** 本分支不包含原始逐样本轨迹、NPZ、checkpoint、特征和历史实验大记录；这些继续保留在训练服务器。具体上传文件与 SHA256 见 [快照清单](DIAGNOSTIC_SNAPSHOT.json)。

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

昂贵梯度／逐层／LOO 诊断采用首 batch＋每 50 steps；固定 Seen probe 和全量 Seen validation 每 epoch 记录。完整原始记录保留在服务器，本分支只上传少量摘要。

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

服务器当前队列继续运行，不要重复 launch。文档中的原始数据目录和 PID 是服务器上下文；GitHub 仅提供归档快照。被省略的原始产物不能被表述为已经上传。
