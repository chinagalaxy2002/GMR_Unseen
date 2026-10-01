# 文献与源码核验：从相关概念到可迁移事件证据

日期：2026-10-01。范围为用户指定的八篇论文，及当前项目相关源代码；不是整个领域的穷尽综述。研究笔记和本地 PDF hash 可追溯，未运行第三方模型或复现其性能。

## 摘要

这组论文共同提示四种需要区分的问题：动作信息是否被编码，动作预测是否借助物体捷径，动作与实体是否在同一时间上下文形成事件，以及局部证据能否传递到最终拒绝和定位。它们不支持直接把分解、交互、残差与新损失堆在一起。IAE-VTG 已覆盖接近的定位、拒绝和组合泛化，使本方案的差异必须收紧到严格协议与 primitive-conditioned 视觉增量；RCORE、Invert4TVG 和 ActPrompt 则要求把动作可读性检查提前到绑定检验之前。EVIDENT 与 HRVTG 的资源或推理协议不能直接移入冻结 pooled 特征主轨；EviDETR 与 CausalVTG 提供了需要控制的证据流和全局 relevance 对照。

## 1. 问题与核验方法

研究问题见 [RESEARCH_BRIEF.md](RESEARCH_BRIEF.md)：RQ1 绑定机制与近邻重叠；RQ2 冻结输入和 S-only 标签可支持哪些干预；RQ3 什么最小实验区分动作、时间对应、joint 和盈余，并验证共同收益。

先读七份已有 PDF 全文，HRVTG 从官方仓库补取全文；用 arXiv、作者机构/项目页和正式 PDF 核对版本/发表状态。源码核对固定 commit，不将“仓库存在”写成效果复现。三个视角独立核查后合并：绑定/实体证据，动作捷径/时间次序，拒绝/证据流。详细内容证据以本地 PDF 为主，不从搜索摘要推出模块细节。

完整提取文本、外部源码和 PDF 下载都在 `research/.local/`，不上传。来源文件及 SHA-256 见 [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json)。下面机制表来自全文，不是仅依据摘要的评价。

## 2. 用户重点清单的核查结果

| 标记 | 本轮核验的状态 | 关注重点是否准确及必要修正 | 对方案的直接影响 |
| --- | --- | --- | --- |
| IAE-VTG | arXiv v1，2026-09-09；未取得可确认官方代码；TIP 模板不等于录用 | FDIM/ISA 重点准确，但还必须看 Table VI 的 NA-VMR 拒绝与 Table IX 的 Novel-C/Novel-W；按公式推导存在单对视觉退化风险 | binding+existence 本身不能当差异；增加单对非退化要求与 IAE-inspired 结构对照 |
| RCORE | 作者项目/官方仓库标 ECCV 2026；官方源码已核查 | object-driven verb shortcut 准确；TORC 为逆序 verb 表征分离与乱序最大熵；CPR 是像素物体 cue 合成与共现先验正则 | 先验证 motion evidence；TORC 先作有限诊断，不把 CPR 合成样本当真实交互正例 |
| Invert4TVG | ICLR 2026 已发表 PDF 可核实；公开实现候选未证实作者关联，也未核验三任务完整实现 | “定位优化不等于动作理解”是其 LVLM/RL 设置下的发现；inversion 是任务输入输出逆置，不是时间倒放 | 借鉴原 S+ segment→verb probe；不直接引入 VC/AR/VD 全套或生成式模型 |
| ActPrompt | Microsoft Research 核实 TIP 2026；本地 PDF 是 2024 arXiv 早期版 | static/action-sensitive cue 与 prompts 准确；机制依赖 image encoder 内 patch/layer prompts | 冻结 clip vectors 上加头不是该机制；必要时另立原像素/新特征资源轨 |
| CausalVTG | 本地全文、官方代码与NeurIPS2025正式proceedings已核查 | counterfactual relevance 重点合理；公开实现 QR 是 pooled video/query relevance scalar，不能当 action/entity joint 因果证明 | 容量/监督匹配的 pooled holistic relevance 是必需控制，不新增跨视频 absence 标签 |
| HRVTG | 官方 CVL-hub/HRVTG 已有全文 PDF 与源代码；作者仓库标 ECCV 2026 | 清单“闭源/无公开论文代码”已过时；在线 LoRA/GRPO 更新，CF 身份/frozen reference 奖励与主协议不同 | 修正状态；只借鉴扰动诊断，主轨不做测试时更新，不误称直接用人工 test GT 反传 |
| EVIDENT | arXiv v1；第一作者官网列 NeurIPS 2026；未取得可确认官方代码 | entity bottleneck 重点准确，但依赖 dense visual patch tokens 和 DINOv2 cluster 蒸馏；对象可见不等于动作发生 | 现有 `(T,D)` pooled 输入无法直接移植 slots/objectness 蒸馏；身份级 binding 不进入主轨承诺 |
| EviDETR | arXiv v1，2026-09-25；作者项目页可访问但本轮未找到公开代码链接 | SFR/TTop2MoE/MR2HD 重点准确；Top-2 是 FFN experts，MR2HD 是 moment retrieval→highlight detection，未验证 existence | 首版用简单 evidence-flow 对照，不上 MoE；不得把高置信幻觉 span 再包装成存在证据 |

“未取得官方源码”只描述本轮核验，不能写成断言闭源。发表身份来源逐项区分作者声明、机构出版页及正式出版物；完整来源链见三份专题笔记。

## 3. 三个机制层面的比较

### 3.1 动作可读性与捷径

RCORE 直接处理 compositional action recognition 中的 object→verb 捷径，而 Invert4TVG 观察到定位 IoU 优化可能不保留动作理解；两者指向不同层次，不能把任一结果直接当本项目已定位到的因果瓶颈。ActPrompt 在 encoder 内注入 action cues，可以改变输出特征；冻结 clip readout 只能利用已有信息，不能补回基础特征丢失的细节。[RCORE](https://arxiv.org/abs/2601.16211)、[Invert4TVG](https://arxiv.org/abs/2508.07388)、[ActPrompt 机构出版页](https://www.microsoft.com/en-us/research/publication/actprompt-in-domain-feature-adaptation-via-action-cues-for-video-temporal-grounding/)

因此增加“原 S+ GT segment 的 motion-only 动作可读性”步骤，与 appearance-only、时间均值/单位置、文本上下文控制比较。同实体不同动作覆盖不足时保留未决。GT 用于独立 probe，不进入事件存在推理；分类词表只由 S train 决定，未见 verb 不能用其标签拟合分类头。

共同乱序/逆序两流是 clip 间时间次序控制，错位单流是局部跨流对应控制。两者不能混称动作绑定破坏。SlowFast 向量顺序逆置仍保留 clip 内原动作方向，方向无关动作、持续实体和周期动作会使扰动不适用。该限制是从输入形式作出的项目推断，不是论文结果。

### 3.2 交互绑定与实体证据

IAE-VTG 的 FDIM 从动作/实体 token 与两流响应生成 pair distribution，再汇聚 noun/verb marginals，而 EVIDENT 在 dense tokens 上蒸馏对象 cluster priors；前者偏时间上下文中的组合，后者提供更细空间 objectness，但不等同对象 tracks 或 verb-sensitive event verification。[IAE-VTG](https://arxiv.org/html/2609.09736v1)、[EVIDENT](https://arxiv.org/abs/2605.26104)

本次按 IAE 公开 Eqs. (3),(7)–(9) 推导：只有一对 noun–verb 时 pair probability 恒为 1，A*/E* 只剩 query token，最终 binding 可退化为文本常数；多对取 marginals 又可能丢失 joint correlation。该推导未获作者实际代码核实，不断言实际实现有 bug，也不否认论文报告的收益。它要求本方案的 J 必须保留原 visual values/residual，并把单对分层作为实施契约。

IAE 已有拒绝与组合泛化，因此不能仅靠“两个输出”或“未见组合”命名宣称创新。需在同输入、同原标签/容量对照、实际文本固定和 primitive 匹配条件下，证明可迁移 joint 的增量；对方训练/划分协议未逐项对齐前，不声称它完全不覆盖严格 S-only。

主轨没有空间 patch/track。它先研究 clip 级局部共同支持；同一帧不同实体的错角色事件可能不可辨识，必须记为粒度限制，而不是追加 identity loss。

### 3.3 证据传递与拒绝决策

CausalVTG 的 QR 在公开代码中是 pooled scalar，而 EviDETR 在 encoder、decoder experts 与 MR→HD 路径保留相关性；前者针对 relevance 决策，后者未验证 query absence，两者都可能带来收益，须与 binding 分开归因。[CausalVTG 官方实现](https://github.com/MxLearner/CausalVTG)、[EviDETR](https://arxiv.org/abs/2609.30724)

CausalVTG标题、作者与NeurIPS2025发表身份亦已核对[正式proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/95a8436cdc3981c37bcab4f684427213-Abstract-Conference.html)，不是仅据本地文件名认定。

HRVTG 则在推理期更新 LoRA，使用构造 CF 身份和 frozen reference。源码 reward 没有直接使用人工 GT 时间，构造脚本会用 PGT 覆盖事件时间；公开按 event 分割的 TTA/test 也不保证 video/语义隔离。与本项目差异是参数更新、输入身份和划分假设，不能简单写成“它依赖 test GT 泄漏”。[HRVTG 官方代码与论文](https://github.com/CVL-hub/HRVTG)

首版坚持 raw-stream→map→两任务的 bottom-up 路径，不从当前候选置信度生成 existence evidence。设置 map bypass、primitive map 替换和 candidate-specific 读出，验证共同作用；遮挡只作分布外敏感性，不能据共同下降宣布因果中介。

## 4. 对方案的统一修订

1. 输入/标签审计之后，先做动作可读性，再做 joint 验证；不得以一个失败 probe 证明所有信息消失。
2. 在统一视频投影前切分 CLIP/SlowFast，排除 TEF 的语义证据路径；依据实际 v_feat_dirs，而不是名称字符串推断流序。
3. 保证单对 J 仍直接依赖 visual values；多对聚合 pair-conditioned visual features，不只聚合两个 marginals。
4. H/P/C/J/T 核心矩阵保留，加单流、静态及时间干预控制；额外拟合分两轮有条件执行，不变成大网格。
5. J 超越容量匹配的 H/P/C 才研究 R；R 是同一时间支撑上的条件增量，非任意峰值相减、非概率意义已证实的 PMI。
6. 加入简单 local holistic map/control 与两输出接入消融；不把 MoE、ISA、TORC、CPR、VC/AR/VD 同时放进首版。
7. 不新增目标 U 标签、跨视频 absent 或变换后的自动负标签；方向敏感子集/解析规则只用原 S 预先定义。
8. 近邻状态和代码可得性按证据修正。所有实现/缓存/产物在新目录，旧数据与代码只读。

当前源码检查还发现原 loader 的缺特征日志会写到 data_path 旁；隔离需覆盖导入副作用，不只是把脚本放新目录。详见 [PROJECT_SOURCE_AUDIT.md](PROJECT_SOURCE_AUDIT.md)。

## 5. 回答研究问题与未决项

RQ1：这条机制有近邻，而且 IAE 已做接近的拒绝/组合泛化；剩余差异必须由 primitive 条件的视觉增量与严格联合评测获得。RQ2：raw-stream/clip 级时间对应、原 S+ 动作 probe、原 S− 事件 MIL 与 map 双输出可在原资源下定义；对象级 slots、encoder prompts、MLLM inversion 全套及在线 LoRA 不属于直接可移植主轨。RQ3：最小顺序是动作可读性→H/P/C/J/T 与单流/静态控制→J 成立后 R→共享 map 联合验证。

仍未决：可靠 binding-hard-negative 覆盖，token/cache 精确对齐，跨流真实时间来源，J 视觉增量与其跨语义迁移，残差 null 的外推稳定性，以及共同收益。现有论文不能替代这些本项目实验，也不能证明当前模型已经缺少绑定。若 holistic 或 AND 已同样有效，接受简单机制；若只有 J 成立，放弃盈余而不扫损失挽救。

## 6. 可追溯参考

- [BINDING_EVIDENCE_NOTES.md](BINDING_EVIDENCE_NOTES.md)：IAE/EVIDENT 公式、版本与输入粒度。
- [ACTION_TEMPORAL_NOTES.md](ACTION_TEMPORAL_NOTES.md)：RCORE/Invert4TVG/ActPrompt 及固定 commit 源码证据。
- [COUNTERFACTUAL_EVIDENCE_NOTES.md](COUNTERFACTUAL_EVIDENCE_NOTES.md)：CausalVTG/HRVTG/EviDETR、代码与协议差别。
- [PROJECT_SOURCE_AUDIT.md](PROJECT_SOURCE_AUDIT.md)：本项目实际数据/模型/输出和写入副作用。

代码静态核查没有得到训练效果复现；作者论文与候选实现不一致时保留两者边界，不用非官方实现否定原论文。发表状态和“未找到代码”均为本轮时间点的核查结果。
