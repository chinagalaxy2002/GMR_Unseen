# GMR 三组基准实验汇总

本分支汇总 Clean Semantic Existence v3、Balanced v3 与 Charades-CG-GMR v2 的数据、方法源码、运行脚本和冻结结果，更新于 **2026-10-11**。两个 v3 项目各完成五划分 × 三 backbone（15/15）；Charades-CG v2 完成 C3_CG × 三 backbone（3/3），共 **33 个已完成评测设置**。本次仅整理已有实验，未新增训练、调参或方法实验。

## 项目与数据入口

| 项目 | 实验 README | 对应数据集 | 完成设置 |
|---|---|---|---:|
| Clean v3 | [v3_release_baselines_20261009](experiments/agy_test/v3_release_baselines_20261009/README.md) | [semantic_existence_v3_release](data/release/semantic_existence_v3_release/README.md) | 15/15 |
| Balanced v3 | [v3_balanced_baselines_20261010](experiments/agy_test/v3_balanced_baselines_20261010/README.md) | [semantic_existence_v3_balanced](data/release/semantic_existence_v3_balanced/README.md) | 15/15 |
| Charades-CG v2 | [charades_cg](experiments/agy_test/publication_review_20261011/charades_cg/README.md) | [charades_cg_gmr_v2](data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2/README.md) | 3/3 |

方法包含 **Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR**。各项目的 `native_source/` 或 `source_snapshot/native_source/` 保留实际使用的 `models/`、`training/`、`configs/` 和 `eval/`，以各自 `SOURCE_MANIFEST.json` 为准。

## 数据版本、构建方式与划分

**Clean v3**：完成语义审计后保留 15,034 个正例 qid 与 2,869 个不同负例 qid，排除隔离与剔除样本。A1/A2/A3 分别留出放置/拿取、饮用/倾倒、跑步/行走；C1 留出坐×床/椅/沙发，C2 留出打开/关闭×箱/柜。完整查询若含已断言的留出事件便不进入训练。审计未逐视频确认事件缺席。

**Balanced v3**：保留 Clean v3 原始行，补充跨视频伪负例。用归一化 CLIP 文本向量，对目标视频全部正描述取最大余弦相似度，按查询选排名最低 50% 的候选视频，再执行标注冲突过滤与配额采样，使每个完整 split 正负 1:1；Seen/Unseen 内部仍可能不平衡。新增负例未经视频缺席核验，不能将低文本相似度当作真实缺席证明。

**Charades-CG v2**：官方 Test-Trivial 为 Seen，Novel-Composition 为 Unseen；只含 C3_CG。机械剔除 2,119 条非法/越界正例窗口而不截断，再构造同 split 跨视频负例。两类测试正描述共同进入候选池；S−/U− 在联合池重新采样。Train 与 Seen validation 和 v1 逐字节相同，测试使用全量 v2 重新推理。训练为 6,342 正 + 6,342 负，Seen validation 为 684 正 + 684 负，测试为 11,348 行。负例均为构造标签，未经逐视频缺席确认；Unseen 指下游未见组合，不代表预训练从未见过相关概念。

![三套数据的原始构建图合并](assets/gmr_baseline_summary_20261011/construction_pipelines.svg)

*图 1：三套数据具有不同来源与负例构造过程。按项目合并原始矢量管线；最低 50% 指视频排名比例，非余弦阈值 0.5。*

<details>
<summary>五类语义留出：合并原有 A1–C2 示意图</summary>

![五类划分原图合并](assets/gmr_baseline_summary_20261011/semantic_splits.svg)

该图保留 Clean v3 的原始定义、真实查询示例和统计；Balanced v3 沿用相同语义定义，但补充负例后的数量见下表。

</details>

| 数据集 | Test split | S+ | S− | U+ | U− | 总行数 |
|---|---|---:|---:|---:|---:|---:|
| Clean v3 | A1_v3 | 2857 | 983 | 596 | 175 | 4611 |
| Clean v3 | A2_v3 | 3230 | 1066 | 223 | 92 | 4611 |
| Clean v3 | A3_v3 | 3218 | 1036 | 235 | 122 | 4611 |
| Clean v3 | C1_v3 | 3311 | 894 | 142 | 264 | 4611 |
| Clean v3 | C2_v3 | 3322 | 1066 | 131 | 92 | 4611 |
| Balanced v3 | A1_v3 | 2857 | 2882 | 596 | 571 | 6906 |
| Balanced v3 | A2_v3 | 3230 | 3213 | 223 | 240 | 6906 |
| Balanced v3 | A3_v3 | 3218 | 3175 | 235 | 278 | 6906 |
| Balanced v3 | C1_v3 | 3311 | 3095 | 142 | 358 | 6906 |
| Balanced v3 | C2_v3 | 3322 | 3274 | 131 | 179 | 6906 |
| Charades-CG v2 | C3_CG | 2684 | 2684 | 2990 | 2990 | 11348 |

![三版本数据组成合并](assets/gmr_baseline_summary_20261011/dataset_composition.svg)

*图 2：Balanced v3 的完整测试集与 Charades-CG v2 正负平衡，Balanced 的 Seen/Unseen 子集仍有比例差异。图中 S/U 为 Seen/Unseen，+/− 为存在/缺席构造标签；全部 train/val/test 计数见 [DATASET_COUNTS](docs/gmr_baseline_summary_20261011/DATASET_COUNTS.md)。五划分共享视频与查询，不能把行数相加当作独立样本数。*

## 统一训练和评测协议

| 项目 | 固定设置 |
|---|---|
| 特征 | CLIP 文本，CLIP + SlowFast 视频；精确查询 SHA-256 核验复用特征 |
| 训练 | S+/S− only；seed 3407；从头训练，最多 100 epochs；max_es_cnt=26（连续 27 次无改善早停） |
| Checkpoint | Moment/QD：Seen validation MR-full-mAP；Flash：Seen validation R1@0.5 与 R1@0.7 均值 |
| 阈值 | 完整 Seen validation 的 5–95 分位数、91 个候选，最大化 Balanced Accuracy，并列取最早；score ≥ threshold 接受 |
| 分数 | Moment/QD 原生四位 sigmoid；Flash 原生六位 logit，避免三位概率饱和并列 |
| 定位 | 原生输出第一个合法窗口；不因窗口终点超过标注时长改选后续窗口 |
| 不确定性 | 2,000 次 video-cluster bootstrap，seed 3407，冻结 checkpoint 与阈值；Seen/Unseen 共享视频联合重采样 |
| 宏平均 | 仅 Clean/Balanced 的五组全部完成后作等权 MACRO；共同视频宇宙配对抽样；C3_CG 单独报告 |

Charades-CG v2 **复用原 C3_CG 的冻结 checkpoint、Seen-validation 原生预测及阈值**，只重新推理 v2 测试；其训练/验证与 v1 相同。CI 反映固定模型下的视频抽样不确定性，不代表跨训练种子波动。

AUROC 为存在分数的排序能力。Actual Rej-F1 将拒绝作为正决策，`2TN/(2TN+FP+FN)`；TN 为正确拒绝缺席，FP 为错误接受缺席，FN 为错误拒绝存在。G-mIoU@1 接受查询时使用原生 top-1 的集合 IoU；拒绝负例得 1，拒绝正例得 0，再对全部样本平均。**Gap = Seen − Unseen**，统一用 pp；AUROC 差值乘 100，负 Gap 保留为 Unseen 点估计更高。

## 主要结果

下表各单元格为 **Seen → Unseen（Gap pp）**。AUROC 为 0–1；Rej-F1、G-mIoU@1 为百分数。Clean/Balanced 为完整五划分等权宏平均，Charades-CG 为单划分。

| 数据 / 汇总范围 | Backbone | AUROC | Rej-F1 (%) | G-mIoU@1 (%) |
|---|---|---:|---:|---:|
| Clean v3 / MACRO | Moment-DETR-GMR | 0.7238 → 0.5224 (+20.14) | 50.51 → 22.25 (+28.27) | 34.54 → 25.51 (+9.03) |
| Clean v3 / MACRO | QD-DETR-GMR | 0.7413 → 0.5337 (+20.76) | 51.30 → 30.61 (+20.68) | 34.86 → 28.02 (+6.84) |
| Clean v3 / MACRO | FlashVTG-GMR | 0.7543 → 0.5647 (+18.96) | 53.36 → 37.09 (+16.27) | 41.75 → 34.44 (+7.31) |
| Balanced v3 / MACRO | Moment-DETR-GMR | 0.7253 → 0.6466 (+7.87) | 65.88 → 62.11 (+3.76) | 45.99 → 43.16 (+2.83) |
| Balanced v3 / MACRO | QD-DETR-GMR | 0.5445 → 0.5093 (+3.52) | 56.87 → 61.40 (-4.53) | 39.01 → 47.17 (-8.16) |
| Balanced v3 / MACRO | FlashVTG-GMR | 0.7706 → 0.6608 (+10.98) | 68.04 → 61.68 (+6.36) | 51.48 → 44.85 (+6.63) |
| Charades-CG v2 / C3_CG | Moment-DETR-GMR | 0.6338 → 0.5587 (+7.51) | 63.87 → 60.10 (+3.77) | 45.95 → 41.49 (+4.46) |
| Charades-CG v2 / C3_CG | QD-DETR-GMR | 0.5050 → 0.4984 (+0.66) | 57.42 → 57.58 (-0.16) | 39.44 → 38.11 (+1.33) |
| Charades-CG v2 / C3_CG | FlashVTG-GMR | 0.7997 → 0.7204 (+7.93) | 70.63 → 64.24 (+6.39) | 53.43 → 44.96 (+8.47) |

![Seen Unseen 三指标合并](assets/gmr_baseline_summary_20261011/seen_unseen_performance.svg)

*图 3：三套数据中，多数模型的 Unseen AUROC 点估计低于 Seen。每行对应独立数据版本，每列对应一项指标；圆点/方点分别为 Seen/Unseen，误差线为视频聚类 bootstrap 95% CI。不同版本不构成同测试集方法比较。*

![全部划分泛化差距合并](assets/gmr_baseline_summary_20261011/generalization_gaps.svg)

*图 4：泛化差距随划分、模型和指标而改变；负 Gap 原样保留。展示各 split/backbone 与五组 MACRO 的 95% CI，虚线为零。区间含零时不将点估计方向解读为明确退化或改善。*

**完整结果与 CI**：[逐划分、逐 backbone 的三项 Seen/Unseen、Gap 及 overall 表](docs/gmr_baseline_summary_20261011/RESULTS_WITH_CI.md) · [CSV](docs/gmr_baseline_summary_20261011/metrics.csv) · [JSON](docs/gmr_baseline_summary_20261011/metrics.json)。所有汇总均读取未舍入的冻结 JSON。

| 数据 / 汇总范围 | Backbone | Overall Rej-F1 | Overall RR | S+ FRR | U+ FRR | Overall G-mIoU@1 |
|---|---|---:|---:|---:|---:|---:|
| Clean v3 / MACRO | Moment-DETR-GMR | 48.70% | 35.63% | 28.45% | 24.42% | 33.53% |
| Clean v3 / MACRO | QD-DETR-GMR | 49.56% | 38.01% | 30.02% | 31.59% | 33.98% |
| Clean v3 / MACRO | FlashVTG-GMR | 52.46% | 39.15% | 29.66% | 34.68% | 40.91% |
| Balanced v3 / MACRO | Moment-DETR-GMR | 65.46% | 49.32% | 32.59% | 41.07% | 45.65% |
| Balanced v3 / MACRO | QD-DETR-GMR | 57.21% | 63.54% | 59.29% | 71.86% | 39.45% |
| Balanced v3 / MACRO | FlashVTG-GMR | 67.39% | 45.19% | 24.60% | 40.36% | 50.82% |
| Charades-CG v2 / C3_CG | Moment-DETR-GMR | 61.86% | 66.16% | 55.89% | 64.58% | 43.60% |
| Charades-CG v2 / C3_CG | QD-DETR-GMR | 57.50% | 67.15% | 67.29% | 66.62% | 38.74% |
| Charades-CG v2 / C3_CG | FlashVTG-GMR | 67.25% | 43.87% | 21.20% | 27.66% | 48.97% |

**结果解读**：Clean v3 的三模型宏平均 AUROC Gap 为 18.96–20.76 pp；Balanced v3 为 3.52–10.98 pp，但其负例构造、训练分布和测试组成均改变，不能称为同测试集方法净增益。Balanced QD 的 Unseen AUROC 仅 0.5093，却有负的 Rej-F1/G-mIoU Gap；应结合其 U+ FRR 71.86% 阅读。Charades-CG 的 Moment/Flash 三项 Gap CI 均高于零；QD 三项 Gap CI 均含零，其 AUROC 接近随机排序。

Rej-F1 与 G-mIoU 受正负比例影响；高正确拒绝率可以抬高端到端数值，负 Gap 也不直接等价于正例定位提升。在 Charades-CG 每个子集正负 1:1 下，一律拒绝的公式参照为 Rej-F1=66.67%、G-mIoU=50%、正例 FRR=100%（恒定分数 AUROC=0.5）。该参照仅是确定性公式结果。

独立 baseline 的 **Unseen Net Gain、Seen Change、Gap Reduction 对三项指标均未定义（N/A）**。未来方法须与同版本、同 split、同 backbone baseline 进行成对比较并报告 paired bootstrap CI；不把跨版本差值当作方法增益，本包也未检验 backbone 之间的成对显著性。

## 源码、脚本和冻结结果

| 内容 | 位置 |
|---|---|
| 数据制作 / 校验 | [scripts](scripts/)；各数据集 `construction_protocol.json`、`validation_report.json`、清单和 provenance |
| Clean / Balanced 实际模型源码与配置 | 各实验 `native_source/{models,training,configs,eval}/` 与 `SOURCE_MANIFEST.json` |
| Clean / Balanced 训练和推理 | 各实验 `run_baselines.py`、`common.py`、`launch_native.sh`；原训练配置保留于 `groups/*/runs/` |
| Clean / Balanced 冻结输出 | `groups/*/evaluation/*/{predictions.npz,FROZEN_CALIBRATION.json,bootstrap_draws.npz,metrics.json,bootstrap.json}`；`frozen_checkpoints/` 保留权重哈希与原验证预测；`runs/*/test/` 保留原生测试窗口 |
| Clean / Balanced 补充 bootstrap | `evaluation/degradation_cache/`、`degradation_bootstrap.json`，以及原始 Markdown/CSV/JSON |
| Charades-CG 自含审阅包 | [README](experiments/agy_test/publication_review_20261011/charades_cg/README.md)；包内 `docs/reports/charades_cg_gmr_baselines_20261011/{frozen,source_snapshot}/` |
| Charades-CG 原训练与 v2 执行脚本 | [原训练](experiments/agy_test/charades_cg_baselines_20261010/) · [v2 重评估](experiments/agy_test/charades_cg_v2_evaluation_20261011/)；实际 native 源码见审阅包快照 |
| 图表 | [合并图](assets/gmr_baseline_summary_20261011/)；原图与绘制代码保留于 `assets/semantic_existence_v3/` 和 Charades-CG 包内 assets |
| 本次发布元数据 | [PACKAGING](docs/gmr_baseline_summary_20261011/PACKAGING.json) · [PUBLICATION_MANIFEST](docs/gmr_baseline_summary_20261011/PUBLICATION_MANIFEST.json) · [实验完成记录](docs/gmr_baseline_summary_20261011/EXPERIMENTS.json) |

发布范围包含标注、方法/训练/评估源码、配置、脚本、冻结预测、校准与 bootstrap 产物。遵循仓库约定，视频、特征数组、模型权重和凭据不进入提交；权重以原始 SHA-256 清单追溯。Balanced 的超大 `master/negative_added.jsonl` 使用无损 gzip 存储，还原后逐字节匹配原校验值。日志归档为 `.log.gz`。

## 使用与复现

从仓库根目录还原超大标注并校验发布文件：

```bash
python scripts/restore_gmr_publication.py
```

汇总与重绘只读取已保存结果，不需要视频、特征或权重：

```bash
python -m pip install -r requirements-publication.txt
python scripts/build_gmr_publication_summary.py
```

重绘直接合并原始 SVG 元素，并从冻结指标/标注生成数据组成、性能与 Gap 图；导出 SVG/PDF/PNG，原始矢量图可单独查看。

训练依赖见 `requirements.txt`、`requirements-flash-vtg.txt`；数据构建另见 `requirements-dataset.txt`。原始 `run_baselines.py` / `common.py` 是执行时源码记录，包含本机解释器、视频目录及历史特征清单路径；在其他机器运行须先按 README 和 `PROTOCOL.json` 配置路径并准备外部特征、冻结权重或新训练目录。`launch_native.sh` 支持 `V3_NATIVE_REPO`、`DATA_ROOT`、`FEATURE_ROOT`、`VIDEO_ROOT`、`RUN_ROOT`、`TRAIN_GPU`、`GMR_PYTHON` 和 `FLASH_PYTHON`；应使用全新 RUN_ROOT，以免覆盖已有实验。Charades 原训练脚本所用 native 源码在审阅包中，需对应设置其路径。

已有 `RELEASE_VALIDATION`、`LOCAL_VERIFICATION` 和独立验收记录保留为历史证据。本次整理未重新运行训练或实验验证；还原脚本执行发布级 SHA-256 完整性校验。完整重建语义审计或 CLIP 排名还需要原始审计工作材料、外部向量缓存等未发布输入，不能仅凭无权重发布包完成。
