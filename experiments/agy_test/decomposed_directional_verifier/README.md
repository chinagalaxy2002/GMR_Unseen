# DDV：解耦方向反事实验证器实验与独立审计

日期：2026-10-06。当前实验是五划分、seed 3407 的方法开发结果。

## 阅读顺序

1. [发布概览与实验计划](../../../docs/reports/ddv_experiment_20261006.md)。
2. [完整独立审计](../ddv_audit_20261006/DDV_AUDIT_REPORT.md)。
3. [修正后的机器可读指标](benchmark_audited.json)。
4. [原始实验报告](DDV_VERIFIER_REPORT.md)与 [原始汇总](benchmark_summary.json)仅用于历史追溯；原报告存在已知指标和表述错误。

## 目前结果支持什么

| 方法 | Seen AUROC | Unseen AUROC | Gap | Matched PairAcc |
|---|---:|---:|---:|---:|
| HQ QD 原始 logit | 0.7511 | 0.5027 | 0.2484 | 0.5181 |
| 三骨干检测器融合控制 | 0.7778 | 0.5523 | 0.2255 | 0.6014 |
| DDV | 0.7684 | 0.6134 | 0.1550 | 0.6608 |

DDV 相对融合控制的 Unseen AUROC 提高 6.11 pp，视频聚类 Bootstrap 95% CI 为 [4.22, 8.21] pp，同时 Seen 降低 0.94 pp。收益主要来自组合语义；A1 Gap 扩大，A2_alt/C1 的 Seen 阈值在未见负例上拒绝率很低。该控制仅训练检测器融合权重，尚需约 400 参数的 detector-only MLP 与逐模态消融，才能进一步归因。

DDV 点估计超过 0.60，但 95% CI [0.5926, 0.6346] 包含 0.60。路由依据 split ID；模型选择只用 Seen validation，但这些划分已被多轮方法开发查看，不能据此声称全新语义的盲评成功。

## 代码与依赖

- `model.py`：原 DDV 约 400 参数验证头；三个检测骨干与视觉编码器冻结。
- `prepare_data.py`：拼接已有 MCV 10 维缓存及 AC 动作/物体相似度，生成 12 维缓存。
- `train_and_eval.py`：原训练与评估快照；其自定义 G-mIoU 函数有已知错误。
- `reproduce.py` / `reproduce.sh`：原运行入口，同样继承上述指标问题。
- `generate_report.py`：原报告生成器，可重新生成未经审计修正的历史表述。
- [MCV 特征生产代码](../multiscale_counterfactual_verifier/prepare_features.py)：追溯新增 peak 与 SlowFast 标量的来源。
- [AC 特征生产代码](../aligned_calibration_verifier/extract_aligned_features.py)：对齐 CLIP 文本/视觉投影及训练参考。
- [独立审计代码](../ddv_audit_20261006/audit_ddv.py)：重放模型、新训练控制、正确 G-mIoU 和共享视频 Bootstrap；结论以它的落盘指标为准。

当前源码包含原机器上的绝对路径。移植时需按本机资源位置调整 AC 编码器权重路径；不要用 GitHub 中不存在的本地路径作为下载链接。

## 本地资源恢复顺序

GitHub 发布源码、报告、指标 JSON 和哈希清单。检查点、NPZ 特征、逐查询预测、视频和日志保留本地；克隆仓库并不能立即重放本次训练。需先获得来源许可下的 Charades 视频/CLIP/SlowFast 特征，以及一致的三骨干检查点和预测。

1. `data/release/semantic_existence_v2/{split}/`：训练/验证/测试标注及 `matched_u_pairs.jsonl`，已随既有 benchmark 发布。
2. `experiments/agy_test/cache/hq/{split}/{subset}.npz` 和 `cache/features/{split}/{flash,moment,qd}/train.npz`：检测器特征；不能把别的检查点输出混入。
3. `results/semantic_existence/multi_split_v2/{split}/`：Flash/Moment/QD 的 Seen 验证预测和全量测试预测。
4. `features/charades_semantic_existence/{clip,slowfast}/{vid}.npz` 与 AC `aligned_features/{split}/{subset}.npz`。
5. 用 MCV `prepare_features.py` 生成 `cache_features/{split}/{train,val,test}.npz`，再用 DDV `prepare_data.py` 生成 `cache/{split}/`。
6. 若仅重放，恢复 DDV `runs/{split}/{best_model.pt,predictions.npz}`；若复算独立审计，还需 AC/MCV 原缓存及三骨干预测。原文件哈希见 [input_manifest.json](../ddv_audit_20261006/input_manifest.json)。

`train.npz` 包含 `X, labels, qids, vids, same_vid_pairs`；Seen `val.npz` 包含 `X, labels, qids, vids`；`test.npz` 还包含 `partitions, base_scores`。每行 X 为 12 维，qid 拼接必须一致。动作/物体字段来自查询文本，GT 窗口不能用作新增验证特征。

## 运行入口

环境需 Python、PyTorch、NumPy、scikit-learn。原运行环境为 Python 3.8.20 / PyTorch 2.0.1；训练脚本原配置为两张 GPU。审计在 CPU 上运行验证头。

准备好上述本地资源后，在仓库根目录运行：

```bash
# 原模型重放；AUROC 可复现，原自定义 G-mIoU 不作正式指标
python experiments/agy_test/decomposed_directional_verifier/reproduce.py --mode eval

# 正确指标与三骨干融合控制；会在审计目录重训控制并更新其产物
python experiments/agy_test/ddv_audit_20261006/audit_ddv.py
python experiments/agy_test/ddv_audit_20261006/audit_sources.py
```

原 `--mode train` 训练验证头；`--mode all` 只是拼接现有 MCV/AC 缓存再训练，不包含原始视频编码和三骨干训练。不能将数分钟的验证头运行时间解释为完整系统端到端成本。
