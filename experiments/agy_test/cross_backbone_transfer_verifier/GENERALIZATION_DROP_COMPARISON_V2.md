# 泛化掉点对比分析报告 V2 (Generalization Drop Comparison Report V2)
## —— 基于查询相关多模态证据校准的泛化退化缓解分析

> **报告版本**：V2 (2026-10-07 审计修订版)  
> **前序版本**：[`GENERALIZATION_DROP_COMPARISON.md`](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/agy_test/cross_backbone_transfer_verifier/GENERALIZATION_DROP_COMPARISON.md)  
> **核心评估规范**：
> 1. **严格推断协议**：使用仅在 Seen 训练集拟合的参考经验 CDF（保留并列，避免数据泄露与顺序依赖）；
> 2. **收紧学术主张**：放弃“幂律乘积是核心突破”和“内生因果一票否决”等过度包装，正名为**“查询相关多模态证据校准”**；
> 3. **披露 Seen 权衡代价**：如实报告 Unseen 增益伴随的 Seen AUROC 回落（$-1.3 \sim -5.2\text{ pp}$）；
> 4. **统计与阈值闭环**：包含 2,000 次配对视频聚类 Bootstrap 置信区间，以及纯 Seen 验证集锁定阈值下的 Rej-F1、误拒率和 G-mIoU。

---

## 一、 单骨干泛化掉点基准对比总表 (Single-Backbone Macro Benchmark)

本表展示在三大检测骨干上，基线、V1 方案与 V2 校准方案在 5 大划分宏平均下的严格评估（采用保留并列的训练参考 CDF）：

| 骨干模型 | 评估方案 (Variant) | Seen AUROC | Unseen AUROC | 掉点幅度 (Gap) | Unseen 净提升 | 95% 置信区间 (Bootstrap) | Seen 变化 | Gap 缩减幅度 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **QD-DETR** | Baseline (原始基线) | 0.7476 | 0.5144 | -0.2332 | - | - | - | - |
| | V1 旧单骨干方案 | 0.7528 | 0.5490 | -0.2038 | +0.0345 | - | +0.0052 | 减少 2.94 pp |
| | **V2 线性加权和 (0.5+0.5)** | **0.7347** | **0.6080** | **-0.1267** | **+9.36 pp** | `[+7.24, +11.40]` | **-1.29 pp** | **减少 10.65 pp** |
| | V2 幂律乘积 (0.65, 0.85) | 0.7262 | 0.6086 | -0.1176 | +9.42 pp | `[+6.95, +11.81]` | -2.14 pp | 减少 11.56 pp |
| **Moment-DETR** | Baseline (原始基线) | 0.7518 | 0.5287 | -0.2231 | - | - | - | - |
| | V1 旧单骨干方案 | 0.7581 | 0.5615 | -0.1966 | +0.0328 | - | +0.0063 | 减少 2.65 pp |
| | **V2 线性加权和 (0.5+0.5)** | **0.7371** | **0.6155** | **-0.1216** | **+8.68 pp** | `[+6.12, +11.14]` | **-1.47 pp** | **减少 10.15 pp** |
| | V2 幂律乘积 (0.65, 0.85) | 0.7180 | 0.6122 | -0.1058 | +8.35 pp | `[+5.60, +11.04]` | -3.38 pp | 减少 11.73 pp |
| **FlashVTG** | Baseline (原始基线) | 0.7730 | 0.5714 | -0.2016 | - | - | - | - |
| | V1 旧单骨干方案 | 0.7742 | 0.5880 | -0.1862 | +0.0166 | - | +0.0012 | 减少 1.53 pp |
| | **V2 线性加权和 (0.5+0.5)** | **0.7450** | **0.6255** | **-0.1195** | **+5.41 pp** | `[+2.92, +7.77]` | **-2.80 pp** | **减少 8.21 pp** |
| | V2 幂律乘积 (0.65, 0.85) | 0.7211 | 0.6200 | -0.1011 | +4.86 pp | `[+2.00, +7.58]` | -5.19 pp | 减少 10.05 pp |

> **边界说明与统计定论**：
> 1. **配对检验**：加权和与幂律乘积在 Unseen 上的配对差异 95% 置信区间跨越 0（QD: `[-0.96, +0.92]`），**两者在 Unseen 排序能力上统计等价**。不能称“加权和全面反超”，而是**表现相近**。
> 2. **Seen 代价对比**：加权和在 Seen AUROC 上比幂律乘积少损失 **+0.85 ~ +2.40 pp**（置信区间严格排除 0），因此加权和是更稳健的强基线。
> 3. **候选依赖**：此处多模态局部证据依托上游 HQ 候选池提取；检测器得分为单骨干独立输出，局部视觉证据聚合存在候选池共享。

---

## 二、 机制消融实验矩阵 (Ablation Matrix)

在五大划分与三大骨干上对比各融合结构与证据流的作用：

| 实验变体 | 融合机制 / 证据类型 | Moment (Seen / Unseen) | QD (Seen / Unseen) | Flash (Seen / Unseen) | 核心发现 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Baseline** | 原始检测器输出 | 0.7518 / 0.5287 | 0.7476 / 0.5144 | 0.7730 / 0.5714 | 未见概念存在性严重退化 |
| **Evidence Only** | 仅多模态证据（抛弃检测器） | 0.5892 / 0.6127 | 0.5892 / 0.6127 | 0.5892 / 0.6127 | Unseen 可行，但 Seen 暴跌 16 pp（无法单独实用） |
| **去意图路由 (Unrouted)** | 统一证据 + 加权和 | 0.6821 / **0.5312** | 0.6945 / **0.5288** | 0.6804 / **0.5412** | **Unseen 收益丧失，回落至基线附近** |
| **去方向性特征 (No-Dir)** | 移除特征 12/13 (状态转换符号) | 0.7368 / 0.6148 | 0.7335 / 0.6082 | 0.7441 / 0.6251 | **与完整配置几乎持平，方向性非主要贡献** |
| **线性加权和 (WSum)** | 查询意图路由 + 线性加权和 | **0.7371 / 0.6155** | **0.7347 / 0.6080** | **0.7450 / 0.6255** | **Seen 下降小，Unseen 扎实改善** |
| **幂律乘积 (PowerProd)** | 查询意图路由 + 幂律乘积 | 0.7180 / 0.6122 | 0.7262 / 0.6086 | 0.7211 / 0.6200 | 原设定，硬拒绝更激进 |

---

## 三、 Seen 验证集阈值锁定下的真实拒绝与定位评估

二值阈值 $\tau^*$ 严格仅在 Seen 验证集（S+/S-）搜索最大化 Balanced Accuracy 确定，冻结后应用于测试集：

| 骨干模型 | 评估分支 | 实际拒绝 F1 (Rej-F1) | 整体拒绝率 (RR) | S+ 误拒率 (S+ FRR) | U+ 误拒率 (U+ FRR) | 端到端定位 (G-mIoU@1) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Moment-DETR** | Baseline | 58.03% | 40.56% | 28.74% | 29.71% | 37.99% |
| | 幂律乘积 (PowerProd) | **59.40%** (+1.37) | 51.80% | 40.63% | 42.41% | **39.74%** (+1.75) |
| | 线性加权和 (WSum) | 57.38% (-0.65) | 40.92% | 29.40% | 28.15% | 37.74% (-0.25) |
| **QD-DETR** | Baseline | 56.27% | 35.95% | 24.45% | 18.76% | 38.06% |
| | 幂律乘积 (PowerProd) | **58.93%** (+2.66) | 47.82% | 36.65% | 35.55% | **40.23%** (+2.17) |
| | 线性加权和 (WSum) | **57.76%** (+1.49) | 42.14% | 30.64% | 27.79% | **39.20%** (+1.14) |
| **FlashVTG** | Baseline | 58.70% | 38.51% | 26.19% | 21.85% | 43.34% |
| | 幂律乘积 (PowerProd) | **59.41%** (+0.71) | 47.54% | 35.90% | 35.41% | **44.04%** (+0.70) |
| | 线性加权和 (WSum) | 57.13% (-1.57) | 39.67% | 27.55% | 28.01% | 42.81% (-0.53) |

---

## 四、 五大划分逐项明细 (Corrected Split Names)

> 依据官方 `split_specs.json` 订正划分名称：
> - **A1**：`put/take`（动作）
> - **A2_alt**：`drink/pour`（动作）
> - **A3**：`run/walk`（动作）
> - **C1**：`sit` + 家具（`chair, bed, couch`）（组合）
> - **C2_alt**：`open/close` + 容器（`box, cabinet`）（组合）

### 1. QD-DETR 骨干明细 (以加权和 WSum 为主评估)
| 划分类型 | 划分名与语义 | Baseline (Seen $\rightarrow$ Unseen) | WSum (Seen $\rightarrow$ Unseen) | WSum Unseen 净提升 | PowerProd (Seen $\rightarrow$ Unseen) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| 动作语义 | **A1** (put/take) | 0.7827 $\rightarrow$ 0.5058 | 0.7584 $\rightarrow$ **0.5401** | +3.43 pp | 0.7338 $\rightarrow$ 0.5427 |
| 动作语义 | **A2_alt** (drink/pour) | 0.7442 $\rightarrow$ 0.4727 | 0.7371 $\rightarrow$ **0.6012** | +12.85 pp | 0.7421 $\rightarrow$ 0.6435 |
| 动作语义 | **A3** (run/walk) | 0.7334 $\rightarrow$ 0.4870 | 0.7501 $\rightarrow$ **0.5752** | +8.82 pp | 0.7537 $\rightarrow$ 0.6180 |
| 组合语义 | **C1** (sit + 家具) | 0.7798 $\rightarrow$ 0.5618 | 0.7314 $\rightarrow$ **0.7258** | +16.40 pp | 0.7173 $\rightarrow$ 0.7400 |
| 组合语义 | **C2_alt** (open/close + 容器) | 0.6979 $\rightarrow$ 0.5447 | 0.6965 $\rightarrow$ **0.5977** | +5.30 pp | 0.6889 $\rightarrow$ 0.6218 |

### 2. Moment-DETR 骨干明细 (以加权和 WSum 为主评估)
| 划分类型 | 划分名与语义 | Baseline (Seen $\rightarrow$ Unseen) | WSum (Seen $\rightarrow$ Unseen) | WSum Unseen 净提升 | PowerProd (Seen $\rightarrow$ Unseen) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| 动作语义 | **A1** (put/take) | 0.8044 $\rightarrow$ 0.4973 | 0.7712 $\rightarrow$ **0.5262** | +2.89 pp | 0.7458 $\rightarrow$ 0.5284 |
| 动作语义 | **A2_alt** (drink/pour) | 0.7690 $\rightarrow$ 0.5511 | 0.7483 $\rightarrow$ **0.5784** | +2.73 pp | 0.7258 $\rightarrow$ 0.5685 |
| 动作语义 | **A3** (run/walk) | 0.7488 $\rightarrow$ 0.5643 | 0.7521 $\rightarrow$ **0.6120** | +4.77 pp | 0.7440 $\rightarrow$ 0.6226 |
| 组合语义 | **C1** (sit + 家具) | 0.7610 $\rightarrow$ 0.5621 | 0.7275 $\rightarrow$ **0.7495** | +18.74 pp | 0.7048 $\rightarrow$ 0.7539 |
| 组合语义 | **C2_alt** (open/close + 容器) | 0.6759 $\rightarrow$ 0.4687 | 0.6865 $\rightarrow$ **0.6114** | +14.27 pp | 0.6734 $\rightarrow$ 0.5947 |

---

## 五、 相关资产路径索引

* **严格统计与阈值报告**：  
  [`experiments/agy_test/detr_decoder_gmr/RIGOROUS_EVALUATION_REPORT.md`](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/detr_decoder_gmr/RIGOROUS_EVALUATION_REPORT.md)
* **独立审计诊断脚本与数据**：  
  [`experiments/agy_test/dec_gmr_scheme_a_audit_20261006/audit_scheme_a.py`](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/dec_gmr_scheme_a_audit_20261006/audit_scheme_a.py)  
  [`experiments/agy_test/dec_gmr_scheme_a_audit_20261006/IDEA_EVALUATION_V2.md`](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/dec_gmr_scheme_a_audit_20261006/IDEA_EVALUATION_V2.md)
