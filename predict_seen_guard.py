"""Annotation-free inference; parser and historical numeric environments are separate."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from seen_guard import score_seen_guard

def main():
    root=Path(__file__).resolve().parent;p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--split',required=True,choices=('A1','A2_alt','A3','C1','C2_alt'));p.add_argument('--backbone',required=True,choices=('moment','qd','flash'));p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--parser-python',required=True);p.add_argument('--config',type=Path,default=root/'calibration/seen_guard.json')
    a=p.parse_args();f=json.loads(a.config.read_text());setting=next(r for r in f['settings'] if r['split']==a.split and r['backbone']==a.backbone)
    with np.load(a.input,allow_pickle=False) as z:
        target={'X':z['X'].copy(),'queries':z['queries'].copy()};qids=z['qids'].copy() if 'qids' in z.files else np.arange(len(z['queries'])).astype(str)
    if target['X'].shape!=(len(target['queries']),14) or not np.isfinite(target['X']).all():raise ValueError('Expected finite N x 14 features and N queries')
    code='import json,sys; sys.path.insert(0,sys.argv[1]); from text_router import parse_queries; print(json.dumps(parse_queries(json.loads(sys.stdin.read()))))'
    parsed=subprocess.run([a.parser_python,'-c',code,str(root)],input=json.dumps(target['queries'].tolist()),text=True,capture_output=True,check=True);keys=json.loads(parsed.stdout)
    train=dict(np.load(root/'data'/a.split/'train.npz',allow_pickle=False));sc=score_seen_guard(train,target,setting,keys,f['inventories'][a.split]);a.output.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(a.output,qids=qids,scores=sc,accept=sc>=0.,query_keys=np.array([k or '' for k in keys]));print('Saved',len(sc),'annotation-free predictions:',a.output)

if __name__=='__main__':main()
