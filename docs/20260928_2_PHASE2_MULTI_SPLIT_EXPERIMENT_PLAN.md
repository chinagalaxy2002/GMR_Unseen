# 第二阶段实验方案：多语义划分重复验证

> 本文件保留事前方案与执行记录；当前完成状态见[项目总交接](PROJECT_HANDOFF.md)。

制定于 2026-09-28。本文件记录第二阶段预先冻结的协议及构建过程。五组数据均已通过正式发布校验；截至 2026-09-29 15:06（北京时间），15 个模型训练和全部测试评测均已完成。五组标注、选择资料及完整结果见 [`data/release/semantic_existence_v2/`](../data/release/semantic_existence_v2/)、[多划分结果报告](reports/semantic_existence_multisplit_results.md)和[机器可读指标](semantic_existence_v2_metrics/)。第一阶段的 `semantic_existence_v1` 保持原样，作为固定参照 A0；第二阶段检验存在判断退化能否在其他动作及动作–物体组合保留划分中重复出现。原始协议见 [v1 plan](../data/release/semantic_existence_v1/plan.md)，已完成结果及限制见[当前工作交接](20260928_1_CURRENT_WORK_HANDOFF.md)。

## 1. 研究问题与证据边界

第一阶段动作级未见只涉及 `open/close`；组合级另有 16 个不同类型的动作–物体组合。三个严格 GMR 模型的 seen→unseen 存在判断均下降，但不能仅凭 `open/close` 推断多种未见动作都有相同现象。v1 的 535 对 matched-U 全在动作级，组合级没有配对排序结果。

本阶段分别回答：

1. **动作级**：换成语义不同、非反义词主导的完整动作保留组后，三个模型的存在判断下降是否重复？
2. **组合级**：动作和物体各自在下游训练中出现，但二者的组合未见时，是否出现类似下降？
3. 两种新颖性下，U+ 定位的损失有多少来自同一 GMR checkpoint 的 existence 硬拒绝？
4. 同一个测试视频和查询在一个划分是 U、在另一个划分是 S 时，存在分数与定位表现如何变化？

“独立划分”指每组有不同的预先固定保留语义，并**分别构建训练集、分别训练模型和评测**；它们复用 Charades 域、原始视频划分和部分查询，统计上并非独立样本。即使趋势一致，论文也只主张 Charades 域内多种下游未见语义划分上的可重复现象，不概括为所有开放视频环境。

## 2. 固定协议与划分矩阵

所有新划分沿用原测试视频、按视频 ID SHA-256 分出的验证视频、正例原始时间窗、相同特征和现有三种 backbone。每组训练仅用本组 S+/S−；checkpoint、阈值和一切超参数仅用本组 **seen validation**。val U+/U− 仅在冻结选择规则后用于诊断，test 只用于一次最终评价。`unseen` 始终指下游任务训练未见，不声称通用预训练未见。不要用原始全量 Charades-STA 微调严格模型。

| 组别 | 保留语义 | 主要作用 | 状态 |
| --- | --- | --- | --- |
| A0 | v1 `open/close` + 原 16 组合 | 固定历史参照；动作和组合分别报告 | 已完成，原包不变 |
| A1、A2、A3 | 三组互不重叠的完整动作，各组从候选表自动筛选并经语义 QC | 三次新的动作级重复 | 待选定 |
| C1、C2 | 两组互不重叠的动作–物体组合；各组成分在该组训练中仍有出现 | 两次组合级重复与配对诊断 | 待选定 |

上述是目标矩阵，**不是预先指定具体动作或声称这些组已有足量样本**。A1–A3 尽量覆盖不同语义类型，例如移动、物体操作、饮食、穿戴、清洁/家务；不让单个反义动作对定义整组。C1–C2 独立于动作级主实验构建，不整体保留动作。新构建器只从冻结的 `--split-spec` 读取保留语义；动作组不自动附加组合。A0 按原样分析，不回写或重训。

若候选表和试构建表明三组动作或两组组合达不到预先冻结的质量/规模门槛，记录失败原因并缩小论文主张；不可在查看模型测试结果后挑选“更显著”的划分。也不把所有动作合并成单一大 U 集合来代替逐组重复。

## 3. 先生成候选表，再冻结划分

候选统计以**原始正例**为母集，使用与 v1 相同的语义解析器和视频划分；不能从已过滤的 v1 正式训练集统计，因为其中已删掉 `open/close` 及组合。外部 [v1 数据交接](/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v1/HANDOFF.md)给出了本机真实输入：`/home/guoxiangyu/paper/Openword/data/raw/charades_sta/charades_pos_train.jsonl`（12,404 条）和 `charades_pos_test.jsonl`（3,720 条），来自 GMR 的 Charades-STA `pos_only` 导出。构建时还需`/home/guoxiangyu/paper/Openword/data/raw/charades/annotations/`、`/home/guoxiangyu/paper/Openword/data/raw/action_genome/annotations/`、`/home/guoxiangyu/paper/Openword/external/verbnet/verbnet3.4/`；原视频归档在 `/home/guoxiangyu/paper/Openword/downloads/Charades_v1_480.zip`。这些路径须在运行记录里写成实际解析后的绝对路径及哈希。应缓存每条原始正例的规范化 graph、句中所有动作 `_verbs`、所有事件对 `_pairs`、解析标记和来源哈希，随后对每个候选重复使用同一解析结果。先形成 `action_candidates.csv` 与 `composition_candidates.csv`，字段至少包括：

| 层面 | 必需字段 |
| --- | --- |
| 数量 | 原训练池/验证池/测试的正例数、互异视频数、互异来源 qid 数；对动作同时统计“主谓词为该动作”和“句中任何动作命中”数量 |
| 多样性 | 不同物体数、前 1 物体占比、物体分布、动作语义类型；组合同时记录其动作及物体在移除组合后的训练留存数 |
| 可构造性 | 按现有编辑规则预计的 U− 候选数、同视频同来源 U+/U− 潜在配对数、编辑类型、冲突过滤后数量；**候选数不等于已确认负例数** |
| 质量 | 解析抽样的正确率/错误类型、同义词或词形别名归并组、歧义对象/角色、是否落入明显相反动作对 |

统计表必须同时保留未通过筛选的候选及原因。先按统一的**事前规则**筛掉测试正例或视频太少、物体几乎单一、解析错误明显、与其他候选互为同义/词形变体、负例与配对几乎不可构造的动作；具体数值门槛根据完整候选分布在看模型结果前写入 `selection_rules.json`。组合候选另外要求，移除该组合后，动作、物体以及其他相关组合在训练池仍有足够实例，防止“组合级”实际退化成动作或物体级未见。对于可能无法生成反义负例的动作，允许通过对象替换或同视频重组产生 U−；若现有规则无此能力，应先扩展候选生成器并做语义/视频审查，不能降低缺席证明标准。

选组程序以冻结规则、固定随机种子和候选表为输入，优化组间动作/组合不重叠、语义类型覆盖、U+/U− 和配对的预计规模接近、不同物体分散；输出带选择理由及舍弃理由的 `split_specs.json`。之后人工只做解析和语义等价 QC，修改须记录版本与原因，并在训练/测试评分前冻结。A0 `open/close` 不参与新动作组；同义及粒子变体跨组禁止。各组最终规模在正式复核后再定，报告每组差异，不强行重采样到 v1 规模。

在任何模型预测出来之前，把最低正式门槛写入 `selection_rules.json` 并冻结：每组测试 U+、复核后的 U−、互异视频数、同视频同来源且同一新颖性轴的配对数、配对覆盖率（已配对 U+ / 全部 U+）、每组最大单动作或单组合所占比例。C1/C2 的**配对数和覆盖率均是准入门槛**，零配对不得作为组合级重复；A1–A3 的单动作占比也须过门槛。候选阶段的编辑机会只是上界，正式门槛按视频复核后重新判定。达不到门槛的预定组记为数据可行性失败，不依据模型结果替换。

## 4. 每组数据构建与质量关口

1. 从同一份原始正例/视频划分和冻结 spec 构建该组独立清单。含保留动作或组合的原训练正例完整移除；保留动作需要检查**句中任何动作**及其别名/粒子形式，而非只看 `semantic_graph.action`。重新计算该组 seen inventory。对组合组验证组成动作和物体仍 seen，且 held pair 不在训练中。
2. 独立生成 `train/val/test` 四象限候选以及同视频、同来源 U+/U− 对。配对需在正式发布后逐对校验：同一视频、同一来源、两条都属同一新颖性轴、正例有原时间窗、负例为空窗且已视频复核。当前 v1 贪心配对只要求双方为 U；第二阶段要补充轴一致性约束、组合级配对生成和每组 `pair_coverage` 审计。
3. 对所有新负例按整段视频逐 qid 判 `absent/present/ambiguous`，记录 reviewer、决定和备注；只发布已确认 absent。可复用**完全相同视频与查询**的既有逐 qid 审查记录，须写明来源和哈希；v1 的全局 attestation 不能自动覆盖新候选。对解析疑点做抽样复核并隔离已知 `dress|front` 一类错误。元数据无冲突只说明“未找到正证据”，不等于视频缺席。
4. 校验每组 train/val/test 视频互斥、qid 唯一、held-out 泄漏为零、train 无 U、所有负例有复核记录、正例时间窗合法、组合组成部分 seen、配对引用有效。发布 `statistics.json`、审查来源、规则及输入哈希、SHA-256 manifest；若任一核心条件失败，不进入模型训练。

冻结各组 spec 后，从各组训练候选中取**所有划分均为 S−、且其来源 S+ 在所有划分均保留**的 qid 交集，形成经视频复核的公共训练负例池。优先让 A1–A3 使用同一池、C1–C2 使用同一池；先检查公共池规模与动作/物体分布，再决定是否还需各组补充负例。公共池不足时，完整记录每组新增 S− 的数量、动作与物体分布，并在跨划分比较中说明这项训练差异。公共池只是减少混杂，不能使不同划分的正例训练集完全相同。

数据**生成与发布根目录**按本项目约定放在 `/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v2/`，不覆盖现有 `semantic_existence_v1`。v1 中间产物位于 `/home/guoxiangyu/paper/Openword/data/processed/semantic_existence/`，可用来核对字段和流程；新划分必须从上述原始正例重新构建，不能把 v1 已过滤的中间文件当作原始母集。建议布局：

```text
/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v2/
  selection/action_candidates.csv
  selection/composition_candidates.csv
  selection/selection_rules.json
  selection/split_specs.json
  A1/{train,val,test,matched_u_pairs}.jsonl
  A2/...
  A3/...
  C1/...
  C2/...
```

每组目录还应包含 inventory、statistics、review provenance、manifest 和按动作/组合展开的计数。构建过程的大文件可放该根目录下的 `work/<split_id>/`；正式读入只使用冻结的发布子目录。模型 checkpoint、预测和诊断结果仍放仓库本地 `results/semantic_existence/multi_split_v2/<split_id>/<model>/`，避免与数据包混放。运行脚本必须显式传入绝对源数据与目标路径。`build_semantic_existence.py` 原本支持 `--held-actions`、`--out`，但只通过数量参数自动选组合；新划分统一用 `--split-spec`。`package_semantic_existence.py` **已有** `--data`、`--out`，其默认值才指向 v1；`validate_release.py`、`audit_text_only.py` 原本硬编码 v1，需支持显式发布路径。仓库内 `data/raw/charades_sta` 和 `data/processed/semantic_existence` 在本次检查时不存在；数据实际位于上一级 `/home/guoxiangyu/paper/Openword/data/`，不要让脚本默认路径误导复现。

## 5. 模型实验与指标

先只重复三种**严格 GMR**：Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR。每个新组从相同非任务微调初始化独立训练，沿用 seed 3407、100 epoch、特征、优化设置、seen-val 选模和 seen-val 阈值规则；不要从 A0 或其他组的任务 checkpoint 接着训练。阶段二暂不重复 E6、定位-only 或多种子实验。若本阶段发现重大机制歧义，再另行设计辅助实验。

| 指标 | 每组/每轴报告口径 |
| --- | --- |
| 存在区分 | seen AUROC、unseen AUROC、两者差（百分点）；同时列 S+ FRR、S− RR、U+ FRR、U− RR，避免 AUROC 掩盖不同错误方向 |
| 同视频配对 | 复核后的 matched-U PairAcc，平局计 0.5；报告配对数、覆盖 U+ 比例，并给按视频聚类的 95% bootstrap 区间；无配对写 N/A，不以无配对集上的 AUROC 替代 |
| U+ 定位 | 同一 GMR checkpoint 的 raw R@1@IoU 0.5 与 seen-val 阈值硬拒绝后 R@1@IoU 0.5，报告 raw→hard-gated 损失；硬拒绝是诊断操作，不混称为官方 GMR 软 gate |
| 同样本跨划分 | 先在发布 test 中找 qid、视频、查询、真值及正例窗口完全相同，且在一个划分为 U、另一个为 S 的行；同一 backbone 分别计算存在分数的 seen−unseen 差，以及 raw/硬拒绝 R@1 差。U+ 与 U− 分开，动作与组合分开，按视频聚类给区间 |

所有结果首先按 `unseen_action` / `unseen_composition` 分开，再按预先固定的组做**等权组平均、范围和逐组表**；可补充按视频/查询加权值，但不能只报合并 U 集。跨划分同样本对照固定了测试内容，仍会同时改变训练正例分布及可能的负例组成，因此是更强的关联证据，不能单独称语义新颖性的纯因果效应。比较 A0 与新组时需指出 A0 的组合级无 matched pair。对每组的文本-only 诊断和 query 长度/对象分布也应复跑，以检查语言捷径与分布偏移；组合级尤其要同时报告 U+、U− 和 pair 的可用数量。置信区间按视频聚类，仅反映测试样本不确定性；单种子训练限制单独写明。

## 6. 执行顺序与完成判据

1. 找齐原始正例和依赖，产生候选表及解析 QC；审定并冻结规则与 split specs。**在这一步以前不指定 A1–A3/C1–C2 的语义内容。**
2. 参数化构建、审查、打包、验证和特征准备脚本；先做一组端到端试构建，检查组合级 U− 与配对能否生成。试构建数字只用于数据可行性判定，不用于选择模型效果好的组。
3. 构建并逐条复核各组负例，打包至上述外部 `data/release` 路径；先通过所有质量关口并冻结 manifest，再启动三模型训练。
4. 每组独立训练与测试；保存训练/评测退出码、选中 epoch、阈值、逐查询预测、评测脚本版本与配置。汇总每组、每轴结果和失败/缺失原因。
5. 仅当多个预先选定的动作组及组合组在三个模型上均有可解释的 seen→unseen 退化，且配对与 U+ 定位拆解支持相应结论，才写“多种未见语义划分上可重复”。若组间分歧大，直接报告异质性及样本/解析/负例质量限制。

本方案的最小交付物是：候选表、冻结选择规则与划分 spec、每组经复核的数据与校验报告、三模型逐组结果、动作/组合分轴总表。第二阶段是否真的支持更宽的结论，由这些预先固定的组和正式结果决定。

## 7. 候选阶段实施记录（历史状态）

原始正例候选表、选择规则、初选失败记录、替代组选择记录及冻结哈希均已保存在 `/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v2/selection/`。123 个动作、1,221 个组合经过统计；初选 A2（`eat/drink`）仅有 11 对候选配对，初选 C2（`drink|cup/glass/bottle`）仅有 1 对，均未通过事前配对门槛。替代组由同一候选表的共享对象/组合规则提出，初选记录保留在 `split_specs.initial.json` 与 `candidate_feasibility.initial.json`；最终 `split_specs.json` 和 `frozen_selection_manifest.json` 在任何新模型结果出现前写定。

| 最终组 | 保留语义 | 候选 U+ | 候选 U− | 候选同来源配对 | 候选配对覆盖 |
| --- | --- | ---: | ---: | ---: | ---: |
| A1 | `put,take` | 465 | 1,119 | 312 | 67.1% |
| A2_alt | `drink,pour` | 168 | 312 | 79 | 47.0% |
| A3 | `run,walk` | 192 | 594 | 129 | 67.2% |
| C1 | `sit|bed, sit|chair, sit|couch` | 162 | 270 | 144 | 88.9% |
| C2_alt | `close|box, close|cabinet, open|box, open|cabinet` | 115 | 254 | 33 | 28.7% |

这些 U− 和配对数是**视频复核前的上界**。五组候选都通过 `scripts/validate_semantic_existence.py --data <work/split>` 的结构检查，以及冻结规则下的候选质量门槛。正式复核后必须重新运行门槛检查，失败组仍按失败报告。C2_alt 含开/关相关组合，因此组合轴的语义多样性仍有限，论文须逐组呈现，不能只给组合轴平均值。

动作组三组共享候选 S− 池取自 4,243 条共同合格行，组合组两组取自 3,635 条；每轴按固定 SHA-256 顺序截取 1,500 条，与 v1 训练负例量级接近。去重后的五组复核队列有 6,976 条，其中 2,485 条与 v1 已发布的负例在 qid、视频、查询、来源和语义图关键字段上完全相同，可沿用 v1 **原有批次确认来源**；其余 **4,491 条新候选**在 `selection/negative_review_template.csv` 等待逐条视频决定。`selection/parser_qc_template.csv` 另有 156 条待核对的语义解析抽样；这两份空白表不能视作复核已完成。正式复核后，工具会保留旧行的原状态，只给新逐条确认行写 `manual_video_review_confirmed`。

候选级同样本跨划分清单在 `selection/cross_status_candidate_manifest.csv`：相同 qid、视频、查询与真值从 U 变 S 的有向比较共 16,232 行；其中新组作为 U 的正例涉及 1,066 个互异 qid。负例清单仍是候选，正式分析必须重新从已复核的发布包取交集，并按模型分别加入存在分数与 raw/硬拒绝定位指标。工具为 `scripts/analyze_cross_split_status.py`，按视频聚类给 95% 区间。

下一道不可跳过的关口是完成上述视频与解析复核，然后运行 `scripts/review_semantic_multisplit.py --reviews <completed.csv>`，重新形成共享的已确认 S− 池，执行 `scripts/audit_multisplit_feasibility.py --reviewed --parser-qc <completed.csv>`；通过后才可用 `scripts/package_semantic_multisplit.py` 发布到本文件指定的外部目录。`scripts/validate_release.py --release <split>` 和 `scripts/audit_text_only.py --release <split>` 已支持新路径。各模型仍须单独准备该组的 CLIP 文本特征与 seen validation 视图，再沿用 v1 的 100 epoch 配置分别训练。当前没有启动新模型，避免将未经确认的负例输入正式实验。

完成复核后，在仓库根目录以**另存的**两份已填写 CSV 运行下列入口；它会导入决定、形成两个经复核的公共 S− 池、检查全部正式门槛、打包并校验五组，任一门槛失败即停止：

```bash
export NEGATIVE_REVIEWS=/path/to/completed_negative_reviews.csv
export PARSER_QC=/path/to/completed_parser_qc.csv
bash scripts/finalize_semantic_multisplit_v2.sh
```

随后每组使用 `scripts/prepare_charades_semantic_existence.py --release <v2组目录> --output <该组特征目录>` 准备文本特征；原正例文本特征位于本机已有的 Charades `txt_clip` 目录。设置 `VIDEO_ROOT`、`GMR_PYTHON`、`FLASH_PYTHON` 后，逐组运行 `bash scripts/run_semantic_multisplit_100ep.sh A1 launch` 等命令。该入口会先检查发布包哈希、特征与结果目录，再用原严格 GMR 的 100 epoch 设置启动三个 backbone；各组依次启动，避免 GPU 资源互相争用。跨划分正式分析使用发布 test 与每组对应模型的预测文件，配置可参照 `selection/cross_status_candidate_config.json`，并填入各组 seen validation 阈值。

## 8. 正式发布和训练状态

数据负责人对哈希绑定的当前批次作出全局人工核对确认，涵盖 4,491 条新负例与 156 条语义解析样本；没有逐 qid 决定表，发布元数据明确保留这一粒度。五组都通过正式质量门槛并打包，A1、A2_alt、A3、C1、C2_alt 的标注和选择资料均已纳入仓库。15 个模型以 seed 3407、强制 100 epoch 完成训练；各组测试预测均精确覆盖其 test qid，并已通过四象限诊断、官方评分、text-only 对照和查询分布检查。跨划分相同 qid 的 U→S 对照已按动作轴、组合轴分别完成。测试评测入口为 `scripts/finalize_semantic_multisplit_group.sh <组名>`，逐组结果及按视频 cluster bootstrap 区间见[多划分结果报告](reports/semantic_existence_multisplit_results.md)和机器可读指标目录。
