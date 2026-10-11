# C3_CG v2: frozen-baseline re-evaluation

Evaluate Moment-DETR-GMR, QD-DETR-GMR and FlashVTG-GMR on `charades_cg_gmr_v2` using the original C3_CG frozen checkpoints and exact Seen-validation thresholds. No training or threshold reselection is part of this run. Train and Seen validation are byte-identical to v1; all 11,348 v2 test records are inferred anew because both negative pools changed.

Test composition: S+/S− each 2,684, U+/U− each 2,990; 2,589 distinct target videos. The two positive official test subsets share 1,087 videos; including negatives, Seen/Unseen rows share 2,084 target videos. Use joint target-video-cluster bootstrap (2,000 draws, seed 3407) for absolute scores and Seen − Unseen gaps. AUROC is 0–1; actual Rej-F1/G-mIoU@1 are percentages and gaps are percentage points, retaining negative gaps. These metrics describe the CLIP-reassigned construction-label distribution, without semantic re-audit or video absence certification.

Frozen input annotations, checkpoint manifests, original calibration, native outputs, standardized predictions, all point metrics and bootstrap draws are under `groups/C3_CG/`. Aggregate Markdown/CSV/JSON and intervals are in `evaluation/`. `PROTOCOL.json`, `DATA_AUDIT.json`, `TEXT_FEATURE_MANIFEST.json`, `SOURCE_MANIFEST.json` and per-model `INFERENCE_COMMAND.json` record provenance. Original source/checkpoints are reused from `../charades_cg_baselines_20261010`, without changing them. Exact-query SHA256 matching reuses token features; 161 missing distinct texts were encoded with the same verified CLIP weights/tokenizer, yielding 7,895 distinct query features shared by all three backbones.

Run from repository root:

```bash
env OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /home/guoxiangyu/miniconda3/envs/univtg/bin/python -u experiments/agy_test/charades_cg_v2_evaluation_20261011/run_baselines.py
/home/guoxiangyu/miniconda3/envs/univtg/bin/python experiments/agy_test/charades_cg_v2_evaluation_20261011/verify_evaluation.py
```

The runner checks existing native prediction hashes and does not train. `FINAL_EVALUATION_STATUS.json`, `PIPELINE_EXIT.json` and `LOCAL_VERIFICATION_INDEPENDENT.json` provide completion and independent acceptance gates. `START_HERE.md` and `progress.json` record recovery state.

Only after complete evaluation and independent PASS, `refresh_publication.py` archives the old Charades report and replaces `../publication_review_20261011/charades_cg/README.md`, its tables/figures/frozen artifacts and the parent index. Balanced v3 remains unchanged. The old original v1 experiment remains an immutable historical run; cross-version differences are not method net gains. Checkpoints and thresholds were originally selected only on Seen validation. This single C3_CG experiment is not a five-split macro result.
