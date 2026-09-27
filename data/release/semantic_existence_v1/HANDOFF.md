# Semantic novelty × existence 数据集交接

## 交接状态与完成口径

- 当前版本：`semantic_existence_v1`。正式 train/val/test、同视频 U+/U− 配对、语义清单、统计、来源校验和均已生成；正式文件通过 `scripts/validate_release.py` 校验。
- “全量”指当前规则下所有可发布样本，不等于收录全部原始 Charades-STA 句子。未入集的正例包含语义 holdout 后的训练样本、无法可靠规范化或不符合所选语义类别的样本；另隔离 3 条已发现的解析错误。数量见下文。
- 负例的视频不存在性依据数据负责人对本批候选的**统一复核确认**；没有逐 qid 复核表。`review_report.json` 如实记录此复核口径，不能将其表述成逐条双人审核。

## 版本与路径

- 正式数据目录：`/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v1`
- 正式训练、验证、测试：`train.jsonl`、`val.jsonl`、`test.jsonl`。所有纳入正式 split 的负例均依据数据负责人的统一复核确认。
- Action Genome 下载：`scripts/download_action_genome.py`；构建脚本：`scripts/build_semantic_existence.py`；复核导出：`scripts/review_semantic_existence.py`；打包：`scripts/package_semantic_existence.py`；校验：`scripts/validate_semantic_existence.py`、`scripts/validate_release.py`。
- 格式：每行一个 JSON，包含 GMR 字段 `qid`、`vid`、`query`、`duration`、`relevant_windows`，并保留 `video_id`、`exist_label`、`semantic_status`、`partition`、`novelty_type`、`construction_type`、`source_qid`、`semantic_graph`、`verification_status`。

## 原始数据和产生方法

1. 真实正例：`data/raw/charades_sta/charades_pos_train.jsonl`（12404 条）和 `data/raw/charades_sta/charades_pos_test.jsonl`（3720 条）。它们复制自已有 GMR `pos_only` 的 Charades-STA 导出；query 和时间窗保留原始标注。Charades 元数据来自 `downloads/Charades.zip`，展开到 `data/raw/charades/annotations/`，用于视频级动作冲突筛查。视频在 `downloads/Charades_v1_480.zip`，zip 内路径为 `Charades_v1_480/<video_id>.mp4`；正式包 5449 个不同视频 ID 中缺失 0 个。
   Action Genome 官方仓库 `https://github.com/JingweiJ/ActionGenome` 指向的标注已保存到 `data/raw/action_genome/annotations/`，包括 `object_bbox_and_relationship.pkl`、`person_bbox.pkl`、`frame_list.txt` 和类别表。构建器把场景图关系作为视频级正面冲突证据。相比未接入 AG 的上一版，移除 360 条潜在冲突候选，分 split 为 {'train': 265, 'val': 26, 'test': 69}。
   Action Genome 帧标注覆盖正式训练视频 3763/3770、验证视频 466/466、测试视频 1213/1213。移除条目及 qid 见 `data/audit/action_genome_removed_candidates.jsonl`；分 split 统计见 `data/audit/action_genome_conflict_report.json`。
2. 切分与语义清单：原测试视频保持测试；原训练视频按 SHA-256(video_id) 的前 10% 桶划验证。只用其余训练视频构建 `semantic_inventory.json`。动作 `open`、`close`（`shut` 归一为 `close`）和 16 个动作–物体组合被 hold out；含这些语义的训练正例移除。清单收录 105 个训练动作、261 个物体和 929 个动作–物体组合。
3. S+ / U+：从真实 Charades-STA 正例直接提取，沿用人工时间窗。训练清单已出现的组合标 S+；held-out 动作或指定 held-out 组合标 U+。
4. S− / U−：从同视频真实正例做一个语义边的改写。短语动作作为整体处理，例如 `take off → put on`；物体采用语义近邻。改写后的谓词、物体、角色和介词组合必须在另一条真实正例中出现，并通过重解析检查。同视频 Charades-STA、Charades 动作及可用 Action Genome 的正面证据用于排除冲突。根据训练清单标 S− 或 U−；只有视频复核判 `absent` 的测试候选进入正式测试集。
5. 匹配：`matched_u_pairs.jsonl` 只收录复核后同视频、同来源正例的 U+/U− 对。当前共 535 对。
   `test_matched_u.jsonl` 展开这些配对，每对两行，可直接用于核心 U+/U− 诊断；它是 `test.jsonl` 的子集。
6. 发布前 QC：解析器将部分 `dress in front of ...` 错取为 `dress|front`，因此从正式包隔离 3 条；qid 清单在 `statistics.json`。这属于语义解析错误，与视频复核结论无关。

原训练标注 12404 条，其中 11182 条原样本进入 downstream train 视频池，1222 条进入验证视频池。训练池删除 2679 条 holdout 正例，另有 1652 条因事件解析或语义清单资格不足未入正式训练；验证池有 228 条正例未入正式验证。原测试正例有 749 条未进入正式测试（包含发布前隔离的 3 条）。

## 数据文件及统计

| 文件 | 条数 | S+ | S− | U+ | U− |
|---|---:|---:|---:|---:|---:|
| `train.jsonl` | 8317 | 6851 | 1466 | 0 | 0 |
| `val.jsonl` | 1518 | 694 | 168 | 300 | 356 |
| `test.jsonl` | 4510 | 2090 | 592 | 881 | 947 |

| split | 象限 | 条数 | 视频数 | 平均 query 词数 | 平均视频秒数 |
|---|---|---:|---:|---:|---:|
| train | S+ | 6851 | 3770 | 6.66 | 31.514 |
| train | S- | 1466 | 1049 | 6.755 | 30.567 |
| val | S+ | 694 | 384 | 6.67 | 31.078 |
| val | S- | 168 | 117 | 6.506 | 29.229 |
| val | U+ | 300 | 190 | 5.513 | 31.526 |
| val | U- | 356 | 140 | 5.166 | 30.939 |
| test | S+ | 2090 | 1027 | 6.623 | 29.665 |
| test | S- | 592 | 372 | 6.605 | 30.203 |
| test | U+ | 881 | 505 | 5.531 | 30.176 |
| test | U- | 947 | 365 | 5.254 | 29.792 |

各文件的完整路径均为上面的正式数据目录加表内文件名。中间产物保存在 `/home/guoxiangyu/paper/Openword/data/processed/semantic_existence`：`semantic_inventory.json` 是仅由下游训练正例构建的清单，`removed_train_holdouts.jsonl` 是被排除的原训练正例，`*_candidates.jsonl` 是复核前四象限候选，`*_reviewed.jsonl` 是复核确认后的数据，`matched_u_pairs_reviewed.jsonl` 是复核后的配对，`audit.json` 是构建期审计。正式包中的同名清单和配对是交付副本。

### 数据流与逐项路径

| 数据 | 路径（相对项目根目录） | 如何产生 | 条数 |
|---|---|---|---:|
| 原始训练正例 | `data/raw/charades_sta/charades_pos_train.jsonl` | 复制已有 GMR Charades-STA positive 导出，保留人工 query 和时间窗 | 12404 |
| 原始测试正例 | `data/raw/charades_sta/charades_pos_test.jsonl` | 同上 | 3720 |
| 被 holdout 的训练正例 | `data/processed/semantic_existence/removed_train_holdouts.jsonl` | 在训练视频内按选定动作和组合移除，以建立 downstream train 清单 | 2679 |
| 训练候选 | `data/processed/semantic_existence/train_candidates.jsonl` | 合格真实 S+ 加同视频最小语义改写 S−；以已有正面证据排除冲突 | 8317 |
| 验证候选 | `data/processed/semantic_existence/val_candidates.jsonl` | 原训练视频独立切出验证；真实 S+/U+ 与改写 S−/U− | 1518 |
| 测试候选 | `data/processed/semantic_existence/test_candidates.jsonl` | 原测试视频的真实 S+/U+ 与改写 S−/U− | 4513 |
| 正式训练集 | `data/release/semantic_existence_v1/train.jsonl` | 复核确认后发布的训练候选 | 8317 |
| 正式验证集 | `data/release/semantic_existence_v1/val.jsonl` | 复核确认后发布的验证候选 | 1518 |
| 正式测试集 | `data/release/semantic_existence_v1/test.jsonl` | 复核确认后发布的测试候选，隔离 3 条解析错误 | 4510 |
| 同视频 U+/U− 配对 | `data/release/semantic_existence_v1/matched_u_pairs.jsonl` | 在已发布 U+/U− 中按同视频、同 source 正例匹配 | 535 对 |
| 配对展开集 | `data/release/semantic_existence_v1/test_matched_u.jsonl` | 每对展开成正负各一行，供配对评测 | 1070 |

`data/release/semantic_existence_v1/semantic_inventory.json` 记录训练语义、holdout 动作与组合；`statistics.json` 是逐象限统计；`manifest.json` 含输入及交付文件 SHA-256；`review_report.json` 是复核口径；`text_only_diagnostic.json` 是语言泄漏诊断。Action Genome 冲突移除的逐条记录在 `data/audit/action_genome_removed_candidates.jsonl`，汇总在 `data/audit/action_genome_conflict_report.json`。

完整统计见 `statistics.json`：每象限视频数、query 长度、视频时长、正例时间窗位置、负例来源窗口位置、novelty 类型、构造类型、动作和物体频次及复核状态。校验和见 `manifest.json`。

## 文件用途与限制

- 本次训练、验证和测试的负例均已进入正式 split；复核前候选仍保存在中间产物目录，便于追溯。
- `test.jsonl` 中的负例复核来源见 `review_report.json`；测试集须按 S+/S−/U+/U− 分别报告，特别是 U+ 错误拒绝率和 U− 拒绝率。
- Action Genome 标注当前已接入；场景图只覆盖采样帧，缺失图谱边不能证明事件不存在。
- 正例均为原始人工句子，负例均由最小编辑生成，存在文本来源与存在标签相关的风险。发表前需做文本单模态基线及语言风格平衡分析。
- 文本单模态诊断见 `text_only_diagnostic.json`。当前字符 n-gram 基线测试 AUC=0.7885，seen AUC=0.8889，unseen AUC=0.5678，U+/U− 同视频配对排序准确率=0.5421；这表明尤其 seen 子集仍有语言线索，发布论文时必须报告并做风格平衡。
- `review_report.json` 记录此次复核汇总：{"counts": {"S+": 2090, "U+": 884, "S-": 592, "U-": 947}, "reviewed_negatives": 1539, "matched_u_pairs": 535, "unreviewed_or_excluded_negatives": 0, "review_method": "dataset_owner_global_attestation", "review_record": "User stated all candidates passed review; no per-qid review file supplied", "other_reviewed_splits": {"train": {"S+": 6851, "S-": 1466}, "val": {"S+": 694, "U+": 300, "U-": 356, "S-": 168}}}。此次依据数据负责人对所有当前候选的统一确认，没有逐 qid 复核表。

## 重建与校验

在项目根目录运行：

```bash
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/download_action_genome.py
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/build_semantic_existence.py
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/validate_semantic_existence.py
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/review_semantic_existence.py --user-attests-all-absent
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/package_semantic_existence.py
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/audit_text_only.py
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/package_semantic_existence.py
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/validate_release.py
```

第四条命令只在数据负责人已经确认**当前构建得到的全部候选**通过复核时使用；如对数据进行了重新生成并出现新 qid，需要重新确认新候选。本次接入 Action Genome 后新 qid 为 0，原已确认候选的子集保留下来，详见 `data/audit/action_genome_conflict_report.json`。
