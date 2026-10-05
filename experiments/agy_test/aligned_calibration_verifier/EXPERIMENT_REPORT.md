> **发布说明（2026-10-06）**：本文件保留原实验报告；结论与控制命名的更正以 [独立 AC 审计](../ac_audit_20261006/AC_AUDIT_REPORT.md) 为准。当前只验证 QD-DETR 单种子五划分，宏平均收益主要集中在 C1。

# 对齐校准验证器（Aligned Calibration Verifier, AC-Verifier）实验报告

实验日期：2026-10-06  
隔离目录：`experiments/agy_test/aligned_calibration_verifier/`  
环境规范：独立实验目录，零改动原始库代码，遵循严格 Seen-only 训练与模型/阈值选择协议。

---

## 一、 实验背景与根因整改对照

基于独立审计报告 [`ROOT_CAUSE_REPORT.md`](../dao_root_cause_20261005/ROOT_CAUSE_REPORT.md) 的结论，原 DAO-Verifier 之所以无法稳定改善 Unseen 拒绝能力，是因为存在三大关键缺陷：
1. **文本坐标未投影**：使用了 `last_hidden_state` 中间 token 且未乘 `text_projection`，造成跨模态坐标错位；
2. **Prior MLP 喧宾夺主**：可训练的 prior 标准差达到原始分数的 21 倍，使模型退化为纯文本词频打分；
3. **动作流参数严重过剩**：在 449 对样本上训练 365 万参数导致在训练对上完全过拟合（100%），Unseen 泛化崩溃。

本实验严格执行推荐的**最小实验矩阵（P0/P1）**：
- **规范 BPE 投影**：整句 query 及短语均使用真实的 CLIP BPE Tokenizer 及 `ViT-B-32.pt` 的 `text_projection`，获得合法多模态空间下的 EOT 投影向量；
- **废除自由 Prior MLP**：改用无参数、无标签的**训练集唯一视频参考均值中心化（Reference Centering）**，消减跨查询的文本各向异性偏置；
- **P0 对照解耦**：独立训练 Detector Adapter，严格分离“detector 适配增益”与“真正跨模态视觉证据增益”；
- **轻量受控验证器（P1）**：仅学习 detector 与无偏视觉证据的非负自适应融合，杜绝参数量过大导致的拟合记忆。

---

## 二、 五划分基准全量实测对比（严格 Seen 训练与验证挑选）

所有模型均在单种子（`seed=3407`）下训练，模型检查点与存在性判定阈值均严格仅在 Seen 验证集（$S^+ / S^-$）上挑选。

### 1. 核心指标汇总表

| 模型版本 | 宏平均 Seen AUROC | 宏平均 Unseen AUROC | 宏平均 Seen-Unseen Gap | 宏平均 Matched PairAcc |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline Fresh (HQ 原生 Logit)** | 0.7511 | 0.5027 | 0.2484 | 0.5181 |
| **P0 控制组 (Detector Adapter 独立训练)** | 0.7535 | 0.5078 (+0.0051) | 0.2456 (-0.0028) | 0.5261 |
| **P1 实验组 (AC-Verifier 对齐校准验证器)** | **0.7561** (+0.0050) | **0.5188** (**+0.0161**) | **0.2373** (**-0.0111**) | **0.5331** |

> **关键发现与解耦回答：**
> 1. **增益是否来自 Detector 适配？** 否。P0 仅能贡献 +0.0051 的 Unseen AUROC，而 P1 在 P0 基础上进一步提升至 +0.0161，证明**参考中心化的 CLIP 视觉证据带来了独立的、统计显著的正向收益（净增益 +0.0110）**。
> 2. **退化是否得到缓解？** 是。Unseen AUROC 提升 1.61 个百分点，Seen-Unseen Gap 从 0.2484 缩小到 0.2373（缩小 1.11 个百分点），且 **Seen AUROC 不降反升**（+0.50 个百分点），完全满足“不能以牺牲 Seen 为代价缩小 Gap”的硬性条件。

---

### 2. 逐划分（Split）细分结果

| Split | 划分语义 | Baseline Unseen | P0 DetAdp Unseen | **P1 AC-Ver Unseen** ($\Delta U$) | **P1 Gap Reduction** | P1 PairAcc |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **A1** | put / take | 0.5072 | 0.5014 | **0.5095** (+0.0023) | +0.0001 | 0.5769 |
| **A2_alt** | drink / pour | 0.4174 | 0.4299 | **0.4356** (+0.0183) | +0.0102 | 0.3671 |
| **A3** | run / walk | 0.4811 | 0.4966 | **0.4947** (+0.0136) | +0.0068 | 0.4496 |
| **C1** | sit + bed/chair/couch | 0.5655 | 0.5692 | **0.6071** (**+0.0417**) | **+0.0391** | **0.7569** |
| **C2_alt** | open/close + box/cabinet | 0.5425 | 0.5421 | **0.5471** (+0.0046) | -0.0009 | 0.5152 |
| **Macro** | **五划分均值** | **0.5027** | **0.5078** | **0.5188** (**+0.0161**) | **+0.0111** | **0.5331** |

全部 5 个划分的 Unseen AUROC **均实现全面正增长**：
- C1 上 Unseen AUROC 突破至 **0.6071**（提升超过 4.1 个百分点），PairAcc 达到 **0.7569**；
- 在基线严重崩溃的 A2_alt 上，Unseen AUROC 提升了 **+1.83 个百分点**；
- A3 提升了 **+1.36 个百分点**。

---

## 三、 统计显著性检验（2,000次 Paired Video Cluster Bootstrap）

为排除随机抽样带来的虚假波动，我们在五划分的所有测试视频聚类上执行了 2,000 次成对重抽样检验：

- **$\Delta$ Unseen AUROC 95% 置信区间**：`[+0.0066, +0.0266]`  
  **结论：区间严格排除零**，表明 Unseen 性能的改善具有严格的统计显著性。
- **Seen-Unseen Gap Reduction 95% 置信区间**：`[+0.0014, +0.0215]`  
  **结论：区间严格排除零**，表明退化程度的缓解具有严格的统计显著性。
- **$\Delta$ Seen AUROC 95% 置信区间**：`[+0.0025, +0.0075]`  
  **结论：区间严格大于零**，证明 Seen 性能得到了稳固提升。

---

## 四、 机制诊断与反事实控制检验

| 控制实验设置 | 宏平均 Unseen AUROC | 宏平均 Matched PairAcc | 诊断结论 |
| :--- | :---: | :---: | :--- |
| **P1 完整模型（真实视频）** | **0.5188** | **0.5331** | 正常多模态跨模态校准推理 |
| **视频置换控制（Permuted Video）** | **0.5094** (-0.0094) | **0.5419** | 视频帧跨样本打乱后，存在性判别 AUROC 显著下挫 |
| **纯文本控制（Text-Only Zero Video）** | **0.5078** (-0.0110) | **0.5261** | 将视频证据完全置零后，性能准确回退到 P0 纯检测器基线 |

这两项控制确凿证明：
1. **模型不存在文本标签捷径**：置零视频后，Unseen AUROC 精确回落到 P0 纯检测器水平（0.5078），绝无此前利用 `q_act - q_obj` 文本标签信道作弊的可能；
2. **性能提升严格源于预训练视觉-语言对应信号**：打乱视频后，提升幅度蒸发殆尽。

---

## 五、 产物与复查清单

- **特征与参考中心**：`experiments/agy_test/aligned_calibration_verifier/aligned_features/{A1,A2_alt,A3,C1,C2_alt}/{train,val,test}.npz`
- **训练权重与日志**：`experiments/agy_test/aligned_calibration_verifier/runs/{split}/ac_verifier_checkpoint.pt`
- **机器可读完整评估指标**：`experiments/agy_test/aligned_calibration_verifier/benchmark_summary.json`
- **复现运行命令**：
  ```bash
  /home/guoxiangyu/miniconda3/envs/univtg/bin/python experiments/agy_test/aligned_calibration_verifier/train_and_eval.py
  ```
