"""Measure the annotation-presence label channel in every saved DAO subset."""
from pathlib import Path
import json
import numpy as np
from sklearn.metrics import roc_auc_score

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
result={}
for split in ['A1','A2_alt','A3','C1','C2_alt']:
    result[split]={}
    for subset in ['train','val','test']:
        d=np.load(ROOT/'experiments/agy_test/decomposed_action_object_verifier/features'/split/(subset+'.npz'))
        meta={str(x['qid']):x for x in [json.loads(l) for l in (ROOT/'data/release/semantic_existence_v2'/split/(subset+'.jsonl')).read_text().splitlines()]}
        act,obj=d['q_act'],d['q_obj'];y=d['labels'];dist=np.linalg.norm(act-obj,axis=1)
        equal=np.all(act==obj,axis=1)
        has_act=np.array([meta[str(q)]['semantic_graph'].get('action_span') is not None for q in d['qids']])
        has_obj=np.array([meta[str(q)]['semantic_graph'].get('object_span') is not None for q in d['qids']])
        item={'q_act_q_obj_distance_AUROC':float(roc_auc_score(y,dist)),'counts':{}}
        for name,mask in [('positive',y==1),('negative',y==0)]:
            item['counts'][name]={'n':int(mask.sum()),'action_span_present':int(has_act[mask].sum()),'object_span_present':int(has_obj[mask].sum()),'q_act_equals_q_obj':int(equal[mask].sum())}
        if subset=='test':
            seen=np.isin(d['partitions'],['S+','S-'])
            item.update(Seen_AUROC=float(roc_auc_score(y[seen],dist[seen])),Unseen_AUROC=float(roc_auc_score(y[~seen],dist[~seen])))
        result[split][subset]=item
        print(split,subset,item,flush=True)
(OUT/'annotation_label_channel.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
