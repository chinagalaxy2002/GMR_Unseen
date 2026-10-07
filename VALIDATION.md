# 复现验证记录（2026-10-08）

- NumPy 1.24.4，scikit-learn 1.3.2，Python 3.8.20，CPU 运行。
- 五划分训练/验证/测试缓存与官方 JSONL 的 qid、视频、标签、分区顺序核对通过；验证集仅 Seen。
- 15 组 baseline 和 DEC 的 Seen/Unseen AUROC 及 Gap 与独立审计的训练参考 CDF 结果一致，最大绝对误差 0。
- 15 组验证/测试 DEC 分数与历史修正版逐元素完全一致，全部 30 个验证阈值与历史实现完全一致。
- 全部 15 组 native top-1 窗口重新计算 IoU 并通过与原仓库指标实现的数值核对。
- baseline 独立入口的 15 组结果与联合复算的 baseline 逐项一致。
- 加权视频计数 AUROC 与 sklearn 加权 AUROC 对照，最大绝对误差 1.11e-16。
- 2,000 次共享视频聚类抽样均有效。宏平均 ΔUnseen 区间（pp）：Moment [5.68,11.07]、QD [6.98,11.97]、Flash [2.14,7.56]，与历史修正版日志一致。
- 阈值拒绝/定位宏平均与历史日志按两位小数一致；精确数值、逐划分结果及 CI 见 results。

复算无新训练，使用冻结特征及历史原始定位结果；复现范围和限制见 METHOD.md。文件 SHA256 见 data/ASSET_MANIFEST.json，来源文件 SHA256 见 data/SOURCE_MANIFEST.json。
