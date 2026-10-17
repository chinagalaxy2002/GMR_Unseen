# 四 seed 复现与第二阶段微调交接文档

更新日期：2026-10-17（Asia/Shanghai）

目标分支：`fintune`

复现实验种子：`2024, 2025, 2026, 2027`

## 1. 结论摘要

本次工作已完成以下链路：

1. 从头训练四个同 seed 的 FlashVTG-GMR E0 baseline；
2. 从各自 E0 最优 checkpoint 分别启动 Task A 对照分支；
3. 按公开 A3 路径，从各自 E0 最优 checkpoint 直接启动 min neg 第二阶段微调；
4. A3 仅依据 Val AUROC 选模，冻结后运行官方 Test；
5. 对 Test 的存在性阈值 `0.00–1.00`（步长 `0.01`）进行完整扫描；
6. 生成四 seed 均值、样本标准差、同 seed 配对增益以及完美存在性 oracle 图。

需要特别强调，最终拓扑是：

```text
E0 baseline (same seed)
├── Task A：独立对照分支
└── min neg (A3)：公开路径的第二阶段微调 → Test → 全阈值统计/绘图
```

**A3 不是从 Task A checkpoint 初始化。** 曾经启动的 `Task A → min neg` pilot 已停止并排除在最终结果之外。本文所说的“第二阶段微调”是 `E0 → min neg (A3)`。

## 2. 微调后的 mAP

### 2.1 建议报告的主口径

A3 四 seed 的官方 Test、FlashVTG 原生 pre-NMS `MR-full-mAP` 为：

| Seed | Test native pre-NMS mAP (%) |
|---:|---:|
| 2024 | 24.50 |
| 2025 | 24.05 |
| 2026 | 23.80 |
| 2027 | 23.48 |
| **均值 ± 样本标准差** | **23.96 ± 0.43** |

因此，对“第二阶段微调后 mAP 为多少”的简短回答是：**23.96±0.43%（四 seed，Test native pre-NMS mAP）**。

### 2.2 另一个不可混淆的诊断口径

`test_metrics.json` 还报告 A3 模型自身在存在性门控前的 `raw_localizer_pre_exist`：

| Seed | Raw-localizer pre-existence mAP (%) |
|---:|---:|
| 2024 | 25.54 |
| 2025 | 24.96 |
| 2026 | 24.74 |
| 2027 | 24.63 |
| **均值 ± 样本标准差** | **24.97 ± 0.41** |

这两个值回答不同问题：

- `native_pre_nms = 23.96±0.43%`：在 A3 的标准 pre-NMS submission 上运行原生 evaluator，是当前日志和控制台输出的主口径。A3 同时通过断言验证其门控前定位窗口与同 seed E0 reference 一致；该 native mAP 与 E0 相同，符合固定定位器设计。
- `raw_localizer_pre_exist = 24.97±0.41%`：把 evaluator 的窗口字段显式替换为 `pred_relevant_windows_pre_exist` 后得到的门控前候选定位诊断值。

不能用 `24.97 - 23.96` 直接声称定位 mAP 提升，因为两列来自不同预测提取路径。若论文需要宣称定位能力提升，必须先统一同一套 prediction/NMS/rounding 路径重新评测。

补充的 A3 Test 定位指标如下：

| 口径 | mAP | mAP@0.5 | mAP@0.75 |
|---|---:|---:|---:|
| Native pre-NMS | 23.96±0.43 | 44.82±0.75 | 25.22±0.32 |
| Raw localizer、门控前 | 24.97±0.41 | 45.43±1.20 | 23.51±0.58 |

## 3. 实验协议

| 项目 | 设置 |
|---|---|
| 冻结源代码 commit | `857b1fdf03a9afc5cb81731752268ea4fdd7ebf5` |
| 随机种子 | 2024、2025、2026、2027 |
| 最大 epoch | 100 |
| early-stop patience | 23 |
| GPU | GPU 0、GPU 1 |
| 单卡并发上限 | 2 个训练任务 |
| E0 选模 | Val native pre-NMS `MR-full-mAP`，严格提升 |
| Task A 选模 | Val native pre-NMS `MR-full-mAP`，严格提升 |
| A3 选模 | Val AUROC，严格提升 |
| Test 数量 | 1036：544 positive、492 negative |
| Test 阈值网格 | 0.00–1.00，步长 0.01，共 101 点 |
| 不确定性 | 四 seed 样本标准差，`ddof=1` |
| 方法比较 | 同 seed 配对差值 |
| CUDA 确定性 | `CUBLAS_WORKSPACE_CONFIG=:4096:8` |

Test 不参与 checkpoint 选择。本次全阈值扫描用于敏感性分析，不用于反向选择模型或部署阈值。Val 派生阈值在 Test 前冻结；Test 最优阈值仅能标为 oracle diagnostic。

## 4. 各阶段 checkpoint

### 4.1 E0 baseline

E0 完成了 patience=23 的正常早停：

| Seed | Val-mAP 最优 epoch | 完成训练 epoch 数 | Val mAP | Test native mAP |
|---:|---:|---:|---:|---:|
| 2024 | 32 | 55 | 25.84 | 24.50 |
| 2025 | 40 | 63 | 26.38 | 24.05 |
| 2026 | 32 | 55 | 27.73 | 23.80 |
| 2027 | 41 | 64 | 26.91 | 23.48 |

四 seed E0 Test native mAP 为 `23.96±0.43%`。

### 4.2 Task A 独立对照

Task A 从同 seed E0 初始化，但不作为 A3 的上游 checkpoint。四个 seed 都在 epoch 1 获得最佳 Val native mAP，并训练至 epoch 24 后触发 patience=23。其 Test `positive_localization.mAP` 分别为 `25.99 / 25.22 / 25.43 / 25.26%`，均值为 `25.48±0.36%`。

### 4.3 min neg (A3) 第二阶段微调

| Seed | 冻结 epoch | Val AUROC | Test AUROC（直接 evaluator） | G-mIoU@1 τ=0.4 | τ=0.5 | τ=0.6 |
|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 6 | 74.2801 | 75.2769 | 46.87 | 53.04 | 55.46 |
| 2025 | 17 | 74.0056 | 74.3775 | 47.77 | 52.01 | 53.50 |
| 2026 | 10 | 74.8403 | 75.3045 | 52.64 | 54.70 | 54.56 |
| 2027 | 8 | 74.5546 | 75.6714 | 46.13 | 53.11 | 55.43 |
| **均值 ± SD** | — | — | **75.16±0.55** | **48.35±2.94** | **53.22±1.11** | **54.74±0.92** |

README 图表从序列化预测重新计算 AUROC，得到 `75.15±0.55%`；直接 evaluator 使用未量化分数，得到 `75.16±0.55%`。约 `0.01 pp` 的差异来自预测分数序列化/精度路径，图表及公开文字统一采用 `REPORT.json` 中的 `75.15±0.55%`。

A3 checkpoint SHA256：

| Seed | SHA256 |
|---:|---|
| 2024 | `96900252b4642e977c850832a2586c72f1d4875fb8b3a7cfbb76553e2ee5c96c` |
| 2025 | `ed301836a2cb4e2ad6634615cb68b9e02623ae756b51d67d442ab03ae674a1fc` |
| 2026 | `0a16aad290773e9005e87bd1fef746ae60ec910008275b1087a8976bafb6c0ab` |
| 2027 | `014b371324a93c2afd7fcd348a2710d402f7aa2c25416925b700d1f8d7479a17` |

## 5. A3 提升与 oracle 诊断

A3 相对同 seed E0 的 G-mIoU@1 配对增益：

| 阈值 | E0 | A3 | A3−E0 配对增益 |
|---:|---:|---:|---:|
| 0.4 | 32.90±3.84 | 48.35±2.94 | +15.45±6.62 pp |
| 0.5 | 45.64±2.08 | 53.22±1.11 | +7.58±2.66 pp |
| 0.6 | 50.58±1.01 | 54.74±0.92 | +4.16±1.29 pp |

固定每个 seed 的 E0 定位窗口、仅用 Test 真值替换存在性判断后，perfect-existence oracle G-mIoU@1 为 `61.88±0.20%`。A3 在 τ=0.4、0.5、0.6 分别填补 `53% / 47% / 37%` 的平均 oracle 增益空间。

oracle 使用 Test 标签，只能用于瓶颈分析，不能作为模型结果。

## 6. 本地目录与关键产物

本地完整实验根目录：

```text
/home/guoxiangyu/GMR_Unseen/experiments/agy_test/
  soccer_flash_kim_mechanism_20261016/multiseed_reproduction/
```

关键目录：

```text
multiseed_reproduction/
├── pipeline.py
├── baseline/runs/E0_s<seed>/
├── task_a/runs/task_a_s<seed>/
├── minneg/runs/minneg_s<seed>/
├── logs/
└── reports/
```

每个 A3 run 至少应包含：

```text
best.ckpt
selected.json
validation_metrics.json
test_metrics.json
test_predictions.jsonl
test_predictions_pre_nms.jsonl
```

公开分支中的可移交结果位于：

```text
figures/data/four_seed_auroc/
├── CHECKPOINT_FREEZE.json
├── EVALUATION_PROTOCOL.json
├── REPORT.json
├── fixed_threshold_summary.csv
├── paired_gain_summary.csv
├── threshold_sweep_per_seed.csv
├── oracle_gmiou_per_seed.csv
└── oracle_gmiou_metadata.json
```

## 7. 从 baseline 到第二阶段微调的复现命令

以下命令在实验根目录的 `multiseed_reproduction` 下执行。Python 环境为：

```bash
export REPRO_ROOT=/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction
export GMR_PYTHON=/home/guoxiangyu/miniconda3/envs/gmr/bin/python
cd "$REPRO_ROOT"
```

### 7.1 自动全流程

`pipeline.py` 会维护依赖关系，并限制每张 GPU 同时最多两个任务：

```bash
CUBLAS_WORKSPACE_CONFIG=:4096:8 "$GMR_PYTHON" -B pipeline.py
```

注意：现有目录的 `PIPELINE_STATE.json` 保留了人工冻结 A3 前的历史运行态，其中 A3 仍可能显示为 `running`，不能作为最终完成状态依据。最终状态应以 `reports/EVALUATION_PROTOCOL.json`、四个 `test_metrics.json` 和 `reports/REPORT.json` 为准。全新复现应在新的实验副本/输出目录中启动，不要直接删除当前归档结果。

### 7.2 单 seed 手工复现模板

以 seed 2024 为例。

第一阶段，训练 E0：

```bash
cd "$REPRO_ROOT/baseline"
CUBLAS_WORKSPACE_CONFIG=:4096:8 "$GMR_PYTHON" -B code/run.py \
  --variant E0 --device cuda --seed 2024 \
  --epochs 100 --patience 23 --run-name E0_s2024
```

Task A 独立对照：

```bash
cd "$REPRO_ROOT/task_a"
CUBLAS_WORKSPACE_CONFIG=:4096:8 "$GMR_PYTHON" -B code/train.py \
  --job E2M_scheme_A_twostage_s2024 --device cuda \
  --seed 2024 --epochs 100 --patience 23 \
  --run-name task_a_s2024 \
  --init-checkpoint "$REPRO_ROOT/baseline/runs/E0_s2024/best.ckpt"
```

第二阶段，按公开路径直接从 E0 微调 A3：

```bash
cd "$REPRO_ROOT/minneg"
CUBLAS_WORKSPACE_CONFIG=:4096:8 "$GMR_PYTHON" -B code/train.py \
  --job A3_similarity_hardneg_s2024 --device cuda \
  --seed 2024 --epochs 100 --patience 23 \
  --run-name minneg_s2024 \
  --init-checkpoint "$REPRO_ROOT/baseline/runs/E0_s2024/best.ckpt" \
  --reference-predictions "$REPRO_ROOT/baseline/runs/E0_s2024/validation_predictions_pre_nms.jsonl"
```

冻结 A3 checkpoint 后运行 Test：

```bash
cd "$REPRO_ROOT/minneg"
"$GMR_PYTHON" -B code/eval_test.py \
  --run minneg_s2024 --device cuda \
  --reference-predictions "$REPRO_ROOT/baseline/runs/E0_s2024/test_predictions_pre_nms.jsonl"
```

四个 seed 全部完成后生成逐阈值报告：

```bash
cd "$REPRO_ROOT"
"$GMR_PYTHON" -B threshold_report.py
"$GMR_PYTHON" -B multiseed_figures.py
```

## 8. 公开 README 图的重绘

在 `fintune` 分支仓库根目录执行：

```bash
python figures/generate_multiseed_readme_figures.py
python figures/fig4_existence_oracle_gmiou_multiseed.py
```

如需从本地原始 Test predictions 重新计算 oracle CSV：

```bash
python figures/fig4_existence_oracle_gmiou_multiseed.py \
  --source-root "$REPRO_ROOT"
```

图 1–4 均提供 PNG、PDF、SVG。README 使用单独的 `assets/*.png`，避免 GitHub 图片缓存影响。

## 9. 科学性边界与已知限制

1. **A3 没有自然触发 patience=23。** 用户要求在当时冻结四个 Val-AUROC-best checkpoint 并立即测试；对应 epoch 为 6、17、10、8。因此不能把本轮 A3 描述为“完整早停收敛”。
2. **Task A 与 A3 是独立分支。** A3 从同 seed E0 初始化，不从 Task A 初始化。
3. **模型选择只用 Val。** Test 只在 checkpoint 冻结后运行。
4. **全阈值图是敏感性分析。** 不得根据 Test 曲线反向挑选并宣称最佳部署阈值。
5. **mAP 与 G-mIoU 的样本域不同。** mAP 评价正样本定位；G-mIoU 同时评价正样本定位和负样本拒识。
6. **mAP 存在多个输出路径。** A3 的 `native_pre_nms`、`raw_localizer_pre_exist` 以及 Task A 的 `positive_localization.mAP` 不是同名同路径的可直接拼接结果。论文主表必须统一 prediction/NMS/rounding 路径后再比较。
7. **AUROC 有约 0.01 pp 的精度路径差异。** 公开图表以序列化预测重算的 `REPORT.json` 为准。
8. **oracle 不是模型成绩。** 它读取 Test 真值，仅用于估计存在性头上限。
9. **四 seed 只支持描述性不确定性。** 当前报告使用均值±样本标准差，没有据此宣称统计显著性。
10. **不要混用旧 README 的单 checkpoint baseline。** 旧单次结果中的 E0 Test mAP 为 26.14%，而本次从头训练的四 seed E0 为 23.96±0.43%；两者不是同一 checkpoint。本次 A3 增益只应与同 seed、同次复现的 E0 配对比较，不能拼接旧 E0 数值。

## 10. 交接验收清单

- [x] 四个 E0 baseline 均完成训练和 Test predictions 导出。
- [x] 四个 Task A 对照均完成。
- [x] 四个 A3 checkpoint 已按 Val AUROC 冻结并记录 SHA256。
- [x] 四个 A3 官方 Test 已完成。
- [x] 101 个阈值 × 3 个阶段 × 4 个 seed 的表完整，共 1212 行。
- [x] oracle 表完整，共 404 行。
- [x] 四张 README 图完成视觉检查。
- [x] PNG、PDF、SVG、CSV 和源码已推送到 `fintune`。
- [x] 公开图表提交：`bea28971ec5ee8e6f55039336721d0e06732a822`。

## 11. 推荐引用入口

- 结果总览：[`README.md`](README.md#五四-seedval-auroc-选模协议下的全部插图重绘)
- 选模协议：[`figures/data/four_seed_auroc/EVALUATION_PROTOCOL.json`](figures/data/four_seed_auroc/EVALUATION_PROTOCOL.json)
- 检查点记录：[`figures/data/four_seed_auroc/CHECKPOINT_FREEZE.json`](figures/data/four_seed_auroc/CHECKPOINT_FREEZE.json)
- 完整逐阈值数据：[`figures/data/four_seed_auroc/threshold_sweep_per_seed.csv`](figures/data/four_seed_auroc/threshold_sweep_per_seed.csv)
- oracle 数据：[`figures/data/four_seed_auroc/oracle_gmiou_per_seed.csv`](figures/data/four_seed_auroc/oracle_gmiou_per_seed.csv)
