# 视频—文本对应关系泛化实验交接

更新：2026-09-30。**清空上下文后，从本文件恢复新研究；已完成项目全貌见[项目总交接](../PROJECT_HANDOFF.md)，算法细节见[当前实验方案](EXPERIMENT_PLAN.md)。**仓库根目录：`/home/guoxiangyu/paper/Openword/generalized-moment-retrieval`。除明确写出的绝对路径外，下文路径均从仓库根目录起算。

## 1. 研究目标与当前状态

核心问题：**在每个冻结划分的训练集、正负样本、标签、特征访问和训练暴露保持不变时，如何从已见语义学到可迁移的视频—文本对应关系，使模型面对下游训练未见的动作或动作—物体组合时，能判断事件是否存在，并在事件存在时正确定位？**“未见”只指当前下游任务训练；不声称 CLIP/SlowFast 预训练未见这些概念。

当前已有 benchmark、三种 GMR 基线、五组完整测试和文献调研。**新方法尚未确定；本方案尚无新模型代码、新训练或新结果。**“对应结构在微调中受损”“共现捷径”“输入缺动作证据”都是待检验的解释。现有证据不能直接证明其中任何一个。研究应先定位瓶颈，再选损失或结构。

当前方案是[固定数据下的对应关系泛化](EXPERIMENT_PLAN.md)；[文献调研](LITERATURE_REVIEW.md)是近邻和新颖性依据。[Witness-DETR](archive/WITNESS_DETR_PLAN.md)及其[训练配对审计](archive/witness_training_pair_audit.json)是历史候选，仅供追溯；ROI、slot 级拒绝和四元组重采样不是当前主线。未来实验代码放在[专用代码目录](../../experiments/correspondence_generalization/README.md)，当前该目录只有说明文件。

## 2. 已证实的问题与证据边界

数据来自 Charades-STA，四格为已见且存在 S+、已见且缺席 S−、下游未见且存在 U+、下游未见且缺席 U−。五组预先冻结划分：动作轴 A1（put/take）、A2_alt（drink/pour）、A3（run/walk）；组合轴 C1（sit|bed/chair/couch）、C2_alt（open/close|box/cabinet）。每组原模型只用本组 S+/S− 训练；checkpoint 与存在阈值只用 seen validation 选择。

Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR 在五组上各用 seed 3407、100 epochs 训练和测试，得到 15/15 的 seen AUROC 高于 unseen AUROC，差值 0.128–0.309。A2_alt 近乎全接受 U，C2_alt 的 Moment 近乎全拒绝 U，故不能把退化归结为统一的阈值方向。C2_alt Moment 的 U+ R@1@IoU 0.5 从 raw 35.65% 经 seen 阈值诊断硬拒绝降为 0%，证明某些已定位正确的 U+ 会被拒绝；这**不能**证明交互表示损坏。精确逐组表、配对、text-only 对照和视频聚类 bootstrap 见[阶段 2 报告](../reports/semantic_existence_multisplit_results.md)和[指标 JSON](../semantic_existence_v2_metrics/)。

证据限于同一 Charades 视频域、每配置一个种子；五组训练集正例组成不同。已有 U test 被研究者阅读过，不能再称严格盲测；后续只可作事先固定方案的最终确认，方法开发需使用训练内开发划分与 seen validation。组合轴存在 text-only 配对信号，尤其 C2_alt 的 matched PairAcc 为 0.818，必须在归因中报告。

## 3. 不可改变的主实验边界

1. 每个划分的 `data/release/semantic_existence_v2/<split>/train.jsonl` 原行、qid、视频、句子、`exist_label`、时间窗保持不变。配对比较的原模型和方法必须使用完全相同的训练行、正负采样、batch/顺序规则、更新步数和每行暴露次数；为算法另造 target-U 负例、新句子、跨视频 absence 标签或额外 U 正例都不合格。
2. 使用原先冻结的 CLIP 文本/视频、SlowFast 视频特征及相同预训练资源。新方法若需要额外编码器、字幕、检测器或特征层，就已进入另一个信息预算，不能作为当前主结论。参考相似度仅在确认缓存仍处于**可比较的图文共同空间**后使用；维度相同不是充分条件。
3. 原 GMR 轨道保留各骨干定位头、存在头、gate、checkpoint 和 seen 阈值选择规则。头结构固定，参数仍正常训练。新算法首先作用于视频/文本投影或交互所得的对应表示，接口应可接入无存在头的传统 VTG；不依赖 DETR slot、Hungarian matching、ROI 或特定拒绝器。
4. 真实 U+、U− 和 U validation 不用于架构、损失权重、超参、阈值或 checkpoint 选择。可以在**训练数据内部**预定义 pseudo-unseen 语义开发拆分；这只用于开发诊断，配对方法必须共用相同拆分。正式模型回到完整原 S 训练。最终 test 不回写调参。
5. 训练数据一致不代表计算预算一致。增加参数或额外 forward 均需记录，并用参数匹配适配层、常规正则和普通保持目标作强对照。

两条轨道**各自内部**作公平配对，不把它们混成一次训练：A 为原 GMR S+/S− 训练与 S/U 四格评估；B 为传统定位-only S+ 训练，双方都不引入 S− 或存在头，评估 seen/unseen 正例定位。轨道 B 至少包含 QD-DETR 和一种非 DETR 时序定位骨干；现有 FlashVTG 可优先评估可行性。只有 A 改善，不能称通用 VTG 对应方法。

## 4. 下一位实验者的执行顺序与阶段门槛

| 阶段 | 具体工作 | 继续条件或分支 |
| --- | --- | --- |
| 0. 恢复和冻结 | 核对发布包、原基线指标、本地特征与 checkpoint；为每组记录 train SHA-256、特征版本、代码 commit、环境、随机种子。定下候选与评估清单。 | 原始数据/模型资产缺失时先恢复；不得重构或改写发布包。 |
| 1. 输入参考可用性 | 检查缓存 CLIP 视频帧/文本句向量的来源、projection、归一化和语义可比性；检查原 S+ 真值窗内相似度相对背景的表现及动作顺序敏感性。不要把文本 token hidden state 直接当共同空间向量。 | 参考若主要认物体、不能辨动作或空间不匹配，停止教师保持分支，转做无教师诊断。 |
| 2. 机制诊断 | 对同一模型不同层/训练阶段作固定容量与预算的读出；比较原存在输出、固定表示简单读出、原阈值/seen 校准、原始对应分数。用 S+ 真值窗和已有 S− 标签检查视觉信息利用；无需制造新标签。 | 先判断“输入证据不足”“表示退化”“输出头/校准问题”，不能用 attention 图或单次 probe 当因果证明。 |
| 3. 最小同数据对照 | 首选已跑通的 QD-DETR。重跑原基线；加入参数匹配适配层、常规正则、普通表示 L2、普通对应结构 KL，再试选择性保持。所有模型同样本、同特征、同原头和开发协议。 | 若普通正则/蒸馏已解释收益，停止包装复杂机制；若无可靠参考，不实施 KL 保持。 |
| 4. 双轨扩展 | 固定机制和超参后，扩到动作与组合五组、三个 GMR 骨干；并在独立 S+ 定位-only 轨道检验 QD 与非 DETR。按相同样本输出存在、定位和对应诊断。 | 预先定义成功指标；只降低 seen 分数而缩小 gap、只接受 U+ 使 U− 拒绝崩溃、只提升 GMR 而不提升 VTG，均不能支撑目标主张。 |
| 5. 稳健性确认 | 对最终方法及最强简单对照至少增加三个训练种子，保持每个划分协议相同；按视频 paired bootstrap 和种子变化分别报告。 | 汇总动作与组合轴，不能把共享视频域五组当独立域；若需更强新颖性，另设计新的确认域/语义包，不改本次冻结数据。 |

候选最小形式见[方案 §4](EXPERIMENT_PLAN.md)：同一样本可靠粒度的参考对应分布 `P0` 与模型对应分布 `Pθ`，先测普通 `KL(stopgrad(P0)||Pθ)`，再测由**已有 S+ 时间窗**确定的选择性权重。S− 的时间 softmax 必有质量，不可据此伪造 S− 的正确片段；S− 继续原监督。普通 KL/L2 是必须报告的先例基线，不能直接宣称新算法。若阶段 1/2 显示瓶颈只在输出校准，应据实转向决策层问题，而不是强推对应学习。

## 5. 对照、指标及判定

最低矩阵：原模型、参数匹配适配层、常规正则、普通 L2 保持、普通对应 KL、候选选择性保持、表示不变的存在头校准。各方法应在同一 split/seed 上成对比较，并报告训练样本集合哈希、暴露次数、参数量、训练 forward 数和推理开销。不能将不同数据或额外信息预算的方法混入主表。

GMR 必报 seen/unseen AUROC 和各自绝对值、`seen−unseen` gap、U+ FRR、U− RR、同视频 U+/U− PairAcc、U+ raw 定位和 seen 阈值后定位，以及**raw 原本定位正确的 U+ 中被误拒的比例**。同时区分诊断硬拒绝与官方 GMR gate 指标。VTG 轨道报告 seen/unseen S+ 的 R@1@IoU 0.5 及其他既有定位指标；传统 VTG 不报告不存在事件的拒绝能力。动作轴 A1/A2_alt/A3 和组合轴 C1/C2_alt 分开给逐组值及等权摘要，不用 pooled 大样本掩盖小组失败。

判断新方向是否成立须有连贯证据：先证实训练对应表示的可迁移性缺口，再证实方法改善该诊断，同时提高 unseen 存在**绝对**表现而保住 U− 拒绝，最后在无存在头的 VTG 上观察定位迁移。一个指标改善不能代替整条证据链。若只有输出层校准起效，应写成校准发现；若输入原特征缺动作证据，无法由头部保持项保证修复。

## 6. 文件、代码入口与产物约定

| 路径 | 用途 |
| --- | --- |
| [当前方案](EXPERIMENT_PLAN.md) / [文献调研](LITERATURE_REVIEW.md) | 研究问题、候选原型、近邻先例与停止条件。 |
| [项目总交接](../PROJECT_HANDOFF.md) / [阶段 2 运行交接](../20260929_PHASE2_CURRENT_WORK_HANDOFF.md) | 已有基线状态、具体训练路径和历史约束。 |
| [正式 v2 数据](../../data/release/semantic_existence_v2/) / [指标 JSON](../semantic_existence_v2_metrics/) | 冻结训练行、发布 manifest 和可核对的已有结果。 |
| `models/{moment_detr_gmr,qd_detr_gmr,flash_vtg_gmr}/`，`configs/` | 现有三骨干与配置，开发时先追踪输入投影、交互层、存在头与定位头的实际张量。 |
| `scripts/run_semantic_multisplit_100ep.sh`，`scripts/run_semantic_localization_controls.sh` | 历史 GMR 与定位-only 运行协议参考；调用前核对参数、输出目录和是否会覆盖结果。 |
| [新代码目录](../../experiments/correspondence_generalization/README.md) | 未来新代码及实验配置的唯一专用工作区；此刻只有 README，无算法实现。 |
| `results/semantic_existence/multi_split_v2/<split>/<moment\|qd\|flash>/` | 本地旧基线 checkpoint、预测、日志；通常被 Git 忽略，勿覆盖。 |
| `features/semantic_existence_v2/<split>/clip_text/`、`features/semantic_existence_v2/<split>/val_seen.jsonl` | 本地文本特征与 seen 验证视图；通常不随 Git 发布。 |
| `/home/guoxiangyu/paper/新建文件夹/charades/{vid_clip,vid_slowfast}/` | 本地视频特征；新机器复现需另备。 |

推荐给未来每次新运行写一个不可覆盖的实验记录，至少包含：研究假设、split/seed、训练行 SHA-256 与 qid 核对、特征/checkpoint 来源、配置和代码 commit、方法及最强对照、超参选择依据、训练步数与暴露统计、每 epoch/最佳 checkpoint 的 seen validation 指标、test 全指标与预测路径、计算成本、失败或偏离协议的说明。新运行产物使用独立目录，**不得写入旧 `results/semantic_existence/multi_split_v2/`，也不得改发布包与已发布指标**。记录内容先冻结再看 U test。具体文件名和执行脚本在开始编码时确定，本交接没有虚构尚不存在的运行命令。

只读恢复检查（在仓库根目录执行）：

```bash
for split in A1 A2_alt A3 C1 C2_alt; do
  python scripts/validate_release.py --release "data/release/semantic_existence_v2/$split"
  sha256sum "data/release/semantic_existence_v2/$split/train.jsonl"
done
```

本地结果、视频和特征若不可用，已发布的标注与指标仍可恢复科学问题和既有证据，但不能据此直接复现训练。恢复资产后先做阶段 0，不要直接启动新模型训练。
