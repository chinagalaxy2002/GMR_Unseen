"""D1 auxiliary input sensitivity; no counterfactual accuracy or model updates."""
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

from phase2 import HERE, STAGE, dump, rows, sha

sys.path.insert(0, str(HERE / 'code'))


def main():
    import numpy as np
    import torch
    from torch.utils.data import DataLoader
    import queue_worker as w

    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--family', required=True)
    parser.add_argument('--method', default='baseline')
    args = parser.parse_args()
    dest = STAGE / 'diagnostics' / args.family / args.method
    output = dest / 'INPUT_SENSITIVITY.json'
    if output.exists():
        raise RuntimeError(f'Refusing to overwrite {output}')
    torch.set_num_threads(4)
    torch.manual_seed(3407)
    ckpath = args.run / 'best.ckpt'
    ck = torch.load(ckpath, map_location='cpu', weights_only=False)
    opt = ck['opt']
    opt.device = 'cuda:0'
    opt.num_workers = 0
    ev, dsmod = w.modules('qd')
    model, _, *_ = w.make_model(opt, ev, args.method, 'qd')
    model.load_state_dict(ck['model'])
    model.eval()
    ds = w.dataset(opt, dsmod, args.run / 'views/pseudo.jsonl', 'qd', labels=False)
    # Audit real branch dimensions rather than assuming CLIP/SlowFast sizes.
    stem = dsmod.video_id_to_feature_stem(ds.data[0]['vid'])
    dims = []
    for directory in opt.v_feat_dirs:
        f = Path(directory) / (stem + '.npz')
        if f.exists():
            with np.load(f) as pack:
                dim = pack['features'].shape[-1]
        else:
            pack = torch.load(Path(directory) / (stem + '.pt'), map_location='cpu', weights_only=False)
            dim = (pack['features'] if isinstance(pack, dict) else pack).shape[-1]
        dims.append(int(dim))
    branches = []
    offset = 0
    for directory, dim in zip(opt.v_feat_dirs, dims):
        name = Path(directory).name
        assert name in ('vid_clip', 'vid_slowfast'), name
        branches.append((name, offset, offset + dim))
        offset += dim
    modes = ['identity', 'zero_visual', 'shuffle_time', 'zero_clip', 'zero_slowfast']
    manifest = {
        'state': 'frozen_before_inference', 'seed': 3407, 'training_updates': 0,
        'checkpoint_sha256': sha(ckpath), 'checkpoint_epoch_zero_based': ck['epoch'],
        'source_sha256': sha(Path(__file__)),
        'view_sha256': sha(args.run / 'views/pseudo.jsonl'),
        'qids': [str(r['qid']) for r in ds.data], 'branches': branches, 'modes': modes,
        'perturbation': 'zero normalized visual channels; shuffle valid visual rows only; masks, padded rows, text and TEF preserved',
        'permutation': 'same permutation for each video and all queries; CPU generator seeded by SHA256(seed|vid|length)',
        'selection': 'all existing pseudo rows, original order; no outcome-based selection',
        'accuracy_under_perturbation': 'not computed',
    }
    dump(dest / 'INPUT_SENSITIVITY_MANIFEST.json', manifest)

    def readout(out):
        score = out['pred_logits'].softmax(-1)[..., 0]
        idx = score.argmax(-1)
        cxw = out['pred_spans'][torch.arange(len(idx), device=idx.device), idx]
        span = torch.stack((cxw[:, 0] - cxw[:, 1] / 2, cxw[:, 0] + cxw[:, 1] / 2), -1).clamp(0, 1)
        return out['pred_exist_logits'].sigmoid().cpu().numpy(), idx.cpu().numpy(), span.cpu().numpy()

    data = {m: [] for m in modes}
    identity_max = 0.0
    with torch.inference_mode():
        for meta, batch in DataLoader(ds, batch_size=16, num_workers=0, collate_fn=dsmod.start_end_collate):
            inputs, _ = dsmod.prepare_batch_inputs(batch, 'cuda:0')
            assert inputs['src_vid'].shape[-1] == offset + (2 if ds.use_tef else 0)
            base = readout(model(**inputs))
            for mode in modes:
                changed = dict(inputs)
                v = inputs['src_vid'].clone()
                if mode == 'zero_visual':
                    v[..., :offset] = 0
                elif mode in ('zero_clip', 'zero_slowfast'):
                    branch = 'vid_clip' if mode == 'zero_clip' else 'vid_slowfast'
                    start, end = next((a, b) for n, a, b in branches if n == branch)
                    v[..., start:end] = 0
                elif mode == 'shuffle_time':
                    for i, r in enumerate(meta):
                        length = int(inputs['src_vid_mask'][i].sum())
                        seed = int.from_bytes(hashlib.sha256(f"3407|{r['vid']}|{length}".encode()).digest()[:8], 'little') % (2**63)
                        perm = torch.randperm(length, generator=torch.Generator().manual_seed(seed)).to(v.device)
                        v[i, :length, :offset] = inputs['src_vid'][i, perm, :offset]
                changed['src_vid'] = v
                result = readout(model(**changed))
                if mode == 'identity':
                    identity_max = max(identity_max, float(np.max(np.abs(result[0] - base[0]))), float(np.max(np.abs(result[2] - base[2]))))
                for i, r in enumerate(meta):
                    data[mode].append({
                        'qid': str(r['qid']), 'vid': r['vid'],
                        'exist_score_original': float(base[0][i]), 'exist_score_perturbed': float(result[0][i]),
                        'exist_abs_delta': float(abs(result[0][i] - base[0][i])),
                        'raw_top_slot_changed': bool(result[1][i] != base[1][i]),
                        'raw_top_span_original_normalized': base[2][i].tolist(),
                        'raw_top_span_perturbed_normalized': result[2][i].tolist(),
                        'raw_top_endpoint_mean_abs_delta': float(np.abs(result[2][i] - base[2][i]).mean()),
                    })
    assert identity_max <= 1e-6, f'Identity control failed: {identity_max}'
    unique = sorted({r['vid'] for r in ds.data})
    rng = np.random.default_rng(3407)
    weights = [collections.Counter(rng.choice(unique, len(unique), replace=True)) for _ in range(1000)]
    summaries = {}
    for mode, records in data.items():
        summaries[mode] = {}
        for key in ('exist_abs_delta', 'raw_top_slot_changed', 'raw_top_endpoint_mean_abs_delta'):
            grouped = collections.defaultdict(list)
            for r in records:
                grouped[r['vid']].append(float(r[key]))
            vals = np.array([np.mean(grouped[v]) for v in unique])
            samples = [sum(vals[i] * weight[v] for i, v in enumerate(unique)) / len(unique) for weight in weights]
            summaries[mode][key] = {
                'row_mean': float(np.mean([r[key] for r in records])),
                'video_mean': float(vals.mean()),
                'video_bootstrap_ci95': np.quantile(samples, [.025, .975]).tolist(),
            }
    for mode, records in data.items():
        path = dest / f'sensitivity_{mode}.jsonl'
        path.write_text(''.join(json.dumps(r) + '\n' for r in records))
    dump(output, {
        'state': 'completed', 'training_updates': 0, 'rows': len(ds), 'videos': len(unique),
        'manifest_sha256': sha(dest / 'INPUT_SENSITIVITY_MANIFEST.json'),
        'identity_max_abs_error': identity_max, 'summaries': summaries,
        'limitations': 'Sensitivity of frozen model, not necessity/causal proof. Zeroing is out of distribution; shuffle preserves positions. No perturbed-label AUROC, R1, FRR or RR computed. Raw top span before official temporal postprocessing; original official gate is a scalar per row and does not change exact-precision slot ranking.',
    })
    print(json.dumps({'state': 'completed', 'output': str(output), 'rows': len(ds)}))


if __name__ == '__main__':
    main()
