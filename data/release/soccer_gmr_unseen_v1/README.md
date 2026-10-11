# Soccer-GMR WorldCup Semantic-Unseen v1

This release contains mechanically cleaned annotations from `data/label/Full/`, filtered to `dataset_source == "worldcup2022"`. It preserves the source `qid`, `vid`, `query`, `duration`, `relevant_windows`, `moment`, action and match metadata. It does not include videos, features, model outputs, or checksums.

## Protocol

Each of five independent groups has a `train.jsonl` containing only S+/S−, a four-quadrant `val.jsonl`, a Seen-only `val_seen.jsonl` for checkpoint and threshold selection, and a four-quadrant `test.jsonl`. Use `val_seen.jsonl` for all model and threshold selection. `excluded_train.jsonl` records clean original training queries withheld by that group's semantic rule. `review/quarantine.jsonl` contains source rows removed by mechanical quality rules, with all detected reasons.

## Recomputed counts

| Source split | Raw + | Raw − | Raw total | Clean + | Clean − | Clean total | Quarantined |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 5535 | 8669 | 14204 | 5470 | 8534 | 14004 | 200 |
| val | 705 | 1080 | 1785 | 695 | 1060 | 1755 | 30 |
| test | 952 | 1327 | 2279 | 940 | 1306 | 2246 | 33 |

Quadrant counts below use the order S+/S−/U+/U−. Counts are queries; the same validation and test qids appear in all five groups with group-specific partitions.

| Group | Train | Val | Test | Train exclusions | val_seen | Test U pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A1_soccer | 4650/7384/0/0 | 587/911/108/149 | 818/1111/122/195 | 1970 (held_out_action 1970) | 1498 | 37 |
| A2_soccer | 4777/7470/0/0 | 625/914/70/146 | 833/1136/107/170 | 1757 (held_out_action 1757) | 1539 | 35 |
| A3_soccer | 4822/7543/0/0 | 624/927/71/133 | 812/1158/128/148 | 1639 (held_out_action 1639) | 1551 | 43 |
| C1_soccer | 4145/7252/0/0 | 603/914/92/146 | 839/1132/101/174 | 2607 (generic_actor_query_for_held_action 729, held_out_action_actor_combination 1878) | 1517 | 20 |
| C2_soccer | 4607/7593/0/0 | 627/915/68/145 | 867/1163/73/143 | 1804 (generic_actor_query_for_held_action 375, held_out_action_actor_combination 1429) | 1542 | 16 |

The action groups hold out dribble (A1), shot (A2), or interception (A3). The composition groups hold out eight action–team combinations for each of two actions, selected by the predeclared train-only support ranking; the exact lists and candidate counts are in `selection/`. Generic-actor queries in composition-group validation and test are S because they do not name a held-out action–team relation. They are excluded from composition-group training when their action is held out.

`matched_u_pairs.jsonl` and `test_matched_u.jsonl` are optional observational diagnostics. A pair shares a normalized clip identifier and action but is not a source-positive edit or a counterfactual pair.

## Construction and validation

From the repository root:

```bash
python scripts/build_soccer_gmr_unseen.py --source data/label/Full --output data/release/soccer_gmr_unseen_v1
python scripts/validate_soccer_gmr_unseen.py --source data/label/Full --release data/release/soccer_gmr_unseen_v1
```

See `construction_protocol.json`, `source_statistics.json`, `audit_summary.json`, and `validation_report.json` for the recorded rules, recomputed counts, cleaning audit, and independent validation results.

## Limitations

The source train/val/test assignment is preserved, and clip overlap across those sets is not analyzed or repaired. This does not establish match-level or complete visual independence. All data come from WorldCup 2022, but team, match, and query-template biases may remain. Negative labels and positive windows are inherited from source annotation and were not reviewed against videos for this release; mechanical checks cannot establish annotation truth. The action and action–team groups control different semantic axes, and generic-actor queries limit interpretation of composition splits. C2 has a small test U+ subset (73 queries); see per-group statistics. This release contains no experiment results and does not imply that any model was trained.
