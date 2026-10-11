#!/usr/bin/env python3
"""Validate the Charades-CG-GMR construction workspace without claiming release completion."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1'


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    checks, failures = {}, []
    manifest = json.loads((BASE / 'source/source_manifest.json').read_text())
    for item in manifest['files']:
        path = BASE / item['path']
        checks[f"source_hash:{item['path']}"] = path.exists() and sha(path) == item['sha256']
    checksum_file = BASE / 'source/checksums.sha256'
    checksum_results = []
    for line in checksum_file.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        expected, rel = line.split(None, 1)
        checksum_path = ROOT / rel.strip().lstrip('*')
        checksum_results.append(checksum_path.is_file() and sha(checksum_path) == expected)
    checks['source_checksum_manifest_valid'] = bool(checksum_results) and all(checksum_results)
    source = rows(BASE / 'work/staging/positive_source_rows.jsonl')
    raw = {name: json.loads((BASE / 'source' / name).read_text(encoding='utf-8'))
           for name in ('train.json', 'test_trivial.json', 'novel_composition.json', 'novel_word.json')}
    checks['source_row_count_15514'] = len(source) == 15514
    checks['source_qid_unique'] = len({x['source_qid'] for x in source}) == len(source)
    checks['all_positive_labels_one'] = all(x['exist_label'] == 1 for x in source)
    checks['source_windows_preserved'] = all(bool(x['relevant_windows']) for x in source)
    checks['expanded_source_matches_raw_queries_windows_and_tags'] = all(
        x['query'] == raw[x['source_file']][x['vid']]['sentences'][x['source_sentence_index']]
        and x['relevant_windows'] == [raw[x['source_file']][x['vid']]['timestamps'][x['source_sentence_index']]]
        and x['duration'] == raw[x['source_file']][x['vid']]['duration']
        and x['official_compositions'] == raw[x['source_file']][x['vid']].get('novels', [{}] * len(raw[x['source_file']][x['vid']]['sentences']))[x['source_sentence_index']]
        and x['official_novel_words'] == raw[x['source_file']][x['vid']].get('news', [{}] * len(raw[x['source_file']][x['vid']]['sentences']))[x['source_sentence_index']]
        for x in source)
    vids = {}
    for x in source:
        vids.setdefault(x['vid'], set()).add(x['video_split'])
    train = {v for v, s in vids.items() if 'train' in s}
    val = {v for v, s in vids.items() if 'val_seen' in s}
    test = {v for v, s in vids.items() if 'test' in s}
    checks['train_val_video_disjoint'] = not train & val
    checks['train_test_video_disjoint'] = not train & test
    checks['val_test_video_disjoint'] = not val & test
    checks['val_seen_356_videos'] = len(val) == 356
    checks['test_subset_video_sharing_allowed'] = True
    win = rows(BASE / 'work/review/source_window_issues.jsonl')
    checks['window_issue_count_2228'] = len(win) == 2228
    checks['window_issues_preserve_source_values'] = all(
        x['decision'] == 'include_with_quality_flag'
        and x['resolved_source_window_status'] == 'include_source_faithful_with_flag_pending_full_semantic_review'
        and x['source_action_interval_match']
        and x['source_duration_flag'] == 'source_action_interval_exceeds_csv_length'
        and x['original_window']
        for x in win)
    endpoint_map = rows(BASE / 'work/reports/source_window_action_endpoint_mapping.jsonl')
    checks['window_exact_official_action_interval_coverage'] = len(endpoint_map) == 2228 and all(
        bool(x['matching_full_action_intervals']) and x['matching_action_endpoint_also_exceeds_duration']
        for x in endpoint_map)
    quality_path = BASE / 'work/review/source_window_quality_flags.jsonl'
    quality = rows(quality_path) if quality_path.exists() else []
    quality_by_qid = {x['source_qid']: x for x in quality}
    checks['all_source_windows_quality_flagged'] = len(quality) == len(source) and set(quality_by_qid) == {x['source_qid'] for x in source}
    if checks['all_source_windows_quality_flagged']:
        checks['window_flags_preserve_all_source_intervals'] = all(
            quality_by_qid[x['source_qid']]['source_window'] == x['relevant_windows'][0]
            and quality_by_qid[x['source_qid']]['duration'] == x['duration']
            and quality_by_qid[x['source_qid']]['source_action_interval_match']
            and not quality_by_qid[x['source_qid']]['visual_confirmation']
            for x in source)
        checks['window_overrun_quality_flag_count_2228'] = sum(bool(x['source_action_interval_exceeds_csv_length']) for x in quality) == 2228
    ev = rows(BASE / 'work/staging/pilot_evidence.jsonl')
    ids = {x['candidate']['candidate_id']: x['candidate']['input_hash'] for x in ev}
    checks['pilot_200_evidence_rows'] = len(ev) == 200 and len(ids) == 200
    a = rows(BASE / 'work/review/pilot_agent_a.jsonl')
    b = rows(BASE / 'work/review/pilot_agent_b_v2.jsonl')
    for label, review in [('A', a), ('B_v2', b)]:
        checks[f'pilot_{label}_coverage_200'] = len(review) == 200 and {x['candidate_id'] for x in review} == set(ids)
        checks[f'pilot_{label}_hash_match'] = all(ids.get(x['candidate_id']) == x.get('input_hash') for x in review)
        checks[f'pilot_{label}_no_pending'] = all(x.get('decision') in {'keep', 'exclude', 'quarantine'} for x in review)
    checks['B_v2_keep_evidence_citations'] = all(
        bool(x.get('compared_target_annotation') or x.get('target_same_video_annotation_evidence_ids'))
        and bool(x.get('reason')) for x in b if x['decision'] == 'keep')
    clip = rows(BASE / 'work/staging/pilot_clip_scores.jsonl')
    checks['pilot_clip_100_cross_scores'] = len(clip) == 100 and all(x.get('status') == 'scored' for x in clip)
    checks['pilot_clip_lower_half_screen'] = all(x.get('rank_fraction') is not None and x.get('eligible_target_video_count') for x in clip)
    cpath = BASE / 'work/review/pilot_agent_c.jsonl'
    c = rows(cpath) if cpath.exists() else []
    disagree = {x['candidate_id'] for x in a if (lambda other: other is None or any(x.get(k) != other.get(k) for k in ('decision', 'audited_partition', 'construction_valid')))(next((z for z in b if z['candidate_id'] == x['candidate_id']), None))}
    checks['pilot_C_adjudication_coverage'] = {x.get('candidate_id') for x in c} == disagree
    checks['pilot_C_decisions_complete'] = bool(c) and all(
        x.get('decision') in {'keep', 'exclude', 'quarantine'} and bool(x.get('reason'))
        and bool(x.get('decisive_evidence')) for x in c)
    corrected = BASE / 'work/staging/corrected_pilot_v3_candidates_unscored.jsonl'
    corrected_evidence = BASE / 'work/staging/corrected_pilot_v3_evidence.jsonl'
    checks['corrected_v3_pilot_candidate_and_evidence_rows'] = corrected.exists() and corrected_evidence.exists() and len(rows(corrected)) == 200 and len(rows(corrected_evidence)) == 200
    if corrected.exists() and corrected_evidence.exists():
        cv3, ev3 = rows(corrected), rows(corrected_evidence)
        checks['corrected_v3_pilot_input_hash_links'] = all(x['candidate']['input_hash'] == y['input_hash'] for x, y in zip(ev3, cv3))
        checks['corrected_v3_cross_target_duration_matches'] = all(
            x['duration'] == x['target_duration'] and x['target_duration'] == next(z['duration'] for z in source if z['vid'] == x['target_vid'])
            for x in cv3 if x['construction_type'] == 'cross_video')
        checks['corrected_v3_all_source_subset_evidence'] = all(
            {z['source_qid'] for z in ev['same_video_positive_evidence']} ==
            {z['source_qid'] for z in source if z['vid'] == ev['candidate'].get('target_vid', ev['candidate']['vid'])}
            for ev in ev3)
    checks['corrected_v3_clip_scored'] = (BASE / 'work/staging/corrected_pilot_v3_clip_scores.jsonl').exists() and len(rows(BASE / 'work/staging/corrected_pilot_v3_clip_scores.jsonl')) == 100
    v2_history = BASE / 'work/review/corrected_pilot_v2_review_history.jsonl'
    checks['corrected_v2_invalid_pilot_fully_adjudicated'] = v2_history.exists() and len(rows(v2_history)) == 200 and all(
        x['release_eligibility'] == 'ineligible_process_pilot_generation_invalid_duration'
        and x['final_status'] in {'exclude', 'quarantine'} for x in rows(v2_history))
    v3_a = BASE / 'work/review/corrected_pilot_v3_agent_a.jsonl'
    v3_b = BASE / 'work/review/corrected_pilot_v3_agent_b.jsonl'
    for label, path in [('A', v3_a), ('B', v3_b)]:
        check = path.exists() and len(rows(path)) == 200 and {x['candidate_id'] for x in rows(path)} == {x['candidate_id'] for x in cv3}
        checks[f'corrected_v3_agent_{label}_review_coverage'] = check
        if check:
            by_id = {x['candidate_id']: x for x in cv3}
            checks[f'corrected_v3_agent_{label}_hash_match_no_pending'] = all(
                x.get('input_hash') == by_id[x['candidate_id']]['input_hash']
                and x.get('decision') in {'keep', 'exclude', 'quarantine'} for x in rows(path))
    v3_c = BASE / 'work/review/corrected_pilot_v3_agent_c.jsonl'
    checks['corrected_v3_agent_c_disagreements_adjudicated'] = False
    if v3_a.exists() and v3_b.exists() and v3_c.exists():
        ar, br, cr = ({x['candidate_id']: x for x in rows(path)} for path in (v3_a, v3_b, v3_c))
        disagreements = {cid for cid in ar if any(ar[cid].get(k) != br[cid].get(k) for k in ('decision', 'audited_partition', 'construction_valid'))}
        checks['corrected_v3_agent_c_disagreements_adjudicated'] = set(cr) == disagreements and all(
            cr[cid].get('decision') in {'keep', 'exclude', 'quarantine'} and bool(cr[cid].get('reason')) for cid in cr)
    pos_pilot = BASE / 'work/review/positive_pilot_agent_a.jsonl'
    pos_b = BASE / 'work/review/positive_pilot_agent_b.jsonl'
    checks['positive_audit_pilot_A_80'] = pos_pilot.exists() and len(rows(pos_pilot)) == 80
    checks['positive_audit_pilot_B_80'] = pos_b.exists() and len(rows(pos_b)) == 80
    pos_c = BASE / 'work/review/positive_pilot_agent_c.jsonl'
    pos_disagree = rows(BASE / 'work/staging/positive_pilot_disagreements.jsonl')
    pos_c_rows = rows(pos_c) if pos_c.exists() else []
    checks['positive_pilot_C_adjudication_coverage'] = {x.get('sample_id') for x in pos_c_rows} == {x['evidence']['sample_id'] for x in pos_disagree}
    checks['positive_pilot_C_decisions_complete'] = len(pos_c_rows) == len(pos_disagree) and all(
        x.get('decision') in {'keep', 'exclude', 'quarantine'} and bool(x.get('reason')) for x in pos_c_rows)
    checks['formal_release_files_exist'] = (BASE / 'README.md').exists() and (BASE / 'checksums.sha256').exists()
    checks['full_positive_audit_complete'] = False
    checks['full_negative_review_complete'] = False
    checks['release_complete'] = all(checks.values())
    failures = [name for name, ok in checks.items() if not ok]
    report = {'dataset': 'Charades-CG-GMR v1 construction workspace', 'checked_at': '2026-10-10',
              'status': 'pass' if not failures else 'incomplete', 'checks': checks, 'failed_or_pending_checks': failures,
              'counts': {'source_instances': len(source), 'source_videos': len(vids), 'quarantined_window_issues': len(win),
                         'pilot_candidates': len(ev), 'pilot_A_reviews': len(a), 'pilot_B_v2_reviews': len(b), 'pilot_C_reviews': len(c),
                         'positive_pilot_A_reviews': len(rows(pos_pilot)) if pos_pilot.exists() else 0,
                         'positive_pilot_B_reviews': len(rows(pos_b)) if pos_b.exists() else 0,
                         'positive_pilot_C_reviews': len(pos_c_rows),
                         'corrected_v3_pilot_candidates': len(rows(corrected)) if corrected.exists() else 0,
                         'window_overruns_exactly_mapped_to_source_actions': sum(bool(x.get('source_action_interval_match')) for x in win),
                         'all_source_window_quality_records': len(quality)},
              'limitations': ['This validator checks the work-in-progress protocol artifacts, not an accepted data release.',
                              'Overrun windows are retained source-faithfully with flags; no video review was done.',
                              'Only pilot candidate rows have dual agent review; source positives and full candidates remain incomplete.']}
    out = BASE / 'work/reports/validation_report.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'checks_passed': sum(checks.values()), 'checks_total': len(checks),
                      'pending_or_failed': failures, 'report': str(out.relative_to(ROOT))}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
