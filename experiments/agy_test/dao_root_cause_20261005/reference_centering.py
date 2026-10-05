"""Predefined query centering against an unlabeled train-video reference; no fitting."""
import json
import numpy as np
from diagnose import BASE, OUT, ROOT, norm, metrics, pair_indices, exact_pairs, rows, write

with np.load(BASE/'clean_features/A1/train.npz') as z:
    video=z['v_clip_glob'];_,ix=np.unique(z['vids'],return_index=True)
reference=norm(video[ix]).mean(0)
result={}
for subset in ['train','val','test']:
    with np.load(OUT/('A1_'+subset+'_clip_scores.npz')) as z:
        d={k:z[k] for k in ['qids','vids','labels','partitions','query_EOT_projected']}
        expected=d['query_EOT_projected']@reference
        scores={k+'_minus_train_reference':z[k]-expected for k in ['fresh_EOT_projected_candidate','fresh_EOT_projected_global']}
    pp=pair_indices(d,'A1') if subset=='test' else np.empty((0,2),int)
    meta={str(r['qid']):r for r in rows(ROOT/'data/release/semantic_existence_v2/A1'/(subset+'.jsonl'))}
    ep,_=exact_pairs(d,meta)
    result[subset]={k:metrics(s,d,pp,ep) for k,s in scores.items()}
    np.savez_compressed(OUT/('A1_'+subset+'_reference_centered_scores.npz'),qids=d['qids'],vids=d['vids'],labels=d['labels'],partitions=d['partitions'],**scores)
write('A1_reference_centering_diagnosis.json',{'scope':'predefined unlabelled unique-train-video reference, no fitted weights; exploratory diagnostic, not a selected final method',
    'reference_norm':float(np.linalg.norm(reference)),'subsets':result})
print(json.dumps(result,indent=2,allow_nan=False))
