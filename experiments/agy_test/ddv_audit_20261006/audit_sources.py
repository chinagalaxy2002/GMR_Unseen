"""Audit DDV's input sources, pair mining and active model parameters."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
import importlib.util
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT/'experiments/agy_test/decomposed_directional_verifier'
AC = ROOT/'experiments/agy_test/aligned_calibration_verifier/aligned_features'
spec = importlib.util.spec_from_file_location('ddv_source_model',BASE/'model.py')
mod = importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
torch.set_num_threads(2)
report = {'detector_source_columns':{},'train_pair_source_fraction':{},
          'feature_spot_checks':{},'model_parameters':{}}
for sp in ['A1','A2_alt','A3','C1','C2_alt']:
    d = np.load(BASE/'cache'/sp/'train.npz')
    for c,b in enumerate(['flash','moment','qd']):
        z = np.load(ROOT/f'experiments/agy_test/cache/features/{sp}/{b}/train.npz')
        raw = z['original_exist_logits']
        expected = raw if b == 'flash' else 1/(1+np.exp(-raw))
        report['detector_source_columns'][sp+'/'+b] = {
            'max_error':float(abs(expected-d['X'][:,c]).max()),
            'representation':'logit' if b == 'flash' else 'sigmoid probability'}
        assert np.array_equal(d['X'][:,c],expected)
    gt = {str(v['qid']):v for v in map(json.loads,(ROOT/f'data/release/semantic_existence_v2/{sp}/train.jsonl').read_text().splitlines())}
    q, pp = d['qids'], d['same_vid_pairs']
    exact = np.array([str(q[a]) == str(gt[str(q[b])].get('source_qid')) for a,b in pp])
    report['train_pair_source_fraction'][sp] = {'pairs':len(pp),'source_exact_pairs':int(exact.sum()),
                                               'source_exact_fraction':float(exact.mean())}
    model = mod.DecomposedDirectionalVerifier(sp,alpha_max=.6 if sp == 'A3' else .55)
    model.load_state_dict(torch.load(BASE/'runs'/sp/'best_model.pt',map_location='cpu'))
    model(torch.tensor(np.clip(d['X'][:32],0,1))).sum().backward()
    report['model_parameters'][sp] = {'parameter_count':sum(p.numel() for p in model.parameters()),
            'parameters_with_no_gradient':[n for n,p in model.named_parameters() if p.grad is None]}
    for sub in ['train','val','test']:
        z = np.load(BASE/'cache'/sp/f'{sub}.npz');a = np.load(AC/sp/f'{sub}.npz')
        ai = {str(q):i for i,q in enumerate(a['qids'])}
        selected = sorted(set(np.r_[np.flatnonzero(z['labels'] == 1)[:3],
                                     np.flatnonzero(z['labels'] == 0)[:3]].tolist()))
        err = []
        for i in selected:
            j = ai[str(z['qids'][i])];v = str(z['vids'][i])
            sf = np.load(ROOT/f'features/charades_semantic_existence/slowfast/{v}.npz')['features'].astype('float32')
            clip = np.load(ROOT/f'features/charades_semantic_existence/clip/{v}.npz')['features'].astype('float32')
            st,en = a['best_spans'][j];n = len(sf)
            velocity = np.linalg.norm(np.diff(sf,axis=0),axis=1)
            left = max(0,min(n-2,int(st*(n-1))))
            right = max(left+1,min(n-1,int(en*(n-1))+1))
            contrast = velocity[left:right].mean()-velocity.mean()
            leftframe = max(0,min(n-1,int(st*n)));rightframe = max(0,min(n-1,int(en*n)))
            displacement = np.linalg.norm(sf[rightframe]-sf[leftframe])
            clip = clip/(np.linalg.norm(clip,axis=1,keepdims=True)+1e-8)
            peak = (clip@a['q_proj_sent'][j] - a['train_reference']@a['q_proj_sent'][j]).max()
            err.append([abs(float(peak)-float(z['X'][i,5])),
                        abs(float(contrast)-float(z['X'][i,8])),
                        abs(float(displacement)-float(z['X'][i,9]))])
        errors = np.max(err,axis=0)
        assert np.all(errors < 1e-4)
        report['feature_spot_checks'][sp+'/'+sub] = {
            'n':len(selected),'max_abs_errors_peak_velocity_displacement':errors.tolist()}
report['note'] = ('Training pairs contain all same-video positive-negative combinations; exact construction-source '
                  'pairs are only a subset. Flash logit and Moment/QD probability units differ, but '
                  'train/val/test are consistent per channel and train-only CDF normalizes them. '
                  'Feature checks are 90 sampled rows, not a complete raw-video recomputation.')
(OUT/'source_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'spot_check_rows':sum(x['n'] for x in report['feature_spot_checks'].values()),
                  'model_parameters':report['model_parameters']},ensure_ascii=False))
