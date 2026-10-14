"""Read-only diagnostics: never replace a training loss or model output.

Heavy tensor diagnostics run on sampled training batches and complete fixed probes.
Every validation query retains score/geometry/difficulty diagnostics. Unseen only
enters after the runner writes FROZEN_CALIBRATION.json.
"""
from pathlib import Path
from functools import lru_cache
import zipfile
import numpy as np
import torch
import torch.nn.functional as F
from mechanism_monitor import append_json, save_json
from response_monitor import geometry_record


@lru_cache(maxsize=200000)
def feature_shape(path, key):
    with zipfile.ZipFile(path) as archive, archive.open(key + '.npy') as stream:
        version = np.lib.format.read_magic(stream)
        shape, _, _ = np.lib.format._read_array_header(stream, version)
    return shape


def annotate_lengths(dataset, paths, opt, registry, module):
    clip, sf = registry.video_dirs(paths['dataset'])
    for row in dataset.data:
        stem = module.video_id_to_feature_stem(row['vid']) if hasattr(module, 'video_id_to_feature_stem') else dataset._vid_to_stem(row['vid'])
        lengths = [feature_shape(str(folder / (stem + '.npz')), 'features')[0] for folder in (clip, sf)]
        text = feature_shape(str(paths['text'] / f"qid{row['qid']}.npz"), 'last_hidden_state')[0]
        capv = opt.max_v_l if opt.max_v_l > 0 else 100000000
        capt = opt.max_q_l if opt.max_q_l > 0 else 100
        effective = min(min(lengths), capv)
        gt = row['relevant_windows']
        row['_diagnostic'] = dict(raw_video_lengths=lengths, raw_text_length=text,
            effective_video_length=effective, text_truncated=text > capt,
            video_truncated=min(lengths) > capv, component_truncated=max(lengths) > capv,
            feature_length_mismatch=len(set(lengths)) > 1, gt_count=len(gt),
            gt_truncated=len(gt) > opt.max_windows, context_seconds=effective * opt.clip_length,
            gt_outside_context=sum(b > effective * opt.clip_length for a,b in gt),
            gt_duration_ratio=sum(max(0,b-a) for a,b in gt) / max(float(row['duration']), 1e-9))


def auc_pairs(pos, neg):
    if not len(pos) or not len(neg):
        return None
    neg = np.sort(neg)
    lo, hi = np.searchsorted(neg, pos, 'left'), np.searchsorted(neg, pos, 'right')
    return dict(auroc=float(np.mean((lo + hi) * .5 / len(neg))),
        strict_error_fraction=float(np.mean((len(neg)-hi) / len(neg))),
        tie_fraction=float(np.mean((hi-lo) / len(neg))), pairs=int(len(pos)*len(neg)))


def score_report(rows):
    result = dict(count=len(rows), subsets={}, same_video={})
    if not rows:
        return result
    p = np.array([r['partition'] for r in rows]); y = np.array([r['label'] for r in rows])
    for prefix in ('S','U'):
        mask = np.char.startswith(p,prefix)
        if not mask.any():
            continue
        rr = [r for r,m in zip(rows,mask) if m]
        result['subsets'][prefix] = {}
        for key in ('logit','raw_probability','score'):
            s = np.array([r[key] for r in rows]); pos,neg=s[mask & (y==1)],s[mask & (y==0)]
            result['subsets'][prefix][key] = dict(ranking=auc_pairs(pos,neg),
                positive_quantiles=np.quantile(pos,[0,.05,.25,.5,.75,.95,1]).tolist() if len(pos) else None,
                negative_quantiles=np.quantile(neg,[0,.05,.25,.5,.75,.95,1]).tolist() if len(neg) else None,
                unique_scores=int(len(np.unique(s[mask]))))
        pairs=[]; values=[]
        by_video={}
        for r in rr:by_video.setdefault(r['vid'],[]).append(r)
        for vid,group in sorted(by_video.items()):
            a=auc_pairs(np.array([r['logit'] for r in group if r['label']]),np.array([r['logit'] for r in group if not r['label']]))
            if a: values.append(a['auroc']); pairs.append(a['pairs'])
        result['same_video'][prefix]=dict(videos_with_both_classes=len(values), macro_auroc=float(np.mean(values)) if values else None,
            pair_weighted_auroc=float(np.average(values,weights=pairs)) if values else None)
        positive=sorted([r for r in rr if r['label']],key=lambda r:r['logit'])[:10]
        negative=sorted([r for r in rr if not r['label']],key=lambda r:-r['logit'])[:10]
        worst=sorted([(a['logit']-b['logit'],a,b) for a in positive for b in negative],key=lambda x:x[0])[:20]
        result['subsets'][prefix]['worst_pairs']=[dict(margin=float(d),positive_qid=a['qid'],negative_qid=b['qid'],same_video=a['vid']==b['vid']) for d,a,b in worst]
        result['subsets'][prefix]['strata']={}
        result['subsets'][prefix]['positive_joint']={str((loc,accept)):sum(r['label']==1 and r.get('localization_success')==loc and (r['raw_probability']>=.5)==accept for r in rr) for loc in (False,True) for accept in (False,True)}
        for key in ('duration','raw_text_length','effective_video_length','gt_count','gt_duration_ratio'):
            values=np.array([r.get(key,r.get('difficulty',{}).get(key,np.nan)) for r in rr],dtype=float)
            finite=np.isfinite(values)
            if not finite.any():continue
            edges=np.unique(np.quantile(values[finite],[0,.25,.5,.75,1]))
            result['subsets'][prefix]['strata'][key]=[]
            for j in range(len(edges)-1):
                selected=finite & (values>=edges[j]) & ((values<=edges[j+1]) if j==len(edges)-2 else (values<edges[j+1]))
                pp=np.array([r['logit'] for r,m in zip(rr,selected) if m and r['label']]);nn=np.array([r['logit'] for r,m in zip(rr,selected) if m and not r['label']])
                result['subsets'][prefix]['strata'][key].append(dict(low=float(edges[j]),high=float(edges[j+1]),n=int(selected.sum()),ranking=auc_pairs(pp,nn)))
        for key in ('text_truncated','video_truncated','feature_length_mismatch','gt_truncated'):
            result['subsets'][prefix]['strata'][key]={str(flag):dict(n=sum(r.get('difficulty',{}).get(key)==flag for r in rr),
                ranking=auc_pairs(np.array([r['logit'] for r in rr if r['label'] and r.get('difficulty',{}).get(key)==flag]),
                                  np.array([r['logit'] for r in rr if not r['label'] and r.get('difficulty',{}).get(key)==flag]))) for flag in (False,True)}
    cells={}
    for a,b in (('S+','S-'),('U+','S-'),('S+','U-'),('U+','U-')):
        values=auc_pairs(np.array([r['logit'] for r in rows if r['partition']==a]),np.array([r['logit'] for r in rows if r['partition']==b]))
        cells[a+'/'+b]=values['auroc'] if values else None
    result['cross_partition_auroc_logit']=cells
    if all(v is not None for v in cells.values()):
        ss,us,su,uu=[cells[k] for k in ('S+/S-','U+/S-','S+/U-','U+/U-')]
        result['gap_decomposition_pp']=dict(positive_shift=50*((ss-us)+(su-uu)),negative_shift=50*((ss-su)+(us-uu)),gap=100*(ss-uu),interpretation='symmetric descriptive ranking decomposition; not causal')
    return result


class AUROCMechanismMonitor:
    def __init__(self, model, output, backbone, every=50):
        self.model,self.output,self.backbone,self.every=model,Path(output)/'auroc_mechanisms',backbone,every
        self.output.mkdir(parents=True)
        self.hs=None; self.parent=None; self.head_input=None; self.context=None
        self.handles=[model.exist_head.register_forward_pre_hook(self.capture_head)]
        if backbone != 'flash': self.handles.append(model.transformer.register_forward_hook(self.capture_hs))
        else:
            self.handles.append(model.pyramid.register_forward_pre_hook(self.capture_video))
        save_json(self.output/'METADATA.json',dict(version=2,training_interval=every,
            gradient='weighted native losses on shared representations; autograd.grad without modifying .grad',
            flash='temporal units and pyramid candidates; DETR query/Hungarian/decoder-SA not applicable',
            pooling_loo='head-only leave-one-unit-out; diagnostic perturbation, not a training loss',
            score_threshold='.5 probability descriptive only; final threshold Seen validation',
            records='sampled training; full fixed Seen probe and full Seen validation; frozen final test'))

    def capture_head(self,module,inputs):
        if not getattr(self,"diagnostic_head",False): self.head_input=inputs[0]
    def capture_hs(self,module,inputs,outputs):
        if self.hs is None:
            self.parent=outputs[0]; self.hs=outputs[0][-1]
    def capture_video(self,module,inputs):
        if self.hs is None: self.hs=inputs[0]
    def begin(self,phase,epoch,step=0,batch=0):
        self.phase,self.epoch,self.step,self.batch=phase,epoch,step,batch
        self.hs=None; self.parent=None; self.head_input=None
        self.enabled=phase!='train' or (step-1)%self.every==0 or batch==1

    def gradients(self,losses,criterion,metadata):
        if not self.enabled or self.hs is None: return
        groups={}
        for name,keys in dict(localization=('loss_span','loss_giou','loss_reg','loss_coord'),
                existence=('loss_exist',),classification=('loss_label','loss_cls','loss_conf'),
                other=()).items():
            terms=[v*criterion.weight_dict[k] for k,v in losses.items() if k in criterion.weight_dict and any(k.startswith(t) for t in keys)]
            if terms: groups[name]=sum(terms)
        ancestor=self.parent if self.parent is not None else self.hs
        gs={k:torch.autograd.grad(v,ancestor,retain_graph=True,allow_unused=True)[0] if v.requires_grad else None for k,v in groups.items()}
        if self.parent is not None: gs={k:(v[-1] if v is not None else None) for k,v in gs.items()}
        for a in gs:
            for b in gs:
                if a>=b: continue
                for part in ('all','S+','S-'):
                    mask=torch.tensor([part=='all' or r['partition']==part for r in metadata],device=self.hs.device)
                    if not mask.any(): continue
                    ga,gb=gs[a],gs[b]; cosine=None;na=nb=None
                    if ga is not None and gb is not None:
                        x,z=ga[mask].detach().double(),gb[mask].detach().double();na=float(x.norm());nb=float(z.norm())
                        if na and nb: cosine=float((x*z).sum()/(na*nb))
                    append_json(self.output/'shared_gradients.jsonl',dict(epoch=self.epoch,step=self.step,subset=part,pair=a+'/'+b,
                        cosine=cosine,conflict=cosine<0 if cosine is not None else None,norm_a=na,norm_b=nb))
        logits=self._logits
        for part,label in (('S+',1),('S-',0)):
            mask=torch.tensor([r['partition']==part for r in metadata],device=logits.device)
            if mask.any():
                contribution=F.binary_cross_entropy_with_logits(logits[mask],torch.full_like(logits[mask],label),reduction='sum')/len(metadata)
                append_json(self.output/'existence_loss_contributions.jsonl',dict(epoch=self.epoch,step=self.step,subset=part,
                    n=int(mask.sum()),weighted_contribution=float(contribution.detach())*criterion.weight_dict.get('loss_exist',1)))

    def optimization(self,losses,criterion,norm,clip,lr,metadata):
        append_json(self.output/'optimization.jsonl',dict(epoch=self.epoch,step=self.step,
            counts={p:sum(r['partition']==p for r in metadata) for p in ('S+','S-')},
            weighted_losses={k:float(v.detach() if torch.is_tensor(v) else v)*criterion.weight_dict[k] for k,v in losses.items() if k in criterion.weight_dict},
            preclip_global_norm=float(norm),clip_threshold=clip,clip_coefficient=min(1.,clip/(float(norm)+1e-6)) if clip>0 else 1.,lr=lr))

    @torch.no_grad()
    def observe(self,outputs,metadata,inputs,indices=None,geometry=None,targets=None):
        self._logits=outputs['pred_exist_logits']
        if not self.enabled: return []
        logits=self._logits.detach().reshape(-1); probs=logits.sigmoid(); hs=self.hs.detach() if self.hs is not None else None
        mask=inputs['src_vid_mask'].bool() if self.backbone=='flash' else None
        rows=[]
        for i,meta in enumerate(metadata):
            row=dict(epoch=self.epoch,step=self.step,batch=self.batch,qid=str(meta['qid']),vid=str(meta['vid']),
                partition=meta['partition'],label=int(meta['exist_label']),duration=float(meta['duration']),
                difficulty=meta.get('_diagnostic',{}),valid_video_tokens=int(inputs['src_vid_mask'][i].sum()),
                valid_text_tokens=int(inputs['src_txt_mask'][i].sum()),logit=float(logits[i]),raw_probability=float(probs[i]),
                score=float(np.round(float(logits[i]),6)) if self.backbone=='flash' else float(np.round(float(probs[i]),4)),
                probability_saturated=bool(probs[i]==0 or probs[i]==1))
            if geometry is not None:
                g=geometry[i]; fg=np.asarray(g['slot_scores']); ov=np.asarray(g['iou_with_gt']); correct=ov>=.5 if row['label'] else np.zeros(len(fg),bool)
            elif self.backbone!='flash':
                fg=outputs['pred_logits'][i].softmax(-1)[:,0].detach().cpu().numpy();correct=None;ov=None
                if targets is not None:
                    from response_monitor import overlap_matrix
                    cxw=outputs['pred_spans'][i].detach().cpu().numpy(); xx=np.stack((cxw[:,0]-.5*cxw[:,1],cxw[:,0]+.5*cxw[:,1]),-1).clip(0,1)
                    gt=targets['span_labels'][i]['spans'].detach().cpu().numpy(); gx=np.stack((gt[:,0]-.5*gt[:,1],gt[:,0]+.5*gt[:,1]),-1)
                    ov=overlap_matrix(xx,gx).max(1) if len(gt) else np.zeros(len(fg));correct=ov>=.5 if len(gt) else np.zeros(len(fg),bool)
            else:
                fg=outputs.get('out_class',torch.empty(0,device=logits.device))[i].sigmoid().reshape(-1).cpu().numpy() if 'out_class' in outputs else np.array([]);correct=None;ov=None
            row['foreground_scores']=fg.tolist(); row['active_units_ge_0_5']=int((fg>=.5).sum())
            if correct is not None:
                row.update(correct_units=int(correct.sum()) if row['label'] else None,
                    correct_active_units=int((correct & (fg>=.5)).sum()) if row['label'] else None,
                    best_gt_iou=float(ov.max()) if row['label'] and len(ov) else None,
                    best_correct_rank=int(np.where(correct[np.argsort(-fg,kind='stable')])[0][0]+1) if correct.any() else None,
                    correct_incorrect_margin=float(fg[correct].max()-fg[~correct].max()) if correct.any() and (~correct).any() else None,
                    oracle_localization_success=bool(correct.any()) if row['label'] else None,
                    localization_success=bool(correct[int(np.argmax(fg))]) if row['label'] and len(fg) else None,
                    top1_iou=float(ov[int(np.argmax(fg))]) if row['label'] and len(fg) else None)
            matched=np.zeros(len(fg),bool)
            if indices is not None:
                matched[indices[i][0].detach().cpu().numpy()]=True
                row.update(matched_foreground=fg[matched].tolist(),unmatched_foreground=fg[~matched].tolist())
            if hs is not None:
                h=hs[i]; valid=mask[i] if mask is not None else torch.ones(len(h),device=h.device,dtype=torch.bool)
                h=h[valid]; n=len(h)
                pool=getattr(self.model,'exist_pool','max')
                if pool=='max':
                    values,owners=h.max(0);counts=torch.bincount(owners,minlength=n);row['pool_owner_counts']=counts.cpu().tolist()
                    if self.backbone!='flash':
                        row['pool_matched_fraction']=float(counts[matched].sum())/h.shape[-1] if indices is not None else None
                        row['pool_correct_fraction']=float(counts[correct].sum())/h.shape[-1] if correct is not None and row['label'] else None
                    row['pool_tied_dimensions']=int((h==values).sum(0).gt(1).sum())
                else: row['pool_owner_counts']=None
                if n>1:
                    self.diagnostic_head=True
                    if self.backbone=='flash':
                        if pool=='mean': pooled=(h.sum(0,keepdim=True)-h)/(n-1)
                        else:
                            top=h.topk(2,dim=0).values
                            pooled=torch.where(h==top[0],top[1],top[0])
                        query=self.head_input[i,:h.shape[-1]].detach().expand(n,-1)
                        values=self.model.exist_head(torch.cat((query,pooled),-1)).reshape(-1)
                    else:
                        values=torch.stack([self.model.exist_head(torch.cat((h[:j],h[j+1:]),0).unsqueeze(0)).reshape(()) for j in range(n)])
                    self.diagnostic_head=False
                    row['leave_one_unit_out_logit_drop']=(logits[i]-values).cpu().tolist()
                    row['leave_one_unit_out_probability_drop']=(probs[i]-values.sigmoid()).cpu().tolist()
                if self.phase=='probe' or self.batch==1:
                    z=F.normalize(h,dim=-1);similarity=z@z.T
                    row['mean_off_diagonal_unit_cosine']=float((similarity.sum()-similarity.diagonal().sum())/max(n*(n-1),1))
                    spectrum=torch.linalg.svdvals((h-h.mean(0)).float()).square();prob=spectrum/spectrum.sum().clamp(min=1e-12)
                    row['centered_effective_rank']=float((-prob*prob.clamp(min=1e-12).log()).sum().exp()) if spectrum.sum()>0 else 0.
                head_input=self.head_input[i].detach()
                pooled=head_input.max(0).values if self.backbone!='flash' and getattr(self.model,'exist_pool','max')=='max' else (head_input.mean(0) if self.backbone!='flash' else head_input)
                first=self.model.exist_head[0] if self.backbone=='flash' else self.model.exist_head.layers[0]
                pre=first(pooled)
                row['existence_head_input_l2']=float(pooled.norm())
                row['existence_head_relu_active_fraction']=float((pre>0).float().mean())
                row['unit_type']='temporal_video_unit' if self.backbone=='flash' else 'decoder_query'
                from pool_provenance import record as record_pool_provenance
                row.update(record_pool_provenance(self,h,valid,meta,logits[i],self.head_input[i],fg,ov,indices,i,outputs,targets,int(inputs['src_vid_mask'][i].sum())))
            rows.append(row)
            append_json(self.output/f'{self.phase}_queries.jsonl',row)
        return rows

    def finish(self,phase,epoch,rows):
        if rows:
            errors=[]
            score_groups={(prefix,label):np.sort(np.array([r['logit'] for r in rows if r['partition'].startswith(prefix) and r['label']==label])) for prefix in ('S','U') for label in (0,1)}
            for row in rows:
                opponents=score_groups[(row['partition'][0],1-row['label'])]
                lo,hi=np.searchsorted(opponents,row['logit'],'left'),np.searchsorted(opponents,row['logit'],'right')
                errors.append((len(opponents)-hi+.5*(hi-lo))/len(opponents) if row['label'] and len(opponents) else ((lo+.5*(hi-lo))/len(opponents) if len(opponents) else np.nan))
            np.savez_compressed(self.output/f'{phase}_epoch_{epoch:04d}_ranking.npz',misranking_fractions=np.array(errors),qids=np.array([r['qid'] for r in rows]),vids=np.array([r['vid'] for r in rows]),partitions=np.array([r['partition'] for r in rows]),labels=np.array([r['label'] for r in rows]),logits=np.array([r['logit'] for r in rows]),raw_probabilities=np.array([r['raw_probability'] for r in rows]),native_scores=np.array([r['score'] for r in rows]))
        save_json(self.output/f'{phase}_epoch_{epoch:04d}_scores.json',score_report(rows))
    def close(self):
        for handle in self.handles: handle.remove()

class ObjectiveSplitMonitor:
    """Reuse actual native final/aux matcher results; never invoke a new match."""
    def __init__(self,criterion,output):
        self.criterion=criterion;self.output=Path(output)/'auroc_mechanisms';self.matches=[]
        self.handle=criterion.matcher.register_forward_hook(self.capture)
    def capture(self,module,args,result): self.matches.append((args[0],args[1],result))
    def begin(self): self.matches=[]
    def observe(self,metadata,epoch,step,losses):
        c=self.criterion;parts={};n=len(metadata)
        for part in ('S+','S-'):
            ids=[i for i,r in enumerate(metadata) if r['partition']==part]
            if not ids:continue
            terms={}
            for level,(out,targets,indices) in enumerate(self.matches):
                sub={k:v[ids] for k,v in out.items() if torch.is_tensor(v) and v.ndim and v.shape[0]==n}
                target={'span_labels':[targets['span_labels'][i] for i in ids], 'exist_label':targets['exist_label'][ids]}
                match=[indices[i] for i in ids]
                # Native span means use all matched GTs; class/BCE means use B*Q/B.
                all_gt=sum(len(x[0]) for x in indices);group_gt=sum(len(x[0]) for x in match)
                with torch.no_grad():
                    if group_gt:
                        raw=c.loss_spans(sub,target,match)
                        for key,value in raw.items():
                            name=key if level==0 else f'{key}_{level-1}'
                            if name in c.weight_dict:terms[name]=float(value)*c.weight_dict[name]*group_gt/max(all_gt,1)
                    raw=c.loss_labels(sub,target,match,log=False)
                    for key,value in raw.items():
                        name=key if level==0 else f'{key}_{level-1}'
                        if name in c.weight_dict:terms[name]=float(value)*c.weight_dict[name]*len(ids)/n
                    if level==0 and 'pred_exist_logits' in sub:
                        val=F.binary_cross_entropy_with_logits(sub['pred_exist_logits'].reshape(-1),target['exist_label'].float().reshape(-1))
                        terms['loss_exist']=float(val)*c.weight_dict.get('loss_exist',1)*len(ids)/n
            parts[part]=dict(n=len(ids),weighted_contributions=terms)
        append_json(self.output/'objective_split.jsonl',dict(epoch=epoch,step=step,subsets=parts,
            note='S+/S- native localization, foreground classification and existence; actual final/aux matches; saliency excluded from decomposition'))
    def close(self):self.handle.remove()


class FlashTemporalMonitor:
    def __init__(self,model,criterion,folder,every=50):
        self.model,self.criterion,self.folder,self.every=model,criterion,Path(folder)/'flash_temporal',every
        self.folder.mkdir(parents=True);self.enabled=False;self.arrays={};self.targets=[]
        self.handles=[model.pyramid.register_forward_hook(self.capture_pyramid),model.transformer.register_forward_hook(self.capture_transformer)]
        bundle=criterion.loss;self.original=bundle.get_target
        def targets(data):
            result=self.original(data)
            if self.enabled:
                self.targets.append(dict(qids=[str(r['qid']) for r in data['label']],
                    foreground_target=result[0].detach().cpu().numpy(),regression_target=result[1].detach().cpu().numpy()))
            return result
        bundle.get_target=targets
        save_json(self.folder/'METADATA.json',dict(unit='native temporal pyramid points, not DETR decoder slots',
            supervision='actual BundleLoss center/range target outputs on S+ only; S- localization not supervised',
            attention='native transformer returned cross attention',raw='sampled training first batch / fixed probe all batches'))
    def begin(self,phase,epoch,step,batch):
        self.phase,self.epoch,self.step,self.batch=phase,epoch,step,batch
        self.enabled=phase=='probe' or (phase=='train' and (batch==1 or (step-1)%self.every==0))
        self.arrays={};self.targets=[]
    def capture_pyramid(self,module,args,out):
        if self.enabled and 'video_emb' not in self.arrays:
            self.arrays.update(video_emb=args[0].detach().cpu().numpy(),video_mask=args[1].detach().cpu().numpy())
            for i,h in enumerate(out[0]):self.arrays[f'pyramid_{i}']=h.detach().cpu().numpy()
    def capture_transformer(self,module,args,out):
        if self.enabled and 'cross_attention' not in self.arrays:
            self.arrays['cross_attention']=out[3].detach().cpu().numpy()
    def observe(self,outputs,metadata,geometry):
        if not self.enabled:return
        for key in ('point','out_class','out_coord','pred_spans'):
            if key in outputs:self.arrays[key]=outputs[key].detach().cpu().numpy()
        for i,t in enumerate(self.targets):
            for k,v in t.items():self.arrays[f'target_{i}_{k}']=np.array(v)
        records=[]
        for meta,g in zip(metadata,geometry):
            h=dict(qid=str(meta['qid']),vid=str(meta['vid']),partition=meta['partition'],
                existence_probability=float(outputs['pred_exist_logits'][len(records)].detach().sigmoid()))
            h.update(geometry_record(g['slot_spans_sec'],g['slot_scores'],meta['relevant_windows']))
            records.append(h)
        append_json(self.folder/f'{self.phase}.jsonl',dict(epoch=self.epoch,step=self.step,batch=self.batch,records=records,
            gt_positive_points=[dict(qids=t['qids'],counts=t['foreground_target'].sum(1).tolist()) for t in self.targets]))
        if self.phase=='probe' or self.batch==1:
            np.savez_compressed(self.folder/f'{self.phase}_epoch_{self.epoch:04d}_batch_{self.batch:05d}.npz',qids=np.array([str(r['qid']) for r in metadata]),**self.arrays)
    def close(self):
        for h in self.handles:h.remove()
        self.criterion.loss.get_target=self.original


def final_ranking_bootstrap(output,diagnostics,frozen):
    """Four cross-partition AUROCs and exact symmetric gap split, shared video draws."""
    output=Path(output);boot=np.load(output/'bootstrap.npz');videos=boot['videos'];weights=boot['cluster_counts']
    vi=np.searchsorted(videos,frozen['vids']);parts=frozen['partitions'];draws={}
    for a,b in (('S+','S-'),('U+','S-'),('S+','U-'),('U+','U-')):
        mask=(parts==a)|(parts==b)
        values=[]
        for start in range(0,len(weights),32):
            w=weights[start:start+32][:,vi]
            values.extend(diagnostics.diag.auc_draws(frozen['labels'],frozen['scores'],mask,w))
        point=diagnostics.diag.auc_draws(frozen['labels'],frozen['scores'],mask,np.ones((1,len(parts))))[0]
        draws[a+'/'+b]=np.r_[point,values]
    ss,us,su,uu=[draws[k] for k in ('S+/S-','U+/S-','S+/U-','U+/U-')]
    draws.update(positive_shift=.5*((ss-us)+(su-uu)),negative_shift=.5*((ss-su)+(us-uu)),gap=ss-uu)
    metrics={}
    for k,v in draws.items():
        finite=v[1:][np.isfinite(v[1:])]
        metrics[k]=dict(point=float(v[0]) if np.isfinite(v[0]) else None,ci95=np.percentile(finite,[2.5,97.5]).tolist() if len(finite) else None,valid_draws=len(finite))
    save_json(output/'monitor/auroc_mechanisms/final_gap_decomposition.json',dict(metrics=metrics,
        units='AUROC percentage points / gap contributions pp',score='native frozen evaluation score',interpretation='descriptive symmetric ranking decomposition; not causal',bootstrap='shared video-cluster draws from bootstrap.npz'))
    np.savez_compressed(output/'monitor/auroc_mechanisms/final_gap_decomposition_bootstrap.npz',**draws)
