"""Matched-pair preserving video controls and independent AUROC uncertainty."""
import json
from pathlib import Path
import numpy as np
from diagnose import BASE, ROOT, OUT, SPLITS, rows, module, cosine, pair_indices, metrics, exact_pairs, write

report={};boot={};detboot={}
for split in SPLITS:
    with np.load(OUT/(split+'_frozen_scores.npz')) as z:d={k:z[k] for k in z.files}
    boot[split]={'y':d['labels'],'parts':d['partitions'],'vids':d['vids'],'original':d['baseline'],'final':d['full']}
    detboot[split]={**boot[split],'original':d['detector_only']}
    raw=d['object_raw'];prior=raw-d['object_evidence']
    report[split]={'object_raw_std':float(raw.std()),'object_prior_std':float(prior.std()),
        'object_evidence_vs_negative_prior_correlation':float(np.corrcoef(d['object_evidence'],-prior)[0,1])}
mod=module('clean_bootstrap_diagnosis',BASE/'train_and_eval.py')
ci=mod.run_cluster_bootstrap(boot,2000,20261005);di=mod.run_cluster_bootstrap(detboot,2000,20261005)
report['full_vs_baseline_video_bootstrap']=ci
report['full_vs_detector_video_bootstrap']=di

with np.load(OUT/'A1_test_clip_scores.npz') as z:d={k:z[k] for k in z.files}
with np.load(BASE/'clean_features/A1/test.npz') as z:glob=z['v_clip_glob']
pp=pair_indices(d,'A1');meta={str(r['qid']):r for r in rows(ROOT/'data/release/semantic_existence_v2/A1/test.jsonl')}
ep,sizes=exact_pairs(d,meta);uv,first,vi=np.unique(d['vids'],return_index=True,return_inverse=True)
rng=np.random.default_rng(3407);controls=[];control_scores=[]
for rep in range(5):
    perm=rng.permutation(len(uv))
    # Cyclic rotations keep a bijection and exclude donors from the same video.
    if np.any(perm==np.arange(len(uv))):perm=np.roll(np.arange(len(uv)),int(rng.integers(1,len(uv))))
    assert not np.any(perm==np.arange(len(uv)))
    s=cosine(d['query_EOT_projected'],glob[first[perm[vi]]])
    controls.append(metrics(s,d,pp,ep));control_scores.append(s)
pv=d['vids'][pp[:,0]];unique_pair_video,pvi=np.unique(pv,return_inverse=True)
counts=np.bincount(pvi,minlength=len(unique_pair_video))
actual=d['fresh_EOT_projected_global'];values={}
for k,s in [('actual',actual),('fixed_query_reference',d['query_only_fixed_train_video_reference'])]+[(f'shuffle_{i}',s) for i,s in enumerate(control_scores)]:
    values[k]=(s[pp[:,0]]>s[pp[:,1]]).astype(float)+.5*(s[pp[:,0]]==s[pp[:,1]])
sums={k:np.bincount(pvi,weights=v,minlength=len(counts)) for k,v in values.items()}
rng=np.random.default_rng(20261005);samples={k:[] for k in sums}
for rep in range(2000):
    w=np.bincount(rng.integers(len(counts),size=len(counts)),minlength=len(counts))
    for k in samples:samples[k].append(float(w@sums[k]/(w@counts)))
report['A1_pair_preserving_CLIP_global_controls']={'same_donor_video_for_both_queries':True,
    'actual':metrics(actual,d,pp,ep),'controls':controls,
    'actual_minus_controls_pairacc_95ci':{k:np.quantile(np.array(samples['actual'])-np.array(samples[k]),[.025,.975]).tolist() for k in samples if k!='actual'},
    'pair_n':len(pp),'pair_video_clusters':len(unique_pair_video)}
write('paired_controls.json',report)
print(json.dumps(report,indent=2,allow_nan=False))
