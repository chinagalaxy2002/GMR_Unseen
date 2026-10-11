#!/usr/bin/env python3
"""Prepare blind A/B disagreements for item-level Agent C arbitration."""
import hashlib
import json
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1/work'


def read(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def decision(row):
    # A's frozen-protocol addendum is the latest decision in review_history.
    history = row.get('review_history', [])
    return history[-1].get('decision') if history and history[-1].get('record_type') == 'compatibility_addendum' else row.get('decision', row.get('final_status'))


def part(row):
    value = str(row.get('audited_seen_unseen_partition', row.get('tentative_seen_unseen', ''))).lower()
    if not value or any(x in value for x in ('undetermined', 'unresolved', 'pending', 'unknown')):
        return 'undetermined'
    if 'unseen' in value:
        return 'Unseen'
    if 'seen' in value:
        return 'Seen'
    return value


def latest_semantic_decision(row, reviewer):
    if reviewer == 'A':
        history = row.get('review_history') or []
        if history:
            return history[-1].get('semantic_content_decision', history[-1].get('decision'))
        return row.get('audit_v0_3', {}).get('semantic_content_decision', row.get('decision'))
    history = row.get('audit_history') or []
    if history:
        return history[-1].get('semantic_content_decision', history[-1].get('decision'))
    return row.get('semantic_content_decision', row.get('decision'))


def norm(value):
    value = re.sub(r'[^a-z0-9 ]', ' ', str(value or '').lower())
    value = re.sub(r'\b(a|an|the|person|generic|subject|singular|plural|as expressed in query|unless another participant is explicitly stated)\b', ' ', value)
    return re.sub(r'\s+', ' ', value).strip()


def event_signature(row, reviewer):
    if reviewer == 'A':
        events = row.get('audit_v0_3', {}).get('semantic_review', {}).get('all_events') or row.get('semantic_events') or []
        if isinstance(events, dict):
            events = events.get('events', [])
        if events and isinstance(events[0], dict):
            return [(norm(e.get('event_or_state', e.get('action_sense'))), ('' if 'generic' in norm(e.get('agent')) else norm(e.get('agent'))), norm(e.get('theme', e.get('object'))),
                     norm(e.get('source')), norm(e.get('goal')), norm(e.get('location')),
                     norm(e.get('support_surface'))) for e in events]
    events = row.get('all_events') or row.get('semantic_parse') or []
    if isinstance(events, dict):
        events = events.get('events', [])
    if events and isinstance(events[0], str):
        actions = row.get('action_sense') or events
        if not isinstance(actions, list):
            actions = [actions]
        role_map = {x.get('role'): x.get('value') for x in (row.get('role_bindings') or []) if isinstance(x, dict)}
        return [(norm(action), norm(role_map.get('agent')), norm(role_map.get('theme', row.get('theme'))),
                 norm(role_map.get('source', row.get('source'))), norm(role_map.get('goal', row.get('goal'))),
                 norm(role_map.get('location', row.get('location'))),
                 norm(role_map.get('support_surface', row.get('support_surface')))) for action in actions]
    sig = []
    for e in events:
        if not isinstance(e, dict):
            continue
        roles = e.get('roles') or {}
        agent = norm(roles.get('agent', e.get('agent')))
        if agent in {'person subject expressed in query', 'person subject', 'generic person', 'person'}:
            agent = ''
        sig.append((norm(e.get('action_sense', e.get('event_or_state'))),
                    agent,
                    norm(roles.get('theme_or_object', e.get('theme', e.get('object')))),
                    norm(roles.get('source', e.get('source'))), norm(roles.get('goal', e.get('goal'))),
                    norm(roles.get('location', e.get('location'))),
                    norm(roles.get('support_surface', e.get('support_surface')))))
    return sig


def final_support_resolved(row, reviewer):
    if reviewer == 'A':
        support = row.get('member_support_evidence') or row.get('audit_v0_3', {}).get('training_positive_support') or {}
        state = str(support.get('status', '')).lower() if isinstance(support, dict) else ''
        return any(s in state for s in ('verified_final', 'audited_final', 'resolved')) and not any(s in state for s in ('unresolved', 'pending', 'candidate'))
    support = row.get('training_positive_support')
    if isinstance(support, dict):
        state = str(support.get('status', '')).lower()
        return any(s in state for s in ('verified_final', 'audited_final', 'resolved')) and not any(s in state for s in ('unresolved', 'pending', 'unreviewed', 'candidate'))
    return isinstance(support, list) and any(
        str(item.get('support_status', item.get('status', ''))).lower() in {'verified_final_audited_support', 'final_audited_support'}
        for item in support if isinstance(item, dict))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', type=int, required=True)
    batch = parser.parse_args().batch
    tag = f'{batch:03d}'
    evidence = read(BASE / f'staging/positive_audit_shards/batch_{tag}.jsonl')
    a = read(BASE / f'review/full_positive_agent_a_batch{tag}.jsonl')
    b = read(BASE / f'review/full_positive_agent_b_batch{tag}.jsonl')
    amap, bmap = {x['audit_id']: x for x in a}, {x['audit_id']: x for x in b}
    if len(amap) != len(evidence) or len(bmap) != len(evidence):
        raise RuntimeError(f'batch{tag} coverage must be exact for evidence/A/B')
    out, disagreements = [], []
    for item in evidence:
        qid = item['audit_id']; ra, rb = amap[qid], bmap[qid]
        for row in (ra, rb):
            if row.get('input_hash') != item['input_hash'] or row.get('evidence_hash') != item['evidence_hash']:
                raise RuntimeError(f'input/evidence hash mismatch for {qid}')
        fields = {
            'decision': (decision(ra), decision(rb)),
            'partition': (part(ra), part(rb)),
            'semantic_content_decision': (latest_semantic_decision(ra, 'A'), latest_semantic_decision(rb, 'B')),
            'semantic_event_signature': (event_signature(ra, 'A'), event_signature(rb, 'B')),
            'final_support_resolved': (final_support_resolved(ra, 'A'), final_support_resolved(rb, 'B')),
            'exposure_status': (ra.get('audit_v0_3', {}).get('exposure_check'), rb.get('exposure_check')),
        }
        # Event structures are independently worded; decision/partition/support disagreements
        # are the mandatory C gates. All 100 are sent if any required gate differs.
        differs = (fields['decision'][0] != fields['decision'][1]
                   or fields['partition'][0] != fields['partition'][1]
                   or fields['semantic_content_decision'][0] != fields['semantic_content_decision'][1]
                   or fields['semantic_event_signature'][0] != fields['semantic_event_signature'][1]
                   or fields['final_support_resolved'][0] != fields['final_support_resolved'][1])
        if differs:
            disagreements.append(qid)
            out.append({
                'audit_id': qid, 'input_hash': item['input_hash'], 'evidence_hash': item['evidence_hash'],
                'original_evidence': item, 'agent_a': ra, 'agent_b': rb,
                'disagreement_fields': fields,
                'instruction': 'Independently review the original evidence and resolve all required disagreements; do not merely vote. Cite item-specific source evidence. Apply frozen protocol v0.3. If final train support/exposure remains unresolved, quarantine rather than infer. No video absence claim.'
            })
    path = BASE / f'staging/full_positive_agent_c_batch{tag}_input.jsonl'
    path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in out), encoding='utf-8')
    report = {
        'batch': tag, 'evidence_rows': len(evidence), 'A_rows': len(a), 'B_rows': len(b),
        'input_hash_match': True, 'evidence_hash_match': True,
        'C_rows': len(out), 'disagreement_ids': disagreements,
        'C_input_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'status': 'ready_for_independent_item_level_C_adjudication',
    }
    (BASE / f'reports/full_positive_agent_c_batch{tag}_queue.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
