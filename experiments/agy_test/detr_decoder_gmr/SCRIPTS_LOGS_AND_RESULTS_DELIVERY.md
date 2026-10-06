# DEC-GMR 实验脚本、运行日志与全量审计结果交付文档 (Scripts, Logs & Audited Results Delivery)

> **交付时间**：2026-10-07  
> **根目录**：`/home/guoxiangyu/paper/Openword/generalized-moment-retrieval`  
> **工作区目录**：`/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/detr_decoder_gmr/`  
> **Python 环境**：`/home/guoxiangyu/miniconda3/envs/univtg/bin/python`  
> **数据审计源**：[`experiments/agy_test/delivery_audit_20261007/audit.json`](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/delivery_audit_20261007/audit.json)

---

## 一、 交付脚本与对应运行日志索引清单 (Scripts & Logs Index)

| 序号 | 脚本功能 | 独立执行脚本路径 | 对应原始日志路径 |
| :---: | :--- | :--- | :--- |
| **Script 1** | **2,000 次联合视频聚类 Bootstrap 统计检验** (保留跨划分视频相关性) | [`run_joint_bootstrap_cluster.py`](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/detr_decoder_gmr/run_joint_bootstrap_cluster.py) | [`logs/joint_bootstrap_cluster_2000.log`](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/detr_decoder_gmr/logs/joint_bootstrap_cluster_2000.log) |
| **Script 2** | **纯 Seen 验证集阈值锁定真实拒绝评测** (按 All / Seen / Unseen 严谨切分) | [`run_thresholded_gmr_eval.py`](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/detr_decoder_gmr/run_thresholded_gmr_eval.py) | [`logs/thresholded_gmr_eval.log`](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/detr_decoder_gmr/logs/thresholded_gmr_eval.log) |
| **Script 3** | **P1 融合机制与证据流消融全量对比** | [`run_mechanism_ablations.py`](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/detr_decoder_gmr/run_mechanism_ablations.py) | [`logs/mechanism_ablations.log`](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/detr_decoder_gmr/logs/mechanism_ablations.log) |
| **Script 4** | **独立数据对齐与指标口径核验审计脚本** | [`check_delivery.py`](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/delivery_audit_20261007/check_delivery.py) | [`audit.json`](file:///home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/delivery_audit_20261007/audit.json) |

---

## 二、 指标定义与统计口径严谨澄清

1. **拒绝指标澄清**：
   * **`Rej-F1`**：以“无对应时刻查询（负样本）”作为正类计算的二值 F1 分数；
   * **`U− 正确拒绝率 (Negative Recall)`**：$\text{TN} / (\text{TN} + \text{FP})$，在非存在查询中被正确拒绝的比例；
   * **`U+ 误拒率 (Positive FRR)`**：$\text{FN} / (\text{TP} + \text{FN})$，在存在时刻的真实正例中被错误拒绝为不存在的比例；
   * **`总体拒绝比例 (Overall Rejected Fraction)`**：$(\text{TN} + \text{FN}) / \text{Total}$，原脚本中简记为 `rr`，代表模型做出拒绝决策的宏观比例（包含错误拒绝正例）。
2. **阈值搜索机制说明**：
   * 阈值 $\tau^*$ 仅在 Seen 验证集（S+/S-）的分数第 5~95 百分位的 91 个候选网格上搜索最大化 Balanced Accuracy 产生，非无限边界全局极值；决策规则为 $\text{score} \ge \tau^*$ 接受，否则拒绝。
3. **消融实验归因边界**：
   * “去路由”版本统一使用静态权重（`0.4 peak + 0.3 global + 0.3 velocity`），该配置除无路由外同时删除了物体对齐并变更了权重；
   * “去方向”并非将特征直接置零，而是将方向项的 0.15 权重重新分配给峰值帧显著性（`peak`）。

---

## 三、 全量评测数据交付 (Audited Results Tables)

### 交付表 1：Unseen 测试集真实拒绝与排序收益表 (Unseen Group Results)
> 阈值 $\tau^*$ 严格由 Seen 验证集确定，五划分宏平均：

| 骨干模型 | 方案分支 | Unseen AUROC | Unseen Rej-F1 | U− 正确拒绝率 | U+ 误拒率 (FRR) | Unseen 总体拒绝比例 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Moment-DETR** | Baseline (原始检测器) | 0.5287 | 35.10% | 31.96% | 29.71% | 31.27% |
| | **线性加权和 (0.5+0.5)** | **0.6155** | **46.76%** (+11.66) | **38.73%** (+6.77) | **28.15%** (-1.56) | 35.30% |
| | 幂律乘积 (0.65, 0.85) | 0.6122 | **62.25%** (+27.15) | **56.09%** (+24.13) | 42.41% (+12.70) | 51.56% |
| **QD-DETR** | Baseline (原始检测器) | 0.5144 | 28.51% | 21.47% | 18.76% | 20.62% |
| | **线性加权和 (0.5+0.5)** | **0.6080** | **44.78%** (+16.27) | **36.93%** (+15.46) | 27.79% (+9.03) | 34.19% |
| | 幂律乘积 (0.65, 0.85) | 0.6086 | **58.25%** (+29.74) | **49.47%** (+28.00) | 35.55% (+16.79) | 45.03% |
| **FlashVTG** | Baseline (原始检测器) | 0.5714 | 33.42% | 27.04% | 21.85% | 25.69% |
| | **线性加权和 (0.5+0.5)** | **0.6255** | **48.15%** (+14.73) | **40.90%** (+13.86) | 28.01% (+6.16) | 36.71% |
| | 幂律乘积 (0.65, 0.85) | 0.6200 | **57.95%** (+24.53) | **49.13%** (+22.09) | 35.41% (+13.56) | 44.67% |

* **科学权衡定论**：
  * **加权和 (WSum)**：Unseen Rej-F1 取得 **+11.7 ~ +16.3 pp** 的稳步增益，U+ 误拒率保持在 **28%** 较低水平（在 Moment 上甚至降低 1.56 pp），是兼顾正例保留的平衡策略；
  * **幂律乘积 (PowerProd)**：Unseen Rej-F1 激进提升 **+24.5 ~ +29.7 pp**，负例正确拒绝率突破 50%~56%，但代价是正例误拒率上升至 **35%~42%**。

---

### 交付表 2：2,000 次联合视频聚类 Bootstrap 统计显著性 (保留跨划分 1,164 视频相关性)
> 联合采样 1,217 个测试视频总体，同时评估五划分宏平均：

| 骨干模型 | 统计维度 | 幂律乘积 (PowerProd) | 线性加权和 (WSum) | 配对差值 (WSum − Power) | 95% 置信区间 (Bootstrap) | 统计推断结论 |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Moment-DETR** | **Unseen AUROC 增益** | +8.36 pp | +8.69 pp | +0.33 pp | `[-0.42, +1.12]` | **AUROC 排序统计等价 (含 0)** |
| | **Seen AUROC 变化** | -3.38 pp | -1.47 pp | **+1.91 pp** | `[+1.32, +2.51]` | **加权和极显著减少 Seen 损失** |
| | **Unseen Rej-F1 增益** | **+27.20 pp** `[+24.66, +29.81]` | **+11.68 pp** `[+8.89, +14.48]` | -15.52 pp | `[-18.23, -12.78]` | **两者真实拒绝收益均极显著 (>0)** |
| **QD-DETR** | **Unseen AUROC 增益** | +9.47 pp | +9.40 pp | -0.07 pp | `[-0.96, +0.85]` | **AUROC 排序统计等价 (含 0)** |
| | **Seen AUROC 变化** | -2.14 pp | -1.30 pp | **+0.84 pp** | `[+0.33, +1.35]` | **加权和极显著减少 Seen 损失** |
| | **Unseen Rej-F1 增益** | **+29.78 pp** `[+26.72, +32.69]` | **+16.27 pp** `[+13.54, +19.13]` | -13.51 pp | `[-16.14, -10.95]` | **两者真实拒绝收益均极显著 (>0)** |
| **FlashVTG** | **Unseen AUROC 增益** | +4.88 pp | +5.44 pp | +0.56 pp | `[-0.19, +1.37]` | **AUROC 排序统计等价 (含 0)** |
| | **Seen AUROC 变化** | -5.20 pp | -2.81 pp | **+2.39 pp** | `[+1.80, +2.99]` | **加权和极显著减少 Seen 损失** |
| | **Unseen Rej-F1 增益** | **+24.56 pp** `[+21.50, +27.55]` | **+14.77 pp** `[+12.17, +17.29]` | -9.79 pp | `[-12.11, -7.42]` | **两者真实拒绝收益均极显著 (>0)** |

---

### 交付表 3：全量测试集 (All) 与 Seen 集合宏平均结果表

| 骨干模型 | 方案分支 | All Rej-F1 | All 总体拒绝率 | All 正例误拒率 | G-mIoU@1 | Seen AUROC | Seen Rej-F1 | S+ 误拒率 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Moment-DETR** | Baseline | 58.03% | 40.56% | 28.38% | 37.99% | 0.7518 | 62.02% | 28.74% |
| | 加权和 (WSum) | 57.38% | 40.92% | 29.24% | 37.74% | 0.7371 | 59.72% | 29.40% |
| | 幂律乘积 (Power) | 59.40% | 51.80% | 40.74% | 39.74% | 0.7180 | 59.41% | 40.63% |
| **QD-DETR** | Baseline | 56.27% | 35.95% | 23.86% | 38.06% | 0.7476 | 61.42% | 24.45% |
| | 加权和 (WSum) | 57.76% | 42.14% | 30.45% | 39.20% | 0.7347 | 60.07% | 30.64% |
| | 幂律乘积 (Power) | 58.93% | 47.82% | 36.58% | 40.23% | 0.7262 | 59.08% | 36.65% |
| **FlashVTG** | Baseline | 58.70% | 38.51% | 25.63% | 43.34% | 0.7730 | 62.91% | 26.19% |
| | 加权和 (WSum) | 57.13% | 39.67% | 27.56% | 42.81% | 0.7450 | 59.19% | 27.55% |
| | 幂律乘积 (Power) | 59.41% | 47.54% | 35.90% | 44.04% | 0.7211 | 59.89% | 35.90% |

---

### 交付表 4：五大划分逐项 AUROC 精确审计值 (彻底剔除旧排名混用)
> 严格提取自 `audit.json` 中的 `split_auroc`，统一使用冻结训练参考 CDF：

#### 1. QD-DETR
| 划分名与官方语义 | Baseline (Seen / Unseen) | 线性加权和 WSum (Seen / Unseen) | 幂律乘积 Power (Seen / Unseen) |
| :--- | :---: | :---: | :---: |
| **A1** (`put/take`) | 0.7827 / 0.5058 | 0.7627 / **0.5301** | 0.7451 / 0.5422 |
| **A2_alt** (`drink/pour`) | 0.7442 / 0.4727 | 0.7366 / **0.5262** | 0.7433 / 0.5406 |
| **A3** (`run/walk`) | 0.7334 / 0.4870 | 0.7363 / **0.5805** | 0.7273 / 0.5884 |
| **C1** (`sit` + 家具) | 0.7798 / 0.5618 | 0.7426 / **0.7440** | 0.7162 / 0.7414 |
| **C2_alt** (`open/close` + 容器) | 0.6979 / 0.5447 | 0.6951 / **0.6594** | 0.6992 / 0.6306 |

#### 2. Moment-DETR
| 划分名与官方语义 | Baseline (Seen / Unseen) | 线性加权和 WSum (Seen / Unseen) | 幂律乘积 Power (Seen / Unseen) |
| :--- | :---: | :---: | :---: |
| **A1** (`put/take`) | 0.8044 / 0.4973 | 0.7828 / **0.5210** | 0.7526 / 0.5304 |
| **A2_alt** (`drink/pour`) | 0.7690 / 0.5511 | 0.7543 / **0.5817** | 0.7280 / 0.5683 |
| **A3** (`run/walk`) | 0.7488 / 0.5643 | 0.7368 / **0.6225** | 0.7280 / 0.6187 |
| **C1** (`sit` + 家具) | 0.7610 / 0.5621 | 0.7337 / **0.7452** | 0.7063 / 0.7531 |
| **C2_alt** (`open/close` + 容器) | 0.6759 / 0.4687 | 0.6782 / **0.6071** | 0.6752 / 0.5903 |

#### 3. FlashVTG
| 划分名与官方语义 | Baseline (Seen / Unseen) | 线性加权和 WSum (Seen / Unseen) | 幂律乘积 Power (Seen / Unseen) |
| :--- | :---: | :---: | :---: |
| **A1** (`put/take`) | 0.8253 / 0.4703 | 0.7878 / **0.5142** | 0.7538 / 0.5288 |
| **A2_alt** (`drink/pour`) | 0.7756 / 0.5558 | 0.7520 / **0.5871** | 0.7288 / 0.5735 |
| **A3** (`run/walk`) | 0.7550 / 0.6280 | 0.7400 / **0.6437** | 0.7212 / 0.6324 |
| **C1** (`sit` + 家具) | 0.7716 / 0.6679 | 0.7343 / **0.7751** | 0.7090 / 0.7520 |
| **C2_alt** (`open/close` + 容器) | 0.7375 / 0.5352 | 0.7110 / **0.6076** | 0.6926 / 0.6135 |

---

## 四、 一键复现指令 (Reproduction Commands)

在仓库根目录下可一键运行并核验全部结果：

```bash
# 1. 运行 2,000 次联合视频聚类 Bootstrap 统计检验（输出对应 logs/joint_bootstrap_cluster_2000.log）
/home/guoxiangyu/miniconda3/envs/univtg/bin/python experiments/agy_test/detr_decoder_gmr/run_joint_bootstrap_cluster.py

# 2. 运行纯 Seen 验证集阈值硬切分评测（输出对应 logs/thresholded_gmr_eval.log）
/home/guoxiangyu/miniconda3/envs/univtg/bin/python experiments/agy_test/detr_decoder_gmr/run_thresholded_gmr_eval.py

# 3. 运行 P1 机制与证据流消融矩阵（输出对应 logs/mechanism_ablations.log）
/home/guoxiangyu/miniconda3/envs/univtg/bin/python experiments/agy_test/detr_decoder_gmr/run_mechanism_ablations.py

# 4. 执行独立对齐与分组核验审计脚本
/home/guoxiangyu/miniconda3/envs/univtg/bin/python experiments/agy_test/delivery_audit_20261007/check_delivery.py
```
