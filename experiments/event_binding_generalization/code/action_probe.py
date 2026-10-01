"""Stage A1: frozen SlowFast segment-to-verb diagnostic, S_train fit only."""
from common import *
import collections
import torch
from torch import nn

NAMES = ['motion_temporal', 'motion_mean', 'motion_static', 'appearance_mean']

def main():
    assert (BASE / 'EXECUTION_FREEZE.json').exists()
    assert not (BASE / 'audit/ACTION_PROBE.json').exists()
    status('action', 'running')
    torch.set_num_threads(4)
    rng = np.random.default_rng(SEED)
    projections = {d: (rng.normal(size=(d, 128)) / np.sqrt(128)).astype(np.float32) for d in [512, 2304, 6912]}
    np.savez(BASE / 'runs/minimal_validation/action_projections.npz', **{str(k): v for k, v in projections.items()})
    cache = {}
    results = {}
    for fam in FAMILIES:
        rr = {s: rows(fam, s) for s in ['train', 'seen', 'pseudo']}
        data = {}
        for split, rs in rr.items():
            feats = {k: [] for k in NAMES}; meta = []; missing = []
            for x in rs:
                if x['exist_label'] != 1:
                    continue
                if x['vid'] not in cache:
                    cache[x['vid']] = visual(x['vid'])
                a, m = cache[x['vid']]; mask = gtmask(x, len(m))
                if not mask.any() or not x['semantic_graph'].get('action_class'):
                    missing.append(x['qid']); continue
                aa, mm = a[mask], m[mask]
                # Use vectorized raw-summary projections; projection has no fitted labels.
                feats['motion_mean'].append(mm.mean(0) @ projections[2304])
                feats['motion_static'].append(mm[len(mm)//2] @ projections[2304])
                feats['appearance_mean'].append(aa.mean(0) @ projections[512])
                feats['motion_temporal'].append(np.concatenate([mm.mean(0), mm.std(0), mm[-1]-mm[0]]) @ projections[6912])
                meta.append({'qid': str(x['qid']), 'vid': x['vid'], 'verb': x['semantic_graph']['action_class'], 'object': x['semantic_graph'].get('object_concept'), 'gt_bins': int(mask.sum())})
            data[split] = {'features': {k: np.array(v, dtype=np.float32) for k, v in feats.items()}, 'meta': meta, 'missing': missing}
        counts = collections.Counter(x['verb'] for x in data['train']['meta'])
        vocab = sorted(k for k, n in counts.items() if n >= 10)
        lookup = {v: i for i, v in enumerate(vocab)}
        train_mask = np.array([x['verb'] in lookup for x in data['train']['meta']])
        seen_mask = np.array([x['verb'] in lookup for x in data['seen']['meta']])
        ytr = torch.tensor([lookup[x['verb']] for x in data['train']['meta'] if x['verb'] in lookup], device='cuda')
        yva = np.array([lookup[x['verb']] for x in data['seen']['meta'] if x['verb'] in lookup])
        weights = torch.bincount(ytr, minlength=len(vocab)).float().clamp_min(1).reciprocal()
        weights /= weights.mean()
        result = {'vocab_from_train_only': vocab, 'class_counts': counts, 'coverage': {}, 'probes': {}}
        for split, dd in data.items():
            ncovered = sum(x['verb'] in lookup for x in dd['meta'])
            result['coverage'][split] = {'usable_positive_segments': len(dd['meta']), 'in_train_vocab': ncovered, 'out_of_vocab': len(dd['meta']) - ncovered, 'unusable_qids': dd['missing'], 'out_of_vocab_classes': dict(collections.Counter(x['verb'] for x in dd['meta'] if x['verb'] not in lookup))}
        for name in NAMES:
            torch.manual_seed(SEED)
            xtr0 = data['train']['features'][name][train_mask]
            mean = xtr0.mean(0); scale = np.maximum(xtr0.std(0), 1e-5)
            xtr = torch.tensor((xtr0-mean)/scale, device='cuda')
            xva = torch.tensor((data['seen']['features'][name][seen_mask]-mean)/scale, device='cuda')
            model = nn.Linear(128, len(vocab)).cuda()
            opt = torch.optim.Adam(model.parameters(), lr=.01, weight_decay=.0001)
            best = -1; history = []; best_state = None
            for epoch in range(20):
                model.train(); order = torch.randperm(len(ytr), device='cuda')
                for idx in order.split(512):
                    opt.zero_grad(); loss = nn.functional.cross_entropy(model(xtr[idx]), ytr[idx], weight=weights)
                    loss.backward(); opt.step()
                with torch.no_grad():
                    pred = model(xva).argmax(1).cpu().numpy()
                balanced = float(np.mean([np.mean(pred[yva == c] == c) for c in np.unique(yva)]))
                history.append({'epoch': epoch+1, 'seen_balanced_accuracy': balanced})
                if balanced > best:
                    best = balanced; best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}; best_epoch = epoch+1
            model.load_state_dict(best_state); model.eval()
            torch.save({'state': best_state, 'mean': mean, 'scale': scale, 'vocab': vocab, 'selected_epoch': best_epoch}, BASE / f'runs/minimal_validation/{fam}_action_{name}.pt')
            predictions = []
            for split, dd in data.items():
                inp = torch.tensor((dd['features'][name]-mean)/scale, device='cuda')
                with torch.no_grad():
                    pp = model(inp).argmax(1).cpu().numpy()
                predictions.extend({**x, 'split': split, 'in_train_vocab': x['verb'] in lookup, 'predicted': vocab[p], 'correct': bool(vocab[p] == x['verb']) if x['verb'] in lookup else None} for x, p in zip(dd['meta'], pp))
            jsonl(f'runs/minimal_validation/{fam}_action_{name}_predictions.jsonl', predictions)
            result['probes'][name] = {'parameters': 129*len(vocab), 'seen_balanced_accuracy': best, 'selected_epoch': best_epoch, 'history': history, 'seen_accuracy': float(np.mean([x['correct'] for x in predictions if x['split']=='seen' and x['in_train_vocab']]))}
            print(fam, name, 'seen balanced', round(best, 4), flush=True)
        # Paired seen classification diagnostics using common video resamples; OOV not scored.
        valmeta = [x for x in data['seen']['meta'] if x['verb'] in lookup]
        videos = sorted({x['vid'] for x in valmeta}); vi = {v:i for i,v in enumerate(videos)}
        ids = np.array([vi[x['vid']] for x in valmeta]); yy = np.array([x['verb'] for x in valmeta])
        correct = {k: np.array([x['correct'] for x in read(BASE / f'runs/minimal_validation/{fam}_action_{k}_predictions.jsonl') if x['split']=='seen' and x['in_train_vocab']], dtype=float) for k in NAMES}
        boots = {k:[] for k in NAMES[1:]}; brng = np.random.default_rng(SEED)
        for _ in range(1000):
            w = np.bincount(brng.integers(len(videos), size=len(videos)), minlength=len(videos))[ids]
            acc = {k: np.mean([np.average(c[yy==label], weights=w[yy==label]) for label in sorted(set(yy)) if w[yy==label].sum()>0]) for k,c in correct.items()}
            for k in boots:
                boots[k].append(float(acc['motion_temporal']-acc[k]))
        result['paired_seen_balanced_temporal_minus_control_ci95'] = {k:ci(v) for k,v in boots.items()}
        result['interpretation'] = 'GT segment supervised readout of seen verbs only; SlowFast static retains clip-internal motion; success does not certify held-out verb readability or object-shortcut-free action understanding.'
        results[fam] = result
        dump('audit/ACTION_PROBE_PROGRESS.json', results)
    dump('audit/ACTION_PROBE.json', results)
    status('action', 'completed', fits=12, held_out_class_training=False)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        status('action', 'failed', error=repr(e)); raise
