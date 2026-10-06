"""Independent DDV artifact audit. Original experiment directories are read only.

Replay checkpoints, audit joins, fit a matched detector-only control on Seen,
and compute shared-video bootstrap and the repository's G-mIoU definition.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from collections import Counter
import importlib.util
import hashlib
import json
import time
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from sklearn.metrics import roc_auc_score, f1_score

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DDV = ROOT / 'experiments/agy_test/decomposed_directional_verifier'
AC = ROOT / 'experiments/agy_test/aligned_calibration_verifier/aligned_features'
MCV = ROOT / 'experiments/agy_test/multiscale_counterfactual_verifier/cache_features'
RELEASE = ROOT / 'data/release/semantic_existence_v2'
RESULTS = ROOT / 'results/semantic_existence/multi_split_v2'
SPLITS = ['A1', 'A2_alt', 'A3', 'C1', 'C2_alt']
sys.path.insert(0, str(ROOT))
from eval.metrics import _compute_set_iou_score, prepare_submission_for_gmiou, compute_G_mIoU
spec = importlib.util.spec_from_file_location('ddv_audited_model', DDV / 'model.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
torch.set_num_threads(2)
MANIFEST = {}


def record(p):
    p = Path(p)
    MANIFEST[str(p.relative_to(ROOT))] = {
        'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
    return p


def read(p):
    return [json.loads(line) for line in record(p).read_text().splitlines() if line.strip()]


def load(p):
    with np.load(record(p)) as z:
        return {k: z[k] for k in z.files}


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def rank(train, apply):
    return np.stack([np.searchsorted(np.sort(train[:, c]), apply[:, c], side='left') /
                     len(train) for c in range(train.shape[1])], axis=1).astype(np.float32)


def threshold(scores, labels):
    ts = np.unique(scores)
    if len(ts) > 1000:
        ts = np.quantile(scores, np.linspace(0, 1, 1000))
    balanced = [.5 * ((scores[labels == 1] >= t).mean() +
                      (scores[labels == 0] < t).mean()) for t in ts]
    return float(ts[np.argmax(balanced)])


def pairacc(scores, pairs):
    a, b = scores[pairs[:, 0]], scores[pairs[:, 1]]
    return float(np.mean((a > b) + .5 * (a == b)))


def metrics(scores, d, pairs, th=None):
    s, u = np.isin(d['partitions'], ['S+', 'S-']), np.isin(d['partitions'], ['U+', 'U-'])
    y = d['labels']
    sa, ua = float(roc_auc_score(y[s], scores[s])), float(roc_auc_score(y[u], scores[u]))
    m = dict(seen=sa, unseen=ua, gap=sa-ua, pair_acc=pairacc(scores, pairs))
    if th is not None:
        m.update(threshold=th, rej_f1=float(f1_score(1-y[u], (scores[u] < th).astype(int))),
                 u_pos_frr=float((scores[d['partitions'] == 'U+'] < th).mean()),
                 u_neg_rr=float((scores[d['partitions'] == 'U-'] < th).mean()))
    return m


def streams(model, r):
    w = F.softmax(model.w_det, 0).detach().numpy()
    lam = .7 if model.split in ['A2_alt', 'A3'] else .5
    det = lam * np.median(r[:, :3], axis=1) + (1-lam) * (r[:, :3] @ w)
    channels = {'A1': [3,4,5,9], 'A2_alt': [5,3,7], 'A3': [8,9],
                'C1': [5,6,3], 'C2_alt': [6,5,3]}[model.split]
    ew = F.softmax(model.w_ev_split, 0).detach().numpy()
    ev = r[:, channels] @ ew
    ctx = np.stack([det, ev, np.abs(r[:,0]-r[:,1])+np.abs(r[:,1]-r[:,2]),
                    r[:,5], r[:,6], r[:,8], r[:,10], r[:,11]], axis=-1)
    with torch.no_grad():
        a = model.alpha_min + (model.alpha_max-model.alpha_min) * torch.sigmoid(
            model.raw_gate + .1*model.gate_mlp(torch.tensor(ctx)).squeeze(-1))
    return det, ev, a.numpy(), channels, w, ew


class DetectorOnly(nn.Module):
    """Same detector stream, same split lambda, without new evidence or gate."""
    def __init__(self, split):
        super().__init__()
        self.w_det = nn.Parameter(torch.ones(3))
        self.lam = .7 if split in ['A2_alt', 'A3'] else .5

    def forward(self, x):
        return self.lam*x[:,:3].median(1).values + (1-self.lam)*(x[:,:3]*self.w_det.softmax(0)).sum(1)


def fit_detector_control(split, tr, val, rtr, rval, rte):
    """Matched 400 epochs x 10 steps, seed, pair sampling, loss and Seen selection."""
    torch.manual_seed(3407)
    model = DetectorOnly(split)
    opt = torch.optim.AdamW(model.parameters(), lr=.003, weight_decay=.001)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=400, eta_min=1e-5)
    x = torch.tensor(rtr)
    xv, xt = torch.tensor(rval), torch.tensor(rte)
    pp = torch.tensor(tr['same_vid_pairs'], dtype=torch.long)
    pos = torch.tensor(np.flatnonzero(tr['labels'] == 1))
    neg = torch.tensor(np.flatnonzero(tr['labels'] == 0))
    best, best_ep, best_state = -1., None, None
    started = time.time()
    for ep in range(1,401):
        for _ in range(10):
            ip = pp[torch.randint(len(pp),(128,))]
            p = torch.cat([ip[:,0], pos[torch.randint(len(pos),(128,))]])
            n = torch.cat([ip[:,1], neg[torch.randint(len(neg),(128,))]])
            sp, sn = model(x[p]), model(x[n])
            rank_loss = F.softplus(-(sp-sn)/.15).mean()
            sc = model(x[torch.cat([p,n])])
            yy = torch.cat([torch.ones_like(sp),torch.zeros_like(sn)])
            calib_loss = F.binary_cross_entropy(sc.clamp(1e-6,1-1e-6),yy)
            w = model.w_det.softmax(0)
            loss = rank_loss + .4*calib_loss + .05*(w*(w+1e-8).log()).sum()
            opt.zero_grad();loss.backward();opt.step()
        scheduler.step()
        with torch.no_grad():
            va = float(roc_auc_score(val['labels'],model(xv).numpy()))
        if va > best:
            best, best_ep = va, ep
            best_state = {k:v.clone() for k,v in model.state_dict().items()}
    model.load_state_dict(best_state)
    with torch.no_grad():
        vs, ts = model(xv).numpy(), model(xt).numpy()
    folder = OUT / split
    folder.mkdir(exist_ok=True)
    torch.save({'state_dict':best_state,'best_epoch':best_ep,'val_seen_auc':best,
                'seed':3407,'epochs':400,'steps_per_epoch':10},folder/'detector_only_control.pt')
    return ts, vs, {'best_epoch':best_ep,'val_seen_auc':best,
                    'seconds':time.time()-started,'weights':model.w_det.softmax(0).detach().tolist()}


def weighted_auc(y, score, vi):
    order = np.argsort(score, kind='stable')
    y, score, vi = y[order], score[order], vi[order]
    starts = np.r_[0,np.flatnonzero(np.diff(score))+1]
    def calc(counts):
        w = counts[vi]
        p = np.add.reduceat(w*(y == 1),starts)
        n = np.add.reduceat(w*(y == 0),starts)
        return float((p*(np.cumsum(n)-.5*n)).sum()/(p.sum()*n.sum()))
    return calc


def gmiou(scores, th, d, gt, rows, field):
    # Feed binary decisions to the official strict >.5 gate; preserve DDV >=th policy.
    raw = [{'qid':str(q),'pred_exist_score':float(scores[i] >= th),
            'pred_relevant_windows':rows[str(q)].get(field,[])} for i,q in enumerate(d['qids'])]
    gated, _ = prepare_submission_for_gmiou(raw,.5,10)
    gm = {str(r['qid']):r['relevant_windows'] for r in gt}
    val = np.array([[_compute_set_iou_score([w[:2] for w in p['pred_relevant_windows'][:k]],
                                           gm[str(p['qid'])]) for k in [1,3,5]] for p in gated])
    result = {}
    for group, mask in [('seen',np.isin(d['partitions'],['S+','S-'])),
                        ('unseen',np.isin(d['partitions'],['U+','U-']))]:
        result[group] = (100*val[mask].mean(0)).tolist()
        selected_qids = set(d['qids'][mask])
        official = compute_G_mIoU([p for i,p in enumerate(gated) if mask[i]],
                                  [r for r in gt if str(r['qid']) in selected_qids], [1,3,5])
        assert all(official[f'G-mIoU@{k}'] == round(result[group][j],2) for j,k in enumerate([1,3,5]))
    return result, val


def main():
    OUT.mkdir(exist_ok=True)
    report = {'protocol':{'seed':3407,'bootstrap_replicates':2000,
              'control':'Detector-only matched 400x10 training, same losses, pairs, rank normalization, Seen validation selection; CPU audit control, no original files overwritten.',
              'inference_replay':'CPU frozen original checkpoints; no original retraining.',
              'gmiou':'Repository eval/metrics.py; both empty=1, set IoU otherwise; decisions >= Seen-selected threshold.'},
              'subsets':{},'splits':{},'macro':{}}
    boots, localization = {}, {}
    for split in SPLITS:
        tr, val, te = [load(DDV/'cache'/split/f'{s}.npz') for s in ['train','val','test']]
        for sub,d in [('train',tr),('val',val),('test',te)]:
            a, c = load(AC/split/f'{sub}.npz'), load(MCV/split/f'{sub}.npz')
            gt = read(RELEASE/split/f'{sub}.jsonl'); gm = {str(x['qid']):x for x in gt}
            am = {str(q):i for i,q in enumerate(a['qids'])}; ai = np.array([am[str(q)] for q in d['qids']])
            assert np.array_equal(d['qids'],c['qids'])
            assert all(int(d['labels'][i]) == int(gm[str(q)]['exist_label']) and str(d['vids'][i]) == str(gm[str(q)]['vid']) for i,q in enumerate(d['qids']))
            assert np.array_equal(d['labels'],a['labels'][ai])
            expected = np.concatenate([c['X'][:,:6],a['sim_cand_obj'][ai,None],
                                       a['sim_cand_act'][ai,None],c['X'][:,6:]],axis=1).astype('float32')
            assert np.array_equal(expected,d['X'])
            if sub in ['train','test']:assert np.array_equal(d['qids'],a['qids'])
            parts = [gm[str(q)]['partition'] for q in d['qids']]
            if sub in ['train','val']:assert all(p in ['S+','S-'] for p in parts)
            report['subsets'][split+'/'+sub] = {'n':len(d['qids']),'partitions':dict(Counter(parts)),
                'expected_seen_n':sum(x['partition'] in ['S+','S-'] for x in gt),
                'features_max_join_error':float(abs(expected-d['X']).max()),
                'finite':bool(np.isfinite(d['X']).all()),
                'sf_displacement_zero_fraction':float((d['X'][:,9] == 0).mean())}
        for b in ['flash','moment','qd']:
            p = ROOT/f'experiments/agy_test/cache/features/{split}/{b}/train.npz'
            with np.load(p) as z:
                assert np.array_equal(z['qids'].astype(str),tr['qids'].astype(str))
                assert np.array_equal(z['labels'],tr['labels'])
        assert np.all(tr['vids'][tr['same_vid_pairs'][:,0]] == tr['vids'][tr['same_vid_pairs'][:,1]])
        assert np.all(tr['labels'][tr['same_vid_pairs'][:,0]] == 1)
        assert np.all(tr['labels'][tr['same_vid_pairs'][:,1]] == 0)
        rtr, rval, rte = [rank(tr['X'],d['X']) for d in [tr,val,te]]
        pred = load(DDV/'runs'/split/'predictions.npz')
        assert all(np.array_equal(pred[k],te[k]) for k in ['qids','vids','labels','partitions'])
        model = module.DecomposedDirectionalVerifier(split,alpha_max=.60 if split == 'A3' else .55)
        model.load_state_dict(torch.load(record(DDV/'runs'/split/'best_model.pt'),map_location='cpu'))
        model.eval()
        with torch.no_grad():
            replay = model(torch.tensor(rte)).numpy()
            vs = model(torch.tensor(rval)).numpy()
        maxerr = float(abs(replay-pred['ddv_scores']).max())
        assert maxerr < 2e-6
        ddet, dev, alpha, channels, wd, we = streams(model,rte)
        vdet, vev, va, _, _, _ = streams(model,rval)
        th = float(pred['threshold'])
        gt = read(RELEASE/split/'test.jsonl')
        rows = {str(r['qid']):r for r in read(RESULTS/split/'qd/test/qd_detr_gmr_test_submission.jsonl')}
        flrows = {str(r['qid']):r for r in read(RESULTS/split/'flash/test/hl_test_submission.jsonl')}
        pp = read(RELEASE/split/'matched_u_pairs.jsonl'); qi = {str(q):i for i,q in enumerate(te['qids'])}
        pairs = np.array([(qi[str(p['positive_qid'])],qi[str(p['negative_qid'])]) for p in pp])
        scores = {'ddv':pred['ddv_scores'],'hq_qd':pred['base_hq_scores'],
                  'release_qd':pred['base_rel_scores'],'flash_logit':te['X'][:,0],
                  'flash_published_probability':np.array([flrows[str(q)]['pred_exist_score'] for q in te['qids']]),
                  'moment':te['X'][:,1],'rank_mean':rte[:,:3].mean(1),'rank_median':np.median(rte[:,:3],1),
                  'frozen_detector_stream':ddet,'frozen_evidence_stream':dev,
                  'frozen_constant_gate':(1-(model.alpha_min+model.alpha_max)/2)*ddet + (model.alpha_min+model.alpha_max)/2*dev}
        acval = load(AC/split/'val.npz'); avs = np.isin(acval['partitions'],['S+','S-'])
        ths = {'ddv':th,'hq_qd':threshold(acval['orig_logits'][avs],acval['labels'][avs]),
               'flash_logit':threshold(val['X'][:,0],val['labels']),
               'rank_mean':threshold(rval[:,:3].mean(1),val['labels']),
               'rank_median':threshold(np.median(rval[:,:3],1),val['labels']),
               'frozen_detector_stream':threshold(vdet,val['labels'])}
        pv, pvs, control_meta = fit_detector_control(split,tr,val,rtr,rval,rte)
        scores['matched_detector_only'] = pv
        ths['matched_detector_only'] = threshold(pvs,val['labels'])
        sm = {n:metrics(sc,te,pairs,ths.get(n)) for n,sc in scores.items()}
        split_report = {'replay_max_abs_error':maxerr,'replayed_val_auc':float(roc_auc_score(val['labels'],vs)),
            'replayed_threshold':threshold(vs,val['labels']),'saved_threshold':th,
            'model':{'alpha_min':model.alpha_min,'alpha_max':model.alpha_max,
                     'actual_alpha_quantiles':np.quantile(alpha,[0,.5,1]).tolist(),
                     'detector_weights':wd.tolist(),'evidence_channels':channels,'evidence_weights':we.tolist()},
            'matched_detector_control':control_meta,'metrics':sm,
            'train_val_video_overlap':len(set(tr['vids']) & set(val['vids'])),
            'train_test_video_overlap':len(set(tr['vids']) & set(te['vids'])),
            'test_gt_same_positional_qids':bool(np.array_equal(te['qids'].astype(str),np.array([str(r['qid']) for r in gt]))),
            'qd_empty_post_exist_candidates':sum(not r['pred_relevant_windows'] for r in rows.values()),
            'qd_empty_pre_exist_candidates':sum(not r.get('pred_relevant_windows_pre_exist',[]) for r in rows.values()),
            'localization':{}}
        for bank in ['pred_relevant_windows','pred_relevant_windows_pre_exist']:
            bankres = {}
            for name in ['hq_qd','ddv','matched_detector_only']:
                gm, values = gmiou(scores[name],ths[name],te,gt,rows,bank)
                bankres[name] = gm
                if bank == 'pred_relevant_windows_pre_exist':
                    localization[(split,name)] = values
            split_report['localization'][bank] = bankres
        report['splits'][split] = split_report
        boots[split] = (te,scores,pairs)
        np.savez_compressed(OUT/split/'audit_predictions.npz',qids=te['qids'],vids=te['vids'],
                            labels=te['labels'],partitions=te['partitions'],**scores,
                            thresholds_json=json.dumps(ths),hq_gmiou=localization[(split,'hq_qd')],
                            ddv_gmiou=localization[(split,'ddv')])
        write('audit_metrics.json',report)
        print(split, 'replay',maxerr,'Unseen', {n:round(sm[n]['unseen'],4) for n in ['ddv','flash_logit','rank_median','matched_detector_only']},
              'control_sec',round(control_meta['seconds'],1),flush=True)
    for n in report['splits']['A1']['metrics']:
        mm = [report['splits'][s]['metrics'][n] for s in SPLITS]
        report['macro'][n] = {k:float(np.mean([m[k] for m in mm])) for k in mm[0] if k != 'threshold'}
    report['macro_localization'] = {bank:{n:{g:np.mean([report['splits'][s]['localization'][bank][n][g]
                for s in SPLITS],axis=0).tolist() for g in ['seen','unseen']}
                for n in ['hq_qd','ddv','matched_detector_only']}
                for bank in ['pred_relevant_windows','pred_relevant_windows_pre_exist']}
    write('audit_metrics.json',report)
    vids = sorted(set().union(*(set(boots[s][0]['vids']) for s in SPLITS)))
    vm = {v:i for i,v in enumerate(vids)}
    names = ['ddv','hq_qd','release_qd','flash_logit','rank_median','rank_mean','matched_detector_only',
             'frozen_detector_stream','frozen_constant_gate']
    fns = {}
    for s,(d,sc,pp) in boots.items():
        vi = np.array([vm[v] for v in d['vids']])
        for group, mask in [('seen',np.isin(d['partitions'],['S+','S-'])),('unseen',np.isin(d['partitions'],['U+','U-']))]:
            for n in names:fns[(s,group,n)] = weighted_auc(d['labels'][mask],sc[n][mask],vi[mask])
    rng = np.random.RandomState(3407)
    draws = np.empty((2000,5,2,len(names)))
    pair_draws = np.empty((2000,5,2))
    loc_draws = np.empty((2000,5,2,2,3))
    for b in range(2000):
        counts = np.bincount(rng.choice(len(vids),len(vids),replace=True),minlength=len(vids))
        for si,s in enumerate(SPLITS):
            d,sc,pp = boots[s]
            vi = np.array([vm[v] for v in d['vids']])
            pw = counts[vi[pp[:,0]]]
            for j,n in enumerate(['ddv','hq_qd']):
                a,c = sc[n][pp[:,0]],sc[n][pp[:,1]]
                pair_draws[b,si,j] = np.sum(pw*((a>c)+.5*(a==c)))/pw.sum()
            for gi,g in enumerate(['seen','unseen']):
                for ni,n in enumerate(names):draws[b,si,gi,ni] = fns[(s,g,n)](counts)
                mask = np.isin(d['partitions'],['S+','S-'] if g == 'seen' else ['U+','U-'])
                ww = counts[vi[mask]]
                for ni,n in enumerate(['hq_qd','ddv']):
                    loc_draws[b,si,gi,ni] = (localization[(s,n)][mask]*ww[:,None]).sum(0)/ww.sum()
        if (b+1)%500 == 0:print('bootstrap',b+1,flush=True)
    def ci(x):
        return {'mean':float(np.mean(x)), 'ci95':np.quantile(x,[.025,.975]).tolist()}
    macro = draws.mean(1)
    bs = {'n':2000,'unique_videos':len(vids),'method':'Paired shared-video percentile bootstrap; fixed single-seed models.',
          'ddv_seen':ci(macro[:,0,0]),'ddv_unseen':ci(macro[:,1,0]),'comparisons':{},'splits':{},
          'pair_gain_ddv_vs_hq':ci((pair_draws[:,:,0]-pair_draws[:,:,1]).mean(1))}
    for ni,n in enumerate(names[1:],1):
        bs['comparisons']['ddv_minus_'+n] = {'seen':ci(macro[:,0,0]-macro[:,0,ni]),
             'unseen':ci(macro[:,1,0]-macro[:,1,ni]),
             'gap_reduction':ci((macro[:,0,ni]-macro[:,1,ni])-(macro[:,0,0]-macro[:,1,0]))}
    for si,s in enumerate(SPLITS):
        bs['splits'][s] = {'ddv_unseen':ci(draws[:,si,1,0]),
                           'gain_vs_hq':ci(draws[:,si,1,0]-draws[:,si,1,1]),
                           'gap_reduction_vs_hq':ci((draws[:,si,0,1]-draws[:,si,1,1])-(draws[:,si,0,0]-draws[:,si,1,0])),
                           'pair_gain_vs_hq':ci(pair_draws[:,si,0]-pair_draws[:,si,1])}
        bs['splits'][s]['gain_vs_flash_logit'] = ci(draws[:,si,1,0]-draws[:,si,1,names.index('flash_logit')])
    for group, ids in [('action',[0,1,2]),('composition',[3,4])]:
        bs[group] = {'ddv_unseen':ci(draws[:,ids,1,0].mean(1)),
                     'gain_vs_hq':ci((draws[:,ids,1,0]-draws[:,ids,1,1]).mean(1))}
        bs[group]['point_estimates'] = {n:float(np.mean([report['splits'][SPLITS[i]]['metrics'][n]['unseen']
                for i in ids])) for n in ['ddv','flash_logit','matched_detector_only']}
        for n in ['flash_logit','matched_detector_only']:
            bs[group]['gain_vs_'+n] = ci((draws[:,ids,1,0]-draws[:,ids,1,names.index(n)]).mean(1))
    ld = loc_draws.mean(1)
    bs['corrected_gmiou_ddv_minus_hq_pp'] = {g:{str(k):ci(100*(ld[:,gi,1,j]-ld[:,gi,0,j]))
                 for j,k in enumerate([1,3,5])} for gi,g in enumerate(['seen','unseen'])}
    write('bootstrap.json',bs)
    np.savez_compressed(OUT/'bootstrap_draws.npz',auc=draws,names=names,splits=SPLITS,
                        pair_acc=pair_draws,gmiou=loc_draws)
    for f in ['model.py','prepare_data.py','train_and_eval.py','benchmark_summary.json','DDV_VERIFIER_REPORT.md']:
        record(DDV/f)
    record(ROOT/'eval/metrics.py')
    write('input_manifest.json',MANIFEST)
    print('macro',json.dumps(report['macro'],ensure_ascii=False),flush=True)
    print('CIs',json.dumps(bs['comparisons'],ensure_ascii=False),flush=True)


if __name__ == '__main__':
    main()
