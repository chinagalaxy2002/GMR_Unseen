"""Frozen-model diagnostics, not retrained ablations or test-selected models."""
import sys
sys.dont_write_bytecode = True
import numpy as np
import torch
from torch.nn import functional as F
import audit_sdcv as a

def evaluate(m, r, route_mode=None):
    x = torch.tensor(r)
    det = .5 * (x[:, :3] * F.softmax(m.w_det, 0)).sum(1) + .5 * x[:, :3].median(1).values
    sub = torch.stack([(x[:, [8, 9, 12]] * F.softmax(m.w_kin, 0)).sum(1),
                       (x[:, [6, 5, 13, 3]] * F.softmax(m.w_obj, 0)).sum(1),
                       (x[:, [5, 7, 12, 4]] * F.softmax(m.w_man, 0)).sum(1)], 1)
    props = x[:, [3, 4, 5, 6, 7, 8, 9, 12, 13]]
    route = m.semantic_router(props).softmax(1)
    if route_mode == 'uniform':
        route = torch.ones_like(route) / 3
    elif isinstance(route_mode, int):
        route = torch.zeros_like(route)
        route[:, route_mode] = 1
    ev = (sub * route).sum(1)
    disc = (x[:, 0] - x[:, 1]).abs() + (x[:, 1] - x[:, 2]).abs()
    ctx = torch.stack([det, ev, disc, x[:, 5], x[:, 6], x[:, 8], x[:, 10], x[:, 11]], 1)
    alpha = m.alpha_min + (m.alpha_max-m.alpha_min) * torch.sigmoid(m.raw_gate + .1*m.gate_mlp(ctx).squeeze(1))
    return ((1-alpha)*det + alpha*ev).numpy(), route.numpy(), sub.numpy(), alpha.numpy(), det.numpy(), ev.numpy()

def main():
    result = {'protocol': 'Frozen checkpoints; intervention diagnostics only. Not retrained ablations; no setting selected for deployment.', 'splits': {}}
    for split in a.SPLITS:
        tr, te = [a.load(a.BASE/'cache'/split/(sub+'.npz')) for sub in ['train', 'test']]
        r = a.helper.rank(tr['X'], te['X'])
        m = a.model.SemanticDirectionalCalibratedVerifier(alpha_max=.60 if split == 'A3' else .55).eval()
        m.load_state_dict(torch.load(a.BASE/'runs'/split/'best_model.pt', map_location='cpu'))
        qmap = {str(q): i for i, q in enumerate(te['qids'])}
        pairs = np.array([[qmap[str(p['positive_qid'])], qmap[str(p['negative_qid'])]] for p in a.rows(a.ROOT/'data/release/semantic_existence_v2'/split/'matched_u_pairs.jsonl')])
        with torch.no_grad():
            score, route, streams, alpha, det, ev = evaluate(m, r)
            vals = {'trained': a.helper.metrics(score, te, pairs), 'detector_stream': a.helper.metrics(det, te, pairs), 'evidence_stream': a.helper.metrics(ev, te, pairs)}
            for name, mode in [('uniform', 'uniform'), ('kinetic_only', 0), ('object_only', 1), ('manual_only', 2)]:
                modified = evaluate(m, r, mode)[0]
                vals[name] = a.helper.metrics(modified, te, pairs)
            for name, modified_raw in [('negate_signed', -te['X'][:, 12:14]), ('absolute_signed', abs(te['X'][:, 12:14])), ('zero_signed', np.zeros_like(te['X'][:, 12:14]))]:
                modified = te['X'].copy()
                modified[:, 12:14] = modified_raw
                rs = a.helper.rank(tr['X'], modified)
                vals[name] = a.helper.metrics(evaluate(m, rs)[0], te, pairs)
        partitions = {}
        for group, mask in [('seen', np.isin(te['partitions'], ['S+', 'S-'])), ('unseen', np.isin(te['partitions'], ['U+', 'U-']))]:
            partitions[group] = {'mean_route_kin_obj_manual': route[mask].mean(0).tolist(), 'alpha_min_median_max': np.quantile(alpha[mask], [0, .5, 1]).tolist()}
        result['splits'][split] = {'routing_and_gate': partitions, 'detector_weights': m.w_det.softmax(0).detach().tolist(), 'metrics': vals}
    a.write('route_diagnostics.json', result)
    print('Frozen route diagnostics saved')

if __name__ == '__main__':
    main()
