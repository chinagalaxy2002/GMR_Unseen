# 独立候选验证器：消融与跨骨干迁移实验

本目录发布最新冻结实验的训练源码、模型权重、12 维特征缓存和逐查询预测。模型为 `TargetCandidateVerifier`：在存在性分数基础上融合候选/全局 CLIP 语义证据、SlowFast 时序特征及 CLIP 端点差分，通过可学习路由和有界残差门控校验查询是否在视频中发生。

## 当前结果与结论

五划分 A1、A2_alt、A3、C1、C2_alt 等权平均；迁移训练 seeds 为 3407、42、2024。相对各自骨干基线，机制 A 自验证的 Unseen AUROC 分别提高 1.69、2.39、2.67 pp，Seen−Unseen Gap 分别缩小 1.17、1.73、1.86 pp（相对 5.81%、7.76%、7.98%），Seen AUROC 同时提高。三组 Gap 缩小的配对视频聚类 bootstrap 95% 区间均排除零。

结论范围：支持当前五划分的平均 AUROC 退化缓解。A3 仍存在局部失败；方向通道独立作用和机制 A 优于 B 的区间跨零。目标 CDF 使用目标 Seen 训练数据，阈值使用目标 Seen 验证标签，故属于允许目标校准的权重迁移。Moment-DETR 的 Unseen G-mIoU 在 Seen 标定阈值下略降；不能将排序改善写成所有实际拒绝/定位指标全面提高。

**以[完整独立审计](../candidate_suite_final_audit_20261006/FINAL_INDEPENDENT_AUDIT.md)和[论文指标表格](../paper_tables_20261006/PAPER_TABLES.md)为准。** `reports/INDEPENDENT_CANDIDATE_TRANSFER_REPORT.md` 保留原作者报告，其中部分机制和显著性结论已被独立审计收窄。其他历史实验不与本目录主结果混用。

## 发布内容

| 目录 | 内容 | 数量 |
|---|---|---:|
| `models/` | 验证器模型 | 1 个实现 |
| `scripts/` | 候选特征提取、400 epochs 训练、消融、3-seed 迁移与报告生成 | 4 个脚本 |
| `cache/{split}/{backbone}/{train,val,test}.npz` | 当前训练/验证/测试所需紧凑特征 | 45 |
| `runs/{target_specific,shared}/seed_{seed}/{split}/verifier_src_{backbone}.pt` | 迁移训练模型 | 90 |
| `runs/ablation/{backbone}/{split}/{mode}/verifier.pt` | 消融模型 | 35 |
| `runs/**/predictions.npz`, `transfer_predictions.npz` | 逐查询预测 | 72 |
| `reports/` | 消融和迁移 JSON、原实验报告 | 已发布 |
| `publication/ARTIFACT_MANIFEST.json` | 本次上传原始文件 SHA-256 与大小 | 已发布 |

权重是轻量验证器的 state_dict，不包含 FlashVTG/Moment-DETR/QD-DETR 的大型骨干权重。已有数据生成管线与发布划分位于仓库 `pipeline/` 和 `data/release/semantic_existence_v2/`。另外发布了 15 份目标自身测试候选 JSONL，位于 `results/semantic_existence/multi_split_v2/`，用于定位/G-mIoU 复算。

机制 A：用目标自身候选证据与目标 train-CDF；机制 B：验证/测试改用 Flash 特征。B 的训练仍用来源自身候选，不等同于完全共享候选训练。固定未训练初始化原输出曾被 full 覆盖，独立审计按 seed 3407 重建；不能将它计作另一个已保存的独立检查点。

## 环境与下载

已使用 Python 3.8.20、PyTorch 2.0.1+cu118、NumPy 1.24.4、scikit-learn 1.3.2。CPU 冻结重放不需要 GPU；原训练使用两张 GPU。

```bash
git clone --branch experiments/independent-candidate-verifier-20261006 --single-branch   https://github.com/chinagalaxy2002/GMR_Unseen.git
cd GMR_Unseen
```

依赖版本见 `publication/requirements-replay.txt`；可在已有 PyTorch 环境安装 NumPy/scikit-learn 等科学计算依赖。

## 不重新训练的复算入口

```bash
# 完整独立审计：125 权重、270 条迁移路径、消融、拒绝指标和 2000 次 bootstrap
python experiments/agy_test/candidate_suite_final_audit_20261006/audit_final.py
python experiments/agy_test/candidate_suite_final_audit_20261006/write_report.py

# 原论文 Table 2 风格指标：All/Seen/Unseen，Seen 标定及固定 tau=0.4
python experiments/agy_test/paper_tables_20261006/build_tables.py
```

这些命令会更新对应审计/表格目录的输出，不会重新训练模型。原 `verify_suite.py` 也保留作历史脚本，但其覆盖和断言不足，完整核验应使用上面的 `audit_final.py`。当前仓库足以重放最新实验及重算表格。

## 从已发布特征重新训练

建议先保留原 `runs/` 和 `reports/` 的备份，训练脚本会写入相同结果路径。

```bash
python experiments/agy_test/independent_candidate_transfer_suite/scripts/02_ablation_and_a3_diagnosis.py
python experiments/agy_test/independent_candidate_transfer_suite/scripts/03_run_multi_seed_transfer.py
python experiments/agy_test/independent_candidate_transfer_suite/scripts/05_generate_suite_report.py
```

训练只使用 S+/S−；检查点/阈值只使用 Seen val。400 epochs、双课程成对损失与选模代码原样保存。当前保存的 state_dict 不带完整选模轨迹、最佳 epoch 和训练日志；冻结推理可重放，不能凭最终权重认证全部研发过程的严格盲评。

## 从原始预训练特征重提取

```bash
python experiments/agy_test/independent_candidate_transfer_suite/scripts/01_extract_target_candidate_features.py
```

此步骤还需要外部原始特征：`features/charades_semantic_existence/{clip,slowfast}/`、`experiments/agy_test/aligned_calibration_verifier/aligned_features/`、`experiments/agy_test/cache/features/`，以及 train/val/test 的检测器输出。大型预训练特征与骨干权重没有打包；已发布的 45 份紧凑特征足以重新训练当前验证器。

## 指标口径

AUROC 的正类为事件存在，Rej-F1 的正类为无对应时刻的查询。G-mIoU 使用存在性决策筛选后的候选集；mAP/mR 只在正查询上使用未筛选窗口。当前数据没有多时刻正查询，mR+@5 标记为不适用。论文表格的数据为 Charades-STA 语义划分，不是 Soccer-GMR 原 Table 2 的复现。
