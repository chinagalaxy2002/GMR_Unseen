# Semantic-Existence v4 Comp — Final Report

**Status: provisional candidate release with inherited v3 annotation views. New negative candidates are not gold labels and require visual verification.**

## Composition groups

| Group | Held composition | Test U+ qids / videos | Inherited test U− qids / videos | Exact target train exclusions (positive / negative) | Ambiguous door exclusions | Query/event mismatch quarantines | Strict lexical-seen U+ |
|---|---|---:|---:|---:|---:|---:|---:|
| CG01_open_theme_door | `open|theme|door` | 173 / 126 | 53 / 37 | 541 / 91 | 38 | 6 | 163/173 (94.2%) |
| CG02_close_theme_door | `close|theme|door` | 82 / 66 | 102 / 73 | 451 / 98 | 31 | 1 | 79/82 (96.3%) |
| CG03_sit_support_surface_chair | `sit|support_surface|chair` | 66 / 44 | 42 / 27 | 288 / 58 | 0 | 0 | 64/66 (97.0%) |

## Full partition coverage

| Group | Split | S+ qids / videos | S− qids / videos | U+ qids / videos | U− qids / videos | Strict lexical-seen U− |
|---|---|---:|---:|---:|---:|---:|
| CG01_open_theme_door | train | 9805 / 4593 | 1203 / 947 | 0 / 0 | 0 / 0 | 0/0 |
| CG01_open_theme_door | val | 1036 / 482 | 368 / 207 | 35 / 31 | 23 / 17 | 23/23 (100.0%) |
| CG01_open_theme_door | test | 3193 / 1274 | 1076 / 575 | 173 / 126 | 53 / 37 | 52/53 (98.1%) |
| CG02_close_theme_door | train | 9908 / 4619 | 1195 / 934 | 0 / 0 | 0 / 0 | 0/0 |
| CG02_close_theme_door | val | 1061 / 485 | 345 / 199 | 28 / 23 | 44 / 33 | 44/44 (100.0%) |
| CG02_close_theme_door | test | 3269 / 1274 | 1031 / 550 | 82 / 66 | 102 / 73 | 99/102 (97.1%) |
| CG03_sit_support_surface_chair | train | 10097 / 4646 | 1241 / 992 | 0 / 0 | 0 / 0 | 0/0 |
| CG03_sit_support_surface_chair | val | 1067 / 490 | 373 / 218 | 24 / 20 | 18 / 15 | 17/18 (94.4%) |
| CG03_sit_support_surface_chair | test | 3344 / 1289 | 1096 / 599 | 66 / 44 | 42 / 27 | 40/42 (95.2%) |

## Independent negative candidate audit

| Group | Conservative reassignment | Hard reassignment | Counterfactual sentences generated | Accepted structurally | Quarantined | Rejected | Matched candidate pairs |
|---|---:|---:|---:|---:|---:|---:|---:|
| CG01_open_theme_door | 173 | 173 | 0 | 344 | 2 | 0 | 0 |
| CG02_close_theme_door | 82 | 82 | 0 | 162 | 2 | 0 | 0 |
| CG03_sit_support_surface_chair | 66 | 66 | 0 | 132 | 0 | 0 | 0 |

The pipeline generated **642** cross-video reassignment candidates (321 conservative and 321 hard). It generated **0** counterfactual sentences because v3 annotations do not include reliable sentence-role spans for minimal edits that preserve these target keys. Newly generated candidate matched pairs: **0**. The release includes **1** inherited same-video U+/U− pair from original annotations (CG01); it retains the original qids and labels. The independent audit records structural decisions only; every accepted candidate still requires video review before it can become an absence label.

## Feasibility, roles, and constituents

The deterministic profile found **5** keys meeting the initial positive-support and constituent screens. The frozen primary set contains **3** groups after the preferred inherited-negative support screen (30 test negative qids) and diversity rules. Exact candidates and rejection reasons are in `selection/composition_candidates.jsonl` and `selection/split_specs.json`.

| Group | Action positive training qids outside target | Filler training qids outside target | Exact train qids removed for target | Test original U+ | Inherited test U− |
|---|---:|---:|---:|---:|---:|
| CG01_open_theme_door | 837 | 512 | 541 positive + 91 negative target-exposure qids; 38 ambiguous door qids; 6 query/event mismatch qids; 92 unresolved-event qids | 173 | 53 |
| CG02_close_theme_door | 293 | 613 | 451 positive + 98 negative target-exposure qids; 31 ambiguous door qids; 1 query/event mismatch qids; 92 unresolved-event qids | 82 | 102 |
| CG03_sit_support_surface_chair | 791 | 97 | 288 positive + 58 negative target-exposure qids; 0 ambiguous door qids; 0 query/event mismatch qids; 92 unresolved-event qids | 66 | 42 |

Semantic roles supported by the v3 event inventory:

| Role | Event records | Action families |
|---|---:|---:|
| agent | 2976 | 72 |
| container | 1 | 1 |
| covering | 1 | 1 |
| experiencer | 1 | 1 |
| goal | 172 | 7 |
| instrument | 40 | 7 |
| location | 206 | 6 |
| patient | 1 | 1 |
| result | 3 | 1 |
| source | 64 | 2 |
| stimulus | 10 | 2 |
| support_surface | 1494 | 8 |
| target | 165 | 8 |
| theme | 14639 | 163 |
| viewpoint | 1 | 1 |

The main feasible groups use theme and support_surface. Goal, source, instrument, location, target, and agent are represented but much sparser or more heterogeneous; patient appears only once and was not suitable for a primary group. Agent-as-filler groups mostly encode generic person/actor variation rather than event composition.

## Video allocation and semantic coverage

All 6,507 videos represented in the clean v3 masters map consistently across all five v3 groups: 4,707 train, 498 validation, and 1,302 test. The v3 input inventory lists 6,670 assignments; the other 163 are absent from the available release and are outside v4. No video was moved between partitions. Original positive query text and windows are retained.

The builder checks every event in `events`, including multi-event rows; `semantic_graph` is only a primary-event projection. Queries with any event lacking an explicit action-role-filler composition are quarantined from labeled views and listed in each group's `unresolved_semantics.jsonl`. Independent semantic review also prompted conservative train removal for direct door wording that conflicts with the event graph and for ambiguous cabinet-door scope. Exact train exclusion qids and reasons are in `train_exclusions.jsonl`.

Strict lexical-seen coverage is calculated over content lemmas from all downstream training queries (S+ and S−). Exact missing lemmas for every U+/U− row are recorded in `statistics.json`; percentages are descriptive and lexicalization uses a deterministic lightweight lemma map, not a linguistic parser.

## Negative provenance and validation status

v3 contributes inherited negatives only when the source qid resolves to a clean positive with matching video, sentence, windows, and review provenance. These remain inherited text-reviewed labels; v3 says it performed no per-video review. Three inherited negative rows with unresolved source qids were quarantined globally and are documented under `audit/ineligible_inherited_negatives.jsonl`. Newly reassigned candidates are stored separately and have empty windows; neither low text similarity nor no annotation conflict establishes visual absence. Similarity is token cosine as a lightweight surrogate, not CLIP. This adapts the cross-video in-domain reassignment motivation from [Moment of Untruth](https://openaccess.thecvf.com/content/WACV2025/html/Flanagan_Moment_of_Untruth_Dealing_with_Negative_Queries_in_Video_Moment_WACV_2025_paper.html); the paper's method and our proposed role-sensitive counterfactual extension are kept separate. OOD negatives are not included.

| Validation gate | Result |
|---|---|
| ambiguous scope quarantine | PASS |
| candidate not promoted to gold | PASS |
| cross split reassignment | PASS |
| frozen group candidate identity | PASS |
| frozen specification integrity | PASS |
| full event train leakage | PASS |
| independent audit completeness | PASS |
| matched pair integrity | PASS |
| negative window emptiness | PASS |
| positive timestamp validity | PASS |
| quadrant assignment | PASS |
| release hashes | PASS |
| source and candidate provenance | PASS |
| source annotation preservation | PASS |
| source input hashes | PASS |
| split order determinism | PASS |
| train qid conservation | PASS |
| v3 stage1 regression hashes | PASS |
| validation view conservation | PASS |
| video disjointness | PASS |

The validation report also contains per-group counts and any explicit errors. The v4 input inventory hashes all 28 source files used for construction, including the 15 split JSONLs. Four Stage-1 baseline hashes (clean positive/negative masters, ontology rules, and split specs) separately confirm those v3 files remained unchanged; package artifact hashes are checked against `manifest.json`.

## Feasibility limits and next steps

The main supported families are action–theme/object and action–support-surface. Action–goal and action–source are profile-only because typed roles are sparse and current inherited negative test support is inadequate; instrument and agent-patient relations are also too sparse or ambiguous for primary groups. Temporal order and state-transition compositions are exploratory only. Synonym substitution is not used as a generation method.

Principal limitations: only three groups pass the available coverage and inherited-negative screen; two use the filler `door`, which reflects source-data concentration; strict lexical coverage is not 100%; annotations do not provide visual absence evidence; exact role equivalence is limited by the frozen v3 ontology; and 163 source assignments cannot be reconstructed from the release. No model was trained and no performance claim is made.

If raw Charades videos become available, review reassignment candidates individually or in a documented video-review protocol, then import qid-level decisions without changing the frozen composition specs. If an additional video dataset becomes available, map its roles to this ontology, verify that action and filler constituents are familiar under comparable training conditions, and use its videos only under a separately versioned assignment and annotation protocol.

## Release contents and commands

Usable immediately for annotation experiments: frozen train/validation/test views with original positive windows and inherited v3 negative provenance. Candidate-only files require future video verification. The deliverable is a **mixture of labeled inherited annotation views and separately labeled provisional negative candidates**, not a video-verified gold benchmark.

Generated outputs: `data/processed/semantic_existence_v4_comp/work/` (inventory, profile, candidate generation, exclusions, review queue); `data/release/semantic_existence_v4_comp/` (frozen specs, group splits, candidate sidecars, audit, statistics, hashes, this report); `scripts/semantic_comp_v4/` (pipeline and integration tests).

Exact commands from repository root:

```bash
python scripts/semantic_comp_v4/pipeline.py inventory
python scripts/semantic_comp_v4/pipeline.py profile
python scripts/semantic_comp_v4/pipeline.py build
python scripts/semantic_comp_v4/pipeline.py negatives
python scripts/semantic_comp_v4/pipeline.py export-review
python scripts/semantic_comp_v4/pipeline.py import-review data/processed/semantic_existence_v4_comp/work/audit/independent_review.jsonl
python scripts/semantic_comp_v4/test_pipeline.py
python scripts/semantic_comp_v4/pipeline.py package
python scripts/semantic_comp_v4/pipeline.py validate
python scripts/semantic_comp_v4/pipeline.py report
python scripts/semantic_comp_v4/pipeline.py validate
```

The CLI also accepts `--repo-root`, `--v3-release`, `--work-dir`, and `--output-release` before the subcommand for alternate checkout and output paths.
