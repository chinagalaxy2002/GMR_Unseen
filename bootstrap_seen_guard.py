"""Fixed-calibration paired shared-video bootstrap."""
import numpy as np
from dec import SPLITS, BACKBONES
from evaluate import auc_plan, weighted_auc
COLS=BACKBONES

def bootstrap(datasets,n=2000):
    videos=np.unique(np.concatenate([d['vids'] for d in datasets.values()]));plans={};sufficient={}
    for sp,d in datasets.items():
        vi=np.searchsorted(videos,d['vids']);y=d['labels']
        for bb in COLS:
            for m in ('baseline','dec','guarded'):
                sc=d[bb+'_'+m];a=sc>=d[bb+'_'+m+'_threshold']
                for name,prefix in [('seen','S'),('unseen','U')]:
                    mask=np.char.startswith(d['partitions'],prefix);plans[sp,bb,m,name]=auc_plan(y[mask],sc[mask],vi[mask])
                g=np.where(a,d[bb+'_accept_iou'],d['reject_iou'])
                sufficient[sp,bb,m]=np.stack([np.bincount(vi,weights=w,minlength=len(videos)) for w in (np.ones(len(y)),g,((y==0)&~a).astype(float),((y==0)&a).astype(float),((y==1)&~a).astype(float),((d['partitions']=='S+')&~a).astype(float),(d['partitions']=='S+').astype(float),((d['partitions']=='U+')&~a).astype(float),(d['partitions']=='U+').astype(float))])
    fields=('seen_vs_baseline_pp','seen_vs_dec_pp','unseen_vs_baseline_pp','unseen_vs_dec_pp','gmiou_vs_dec_pp','f1_vs_dec_pp','s_frr_improvement_pp','u_frr_improvement_pp')
    draws={(sp,bb):[] for sp in SPLITS for bb in COLS};rng=np.random.RandomState(3407);valid=0
    for index in range(n):
        weights=np.bincount(rng.choice(len(videos),len(videos),replace=True),minlength=len(videos));current={}
        for sp in SPLITS:
            for bb in COLS:
                au={m:{subset:weighted_auc(plans[sp,bb,m,subset],weights) for subset in ('seen','unseen')} for m in ('baseline','dec','guarded')}
                old=sufficient[sp,bb,'dec']@weights;new=sufficient[sp,bb,'guarded']@weights
                f1=lambda x:100*2*x[2]/(2*x[2]+x[3]+x[4])
                current[sp,bb]=[100*(au['guarded']['seen']-au['baseline']['seen']),100*(au['guarded']['seen']-au['dec']['seen']),100*(au['guarded']['unseen']-au['baseline']['unseen']),100*(au['guarded']['unseen']-au['dec']['unseen']),100*(new[1]-old[1])/new[0],f1(new)-f1(old),100*(old[5]/old[6]-new[5]/new[6]),100*(old[7]/old[8]-new[7]/new[8])]
        if not all(np.all(np.isfinite(v)) for v in current.values()):continue
        valid+=1
        for k,v in current.items():draws[k].append(v)
        if (index+1)%500==0:print('Bootstrap',index+1,'/',n,flush=True)
    output={}
    for (sp,bb),values in draws.items():output[sp+'|'+bb]={k:v.tolist() for k,v in zip(fields,np.percentile(values,[2.5,97.5],axis=0).T)}
    for bb in COLS:
        macro=np.mean([draws[sp,bb] for sp in SPLITS],axis=0)
        output['MACRO|'+bb]={k:v.tolist() for k,v in zip(fields,np.percentile(macro,[2.5,97.5],axis=0).T)}
    return dict(requested_draws=n,valid_draws=valid,seed=3407,unit='shared video cluster',intervals=output,limitations='Fixed train statistics, fixed validation selections and fixed thresholds; excludes method search uncertainty. Benchmarks were repeatedly exposed during exploratory method development.')
