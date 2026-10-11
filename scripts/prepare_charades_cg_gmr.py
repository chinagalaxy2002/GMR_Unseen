#!/usr/bin/env python3
"""Prepare source-faithful Charades-CG-GMR rows and a deterministic 200-row pilot."""
import hashlib
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1'
SOURCE = BASE / 'source'
STAGING = BASE / 'work/staging'
SEED = 3407


def read(name):
    return json.loads((SOURCE / name).read_text(encoding='utf-8'))


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in rows), encoding='utf-8')


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def expand(filename, subset, official_split, data):
    result = []
    for vid, payload in data.items():
        for i, query in enumerate(payload['sentences']):
            row = {
                'source_file': filename, 'source_commit': '2372337e9166b8e26b83ce936a8474c6ae127290',
                'source_vid': vid, 'source_sentence_index': i, 'source_qid': f'{filename}:{vid}:{i}',
                'vid': vid, 'query': query, 'relevant_windows': [payload['timestamps'][i]],
                'duration': payload['duration'], 'official_subset': subset,
                'official_split': official_split,
                'official_compositions': payload.get('novels', [{}] * len(payload['sentences']))[i],
                'official_novel_words': payload.get('news', [{}] * len(payload['sentences']))[i],
                'exist_label': 1,
            }
            row['input_hash'] = digest(row)
            result.append(row)
    return result


def hard_variant(query):
    """Create one-factor candidate variants; every variant remains pending agent review."""
    changes = [
        (r'\bopens?\b', 'closes', 'action'), (r'\bcloses?\b', 'opens', 'action'),
        (r'\bturns on\b', 'turns off', 'action'), (r'\bturns off\b', 'turns on', 'action'),
        (r'\bsits?\b', 'stands', 'action'), (r'\bstands?\b', 'sits', 'action'),
        (r'\bdrinks?\b', 'eats', 'action'), (r'\beat(?:s|ing)?\b', 'drinks', 'action'),
        (r'\bbook\b', 'phone', 'object'), (r'\bphone\b', 'book', 'object'),
        (r'\bglass\b', 'cabinet', 'object'), (r'\bcabinet\b', 'glass', 'object'),
        (r'\bsofa\b', 'table', 'object'), (r'\btable\b', 'sofa', 'object'),
        (r'\binto\b', 'out of', 'relation'), (r'\bout of\b', 'into', 'relation'),
        (r'\bon the\b', 'under the', 'relation'),
    ]
    for pattern, replacement, factor in changes:
        changed, count = re.subn(pattern, replacement, query, count=1, flags=re.I)
        if count and changed != query:
            return changed, factor
    return None, None


def main():
    train = expand('train.json', 'official_train', 'train_pool', read('train.json'))
    trivial = expand('test_trivial.json', 'test_trivial', 'test', read('test_trivial.json'))
    novel = expand('novel_composition.json', 'novel_composition', 'test', read('novel_composition.json'))
    novel_word = expand('novel_word.json', 'novel_word', 'test', read('novel_word.json'))
    rng = random.Random(SEED)
    train_vids = sorted({x['vid'] for x in train})
    val_vids = set(rng.sample(train_vids, round(len(train_vids) * .10)))
    for row in train:
        row['video_split'] = 'val_seen' if row['vid'] in val_vids else 'train'
        row['audited_partition'] = 'pending_agent_review'
    for row in trivial:
        row['video_split'] = 'test'
        row['audited_partition'] = 'pending_agent_review'
    for row in novel:
        row['video_split'] = 'test'
        row['audited_partition'] = 'pending_agent_review'
    for row in novel_word:
        row['video_split'] = 'test_novel_word'
        row['audited_partition'] = 'novel_word_separate_pending_agent_review'
    write_jsonl(STAGING / 'positive_source_rows.jsonl', train + trivial + novel + novel_word)
    # A pilot is a protocol exercise only. Seen/Unseen here are provisional source strata.
    pools = {
        ('Seen', 'cross_video'): [x for x in trivial if x['query']],
        ('Unseen', 'cross_video'): [x for x in novel if x['query']],
        ('Seen', 'hard_same_video'): [x for x in trivial if hard_variant(x['query'])[0]],
        ('Unseen', 'hard_same_video'): [x for x in novel if hard_variant(x['query'])[0]],
    }
    pilot, all_refs = [], train + trivial + novel
    for (partition, kind), pool in pools.items():
        pool = sorted(pool, key=lambda x: x['source_qid'])
        chosen = rng.sample(pool, min(50, len(pool)))
        for idx, donor in enumerate(chosen):
            row = dict(donor)
            row.update({'candidate_id': f'pilot-{partition.lower()}-{kind}-{idx:03d}',
                        'construction_type': kind, 'audited_partition': partition,
                        'evidence_level': 'text_audited_pending', 'generated_by': 'primary_agent'})
            if kind == 'cross_video':
                candidates = sorted({x['vid'] for x in all_refs if x['video_split'] == 'test' and x['vid'] != donor['vid']})
                if not candidates:
                    row['target_vid'] = None
                    row['generation_status'] = 'retry_no_target_video'
                else:
                    row['target_vid'] = candidates[(idx * 37 + (0 if partition == 'Seen' else 7)) % len(candidates)]
                    row['vid'] = row['target_vid']
                    row['source_vid'] = donor['vid']
                    row['relevant_windows'] = []
                    row['source_relevant_windows'] = donor['relevant_windows']
                    row['exist_label'] = 0
                    row['generation_status'] = 'candidate'
            else:
                variant, factor = hard_variant(donor['query'])
                row['query'] = variant
                row['changed_factor'] = factor
                row['source_vid'] = donor['vid']
                row['source_relevant_windows'] = donor['relevant_windows']
                row['relevant_windows'] = []
                row['exist_label'] = 0
                row['generation_status'] = 'candidate'
            row['input_hash'] = digest(row)
            pilot.append(row)
    write_jsonl(STAGING / 'pilot_candidates_unscored.jsonl', pilot)
    # Evidence includes every positive text known for the candidate video.
    by_vid = {}
    for x in all_refs:
        by_vid.setdefault(x['vid'], []).append({'source_qid': x['source_qid'], 'query': x['query'], 'source_file': x['source_file']})
    evidence = []
    for row in pilot:
        evidence.append({'candidate': row, 'same_video_positive_evidence': by_vid.get(row.get('target_vid') or row['vid'], []),
                         'donor_positive': {'source_qid': row['source_qid'], 'query': next((x['query'] for x in train + trivial + novel if x['source_qid'] == row['source_qid']), row['query'])},
                         'instruction': 'Judge only this item from the supplied source evidence. No predictions or metric results are provided.'})
    (STAGING / 'pilot_evidence.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False)+'\n' for x in evidence), encoding='utf-8')
    print(json.dumps({'positive_rows': len(train)+len(trivial)+len(novel)+len(novel_word),
                      'split_videos': {'train': len(train_vids)-len(val_vids), 'val_seen': len(val_vids),
                                       'test_trivial': len({x['vid'] for x in trivial}), 'novel_composition': len({x['vid'] for x in novel})},
                      'pilot': {f'{p}/{k}': sum(x['audited_partition']==p and x['construction_type']==k for x in pilot) for p,k in pools},
                      'candidate_records':len(pilot)}, indent=2))


if __name__ == '__main__':
    main()
