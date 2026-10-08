"""Rebuild the published calibration using train and Seen validation only."""
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
from dec import SPLITS,BACKBONES,score,select_threshold
from seen_guard import blend_score

def val_metrics(y,sc,iou,threshold=None):
    t=select_threshold(y,sc) if threshold is None else float(threshold)
    accept=sc>=t;tn=np.sum((y==0)&~accept);fp=np.sum((y==0)&accept);fn=np.sum((y==1)&~accept)
    return dict(auc=float(roc_auc_score(y,sc)),threshold=t,gmiou=float(100*np.where(accept,iou,y==0).mean()),f1=float(100*2*tn/(2*tn+fp+fn)),frr=float(100*(~accept[y==1]).mean()),ba=float(.5*(accept[y==1].mean()+(~accept[y==0]).mean())))

def main():
    root=Path(__file__).resolve().parent;p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=root/'data');p.add_argument('--query-keys',type=Path,default=root/'calibration/query_keys.json');p.add_argument('--output',type=Path,default=root/'calibration/rebuilt_seen_guard.json');p.add_argument('--risk-budget-pp',type=float,default=5.)
    a=p.parse_args();keys=json.loads(a.query_keys.read_text());settings=[];inventories={};audit=[]
    for sp in SPLITS:
        train,val=[dict(np.load(a.data/sp/(part+'.npz'),allow_pickle=False)) for part in ('train','val')]
        quality=dict(np.load(a.data/sp/'val_quality.npz',allow_pickle=False));np.testing.assert_array_equal(quality['qids'],val['qids'])
        for part,d in [('train',train),('val',val)]:assert keys[sp][part]['qids']==d['qids'].tolist()
        inventory=Counter(k for k,y in zip(keys[sp]['train']['keys'],train['labels']) if k is not None and y==1);inventories[sp]=dict(inventory)
        if not all(inventory.get(k,0)>0 for k in keys[sp]['val']['keys']):raise ValueError('This published calibration assumes Seen-val queries are covered; new data require a revised calibration audit')
        y=val['labels']
        for bb in BACKBONES:
            iou=quality[bb+'_accept_iou'];b=val_metrics(y,score(train,val,bb,'baseline'),iou);d=val_metrics(y,score(train,val,bb),iou);original=score(train,val,bb)
            candidates=[]
            for alpha in np.linspace(0,1,41):
                sc=blend_score(train,val,bb,float(alpha));m=val_metrics(y,sc,iou)
                main=m['auc']>=b['auc']-1e-12 and m['gmiou']>=max(b['gmiou'],d['gmiou'])-1e-12 and m['f1']>=max(b['f1'],d['f1'])-1e-12
                candidates.append(dict(alpha=float(alpha),metrics=m,main=bool(main),distance=float(np.mean((sc-original)**2))))
            strict=[c for c in candidates if c['main']];pool=strict or [c for c in candidates if c['metrics']['auc']>=b['auc']-1e-12]
            if not pool:raise ValueError('No validated blend candidate: '+sp+'/'+bb)
            chosen=min(pool,key=lambda c:c['distance']);alpha=chosen['alpha'];m=chosen['metrics']
            cal=dict(known_threshold=m['threshold'],dec_threshold=d['threshold'],known_scale=float(max(np.std(blend_score(train,train,bb,alpha)),1e-8)),dec_scale=float(max(np.std(score(train,train,bb)),1e-8)))
            config=dict(family='blend',alpha=alpha);extra={}
            if chosen['main'] and m['frr']<=d['frr']+1e-12:mode='calibrated_blend'
            elif not chosen['main']:
                raw=val['X'][:,BACKBONES[bb]].astype(np.float64)
                grouped=np.where(original>=d['threshold'],1.,-1.)+.25+np.arctan(raw)/(2*np.pi)
                if roc_auc_score(y,grouped)<b['auc']-1e-12:raise ValueError('Decision-preserving fallback fails Seen validation')
                mode='preserve_dec_decisions';config=dict(family='baseline');cal['known_threshold']=None;cal['known_scale']=None
            else:
                sc=score(train,val,bb,'baseline');options=[val_metrics(y,sc,iou,t) for t in np.percentile(sc,np.linspace(5,95,91))]
                eligible=[v for v in options if v['frr']<=d['frr']-a.risk_budget_pp+1e-12 and v['gmiou']>=d['gmiou']-1e-12 and v['f1']>=d['f1']-1e-12]
                if not eligible:raise ValueError('No FRR-constrained threshold')
                best=max(eligible,key=lambda v:v['ba']);mode='frr_constrained_baseline';config=dict(family='baseline');cal['known_threshold']=best['threshold'];cal['known_scale']=float(max(np.std(score(train,train,bb,'baseline')),1e-8));extra=dict(risk_budget_pp=a.risk_budget_pp,validation=best)
            settings.append(dict(split=sp,backbone=bb,mode=mode,config=config,calibration=cal,final_threshold=0.,**extra));audit.append(dict(split=sp,backbone=bb,baseline=b,dec=d,blend_candidates=candidates))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(dict(name='DEC-Power-CDF + Seen Guard',settings=settings,inventories=inventories,score_threshold=0.,additional_trainable_parameters=0,threshold_protocol_changed=True),indent=2)+'\n');a.output.with_suffix('.audit.json').write_text(json.dumps(audit,indent=2)+'\n');print('Rebuilt 15 configurations from train/Seen validation:',a.output)

if __name__=='__main__':main()
