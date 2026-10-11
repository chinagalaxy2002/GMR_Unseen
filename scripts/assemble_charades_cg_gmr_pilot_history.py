#!/usr/bin/env python3
"""Assemble invalid-v2 and pending-v3 pilot review histories for audit only."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1/work'


def read(relative):
    return [json.loads(x) for x in (BASE / relative).read_text(encoding='utf-8').splitlines() if x.strip()]


def write(relative, rows):
    (BASE / relative).write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in rows), encoding='utf-8')


def assemble_v2():
    evidence = {x['candidate']['candidate_id']: x for x in read('staging/corrected_pilot_evidence.jsonl')}
    a = {x['candidate_id']: x for x in read('review/corrected_pilot_agent_a.jsonl')}
    b = {x['candidate_id']: x for x in read('review/corrected_pilot_agent_b.jsonl')}
    c = {x['candidate_id']: x for x in read('review/corrected_pilot_agent_c.jsonl')}
    scores = {x['candidate_id']: x for x in read('staging/corrected_pilot_clip_scores.jsonl')}
    source_rows = read('staging/positive_source_rows.jsonl')
    target_durations = {x['vid']: x['duration'] for x in source_rows}
    out = []
    for cid in sorted(evidence):
        inp, ra, rb = evidence[cid], a[cid], b[cid]
        disagreement = any(ra.get(k) != rb.get(k) for k in ('decision', 'audited_partition', 'construction_valid'))
        rc = c.get(cid) if disagreement else None
        if disagreement and rc is None:
            raise SystemExit(f'missing C adjudication for {cid}')
        status = rc['decision'] if rc else ra['decision']
        reason = 'Agent C adjudicated A/B disagreement.' if rc else 'A and B agreed.'
        candidate = inp['candidate']
        known_invalid = candidate['construction_type'] == 'cross_video' and candidate['duration'] != target_durations[candidate['target_vid']]
        if known_invalid:
            status = 'quarantine'
            reason = 'Generation-invalid: target video carried donor duration; retained as process-only failure record.'
        out.append({
            'sample_id': cid, 'input_hash': inp['candidate']['input_hash'], 'candidate_input': inp['candidate'],
            'source_evidence': inp, 'review_history': {'A': ra, 'B': rb, 'C': rc},
            'review_resolution': 'agent_c_adjudicated' if rc else 'A_B_agreement',
            'final_status': status, 'reason': reason,
            'release_eligibility': 'ineligible_process_pilot_generation_invalid_duration',
            'evidence_level': None,
        })
    write('review/corrected_pilot_v2_review_history.jsonl', out)
    return out


def main():
    rows = assemble_v2()
    counts = Counter(x['final_status'] for x in rows)
    summary = {
        'v2_records': len(rows), 'final_status_counts': dict(counts),
        'A_reviews': 200, 'B_reviews': 200, 'C_adjudications': 100,
        'pending_or_retry': sum(x['final_status'] in {'pending', 'retry'} for x in rows),
        'release_eligible': 0,
        'reason': 'All 100 cross-video rows use donor duration in place of target duration; entire v2 set is process-only and ineligible for the release.',
    }
    (BASE / 'reports/corrected_pilot_v2_review_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
