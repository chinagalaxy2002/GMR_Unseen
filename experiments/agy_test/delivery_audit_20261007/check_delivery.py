"""Independent definitions/alignment/partition audit, retaining original thresholds."""
import importlib.util,json
from pathlib import Path
import numpy as np
from sklearn.metrics import f1_score,roc_auc_score
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
BASE=ROOT/'experiments/agy_test/detr_decoder_gmr'
spec=importlib.util.spec_from_file_location('source',BASE/'run_thresholded_gmr_eval.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
details=[];videos={}; splits_auc=[];empties=[]
for split in m.SPLITS:
    d={z:dict(np.load(BASE/'cache'/split/(z+'.npz'))) for z in ['train','val','test']}
    gt={z:m.rows(ROOT/'data/release/semantic_existence_v2'/split/(z+'.jsonl')) for z in d}
    q={}
    for z in d:
        rows=gt[z] if z!='val' else [r for r in gt[z] if r['partition'] in ['S+','S-']]
        assert list(map(str,d[z]['qids']))==[str(r['qid']) for r in rows]
        assert all(r['exist_label']==y and r['vid']==str(v) for r,y,v in zip(rows,d[z]['labels'],d[z]['vids']))
        if z!='test':assert all(r['partition'] in ['S+','S-'] for r in rows)
        q[z]=[r['query'].lower() for r in rows]
    ev={z:m.route_evidence(q[z],d[z]['X']) for z in d}
    videos[split]=set(map(str,d['test']['vids']))
    for bb,(bbdir,col,fn) in m.BACKBONES.items():
        pred={str(r['qid']):r for r in m.rows(ROOT/f'results/semantic_existence/multi_split_v2/{split}/{bbdir}/test/{fn}')}
        assert set(pred)==set(map(str,d['test']['qids']))
        empties.append({'split':split,'bb':bb,'empty_published':sum(not r.get('pred_relevant_windows') for r in pred.values()),'empty_pre_exist':sum(not r.get('pred_relevant_windows_pre_exist') for r in pred.values())})
        scores={}
        for z in ['val','test']:
            rd=m.cdf(d['train']['X'][:,col],d[z]['X'][:,col]); re=m.cdf(ev['train'],ev[z])
            scores[z]={'baseline':d[z]['X'][:,col],'power':rd**.65*re**.85,'wsum':.5*(rd+re)}
        for arm in scores['val']:
            th=m.find_best_threshold(d['val']['labels'],scores['val'][arm])
            sc=scores['test'][arm]; reject=sc<th; y=d['test']['labels']; parts=d['test']['partitions']
            for group,ix in [('All',np.ones(len(y),bool)),('Seen',np.isin(parts,['S+','S-'])),('Unseen',np.isin(parts,['U+','U-']))]:
                yy=y[ix];rr=reject[ix]; neg=yy==0;pos=yy==1
                tn=int(np.sum(rr&neg));fp=int(np.sum(~rr&neg)); fn=int(np.sum(rr&pos))
                details.append({'split':split,'backbone':bb,'arm':arm,'group':group,'tau':float(th),
                    'rej_f1':float(f1_score(1-yy,rr,zero_division=0)), 'negative_recall':tn/(tn+fp),
                    'overall_rejected_fraction':float(rr.mean()),'positive_frr':float(rr[pos].mean()),
                    'tn':tn,'fp':fp,'fn':fn,'auc':float(roc_auc_score(yy,sc[ix]))})
                assert details[-1]['rej_f1']<=2*details[-1]['negative_recall']/(1+details[-1]['negative_recall'])+1e-12
            splits_auc.append({'split':split,'bb':bb,'arm':arm,'seen':float(roc_auc_score(y[np.isin(parts,['S+','S-'])],sc[np.isin(parts,['S+','S-'])])),'unseen':float(roc_auc_score(y[np.isin(parts,['U+','U-'])],sc[np.isin(parts,['U+','U-'])]))})
macro=[]
for bb in m.BACKBONES:
    for arm in ['baseline','power','wsum']:
        for g in ['All','Seen','Unseen']:
            r=[x for x in details if x['backbone']==bb and x['arm']==arm and x['group']==g]
            macro.append({'bb':bb,'arm':arm,'group':g,**{k:float(np.mean([v[k] for v in r])) for k in ['rej_f1','negative_recall','overall_rejected_fraction','positive_frr','auc']}})
overlap={a+'__'+b:len(videos[a]&videos[b]) for i,a in enumerate(m.SPLITS) for b in m.SPLITS[i+1:]}
out={'macro':macro,'details':details,'split_auroc':splits_auc,'cross_split_video_overlap':overlap,'window_counts':empties,'alignment':'all train/Seen-val/test qids,labels,vids aligned; no missing target proposals'}
(OUT/'audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
