> 整理于 2026-09-30：此文为已有调研的链接整理副本，本轮未新增文献核查。当前实验状态与恢复顺序见 [HANDOFF.md](HANDOFF.md)。

# 未见语义下的存在判断与定位：算法调研及方法选择

日期：2026-09-30。文献检索完成于 2026-09-29，覆盖检索时可核实的 2026 年 9 月论文；不声称穷尽全部最新工作。本文是研究决策文档，所提方法尚未实现、训练或验证。2026-09-30 根据研究目标修订：当前入口为 [对应关系泛化研究方案](EXPERIMENT_PLAN.md)；Witness-DETR 已降为历史候选。

## 摘要

现有实验显示，三种 GMR 模型在五个冻结语义划分上均出现存在 AUROC 退化，同时存在误接受与误拒绝两种失败。本次调研发现，负查询拒绝、组合负例、局部验证及统一定位—拒绝已有较多先例。研究重心现调整为：在训练集、正负样本及标签不变的条件下，如何从已见语义学习更能迁移的视频—文本对应关系，并使这种对应关系同时服务传统 VTG 定位与存在判断。DETR 是首个验证载体，不是算法依赖。当前优先研究下游适配是否使原有跨模态关系发生有害偏移，再据证据设计对应结构保持与任务适配机制。结构保持只是候选方向，尚未认定为新颖方法；原 Witness-DETR 的 ROI 和交叉标签设计保留为历史探索，不再是主方案。

## 1. 研究问题与约束

RQ1：近期研究是否已经解决仅用已见语义训练、同时接受 U+ 和拒绝 U− 的问题？

RQ2：已见语义训练中的视频—文本对应关系为何未能迁移，退化发生在跨模态表示还是输出决策？

RQ3：能否在数据和标签不变的条件下，设计可接入不同 VTG 模型的对应关系学习机制，同时改善未见语义定位与存在判断？

本文把用户所说的“原来数据训练”解释为每个冻结划分原有的 S+/S−，不是把移除的 held-out 正例加回。外部预训练的 CLIP/SlowFast 特征保持与原基线相同；真实 U 语义不能通过增强、教师、检索库或额外任务训练进入模型。语义熟悉度干扰属于待验证解释；当前实验确认的是现象，尚未确定唯一原因。

## 2. 检索与证据方法

四个检索视角分别覆盖负查询与广义检索、DETR 定位结构、邻域去偏与反证，以及项目代码和数据可用性。前三个视角并行检索，综合写作与方法选择串行完成。关键词包括 negative-aware/generalized/open-set moment retrieval、unseen action/compositional temporal grounding、local evidence/null-set/DETR、counterfactual calibration 和 Routing Evidence。来源优先采用 CVF、NeurIPS、ECVA、AAAI、ACM、arXiv 与作者仓库。

下文区分会议论文、预印本和仅由作者仓库标记的发表状态。Routing Evidence 的 ACM 全文未能取得，仅依据出版摘要和官方仓库讨论其已公开的机制，不冒充全文分析。其他表格中的细节来自一手全文或作者资料；不跨论文直接比较异协议性能数值。分类按研究目标划分，跨类工作在比较中说明。

## 3. 算法版图

| 分支 | 已解决或已研究的核心问题 | 与本项目的剩余距离 |
| --- | --- | --- |
| A. 查询可能不成立 | 输出空集、困难负查询、拒绝训练及测试时适应 | 需检验严格 S-only 训练后的 U+/U− 联合迁移 |
| B. 未见语义定位 | 新动作、新组合、语义负例和不确定性 | 正例定位改善不能代替不存在事件的拒绝 |
| C. DETR 证据与边界 | 查询依赖表示、背景消歧、局部匹配、边界质量 | 强定位模型并不自动有可靠的存在分数 |
| D. 视觉证据去偏 | 对比视觉输入、局部验证、查询条件校准 | 需证明收益来自视觉交互，而非阈值或文本来源 |

## 4. 允许拒绝已经是成熟研究方向

OpenVMR 从查询分布学习 ID/OOD 边界，而 RaTSG 同时建模帧级与视频级相关性，并把无结果纳入定位输出；两者都早于当前项目。必须区分各论文的术语：OpenVMR 把 video-irrelevant 称为 OOD，本项目则把 downstream-unseen 与存在标签交叉定义，U+ 仍应接受。因此不能把语义新颖性检测直接用作拒绝条件。[OpenVMR](https://arxiv.org/html/2605.29812v1)、[RaTSG](https://proceedings.neurips.cc/paper_files/paper/2024/file/4b96695d9885f038110b8b16ef50e882-Paper-Conference.pdf)

NA-VMR 和 GMR 提供了负查询学习及空集评测；CausalVTG 又将去偏表示与 query relevance 联合建模。因此，“增加 BCE 存在头”“联合训练定位和拒绝”“去语义偏差”均不能单独支撑新颖性。CausalVTG 正文中的 relevance 模块使用 pooled video/query 特征与二分类监督，和本项目候选区间级验证存在可比较的结构差别，但差别是否有效需要同协议实验。[NA-VMR](https://arxiv.org/abs/2502.08544)、[GMR](https://arxiv.org/abs/2605.02623)、[CausalVTG](https://proceedings.neurips.cc/paper_files/paper/2025/file/95a8436cdc3981c37bcab4f684427213-Paper-Conference.pdf)

2026 年的 RA-RFT 已直接研究语义相近却不成立的 hard-irrelevant queries；HRVTG 则讨论离线拒绝对新型幻觉诱因的迁移问题，并使用测试时反事实探针与在线优化。前者依赖 LVLM 强化微调和专门拒绝数据，后者会在测试流上更新参数。它们与固定特征、固定 S 训练的 DETR 方案有协议差别，却足以否定“此前无人研究可靠拒绝或拒绝泛化”的宽泛表述。[RA-RFT](https://openaccess.thecvf.com/content/CVPR2026/html/Lee_Learning_to_Refuse_Refusal-Aware_Reinforcement_Fine-Tuning_for_Hard-Irrelevant_Queries_in_CVPR_2026_paper.html)、[HRVTG 官方论文](https://github.com/CVL-hub/HRVTG/blob/main/ECCV2026_HRVTG.pdf)

| 工作 | 机制 | 作为本项目对照的用途 |
| --- | --- | --- |
| OpenVMR，MM 2024 | Query normalizing flow、ID/OOD 边界、PU grounding | 检验按查询分布拒绝是否伤害 U+；2026 arXiv 上传不是发表年份 |
| RaTSG，NeurIPS 2024 | 帧/视频 relevance、无结果边界 token | 统一拒绝和定位、帧级 MIL 的直接先例 |
| NA-VMR，WACV 2025 | 负查询训练、indicator/saliency 拒绝 | 最重要的公开负查询适配基线之一 |
| CausalVTG，NeurIPS 2025 | 去偏表示、多尺度定位、relevance 判别 | 对“去偏改善存在判断”构成直接新颖性压力 |
| GMR，2026 | 集合检索、decoder pooled existence adapter | 本仓库直接基线 |
| RA-RFT，CVPR 2026 | Hard-irrelevant 数据、GRPO 多奖励 | 高语义相似负例并非新发现；外部数据预算要分开 |
| HRVTG，作者仓库标记 ECCV 2026 | 测试时反事实探针、LoRA/GRPO | 拒绝迁移的重要近邻；不是固定参数推理协议 |

## 5. 未见语义定位研究的启发与边界

Routing Evidence 以训练/测试动作不同为出发点，用多个 Normal-Inverse Gamma 回归头表达预测证据与不确定性，并选择适合样本的头；SHINE 则通过合理的层级负查询和 saliency ranking 改善组合定位。前者说明可以围绕明确的泛化缺口组织全文，后者说明“微小语义编辑 + 对比排序”已有直接先例。二者均不能被简单改名为当前方法。[Routing Evidence](https://doi.org/10.1145/3637528.3671693)、[SHINE](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/02948.pdf)

Compositional Temporal Grounding 已建立新组合定位任务，FVE 则使用目标新语义文本生成视频进行扩增。当前方案可沿用前者对组合泛化的重视，但不能把 FVE 的目标语义暴露搬进严格 S-only 主实验。CoMET-Bench 又同时包含组合时空条件与负查询，进一步说明“组合查询 + 拒绝”的宽泛交集不足以宣称新任务。[CTG](https://arxiv.org/abs/2203.13049)、[FVE](https://ojs.aaai.org/index.php/AAAI/article/view/32624)、[CoMET](https://arxiv.org/abs/2606.15320)

我们适合借鉴 RE 的论证顺序：指出一个训练假设 → 设计相应语义留出评测 → 找到具体失败 → 提出针对性结构 → 用机制对照证明修复。对本项目而言，顺序应为：S 上可靠的存在判断在 U 上失效 → 一部分本来正确的候选被拒绝 → 检验存在判断是否缺少与实际输出片段一致的语义证据 → 在原 S 数据上训练统一模型 → 同时报接受、拒绝、排序和定位。这里不预先要求 router，也不把高 uncertainty 当作 absent。

## 6. DETR 的哪些结构已被覆盖

QD/CG-DETR 已研究查询依赖视频表示和相关性校准；BM-DETR 利用同视频其他事件查询消歧背景。BM-DETR 的“负查询”可能在视频其他位置真实存在，不能直接作为当前 S− 标签。TD-DETR 与 CVA 进一步研究背景伪相关和上下文变化；CVA 特别指出任意内容混合可能引入假负例。这支持严格控制视觉增强，而不是随意删除标注区间就标为 absent。[QD-DETR](https://arxiv.org/html/2303.13874)、[CG-DETR](https://arxiv.org/html/2311.08835v4)、[BM-DETR](https://arxiv.org/html/2306.02728)、[TD-DETR](https://arxiv.org/html/2501.07305)、[CVA](https://arxiv.org/abs/2603.24934)

Sim-DETR 已用 query-to-frame matching 联系全局候选与局部证据，DE²TR 已区分语义与边界证据；最新 EviDETR 又加入特征重加权、Top-2 MoE 与 MR→HD 证据融合。所以“局部证据”“双证据”“多专家路由”本身不够新。尤其 EviDETR 是 2026-09-25 预印本，作者注明投稿 ICASSP 2027，不能写成已录用论文。[Sim-DETR](https://arxiv.org/html/2509.23867)、[DE²TR](https://ivanz106.github.io/DE2TR-page/static/pdf/main.pdf)、[EviDETR](https://arxiv.org/abs/2609.30724)

首个原型建议使用已在仓库跑通的 QD-DETR，再在 Moment-DETR 上验证迁移。DE²TR 可作为较新的定位底座对照；不应同时换骨干、特征和存在机制。SG-DETR 使用更强特征和额外预训练的设置需要独立预算，不宜将其公开数字直接与本仓库固定 CLIP/SlowFast 比较。[SG-DETR](https://openaccess.thecvf.com/content/WACV2026/html/Gordeev_Saliency-Guided_DETR_for_Moment_Retrieval_and_Highlight_Detection_WACV_2026_paper.html)

## 7. 邻域研究如何限制创新主张

VCD 已通过原始与扰动视觉输出对比抑制先验；TRACE 已在 PRVR 中用查询条件的全局到局部路径验证局部高分；OV-DQUO 则在开放词汇 DETR 中处理 novel foreground 被当作背景的问题。三者的任务不同，却共同限制了“减掉无视觉分数”“验证局部证据”“未知不应成为背景”的独占性主张。[VCD](https://openaccess.thecvf.com/content/CVPR2024/html/Leng_Mitigating_Object_Hallucinations_in_Large_Vision-Language_Models_through_Visual_Contrastive_CVPR_2024_paper.html)、[TRACE](https://arxiv.org/abs/2609.08999)、[OV-DQUO](https://ojs.aaai.org/index.php/AAAI/article/view/32836)

局部打分同样可能仅识别“有人活动”，或者利用编辑文本的表面特征。一个统一网络不自动排除这些捷径。真正值得检验的是：同一句查询在视觉真值改变后，存在分数是否随之改变；同一视觉片段在动作或对象被修改后，分数是否响应关键语义差异。纯文本、纯视频以及普通图文匹配都必须成为对照。

## 8. 原方案的实现观察与数据核查（历史记录）

当前 Moment/QD 的 `GMRAdapter` 先对所有 decoder slots 按维度 max/mean pooling，再经 MLP 输出视频级存在分数；定位分类与边界是另一组输出。其代码允许存在决策与实际返回的候选脱钩。按维度 max 的不同维度可以来自不同 slot，这是结构事实；“因此造成语义伪证据”仍是实验假设，不能直接因果归因。[adapter](../../../../models/moment_detr_gmr/gmr_adapter.py)、[Moment 输出](../../../../models/moment_detr_gmr/moment_detr.py)、[QD 输出](../../../../models/qd_detr_gmr/model.py)

对冻结 train.jsonl 的只读核查发现如下资源。使用完全相同的 query 字符串，不使用语义近似、词形归并或测试数据：

| 每个划分 | 有同视频来源 S+ 的 S− | 来源正查询在其他训练视频中有缺席标签的编辑对 | 有完整交叉标签的来源编辑对 | 不同查询对 | 不同视频×查询四元组 |
| --- | ---: | ---: | ---: | ---: | ---: |
| A1 / A2_alt / A3，各自 | 1,499 | 712 | 433 | 75 | 969 |
| C1 / C2_alt，各自 | 1,499 | 433 | 317 | 49 | 765 |

交叉标签表示 `(Va, qa)=+、(Va, qb)=−、(Vb, qa)=−、(Vb, qb)=+`。这是原训练数据已有四条记录的重组，不是新造负例。969/765 是去重视频—查询组合数，不是独立统计样本，彼此会共享视频和句子；动作组或组合组之间也共享负例池，不能相加成独立证据。查询标签冲突计数为 0。计数核查不提升已有整批审核的证据等级。[机器可读核查](../../../../docs/correspondence_generalization/archive/witness_training_pair_audit.json)、[复算脚本](../../../../scripts/audit_witness_training_pairs.py)

## 9. 历史候选：Witness-DETR（不再推荐为主线）

工作名仅用于方案交流，未作名称唯一性认定。核心思想是：**一条查询的存在分数，应由模型实际输出的某个片段所支持；该支持必须对视频变化和关键语义变化都敏感。**

保留 DETR 的候选生成和边界回归，从文本注入之前的视频特征中，对每个候选区间读取短序列证据。共享的轻量 verifier 让完整查询与该序列交互，输出 slot 的支持分数。最终存在分数取最高支持分数，返回的也是该分数对应的候选；不再由独立全局分类器统一否决全部候选。S+ 真值区间与高质量匹配候选提供局部正监督，真实 S− 提供局部负监督。模型仍可误判，结构一致性不是正确性保证。

最有针对性的训练信号是上述交叉标签四元组。对 Va 中 qa 的真实区间和 Vb 中 qb 的真实区间，用同一个 verifier 计算四种图文组合。要求 qa 的优势在 Va 成立、qb 的优势在 Vb 成立。这一目标使固定文本偏好和通用 eventness 无法独自解释标签。与“同视频正负句排序”相比，标签在另一真实视频中的反转是关键约束；与人工剪视频相比，它不需要把未核查的剩余视频硬标为 absent。

候选结构与损失的精确定义在实验方案中。潜在贡献不是 ROI、max、双向对比或统一网络本身；这些均有先例。需要证明的是：**把可返回区间与跨视觉真值的语义判别绑定，能在严格语义保留条件下带来普通 MIL、普通对比学习和全局 relevance 无法解释的增益。** 若对照不能支持这一点，应把成果定位为有效适配或诊断，而非强方法创新。

## 10. 修订后的算法方向与近邻工作

当前要学习的是跨语义可迁移的对应关系，而不是通过更精细的负例利用提高一个局部拒绝器。固定样本、标签、特征访问与训练暴露次数，方法应位于视频/文本投影或跨模态交互层，输出可供原定位头和存在头使用的表示；不要求候选区间、ROI、Hungarian matching 或交叉标签四元组。

Zero-Shot VMR 已指出有限下游数据学到的图文相关性可能偏窄，而 R²-Tuning 研究如何有效适配 CLIP 的多层信息；前者侧重直接利用通用先验，后者侧重时空适配。二者支持“迁移对应关系”这一研究角度，但不证明本项目的失效来自表示漂移。R²-Tuning 需要中间层信息，不能直接移入只有末层缓存特征的同信息预算主实验。[Zero-Shot VMR](https://arxiv.org/abs/2309.00661)、[R²-Tuning](https://arxiv.org/abs/2404.00801)

KgCoOp 已通过约束文本表示变化保持预训练知识，CG-DETR 已有细粒度相关性蒸馏，2026 年 EVIDENT 又研究实体证据引导的跨域 MLLM 适配。因此，笼统的“保持 CLIP 知识”“加对齐损失”“用证据路由”都不足以支撑方法创新；当前需要识别哪一类对应关系应保留、哪一类应被时间监督修正，以及这个选择是否真正促进未见语义泛化。[KgCoOp](https://openaccess.thecvf.com/content/CVPR2023/papers/Yao_Visual-Language_Prompt_Tuning_With_Knowledge-Guided_Context_Optimization_CVPR_2023_paper.pdf)、[CG-DETR](https://arxiv.org/html/2311.08835v4)、[EVIDENT](https://arxiv.org/abs/2605.26104)

优先研究“任务监督下的对应结构保持与选择性适配”，先做表示与校准分离诊断，再决定是否实现。保留结构不等于盲目复制教师：原预训练模型也可能忽略动作或依赖物体。只有在当前输入特征存在可靠、可比的对应参考时才进入该路线；特征维度相同不能证明跨模态内积有意义。具体门槛与实验见当前方案。

## 11. 对三个研究问题的修订回答

RQ1：相关研究已经覆盖拒绝和语义泛化的多个方面，严格 S-only→U+/U− 仍需细化协议比较，不能宣称宽泛的首次性。

RQ2：当前证据尚未定位对应关系退化的具体来源。独立存在头是一个实现观察，不能据此把全部退化解释为候选—拒绝冲突，更不能据此限制算法形态。

RQ3：可探索仅改变对应关系学习、保持数据与输出头对照一致的通用方法。必须在传统正例 VTG 与原四象限 GMR 两条轨道上验证；若只改善空集判别而不改善跨模态对应诊断，应缩小为拒绝方法。Witness-DETR 暂不承担这个目标，新方案尚处于机制验证阶段。

## 参考文献与核查入口

1. Guolong Wang, Xun Wu, Zheng Qin, Liangliang Shi. **Routing Evidence for Unseen Actions in Video Moment Retrieval**. KDD 2024. [出版页](https://doi.org/10.1145/3637528.3671693)。摘要/官方资料核查。
2. Xiang Fang, Wanlong Fang, Daizong Liu, et al. **Not All Inputs Are Valid: Towards Open-Set Video Moment Retrieval Using Language**. ACM MM 2024. [全文](https://arxiv.org/html/2605.29812v1)。2026 补上传版本。
3. Jianfeng Dong, Xiaoman Peng, Daizong Liu, et al. **Temporal Sentence Grounding with Relevance Feedback in Videos**. NeurIPS 2024. [全文](https://proceedings.neurips.cc/paper_files/paper/2024/file/4b96695d9885f038110b8b16ef50e882-Paper-Conference.pdf)。
4. Kevin Flanagan, Dima Damen, Michael Wray. **Moment of Untruth: Dealing with Negative Queries in Video Moment Retrieval**. WACV 2025. [论文](https://arxiv.org/abs/2502.08544)。
5. Qiyi Wang, Senda Chen, Ying Shen. **CausalVTG: Towards Robust Video Temporal Grounding via Causal Inference**. NeurIPS 2025. [全文](https://proceedings.neurips.cc/paper_files/paper/2025/file/95a8436cdc3981c37bcab4f684427213-Paper-Conference.pdf)。
6. Yiming Ding et al. **Retrieving Any Relevant Moments: Benchmark and Models for Generalized Moment Retrieval**. 2026. [论文](https://arxiv.org/abs/2605.02623)。
7. Jin-Seop Lee, SungJoon Lee, SeongJun Jung, Boyang Li, Jee-Hyong Lee. **Learning to Refuse: Refusal-Aware Reinforcement Fine-Tuning for Hard-Irrelevant Queries in Video Temporal Grounding**. CVPR 2026. [会议页](https://openaccess.thecvf.com/content/CVPR2026/html/Lee_Learning_to_Refuse_Refusal-Aware_Reinforcement_Fine-Tuning_for_Hard-Irrelevant_Queries_in_CVPR_2026_paper.html)。
8. Chufan Yi, Hongyu Qu, Shiyu Xuan, et al. **Test-time Counterfactual Calibration for Hallucination-Resistant Temporal Grounding**. 作者仓库标记 ECCV 2026. [官方 PDF](https://github.com/CVL-hub/HRVTG/blob/main/ECCV2026_HRVTG.pdf)。
9. Zixu Cheng, Yujiang Pu, Shaogang Gong, Parisa Kordjamshidi, Yu Kong. **SHINE: Saliency-aware HIerarchical NEgative Ranking for Compositional Temporal Grounding**. ECCV 2024. [全文](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/02948.pdf)。
10. Juncheng Li et al. **Compositional Temporal Grounding with Structured Variational Cross-Graph Correspondence Learning**. CVPR 2022. [论文](https://arxiv.org/abs/2203.13049)。
11. Dezhao Luo, Shaogang Gong, Jiabo Huang, Hailin Jin, Yang Liu. **Generative Video Diffusion for Unseen Novel Semantic Video Moment Retrieval**. AAAI 2025. [出版页](https://ojs.aaai.org/index.php/AAAI/article/view/32624)。
12. Yuanhao Zou et al. **Conditional Multi-Event Temporal Grounding in Long-Form Video**. 2026 预印本. [论文](https://arxiv.org/abs/2606.15320)。
13. WonJun Moon et al. **Query-Dependent Video Representation for Moment Retrieval and Highlight Detection**. CVPR 2023. [全文](https://arxiv.org/html/2303.13874)。
14. WonJun Moon, Sangeek Hyun, SuBeen Lee, Jae-Pil Heo. **Correlation-Guided Query-Dependency Calibration for Video Temporal Grounding**. [核查版本](https://arxiv.org/html/2311.08835v4)，2023 首稿、2024 修订。
15. Minjoon Jung et al. **Background-aware Moment Detection for Video Moment Retrieval**. WACV 2025. [全文](https://arxiv.org/html/2306.02728)。
16. Xinyang Zhou, Fanyue Wei, Lixin Duan, Angela Yao, Wen Li. **The Devil is in the Spurious Correlations: Boosting Moment Retrieval with Dynamic Learning**. ICCV 2025. [全文](https://arxiv.org/html/2501.07305)。
17. Sungho Moon, Seunghun Lee, Jiwan Seo, Sunghoon Im. **CVA: Context-aware Video-text Alignment for Video Temporal Grounding**. CVPR 2026. [论文](https://arxiv.org/abs/2603.24934)。
18. Jiajin Tang et al. **Sim-DETR: Unlock DETR for Temporal Sentence Grounding**. ICCV 2025. [全文](https://arxiv.org/html/2509.23867)。
19. Yifan Zhang, Chengxu Liu, Yujie Dun, Xueming Qian. **DE²TR: Dual Evidence Detection Transformer for Video Temporal Grounding**. ECCV 2026. [作者项目](https://ivanz106.github.io/DE2TR-page/)。
20. Haoran Sun, Yufan Li, Qichen Zhang, Haoran Zhao, Shuqi Wang. **EviDETR: Preserving Query-Relevant Temporal Evidence for Moment Retrieval and Highlight Detection**. arXiv 2026-09-25，投稿状态. [论文](https://arxiv.org/abs/2609.30724)。
21. Aleksandr Gordeev et al. **Saliency-Guided DETR for Moment Retrieval and Highlight Detection**. WACV 2026. [会议页](https://openaccess.thecvf.com/content/WACV2026/html/Gordeev_Saliency-Guided_DETR_for_Moment_Retrieval_and_Highlight_Detection_WACV_2026_paper.html)。
22. Shuaiqi Cheng, Siyu You, Yanbi Wu, Yuxi Chen, Jiahao Zhang, Xuming Hu. **Concentrate After Imagination: Text-Conditioned Evidence Grounding for Partially Relevant Video Retrieval**. arXiv 2026-09-08. [论文](https://arxiv.org/abs/2609.08999)。
23. Sicong Leng et al. **Mitigating Object Hallucinations in Large Vision-Language Models through Visual Contrastive Decoding**. CVPR 2024. [会议页](https://openaccess.thecvf.com/content/CVPR2024/html/Leng_Mitigating_Object_Hallucinations_in_Large_Vision-Language_Models_through_Visual_Contrastive_CVPR_2024_paper.html)。
24. Junjie Wang, Bin Chen, Bin Kang, Yulin Li, Weizhi Xian, Yichi Chen, Yong Xu. **OV-DQUO: Open-Vocabulary DETR with Denoising Text Query Training and Open-World Unknown Objects Supervision**. AAAI 2025. [出版页](https://ojs.aaai.org/index.php/AAAI/article/view/32836)。仅用作开放词汇 DETR 邻域机制比较。

25. Dezhao Luo, Jiabo Huang, Shaogang Gong, Hailin Jin, Yang Liu. **Zero-Shot Video Moment Retrieval from Frozen Vision-Language Models**. WACV 2024. [论文](https://arxiv.org/abs/2309.00661)。
26. Ye Liu, Jixuan He, Wanhua Li, Junsik Kim, Donglai Wei, Hanspeter Pfister, Chang Wen Chen. **R²-Tuning: Efficient Image-to-Video Transfer Learning for Video Temporal Grounding**. ECCV 2024. [论文](https://arxiv.org/abs/2404.00801)。
27. **Visual-Language Prompt Tuning With Knowledge-Guided Context Optimization (KgCoOp)**. CVPR 2023. [会议论文](https://openaccess.thecvf.com/content/CVPR2023/papers/Yao_Visual-Language_Prompt_Tuning_With_Knowledge-Guided_Context_Optimization_CVPR_2023_paper.pdf)。
28. **EVIDENT: Routing MLLM Adaptation through Entity-Grounded Visual Evidence for Cross-Domain Video Temporal Grounding**. 2026 预印本. [论文](https://arxiv.org/abs/2605.26104)。本轮仅核查摘要层面的适配目标，不据此推定完整协议或性能。
