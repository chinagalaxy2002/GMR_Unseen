# 2026-09-30 A1/QD 双轨简单对照实验记录

整理时间：2026-09-30T21:43:41+08:00。阶段状态：六组训练完成、六组评测完成、最终报告完成。本文根据本次正式运行产物整理，不以历史基线或开发结果替代正式结果。

## 1. 本阶段问题与实验意义

本阶段检验：在固定已有数据与特征、保留原任务输出规则的条件下，普通正则或增加适配容量能否改善下游未见语义的存在判断与定位？研究目标是从已见语义学习可迁移的视频—文本对应关系；目前还没有确定新算法，也没有证实表示受损、语义捷径或输入动作证据不足中的任一解释。

六组对照提供同一 A1/QD 设置下的正式参照，并通过 GMR 与独立正例 VTG 两条轨道检验收益是否一致。它可以判断本次两种简单改动是否足以产生共同收益，不能单独定位失效原因或证明通用机制。

## 2. 执行范围与协议

- 唯一划分 A1（动作留出 put/take），唯一骨干 QD，唯一 seed=3407，每组100 epochs。
- GMR：原 S+/S−，8608行（7108正例、1500负例），同时学习存在与定位。
- 正例 VTG：仅原 S+，7108行，无存在头，不使用 S−。两条轨道各自训练，不能跨轨道作为同数据的因果消融。
- 六组均从头训练；旧 checkpoint 仅提供配置模板，不加载其训练权重。使用已有冻结 CLIP/SlowFast 特征，原发布数据不修改。
- batch=16，workers=0，AdamW，lr=0.0001。Baseline/adapter 的 weight decay=0.0001、dropout=0.1；regularized 分别为0.001、0.2。
- Adapter 在视频和文本输入投影后分别加入残差瓶颈层：256→64→256，ReLU，输出线性层零初始化。没有教师保持或额外 window 损失。实现快照见 [methods.py](evidence/code/methods.py)。
- 每组按 seen validation 的 MR-full-mAP 选择 best checkpoint；GMR 诊断硬阈值由 seen validation 的 Youden J 选择并在 test 前冻结。真实 U 不用于本次方法、checkpoint 或阈值选择。
- 按最新用户范围，不进行同预算成对核验，不声明初始化、batch顺序或逐行曝光已经通过成对核验。旧任务已有日志保留。
- 每卡最多两个并发任务。其他划分、骨干、教师、window、多 seed 与75组矩阵均不在本次执行范围。

完整运行配置及选择记录见 [run_configs.json](evidence/run_configs.json)。配置说明以运行时 provenance 为准，代码快照用于追溯，不替代运行记录。

## 3. 完成状态

队列于2026-09-30 17:58:04（Asia/Shanghai）正常结束，状态 completed，汇总返回码0。21:31复核各组 status/result、连续1–100 epoch账本、test报告和 checkpoint哈希。六组无失败或阻塞，当前本实验调度、训练、评测进程及 tmux 会话均已退出。

| 轨道 | 方法 | 完成 epoch | 训练 | 评测 | seen-selected best epoch（1起始） |
| --- | --- | ---: | --- | --- | ---: |
| GMR | baseline | 100/100 | 完成 | 完成 | 70 |
| GMR | regularized | 100/100 | 完成 | 完成 | 19 |
| GMR | adapter | 100/100 | 完成 | 完成 | 79 |
| VTG | baseline | 100/100 | 完成 | 完成 | 90 |
| VTG | regularized | 100/100 | 完成 | 完成 | 68 |
| VTG | adapter | 100/100 | 完成 | 完成 | 100 |

运行文件中的 best_epoch/selection epoch 为0起始索引，上表统一加1；训练账本的 epoch 为1起始。GMR adapter 沿用原调度器已启动的任务，其队列 attempts=[]，不表示没有训练，完成证据是该运行实际产物。

报告 failed_or_skipped.json 中3个节点是历史 window开发、teacher L2、teacher KL 的条件跳过，不是本次六组失败。范围外节点的取消记录保留。[完成核验快照](evidence/report/COMPLETION_VERIFIED.json)

## 4. 正式结果

### 4.1 GMR 四象限轨道

AUROC 为0–1，其余数值为百分比。FRR越低越好，RR及定位越高越好。FRR/RR和“硬拒绝”使用seen选择的诊断阈值；官方gate与诊断硬拒绝分别列出，不能混用。

| 方法 | S AUROC | U AUROC | U+ FRR↓ | U− RR↑ | raw U R1@0.5↑ | 官方gate U R1@0.5↑ | 硬拒绝 U R1@0.5↑ | raw正确U+误拒率↓ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 0.7966 | 0.5309 | 15.05 | 17.07 | 26.02 | 26.24 | 21.08 | 19.01 |
| regularized | 0.8316 | 0.4954 | 12.69 | 14.66 | 21.08 | 20.86 | 18.28 | 13.27 |
| adapter | 0.7933 | 0.4771 | 24.30 | 21.27 | 21.29 | 21.51 | 15.05 | 29.29 |

常规正则提高seen AUROC，但unseen AUROC下降；降低U+误拒的同时U−拒绝率也下降。Adapter的unseen AUROC和raw定位低于baseline，U−拒绝率增加同时U+误拒率增加。本次没有观察到存在排序、接受/拒绝和定位的共同改善。

### 4.2 独立正例 VTG

数值为百分比；本轨道不评测不存在事件的拒绝能力。Test包含2218条S+与465条U+。

| 方法 | Seen R1@0.5 | Seen R1@0.7 | Unseen R1@0.5 | Unseen R1@0.7 |
| --- | ---: | ---: | ---: | ---: |
| baseline | 38.73 | 21.24 | 20.65 | 8.39 |
| regularized | 39.81 | 22.99 | 18.71 | 7.53 |
| adapter | 43.46 | 24.57 | 26.24 | 10.97 |

Adapter相对baseline的unseen R1@0.5提高5.59个百分点，R1@0.7提高2.58个百分点；regularized的两个unseen定位点估计均下降。跨轨道不能直接比较绝对值来推断负例或存在头的因果作用。

### 4.3 相对同轨道 baseline 的统计区间

使用已有1000次视频paired bootstrap，随机种子3407。同一次抽样中方法与baseline共享视频抽样；这是视频抽样不确定性，不是多训练种子稳定性。

| 轨道 | 方法 | 指标 | 增益95%区间下界 | 上界 |
| --- | --- | --- | ---: | ---: |
| GMR | regularized | U AUROC | -0.0682 | -0.0075 |
| GMR | adapter | U AUROC | -0.0831 | -0.0250 |
| VTG | regularized | U R1@0.5（百分点） | -7.6144 | 2.4125 |
| VTG | adapter | U R1@0.5（百分点） | 0.2164 | 10.0630 |

GMR两种改动的AUROC增益区间均低于零；VTG adapter的R1@0.5区间高于零，但下界接近零。其R1@0.7增益95%区间约为[0.00, 7.05]个百分点，不能表述为所有定位指标均获得稳健提升。完整区间见 [report快照](evidence/report/)。

## 5. 分析：已支持的判断与未解决问题

### 5.1 已支持的阶段判断

本次配置的常规正则与适配容量增加不足以修复GMR存在泛化，不能把更高seen性能当作unseen成功。Adapter在正例VTG上的收益没有迁移为GMR的共同收益。因此双轨对照对限制结论是必要的：当前只能报告A1/QD单seed下的定位适配收益，不能宣称通用对应关系机制成立。

这也说明简单对照仍然重要。未来候选若只在VTG上超过原baseline，还需与已取得收益的普通adapter比较；仅有“超过baseline”不足以证明新增机制有价值。

### 5.2 机制仍未确定

“同一种adapter为何在VTG有效、在GMR未获共同收益”是本阶段值得追查的现象。但两轨同时改变了训练行组成、负例监督及存在任务，不能直接归因为存在损失损坏表示。

负例训练引起表示变化、存在与定位监督冲突、seen checkpoint选择带来不同取舍，是待检验解释，不是本次结论。也没有证据证明CLIP本体被训练遗忘：输入特征是冻结的，变化只可能发生在其下游使用方式中。

### 5.3 先前开发证据如何影响解释

此前训练侧strict pseudo-unseen诊断和canonical开发对照属于方法开发记录，不是本次真实U正式结果。联合探针未通过胜过单模态控制的机制门槛；window候选未启用。教师参考的来源、共同空间和信息条件未充分验证，L2/KL分支保持暂停。

探针失败不证明输入无动作信息；文本读出较强也不证明原模型实际依赖文本捷径。开发阶段冻结strongest_simple=adapter表示控制选择，不表示adapter的GMR有效性已经成立。冻结记录见 [SELECTION_FROZEN.json](evidence/SELECTION_FROZEN.json) 与 [MECHANISM_GATE.json](evidence/MECHANISM_GATE.json)。

## 6. Plan如何决定下一阶段方向

当前推荐保留科学问题，先定位瓶颈，再决定候选方法。以下为方向建议，没有创建新任务或恢复被取消实验。

| 待区分的瓶颈 | 支持判断所需证据 | 方向决策 |
| --- | --- | --- |
| 表示可区分，输出映射失配 | 固定表示的受控读出在训练侧pseudo-unseen有效，并优于单模态控制 | 研究存在读出或决策映射；若只有阈值收益则限定为校准 |
| 下游交互未利用可迁移信息 | 输入侧具有可用语义证据，投影/交互后诊断变差；联合收益确实依赖视觉 | 研究投影/交互层对应学习 |
| 固定输入缺关键动作证据 | 可靠的语义辨别、真值窗和时间诊断支持输入受限 | 缩小当前特征条件下目标，不承诺保持项可修复 |
| 有可靠输入对应参考 | 来源、图文共同空间和动作辨别能力通过核查 | 才讨论普通保持与选择性保持；不可靠则暂停教师路线 |

优先利用已有checkpoint、预测和阶段诊断，区分raw定位错误、正确候选被拒绝、存在排序不足与checkpoint选择的表现取舍。单调校准和阈值调整不能修复AUROC排序。

未来若恢复实验，应先在训练侧冻结一个可证伪假设，再选择能区分解释的最小设计；真实U不用于反复挑结构、超参或解释。机制支持后再设计方法：只有GMR存在排序、接受/拒绝、定位及正例VTG共同改善，才支持进一步讨论通用对应学习。只有一条轨道有效则缩小主张。

文献调研为贡献表述提供边界；本记录不新增或重新核验论文主张。原始研究依据：[LITERATURE_REVIEW.md](../../../docs/correspondence_generalization/LITERATURE_REVIEW.md)、[HANDOFF.md](../../../docs/correspondence_generalization/HANDOFF.md)、[EXPERIMENT_PLAN.md](../../../docs/correspondence_generalization/EXPERIMENT_PLAN.md)。其中旧多seed、扩骨干等执行要求已被当前用户范围覆盖。

## 7. 局限与停止边界

仅A1/QD、单seed、同一视频域，不能推断其他语义划分、架构或种子稳定性。两个轨道不是仅开关存在损失的因果对照。未完成同预算成对核验，不能声称排除了全部优化或计算差异。精确总FLOPs与GPU活跃时间未测量。现有真实U结果已被阅读，不能再称盲测。

本阶段没有产生已验证新方法；简单控制失效不等于所有对应学习无效。下一方向仍需机制证据，不自动恢复75组、教师/window、多seed或其他已取消训练。

## 8. 产物与追溯

- [RESULTS.csv](RESULTS.csv)：六组机器可读结果，AUROC与比率保存原始0–1值。
- [原自动最终报告快照](evidence/report/FINAL_REPORT.md)：保留自动流程输出及完成复核。
- [records.json](evidence/report/records.json)：六组正式评测原始数值。
- [evidence/](evidence/)：状态、开发门槛、冻结选择、配置、epoch日志、统计区间及代码/plan快照。
- [ARTIFACT_INDEX.md](ARTIFACT_INDEX.md)：运行目录、checkpoint、预测与日志索引。
- [MANIFEST.json](MANIFEST.json)：归档来源与SHA-256，用于识别快照。

原始训练目录保留在 ../runs/；未移动checkpoint、预测或训练日志，原恢复路径与失败记录不变。
