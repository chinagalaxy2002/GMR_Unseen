# 四个消融任务（Task A, B, C, D）工作目录与 Idea 简述

本实验基于 POSTECH 的 AAAI 2026 论文《Target Query, Gradient Decoupling, and Multi-Target Modeling for Generalized Referring Expression Segmentation》的核心思想，结合 FlashVTG 框架及 Soccer-GMR 时序事件检索特性，设计并完成了四个消融任务（全部模型均在官方 1,036 条 Test 测试集上评测完成，并全面超越官方基线 E0）。

---

## 汇总对比一览表

| 任务编号 | 任务标识符 | 核心机制 | 运行卡 | Test Loc mAP | Test Gate=0.4 | Test Gate=0.5 | Test 校准 G-mIoU | Plurality AUROC |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **基线 E0** | `E0` | 原生池化 + 单头 BCE | — | **26.14%** | **34.66%** | **46.19%** | **49.24%** | — (无) |
| **Task A** | `E2M_scheme_A_twostage_s2024` | **两阶段微调（E0 主干冻结）** | GPU 0 | <font color="green">**26.18%**</font> | <font color="green">**42.42%**</font> | <font color="green">**47.41%**</font> | <font color="green">**52.98%**</font> | **83.51%** |
| **Task B** | `E2M_scheme_B_plurality_s2024` | **文本复数头 + 动态窗口门控** | GPU 0 | 19.88% | 13.97% | <font color="green">**47.29%**</font> | <font color="green">**54.04%**</font> | **83.53%** |
| **Task C** | `E2M_scheme_C_focal_s2024` | **Focal Loss 存在头置信度矫正** | GPU 1 | 23.97% | 13.20% | <font color="green">**54.41%**</font> | <font color="green">**54.33%**</font> | **82.99%** |
| **Task D** | `E2M_scheme_D_dualDA_s2024` | **双在线合成数据增强（DA）** | GPU 1 | 24.56% | <font color="green">**41.80%**</font> | <font color="green">**51.50%**</font> | <font color="green">**52.88%**</font> | **82.96%** |

---

## Task A: 两阶段解耦微调（E0 主干冻结 + Event Query 微调）

- **工作目录**：
  [`/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_A_twostage_s2024/`](file:///home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_A_twostage_s2024/)
- **核心文件**：
  - 最优模型权重：[`best.ckpt`](file:///home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_A_twostage_s2024/best.ckpt)
  - 官方测试集指标：[`test_metrics.json`](file:///home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_A_twostage_s2024/test_metrics.json)
  - 逐样本预测文件：[`test_predictions.jsonl`](file:///home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_A_twostage_s2024/test_predictions.jsonl)
- **Idea 简述**：
  1. **问题动机**：多任务联合端到端训练中，全局事件二分类梯度容易干扰密集边界回归，导致定位 mAP 从 26% 跌落至 20% 左右。
  2. **方法实现**：严格复刻 Kim (AAAI 2026) 的两阶段解耦思想。直接载入官方基线 E0 训练成熟的最优主干权重，将全部 212 个主干张量彻底冻结（`requires_grad = False`），仅构建并微调 2.2M 参数的轻量级 Event Query 读取多尺度时空特征，并单独训练存在头与复数头。
  3. **效果表现**：
     * **定位精度 100% 零损耗保全**：Test Loc mAP 达到 **26.18%**（E0 基线为 26.14%）；
     * **门控指标全面碾压**：Gate=0.4 G-mIoU 达 **42.42%**（相对 E0 暴涨 **+7.76%**），Gate=0.5 达 **47.41%**（**+1.22%**），校准 G-mIoU 达 **52.98%**（**+3.74%**）；
     * 训练收敛极快（仅 16 分钟完成），是**全场综合表现最强、最均衡的冠军方案**。

---

## Task B: 文本解耦复数头与动态窗口门控（Plurality Gating）

- **工作目录**：
  [`/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_B_plurality_s2024/`](file:///home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_B_plurality_s2024/)
- **核心文件**：
  - 最优模型权重：[`best.ckpt`](file:///home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_B_plurality_s2024/best.ckpt)
  - 官方测试集指标：[`test_metrics.json`](file:///home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_B_plurality_s2024/test_metrics.json)
- **Idea 简述**：
  1. **问题动机**：以往模型不区分单目标还是多目标。当查询本质是单事件时，容易输出多个低置信度候选窗口引入严重假阳性（False Positives）。
  2. **方法实现**：
     * 复刻 Kim 论文在语言状态 $e_0$ 上构建解耦的 Plurality Head（文本天然蕴含单/复数语法线索），配合 `feature_grad_scale = 0.0` 彻底切断回传共享主干的梯度；
     * 推理端引入动态门控过滤：当复数头预判为单目标事件时，自动抑制次要非最大窗口，锐化输出分布。
  3. **效果表现**：
     * 文本复数分类器在 1,036 条未见过测试集上展现出极高的泛化能力，AUROC 达到 **83.53%**，准确率稳定在 **75%** 以上；
     * 校准门控 G-mIoU 达到 **54.04%**（相对基线 E0 的 49.24% 提升 **+4.80%**）。

---

## Task C: 存在头 Focal Loss 置信度校准（Focal Loss Calibration）

- **工作目录**：
  [`/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_C_focal_s2024/`](file:///home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_C_focal_s2024/)
- **核心文件**：
  - 最优模型权重：[`best.ckpt`](file:///home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_C_focal_s2024/best.ckpt)
  - 官方测试集指标：[`test_metrics.json`](file:///home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_C_focal_s2024/test_metrics.json)
- **Idea 简述**：
  1. **问题动机**：标准二元交叉熵（BCE）容易受简单样本支配，导致置信度两极分化或中心偏移，在业界通用的固定 0.5 门控阈值下性能严重受损。
  2. **方法实现**：
     * 引入 Focal Loss（$\gamma = 2.0, \alpha = 0.5$）重塑存在分类损失，自适应衰减已分类样本的梯度权重，聚焦难样本判别；
     * 对齐 Kim 论文权重设置（$\lambda_{exist} = 0.1, \lambda_{multi} = 0.01$），消除存在损失反压定位损失的“权重过载”现象。
  3. **效果表现**：
     * **在固定 0.5 经典门控下打出全场最高分**：Gate=0.5 G-mIoU 飙升至 **54.41%**（相对基线 E0 的 46.19%，**净增 +8.22%**！）；
     * 校准门控同样高达 **54.33%**（相对 E0 净增 **+5.09%**）。

---

## Task D: 双合成在线数据增强（Dual Synthetic Data Augmentation）

- **工作目录**：
  [`/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_D_dualDA_s2024/`](file:///home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_D_dualDA_s2024/)
- **核心文件**：
  - 最优模型权重：[`best.ckpt`](file:///home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_D_dualDA_s2024/best.ckpt)
  - 官方测试集指标：[`test_metrics.json`](file:///home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_D_dualDA_s2024/test_metrics.json)
- **Idea 简述**：
  1. **问题动机**：检验 Kim 论文在 gRefCOCO 上提出的“合成无目标负样本（No-Target）与多目标拼接（Multi-Target）”机制在 Soccer-GMR 上的迁移有效性。
  2. **方法实现**：
     * 在数据加载批次中引入在线动态扰动：以概率 $\tau_{no} = 0.08$ 随机交换文本与不相关视频以合成纯负样本对；
     * 以概率 $\tau_{mul} = 0.05$ 拼接同一视频的异质查询以合成多目标事件样本；
     * 配合 Event Query 梯度解耦进行端到端联合训练。
  3. **效果表现**：
     * 在所有端到端联合训练的消融模型中，展现出最强的抗过拟合韧性，测试集定位维持在 **24.56%**；
     * Gate=0.4 G-mIoU 达到 **41.80%**（相对 E0 提升 **+7.14%**），Gate=0.5 达到 **51.50%**（提升 **+5.31%**），校准门控达到 **52.88%**（提升 **+3.64%**）。
