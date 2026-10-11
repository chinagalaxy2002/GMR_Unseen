"""Freeze C3_CG inputs and link verified exact-text token features."""
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

from common import ROOT, REPO, RELEASE, NATIVE, VIDEO, digest, read_rows, save_json


def prepare():
    group = 'C3_CG'
    target = ROOT / 'groups' / group / 'release' / group
    target.mkdir(parents=True, exist_ok=True)
    for p in (RELEASE / 'splits' / group).iterdir():
        dest = target / p.name
        if dest.exists() and digest(dest) != digest(p):
            raise ValueError('Frozen release changed: ' + str(p))
        shutil.copy2(p, dest)
    parts = {n: read_rows(target / (n + '.jsonl')) for n in ('train', 'val_seen', 'test')}
    for a, b in [('train', 'val_seen'), ('train', 'test'), ('val_seen', 'test')]:
        assert not ({r['vid'] for r in parts[a]} & {r['vid'] for r in parts[b]})
    assert all(r['partition'] in ('S+', 'S-') for r in parts['train'] + parts['val_seen'])
    rows = [r for rr in parts.values() for r in rr]
    for rr in parts.values():
        assert len({str(r['qid']) for r in rr}) == len(rr)
    for row in rows:
        assert bool(row['relevant_windows']) == bool(row['exist_label'])
        for folder in ('vid_clip', 'vid_slowfast'):
            assert (VIDEO / folder / (row['vid'] + '.npz')).is_file(), row['vid']
    prior_path = ROOT.parent / 'v3_balanced_baselines_20261010/TEXT_FEATURE_MANIFEST.json'
    prior = {}
    for rec in json.loads(prior_path.read_text()):
        prior.setdefault(rec['query_sha256'], rec)
    texts = {hashlib.sha256(r['query'].encode()).hexdigest(): r['query'] for r in rows}
    missing = sorted(set(texts) - set(prior))
    generated = ROOT / 'features/generated_tokens'
    generated.mkdir(parents=True, exist_ok=True)
    encode = [h for h in missing if not (generated / (h + '.npz')).exists()]
    if encode:
        import numpy as np
        import torch
        config = json.loads((RELEASE / 'negative_generation.json').read_text())['clip']
        sys.path.insert(0, config['clip_code_path'])
        import clip
        model, _ = clip.load(config['weights_path'], device='cuda:0', jit=False)
        model.eval()
        with torch.no_grad():
            for start in range(0, len(encode), 64):
                hashes = encode[start:start+64]
                tokens = clip.tokenize([texts[h] for h in hashes]).to('cuda:0')
                output = model.encode_text(tokens)
                assert isinstance(output, dict) and 'last_hidden_state' in output
                states = output['last_hidden_state'].float().cpu().numpy()
                lengths = (tokens != 0).sum(1).tolist()
                for h, state, length in zip(hashes, states, lengths):
                    np.savez_compressed(generated / (h + '.npz'), last_hidden_state=state[:length])
                print('Encoded new texts', min(start+64, len(encode)), '/', len(encode), flush=True)
        del model
        torch.cuda.empty_cache()
        save_json(ROOT / 'TEXT_ENCODER.json', config)
    shared = ROOT / 'features/clip_text'
    shared.mkdir(parents=True, exist_ok=True)
    verified = {}
    manifest = []
    for row in rows:
        h = hashlib.sha256(row['query'].encode()).hexdigest()
        source = Path(prior[h]['source']).resolve() if h in prior else generated / (h + '.npz')
        if source not in verified:
            verified[source] = digest(source)
        if h in prior:
            assert verified[source] == prior[h]['feature_sha256']
        dest = shared / ('qid' + str(row['qid']) + '.npz')
        if dest.is_symlink():
            assert dest.resolve() == source.resolve()
        elif not dest.exists():
            dest.symlink_to(source.resolve())
        manifest.append(dict(qid=row['qid'], query_sha256=h, source=str(source), feature_sha256=verified[source]))
    feat = ROOT / 'groups' / group / 'features' / group
    feat.mkdir(parents=True, exist_ok=True)
    for name, src in [('clip_text', shared), ('val_seen.jsonl', target / 'val_seen.jsonl')]:
        if not (feat / name).exists():
            (feat / name).symlink_to(src)
    save_json(ROOT / 'DATA_AUDIT.json', dict(release=str(RELEASE), groups={group: {
        'counts': {n: dict(Counter(r['partition'] for r in rr)) for n, rr in parts.items()},
        'videos': {n: len({r['vid'] for r in rr}) for n, rr in parts.items()},
        'sha256': {p.name: digest(p) for p in target.iterdir() if p.is_file()}}},
        unique_texts=len(texts), encoded_new_texts=len(missing), video_disjoint=True,
        seen_only_train=True, exact_text_feature_identity=True, seen_test_available=False))
    save_json(ROOT / 'TEXT_FEATURE_MANIFEST.json', manifest)
    save_json(ROOT / 'SOURCE_MANIFEST.json', {str(p.relative_to(NATIVE)): digest(p)
        for p in NATIVE.rglob('*') if p.is_file() and '__pycache__' not in p.parts})
    print('Prepared C3_CG:', {n: len(rr) for n, rr in parts.items()}, flush=True)


if __name__ == '__main__':
    prepare()
