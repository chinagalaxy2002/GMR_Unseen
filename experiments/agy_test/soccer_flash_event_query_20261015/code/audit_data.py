"""Fail closed on missing features, dimensions, or inconsistent official labels."""
from common import ROOT,ASSETS,save,sha,rows,scope_audit
import numpy as np
from collections import Counter

def main():
    reports={};groups={};missing=[];features={}
    for split,n in [('train',4138),('val',465),('test',1036)]:
        data=rows(ROOT/'data'/f'{split}.jsonl');assert len(data)==n
        assert len({d['qid'] for d in data})==n
        groups[split]={'qids':{d['qid'] for d in data},'vids':{d['vid'] for d in data}}
        for d in data:
            assert d['duration']>0
            for s,e in d['relevant_windows']:assert 0<=s<e<=d['duration'],d
            for folder,key,dim,name in [('slowfast','features',2304,d['vid']),('clip','features',512,d['vid']),('clip_text','last_hidden_state',512,f"qid{d['qid']}")]:
                path=ASSETS/folder/f'{name}.npz'
                if str(path) in features:continue
                if not path.exists():missing.append(str(path));continue
                with np.load(path,allow_pickle=False) as z:
                    a=z[key];assert a.ndim==2 and a.shape[0]>0 and a.shape[1]==dim,(path,a.shape)
                    assert np.isfinite(a).all(),path
                    features[str(path)]={'shape':list(a.shape),'sha256':sha(path)}
        reports[split]={'n':n,'positive':sum(bool(d['relevant_windows']) for d in data),
                        'negative':sum(not d['relevant_windows'] for d in data),
                        'multi':sum(len(d['relevant_windows'])>1 for d in data),
                        'gt_count':dict(Counter(len(d['relevant_windows']) for d in data)),
                        'label_sha256':sha(ROOT/'data'/f'{split}.jsonl')}
    overlaps={}
    for a,b in [('train','val'),('train','test'),('val','test')]:
        overlaps[a+'/'+b]={k:len(groups[a][k]&groups[b][k]) for k in ['qids','vids']}
        assert not overlaps[a+'/'+b]['qids']
        assert not overlaps[a+'/'+b]['vids'],overlaps
    save(ROOT/'DATA_AUDIT.json',{'state':'FAIL' if missing else 'PASS','splits':reports,'overlaps':overlaps,
         'missing_features':missing,'feature_files':len(features),'asset_root':str(ASSETS),'outside_source':scope_audit()})
    save(ROOT/'provenance/FEATURE_MANIFEST.json',features)
    assert not missing,f'{len(missing)} missing features'
    print(reports,flush=True)
if __name__=='__main__':main()
