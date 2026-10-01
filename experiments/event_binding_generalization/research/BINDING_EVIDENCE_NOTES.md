# 绑定与实体证据核查：IAE-VTG / EVIDENT

核查日期：2026-10-01。范围：本地完整论文文本、作者及 arXiv 官方页面、项目现有源码的只读检查。本笔记不包含训练结果。全文提取位于 `research/.local/`，不应上传；原 PDF 位于 `/home/guoxiangyu/paper/Openword/paper/`。下面“推导”和“建议”均不等于论文作者已验证结论。

## 研究问题和证据边界

RQ1：已有 action–entity interaction 是否已经覆盖定位、拒绝和组合泛化？RQ2：公开公式是否保证单 noun–verb 对也有视觉依赖的 binding？RQ3：实体 slots 能否直接落到严格冻结的现有 pooled CLIP/SlowFast 输入？

检索从正向 binding、反向文本退化、实现资源三个视角执行；本子任务按父任务限定范围串行核查，不另建代理。方法细节来自本地全文，不根据摘要或搜索片段推断。官方实现未发现时明确保留空缺，不以第三方实现冒充复现。

## 官方来源与状态

| 工作 | 已核实来源 | 状态与实现限制 |
|---|---|---|
| IAE-VTG | [arXiv abstract](https://arxiv.org/abs/2609.09736)，[官方 HTML](https://arxiv.org/html/2609.09736v1) | arXiv v1，2026-09-09；PDF 有 IEEE TIP 模板页眉，但 abstract 页面未给正式发表信息，模板不能证明录用。全文未附 GitHub 地址；检索 exact title / IAE-VTG + github/code 未取得作者关联的官方仓库。不能完成 FDIM 源码级核验。 |
| EVIDENT | [arXiv abstract](https://arxiv.org/abs/2605.26104)，[第一作者主页](https://ahngeo.github.io/) | arXiv v1，2026-05-25；作者主页当前 Publications 明确列 NeurIPS 2026。应写“作者官网列 NeurIPS 2026”，不把未检索到的正式 proceedings 当作已核验。作者该项只有 arXiv 链接；全文无官方仓库链接，exact-title + github 检索未取得可确认官方源码。 |

这里“未取得”是本次检索结果，不是断言闭源。没有下载未经确认的同名仓库，没有启动模型。

## IAE-VTG：可借鉴的机制与关键反证

本地证据：`research/.local/IAE-VTG (arXiv:2609.09736).txt`，原 PDF pp. 3–5，对应文本行 190–458；FDIM pairing 和 binding 特别见行 339–421，Eqs. (1)–(9)。

FDIM 用 noun/verb role mask，将 motion 作为 query 访问 verb tokens、appearance 作为 query 访问 noun tokens；保留跨 attention 的 token 响应，构造 noun×verb 候选对。pair logit 包含三项：角色响应的 log 和、文本 compatibility MLP g、视觉上下文 compatibility MLP h。h 的参数来自 appearance/motion 与 noun/verb tokens，因此论文设计并非纯文本 scorer。然而最终 binding 并不是直接在视觉 values 上运算：Eq. (7) 的 A* 和 E* 是原 query verb/noun token 在 pair marginals 下的加权和，Eq. (8) 连接 A*、E*、逐元素乘积和绝对差，Eq. (9) 由 MLP/sigmoid 生成 binding。

**公式层面的单对退化（本次推导，未经作者源码核实）**：当候选只有一个 noun 和一个 verb 时，pair distribution 的唯一项恒为 1，因此 A*_t=x_v、E*_t=x_n；相同 query 所有时间位置的 Eq. (8) 输入相同，S_binding(t) 变为文本条件常数。即便 h 看到视觉，唯一项 softmax 也会将其变化消掉。在标准不带视觉 residual 的 Eq. (1) attention 中，只有一个有效 key/value 时响应同样恒为 1。不能据此断言作者实际代码有 bug：源码可能增加论文未写出的 residual 或不同值路径；但不能照抄这些公式并承诺获得局部事件证据。

**多对限制（推导）**：分别取 noun、verb marginals 会丢失联合 pairing correlation。不同 joint distributions 可能有相同两组 marginals，而 Eq. (7)–(9) 对其给出相同响应。文本 compatibility g 也可能学习常见组合先验。应分别对语言先验、视觉交互和 joint-pair 保真作检验；“使用两个流”不证明身份级绑定。

ISA 是训练时的 Hungarian matching cost 增项：IoU 乘 backbone saliency 与 binding 的绝对差。差异为零既可对应“两者都高”，也可对应“两者都低”，因此一致性并不自动等于足够视觉支持。proposal refinement 的分类梯度训练 FDIM；matching 本身不反传。现方案首版不改变匹配是合理的隔离选择。

**新颖性必须收紧**：本地 pp. 10–11，文本行 866–931：Table VI 已做 NA-VMR 正定位和 RA-ID / RA-OOD 负查询拒绝；Table IX 已做 Trivial / Novel-C / Novel-W。所以“action–entity binding 同时用于 localization 和 existence，并有组合泛化”不足以作为本项目差异。该文已有这些接近实验，但这些表没有证明严格目标 S-only → U+/U− 协议、阈值在 U 的迁移或 primitive-conditional 额外证据。因此需要强调受控协议和可证伪的 evidence surplus，而不是宣称先首次引入 binding。

## EVIDENT：实体 bottleneck 可提供什么，不能提供什么

本地证据：`research/.local/EVIDENT (arXiv:2605.26104).txt`，原 PDF pp. 5–8，文本行 333–340、388–525。

EB Adapter 输入每帧 N 个 dense visual tokens，插入 MLLM early decoder layers。Slot Attention 在每帧独立进行，先沿 slot 轴 softmax，再沿 token 轴归一化，以 GRU/MLP 更新 slots；最终使用 assignments 重建原 token 个数并 residual up-project。它不是在每帧一个 pooled vector 上提取有监督的真实对象 tracks，也没有这些公式中的跨帧身份一致性保证。

EB Distillation 明确使用 DINOv2 patch features：2×2 pooling 与 MLLM spatial resolution 对齐，每帧 K-means 得到 K=slot 数的 binary cluster maps，再按 patch-averaged BCE 做每帧 Hungarian matching，匹配后的 BCE 蒸馏 objectness prior。作者指出单 bottleneck 不足，缺 teacher 时 slots 接近均匀。这意味着仅加几个 learnable slots 不可以标为 EVIDENT 式显式实体证据。

E2V gating 离线用 Qwen3-4B 提取 subject/object，计算 reconstructed visual tokens 的 frame mean 与两种文本 token 的 cosine，min-max normalization 后相乘，再调制 adapter output。它关注 subject/object 共可见性；没有 verb-sensitive motion 判别，因此不能将高 gating 当作 queried action occurrence，更不能当作完整事件存在概率。该论文是源数据集到其他视频域的 MLLM VTG，不等于本项目 seen semantics 到 unseen semantics 的负查询存在测试。

严格主轨冻结 pooled CLIP/SlowFast 时，缺 N>1 空间 patch tokens、MLLM decoder 与教师 cluster map，EB Adapter / distillation 无法直接移植。重新提取 patch tokens、引入 DINOv2、采用 LLM parser 或 LoRA 都应列为额外资源轨并重设比较条件，不能偷偷进入严格 S-only / 原冻结输入的主结论。可迁移的是“显式证据容量和监督必须被审计”的原则。

## 原工程只读核验

IAE/EVIDENT 官方实现没有确认，因此本节只核验当前工程，不能冒充两篇方法的源码核验。

- `/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/training/flash_vtg_gmr/dataset.py:552–577, 581–622`：各流先独立归一化、截断到 min_len，再在 feature 维 concatenate；返回 `(Lv, D)`，没有显式空间 patch 轴。按 min_len 截断是长度处理，不证明两流时间戳或 receptive field 对齐。
- `/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/models/flash_vtg_gmr/model.py:161–163`：拼接后先通过统一 input_vid_proj。需要在新目录 wrapper 保留原流切分和独立投影，不能把统一 hidden 的任意坐标拆成 motion/entity。保持原 holistic 路径作控制。
- 同模型 `model.py:192–205` 将时序视频和文本 token 合并进入 transformer，并生成 pyramid。这证明可以在独立 adapter 中提供局部 evidence map，但不证明其原输出有对象身份。

尚未逐一检查实际 feature NPZ shape、时间戳和 tokenizer offset；执行前必须在 S train 做样本级审计。所有读过的旧代码均未修改。

## 对 METHOD_SPEC 的具体补充建议

1. 在输入定义加入“单 noun–verb 对非退化”硬要求：J 直接保留 m_t/a_t 的视觉 values 或 residual，pair weights 只控制视觉证据的聚合，不仅加权文本 values。先在固定 query、替换视频或平移两流的情况下检查 map 是否能变化；单对和多对分层报告。
2. 若保留多 noun/verb pairing，聚合 pair-conditioned visual interaction features 后再求和，不先取两组 marginals 从而丢失 correlation。对照独立 marginal、同时间 AND 和 joint 分支，参数量与训练监督尽量对齐。
3. 明确严格主轨仅支持 clip-level temporal correspondence，禁止宣称 object/agent identity binding；身份交换样本作为能力上限审计。如果错误施事/受事只能靠空间身份区分，原 pooled 输入可能不足，结果应判为表征限制而非追加损失。
4. 设 IAE-inspired 机制为结构对照，注明按公式复现且官方源码未确认。不能把单对退化版本的失败当作全面否定 IAE 作者结果，也不能用自己的修正结果替代官方方法。
5. 把 EVIDENT 归入“资源不匹配但给出实体证据监督原则”的邻接工作，移除直接接入 slots/distillation 的首版暗示；可选 patch/teacher 轨须单独说明额外数据与模型资源。
6. 证据盈余必须在 J 对 capacity-matched primitive-only / AND 增量成立后再研究。文本-only、motion-only、appearance-only、对齐破坏是机制诊断；不自动给予人工扰动 absent 标签。若 J 没有视觉依赖或只赢最弱加性对照，停止 surplus 方法化。
7. 新颖性定位改为“严格冻结输入和 S-only 训练下，验证可迁移视觉 joint 是否比 primitive 共激活更有效，以及相对 primitive 的条件证据是否改善 U+/U− 与同 map 定位”。这仍是待证实机制，不是已成立研究贡献。

## 回答研究问题

RQ1：IAE 已覆盖接近的定位、拒绝、组合泛化，差异必须落到协议与 primitive-conditioned 增量。RQ2：公开公式不保证单对视觉 binding，且有可明确推导的退化；当前实现应在训练前解决该问题。RQ3：EVIDENT 依赖 dense tokens 和额外 DINOv2 objectness 蒸馏，不能直接移植现有 pooled 冻结输入；当前证据粒度必须诚实限制到时间局部共同支持。
