# 动作理解与时序捷径核查：RCORE / Invert4TVG / ActPrompt

核查日期：2026-10-01。本文只读本地论文与公开源码，不训练、不部署。全文提取和第三方代码仅保存在 `research/.local/`，不作为上传材料；下面的行号按 `nl -ba` 的换行计数，对应该本地快照证据。研究问题：joint evidence 的收益是否能排除 object-driven verb shortcut？冻结特征是否已经含有所需动作信息？哪些最小控制能够判断当前机制，而不改变严格 S-only 设置？

## 来源、版本与核查边界

| 工作 | 可核实身份/状态 | 本次源码核查 |
|---|---|---|
| RCORE | [arXiv:2601.16211](https://arxiv.org/abs/2601.16211)；[作者项目页](https://ahngeo.github.io/assets/html/RCORE.html)与[论文链接的仓库](https://github.com/KHU-VLL/RCORE)标明 ECCV 2026 | 官方仓库快照 `7b8bc333b0fc0cab9e6d0f5006d1ca1c87514529`，静态读取，未运行 |
| Invert4TVG | [arXiv:2508.07388](https://arxiv.org/abs/2508.07388)，2026-02-13 v2；本地 PDF 首页及正文标 Published as a conference paper at ICLR 2026；[OpenReview 已发表 PDF](https://openreview.net/pdf/582e524c1bd524f97dbdef3bad8854f37ce8e398.pdf)支持该身份 | 找到 [nian1125/Invert4TVG](https://github.com/nian1125/Invert4TVG)，快照 `35970155e7670f52774055149231f8c08d21b632`。它自述 implementation，但此次未找到论文/作者主页到该仓库的身份链接，因此只称公开实现候选，不能称已验证官方仓库 |
| ActPrompt | [arXiv:2408.06622](https://arxiv.org/abs/2408.06622)是 2024 v1、9 页；[作者所属机构 Microsoft Research 出版页](https://www.microsoft.com/en-us/research/publication/actprompt-in-domain-feature-adaptation-via-action-cues-for-video-temporal-grounding/)核实 TIP 2026、35:2714–2726；DOI 10.1109/TIP.2026.3671609 | arXiv 摘要说完整代码在补充材料。此次未找到并核实可访问的官方独立代码仓库。以下机制依据本地早期 PDF，不能声称逐项核查了 TIP 最终扩展版 |

OpenReview 页面直接打开遇到 browser verification，发表状态由可检索的正式 PDF 和本地已发表 PDF 交叉支持，未使用论坛页面猜测审稿结论。代码仅做静态检查，不据此保证复现结果。

## 1. RCORE：分解本身不能消除物体推断动作的捷径

**论文陈述。** 在 zero-shot compositional action recognition 中，verb 与 object 共现偏斜、动作学习比静态物体更难，使模型由物体猜高频 verb；其控制实验及 FSP/FCP 分解显示，独立动作/物体分支也会失效。这里是动作分类证据，不是本文 generalized moment retrieval / U− absence 的直接验证。证据：`research/.local/RCORE (arXiv:2601.16211).txt` 90–132、394–447 行，诊断定义在 306 行附近；[原论文](https://arxiv.org/abs/2601.16211)。

**CPR 的具体机制。** Co-occurrence Prior Regularization 不是从总分减去 primitive 得分。它把另一个视频中间帧的静态 object cue 注入当前视频高运动区域，保留当前 verb，形成软 object/组合标签；让目标合成组合超过频繁 seen hard negatives 一个 margin；分类空间按 batch 从 seen pairs 扩展到该批合成 pairs。论文证据：上述文本 513–576 行，公式 3–7。

**TORC 的具体机制。** Temporal Order Regularization for Composition 在 frame features 上构造逆序与随机乱序：正序/逆序 verb 表征 cosine similarity 最小化；乱序 verb 类别分布最大熵，以削弱从静态 object cue 得到高置信动作的路径。论文证据：578–624 行，公式 8；并不是要求所有 reversed videos 都是不存在事件。

**源码核实。** [官方 `model/custom_clip_c2c_prompts.py`](https://github.com/KHU-VLL/RCORE/blob/7b8bc333b0fc0cab9e6d0f5006d1ca1c87514529/model/custom_clip_c2c_prompts.py#L278) 278–296 行分别执行随机与逆序 gather，经过 `c2c_VE1` 后计算 cosine 和乱序 logits；[`engine/train_comp_engine_penalty.py`](https://github.com/KHU-VLL/RCORE/blob/7b8bc333b0fc0cab9e6d0f5006d1ca1c87514529/engine/train_comp_engine_penalty.py#L195) 195–201 行确实返回 cosine loss 减 entropy。[`utils/cpr.py`](https://github.com/KHU-VLL/RCORE/blob/7b8bc333b0fc0cab9e6d0f5006d1ca1c87514529/utils/cpr.py#L79) 79–127 行做像素混合/区域 resize-paste，129–149 行生成新 object/pair 标签及扩展 label space。代码支持“在 feature sequence 上实现 TORC”的操作层面，但骨干使用可训练 adapter/LoRA，不能等同于本项目纯冻结特征。

**本项目推断。** joint 分支可能继续读 object→verb 共现；给它 cross-attention 或 bilinear 不自动产生运动证据。CPR 的合成组合标签改变了监督解释，且注入物体不保证物理交互真实发生，因此首版不移植。可以借用 TORC 的诊断思想，但不复制对所有动作的逆序分離/高熵约束：walking 等动作逆序未必变 absent，乱序也可能仍保留动作证据。先区分 temporal-direction-sensitive 与 direction-insensitive queries，只对经核实的前者测试预期下降。

## 2. Invert4TVG：定位目标与动作理解目标必须分别检验

**论文陈述。** 论文在 Qwen2.5-VL / RL TVG 设置下观察到，仅用 IoU 奖励改善定位可能损害动作理解；它用已有 query 与 GT segment 导出三种辅助任务，不需要新增人工动作标签。这是其 LVLM 设定中的经验结论，不是所有监督定位器的普遍定理。证据：`research/.local/Invert4TVG (arXiv:2508.07388).txt` 77–136、234–285 行；[原论文](https://arxiv.org/abs/2508.07388)。

| 任务 | 输入/输出与原 annotation 的关系 | 论文奖励边界 |
|---|---|---|
| Verb Completion (VC) | GT segment + mask verbs 的原 query → 补动词 | lemma 与 GT 匹配 |
| Action Recognition (AR) | GT segment → 一个 verb | 预测 verb 属于原 query 的 verb 集合 |
| Video Description (VD) | GT segment → 完整描述 | 原 query 动词出现在生成描述中；不是实体身份/交互完整正确性奖励 |

论文 321–347 行说明 TVG 与三种 inversion tasks 概率交替，不能把三种任务称为三种视频时间反转：这里 inversion 是输入/输出角色的逆置。S+ segment 用 GT 训练辅助识别合法，但 GT segment 不能进入真实 existence 推理。

**公开实现候选核实。** [`qwenvl_grpo_trainer.py`](https://github.com/nian1125/Invert4TVG/blob/35970155e7670f52774055149231f8c08d21b632/qwen-vl-finetune/qwenvl/train/qwenvl_grpo_trainer.py#L73) 73–74 行是 VC prompt；501–525 行只见 grounding/VC 两路；538–559 行按 `inputs[0]["action"]` 切换并裁 GT segment，没在这一路核实三任务均匀随机采样。547–550 行使用首样本裁剪范围裁每个样本，代码 567 行还注明 only support bs==1，不能直接拷贝成通用 batch 实现。候选 [`reward.py`](https://github.com/nian1125/Invert4TVG/blob/35970155e7670f52774055149231f8c08d21b632/qwen-vl-finetune/qwenvl/train/reward.py#L121) 121–138、205–217 行默认给“GT verb 集合被输出包含”奖励，允许多输出 verbs；20 行有本地绝对 SpaCy 路径。这些是候选实现的边界，不能反向改写论文三种任务定义，也不能称完整复现已验证。

**本项目推断。** 首版不引入 LVLM、文本生成或 GRPO。最小可移植控制是在 S+ GT 内的 motion representations 上做 masked-verb 分类/检索或 segment→verb 识别，同时对照 entity-only 与 text-only。这些是 Invert4TVG-inspired probes，不是原方法复现。只用训练侧已出现 primitive vocabulary；若动作类别本身也 held out，应另列该评价条件，不能偷偷读 U label 建分类器。AR 能改善动作表征，但仍不能证明特定动作施加到特定实体上。

## 3. ActPrompt：骨干内部补信息与冻结特征读出是不同干预

**论文机制。** 原 CLIP 捕捉物体/场景、SlowFast 捕捉视频信息。ACI 将 video features 线性映射为 prompt 插入 CLIP image encoder 首层 patch tokens；verb-guided prompt 来源是 CLIP text encoder 逐层 verb token embeddings，逐层注入 image encoder。ACI 的 attention 分布用于挑选动作相关 patches；CTPL 汇集相邻帧选中的 patch embeddings 加时间位置编码，经 MLP/residual 生成后续层 temporal prompts。两路 patch attention consistency 与 moment-query ranking/contrastive pretext tasks 训练这些轻量模块。证据：`research/.local/ActPrompt (arXiv:2408.06622).txt` 214–243、245–332 行；[2024 原论文](https://arxiv.org/abs/2408.06622)。

**本项目推断。** “原骨干参数冻结”仍需重跑有 prompts 的 image encoder，访问像素、patch tokens、各层 attention/text embeddings；这与已经预提取 CLIP/SlowFast clip vectors 上加一个 head 不同。当前首版最多验证已有 feature 是否支持动作/局部联合读出，不能说实现了 ActPrompt 的 action-sensitive adaptation。既无像素也无 patch/region/track 时，J 只能称时间局部联合证据，不能称实体身份绑定。若动作 probe 在 motion features 上也无效，应检查 feature 的可识别性、采样时间分辨率与 extraction 设置，之后再考虑新目录内独立像素级提取适配；增加 joint loss 不能创造冻结特征丢失的信息。

## 4. 对方案的最小修改：将动作可识别性放在 binding 验证之前

以下都是待验证的本项目设计，不是论文已证明结论。

1. **输入能力门槛。** 先用训练侧 S+ GT segments 评估 motion-only segment→verb probe；与 appearance-only、temporal-mean、single-frame、text-only 对照。报告同实体不同动作的 paired 排序/识别，不能只报告总平均。GT 只用于该独立动作 probe，正式 map→existence 仍全视频搜索。
2. **单流 shortcut 控制。** 当前 H/P/C/J 外增加 entity-only、motion-only、两流时间均值/单位置控制；三者使用相同监督、容量预算和主聚合。若 J 的提升由 appearance-only 达到，不支持动作—实体共同发生解释。
3. **两类时间干预分开。** 动作时序破坏把两流共同逆序或共同乱序，测试动作 order；绑定破坏仅错位一流，测试跨流局部对应。分别报告，不能把 cross-stream misalignment 的下降等同于动作理解改善。预提取 SlowFast clip vectors 的序列逆置仅打乱 clip 间次序，保留 clip 内编码的原方向；不能称 pixel-video reversal，也不能期望一定翻转 open/close 的 motion representation。
4. **扰动标签限制。** 所有错位/乱序先作诊断，不能自动用作 S−、U− 或负 MIL 标签。对持续实体、周期动作、方向无关动作设置可解释子集及适用性报告；方向敏感判定规则在训练侧冻结。测试 U 上的这些分析仅属于事后报告，不选择超参或 checkpoint。
5. **一个最小训练候选。** 若 motion probe 有信息且 J 存在 object shortcut，再只增加训练侧 annotation-derived verb recognition 辅助目标，单独对照 `J` 与 `J + verb auxiliary`；另一独立臂才考察经过动作适用性筛选的 order regularization。不要首次同时加入 VC/AR/VD、TORC、CPR、binding、residual。保留语义词频控制与当前 seed3407 单种子边界；不自动启动多 seed 或同预算配对核验。
6. **停止条件。** motion-only probe 没有超越静态/物体对照时，先定位表示/采样瓶颈；J 不超过同时间 AND 时，报告“共激活足够解释”；J 的存在收益只来自 appearance、或 order 破坏无影响时，不能将收益表述为 motion-grounded binding。原 U+/U− 与 localization 共同收益仍需独立成立。

## 综合判断

RCORE 针对共现捷径，Invert4TVG 针对动作理解未被定位奖励保留，ActPrompt 针对 image backbone 对动作线索的表达不足。三者支持设置三个可分离的故障检查，而不是用三个模块拼成一个方法。对当前方案最必要的新增步骤是“动作证据在现有冻结特征上可识别吗”，再判断 J 是否增加了跨流时间对应信息。只有两关均过，primitive-conditioned surplus 才有值得解释的输入基础。
