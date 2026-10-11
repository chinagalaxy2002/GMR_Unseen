# Charades-CG-GMR C3_CG extension

Release: `data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2/`. Independent of A1–C2. Included official subsets: official_train, novel_composition, test_trivial. Novel-Word remains excluded. Official Test-Trivial is the Seen test reference and Novel-Composition is Unseen; these are inherited source identities, without semantic re-audit. Unseen refers to the downstream composition split, not pretrained-model exposure.

Source positives retain exact queries, videos, time windows and composition markers; invalid source rows are removed without clipping. Train/Val reuse the seed-3407 video assignments. Train, validation and test videos are disjoint; the two test query subsets may share videos.

Negatives use Moment of Untruth §3.3 in-domain text reassignment: OpenAI CLIP ViT-B/32 text embeddings, max cosine against every positive description on each same-split candidate video, then uniform sampling among the lowest-scoring floor(50%) of eligible videos. Query text is unchanged; S/U follows the source query. All included test descriptions are combined per video for both Seen and Unseen queries. Negatives have `relevant_windows=[]` and are construction labels; they are neither agent text-audited nor confirmed absent by video inspection.

| Output | S+ | S− | U+ | U− | Total |
|---|---:|---:|---:|---:|---:|
| train | 6342 | 6342 | 0 | 0 | 12684 |
| val_seen | 684 | 684 | 0 | 0 | 1368 |
| test | 2684 | 2684 | 2990 | 2990 | 11348 |

Removed source rows within included subsets: 2119. Sampling deficits: 0. See `statistics.json`, `negative_generation.json`, `removed_rows.jsonl`, and `splits/C3_CG/`.

Use Seen validation only to freeze checkpoints, thresholds and hyperparameters. Report AUROC, actual Rej-F1, end-to-end G-mIoU@1 separately on Seen/Unseen and Gap = Seen − Unseen (percentage points, preserving negative gaps). Also report overall Rej-F1, rejection rate, S+/U+ false rejection rates, overall G-mIoU@1 and all class counts. Use video-cluster bootstrap 95% CIs, jointly resampling shared test videos across subsets; for baseline comparisons use paired intervals for Unseen Net Gain, Seen Change and Gap Reduction with the same split/backbone. Rej-F1 and G-mIoU gaps depend on class proportions. C3_CG alone is not a five-split macro result. Preserve predictions, calibration metadata and bootstrap artifacts as required by AGENTS.md. No model training or evaluation is included in this release.

This v2 restores the Seen test reference while preserving v1. Train/Val are byte-identical to v1; both test negative groups were regenerated. See `REVISION_NOTES.md` for commands, compatibility and acceptance evidence.
