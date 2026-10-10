# Final independent audit of reassignment candidates

## Fingerprinted snapshot

The candidate files matched the hashes provided by the parent before and after this audit. Review used v3 positive source annotations, the frozen video assignment reconstructed across the five v3 groups, and text-level v4 composition rules. No raw videos or feature tensors were inspected.

| Group | SHA-256 | Candidate rows | Source qids | Target videos |
|---|---|---:|---:|---:|
| CG01_open_theme_door | `cf66e9c46a61a51950f05bb39c8150c8b62db8cb8e357e02f2af3342d69f386c` | 346 | 173 | 344 |
| CG02_close_theme_door | `a8507318914eea75bb0ca9b52b85239636bb3e3e4f62cfa4310eaf3e4a51eced` | 164 | 82 | 164 |
| CG03_sit_support_surface_chair | `e54ba44b8a4cd172ebc1e8e08436f158bae47aa6af09038edc4b421ec30a59f9` | 132 | 66 | 132 |

## Decisions and checks

| Group | Held key | Candidates | Accept candidate | Quarantine | Reject | Score mismatches | Overlap mismatches | Exact replay mismatches | Target annotation conflicts |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CG01_open_theme_door | `open|theme|door` | 346 | 344 | 2 | 0 | 0 | 0 | 0 | 0 |
| CG02_close_theme_door | `close|theme|door` | 164 | 162 | 2 | 0 | 0 | 0 | 0 | 0 |
| CG03_sit_support_surface_chair | `sit|support_surface|chair` | 132 | 132 | 0 | 0 | 0 | 0 | 0 | 0 |

## Independent method

- Each candidate was checked for exact source qid/video/query provenance, different source and target videos, same frozen split, frozen target key, source and candidate assertion in the complete event list, independent text-level action/role interpretation, target positive annotation conflicts, deterministic qid, and candidate-only label fields.
- The v4 ontology was applied explicitly: ordinary door-part subtypes map to the `door` filler; cabinet/cupboard door entry and doorways remain distinct; chair modifiers normalize only when they denote a chair; explicit “sit on/in chair” language can establish the support relation. Purpose, intended, and negated source events are not eligible positive sources.
- Similarity was independently recomputed as the maximum token-set cosine from the source query to any positive query on the target video. Component overlap was independently recomputed as the maximum per-target-caption intersection size. Scores are lexical surrogates, not CLIP and not visual evidence.
- Exact quartile rule: for n feasible target videos, q=max(1, ceil(n/4)). Conservative pool is the first q after sorting by (similarity ascending, overlap descending, target video ascending). Hard pool is the first q after sorting by (overlap descending, similarity descending, target video ascending). Ties are resolved deterministically by later sort fields before truncation; boundary ties are not expanded. Candidate choice inside each pool is replayed using minimum prior per-strategy target use and the recorded deterministic SHA-256 tie-break.
- A positive target annotation expressing the held key quarantines the candidate. A text-annotation nonmatch does not establish absence from video. Attempts/purpose wording and ontology-ambiguous door scope are quarantined. Structural acceptance still means candidate-only; all new negatives require visual verification before gold use.

## Detailed records

Per-candidate JSON decisions are in `data/processed/semantic_existence_v4_comp/work/audit/independent_review.jsonl`; group counts and the complete snapshot hashes are in `independent_review_summary.json`.
