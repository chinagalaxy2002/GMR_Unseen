# DAO-Verifier 独立审计：当前实验版本存在确定的标签泄漏

日期：2026-10-05。被核验目录：`experiments/agy_test/decomposed_action_object_verifier/`。审计产物独立存于本目录，旧训练/预测/报告未覆盖；本次没有训练新模型。

## 结论

**当前版本不能作为“缓解 GMR 未见语义拒绝退化”的有效证据。** 报告中的预测、AUROC、PairAcc 和 bootstrap 区间可复现，但输入提取流程通过正负例不同的标注完整性泄漏了标签。几乎全部新增分支的排序收益可以在不读取视频的条件下取得。必须修复数据路径并重新训练、验证和测试，才有资格判断 DAO 的动作–物体分解是否有用。

这个结论针对当前实现与产物。现有数据无法估计移除泄漏后 DAO 方法会达到什么性能，不能给出修复后的虚构数字。

## 已复现的部分

- 五个 checkpoint 均可加载，每个模型 3,646,730 个参数。
- 模型推理没有读取 `labels` 字段；梯度仅来自训练 S+/S−，checkpoint 与阈值仅由 Seen validation 选择；train/val/test 视频交集为 0。
- 从冻结 checkpoint 重算全部 test 分数，与原 `final_logit` 最大绝对误差不超过 1.91e-6；AUROC、Gap、PairAcc、FRR、RR 与原报告一致。
- Seen validation AUROC 和选出的阈值均复现。
- 独立实现配对视频聚类 bootstrap，按原方案对 1,217 个共享测试视频联合重抽样 2,000 次，所得区间与原报告一致：Seen 增益 [0.087974,0.095717]，Unseen 增益 [0.174422,0.197332]，Gap 缩小 [0.081755,0.106344]。

因此数值不是凭空生成的问题。问题在于这些数值衡量了包含标签信息的输入；bootstrap 无法消除这种系统性偏差。“仅 Seen 训练与选模”本身不能保证测试输入没有泄漏标签。

## CRITICAL：标注完整性变成了模型输入的标签通道

根因链条：

1. 发布数据的正例均有 `semantic_graph.action_span/object_span`，负例均缺少这两个字段。
2. [extract_features.py](../decomposed_action_object_verifier/extract_features.py) 第 134 行直接使用这两个标注字段提取动作与物体 token。
3. 第 50–52 行在缺少 span 时回退为整句均值向量。
4. 因而所有负例均满足 `q_act == q_obj == q_sent`，所有正例均满足 `q_act != q_obj`。
5. 正负标签由输入结构即可完全判断，与视频内容及未见语义理解无关。

我对所有五个 split 的 **train、val、test，共 15 个保存特征文件**全量核验，没有例外：

| Split | Train `‖q_act−q_obj‖` AUROC | Val AUROC | Test Seen AUROC | Test Unseen AUROC |
| --- | ---: | ---: | ---: | ---: |
| A1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| A2_alt | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| A3 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| C1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| C2_alt | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

该分数不需要训练，不读取视频，不使用测试标签来形成分数；标签只在计算 AUROC 时使用。它直接证明当前特征含有完美的标签通道。

相同文本的反证也成立。例如 A2_alt 的 `person drinking a glass of water.`，正例 `test33` 的动作 span=[7,15]、物体 span=[18,23]；负例 `neg_a1933a0789bbde8c` 的两个 span 均缺失，取到的动作向量余弦相似度仅约 0.7902，最大逐元素差约 2.2839。这里的主要问题是**取了不同文本位置**，远大于上次指出的旧文本编码数值差异。

在五组 U 中共发现 84 个同时具有正负样本的相同文本组。每组所选正负代表的动作/物体 span 均不一致，动作/物体向量均不一致。当前模型在这些 same-query 对上的高排序也不能解释为视觉理解。

机器可读证据：[annotation_label_channel.json](annotation_label_channel.json)、[exact_query_feature_identity.json](exact_query_feature_identity.json)。复验程序：[audit_label_channel.py](audit_label_channel.py)。

## 冻结模型干预：新增分支主要依靠文本通道

以下为当前 checkpoint 的诊断干预，不是重新训练的消融模型；每项都保留原权重，且没有利用 U 结果重新选择参数。

“仅负文本先验”使用 `−alpha_act*prior_act−alpha_obj*prior_obj`，输入只有 `q_act/q_obj`。“局部视觉置换”将 SlowFast 的 cand/start/end/global 与 CLIP 的 cand/global 成组换成其他视频的描述，保持 query、原 QD logit、槽表示和前景分数固定。

| Split | 原 DAO Unseen AUROC | 仅负文本先验 | 局部视觉置换一次 |
| --- | ---: | ---: | ---: |
| A1 | 0.6485 | 0.9999 | 0.6492 |
| A2_alt | 0.6159 | 1.0000 | 0.6190 |
| A3 | 0.6335 | 1.0000 | 0.6330 |
| C1 | 0.8821 | 1.0000 | 0.8776 |
| C2_alt | 0.6615 | 1.0000 | 0.6577 |
| 等权平均 | **0.6883** | **0.999978** | **0.6873** |

每组执行了五次局部视觉置换，结论一致。将所有视觉输入、QD 槽和原 logit 清零、前景设为常数 0.5，整个冻结模型仍得到宏平均 Unseen AUROC **0.999986**。单独动作证据的宏平均为 0.9841，物体证据为 0.9979，负文本先验的 matched-U PairAcc 为 1.0。

这不是“去偏彻底成功”的证据。文本先验本身近乎完美地识别了标签；从原分数减去它就能提高正例排名。局部视觉描述错配几乎不影响新增收益，当前“动力学验证”归因受到直接反证。

上述置换保留了查询条件化的 QD 表示，不能据此宣称整个系统完全不读取任何视频；它针对报告所宣称的**新增 SlowFast/CLIP 验证分支**。不读视频的文本先验诊断与无训练距离分数已足以判定标签通道，不依赖这项置换的因果解释。

完整冻结推理、各组件分数、五次置换、same-query 指标、bootstrap 与哈希见 [audit_metrics.json](audit_metrics.json)。各组逐样本诊断分数在 `{split}_audit_scores.npz`。

## MAJOR：候选窗口坐标被误读

HQ 缓存中的 `spans` 是归一化 `[center,width]`。DAO 的 `best_spans` 与 HQ 的 top-foreground slot 原值完全一致。但 `extract_features.py` 第 151–153 行将其直接当成 `[start,end]`：

```python
s0, s1 = best_spans_arr[i]
st = floor(s0*T)
ed = max(st+1, ceil(s1*T))
```

正确转换应先执行 `start=center-width/2`、`end=center+width/2`，再截断至 [0,1] 并转成帧索引。还需要确认截断后的实际视频序列长度与候选归一化所用长度一致。

错误裁窗使大量序列只剩一个时间步；此时 start/end 两半被设置为相同值，动力学流差分精确为零：

| Split | `center > width` 的比例 | 实际 `v_sf_start == v_sf_end` 的比例 |
| --- | ---: | ---: |
| A1 | 57.50% | 59.57% |
| A2_alt | 66.29% | 68.43% |
| A3 | 64.22% | 66.11% |
| C1 | 37.17% | 41.28% |
| C2_alt | 59.83% | 62.19% |

这些比例来自全部 test 特征。当前所谓“时序动力学”并非报告描述的预测候选窗内动力学。直接给旧 checkpoint 换成正确窗口再推理，只能作为分布变化诊断；修复后的正式结果必须重训。

## 其他需要更正的结论

- “Official Baseline” 的 0.5027 实际是上次指出存在源推理差异的 **HQ 缓存完整 logit 基线**。发布表是 0.5144；按原输入全量重放完整 logit 是 0.5033。正文必须准确命名。本次大幅增益不能通过更换基线名字或分数精度获得有效性，标签通道须先解决。
- regex 分词加字符比例映射不保证与 CLIP BPE token 对齐。修复后应从真实 tokenizer 取得可靠映射，或者把纯文本提取出的动作短语和物体短语分别统一编码；不能依据发布样本的标注是否缺失决定使用哪一种表示。
- 继承的正负 CLIP 文本编码来源差异仍存在，应统一编码所有文本，相同字符串共享完全一致的 token states。动作/物体 span 也必须由同一纯文本流程生成。
- 报告把四组有效 Action-CF AUROC 均值写为约 0.6418，而总 JSON 通过 `mean` 包含 C1 的 NaN，结果为 NaN。应写明四组均值及缺失原因，标准 JSON 使用 null。这是报告完整性问题，不能修复核心有效性。
- “未见负例 86%–97% 均为动作反事实”的表述仅适用于动作划分：C1 的 U− 中 267/270 是物体反事实，C2_alt 的 U− 中 219/254 是物体反事实、33/254 是动作反事实。不能据这些数据统一断言动作验证是全部增益来源。
- 固定 Seen 阈值仍有明显代价。C1 U− 只拒绝约 2.96%；A3 U+ 误拒约 42.71%，C2_alt 约 61.74%。按正确 cxw 转换诊断原候选，A3 的 U+ R1 从 44.27% 被 gate 降至 30.21%，C2_alt 从 38.26% 降至 18.26%。这些仍是有泄漏的模型结果，不可作为正式 GMR 性能。

## 必须先完成的修复与实验顺序

1. **封存当前版本并更正结论。** 当前 0.6883、84.87% 和区间只能记录为“存在标签通道的旧实现结果”，撤回“彻底解决”“根因证明”“目标完美达成”。不要覆盖旧产物来伪装成干净实验。
2. **重建输入。** 新目录中统一编码全部文本；动作/物体解析只接受原始 query，使用同一规则，禁用标签、construction type、source qid、partition 和正负样本不同的注释缺失情况。对相同文本断言 span 与 q_act/q_obj 一致。存在未解析词时的回退也按 query 本身决定。修正 cxw 裁窗及 BPE 对齐；重新提取 train、Seen validation、test，锁定 manifest。
3. **在训练侧验证修复。** 原字符串的重复实例应得到同一特征；直接计算缺失模式、向量距离等旧标签通道，确认它们不再因为正负来源而分离。同 query 的文本先验分数必须完全相同，因此其同 query 配对准确率应为 0.5。普通 text-only pooled AUROC 仍可能因措辞分布偏差大于 0.5，不能把这一点误判成编码泄漏。
4. **重新训练受控版本。** 原 GMR 基线与 DAO 共享同一干净输入、初始化和开发预算。至少对照 detector-only、动作-only、物体-only、完整分解、无 prior、无 pair loss、无时序差分/背景差分，以及不分解的同规模双流 verifier。不要使用当前污染输入训练的 checkpoint 作为修复后方法的正式模型。
5. **先证明视觉对应，再看确认集。** 完全相同 query 的存在/不存在视频排序、text-only、候选内多次视觉置换；区分额外表征、参数量、成对监督与 prior 的贡献。在 Seen 开发侧通过这些检查后，冻结方法，再访问新语义留出。当前五组 U 已反复查看，是探索集。
6. **确认成功才扩展。** 新留出、至少三个配对训练种子；报告 Seen/Unseen AUROC、Gap、Rej-F1、U+ FRR/U− RR、raw/gated 定位及 G-mIoU。先保证 Seen 非劣和真实 Unseen 增益，再扩至其他骨干。

现在应先修复输入，再评估研究方向。扩大模型、增加种子或对当前污染输入重跑 bootstrap，都不能使这批结果变成有效泛化证据。

## 复验

在仓库根目录：

```bash
PYTHONDONTWRITEBYTECODE=1 python experiments/agy_test/dao_audit_20261005/audit_label_channel.py
PYTHONDONTWRITEBYTECODE=1 python experiments/agy_test/dao_audit_20261005/audit_dao.py
```

前者验证 15 份特征的标签通道；后者加载冻结模型验证原预测、阈值、指标、分支与置换控制、bootstrap。程序不训练、不覆盖 DAO 的原产物。后者使用现有 GPU 和原特征。核心证据不需要联网或外部文献推断。
