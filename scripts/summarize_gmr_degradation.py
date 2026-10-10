#!/usr/bin/env python3
"""Summarize Seen/Unseen GMR degradation from frozen predictions.npz files."""
import argparse
import csv
import hashlib
import json
import time
from pathlib import Path
import numpy as np

NAMES = {'moment':'Moment-DETR-GMR','qd':'QD-DETR-GMR','flash':'FlashVTG-GMR'}
GROUPS = ('A1_v3','A2_v3','A3_v3','C1_v3','C2_v3')
KEYS = ('seen_rej_f1','unseen_rej_f1','rej_f1_gap_pp','seen_gmiou1','unseen_gmiou1','gmiou1_gap_pp')


def save(path, obj):
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    tmp.replace(path)


def summarize(path, count, seed):
    data = np.load(path,allow_pickle=False)
    y,p,scores = data['labels'],data['partitions'],data['scores']
    accept = scores >= float(data['threshold'])
    gmiou = np.where(accept,data['accept_iou'],y==0)
    videos,vi = np.unique(data['vids'],return_inverse=True)
    # Aggregate sufficient statistics per video, retaining within-video dependence.
    columns = []
    counts = {}
    for prefix in ('S','U'):
        mask = np.char.startswith(p,prefix)
        counts[prefix] = dict(rows=int(mask.sum()),positive=int((mask&(y==1)).sum()),negative=int((mask&(y==0)).sum()))
        for values in (mask&(y==0)&~accept,mask&(y==0)&accept,mask&(y==1)&~accept,mask,mask*gmiou):
            columns.append(np.bincount(vi,weights=values,minlength=len(videos)))
    sufficient = np.array(columns).T
    def readout(sums):
        result = []
        for start in (0,5):
            tn,fp,fn,n,gi = [sums[...,start+i] for i in range(5)]
            denominator = 2*tn+fp+fn
            # Undefined F1 (no rejection positives/predictions) remains NaN.
            f1 = np.divide(200*tn,denominator,out=np.full_like(tn,np.nan,dtype=float),where=denominator>0)
            g = np.divide(100*gi,n,out=np.full_like(n,np.nan,dtype=float),where=n>0)
            result.append((f1,g))
        sf,sg = result[0]; uf,ug = result[1]
        return np.stack([sf,uf,sf-uf,sg,ug,sg-ug],axis=-1)
    point = readout(sufficient.sum(axis=0))
    rng = np.random.RandomState(seed)
    # Same sorted video universe and randint sampler as the baseline AUROC bootstrap.
    weights = np.array([np.bincount(rng.randint(len(videos),size=len(videos)),minlength=len(videos)) for _ in range(count)])
    draws = readout(weights@sufficient)
    intervals = {}
    for i,key in enumerate(KEYS):
        finite = draws[np.isfinite(draws[:,i]),i]
        intervals[key] = dict(ci95=np.percentile(finite,[2.5,97.5]).tolist() if len(finite) else None,valid_draws=len(finite))
    return dict(zip(KEYS,map(float,point))), intervals, draws, videos, counts


def build(root,count,seed):
    output = root/'evaluation'; output.mkdir(exist_ok=True)
    records,intervals,all_draws = [],{},{}
    cache = output/'degradation_cache'; cache.mkdir(exist_ok=True)
    for path in sorted(root.glob('groups/*/evaluation/*/predictions.npz')):
        group,bb = path.parents[2].name,path.parent.name
        metric_path = path.parent/'metrics.json'
        if not metric_path.exists(): continue
        signature = hashlib.sha256(path.read_bytes()).hexdigest()+f':{count}:{seed}'
        cached = cache/f'{group}_{bb}.json'; draw_path = cache/f'{group}_{bb}.npz'
        if cached.exists() and json.loads(cached.read_text())['signature']==signature:
            saved = json.loads(cached.read_text()); point,ci,counts = saved['point'],saved['intervals'],saved['counts']
            d=np.load(draw_path); draws,videos=d['draws'],d['videos']
        else:
            point,ci,draws,videos,counts=summarize(path,count,seed)
            np.savez_compressed(draw_path,draws=draws,videos=videos,keys=np.array(KEYS))
            save(cached,dict(signature=signature,point=point,intervals=ci,counts=counts))
        base=json.loads(metric_path.read_text())
        records.append(dict(**base,**point,seen_n=counts['S']['rows'],unseen_n=counts['U']['rows'],seen_positive_n=counts['S']['positive'],unseen_positive_n=counts['U']['positive']))
        auc_bootstrap=json.loads((path.parent/'bootstrap.json').read_text())
        ci=dict(ci)
        ci['auroc_gap_pp']=dict(ci95=[100*x for x in auc_bootstrap['absolute']['gap']],valid_draws=auc_bootstrap['valid_draws'])
        intervals[group+'|'+bb]=ci
        all_draws[(group,bb)]=(draws,videos)
    for bb in NAMES:
        rr=[r for r in records if r['backbone']==bb]
        if set(r['split'] for r in rr)!=set(GROUPS): continue
        dd=[all_draws[(g,bb)] for g in GROUPS]
        assert all(np.array_equal(dd[0][1],d[1]) for d in dd)
        macro=np.mean([d[0] for d in dd],axis=0)
        numerical=[k for k in rr[0] if k not in ('split','backbone','method','threshold')]
        records.append(dict(split='MACRO',backbone=bb,method='Baseline',threshold=None,**{k:float(np.mean([r[k] for r in rr])) for k in numerical}))
        ci={}
        for i,k in enumerate(KEYS):
            finite=macro[np.isfinite(macro[:,i]),i]
            ci[k]=dict(ci95=np.percentile(finite,[2.5,97.5]).tolist() if len(finite) else None,valid_draws=len(finite))
        auc_draws=[np.load(root/'groups'/g/'evaluation'/bb/'bootstrap_draws.npz') for g in GROUPS]
        gap_draws=np.mean([d['draws'][:,list(d['keys']).index('gap')] for d in auc_draws],axis=0)*100
        finite=gap_draws[np.isfinite(gap_draws)]
        ci['auroc_gap_pp']=dict(ci95=np.percentile(finite,[2.5,97.5]).tolist(),valid_draws=len(finite))
        intervals['MACRO|'+bb]=ci
    save(output/'degradation_metrics.json',records)
    save(output/'degradation_bootstrap.json',dict(draws=count,seed=seed,unit='video cluster; frozen Seen-validation threshold',intervals=intervals))
    if records:
        with (output/'degradation_metrics.csv').open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    lines=['# Seen–Unseen degradation: AUROC, Rej-F1 and G-mIoU@1','',f'Completed settings: {sum(r["split"]!="MACRO" for r in records)}/15. Gap = Seen − Unseen; positive means deterioration, negative means improvement. All gaps use percentage points (pp). Rej-F1 and G-mIoU are percentages; AUROC is 0–1. Thresholds and checkpoints are selected on Seen validation only and remain fixed for both subsets.','', '| Split | Backbone | Seen AUROC | Unseen AUROC | AUROC Gap (pp) | Seen Rej-F1 | Unseen Rej-F1 | Rej-F1 Gap (pp) | Seen G-mIoU@1 | Unseen G-mIoU@1 | G-mIoU Gap (pp) |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in records:
        lines.append(f"| {r['split']} | {NAMES[r['backbone']]} | {r['seen_auc']:.4f} | {r['unseen_auc']:.4f} | {100*r['gap']:+.2f} | {r['seen_rej_f1']:.2f}% | {r['unseen_rej_f1']:.2f}% | {r['rej_f1_gap_pp']:+.2f} | {r['seen_gmiou1']:.2f}% | {r['unseen_gmiou1']:.2f}% | {r['gmiou1_gap_pp']:+.2f} |")
    lines+=['','| Split / Backbone | Overall Rej-F1 | Overall RR | S+ FRR | U+ FRR | Overall G-mIoU@1 | Seen rows (+) | Unseen rows (+) |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in records:
        lines.append(f"| {r['split']} / {NAMES[r['backbone']]} | {r['rej_f1']:.2f}% | {r['rr']:.2f}% | {r['s_frr']:.2f}% | {r['u_frr']:.2f}% | {r['gmiou1']:.2f}% | {r['seen_n']:g} ({r['seen_positive_n']:g}) | {r['unseen_n']:g} ({r['unseen_positive_n']:g}) |")
    lines+=['',f'95% CI uses {count:,} paired video-cluster bootstrap draws (seed {seed}). Valid draw counts are recorded per metric; undefined F1 draws are omitted.','', '| Split / Backbone | AUROC Gap 95% CI (pp) | Rej-F1 Gap 95% CI (pp) | G-mIoU Gap 95% CI (pp) |','|---|---:|---:|---:|']
    for r in records:
        ci=intervals[r['split']+'|'+r['backbone']]
        formatted=[]
        for k in ('auroc_gap_pp','rej_f1_gap_pp','gmiou1_gap_pp'):
            limits=ci[k]['ci95']; formatted.append(f'[{limits[0]:+.2f}, {limits[1]:+.2f}]' if limits else 'undefined')
        lines.append(f"| {r['split']} / {NAMES[r['backbone']]} | {' | '.join(formatted)} |")
    lines+=['','Seen metrics use S+/S−; Unseen metrics use U+/U−. Rej-F1 = 2TN/(2TN+FP+FN), with rejection as positive. G-mIoU includes positives and negatives: accepted queries use native top-1 set IoU; rejected negatives score 1, rejected positives score 0. Different class proportions between subsets affect Rej-F1 and G-mIoU; these gaps describe the released test subsets rather than controlling for prevalence. Negative gaps are preserved, not forced into a deterioration claim. Formal MACRO rows require all five groups; counts in MACRO rows are group averages, not distinct-query totals.','', 'The original requested branch tables and AUROC bootstrap intervals remain in [STANDARD_EVALUATION.md](STANDARD_EVALUATION.md). All Seen/Unseen absolute and gap CIs for Rej-F1 and G-mIoU are in degradation_bootstrap.json.','']
    (output/'GENERALIZATION_DROP_COMPARISON.md').write_text('\n'.join(lines))
    return len([r for r in records if r['split']!='MACRO'])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--experiment',type=Path,required=True)
    parser.add_argument('--bootstrap',type=int,default=2000)
    parser.add_argument('--seed',type=int,default=3407)
    parser.add_argument('--watch',action='store_true')
    args=parser.parse_args(); root=args.experiment.resolve()
    while True:
        n=build(root,args.bootstrap,args.seed)
        if not args.watch: break
        status=root/'FINAL_EVALUATION_STATUS.json'
        if status.exists() and json.loads(status.read_text()).get('complete'):
            build(root,args.bootstrap,args.seed); break
        time.sleep(30)
    print(f'Summarized {n} completed settings',flush=True)

if __name__=='__main__': main()
