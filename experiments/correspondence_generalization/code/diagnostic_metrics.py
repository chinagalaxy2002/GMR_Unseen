"""Raw localization and seen-threshold diagnostic hard rejection."""
import json
from pathlib import Path
import numpy as np

def iou(a,b):
    inter=max(0,min(a[1],b[1])-max(a[0],b[0]));union=max(a[1],b[1])-min(a[0],b[0]);return inter/max(union,1e-9)
def localization(dst,rows,scores,threshold):
    preds={r['qid']:r for r in (json.loads(l) for l in Path(dst).read_text().splitlines())}
    positive=[];accepted=[]
    for r,s in zip(rows,scores):
        if r['exist_label']!=1:continue
        wins=preds[r['qid']].get('pred_relevant_windows_pre_exist',[])
        gt=r['relevant_windows'];val=max((iou(wins[0],g) for g in gt),default=0.) if wins else 0.
        positive.append(val);accepted.append(s>=threshold)
    v=np.array(positive);acc=np.array(accepted)
    return {'positive_rows':len(v),'diagnostic_hard_threshold':float(threshold),'raw_R1@0.5':float((v>=.5).mean()),'raw_R1@0.7':float((v>=.7).mean()),'hard_R1@0.5':float(((v>=.5)&acc).mean()),'hard_R1@0.7':float(((v>=.7)&acc).mean()),'raw_correct_positive_false_reject_0.5':float((~acc[v>=.5]).mean()) if (v>=.5).any() else None,'raw_correct_positive_false_reject_0.7':float((~acc[v>=.7]).mean()) if (v>=.7).any() else None,'raw_miou':float(v.mean()),'hard_miou':float((v*acc).mean()),'scope':'training-side pseudo-unseen or seen only; not real U or positive-only VTG'}
