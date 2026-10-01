# 事件绑定证据与存在定位共同泛化：研究方案

日期：2026-10-01。本文记录执行前的研究设计。A/A1/B 阶段之后的当前状态和测量值见[实验报告](report/REPORT.md)。

**阶段记录：** 本方案覆盖的 A/A1/B 已执行结束；本段描述执行前冻结的范围。逐项观测值见[实验报告](report/REPORT.md)。精确执行边界见 [MINIMAL_VALIDATION_SCOPE.md](MINIMAL_VALIDATION_SCOPE.md)，当前状态见 [RECOVERY_PROMPT.md](RECOVERY_PROMPT.md)。

修订依据：执行前已完成[八篇论文全文/源码核验](research/LITERATURE_REVIEW.md)与[工程输入核验](research/PROJECT_SOURCE_AUDIT.md)。本轮实验执行状态见[实验报告](report/REPORT.md)。

## 1. 目标与定位

在冻结视觉/文本特征、严格 downstream S-only 训练下，检验动作—实体绑定证据是否能够迁移到未见动作或组合，并同时提高 GMR 的存在排序与时间定位。真实 U+ 应接受、真实 U− 应拒绝，不能用语义熟悉度或查询 OOD 检测替代事件存在判断。

研究定位为已有绑定思想在严格未见语义存在判别中的机制验证及可能的方法扩展。不是首次建模动作—实体关系，也不是首次将局部相关性用于拒绝。先验证绑定，再验证相对于 primitive 的证据盈余，最后验证共同输出。

IAE-VTG 已分别评估负查询拒绝及 Novel-C/Novel-W 组合泛化；不能只用 binding+两个输出+组合泛化界定差异。先审计其输入、训练与评价协议，实际差异必须由 primitive 条件视觉增量、受控 S-only→U+/U− 以及共同收益获得。论文没有公开足够实现细节时注明无法全面对齐，不因术语不同断言本项目首次。

不继续以 local sigmoid → 统一 absolute scale → existence 为主线；跨查询可比较的最终决策仍需验证，但不预设绝对分数校准是核心机制。

## 2. 两项已有工作的事实依据

| 来源 | 已有结果 | 支持的结论与边界 |
| --- | --- | --- |
| 第一阶段六组 A1/QD、seed3407 | Adapter 在独立正例 VTG 的 unseen R1@.5 从 .2065 到 .2624；GMR unseen AUROC 从 .5309 到 .4771 | 定位单项改善不能替代存在/定位共同改善；未证明绑定缺失 |
| 第二阶段三族诊断 | pseudo baseline 等权 AUROC .5873，raw R1@.5 .2936；canonical 跨族存在排序证据不充分；稳定共享块梯度冲突未达到规则 | 不以优化冲突或简单标尺问题为既定瓶颈 |
| 固定候选与支持桥接 | max foreground 的 pseudo 等权 AUROC .5037；foreground×候选几何一致性为 .5315，raw .2685，均劣于原读出 | 该具体几何桥接路线已失败；不能把候选置信度或一致性直接当事实证据 |
| 冻结时序表示读出 | early mean pseudo AUROC .6130，纯文本 .6264；GT 条件局部读出有有限信号，但无 GT 稳定视觉支持未建立 | 改读出没有证明恢复可靠视觉支持；局部信息不能被宣布完全消失 |

数据来自原项目的[第一阶段最终报告](../correspondence_generalization/2026年9月30日_正则化与残差适配的未见动作泛化实验/evidence/report/FINAL_REPORT.md)、[第二阶段决策](../correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/DECISION.md)、[支持桥接](../correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/support_bridge_analysis/REPORT.md)及[时序表示报告](../correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/temporal_representation_analysis/REPORT.md)。

三族不是独立重复试验，有共享视频；sit 停于 77 轮，使用原 seen-only best（编号11），不补训练。时序报告使用 native 精度及自身口径，与旧四位输出统计不混接。18 个诊断读出器确实拟合过，不能称其全部参数更新为零。

## 3. 研究问题与可证伪假设

- **RQ1：primitive 是否可迁移？** 动作相关的运动响应、实体相关的外观响应在 pseudo 上是否各有受控信号？若输入中无法读出，不直接归因于缺少绑定。
- **RQ2：joint 是否超越独立响应？** 在原标签确认的事件正负例中，显式 joint 是否优于 holistic、primitive 加和以及简单同时间 AND？
- **RQ3：盈余是否必要？** 在 joint 已有效的前提下，消除 primitive-only 可解释部分是否进一步提高 U+/U− 排序？不预设残差优于 joint。
- **RQ4：是否可共同使用？** 无 GT 的同一 map 能否改善 AUROC 与 raw R1@.5，而不是仅在 GT 条件或候选 oracle 中有效？

H1：当前 holistic 表示更容易对单个相关概念响应，joint 带来额外视觉条件判别。H2：该额外响应在 held-out 语义上仍成立。H3：盈余可帮助排除 primitive 相关但事件不成立的假阳性。H4：同一证据场具有定位与存在共同作用路径。四项分别检验，任一不成立都允许缩小或改变机制。

增加前置问题：动作理解是否已经存在于原冻结特征？RCORE 的 object-driven verb shortcut 与 Invert4TVG 的定位/动作理解分离提示，分解和交互不保证使用运动。该问题与绑定缺失独立，失败时先记录表示/读出/采样限制。

“动作与实体同时出现”与“动作由查询指定实体实施/作用于指定对象”要区分。全局 clip 特征只能先检验时间层面的组合支持；无对象级证据时，不宣称验证了实体身份、施事/受事或物理因果绑定。

## 4. 协议与数据边界

- **用户明确的代码隔离要求：** 全部新增训练/评测/部署代码、脚本和配置只能写入本新目录（原 `new`，现 `event_binding_generalization`）。日志、缓存、临时构建和模型产物也写入本目录。其他目录代码只读，需要适配则复制或封装到本目录并记录来源；不能修改原项目 `code/`、vendor、模型源码或外部部署文件。原项目 `plan/` 仅补充 Markdown 方案与入口文档。
- 初始范围：A1/QD、seed3407，沿用 throw/open_close/sit 三个训练侧留族视图及原 seen-only best。每族仅用其原 train 拟合新增诊断模块，seen 用于既定选择，pseudo 用于研究验证；真实 U/test 不进入开发。
- 严格 S-only 指下游训练不使用目标 U 标签；冻结骨干的预训练暴露不宣称为零。held-out 动作与 held-out 组合的定义分别记录，不把词形隔离写成完整概念隔离。
- 原发布标签、时间窗、特征、checkpoint 与旧结果只读。仅使用原 S+/S−，不新增跨视频 absence 标签，不将 S+ 窗外全部当负例。
- 原 S− 只确认完整事件缺席，不能推出动作缺席或实体缺席。原 S+ 的事件窗不自动提供逐 primitive 精确边界。
- 只有原注释/已有可靠标注能确认的“primitive 存在但事件不存在”才进入该硬负例分层。仅 noun/verb 文本重合的组标为语义匹配代理；不能写成已确认视觉绑定负例。
- canonical 控制使用相同实际文本特征与 mask，而非仅相同字符串。新增分解分支也需统一其输入。
- 时间错位、stream 重配及查询替换属于机制扰动。除非有独立标签依据，不把它们制造成 absence 监督或反事实准确率样本。

## 5. 分阶段验证

### A：输入、语义分解和负例覆盖审计

先只读检查 CLIP/SlowFast 原特征的时间轴、维数、归一化、截断及双流对齐；核对文本 token 与原查询词的可映射性。CLIP 偏外观、SlowFast 偏运动只是归纳偏置，两者不保证语义纯净。

本轮源码/一个 train 样本确认实际拼接为 `[CLIP 512 | SlowFast 2304 | TEF 2]`，由 `v_feat_dirs` 决定而非 `slowfast_clip` 字符串；原模型在拼接后统一投影。因此新分支须在统一投影前保留两流，TEF 单独控制，不将融合 hidden 的任意坐标当两种 primitive。样本两流长度29/30，min_len 截断只保证长度一致，不证明时间对应。此样本检查不是完整阶段 A 的覆盖审计。

冻结 action/entity/角色提取规则，报告解析失败、多动词、多实体、无显式实体和歧义的覆盖，保留完整 query 基线。不能看 pseudo 结果后挑 token 或 noun–verb pair。若缓存 token 不能可靠对齐，优先选可验证的 span 映射；重新提取特征会改变协议，须先明确新范围，不能暗中引入更强模型。

已检查的 text NPZ 只有 `last_hidden_state`，无 token IDs；原 loader 截前32 token。核对同 tokenizer 的 BPE、SOT/EOT、截断和正负缓存来源，在新目录保存 offset/mask；不把词位置当 token 位置。角色 token 带完整句子上下文，不能据 verb/noun mask 自称语义 disentanglement。

统计原 S− 的组成：动作不匹配、实体不匹配、primitive-only 代理、可靠绑定负例、无法归类；证据不够时保留 unknown。若绑定硬负例或相同实际文本控制覆盖不足，结论记未决，不用自动生成负标签填满。

产物建议：AUDIT_FREEZE.json、FEATURE_AUDIT.json、QUERY_DECOMPOSITION.jsonl、NEGATIVE_COVERAGE.json、AUDIT_REPORT.md。当前均未生成。

阶段 A 还须审计负例语义轴和组成：现有 throw/open_close/sit 都是留动作族证据，不能单独支撑“组件已见而组合未见”的机制。可先从原 A1 S train 元数据审计可留出的 pair 及组件覆盖，只有明确新的训练侧组合视图定义后才比较；不自动启动 C1/C2 正式训练，不使用真实 U 选择 pair。

### A1：动作可读性与静态捷径门槛

在原 S+ GT 内做 motion-only segment→verb 小 probe，词表和样本只取原 S train；对照 appearance-only、时间均值、单位置/静态内容以及 masked-query text-only（不能把答案 verb 自身输入该控制）。同实体不同动作和不同实体同动作分层，报告 coverage；组件含 held-out verb 时不能把 U 类标签拟合到闭集分类头。可迁移 verb 的检索/相似性评价需先固定由 S 定义的 scorer，不能拿 GT verb 拟合测试类别。

该 probe 是 annotation-derived 动作可读性诊断，不是 Invert4TVG 的完整生成式 VC/AR/VD 复现，也不是无 GT existence。motion-only 无明显信号不证明所有非线性读出都无信息；若静态/物体控制同样有效，暂不将后续 J 的增益归于运动绑定。

clip 间 order 控制与 cross-stream alignment 控制分开：两流共同逆序/乱序检验时间次序；单流错位检验局部对应。SlowFast clip vectors 逆序保留 clip 内原运动方向，不等于像素视频倒放。持续实体、周期/方向无关动作分层，不为所有扰动赋 absent 标签，不把“分数下降”记作已验证反事实准确率。

### B：冻结骨干上的最小证据比较

原模型与特征冻结，当前范围仅拟合 H/P/C/J/T 小模块。所有拟合都计为参数更新；先验证读出，不直接全模型重训。下表 R 保留为后续候选，本阶段不执行：

| 臂 | 时序证据 | 要排除的解释 |
| --- | --- | --- |
| H | 完整 query × 双流的 holistic 小读出 | 新监督、非线性容量或局部 map 本身有效 |
| P | 动作响应 + 实体响应的加性 primitive-only 读出 | 分解或双流本身已足够 |
| C | 同时间动作/实体响应的简单 AND，例如固定乘积 | 共激活已足够，不需要额外绑定模块 |
| J | 显式局部动作—实体交互读出 | joint 是否超越 H/P/C |
| R | J 加 primitive-only 对照形成的盈余机制 | 盈余是否超越 J，而不是包装已有 joint 收益 |
| T | 仅文本、相近读出容量 | 查询先验或语义熟悉度解释收益 |

补充最低机制控制：motion-only、appearance-only，以及静态/时间均值的证据读出；同事件监督、相近容量与同一主聚合。H 本身提供 local holistic evidence map，再单列其 pooled scalar（CausalVTG-inspired）读出，区分局部证据流与绑定增量。前置动作 probe 与这些 event-existence 控制任务不同，不能以 probe 准确率代替 AUROC。

J 的实施硬约束：单个 noun–verb 对也必须直接依赖 raw visual values/residual；多对在 pair-conditioned visual interaction 上聚合。公开 IAE 公式的 pair softmax+marginal-only 路径存在单对退化风险（本轮公式推导，非作者代码 bug 结论）。可设按公式构建的 IAE-inspired 结构控制，明确非官方复现；不以退化控制的失败全面否定论文。固定 query 换视频的 map 响应检查只是非退化检查，还需真实标签的视觉条件判别。

当前只比较 H/P/C/J/T，J 获得支持后也不自动执行 R；仅给下一阶段建议，不因 J 失败转而扫残差系数。基线原存在头与原定位输出另保留为参照，不计作新拟合臂。

当前实施分两轮：A/A1 确认可测性；B 只执行 H/P/C/J/T 与必要单流/静态控制。R 必须另属后续阶段，不一次铺开多种 temporal 模块、全套 auxiliary 或多个 null。

统一输入、原事件标签、时间监督可用性及聚合协议；记录各臂参数量、训练轮数、呈现条数和实际耗时。H 提供相近容量控制，避免把更大网络收益归于绑定；不宣称完成此前已排除的同预算成对核验。具体宽度、优化器、轮数上限、聚合及选择准则须在执行前一次冻结，当前不虚构硬件预算或可运行配置。

使用原 S+ GT 的局部事件支持监督和原 S− 整段 event absence/MIL 监督，所有臂公平共享可用监督。GT 只用于训练和单列诊断，实际正负例均使用相同的无 GT map 聚合。窗口标签监督的是事件，不保证 primitive 分支学到了纯动作/纯实体。

R 的 J 与 primitive/null 必须在同一时间索引或候选窗上比较，不先分别取各自最有利峰值再相减；null 的预测单位和拟合只由 S 决定。残差不是已验证概率、PMI 或因果证据，原 label 只确认 event，不为残差赋新的真值。

主要报告 pseudo 无 GT 存在 AUROC、相同实际文本 PairAcc、视频/查询覆盖。局部定位先报告非 oracle 的选窗/候选排序作用；GT 条件 AUC、峰入 GT 仅辅助，不替代 R1。动作/实体干扰、时间错位敏感性只作为解释证据，与分布外扰动限制同报。

本次B必须补全两项：其一，原标签/元数据或S_train预定义的primitive支持匹配/分层，检查primitive已相关时J是否仍有增量，分数代理不得冒充确认的binding标签；其二，将H/P/C/J的map用同一seen冻结读取规则对原候选作candidate-specific重排，评估完整pseudo正例raw R1@.5，GT只计算指标。这是冻结模型输出诊断，不是C阶段的联合训练。条件证据或覆盖不足记未决，不以总体AUROC取代科学问题。

### C：共同输出的最小干预

仅在 B 支持 joint 的视觉增量后，冻结具体 METHOD_SPEC 和普通控制，研究同一 map 对候选排序、边界表示与存在输出的作用。先采用原候选上的 map 窗内汇聚重排；它不能修复全部候选缺失。需要新边界回归时另立最小变体，不把 oracle 覆盖当预期收益。

对照至少包括原模型、H 共享 map、J 共享 map，以及 B 支持后才加入的 R 共享 map；另做只接定位、只接存在两个作用路径消融。输入与原任务监督保持；不同时引入 ISA 匹配修改、额外教师、梯度协调和多个新损失，以免收益不可归因。

增加 map bypass/primitive substitution：保持输出模块容量，对照移除 map、用 primitive map 替换，明确各任务的读取点。若采用可训练 shared map，detach 消融仅检验训练耦合；零填/遮挡属于分布外敏感性，不自动证明因果中介。需要辅助训练时仅选一个候选（原 S+ annotation-derived verb recognition），单独比较 J 与 J+aux，不一次加入 TORC/CPR/VC/AR/VD/MoE。

同一 map 不要求两个任务使用同一个 scalar：定位保留时间结构，存在执行固定的全局聚合。所有正负 query 使用同一长度处理和有效时间 mask。不能仅给全 query 候选乘一个共同 scalar 后宣称 raw 排序改善。

### D：冻结后的确认与迁移范围

训练侧开发成立后才形成正式 U 确认范围；真实 U 只评一次冻结方案，不选公式、epoch、阈值或族。独立正例 VTG 验证定位迁移，移除存在任务头，不使用 S−/存在损失。两轨结论分别报告；没有 VTG 新收益时仅声明 GMR 范围。

## 6. 统计、指标和成功条件

- GMR 共同主要终点：存在 AUROC 和 raw R1@.5；gated R1@.5 为关键最终表现；R1@.7、FRR、RR 及 hard 指标辅助解释。只提高接受率不算成功。
- 沿用既有标准：主要终点候选对基线的 paired 增益显著为正；seen 不劣界限 1 个百分点，FRR/RR 恶化界限 3 个百分点，raw-correct 硬拒恶化界限 5 个百分点。主要终点使用既有 97.5% 区间口径，其他 95%；在确认阶段预先冻结 gate、阈值与检验实现。
- 开发分析均为探索性，已看过旧结果；不得改称预登记的独立确认。1000 次、seed3407、共同原视频 bootstrap，跨族视频使用同一乘数，族等权。PairAcc 明确 query/pair 权重与端点权重；组合对数不是独立样本数。
- 报告候选对 baseline、J 对 H/P/C、R 对 J 的配对差值及覆盖。族间不按有利对数加权；单族支持与跨族未决分别陈述。不用 U 不变而 S 降低的 gap 缩小作为改善。
- 真实联合成功需同时满足存在/定位共同改善及护栏。B 中只读出存在增量意味着机制线索成立，不能提前声明共同方法有效。

## 7. 停止与分支规则

| 观察 | 决策 |
| --- | --- |
| primitive 输入/覆盖不足 | 记录测量或表示限制；不宣布绑定缺失 |
| J 未优于 H/P/C | 停止“显式绑定必要”这一版本，接受简单机制或换机制 |
| J 有效、R 无效 | 保留 joint，放弃盈余作为核心贡献，不扫残差系数挽救 |
| 全局 AUROC 上升、固定文本控制无支持 | 不归因于可迁移视觉绑定；检查文本先验和覆盖 |
| 只有 GT 条件/峰入 GT 有效 | 无 GT 选取问题仍未解决，不进入共同成功声明 |
| 定位有益、存在不益，或反之 | 限定单任务发现；不符合本研究共同目标 |
| U+ 接受上升但 U− 拒绝明显恶化 | 判为共同目标失败，不通过 U 阈值挽救 |
| 硬绑定负例覆盖不足 | 只能验证普通事件存在，绑定特异性保持未决 |
| 单对 J 不依赖视觉、或只有 appearance/static 控制也达相同收益 | 修正实现或缩小为静态相关性发现，停止运动绑定解释 |
| 只有动作留族，未验证组件已见的组合留出 | 限定未见动作结论，不称组合绑定泛化已成立 |

## 8. 最近邻与创新边界

- Shiwen Zhao 等，2026，**IAE-VTG: Interaction-Aligned Action–Entity Video Temporal Grounding**：动作/实体对齐到运动/外观流，binding用于proposal/matching；Table VI 已做 NA-VMR 拒绝，Table IX 已做 Novel-C/Novel-W。本方案需验证 primitive 条件视觉增量及相同严格协议的差异，不能仅以共同输出区别。官方实现未取得，单对退化是公式推导。[原文](https://arxiv.org/html/2609.09736v1)
- Jianfeng Dong 等，NeurIPS 2024，**Temporal Sentence Grounding with Relevance Feedback in Videos（RaTSG）**：已联合帧/视频相关性与拒绝定位。本方案不能以局部证据服务两个输出作首次贡献；差别应落在未见语义下的组合证据。[原文](https://proceedings.neurips.cc/paper_files/paper/2024/hash/4b96695d9885f038110b8b16ef50e882-Abstract-Conference.html)
- Geo Ahn 等，2026，**EVIDENT: Routing MLLM Adaptation through Entity-Grounded Visual Evidence for Cross-Domain Video Temporal Grounding**：实体 slot、绑定蒸馏与 evidence gating 是近邻；其对象级 MLLM/视觉域迁移机制不同于本项目冻结 clip 特征及未见语义存在判别。[原文](https://arxiv.org/abs/2605.26104)

用户另指定的 RCORE、Invert4TVG、ActPrompt、CausalVTG、HRVTG、EviDETR 已完成全文及可得源码核查，详见[八篇重点清单](research/LITERATURE_REVIEW.md)。RCORE官方TORC源码已核查，CPR不是primitive残差；ActPrompt需要encoder内部patch/prompt；Invert inversion不是时间倒放；CausalVTG提供pooled relevance普通控制；EviDETR服务MR/HD，不能替代existence验证；HRVTG已公开PDF和代码，但TTA不满足主轨固定推理。EVIDENT作者官网列NeurIPS2026，空间dense tokens+DINOv2教师不直接适配原pooled输入。

以上原始来源于 2026-10-01 本轮核查。尚不声称穷尽文献或通过新颖性审查。旧报告引用的 Learning to Refuse 官方页本轮访问失败，不据其未获取全文新增技术判断。

## 9. 路线评估与执行风险

判断：**Accept with Revisions，值得先做机制验证，尚不足以承诺新算法。** 最大风险是与 IAE-VTG 重叠，以及无法从 pooled clip 特征/原事件标签验证真正实体身份绑定。防线分别是 J/H/P/C/R 的严格未见语义对照，以及按标签覆盖和空间粒度限制结论。

五维定位：Higher 6、Stronger 7、Broader 6，均为机制推断，未获本项目实测确认；Faster 5、Cheaper 5，没有加速/降成本证据。强项是未见语义鲁棒性，普通精度与双任务共享仍需验证。不把本路线包装为范式转移：它质疑“概念相关即事件成立”，但绑定和拒绝已有近邻，没有已证实的新技术周期或领域级影响依据。

属前沿机制探索；采用小模块验证压缩迭代范围。现有工程和冻结双流可复用，但 token 对齐、可靠硬负例覆盖、对象级信息是实际可行性风险。每周投入、设备空闲和提交期限未知，不作人员能力、耗时或 GPU 预算承诺。阶段 A 明确数据条件，阶段 B 冻结小模块预算后才进入实施。

## 10. 交付与实际状态

本方案版本保存于实验运行之前。A/A1/B 实际文件和观测值见[实验目录索引](ARTIFACT_INDEX.md)与[实验报告](report/REPORT.md)。

本轮新增研究产物为论文专题笔记、综述、源码审计及一个train输入metadata检查。GitHub上传辅助脚本只在本目录本地缓存，不是训练代码。原dataset可回写data_path旁缺特征日志；未来wrapper必须接管日志、pycache、临时目录和所有第三方副作用，只读引用不等于无副作用。
