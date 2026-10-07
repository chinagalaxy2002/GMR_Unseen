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

## 新增消融与核验

四组消融、修正后的表格与复现命令见 [完整消融报告](MECHANISM_AND_ABLATION_STUDY.md) 和根 README。`ablation_results.json` 是原始完整归档；已核验版本为 [verified_ablation_results.json](../../../docs/cog/ablation_audit/verified_ablation_results.json)。固定规则变体的 1,800 个指标重放一致；逻辑回归 90 项指标中 49 项有差异，排除在已核验结论之外。

```bash
# 不覆盖原始 JSON；当前逻辑回归差异会导致 PARTIAL / exit 1
python experiments/agy_test/co_generalization_gmr/verify_ablations.py
python experiments/agy_test/co_generalization_gmr/render_ablation_report.py
```
