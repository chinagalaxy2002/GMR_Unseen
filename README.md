# GMR Unseen：查询相关多模态证据校准

本分支：`experiments/evidence-calibration-20261007`。研究目标是让 GMR 视频检索模型对下游训练未见的语义，既返回真实发生事件的正确时间片段，也拒绝合理但不存在的事件。

## 1. 当前 idea 与研究状态

**事件是否发生与语义是否熟悉是两个不同的问题。**定位能力与存在性头在未见语义下可能出现分离。我们用查询相关的视觉与时序证据校准已有骨干的存在性输出，检验能否缓解这种退化。语义熟悉度是否导致分离仍是机制假设。

当前方法是外部证据校准，不改动 Decoder。查询关键词规则选择峰值帧匹配、物体匹配、全局场景、SlowFast 动态或端点方向证据；以 Seen 训练集参考 CDF 映射检测分数与证据，保留并列。对照两种融合：

- 加权和：`s = 0.5 * CDF_train(det) + 0.5 * CDF_train(evidence)`。
- 幂律：`s = CDF_train(det)**0.65 * CDF_train(evidence)**0.85`。

仅用 Seen 验证集在 91 个百分位候选阈值上挑选 Balanced Accuracy 最优值，测试固定使用 `score >= tau` 接受。未见指下游任务训练未见，不指 CLIP/SlowFast 预训练未见。

**阶段目标已获得支持：现有缓存上 Unseen AUROC 和 Rej-F1 改善。完整科学目标尚未达成：仍需证明真实未见事件的接受且正确定位、负例拒绝共同泛化，并解释存在判断与定位分离的机制。**

## 2. 当前结果：冻结训练参考 CDF

Charades-STA 派生 A1、A2_alt、A3、C1、C2_alt 五划分等权宏平均。AUROC 为 0–1；增益、Gap 缩小与 Seen 变化为百分点 pp。Gap = Seen − Unseen。以下为原测试集点估计，不是 Bootstrap 均值。

| 骨干 | Baseline Seen | Baseline Unseen | 加权和 Seen | 加权和 Unseen | ΔUnseen pp | Gap 缩小 pp | ΔSeen pp |
|---|---:|---:|---:|---:|---:|---:|---:|
| Moment-DETR | 0.7518 | 0.5287 | 0.7371 | 0.6155 | +8.68 | 10.15 | -1.47 |
| QD-DETR | 0.7476 | 0.5144 | 0.7347 | 0.6080 | +9.36 | 10.65 | -1.29 |
| FlashVTG | 0.7730 | 0.5714 | 0.7450 | 0.6255 | +5.41 | 8.21 | -2.80 |

### 固定 Seen 验证阈值：Unseen 查询

以下 Rej-F1 的正类为负查询；U−正确拒绝率 = 正确拒绝的 U− / 全部 U−；U+误拒率 = 被拒绝的 U+ / 全部 U+。全部数值为 %。

| 骨干 | 分支 | Unseen Rej-F1 ↑ | U−正确拒绝率 ↑ | U+误拒率 ↓ |
|---|---|---:|---:|---:|
| Moment-DETR | Baseline | 35.10 | 31.96 | 29.71 |
| Moment-DETR | 加权和 | 46.76 | 38.73 | 28.15 |
| Moment-DETR | 幂律乘积 | 62.25 | 56.09 | 42.41 |
| QD-DETR | Baseline | 28.51 | 21.47 | 18.76 |
| QD-DETR | 加权和 | 44.78 | 36.93 | 27.79 |
| QD-DETR | 幂律乘积 | 58.25 | 49.47 | 35.55 |
| FlashVTG | Baseline | 33.42 | 27.04 | 21.85 |
| FlashVTG | 加权和 | 48.15 | 40.90 | 28.01 |
| FlashVTG | 幂律乘积 | 57.95 | 49.13 | 35.41 |

加权和在 Moment-DETR 上同时提高负例拒绝并降低正例误拒；QD 与 Flash 仍增加正例误拒。幂律获得更高拒绝 F1，同时更激进地拒绝真实事件。不能称为所有骨干无代价提升。

### 联合视频 Bootstrap

[原始联合采样日志](experiments/agy_test/detr_decoder_gmr/logs/joint_bootstrap_cluster_2000.log)记录 2,000 次全局视频联合采样，跨五划分使用相同视频重复次数。固定模型、训练 CDF 与 Seen 阈值；区间仅反映测试视频抽样，不覆盖训练种子、超参数选择及负例标注不确定性。

| 骨干 | 加权和 ΔUnseen AUROC 95% CI，pp | 加权和 ΔUnseen Rej-F1 95% CI，pp |
|---|---|---|
| Moment-DETR | [6.33, 11.22] | [8.89, 14.48] |
| QD-DETR | [7.27, 11.54] | [13.54, 19.13] |
| FlashVTG | [3.11, 7.80] | [12.17, 17.29] |

加权和与幂律的 Unseen AUROC 差值区间包含零，含义是未检测到显著差异，不能证明等价。日志中的差值均值是 Bootstrap 均值，与主表点估计略有不同。

### G-mIoU 的范围

历史阈值日志中的 G-mIoU@1 是 **All 查询**，不是 Unseen；Baseline / 加权和 / 幂律分别为 Moment 37.99 / 37.74 / 39.74，QD 38.06 / 39.20 / 40.23，Flash 43.34 / 42.81 / 44.04（%）。它不能替代 U+ 接受且正确定位的直接评估。

## 3. 证据边界与下一步

- 多模态局部证据共享上游 HQ 候选窗口；检测分数各用单骨干输出。尚未证明各骨干仅用自身候选也获得这些收益。
- 缓存检测分数存在概率量化/饱和；需要原始 logit 的公平对照。
- 原幂律结构没有证明优于简单加权和；路由消融混杂权重及特征选择；“去方向”实际将方向权重转给峰值帧，不能解释成严格置零。
- 现有测试语义已多次参与方法分析；需要冻结规则和参数后，用新动作/组合做独立评估。
- 负例来自人工审查的构建流程，其缺席标注边界见数据说明。

优先实验：①相同 Seen 正例保护预算下比较 U−拒绝；②统计全部 U+ 中“接受且定位 IoU≥δ”的比例及定位正确却被拒绝比例；③各骨干自身候选与原始 logit；④新语义冻结评估；⑤语义熟悉度的受控机制实验。

## 4. 文件组织

| 路径 | 用途 |
|---|---|
| [docs/current_idea/RESEARCH_QUESTION.md](docs/current_idea/RESEARCH_QUESTION.md) | 当前研究问题与结论边界 |
| [experiments/agy_test/detr_decoder_gmr/](experiments/agy_test/detr_decoder_gmr/) | 方法 A/B、P1、联合 Bootstrap、阈值脚本和原始日志 |
| [独立 idea 评估](experiments/agy_test/dec_gmr_scheme_a_audit_20261006/IDEA_EVALUATION_V2.md) | 研究贡献、机制和最小实验矩阵 |
| [方案 A 审计](experiments/agy_test/dec_gmr_scheme_a_audit_20261006/SCHEME_A_INDEPENDENT_AUDIT.md) | 原排名、并列和训练 CDF 诊断 |
| [交付审计](experiments/agy_test/delivery_audit_20261007/DELIVERY_AUDIT.md) | 定义核验、逐划分错误与分组复算 |
| [audit.json](experiments/agy_test/delivery_audit_20261007/audit.json) | 点估计、阈值、混淆计数与逐划分数据 |
| [SOURCE_ASSET_MANIFEST.json](docs/current_idea/SOURCE_ASSET_MANIFEST.json) | 新增源文件 SHA256 与大小 |
| [历史独立候选方案复现](docs/reproduction/INDEPENDENT_CANDIDATE_REPRODUCTION.md) | 旧验证器及 baseline 从头训练指南 |

**结果版本优先级：本 README 的范围说明与独立审计优先于历史报告。**原 `detr_decoder_gmr/benchmark_summary.json`、`runs/*/predictions.npz` 是旧测试集 ordinal ranking 的方案 A 产物，不代表修正训练 CDF 主结果。10 份 `.pt` 属于历史方案 B，当前免训练加权和/幂律不需要这些权重。

原 `run_thresholded_gmr_eval.py` 仍输出 All Rej-F1 和整体拒绝比例；分组核验使用 `check_delivery.py`。交付文档若与此冲突，以源代码和审计为准。保留旧报告供追溯，不把未经支持的因果/Decoder 内生解释作为新结论。

## 5. 获取与复算

```bash
git clone --single-branch --branch experiments/evidence-calibration-20261007 \
  https://github.com/chinagalaxy2002/GMR_Unseen.git
cd GMR_Unseen
```

数据、原始视频、特征、候选和 baseline 权重沿用已上传的 [Google Drive 包](https://drive.google.com/drive/folders/17wf_qE7wdGpplPxaHuYA-JGdnb_1CHHs)。该包支持 baseline 训练。若归档已放在本机指定位置，从仓库根目录执行：

```bash
python /home/guoxiangyu/paper/Openword/repro/data/restore_bundle.py \
  --repo-root "$PWD" --verify-files
python reproduction/prepare_evidence_calibration.py
```

其他机器请将归档和 `restore_bundle.py` 下载至自选目录，替换上述路径。缓存来自 `07_verifier_experiment_feature_caches.tar.gz` 中 SDCV 的 15 个 NPZ；准备脚本创建相对路径链接，不绑定原机器。完整下载、依赖、baseline 训练与推理见[历史复现指南](docs/reproduction/INDEPENDENT_CANDIDATE_REPRODUCTION.md)的环境及 baseline 章节，数据说明见 [Drive 资产文档](docs/datasets/GMR_DRIVE_ASSETS_20261006.md)。

复算环境为 Python 3.8，依赖 numpy、scipy、scikit-learn；方案 B 另需 PyTorch。以下都是评估复算，不会训练骨干：

```bash
# P1：融合与证据消融
python experiments/agy_test/detr_decoder_gmr/run_mechanism_ablations.py
# Seen 阈值：All 指标（RR 是整体拒绝比例）
python experiments/agy_test/detr_decoder_gmr/run_thresholded_gmr_eval.py
# 单独分组：All / Seen / Unseen，保存 audit.json
python experiments/agy_test/delivery_audit_20261007/check_delivery.py
# 全局视频联合采样：2,000 次 AUROC 与 Unseen Rej-F1 差值区间
python experiments/agy_test/detr_decoder_gmr/run_joint_bootstrap_cluster.py
```

原始日志在 `experiments/agy_test/detr_decoder_gmr/logs/`。上述脚本使用恢复缓存和既有骨干输出；这不等于端到端训练重现。`evaluate_dec_gmr.py` 与 `train_and_evaluate.py` 是历史方案 A/B，并写入同名预测及汇总，运行会覆盖相应旧产物；主结果复算使用上列命令。
