# Semantic-Existence v4 Comp (provisional)

This package contains composition holdout annotation views built only from `semantic_existence_v3_release`, plus separate unverified negative candidate sidecars. It is not a video-verified gold release. Existing v3 negative labels retain their v3 provenance; the v3 audit reports text semantic review and no per-video review. New reassignment candidates are never merged into annotation labels.

Training contains S+/S− only and removes a complete query when any event in its full `events` list matches the held composition. Test positives and windows are original v3 annotations. Video splits are reconstructed and checked across five v3 groups.

Run `python scripts/semantic_comp_v4/pipeline.py validate` from the repository root. Rebuild with `inventory`, `profile`, `build`, `negatives`, then `package` and `validate`. See `FINAL_REPORT.md` for counts, limits, and exact commands.
