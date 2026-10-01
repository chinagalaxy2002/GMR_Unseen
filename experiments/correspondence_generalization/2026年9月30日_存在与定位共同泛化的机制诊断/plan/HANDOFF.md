# 上下文恢复：冻结时序表示绝对支持诊断已完成

最新更新：2026-10-01T05:22:50.494368+08:00

先读根plan/EXPERIMENT_PLAN.md → 本HANDOFF → 阶段DECISION最新条目 → temporal_representation_analysis/REPORT.md、FREEZE/RESULTS/VALIDATION/INTEGRITY、POOLING_ROBUSTNESS → progress/HANDOFF_STATUS；NEXT_TASK为已完成的历史候选诊断，不是待执行命令。


## 冻结时序表示绝对支持诊断已完成

用户将问题收束到跨查询可比较的绝对支持，已实际完成[时序表示诊断](../temporal_representation_analysis/REPORT.md)。early mean的pseudo等权AUROC增益+.0271 [.0094,.0438]，但纯文本AUROC=.6264，高于early=.6130；固定实际文本控制未形成跨族稳定视觉判别。memory mean基本没有恢复增益。额外原GT监督的window probe保留相对峰值信号（pseudo峰入GT=.3528、机会率=.2566），但纯视频+TEF也有位置偏置，不能等同文本条件定位；更不能替代raw R1@.5。GTmax对整段S−max有搜索范围不等问题；追加均值诊断在GT已知时三族pseudo AUC=.6241/.6078/.6726，无GT同一读出mean/max仅.5686/.5402。固定实际文本后只有open_close的GTmean PairAcc=.5646 [.5339,.6263]支持有限局部证据；throw/sit未定。相关敏感性均后加探索、单列冻结。

结论：未支持“可靠绝对视觉支持已经在表示中，只需修原存在头”；也不能断言“表示完全没有支持信息”。当前缺口在无GT的局部证据选取、聚合标尺及其跨语义迁移之间，线性容量、监督和控制覆盖仍限制二选一判断。下一步不再围绕候选一致性扫变体；绝对支持场仅为待具体化研究候选，未启动新目标训练。

原模型更新0，新增骨干0；确实拟合18个257参数诊断读出器（合计4626参数），不是所有参数更新0。28370冻结前向query呈现、原train19162、原评估7345、canonical1863；1000次seed3407共同原视频探索95%区间。18次拟合收敛、独立核验通过、18230保护资产hash未变。原gate/阈值/主要指标/旧结果不变，无新raw/gated共同成功，无独立VTG新迁移结论；sit训练仍停止。RaTSG及Learning to Refuse近邻已核验，不能把局部证据判断存在写成首次贡献。详细范围/文献见报告。

本次授权诊断已完成，没有待运行任务。原训练队列保持停止，不启动全模型干预、正式U、75组、教师/window、多seed、同预算核验、第一阶段六组或sit补训练。若未来训练必须先具体化METHOD_SPEC与普通控制，并验证AUROC+raw共同路径，gated、seen、FRR/RR及独立VTG范围仍依原冻结标准。

恢复查看保存产物即可，不重复已完成collect/probe/verify；实现均在code/temporal_representation_*.py。两次失败/主动终止已保留在temporal_representation_failures，未改主统计定义。诊断读出拟合与全模型训练必须分别记账。

---
以下为历史交接，保留既有资产入口与此前决策：

# 上下文恢复交接：候选级诊断已完成

更新：2026-10-01T01:33:10.709845+08:00。NEXT_TASK及用户后来授权的下一步支持桥接研究均已完成；本次新研究未支持另开训练阶段，不重复已有评测/分析，不恢复旧训练。

总目标见[根计划](../../plan/EXPERIMENT_PLAN.md)：未见存在AUROC和raw R1@.5共同改善，gated为关键最终指标，seen小幅不劣、FRR/RR护栏保持；独立VTG界定迁移范围。原冻结门槛不变，探索性95%诊断不能替代97.5%共同主要增益检验。

## 完成状态

第一阶段六组、第二阶段三族评测/机制诊断、固定读出分析及[候选级诊断](../candidate_geometry_analysis/REPORT.md)均完成。Throw/open_close完成100轮；sit停止、77轮训练账本、best 11/latest76，未补训练、未伪造训练result。queue_state/followup_state仍stopped_by_user。

候选诊断只读取三族原seen-selected best的seen/pseudo预测及GT，六组4878 S+，新增训练/更新/前向0。2302原视频共同bootstrap，1000次seed3407；原顺序rank、IoU .5/.7、K1/2/3/5/10、query→video聚合已冻结。K1/K10及逐query原IoU复现；117保护资产hash未变，独立pair/相关/IoU/权重核验通过。没有native slot→保存window的索引拼接。

## 证据与决定

分类排序缺口和窗几何缺失并存。Pseudo同query PairAcc（video等权）throw/open_close/sit=.6645/.6984/.5821，探索95%区间均高于.5，但连续score–IoU相关性跨族不一致。缺失组GT更短、oracle过宽且中心偏移更大，seen/pseudo均有描述支持；具体边界方向和seen/pseudo排序差值不一致。

原query等权pseudo raw29.36%/oracle70.60%保持，新video等权诊断29.89%/69.98%不替换原主要终点。Oracle、GT匹配/rank不能进入真实无GT推理；不能承诺学出oracle，不预设损失冲突。S+内部候选分析没有证明存在判别的共同机制或独立VTG迁移，未形成METHOD_SPEC/普通控制/新训练范围。维持不进入复杂训练及正式U确认。

## 恢复阅读与资产

依次阅读根计划→本交接→[DECISION](../DECISION.md)最新追加→[候选REPORT](../candidate_geometry_analysis/REPORT.md)与RESULTS/VALIDATION/INTEGRITY→NEXT_TASK（完成版，保留冻结定义）→readout报告→progress/HANDOFF_STATUS。原历史交接在handoff_revisions等快照保留。

原资产基目录：throw为根runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1；open_close为阶段runs/open_close_qd_gmr_baseline_s3407_attempt1；sit为diagnostics/sit/baseline/evaluation_bundle（原checkpoint/views链接）。每组原pred_relevant_windows_pre_exist按score排序，native数组按slot顺序，不能无映射拼接。FREEZE内记录输入路径、hash、定义和代码hash。

新产物：candidate_geometry_analysis/FREEZE.json、COVERAGE.json、CANDIDATE_ROWS.jsonl、RESULTS.json、GEOMETRY_CONTRASTS.json、BOOTSTRAP_WEIGHTS.npz、REPORT.md、VALIDATION.json、INTEGRITY.json、state.json、EXECUTION.log。独立实现code/candidate_geometry_analyze.py已有输出防覆盖；不运行其main重做，查看保存产物即可。

## 后续边界

没有待执行训练或正式确认；新工作需明确新范围。不得启动旧run_phase2/run_followup/根launch_queue，不恢复75组、教师/window、多seed、同预算核验、第一阶段六组或sit训练。训练前共同机制、具体METHOD_SPEC和普通控制仍有缺口；不能用新增训练代替诊断证据。当前真实运行核对见candidate_geometry_analysis/RUNTIME_BEFORE.json与RUNTIME_AFTER.json，无本阶段实验进程及GPU计算任务；另有无关目录历史监控，未操作。

## 用户授权的下一步研究已完成（2026-10-01T01:57:22.358463+08:00）

见[支持桥接研究](../support_bridge_analysis/REPORT.md)及[方向评估](../support_bridge_analysis/IDEA_EVALUATION.md)。新增独立代码只分析7345条已有query/原S+/S−，未重跑旧评测，训练/更新/前向均0。完成固定foreground、候选几何一致性、二者乘积及query标量普通控制，1000次seed3407共同视频bootstrap。

新证据区分相对候选排序与存在：max foreground的pseudo等权AUROC=.5037，较原存在读出−.0836；S+内部PairAcc仍.6483。冻结primary p×平均预测窗IoU的等权pseudo AUROC=.5315（差−.0558，97.5%辅助区间[−.0934,−.0214]），raw=26.85%（差−2.51pp，[−4.20,−.69]pp），seen也退化，不能共同成功。保存候选内几何一致性不是已证实事实支持，该具体路线被拒绝，不扫系数挽救。

原缓存同句混合组没有实际文本完全一致组，本项候选视觉控制为NA而非.5；原canonical存在控制独立保留，不能拼接原候选替代。所有7345条候选/配对、完整bootstrap AUC及修复−破坏重构独立核验通过，2219保护路径hash未变。一项JSON序列化失败完整保留，两次冻结定义一致，修复未改统计口径。

按用户“发现充分才新建实验”的条件，**当前未触发新训练目录/训练代码修改**；实际下一步研究及拒绝决策已完成，继续保留存在/定位共同机制未决，不恢复旧队列、不正式U确认、不启用教师/window、多seed、同预算或补sit。冻结门槛、原gate/checkpoint/结果不变，独立VTG没有新迁移声明。
