# 第二阶段上下文恢复交接

核验时间：**2026-09-30T23:41:52+08:00**。本文件是阶段详细恢复入口；动态进度必须结合实际进程、日志与epoch账本，不以本快照或旧PID代替核验。

## 1. 目标与最新用户授权

目标是未见语义的存在排序、接受/拒绝与定位共同改善。用户明确批准第二阶段修订后继续执行，不需重复请求启动批准。三项修订优先于第一版计划：

1. 执行顺序 **D0 → D3 → D1 → D2**，先用已有预测做失败分解，再决定梯度分析预算。
2. 增加训练侧伪未见语义族：固定 **throw、open_close、sit**。后两族从A1原S训练行构造留族视图并从头训练；不能拿见过该族的throw模型当伪未见验证。
3. 共同主要终点 **AUROC与raw R1@0.5**；官方gated R1@0.5为关键最终表现。FRR/RR/raw-correct拒绝率为诊断护栏，不机械要求所有点估计上涨；seen设小幅不劣界限。

数值已冻结在EXPERIMENT_PLAN.md §7：seen AUROC/raw/gated允许下降0.01；FRR增加、RR下降护栏0.03；raw-correct误拒护栏0.05，低分母单列。共同主要终点用97.5%视频paired bootstrap区间，gated报告95%区间与1个百分点不劣护栏。跨界区间为不确定，不当失败或伪装不劣。不能后看结果调整界限。跨族共同视频抽样，逐族报告并等权汇总，不能按结果挑族。

长期约束：A1/QD、seed3407、100epochs、每卡最多两个任务；不做多seed或同预算核验。不恢复75组、其他正式划分/骨干、教师、旧window、Witness/ROI或专属四元组训练。不新增目标U信息和跨视频absence标签，原发布数据/特征/框架/旧结果只读。第二阶段新增训练侧语义族已获得本次用户明确授权，旧“不得新增开发划分”不再阻止此项。

## 2. 文件组织与阅读顺序

工作根：`/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization`。

1. 根plan/HANDOFF.md和plan/EXPERIMENT_PLAN.md：只保存研究方向与阶段入口。
2. 本阶段plan/EXPERIMENT_PLAN.md：修订后详细假设、矩阵、进入和停止规则。
3. 本阶段plan/progress.md：实际完成项与待办。
4. 本文件与plan/HANDOFF_STATUS.json：上下文恢复快照。
5. 文献依据：`../2026年9月30日_正则化与残差适配的未见动作泛化实验/plan/LITERATURE_REVIEW.md`。原根plan内容已经归档到第一阶段，不再读旧路径恢复执行。

第一阶段六组训练、评测与报告均完成，目录名以用户重命名后的中文路径为准；旧名字20260930_A1_QD双轨对照实验已不用。其结果不支持GMR共同改善，adapter仅在正例VTG上提升。第一阶段原runs目录仍在根runs/，不重跑、不挪动checkpoint。

## 3. 当前实时快照

调度器PID **167959**，queue_state.state=running。tmux `correspondence_phase2`，socket位于工作根 `cache/runtime/phase2.sock`，检查方式：进入cache/runtime后运行 `tmux -S phase2.sock ls`。默认tmux socket不属于本阶段。

| 训练侧伪未见族 | 已完成epoch | 状态 | 训练PID（恢复时重核） |
| --- | ---: | --- | ---: |
| sit | 15/100 | training | 167965 |
| open_close | 21/100 | training | 167964 |

核验时GPU0运行open_close baseline、GPU1运行sit baseline，两者CUDA进程真实存在。两个result.json均尚未生成，因此训练和pseudo评测均尚未完成。throw已有模型复用，不在后台重新训练。

## 4. 已完成诊断及解释边界

本阶段diagnostics/下有视图hash、覆盖manifest、throw baseline/adapter的FAILURE_DECOMPOSITION.json、VISUAL_INCREMENT.json、CONTROLLED_QUERY.json、GRADIENT_RELATIONS_best/latest.json。梯度诊断training_updates=0。

Throw baseline的464个pseudo正例：340个raw错误、109个raw正确且接受、15个raw正确但被诊断硬阈值拒绝；106负例中92个错误接受。95.8%的hard失败来自raw定位错误，所以D2降低为16batch筛查。官方soft gate的raw正确→gated错误为6条，另有7条反向变化；**不能把诊断硬拒绝15条说成官方gate完全否决**。

同query字符串的原缓存并不完全一致，已用共享canonical缓存特征及mask作控制：10个query组、36行、37个跨视频正负配对。Baseline PairAcc=.2568，95%视频endpoint区间约[.0294,.5233]；adapter=.5135，区间[.1713,.8502]。覆盖少、区间宽，目前不能宣称证明视觉判断能力。现有结果没有触发复杂方法。

D2已分析throw baseline与adapter的best/latest。Baseline best选在epoch100，与latest相同，不能把它们算两个独立训练阶段。Adapter best为epoch14，latest为epoch100。单decoder局部负cosine不证明稳定冲突，更不证明泛化因果。

## 5. 自动流程究竟做什么

- `code/run_phase2.py`：独立队列，fcntl queue.lock防重复调度；启动open_close、sit各一个baseline，从头100epoch，seen-only MR-full-mAP选择best，训练结束自动生成pseudo预测与训练结果。
- 各新族训练完成后，自动按D3→D1同句共享文本控制→D2 best/latest执行；D3的失败占比决定16或64batch。
- Throw的上述诊断已完成。GPU0最多新族训练+throw诊断两个进程；GPU1最多一个进程，符合每卡上限。
- 队列全部正常返回后状态为 **diagnostics_completed_decision_pending**，意为诊断结果等待跨族解释，**不是候选方法、正式评测或最终报告完成**。
- 队列不会自动训练PCGrad、损失重权或复杂方法，不会自动生成DECISION.md。必须按诊断进入规则继续判断。
- D1遮蔽/乱序/CLIP-SlowFast屏蔽辅助敏感性尚未实现/执行，不能把同句控制完成写成全部D1完成。

关键路径：本阶段queue_state.json、queue.lock、console.log、logs/、runs/*/status.json、epochs.jsonl、result.json、pseudo_predictions.jsonl、threshold_frozen.json、diagnostics/。

训练worker为本阶段code/development_worker.py，是旧queue_worker的隔离副本，仅增加显式留族视图和阶段输出路径；原worker与原队列没有修改。seed、100epoch、原头、官方gate、seen选择规则保留。执行配置为plan/EXECUTION_CONFIG.json；启动前冻结为EXECUTION_FREEZE.json；后续梯度元数据修订另记EXECUTION_CODE_REVISION.json，不能把旧freeze当当前唯一源hash。

## 6. 恢复时避免重复和错误重启

先核验实际进程命令行是否含本阶段路径，而非只看PID是否存在。检查GPU、tmux、日志尾部和epoch是否增加。调度器正常运行则沿用，不另开队列。

**当前run_phase2.py不是训练断点恢复器。** 新族运行目录存在且没有result.json时，直接重启会报Incomplete existing run；它也不会接管孤立活着的worker。调度器若退出但训练worker仍活着，先让现有worker继续并核对日志，不重复启动训练；待其完成，再接续诊断。若确实失败，先查明原因、保留失败目录和日志，再实现或安排有记录的恢复/新attempt，不能删目录让队列误认为未启动。

启动命令仅在确认需要且不存在活动或不完整待处理任务后使用：

```bash
/home/guoxiangyu/miniconda3/envs/gmr/bin/python -u \
  '2026年9月30日_存在与定位共同泛化的机制诊断/code/run_phase2.py'
```

工作目录必须为实验根；后台恢复需沿本阶段tmux与追加日志，不覆盖console.log。不要使用根code/launch_queue.sh：它属于已完成第一阶段六组。诊断已有产物重跑会覆盖诊断JSON，必要复算先另存版本。

## 7. 恢复后授权内的继续任务

1. 报告两个新增族的最新epoch、训练和pseudo评测完成情况、进程及失败/阻塞。
2. 正常队列继续；异常先检查再恢复，不重复启动。
3. 核对两族训练完成后各项自动诊断的实际产物与returncode；检查共享文本控制和梯度输出的checkpoint来源、有效batch数、不同epoch。
4. 补充尚未执行的D1辅助敏感性，使用训练侧数据，扰动无新标签，不报告反事实准确率。
5. 汇总三个族失败分解、视觉控制和梯度结果到本阶段report/及DECISION.md。结合覆盖/区间判定支持、未决或否定，不能从throw单族推断全部机制。
6. 若跨族证据满足进入条件，按详细计划冻结一个METHOD_SPEC，再执行有限的普通控制/干预；用户已授权修订后方案继续，常规必要工作无需重复请示。若证据没有出现，停止复杂方法并写清原因，不保证导向某个预想模块。
7. 只有开发主指标与护栏通过，才进入计划限定的正式确认；不以真实U结果挑方法。不自行扩展种子、教师、骨干或正式划分。
8. 细节、日志、结果、计划修订只写本阶段目录；根plan仅更新方向和入口。明确区分训练完成、诊断完成、干预完成、评测完成与报告完成。
