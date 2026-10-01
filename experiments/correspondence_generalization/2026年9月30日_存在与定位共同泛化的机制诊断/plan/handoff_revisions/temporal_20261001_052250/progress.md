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

## 最新恢复任务准备（2026-10-01T01:16:27.459511+08:00）

已重写HANDOFF、RECOVERY_PROMPT与HANDOFF_STATUS，新增NEXT_TASK.md，兼顾根研究总计划。下一项零训练候选排序/置信度/几何诊断状态planned，尚未实现或执行；恢复prompt提交后按明确范围直接开展。旧训练停止状态不变。

## 已完成候选级零训练诊断（2026-10-01T01:33:10.709845+08:00）

见[候选报告](../candidate_geometry_analysis/REPORT.md)。固定六组共4878条S+，只读已有窗/GT，新增训练、参数更新与前向均0；1000次seed3407共同原视频探索性95%bootstrap。K1/K10逐组复现原raw/oracle，独立计算核验通过，117个保护资产hash未变。

证据支持**分类排序缺口和窗几何缺失并存**，与存在/定位共同机制仍未决。Pseudo同query候选PairAcc三族.6645/.6984/.5821（视频等权），区间均高于.5；连续IoU关联较弱且跨族不一致。任一候选与top1差距明确，但oracle仍为GT依赖诊断。候选缺失组相对排序错误组GT更短，最高IoU窗过宽、中心偏移更大，seen/pseudo均有描述线索；具体边界方向及seen→pseudo排序变化不一致，不支持直接给出通用几何修复。

原query等权pseudo raw=29.36%、oracle=70.60%保持；主要诊断视频等权为29.89%/69.98%，口径不同不替换旧指标。S+内PairAcc不能证明S+/S−存在判别或因果损失冲突，也没有独立VTG迁移新证据。总目标、冻结门槛与gate保持，不宣称共同成功。继续不进入复杂干预/正式U确认；具体共同机制、METHOD_SPEC、普通控制及新训练范围仍未形成。此次NEXT_TASK已完成，没有自动续跑队列。

## 用户授权的下一步研究已完成（2026-10-01T01:57:22.358463+08:00）

见[支持桥接研究](../support_bridge_analysis/REPORT.md)及[方向评估](../support_bridge_analysis/IDEA_EVALUATION.md)。新增独立代码只分析7345条已有query/原S+/S−，未重跑旧评测，训练/更新/前向均0。完成固定foreground、候选几何一致性、二者乘积及query标量普通控制，1000次seed3407共同视频bootstrap。

新证据区分相对候选排序与存在：max foreground的pseudo等权AUROC=.5037，较原存在读出−.0836；S+内部PairAcc仍.6483。冻结primary p×平均预测窗IoU的等权pseudo AUROC=.5315（差−.0558，97.5%辅助区间[−.0934,−.0214]），raw=26.85%（差−2.51pp，[−4.20,−.69]pp），seen也退化，不能共同成功。保存候选内几何一致性不是已证实事实支持，该具体路线被拒绝，不扫系数挽救。

原缓存同句混合组没有实际文本完全一致组，本项候选视觉控制为NA而非.5；原canonical存在控制独立保留，不能拼接原候选替代。所有7345条候选/配对、完整bootstrap AUC及修复−破坏重构独立核验通过，2219保护路径hash未变。一项JSON序列化失败完整保留，两次冻结定义一致，修复未改统计口径。

按用户“发现充分才新建实验”的条件，**当前未触发新训练目录/训练代码修改**；实际下一步研究及拒绝决策已完成，继续保留存在/定位共同机制未决，不恢复旧队列、不正式U确认、不启用教师/window、多seed、同预算或补sit。冻结门槛、原gate/checkpoint/结果不变，独立VTG没有新迁移声明。
