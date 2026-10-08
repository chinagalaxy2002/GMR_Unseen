"""Reproduce baseline, DEC and Seen Guard from portable frozen inputs."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from dec import SPLITS,BACKBONES,score,select_threshold
from evaluate import METRICS,metrics,restore_window_metrics
from seen_guard import score_seen_guard
from bootstrap_seen_guard import bootstrap

def main():
    root=Path(__file__).resolve().parent;p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=root/'data');p.add_argument('--config',type=Path,default=root/'calibration/seen_guard.json');p.add_argument('--query-keys',type=Path,default=root/'calibration/query_keys.json');p.add_argument('--output',type=Path,default=root/'reproduced_seen_guard');p.add_argument('--bootstrap',type=int,default=2000)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);f=json.loads(a.config.read_text());keys=json.loads(a.query_keys.read_text());records=[];datasets={};routing=[]
    for sp in SPLITS:
        train,val,test=[dict(np.load(a.data/sp/(part+'.npz'),allow_pickle=False)) for part in ('train','val','test')]
        assert keys[sp]['test']['qids']==test['qids'].tolist();restore_window_metrics(test,a.data/sp/'windows.jsonl')
        known=np.array([f['inventories'][sp].get(k,0)>0 for k in keys[sp]['test']['keys']]);routing.append(dict(split=sp,by_partition={str(part):dict(total=int(np.sum(test['partitions']==part)),covered=int(np.sum(known & (test['partitions']==part)))) for part in np.unique(test['partitions'])}))
        for bb in BACKBONES:
            for method in ('baseline','dec'):
                sc=score(train,test,bb,method);t=select_threshold(val['labels'],score(train,val,bb,method));test[bb+'_'+method]=sc;test[bb+'_'+method+'_threshold']=t;records.append(dict(split=sp,backbone=bb,method=method,threshold=t,**metrics(test,sc,t,bb)))
            setting=next(r for r in f['settings'] if r['split']==sp and r['backbone']==bb)
            minimal={'X':test['X'],'queries':test['queries']};sc=score_seen_guard(train,minimal,setting,keys[sp]['test']['keys'],f['inventories'][sp]);test[bb+'_guarded']=sc;test[bb+'_guarded_threshold']=0.;records.append(dict(split=sp,backbone=bb,method='seen_guard',threshold=0.,**metrics(test,sc,0.,bb)))
        datasets[sp]=test
    for bb in BACKBONES:
        for method in ('baseline','dec','seen_guard'):
            selected=[r for r in records if r['backbone']==bb and r['method']==method];records.append(dict(split='MACRO',backbone=bb,method=method,threshold=None,**{k:float(np.mean([r[k] for r in selected])) for k in METRICS}))
    (a.output/'metrics.json').write_text(json.dumps(records,indent=2)+'\n')
    with (a.output/'metrics.csv').open('w',newline='') as file:w=csv.DictWriter(file,fieldnames=['split','backbone','method','threshold']+list(METRICS),lineterminator='\n');w.writeheader();w.writerows(records)
    (a.output/'routing_audit.json').write_text(json.dumps(routing,indent=2)+'\n')
    if a.bootstrap>0:(a.output/'bootstrap.json').write_text(json.dumps(bootstrap(datasets,a.bootstrap),indent=2)+'\n')
    print('Reproduced 15 settings and five-split macro for three methods:',a.output)

if __name__=='__main__':main()
