# v2: add Seen test reference

User-requested revision on 2026-10-11. Preserved predecessor: `../charades_cg_gmr_v1/`.

- Restore 2,684 clean official Test-Trivial positives as S+ and generate 2,684 same-query S− pairs. Remove 412 invalid Test-Trivial windows without clipping; original source snapshots remain intact.
- Preserve all 2,990 original Unseen test positives, including query, source ID, video, windows and composition markers.
- Regenerate BOTH test negative groups from the joint cleaned Test-Trivial and Novel-Composition pool. Each target video's complete positive descriptions contribute to its max-cosine score. Of the 2,990 U− targets, 2,987 changed and 3 stayed the same. IDs stay stable for source tracking; old v1 test-negative predictions are not valid v2 evaluation artifacts.
- Train and Seen validation are byte-identical to v1. Existing training/calibration can be reused if its remaining configuration is unchanged, but inference must cover the new v2 test records. No training or evaluation was run here.
- Train/Val/Test have 2,892/321/2,589 disjoint videos. The two positive test subsets share 1,087 videos; resample shared target-video clusters jointly for Seen/Unseen bootstrap gaps.
- Reuse 6,503 exact prior CLIP vectors and encode 1,392 additional distinct texts with the same verified encoder/tokenizer/weights. Total distinct texts: 7,895.
- All 12,700 positives are paired. Mechanical validator and separate agent acceptance passed. Independent acceptance recomputed all full candidate-ranking digests and replayed every seed-3407 random choice. Invalid included source rows: 2,119 (Train 1,255; Novel-Composition 452; Test-Trivial 412). Novel-Word remains excluded.
- Seen/Unseen identities are inherited from official subsets. This revision makes no claim of new semantic audits, final-clean-training semantic support certification, or video-confirmed negative absence.

Reproduction commands, from repository root:

```bash
python scripts/build_charades_cg_gmr_c3.py --include-test-trivial --reuse-embeddings-from data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v1
python scripts/validate_charades_cg_gmr_c3.py --output-dir data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2 --compare-release data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v1
```

The builder refuses to overwrite populated output/work directories. For an additional reproduction, supply fresh `--output-dir` and `--work-dir` to the builder and the matching `--output-dir` to the validator. `negative_generation.json` records immutable CLIP cache and sampling-trace paths/hashes. `source_manifest.json` records source and construction-code hashes. `validation_report.json` and `independent_acceptance_report.json` contain acceptance results. Release and external construction evidence have separate checksum manifests.
