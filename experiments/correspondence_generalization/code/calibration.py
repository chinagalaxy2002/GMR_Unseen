"""Seen-only positive-slope calibration control with an explicit fit budget."""
import numpy as np
import torch

def fit(rows,pred):
    pp={str(p['qid']):p for p in pred};s=np.array([pp[str(r['qid'])]['pred_exist_score'] for r in rows]);y=np.array([r['exist_label'] for r in rows]);x=np.log(s.clip(1e-6,1-1e-6)/(1-s.clip(1e-6,1-1e-6)))
    tx=torch.tensor(x,dtype=torch.float64);ty=torch.tensor(y,dtype=torch.float64);scale=torch.nn.Parameter(torch.zeros((),dtype=torch.float64));bias=torch.nn.Parameter(torch.zeros((),dtype=torch.float64));optimizer=torch.optim.Adam([scale,bias],lr=.01)
    for _ in range(100):
        optimizer.zero_grad();loss=torch.nn.functional.binary_cross_entropy_with_logits(scale.exp()*tx+bias,ty);loss.backward();optimizer.step()
    return {'positive_slope':float(scale.exp().detach()),'bias':float(bias.detach()),'updates':100,'seen_rows':len(rows),'seen_row_exposures':len(rows)*100,'per_seen_row_exposures':100,'training_row_exposures':0,'selection_source':'seen validation only','fit_forwards':100,'loss_final':float(loss.detach()),'parameters':2,'lr':.01,'seed':'deterministic zero initialization; no random draws'}
def transform(score,record):
    s=np.clip(np.asarray(score,dtype=np.float64),1e-6,1-1e-6);logit=np.log(s/(1-s))*record['positive_slope']+record['bias'];return 1/(1+np.exp(-logit))
