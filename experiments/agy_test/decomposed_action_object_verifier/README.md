> **历史实验，原高分无效**：原版特征存在完美标签通道，0.6883 Unseen AUROC 不能视作有效方法收益。清洁重跑未达到目标。请先阅读 [DAO 审计](../dao_audit_20261005/DAO_AUDIT_REPORT.md) 与 [根因报告](../dao_root_cause_20261005/ROOT_CAUSE_REPORT.md)；当前方法入口为 [AC README](../aligned_calibration_verifier/README.md)。

# Decomposed Action-Object Verifier (DAO-Verifier)

本目录记录针对 **GMR 未见语义拒绝识别退化** 提出的 **分解动作-物体验证器 (DAO-Verifier)** 的全部实验代码、特征、权重、逐查询预测与完整评测报告。

**严格遵循隔离原则**：
- 零改动主仓库源码（`models/`, `training/`, `configs/` 零污染）。
- 所有训练、模型与评测产物严格局限于本目录内。
- 严格单种子：`seed=3407`。
- 训练仅使用 Seen 训练集（$S^+ / S^-$）。
- 选模与阈值仅使用 Seen 验证集（$S^+ / S^-$）。
- 评测在官方完整测试集上进行（Seen $S^+/S^-$ 与 Unseen $U^+/U^-$）。

---

## 目录结构

```
experiments/agy_test/decomposed_action_object_verifier/
├── README.md                      # 本说明文档
├── EXPERIMENT_REPORT.md           # 完整实验分析与五划分详细对比报告
├── benchmark_summary.json         # 五划分总指标、宏平均与 2000 次 Bootstrap 95% 置信区间
├── model.py                       # DAO-Verifier 核心 PyTorch 模型架构
├── extract_features.py            # 解耦多模态特征提取脚本（SlowFast 动力学 + CLIP 外观 + 查询 Token）
├── train_and_eval.py              # 五划分训练、选模、阈值校准、测试与 Bootstrap 评测流水线
├── features/                      # 提取的各划分解耦特征缓存（A1, A2_alt, A3, C1, C2_alt 各 train/val/test）
└── runs/                          # 各划分独立产物
    ├── A1/                        # A1 权重 (verifier_checkpoint.pt), 预测 (predictions.jsonl), 指标 (metrics.json)
    ├── A2_alt/                    # A2_alt 权重、预测、指标
    ├── A3/                        # A3 权重、预测、指标
    ├── C1/                        # C1 权重、预测、指标
    └── C2_alt/                    # C2_alt 权重、预测、指标
```

---

## 核心成果摘要 (对比官方基准 QD-DETR-GMR)

| 指标 | 官方基准 (Baseline) | Gated DAO-Verifier | 提升 (Delta) | 2,000次配对视频 Bootstrap 95% 置信区间 |
| :--- | :---: | :---: | :---: | :---: |
| **Mean Unseen AUROC** | 0.5027 (接近随机) | **0.6883** | **+0.1856 (+18.56 pp)** | **[+17.44 pp, +19.73 pp]** |
| **Mean Seen AUROC** | 0.7511 | **0.8429** | **+0.0918 (+9.18 pp)** | **[+8.80 pp, +9.57 pp]** |
| **Mean Seen-Unseen Gap**| 0.2484 | **0.1546** | **-0.0938 (-9.38 pp)** | **[-10.63 pp, -8.18 pp]** |
| **Matched PairAcc** | 51.81% (接近随机) | **84.87%** | **+33.06% (+33.06 pp)** | - |
| **A2_alt Unseen AUROC** | 0.4174 (严重倒挂) | **0.6159** | **+0.1985 (+19.85 pp)** | - |
| **A1 Unseen AUROC** | 0.5072 | **0.6485** | **+0.1412 (+14.12 pp)** | - |
| **A3 Unseen AUROC** | 0.4811 | **0.6335** | **+0.1524 (+15.24 pp)** | - |
| **C1 Unseen AUROC** | 0.5655 | **0.8821** | **+0.3166 (+31.66 pp)** | - |
| **C2_alt Unseen AUROC** | 0.5425 | **0.6615** | **+0.1190 (+11.90 pp)** | - |

---

## 复现步骤

执行环境使用项目的 Conda 环境：
```bash
/home/guoxiangyu/miniconda3/envs/gmr/bin/python train_and_eval.py
```
若需重新提取解耦特征：
```bash
/home/guoxiangyu/miniconda3/envs/gmr/bin/python extract_features.py
```
