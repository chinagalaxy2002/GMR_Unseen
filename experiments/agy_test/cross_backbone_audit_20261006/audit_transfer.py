"""Independent CPU replay and paired-video audit; original experiments read only."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import importlib.util
import hashlib
import json
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EXP = ROOT/'experiments/agy_test/cross_backbone_transfer_verifier'
SPLITS = ['A1','A2_alt','A3','C1','C2_alt']
BBS = ['flash','moment','qd']
MANIFEST = {}

def module(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

sys.path.insert(0,str(ROOT))
h=module('ddv_transfer_audit_helper',ROOT/'experiments/agy_test/ddv_audit_20261006/audit_ddv.py')
model=module('transfer_frozen_model',EXP/'model.py')
torch.set_num_threads(2)

def record(p):
    p=Path(p).absolute()
    MANIFEST[str(p.relative_to(ROOT))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
    return p

def load(p):
    with np.load(record(p)) as z:
        return {k:z[k] for k in z.files if k!='q_proj_sent'}

def rows(p):
    return [json.loads(l) for l in record(p).read_text().splitlines() if l.strip()]

def write(n,d):
    (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def ci(x):
    return {'mean':float(np.mean(x)),'ci95':np.quantile(x,[.025,.975]).tolist()}

def main():
    summary=json.loads(record(EXP/'benchmark_summary.json').read_text())
    result={'protocol':'Frozen 15 checkpoints, 45 source-target evaluations; Seen-training empirical CDF; 2000 shared-video bootstrap, seed3407; no retraining or original writes.', 'subsets':{},'splits':{},'macro':{}}
    banks={}
    for split in SPLITS:
        tr,va,te=[load(EXP/'cache'/split/(s+'.npz')) for s in ['train','val','test']]
        for subset,d in [('train',tr),('val',va),('test',te)]:
            gt={str(r['qid']):r for r in rows(ROOT/'data/release/semantic_existence_v2'/split/(subset+'.jsonl'))}
            assert len(set(d['qids']))==len(d['qids'])
            assert all(int(y)==int(gt[str(q)]['exist_label']) and str(v)==str(gt[str(q)]['vid']) for q,y,v in zip(d['qids'],d['labels'],d['vids']))
            parts={gt[str(q)]['partition'] for q in d['qids']}
            if subset!='test': assert parts<= {'S+','S-'}
            result['subsets'][split+'/'+subset]={'n':len(d['qids']),'partitions':sorted(parts),'cache_real_path':str((EXP/'cache'/split/(subset+'.npz')).resolve())}
        saved=load(EXP/'runs'/split/'transfer_predictions.npz')
        assert all(np.array_equal(saved[k],te[k]) for k in ['qids','vids','labels','partitions'])
        qmap={str(q):i for i,q in enumerate(te['qids'])}
        pairs=np.array([[qmap[str(p['positive_qid'])],qmap[str(p['negative_qid'])]] for p in rows(ROOT/'data/release/semantic_existence_v2'/split/'matched_u_pairs.jsonl')])
        assert all(te['vids'][p]==te['vids'][n] for p,n in pairs)
        rva,rte=h.rank(tr['X'],va['X']),h.rank(tr['X'],te['X'])
        scores={bb+'_base':rte[:,i] for i,bb in enumerate(BBS)}
        scores.update({bb+'_raw':te['X'][:,i] for i,bb in enumerate(BBS)})
        replay,val_aucs,diagnostics={}, {}, {}
        for src in BBS:
            m=model.SingleBackboneVerifier().eval()
            m.load_state_dict(torch.load(record(EXP/'runs'/split/('verifier_src_'+src+'.pt')),map_location='cpu'))
            with torch.no_grad():
                for j,tgt in enumerate(BBS):
                    name=src+'_to_'+tgt
                    pred=m(torch.tensor(rte[:,j]),torch.tensor(rte[:,3:])).numpy()
                    replay[name]=float(np.abs(pred-saved['pred_'+name]).max())
                    assert replay[name]<1e-6
                    # Saved scores define the exact original numerical experiment; replay verifies them.
                    scores[name]=saved['pred_'+name]
                v=m(torch.tensor(rva[:,BBS.index(src)]),torch.tensor(rva[:,3:])).numpy()
                val_aucs[src]=float(h.roc_auc_score(va['labels'],v))
                x=torch.tensor(rte[:,3:])
                route=m.router(x[:,[0,2,3,4,5,6,9,10]]).softmax(1).numpy()
                diagnostics[src]={'params':sum(p.numel() for p in m.parameters()),'mean_route_kinetic_composite':route.mean(0).tolist()}
        for tgt in BBS:
            scores['ensemble_'+tgt]=(scores['flash_to_'+tgt]+scores['moment_to_'+tgt]+scores['qd_to_'+tgt])/3
        met={n:h.metrics(s,te,pairs) for n,s in scores.items()}
        reported=next(v for v in summary['splits'] if v['split']==split)
        errors=[]
        for src in BBS:
            for tgt in BBS:
                for key in ['seen','unseen','gap','pair_acc']:
                    errors.append(abs(met[src+'_to_'+tgt][key]-reported['transfer_matrix'][src][tgt][key]))
        assert max(errors)<1e-12
        # An untrained initialization is a diagnostic, not a validated deployment model.
        torch.manual_seed(3407)
        untrained=model.SingleBackboneVerifier().eval()
        with torch.no_grad():
            init={tgt:h.metrics(untrained(torch.tensor(rte[:,j]),torch.tensor(rte[:,3:])).numpy(),te,pairs) for j,tgt in enumerate(BBS)}
        result['splits'][split]={'metrics':met,'max_summary_error':max(errors),'replay_max_errors':replay,'seen_val_auc_replay':val_aucs,'model_diagnostics':diagnostics,'untrained_initialization_diagnostic':init}
        banks[split]=(te,scores,pairs)
        np.savez_compressed(OUT/(split+'_audited_scores.npz'),qids=te['qids'],vids=te['vids'],labels=te['labels'],partitions=te['partitions'],**scores)
        print(split,'max replay error',max(replay.values()),'summary error',max(errors),flush=True)
    names=list(banks['A1'][1])
    for n in names:
        result['macro'][n]={k:float(np.mean([result['splits'][s]['metrics'][n][k] for s in SPLITS])) for k in ['seen','unseen','gap','pair_acc']}
    write('audit_metrics.json',result)
    videos=sorted(set.union(*[set(d['vids']) for d,_,_ in banks.values()]))
    vmap={v:i for i,v in enumerate(videos)}
    funcs=[]
    for split in SPLITS:
        d,scores,pairs=banks[split]
        vi=np.array([vmap[v] for v in d['vids']])
        group=[]
        for pp in [['S+','S-'],['U+','U-']]:
            mask=np.isin(d['partitions'],pp)
            group.append([h.weighted_auc(d['labels'][mask],scores[n][mask],vi[mask]) for n in names])
        funcs.append(group)
    draws=np.empty((2000,5,2,len(names)))
    rng=np.random.RandomState(3407)
    for b in range(2000):
        counts=np.bincount(rng.choice(len(videos),len(videos),replace=True),minlength=len(videos))
        for j in range(5):
            for g in range(2): draws[b,j,g]=[f(counts) for f in funcs[j][g]]
        if (b+1)%500==0: print('bootstrap',b+1,flush=True)
    macro=draws.mean(1)
    index={n:i for i,n in enumerate(names)}
    boot={'n':2000,'unique_videos':len(videos),'cells':{},'splits':{}}
    for src in BBS:
        for tgt in BBS:
            n=src+'_to_'+tgt
            i,j,k=index[n],index[tgt+'_base'],index[tgt+'_to_'+tgt]
            boot['cells'][n]={'unseen':ci(macro[:,1,i]),'unseen_gain_vs_target':ci(macro[:,1,i]-macro[:,1,j]),'gap_reduction_vs_target':ci((macro[:,0,j]-macro[:,1,j])-(macro[:,0,i]-macro[:,1,i])),'unseen_difference_vs_target_self':ci(macro[:,1,i]-macro[:,1,k])}
            for sj,split in enumerate(SPLITS):
                boot['splits'].setdefault(split,{})[n]={'unseen_gain_vs_target':ci(draws[:,sj,1,i]-draws[:,sj,1,j])}
    write('bootstrap.json',boot)
    np.savez_compressed(OUT/'bootstrap_draws.npz',auc=draws,names=names,splits=SPLITS)
    for f in ['model.py','train_and_transfer.py','generate_report.py','verify_benchmark.py','CROSS_BACKBONE_TRANSFER_REPORT.md']:
        record(EXP/f)
    record(ROOT/'experiments/agy_test/ddv_audit_20261006/audit_ddv.py')
    record(Path(__file__))
    write('input_manifest.json',MANIFEST)
    print('DONE',flush=True)

if __name__=='__main__': main()
