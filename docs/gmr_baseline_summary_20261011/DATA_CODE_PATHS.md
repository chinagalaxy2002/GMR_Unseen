# 当前结果的数据、训练测试与模型代码路径

对应主 README 的四套数据与 48 个评测设置，更新于 2026-10-11。所有仓库路径均相对于仓库根目录；链接可直接打开。

本机原实验根目录为 `/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/`。下文标为“本机”的特征、视频和权重仅保存在这台机器上；GitHub 保存标注、源码快照、预测、阈值、bootstrap 与结果。

训练读取 `train.jsonl`（仅 S+/S−），选模型及阈值读取 `val_seen.jsonl`，最终评测读取 `test.jsonl`。`val.jsonl` 可含 Unseen，不用于选模；`test_matched_u.jsonl` 只是配对诊断，不是本文完整测试集。

## 1. 数据入口与原始来源

| 数据 | 发布数据 | 本次实际输入 |
| --- | --- | --- |
| Clean v3 | [data/release/semantic_existence_v3_release](../../data/release/semantic_existence_v3_release) | [experiments/agy_test/v3_release_baselines_20261009/groups](../../experiments/agy_test/v3_release_baselines_20261009/groups) |
| Balanced v3 | [data/release/semantic_existence_v3_balanced](../../data/release/semantic_existence_v3_balanced) | [experiments/agy_test/v3_balanced_baselines_20261010/groups](../../experiments/agy_test/v3_balanced_baselines_20261010/groups) |
| Charades-CG v2 | [data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2](../../data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2) | [data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2/splits/C3_CG](../../data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2/splits/C3_CG) |
| Soccer-GMR-Unseen v1 | [data/release/soccer_gmr_unseen_v1](../../data/release/soccer_gmr_unseen_v1) | [data/experiment_inputs/soccer_unseen_baselines_20261011/splits](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits) |

Clean / Balanced 的冻结标注位于实验目录的 `groups/<group>/release/<group>/`。CG v2 公开 split 与本机冻结副本逐字节一致。Soccer 的实际输入已经统一排除 37 条缺失特征关联查询，Test 每组为 2,233 条；原发布数据保持不变。

| 来源或辅助数据 | 路径 / 用途 |
| --- | --- |
| Charades 原始正例（本机） | `/home/guoxiangyu/paper/Openword/data/raw/charades_sta/{charades_pos_train,charades_pos_test}.jsonl` |
| Clean 审核后的正负池 | [positive_clean.jsonl](../../data/release/semantic_existence_v3_release/master/positive_clean.jsonl)；[negative_clean.jsonl](../../data/release/semantic_existence_v3_release/master/negative_clean.jsonl) |
| Clean 审核与旧候选（本机） | `data/release/semantic_existence_v3/`（审核档案）；`data/release/semantic_existence_v2/`（历史候选） |
| Balanced 追加负例 | [negative_added.jsonl.gz](../../data/release/semantic_existence_v3_balanced/master/negative_added.jsonl.gz)（解压后为 negative_added.jsonl）；[provenance/](../../data/release/semantic_existence_v3_balanced/provenance) |
| Charades-CG 官方原始文件 | [source/](../../data/release/charades_cg_gmr_v1/source) 下的 train.json、test_trivial.json、novel_composition.json；Novel-Word 不进入当前评测 |
| CG 原 v1 训练标注（本机） | `data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v1/`；Train / Seen Val 与 v2 相同 |
| Soccer 源标注 | [data/label/Full/](../../data/label/Full) 下的 train/val/test/full.jsonl；仅取 worldcup2022 |
| Soccer 干净来源池 | [data/release/soccer_gmr_unseen_v1/master/worldcup_clean.jsonl](../../data/release/soccer_gmr_unseen_v1/master/worldcup_clean.jsonl) |

## 2. Clean v3

发布数据：[data/release/semantic_existence_v3_release](../../data/release/semantic_existence_v3_release)。

本机运行目录：`experiments/agy_test/v3_release_baselines_20261009/`。

本次源码快照根目录 N：[experiments/agy_test/v3_release_baselines_20261009/native_source](../../experiments/agy_test/v3_release_baselines_20261009/native_source)。下表显示相对于 N 的路径，点击可打开完整文件。

初始化、分组和打包脚本依赖已经完成的逐条语义审核结果；审核档案与干净发布数据分开保存。

| 用途 | 脚本 / 文件路径 |
| --- | --- |
| 构建数据 | [init_semantic_existence_v3.py](../../scripts/init_semantic_existence_v3.py) → [build_semantic_existence_v3.py](../../scripts/build_semantic_existence_v3.py) → [package_semantic_existence_v3_clean_release.py](../../scripts/package_semantic_existence_v3_clean_release.py) |
| 校验数据 | [validate_semantic_existence_v3_clean_release.py](../../scripts/validate_semantic_existence_v3_clean_release.py) |
| 训练总控 | [experiments/agy_test/v3_release_baselines_20261009/run_baselines.py](../../experiments/agy_test/v3_release_baselines_20261009/run_baselines.py) |
| 训练启动器（moment / qd / flash） | [experiments/agy_test/v3_release_baselines_20261009/launch_native.sh](../../experiments/agy_test/v3_release_baselines_20261009/launch_native.sh) |
| 测试推理与指标评测总控 | [experiments/agy_test/v3_release_baselines_20261009/run_baselines.py](../../experiments/agy_test/v3_release_baselines_20261009/run_baselines.py) |
| 最终评测与高精度分数补算 | [experiments/agy_test/v3_release_baselines_20261009/finalize_baselines.py](../../experiments/agy_test/v3_release_baselines_20261009/finalize_baselines.py) |
| Seen/Unseen 退化汇总 | [scripts/summarize_gmr_degradation.py](../../scripts/summarize_gmr_degradation.py) |
| 固定训练 / 评测协议 | [experiments/agy_test/v3_release_baselines_20261009/PROTOCOL.json](../../experiments/agy_test/v3_release_baselines_20261009/PROTOCOL.json) |
| 源码校验清单 | [experiments/agy_test/v3_release_baselines_20261009/SOURCE_MANIFEST.json](../../experiments/agy_test/v3_release_baselines_20261009/SOURCE_MANIFEST.json) |
| 文本特征来源清单 | [experiments/agy_test/v3_release_baselines_20261009/TEXT_FEATURE_MANIFEST.json](../../experiments/agy_test/v3_release_baselines_20261009/TEXT_FEATURE_MANIFEST.json) |
| 最终结果目录 | [experiments/agy_test/v3_release_baselines_20261009/evaluation](../../experiments/agy_test/v3_release_baselines_20261009/evaluation) |

### 三个 backbone 的训练、测试与模型实现

| Backbone | 训练脚本 | 测试脚本 | 模型代码 | 模型配置 |
| --- | --- | --- | --- | --- |
| Moment-DETR-GMR | [training/moment_detr_gmr/train.py](../../experiments/agy_test/v3_release_baselines_20261009/native_source/training/moment_detr_gmr/train.py) | [training/moment_detr_gmr/evaluate.py](../../experiments/agy_test/v3_release_baselines_20261009/native_source/training/moment_detr_gmr/evaluate.py) | [models/moment_detr_gmr/moment_detr.py](../../experiments/agy_test/v3_release_baselines_20261009/native_source/models/moment_detr_gmr/moment_detr.py)<br>[GMR 存在判断：gmr_adapter.py](../../experiments/agy_test/v3_release_baselines_20261009/native_source/models/moment_detr_gmr/gmr_adapter.py) | [configs/moment_detr_gmr/model/moment_detr.yml](../../experiments/agy_test/v3_release_baselines_20261009/native_source/configs/moment_detr_gmr/model/moment_detr.yml) |
| QD-DETR-GMR | [training/qd_detr_gmr/train.py](../../experiments/agy_test/v3_release_baselines_20261009/native_source/training/qd_detr_gmr/train.py) | [training/qd_detr_gmr/evaluate.py](../../experiments/agy_test/v3_release_baselines_20261009/native_source/training/qd_detr_gmr/evaluate.py) | [models/qd_detr_gmr/model.py](../../experiments/agy_test/v3_release_baselines_20261009/native_source/models/qd_detr_gmr/model.py)<br>[GMR 存在判断：gmr_adapter.py](../../experiments/agy_test/v3_release_baselines_20261009/native_source/models/qd_detr_gmr/gmr_adapter.py) | [configs/qd_detr_gmr/model/qd_detr.yml](../../experiments/agy_test/v3_release_baselines_20261009/native_source/configs/qd_detr_gmr/model/qd_detr.yml) |
| FlashVTG-GMR | [training/flash_vtg_gmr/train.py](../../experiments/agy_test/v3_release_baselines_20261009/native_source/training/flash_vtg_gmr/train.py) | [training/flash_vtg_gmr/inference.py](../../experiments/agy_test/v3_release_baselines_20261009/native_source/training/flash_vtg_gmr/inference.py) | [models/flash_vtg_gmr/model.py](../../experiments/agy_test/v3_release_baselines_20261009/native_source/models/flash_vtg_gmr/model.py) | [configs/flash_vtg_gmr/model.py](../../experiments/agy_test/v3_release_baselines_20261009/native_source/configs/flash_vtg_gmr/model.py) |

数据集配置：[moment_detr_gmr](../../experiments/agy_test/v3_release_baselines_20261009/native_source/configs/moment_detr_gmr/dataset/charades_semantic_existence.yml)；[qd_detr_gmr](../../experiments/agy_test/v3_release_baselines_20261009/native_source/configs/qd_detr_gmr/dataset/charades_semantic_existence.yml)。最终参数同时以启动器命令行和冻结模型 metadata / opt.json 为准。

### 实际训练、选模和测试标注

| 划分 | 训练 | Seen 验证 | 完整测试 | 完整验证归档 |
| --- | --- | --- | --- | --- |
| A1_v3 | [train.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/A1_v3/release/A1_v3/train.jsonl) | [val_seen.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/A1_v3/release/A1_v3/val_seen.jsonl) | [test.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/A1_v3/release/A1_v3/test.jsonl) | [val.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/A1_v3/release/A1_v3/val.jsonl) |
| A2_v3 | [train.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/A2_v3/release/A2_v3/train.jsonl) | [val_seen.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/A2_v3/release/A2_v3/val_seen.jsonl) | [test.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/A2_v3/release/A2_v3/test.jsonl) | [val.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/A2_v3/release/A2_v3/val.jsonl) |
| A3_v3 | [train.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/A3_v3/release/A3_v3/train.jsonl) | [val_seen.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/A3_v3/release/A3_v3/val_seen.jsonl) | [test.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/A3_v3/release/A3_v3/test.jsonl) | [val.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/A3_v3/release/A3_v3/val.jsonl) |
| C1_v3 | [train.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/C1_v3/release/C1_v3/train.jsonl) | [val_seen.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/C1_v3/release/C1_v3/val_seen.jsonl) | [test.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/C1_v3/release/C1_v3/test.jsonl) | [val.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/C1_v3/release/C1_v3/val.jsonl) |
| C2_v3 | [train.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/C2_v3/release/C2_v3/train.jsonl) | [val_seen.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/C2_v3/release/C2_v3/val_seen.jsonl) | [test.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/C2_v3/release/C2_v3/test.jsonl) | [val.jsonl](../../experiments/agy_test/v3_release_baselines_20261009/groups/C2_v3/release/C2_v3/val.jsonl) |

### 当前结果与冻结预测

[三项指标与退化表](../../experiments/agy_test/v3_release_baselines_20261009/evaluation/GENERALIZATION_DROP_COMPARISON.md) · [标准评测表](../../experiments/agy_test/v3_release_baselines_20261009/evaluation/STANDARD_EVALUATION.md)

| 划分 | Backbone | 冻结结果目录 |
| --- | --- | --- |
| A1_v3 | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/A1_v3/evaluation/moment) |
| A1_v3 | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/A1_v3/evaluation/qd) |
| A1_v3 | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/A1_v3/evaluation/flash) |
| A2_v3 | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/A2_v3/evaluation/moment) |
| A2_v3 | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/A2_v3/evaluation/qd) |
| A2_v3 | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/A2_v3/evaluation/flash) |
| A3_v3 | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/A3_v3/evaluation/moment) |
| A3_v3 | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/A3_v3/evaluation/qd) |
| A3_v3 | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/A3_v3/evaluation/flash) |
| C1_v3 | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/C1_v3/evaluation/moment) |
| C1_v3 | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/C1_v3/evaluation/qd) |
| C1_v3 | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/C1_v3/evaluation/flash) |
| C2_v3 | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/C2_v3/evaluation/moment) |
| C2_v3 | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/C2_v3/evaluation/qd) |
| C2_v3 | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_release_baselines_20261009/groups/C2_v3/evaluation/flash) |

## 3. Balanced v3

发布数据：[data/release/semantic_existence_v3_balanced](../../data/release/semantic_existence_v3_balanced)。

本机运行目录：`experiments/agy_test/v3_balanced_baselines_20261010/`。

本次源码快照根目录 N：[experiments/agy_test/v3_balanced_baselines_20261010/native_source](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source)。下表显示相对于 N 的路径，点击可打开完整文件。

| 用途 | 脚本 / 文件路径 |
| --- | --- |
| 构建数据 | [build_semantic_existence_v3_balanced.py](../../scripts/build_semantic_existence_v3_balanced.py) |
| 校验数据 | [validate_semantic_existence_v3_balanced.py](../../scripts/validate_semantic_existence_v3_balanced.py) |
| 训练总控 | [experiments/agy_test/v3_balanced_baselines_20261010/run_baselines.py](../../experiments/agy_test/v3_balanced_baselines_20261010/run_baselines.py) |
| 训练启动器（moment / qd / flash） | [experiments/agy_test/v3_balanced_baselines_20261010/launch_native.sh](../../experiments/agy_test/v3_balanced_baselines_20261010/launch_native.sh) |
| 测试推理与指标评测总控 | [experiments/agy_test/v3_balanced_baselines_20261010/run_baselines.py](../../experiments/agy_test/v3_balanced_baselines_20261010/run_baselines.py) |
| Seen/Unseen 退化汇总 | [experiments/agy_test/v3_balanced_baselines_20261010/summarize_gmr_degradation.py](../../experiments/agy_test/v3_balanced_baselines_20261010/summarize_gmr_degradation.py) |
| 固定训练 / 评测协议 | [experiments/agy_test/v3_balanced_baselines_20261010/PROTOCOL.json](../../experiments/agy_test/v3_balanced_baselines_20261010/PROTOCOL.json) |
| 源码校验清单 | [experiments/agy_test/v3_balanced_baselines_20261010/SOURCE_MANIFEST.json](../../experiments/agy_test/v3_balanced_baselines_20261010/SOURCE_MANIFEST.json) |
| 文本特征来源清单 | [experiments/agy_test/v3_balanced_baselines_20261010/TEXT_FEATURE_MANIFEST.json](../../experiments/agy_test/v3_balanced_baselines_20261010/TEXT_FEATURE_MANIFEST.json) |
| 最终结果目录 | [experiments/agy_test/v3_balanced_baselines_20261010/evaluation](../../experiments/agy_test/v3_balanced_baselines_20261010/evaluation) |

### 三个 backbone 的训练、测试与模型实现

| Backbone | 训练脚本 | 测试脚本 | 模型代码 | 模型配置 |
| --- | --- | --- | --- | --- |
| Moment-DETR-GMR | [training/moment_detr_gmr/train.py](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/training/moment_detr_gmr/train.py) | [training/moment_detr_gmr/evaluate.py](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/training/moment_detr_gmr/evaluate.py) | [models/moment_detr_gmr/moment_detr.py](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/models/moment_detr_gmr/moment_detr.py)<br>[GMR 存在判断：gmr_adapter.py](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/models/moment_detr_gmr/gmr_adapter.py) | [configs/moment_detr_gmr/model/moment_detr.yml](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/configs/moment_detr_gmr/model/moment_detr.yml) |
| QD-DETR-GMR | [training/qd_detr_gmr/train.py](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/training/qd_detr_gmr/train.py) | [training/qd_detr_gmr/evaluate.py](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/training/qd_detr_gmr/evaluate.py) | [models/qd_detr_gmr/model.py](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/models/qd_detr_gmr/model.py)<br>[GMR 存在判断：gmr_adapter.py](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/models/qd_detr_gmr/gmr_adapter.py) | [configs/qd_detr_gmr/model/qd_detr.yml](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/configs/qd_detr_gmr/model/qd_detr.yml) |
| FlashVTG-GMR | [training/flash_vtg_gmr/train.py](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/training/flash_vtg_gmr/train.py) | [training/flash_vtg_gmr/inference.py](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/training/flash_vtg_gmr/inference.py) | [models/flash_vtg_gmr/model.py](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/models/flash_vtg_gmr/model.py) | [configs/flash_vtg_gmr/model.py](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/configs/flash_vtg_gmr/model.py) |

数据集配置：[moment_detr_gmr](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/configs/moment_detr_gmr/dataset/charades_semantic_existence.yml)；[qd_detr_gmr](../../experiments/agy_test/v3_balanced_baselines_20261010/native_source/configs/qd_detr_gmr/dataset/charades_semantic_existence.yml)。最终参数同时以启动器命令行和冻结模型 metadata / opt.json 为准。

### 实际训练、选模和测试标注

| 划分 | 训练 | Seen 验证 | 完整测试 | 完整验证归档 |
| --- | --- | --- | --- | --- |
| A1_v3 | [train.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A1_v3/release/A1_v3/train.jsonl) | [val_seen.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A1_v3/release/A1_v3/val_seen.jsonl) | [test.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A1_v3/release/A1_v3/test.jsonl) | [val.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A1_v3/release/A1_v3/val.jsonl) |
| A2_v3 | [train.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A2_v3/release/A2_v3/train.jsonl) | [val_seen.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A2_v3/release/A2_v3/val_seen.jsonl) | [test.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A2_v3/release/A2_v3/test.jsonl) | [val.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A2_v3/release/A2_v3/val.jsonl) |
| A3_v3 | [train.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A3_v3/release/A3_v3/train.jsonl) | [val_seen.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A3_v3/release/A3_v3/val_seen.jsonl) | [test.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A3_v3/release/A3_v3/test.jsonl) | [val.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A3_v3/release/A3_v3/val.jsonl) |
| C1_v3 | [train.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C1_v3/release/C1_v3/train.jsonl) | [val_seen.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C1_v3/release/C1_v3/val_seen.jsonl) | [test.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C1_v3/release/C1_v3/test.jsonl) | [val.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C1_v3/release/C1_v3/val.jsonl) |
| C2_v3 | [train.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C2_v3/release/C2_v3/train.jsonl) | [val_seen.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C2_v3/release/C2_v3/val_seen.jsonl) | [test.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C2_v3/release/C2_v3/test.jsonl) | [val.jsonl](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C2_v3/release/C2_v3/val.jsonl) |

### 当前结果与冻结预测

[三项指标与退化表](../../experiments/agy_test/v3_balanced_baselines_20261010/evaluation/GENERALIZATION_DROP_COMPARISON.md) · [标准评测表](../../experiments/agy_test/v3_balanced_baselines_20261010/evaluation/STANDARD_EVALUATION.md)

| 划分 | Backbone | 冻结结果目录 |
| --- | --- | --- |
| A1_v3 | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A1_v3/evaluation/moment) |
| A1_v3 | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A1_v3/evaluation/qd) |
| A1_v3 | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A1_v3/evaluation/flash) |
| A2_v3 | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A2_v3/evaluation/moment) |
| A2_v3 | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A2_v3/evaluation/qd) |
| A2_v3 | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A2_v3/evaluation/flash) |
| A3_v3 | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A3_v3/evaluation/moment) |
| A3_v3 | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A3_v3/evaluation/qd) |
| A3_v3 | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/A3_v3/evaluation/flash) |
| C1_v3 | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C1_v3/evaluation/moment) |
| C1_v3 | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C1_v3/evaluation/qd) |
| C1_v3 | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C1_v3/evaluation/flash) |
| C2_v3 | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C2_v3/evaluation/moment) |
| C2_v3 | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C2_v3/evaluation/qd) |
| C2_v3 | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/v3_balanced_baselines_20261010/groups/C2_v3/evaluation/flash) |

## 4. Charades-CG v2

发布数据：[data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2](../../data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2)。

本机运行目录：`experiments/agy_test/charades_cg_v2_evaluation_20261011/`。

本次源码快照根目录 N：[experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source)。下表显示相对于 N 的路径，点击可打开完整文件。

当前 v2 **未重新训练**：训练使用 v1 的原实验；v2 复用其 Seen 验证选定的 checkpoint 和阈值，重新推理全部 v2 Test。下面分别列出原训练入口与当前 v2 测试入口。原训练 common.py 的 RELEASE 仍指向本机 v1 数据目录，复现原训练时须提供该目录；其 Train / Seen Val 与 v2 逐字节一致。

| 用途 | 脚本 / 文件路径 |
| --- | --- |
| 构建数据 | [build_charades_cg_gmr_c3.py](../../scripts/build_charades_cg_gmr_c3.py) |
| 校验数据 | [validate_charades_cg_gmr_c3.py](../../scripts/validate_charades_cg_gmr_c3.py) |
| 训练总控 | [experiments/agy_test/charades_cg_baselines_20261010/run_baselines.py](../../experiments/agy_test/charades_cg_baselines_20261010/run_baselines.py) |
| 训练启动器（moment / qd / flash） | [experiments/agy_test/charades_cg_baselines_20261010/launch_native.sh](../../experiments/agy_test/charades_cg_baselines_20261010/launch_native.sh) |
| 测试推理与指标评测总控 | [experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/run_baselines.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/run_baselines.py) |
| 独立评测复核 | [experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/verify_evaluation.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/verify_evaluation.py) |
| 原训练使用的源码 | [experiments/agy_test/charades_cg_baselines_20261010/native_source](../../experiments/agy_test/charades_cg_baselines_20261010/native_source) |
| Seen/Unseen 退化汇总 | [experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/summarize_gmr_degradation_repository.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/summarize_gmr_degradation_repository.py) |
| 固定训练 / 评测协议 | [experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/PROTOCOL.json](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/PROTOCOL.json) |
| 源码校验清单 | [experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/SOURCE_MANIFEST.json](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/SOURCE_MANIFEST.json) |
| 文本特征来源清单 | [experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/TEXT_FEATURE_MANIFEST.json](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/TEXT_FEATURE_MANIFEST.json) |
| 最终结果目录 | [experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011) |

### 三个 backbone 的训练、测试与模型实现

| Backbone | 训练脚本 | 测试脚本 | 模型代码 | 模型配置 |
| --- | --- | --- | --- | --- |
| Moment-DETR-GMR | [training/moment_detr_gmr/train.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/training/moment_detr_gmr/train.py) | [training/moment_detr_gmr/evaluate.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/training/moment_detr_gmr/evaluate.py) | [models/moment_detr_gmr/moment_detr.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/models/moment_detr_gmr/moment_detr.py)<br>[GMR 存在判断：gmr_adapter.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/models/moment_detr_gmr/gmr_adapter.py) | [configs/moment_detr_gmr/model/moment_detr.yml](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/configs/moment_detr_gmr/model/moment_detr.yml) |
| QD-DETR-GMR | [training/qd_detr_gmr/train.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/training/qd_detr_gmr/train.py) | [training/qd_detr_gmr/evaluate.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/training/qd_detr_gmr/evaluate.py) | [models/qd_detr_gmr/model.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/models/qd_detr_gmr/model.py)<br>[GMR 存在判断：gmr_adapter.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/models/qd_detr_gmr/gmr_adapter.py) | [configs/qd_detr_gmr/model/qd_detr.yml](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/configs/qd_detr_gmr/model/qd_detr.yml) |
| FlashVTG-GMR | [training/flash_vtg_gmr/train.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/training/flash_vtg_gmr/train.py) | [training/flash_vtg_gmr/inference.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/training/flash_vtg_gmr/inference.py) | [models/flash_vtg_gmr/model.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/models/flash_vtg_gmr/model.py) | [configs/flash_vtg_gmr/model.py](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/configs/flash_vtg_gmr/model.py) |

数据集配置：[moment_detr_gmr](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/configs/moment_detr_gmr/dataset/charades_semantic_existence.yml)；[qd_detr_gmr](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/source_snapshot/native_source/configs/qd_detr_gmr/dataset/charades_semantic_existence.yml)。最终参数同时以启动器命令行和冻结模型 metadata / opt.json 为准。

### 实际训练、选模和测试标注

| 划分 | 训练 | Seen 验证 | 完整测试 | 完整验证归档 |
| --- | --- | --- | --- | --- |
| C3_CG | [train.jsonl](../../data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2/splits/C3_CG/train.jsonl) | [val_seen.jsonl](../../data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2/splits/C3_CG/val_seen.jsonl) | [test.jsonl](../../data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2/splits/C3_CG/test.jsonl) | — |

### 当前结果与冻结预测

[三项指标与退化表](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/GENERALIZATION_DROP_COMPARISON.md) · [标准评测表](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/STANDARD_EVALUATION.md)

| 划分 | Backbone | 冻结结果目录 |
| --- | --- | --- |
| C3_CG | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/frozen/C3_CG/moment) |
| C3_CG | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/frozen/C3_CG/qd) |
| C3_CG | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/charades_cg/docs/reports/charades_cg_gmr_baselines_20261011/frozen/C3_CG/flash) |

## 5. Soccer-GMR-Unseen v1

发布数据：[data/release/soccer_gmr_unseen_v1](../../data/release/soccer_gmr_unseen_v1)。

本机运行目录：`experiments/agy_test/soccer_unseen_baselines_20261011/`。

本次源码快照根目录 N：[experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source)。下表显示相对于 N 的路径，点击可打开完整文件。

GitHub 的 `source_snapshot/` 是原实验源码归档；本机运行目录仍是上面的 `soccer_unseen_baselines_20261011/`。其中 `common.py` 的 ROOT/REPO 按原运行布局解析，复现时应恢复该布局并配置本机视频、特征路径。

| 用途 | 脚本 / 文件路径 |
| --- | --- |
| 构建数据 | [build_soccer_gmr_unseen.py](../../scripts/build_soccer_gmr_unseen.py) |
| 校验数据 | [validate_soccer_gmr_unseen.py](../../scripts/validate_soccer_gmr_unseen.py) |
| 训练总控 | [experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/run_baselines.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/run_baselines.py) |
| 训练启动器（moment / qd / flash） | [experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/launch_native.sh](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/launch_native.sh) |
| 测试推理与指标评测总控 | [experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/run_baselines.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/run_baselines.py) |
| 特征准备与重新编码 | [experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/prepare_features.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/prepare_features.py) |
| 覆盖检查与冻结输入 | [experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/prepare_experiment.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/prepare_experiment.py) |
| 特征完成后自动训练 | [experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/continue_after_features.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/continue_after_features.py) |
| 后台全流程 | [experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/background_pipeline.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/background_pipeline.py) |
| Seen/Unseen 退化汇总 | [experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/summarize_gmr_degradation.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/summarize_gmr_degradation.py) |
| 固定训练 / 评测协议 | [experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/PROTOCOL.json](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/PROTOCOL.json) |
| 源码校验清单 | [experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/SOURCE_MANIFEST.json](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/SOURCE_MANIFEST.json) |
| 文本特征来源清单 | [experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/TEXT_FEATURE_MANIFEST.json](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/TEXT_FEATURE_MANIFEST.json) |
| 最终结果目录 | [experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011) |

### 三个 backbone 的训练、测试与模型实现

| Backbone | 训练脚本 | 测试脚本 | 模型代码 | 模型配置 |
| --- | --- | --- | --- | --- |
| Moment-DETR-GMR | [training/moment_detr_gmr/train.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/training/moment_detr_gmr/train.py) | [training/moment_detr_gmr/evaluate.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/training/moment_detr_gmr/evaluate.py) | [models/moment_detr_gmr/moment_detr.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/models/moment_detr_gmr/moment_detr.py)<br>[GMR 存在判断：gmr_adapter.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/models/moment_detr_gmr/gmr_adapter.py) | [configs/moment_detr_gmr/model/moment_detr.yml](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/configs/moment_detr_gmr/model/moment_detr.yml) |
| QD-DETR-GMR | [training/qd_detr_gmr/train.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/training/qd_detr_gmr/train.py) | [training/qd_detr_gmr/evaluate.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/training/qd_detr_gmr/evaluate.py) | [models/qd_detr_gmr/model.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/models/qd_detr_gmr/model.py)<br>[GMR 存在判断：gmr_adapter.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/models/qd_detr_gmr/gmr_adapter.py) | [configs/qd_detr_gmr/model/qd_detr.yml](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/configs/qd_detr_gmr/model/qd_detr.yml) |
| FlashVTG-GMR | [training/flash_vtg_gmr/train.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/training/flash_vtg_gmr/train.py) | [training/flash_vtg_gmr/inference.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/training/flash_vtg_gmr/inference.py) | [models/flash_vtg_gmr/model.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/models/flash_vtg_gmr/model.py) | [configs/flash_vtg_gmr/model.py](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/configs/flash_vtg_gmr/model.py) |

数据集配置：[moment_detr_gmr](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/configs/moment_detr_gmr/dataset/soccer_gmr.yml)；[qd_detr_gmr](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/configs/qd_detr_gmr/dataset/soccer_gmr.yml)；[Flash Soccer 配置](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/source_snapshot/native_source/configs/flash_vtg_gmr/soccer_gmr.json)。最终参数同时以启动器命令行和冻结模型 metadata / opt.json 为准。

### 实际训练、选模和测试标注

| 划分 | 训练 | Seen 验证 | 完整测试 | 完整验证归档 |
| --- | --- | --- | --- | --- |
| A1_soccer | [train.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/A1_soccer/train.jsonl) | [val_seen.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/A1_soccer/val_seen.jsonl) | [test.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/A1_soccer/test.jsonl) | [val.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/A1_soccer/val.jsonl) |
| A2_soccer | [train.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/A2_soccer/train.jsonl) | [val_seen.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/A2_soccer/val_seen.jsonl) | [test.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/A2_soccer/test.jsonl) | [val.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/A2_soccer/val.jsonl) |
| A3_soccer | [train.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/A3_soccer/train.jsonl) | [val_seen.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/A3_soccer/val_seen.jsonl) | [test.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/A3_soccer/test.jsonl) | [val.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/A3_soccer/val.jsonl) |
| C1_soccer | [train.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/C1_soccer/train.jsonl) | [val_seen.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/C1_soccer/val_seen.jsonl) | [test.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/C1_soccer/test.jsonl) | [val.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/C1_soccer/val.jsonl) |
| C2_soccer | [train.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/C2_soccer/train.jsonl) | [val_seen.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/C2_soccer/val_seen.jsonl) | [test.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/C2_soccer/test.jsonl) | [val.jsonl](../../data/experiment_inputs/soccer_unseen_baselines_20261011/splits/C2_soccer/val.jsonl) |

### 当前结果与冻结预测

[三项指标与退化表](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/GENERALIZATION_DROP_COMPARISON.md) · [标准评测表](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/STANDARD_EVALUATION.md)

| 划分 | Backbone | 冻结结果目录 |
| --- | --- | --- |
| A1_soccer | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/A1_soccer/moment) |
| A1_soccer | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/A1_soccer/qd) |
| A1_soccer | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/A1_soccer/flash) |
| A2_soccer | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/A2_soccer/moment) |
| A2_soccer | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/A2_soccer/qd) |
| A2_soccer | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/A2_soccer/flash) |
| A3_soccer | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/A3_soccer/moment) |
| A3_soccer | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/A3_soccer/qd) |
| A3_soccer | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/A3_soccer/flash) |
| C1_soccer | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/C1_soccer/moment) |
| C1_soccer | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/C1_soccer/qd) |
| C1_soccer | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/C1_soccer/flash) |
| C2_soccer | Moment-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/C2_soccer/moment) |
| C2_soccer | QD-DETR-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/C2_soccer/qd) |
| C2_soccer | FlashVTG-GMR | [预测 / 阈值 / bootstrap](../../experiments/agy_test/publication_review_20261011/soccer_unseen/docs/reports/soccer_unseen_baselines_20261011/frozen/C2_soccer/flash) |

## 6. 本机视频、特征与模型权重

以下为原实验机器上的完整目录，文件未上传 GitHub。所有本机路径已核对存在。

| 内容 | 本机路径 |
| --- | --- |
| Charades CLIP 视频特征（Clean / Balanced / CG 共用） | `/home/guoxiangyu/paper/新建文件夹/charades/vid_clip/` |
| Charades SlowFast 视频特征（同上） | `/home/guoxiangyu/paper/新建文件夹/charades/vid_slowfast/` |
| Clean v3 查询 token 特征 | `/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/v3_release_baselines_20261009/features/clip_text/` |
| Balanced v3 查询 token 特征 | `/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/v3_balanced_baselines_20261010/features/clip_text/` |
| Charades-CG v2 查询 token 特征 | `/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/charades_cg_v2_evaluation_20261011/features/clip_text/` |
| Soccer-GMR-Unseen v1 查询 token 特征 | `/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/soccer_unseen_baselines_20261011/features/clip_text/` |
| Soccer CLIP 视频特征 | `/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/soccer_unseen_baselines_20261011/features/clip/` |
| Soccer SlowFast 视频特征 | `/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/soccer_unseen_baselines_20261011/features/slowfast/` |
| Soccer 按完整 query 哈希共享的文本缓存 | `/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/agy_test/soccer_unseen_baselines_20261011/features/generated_text/` |
| Soccer 原视频片段 | `/home/guoxiangyu/VLMbasedIter_momentretrival/generalized-moment-retrieval/Soccergmr/WC2022-GMR/` |

Clean / Balanced 的 token 特征按 qid 与文本哈希核验复用；Balanced 新 qid 映射到 donor 特征。CG v2 在精确文本核验后复用并补编码缺失文本；Soccer 按完整 query 重新编码。逐条来源以各节 TEXT_FEATURE_MANIFEST.json 为准。

本机 checkpoint 与日志目录如下；`<group>` 取对应数据集的划分，`<bb>` 取 `moment`、`qd` 或 `flash`。Moment/QD 权重名为 `best.ckpt`，Flash 为 `model_best.ckpt`。

| 数据 / 用途 | 相对于本机原实验根目录的路径 |
| --- | --- |
| Clean v3 冻结权重 | `experiments/agy_test/v3_release_baselines_20261009/groups/<group>/frozen_checkpoints/<bb>/` |
| Balanced v3 冻结权重 | `experiments/agy_test/v3_balanced_baselines_20261010/groups/<group>/frozen_checkpoints/<bb>/` |
| Charades-CG v2 冻结权重 | `experiments/agy_test/charades_cg_baselines_20261010/groups/<group>/frozen_checkpoints/<bb>/` |
| Soccer-GMR-Unseen v1 冻结权重 | `experiments/agy_test/soccer_unseen_baselines_20261011/groups/<group>/frozen_checkpoints/<bb>/` |
| Clean v3 训练日志 | `experiments/agy_test/v3_release_baselines_20261009/groups/<group>/runs/<bb>/` |
| Balanced v3 训练日志 | `experiments/agy_test/v3_balanced_baselines_20261010/groups/<group>/runs/<bb>/` |
| Charades-CG v2 训练日志 | `experiments/agy_test/charades_cg_baselines_20261010/groups/<group>/runs/<bb>/` |
| Soccer-GMR-Unseen v1 训练日志 | `experiments/agy_test/soccer_unseen_baselines_20261011/groups/<group>/runs/<bb>/` |

CG v2 的模型权重归属于旧训练目录 charades_cg_baselines_20261010，v2 原生测试输出归属于 charades_cg_v2_evaluation_20261011。GitHub 仅保留 checkpoint 的 MANIFEST、验证预测与 opt.json 等元数据，不含模型权重。

## 7. 统一汇总与归档

| 内容 | 入口 |
| --- | --- |
| 48 设置的逐划分指标与置信区间 | [docs/gmr_baseline_summary_20261011/RESULTS_WITH_CI.md](../../docs/gmr_baseline_summary_20261011/RESULTS_WITH_CI.md) |
| 机器可读汇总 | [metrics.json](../../docs/gmr_baseline_summary_20261011/metrics.json)；[metrics.csv](../../docs/gmr_baseline_summary_20261011/metrics.csv) |
| 实际样本计数 | [docs/gmr_baseline_summary_20261011/DATASET_COUNTS.md](../../docs/gmr_baseline_summary_20261011/DATASET_COUNTS.md) |
| 实验归属 | [docs/gmr_baseline_summary_20261011/EXPERIMENTS.json](../../docs/gmr_baseline_summary_20261011/EXPERIMENTS.json) |
| 工程实验报告 | [README_ENGINEERING.md](../../README_ENGINEERING.md) |
| 原主 README 原样归档 | [README_EXPERIMENT_REPORT.md](../../README_EXPERIMENT_REPORT.md) |
