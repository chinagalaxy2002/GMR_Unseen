"""Read-only candidate-suite audit. No trained checkpoints/predictions exist.

Verify cache joins, raw-video feature samples, baseline/untrained inference,
summary arithmetic, ablation semantics, and definitions of operating metrics.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import importlib.util
import hashlib
import json
from collections import Counter
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
EXP=ROOT/'experiments/agy_test/independent_candidate_transfer_suite'
SPLITS=['A1','A2_alt','A3','C1','C2_alt']
BBS=['flash','moment','qd']
MANIFEST={}
sys.path.insert(0,str(ROOT))

def module(n,p):
    spec=importlib.util.spec_from_file_location(n,p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

h=module('candidate_suite_helpers',ROOT/'experiments/agy_test/ddv_audit_20261006/audit_ddv.py')
model=module('candidate_suite_model',EXP/'models/verifier_models.py')
torch.set_num_threads(2)

def record(p):
    p=Path(p).absolute();MANIFEST[str(p.relative_to(ROOT))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size};return p

def load(p):
    with np.load(record(p)) as z:return {k:z[k] for k in z.files}

def rows(p):return [json.loads(l) for l in record(p).read_text().splitlines() if l.strip()]

def write(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def norm(v):return v/(np.linalg.norm(v,axis=-1,keepdims=True)+1e-8)

def main():
    abl=json.loads(record(EXP/'reports/ablation_summary.json').read_text())
    ms=json.loads(record(EXP/'reports/multi_seed_transfer_summary.json').read_text())
    out={'scope':'No training performed. Trained weights and per-query predictions not saved; verify only available artifacts.', 'subsets':{},'splits':{},'matrix_means':{},'ablation_numeric_checks':{}}
    cc,sc={},{}
    for split in SPLITS:
        teflash=load(EXP/'cache'/split/'flash/test.npz')
        qmap={str(q):i for i,q in enumerate(teflash['qids'])}
        pairs=np.array([[qmap[str(p['positive_qid'])],qmap[str(p['negative_qid'])]] for p in rows(ROOT/'data/release/semantic_existence_v2'/split/'matched_u_pairs.jsonl')])
        old=load(ROOT/'experiments/agy_test/ddv_audit_20261006'/split/'audit_predictions.npz')
        assert np.array_equal(old['qids'],teflash['qids'])
        baselines={}
        fixed=None
        for bb in BBS:
            tr=load(EXP/'cache'/split/bb/'train.npz')
            for subset in ['train','val','test']:
                d=load(EXP/'cache'/split/bb/(subset+'.npz'))
                a=load(ROOT/'experiments/agy_test/aligned_calibration_verifier/aligned_features'/split/(subset+'.npz'))
                amap={str(q):i for i,q in enumerate(a['qids'])}
                gt={str(r['qid']):r for r in rows(ROOT/'data/release/semantic_existence_v2'/split/(subset+'.jsonl'))}
                assert all(int(y)==gt[str(q)]['exist_label'] and str(v)==str(gt[str(q)]['vid']) for q,v,y in zip(d['qids'],d['vids'],d['labels']))
                assert np.array_equal(d['qids'],(tr if subset=='train' else load(EXP/'cache'/split/'flash'/(subset+'.npz')))['qids'])
                parts=Counter(gt[str(q)]['partition'] for q in d['qids'])
                if subset!='test':assert set(parts)<= {'S+','S-'}
                if subset=='train':
                    source=load(ROOT/'experiments/agy_test/cache/features'/split/bb/'train.npz')
                    assert np.array_equal(d['qids'],source['qids'])
                else:
                    if subset=='test':
                        suffix={'flash':'flash/test/hl_test_submission.jsonl','moment':'moment/test/moment_detr_gmr_test_submission.jsonl','qd':'qd/test/qd_detr_gmr_test_submission.jsonl'}[bb]
                        source_rows=rows(ROOT/'results/semantic_existence/multi_split_v2'/split/suffix)
                    else:
                        base=ROOT/'results/semantic_existence/multi_split_v2'/split
                        path=list((base/'flash').glob('*/hl_val_submission.jsonl'))[0] if bb=='flash' else base/(bb+'/best_charades_semantic_existence_val_preds.jsonl')
                        source_rows=rows(path)
                    smap={str(r['qid']):r for r in source_rows}
                errors=[]
                for i in np.linspace(0,len(d['qids'])-1,2,dtype=int):
                    q,v=str(d['qids'][i]),str(d['vids'][i]);ai=amap[q]
                    if subset=='train':
                        k=source['foreground_scores'][i].argmax();sp=source['spans_xx'][i,k]
                        spans=np.clip([sp[0]-sp[1]/2,sp[0]+sp[1]/2] if bb=='flash' else sp,0,1)
                        fg=source['foreground_scores'][i,k]
                    else:
                        wins=smap[q].get('pred_relevant_windows',[])
                        duration=max(1.,float(gt[q]['duration']))
                        spans=np.clip(np.array(wins[0][:2])/duration,0,1) if wins else np.array([0.,1.])
                        fg=wins[0][2] if wins and len(wins[0])>2 else (1. if wins else .5)
                    if v not in cc:
                        cc[v]=norm(np.load(record(ROOT/'features/charades_semantic_existence/clip'/(v+'.npz')))['features'].astype(np.float32))
                        sc[v]=np.load(record(ROOT/'features/charades_semantic_existence/slowfast'/(v+'.npz')))['features'].astype(np.float32)
                    c,s=cc[v],sc[v]
                    st,en=sorted([max(0,min(len(c)-1,int(round(t*(len(c)-1))))) for t in spans])
                    qs,qa,qo=[a[k][ai] for k in ['q_proj_sent','q_proj_act','q_proj_obj']]
                    ref=a['train_reference'];cand=norm(c[st:en+1].mean(0));glob=norm(c.mean(0))
                    dif=np.linalg.norm(s[1:]-s[:-1],axis=-1);ss,se=sorted([max(0,min(len(s)-1,int(round(t*(len(s)-1))))) for t in spans])
                    speed=dif[ss:se].mean() if se>ss else (dif[ss] if ss<len(dif) else dif.mean())
                    vec=np.array([np.dot(glob,qs)-np.dot(ref,qs),np.dot(cand,qs)-np.dot(ref,qs),np.max(c@qs-np.dot(ref,qs)),np.dot(cand,qo)-np.dot(ref,qo),np.dot(cand,qa)-np.dot(ref,qa),speed-dif.mean(),np.linalg.norm(s[se]-s[ss]),fg,spans[1]-spans[0],np.dot(c[en]-c[st],qa),np.dot(c[en]-c[st],qo)])
                    errors.append(float(np.abs(d['X'][i,1:]-vec).max()))
                assert max(errors)<1e-4
                out['subsets'][split+'/'+bb+'/'+subset]={'n':len(d['qids']),'partitions':dict(parts),'feature_checks':2,'feature_max_error':max(errors)}
                if subset=='test':
                    baselines[bb]=h.metrics(d['X'][:,0],d,pairs)
                    if bb=='flash':
                        torch.manual_seed(3407);m=model.TargetCandidateVerifier().eval()
                        r=h.rank(tr['X'],d['X'])
                        with torch.no_grad():pred=m(torch.tensor(r[:,0]),torch.tensor(r[:,1:])).numpy()
                        fixed=h.metrics(pred,d,pairs)
                        with torch.no_grad():
                            u=model.TargetCandidateVerifier(ablation_mode='unsigned').eval();u.load_state_dict(m.state_dict());alt=u(torch.tensor(r[:,0]),torch.tensor(r[:,1:])).numpy()
                        assert np.array_equal(pred,alt)
            print(split,bb,'joins and feature samples checked',flush=True)
        out['splits'][split]={'baselines':baselines,'fixed_prior_replay':fixed,'old_flash_raw':h.metrics(old['flash_logit'],old,pairs),'flash_probability_one_fraction':float(np.mean(teflash['X'][:,0]==1.))}
    out['baseline_macro']={bb:{k:float(np.mean([out['splits'][s]['baselines'][bb][k] for s in SPLITS])) for k in ['seen','unseen','gap','pair_acc']} for bb in BBS}
    out['old_flash_raw_macro']={k:float(np.mean([out['splits'][s]['old_flash_raw'][k] for s in SPLITS])) for k in ['seen','unseen','gap','pair_acc']}
    out['fixed_prior_macro']={k:float(np.mean([out['splits'][s]['fixed_prior_replay'][k] for s in SPLITS])) for k in ['seen','unseen','gap','pair_acc']}
    for regime,data in ms.items():
        raw=data['raw_runs']
        means={}
        for src in BBS:
            means[src]={}
            for tgt in BBS:
                values=[]
                for seed in data['macro_seeds']:
                    selected=[r for r in raw if r['seed']==seed['seed']]
                    assert len(selected)==5
                    mean=float(np.mean([r['transfer_results'][src][tgt]['unseen'] for r in selected]))
                    assert abs(mean-seed['macro_tm'][src][tgt]['unseen'])<1e-12
                    values.append(mean)
                means[src][tgt]={'mean':float(np.mean(values)),'population_std':float(np.std(values)),'sample_std':float(np.std(values,ddof=1)),'seed_values':values}
        out['matrix_means'][regime]=means
    out['A_minus_B']={}
    for src in BBS:
        out['A_minus_B'][src]={}
        for tgt in BBS:
            aa=out['matrix_means']['target_specific'][src][tgt]
            bb=out['matrix_means']['shared'][src][tgt]
            out['A_minus_B'][src][tgt]={'mean':aa['mean']-bb['mean'],'seed_differences':(np.array(aa['seed_values'])-np.array(bb['seed_values'])).tolist()}
    out['full_equals_unsigned_summary']=abl['macro_flash_ablation']['Full Trained Verifier']==abl['macro_flash_ablation']['Ablation: Unsigned Direction (|delta|)']
    out['operational_table']={}
    for regime,data in ms.items():
        out['operational_table'][regime]={}
        for tgt in BBS:
            selected=[r['operational_results']['flash'][tgt] for r in data['raw_runs']]
            out['operational_table'][regime][tgt]={k:float(np.mean([r[k] for r in selected])) for k in ['seen_frr','unseen_frr','unseen_rr','unseen_f1']}
    out['saved_runs_files']=[str(p.relative_to(EXP)) for p in (EXP/'runs').rglob('*') if p.is_file()]
    for p in list((EXP/'scripts').glob('*.py'))+[EXP/'models/verifier_models.py',Path(__file__).absolute()]:record(p)
    write('audit_metrics.json',out);write('input_manifest.json',MANIFEST);print('DONE',flush=True)

if __name__=='__main__':main()
