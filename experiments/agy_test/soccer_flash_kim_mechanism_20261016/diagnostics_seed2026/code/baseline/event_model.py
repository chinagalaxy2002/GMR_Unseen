"""Scheme A: one text read and three semantic temporal encoder reads."""
import torch
from torch import nn

class CrossBlock(nn.Module):
    def __init__(self):
        super().__init__()
        self.attn=nn.MultiheadAttention(256,8,dropout=.1,batch_first=True)
        self.ff=nn.Sequential(nn.Linear(256,512),nn.ReLU(),nn.Dropout(.1),nn.Linear(512,256))
        self.norm1=nn.LayerNorm(256);self.norm2=nn.LayerNorm(256);self.drop=nn.Dropout(.1)
    def forward(self,q,memory,valid):
        x,_=self.attn(q,memory,memory,key_padding_mask=~valid,need_weights=False)
        q=self.norm1(q+self.drop(x));return self.norm2(q+self.drop(self.ff(q)))

class EventHead(nn.Module):
    def __init__(self,depth):
        super().__init__()
        self.query=nn.Parameter(torch.randn(1,1,256)*.02)
        self.text=CrossBlock();self.temporal=nn.ModuleList([CrossBlock() for _ in range(depth)])
        self.head=nn.Sequential(nn.Linear(256,256),nn.ReLU(),nn.Linear(256,1))
        self.context=None
    def forward(self,unused_pooled_features):
        c=self.context;assert c is not None and len(c['features'])==len(self.temporal)
        q=self.text(self.query.expand(c['text'].shape[0],-1,-1),c['text'],c['tm'])
        for block,memory in zip(self.temporal,c['features']):q=block(q,memory,c['vm'])
        return self.head(q[:,0])

class EventModel(nn.Module):
    def __init__(self,base,variant):
        super().__init__();assert variant in ('E0','E2')
        self.base=base;self.variant=variant;self.handles=[]
        if variant=='E2':
            base.exist_head=EventHead(len(base.transformer.encoder.layers))
            self.handles.append(base.input_txt_proj.register_forward_hook(self._text))
            for layer in base.transformer.encoder.layers:self.handles.append(layer.register_forward_hook(self._memory))
    def _text(self,module,args,out):self.base.exist_head.context['text']=out
    def _memory(self,module,args,out):self.base.exist_head.context['features'].append(out.transpose(0,1))
    def forward(self,**inputs):
        if self.variant=='E0':return self.base(**inputs)
        self.base.exist_head.context={'tm':inputs['src_txt_mask'].bool(),'vm':inputs['src_vid_mask'].bool(),'features':[]}
        try:return self.base(**inputs)
        finally:self.base.exist_head.context=None
