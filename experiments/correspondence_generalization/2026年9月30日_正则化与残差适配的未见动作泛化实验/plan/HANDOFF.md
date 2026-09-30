# 对应关系泛化实验：清空上下文后的恢复入口

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

## 最新范围覆盖：六组自动训练，每卡两个并发

2026-09-30 最新用户指令优先于下文旧范围：**只训练 A1/QD baseline/regularized/adapter × GMR/正例 VTG 六组，seed=3407、100 epoch；取消其他训练及评测，不进行同预算核验。** 75组矩阵、其他骨干/划分及旧预算核验要求均不再执行。详见 [progress.md 顶部更新](progress.md)。

已经切换并实际启动 [six_task_queue.py](../../code/six_task_queue.py)，tmux会话 `correspondence_six_tasks`，每卡两个训练任务。GPU0：原QD-GMR adapter + QD-VTG adapter；GPU1：QD-VTG baseline + regularized。QD-GMR baseline/regularized已完成训练。旧调度器已停止，范围外Moment已终止，其他正式节点已取消，历史产物保留。新队列完成后自动评测和汇总，不调用同预算核验。

恢复先读本节 → [progress.md](progress.md) 顶部 → [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md) 顶部最新范围。实时状态读 [queue_state.json](../../runs/autonomous_queue_20260930_strict/queue_state.json)。不要根据下方历史要求恢复75组或追加实验。启动入口仍为 `bash code/launch_queue.sh`，仅确认调度进程确实退出后使用，避免重复启动。

更新：2026-09-30。本文件是今后继续本研究的首读入口。仓库根目录为 `/home/guoxiangyu/paper/Openword/generalized-moment-retrieval`。用户已明确授权继续实际编写代码、训练、评估与机制分析；早期“本轮不编写/不训练”的指令已被本次继续实验指令替代。

## 最新交接补充：先配合 progress.md 恢复

**2026-09-30 16:07（Asia/Shanghai）核验更新。** 清空上下文后，本文件与 [progress.md](progress.md)、[EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md) 配合阅读：本文件提供约束与入口，progress 提供最新判断、最小实验和待办，实验方案提供固定协议。下方 10:56 状态及阶段结果为历史快照，不再代表当前进度。

- 用户再次明确：未来不做任何多 seed 实验，只沿本 plan 方案；唯一 seed=3407，不新增分支或骨干。
- 严格训练 100 epoch 和 1/10/30/100/best 诊断均完成；100/best 机制门槛未通过，window 跳过，教师 L2/KL 仍跳过。
- canonical baseline/regularized/adapter 开发控制均完成；选择已冻结为 strongest_simple=adapter、candidate_formal_enabled=false。选择结果不表示 adapter 已验证有效。
- 队列已进入 formal_training。核验时 A1 QD-GMR baseline/regularized 完成训练，QD-GMR adapter 与 Moment-GMR baseline 运行中。状态以 [queue_state.json](../../runs/autonomous_queue_20260930_strict/queue_state.json) 和实际运行记录为准；不要重跑已完成开发任务。
- 当前最小分析单元为 A1/QD 的 baseline/regularized/adapter × GMR/正例 VTG，共 6 次正式训练，包含在原 75 次单 seed 矩阵中。它不替代完整计划，不改变运行队列或提前测试规则。目的、指标、解释边界与后续任务详见 [progress.md](progress.md)。
- 本次仅建立文档交接，没有修改训练、队列配置或冻结选择。此前探索性额外诊断建议未成为必做任务。

## 历史续跑状态（2026-09-30 10:56 快照）

核验时间：**2026-09-30T10:56:52+08:00**。本节为状态快照；动态进度以运行目录中的状态和逐 epoch 账本为准。可机器核对的本次快照见 [CURRENT_STATUS_20260930.json](CURRENT_STATUS_20260930.json)。

### 用户范围与唯一活动任务

用户已授权持久化自动队列，无需每阶段人工重启；**仅 seed=3407，不进行多种子实验，也不新增研究分支或骨干**。保留方案已有的五划分、三 GMR 骨干和 QD/Flash 正例 VTG。Witness-DETR 不作为主线。

| 活动项 | 实际状态 | 产物入口 |
| --- | --- | --- |
| 严格 QD 开发训练 | 从头训练，已完成 76/100 epoch；PID 79891 活着 | [status.json](../../runs/qd_throw_strict_diagnostic_20260930/status.json)、[epochs.jsonl](../../runs/qd_throw_strict_diagnostic_20260930/epochs.jsonl) |
| 阶段诊断 watcher | 1/10/30 完成、无失败；等待 100，随后 best；PID 79894 活着 | [diagnostics_status.json](../../runs/qd_throw_strict_diagnostic_20260930/diagnostics_status.json) |
| 自动执行队列 | waiting_initial_diagnostic；PID 80542 活着；尚未开始完整同预算开发控制或正式训练 | [queue_state.json](../../runs/autonomous_queue_20260930_strict/queue_state.json)、[execution_queue.json](../../code/configs/execution_queue.json) |

当前两张 RTX 3090 可用：GPU 0 执行训练，GPU 1 等待下一阶段诊断；核验时显存分别 1838/321 MiB。GPU 1 空闲符合等待状态。tmux 会话为 `correspondence_strict_diagnostic` 和 `correspondence_queue`，使用本实验 `cache/runtime/queue.sock`。检查时进入 `cache/runtime/` 执行 `tmux -S queue.sock ls`；绝对 socket 路径过长，默认 socket 不属于本队列。**不要重复启动或覆盖活动运行。**

### 严格视图与旧结果处理

原开发视图有 3 条 throw 词形查询泄漏，扩展词形审计另发现 2 条 toss 查询，共涉及 5 个额外视频、8 行。旧训练 `qd_throw_diagnostic_20260930_0916` 已停止，状态为 `terminated_semantic_isolation_audit`；其阶段 1/10/30 和部分训练只作探索性记录，**不进入当前机制门槛**。旧队列 `autonomous_queue_20260930` 在等待阶段被替代，没有正式任务启动；不要续跑它。更早的 `qd_throw_diagnostic_20260930_0909` 导入失败、0 更新。

唯一活动视图：[pseudo_unseen_a1_throw_strict/view_manifest.json](../../runs/pseudo_unseen_a1_throw_strict/view_manifest.json)。train=7559（6252+/1307−），pseudo-dev=570（464+/106−），seen val=1185（709+/476−）。排除 394 个视频，train/dev qid 和视频无重叠；原行字节、标签、时间窗不改。只声称标注主动作族与 throw/toss/hurl/fling/lob 词形隔离，不声称完全概念分离或预训练未见；视频排除带来分布变化。**正式五组全 S 训练不改。**

严格 train SHA-256：`358a1d0a00c97ebb27395df96535b51ab74249793395373ceae94691c59dd0ef`；pseudo-dev：`396ff0195a7577b03404e1d25a2aa9ceedd36582e4e07860a407a670b65be61b`；seen：`29166e4d694480fd41184bd4ff5802d1251103f4a042cdcbd9ac25ab7ddb6685`。

完整开发训练预算为 47,300 更新、755,900 行曝光（7559×100），batch=16、尾批=7、workers=0。截至核验，完整 epoch 累计 35,948 更新、574,484 行曝光；每个完整 epoch 均核验 7559 行各出现一次。不含正在执行的部分 epoch。workers=0 与历史 workers=4 不同，后续配对方法统一当前设置。运行中的 provenance、protocol、源文件 hash 和配置快照是实际版本依据；旧 `qd_throw_seed3407_*` 配置不代表当前严格视图。

### 当前结果：阶段诊断，尚非最终结论

以下为 **seen / 训练侧 pseudo-unseen AUROC**，不是正式真实 U 指标。来源分别为 [stage 1](../../runs/qd_throw_strict_diagnostic_20260930/diagnostic_1/metrics.json)、[stage 10](../../runs/qd_throw_strict_diagnostic_20260930/diagnostic_10/metrics.json)、[stage 30](../../runs/qd_throw_strict_diagnostic_20260930/diagnostic_30/metrics.json)。

| 读出 | epoch 1 | epoch 10 | epoch 30 |
| --- | --- | --- | --- |
| 原存在头 | 0.8045 / 0.3872 | 0.8405 / 0.5860 | 0.8457 / 0.5192 |
| 原输入联合 | 0.8056 / 0.4885 | 0.8056 / 0.4885 | 0.8056 / 0.4885 |
| 原输入文本控制 | 0.8376 / 0.6378 | 0.8376 / 0.6378 | 0.8376 / 0.6378 |
| 投影联合 | 0.8270 / 0.5243 | 0.8343 / 0.5890 | 0.7840 / 0.6132 |
| 投影文本控制 | 0.8322 / 0.5920 | 0.8432 / 0.6948 | 0.8477 / 0.6954 |
| decoder 均值 | 0.8134 / 0.4163 | 0.8393 / 0.5620 | 0.8380 / 0.4781 |

三个阶段的联合读出均未通过“胜过两种单模态控制”门槛。epoch 30 投影联合相对原头 pseudo AUROC +0.0940，但 seen AUROC −0.0618，超过允许损失 0.01；相对文本控制 pseudo AUROC −0.0822，视频 paired bootstrap 95% CI=[−0.1388, −0.0233]。阶段 1 相对原头的联合收益也不能排除文本捷径。**当前不支持对应机制成立，不提前启用候选；最终判断等待 100/best。**

epoch 30 原头定位：seen raw/hard R1@0.5=0.3794/0.3004；pseudo raw/hard=0.2866/0.2565。pseudo raw 正确正例被硬拒绝比例=0.1053。hard 阈值 1.27555 仅由 seen 选择；这些是诊断硬拒绝指标，不能当官方 gate 或独立正例 VTG。原输入读出随阶段不变是固定特征及固定拟合协议的结果。

每个 256 维 probe 为 257 参数，100 epoch、3000 更新、755900 行曝光，使用相同 batch 排列；标量校准另作容量不同的控制。原输入联合是压缩拼接上的线性读出，不足以排除复杂输入交互；投影乘积不是已对齐 CLIP 空间。probe/区间只给关联证据，不是因果机制证明。视频 bootstrap 不等同训练种子方差。

### 已实现与未完成的边界

- 新代码和复制适配实现均在 `code/`；严格队列三骨干实际 train/seen smoke 已通过，QD 基线/正则初始化和采样顺序一致，Moment 正例 VTG 无存在头，Flash 负例窗口辅助跳过。见 [INTEGRATION_CHECKS.json](../../runs/autonomous_queue_20260930_strict/INTEGRATION_CHECKS.json)。smoke 不用于模型选择。
- 队列资产清单已冻结 67,628 项；运行记录源/数据/特征/旧 checkpoint hash、配置、seed、曝光、更新、forward、参数、时间/峰值显存与路径。准确完整训练 FLOPs 和 GPU 活跃时间尚未测得；旧单批算子 profile 仅为不完整计数，不能外推总 FLOPs。
- 队列注册 206 节点：104 pending、100 waiting_training、2 skipped；这是预登记，**不是完成了 100 次训练**。固定正式矩阵 75 次训练；仅候选过门槛时增加 25 次，均单 seed。教师控制因来源/信息预算未通过被跳过，不代表实验证明教师无效。
- canonical 开发基线将重新从头训练，以统一独立 sampler；当前初始机制诊断的全局 RNG 采样不能直接当后续配对基线。
- Flash 空 proposal 保留 qid/空预测；原官方 R1 可能漏计空预测正例，最终报告另按完整正例分母计算，并保留原 seen checkpoint 规则。原 Flash `StepLR.step(loss)` 行为保留并作为局限记录。
- 尚未完成：100/best 诊断、完整开发控制、候选选择冻结、新正式 GMR 四象限、独立正例 VTG、新正式真实 U 测试和最终机制汇总。不得把实现就绪、smoke 或历史结果写成这些工作的完成证据。

最终自动产物路径为 `runs/autonomous_queue_20260930_strict/report/FINAL_REPORT.md` 和同目录 `MECHANISM_ANALYSIS.json`，当前尚未生成最终结果。

## 1. 阅读顺序与目录

1. 先读本文件顶部最新交接，恢复约束和运行入口。
2. 读 [progress.md](progress.md)，恢复最新判断、最小实验、与计划的关系和继续任务清单。
3. 读 [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md)，了解完整阶段门槛和双轨实验。
4. 读 [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md)，了解近邻工作和新颖性边界。文献内容是已有调研的整理副本，本轮没有重新联网核查。
5. 需要核对证据时读运行 JSON；[既有诊断报告](../../STAGE_GATE_REPORT.md)及其关联 JSON 是早期记录。

| 路径 | 用途 |
| --- | --- |
| `experiments/correspondence_generalization/plan/` | 当前方案、当前交接、来源快照和哈希清单 |
| `experiments/correspondence_generalization/code/` | 今后新实验实现的代码工作区；已有正式开发训练入口、复制实现与阶段诊断，见当前续跑状态 |
| `experiments/correspondence_generalization/runs/` | 已有诊断、派生视图和 smoke 记录；未来运行必须新建独立目录 |
| `experiments/correspondence_generalization/cache/` | 已有缓存；未来各运行建议使用独立缓存子目录 |
| 本实验目录根部已有 `.py` / `.sh` | 前序会话的诊断原型，保留原路径供哈希和记录追溯；不是完成的新算法或已审计的正式训练管线 |
| `plan/source_snapshots/` | 四份原始入口文档的逐字节快照；其中状态可能早于实际诊断，恢复进度以本文件为准 |

整理时采用复制方式保存原始文档，没有移动或改写只读 `docs/`。来源路径及 SHA-256 见 [DOCUMENT_MANIFEST.json](DOCUMENT_MANIFEST.json)。不要把来源快照中的“尚无代码、目录只有 README”当作当前状态。

## 2. 研究目标及禁止越过的边界

在冻结划分训练样本、正负标签、时间窗、特征、采样策略和更新预算不变的条件下，从 seen 语义学习更可迁移的视频—文本对应关系，改善 unseen 存在判别与定位。方法还应适用于只用正例、无存在头的传统 VTG。未见仅指下游训练未见，不声称预训练未见。当前未确定最终算法。

所有新代码、配置、脚本、派生数据、缓存、checkpoint、预测、日志、图和报告必须留在 `experiments/correspondence_generalization/`；今后新实现放入 `code/`。`models/`、`configs/`、`scripts/`、`features/`、`data/release/`、旧 `results/semantic_existence/` 和已发布指标均只读。需要修改原实现时，将必要实现复制到新工作区并记录来源哈希；原框架保持可直接复现。

不得增加目标 U 样本、查询、标签、跨视频 absence 标签或额外教师信息。不得为了新方法改变原训练行、时间窗、采样、batch 顺序或每行暴露次数。正式成对比较使用相同原始行、特征、seed、采样及更新预算。参数、forward 数和计算量不同须单列并设置相应控制。

真实 U validation/test 不用于方法设计、损失权重、超参、checkpoint 或阈值选择。仅用训练侧开发数据和 seen validation 选择；正式 test 方案预先冻结。U test 已被历史研究阅读过，不能称盲测；已有输出诊断也读取过五组 U test，不能反复据此挑选最有利方法。

**Witness-DETR 已归档，不作为主线。** 不恢复 ROI verifier、slot 拒绝器或专属四元组采样。普通 L2/KL 蒸馏属于控制，不能直接包装成新算法。

## 3. 基准与本地资产

五组冻结划分：动作轴 A1（put/take）、A2_alt（drink/pour）、A3（run/walk）；组合轴 C1（sit|bed/chair/couch）、C2_alt（open/close|box/cabinet）。三种原 GMR 骨干 Moment/QD/Flash 的 15 次 100-epoch 基准训练与测试早已完成，seed 3407。原始四格为 S+、S−、U+、U−；新方法完整实验尚未运行。

| 划分 | 原 train 行数 | S+ / S− | train SHA-256 |
| --- | ---: | ---: | --- |
| A1 | 8608 | 7108 / 1500 | `0cd951d33e1429d1cecf4ce0a661fc290dc4997b995abba362f76545bb486a14` |
| A2_alt | 10323 | 8823 / 1500 | `d00938614ba3e0583dbb32d129804adc8938f5c1f89a66316b4b754d539f71a3` |
| A3 | 10352 | 8852 / 1500 | `53a1976cad3aedead9019daa3b25967c44f6e7f993b502e4521eb30dff0e6ffe` |
| C1 | 10516 | 9016 / 1500 | `0fa9cc62f1964069e9ec35808533c89845049dc93e0d7ecd16c6eb0576be0638` |
| C2_alt | 10612 | 9112 / 1500 | `bb731690357dbb9af7b0641ec7649ba42b4fe3f3aad9798281cfb482caccbf3e` |

发布标注：`data/release/semantic_existence_v2/<split>/`。文本缓存：`features/semantic_existence_v2/<split>/clip_text/`，指向共享文本目录；seen validation 视图在同级 `val_seen.jsonl`。视频缓存：`/home/guoxiangyu/paper/新建文件夹/charades/{vid_clip,vid_slowfast}/`。旧 checkpoint：`results/semantic_existence/multi_split_v2/<split>/<moment|qd|flash>/`；Moment/QD 为 `best.ckpt`，Flash 为内部运行子目录的 `model_best.ckpt`。

前序阶段 0 验证五组发布包均通过，每组十个发布哈希通过、视频切分无重叠、训练特征无缺失、15 个最佳 checkpoint 均存在。资产清单及 checkpoint 哈希见 [stage0/manifest.json](../../runs/stage0/manifest.json)。恢复会话必须重新核对，不能假定设备和文件仍可用。代码基准 commit 为 `bc88348e0e6b7b629a77d884fe66efe8c87b2774`；工作树已有未提交内容，因此每个运行还必须记录实际源文件哈希，不能仅靠 commit 标识代码版本。

## 4. 实际完成的诊断与证据限制

| 已执行工作 | 产物 | 观察及限制 |
| --- | --- | --- |
| 缓存 CLIP 参考审计 | [reference_audit/audit.json](../../runs/reference_audit/audit.json) | 每组抽取 400 个 S+ 训练行；真值窗平均相似度有一定优势。原正查询对同视频编辑负查询的窗内排序约为动作池 63.2%、组合池 56.0%，各 1499 对。组间共享负例池，不能当五次独立验证。 |
| 输出层简单读出 | [output_diagnostic/qd_readouts.json](../../runs/output_diagnostic/qd_readouts.json) | 在 seen validation 拟合固定 C=1 的两分数 logistic，读取五组 test。未出现一致的 unseen 收益；A3 AUROC 提高同时 U− RR 下降。该结果不能证明只需校准，也不能排除其他输出头设计。 |
| 输入投影余弦探针 | [projector_probe/qd_projector.json](../../runs/projector_probe/qd_projector.json) | A1/C1 原训练编辑对排序约 47.1%/48.4%；投影层并非余弦匹配空间，不能据此证明表示损坏。 |
| 固定容量 seen 读出 | [fixed_readout/metrics.json](../../runs/fixed_readout/metrics.json) | A1 取 500 S+、500 S− 拟合 256 维线性读出，在 1257 条 seen val 测量：原头 .812、早期投影乘积 .700、后期 decoder 均值 .795 AUROC。checkpoint 已见过这些语义，summary 统计也不同，不能称 pseudo-unseen 验证。 |

文本缓存保存的是 `last_hidden_state`，不是直接对齐图像空间的 token embedding。前序审计使用本地 ViT-B/32 的 `text_projection` 重构 EOT 句向量，但正例旧缓存与视频缓存的权重身份、精确帧时间戳尚未独立证实。这个重构访问了额外投影权重，不能自动视为已经通过同信息预算审计。均值句—帧参考对窗内帧顺序不敏感，不能为动作顺序提供教师信号。

此前报告写“teacher 分支失败”是当时的保守执行决定；**没有事先冻结的数值通过门槛，也没有足够因果证据证明所有教师保持都无效**。当前准确状态是“参考可靠性和预算未充分验证，暂停 L2/KL 教师分支”。若以后恢复它，先补来源和可比性证据，所有相关控制必须共享同一信息。

Logistic 记录中的“一次 fit / 一次暴露”表示一次拟合调用，并非一次优化更新或真实逐行访问次数。前序 probe 没有完整优化访问账本；不能作为正式等暴露训练证据。正式实验须记录迭代数、更新数与逐行曝光。

## 5. 历史初版开发视图（已被严格视图替代）

本节记录旧视图及旧 smoke 历史；活动训练使用上方 strict 视图，不能据本节判定尚未训练。位置：`runs/pseudo_unseen_a1_throw/`；来源和哈希见 [view_manifest.json](../../runs/pseudo_unseen_a1_throw/view_manifest.json)。仅取 A1 原 train 行，保留原行字节、标签和时间窗：

| 视图 | 行数 | 正 / 负 | 用途 |
| --- | ---: | ---: | --- |
| `train.jsonl` | 7567 | 6259 / 1308 | 排除 action_base=throw，且排除包含该动作行的 389 个视频 |
| `pseudo_unseen_dev.jsonl` | 570 | 464 / 106 | 原 train 中 throw 行；仅做开发诊断 |
| `val_seen.jsonl` | 1185 | 709 / 476 | 原 A1 seen val 去除 throw 行；用于该开发模型选择 |

train/dev qid 与视频重叠均为 0。选择 throw 基于训练侧标签覆盖，未使用真实 U 调参。这是暂定的单动作开发诊断；视频排除还改变训练视频分布，不能把差异全部归因于语义未见。它不是新的正式发布划分，也不是正式全 S 训练集；正式方法比较仍从头使用完整原 train。

前序 `launch_pseudo_unseen_qd.sh` 曾在 GPU 预检处退出，**没有完成正式 100-epoch 开发训练**。`cpu_smoke_workers0_v2/` 已完成 debug 模式 3 次更新（48 行总暴露）和 16 行 eval，仅验证入口可运行；其 checkpoint 和指标不用于算法开发或正式选择。其前两个 smoke 尝试分别因 multiprocessing socket 权限和 import 路径失败。详见 [execution_status.json](../../runs/pseudo_unseen_a1_throw/execution_status.json)。

旧原型入口将 DataLoader workers 改为 0 以兼容当时环境；这不是已经审计的正式复现设置。未来所有配对方法必须统一 worker/seed 规则，确认数据加载随机性与历史基准的关系，并记录偏离。

## 6. 后续实际执行顺序与阶段门槛

1. 恢复时先读状态、PID、tmux 和账本。当前队列持续自动执行，无需再次启动；仅进程确实退出时再按状态处理，不覆盖已完成/失败记录。显存或磁盘不足等待；不终止其他进程，不清理只读资产。
2. 完成严格 100 epoch 和 100/best 诊断。两阶段均须存在联合 probe：相对原头 pseudo AUROC≥+0.03、paired CI 下界>0、seen 损失≤0.01，同时胜过对应视频和文本单模态各≥0.03且 CI 下界>0，才开启窗口候选。生成 `MECHANISM_GATE.json`；不通过则标注 skipped，继续普通控制，不强行认定机制有效。
3. 队列执行相同严格视图/seed/独立 sampler 的 canonical baseline、常规正则和参数匹配 adapter，各100 epoch、相同更新/每行曝光。若通过诊断门槛才加入 window；辅助损失仅使用原 S+ 时间窗，不增加目标 U、absence 标签或教师。
4. 只用 seen 和 pseudo 开发指标冻结选择。window 必须相对最强简单控制 pseudo AUROC≥+0.03、seen 损失≤0.01、pseudo FRR/RR 恶化各≤0.03，才加入正式候选矩阵。注意当前实现若没有满足 seen 约束的简单控制，会回退选一个普通控制作参照；该参照不能自动宣称有效，最终报告必须标出失败。冻结文件为队列根与 `jobs/SELECTION_FROZEN.json`。
5. 单 seed 正式矩阵：五划分×三 GMR 骨干×baseline/regularized/adapter；独立正例 VTG 五划分×QD/Flash×相同三方法，共75训练。若候选通过则最多100训练。正式 GMR 使用原完整 S+/S−，VTG 仅原 S+ 且无存在头；预算按各原样本数统一100 epoch，不扩展种子或新方法。
6. 核验同预算、共同参数初始化和逐 epoch 顺序；seen-only 原规则选择 checkpoint，阈值/正斜率单调校准在测试前冻结。仅 `SELECTION_FROZEN.json` 后进入真实 U 测试，测试不回流选择。每任务失败最多新目录重试一次，保留失败证据，其他独立任务继续。
7. 自动汇总四象限/独立 VTG、逐组与动作/组合等权结果、同视频 PairAcc、视频 paired CI、计算与局限。有效、无效及未完成分别记录；若机制不成立，结论收缩为普通控制或诊断结果。教师分支保持暂停；不因结果不佳另加分支、多种子或额外信息。

## 7. 必须交付的指标与运行记录

GMR 按组分别报告 seen/unseen AUROC 绝对值和 gap、U+ FRR、U− RR、同视频 PairAcc（明确 ties=0.5）、raw 定位、seen 阈值诊断硬拒绝后的定位、raw 正确 U+ 中误拒比例；同时报告官方 GMR gate 指标与其阈值，不能混用两个 gate。

正例 VTG 分别报告 seen/unseen R@1@IoU .5、.7 及原有定位指标；GMR 正例的定位不等同于无存在头的独立 VTG 训练结果。动作轴三组和组合轴两组给逐组值与等权摘要，不用 pooled 大组掩盖失败。仅报告 seed=3407 的视频 paired bootstrap 区间；没有多种子训练，不估计训练种子变化。

每次运行先保存研究假设、源代码 commit 与文件哈希、源/派生数据及特征/checkpoint 哈希、完整配置、随机 seed、qid/batch 顺序规则、每行曝光、优化更新、forward 次数、参数量、设备及 wall/GPU 时间、checkpoint/阈值选择证据、所有输出路径、失败/偏离说明。只更新状态记录不能冒充新实验结果；任何未完成、低可靠性或不支持机制的结果明确标注。

## 8. 可直接复制的恢复提示词

> 先读 HANDOFF.md、EXPERIMENT_PLAN.md、LITERATURE_REVIEW.md，按当前 strict 运行与队列继续。先核对 `qd_throw_strict_diagnostic_20260930` 和 `autonomous_queue_20260930_strict` 的状态/PID/tmux，禁止重复启动。旧非 strict 训练和队列已被语义审计替代，不能进当前门槛。新实现仅写 code/，全部新产物留在本实验，其外只读。仅 seed3407、不扩展新分支；Witness-DETR 不作为主线。等待100/best诊断后据门槛执行同预算控制及条件候选，冻结后验证原五组GMR四象限和独立正例VTG；真实U不调参，原正式行/标签/窗/采样/预算不改。联合probe尚未胜过文本控制，不能提前宣称对应机制成立。保留哈希、曝光、计算、失败与未完成记录，后台队列自动继续。
