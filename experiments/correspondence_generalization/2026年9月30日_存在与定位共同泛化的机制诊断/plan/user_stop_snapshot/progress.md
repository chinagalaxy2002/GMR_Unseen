# 第二阶段进度与恢复任务

更新时间：2026-09-30T23:34:38+08:00。用户已批准三项修订后执行，不需要重复请求启动批准。

## 已完成

- 第一版保存在EXPERIMENT_PLAN_v1_before_user_revision.md；新版固定D0→D3→D1→D2。
- 主要指标AUROC和raw R1@0.5，gated为关键最终指标；seen不劣界限1个百分点，FRR/RR护栏3个百分点，raw-correct误拒护栏5个百分点；统计不确定与失败分开。
- 固定throw、open_close、sit三个训练侧族，新增两族原行派生视图与hash；正式数据未改，无真实U读取。
- Throw baseline/adapter的失败分解、共享文本输入的同句跨视频控制及best/latest局部梯度16batch筛查已完成；梯度不做参数更新。Baseline的best与latest均为epoch100，不能作为两个阶段的独立证据。

## 初步结果

Throw baseline：464正例中340个raw错误、109个raw正确且接受、15个raw正确但被诊断硬阈值拒绝；106负例中92个被接受。约95.8%的hard失败来自raw定位错误。官方soft gate的raw正确→gated错误只有6条，另有7条raw错误→gated正确；不能把硬阈值的15条说成官方gate完全否决。

固定相同query输入特征后，只有10个query族、36行、37个跨视频正负配对。Baseline PairAcc=.2568（video endpoint bootstrap95%区间约[.0294,.5233]），adapter=.5135（[.1713,.8502]）；覆盖稀疏，当前不能宣称证明视觉判断能力。

仅decoder出现局部负cosine不足以证明稳定共享层冲突；候选干预尚未启动，等待两个新增族完成后再决策。

## 正在执行与后续

阶段独立调度run_phase2.py已启动，tmux correspondence_phase2，socket cache/runtime/phase2.sock。GPU0训练open_close baseline，GPU1训练sit baseline，均seed3407、100epochs。每卡最多两个进程，现有throw模型不重训。

动态状态看../queue_state.json和../runs/*/status.json、epochs.jsonl，并核对进程。两个训练完成后队列自动执行各族D3→D1同句控制→D2 best/latest，保留失败记录，不自动重跑或启动复杂候选。队列结束为diagnostics_completed_decision_pending，表示诊断产物待跨族解释，不是方法成功。

待办：核对两新增族100epoch训练与pseudo评测完成；汇总三族失败分解和视觉控制；统计独立checkpoint的梯度关系；补D1遮蔽/乱序辅助敏感性（当前未执行）；生成DECISION.md，根据证据决定有限干预或停止复杂方法。候选训练、联合显著性比较和正式U确认均未完成。

恢复时检查实际PID与queue.lock，勿重复启动。失败需查日志后独立记录恢复，不覆盖已有run。旧code/launch_queue.sh不用于第二阶段。

## 清空上下文前核验（2026-09-30T23:41:52+08:00）

open_close已完成14/100epoch，sit9/100；调度器167959与训练167964/167965实际活着，tmux correspondence_phase2正常，各卡一个训练进程，无失败。训练结果与新族pseudo评测尚未完成。详细恢复见[HANDOFF.md](HANDOFF.md)，机器快照为HANDOFF_STATUS.json。

## 本次接手核验与补充（2026-09-30T23:56:57.701677+08:00）

实际调度器167959、worker167964/167965与阶段tmux正常；正常队列沿用，未重复训练或调用旧launch_queue。当前epoch见RESUMPTION_CHECK.json，旧快照数字不作当前进度。

Throw baseline/adapter的D1视频全遮蔽、时间乱序、CLIP/SlowFast分支屏蔽已完成，恒等复算误差0；只报告分数/预测变化，无扰动标签准确率。Latest D3已补，baseline best/latest模型权重完全相同；adapter latest与best不同。新族补充随各族原D2完成后串行执行，独立followup_state.json和tmux diagnostics_followup窗口，不改变主队列。

源码审计发现官方时间裁剪/取整只作用于gated保存窗，raw保存窗未作这一步；因此原raw/gated命中变化不能直接叫gate改top1。保持冻结raw主指标，另存GATE_POSTPROCESS_AUDIT.json做后处理对齐归因。补充代码执行前hash保存在SUPPLEMENT_FREEZE.json。跨族诊断、报告和DECISION仍待新族完成，不预先选择干预。
