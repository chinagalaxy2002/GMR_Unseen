#!/usr/bin/env python3
"""Validate preservation, semantics, balancing and recomputed CLIP ranks for v3 balanced."""
import argparse
import datetime
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from build_semantic_existence_v3_balanced import (
    GROUPS, ROOT, SPLITS, VERSION, canon, dump, event_conflict, file_inventory,
    pseudo_scores, quotas, read_rows, row_held, sha256,
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(args):
    output = args.release
    frozen = json.loads((output / 'source_manifest.json').read_text())
    source = args.source or Path(frozen['source'])
    require(file_inventory(source) == frozen['sha256'], 'Source release checksums changed')
    manifest_path = output / 'checksums.sha256'
    if manifest_path.exists():
        expected = {}
        for line in manifest_path.read_text().splitlines():
            digest, relative = line.split('  ', 1)
            expected[relative] = digest
        current = file_inventory(output)
        current.pop('checksums.sha256', None)
        require(current == expected, 'Balanced release checksums changed')
    specs = json.loads((source / 'selection/split_specs.json').read_text())['groups']
    for folder in ('ontology', 'selection'):
        require(file_inventory(source / folder) == file_inventory(output / folder), f'{folder} changed')
    for name in ('positive_clean.jsonl', 'negative_clean.jsonl'):
        require(sha256(source / 'master' / name) == sha256(output / 'master' / name), f'Master {name} changed')
    positives = read_rows(source / 'master/positive_clean.jsonl')
    references = defaultdict(list)
    for row in positives:
        references[row['vid']].append(row)
    original_master = positives + read_rows(source / 'master/negative_clean.jsonl')
    old_qids = {r['qid'] for r in original_master}
    clip_metadata = json.loads((output / 'clip_metadata.json').read_text())
    cache = args.embedding_cache or Path(clip_metadata['cache_file'])
    require(sha256(cache) == clip_metadata['cache_sha256'], 'CLIP sentence vector cache checksum mismatch')
    with np.load(cache, allow_pickle=False) as data:
        queries = data['queries'].tolist()
        embeddings = data['embeddings'].copy()
    require(set(queries) == {r['query'] for r in positives}, 'CLIP cache does not cover source positive queries exactly')
    require(np.isfinite(embeddings).all() and np.allclose(np.linalg.norm(embeddings, axis=1), 1, atol=1e-5), 'Invalid CLIP vectors')
    query_index = {q: i for i, q in enumerate(queries)}
    expected_statistics = json.loads((output / 'statistics.json').read_text())
    stats_by_key = {(r['group'], r['split']): r for r in expected_statistics}
    added_master = read_rows(output / 'master/negative_added.jsonl')
    require(len({r['qid'] for r in added_master}) == len(added_master), 'Duplicate added master qid')
    require(not ({r['qid'] for r in added_master} & old_qids), 'New qids collide with source master')
    added_by_qid = {r['qid']: r for r in added_master}
    visited_new_qids, summaries = set(), []
    for group in GROUPS:
        group_rows, group_summaries = {}, []
        for name in ('matched_u_pairs.jsonl', 'test_matched_u.jsonl'):
            require(sha256(source / 'splits' / group / name) == sha256(output / 'splits' / group / name), f'{group}/{name} changed')
        for split in SPLITS:
            context = f'{group}/{split}'
            path = output / 'splits' / group / f'{split}.jsonl'
            old_path = source / 'splits' / group / f'{split}.jsonl'
            original = read_rows(old_path)
            rows = read_rows(path)
            group_rows[split] = rows
            added = rows[len(original):]
            require(path.read_bytes().startswith(old_path.read_bytes()), f'{context}: original bytes not preserved')
            require(rows[:len(original)] == original, f'{context}: original rows changed')
            require(len({r['qid'] for r in rows}) == len(rows), f'{context}: duplicate qids')
            require(sum(r['exist_label'] == 1 for r in rows) * 2 == len(rows), f'{context}: not 1:1')
            original_vids = {r['vid'] for r in original}
            require({r['vid'] for r in rows} == original_vids, f'{context}: video membership changed')
            require(all(r['split'] == split for r in rows), f'{context}: wrong split field')
            if split == 'train':
                require(all(r['partition'] in {'S+', 'S-'} for r in rows), f'{context}: unseen training row')
            for r in rows:
                expected_partition = ('U' if row_held(r, specs[group]) else 'S') + ('+' if r['exist_label'] else '-')
                require(r['partition'] == expected_partition, f'{context}/{r["qid"]}: held-out partition inconsistent')
                require(bool(r['relevant_windows']) == bool(r['exist_label']), f'{context}/{r["qid"]}: window/label mismatch')
            require(read_rows(output / 'provenance' / group / f'{split}_added.jsonl') == added, f'{context}: provenance mismatch')
            source_positives = {r['qid']: r for r in original if r['exist_label'] == 1}
            donor_qids = sorted({r['source_qid'] for r in added})
            require(set(donor_qids) <= set(source_positives), f'{context}: donor is not a same-split released positive')
            donors = [source_positives[qid] for qid in donor_qids]
            targets = sorted(original_vids)
            target_index = {vid: i for i, vid in enumerate(targets)}
            scores = pseudo_scores(donors, targets, references, embeddings, query_index, args.device, args.batch_size)
            donor_index = {qid: i for i, qid in enumerate(donor_qids)}
            rank_arrays, cutoffs = {}, {}
            for donor in donors:
                i = donor_index[donor['qid']]
                indices = np.array([j for j, vid in enumerate(targets) if vid != donor['vid']])
                # Independent ordering: lexsort explicitly supplies video-index tie break.
                ordered = indices[np.lexsort((indices, scores[i, indices]))]
                ranks = np.zeros(len(targets), dtype=np.int32)
                ranks[ordered] = np.arange(1, len(ordered) + 1)
                rank_arrays[donor['qid']] = ranks
                cutoffs[donor['qid']] = float(scores[i, ordered[len(ordered) // 2 - 1]])
            occupied = {(r['vid'], canon(r['query'])) for r in original}
            durations = {r['vid']: r['duration'] for r in original}
            addition_counts = Counter()
            for row in added:
                tag = f'{context}/{row["qid"]}'
                require(row['qid'] not in visited_new_qids, f'{tag}: reused new qid')
                visited_new_qids.add(row['qid'])
                require(row == added_by_qid.get(row['qid']), f'{tag}: master mismatch')
                require(row['exist_label'] == 0 and row['relevant_windows'] == [], f'{tag}: invalid negative label')
                require(row['construction_type'] == 'clip_in_domain_cross_video_pseudo_negative', f'{tag}: construction type')
                require(row['existence_status'] == 'pseudo_absent_unverified', f'{tag}: pseudo status missing')
                require(row['verification_status'] == 'clip_rank_and_annotation_veto_only_no_video_review', f'{tag}: verification status')
                require(row['generation_rule_version'] == VERSION and row['group'] == group, f'{tag}: version/group mismatch')
                donor = source_positives[row['source_qid']]
                require(row['source_vid'] == donor['vid'] != row['vid'], f'{tag}: not cross-video')
                require(row['source_split'] == split and row['source_query'] == donor['query'] == row['query'], f'{tag}: donor fields mismatch')
                require(row['source_windows'] == donor['relevant_windows'], f'{tag}: donor windows mismatch')
                require(row['events'] == donor['events'] and row['semantic_graph'] == donor.get('semantic_graph'), f'{tag}: donor semantics changed')
                require(row['duration'] == durations[row['vid']], f'{tag}: target duration mismatch')
                pair = (row['vid'], canon(row['query']))
                require(pair not in occupied, f'{tag}: duplicate video-query pair')
                occupied.add(pair)
                require(event_conflict(row, references[row['vid']]) is None, f'{tag}: positive annotation conflict')
                i, j = donor_index[row['source_qid']], target_index[row['vid']]
                filt = row['clip_filter']
                rank = int(rank_arrays[row['source_qid']][j])
                n = len(targets) - 1
                require(1 <= rank <= n // 2, f'{tag}: outside per-query bottom half')
                require(filt['rank_ascending'] == rank and filt['candidate_video_count'] == n, f'{tag}: rank/count mismatch')
                require(filt['retained_video_count'] == n // 2 and filt['retained_fraction'] == 0.5, f'{tag}: retained count mismatch')
                require(abs(filt['pseudo_similarity'] - float(scores[i, j])) < 1e-6, f'{tag}: similarity mismatch')
                require(abs(filt['cutoff_similarity'] - cutoffs[row['source_qid']]) < 1e-6, f'{tag}: cutoff mismatch')
                require(abs(filt['rank_fraction'] - rank / n) < 1e-12, f'{tag}: rank fraction mismatch')
                require(filt['target_positive_reference_count'] == len(references[row['vid']]), f'{tag}: reference count mismatch')
                addition_counts[row['partition'][0]] += 1
            require(dict(addition_counts) == {k: v for k, v in quotas(original, len(added)).items() if v}, f'{context}: S/U addition quotas mismatch')
            counts = Counter(r['partition'] for r in rows)
            saved = stats_by_key[group, split]
            require(saved['quadrants'] == dict(counts), f'{context}: statistics quadrant mismatch')
            require(saved['added_negative'] == len(added) and saved['rows'] == len(rows), f'{context}: statistics count mismatch')
            summary = {'group': group, 'split': split, 'positive': len(rows) // 2,
                       'negative': len(rows) // 2, 'original_rows_preserved': len(original),
                       'added_pseudo_negatives': len(added), 'quadrants': dict(counts),
                       'recomputed_clip_ranks_passed': len(added)}
            summaries.append(summary)
            group_summaries.append(summary)
            print(f'{context}: PASS; {len(rows)//2}:{len(rows)//2}; recomputed {len(added)} CLIP ranks', flush=True)
        for left, right in (('train', 'val'), ('train', 'test'), ('val', 'test')):
            require(not ({r['vid'] for r in group_rows[left]} & {r['vid'] for r in group_rows[right]}), f'{group}: video leakage')
            require(not ({r['qid'] for r in group_rows[left]} & {r['qid'] for r in group_rows[right]}), f'{group}: qid leakage')
        seen = read_rows(output / 'splits' / group / 'val_seen.jsonl')
        require(seen == [r for r in group_rows['val'] if r['partition'].startswith('S')], f'{group}: val_seen mismatch')
        group_stats = json.loads((output / 'splits' / group / 'statistics.json').read_text())
        require(group_stats['rows'] == sum(len(rs) for rs in group_rows.values()), f'{group}: group count mismatch')
        inventory = json.loads((output / 'splits' / group / 'semantic_inventory.json').read_text())
        expected_counts = {f'{r["split"]}_{part}': value for r in group_summaries for part, value in r['quadrants'].items()}
        require(inventory['counts'] == expected_counts and inventory['spec'] == specs[group], f'{group}: semantic inventory mismatch')
    require(visited_new_qids == set(added_by_qid), 'Added master contains unused rows')
    require(file_inventory(source) == frozen['sha256'], 'Source release changed during validation')
    return {'status': 'PASS', 'validated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source_checksum_validation': 'PASS', 'original_rows_byte_preserved': True,
            'same_split_cross_video_donors': True, 'semantic_constraints': 'PASS',
            'video_and_qid_split_isolation': 'PASS', 'clip_rank_recomputation': 'all_added_pairs',
            'added_pseudo_negative_qids': len(visited_new_qids), 'new_negative_video_review': False,
            'groups_and_splits': summaries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, default=ROOT / 'data/release/semantic_existence_v3_balanced')
    parser.add_argument('--source', type=Path)
    parser.add_argument('--embedding-cache', type=Path)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--batch-size', type=int, default=128)
    args = parser.parse_args()
    try:
        report = validate(args)
    except (ValueError, KeyError, OSError) as error:
        print(json.dumps({'status': 'FAIL', 'error': str(error)}, ensure_ascii=False, indent=2))
        return 1
    dump(args.release / 'validation_report.json', report)
    info_path = args.release / 'release_info.json'
    info = json.loads(info_path.read_text())
    info.update(status='balanced_pseudo_negative_release_validated', validation='PASS', validated_at=report['validated_at'])
    dump(info_path, info)
    inventory = file_inventory(args.release)
    inventory.pop('checksums.sha256', None)
    (args.release / 'checksums.sha256').write_text(''.join(f'{digest}  {name}\n' for name, digest in inventory.items()))
    print(f'PASS: 15 group/split datasets; {report["added_pseudo_negative_qids"]} new pairs; source unchanged')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
