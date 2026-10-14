"""Keep the old nine diagnostic areas and their exact native execution frequencies."""
import copy
import importlib
import json
import os
from pathlib import Path
import numpy as np
import torch
from legacy_support import (BackboneMonitor, RepresentationMonitor, ResponseMonitor, ParameterUpdateMonitor,
    DecoderSlotMonitor, AUROCMechanismMonitor, ObjectiveSplitMonitor, fixed_probe, stable_subset, predict,
    preserve_rng, diagnostics, annotate_lengths, metric_report, calibrate, final_ranking_bootstrap)
from mechanism_monitor import append_json, save_json
from response_monitor import frozen_records, save_records, summarize


class LegacyBridge:
    def __init__(self, model, criterion, backbone, root, train, validation, opt):
        self.model,self.criterion,self.backbone,self.root,self.opt=model,criterion,backbone,root,opt
        self.output=root/'monitor';self.output.mkdir(parents=True,exist_ok=True)
        self.steps=0;self.epoch=0
        self.module=importlib.import_module('training.'+dict(moment='moment_detr_gmr',qd='qd_detr_gmr',flash='flash_vtg_gmr')[backbone]+'.dataset')
        self.paths=diagnostics.registry.paths(os.environ['PUBLICATION_DATASET'],os.environ['PUBLICATION_SPLIT'],backbone)
        self.paths['dataset']=os.environ['PUBLICATION_DATASET']
        self.validation=copy.copy(validation)
        self.validation.load_labels=False
        opt.native_clip_to_duration=backbone!='moment'
        self.updates=ParameterUpdateMonitor(model,self.output)
        self.auroc=AUROCMechanismMonitor(model,self.output,backbone,50)
        self.auroc.provenance_clip_length=opt.clip_length
        if backbone!='flash':
            matcher=criterion.matcher
            self.auroc.provenance_matcher_cost={k:getattr(matcher,k) for k in ('cost_class','cost_span','cost_giou','span_loss_type','max_v_l')}
        for data in (train,self.validation):annotate_lengths(data,self.paths,opt,diagnostics.registry,self.module)
        self.probe=stable_subset(train,64)
        if backbone!='flash':
            self.probe.data=[r for r in self.probe.data if len(r['relevant_windows'])<=opt.max_windows]
            self.observer=BackboneMonitor(model,criterion,self.output,50)
            self.representation=RepresentationMonitor(model,criterion,self.output)
            self.response=ResponseMonitor(self.output,50)
            self.decoder=DecoderSlotMonitor(model,self.output,50)
            self.objective=ObjectiveSplitMonitor(criterion,self.output)
            self.previous=None
        else:
            from auroc_mechanism_monitor import FlashTemporalMonitor
            self.temporal=FlashTemporalMonitor(model,criterion,self.output,50)
            self.auroc.temporal=self.temporal
            self.probe.txt_drop_ratio=0
        save_json(root/'probe_metadata.json',dict(qids=[str(r['qid']) for r in self.probe.data],
            selection='same legacy hash-ranked training Seen cohort, at most 64/class; DETR GT-truncated excluded'))
        # Legacy epoch zero observations are retained and never eligible for selection.
        self.run_probe(0)
        self.run_validation(0)

    def run_probe(self,epoch):
        self.auroc.epoch=epoch
        if self.backbone!='flash':
            self.previous=fixed_probe(self.model,self.criterion,self.probe,self.module,self.opt,self.output,epoch,
                self.previous,self.response,self.decoder,self.auroc)
        else:
            from legacy_flash import predict as flash_predict
            flash_predict(self.model,self.probe,self.opt,self.auroc,epoch,'probe')

    def run_validation(self,epoch,phase='validation',data=None):
        data=self.validation if data is None else data
        if self.backbone!='flash':
            frozen,candidates=predict(self.model,data,self.module,self.opt,self.opt.num_workers,True,self.auroc,phase,epoch)
        else:
            from legacy_flash import predict as flash_predict
            frozen,candidates=flash_predict(self.model,data,self.opt,self.auroc,epoch,phase)
        if phase=='validation':
            response=frozen_records(dict(**frozen,threshold=np.array(.5)),candidates)
            append_json(self.output/'validation_responses.jsonl',dict(epoch=epoch,threshold_usage='0.5 descriptive, not final calibration',subsets=summarize(response)))
            save_records(self.output/f'validation_responses_epoch_{epoch:04d}.npz',response)
        return frozen,candidates

    def start_epoch(self,epoch):
        self.epoch=epoch
        self.updates.begin_epoch(epoch)
        if self.backbone!='flash':
            self.observer.begin_epoch(epoch-1)
            self.response.begin_epoch(epoch)

    def begin(self,metadata,batch):
        self.steps+=1
        self.metadata=metadata
        self.auroc.begin('train',self.epoch,self.steps,batch)
        if self.backbone!='flash':
            self.observer.begin_batch(metadata)
            self.representation.begin_batch()
            self.decoder.begin('train',self.epoch,self.steps,batch)
            self.objective.begin()
        else:self.temporal.begin('train',self.epoch,self.steps,batch)

    def observe(self,outputs,targets,inputs,losses):
        self.losses=losses
        if self.backbone!='flash':
            self.objective.observe(self.metadata,self.epoch,self.steps,losses)
            self.observer.observe(outputs,targets,losses)
            self.decoder.observe(outputs,targets,self.metadata,inputs,self.observer.indices)
            self.response.observe(outputs,targets,self.metadata,self.observer.indices,self.steps)
            self.auroc.observe(outputs,self.metadata,inputs,self.observer.indices,targets=targets)
            self.auroc.gradients(losses,self.criterion,self.metadata)
            if (self.steps-1)%50==0:self.representation.observe(self.epoch,self.steps,losses,self.metadata)
        else:
            from legacy_flash import candidates_from_train
            from response_monitor import geometry_record
            geometry=candidates_from_train(outputs,self.metadata)
            self.temporal.observe(outputs,self.metadata,geometry)
            self.auroc.observe(outputs,self.metadata,inputs,geometry=geometry)
            records=[]
            for i,(meta,g) in enumerate(zip(self.metadata,geometry)):
                r=dict(qid=str(meta['qid']),vid=str(meta['vid']),partition=meta['partition'],label=meta['exist_label'],
                    existence_score=float(outputs['pred_exist_logits'][i].detach().sigmoid()),existence_logit=float(outputs['pred_exist_logits'][i].detach()))
                r.update(geometry_record(g['slot_spans_sec'],g['slot_scores'],meta['relevant_windows']));records.append(r)
            append_json(self.output/'train_responses.jsonl',dict(epoch=self.epoch,step=self.steps,subsets=summarize(records),unit='temporal candidates; not DETR slots'))
            self.auroc.gradients(losses,self.criterion,self.metadata)

    def optimization(self,norm,optimizer):
        self.auroc.optimization(self.losses,self.criterion,norm,float(self.opt.grad_clip),float(optimizer.param_groups[0]['lr']),self.metadata)
        if self.backbone!='flash':self.representation.hs=None

    def end_epoch(self,epoch):
        if self.backbone!='flash':
            self.observer.end_epoch();self.response.end_epoch()
            self.observer.pending=None
        self.updates.end_epoch()
        self.run_probe(epoch)
        val,candidates=self.run_validation(epoch)
        return val,candidates
