# Counterfactual relevance、证据流与固定推理边界核查

核查日期：2026-10-01。本文只核查 CausalVTG、EviDETR、HRVTG；没有运行第三方代码、训练或复现性能。作者论文结论、公开代码事实与本项目设计推论分别表述。所有下载/克隆只进入新目录 `research/.local/`，这些缓存不应上传。

## 研究问题与证据等级

RQ1：counterfactual relevance 是否已等同于动作—实体绑定证据？RQ2：EviDETR 的 evidence preservation 是否已经验证 existence？RQ3：HRVTG 是否闭源，其推理协议能否直接用于严格 S-only → U+/U−？

证据来自用户提供论文的全文提取文本、官方 arXiv/项目网页及官方 GitHub 仓库。页码指 PDF 顺序页（1 起），文本行号指 `pdftotext -layout` 文件的物理行号。下面区间方便复核；代码行号随 commit 固定。这里只读检查，不把“代码存在”写成“性能复现”。

| 工作 | 已验证来源 | 核查状态 |
|---|---|---|
| CausalVTG | 用户本地 `16006_CausalVTG_Towards_Robust.txt`；[官方代码](https://github.com/MxLearner/CausalVTG) | 官方仓库成功克隆，commit `1e36a44d6e54d8b82b5c0675b7bbd40cda5b23c2`；头部、负样本与 loss 路径已检查 |
| EviDETR | [arXiv v1](https://arxiv.org/abs/2609.30724)、本地全文、[作者项目页](https://kevin-kas.github.io/Evi-detr-webpage/) | v1 日期为 2026-09-25。web 工具打开项目页失败，但 curl 成功取得作者 HTML；全文方法可核验，项目页未见公开代码链接，未核验独立代码 |
| HRVTG | [官方仓库及全文 PDF](https://github.com/CVL-hub/HRVTG)、[作者主页](https://quhongyu.github.io/) | PDF 与源代码均公开，commit `a2784c5d81f3b735cbebb90a85827ec185ec4e3e`；“闭源/尚未公开 PDF”应纠正。ECCV 2026 身份由作者仓库/主页确认，未独立核验出版社 DOI |

## 1. CausalVTG：video-level relevance 与事件绑定不同

### 全文核对

论文 §4.3 将 refined video features 与 query features adaptive pooling 后拼接，输入 FFN + sigmoid 生成全视频 relevance `r`，使用 Dynamic BCE 监督。训练负对为视频与语义不 grounded 的 query，推理由 `r` 决定是否输出定位。原文称 counterfactual contrastive learning，但 §4.3–4.4 的实际 QR 形式是二分类头，不应笼统转述成已经学到了逐时刻动作—实体 interaction。证据：PDF p.7；本地 `16006_CausalVTG_Towards_Robust.txt:431–458`。

论文还提出 front-door adjustment，经验训练分布经 K-means 采样得到 `x'`，注意力近似聚合 mediator 与 sampled inputs（PDF pp.5–6，文本 306–360）。这是论文的建模解释；观测 benchmark 与架构消融不能单独证明数据中的因果识别假设成立，也不能证明本项目 joint evidence 的因果性。应借鉴可操作的 negative relevance/control 思路，避免将“因果解耦已被证明”写入方案。

### 官方代码核对

- `research/.local/CausalVTG/models/new_vtg.py:55–57`：`contrastive_head = LayerNorm(2D) + Linear(2D,1)`。
- 同文件 `:81–84`：video/query 的 `mean(dim=1)` 拼接得全局 `relavent_score`，代码并非论文公式中的显式 adaptive pool 实现。
- 同文件 `:87–101`：batch 视频循环移位构造负对，以不同 video ID 判定负样本有效；`:103–131`：用 query embedding 余弦相似度寻找 hard-negative video，再经同一全局头得分。
- `research/.local/CausalVTG/models/loss.py:271–277`：拼接 positive/negative logits，正样本 target=1，negative target 由 `neg_mask` 得到，并交给 `loss_neg`。
- `research/.local/CausalVTG/configs/qvhighlights/qvhighlights_clip.py:66` 等指定 `DynamicBCELoss`；具体实现来自依赖，不在仓库本地 loss.py 中，本文未进一步核查该第三方依赖。

这些代码验证了“pooled holistic relevance + mismatch negatives”的路径，没有显式 action/entity primitive 分解或 excess-over-primitives 证据图。batch 不同视频也并不逻辑保证事件不存在：相似视频可能同时含同一动作；原协议可以如此训练，本项目不能把这种生成方式当作严格 U− 真值证明。

### 对新方案的约束

CausalVTG 是必要的 holistic relevance 近邻对照。新方案须保持相同 negative budget、特征与训练 split，比较 pooled joint representation、primitive co-activation、relation-aware binding 和 evidence surplus；只有 relation-aware 分支在相同 primitives 存在的 U− 上仍有收益，才支持绑定机制，而非额外二分类监督或模型容量解释。

## 2. EviDETR：跨阶段与跨任务传递证据，尚未验证拒绝

### 三个模块精确作用

| 模块 | 论文操作 | 对本项目的可借鉴部分与边界 |
|---|---|---|
| SFR | pooled query 与 clip 拼接，经 sigmoid local saliency head 得到 `a_t`，以 `a_t v_t` 重加权；再与 query tokens 做 tri-linear similarity 及双向 cross-modal attention，编码 memory | 可借鉴保留 query-relevant temporal representation；`a_t` 仍是整体 query 的局部分数，既未分解 motion/entity，也未统一 absolute existence scale |
| TTop2MoE | 每个 decoder temporal query 在 attention 后路由到两个专家，以归一化概率加权；三个 decoder stages、每 stage 八专家 | 是参数条件化与 refinement，并非 top-2 时间位置或 action/entity 双专家；不是事件绑定证据定义 |
| MR2HD | 最高 confidence span 经 GRU，与 SFR clip features 点积用于重加权；所有候选 span 经 1D ROIAlign 在 `{1,2,4}` scales 聚合，以 `exp(kappa p_i)` confidence weighting 得到 span evidence，再通过 clip 与聚合证据 cosine response 残差更新 memory，预测 highlight | 可借鉴显式局部证据流；实际方向是预测 MR span → HD，不是 existence 与 localization 共享同一外部验证过的绑定图 |

证据：本地 `EviDETR (arXiv:2609.30724).txt:69–91`（PDF p.2，SFR）；`:93–123`（pp.2–3，TTop2MoE）；`:125–156`（p.3，MR2HD）。

训练是 Hungarian matching 的 foreground/span/GIoU、saliency、alignment、load balancing 和中间 decoder supervision（文本 158–175）。论文评估 QVHighlights MR/HD、Charades-STA/TACoS localization，没有 S-only/U+/U−、event absence rejection 或 binding-specific counterexamples 的验证。三个 benchmark 上各自获得好结果也不能自动写成训练一个模型的跨数据集零样本迁移。

### 消融与代码发布边界

论文明确说明 TTop2MoE 的提升同时包含三阶段 refinement 和辅助监督，不能把全部增益归因于 sparse routing；dense FFN 加宽已解释相当一部分增益。证据：PDF p.4，文本 224–240。新方案任何容量增加须给 matched capacity 对照。

作者项目页缓存 `research/.local/EviDETR_project.html:54–58` 仅有 arXiv/BibTeX 按钮，`:109–115` 给架构图说明，`:233` 提到 implementation 沿用 DETR copyright。所检视 HTML 没有 Code/GitHub 仓库链接。**这表示本次未找到公开实现，不能推导“确定闭源”，也不能声称代码与 v1 已逐行匹配。**

本项目应保留 **bottom-up binding evidence map → localization 与 existence** 的逻辑方向，并加入 map bypass/detach 对照。不能把候选 span confidence 再包装为 existence evidence；否则 MR2HD 式反馈可能继承已幻觉的 span。localization 与 existence 必须在证据遮挡/替换后产生预先规定的共同变化，方能证明共享证据的用途。

## 3. HRVTG：已开源，但在线自适应协议不同

### 发布事实纠正

[官方仓库](https://github.com/CVL-hub/HRVTG) 含 `ECCV2026_HRVTG.pdf`、`src/cftool`、`src/open_r1/grpo_video_tta.py`、TTA trainer、eval 与运行脚本；本次已成功克隆。用户清单第 6 项应改为“PDF 与官方代码已公开；可只读核查”。

论文的三类 absence probes 是 textual alteration（action reversal、temporal misalignment、attribute/entity hallucination），visual pruning（删除预测 Pseudo-GT），hybrid fabrication（先移除 PGT 找 PHN，caption PHN 后从原视频移除 PHN）。PDF pp.7–8；本地 `HRVTG_paper.txt:330–387`。这些改变输入的 counterfactual controls 可启发诊断，但不能把“预测区间删除”自动当作真实事件全视频不存在。

### 参数、标签与评测严格区分

1. **参数确实更新。** 论文 p.8 文本 401、p.12 文本 602–609 指在线 LoRA/GRPO；`src/open_r1/trainer/grpo_trainer_tta.py:629–641` 进入 train step、`:720–748` backward、`:758–772` optimizer/deepspeed step。因此 backbone frozen 不等于推理模型参数 frozen。
2. **reward 没有直接用人工 GT 时间。** `src/open_r1/grpo_video_tta.py:127–161`：counterfactual refusal 奖励由 sample_type 与是否拒绝决定；positive consistency 奖励比较当前输出与 frozen reference 输出。trainer `:671–684` 传入 sample_type/ref_outputs；没有把 solution 送入这条 reward 路径。不能宣称其通过测试 GT 时间直接反传。
3. **它利用 positive/counterfactual 身份信号。** `grpo_video_tta.py:319–360` 从 original query 构造 positive，用已生成 CF 构造 absent sample；需要可信 genuine query 起点。对混合未知 U+/U− 的匿名输入流，这个起点不是无代价已知事实。
4. **时间标签读取与 reward 用途不同，且可能是 pseudo 标签。** TTA loader 读取 event.timestamp 成为 solution（`:320–331`）；在线 IoU monitor 使用 solution（`:675–677`）。更关键，`src/cftool/gen_cf_vphf.py:318–327` 从模型预测 PGT，不读原 event.timestamp，`:337` 将输出 event.timestamp 覆盖为 PGT，`:338–340` 用 PGT 形成 removal。依公开构造脚本得到的文件，solution 可能是 PGT，而非原人工标签。具体实验数据文件/跑法未核对，不能把所有报告指标统一断言成“人工 GT 监控”或“使用 GT 泄漏”。
5. **公开运行脚本与论文在线叙述需分开。** README `:29–31` 与 `src/cftool/tvg_split.py:4–27` 从 train_cf_full 按 event 随机对半拆 tta/test。event 划分并不保证 video disjoint，更不是 action/entity composition holdout。README `:89–102` 的 eval 加载已保存 adapter，在独立 test_cf_full 上测量；论文叙述 online stream（文本 333、385–387）。本次未运行其数据 pipeline，不能断言所有论文实验都与 README 完全一致。

### 对本项目的处理

HRVTG 可放进协议不同的讨论/额外对照表，不能把完整 TTA 当严格 S-only 固定参数主结果。可借鉴三类 controls 与分别报告 refusal/answer/localization 的指标思想；若离线制作训练 CF，只允许 S_train 数据，所有生成器、过滤器/阈值须在 U 评测前冻结。主方法不读取 U 的 genuine/absent label、不在线调 LoRA、不按 U+ 分组构造正样本 anchor。

需要评测不同误差：U+ 被拒绝、U− 被接纳、U+ 被接纳但定位错误。只报告 conditional IoU 会被拒绝难例抬高，因此同时报告无条件 U+ localization 与 coverage。对于 unknown original query，任何“一删 span 就存在性转负”的标签仅作为扰动假设，需检查重复事件和剪接 artifact。

## 4. 对方案的可执行修订建议（设计推论）

- **定义绑定而非共现。** action-only 与 entity-only maps 做 primitive；`min/product` 是 co-activation 对照。新 joint map 要对 same-time/wrong-role、正确 primitives 但不同事件/不同时间、相同实体错误动作提供超出这些对照的判别。
- **surplus 必須对齐同一时间支撑。** 用同一视频、同一候选时间支撑、同 primitive 证据预算比较完整事件与 primitive controls；不比较分别 max-pool 的任意三个 peaks。S_train 上确定 primitive baseline 与 residual 的形式，S_val 上冻结阈值；U 只一次评估。
- **保留反证条件。** 如果 matched-capacity holistic QR 已获得同样改善，或 joint map 的改善只在 primitive 缺失 U− 上成立，或遮挡绑定支持区只影响 score 不影响 localization，就不能声称缺失的是可迁移 interaction binding。
- **map 必须承担两项任务。** 显式标注 evidence map 在 localization 与 existence 的读取点，提供 bypass/detach、primitive substitution、matched-support occlusion 检验。可以使用学习型 local weighting，但不能把它命名为已校准 absolute existence；EviDETR 的局部 sigmoid 只验证了 relevance weighting。
- **机制与协议同时控制。** CausalVTG 式 pooled scalar、EviDETR 式 evidence propagation、纯 primitive co-activation 应各有独立对照；HRVTG 只列协议不同，避免将在线适应增益作为 offline S-only 绑定机制证据。

RQ1 的答案是未等同：CausalVTG 的公开 QR 实现仍是 pooled scalar；RQ2 的答案是未验证：EviDETR 研究 MR/HD relevance flow，没有 absence/binding 协议；RQ3 的答案是已公开但不能直接移植：HRVTG 在线更新参数且利用 probe 身份，严格固定推理须另设离线受控版本。
