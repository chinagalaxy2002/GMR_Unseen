# 存在与定位共同泛化的机制诊断

**训练已结束，已完成仅评测的三族诊断收尾。** Throw/open_close完成100轮；sit按用户要求停止，保留77轮训练账本，seen-only best checkpoint编号11。随后用户批准用保存模型补评测和汇总；本次新增训练为零。

三族诊断未获得充分的跨族视觉条件排序支持，也未达到稳定共享块损失冲突规则；本次不进入复杂干预或正式U确认。Sit仍不标记为100轮训练完成。

- [最终决策及证据边界](DECISION.md)
- [完整三族诊断报告](report/DIAGNOSTIC_REPORT.md)
- [阶段交接](plan/HANDOFF.md)与[进度](plan/progress.md)
- [本次评测任务状态](closeout_state.json)与[资产完整性](report/CLOSEOUT_INTEGRITY.json)
- [冻结收尾范围](plan/CLOSEOUT_FREEZE.json)与[历史实验方案](plan/EXPERIMENT_PLAN.md)
- [逐族诊断产物](diagnostics/)

主要终点AUROC与raw R1@0.5，gated为关键最终指标；冻结的seen与FRR/RR护栏未修改。本报告展示baseline绝对指标，没有候选paired增益或共同改善通过声明。旧queue_state.json/followup_state.json保持用户停止状态，不能据旧交接重启。

## 后续结果：固定模型定位与存在读出分析

用户新授权的零训练分析已完成，见[REPORT.md](readout_analysis/REPORT.md)、[RESULTS.json](readout_analysis/RESULTS.json)及[执行冻结](readout_analysis/FREEZE.json)。发现候选排序错误与候选缺失并存；存在分数不适合充当定位质量代理；原生logit精度没有一致AUROC收益。原主要指标不变，仍不启动复杂训练或正式确认。

## 候选级零训练诊断已完成

[NEXT_TASK](plan/NEXT_TASK.md)已完成，见[候选报告](candidate_geometry_analysis/REPORT.md)、[结果](candidate_geometry_analysis/RESULTS.json)、[独立核验](candidate_geometry_analysis/VALIDATION.json)和[完整性](candidate_geometry_analysis/INTEGRITY.json)。证据支持分类排序缺口与窗几何缺失并存，共同机制仍未决；没有新训练或方法联合收益。117个保护资产hash未变。

最新状态见[交接](plan/HANDOFF.md)及[恢复说明](plan/RECOVERY_PROMPT.txt)。当前没有已授权待运行任务，旧队列继续停止。

## 下一步共同支持研究已完成

用户随后授权继续研究、证据充分时另开实验。已实际完成[原S+/S−支持桥接与普通控制](support_bridge_analysis/REPORT.md)、[方向评估](support_bridge_analysis/IDEA_EVALUATION.md)和[独立核验](support_bridge_analysis/VALIDATION.json)。候选foreground的同query排序信号不能直接替代存在证据；冻结候选几何支持公式共同读出及seen退化，不触发新训练阶段。7345条输出，训练/更新/前向0；2219保护路径未变。共同机制继续未决。
