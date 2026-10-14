"""Additional pooling provenance; preserves all existing legacy diagnostic records."""
import numpy as np
import torch
from pool_algebra import provenance, head_measure


@torch.no_grad()
def record(monitor,h,valid,meta,logit,head_input,foreground,overlap,indices,index,outputs=None,targets=None,context_length=None):
    # CPU copies and plain algebra preserve native output, gradient and RNG streams.
    unit=h.detach().cpu()
    root=monitor.output/'pool_sources'/monitor.phase/f'epoch_{monitor.epoch:04d}'
    root.mkdir(parents=True,exist_ok=True)
    key=f'batch_{monitor.batch:05d}_query_{index:03d}'
    data=dict(qid=np.array(str(meta['qid'])),vid=np.array(str(meta['vid'])),partition=np.array(meta['partition']),
        epoch=np.array(monitor.epoch),native_epoch_index=np.array(monitor.epoch-1),
        native_logit=np.array(float(logit)),foreground=np.asarray(foreground),
        gt_iou=np.asarray(overlap) if overlap is not None and meta['exist_label'] else np.full(len(foreground),np.nan))
    head=monitor.model.exist_head
    # Construct CPU head by copying module so all new arithmetic stays detached.
    from types import SimpleNamespace
    class Linear:
        def __init__(self,layer):
            self.weight=layer.weight.detach().cpu()
            self.bias=layer.bias.detach().cpu()
        def __call__(self,value):
            return torch.nn.functional.linear(value,self.weight,self.bias)
    cpu_head=([Linear(head[0]),None,Linear(head[2])] if monitor.backbone=='flash' else
        SimpleNamespace(layers=[Linear(layer) for layer in head.layers]))
    if monitor.backbone!='flash':
        data.update(provenance(unit))
        matched=np.full(len(unit),-1,np.int32)
        if indices is not None:
            a,b=indices[index]
            matched[a.cpu().numpy()]=b.cpu().numpy()
        data['matched_gt_id']=matched
        cxw=outputs['pred_spans'][index].detach().cpu().numpy()
        data['slot_span_native_cxw']=cxw
        data['slot_span_seconds']=np.stack((cxw[:,0]-.5*cxw[:,1],cxw[:,0]+.5*cxw[:,1]),-1)*float(meta['duration'])
        data['gt_windows_seconds']=np.asarray(meta.get('relevant_windows',[]),dtype=np.float32).reshape(-1,2)
        if targets is not None and 'span_labels' in targets:
            data['matching_target_spans_native_cxw']=targets['span_labels'][index]['spans'].detach().cpu().numpy()
        data['matched_gt_status']=np.array('native_matcher' if indices is not None else 'not_applicable_negative_no_gt')
        if indices is None and meta['exist_label']:
            package='moment_detr_gmr' if monitor.backbone=='moment' else 'qd_detr_gmr'
            import importlib
            Matcher=importlib.import_module('models.'+package+'.matcher').HungarianMatcher
            cost=getattr(monitor,'provenance_matcher_cost',dict(cost_class=1,cost_span=1,cost_giou=1))
            matcher=Matcher(**cost)
            gt=torch.tensor(meta['relevant_windows'],dtype=torch.float32).reshape(-1,2)
            context_seconds=float(context_length)*getattr(monitor,'provenance_clip_length',1.)
            gt=gt/max(context_seconds,1e-9)
            gt_cxw=torch.stack(((gt[:,0]+gt[:,1])/2,gt[:,1]-gt[:,0]),-1)
            out={k:outputs[k][index:index+1].detach().cpu() for k in ('pred_spans','pred_logits')}
            match=matcher(out,{'span_labels':[{'spans':gt_cxw}]})[0]
            matched[match[0].numpy()]=match[1].numpy()
            data['matched_gt_id']=matched
            data['matching_target_spans_native_cxw']=gt_cxw.numpy()
            data['matched_gt_status']=np.array('offline_recomputed_full_annotation_gt_not_native_criterion')
        data['slot_span_normalization_context_seconds']=np.array(float(context_length)*getattr(monitor,'provenance_clip_length',1.))
        data['slot_span_seconds_training_context']=np.stack((cxw[:,0]-.5*cxw[:,1],cxw[:,0]+.5*cxw[:,1]),-1)*float(data['slot_span_normalization_context_seconds'])
        owner=data['pool_source_slot']
        qid=str(meta['qid'])
        previous=getattr(monitor,'pool_previous',{})
        current_key=(monitor.phase,qid)
        before=previous.get(current_key)
        data['pool_source_changed_fraction']=np.array(np.mean(before[1]!=owner) if before is not None and before[0]==monitor.epoch-1 else np.nan)
        # Cache fixed probes only, so full validation history does not grow memory unnecessarily.
        if monitor.phase=='probe':
            previous[current_key]=(monitor.epoch,owner.copy());monitor.pool_previous=previous
        data.update(head_measure(unit,cpu_head,monitor.backbone))
    else:
        mask=valid.detach().cpu().bool()
        # h is already restricted to valid units by the legacy observer.
        data.update(valid_temporal_mask=mask.numpy(),original_temporal_indices=np.flatnonzero(mask.numpy()),
            valid_count=np.array(len(unit)),unit_weight_1_over_valid_count=np.ones(len(unit))/max(1,len(unit)),
            pool_source_slot_status=np.array('not_applicable_native_mean_pooling'))
        data.update(head_measure(unit,cpu_head,'flash',torch.ones(len(unit),dtype=torch.bool),head_input.detach().cpu()))
    if monitor.backbone!='flash' and (monitor.phase=='probe' or (monitor.phase=='train' and monitor.batch==1)):
        data['unit_features']=unit.numpy()
    if monitor.backbone=='flash':data['raw_unit_feature_location']=np.array('legacy flash_temporal raw probe/first-training-batch; no duplicate copy')
    if 'recomputed_logit' in data:
        assert abs(float(data['recomputed_logit'])-float(logit))<2e-4,'CPU head replay differs from captured native logit'
    data['removal_delta_definition']=np.array('removed_logit_minus_original; legacy leave_one_unit_out_logit_drop has opposite sign')
    np.savez_compressed(root/(key+'.npz'),**data)
    return dict(pool_dimension_count=unit.shape[-1],pool_source_record=str(root/(key+'.npz')),
        pool_signed_component_sum=float(np.sum(data['pool_signed_logit_component'])),
        pool_head_bias_component=float(data['pool_head_bias_component']),pool_head_decomposition_residual=float(data['head_decomposition_residual']))
