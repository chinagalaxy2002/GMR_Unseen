# Final independent train leakage audit v4

**Review ID:** `final_independent_train_leakage_audit_v4_20261010`

## Four previously reported qids

| Qid | Fold | In train | Exclusion reason |
|---|---|---:|---|
| `train4363` | CG01_open_theme_door | False | held_query_semantics_not_resolved_in_event_graph |
| `train10901` | CG01_open_theme_door | False | held_query_semantics_not_resolved_in_event_graph |
| `train4478` | CG01_open_theme_door | False | ambiguous_cabinet_door_scope_quarantined |
| `train10123` | CG02_close_theme_door | False | held_query_semantics_not_resolved_in_event_graph |

All four are absent from their group training file. `train4363` and `train10901` are among the six open query/event mismatch quarantines; `train10123` is the one close mismatch quarantine. `train4478` is also excluded, under `ambiguous_cabinet_door_scope_quarantined`, so it is not counted in the six mismatch quarantines.

## Residual scan

The refreshed exclusions contain six open query/event mismatch qids and one close qid. The additional open qids are:
- `train10171` — “person closes the open door behind them.” (event families: close). The extra “open door” wording is state/background or the query asserts closing, not opening.
- `train10901` — “the person pushes the door open.” (event families: push). The extra “open door” wording is state/background or the query asserts closing, not opening.
- `train11072` — “person they close a nearby open door.” (event families: close, open_state). The extra “open door” wording is state/background or the query asserts closing, not opening.
- `train2971` — “a person sweeps dirt out of an open door.” (event families: sweep, open_state). The extra “open door” wording is state/background or the query asserts closing, not opening.
- `train4363` — “the person walks away opens a door removes hat.” (event families: walk, open_state, undress). The extra “open door” wording is state/background or the query asserts closing, not opening.
- `train5708` — “the person sees the open refrigerator door.” (event families: see, open_state). The extra “open door” wording is state/background or the query asserts closing, not opening.

A direct active door-query scan of train files found 8 rows whose event lists did not encode the target key. Open fold: 8; close fold: 0. These are state/holding/leaving descriptions or close events in the open fold; close fold has none. The chair scan found 1 query hit(s): `train4037`, sitting on a pillow on a chair, with `support_surface=pillow`; it is not target leakage.

## Decision

Four prior qids are absent from train; train4478 is separately cabinet-scope quarantined. All six open and one close query/event-mismatch quarantine records are present. Remaining train active-door-query projection hits are close events or open-state/holding/leaving descriptions rather than an unrepresented asserted opening; the close fold has zero active close-door query/event mismatch hits. The only sit/chair query hit is sitting on a pillow on a chair, correctly represented as support_surface=pillow and not the target. No residual direct held composition exposure was found in train.

This is a text and annotation consistency audit only; it makes no claim of visual verification. Full row evidence and scan hits are in the paired JSON artifact.
