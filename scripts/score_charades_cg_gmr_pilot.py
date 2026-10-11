#!/usr/bin/env python3
"""Score pilot cross-video candidates against all supplied positive target annotations."""
import hashlib
import json
import sys
import types
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1'
CLIP_CODE = Path('/home/guoxiangyu/paper/新建文件夹/MomentofUntruth/UniVTG-NA/run_on_video')
WEIGHTS = Path('/home/guoxiangyu/Beyond_Caption-Based_Queries_for_Video_Moment_Retrieval/experiments_and_data/evaluations/flash_vtg_subset_consistency_eval/models/ViT-B-32.pt')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    staging = BASE / 'work/staging'
    rows = [json.loads(x) for x in (staging / 'pilot_candidates_unscored.jsonl').read_text().splitlines() if x]
    evidence = [json.loads(x) for x in (staging / 'positive_source_rows.jsonl').read_text().splitlines() if x]
    rows = [x for x in rows if x['construction_type'] == 'cross_video' and x.get('target_vid')]
    refs = {}
    test_vids = {x['vid'] for x in evidence if x['video_split'] in ('test', 'test_novel_word')}
    for x in evidence:
        if x['vid'] in test_vids:
            refs.setdefault(x['vid'], []).append(x['query'])
    texts = sorted({x['query'] for x in evidence} | {x['query'] for x in rows})
    if any(not text.isascii() for text in texts):
        raise ValueError('The ftfy identity fallback is only valid for this verified ASCII source.')
    sys.path.insert(0, str(CLIP_CODE / 'clip'))
    # Charades queries are ASCII; ftfy is only used for Unicode repair in the
    # tokenizer. Keep the official tokenizer and supply an identity repair for
    # this ASCII-only source rather than silently changing BPE tokenization.
    ftfy_stub = types.ModuleType('ftfy')
    ftfy_stub.fix_text = lambda value: value
    sys.modules['ftfy'] = ftfy_stub
    from simple_tokenizer import SimpleTokenizer
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    # Load the frozen TorchScript checkpoint directly. The vendored CLIP image
    # preprocessing imports torchvision, which is irrelevant for text encoding.
    model = torch.jit.load(str(WEIGHTS), map_location=device).eval()
    tokenizer = SimpleTokenizer()
    sot, eot = tokenizer.encoder['<|startoftext|>'], tokenizer.encoder['<|endoftext|>']
    device = next(model.parameters()).device
    vectors = {}
    with torch.inference_mode():
        for start in range(0, len(texts), 256):
            batch = texts[start:start+256]
            tokens = torch.zeros((len(batch), 77), dtype=torch.long, device=device)
            for i, text in enumerate(batch):
                ids = [sot] + tokenizer.encode(text) + [eot]
                if len(ids) > 77:
                    raise ValueError(f'CLIP token limit exceeded; no truncation allowed: {text}')
                tokens[i, :len(ids)] = torch.tensor(ids, device=device)
            out = model.encode_text(tokens)
            out = out['pooler_output'] if isinstance(out, dict) else out
            out = torch.nn.functional.normalize(out.float(), dim=-1).cpu().numpy()
            vectors.update(zip(batch, out))
    scores = []
    for x in rows:
        targets = sorted(refs)
        q = vectors[x['query']]
        ranked = []
        for vid in targets:
            target_refs = refs[vid]
            maximum = max(float(q @ vectors[t]) for t in target_refs)
            ranked.append((maximum, vid, len(target_refs)))
        ranked.sort(key=lambda z: (z[0], z[1]))
        rank_by_vid = {vid: (i + 1, score, count) for i, (score, vid, count) in enumerate(ranked)}
        rank, maximum, ref_count = rank_by_vid[x['target_vid']]
        scores.append({'candidate_id': x['candidate_id'], 'input_hash': x['input_hash'], 'status': 'scored',
                       'target_vid': x['target_vid'], 'max_clip_cosine': maximum,
                       'target_reference_count': ref_count, 'eligible_target_video_count': len(ranked),
                       'rank_within_eligible_videos': rank, 'rank_fraction': rank / len(ranked),
                       'in_lowest_half': rank <= len(ranked) // 2,
                       'selection_rule': 'CLIP max similarity to all positive target-video query annotations; candidate passes score screen iff target video is in the lower-scoring half. Ties break by video ID.'})
    out = staging / 'pilot_clip_scores.jsonl'
    out.write_text(''.join(json.dumps(x, ensure_ascii=False)+'\n' for x in scores), encoding='utf-8')
    meta = {'encoder': 'OpenAI CLIP ViT-B/32', 'weights': str(WEIGHTS), 'weights_sha256': sha(WEIGHTS),
            'clip_code': str(CLIP_CODE), 'clip_model_sha256': sha(CLIP_CODE / 'clip/model.py'),
            'tokenizer_sha256': sha(CLIP_CODE / 'clip/simple_tokenizer.py'), 'torch': torch.__version__,
            'numpy': np.__version__, 'device': str(device), 'unique_texts': len(texts),
            'candidate_count': len(scores), 'unicode_repair': 'identity fallback; validated all input queries are ASCII',
            'truncation': False,
            'evidence_scope': 'official query annotation text for target video; not video review'}
    (staging / 'pilot_clip_metadata.json').write_text(json.dumps(meta, indent=2)+'\n')
    print(json.dumps({'meta': meta, 'scored': sum(x.get('status')=='scored' for x in scores),
                      'lowest_half': sum(bool(x.get('in_lowest_half')) for x in scores)}, indent=2))


if __name__ == '__main__':
    main()
