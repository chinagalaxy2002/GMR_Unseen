"""Ordinary capacity control and conditional window-supervised correspondence.
No teacher, new rows, synthetic queries, or new absence labels.
"""
import torch
from torch import nn

class ResidualAdapter(nn.Module):
    def __init__(self,d=256,k=64):
        super().__init__();self.down=nn.Linear(d,k);self.up=nn.Linear(k,d)
        nn.init.zeros_(self.up.weight);nn.init.zeros_(self.up.bias)
    def forward(self,x):return x+self.up(torch.relu(self.down(x)))

def attach(model,method):
    captured={};handles=[]
    if method in ('adapter','window'):
        # Identical trainable capacity and initialization for these two controls.
        for name in ('input_vid_proj','input_txt_proj'):
            layer=getattr(model,name);layer.add_module('correspondence_adapter',ResidualAdapter(model.transformer.d_model))
    if method=='window':
        for key,name in [('video','input_vid_proj'),('text','input_txt_proj')]:
            def hook(m,i,o,key=key):captured[key]=o
            handles.append(getattr(model,name).register_forward_hook(hook))
    return captured,handles

def window_mass_loss(captured,inputs,targets):
    """Positive window-mass supervision, not absent labels for outside frames."""
    if not captured:return inputs['src_vid'].sum()*0
    v=captured['video'];t=captured['text'];tm=inputs['src_txt_mask']
    q=(t*tm[...,None]).sum(1)/tm.sum(1)[:,None].clamp_min(1)
    logits=(v*q[:,None]).sum(-1)/(v.shape[-1]**.5)
    vm=inputs['src_vid_mask'].bool();logits=logits.masked_fill(~vm,float('-inf'));loss=[]
    for i,r in enumerate(targets['span_labels']):
        if 'exist_label' in targets and targets['exist_label'][i].item()==0:continue
        spans=r['spans']
        if len(spans)==0:continue
        length=int(vm[i].sum());centers=(torch.arange(length,device=v.device)+.5)/length
        start=spans[:,0]-spans[:,1]/2;end=spans[:,0]+spans[:,1]/2
        inside=((centers[:,None]>=start)&(centers[:,None]<=end)).any(-1)
        if not inside.any():
            inside[(centers-spans[0,0]).abs().argmin()]=True
        loss.append(torch.logsumexp(logits[i,:length],0)-torch.logsumexp(logits[i,:length][inside],0))
    return torch.stack(loss).mean() if loss else v.sum()*0
