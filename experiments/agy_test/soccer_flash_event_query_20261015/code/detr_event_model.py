"""Scheme A on DETR backbones; preserve native decoder and localization."""
from torch import nn
from event_model import EventHead

class DetrEventHead(EventHead):
    def forward(self,unused_slots):
        value=super().forward(unused_slots).squeeze(-1)
        self.context['consumed']=True
        return value

class EventModel(nn.Module):
    def __init__(self,base,variant,backbone):
        super().__init__();self.base=base;self.variant=variant;self.backbone=backbone;self.handles=[]
        if variant=='E2':
            base.exist_head=DetrEventHead(len(base.transformer.encoder.layers))
            self.handles.append(base.input_txt_proj.register_forward_hook(self._text))
            for layer in base.transformer.encoder.layers:self.handles.append(layer.register_forward_hook(self._memory))
    def _text(self,module,args,out):self.base.exist_head.context['text']=out
    def _memory(self,module,args,out):
        c=self.base.exist_head.context
        # QD performs a second rolled-text saliency forward after existence.
        if c is not None and not c['consumed']:
            offset=1 if self.backbone=='qd' else 0
            c['features'].append(out.transpose(0,1)[:,offset:offset+c['length']])
    def forward(self,**inputs):
        if self.variant=='E0':return self.base(**inputs)
        self.base.exist_head.context={'tm':inputs['src_txt_mask'].bool(),'vm':inputs['src_vid_mask'].bool(),
            'length':inputs['src_vid_mask'].shape[1],'features':[],'consumed':False}
        try:return self.base(**inputs)
        finally:self.base.exist_head.context=None
