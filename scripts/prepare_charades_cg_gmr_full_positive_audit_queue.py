#!/usr/bin/env python3
"""Build hash-linked per-instance evidence bundles for the full positive audit."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1'
WORK = BASE / 'work'
STAGING = WORK / 'staging'
REVIEW = WORK / 'review'


def rows(path):
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def sha256(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def main():
    source = list(rows(STAGING / 'positive_source_rows.jsonl'))
    by_video = defaultdict(list)
    for row in source:
        by_video[row['vid']].append({
            'source_qid': row['source_qid'], 'source_file': row['source_file'],
            'query': row['query'], 'official_subset': row['official_subset'],
            'official_compositions': row['official_compositions'],
            'official_novel_words': row['official_novel_words'],
        })
    quality = {r['source_qid']: r for r in rows(REVIEW / 'source_window_quality_flags.jsonl')}
    train_pool = [
        {'source_qid': x['source_qid'], 'source_file': x['source_file'],
         'query': x['query'], 'official_subset': x['official_subset']}
        for x in source if x['video_split'] == 'train'
    ]
    train_pool_path = STAGING / 'full_positive_training_support_pool.jsonl'
    train_pool_path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in train_pool), encoding='utf-8')
    out = []
    for row in source:
        flag = quality.get(row['source_qid'])
        if flag is None:
            raise RuntimeError(f"missing source window quality row: {row['source_qid']}")
        bundle = {
            'audit_id': row['source_qid'],
            'input_hash': row['input_hash'],
            'source_row': row,
            'same_video_positive_annotations': by_video[row['vid']],
            'source_window_quality': flag,
            'training_support_pool_path': str(train_pool_path.relative_to(ROOT)),
            'audit_scope': (
                'Independently judge this complete query and source instance from text and official annotations. '
                'Parse all events and role arguments; verify synonyms/entailments, plurality, pronouns/coreference, '
                'multi-event meaning, official composition identity, and train-positive member support. '
                'Do not infer visual presence/absence from incomplete annotation lists. Preserve source timestamps exactly.'
            ),
        }
        # Hash only immutable source input and evidence, so review edits cannot alter the key.
        bundle['evidence_hash'] = sha256({k: v for k, v in bundle.items() if k != 'evidence_hash'})
        out.append(bundle)
    path = STAGING / 'full_positive_audit_evidence.jsonl'
    path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in out), encoding='utf-8')
    shard_dir = STAGING / 'positive_audit_shards'
    shard_dir.mkdir(parents=True, exist_ok=True)
    shard_size = 100
    shard_manifest = []
    for start in range(0, len(out), shard_size):
        end = min(start + shard_size, len(out))
        shard_path = shard_dir / f'batch_{start // shard_size:03d}.jsonl'
        payload = ''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in out[start:end])
        shard_path.write_text(payload, encoding='utf-8')
        shard_manifest.append({
            'batch': start // shard_size, 'start_index': start, 'end_index_exclusive': end,
            'records': end - start, 'path': str(shard_path.relative_to(ROOT)),
            'sha256': hashlib.sha256(payload.encode('utf-8')).hexdigest(),
            'first_audit_id': out[start]['audit_id'], 'last_audit_id': out[end - 1]['audit_id'],
        })
    (WORK / 'reports/full_positive_audit_shards.json').write_text(
        json.dumps({'shard_size': shard_size, 'shard_count': len(shard_manifest),
                    'records': len(out), 'batches': shard_manifest}, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8')
    report = {
        'records': len(out), 'unique_audit_ids': len({x['audit_id'] for x in out}),
        'unique_input_hashes': len({x['input_hash'] for x in out}),
        'unique_evidence_hashes': len({x['evidence_hash'] for x in out}),
        'source_window_rows': len(quality),
        'source_file_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'shard_count': len(shard_manifest), 'shard_size': shard_size,
        'training_support_candidate_rows': len(train_pool),
        'training_support_pool_sha256': hashlib.sha256(train_pool_path.read_bytes()).hexdigest(),
        'status': 'evidence prepared; no semantic decisions made',
    }
    (WORK / 'reports/full_positive_audit_queue.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
