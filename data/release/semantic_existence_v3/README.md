# Semantic Existence v3

This release rebuilds five action and action-object generalization groups from resolved Charades-derived positive query events and individually reviewed legacy negative candidates. All videos use the persisted shared train/val/test assignment.

## Groups

- `A1_v3`: physical placement and taking actions held out.
- `A2_v3`: drinking and pouring held out.
- `A3_v3`: running and walking held out.
- `C1_v3`: sitting on bed, chair, or couch held out. Sofa is normalized to couch.
- `C2_v3`: opening/closing boxes and cabinets held out.

Each group contains `train.jsonl`, `val.jsonl`, `val_seen.jsonl`, `test.jsonl`, and matched unseen pair files. Train contains S+/S- only. Rows keep their shared video split. `semantic_inventory.json` and `statistics.json` report actual group contents.

## Review

All 6,976 unique legacy negative candidates have final decisions. Release negatives are only `keep` with `distinct` relation; excludes and quarantines are retained in `review/`. Positive qids unresolved after normalization are omitted from the clean pool. No model predictions, hashes, or preset scale gates were used. See `construction_protocol.json`, `review/review_statistics.json`, and `release_info.json`.

## A1 semantic repair

Revision `a1-semantic-repair-20261009-1` corrects 48 qids (47 A1 membership/partition changes and one unsupported event removal). Original queries, windows, existence labels, and video splits are preserved. 29 ambiguous candidates remain pending. See `review/a1_semantic_corrections.jsonl` and `review/a1_semantic_revision.json`. Other groups retain their membership and partition counts. Existing runs on the prior data version are not runs on this revision.
