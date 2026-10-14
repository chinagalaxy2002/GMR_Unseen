"""Read-only decoder instrumentation; consumes attention weights already returned.

Training is sampled, fixed Seen probes are recorded every epoch. No extra model
forward, attention recomputation, loss, RNG draw, or head is introduced.
"""
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from mechanism_monitor import append_json, save_json


def pairwise_iou(spans):
    inter = (torch.minimum(spans[..., :, None, 1], spans[..., None, :, 1]) -
             torch.maximum(spans[..., :, None, 0], spans[..., None, :, 0])).clamp(min=0)
    length = (spans[..., 1] - spans[..., 0]).clamp(min=0)
    union = length[..., :, None] + length[..., None, :] - inter
    return inter / union.clamp(min=1e-8)


def normalized_entropy(weights):
    probability = weights / weights.sum(-1, keepdim=True).clamp(min=1e-12)
    return -(probability * probability.clamp(min=1e-12).log()).sum(-1)


class DecoderSlotMonitor:
    def __init__(self, model, folder, every=50):
        self.folder = Path(folder) / 'decoder_slots'
        self.folder.mkdir(parents=True, exist_ok=True)
        self.model = model
        self.every, self.enabled, self.phase = every, False, None
        self.handles, self.seen, self.hs, self.attention = [], set(), None, {}
        self.layer_count = len(model.transformer.decoder.layers)
        self.no_sa = [bool(getattr(layer, 'rm_self_attn_decoder', False))
                      for layer in model.transformer.decoder.layers]
        for i, layer in enumerate(model.transformer.decoder.layers):
            if hasattr(layer, 'self_attn'):
                self.handles.append(layer.self_attn.register_forward_hook(self.attention_hook(i, 'self')))
            cross = getattr(layer, 'multihead_attn', None)
            if cross is None:
                cross = layer.cross_attn
            self.handles.append(cross.register_forward_hook(self.attention_hook(i, 'cross')))
        self.handles.append(model.transformer.register_forward_hook(self.capture_hs))
        save_json(self.folder / 'METADATA.json', dict(
            schema='decoder_slots_v1', training_sampling=f'first batch and every {every} steps',
            raw_training='one sampled batch per epoch; summaries for every sampled batch',
            fixed_probe='all fixed Seen queries, every epoch including epoch zero',
            representations='normalized decoder outputs used by native prediction heads, layer/batch/slot/feature',
            query_parameters='Moment: learned query embeddings; QD: learned reference-anchor logits',
            geometry='normalized native cxw and clipped xx; not postprocessed seconds',
            attention='native head-averaged returned weights; training weights include dropout; summaries row-renormalize',
            cross_tokens='Moment: video then text (including padded positions); QD: video only, no global token',
            self_attention_disabled=self.no_sa, disabled_attention='absent, never fabricated as zero',
            thresholds=dict(foreground=.5, correct_iou=.5, duplicate_iou=.9),
            selection='diagnostic only; no Unseen use before frozen final evaluation'))

    def begin(self, phase, epoch, step, batch):
        self.phase, self.epoch, self.step, self.batch = phase, epoch, step, batch
        self.enabled = phase == 'probe' or batch == 1 or (step - 1) % self.every == 0
        self.seen, self.hs, self.attention = set(), None, {}

    def attention_hook(self, layer, kind):
        def capture(module, args, output):
            key = (layer, kind)
            if self.enabled and key not in self.seen:
                self.seen.add(key)
                if isinstance(output, tuple) and len(output) > 1 and output[1] is not None:
                    self.attention[key] = output[1].detach().cpu()
        return capture

    def capture_hs(self, module, args, output):
        if self.enabled and self.hs is None:
            self.hs = output[0].detach().cpu()

    @torch.no_grad()
    def observe(self, outputs, targets, metadata, inputs, indices):
        if not self.enabled:
            return
        hs = self.hs
        assert hs is not None and hs.ndim == 4 and hs.shape[0] == self.layer_count
        predictions = list(outputs.get('aux_outputs', [])) + [outputs]
        assert len(predictions) == len(hs), 'Layerwise spans require native auxiliary predictions'
        spans = torch.stack([p['pred_spans'].detach().cpu() for p in predictions])
        foreground = torch.stack([p['pred_logits'].detach().cpu().softmax(-1)[..., 0] for p in predictions])
        xx = torch.stack([spans[..., 0] - spans[..., 1]/2, spans[..., 0] + spans[..., 1]/2], -1).clamp(0, 1)
        valid = xx[..., 1] > xx[..., 0]
        cosine = F.normalize(hs, dim=-1) @ F.normalize(hs, dim=-1).transpose(-1, -2)
        distance = torch.cdist(hs, hs)
        overlaps = pairwise_iou(xx)
        bsz, slots = hs.shape[1:3]
        off_diagonal = ~torch.eye(slots, dtype=torch.bool)
        assignments = torch.full((bsz, slots), -1, dtype=torch.long)
        max_gt = max(len(t['spans']) for t in targets['span_labels'])
        gt = torch.zeros(bsz, max_gt, 2)
        gt_valid = torch.zeros(bsz, max_gt, dtype=torch.bool)
        best_iou = torch.full(spans.shape[:-1], float('nan'))
        matched_iou = torch.full(spans.shape[:-1], float('nan'))
        for b, (target, (src, dst)) in enumerate(zip(targets['span_labels'], indices)):
            truth = target['spans'].detach().cpu()
            gt[b, :len(truth)] = truth
            gt_valid[b, :len(truth)] = True
            assignments[b, src.cpu()] = dst.cpu()
            if not len(truth):
                continue
            gx = torch.stack([truth[:, 0]-truth[:, 1]/2, truth[:, 0]+truth[:, 1]/2], -1)
            inter = (torch.minimum(xx[:, b, :, None, 1], gx[None, None, :, 1]) -
                     torch.maximum(xx[:, b, :, None, 0], gx[None, None, :, 0])).clamp(min=0)
            union = (xx[:, b, :, None, 1]-xx[:, b, :, None, 0] +
                     gx[None, None, :, 1]-gx[None, None, :, 0]-inter)
            iou = inter / union.clamp(min=1e-8)
            best_iou[:, b] = iou.max(-1).values
            matched_iou[:, b, src.cpu()] = iou[:, src.cpu(), dst.cpu()]
        vid_mask, txt_mask = inputs['src_vid_mask'].detach().cpu().bool(), inputs['src_txt_mask'].detach().cpu().bool()
        arrays = dict(query_parameters=self.model.query_embed.weight.detach().cpu().numpy(),
            duration_seconds=np.array([m['duration'] for m in metadata]), hs=hs.numpy(), spans_cxw=spans.numpy(), spans_xx=xx.numpy(), foreground=foreground.numpy(),
            valid_span=valid.numpy(), slot_cosine=cosine.numpy(), slot_l2_distance=distance.numpy(),
            pairwise_iou=overlaps.numpy(), best_gt_iou=best_iou.numpy(), final_gt_assignment=assignments.numpy(),
            final_assignment_iou_by_layer=matched_iou.numpy(), gt_cxw=gt.numpy(), gt_valid=gt_valid.numpy(),
            video_mask=vid_mask.numpy(), text_mask=txt_mask.numpy(),
            qids=np.array([str(m['qid']) for m in metadata]), vids=np.array([str(m['vid']) for m in metadata]),
            partitions=np.array([m['partition'] for m in metadata]),
            existence=outputs['pred_exist_logits'].detach().sigmoid().cpu().reshape(-1).numpy())
        for (layer, kind), weights in self.attention.items():
            arrays[f'attention_{kind}_layer_{layer}'] = weights.numpy()
        if 'pred_evidence_logits' in outputs:
            arrays['evidence'] = outputs['pred_evidence_logits'].detach().sigmoid().cpu().numpy()
        rows = []
        for layer in range(len(hs)):
            for b, meta in enumerate(metadata):
                active = valid[layer, b] & (foreground[layer, b] > .5)
                pair_valid = off_diagonal & valid[layer, b, :, None] & valid[layer, b, None, :]
                pair_active = pair_valid & active[:, None] & active[None, :]
                centered = hs[layer, b] - hs[layer, b].mean(0, keepdim=True)
                singular = torch.linalg.svdvals(centered.double())
                energy = singular.square()
                probability = energy / energy.sum().clamp(min=1e-12)
                rank = float((-(probability * probability.clamp(min=1e-12).log()).sum()).exp()) if energy.sum() > 1e-12 else 0.
                row = dict(qid=str(meta['qid']), vid=str(meta['vid']), partition=meta['partition'], layer=layer,
                    cosine_offdiag_mean=float(cosine[layer, b][off_diagonal].mean()),
                    l2_offdiag_mean=float(distance[layer, b][off_diagonal].mean()), effective_centered_rank=rank,
                    foreground_range=float(foreground[layer, b].max()-foreground[layer, b].min()),
                    foreground_std=float(foreground[layer, b].std(unbiased=False)), active_count=int(active.sum()),
                    valid_pair_count=int(pair_valid.sum()), active_pair_count=int(pair_active.sum()),
                    pair_iou_mean=float(overlaps[layer, b][pair_valid].mean()) if pair_valid.any() else None,
                    duplicate_pair_fraction=float((overlaps[layer, b][pair_valid] >= .9).float().mean()) if pair_valid.any() else None,
                    active_duplicate_pair_fraction=float((overlaps[layer, b][pair_active] >= .9).float().mean()) if pair_active.any() else None,
                    hs_norm_by_slot=hs[layer, b].norm(dim=-1).tolist(), foreground_by_slot=foreground[layer, b].tolist())
                if layer:
                    row['layer_change_l2_by_slot'] = (hs[layer, b]-hs[layer-1, b]).norm(dim=-1).tolist()
                if gt_valid[b].any():
                    row['correct_active_count'] = int((active & (best_iou[layer, b] >= .5)).sum())
                    row['best_gt_iou_by_slot'] = best_iou[layer, b].tolist()
                for kind in ('self', 'cross'):
                    weights = self.attention.get((layer, kind))
                    if weights is None:
                        row[f'{kind}_attention_status'] = 'disabled' if kind == 'self' and self.no_sa[layer] else 'unavailable'
                        continue
                    w = weights[b]
                    row[f'{kind}_attention_status'] = 'observed'
                    row[f'{kind}_attention_entropy_by_slot'] = normalized_entropy(w).tolist()
                    row[f'{kind}_attention_row_sum_by_slot'] = w.sum(-1).tolist()
                    similarities = F.normalize(w, dim=-1) @ F.normalize(w, dim=-1).T
                    row[f'{kind}_attention_slot_cosine'] = float(similarities[off_diagonal].mean())
                    if kind == 'self':
                        row['self_attention_diagonal_mass_by_slot'] = (w.diagonal()/w.sum(-1).clamp(min=1e-12)).tolist()
                    else:
                        nvideo = vid_mask.shape[1]
                        assert w.shape[-1] in (nvideo, nvideo+txt_mask.shape[1])
                        video = w[:, :nvideo] * vid_mask[b]
                        row['cross_video_mass_by_slot'] = (video.sum(-1)/w.sum(-1).clamp(min=1e-12)).tolist()
                        position = (torch.arange(nvideo)+.5)/vid_mask[b].sum().clamp(min=1)
                        center = (video*position).sum(-1)/video.sum(-1).clamp(min=1e-12)
                        row['cross_video_center_by_slot'] = center.tolist()
                        row['cross_video_spread_by_slot'] = ((video*(position-center[:, None]).square()).sum(-1)/video.sum(-1).clamp(min=1e-12)).sqrt().tolist()
                rows.append(row)
        append_json(self.folder / f'{self.phase}_slots.jsonl', dict(epoch=self.epoch, step=self.step, batch=self.batch, records=rows))
        if self.phase == 'probe' or self.batch == 1:
            filename = f'{self.phase}_epoch_{self.epoch:04d}_step_{self.step:08d}_batch_{self.batch:04d}.npz'
            np.savez_compressed(self.folder / filename, **arrays)
        self.enabled, self.hs, self.attention = False, None, {}

    def close(self):
        for handle in self.handles:
            handle.remove()
