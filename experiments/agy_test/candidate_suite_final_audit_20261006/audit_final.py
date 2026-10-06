"""Independent frozen replay of all 125 checkpoints and 270 transfer paths.

Original inputs read only. Replay ablations, recompute operational rejection,
and run 2000 shared-video paired bootstrap on mean AUROC across fixed seeds.
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
from sklearn.metrics import f1_score

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
EXP=ROOT/'experiments/agy_test/independent_candidate_transfer_suite'
SPLITS=['A1','A2_alt','A3','C1','C2_alt']
BBS=['flash','moment','qd']
SEEDS=[3407,42,2024]
MODES=['none','unsigned','no_direction','visual_only','kinetic_only']
MANIFEST={}
sys.path.insert(0,str(ROOT))

def module(n,p):
    spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

h=module('final_helpers',ROOT/'experiments/agy_test/ddv_audit_20261006/audit_ddv.py')
mod=module('final_candidate_model',EXP/'models/verifier_models.py')
torch.set_num_threads(2)

def record(p):
    p=Path(p).absolute();MANIFEST[str(p.relative_to(ROOT))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size};return p

def load(p):
    with np.load(record(p)) as z:return {k:z[k] for k in z.files}

def rows(p):return [json.loads(l) for l in record(p).read_text().splitlines() if l.strip()]

def write(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def predict(m,r):
    with torch.no_grad():return m(torch.tensor(r[:,0]),torch.tensor(r[:,1:])).numpy()

def operating(vs,yv,score,d):
    ts=np.linspace(.01,.99,100)
    js=[np.mean(vs[yv==1]>=t)-np.mean(vs[yv==0]>=t) for t in ts]
    th=float(ts[np.argmax(js)])
    masks={p:d['partitions']==p for p in ['S+','U+','U-']}
    u=np.isin(d['partitions'],['U+','U-']);y=d['labels']
    rr=float(np.mean(score[masks['U-']]<th));frr=float(np.mean(score[masks['U+']]<th))
    return {'calibrated_tau':th,'seen_frr':float(np.mean(score[masks['S+']]<th)),'unseen_rr':rr,'unseen_frr':frr,'rejection_f1':float(f1_score(1-y[u],score[u]<th)),'balanced_accuracy':.5*(1-frr+rr)}

def ci(x):return {'mean':float(np.mean(x)),'ci95':np.quantile(x,[.025,.975]).tolist()}

def main():
    report={'protocol':'Frozen CPU replay, no retraining; 2000 paired shared-video bootstrap seed3407; seed-average AUROC, not prediction ensemble; original inputs read only.', 'subsets':{},'splits':{},'macro':{},'replay_counts':{}}
    summary=json.loads(record(EXP/'reports/multi_seed_transfer_summary.json').read_text())
    banks={};count_ckpt=0;count_path=0
    for split in SPLITS:
        data={bb:{sub:load(EXP/'cache'/split/bb/(sub+'.npz')) for sub in ['train','val','test']} for bb in BBS}
        d=data['flash']['test'];scores={};met={};ops={};replay={};aba={}
        for bb in BBS:
            for sub in ['train','val','test']:
                z=data[bb][sub]
                gt={str(r['qid']):r for r in rows(ROOT/'data/release/semantic_existence_v2'/split/(sub+'.jsonl'))}
                assert all(int(y)==int(gt[str(q)]['exist_label']) and str(v)==str(gt[str(q)]['vid']) for q,v,y in zip(z['qids'],z['vids'],z['labels']))
                assert all(np.array_equal(z[k],data['flash'][sub][k]) for k in ['qids','vids','labels'])
                pp=Counter(gt[str(q)]['partition'] for q in z['qids'])
                if sub!='test':assert set(pp)<= {'S+','S-'}
                report['subsets'][split+'/'+bb+'/'+sub]={'n':len(z['qids']),'partitions':dict(pp)}
        qmap={str(q):i for i,q in enumerate(d['qids'])}
        pairs=np.array([[qmap[str(p['positive_qid'])],qmap[str(p['negative_qid'])]] for p in rows(ROOT/'data/release/semantic_existence_v2'/split/'matched_u_pairs.jsonl')])
        rank={bb:{sub:h.rank(data[bb]['train']['X'],data[bb][sub]['X']) for sub in ['val','test']} for bb in BBS}
        for bb in BBS:
            n=bb+'_base';scores[n]=data[bb]['test']['X'][:,0];met[n]=h.metrics(scores[n],d,pairs)
            ops[n]=operating(data[bb]['val']['X'][:,0],data[bb]['val']['labels'],scores[n],d)
        old=load(ROOT/'experiments/agy_test/ddv_audit_20261006'/split/'audit_predictions.npz')
        assert np.array_equal(old['qids'],d['qids'])
        scores['flash_raw']=old['flash_logit'];met['flash_raw']=h.metrics(scores['flash_raw'],d,pairs)
        for regime in ['target_specific','shared']:
            for seed in SEEDS:
                folder=EXP/'runs'/regime/('seed_'+str(seed))/split
                saved=load(folder/'transfer_predictions.npz')
                assert all(np.array_equal(saved[k],d[k]) for k in ['qids','vids','labels','partitions'])
                reported=next(r for r in summary[regime]['raw_runs'] if r['seed']==seed and r['split']==split)
                for src in BBS:
                    m=mod.TargetCandidateVerifier().eval();m.load_state_dict(torch.load(record(folder/('verifier_src_'+src+'.pt')),map_location='cpu'));count_ckpt+=1
                    for tgt in BBS:
                        n=f'{regime}_{seed}_{src}_to_{tgt}'
                        rt=rank[tgt]['test'].copy();rv=rank[tgt]['val'].copy()
                        if regime=='shared':rt[:,1:]=rank['flash']['test'][:,1:];rv[:,1:]=rank['flash']['val'][:,1:]
                        pred=predict(m,rt);count_path+=1
                        original=saved[f'pred_{src}_to_{tgt}'];err=float(abs(pred-original).max());assert err<1e-6;replay[n]=err
                        vs=predict(m,rv)
                        metric=h.metrics(original,d,pairs)
                        assert all(abs(metric[k]-reported['transfer_results'][src][tgt][k])<1e-12 for k in ['seen','unseen','gap','pair_acc'])
                        op=operating(vs,data[tgt]['val']['labels'],original,d)
                        assert all(abs(op[k]-reported['operational_results'][src][tgt][k])<1e-6 for k in reported['operational_results'][src][tgt])
                        met[n]=metric;ops[n]=op
                        # All A paths and B diagonals are retained for paired bootstrap.
                        if regime=='target_specific' or src==tgt:scores[n]=original
        for bb in (BBS if split=='A3' else ['flash']):
            aba[bb]={}
            tr0=data[bb]['train']['X'];te0=data[bb]['test']['X']
            for mode in MODES:
                tr,te=tr0.copy(),te0.copy()
                if mode=='unsigned':tr[:,10:12]=abs(tr[:,10:12]);te[:,10:12]=abs(te[:,10:12])
                if mode=='no_direction':tr[:,10:12]=0;te[:,10:12]=0
                r=h.rank(tr,te)
                m=mod.TargetCandidateVerifier(ablation_mode=mode if mode in ['visual_only','kinetic_only'] else 'none').eval()
                folder=EXP/'runs/ablation'/bb/split/mode
                m.load_state_dict(torch.load(record(folder/'verifier.pt'),map_location='cpu'));count_ckpt+=1
                saved=load(folder/'predictions.npz');assert all(np.array_equal(saved[k],d[k]) for k in ['qids','labels','partitions'])
                pred=predict(m,r);err=float(abs(pred-saved['preds']).max());assert err<1e-6;replay['ablation_'+bb+'_'+mode]=err
                aba[bb][mode]=h.metrics(saved['preds'],d,pairs)
                if bb=='flash':scores['aba_'+mode]=saved['preds'];met['aba_'+mode]=aba[bb][mode]
            torch.manual_seed(3407);m=mod.TargetCandidateVerifier().eval();prior=predict(m,h.rank(tr0,te0));aba[bb]['fixed_prior']=h.metrics(prior,d,pairs)
            if bb=='flash':scores['fixed_prior']=prior;met['fixed_prior']=aba[bb]['fixed_prior']
        report['splits'][split]={'metrics':met,'operating':ops,'ablations':aba,'replay_max_errors':replay,'flash_probability_unique':len(np.unique(d['X'][:,0])),'flash_probability_one_count':int(np.sum(d['X'][:,0]==1))}
        banks[split]=(d,scores)
        print(split,'checked checkpoints/paths',count_ckpt,count_path,'max error',max(replay.values()),flush=True)
    report['replay_counts']={'checkpoints':count_ckpt,'transfer_paths':count_path,'max_error':max(max(v['replay_max_errors'].values()) for v in report['splits'].values())}
    assert count_ckpt==125 and count_path==270
    for n in report['splits']['A1']['metrics']:
        report['macro'][n]={k:float(np.mean([report['splits'][s]['metrics'][n][k] for s in SPLITS])) for k in ['seen','unseen','gap','pair_acc']}
    report['macro_operating']={n:{k:float(np.mean([report['splits'][s]['operating'][n][k] for s in SPLITS])) for k in ['seen_frr','unseen_frr','unseen_rr','rejection_f1','balanced_accuracy']} for n in report['splits']['A1']['operating']}
    write('audit_metrics.json',report)
    names=list(banks['A1'][1]);index={n:i for i,n in enumerate(names)}
    vids=sorted(set.union(*[set(d['vids']) for d,_ in banks.values()]));vm={v:i for i,v in enumerate(vids)}
    funcs=[]
    for split in SPLITS:
        d,ss=banks[split];vi=np.array([vm[v] for v in d['vids']]);groups=[]
        for pp in [['S+','S-'],['U+','U-']]:
            mask=np.isin(d['partitions'],pp);groups.append([h.weighted_auc(d['labels'][mask],ss[n][mask],vi[mask]) for n in names])
        funcs.append(groups)
    draws=np.empty((2000,5,2,len(names)));rng=np.random.RandomState(3407)
    for j in range(2000):
        counts=np.bincount(rng.choice(len(vids),len(vids),replace=True),minlength=len(vids))
        for s in range(5):
            for g in range(2):draws[j,s,g]=[f(counts) for f in funcs[s][g]]
        if (j+1)%250==0:print('bootstrap',j+1,flush=True)
    macro=draws.mean(1);boot={'n':2000,'unique_videos':len(vids),'scope':'Mean AUROC across three fixed seeds; confidence intervals reflect video sampling, not the population of all training seeds. Unadjusted 95% intervals.', 'transfer':{},'A_minus_B':{},'ablation':{},'A3':{}}
    for src in BBS:
        for tgt in BBS:
            ids=[index[f'target_specific_{seed}_{src}_to_{tgt}'] for seed in SEEDS]
            a=macro[:,:,ids].mean(2);base=macro[:,:,index[tgt+'_base']]
            boot['transfer'][src+'_to_'+tgt]={'unseen_gain':ci(a[:,1]-base[:,1]),'seen_gain':ci(a[:,0]-base[:,0]),'gap_reduction':ci((base[:,0]-base[:,1])-(a[:,0]-a[:,1]))}
            if src==tgt:
                bid=[index[f'shared_{seed}_{src}_to_{tgt}'] for seed in SEEDS]
                boot['A_minus_B'][tgt]=ci(a[:,1]-macro[:,1,bid].mean(1))
    full=macro[:,:,index['aba_none']]
    for mode in ['unsigned','no_direction','visual_only','kinetic_only']:
        alt=macro[:,:,index['aba_'+mode]]
        boot['ablation']['full_minus_'+mode]={'unseen':ci(full[:,1]-alt[:,1])}
    for n in ['flash_base','flash_raw','fixed_prior']:
        alt=macro[:,:,index[n]];boot['ablation']['full_minus_'+n]={'unseen':ci(full[:,1]-alt[:,1]),'seen':ci(full[:,0]-alt[:,0]),'gap_reduction':ci((alt[:,0]-alt[:,1])-(full[:,0]-full[:,1]))}
    for bb in BBS:
        ids=[index[f'target_specific_{seed}_{bb}_to_{bb}'] for seed in SEEDS]
        boot['A3'][bb]={'self_unseen_gain':ci(draws[:,2,1,ids].mean(1)-draws[:,2,1,index[bb+'_base']])}
    np.savez_compressed(OUT/'bootstrap_draws.npz',auc=draws,names=names,splits=SPLITS);write('bootstrap.json',boot)
    for f in list((EXP/'scripts').glob('*.py'))+[EXP/'verify_suite.py',EXP/'models/verifier_models.py',EXP/'reports/ablation_summary.json',Path(__file__).absolute()]:record(f)
    write('input_manifest.json',MANIFEST);print('DONE',flush=True)

if __name__=='__main__':main()
