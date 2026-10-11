# C3_CG v2 frozen-baseline re-evaluation

**Status: complete.** 3/3 models evaluated, independent numerical verification PASS, original report replaced with v2 and old report archived. See `progress.json`, `PUBLICATION_REFRESH_STATUS.json`, `LOCAL_VERIFICATION_INDEPENDENT.json` and `VISUAL_REVIEW.json`.

User requested evaluation on the latest Seen+Unseen v2 dataset and replacement of the original report. This directory contains inference/evaluation only; no training or test tuning.

Entry point: `run_baselines.py`, executed with `/home/guoxiangyu/miniconda3/envs/univtg/bin/python`. Progress: `QUEUE_STATUS.json`, `queue.log`, per-model `groups/C3_CG/runs/*/inference.log`. Final gate: `FINAL_EVALUATION_STATUS.json` and `PIPELINE_EXIT.json`, then independent verification.

Inputs: immutable `data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2`. Frozen annotations copied under `groups/C3_CG/release/C3_CG`. Checkpoints/Seen validation predictions/native source reused from `../charades_cg_baselines_20261010`; verify original manifests and copy thresholds unchanged. Text features are matched by exact-query SHA256 from the original and balanced baselines; only missing token-state features are encoded using the identical CLIP encoder. All backbones use the same verified features.

Test has S+/S− each 2,684 and U+/U− each 2,990. Both negative groups were regenerated. Infer all 11,348 rows; do not mix old v1 negative predictions. Compute actual rejection F1 and native top-1 set-IoU G-mIoU. Joint target-video-cluster bootstrap: 2,000 draws, seed 3407, same sorted full test-video universe for both subsets and all backbones; preserve negative gaps.

Outputs: per-backbone native/standardized predictions, frozen calibration, point metrics, raw bootstrap draws and intervals; aggregate `evaluation/`. Report refresh: `refresh_publication.py` (owned by report agent), replace `../publication_review_20261011/charades_cg/` and its parent index only after complete 3/3 evaluation and independent verification, archive prior package first. Balanced v3 content must remain unchanged. No upload or external publication authorized.
