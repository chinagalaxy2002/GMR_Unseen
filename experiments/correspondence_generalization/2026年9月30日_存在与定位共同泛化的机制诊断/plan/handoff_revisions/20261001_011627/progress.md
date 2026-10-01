# 第二阶段诊断收尾已完成

更新时间：2026-10-01T00:45:36.130365+08:00。

用户停止训练后，重新授权仅评测的收尾：sit保存best/latest评测、三族汇总和更新DECISION。**新增训练为零，原停止状态不变。**

- Throw/open_close已完成训练及原诊断，旧结果保留。
- Sit保留77轮训练账本、best编号11/latest编号76；best评测输出在diagnostics/sit/baseline/evaluation_bundle/，未写原训练result.json。
- Sit的D3失败分解、D1同句控制/辅助敏感性/后处理审计、best/latest D2和完整块梯度已完成；open_close完整块梯度补充已完成。
- 三族共同原视频bootstrap（1000次、seed3407）、逐族指标/拒绝护栏、同句控制、覆盖与梯度汇总已完成。
- 12项任务返回码均0，原56个受保护文件hash未变。无新训练、参数更新、真实U评测或干预。
- 等权同句控制PairAcc=.4573，95%区间[.3706,.5578]；跨族视觉排序仍不充分。各族均未满足跨checkpoint的稳定两共享块冲突线索。
- 最终决定：不进入复杂方法或正式确认。结论是证据不足/未达到进入线索，不是输入无信息或因果冲突被全面否定。

见[DECISION.md](../DECISION.md)、[完整报告](../report/DIAGNOSTIC_REPORT.md)、closeout_state.json、CLOSEOUT_FREEZE.json。停止前及收尾前快照分别保存在user_stop_snapshot/、pre_evaluation_closeout/。

## 后续零训练读出分析已完成（2026-10-01T01:08:15.371159+08:00）

最新用户要求已完成为固定模型分析，见[readout报告](../readout_analysis/REPORT.md)。三模型六数据组的四位小数预测逐条复现；81个受保护原文件hash未变，参数更新0。未启动任何训练或正式U评测。新细节和解释见DECISION追加章节；候选级rank/置信度/几何诊断仅为下一项待定义研究，旧队列不重启。
