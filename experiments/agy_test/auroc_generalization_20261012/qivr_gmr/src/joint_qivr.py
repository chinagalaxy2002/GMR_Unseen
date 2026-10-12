"""Versioned end-to-end QIVR: native localization + trainable interval verification.

Unlike cached QIVR, Gaussian ROI pooling is differentiable and padding-masked.
The intended best-slot fallback is applied last, so negatives cannot overwrite it.
The original Hybrid verifier (including its global residual) is retained.
"""
import torch
import torch.nn.functional as F


def gaussian_roi(video, valid, spans):
    lengths = valid.sum(-1).clamp(min=1)
    position = (torch.arange(video.shape[1], device=video.device, dtype=video.dtype)[None] + .5) / lengths[:, None]
    center, sigma = spans[..., :1], spans[..., 1:].clamp(min=.05) / 2
    logits = -.5 * ((position[:, None] - center) / sigma).square()
    logits = logits.masked_fill(~valid[:, None].bool(), float('-inf'))
    weights = logits.softmax(-1)
    return torch.einsum('bqt,btd->bqd', weights, video)


def evidence_loss(logits, spans, targets):
    labels = torch.zeros_like(logits)
    weights = torch.ones_like(logits)
    fallback = torch.zeros(len(logits), device=logits.device, dtype=torch.bool)
    max_ious = []
    with torch.no_grad():
        xx = torch.stack([spans[..., 0] - .5*spans[..., 1], spans[..., 0] + .5*spans[..., 1]], -1).clamp(0, 1)
        for i, target in enumerate(targets['span_labels']):
            gt = target['spans']
            if not len(gt):
                max_ious.append(torch.zeros(logits.shape[1], device=logits.device))
                continue
            gx = torch.stack([gt[:, 0] - .5*gt[:, 1], gt[:, 0] + .5*gt[:, 1]], -1)
            inter = (torch.minimum(xx[i, :, None, 1], gx[None, :, 1]) - torch.maximum(xx[i, :, None, 0], gx[None, :, 0])).clamp(min=0)
            union = xx[i, :, None, 1] - xx[i, :, None, 0] + gx[None, :, 1] - gx[None, :, 0] - inter
            iou = (inter / union.clamp(min=1e-8)).max(-1).values
            max_ious.append(iou)
            weights[i] = ((iou < .1) | (iou >= .5)).to(logits.dtype)
            labels[i] = (iou >= .5).to(logits.dtype)
            if not (iou >= .5).any():
                best = iou.argmax()
                labels[i, best], weights[i, best], fallback[i] = 1., 1., True
    loss = (F.binary_cross_entropy_with_logits(logits, labels, reduction='none') * weights).sum() / weights.sum().clamp(min=1e-6)
    return loss, fallback, torch.stack(max_ious)


def attach_joint_qivr(model, criterion, verifier_class, hidden_dim):
    model.exist_head = None  # Replaced by QIVR, not a second existence objective.
    model.qivr_head = verifier_class(d_model=hidden_dim)
    criterion.weight_dict['loss_evidence'] = 1.

    def verify(module, args, kwargs, outputs):
        inputs = kwargs
        if not inputs:
            inputs = dict(zip(('src_txt', 'src_txt_mask', 'src_vid', 'src_vid_mask'), args))
        video, text = outputs['vid_mem'], outputs['txt_mem']
        video_mask, text_mask = inputs['src_vid_mask'].bool(), inputs['src_txt_mask'].bool()
        roi = gaussian_roi(video, video_mask, outputs['pred_spans'])
        query = (text * text_mask[..., None]).sum(1) / text_mask.sum(1, keepdim=True).clamp(min=1)
        evidence, existence = module.qivr_head(outputs['hs'], roi, query)
        outputs['pred_evidence_logits'], outputs['pred_exist_logits'] = evidence, existence
        with torch.no_grad():
            hs = outputs['hs']
            qe = query[:, None].expand_as(hs)
            outputs['qivr_attention'] = module.qivr_head.gate_mlp(torch.cat([hs, roi, qe], -1)).squeeze(-1).softmax(-1)
            outputs['qivr_global_residual'] = module.qivr_head.global_context(torch.cat([hs.max(1).values, hs.mean(1), query], -1)).reshape(-1)
        return outputs

    def supervise(module, args, losses):
        outputs, targets = args
        loss, fallback, iou = evidence_loss(outputs['pred_evidence_logits'], outputs['pred_spans'], targets)
        losses['loss_evidence'] = loss
        outputs['qivr_fallback'] = fallback
        outputs['qivr_evidence_target_max_iou'] = iou.max(-1).values
        return losses

    model.register_forward_hook(verify, with_kwargs=True)
    criterion.register_forward_hook(supervise)
    return model, criterion
