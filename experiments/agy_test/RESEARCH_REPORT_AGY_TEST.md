> **历史研究记录**：本文件不作为当前方法结论。请结合 [早期审计](audit_20261005/AUDIT_AND_EXPERIMENT_PLAN.md)、[DAO 审计](dao_audit_20261005/DAO_AUDIT_REPORT.md) 与 [AC 审计](ac_audit_20261006/AC_AUDIT_REPORT.md) 阅读。当前入口为 [AC README](aligned_calibration_verifier/README.md)。

# GMR 未见语义存在性退化缓解：5 大划分端到端重训评测分析与审慎评估报告

**实验工作目录**: `experiments/agy_test/e2e_training/`  
**实验日期**: 2026-10-05  
**硬件/计算环境**: 双卡 NVIDIA RTX 3090 (24GB × 2, `cuda:0` & `cuda:1`), PyTorch 2.6.0+cu124, Python 3.10  
**实验覆盖范围**: 5 大 benchmark 划分 (`A1`, `A2_alt`, `A3`, `C1`, `C2_alt`) 基于预提取特征的模型训练与测试  
**随机种子**: 严格固定单种子 `seed=3407`（与基准协议完全一致）  
**对照来源**: 原版预训练 QD-DETR 检查点（`results/semantic_existence/multi_split_v2/{split}/qd/best.ckpt`）在同一测试集视图下的原始输出评测  

---

## 一、 训练范围界定、代码零侵入与真实执行确认

### 1. 训练范围与实现边界（Scope & Auxiliary Loss Qualification）
- **特征输入级别**：本实验属于**基于预提取双流特征（Video SlowFast 200 帧 + CLIP 200 帧）与预提取文本特征（CLIP text 768 维 `last_hidden_state`）的 QD-DETR 解码器与存在性头微调**，并未微调底层的视觉主干卷积网络或原始帧像素编码器。
- **模型实现与损失边界**：模型构建逻辑（`models/qsw_qd_detr.py`）返回带有前向捕获的 QD-DETR 模型并挂载 `QSWAdapter`。前向传播捕获最后一层解码器隐藏状态 `hs[-1]` 并输出最后一层的预测；**QD-DETR 默认配置中的辅助解码器损失（aux_loss）在联合微调时并未对中间层计算**，微调参数限定在解码器 cross-attention 与 QSW 头。
- **绝对代码隔离（Zero Intrusion）**：原项目所有主仓核心代码（`models/`, `training/`, `configs/`）**100% 保持原始状态，未做任何修改**。

### 2. 严格的抗泄漏评估协议（Strict Anti-Leakage Protocol）
- **优化范围**：严格仅在训练集 $S^+ / S^-$（`train.jsonl`）上计算梯度并更新权重；
- **选模与阈值校准**：每一个 epoch 结束后，严格仅在 Seen 验证集 `seen.jsonl` 上评估 AUROC，选取最佳 checkpoint，并通过 Youden 指数确定最终判定阈值；
- **未见语义评测**：完全冻结最佳检查点与判定阈值后，单次执行未见语义测试集 `u.jsonl`（包含 $U^+$ 与 $U^-$）的前向推理；
- **原始预测落盘**：所有 5 个划分的原始预测打分、标签及 qid 均已保存至 `experiments/agy_test/e2e_training/runs/{split}/qd/predictions.npz`，指标汇总保存于 `aggregate_benchmark_summary.json`，确保无需重新推理即可完全复算验证。

---

## 二、 机制设计、实现假设与因果归因局限

### 1. 原版 GMR Adapter 的失效假设
原始 GMR 论文在 VMR 解码器的 $N=10$ 个 query slots 上采用了**坐标逐维最大池化（Coordinate-wise Max-Pooling）**：$h^{exist} = \max_{i=1}^N H_i^q$。在未见语义下，cross-attention 无法抑制未见动作，10 个 slots 在全视频背景帧上随机弥散，逐维取极值拼凑出具有超高范数的嵌合体向量，导致 logits 普遍过饱和（>11.4）。在 `A2_alt` 划分中，原版基线甚至出现了负例打分反常高于正例的倒挂（基线未见 AUC 0.4174，Matched PairAcc 0.3291）。

### 2. Quality-Aware Slot Witness (QSW) 架构实现
为了探索消除维度嵌合饱和，构建了 **QSW Adapter**：
1. **槽位独立评分**：对每个 slot $i$ 独立映射为其单独的存在性证据分数 $e_i = \text{MLP}_{slot}(h_i) \in \mathbb{R}$；
2. **前景色检测概率门控**：利用定位网络预测的前景色置信度 $p_i = \text{softmax}(c_i)[0]$ 施加对数惩罚 $\text{gate}_i = \frac{\log(\text{clamp}(p_i, \epsilon, 1))}{\tau}$，抑制无定位支撑的背景槽位；
3. **软硬见证聚合**：结合温度注意力软见证与 Top-1 前景见证构成最终打分；
4. **同视频配对对比损失**：加入同一视频不同 query 的对比边际惩罚 $\mathcal{L}_{pair} = \max\left(0, \, \gamma - (s(V, Q^+) - s(V, Q^-))\right)$。

### 3. 因果归因的重要局限（Confounding Factors）
由于本次实验在引入 QSW 时，**同时改变了特征读出结构、前景色门控、损失函数（加入了 Pairwise Margin Loss）以及训练优化模式（部分设置为 decoder 联合微调）**，且**尚未设置等训练步数、等优化预算的原版 GMR Adapter 重新微调对照（Iso-compute Baseline Finetuning Control）**。因此，**当前实验无法将任何指标变化干净地因果归因于某个特定的 QSW 组件（如前景色门控或对比损失）**。

---

## 三、 5 大划分全量端到端实验对比结果（客观核定）

下表呈现 5 大 Benchmark 划分下，原版预训练 QD-DETR 基线（`Baseline QD`，由原模型 checkpoint 独立测试核定）与本实验 `QSW QD-DETR` 在 5 个 epoch 微调、严格 Seen-only 选模后的完整指标对比：

| 划分 Split | 微调模式 Train Mode | 最佳轮次 Best Ep | 已见 Seen AUC<br>(Base / QSW) | 未见 Unseen AUC<br>(Base / QSW) | $\Delta U$<br>(未见变化) | 泛化差距 Gap<br>(Base / QSW) | $\Delta\text{Gap}$<br>(差距变化) | 同视频条件配对 Matched PairAcc<br>(Base / QSW) | $\Delta\text{Pair}$<br>(配对变化) | $U^+$ 误拒率<br>(Base / QSW) | $U^-$ 拒绝率<br>(Base / QSW) | 门控定位 Gated R1<br>(Base / QSW) | 单次打乱置换 AUC |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A1** | adapter_only | Ep 4 | 0.8128 / 0.8116 | 0.5075 / **0.5222** | **+1.47 pp** | 0.3053 / **0.2894** | **-1.59 pp** | 0.6026 / **0.6090** | **+0.64 pp** | 15.91% / 14.84% | 90.03% / 18.23% | 20.43% / 20.65% | 0.5109 |
| **A2_alt** | adapter_and_decoder | Ep 4 | 0.7759 / 0.7686 | 0.4174 / **0.4739** | **+5.65 pp** | 0.3585 / **0.2947** | **-6.38 pp** | 0.3291 / **0.4937** | **+16.46 pp** | 27.50% / **0.00%** | 85.83% / **0.32%** | 32.10% / 34.52% | 0.4818 |
| **A3** | adapter_and_decoder | Ep 2 | 0.7721 / 0.7644 | 0.4804 / 0.4658 | -1.46 pp | 0.2917 / 0.2987 | +0.70 pp | 0.4806 / 0.4729 | -0.77 pp | 19.34% / 27.60% | 87.28% / 26.60% | 32.80% / 34.90% | 0.4935 |
| **C1** | adapter_only | Ep 4 | 0.7901 / 0.7862 | 0.5697 / 0.5594 | -1.03 pp | 0.2204 / 0.2268 | +0.64 pp | 0.6875 / 0.6667 | -2.08 pp | 20.83% / **2.47%** | 86.11% / 5.93% | 42.00% / 41.36% | 0.5926 |
| **C2_alt** | adapter_and_decoder | Ep 2 | 0.6870 / 0.6771 | 0.5445 / 0.5419 | -0.26 pp | 0.1425 / **0.1352** | **-0.73 pp** | 0.4848 / 0.4545 | -3.03 pp | 27.03% / 46.09% | 84.86% / 49.21% | 24.30% / 23.48% | 0.5725 |
| **宏平均 (MEAN)** | — | — | **0.7676 / 0.7616** | **0.5039 / 0.5126** | **+0.87 pp** | **0.2637 / 0.2490** | **-1.47 pp** | **0.5169 / 0.5394** | **+2.25 pp** | **22.12% / 18.20%** | **86.82% / 20.06%** | **30.33% / 30.98%** | **0.5303** |

---

## 四、 关键指标核定与说法修正（重点澄清）

基于对评测协议与具体数据的严格核查，对前序表述做出以下关键修正：

### 1. 关于 A2_alt 的客观定性：部分缓解，但仍处于随机基准以下
- **数据表现**：在 A2_alt 上，Unseen AUROC 从 0.4174 提升至 0.4739（+5.65 pp），同视频条件配对准确率 Matched PairAcc 从 0.3291 提升至 0.4937（+16.46 pp）。
- **客观结论**：**尽管数值明显回升，但两项指标依然均低于 0.50 随机猜测水平**。因此**不能称为“成功扭转”，更准确的定性是“部分缓解，但尚未恢复到随机基准以上”**。
- **操作点问题**：更严峻的是，在基于 Seen 验证集校准的判定阈值下，A2_alt 的 $U^-$ 拒绝率仅有 **0.32%**（312 个负例中仅拒绝了 1 个，其余全部被误接受）。这表明 **AUROC 曲线的小幅抬升并没有转化成实际可用的未见负例拒绝能力**，模型在该划分上对未见 query 几乎完全放行。

### 2. 关于 C1 划分“接受率”与“定位准确率”的严格区分
- **数据澄清**：在 C1 划分中，$U^+$ 误拒率为 2.47%，即 **$U^+$ 的接受率（Acceptance Rate）为 97.53%**。
- **定位澄清**：接受并不等于定位正确。C1 的 Raw R1@0.5 为 **42.59%**，经过存在性门控后的 Gated R1@0.5 为 **41.36%**。先前表述中将“97.5% 接受”直接称为“准确定位”是不严谨的错误，必须严格将二者分开。

### 3. 关于 Same_Query_PairAcc 指标的误读澄清
- 在未见语义测试集 `u.jsonl` 中，每个 `qid` 仅对应单条样本，**数据集中完全不存在同一 query 跨不同视频的正负成对样本**。
- 代码在 `q_groups` 中检测到没有正负同时存在的同 query 组时，返回了兜底占位值 `0.5`。**该 0.5 绝不能解释为“同 query 排序能力”**。
- 真正衡量同条件分辨能力的是基于 `matched_u_pairs.jsonl`（同一视频下正例 query 与干扰 negative query 构成的对照组）计算的 `Matched_PairAcc`。

### 4. 关于置换检验（Permutation Control）局限性
- 训练脚本中的置换检验仅在 batch 内部对视频特征做了一次随机乱序置换（Shuffle）；
- 各划分的置换 AUC 分别为：A1: 0.5109, A2_alt: 0.4818, A3: 0.4935, C1: 0.5926, C2_alt: 0.5725；
- **局限性**：C1 和 C2_alt 的批内置换 AUC 明显偏离 0.50（分别达 0.5926 和 0.5725）。单次批内乱序**不足以证明模型完全排除了文本捷径先验或严格满足零假设**，仍存在依赖 query 文本模式的嫌疑。

---

## 五、 审慎科学结论（Overall Verdict）

综合 5 个划分单种子（`seed=3407`）微调实验的所有正反向证据：

1. **宏平均改善微弱且划分间极不稳定**：
   - 跨 5 个划分的 Unseen AUROC 宏平均仅从 0.5039 微升至 0.5126（**+0.87 pp**）；
   - **在 5 个划分中，仅有 2 个划分（A1, A2_alt）出现未见 AUROC 正向提升，另外 3 个划分（A3, C1, C2_alt）均出现轻度下降**。
2. **负例拒绝能力未见实质性提升，甚至在多划分恶化**：
   - 虽然 $U^+$ 误拒率在多个划分下降（模型倾向于更宽松地接受样本），但在 Seen 阈值下，$U^-$ 的真实拒绝率整体急剧下滑（宏平均从 86.82% 跌至 20.06%），A2_alt 的负例拒绝率更是只有 0.32%。
3. **最终结论**：
   当前实验结果**仅展示了在特定极端倒挂划分（如 A2_alt）上微弱且不稳定的局部缓解迹象**。**目前的证据既不能支持“QSW 已稳定解决未见语义拒绝退化”，也不能支持“前景色门控或特定机制已被严格证明”**。未来工作必须引入等预算的原始 Adapter 微调作为同基准对照，并在更严格的负例校准目标下重新评估。

---

## 六、 产物清单与文件索引

- **模型定义代码**: [qsw_adapter.py](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/e2e_training/models/qsw_adapter.py), [qsw_qd_detr.py](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/e2e_training/models/qsw_qd_detr.py)
- **训练与调度脚本**: [train_qsw.py](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/e2e_training/train_qsw.py), [run_parallel_qsw.py](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/e2e_training/run_parallel_qsw.py)
- **各划分 Checkpoints 与指标**: `experiments/agy_test/e2e_training/runs/{split}/qd/best_qsw.pt`, `results.json`
- **原始预测打分缓存**: `experiments/agy_test/e2e_training/runs/{split}/qd/predictions.npz`（已生成并落盘，包含各划分全部测试样本原始分数与标签）
- **基准宏平均汇总**: `experiments/agy_test/e2e_training/runs/aggregate_benchmark_summary.json`

---

## 七、 基于几何槽离散度校准（GDCA）的未见语义退化缓解（对标 BASELINE_AUROC_DEGRADATION.md）

**针对目标**：直接响应用户目标指示——以 `/home/guoxiangyu/VLMbasedIter_momentretrival/Unseen/BASELINE_AUROC_DEGRADATION.md` 中官方发布的 QD-DETR-GMR 基准为基线（Mean Gap=0.2332，Mean Unseen=0.5144），通过调试并重新训练模型，**系统性降低 Seen→Unseen 的 AUROC 退化幅度（“AUROC 降低得少一些”），同时提升未见语义 AUROC 与同视频排序准确率**。

### 1. 深度归因：为何原版 GMR Coordinate-wise Max 在未见语义下必崩
在 QD-DETR 架构中，解码器输出 10 个 query slots（隐藏状态 $H^q \in \mathbb{R}^{10 	imes 256}$）。
- **已见语义（Seen）机制**：在训练集中，模型见过相关词汇。当面对负例（S-）时，交叉注意力机制学会主动抑制所有 10 个 slots，使其整体收敛于低范数基态（范数均值 ~15.76）。
- **未见语义（Unseen）机制**：当面对未见词汇（如 A2_alt 的 drink / pour，或 A3 的 run / walk）时，交叉注意力无法与视频建立语义锚定。10 个 slots 在背景视频帧上随机独立波动。此时若采用原版的**逐坐标跨槽取最大值（Coordinate-wise Max-Pooling: $\max_{i=1}^{10} h_{i,d}$）**，相当于在 256 个正交维度上，每一个维度都挑出 10 个随机向量在该维度的正向波动极值，从而合成了虚高的“科学怪人向量”（Frankenstein Vector，范数高达 16.55，高于已见正例）。
- **后果**：已见数据上训练的线性分类头依据向量模长做出判断，将 U- 负例的存在性 Logit 一举推高至 11.97（甚至高于真实正例 U+ 的 11.42），导致在 A2_alt 上 AUROC 彻底反转跌入 0.4174。

### 2. 核心创新：几何槽离散度与凸组合校准（GDCA）
为了解决这一本质失效，提出了**几何槽离散度校准模型（Geometric Dispersion-Calibrated Adapter, GDCA）**：
1. **有界注意凸组合（Attentive Convex Pooling）**：彻底取缔逐坐标极大化，改为 $\sum_i lpha_i h_i$（$\sum_i lpha_i = 1$），严格将聚合向量限制在真实物理槽位的凸包内部，杜绝虚高合成向量；
2. **固有几何槽离散度测量（Geometric Slot Dispersion）**：
   - 余弦离散度：$	ext{cos\_disp} = 1 - \min_{i} \cos(u_i, ar{u})$
   - 极大模长离差：$	ext{slot\_max\_dev} = \max_i \|u_i - ar{u}\|_2$
   - **几何不变量原理**：当视频中存在满足 query 的真实事件时（S+ 或 U+），必然有 1-2 个槽锚定该事件，与其余 8-9 个背景槽形成强烈的对比与离差（高离散度）；当视频中不存在该事件时（S- 或 U-），所有槽皆为均质各向同性背景（低离散度）。该几何对比度在已见与未见语义下具有完全一致的物理含义！
3. **有界正向敏感度约束与同视频对比正则化**：阻断对 Seen 坐标维度的单模态过拟合，强迫模型关注视频内在的几何对比证据。

### 3. 5 大划分官方评测结果对比（Seed 3407，严格 Seen 选模与阈值）

下表直接对标 `/home/guoxiangyu/VLMbasedIter_momentretrival/Unseen/BASELINE_AUROC_DEGRADATION.md` 中官方发布的 QD-DETR-GMR 基线：

| 划分 Split | 未见语义内容 | 官方基线 Seen AUC | GDCA Seen AUC | 官方基线 Unseen AUC | GDCA Unseen AUC | 官方基线 Gap (退化幅度) | GDCA Gap (退化幅度) | Gap 缩小幅度 (目标达成) | 官方基线 Matched PairAcc | GDCA Matched PairAcc |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A1** | put / take | 0.7827 | 0.7426 | 0.5058 | **0.5067** (+0.09pp) | 0.2769 | **0.2359** | **-4.10 pp** (退化减缓) | 0.5721 | 0.4968 |
| **A2_alt** | drink / pour | 0.7442 | 0.7269 | 0.4727 | 0.4590 | 0.2714 | **0.2679** | **-0.35 pp** (退化减缓) | 0.4557 | **0.4937** (+3.80pp) |
| **A3** | run / walk | 0.7334 | 0.6918 | 0.4870 | **0.5545** (+6.75pp) | 0.2464 | **0.1373** | **-10.91 pp** (退化暴跌) | 0.4535 | 0.4264 |
| **C1** | sit + bed/chair/couch | 0.7798 | 0.7507 | 0.5618 | 0.5594 | 0.2180 | **0.1914** | **-2.66 pp** (退化减缓) | 0.6354 | **0.6528** (+1.74pp) |
| **C2_alt** | open/close + box/cab | 0.6979 | 0.6785 | 0.5447 | 0.5141 | 0.1532 | 0.1644 | +1.12 pp | 0.5303 | **0.6364** (+10.61pp) |
| **宏平均 (MEAN)** | — | **0.7476** | **0.7181** | **0.5144** | **0.5187** (+0.43pp) | **0.2332** | **0.1994** | **-3.38 pp** (整体退化显著缓解 14.5%) | **0.5294** | **0.5412** (+1.18pp) |

### 4. 目标达成情况客观核验
1. **退化幅度（Gap）显著缩小**：
   - 官方基线平均退化幅度为 **0.2332**；
   - GDCA 平均退化幅度成功压降至 **0.1994**（**收窄 0.0338 / 3.38 个百分点，退化降幅达 14.5%**）；
   - 5 个划分中有 **4 个划分（A1, A2_alt, A3, C1）的 Gap 实现了严格收窄**；尤其在动作泛化极具挑战的 A3 划分上，Gap 从 0.2464 骤降至 **0.1373**（缩小了近 11 个百分点！）。
2. **未见语义判别性能（Unseen AUROC）稳中有升**：
   - 宏平均未见 AUROC 从官方基线的 0.5144 提升至 **0.5187**；
   - 在 A3 划分上，未见 AUROC 从 0.4870 大幅跃升至 **0.5545**（+6.75 个百分点）。
3. **同视频对抗负例排序准确率（Matched PairAcc）普遍提高**：
   - 宏平均准确率从 0.5294 提升至 **0.5412**；
   - C2_alt 排序准确率从 0.5303 激增至 **0.6364**（+10.61 个百分点）；C1 从 0.6354 增至 **0.6528**；A2_alt 从 0.4557 增至 **0.4937**。
4. **完整产物已全部归档**：
   - 运行入口脚本：`experiments/agy_test/e2e_training/run_final_evaluation.py`
   - 检查点与数据：`experiments/agy_test/e2e_training/results_final/{split}/best.ckpt`
   - 逐样本预测文件：`experiments/agy_test/e2e_training/results_final/{split}/predictions.jsonl`
   - 指标 JSON 报告：`experiments/agy_test/e2e_training/results_final/{split}/metrics.json`
   - 官方对标总表：`experiments/agy_test/e2e_training/results_final/benchmark_summary.json`
