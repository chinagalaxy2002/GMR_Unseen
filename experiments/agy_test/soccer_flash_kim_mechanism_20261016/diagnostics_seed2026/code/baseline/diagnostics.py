"""Passive Train/Val diagnostics; never reads Test for model selection."""
from common import ROOT,save,rows
from pathlib import Path
import gzip,json,math,time
import numpy as np,torch

REFERENCE_COMMIT='349becb99cdfba2b23630af9126af0a532506113'

def append(path,obj):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a') as f:f.write(json.dumps(obj,ensure_ascii=False)+'\n')

def objective_gradient_relation(model,existence,localization):
    named=[(n,p) for n,p in model.named_parameters() if p.requires_grad]
    params=[p for _,p in named]
    ge=torch.autograd.grad(existence,params,retain_graph=True,allow_unused=True)
    gl=torch.autograd.grad(localization,params,retain_graph=True,allow_unused=True)
    pairs=[(n,a.detach().float(),b.detach().float()) for (n,_),a,b in zip(named,ge,gl) if a is not None and b is not None]
    if not pairs:return {'status':'no_shared_connected_parameters'}
    dot=sum(float((a*b).sum()) for _,a,b in pairs);ne=math.sqrt(sum(float(a.square().sum()) for _,a,_ in pairs));nl=math.sqrt(sum(float(b.square().sum()) for _,_,b in pairs))
    cosine=dot/max(ne*nl,1e-30)
    return {'status':'ok','cosine':cosine,'conflict':cosine<0,'existence_norm':ne,'localization_norm':nl,
            'shared_parameter_tensors':len(pairs),'parameter_names':[n for n,_,_ in pairs]}

def parameter_updates(before,model):
    groups={}
    for name,p in model.named_parameters():
        root='existence_head' if name.startswith('base.exist_head') else name.split('.')[1] if name.startswith('base.') and '.' in name[5:] else name.split('.')[0]
        old=before[name];delta=(p.detach().cpu()-old).double();item=groups.setdefault(root,{'parameters':0,'update_sq':0.,'base_sq':0.,'max_abs_update':0.,'changed':False})
        item['parameters']+=p.numel();item['update_sq']+=float(delta.square().sum());item['base_sq']+=float(old.double().square().sum());item['max_abs_update']=max(item['max_abs_update'],float(delta.abs().max()));item['changed']|=bool(torch.any(delta!=0))
    for item in groups.values():
        item['update_l2']=math.sqrt(item.pop('update_sq'));item['relative_update_l2']=item['update_l2']/max(math.sqrt(item.pop('base_sq')),1e-30)
    return groups

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

def _head_logit(state,x):
    """Exact CPU replica of Linear-ReLU-Linear used by the E0 existence head."""
    x=np.asarray(x,dtype=np.float32)
    w0,b0,w2,b2=(state[k].numpy().astype(np.float32) for k in ('0.weight','0.bias','2.weight','2.bias'))
    return float((w2@np.maximum(0,w0@x+b0)+b2).reshape(-1)[0])

def pool_diagnostics(capture,pred,gt,opt):
    """Actual E0 mean-pool attribution plus a separately labelled max counterfactual."""
    lookup={str(p['qid']):p for p in pred};out=[];source=[];ties=[]
    for truth in gt:
        qid=str(truth['qid']);record=capture.pool_records[qid]
        units=record['video_units'].numpy().astype(np.float32)
        valid=record['video_valid'].numpy().astype(bool);original=np.flatnonzero(valid);h=units[valid]
        inp=record['exist_input'].numpy().astype(np.float32);d=h.shape[1];query=inp[:-d]
        duration=float(truth.get('duration',len(valid)*opt.clip_length))
        spans=np.stack([original*opt.clip_length,np.minimum((original+1)*opt.clip_length,duration)],1)
        ground=np.asarray(truth.get('relevant_windows',[]),float).reshape(-1,2)
        gt_iou=overlaps(spans,ground);gt_slots=gt_iou.max(1)>0 if gt_iou.size else np.zeros(len(h),bool)
        owner=h.argmax(0);maximum=h[owner,np.arange(d)];tie=(h==maximum[None,:]).sum(0)
        windows=np.asarray([w[:2] for w in lookup[qid].get('pred_relevant_windows',[])[:3]],float).reshape(-1,2)
        wiou=overlaps(windows,ground);hits=wiou.max(1)>=.5 if wiou.size else np.zeros(len(windows),bool)
        computed_mean=h.mean(0);full=inp[-d:]
        mean_error=float(np.max(np.abs(computed_mean-full)))
        actual=_head_logit(capture.head_state,inp)
        row={'qid':qid,'vid':str(truth['vid']),'label':int(bool(len(ground))),
             'existence_score':float(lookup[qid]['pred_exist_score']),'existence_logit':float(lookup[qid]['pred_exist_logit_raw']),
             'native_pooling':'mean','actual_e0_mechanism':'masked_mean_pool_then_mlp',
             'counterfactual_max_status':'diagnostic_only_not_on_forward_path',
             'counterfactual_max_owner_gt_fraction':float(gt_slots[owner].mean()) if len(ground) else 0.,
             'actual_logit_from_head_hook':record['exist_output'],'actual_logit_recomputed':actual,
             'actual_logit_recompute_abs_error':abs(actual-record['exist_output']),
             'mean_pool_recompute_max_abs_error':mean_error,
             'prediction_hook_abs_error':abs(record['exist_output']-float(lookup[qid]['pred_exist_logit_raw'])),
             'false_reject_at_0.4':bool(len(ground) and lookup[qid]['pred_exist_score']<.4),
             'false_reject_at_0.5':bool(len(ground) and lookup[qid]['pred_exist_score']<.5)}
        for k in (1,2,3):
            selected=windows[:k][hits[:k]];centers=spans.mean(1)
            covered=np.asarray([any(a<=c<=b for a,b in selected) for c in centers],bool)
            contribution=h[covered].sum(0)/len(h) if covered.any() else np.zeros(d,np.float32)
            remainder=full-contribution
            denom=np.abs(contribution).sum()+np.abs(remainder).sum()
            ablated=_head_logit(capture.head_state,np.concatenate([query,remainder]))
            row.update({f'top{k}_gt_hit':bool(hits[:k].any()),
                f'top{k}_actual_mean_abs_contribution_fraction':float(np.abs(contribution).sum()/max(denom,1e-30)),
                f'top{k}_actual_mean_dominant_dimensions':int((np.abs(contribution)>np.abs(remainder)).sum()),
                f'top{k}_actual_mean_dominant_dimension_fraction':float((np.abs(contribution)>np.abs(remainder)).mean()),
                f'top{k}_actual_mean_ablation_logit_drop':float(actual-ablated),
                f'top{k}_counterfactual_max_owner_fraction':float(covered[owner].mean())})
        out.append(row);source.append(owner.astype(np.int16));ties.append(tie.astype(np.int16))
    return out,{'qid':np.asarray([r['qid'] for r in out]),'counterfactual_max_source_slot':np.asarray(source),
                'counterfactual_max_tie_count':np.asarray(ties)}

def write_pool_diagnostics(run,scope,epoch,capture,pred,gt,opt):
    records,arrays=pool_diagnostics(capture,pred,gt,opt)
    folder=Path(run)/'diagnostics'/'pool_sources'/scope/f'epoch_{epoch:04d}';folder.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(folder/'pool_provenance.npz',**arrays)
    positives=[r for r in records if r['label']]
    summary={'epoch':epoch,'scope':scope,'native_pooling':'mean','actual_mechanism':'masked_mean_pool_then_mlp',
      'counterfactual_max_status':'diagnostic_only_not_on_forward_path','per_query':records,
      'actual_logit_recompute_abs_error':score_stats([r['actual_logit_recompute_abs_error'] for r in records]),
      'topk':{str(k):{
        'hit_actual_mean_abs_contribution_fraction':score_stats([r[f'top{k}_actual_mean_abs_contribution_fraction'] for r in positives if r[f'top{k}_gt_hit']]),
        'hit_actual_mean_dominant_dimension_fraction':score_stats([r[f'top{k}_actual_mean_dominant_dimension_fraction'] for r in positives if r[f'top{k}_gt_hit']]),
        'hit_actual_mean_ablation_logit_drop':score_stats([r[f'top{k}_actual_mean_ablation_logit_drop'] for r in positives if r[f'top{k}_gt_hit']]),
        'false_reject_05_actual_mean_abs_contribution_fraction':score_stats([r[f'top{k}_actual_mean_abs_contribution_fraction'] for r in positives if r[f'top{k}_gt_hit'] and r['false_reject_at_0.5']]),
        'counterfactual_max_owner_fraction':score_stats([r[f'top{k}_counterfactual_max_owner_fraction'] for r in positives if r[f'top{k}_gt_hit']])} for k in (1,2,3)}}
    save(folder/'SUMMARY.json',summary);return summary

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

def write_epoch(run,epoch,pre,post,gt,opt,train,metrics,native,capture,keep_features=False):
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
    if keep_features:
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
    pool=write_pool_diagnostics(run,'validation',epoch,capture,pre,gt,opt)
    summary['pool_diagnostics']=str((Path(run)/'diagnostics/pool_sources/validation'/f'epoch_{epoch:04d}'/'SUMMARY.json').relative_to(ROOT))
    save(folder/'SUMMARY.json',summary);save(Path(run)/'diagnostics/LATEST.json',summary)

class FeatureCapture:
    """Read-only hooks on a fixed, Val-only absent/single/multi fixture panel."""
    def __init__(self,ids):
        self.ids=set(ids);self.records={};self.pool_records={};self.handles=[];self.current=None;self.all_current=None;self.head_state=None
    def attach(self,model):
        def before(module,args,kwargs):
            qid=str(kwargs['qid'][0]);self.all_current=qid;self.current=qid if qid in self.ids else None
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
        self.head_state={k:v.detach().cpu().clone() for k,v in base.exist_head.state_dict().items()}
        def transformer_capture(module,args,out):
            valid=(~out[1][0].bool()).detach().cpu().clone()
            self.pool_records[self.all_current]={'video_valid':valid}
        self.handles.append(base.transformer.register_forward_hook(transformer_capture))
        def post_pyramid_capture(module,args,out):
            # The native pyramid mutates its input through in-place activations;
            # existence pooling happens afterwards, so capture the post-call tensor.
            self.pool_records[self.all_current]['video_units']=args[0][0].detach().cpu().float().clone()
        self.handles.append(base.pyramid.register_forward_hook(post_pyramid_capture))
        def exist_input(module,args):
            self.pool_records[self.all_current]['exist_input']=args[0][0].detach().cpu().float().clone()
        self.handles.append(base.exist_head.register_forward_pre_hook(exist_input))
        def exist_output(module,args,out):
            self.pool_records[self.all_current]['exist_output']=float(out.detach().cpu().reshape(-1)[0])
        self.handles.append(base.exist_head.register_forward_hook(exist_output))
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
        self.handles=[];self.current=None;self.all_current=None

def fixed_val_panel(gt):
    ids=[]
    for category in [0,1,2]:
        matching=[r for r in gt if min(len(r['relevant_windows']),2)==category]
        ids.extend(r['qid'] for r in sorted(matching,key=lambda r:str(r['qid']))[:4])
    return ids
