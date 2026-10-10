# Independent negative and candidate feasibility review

## Evidence inspected

I inspected the v3 release metadata and annotation records, including `master/negative_clean.jsonl`, `master/positive_clean.jsonl`, the group-specific matched-pair indexes, the release README/construction protocol, and relevant negative review/package/validation code. This review used text and release metadata only. No raw videos or feature tensors were inspected, and no source-release file was changed.

## What v3 negatives establish

The clean v3 negative pool contains 2,869 unique rows from 1,858 videos: 1,316 train, 395 validation, and 1,158 test. Each has an empty `relevant_windows`, `construction_type=legacy_adjudicated_negative`, and `verification_status=llm_semantic_review_passed`. Every row records the source query, source qid, source windows, semantic events, review notes, and a fixed absence-evidence label describing the short-video construction assumption and no conflict with original GT.

For 2,866 rows, `source_qid` resolves to a positive in the clean v3 positive pool, and video, source query, and source windows all match. Three references do not resolve in that clean pool; keep these as provenance exceptions rather than guessing replacements. A source qid may support multiple negative candidates (308 source qids are reused), so source-query-level statistical dependence should be recorded.

The v3 release is not video-verified: its protocol sets `video_review_performed` to false and its README says there was no per-video review. Thus `llm_semantic_review_passed` is inherited semantic-review provenance, not visual verification of absence. Reuse exact rows only with that distinction intact. The v3 groups demonstrate that text-level held-out-negative coverage exists (for example, C1 test has 264 U− rows from 92 videos and C2 has 92 U− rows from 74 videos), but new v4 keys need their own direct event-level classification and audit.

## Available event structure and risk

The clean negatives carry 3,138 event records; 265 negative queries have multiple events. The event records include anchor roles such as theme, support surface, location, agent, goal, and source. The full `events` list is essential: the `semantic_graph` is a primary-event projection and can miss leakage or target evidence in another event. Positive event records include 23 with no anchor role; those should be unresolved for role-based composition eligibility unless the source sentence plus v3 ontology resolves the relation without guessing.

Event-level existence in a caption or annotation is not exhaustive video evidence. Absence of a matching event among a target video's text annotations is therefore only a conflict screen, never proof that a candidate event is absent.

## Candidate construction recommendation

Both additional methods are feasible as candidate-only sidecars:

1. **In-domain reassignment:** take an existing positive query whose full event list expresses the frozen target key and assign it to a different video in the same frozen split. Reject exact/ontology-equivalent support found in every available target-video annotation, and keep a transparent token/TF-IDF similarity score as a ranking aid if compatible local CLIP text features are unavailable. Report conservative low-similarity and hard component-overlap strata separately. Neither stratum establishes absence.
2. **Structure-preserving counterfactual:** edit one non-target role or event component from a genuine positive while retaining the exact target action–role–filler key. Validate the resulting role direction/key after editing, test equivalence and coherence independently, inspect all same-video positive events, and quarantine unresolved cases. If the target key changes, reject the candidate.

Do not merge either source with the inherited v3 pool or label it `exist_label=0` as confirmed ground truth. Candidate matched pairs should be clearly marked provisional and should include original qid, source/target video, source/candidate sentence, target key, method, changed components, text-conflict evidence, independent semantic decision, and the no-video-evidence limitation.

The existing v3 `matched_u_pairs.jsonl` records within-video minimal edits tied to source positives. They are not cross-video MoU-style reassignment and must not be reported as such. Reuse a legacy pair only if both members still qualify under the newly frozen v4 composition definition.

## Independent conclusion

The source data supports a meaningful inherited-negative audit and likely permits some U− coverage for new compositions, depending on full event/role intersection with selected test positives. Reassignment and counterfactual expansion are methodologically implementable, but only as unverified candidate pools until video review is available. The most important guard is to preserve the inherited review state and distinguish semantic review from evidence of visual absence.
