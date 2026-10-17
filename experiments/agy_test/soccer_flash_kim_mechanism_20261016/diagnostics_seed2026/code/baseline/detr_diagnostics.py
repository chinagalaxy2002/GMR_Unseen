"""DETR-specific passive capture; shared scalar diagnostics stay unchanged."""
import torch

def gradient_sample(model):
    b=model.base
    groups={'existence':list(b.exist_head.parameters()),'temporal_encoder':list(b.transformer.encoder.parameters()),
        'decoder':list(b.transformer.decoder.parameters()),'video_projection':list(b.input_vid_proj.parameters()),
        'text_projection':list(b.input_txt_proj.parameters()),
        'localization':list(b.class_embed.parameters())+list(b.span_embed.parameters())}
    if hasattr(b.transformer,'t2v_encoder'):groups['t2v_encoder']=list(b.transformer.t2v_encoder.parameters())
    result={}
    with torch.no_grad():
        for name,params in groups.items():
            grads=[p.grad for p in params if p.grad is not None]
            norm=torch.stack([g.detach().float().square().sum() for g in grads]).sum().sqrt().item() if grads else 0.
            result[name]={'gradient_l2_before_clip':norm,'tensors_with_grad':len(grads),'parameter_tensors':len(params)}
    return result

class FeatureCapture:
    def __init__(self,ids,backbone):
        self.ids=set(ids);self.backbone=backbone;self.records={};self.handles=[];self.current={};self.finished=False
    def attach(self,model):
        def before(module,args,kwargs):
            self.finished=False;self.current={}
            # DETR forward does not receive qids; predict sets batch metadata.
            for i,meta in enumerate(self.batch_meta):
                qid=meta['qid']
                if qid not in self.ids:continue
                self.current[i]=qid
                self.records[qid]={'qid':qid,'vid':meta['vid'],'video_valid':int(kwargs['src_vid_mask'][i].sum()),
                    'text_valid':int(kwargs['src_txt_mask'][i].sum()),'tensors':{}}
        self.handles.append(model.register_forward_pre_hook(before,with_kwargs=True))
        def hook(name,layout):
            def capture(module,args,out):
                if self.finished:return
                for i,qid in self.current.items():
                    r=self.records[qid]
                    if layout=='text':v=out[i,:r['text_valid']]
                    elif layout=='video':
                        offset=1 if self.backbone=='qd' else 0;v=out[offset:offset+r['video_valid'],i]
                    elif layout=='query':v=out[i]
                    else:v=args[0][i]
                    r['tensors'][name]=v.detach().to(device='cpu',dtype=torch.float16).clone()
                if layout=='slots':self.finished=True
            return capture
        b=model.base
        self.handles.append(b.input_txt_proj.register_forward_hook(hook('projected_text','text')))
        for i,layer in enumerate(b.transformer.encoder.layers):
            self.handles.append(layer.register_forward_hook(hook(f'temporal_encoder_{i}','video')))
        self.handles.append(b.exist_head.register_forward_hook(hook('decoder_slots_input','slots')))
        if model.variant=='E2':
            self.handles.append(b.exist_head.text.register_forward_hook(hook('event_query_after_text','query')))
            for i,layer in enumerate(b.exist_head.temporal):
                self.handles.append(layer.register_forward_hook(hook(f'event_query_after_temporal_{i}','query')))
    def close(self):
        for h in self.handles:h.remove()
        self.handles=[];self.current={}
