#!/usr/bin/env python3
"""Generate a corrected, review-only pilot with subset-matched target pools."""
import hashlib
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1'
STAGING = BASE / 'work/staging'
SEED = 3407


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def read_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def hard_variant(query):
    # Pilot only: deliberately broad candidate rules; the agents decide if the
    # edit is grammatical, meaningful, non-synonymous, and semantically valid.
    rules = [
        (r'\bopens?\b', 'closes', 'action'), (r'\bcloses?\b', 'opens', 'action'),
        (r'\bturns on\b', 'turns off', 'action'), (r'\bturns off\b', 'turns on', 'action'),
        (r'\bsits?\b', 'stands', 'action'), (r'\bstands?\b', 'sits', 'action'),
        (r'\bdrinks?\b', 'eats', 'action'), (r'\beats?\b', 'drinks', 'action'),
        (r'\bbook\b', 'phone', 'object'), (r'\bphone\b', 'book', 'object'),
        (r'\bglass\b', 'cabinet', 'object'), (r'\bcabinet\b', 'glass', 'object'),
        (r'\bsofa\b', 'table', 'object'), (r'\btable\b', 'sofa', 'object'),
        (r'\binto\b', 'out of', 'relation'), (r'\bout of\b', 'into', 'relation'),
        (r'\bon the\b', 'under the', 'relation'),
    ]
    for pattern, replacement, factor in rules:
        changed, n = re.subn(pattern, replacement, query, count=1, flags=re.I)
        if n and changed != query:
            return changed, factor
    return None, None


def main():
    source = read_jsonl(STAGING / 'positive_source_rows.jsonl')
    issues = {x['sample_id'] for x in read_jsonl(BASE / 'work/review/source_window_issues.jsonl')}
    eligible = [x for x in source if x['video_split'] in {'train', 'val_seen', 'test'} and x['source_qid'] not in issues]
    strata = [
        ('Seen', 'test_trivial', 'cross_video'),
        ('Unseen', 'novel_composition', 'cross_video'),
        ('Seen', 'test_trivial', 'hard_same_video'),
        ('Unseen', 'novel_composition', 'hard_same_video'),
    ]
    pools = {}
    for partition, official_subset, kind in strata:
        rows = [x for x in eligible if x['official_subset'] == official_subset]
        if kind == 'hard_same_video':
            rows = [x for x in rows if hard_variant(x['query'])[0]]
        pools[(partition, official_subset, kind)] = sorted(rows, key=lambda x: x['source_qid'])

    rng = random.Random(SEED + 1)
    # Each official query subset defines its own target-video population.
    subset_video_rows = {}
    for subset in ('test_trivial', 'novel_composition'):
        subset_video_rows[subset] = [x for x in source if x['official_subset'] == subset]
    candidates = []
    for partition, subset, kind in strata:
        pool = pools[(partition, subset, kind)]
        selected = rng.sample(pool, min(50, len(pool)))
        test_videos = sorted({x['vid'] for x in subset_video_rows[subset]})
        for i, donor in enumerate(selected):
            row = dict(donor)
            cid = f'corrected-v3-{partition.lower()}-{kind}-{i:03d}'
            row.update({'candidate_id': cid, 'construction_type': kind,
                        'provisional_partition': partition,
                        'partition_basis': 'official subset used only for pilot stratification; final audited identity pending',
                        'donor_official_subset': subset, 'generated_by': 'primary_generator_v3',
                        'review_status': 'candidate_pending_independent_agent_reviews'})
            if kind == 'cross_video':
                target_pool = [v for v in test_videos if v != donor['vid']]
                if not target_pool:
                    row.update({'generation_status': 'retry_no_same_subset_target', 'target_vid': None})
                else:
                    # Deterministic broad coverage; CLIP scoring subsequently
                    # ranks target videos only within this donor's official subset.
                    target = target_pool[(i * 37 + (11 if partition == 'Unseen' else 0)) % len(target_pool)]
                    target_rows = [x for x in subset_video_rows[subset] if x['vid'] == target]
                    target_duration = target_rows[0]['duration']
                    row.update({'target_vid': target, 'source_vid': donor['vid'], 'vid': target,
                                'source_duration': donor['duration'], 'target_duration': target_duration,
                                'duration': target_duration,
                                'relevant_windows': [], 'source_relevant_windows': donor['relevant_windows'],
                                'exist_label': 0, 'generation_status': 'candidate'})
            else:
                variant, factor = hard_variant(donor['query'])
                row.update({'query': variant, 'source_vid': donor['vid'], 'changed_factor': factor,
                            'relevant_windows': [], 'source_relevant_windows': donor['relevant_windows'],
                            'exist_label': 0, 'generation_status': 'candidate'})
            row['input_hash'] = digest(row)
            candidates.append(row)

    # Evidence includes every source positive annotation for the target video,
    # regardless of official test subset, plus the donor source annotation.
    by_video = {}
    for row in source:
        by_video.setdefault(row['vid'], []).append({
            'source_qid': row['source_qid'], 'query': row['query'],
            'source_file': row['source_file'], 'official_subset': row['official_subset'],
            'official_compositions': row['official_compositions'],
            'official_novel_words': row['official_novel_words'],
        })
    by_qid = {x['source_qid']: x for x in source}
    evidence = []
    for row in candidates:
        evidence.append({
            'candidate': row,
            'donor_positive': {k: by_qid[row['source_qid']][k] for k in ('source_qid', 'vid', 'query', 'relevant_windows', 'official_subset', 'official_compositions', 'official_novel_words')},
            'same_video_positive_evidence': by_video.get(row.get('target_vid') or row['vid'], []),
            'evidence_scope': 'all supplied positive queries from the target video across train, Test-Trivial, Novel-Composition, and Novel-Word source files; no visual video inspection',
            'instruction': 'Independently inspect the entire query and all supplied target-video annotations. The official-subset candidate pool and CLIP rank are screening metadata, not absence evidence. Do not use predictions or metrics.'
        })

    write = lambda path, rows: path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in rows), encoding='utf-8')
    write(STAGING / 'corrected_pilot_v3_candidates_unscored.jsonl', candidates)
    write(STAGING / 'corrected_pilot_v3_evidence.jsonl', evidence)
    print(json.dumps({
        'candidate_count': len(candidates),
        'by_provisional_partition_and_method': {f'{p}/{subset}/{kind}': sum(x['provisional_partition'] == p and x['donor_official_subset'] == subset and x['construction_type'] == kind for x in candidates) for p, subset, kind in strata},
        'eligible_source_rows_excluding_window_overruns': len(eligible),
        'cross_target_pools': {s: len({x['vid'] for x in rows}) for s, rows in subset_video_rows.items()},
        'all_candidates_need_A_and_blind_B_review': True,
        'target_duration_matches_target_video': all((x.get('target_duration') == x.get('duration')) for x in candidates if x['construction_type'] == 'cross_video'),
        'status': 'pilot only; not eligible for release'
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
