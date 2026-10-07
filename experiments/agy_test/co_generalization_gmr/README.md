# CoG-Verifier：事件核验与共同泛化

**Idea：给已有 GMR 检索骨干加一道无需额外梯度训练的视频证据核验，尝试少误拒未见真事件、多拒绝未见负事件，并保留正确片段。**

完整方法、所有数字的来源、真实样本逐步计算、结果主表、Bootstrap 区间、已知边界和数据恢复见[本分支根 README](../../../README.md)。

在仓库根目录、数据包已恢复的环境中运行：

```bash
python reproduction/prepare_evidence_calibration.py
python experiments/agy_test/co_generalization_gmr/evaluate_co_generalization.py
python experiments/agy_test/co_generalization_gmr/run_bootstrap_significance.py
```

结果：`benchmark_summary.json`、`bootstrap_significance_summary.json`；已有逐查询预测归档：`runs/{split}/predictions.npz`。当前评估脚本不会重新保存这些 NPZ。CoG 无新训练权重，使用已有骨干与特征。原始报告仅作归档，结论边界以根 README 为准。
