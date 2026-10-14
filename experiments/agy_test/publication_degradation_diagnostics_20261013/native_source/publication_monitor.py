"""Bridge frozen publication training to the retained legacy nine-area diagnostics."""
import os
import json
from pathlib import Path
import numpy as np
import torch
from mechanism_monitor import save_json as json_save, append_json as append


class Recorder:
    def __init__(self,model,criterion,backbone):
        self.model,self.criterion,self.backbone=model,criterion,backbone
        self.root=Path(os.environ['PUBLICATION_RUN']);self.epoch=0;self.batch_id=0;self.legacy=None
        self.phase=None

    def configure(self,train,validation,opt):
        from legacy_bridge import LegacyBridge
        self.legacy=LegacyBridge(self.model,self.criterion,self.backbone,self.root,train,validation,opt)

    def start_epoch(self,epoch):
        self.epoch=epoch+1;self.batch_id=0;self.phase='train'
        self.legacy.start_epoch(self.epoch)

    def begin(self,batch,phase,inputs):
        self.phase=phase;self.inputs=inputs
        if phase=='train':
            self.batch_id+=1
            self.legacy.begin(batch[0],self.batch_id)
        else:
            # Native validation is retained separately. Full legacy diagnostics use
            # their unchanged prediction path in the RNG-preserved end_epoch call.
            self.legacy.auroc.enabled=False
            if self.backbone!='flash':
                self.legacy.observer.pending=None;self.legacy.objective.begin()
                self.legacy.decoder.enabled=False
            else:self.legacy.temporal.enabled=False

    def observe(self,outputs,targets=None,losses=None):
        if self.phase=='train':self.legacy.observe(outputs,targets,self.inputs,losses)

    @torch.no_grad()
    def gradients(self,optimizer):
        norm=sum(float(p.grad.detach().float().square().sum()) for p in self.model.parameters() if p.grad is not None)**.5
        self.legacy.optimization(norm,optimizer)

    def flash_units(self,units,mask):
        pass  # The retained legacy pyramid hook captures the actual same native units.

    def finish(self,model,criterion,optimizer,opt,epoch,score,previous,metrics):
        from legacy_support import preserve_rng
        from sklearn.metrics import roc_auc_score
        with preserve_rng():
            val,candidates=self.legacy.end_epoch(epoch+1)
        auc=float(roc_auc_score(val['labels'],val['scores']))
        selection=self.root/'selection';selection.mkdir(parents=True,exist_ok=True)
        append(selection/'trace.jsonl',dict(epoch=epoch+1,native_epoch_index=epoch,score=score,previous_best=previous,
            improved=score>previous,metrics=metrics,seen_auroc=auc,selection_data='Seen validation only'))
        if score>previous:
            json_save(selection/'selected.json',dict(epoch=epoch+1,native_epoch_index=epoch,score=score,
                metric='MR-full-mAP' if self.backbone!='flash' else 'mean(R1@0.5,R1@0.7)',status='training_provisional'))
        shadow=selection/'auroc_shadow.json'
        old=json.loads(shadow.read_text()) if shadow.exists() else {'auroc':-1}
        local=self.root/'local_only'/'checkpoints';local.mkdir(parents=True,exist_ok=True)
        if auc>old['auroc']:
            json_save(shadow,dict(epoch=epoch+1,auroc=auc,role='diagnostic_only_no_test'))
            torch.save(dict(model=model.state_dict(),opt=opt,epoch=epoch),local/'seen_auroc_shadow.pt')
        if epoch+1 in (1,5,10,20,26):
            torch.save(dict(model=model.state_dict(),opt=opt,epoch=epoch),local/f'epoch_{epoch+1:03d}.pt')
        np.savez_compressed(self.root/'local_only'/'last_validation.npz',**val)
        torch.save(candidates,self.root/'local_only'/'last_candidates.pt')
        json_save(self.root/'STATUS.json',dict(state='training',epoch=epoch+1,max_epochs=opt.n_epoch,
            legacy_diagnostics_complete_for_epoch=True,updated=__import__('time').time()))


def attach(model,criterion,backbone):
    if not os.environ.get('PUBLICATION_RUN'):return None
    if not hasattr(model,'_publication'):model._publication=Recorder(model,criterion,backbone)
    return model._publication
