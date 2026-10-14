"""Isolated CPU diagnostics. No access to test before checkpoint/calibration freeze."""
import os
import sys
import json
import shutil
import importlib
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F


def provenance(h):
    # Exact native torch.max winner, including its first-slot tie rule.
    values, owners = h.max(0)
    masked=h.clone()
    masked.scatter_(0, owners[None], float('-inf'))
    second, runner=masked.max(0)
    ties=h.eq(values[None])
    n,d=h.shape
    counts=torch.bincount(owners,minlength=n)
    return dict(pool_source_slot=owners.numpy().astype(np.int16), pool_selected_value=values.numpy(),
        pool_runner_up_slot=runner.numpy().astype(np.int16),pool_runner_up_value=second.numpy(),
        pool_top2_margin=(values-second).numpy(),pool_tie_mask=ties.numpy(),
        pool_tie_count=ties.sum(0).numpy().astype(np.int16),pool_owner_count=counts.numpy().astype(np.int16),
        pool_owner_fraction=counts.numpy()/d)


def head_measure(h, head, backbone, mask=None, head_input=None):
    if backbone=='flash':
        valid=mask.bool()
        units=h[valid]
        pooled=units.mean(0)
        query=head_input[:head_input.numel()-pooled.numel()]
        p=torch.cat((query,pooled))
        first,last=head[0],head[2]
        forward=lambda x:last(F.relu(first(x))).squeeze(-1)
    else:
        units=h
        p=h.max(0).values
        first,last=head.layers
        forward=lambda x:last(F.relu(first(x))).squeeze(-1)
    activation=first(p)>0
    gradient=(last.weight[0]*activation)@first.weight
    signed=p*gradient
    bias=(last.weight[0]*activation*first.bias).sum()+last.bias[0]
    z=forward(p)
    assert torch.allclose(signed.sum()+bias,z,atol=2e-5,rtol=2e-5), 'Head decomposition mismatch'
    result=dict(pool_logit_grad=gradient.numpy(),pool_signed_logit_component=signed.numpy(),
        pool_head_bias_component=np.array(float(bias)),head_relu_active_fraction=np.array(float(activation.float().mean())),
        head_decomposition_residual=np.array(float(signed.sum()+bias-z)))
    if backbone=='flash':
        n=len(units)
        alternatives=(units.sum(0)[None]-units)/max(1,n-1)
        counter=torch.cat((query.expand(n,-1),alternatives),-1)
        delta=forward(counter)-z
        result.update(unit_removal_logit_delta=delta.numpy(),mean_signed_unit_components=(units*gradient[-h.shape[-1]:]/n).sum(-1).numpy(),
            mean_positive_unit_components=(units*gradient[-h.shape[-1]:]/n).clamp(min=0).sum(-1).numpy(),
            mean_negative_unit_components=(units*gradient[-h.shape[-1]:]/n).clamp(max=0).sum(-1).numpy(),
            query_signed_component=np.array(float(signed[:-h.shape[-1]].sum())))
    else:
        owners=h.max(0).indices
        slot_components=torch.zeros(len(h))
        positive=torch.zeros(len(h));negative=torch.zeros(len(h))
        slot_components.scatter_add_(0,owners,signed)
        positive.scatter_add_(0,owners,signed.clamp(min=0))
        negative.scatter_add_(0,owners,signed.clamp(max=0))
        counter=[]
        for j in range(len(h)):
            counter.append(torch.cat((h[:j],h[j+1:])).max(0).values)
        delta=forward(torch.stack(counter))-z
        result.update(slot_signed_logit_component=slot_components.numpy(),slot_positive_logit_component=positive.numpy(),
            slot_negative_logit_component=negative.numpy(),slot_removal_logit_delta=delta.numpy())
        # Predetermined control slot independent of outcomes, and ownership / signed evidence leaders.
        count=torch.bincount(owners,minlength=len(h))
        control=0
        result.update(removal_owner_leader=np.array(float(delta[count.argmax()])),
            removal_signed_leader=np.array(float(delta[positive.argmax()])),removal_control_slot0=np.array(float(delta[control])))
    result['recomputed_logit']=np.array(float(z))
    return result
