# E0 → A3 机制诊断记录（seed 2026）

本目录归档单 seed 2026 的训练诊断、冻结检查点测试、机制分析结果和原始逐 epoch 诊断记录。它用于解释 E0、普通 EventReadout 微调对照组、公开 A3 三者的差异；这是单 seed 的配对描述性分析，不代表多 seed 统计结论。

## 先看结论

公开 `fintune` 分支定义的 **A3 是 min-neg**：在 EventReadout 微调中启用相似度难负例（`hard_negative: true`）。目录中的 `no_minneg` 是额外增加的控制组（`hard_negative: false`），不是 A3。

在 seed 2026 上，三者的 Test AUROC 分别为 E0 `74.30`、无 min-neg 对照组 `75.95`、A3 `75.46`。因此，这个实验不支持“min-neg 提高全局正负排序 AUROC”的结论。A3 的主要表现是分数整体变低、拒绝更积极：阈值 `0.5` 时 G-mIoU 从 E0 的 `43.57` 提高到对照组的 `47.21`、A3 的 `54.45`；A3 的负例正确拒绝贡献增加 `13.32` 个百分点，同时正例定位贡献减少 `2.44` 个百分点。

min-neg 还提升了 Val 同视频内的 AUROC（宏平均 `61.98 → 63.81`；按正负配对加权 `56.39 → 57.48`），并增强了存在性读取头对命中 GT 的定位 slot 的因果依赖（Top-3 hit 的 mask Δlogit `0.0951 → 0.1715`）。但阈值 `0.5` 下，min-neg 单独救回的 E0 Top-3 命中正例误拒数为 `0`。当前证据更符合“分数校准/拒绝行为改变，并增强局部证据使用”，不足以声称它普遍提高排序能力或解决了正例误拒。

| 实验 | 定义 | Checkpoint 选择 | Test AUROC | Test G-mIoU@0.5 |
|---|---|---|---:|---:|
| E0 | 原始 baseline | Val native pre-NMS mAP | 74.30 | 43.57 |
| EventReadout control | 普通微调，无 min-neg | Val raw-logit AUROC | 75.95 | 47.21 |
| A3 | EventReadout + similarity hard-negative / min-neg | Val raw-logit AUROC | 75.46 | 54.45 |

阈值 `0.5` 下，A3 相对 E0 的 G-mIoU 变化可拆为：正确拒绝负例贡献 `+13.32`，正例定位贡献 `−2.44`，净变化 `+10.88` 个百分点。定位器指纹在对照组和 A3 中均与 E0 一致。

## 文件导航

- [`docs/HANDOFF.md`](docs/HANDOFF.md)：完整实验协议、冻结结果、阈值分解、Top-1/2/3 slot 机制诊断、案例及科学限制。
- [`docs/MECHANISM_DIAGNOSTICS.md`](docs/MECHANISM_DIAGNOSTICS.md)：诊断设计、记录项目和因果解释边界。
- [`reports/mechanism/selected_three_way.csv`](reports/mechanism/selected_three_way.csv)：E0 → 普通微调对照 → A3 的选定检查点配对拆分。
- [`reports/mechanism/paired_queries.csv`](reports/mechanism/paired_queries.csv)：按 query 的机制结果；[`epoch_summary.csv`](reports/mechanism/epoch_summary.csv) 和 [`mechanism_trajectory.png`](reports/mechanism/mechanism_trajectory.png) 展示训练过程变化。
- [`reports/threshold_sweep_summary.csv`](reports/threshold_sweep_summary.csv)、[`threshold_sweep_per_seed.csv`](reports/threshold_sweep_per_seed.csv)、[`all_threshold_metrics.png`](reports/all_threshold_metrics.png)：全阈值指标曲线和数值。
- [`logs/`](logs/)：seed 2026 的 E0、普通微调对照、A3 训练及两个微调分支的测试日志。
- [`runs/`](runs/)：E0、对照组和 A3 的逐 epoch/逐 query 诊断记录；其中包括 pooling/slot 贡献、命中 slot 遮蔽干预、梯度和训练动态记录。
- [`code/`](code/) 与 [`configs/`](configs/)：诊断与训练/评估代码、实验配置；[`source/`](source/) 保存所用评测/模型源码快照。
- [`PIPELINE_STATE.json`](PIPELINE_STATE.json)：自动流程状态与阶段记录。

检查点权重、视频特征缓存和数据集未随诊断包上传。复跑需要按配置提供原始数据及 E0 权重；完整协议见交接文档。全阈值图中的 Test 结果用于报告冻结模型的行为，不用于选择检查点或形成机制假设。
