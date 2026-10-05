# 清洁版 DAO-Verifier 的退化根因诊断

审计完成日期：2026-10-06。目录名称沿用工作开始日期。被诊断对象：`../decomposed_action_object_verifier/clean_features/`、`clean_runs/`。原代码、特征、检查点和报告均未覆盖。本轮没有训练新模型。

## 结论与下一步决定

**当前目标仍未达到，但不能由 PairAcc=0.4263 推断 CLIP 视频表征本身在 Unseen 上有害。** 这项分数使用了未投影文本隐状态；统一编码、采用 CLIP 的 EOT 文本投影后，A1 候选窗口 PairAcc 为 0.6314，全视频为 0.6378。保持一对查询共享同一错误视频的置换会降低配对准确率，说明现有视觉缓存含有部分可用的对应信号。

问题在于：这一对应信号较弱，跨查询分数又受文本偏置影响；现有 DAO 的训练和 prior 减除没有把它转化为稳定的存在性证据。物体分支的最终输出几乎等于负文本 prior，动作分支在训练配对上饱和而在验证与 Unseen 上退化。冻结消融显示，新增 DAO 分支提高 Seen 排序，却降低了五划分平均 Unseen AUROC。

**建议先做输入对齐、去掉自由 prior 的最小受控重训，不扩大网络或替换整个视觉骨干。** 是否改动作时序架构，应由这些对照后的跨视频泛化结果决定。

## 1. 旧标签通道和 cxw 裁窗错误确已修复

对 15 份 train/val/test 特征全量复查：

- `‖q_act−q_obj‖` 标签 AUROC 在 0.4443–0.5436 之间，不再有原版本 AUROC=1.0 的标签通道。
- 全部 11,961 个唯一查询文本的重复实例，在五划分和三个子集中均得到相同的 `q_act/q_obj/q_sent`，没有发现位级差异，也没有同文本的 action/object 元数据差异。
- top-foreground proposal 的 `[center,width]` 转 `[start,end]` 与保存结果最大误差为 0；15 份特征的 start/end SlowFast 描述差分为零的比例均为 0。

这些检查确认已知旧问题消失，不能据此宣称排除了所有可能的输入问题。尚有两项实现规范需要完善：

1. 提取器仍读取 `semantic_graph.action/object`，缓存键是 `(query, action, object)`，并非仅由 query 决定。当前数据没有观测到由此产生的同文本不一致，不应把它重新称为已确认的标签泄漏；后续实现应对 query 使用统一独立解析器。
2. regex 单词序号和字符比例回退仍不等于 CLIP BPE。按真实 tokenizer 重建位置，A1 test 的 5,160 个可直接核对实例中，105 个动作索引、132 个物体索引不一致，约为 2.03% 和 2.56%。这会取错 token；目前未单独重训量化其影响。

证据：[feature_audit.json](feature_audit.json)。

## 2. 磁盘上实际已经完成五划分，整体没有 Unseen 增益

冻结加载五个清洁版 checkpoint，重算全部测试预测，最大绝对误差为 1.91e-6。A1 少量浮点并列排序使 AUROC 与保存值相差约 1e-6，不影响结论。

| 划分 | HQ 原始 logit 基线 Unseen AUROC | 清洁 DAO | 冻结 DAO 去掉新增动作/物体证据 |
| --- | ---: | ---: | ---: |
| A1 | 0.5072 | 0.5016 | 0.5039 |
| A2_alt | 0.4174 | 0.4324 | 0.4328 |
| A3 | 0.4811 | 0.4790 | 0.4934 |
| C1 | 0.5655 | 0.5659 | 0.5693 |
| C2_alt | 0.5425 | 0.5306 | 0.5424 |
| 五划分等权平均 | **0.5027** | **0.5019** | **0.5084** |

Seen 宏平均从 0.7511 上升至 0.7587，Seen−Unseen Gap 从 0.2484 扩大至 0.2568。

独立按共享测试视频重抽样 2,000 次：

- 清洁 DAO 对 HQ 基线的 Unseen AUROC 差：−0.000816，95% CI **[−0.009180, +0.007718]**。没有证据证明其总体改善，也不能把微小负点估计当成显著总体下降。
- A1 对基线的差：−0.005585，95% CI **[−0.016500, +0.004886]**。A1 的单次下降也未达到该抽样检验的显著性。
- 清洁 DAO 对冻结 detector-only 的宏平均 Unseen 差：−0.006453，95% CI **[−0.010072, −0.002880]**。在固定现有权重的消融中，新增证据的净贡献确为负。

这里 detector-only 是从同一个联合训练 checkpoint 去掉新增证据，保留已训练 detector adapter；它不是独立训练的 detector-only 对照。区间反映固定模型的测试视频抽样不确定性，不包含训练种子和方法搜索的不确定性。

这里的 0.5027 是 HQ 缓存完整 logit 基线，脚本中 `baseline_fresh` 的命名不准确；不等于新鲜源推理 0.5033，也不等于发布表的舍入概率结果。下一轮应登记并统一基线输入来源。

证据：[frozen_diagnosis.json](frozen_diagnosis.json)、[paired_controls.json](paired_controls.json)。

## 3. 0.4263 的来源是无共同坐标依据的余弦，不能据此放弃 CLIP

现有动作/物体向量取自 `last_hidden_state` 的中间 token；[model.py 第 109–124 行](../decomposed_action_object_verifier/model.py) 的物体流直接与 CLIP 图像描述求余弦、逐维相乘。

本地 CLIP 实现的 `encode_text` 明确使用 **EOT 隐状态乘 `text_projection`** 得到图文对齐表示。维数同为 512 不能保证隐藏坐标与图像坐标一致。学习到的 MLP 可以尝试补偿错误坐标，但当前直接余弦不能解释成预训练 CLIP 的匹配能力。

我用同一权重、同一 tokenizer，按不依赖标签的字典序统一重新编码 A1 train/val/test 的查询与诊断短语；没有训练或选择分数方向。

| A1 诊断分数 | Unseen AUROC | 同视频、不同查询的 Matched PairAcc |
| --- | ---: | ---: |
| 当前动作 token 隐状态直接对候选视频求余弦 | 0.5316 | 0.4263 |
| **同一新编码完整查询：EOT 未投影** | 0.5532 | **0.4263** |
| **同一新编码完整查询：EOT 正确投影** | 0.5073 | **0.6314** |
| 正确投影 + 全视频池化 | 0.5171 | 0.6378 |
| 正确投影 + 最大帧相似度 | 0.5129 | 0.6538 |

EOT 投影前后的对照保持文本、编码来源和候选视频不变；能确认原 0.4263 不是合格的 CLIP 图文对齐诊断。也要看到，**投影后 PairAcc 增加，不代表总体 Unseen AUROC 增加**。表中所有变体都是机制诊断，没有依据 U 选一个最大值作为最终方法。

缓存视频的原始编码权重身份尚未独立核验，重新编码文本并不等于重新提取原图像；后续应登记视频编码来源。上述数值是现有视频缓存上的实测结果。

### 保持配对结构的视频置换

A1 的 312 对来自 258 个视频，正负成员始终使用同一个视频，但查询不同。它并不是“相同 query 的存在/不存在视频”评测。

- 正确投影全视频 PairAcc：**0.6378**，视频聚类 95% CI [0.5836, 0.6948]。
- 将一对查询同时配给同一个错误视频，并按原视频成组置换五次：PairAcc 为 **0.5641、0.5545、0.5865、0.5673、0.5833**。实际视频对五次置换的配对增益区间均排除零。
- 将视频替换成固定的无标签训练视频均值，分数仅由 query 决定：PairAcc **0.5673**。所以 PairAcc 中存在措辞或语义难度贡献；全部 0.6378 不能归因于视频对应。
- A1 另有 21 个完全相同查询的正负跨视频组，共 34 个比较。正确投影候选/全视频的准确率为 0.4118/0.4412，固定 query 分数为 0.5。这是小样本诊断，尚不支持强跨视频存在性泛化结论。

### 候选窗口不是 0.4263 的主要解释

让配对两个查询都使用正例的预测候选窗，正确投影 PairAcc 为 0.6442；用正例 GT 窗作为 oracle，仍为 0.6442。候选定位有错误，但该配对指标没有因 oracle 裁窗产生明显提升，不能把失败全部归于裁窗。GT 仅用于诊断，没有进入任何正式训练或方法分数。

逐帧先归一化再池化，与当前候选池化的 PairAcc 相同，AUROC 差约 1e-4；两视频流按共同最短长度截断与 QD 数据加载方式一致；A1 本轮没有超过 200 个时间步的样本。因此这些也不是本轮主要证据。

证据：[A1_clip_diagnosis.json](A1_clip_diagnosis.json)、[paired_controls.json](paired_controls.json)，逐查询分数在 `A1_{train,val,test}_clip_scores.npz`。

## 4. 已学习 prior 主导物体流，动作流存在明显泛化落差

### 物体流：名义视觉证据近乎等于负文本 prior

物体流定义为 `evidence_obj = raw_obj(video, query) − prior_obj(query)`。在 A1 test：

- `raw_obj` 标准差 **0.01420**；`prior_obj` 标准差 **0.29766**，约为前者 21 倍。
- `evidence_obj` 与 `−prior_obj` 的相关系数 **0.999492**。
- 原物体分数 Matched PairAcc **0.6090**，减 prior 后为 **0.5032**。
- 五个 checkpoint 的相同相关系数均超过 **0.9992**。

这不是旧标签通道复发，而是学习到了依赖语言分布的评分。当前 prior 同时从分类损失、pair loss 获得梯度，另用 `MSE(prior, raw.detach())` 正则；没有强制它等于独立的视频边际期望。“减去一个仅文本 MLP”本身不足以保证去偏。

这也不是“只去掉 prior 就必然解决”：A3/C2_alt 的 raw object 本身在 U 上就表现差。必须重新训练无 prior 版本，才能检验训练路径和分支结构的贡献。

### 动作流：训练对饱和，验证与未见语义收益不足

A1 有 449 个动作训练反事实对，动作 evidence 的训练 PairAcc **1.0000**；Seen validation 的动作反事实 PairAcc **0.6467**；Unseen Matched PairAcc **0.4840**。动作分支训练 AUROC 为 **0.6690**，Seen validation 为 **0.5413**。

SlowFast 到文本的映射从随机初始化开始，冻结的 checkpoint 约有 365 万参数。上述落差支持“记住训练对、迁移不足”的诊断；尚没有独立实验区分是参数量、成对采样、优化轮数、时序表示还是语义对齐导致。当前 `end−start` 是平均 SlowFast 描述之差，并不是另行提取的光流；不能仅凭分支名称认定它已经学到动作动力学。

QD 的训练缓存本身 AUROC 几乎为 1，测试 Seen 约为 0.79。基于 in-sample detector 分数再训练融合器，可能进一步造成训练/推理分布差；这是需要通过 out-of-fold 或独立开发视频缓存检验的假设，不是本轮已分离证明的原因。

证据：[fit_diagnosis.json](fit_diagnosis.json)、[frozen_diagnosis.json](frozen_diagnosis.json)、[paired_controls.json](paired_controls.json)。

## 5. 一个无训练的校准诊断：问题包含跨查询偏置

预先固定以下定义，训练视频参考均值不读取标签、不拟合系数：

`score(q,v) = cosine(projected_EOT(q), pooled_video(v)) − mean_train_video cosine(projected_EOT(q), video)`。

先对训练集唯一视频的全局归一化特征求平均，然后对所有查询使用同一参考。A1 的结果：

| 分数 | Seen validation AUROC | Test Seen AUROC | Test Unseen AUROC |
| --- | ---: | ---: | ---: |
| 候选原始余弦 | 0.5270 | 0.5296 | 0.5073 |
| 候选减训练视频参考 | 0.5758 | 0.5753 | 0.5384 |
| 全视频原始余弦 | 0.5038 | 0.5098 | 0.5171 |
| 全视频减训练视频参考 | 0.5562 | 0.5573 | 0.5528 |

这说明即使保持视觉编码不变，跨查询校准也会改变总体 AUROC；同 query 的配对结果不变，因为该项会抵消。**这些是探索性独立分数，Seen 明显低于原 GMR；没有与 GMR 正式融合、没有五划分确认，不能视为目标达成。** 它支持下一轮先做可解释、固定参考的校准对照，避免把任意可训练 prior 当成去偏。

证据：[A1_reference_centering_diagnosis.json](A1_reference_centering_diagnosis.json)。

## 6. 推荐最小实验矩阵与决策条件

先统一文本编码并冻结规范：独立 query 解析、实际 BPE 对齐；整句或独立动作/物体短语均用各自 EOT 投影；同文本共享字典；登记视频编码权重与池化方式。token 隐状态仍可用作学习表示，但与图像直接比较前必须有明确对齐方式。

| 优先级 | 实验 | 需要回答的问题 |
| --- | --- | --- |
| P0 | 原 GMR 与独立训练 detector adapter，输入来源一致 | 增益是否来自 detector 适配，而非新验证证据？ |
| P1 | 对齐 CLIP 的小容量验证器，**无自由文本 prior、无 SlowFast 新分支** | 正确跨模态输入能否形成跨视频存在性证据？ |
| P1 | 相同模型加入固定无标签训练视频参考校准 | 跨查询偏置校准能否改善 AUROC，同时保持视觉对应？ |
| P2 | 在 P1 基础上加入 SlowFast，先平均描述、再添加 start/end 差分 | 动作流是否提供独立于外观的迁移收益？ |
| P2 | 相同容量与特征，pair loss 有/无；同视频改词对与相同 query 跨视频对分别报告 | 成对监督是否只提高改词排序，却没有提高真正存在性识别？ |
| P3 | 融合训练使用 out-of-fold detector 输出或独立开发视频；至少三个配对种子 | in-sample stacking 和随机性是否影响结论？ |

候选模型先由 Seen validation 的 AUROC、同 query 视频对应、语言对照、视频置换共同诊断，不按已知 U 结果调符号、权重或选 epoch。跨视频训练负例应有不存在的证据，不能仅因为随机视频未标注某句就默认它不存在。

是否扩大架构的分支决策：

- 如果对齐后的无 prior 版本在 Seen 跨视频验证已有对应收益，再开展融合、SlowFast 增量和留出语义确认。
- 如果只有同视频改词 PairAcc 改善，而同 query 跨视频和门控后的定位没有收益，先改监督/评分目标；此时扩大网络不能解决证据类型不匹配。
- 如果在 GT 窗诊断和独立跨视频验证上，现有视频表征仍缺少可用信号，再考虑更强的视频语言或动作编码器，另列预算与预训练数据对照。

现有五划分 U 已多次查看，适合作为探索结果；确认实验需要新的语义留出。成功判据至少包括真实 Unseen AUROC 增益、Seen 非劣、Gap 缩小，以及固定 Seen 阈值下的误拒/拒绝与定位表现。不能以缩小 Seen AUROC 换取 Gap 数值改善。

## 复验与产物

在仓库根目录运行，所有输出只写本诊断目录：

```bash
PYTHONDONTWRITEBYTECODE=1 /home/guoxiangyu/miniconda3/envs/univtg/bin/python experiments/agy_test/dao_root_cause_20261005/diagnose.py features
PYTHONDONTWRITEBYTECODE=1 python experiments/agy_test/dao_root_cause_20261005/diagnose.py frozen
PYTHONDONTWRITEBYTECODE=1 python experiments/agy_test/dao_root_cause_20261005/diagnose.py fit
PYTHONDONTWRITEBYTECODE=1 /home/guoxiangyu/miniconda3/envs/univtg/bin/python experiments/agy_test/dao_root_cause_20261005/diagnose.py clip --split A1
PYTHONDONTWRITEBYTECODE=1 python experiments/agy_test/dao_root_cause_20261005/paired_controls.py
PYTHONDONTWRITEBYTECODE=1 python experiments/agy_test/dao_root_cause_20261005/reference_centering.py
```

为了复用现有 text-only CLIP，程序直接加载本地 tokenizer 和模型实现，不依赖 torchvision 图像变换。所有视觉干预和 GT 窗分数都是冻结模型/特征诊断，没有重训、选择新的最终方法或覆盖旧版本结果。
