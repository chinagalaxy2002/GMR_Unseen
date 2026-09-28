# GMR Unseen: Semantic Novelty × Event Existence

本项目研究广义视频时刻检索中的一个开放语义问题：查询描述的事件在下游训练中未见过时，模型能否判断它在视频中**真的不存在**，而不是仅仅因为语义陌生就拒绝查询？代码基于 [Generalized Moment Retrieval (GMR)](https://github.com/dymm9977/generalized-moment-retrieval) 扩展，包含 Charades-STA 派生的四象限数据集、构建与校验脚本，以及 Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR 的主实验。

> **状态：E0–E7 已完成。** 数据集 v1、三个 GMR backbone、三个定位-only 对照和三个 semantic-seen reference 都已有训练与测试结果。本仓库目前提供 benchmark、适配代码和诊断实验，尚未提出新模型。每个配置只运行一个种子；文中的 bootstrap 区间反映测试视频抽样，不代表跨训练种子的稳定性。

阅读顺序：[数据集构建与限制](docs/semantic_existence_dataset.md) → [E0–E7 实验方案](data/release/semantic_existence_v1/plan.md) → [严格 GMR 结果](docs/semantic_existence_100ep_results.md) → [定位对照](docs/semantic_existence_localization_controls.md) → [semantic-seen reference](docs/semantic_existence_semantic_seen_reference_results.md)。

## Research question and protocol

An event can be absent from a video, or present while its action or action–object composition was absent from **task-specific training**. Here, *unseen* means held out from downstream model training. It does **not** mean unseen by the pretrained CLIP or SlowFast feature extractors.

| Partition | Semantics in downstream training? | Event in video? | Expected output |
| --- | --- | --- | --- |
| S+ | Seen | Present | Relevant time window(s) |
| S− | Seen | Absent | Empty set |
| U+ | Unseen | Present | Relevant time window(s) |
| U− | Unseen | Absent | Empty set |

Models train on **S+ and S− only**. Checkpoint selection and existence-threshold calibration use only S+/S− validation rows. The test set contains all four partitions. Held-out U+/U− validation rows must not be used to select models, thresholds, or hyperparameters. Training on the original, unfiltered Charades-STA training split would invalidate the downstream-unseen condition.

The main diagnostic asks whether the existence score of a same-video U+ query exceeds that of its matched U− query. We also compare localization from the same checkpoint before and after applying the seen-validation existence threshold; this separates localization ability from erroneous refusal.

### E0–E7 实验矩阵

| 实验 | 模型／分析 | 训练数据 | 验证与测试 | 状态 |
| --- | --- | --- | --- | --- |
| E0 | Moment-DETR 定位-only | S+ | val S+ 选模；test S+/U+ 定位 | 完成 |
| E1 | FlashVTG 定位-only；另补 QD-DETR | S+ | 同 E0 | 完成 |
| E2 | Moment-DETR-GMR | S+、S− | val seen 选模与校准；test 四象限 | 完成 |
| E3 | FlashVTG-GMR；另补 QD-DETR-GMR | S+、S− | 同 E2 | 完成 |
| E4–E5 | E2/E3 checkpoint 的 raw 与硬拒绝定位；另补 QD-DETR | 沿用 GMR checkpoint | 同一 test 正例，比较关闭／启用 seen 阈值硬拒绝 | 完成 |
| E6 | 三 backbone 的 semantic-seen reference | S+、S−，加回 2,679 条 held-out 训练正例 | val seen 选模与校准；同一 test | 完成；**仅作泄漏语义诊断** |
| E7 | 字符 n-gram text-only 对照 | train 查询文本 | full test、unseen test、535 对 matched-U | 完成 |

原方案将 E0/E1 和 E2/E3 分别列为两个主 backbone；本项目按同一协议增加了 QD-DETR。主实验的 *unseen* 只表示相应语义未出现在**下游任务训练**中，不意味着 CLIP/SlowFast 的基础预训练从未接触相关概念。E6 故意违反严格 unseen 条件，不能并入主表作为 zero-shot baseline。

## Released dataset

The versioned release is in [`data/release/semantic_existence_v1/`](data/release/semantic_existence_v1/). Its GMR-style JSONL files include `qid`, `vid`, `query`, `duration`, and `relevant_windows`, plus `exist_label`, `partition`, `semantic_status`, `novelty_type`, `construction_type`, `source_qid`, `semantic_graph`, and `verification_status`. Positive rows retain annotated temporal windows; negative rows have `relevant_windows: []`.

| Split | S+ | S− | U+ | U− | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train | 6,851 | 1,466 | 0 | 0 | 8,317 |
| Validation | 694 | 168 | 300 | 356 | 1,518 |
| Test | 2,090 | 592 | 881 | 947 | 4,510 |

`matched_u_pairs.jsonl` contains 535 same-video U+/U− pairs with the same source positive. `test_matched_u.jsonl` expands these pairs into 1,070 rows. `semantic_inventory.json`, `statistics.json`, `review_report.json`, `text_only_diagnostic.json`, and `manifest.json` record the holdouts, statistics, review provenance, language-only diagnostic, and SHA-256 checksums. [`plan.md`](data/release/semantic_existence_v1/plan.md) is the experiment plan; [`HANDOFF.md`](data/release/semantic_existence_v1/HANDOFF.md) describes the original construction workspace. Absolute paths in that historical handoff refer to the original machine; use repository-relative paths here.

直接检查仓库内发布包，无须下载视频或训练特征：

```bash
python scripts/validate_release.py
```

The release contains **annotations, not videos or pretrained features**. Obtain Charades-STA/Charades videos and CLIP/SlowFast features under their source terms. The original GMR Soccer-GMR data in this upstream-derived repository is a separate benchmark and is not used for the experiments reported below.

### How the dataset was constructed

1. Preserve original Charades-STA positive queries and human temporal windows. Keep original test videos in test; allocate 10% of original training videos to validation by a deterministic SHA-256 bucket of video ID. Splits do not share videos.
2. Build the downstream semantic inventory only from the remaining training videos. Hold out `open`, `close` (including normalized `shut`), and 16 selected action–object compositions. Remove training positives containing the held-out semantics. Label original positive queries as S+ or U+ according to this inventory.
3. Form negative candidates by editing one semantic event edge in a real same-video positive query. Candidate actions/objects must occur in real positive text elsewhere; the edited query is reparsed. Reject candidates contradicted by other same-video positives, Charades action annotations, or available Action Genome relationships. These filters provide **positive conflict evidence only**; their silence does not establish absence.
4. Review surviving negative candidates against the video. The v1 release records a **dataset-owner global attestation** for the reviewed batch, not a per-query or dual-review log. Confirmed negatives become S− or U−. Pair eligible U+ and U− queries by video and source positive. Quarantine three known parser errors before packaging.

发布统计中的 U+ 为 **881**；复核报告曾记录 **884**，其中 3 条 `dress|front` 解析错误在打包前被隔离。负例的元数据过滤只能发现与“缺席”相冲突的正证据，不能替代视频复核。需要逐条复核记录或更强的缺席证明时，应重新构建和审查数据，不能把本版的全局 attestation 解释成双人逐条标注。

Construction details and limitations are in [`docs/semantic_existence_dataset.md`](docs/semantic_existence_dataset.md). Source scripts are [`scripts/build_semantic_existence.py`](scripts/build_semantic_existence.py), `validate_semantic_existence.py`, `review_semantic_existence.py`, `package_semantic_existence.py`, `audit_text_only.py`, and `validate_release.py`. The released JSONL files are ready to use without rebuilding the raw dataset.

To **rebuild** the dataset, supply the original Charades-STA positive JSONL files, Charades annotation CSVs and videos, VerbNet, spaCy `en_core_web_sm`, NLTK WordNet, and Action Genome annotations at the paths described in [`docs/semantic_existence_dataset.md`](docs/semantic_existence_dataset.md). Install builder dependencies with `pip install -r requirements-dataset.txt`, then run:

```bash
python -m spacy download en_core_web_sm
python -m nltk.downloader wordnet
python scripts/download_action_genome.py
python scripts/build_semantic_existence.py
python scripts/validate_semantic_existence.py
python scripts/review_semantic_existence.py --reviews path/to/completed_reviews.csv
python scripts/package_semantic_existence.py
python scripts/audit_text_only.py
python scripts/package_semantic_existence.py
python scripts/validate_release.py
```

The review command requires actual review decisions for a new build. The historical `--user-attests-all-absent` route must only be used when the dataset owner has already verified **that exact candidate batch**. To validate the unchanged included release, run only `python scripts/validate_release.py`.

## Code and environment

| Path | Purpose |
| --- | --- |
| `models/moment_detr_gmr/`, `training/moment_detr_gmr/` | Moment-DETR with GMR existence branch |
| `models/qd_detr_gmr/`, `training/qd_detr_gmr/` | QD-DETR adaptation with GMR existence branch |
| `models/flash_vtg_gmr/`, `training/flash_vtg_gmr/` | FlashVTG with GMR existence branch |
| `configs/` | Model, feature, and dataset configuration |
| `scripts/prepare_charades_semantic_existence.py` | Seen-only validation view and query CLIP features |
| `scripts/run_semantic_existence_100ep_tmux.sh` | Three 100-epoch runs with seed 3407 and no early stopping |
| `scripts/analyze_semantic_existence.py`, `eval/` | Four-partition diagnostics and GMR metrics |
| `scripts/run_semantic_localization_controls.sh`, `scripts/finalize_semantic_localization_controls.sh` | E0/E1 与 QD-DETR 的 S+ 定位训练、测试及评分 |
| `scripts/schedule_semantic_seen_references.sh`, `scripts/finalize_semantic_seen_references.sh` | E6 三 backbone 训练与自动测试；`start` 立即运行 |
| `scripts/analyze_localization_decomposition.py`, `scripts/compare_semantic_seen_reference.py` | raw／硬拒绝定位拆解和 E6 对比 |
| `scripts/audit_text_only.py`, `scripts/analyze_text_only_pair_uncertainty.py` | E7 文本-only 诊断与配对不确定性分析 |
| `docs/` | 数据构建、实验交接、完整结果与限制 |

Install the base dependencies with `pip install -r requirements.txt`. FlashVTG also has [`requirements-flash-vtg.txt`](requirements-flash-vtg.txt); a CUDA-compatible PyTorch installation is needed for GPU training. The recorded runs used separate `gmr` and `univtg` Python environments. Precomputed **CLIP text** features and **CLIP + SlowFast video** features are required and are not committed. In the recorded setup, video feature files have approximately one-second temporal resolution, CLIP video dimension 512, SlowFast dimension 2304, and `max_v_l=200`.

Prepare `features/charades_semantic_existence/val_seen.jsonl` and query features with:

```bash
python scripts/prepare_charades_semantic_existence.py \
  --release data/release/semantic_existence_v1 \
  --old-text /path/to/original_charades_clip_text \
  --clip-code /path/to/compatible_clip_implementation \
  --clip-weights /path/to/clip_vit_b32_weights \
  --output features/charades_semantic_existence
```

`--old-text` must contain the original positive-query features. The script symlinks those features and encodes negative queries; it expects a compatible CLIP implementation whose text encoder returns `last_hidden_state`. Check that all 14,345 released queries have a text feature before training. Set `VIDEO_ROOT` to a directory containing `vid_clip/` and `vid_slowfast/` feature subdirectories.

To reproduce the **three parallel, forced 100-epoch** runs on two GPUs:

```bash
export VIDEO_ROOT=/path/to/charades/features
export GMR_PYTHON=/path/to/gmr-env/bin/python
export FLASH_PYTHON=/path/to/flash-env/bin/python
bash scripts/run_semantic_existence_100ep_tmux.sh launch
```

Moment-DETR and QD-DETR share GPU 0; FlashVTG uses GPU 1. Override `DATA_ROOT`, `FEATURE_ROOT`, `RUN_ROOT`, or `SEMANTIC_SEED` when needed. The script writes `exit_code` and `run_metadata.txt` under `results/semantic_existence/seed3407_100ep/{moment,qd,flash}/`. It is a training launcher, so check for existing results before rerunning. Model-specific inference and scoring commands are in the [experiment handoff](docs/SEMANTIC_EXISTENCE_HANDOFF.md). `results/` and `features/` are local artifacts excluded from Git.

GitHub 发布的是标注、源代码和含数字的实验报告；模型 checkpoint、逐查询预测、原视频及特征文件不随仓库上传。报告里以 `results/` 开头的路径指本地复现产物，不是 GitHub 下载链接。

### 复现 E0/E1 与 QD-DETR 定位对照

在准备好上述特征后，设置 `VIDEO_ROOT`、`GMR_PYTHON` 和 `FLASH_PYTHON`，运行：

```bash
bash scripts/run_semantic_localization_controls.sh launch
```

该脚本从发布包生成仅含 S+ 的训练与验证视图，Moment-DETR 和 QD-DETR 在 GPU 0 顺序训练，FlashVTG 在 GPU 1 训练。三组 `exit_code` 均为 `0` 后执行：

```bash
bash scripts/finalize_semantic_localization_controls.sh
```

输出位于 `results/semantic_existence/localization_only_seed3407_100ep/`。代码默认的本机路径可通过 `VIDEO_ROOT`、`GMR_PYTHON`、`FLASH_PYTHON`、`FEATURE_ROOT` 和 `RUN_ROOT` 环境变量覆盖；公共复现时不要直接使用其他机器上的绝对路径。

### 复现 E6 semantic-seen reference

E6 需要构建期中间文件 `data/processed/semantic_existence/removed_train_holdouts.jsonl`，其中有 2,679 条从正式训练中移除的原始正例；该文件不属于发布包，需要按[数据构建说明](docs/semantic_existence_dataset.md)在本地重新生成。下例合并训练标注，并链接这些正例原有的 CLIP 文本特征。`OLD_TEXT_DIR` 中的文件名应为 `<qid>.npz`，与 `prepare_charades_semantic_existence.py --old-text` 使用的格式相同。

```bash
export HOLDOUTS=data/processed/semantic_existence/removed_train_holdouts.jsonl
export OLD_TEXT_DIR=/path/to/original_charades_clip_text
python - <<'PY'
import json, os
from pathlib import Path

release = Path('data/release/semantic_existence_v1/train.jsonl')
holdouts = Path(os.environ['HOLDOUTS'])
feature_root = Path('features/charades_semantic_existence')
text_dir = feature_root / 'clip_text'
old_text = Path(os.environ['OLD_TEXT_DIR'])
text_dir.mkdir(parents=True, exist_ok=True)
rows = [json.loads(line) for path in (release, holdouts) for line in path.open()]
assert len(rows) == 10996 and len({str(row['qid']) for row in rows}) == 10996
for row in (json.loads(line) for line in holdouts.open()):
    source = (old_text / f"{row['qid']}.npz").resolve(strict=True)
    target = text_dir / f"qid{row['qid']}.npz"
    if not target.exists():
        target.symlink_to(source)
with (feature_root / 'train_semantic_seen_reference.jsonl').open('w') as out:
    for row in rows:
        out.write(json.dumps(row, ensure_ascii=False) + '\n')
PY
```

训练脚本会检查合并文件必须有 10,996 个互异 qid、9,530 条正例及完整文本特征。

```bash
# 准备好合并文件与特征后，在两块 GPU 上启动三个单种子模型：
bash scripts/schedule_semantic_seen_references.sh start
```

`start` 会立即并行训练三个模型，并启动完成后的测试、四象限诊断、官方 GMR 评分和严格训练对照。`schedule` 子命令用于定时启动，默认时间是历史实验日期；复现时应显式设置新的 `TARGET_UTC`。E6 的训练集包含 held-out 正例，故结果仅是 semantic-seen reference。

### 评测文件与指标

预测 JSONL 的 `pred_relevant_windows` 为模型输出窗口，`pred_exist_score` 为存在分数；GMR 预测还保留 `pred_relevant_windows_pre_exist` 供 raw 定位诊断。[`eval/eval_main.py`](eval/eval_main.py) 计算官方 AUROC、Rej-F1、mAP、mR、mIoU 和 G-mIoU；[`scripts/analyze_semantic_existence.py`](scripts/analyze_semantic_existence.py) 计算 seen/unseen AUROC、四象限 FRR/RR、raw 与 seen 阈值硬拒绝后的 R@1@IoU 0.5，以及 matched-U PairAcc。两套阈值和 gate 定义不同，报告时不能混用。阈值和 checkpoint 只由 seen validation 决定，test 仅用于最终报告。

## Current results

All numbers below use the new seed **3407**, 100 epochs without early stopping, best checkpoint selected on seen validation, and thresholds calibrated on seen validation. These are **test-set diagnostics**, not model-selection criteria.

| Baseline | Seen existence AUROC | Unseen existence AUROC | U+ false-refusal rate | U− rejection rate | 535-pair score-order accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| Moment-DETR-GMR | 0.867 | 0.570 | 29.2% | 38.3% | 55.7% |
| QD-DETR-GMR | 0.871 | 0.585 | 63.8% | 80.7% | 48.4% |
| FlashVTG-GMR | 0.857 | 0.559 | 46.4% | 51.5% | 50.7% |

Existence discrimination drops sharply on held-out semantics for all three baselines. QD-DETR and FlashVTG frequently reject present U+ events; Moment-DETR accepts many absent U− events. The failure modes differ, so a single “over-refusal” explanation does not fit all models. Longer training with a different seed did not remove the observed gap, but changing the seed and epoch limit together does not isolate the effect of training duration. The best checkpoint was at epoch 11, 66, and 60 for Moment-DETR, QD-DETR, and FlashVTG respectively. Full raw-versus-gated localization, official GMR metrics, hashes, and the original shorter runs are in [`docs/semantic_existence_100ep_results.md`](docs/semantic_existence_100ep_results.md) and the [handoff](docs/SEMANTIC_EXISTENCE_HANDOFF.md).

定位-only 对照和 E6 的重点结果如下；所有 R@1 使用 IoU 0.5，百分比取自固定 seed 3407 的测试集，完整区间与 checkpoint 核查见[定位对照报告](docs/semantic_existence_localization_controls.md)和[E6 报告](docs/semantic_existence_semantic_seen_reference_results.md)。

| Backbone | 定位-only U+ R@1 | 严格 GMR raw U+ R@1 | 严格 GMR 硬拒绝后 U+ R@1 | E6 U+ FRR | E6 U− RR | E6 matched PairAcc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Moment-DETR | 35.07% | 32.92% | 24.40% | 3.63% | 3.27% | 57.48% |
| QD-DETR | 34.85% | 30.65% | 11.80% | 3.41% | 4.33% | 70.37% |
| FlashVTG | 44.27% | 37.34% | 20.32% | 2.50% | 2.64% | 52.15% |

E6 让模型几乎都接受 U+，同时也几乎都接受 U−。QD-DETR 在 matched-U 上的排序虽从 48.41% 升至 70.37%，seen 阈值下的 U− 拒绝率仍只有 4.33%。因此 E6 不能解释为开放语义存在判断已经解决；它还增加了训练正例，不能单独识别语义新颖性的因果效应。E7 的 text-only 模型在完整 test 上 AUROC 为 0.7885，在 unseen 上为 0.5678；535 对 matched-U 的 PairAcc 为 0.5421，按视频聚类的 95% 区间为 0.4925–0.5928。

**Known limits:** each configuration has only one run per seed. Original human positives and minimally edited negatives can differ in textual style. The included text-only diagnostic reaches 0.789 overall AUROC and 0.568 unseen AUROC, so overall scores alone should not be interpreted as purely visual existence reasoning. The release review provenance is a global owner attestation, not per-query review records.

## Upstream attribution

This project extends the [Generalized Moment Retrieval repository](https://github.com/dymm9977/generalized-moment-retrieval) for semantic-novelty experiments. Its original benchmark, code, and paper remain attributable to the upstream authors. The upstream citation is:

```bibtex
@article{ding2026retrieving,
  title={Retrieving Any Relevant Moments: Benchmark and Models for Generalized Moment Retrieval},
  author={Ding, Yiming and Cao, Siyu and Jiao, Luyuan and Li, Yixuan and Wang, Zitong and Liu, Zhiyong and Zhang, Lu},
  journal={arXiv preprint arXiv:2605.02623},
  year={2026},
  doi={10.48550/arXiv.2605.02623}
}
```

The repository's [`LICENSE`](LICENSE) applies to its software; third-party dataset and model assets retain their own source terms. See the FlashVTG [third-party notices](models/flash_vtg_gmr/THIRD_PARTY_NOTICES.md).

## Test 子集：未见动作与未见组合

发布版 test 中的 U+/U− 样本按 `novelty_type` 分为互不重叠的 `unseen_action` 和 `unseen_composition`。前者再按 `semantic_graph.action` 分为 `open`、`close`；后者按 `semantic_graph.action|semantic_graph.object` 分为 16 个预留的动作–物体组合。拆分文件保留原始 JSONL 记录和顺序，不改变原始 [`test.jsonl`](data/release/semantic_existence_v1/test.jsonl)。

| 子集 | U+ | U− | 合计 |
| --- | ---: | ---: | ---: |
| unseen_action | 675 | 882 | 1,557 |
| └ open | 442 | 439 | 881 |
| └ close | 233 | 443 | 676 |
| unseen_composition | 206 | 65 | 271 |

| Held-out pair | U+ | U− | Held-out pair | U+ | U− |
| --- | ---: | ---: | --- | ---: | ---: |
| `cook|food` | 5 | 0 | `dress|front` | 0 | 0 |
| `drink|water` | 9 | 1 | `eat|food` | 56 | 0 |
| `hold|pillow` | 10 | 0 | `put_down|book` | 15 | 4 |
| `put_in|box` | 6 | 5 | `put_in|clothe` | 7 | 2 |
| `put_on|shoe` | 40 | 22 | `put|picture` | 9 | 14 |
| `put|towel` | 13 | 0 | `take_out|book` | 3 | 1 |
| `take_out|towel` | 3 | 0 | `take|bag` | 8 | 0 |
| `take|book` | 13 | 16 | `walk|room` | 9 | 0 |

可直接读取 [`test_subgroups/views/`](data/release/semantic_existence_v1/test_subgroups/views/) 中的 JSONL 子集；[`counts.csv`](data/release/semantic_existence_v1/test_subgroups/counts.csv) 给出各组数量，[`metrics.csv`](data/release/semantic_existence_v1/test_subgroups/metrics.csv) 给出 Moment-DETR、QD-DETR、FlashVTG 在 strict GMR、semantic-seen reference 和 localization-only 设置下的分组指标。指标定义及空值说明见[子集说明](data/release/semantic_existence_v1/test_subgroups/README.md)。

535 个 matched-U pair 全部属于 `unseen_action`。按**正例 query 的动作**分组时，`open` 有 352 对，`close` 有 183 对；各模型的 PairAcc 见 [`matched_pair_metrics.csv`](data/release/semantic_existence_v1/test_subgroups/matched_pair_metrics.csv)。`unseen_composition` 没有 matched pair，故没有该组的 PairAcc。`dress|front` 在最终 test 中为零条；部分其他 held-out pair 缺少 U− 或样本很少，不能对这些 pair 的 AUROC 作稳定比较。
