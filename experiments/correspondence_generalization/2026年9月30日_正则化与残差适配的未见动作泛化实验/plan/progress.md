# 当前判断、最小实验与任务交接

阶段归档：[20260930 A1/QD双轨实验记录](../EXPERIMENT_RECORD.md)，包含结果、分析、方向决策和产物索引；仅整理记录，无新实验启动。

## 最新核验：六组训练、评测和报告均已完成

核验时间：**2026-09-30T21:31:09+08:00**。本节优先于下方运行中快照；六组范围、seed=3407、100 epoch、不做同预算核验等最新用户约束继续有效。

| 轨道 | 方法 | 已完成 epoch | 训练 | 评测 |
| --- | --- | ---: | --- | --- |
| GMR | baseline | 100/100 | 完成 | 完成 |
| GMR | regularized | 100/100 | 完成 | 完成 |
| GMR | adapter | 100/100 | 完成 | 完成 |
| 正例 VTG | baseline | 100/100 | 完成 | 完成 |
| 正例 VTG | regularized | 100/100 | 完成 | 完成 |
| 正例 VTG | adapter | 100/100 | 完成 | 完成 |

六组各自的 `status.json`、连续 epoch 1–100 的 `epochs.jsonl`、`result.json` 和 `test/report.json` 均已核对；评测记录的 checkpoint SHA-256 与本次运行 `best.ckpt` 一致。`report/records.json` 恰有本次六个正式运行目录，不以开发或历史基线替代本次结果。未执行初始化、batch 顺序或曝光的成对预算核验。

队列于 **2026-09-30 17:58:04（Asia/Shanghai）** 正常完成，`queue_state.json` 为 `completed`，`aggregation_returncode=0`。六组无失败或阻塞；新调度训练/评测日志未发现 traceback/OOM。GMR adapter 沿用旧调度器的活动任务，故其 `attempts=[]`，完成证据以该运行实际产物为准。报告中的三个条件跳过节点是历史 window 开发、teacher L2、teacher KL，均不是六组任务失败；其他正式节点仍取消。

实际本实验调度/训练/评测进程已退出，两张 GPU 无 CUDA 计算任务。`correspondence_six_tasks` 已退出，`cache/runtime/queue.sock` 没有活动 tmux 服务。旧 PID 和 socket 文件仅为遗留记录；与已生成完整产物相符，不属于阻塞。已检查 `code/six_task_queue.py` 与启动入口，**未重新启动队列或重跑任何任务**。

最终报告：[FINAL_REPORT.md](../../runs/autonomous_queue_20260930_strict/report/FINAL_REPORT.md)。机器核验记录：[COMPLETION_VERIFIED.json](../../runs/autonomous_queue_20260930_strict/report/COMPLETION_VERIFIED.json)。训练完成、评测完成、报告完成三者均已确认。

结果：GMR unseen AUROC 为 baseline=.5309、regularized=.4954、adapter=.4771；两种改动均未提升该指标。正例 VTG unseen R1@0.5 为 .2065/.1871/.2624，adapter 比 baseline 提高约 5.59 个百分点，但 GMR 未同步改善，不能据此声称通用对应机制成立。仅限 A1/QD 单 seed，不推断跨划分、架构或种子稳定性。

后续任务：本次授权的自动训练、评测与汇总流程已完成，无待运行任务。保留全部结果、取消与跳过记录；不恢复75组，不新增其他划分、骨干、教师、window、多 seed 或同预算核验。

## 最新用户指令：只运行六组，覆盖下方历史要求

2026-09-30 用户明确取消同预算核验，并将最终训练范围限定为 **A1/QD 的 baseline、regularized、adapter × GMR、正例 VTG，共六组，全部 seed=3407、100 epoch**。其他正式训练和评测全部取消。下方关于“六组不替代75次矩阵”“继续75次训练”“必做同预算核验”的内容仅保留历史，不再执行；不需要扩展其他划分、Moment 或 Flash。

已实际执行范围变更：停止旧调度器，取消运行中的范围外 Moment 任务，保留其部分产物；保留已完成的两组 QD-GMR 与在跑的 QD-GMR adapter。新调度器 [six_task_queue.py](../../code/six_task_queue.py) 已在 tmux `correspondence_six_tasks` 中启动，**每张 GPU 两个并发槽位**，完成六组训练后自动评测、汇总。原启动脚本和旧调度器入口均指向新范围，避免误恢复75组。

| GPU | 当前任务一 | 当前任务二 |
| --- | --- | --- |
| 0 | QD-GMR adapter（沿用原运行） | QD-VTG adapter |
| 1 | QD-VTG baseline | QD-VTG regularized |

QD-GMR baseline/regularized 已完成训练，不重跑。四个训练进程已实际出现在 CUDA 进程列表中，每张卡两个。动态状态见 [queue_state.json](../../runs/autonomous_queue_20260930_strict/queue_state.json)；新调度 PID 核验为126510，但恢复时必须核对实际进程而非依赖旧 PID。188 个范围外正式训练/评测节点标为 `cancelled_by_user`；这是任务节点数，不是188次已运行训练。

同预算核验不再执行：新调度器不调用成对预算审计；新启动的训练关闭参数初始化指纹、batch顺序/逐行曝光核验与逐batch账本。原已经完成及正在运行的任务保留旧记录，不删除历史；这些记录不构成当前已执行成对核验的声明。保留正常训练日志、模型保存、seen-only checkpoint/阈值规则及自动评测。

恢复后的唯一任务：检查六组的训练/评测状态和必要失败重试，等待自动汇总到原 `report/FINAL_REPORT.md`。**不重启旧广矩阵，不追加教师/window，不安排额外诊断训练，不做多seed，不做同预算核验。** 本次修改前状态与配置存于 `runs/autonomous_queue_20260930_strict/scope_changes/20260930_162754/`。

## 以下为缩减范围前的判断与历史记录

更新：2026-09-30；运行状态核验时间：2026-09-30 16:07（Asia/Shanghai）。本文件记录当前判断和下一步任务，须配合 [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md) 使用。状态为时间快照，恢复时重新读取运行文件。

## 1. 清空上下文后的阅读顺序与文件分工

1. [HANDOFF.md](HANDOFF.md)：恢复项目约束、运行入口和历史记录。
2. 本文件 `progress.md`：恢复最新结果、判断、最小实验及继续任务清单。
3. [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md)：核对固定数据、机制门槛、同预算控制、双轨实验和完整验证要求。
4. 按需读 [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md)，核对近邻与新颖性边界。

本文件不是新方案，不替换原计划，不授权新增分支。用户最新要求优先：**未来不进行任何多 seed 实验，只沿本 plan 目录的现有方案继续。唯一训练 seed 为 3407。** 历史文件中的多种子要求不再执行。

此前 [DIRECTION_ASSESSMENT_20260930.md](DIRECTION_ASSESSMENT_20260930.md) 是探索性的方向评估；其中额外诊断建议不是当前必做任务，也没有变成自动队列的新节点。后续最小实验和执行范围以本文件及现有计划为准。

## 2. 已完成工作与当前队列

| 工作 | 核验时状态 | 证据 |
| --- | --- | --- |
| 严格 throw 开发训练 | 完成 100 epoch；训练状态为 training_complete_diagnostics_pending，诊断完成情况以右侧文件为准 | [训练状态](../../runs/qd_throw_strict_diagnostic_20260930/status.json)、[逐 epoch 账本](../../runs/qd_throw_strict_diagnostic_20260930/epochs.jsonl) |
| 阶段诊断 | 1/10/30/100/best 全完成、无失败 | [诊断状态](../../runs/qd_throw_strict_diagnostic_20260930/diagnostics_status.json) |
| Canonical 开发对照 | baseline、regularized、adapter 均完成 | [选择冻结记录](../../runs/autonomous_queue_20260930_strict/SELECTION_FROZEN.json) |
| Window 候选 | 100/best 机制门槛均未通过，开发与正式候选跳过 | [机制门槛](../../runs/autonomous_queue_20260930_strict/MECHANISM_GATE.json) |
| 教师 L2/KL | 来源与同信息预算未通过，跳过；不能称为已训练失败 | [队列配置](../../code/configs/execution_queue.json) |
| 正式训练 | 队列 formal_training；A1 QD-GMR baseline/regularized 已完成训练；A1 QD-GMR adapter 与 A1 Moment-GMR baseline 正在运行 | [动态队列状态](../../runs/autonomous_queue_20260930_strict/queue_state.json) |

核验时 206 个队列节点状态：completed=5、skipped=53、running=2、pending=71、waiting_training=75。completed=5 包含三个开发训练和两个正式训练；**不是五个正式测试结果**。节点还包含评测/门槛，节点数不能当训练次数。

本次只更新文档，没有停止、重启、重排或修改活动队列。恢复时不得因旧交接写着“等待 100/best”而重复运行开发实验。

## 3. 最新结果与当前判断

### 3.1 完整机制诊断

以下为 seen / 训练侧 pseudo-unseen AUROC，不是真实 U test。

| 读出 | Epoch 100 | Seen-selected best（checkpoint epoch=62，零起始索引） |
| --- | --- | --- |
| 原存在头 | .7942 / .5853 | .7848 / .5846 |
| 原输入联合 | .8056 / .4885 | .8056 / .4885 |
| 投影联合 | .7570 / .5728 | .7529 / .5689 |
| 投影文本控制 | .8523 / .7106 | .8486 / .6677 |
| Decoder 均值 | .7168 / .4758 | .7175 / .5922 |

来源：[diagnostic_100](../../runs/qd_throw_strict_diagnostic_20260930/diagnostic_100/metrics.json)、[diagnostic_best](../../runs/qd_throw_strict_diagnostic_20260930/diagnostic_best/metrics.json)。原始机制诊断与 canonical 开发对照的采样 RNG 实现不同，不能相互替代为同预算成对基线。

现有联合探针未通过预登记门槛，不启用 window。失败说明当前测量没有提供启用依据；它不证明冻结输入一定缺少动作信息，也不证明所有对应学习都无效。文本读出较强说明文本中存在可利用的标签线索，不能直接证明原模型实际使用了该捷径。

### 3.2 同预算 canonical 开发对照

三个模型均完成 100 epoch，并依照 seen-only 规则选择 checkpoint。以下只用于恢复已冻结的开发判断，不据真实 U 回调选择。

| 方法 | Seen AUROC | Pseudo AUROC | Pseudo 正例 FRR | Pseudo 负例 RR | Pseudo raw R@1@0.5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | .7996 | .5731 | 8.84% | 13.21% | 26.72% |
| Regularized | .8343 | .5591 | 3.23% | 1.89% | 27.37% |
| Adapter | .8446 | .6000 | 12.07% | 16.04% | 23.49% |

来源：[SELECTION_FROZEN.json](../../runs/autonomous_queue_20260930_strict/SELECTION_FROZEN.json)。FRR/RR 使用 seen 选择的诊断硬阈值，不能当官方 gate 指标。

- Regularized 降低正例误拒，但负例拒绝也下降，不能解释为存在判断共同改善。
- Adapter 的 pseudo AUROC 相对 baseline +.0269，但 raw 定位约下降 3.23 个百分点，正例误拒也增加，尚无明确共同收益。
- `strongest_simple=adapter` 是已冻结的选择结果，**不等于已证明 adapter 有效**。`candidate_formal_enabled=false`。
- 研究问题保留；尚无已验证的新方法。当前先回答普通正则/容量改变能否在正式协议下共同改善存在与定位。

## 4. 当前必需的最小实验：A1 × QD × 三对照 × 双轨

最小首轮判断单元为 **6 次正式训练**，全部 seed=3407、100 epoch。它们均属于原计划和现有队列，不新增方法或骨干。

| 轨道 | 方法 | 数据与输出 | 必须回答的问题 |
| --- | --- | --- | --- |
| QD-GMR | baseline / regularized / adapter | A1 原完整 S+/S−；原存在头和定位头 | 普通正则或容量增加能否改善真实 U 存在判断，同时保住定位？ |
| QD 正例 VTG | baseline / regularized / adapter | A1 原 S+；不设置存在头，不使用 S− | 同样改动离开存在任务后，是否仍改善未见语义定位？ |

开发训练与正式训练使用不同数据视图，开发结果不能抵扣这 6 次正式训练。核验时 GMR baseline/regularized 已完成训练，adapter 在运行；三个 QD-VTG 尚未完成。不要重复启动已完成或运行中的任务。

为什么这 6 次必要：

1. Baseline 提供相同新实现、采样和预算下的参照，不能只依赖历史 checkpoint。
2. Regularized 排除普通防过拟合即可解释的收益；adapter 排除容量与常规适配收益。
3. GMR 与正例 VTG 双轨区分存在任务收益与定位/对应收益。不能仅凭 GMR 的存在分数改善宣称通用对应学习。
4. 开发结果已有 AUROC、拒绝与定位之间的取舍，正式双轨必须联合报告这些变化。

**这 6 次是最小分析单元，不是完整计划的替代，也不是新队列排序指令。** 当前队列依原顺序运行，不因本文件跳过其他任务或提前测试未冻结方案。

## 5. 必做核验与解释规则

不新增 backbone 训练即可完成的必做核验：

- 同一 backbone/split/track/seed 下，检查共同原参数初始化、逐 epoch batch 顺序、更新数、训练行与每行曝光；两个轨道的数据不同，不要求跨轨道曝光相同。
- 模型按原 seen-only checkpoint 规则选择；存在阈值与已有正斜率单调校准仅使用 seen validation，并按队列协议在测试前冻结。
- GMR 报 S/U AUROC、U+ FRR、U− RR、raw/gated 定位、正确定位正例的误拒率。官方 gate 与诊断硬拒绝分别报告。
- 正例 VTG 报 seen/unseen 定位。Flash 后续结果以完整正例分母核验空预测，保留原官方结果和实现局限。
- 使用计划已有的视频 paired bootstrap；其不确定性来自视频抽样，不能称为跨训练种子稳定性。单调校准不能修复 AUROC 排序。

解释规则（不是新增通过阈值）：

| 观察 | 允许的判断 |
| --- | --- |
| GMR 和正例 VTG 均有收益 | 支持进一步检验跨划分/架构的一致性；仍需简单对照和机制证据 |
| 只有 GMR 存在指标提高 | 结论限于存在判别，不能称为通用对应学习 |
| VTG 改善、GMR 定位恶化 | 提示存在任务下的取舍或冲突，尚非因果归因 |
| 只提高接受、拒绝显著恶化 | 不视为共同泛化改善 |
| Unseen 不升而 seen 下降 | 不能以差距缩小宣称成功 |

不因开发结果不利而放宽旧门槛，不新增更有利的真实 U 阈值，不用正式 U 结果回选方法。

## 6. 与完整计划的关系

当前候选关闭后，原计划保留 **75 次单 seed 正式训练**：

- 五划分 × 三 GMR 骨干 × baseline/regularized/adapter = 45 次。
- 五划分 × QD/Flash 正例 VTG × baseline/regularized/adapter = 30 次。

A1/QD 双轨的 6 次包含在这 75 次中，不是额外增加。Flash 验证非 DETR 迁移；其他动作/组合划分验证语义划分间一致性。六次完成不能写成原完整计划已经完成。教师与 window 继续保持当前跳过状态，不恢复 Witness-DETR。

## 7. 恢复后直接执行的任务清单

1. 读取 [queue_state.json](../../runs/autonomous_queue_20260930_strict/queue_state.json)，结合实际进程、运行目录及账本核对状态，避免重复启动。不能仅凭状态文件中的旧 PID 判定进程仍在。
2. 确认 [MECHANISM_GATE.json](../../runs/autonomous_queue_20260930_strict/MECHANISM_GATE.json) 和 [SELECTION_FROZEN.json](../../runs/autonomous_queue_20260930_strict/SELECTION_FROZEN.json) 存在且决定未变；不要重新开发选择。
3. 沿现有队列继续 75 次正式简单控制训练与原评测流程。优先在分析层面跟踪 A1/QD 六个正式任务，不重排队列。
4. 六个任务的训练、预算审计与相应评测都完成后，整理双轨比较表，明确训练完成与测试完成的区别。评测是否启动仍依现有队列协议，不另开提前测试流程。
5. 完成五划分及 Flash 验证后，再汇总泛化范围和局限。自动最终产物预定为 [FINAL_REPORT.md](../../runs/autonomous_queue_20260930_strict/report/FINAL_REPORT.md) 和 [MECHANISM_ANALYSIS.json](../../runs/autonomous_queue_20260930_strict/report/MECHANISM_ANALYSIS.json)；核验时尚未生成，未来应检查实际存在与内容。
6. 后续更新本文件的核验时间、已完成任务和证据入口；保留当前已冻结判断的历史，不覆盖失败记录。

所有代码、配置、运行、报告仍限定在本实验目录；原框架、发布数据、特征与旧结果只读。若发现阻塞，按计划的重试与恢复规则处理，不扩展 seed、研究分支、骨干或教师信息。
