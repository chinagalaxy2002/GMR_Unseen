# 下一项：候选排序、分类置信度与时间窗几何诊断

状态：completed，2026-10-01T01:33:10.709845+08:00。用户已明确授权并实际完成限定零训练诊断。结果见[REPORT](../candidate_geometry_analysis/REPORT.md)，独立核验及原资产hash通过。以下保留执行前任务定义；不作为重复运行或训练授权。

## 与总目标的联系

根plan/EXPERIMENT_PLAN.md的目标仍是GMR未见存在AUROC与raw R1@.5共同改善，官方gated为关键最终表现，seen/FRR/RR护栏保持；独立正例VTG用于判定定位迁移范围。现阶段没有候选联合改善证据。本任务要区分候选级分类排序问题与时间窗几何缺失问题，并判断是否存在可同时服务存在和定位的支持证据；不能用oracle覆盖或定位单项诊断代替共同收益。

## 范围与输入

- 固定A1/QD、seed3407、throw/open_close/sit三个baseline的原seen-only best；seen与training-side pseudo均分析，不读取正式真实U/test。Throw/open_close完成100轮；sit停止于77轮账本，best编号11（0-based），不补训练。
- 原预测、checkpoint、阈值、官方gate、GT、特征、旧结果只读；不重新选epoch/阈值，不拟合质量头、probe或排序模型，不启动干预训练。本任务优先只读已保存预测，通常不需要GPU。
- 对齐预测与GT用qid并核对vid，核验来源hash与行覆盖。原pred_relevant_windows_pre_exist列表已按原精度分数排序后保存：保留列表顺序定义rank，不因四位小数ties自行重排。
- readout_analysis/*_native.jsonl中的native_foreground_slot_probabilities按decoder slot顺序，而保存时间窗按score排序。没有显式slot↔window映射时不得直接按数组index拼接。已有保存窗中的score足以做初步诊断；若必须补映射，先记录必要性并冻结新的无更新前向，不覆盖旧产物。

## 执行前冻结

建立独立candidate_geometry_analysis/，写FREEZE.json：固定模型/预测/GT路径及hash、qid覆盖、指标定义、seed3407、1000次共同原视频bootstrap、训练更新0、与已有分析的关系。明确这项是看过前轮结果后选择的探索性分析，不伪装预登记的确认性检验。代码可放阶段code/新独立模块；不要修改或运行旧队列入口。

## 按顺序回答的问题

1. **正确候选的rank在哪里？**
   在原S+窗上计算每候选对已有GT的最大IoU；IoU=.5为主要诊断，.7辅助。固定K=1,2,3,5,10（不足10候选报告真实覆盖），报告任一top-K候选正确的覆盖和第一正确候选rank分布，无正确候选单列。K=1必须复现原raw R1@.5，K=10必须复现前轮oracle-any-candidate；报告从K=1到K=2/3/5的新增覆盖。这是GT依赖的候选覆盖，不是可实现方法性能或真实reranker收益。
2. **分类置信度是否区分同一query的正确/错误候选？**
   只在同时存在IoU≥.5与IoU<.5候选的S+ query内比较原foreground score，ties记.5。报告query内PairAcc、score与IoU的相关性、top1与最高IoU候选的score gap，score ties和零方差/不可用比例。按query与视频给覆盖，不把slot、candidate pair或query组合视为独立样本。只用窗口附带score作排序诊断，不把video-level存在分数当slot质量。
3. **错误是否来自窗几何？**
   固定三类：top1正确；top1错误但任一候选正确；全部候选错误。以与每个分析窗最大IoU的原GT为诊断对应，记录并列匹配规则。比较top1与最高IoU候选的中心误差/GT长度、预测/GT长度比、起止误差及最大IoU；最高IoU匹配仅作oracle诊断。GT长度>0才计算归一化比率，异常单列，不制造窗口外absent标签。连续量报告分布/分位数，不后看结果挑切点。
4. **Seen与pseudo的差异是否一致？**
   三族逐族报告，同视频bootstrap权重用于所有族和split；等权族汇总，不挑族或按对数加权。Seen与pseudo不是同一组query，差异只作描述，不能称为同样本paired因果变化。Sit截断训练的限制单列。

## 统计与解释

1000次、seed3407、探索性95%区间，不进行确认性多重终点通过判定。涉及同query/candidate/同视频的统计需先明确聚合目标：优先每query摘要后每视频聚合；可附组合对加权结果，但要给分母并与query等权区分。共享原视频用一次联合抽样的共同乘数；零分母/无混合候选的replicate为不可用，报告有效次数，不能填.5。若做相关性，ties与零方差处理显式记录。

高oracle覆盖不证明视觉判断可靠，不承诺可以学出oracle；排序质量关联不证明任务冲突；窗几何偏移不自动解释存在AUROC。GT依赖rank/匹配不能进入实际无GT推理。原主要终点与冻结界限不调整。

## 交付与进入门槛

产物建议：FREEZE.json、COVERAGE.json、CANDIDATE_ROWS.jsonl、RESULTS.json、REPORT.md、INTEGRITY.json及独立状态/日志。保存失败与未运行项，不覆盖旧diagnostics/、readout_analysis/或旧报告。完成后更新阶段README、DECISION、progress和HANDOFF；根plan只更新大方向与入口。

报告必须回答：证据更支持分类排序、时间窗几何、二者并存或仍未决？覆盖和跨族一致性如何？与存在判别的共同机制尚缺什么证据？

本任务到诊断与下一步决策为止。只有得到足够机制证据、写清一个具体METHOD_SPEC与普通控制、明确能影响AUROC和raw定位的路径，才讨论新的训练范围；当前不把“后续工作”解释为PCGrad、loss重权、质量头、绝对支持或正式U确认训练。若证据不足就写未决/停止，不通过新增训练替代进入门槛。
