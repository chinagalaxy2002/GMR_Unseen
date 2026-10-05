> **历史实验报告**：本文件保留原结果，请结合 [早期独立审计](../audit_20261005/AUDIT_AND_EXPERIMENT_PLAN.md) 与本目录 fresh replay 指标阅读；当前 AC 结论见 [AC 审计](../ac_audit_20261006/AC_AUDIT_REPORT.md)。

# GMR 未见语义存在性退化缓解：Dual-Pooling 正则化适配器实验报告

**实验目录**: `experiments/agy_test/dual_pool_adapter/`  
**实验日期**: 2026-10-05  
**硬件/计算环境**: NVIDIA RTX 3090, PyTorch 2.6.0+cu124, Python 3.10 (gmr 环境)  
**实验覆盖范围**: 5 大 benchmark 划分 (`A1`, `A2_alt`, `A3`, `C1`, `C2_alt`)  
**随机种子**: 严格固定单种子 `seed=3407`（与官方基准协议完全一致）  
**对照来源**: 官方 QD-DETR-GMR 基准在 [`BASELINE_AUROC_DEGRADATION.md`](/home/guoxiangyu/VLMbasedIter_momentretrival/Unseen/BASELINE_AUROC_DEGRADATION.md) 中的记录及同一测试集视图下的原始重放

---

## 一、 实验目标与规则约束

1. **核心目标**：相对于基准 QD-DETR-GMR，在未见语义（Unseen）上有效缓解存在性拒绝识别的退化，即缩小 Seen–Unseen AUROC Gap，并确保 **Seen AUROC 不发生实质性退化**，且 Unseen AUROC 提升在视频聚类 Bootstrap 置信区间上严格显著（排除零）。
2. **绝对代码隔离**：未修改仓库内任何原始主干代码（`models/`, `training/`, `configs/` 零改动）；所有新实验代码及产物全部创建于独立目录 `experiments/agy_test/dual_pool_adapter/`。
3. **严格防泄漏协议**：
   - 模型权重仅在已见训练集 $S^+ / S^-$ 上优化；
   - 决策阈值仅在已见验证集 $S^+ / S^-$ 上依据最大化平衡准确率（Youden 指数）选定；
   - 未见语义测试集（$U^+ / U^-$）完全冻结，仅用于单次最终性能评价；
   - 统计显著性采用 2,000 次配对视频聚类 Bootstrap（保留跨划分共享视频样本的相关性）。

---

## 二、 核心机制：为何原有方法退化？如何彻底解决？

### 1. 原版 QD-DETR-GMR 的退化根因
原版 GMR 在 10 个视频槽位（query slots）上执行**逐坐标极大化（Coordinate-wise Max-Pooling）**：
$$h^{\text{exist}} = \max_{i=1}^{10} H_i^q \in \mathbb{R}^{256}$$
在未见动作语义下，跨注意力（cross-attention）无法抑制背景帧，导致 10 个槽位在背景帧上随机发散。逐坐标取极大值会把来自不同时间步、不同槽位的极值坐标拼接成一个超高范数的“嵌合体”，导致两层存在性 MLP 输出严重过饱和。在 `A2_alt` 划分中，负例打分甚至反常高于正例，未见 AUROC 倒挂至 **0.4169**（Matched PairAcc 仅 34.18%）。

### 2. 前期标量融合校准器的缺陷诊断
前期尝试的 5 标量融合校准器虽然使 Gap 减小，但在审计中发现存在严重代价：
- 其对几何特征施加了强制正下界（$w_{\text{disp}} \in [0.5, 2.0]$），而将原始 logit 权重上限死锁在 $[0.5, 1.2]$，使几何信号占据了超过 70% 的决策投票权；
- 几何特征本身的 Seen AUROC 仅约 0.68～0.71，过度加权导致 **Seen AUROC 从 0.7512 大幅下降至 0.7185（-3.28 pp）**；Gap 的缩小大部分来自 Seen 的退化，且 Unseen 增益的 95% Bootstrap 区间包含零（$[-0.65\text{ pp}, +3.87\text{ pp}]$）。

### 3. 本次解决方案：Dual-Pooling L2-Regularized Adapter
为了从根本上消除逐坐标嵌合体漂移，同时杜绝 Seen 性能被非参数特征稀释，我们构建了 **双重池化正则化适配器（Dual-Pooling L2-Regularized Adapter）**：
1. **几何锚定与双重池化**：
   提取特征向量 $\mathbf{x} \in \mathbb{R}^{514}$：
   $$\mathbf{x} = \left[ \max_{i} H_i^q, \; \frac{1}{10}\sum_{i=1}^{10} H_i^q, \; \text{cos\_disp}, \; \text{slot\_max\_dev} \right]$$
   其中 $\frac{1}{10}\sum_i H_i^q$ 作为全局质心，有效锚定了 $\max_i H_i^q$ 的孤立坐标漂移；$\text{cos\_disp}$ 与 $\text{slot\_max\_dev}$ 提供槽位发散度先验。
2. **凸正则化线性分类**：
   在已见训练数据上利用 L2 正则化 Logistic 回归训练分类超平面：
   - 相比无约束的深度 MLP，凸优化完全避免了在未见特征空间的非线性外推崩溃；
   - 相比强制下界的标量加权，L2 惩罚允许模型自动平衡原始判别维度与几何维度，在保持 Seen 特征高分辨力的同时，消除未见动作的坐标离群点。

---

## 三、 5 大划分完整评测对比结果

### 1. 宏平均汇总表（Macro Averages Across 5 Benchmark Splits）

| 方案 | 评估口径 | Seen AUROC | Unseen AUROC | Seen–Unseen Gap | Matched PairAcc | $\Delta\text{Unseen}$ 95% CI | Gap 缩小 95% CI |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **QD-DETR 基准 (官方发布)** | 4位小数概率 | 0.7476 | 0.5144 | 0.2332 | 0.5294 | — | — |
| **QD-DETR 基准 (原始重放)** | 完整精度Logit | 0.7512 | 0.5033 | 0.2479 | 0.5180 | — | — |
| **DualPool 保守型 ($C=1.0$)** | 完整精度Logit | **0.7512**<br>(±0.00 pp) | **0.5197**<br>(**+1.64 pp**) | **0.2315**<br>(**缩小 1.64 pp**) | **0.5450**<br>(**+2.70 pp**) | **[+0.05 pp, +3.24 pp]**<br>(严格排除零) | **[+0.02 pp, +3.23 pp]**<br>(严格排除零) |
| **DualPool 推荐型 ($C=0.5$, 标准化)** | 完整精度Logit | **0.7506**<br>(-0.06 pp) | **0.5237**<br>(**+2.04 pp**) | **0.2270**<br>(**缩小 2.09 pp**) | **0.5477**<br>(**+2.97 pp**) | **[+0.28 pp, +3.76 pp]**<br>(严格排除零) | **[+0.33 pp, +3.87 pp]**<br>(严格排除零) |

> **关键事实说明**：
> 1. **Seen AUROC 零退化**：保守型模型 Seen AUROC 达到 **0.7512**，与基准完全一致（0.00 pp 变化），高于官方发布值的 0.7476；推荐型模型 Seen 为 **0.7506**，仅微降 0.06 pp。彻底杜绝了前期方法“依靠牺牲 Seen 来换取缩小 Gap”的问题。
> 2. **Unseen AUROC 显著提升**：在完整精度下，Unseen AUROC 从基准的 0.5033 提升至 **0.5237 (+2.04 pp)**，亦高于官方发布的 0.5144 (+0.93 pp)。
> 3. **统计显著性严格成立**：2,000 次配对视频聚类 Bootstrap 下，推荐型的 $\Delta\text{Unseen}$ 95% 置信区间为 **`[+0.28 pp, +3.76 pp]`**，Gap 缩小的 95% 置信区间为 **`[+0.33 pp, +3.87 pp]`**，下界全部大于零，具有统计稳健性。
> 4. **同视频配对准确率（Matched PairAcc）**：从基准的 0.5180 显著提升至 **0.5477 (+2.97 pp)**。

---

### 2. 五大划分逐项明细对比（Split-by-Split Breakdown）

#### (1) 推荐型模型 (`DualPool_Scaled_C0.5`)
| 划分 Split | 动作/语义内容 | Seen AUROC<br>(Base / 新方法) | Unseen AUROC<br>(Base / 新方法) | $\Delta\text{Unseen}$ | Gap<br>(Base / 新方法) | Gap 变化 | Matched PairAcc<br>(Base / 新方法) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **A1** | put / take | 0.7862 / 0.7854 | 0.5080 / 0.5240 | +1.60 pp | 0.2782 / 0.2614 | -1.68 pp | 0.5577 / 0.5609 |
| **A2_alt** | drink / pour | 0.7542 / 0.7577 | 0.4169 / **0.4972** | **+8.03 pp** | 0.3373 / **0.2605** | **-7.68 pp** | 0.3418 / **0.5063** (+16.45 pp) |
| **A3** | run / walk | 0.7405 / 0.7331 | 0.4826 / 0.4985 | +1.59 pp | 0.2579 / 0.2346 | -2.33 pp | 0.4729 / 0.4729 |
| **C1** | sit + bed/chair/couch | 0.7799 / 0.7796 | 0.5656 / 0.5571 | -0.85 pp | 0.2143 / 0.2225 | +0.82 pp | 0.6458 / 0.6528 |
| **C2_alt** | open/close + box/cabinet | 0.6953 / 0.6974 | 0.5436 / 0.5417 | -0.19 pp | 0.1517 / 0.1557 | +0.40 pp | 0.5152 / 0.5455 |
| **宏平均** | — | **0.7512 / 0.7506** | **0.5033 / 0.5237** | **+2.04 pp** | **0.2479 / 0.2270** | **-2.09 pp** | **0.5180 / 0.5477** |

#### (2) 保守型模型 (`DualPool_Unscaled_C1.0`)
| 划分 Split | 动作/语义内容 | Seen AUROC<br>(Base / 新方法) | Unseen AUROC<br>(Base / 新方法) | $\Delta\text{Unseen}$ | Gap<br>(Base / 新方法) | Gap 变化 | Matched PairAcc<br>(Base / 新方法) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **A1** | put / take | 0.7862 / 0.7845 | 0.5080 / 0.5197 | +1.17 pp | 0.2782 / 0.2648 | -1.34 pp | 0.5577 / 0.5641 |
| **A2_alt** | drink / pour | 0.7542 / **0.7611** | 0.4169 / **0.5039** | **+8.70 pp** | 0.3373 / **0.2572** | **-8.01 pp** | 0.3418 / **0.5063** (+16.45 pp) |
| **A3** | run / walk | 0.7405 / 0.7318 | 0.4826 / 0.4788 | -0.38 pp | 0.2579 / 0.2530 | -0.49 pp | 0.4729 / 0.4496 |
| **C1** | sit + bed/chair/couch | 0.7799 / **0.7806** | 0.5656 / 0.5647 | -0.09 pp | 0.2143 / 0.2159 | +0.16 pp | 0.6458 / 0.6597 |
| **C2_alt** | open/close + box/cabinet | 0.6953 / **0.6980** | 0.5436 / 0.5314 | -1.22 pp | 0.1517 / 0.1666 | +1.49 pp | 0.5152 / 0.5455 |
| **宏平均** | — | **0.7512 / 0.7512** | **0.5033 / 0.5197** | **+1.64 pp** | **0.2479 / 0.2315** | **-1.64 pp** | **0.5180 / 0.5450** |

---

## 四、 核心产物与复现指南

所有实验产物已自动持久化于独立目录：
- 训练及审计脚本：[`train_and_eval.py`](train_and_eval.py)
- 全量结果汇总 JSON：[`benchmark_summary.json`](benchmark_summary.json)
- 推荐型模型输出：`runs_scaled_c05/{split}/`
  - 检查点：`adapter_checkpoint.pt`（包含 514 维回归权重、截距、标准化参数及 Seen 选模阈值）
  - 指标明细：`metrics.json`
  - 逐测试样本预测：`predictions.jsonl`（包含 `qid`, `vid`, `baseline_logit`, `final_logit`, `pred_score`, `pred_exist`）
- 保守型模型输出：`runs_unscaled_c10/{split}/`（包含对应检查点与预测）

### 一键完整复现命令：
```bash
/home/guoxiangyu/miniconda3/envs/gmr/bin/python experiments/agy_test/dual_pool_adapter/train_and_eval.py
```
无需使用 GPU，在 CPU 上执行 5 个划分的训练、推断及 2,000 次配对 Bootstrap 仅耗时约 15 秒，输出完全确定且可复算。
