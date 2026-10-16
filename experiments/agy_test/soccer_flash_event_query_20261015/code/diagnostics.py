"""Passive Train/Val diagnostics; never reads Test for model selection."""
from common import ROOT,save,rows
from pathlib import Path
import gzip,json,math,time
import numpy as np,torch

def ratio(num,den):return float(num/den) if den else None

def overlaps(pred,gt):
    p=np.asarray(pred,dtype=float).reshape(-1,2);g=np.asarray(gt,dtype=float).reshape(-1,2)
    inter=np.maximum(0,np.minimum(p[:,None,1],g[None,:,1])-np.maximum(p[:,None,0],g[None,:,0]))
    union=np.maximum(0,p[:,1]-p[:,0])[:,None]+np.maximum(0,g[:,1]-g[:,0])[None,:]-inter
    return inter/np.maximum(union,1e-12)

def gradient_sample(model):
    base=model.base
    groups={'existence':list(base.exist_head.parameters()),'temporal_encoder':list(base.transformer.encoder.parameters()),
            't2v_encoder':list(base.transformer.t2v_encoder.parameters()),
            'video_projection':list(base.input_vid_proj.parameters()),'text_projection':list(base.input_txt_proj.parameters()),
            'localization':list(base.class_head.parameters())+list(base.conf_head.parameters())+list(base.coord_head.parameters())}
    result={}
    with torch.no_grad():
        for name,params in groups.items():
            grads=[p.grad for p in params if p.grad is not None]
            norm=torch.stack([g.detach().float().square().sum() for g in grads]).sum().sqrt().item() if grads else 0.
            result[name]={'gradient_l2_before_clip':norm,'tensors_with_grad':len(grads),'parameter_tensors':len(params)}
    return result

def score_stats(values):
    a=np.asarray(values,dtype=float)
    if not len(a):return {'n':0}
    return {'n':len(a),'mean':float(a.mean()),'std':float(a.std()),
            'quantiles':dict(zip(['p00','p05','p25','p50','p75','p95','p100'],np.percentile(a,[0,5,25,50,75,95,100]).tolist()))}

def pair_ranking(pred,gt):
    lookup={r['qid']:r for r in pred};groups={}
    for r in gt:groups.setdefault(r['vid'],{True:[],False:[]})[bool(r['relevant_windows'])].append(lookup[r['qid']]['pred_exist_logit_raw'])
    wins=0.;pairs=0;means=[]
    for group in groups.values():
        if not group[True] or not group[False]:continue
        p=np.asarray(group[True])[:,None];n=np.asarray(group[False])[None,:]
        w=(p>n)+.5*(p==n);wins+=float(w.sum());pairs+=w.size;means.append(float(w.mean()))
    return {'videos':len(means),'pairs':int(pairs),'micro_accuracy':ratio(wins,pairs),
            'macro_accuracy':float(np.mean(means)) if means else None}

def candidate_stats(pred,gt,thresholds):
    lookup={r['qid']:r for r in pred};result={};evidence=[]
    for r in gt:
        p=lookup[r['qid']];wins=p['pred_relevant_windows']
        # Keep top-k positions fixed: degenerate windows count as non-hits.
        iou=overlaps([w[:2] for w in wins],r['relevant_windows'])
        maximum=iou.max(1) if iou.shape[1] else np.zeros(len(wins))
        evidence.append({'qid':r['qid'],'vid':r['vid'],'query':r['query'],
            'gt_windows':r['relevant_windows'],'gt_count':len(r['relevant_windows']),
            'pred_exist_score':p['pred_exist_score'],'pred_exist_logit_raw':p['pred_exist_logit_raw'],
            'windows':wins,'candidate_iou_with_gt':iou.tolist(),
            'top1_hit_iou05':bool(len(maximum) and maximum[0]>=.5)})
    positives=[e for e in evidence if e['gt_count']>0];negatives=[e for e in evidence if e['gt_count']==0]
    for k in [10,50]:
        covered=[];wrong=[];gt_recall=[]
        for e in positives:
            m=np.asarray(e['candidate_iou_with_gt'],dtype=float).reshape(-1,e['gt_count'])[:k]
            covered.append(bool((m>=.5).any()))
            wrong.append(not e['top1_hit_iou05'])
            gt_recall.append(float((m.max(0)>=.5).mean()) if len(m) else 0.)
        covered=np.asarray(covered,dtype=bool);wrong=np.asarray(wrong,dtype=bool)
        entry={'positive_count':len(positives),'covered_positive_count':int(covered.sum()),
            'coverage_iou05':ratio(int(covered.sum()),len(positives)),
            'mean_gt_recall_iou05':float(np.mean(gt_recall)) if gt_recall else None,
            'P3_wrong_given_coverage':ratio(int((covered&wrong).sum()),int(covered.sum())),
            'thresholds':{}}
        for t in thresholds:
            rejected=np.asarray([e['pred_exist_score']<t for e in positives])
            negative_accepted=sum(e['pred_exist_score']>=t for e in negatives)
            entry['thresholds'][str(t)]={
                'P4_rejection_given_coverage':ratio(int((covered&rejected).sum()),int(covered.sum())),
                'positive_false_rejection':ratio(int(rejected.sum()),len(positives)),
                'negative_false_acceptance':ratio(negative_accepted,len(negatives)),
                'N_acc':ratio(len(negatives)-negative_accepted,len(negatives))}
        result[f'top{k}']=entry
    return result,evidence

def write_epoch(run,epoch,pre,post,gt,opt,train,metrics,native,capture):
    """All values derive from the already executed official Val pass."""
    folder=Path(run)/'diagnostics'/f'epoch_{epoch:04d}';folder.mkdir(parents=True,exist_ok=True)
    pre_stats,pre_evidence=candidate_stats(pre,gt,opt.cls_thresholds)
    post_stats,post_evidence=candidate_stats(post,gt,opt.cls_thresholds)
    for name,records in [('val_pre_nms.jsonl.gz',pre_evidence),('val_post_nms.jsonl.gz',post_evidence)]:
        with gzip.open(folder/name,'wt',encoding='utf-8') as f:
            for record in records:f.write(json.dumps(record,ensure_ascii=False)+'\n')
    labels={r['qid']:bool(r['relevant_windows']) for r in gt}
    distributions={}
    for key,label in [(True,'positive'),(False,'negative')]:
        part=[p for p in pre if labels[p['qid']]==key]
        raw=np.asarray([p['pred_exist_logit_raw'] for p in part])
        prob=np.asarray([p['pred_exist_score'] for p in part])
        distributions[label]={'raw_logits':score_stats(raw),'native_probability':score_stats(prob),
            'native_zero_fraction':float((prob==0).mean()),'native_one_fraction':float((prob==1).mean())}
    saved={}
    if capture is not None:
        with gzip.open(folder/'val_fixed_features.pt.gz','wb') as f:torch.save(capture.records,f)
        saved={'path':str((folder/'val_fixed_features.pt.gz').relative_to(ROOT)),
               'qids':[r['qid'] for r in capture.records.values()],
               'precision':'detached float16 diagnostic copy; computation remains float32'}
    summary={'epoch':epoch,'updated':time.time(),'data':'official Standard Val only','train':train,
        'selection':{'metric':'MR-full-mAP','stage':'pre-NMS','value':native['brief']['MR-full-mAP']},
        'native_pre_nms_metrics':native['brief'],'official_post_nms_metrics':metrics['brief'],
        'score_distributions':distributions,'candidate_pre_nms':pre_stats,'candidate_post_nms':post_stats,
        'same_video_positive_negative_ranking':pair_ranking(pre,gt),'fixed_features':saved,
        'definitions':{'P3':'top1 IoU<.5 conditional on at least one candidate IoU>=.5',
                       'P4':'rejected conditional on at least one candidate IoU>=.5',
                       'candidate_k':'first k native ranked proposals; no GT-based reranking',
                       'rates':'fractions in [0,1]; official metrics in percent',
                       'multi_event_coverage':'at least one GT covered; mean_gt_recall also reports all-GT coverage'}}
    save(folder/'SUMMARY.json',summary);save(Path(run)/'diagnostics/LATEST.json',summary)

class FeatureCapture:
    """Read-only hooks on a fixed, Val-only absent/single/multi fixture panel."""
    def __init__(self,ids):
        self.ids=set(ids);self.records={};self.handles=[];self.current=None
    def attach(self,model):
        def before(module,args,kwargs):
            qid=kwargs['qid'][0];self.current=qid if qid in self.ids else None
            if self.current is not None:
                self.records[qid]={'qid':qid,'vid':kwargs['vid'][0],
                    'video_valid':int(kwargs['src_vid_mask'][0].sum()),'text_valid':int(kwargs['src_txt_mask'][0].sum()),'tensors':{}}
        self.handles.append(model.register_forward_pre_hook(before,with_kwargs=True))
        def hook(name,layout):
            def capture(module,args,out):
                if self.current is None:return
                r=self.records[self.current]
                if layout=='text':value=out[0,:r['text_valid']]
                elif layout=='video':value=out[:r['video_valid'],0]
                elif layout=='query':value=out[0]
                else:value=args[0][0]
                r['tensors'][name]=value.detach().to(device='cpu',dtype=torch.float16).clone()
            return capture
        base=model.base
        self.handles.append(base.input_txt_proj.register_forward_hook(hook('projected_text','text')))
        for i,layer in enumerate(base.transformer.encoder.layers):
            self.handles.append(layer.register_forward_hook(hook(f'temporal_encoder_{i}','video')))
        self.handles.append(base.exist_head.register_forward_hook(hook('legacy_pooled_input','input')))
        if model.variant=='E2':
            self.handles.append(base.exist_head.text.register_forward_hook(hook('event_query_after_text','query')))
            for i,layer in enumerate(base.exist_head.temporal):
                self.handles.append(layer.register_forward_hook(hook(f'event_query_after_temporal_{i}','query')))
    def close(self):
        for h in self.handles:h.remove()
        self.handles=[];self.current=None

def fixed_val_panel(gt):
    ids=[]
    for category in [0,1,2]:
        matching=[r for r in gt if min(len(r['relevant_windows']),2)==category]
        ids.extend(r['qid'] for r in sorted(matching,key=lambda r:str(r['qid']))[:4])
    return ids
