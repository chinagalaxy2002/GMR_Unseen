# Semantic Existence v3 Release

This is the clean release built from the completed v3 semantic audit. Quarantined and excluded examples are absent from the master pools and all train/validation/test splits. The prior `semantic_existence_v3` directory remains the audit archive.

## Clean pools

- Positive qids: 15,034
- Reviewed distinct negative qids: 2,869
- Quarantined or excluded examples in this release: 0

## Generalization groups

- `A1_v3`: hold out physical placement and physical taking actions.
- `A2_v3`: hold out drinking and pouring actions.
- `A3_v3`: hold out running and walking actions.
- `C1_v3`: hold out sitting on a bed, chair, or couch; sofa is normalized to couch.
- `C2_v3`: hold out opening/closing boxes and cabinets, including parts with explicit box/cabinet context.

A complete query is removed from training if it contains an asserted held event. Purpose/intended and negated events do not count as events that occurred. Training contains seen positive and negative rows only. Validation and test retain seen and unseen rows according to each group's definition. All groups use the same persisted video-level train/validation/test assignment.

| Group | Train | Validation | Test | Total | U+ | U− | Test matched-U pairs |
|---|---:|---:|---:|---:|---:|---:|---:|
| A1_v3 | 9,819 | 1,514 | 4,611 | 15,944 | 792 | 239 | 128 |
| A2_v3 | 10,809 | 1,514 | 4,611 | 16,934 | 292 | 119 | 90 |
| A3_v3 | 10,765 | 1,514 | 4,611 | 16,890 | 303 | 152 | 100 |
| C1_v3 | 10,881 | 1,514 | 4,611 | 17,006 | 198 | 361 | 116 |
| C2_v3 | 10,939 | 1,514 | 4,611 | 17,064 | 176 | 120 | 32 |

`U+` and `U−` are unseen positive/negative rows across validation and test. The train S− qid pool is identical across groups within each axis: 1,018 qids for the action groups and 839 for the composition groups. `val_seen.jsonl` contains the seen validation subset. `matched_u_pairs.jsonl` is a pair index; `test_matched_u.jsonl` expands test pairs to their positive and negative rows. These counts are also available in each group's `statistics.json` and `semantic_inventory.json`.

## Contents

- `master/`: clean positive and negative qid pools.
- `splits/`: group-specific train, validation, test, seen-validation, and matched-U files.
- `selection/`: split specifications, semantic rules, and clean shared seen-negative pools.
- `ontology/`: v3 ontology rules and version.
- `audit_summary.json`: aggregate decision counts only; it contains no quarantined sample rows.
- `release_info.json`, `input_inventory.json`, `validation_report.json`: release counts and validation status.

The qid-level audit evidence and the separate quarantine-review workbook remain outside this clean release under `data/release/semantic_existence_v3/review/`. No per-video review was performed.
