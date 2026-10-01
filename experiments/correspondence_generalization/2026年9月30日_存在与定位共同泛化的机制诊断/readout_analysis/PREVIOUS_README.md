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
