import sys,json
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'v3_release_baselines_20261009'))
from run_baselines import metrics,read_rows,_clean_pred_windows,_compute_set_iou_score
old=root/'v3_addseen_20261009'; refs=json.loads((old/'cog_evaluation/metrics.json').read_text()); checks=[]
for bb in ('moment','qd','flash'):
    group='A1_v3'; task=old/'groups'/group
    rows=read_rows(task/'release'/group/'test.jsonl')
    pp=read_rows(task/'runs'/bb/'test'/('hl_test_submission.jsonl' if bb=='flash' else bb+'_detr_gmr_test_submission.jsonl'))
    preds={str(r['qid']):r for r in pp}
    ref=next(r for r in refs if r['split']==group and r['backbone']==bb and r['method']=='Baseline')
    y=np.array([r['exist_label'] for r in rows]);p=np.array([r['partition'] for r in rows]);scores=np.array([preds[str(r['qid'])]['pred_exist_logit' if bb=='flash' else 'pred_exist_score'] for r in rows],np.float32)
    iou=np.array([_compute_set_iou_score([w[:2] for w in _clean_pred_windows(preds[str(r['qid'])]['pred_relevant_windows'],1)],r['relevant_windows']) for r in rows])
    result=metrics(y,p,scores,ref['threshold'],iou,np.ones(len(y)))
    for key in result: np.testing.assert_allclose(result[key],ref[key],atol=1e-7,rtol=0)
    checks.append(dict(backbone=bb,rows=len(rows),parity='all eight metrics within 1e-7 of corrected historical evaluator'))
(root/'v3_release_baselines_20261009/EVALUATOR_PARITY.json').write_text(json.dumps(checks,indent=2)+'\n')
print(checks)
