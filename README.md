# 复现 Unseen 拒绝识别退化的缓解

本分支复现 Charades-STA 五个语义划分上的 **baseline → 独立候选验证器**。提供 baseline 从头训练、已发布权重推理、验证器训练，以及 AUROC、Rej-F1、G-mIoU 和定位指标的论文表格复算。

## 1. 复现目标

以下为五划分等权宏平均。验证器使用目标骨干自身候选窗口；验证器指标先按种子 3407、42、2024 分别计算，再平均。AUROC 单位为 %，Gap 为百分点。

| 骨干 | Baseline Seen | Baseline Unseen | +Verifier Seen | +Verifier Unseen | Gap：Baseline → Verifier | 缩小量 | 相对缩小 |
|---|---:|---:|---:|---:|---:|---:|---:|
| FlashVTG | 77.25 | 57.15 | 77.77 | 58.84 | 20.10 → 18.94 | 1.17 pp | 5.81% |
| Moment-DETR | 75.18 | 52.87 | 75.84 | 55.26 | 22.31 → 20.58 | 1.73 pp | 7.76% |
| QD-DETR | 74.76 | 51.44 | 75.57 | 54.11 | 23.32 → 21.46 | 1.86 pp | 7.98% |

Unseen 查询的操作指标如下。阈值仅在 Seen validation 上通过 Youden J 标定。

| 模型 | AUROC | Rej-F1 | G-mIoU@1 | G-mIoU@3 |
|---|---:|---:|---:|---:|
| FlashVTG | 57.15 | 26.89 | 24.07 | 16.93 |
| +Verifier | 58.84 | 31.49 | 27.87 | 21.38 |
| Moment-DETR | 52.87 | 35.26 | 30.26 | 25.14 |
| +Verifier | 55.26 | 35.53 | 30.01 | 24.78 |
| QD-DETR | 51.44 | 21.55 | 19.52 | 13.18 |
| +Verifier | 54.11 | 34.02 | 27.25 | 21.43 |

结果支持宏平均 AUROC 退化缓解。Moment-DETR 的 G-mIoU 略降，A3 也存在局部退化，因此不能声称所有划分、所有指标均改善。

## 2. 获取代码、数据和特征

```bash
git clone --single-branch --branch experiments/independent-candidate-verifier-20261006 \
  https://github.com/chinagalaxy2002/GMR_Unseen.git
cd GMR_Unseen
```

数据包：[Google Drive](https://drive.google.com/drive/folders/17wf_qE7wdGpplPxaHuYA-JGdnb_1CHHs)。共 16 个归档，约 17.89 GB，含：

- 五划分 train/val/test、Seen validation 视图及同视频反事实评测对；
- 6,142 个原始 480p 视频及各自的 CLIP、SlowFast 特征；
- baseline 使用的 CLIP token 文本特征，支持三个骨干从头训练；
- 三骨干 × 五划分的 15 个最佳 baseline 检查点和配置；
- 验证器的训练/验证/测试特征及原始定位候选。

配置自己的 rclone `gdrive:` 后，从仓库根目录运行：

```bash
mkdir -p ../gmr_assets
rclone copy gdrive:GMR_Unseen_Dataset_Features_20261006 ../gmr_assets \
  --drive-root-folder-id 1ERbWP2hl4DYl6n3j3JrvzcbGuDfW80Rm \
  --transfers 2 --checkers 2 --checksum --progress
(cd ../gmr_assets && sha256sum -c SHA256SUMS)
python ../gmr_assets/restore_bundle.py --repo-root "$PWD" --verify-files
python reproduction/check_assets.py --raw-videos
```

恢复脚本校验归档及文件哈希，恢复仓库相对目录和文本特征别名。遇到已有文件内容不同会停止，建议使用干净 checkout。详情见 [数据说明](docs/datasets/GMR_DRIVE_ASSETS_20261006.md)。仓库中的验证器权重和预测无需另外下载。

## 3. 环境

验证器和表格复算的原审计环境为 Python 3.8.20、PyTorch 2.0.1+cu118。可以建立独立环境：

```bash
conda create -n gmr-repro python=3.8 -y
conda activate gmr-repro
pip install torch==2.0.1 --index-url https://download.pytorch.org/whl/cu118
pip install -r experiments/agy_test/independent_candidate_transfer_suite/publication/requirements-replay.txt
pip install pandas==1.5.3 PyYAML easydict tqdm
```

FlashVTG 使用独立环境，避免其 torchtext 依赖与上述环境冲突：

```bash
conda create -n gmr-flash python=3.10 -y
conda run -n gmr-flash pip install -r requirements-flash-vtg.txt
```

训练和 baseline 推理需要 CUDA GPU。验证器检查点重放和论文表格复算可在 CPU 上执行。

## 4. 复算当前论文表格

```bash
# 重放已发布检查点，核对逐查询预测
python experiments/agy_test/independent_candidate_transfer_suite/verify_suite.py

# 复算表格，输出到新目录
python reproduction/recompute_tables.py
```

输出位于 `reproduction_outputs/paper_tables/`：`PAPER_TABLES.md`、`paper_tables.tex`、`paper_metrics.json`、逐 split/seed CSV 和输入哈希。包含 All / Seen / Unseen 的 AUROC、Rej-F1、mAP、mR@1、mR@5、G-mIoU@1/@3，以及固定阈值 0.4 的补充表。

这是在本项目 Charades-STA 语义划分上的 **GMR Table-2-style 指标评估**。原论文 Soccer-GMR 数据表不属于本次复现。当前正查询均为单时刻，mR+@5 不适用，记为 `—`。

## 5. Baseline 权重推理复现

激活 `gmr-repro`，指定 Flash 环境解释器：

```bash
FLASH_PYTHON="$(conda run -n gmr-flash python -c 'import sys; print(sys.executable)' | tail -n 1)"
python reproduction/run_baselines.py --stage infer --published-checkpoints \
  --gpu 0 --flash-python "$FLASH_PYTHON"
python reproduction/evaluate_baselines.py
```

该命令读取 Drive 的 15 个检查点，依次对 Seen validation 和完整 test 推理。新预测和日志写入 `reproduction_outputs/baseline_predictions/`；评估入口生成 `reproduction_outputs/baseline_metrics/BASELINE_TABLE.md` 和逐划分 JSON。检查点相对路径见 [索引](reproduction/baseline_checkpoint_index.json)。

Flash AUROC 必须使用 `pred_exist_logit` 经 float32 sigmoid 转换后的连续分数。其 JSONL 中三位小数的 `pred_exist_score` 会引入 ties，不能用于复现本表的 57.15。Moment-DETR / QD-DETR 使用发布的 `pred_exist_score`。

## 6. Baseline 从头训练复现

数据包已包含训练所需的冻结视频特征和 token 文本特征，无需重新提取编码器特征。训练检测器参数：种子 3407、100 epochs、仅 Seen train、仅 Seen validation 选最佳检查点，关闭提前停止。

```bash
# 先查看完整原训练配方
python reproduction/run_baselines.py --stage train --dry-run

# 五划分、三个骨干从头训练，随后推理
python reproduction/run_baselines.py --stage train-and-infer \
  --gpu 0 --flash-python "$FLASH_PYTHON"
python reproduction/evaluate_baselines.py
```

默认串行执行，可通过 `--splits A1 --models moment` 运行单项。训练写入 `reproduction_outputs/baselines/`；日志旁保存实际命令 JSON。重训时需提供新的 `--output`，脚本拒绝覆盖已有训练目录。这个步骤会重新训练三个定位模型，耗时明显长于验证器训练。

## 7. 验证器重新训练

```bash
python reproduction/train_verifiers.py --gpu 0
```

该命令在提供的冻结 baseline 特征上，按原顺序执行五划分 × 三种子 × 三来源验证器训练：400 epochs、训练集 CDF 分位数变换、同视频/跨视频成对损失，仅 Seen validation AUROC 选模。输出为 `reproduction_outputs/verifiers/` 下的新检查点、逐查询预测及汇总。可用 `--splits A1 --seeds 3407` 运行单项。

**当前论文表格以发布的 baseline 和验证器产物为输入。** 第 6 节重新训练的 baseline 预测与第 7 节冻结特征上的验证器是两组产物；如要用新 baseline 进行新的端到端实验，须先重新导出对应 train/val/test 候选和验证器特征，不能直接混用当前缓存来宣称新 baseline 的增益。新训练存在环境与随机性波动，不承诺逐位等同于冻结重放结果。

## 8. 指标协议

- `Gap = Seen AUROC − Unseen AUROC`；缩小量为 baseline Gap 减 verifier Gap，相对缩小量除以 baseline Gap。
- Rej-F1 的正类为无对应时刻的负查询；Unseen 正查询应接受并定位。
- 主表阈值来自 Seen validation 的 100 点 `[0.01, 0.99]` Youden J 网格，接受条件为 `score >= τ`；CDF 只拟合训练特征。
- mAP/mR 在正查询的原始定位窗口上计算；验证器只改变拒绝分数，定位指标保持相同。G-mIoU 同时衡量空集拒绝和定位。
- 五划分等权；三个种子平均各自指标，不平均分数冒充同一模型。

完整冻结结果与 LaTeX：[论文表格](experiments/agy_test/paper_tables_20261006/PAPER_TABLES.md)。
