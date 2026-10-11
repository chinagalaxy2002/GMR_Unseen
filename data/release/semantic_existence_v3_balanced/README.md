# Semantic Existence v3 Balanced

Independent extension of `semantic_existence_v3_release`; all original rows are retained.

## Counts

| Group | Split | Positive | Original negative | Added pseudo negative | Final negative | S+ | S− | U+ | U− |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A1_v3 | train | 8801 | 1018 | 7783 | 8801 | 8801 | 8801 | 0 | 0 |
| A1_v3 | val | 1119 | 395 | 724 | 1119 | 923 | 928 | 196 | 191 |
| A1_v3 | test | 3453 | 1158 | 2295 | 3453 | 2857 | 2882 | 596 | 571 |
| A2_v3 | train | 9791 | 1018 | 8773 | 9791 | 9791 | 9791 | 0 | 0 |
| A2_v3 | val | 1119 | 395 | 724 | 1119 | 1050 | 1047 | 69 | 72 |
| A2_v3 | test | 3453 | 1158 | 2295 | 3453 | 3230 | 3213 | 223 | 240 |
| A3_v3 | train | 9747 | 1018 | 8729 | 9747 | 9747 | 9747 | 0 | 0 |
| A3_v3 | val | 1119 | 395 | 724 | 1119 | 1051 | 1045 | 68 | 74 |
| A3_v3 | test | 3453 | 1158 | 2295 | 3453 | 3218 | 3175 | 235 | 278 |
| C1_v3 | train | 10042 | 839 | 9203 | 10042 | 10042 | 10042 | 0 | 0 |
| C1_v3 | val | 1119 | 395 | 724 | 1119 | 1063 | 986 | 56 | 133 |
| C1_v3 | test | 3453 | 1158 | 2295 | 3453 | 3311 | 3095 | 142 | 358 |
| C2_v3 | train | 10100 | 839 | 9261 | 10100 | 10100 | 10100 | 0 | 0 |
| C2_v3 | val | 1119 | 395 | 724 | 1119 | 1074 | 1062 | 45 | 57 |
| C2_v3 | test | 3453 | 1158 | 2295 | 3453 | 3322 | 3274 | 131 | 179 |

## Construction and interpretation

Implements the per-query lowest 50% video ranking in [Moment of Untruth, Section 3.3](https://openaccess.thecvf.com/content/WACV2025/papers/Flanagan_Moment_of_Untruth_Dealing_with_Negative_Queries_in_Video_Moment_WACV_2025_paper.pdf). Scores are maxima of L2-normalized projected CLIP EOT sentence vectors against all clean positive query annotations of the target video. Candidate videos come from the same group and split, excluding the donor video. The bottom floor(N/2) is selected before annotation vetoes; exact ties use video ID order. A cosine value of 0.5 is never used as a threshold.

The v3 full-event held-out predicates are preserved, including assertion state, object aliases and anchor roles. Donors are existing group/split positives; train additions contain S− only. Validation/test addition quotas follow original S+/U+ proportions. Total split balance does not imply balance within Seen/Unseen; inherited C1 U− already outnumbers U+.

All target-video clean positive annotations are used for filtering, including held-out train-video annotations that are never inserted into training. Exact query matches and conservative semantic overlaps/opposites on the same anchor are vetoed. These checks cannot detect all false negatives. **Every added label is a pseudo negative, without video verification; low similarity does not prove absence.**

Each negative stores its donor qid/video/split, independent qid, cosine score, ascending rank, candidate count, cutoff and reference count. `provenance/` and `master/negative_added.jsonl` contain only additions. `master/negative_clean.jsonl` remains the original reviewed pool, avoiding any claim that additions were reviewed. Original matched-U files are retained unchanged.

Original shared reviewed pools are preserved in `selection/`; full augmented training pools are group-specific. Original audit metadata is in the source release. Source SHA256 checksums are frozen in `source_manifest.json`; `checksums.sha256` covers this release. `clip_metadata.json` identifies weights, encoder code, embedding cache and numeric environment. Feature vectors remain in ignored `data/processed/`.

Use `val_seen.jsonl` for checkpoint/threshold selection. Freeze Seen-validation choices before Unseen evaluation. Report AUROC, actual Rej-F1 and G-mIoU separately on Seen/Unseen; class proportions influence Rej-F1 and G-mIoU, including after this augmentation. This construction does not establish any model performance improvement.

## Reproduce / validate

Exact build arguments are recorded in `construction_protocol.json`.

```bash
python scripts/validate_semantic_existence_v3_balanced.py
```
