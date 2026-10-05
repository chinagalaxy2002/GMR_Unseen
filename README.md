# GMR Unseen: Semantic Novelty × Event Existence

**本项目研究：如何让视频检索模型将“事件是否发生”的判断泛化到未见语义，使其既能找出陌生但真实发生的事件，也能拒绝语义合理却没有发生的事件？** 例如，用户搜索“把杯子放进柜子”，即使模型在下游训练中没有见过这个动作组合，只要视频里发生了，就应该找到它；如果没有发生，即使杯子、柜子和相关动作都很熟悉，也应该拒绝返回片段。语义是否熟悉与事件是否发生是两个不同的问题。当前实验发现，模型在未见语义上既可能接受不存在的事件，也可能拒绝真实发生、甚至已经定位正确的事件，说明定位能力与存在判断能力未能同步泛化。因此，核心科学问题是：**未见语义下，事件存在判断与定位能力为何出现分离，以及如何使二者共同泛化。** 模型需要从有限的已见语义中学到能够迁移的视频—事件对应关系，并据此同时完成存在判断与时间定位；语义熟悉度是否干扰这一过程，仍是待验证的机制假设。

代码基于 [Generalized Moment Retrieval (GMR)](https://github.com/dymm9977/generalized-moment-retrieval) 扩展，包含 Charades-STA 派生的四象限数据集、构建与校验脚本，以及 Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR 的主实验。

> **状态：E0–E7 已完成。** 数据集 v1、三个 GMR backbone、三个定位-only 对照和三个 semantic-seen reference 都已有训练与测试结果。本仓库目前提供 benchmark、适配代码和诊断实验，尚未提出新模型。每个配置只运行一个种子；文中的 bootstrap 区间反映测试视频抽样，不代表跨训练种子的稳定性。

第二阶段五组划分的三模型训练和测试评测均已完成，发布数据通过 SHA-256 和视频切分校验。五组注释及选择记录见 [`data/release/semantic_existence_v2/`](data/release/semantic_existence_v2/)，完整划分方案见[第二阶段实验方案](docs/20260928_2_PHASE2_MULTI_SPLIT_EXPERIMENT_PLAN.md)，逐组指标及跨划分对照见[多划分结果报告](docs/reports/semantic_existence_multisplit_results.md)。

清空对话上下文后，只需从[项目总交接](docs/PROJECT_HANDOFF.md)恢复；它汇总研究问题、当前状态、关键结果、数据和代码入口，并标明其余文档的用途。

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

### Phase 2 multi-split releases

| Group | Held-out semantics | Axis | Train | Validation | Test | Test U+ / U− | Matched U pairs |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| [A1](data/release/semantic_existence_v2/A1/) | `put`, `take` | Action | 8,608 | 1,759 | 5,170 | 465 / 1,119 | 312 |
| [A2_alt](data/release/semantic_existence_v2/A2_alt/) | `drink`, `pour` | Action | 10,323 | 1,686 | 4,945 | 168 / 312 | 79 |
| [A3](data/release/semantic_existence_v2/A3/) | `run`, `walk` | Action | 10,352 | 1,774 | 5,293 | 192 / 594 | 129 |
| [C1](data/release/semantic_existence_v2/C1/) | `sit|bed`, `sit|chair`, `sit|couch` | Composition | 10,516 | 1,607 | 4,705 | 162 / 270 | 144 |
| [C2_alt](data/release/semantic_existence_v2/C2_alt/) | `close|box`, `close|cabinet`, `open|box`, `open|cabinet` | Composition | 10,612 | 1,607 | 4,705 | 115 / 254 | 33 |

All 15 training jobs completed with exit code 0; the three models were evaluated on all five test sets. A1–A3 use the same reviewed 1,500-row action-axis S− pool; C1/C2_alt use a separate shared 1,500-row composition-axis S− pool. The composition packages include their frozen specs and common negative pool. All five checked-in releases pass `scripts/validate_release.py`, with no video overlap across train, validation and test. The dataset owner attested review of the exact new-negative batch and parser sample as a whole; the packages do not contain per-query review records. Full construction provenance is in each release's manifest and the shared selection directory.

#### Phase 2 data construction: all five groups

1. **Select semantics before model testing.** [`profile_semantic_split_candidates.py`](scripts/profile_semantic_split_candidates.py) counts original train/test positives, videos and object diversity for 123 actions and 1,221 action–object compositions. [`select_semantic_split_specs.py`](scripts/select_semantic_split_specs.py) and the fallback-selection scripts use the frozen [`selection_rules.json`](data/release/semantic_existence_v2/selection/selection_rules.json) to choose disjoint action and composition groups. Initial A2 and C2 failed the candidate pair gate and were replaced by A2_alt and C2_alt before model evaluation. Candidate tables, failure records, final [`split_specs.json`](data/release/semantic_existence_v2/selection/split_specs.json) and the frozen selection hashes are published under [`selection/`](data/release/semantic_existence_v2/selection/).
2. **Build each split from the same original positives.** [`build_semantic_existence.py`](scripts/build_semantic_existence.py) reads one frozen `--split-spec` per group, retains original positive queries and human time windows, keeps original test videos in test, and assigns validation by a deterministic video-ID hash. For A groups it removes training positives containing a held action; for C groups it removes held action–object pairs while checking that their component action and object remain in training. Each group gets its own seen inventory and S+/U+ labels.
3. **Construct and review absent queries.** The builder edits an action or object edge in a same-video positive and can recombine a video action with another object. It reparses the query and discards candidates contradicted by same-video positives, Charades action annotations or Action Genome relationships. Those filters detect conflicts; absence depends on video review. The owner globally attested the exact batch of 4,491 new negative candidates and 156 parser-QC samples; 2,485 exact v1 negatives retain their earlier batch provenance. [`review_semantic_multisplit.py`](scripts/review_semantic_multisplit.py) records that distinction. The release does not contain per-qid review decisions. Known `dress|front` parser errors were quarantined before packaging.
4. **Reuse negatives and enforce release gates.** [`audit_shared_seen_negatives.py`](scripts/audit_shared_seen_negatives.py) forms one reviewed 1,500-row S− training pool shared by all A groups and another shared by both C groups. Each group's test U+/U− pairs use the same video and source positive and the same novelty axis. Before training, [`audit_multisplit_feasibility.py`](scripts/audit_multisplit_feasibility.py) checks at least 80 U+, 40 U−, 50 U+ videos, 20 pairs and 15% pair coverage; it also limits the largest held-semantic share to 70% for actions or 65% for compositions and requires at least 90% parser-QC correctness. [`package_semantic_multisplit.py`](scripts/package_semantic_multisplit.py) writes the five releases and SHA-256 manifests; [`validate_release.py`](scripts/validate_release.py) checks their labels, pairs, video separation, held-out leakage and checksums.

Every release contains `train.jsonl`, `val.jsonl`, `test.jsonl`, `matched_u_pairs.jsonl`, `test_matched_u.jsonl`, `semantic_inventory.json`, `statistics.json`, `review_report.json`, `split_spec_provenance.json` and `manifest.json`. The repository also publishes the frozen specs, candidate statistics, review attestation and both shared S− pools. Rebuilding from scratch additionally needs the original Charades-STA positives, Charades annotations/videos, Action Genome, VerbNet and parser dependencies; raw videos, pretrained feature tensors, checkpoints, per-query predictions and intermediate `work/` candidate files are not part of this release. The exact build protocol, dependency paths and selection rationale are in the [phase 2 plan](docs/20260928_2_PHASE2_MULTI_SPLIT_EXPERIMENT_PLAN.md).

To check the published annotation packages without rebuilding or downloading model features:

```bash
for split in A1 A2_alt A3 C1 C2_alt; do
  python scripts/validate_release.py --release "data/release/semantic_existence_v2/$split"
done
```

#### A1 data and construction

[`data/release/semantic_existence_v2/A1/`](data/release/semantic_existence_v2/A1/) holds out the complete `put` and `take` action classes from downstream training. The published files contain annotations and provenance, without videos, features, or checkpoints. Each test query is assigned by its semantic status under A1; the two actions have 226 and 239 U+ test examples respectively.

| A1 split | S+ | S− | U+ | U− | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train | 7,108 | 1,500 | 0 | 0 | 8,608 |
| Validation | 747 | 510 | 159 | 343 | 1,759 |
| Test | 2,218 | 1,368 | 465 | 1,119 | 5,170 |

A1 has 312 same-video, same-source U+/U− pairs, covering 67.1% of its U+ test rows. The 1,500 training S− rows are the reviewed **shared action-axis pool** used by A1, A2_alt and A3. The exact frozen A1 spec, selection rules, candidate action table, common negative pool, owner attestation and review templates are in [`selection/`](data/release/semantic_existence_v2/selection/). The owner attested review of the exact new-negative batch and parser sample as a whole; this is **not a per-query review log**. The 8 train and 3 test `dress|front` parser errors were quarantined before packaging. `review_report.json` counts are from before that quarantine; `statistics.json` contains final released counts.

The A1 construction pipeline starts from the original Charades-STA positives, uses the same video-level train/validation allocation as v1, and parses action–object events. [`profile_semantic_split_candidates.py`](scripts/profile_semantic_split_candidates.py) counts candidates; the frozen [`A1.json`](data/release/semantic_existence_v2/selection/A1.json) is passed as `--split-spec` to [`build_semantic_existence.py`](scripts/build_semantic_existence.py). It removes all training positives with `put` or `take` and labels test positives accordingly. The builder creates edited negative candidates and same-video pairs. [`review_semantic_multisplit.py`](scripts/review_semantic_multisplit.py) imports the owner's batch attestation, [`audit_multisplit_feasibility.py`](scripts/audit_multisplit_feasibility.py) checks the preset size, diversity and pair-coverage gates, and [`package_semantic_multisplit.py`](scripts/package_semantic_multisplit.py) packages the shared S− pool and final splits. The shared pool is reproduced and audited by [`audit_shared_seen_negatives.py`](scripts/audit_shared_seen_negatives.py). The other candidate splits, fallback selection, and parser QC are documented in the [phase 2 plan](docs/20260928_2_PHASE2_MULTI_SPLIT_EXPERIMENT_PLAN.md).

```bash
python scripts/validate_release.py --release data/release/semantic_existence_v2/A1
```

The A1 manifest records SHA-256 hashes of all packaged files and construction inputs. Paths in `manifest.json`, `review_report.json`, and `split_spec_provenance.json` refer to the original build machine; the published equivalents of the selection files are under `../selection/`.

To retrain A1 after obtaining the same Charades video features and compatible CLIP text encoder, prepare its query features and seen-only validation view, then launch the 100-epoch models. The script uses the v1 model settings with the A1 release and a distinct A1 result directory:

```bash
python scripts/prepare_charades_semantic_existence.py \
  --release data/release/semantic_existence_v2/A1 \
  --old-text /path/to/original_charades_clip_text \
  --clip-code /path/to/compatible_clip_implementation \
  --clip-weights /path/to/clip_vit_b32_weights \
  --output features/semantic_existence_v2/A1
export MULTISPLIT_RELEASE_ROOT="$PWD/data/release/semantic_existence_v2"
export VIDEO_ROOT=/path/to/charades/features
export GMR_PYTHON=/path/to/gmr-env/bin/python
export FLASH_PYTHON=/path/to/flash-env/bin/python
bash scripts/run_semantic_multisplit_100ep.sh A1 launch
# After all three exit_code files report 0:
bash scripts/finalize_semantic_multisplit_group.sh A1
```

The same feature preparation, training and test commands apply to A2_alt, A3, C1 and C2_alt by replacing `A1` with the chosen split ID. Each group trains independently; [`queue_semantic_multisplit_training.sh`](scripts/queue_semantic_multisplit_training.sh) records the original order and two-GPU scheduling, while [`finalize_semantic_multisplit_group.sh`](scripts/finalize_semantic_multisplit_group.sh) runs the three test submissions and diagnostics for one completed group. The published [result JSON files](docs/semantic_existence_v2_metrics/) include the seen-validation threshold, official metrics, text-only control, video-cluster intervals and same-query cross-split summaries.

### How the v1 dataset was constructed

1. Preserve original Charades-STA positive queries and human temporal windows. Keep original test videos in test; allocate 10% of original training videos to validation by a deterministic SHA-256 bucket of video ID. Splits do not share videos.
2. Build the downstream semantic inventory only from the remaining training videos. Hold out `open`, `close` (including normalized `shut`), and 16 selected action–object compositions. Remove training positives containing the held-out semantics. Label original positive queries as S+ or U+ according to this inventory.
3. Form negative candidates by editing one semantic event edge in a real same-video positive query. Candidate actions/objects must occur in real positive text elsewhere; the edited query is reparsed. Reject candidates contradicted by other same-video positives, Charades action annotations, or available Action Genome relationships. These filters provide **positive conflict evidence only**; their silence does not establish absence.
4. Review surviving negative candidates against the video. The v1 release records a **dataset-owner global attestation** for the reviewed batch, not a per-query or dual-review log. Confirmed negatives become S− or U−. Pair eligible U+ and U− queries by video and source positive. Quarantine three known parser errors before packaging.

发布统计中的 U+ 为 **881**；复核报告曾记录 **884**，其中 3 条 `dress|front` 解析错误在打包前被隔离。负例的元数据过滤只能发现与“缺席”相冲突的正证据，不能替代视频复核。需要逐条复核记录或更强的缺席证明时，应重新构建和审查数据，不能把本版的全局 attestation 解释成双人逐条标注。

Construction details and limitations are in [the dataset construction report](docs/reports/semantic_existence_dataset.md). Source scripts are [`scripts/build_semantic_existence.py`](scripts/build_semantic_existence.py), `validate_semantic_existence.py`, `review_semantic_existence.py`, `package_semantic_existence.py`, `audit_text_only.py`, and `validate_release.py`. The released JSONL files are ready to use without rebuilding the raw dataset.

To **rebuild** the dataset, supply the original Charades-STA positive JSONL files, Charades annotation CSVs and videos, VerbNet, spaCy `en_core_web_sm`, NLTK WordNet, and Action Genome annotations at the paths described in [the dataset construction report](docs/reports/semantic_existence_dataset.md). Install builder dependencies with `pip install -r requirements-dataset.txt`, then run:

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

E6 需要构建期中间文件 `data/processed/semantic_existence/removed_train_holdouts.jsonl`，其中有 2,679 条从正式训练中移除的原始正例；该文件不属于发布包，需要按[数据构建说明](docs/reports/semantic_existence_dataset.md)在本地重新生成。下例合并训练标注，并链接这些正例原有的 CLIP 文本特征。`OLD_TEXT_DIR` 中的文件名应为 `<qid>.npz`，与 `prepare_charades_semantic_existence.py --old-text` 使用的格式相同。

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

### Phase 2 A1 test results

All three A1 training jobs completed with exit code 0. The best checkpoint for each model was selected using only A1 seen validation rows; the existence threshold was calibrated on those same seen rows. The table uses A1's 5,170-query test set and 312 matched pairs. AUROC and PairAcc are unit fractions; all other columns are percentages.

| A1 model | Seen AUROC | Unseen AUROC | U+ false refusal | U− rejection | 312-pair accuracy | U+ raw R@1@0.5 | U+ gated R@1@0.5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Moment-DETR-GMR | 0.804 | 0.497 | 23.23% | 25.47% | 0.559 | 23.01% | 17.85% |
| QD-DETR-GMR | 0.783 | 0.506 | 16.13% | 18.23% | 0.572 | 24.52% | 20.65% |
| FlashVTG-GMR | 0.816 | 0.506 | 19.14% | 20.82% | 0.556 | 29.46% | 23.66% |

On this held-out `put/take` action split, seen AUROC exceeds unseen AUROC by 0.277–0.309. Matched-pair score ordering is 0.556–0.572. At the seen-calibrated threshold, U− rejection is only 18.23–25.47%, while gating removes 3.87–5.81 percentage points of U+ R@1@0.5. A1 uses one training seed. Full definitions, run settings and five-split comparisons are in the [phase 2 result report](docs/reports/semantic_existence_multisplit_results.md).

### Phase 2 A2_alt and A3 test results

Both groups completed test inference for all three best checkpoints. Each submission covers every test qid exactly once: 4,945 in A2_alt and 5,293 in A3. The existence threshold in each row comes only from that model's seen validation predictions. AUROC and PairAcc are unit fractions; FRR, RR and R@1@0.5 are percentages.

| Group | Model | Seen AUROC | Unseen AUROC | U+ FRR | U− RR | PairAcc | U+ raw R@1@0.5 | U+ gated R@1@0.5 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A2_alt (79 pairs) | Moment-DETR-GMR | 0.769 | 0.551 | 0.00% | 0.64% | 0.620 | 26.79% | 26.79% |
| A2_alt | QD-DETR-GMR | 0.744 | 0.473 | 0.60% | 0.32% | 0.456 | 31.55% | 31.55% |
| A2_alt | FlashVTG-GMR | 0.773 | 0.524 | 0.00% | 0.96% | 0.506 | 42.86% | 42.86% |
| A3 (129 pairs) | Moment-DETR-GMR | 0.749 | 0.564 | 29.17% | 33.00% | 0.469 | 39.58% | 28.12% |
| A3 | QD-DETR-GMR | 0.733 | 0.487 | 30.21% | 31.31% | 0.453 | 44.27% | 33.33% |
| A3 | FlashVTG-GMR | 0.742 | 0.614 | 23.44% | 43.77% | 0.516 | 46.88% | 34.38% |

All nine action-split models have lower unseen than seen AUROC. A2_alt's U− rejection is below 1% for every model, showing that its near-zero U+ refusal comes with almost universal acceptance of absent unseen queries. In A3, hard gating reduces U+ R@1@0.5 by 10.94–12.50 percentage points. Action same-query comparisons are summarized in the [action-split report](docs/reports/semantic_existence_action_multisplit_results.md).

### Phase 2 composition-split test results

| Group | Model | Seen AUROC | Unseen AUROC | U+ FRR | U− RR | PairAcc | U+ raw R@1@0.5 | U+ gated R@1@0.5 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C1 (144 pairs) | Moment-DETR-GMR | 0.761 | 0.562 | 3.70% | 7.78% | 0.629 | 48.77% | 47.53% |
| C1 | QD-DETR-GMR | 0.780 | 0.562 | 3.09% | 5.56% | 0.635 | 42.59% | 41.98% |
| C1 | FlashVTG-GMR | 0.753 | 0.548 | 3.70% | 3.70% | 0.556 | 51.23% | 48.77% |
| C2_alt (33 pairs) | Moment-DETR-GMR | 0.676 | 0.469 | 98.26% | 96.85% | 0.727 | 35.65% | 0.00% |
| C2_alt | QD-DETR-GMR | 0.698 | 0.545 | 47.83% | 53.94% | 0.530 | 38.26% | 24.35% |
| C2_alt | FlashVTG-GMR | 0.691 | 0.547 | 61.74% | 64.57% | 0.545 | 42.61% | 15.65% |

Seen AUROC exceeds unseen AUROC in all six composition-split runs. C1 shows modest AUROC gaps (0.199–0.218) with small U+ gate losses. C2_alt shows severe false refusal for Moment-DETR and larger gate losses for QD-DETR and FlashVTG. The exact [metric JSON outputs](docs/semantic_existence_v2_metrics/) include seen-validation thresholds and official full-test GMR scores.

The held-out object distribution is intentionally narrow for composition tests: C1 U+ uses three objects, and C2_alt U+ uses two. In A2_alt, `glass` and `cup` account for 72% of U+ queries. The text-only diagnostic also has high matched-pair accuracy in C1 (0.625) and C2_alt (0.818), indicating that query wording retains label signal; paired score accuracy must be interpreted with this confound in mind. See the per-split query length and action/object summaries in [`test_query_distributions.json`](docs/semantic_existence_v2_metrics/test_query_distributions.json) and text-only metrics in [`text_only/`](docs/semantic_existence_v2_metrics/text_only/).

The composition same-query comparison uses 801 directed comparisons, with 78–167 videos per split direction. For C2_alt→C1, the mean seen-minus-unseen existence score rises by 0.128–0.283 for present queries and 0.161–0.258 for absent queries across the models. For C1→C2_alt, present-query changes are near zero; absent-query changes range from −0.003 to +0.027. Video-cluster 95% intervals are in [`cross_status_composition/`](docs/semantic_existence_v2_metrics/cross_status_composition/); the [complete five-split report](docs/reports/semantic_existence_multisplit_results.md) discusses both action and composition axes. These are paired associations across separately trained models, not isolated causal effects. All configurations use one training seed.

### Phase 1 A0 test results

| Baseline | Seen existence AUROC | Unseen existence AUROC | U+ false-refusal rate | U− rejection rate | 535-pair score-order accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| Moment-DETR-GMR | 0.867 | 0.570 | 29.2% | 38.3% | 55.7% |
| QD-DETR-GMR | 0.871 | 0.585 | 63.8% | 80.7% | 48.4% |
| FlashVTG-GMR | 0.857 | 0.559 | 46.4% | 51.5% | 50.7% |

Existence discrimination drops sharply on held-out semantics for all three baselines. QD-DETR and FlashVTG frequently reject present U+ events; Moment-DETR accepts many absent U− events. The failure modes differ, so a single “over-refusal” explanation does not fit all models. Longer training with a different seed did not remove the observed gap, but changing the seed and epoch limit together does not isolate the effect of training duration. The best checkpoint was at epoch 11, 66, and 60 for Moment-DETR, QD-DETR, and FlashVTG respectively. Full raw-versus-gated localization, official GMR metrics, hashes, and the original shorter runs are in [the v1 100-epoch result report](docs/reports/semantic_existence_100ep_results.md) and the [handoff](docs/SEMANTIC_EXISTENCE_HANDOFF.md).

定位-only 对照和 E6 的重点结果如下；所有 R@1 使用 IoU 0.5，百分比取自固定 seed 3407 的测试集，完整区间与 checkpoint 核查见[定位对照报告](docs/reports/semantic_existence_localization_controls.md)和[E6 报告](docs/reports/semantic_existence_semantic_seen_reference_results.md)。

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

## 2026-09-30：未见动作的定位与存在判断收益反转

同一残差适配在正例VTG将未见R1@0.5从20.65%提高到26.24%，但在GMR中raw定位从26.02%下降到21.29%，AUROC从0.5309下降到0.4771。普通正则也未实现共同改善。机制尚未确定；下一阶段检查视觉利用、分数可比性和监督关系。

[实验介绍、结果、日志与复现入口](experiments/correspondence_generalization/2026年9月30日_正则化与残差适配的未见动作泛化实验/INTRODUCTION.md)。六组已完成，下一阶段仅制定计划。

## 2026-10-01：存在与定位共同泛化的全部机制诊断

三族训练侧诊断、候选排序/几何、支持桥接、冻结时序表示及匹配容量读出已完成。候选一致性未支持共同作用路径；给定GT的局部证据与无GT的跨查询绝对支持仍有缺口，未启动新全模型训练。

[完整实验记录、全部指标、冻结协议、逐轮账本、失败记录与源码](experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/EXPERIMENT_RECORD.md)。


## 2026-10-06：AC-Verifier 对齐校准、独立审计与 backbone 范围

本次更新发布 `experiments/agy_test/` 的实验代码、报告和小型指标文件。当前推荐入口是 [AC-Verifier 复现说明](experiments/agy_test/aligned_calibration_verifier/README.md)，结论以 [独立审计报告](experiments/agy_test/ac_audit_20261006/AC_AUDIT_REPORT.md) 为准；[实验索引](experiments/agy_test/README.md)区分当前结果与历史实验。

### 方法与五划分结果

AC-Verifier 在冻结的 QD-DETR-GMR 检测器输出上训练轻量适配器，加入 CLIP ViT-B/32 的整句 EOT 投影与候选/全局视频相似度，并减去固定训练视频参考相似度。训练仅使用 S+/S−，检查点与判定阈值仅由 Seen validation 选择；当前实验为 seed 3407。参考是单位化的训练视频平均向量，不具有自动成立的“无偏”保证。

| 设置 | Mean Seen AUROC | Mean Unseen AUROC | Seen−Unseen Gap | Mean matched PairAcc |
| --- | ---: | ---: | ---: | ---: |
| HQ 缓存完整 logit 基线 | 0.7511 | 0.5027 | 0.2484 | 0.5181 |
| P0：独立 Detector Adapter | 0.7535 | 0.5078 | 0.2456 | 0.5261 |
| P1：AC-Verifier | 0.7561 | 0.5188 | 0.2373 | 0.5331 |

五划分等权宏平均 Unseen AUROC 增益 **+1.61 pp**，Gap 缩小 **1.11 pp**。共享视频成对聚类 bootstrap（2,000 次）95% 区间分别为 **[+0.66, +2.66] pp**、**[+0.14, +2.15] pp**；Seen AUROC 同时提高约 0.50 pp。原始汇总见 [benchmark_summary.json](experiments/agy_test/aligned_calibration_verifier/benchmark_summary.json)，独立统计见 [bootstrap.json](experiments/agy_test/ac_audit_20261006/bootstrap.json)。

这支持当前五组、固定训练结果下的平均 AUROC 改善。收益主要集中于 C1；动作三划分及去掉 C1 的 AUROC/Gap 改善区间仍跨零。A2_alt、A3 的 Unseen AUROC 仍低于 0.5，多种子、新语义留出及完整 GMR 拒绝/定位改善尚待确认。固定查询的视频置换支持新增 CLIP 分支的视频对应贡献；将新增相似度置零仍保留检测器视觉输入，不能称为纯文本控制。

### 是否只有一个 backbone，是否支持迁移？

| 范围 | 当前状态 |
| --- | --- |
| 仓库 GMR 基线 | 已包含 Moment-DETR、QD-DETR、FlashVTG 三类模型与既有基线实验 |
| 本次 AC-Verifier 检测器 backbone | **仅验证 QD-DETR-GMR**；当前 `h_pool` 输入固定为 512 维（256 维 slot 的 max/mean 拼接） |
| 本次新增视觉/文本编码器 | CLIP ViT-B/32；当前 P1 不使用 SlowFast，动作/物体短语也不参与 P1 打分 |
| AC 迁移至 Moment-DETR / FlashVTG | 方法可适配，但尚未提供经过验证的统一多 backbone 接口或迁移结果 |

迁移需为目标检测器导出同一查询顺序的原始存在性 logit、前景分数、slot 表示与候选边界；适配 slot 维度、前景分数定义及时间坐标后，按同一 Seen-only 协议重新训练 P0/P1。应同时报告至少三个配对种子、逐 backbone 的 Unseen AUROC/Gap、拒绝阈值指标与定位结果。更换 CLIP 编码器也需重新提取一致的文本/视频投影，并重新计算训练参考，现有 512 维缓存不可直接复用。

### 代码、历史记录与复现资源

- 当前实现：[model.py](experiments/agy_test/aligned_calibration_verifier/model.py)、[特征提取](experiments/agy_test/aligned_calibration_verifier/extract_aligned_features.py)、[训练评估](experiments/agy_test/aligned_calibration_verifier/train_and_eval.py)。
- 独立复查：[audit_ac.py](experiments/agy_test/ac_audit_20261006/audit_ac.py)、[根因分析](experiments/agy_test/dao_root_cause_20261005/ROOT_CAUSE_REPORT.md)、[DAO 标签泄漏审计](experiments/agy_test/dao_audit_20261005/DAO_AUDIT_REPORT.md)。旧 DAO 的 0.6883 Unseen AUROC 已因输入标签泄漏失效，不能用作有效方法收益。
- GitHub 包含代码、文档、指标 JSON 与原始产物清单；HQ/CLIP 特征、模型权重、检查点、逐查询预测和大缓存保留本地。复跑需要这些输入，详细格式与环境变量见 [AC README](experiments/agy_test/aligned_calibration_verifier/README.md)。当前训练脚本保存 P1 checkpoint，不保存独立 P0 checkpoint 或逐查询预测；审计目录记录了补充复验产物。

准备好本地资源后，在仓库根目录执行：

```bash
python experiments/agy_test/aligned_calibration_verifier/extract_aligned_features.py
python experiments/agy_test/aligned_calibration_verifier/train_and_eval.py
```

本次发布在独立临时副本中完成，原实验工作区及训练产物保持原状。未重新训练或执行模型评测。
