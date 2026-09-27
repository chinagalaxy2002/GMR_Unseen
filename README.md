# GMR Unseen: Semantic Novelty × Event Existence

本项目研究广义视频时刻检索中的一个开放语义问题：查询描述的事件在下游训练中未见过时，模型能否判断它在视频中**真的不存在**，而不是仅仅因为语义陌生就拒绝查询？代码基于 [Generalized Moment Retrieval (GMR)](https://github.com/dymm9977/generalized-moment-retrieval) 扩展，包含 Charades-STA 派生的四象限数据集、构建与校验脚本，以及 Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR 的主实验。

> **Status:** Dataset v1 and three baseline experiments are complete. This repository does not yet introduce a new model. Results are diagnostic observations from single runs, not estimates of statistical significance.

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

## Released dataset

The versioned release is in [`data/release/semantic_existence_v1/`](data/release/semantic_existence_v1/). Its GMR-style JSONL files include `qid`, `vid`, `query`, `duration`, and `relevant_windows`, plus `exist_label`, `partition`, `semantic_status`, `novelty_type`, `construction_type`, `source_qid`, `semantic_graph`, and `verification_status`. Positive rows retain annotated temporal windows; negative rows have `relevant_windows: []`.

| Split | S+ | S− | U+ | U− | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train | 6,851 | 1,466 | 0 | 0 | 8,317 |
| Validation | 694 | 168 | 300 | 356 | 1,518 |
| Test | 2,090 | 592 | 881 | 947 | 4,510 |

`matched_u_pairs.jsonl` contains 535 same-video U+/U− pairs with the same source positive. `test_matched_u.jsonl` expands these pairs into 1,070 rows. `semantic_inventory.json`, `statistics.json`, `review_report.json`, `text_only_diagnostic.json`, and `manifest.json` record the holdouts, statistics, review provenance, language-only diagnostic, and SHA-256 checksums. [`plan.md`](data/release/semantic_existence_v1/plan.md) is the experiment plan; [`HANDOFF.md`](data/release/semantic_existence_v1/HANDOFF.md) describes the original construction workspace. Absolute paths in that historical handoff refer to the original machine; use repository-relative paths here.

The release contains **annotations, not videos or pretrained features**. Obtain Charades-STA/Charades videos and CLIP/SlowFast features under their source terms. The original GMR Soccer-GMR data in this upstream-derived repository is a separate benchmark and is not used for the experiments reported below.

### How the dataset was constructed

1. Preserve original Charades-STA positive queries and human temporal windows. Keep original test videos in test; allocate 10% of original training videos to validation by a deterministic SHA-256 bucket of video ID. Splits do not share videos.
2. Build the downstream semantic inventory only from the remaining training videos. Hold out `open`, `close` (including normalized `shut`), and 16 selected action–object compositions. Remove training positives containing the held-out semantics. Label original positive queries as S+ or U+ according to this inventory.
3. Form negative candidates by editing one semantic event edge in a real same-video positive query. Candidate actions/objects must occur in real positive text elsewhere; the edited query is reparsed. Reject candidates contradicted by other same-video positives, Charades action annotations, or available Action Genome relationships. These filters provide **positive conflict evidence only**; their silence does not establish absence.
4. Review surviving negative candidates against the video. The v1 release records a **dataset-owner global attestation** for the reviewed batch, not a per-query or dual-review log. Confirmed negatives become S− or U−. Pair eligible U+ and U− queries by video and source positive. Quarantine three known parser errors before packaging.

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
| `docs/SEMANTIC_EXISTENCE_HANDOFF.md`, `docs/semantic_existence_100ep_results.md` | Experiment records, commands, checkpoints, and detailed results |

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

## Current results

All numbers below use the new seed **3407**, 100 epochs without early stopping, best checkpoint selected on seen validation, and thresholds calibrated on seen validation. These are **test-set diagnostics**, not model-selection criteria.

| Baseline | Seen existence AUROC | Unseen existence AUROC | U+ false-refusal rate | U− rejection rate | 535-pair score-order accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| Moment-DETR-GMR | 0.867 | 0.570 | 29.2% | 38.3% | 55.7% |
| QD-DETR-GMR | 0.871 | 0.585 | 63.8% | 80.7% | 48.4% |
| FlashVTG-GMR | 0.857 | 0.559 | 46.4% | 51.5% | 50.7% |

Existence discrimination drops sharply on held-out semantics for all three baselines. QD-DETR and FlashVTG frequently reject present U+ events; Moment-DETR accepts many absent U− events. The failure modes differ, so a single “over-refusal” explanation does not fit all models. Longer training with a different seed did not remove the observed gap, but changing the seed and epoch limit together does not isolate the effect of training duration. The best checkpoint was at epoch 11, 66, and 60 for Moment-DETR, QD-DETR, and FlashVTG respectively. Full raw-versus-gated localization, official GMR metrics, hashes, and the original shorter runs are in [`docs/semantic_existence_100ep_results.md`](docs/semantic_existence_100ep_results.md) and the [handoff](docs/SEMANTIC_EXISTENCE_HANDOFF.md).

**Known limits:** each configuration has only one run per seed; localization-only and semantic-oracle controls are still pending. Original human positives and minimally edited negatives can differ in textual style. The included text-only diagnostic reaches 0.789 overall AUROC and 0.568 unseen AUROC, so overall scores alone should not be interpreted as purely visual existence reasoning. The release review provenance is a global owner attestation, not per-query review records.

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
