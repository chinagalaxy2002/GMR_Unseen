#!/usr/bin/env python3
"""Apply the prescribed CLIP lower-half screen within the matching test subset."""
import hashlib
import json
import sys
import types
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1'
STAGING = BASE / 'work/staging'
CLIP_CODE = Path('/home/guoxiangyu/paper/新建文件夹/MomentofUntruth/UniVTG-NA/run_on_video')
WEIGHTS = Path('/home/guoxiangyu/Beyond_Caption-Based_Queries_for_Video_Moment_Retrieval/experiments_and_data/evaluations/flash_vtg_subset_consistency_eval/models/ViT-B-32.pt')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def read(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def main():
    candidates = read(STAGING / 'corrected_pilot_v3_candidates_unscored.jsonl')
    source = read(STAGING / 'positive_source_rows.jsonl')
    rows = [x for x in candidates if x['construction_type'] == 'cross_video' and x.get('target_vid')]
    if any(not x['query'].isascii() for x in source) or any(not x['query'].isascii() for x in rows):
        raise ValueError('The identity Unicode repair is valid only for the verified ASCII inputs.')

    subset_videos, refs = {}, {}
    for row in source:
        refs.setdefault(row['vid'], []).append(row['query'])
        if row['official_subset'] in {'test_trivial', 'novel_composition'}:
            subset_videos.setdefault(row['official_subset'], set()).add(row['vid'])

    texts = sorted({x['query'] for x in source} | {x['query'] for x in rows})
    sys.path.insert(0, str(CLIP_CODE / 'clip'))
    ftfy_stub = types.ModuleType('ftfy')
    ftfy_stub.fix_text = lambda value: value
    sys.modules['ftfy'] = ftfy_stub
    from simple_tokenizer import SimpleTokenizer
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    model = torch.jit.load(str(WEIGHTS), map_location=device).eval()
    tokenizer = SimpleTokenizer()
    sot, eot = tokenizer.encoder['<|startoftext|>'], tokenizer.encoder['<|endoftext|>']
    device = next(model.parameters()).device
    vectors = {}
    with torch.inference_mode():
        for start in range(0, len(texts), 256):
            batch = texts[start:start + 256]
            tokens = torch.zeros((len(batch), 77), dtype=torch.long, device=device)
            for i, text in enumerate(batch):
                ids = [sot] + tokenizer.encode(text) + [eot]
                if len(ids) > 77:
                    raise ValueError(f'CLIP token limit exceeded; no truncation allowed: {text}')
                tokens[i, :len(ids)] = torch.tensor(ids, device=device)
            output = model.encode_text(tokens)
            output = output['pooler_output'] if isinstance(output, dict) else output
            output = torch.nn.functional.normalize(output.float(), dim=-1).cpu().numpy()
            vectors.update(zip(batch, output))

    results = []
    for row in rows:
        subset = row['donor_official_subset']
        eligible = sorted(v for v in subset_videos[subset] if v != row['source_vid'])
        ranked = []
        qvec = vectors[row['query']]
        for vid in eligible:
            score = max(float(qvec @ vectors[ref]) for ref in refs[vid])
            ranked.append((score, vid, len(refs[vid])))
        ranked.sort(key=lambda x: (x[0], x[1]))
        rank_by_vid = {vid: (rank, score, nrefs) for rank, (score, vid, nrefs) in enumerate(ranked, 1)}
        rank, score, nrefs = rank_by_vid[row['target_vid']]
        results.append({
            'candidate_id': row['candidate_id'], 'input_hash': row['input_hash'],
            'target_vid': row['target_vid'], 'matching_official_subset': subset,
            'max_clip_cosine': score, 'target_reference_count': nrefs,
            'eligible_target_video_count': len(ranked), 'rank_within_subset_videos': rank,
            'rank_fraction': rank / len(ranked), 'in_lowest_half': rank <= len(ranked) // 2,
            'selection_rule': 'Within donor official query subset only, compare q with every target video annotation across available source files; score=max cosine; proceed iff in lower-scoring half; ties by video id. Ranking is not absence evidence.'
        })

    (STAGING / 'corrected_pilot_v3_clip_scores.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in results), encoding='utf-8')
    meta = {
        'encoder': 'OpenAI CLIP ViT-B/32', 'weights': str(WEIGHTS), 'weights_sha256': sha(WEIGHTS),
        'clip_code': str(CLIP_CODE), 'clip_model_sha256': sha(CLIP_CODE / 'clip/model.py'),
        'tokenizer_sha256': sha(CLIP_CODE / 'clip/simple_tokenizer.py'), 'torch': torch.__version__,
        'numpy': np.__version__, 'device': str(device), 'unique_texts': len(texts),
        'cross_video_candidates': len(rows), 'unicode_repair': 'identity fallback; ASCII verified',
        'truncation': False, 'target_pool': 'matching official test_trivial or novel_composition only',
        'evidence': 'all supplied query annotations for each eligible target video across all source subsets; no video absence claim'
    }
    (STAGING / 'corrected_pilot_v3_clip_metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'scored': len(results), 'lower_half': sum(x['in_lowest_half'] for x in results), 'metadata': meta}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
