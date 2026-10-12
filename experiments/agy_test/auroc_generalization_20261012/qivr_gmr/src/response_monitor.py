"""Read-only positive localization / positive and negative existence diagnostics.

Foreground active slots, evidence-positive slots and max-pool contributors are
different quantities. Test diagnostics never influence training or selection.
"""
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from mechanism_monitor import append_json, save_json


def overlap_matrix(a, b):
    a, b = np.asarray(a, dtype=float).reshape(-1, 2), np.asarray(b, dtype=float).reshape(-1, 2)
    inter = np.maximum(0, np.minimum(a[:, None, 1], b[None, :, 1]) - np.maximum(a[:, None, 0], b[None, :, 0]))
    union = (a[:, 1] - a[:, 0])[:, None] + (b[:, 1] - b[:, 0])[None, :] - inter
    return np.divide(inter, union, out=np.zeros_like(inter), where=union > 0)


def maximum_matches(adjacency):
    owner = np.full(adjacency.shape[1], -1, dtype=int)
    def visit(slot, used):
        for gt in np.flatnonzero(adjacency[slot]):
            if not used[gt]:
                used[gt] = True
                if owner[gt] < 0 or visit(owner[gt], used):
                    owner[gt] = slot
                    return True
        return False
    return sum(visit(slot, np.zeros(adjacency.shape[1], bool)) for slot in range(len(adjacency)))


def geometry_record(spans, foreground, gt):
    spans, foreground = np.asarray(spans), np.asarray(foreground)
    valid = spans[:, 1] > spans[:, 0]
    active = valid & (foreground > .5)
    relative = valid & (foreground >= .5 * foreground.max()) & (foreground > 0)
    row = dict(active_count=int(active.sum()), relative_active_count=int(relative.sum()), valid_slots=int(valid.sum()),
        foreground_peak=float(foreground.max()), foreground_mean=float(foreground.mean()))
    if len(gt):
        iou = overlap_matrix(spans, gt)
        iou[~valid] = 0
        correct = iou >= .5
        ranked = sorted(np.flatnonzero(valid).tolist(), key=lambda j: -foreground[j])
        top1 = float(iou[ranked[0]].max()) if ranked else 0.
        row.update(top1_iou=top1, oracle_iou=float(iou.max()), top1_hit=float(top1 >= .5),
            coverage=float(correct.any()), active_coverage=float(correct[active].any()),
            gt_recall=maximum_matches(correct) / len(gt), active_gt_recall=maximum_matches(correct[active]) / len(gt),
            correct_active_count=int((active & correct.any(1)).sum()),
            incorrect_active_count=int((active & ~correct.any(1)).sum()), gt_count=len(gt))
    return row


def evidence_record(spans, evidence, gt):
    geometry = geometry_record(spans, evidence, gt)
    # Count all evidence-positive slots, even invalid spans; geometry still excludes invalid spans.
    result = {'evidence_' + key:value for key,value in geometry.items()}
    result['evidence_active_count'] = int((np.asarray(evidence) > .5).sum())
    result['evidence_valid_active_count'] = geometry['active_count']
    return result


@torch.no_grad()
def training_records(outputs, targets, metadata, indices):
    """Native training-coordinate localization; no loss or graph mutation."""
    cxw = outputs["pred_spans"].detach().cpu().numpy()
    xx = np.stack([cxw[..., 0] - cxw[..., 1] / 2, cxw[..., 0] + cxw[..., 1] / 2], -1)
    foreground = outputs["pred_logits"].detach().softmax(-1)[..., 0].cpu().numpy()
    logits = outputs["pred_exist_logits"].detach().reshape(-1)
    scores = logits.sigmoid().cpu().numpy()
    labels = targets["exist_label"].detach().reshape(-1)
    bce = F.binary_cross_entropy_with_logits(logits, labels.float(), reduction="none").cpu().numpy()
    contributors = None
    if "hs" in outputs:
        winners = outputs["hs"].detach().argmax(1).cpu().numpy()
        contributors = [len(np.unique(w)) for w in winners]
    evidence = outputs.get("pred_evidence_logits")
    evidence = evidence.detach().sigmoid().cpu().numpy() if evidence is not None else None
    result = []
    for i, (meta, target, (slots, gt_ids)) in enumerate(zip(metadata, targets["span_labels"], indices)):
        gt_cxw = target["spans"].detach().cpu().numpy()
        gt_xx = np.stack([gt_cxw[:, 0] - .5 * gt_cxw[:, 1], gt_cxw[:, 0] + .5 * gt_cxw[:, 1]], -1)
        row = dict(qid=str(meta["qid"]), vid=str(meta["vid"]), partition=meta["partition"], label=int(labels[i]),
            existence_score=float(scores[i]), existence_logit=float(logits[i]), existence_bce=float(bce[i]),
            coordinate_basis="native training normalization; foreground geometry clipped to [0,1]")
        row.update(geometry_record(xx[i].clip(0, 1), foreground[i], gt_xx))
        if contributors is not None:
            row["max_pool_contributor_count"] = contributors[i]
        if evidence is not None:
            row.update(evidence_record(xx[i].clip(0, 1), evidence[i], gt_xx))
        for key in ("qivr_fallback", "qivr_evidence_target_max_iou", "qivr_global_residual"):
            if key in outputs:
                row[key] = float(outputs[key][i].detach().cpu())
        if "qivr_attention" in outputs:
            attention = outputs["qivr_attention"][i].detach()
            row["qivr_attention_entropy"] = float(-(attention * attention.clamp(min=1e-12).log()).sum().cpu())
        slots, gt_ids = slots.cpu().numpy(), gt_ids.cpu().numpy()
        if len(slots):
            pred, truth = xx[i, slots], gt_xx[gt_ids]
            inter = np.maximum(0, np.minimum(pred[:, 1], truth[:, 1]) - np.maximum(pred[:, 0], truth[:, 0]))
            union = (pred[:, 1] - pred[:, 0]) + (truth[:, 1] - truth[:, 0]) - inter
            iou = np.divide(inter, union, out=np.zeros_like(inter), where=union > 0)
            enclosure = np.maximum(pred[:, 1], truth[:, 1]) - np.minimum(pred[:, 0], truth[:, 0])
            giou = iou - np.divide(enclosure - union, enclosure, out=np.zeros_like(enclosure), where=enclosure > 0)
            row.update(matched_iou=float(iou.mean()), matched_l1=float(np.abs(cxw[i, slots] - gt_cxw[gt_ids]).mean()),
                matched_giou_loss=float((1 - giou).mean()), matched_gt_count=len(slots))
        result.append(row)
    return result


def frozen_records(frozen, candidates):
    lookup = {str(q):i for i,q in enumerate(frozen["qids"])}
    assert len(lookup) == len(candidates)
    result = []
    for candidate in candidates:
        i = lookup[str(candidate["qid"])]
        assert frozen["partitions"][i] == candidate["partition"]
        score, y = float(frozen["scores"][i]), int(frozen["labels"][i])
        probability=float(frozen.get("exist_probabilities",frozen["scores"])[i])
        bce=float(np.logaddexp(0,float(frozen["exist_logits"][i]))-y*float(frozen["exist_logits"][i])) if "exist_logits" in frozen else float(-np.log(np.clip(probability if y else 1-probability,1e-12,1)))
        row = dict(qid=str(candidate["qid"]), vid=str(candidate["vid"]), partition=candidate["partition"], label=y,
            existence_score=probability, native_existence_score=score, existence_bce=bce,
            accepted=bool(score >= float(frozen["threshold"])),
            native_accept_iou=float(frozen["accept_iou"][i]), coordinate_basis="native postprocessed seconds")
        row.update(geometry_record(candidate["slot_spans_sec"], candidate["slot_scores"], candidate["gt_windows"]))
        if "slot_evidence" in candidate:
            row.update(evidence_record(candidate["slot_spans_sec"], candidate["slot_evidence"], candidate["gt_windows"]))
        result.append(row)
    return result


def describe(values):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    return dict(n=len(values), mean=float(values.mean()), q05=float(np.percentile(values, 5)),
        median=float(np.median(values)), q95=float(np.percentile(values, 95))) if len(values) else dict(n=0, mean=None)


def summarize(records):
    groups = {}
    for part in sorted({r["partition"] for r in records}):
        selected = [r for r in records if r["partition"] == part]
        keys = sorted({k for r in selected for k,v in r.items() if isinstance(v, (int, float, bool)) and k != "label"})
        stats = {k:describe([r[k] for r in selected if k in r]) for k in keys}
        histogram = np.bincount([r["active_count"] for r in selected], minlength=11).tolist()
        bins = {}
        for count in sorted({r["active_count"] for r in selected}):
            subset = [r for r in selected if r["active_count"] == count]
            bins[str(count)] = dict(n=len(subset), metrics={k:describe([r[k] for r in subset if k in r])
                for k in ("existence_score", "existence_bce", "top1_iou", "oracle_iou", "coverage", "active_coverage", "active_gt_recall", "correct_active_count", "incorrect_active_count", "accepted")})
        matched = [r for r in selected if r.get("matched_gt_count", 0)]
        weighted = {k:sum(r[k]*r["matched_gt_count"] for r in matched) / sum(r["matched_gt_count"] for r in matched)
            for k in ("matched_iou", "matched_l1", "matched_giou_loss")} if matched else {}
        groups[part] = dict(n=len(selected), metrics=stats, active_count_histogram=histogram, by_active_count=bins,
            gt_weighted_localization=weighted)
        if any("evidence_active_count" in r for r in selected):
            groups[part]["by_evidence_active_count"] = {str(count):dict(n=len(subset), metrics={k:describe([r[k] for r in subset if k in r]) for k in ("existence_score", "top1_iou", "evidence_active_coverage", "evidence_active_gt_recall", "evidence_correct_active_count", "evidence_incorrect_active_count")}) for count in sorted({r["evidence_active_count"] for r in selected}) for subset in [[r for r in selected if r["evidence_active_count"] == count]]}
    return groups


def save_records(path, records):
    keys = sorted({k for r in records for k in r if k != "coordinate_basis"})
    arrays = {k:np.array([r.get(k, np.nan) for r in records], dtype=str if k in ("qid", "vid", "partition") else float) for k in keys}
    np.savez_compressed(path, **arrays)


class ResponseMonitor:
    def __init__(self, folder, log_every=50):
        self.folder, self.log_every = Path(folder), log_every
        self.folder.mkdir(parents=True, exist_ok=True)
        save_json(self.folder / "response_metadata.json", dict(
            activation="valid span and native foreground probability > 0.5; relative activation also recorded",
            max_pool_contributors="unique feature-wise max owners, NOT existence evidence or GT matches",
            evidence_activation="sigmoid per-slot evidence > 0.5, when an evidence head exists",
            observation="training records follow changing model state; fixed eval probes are separate",
            losses="unweighted per-query existence BCE and matched localization; no optimizer changes",
            unseen_usage="final frozen test diagnosis only"))

    def begin_epoch(self, epoch):
        self.epoch, self.records, self.window = epoch, [], []

    def observe(self, outputs, targets, metadata, indices, step):
        records = training_records(outputs, targets, metadata, indices)
        for row in records:
            row.update(epoch=self.epoch, step=step)
        self.records.extend(records)
        self.window.extend(records)
        if step == 1 or step % self.log_every == 0:
            append_json(self.folder / "train_responses.jsonl", dict(epoch=self.epoch, step=step, subsets=summarize(self.window)))
            self.window = []

    def end_epoch(self):
        append_json(self.folder / "epoch_responses.jsonl", dict(epoch=self.epoch, subsets=summarize(self.records)))
        save_records(self.folder / f"train_responses_epoch_{self.epoch:04d}.npz", self.records)

    def probe(self, epoch, records):
        append_json(self.folder / "probe_responses.jsonl", dict(epoch=epoch, subsets=summarize(records)))
        save_records(self.folder / f"probe_responses_epoch_{epoch:04d}.npz", records)


class ParameterUpdateMonitor:
    """Show actual module updates, separately from requires_grad flags."""
    def __init__(self, model, folder):
        self.model, self.folder = model, Path(folder)

    def begin_epoch(self, epoch):
        self.epoch = epoch
        self.before = {name:p.detach().cpu().clone() for name,p in self.model.named_parameters()
            if name.split('.')[0] in ('transformer', 'span_embed', 'class_embed', 'exist_head', 'qivr_head', 'input_vid_proj', 'input_txt_proj', 'pyramid', 'coord_head', 'conf_head', 'class_head', 'pooling')}

    @torch.no_grad()
    def end_epoch(self):
        groups = {}
        for name,param in self.model.named_parameters():
            if name not in self.before:
                continue
            before, after = self.before[name].double(), param.detach().cpu().double()
            group = groups.setdefault(name.split('.')[0], dict(parameters=0, trainable_parameters=0, delta_squared=0., before_squared=0.))
            group['parameters'] += param.numel()
            group['trainable_parameters'] += param.numel() if param.requires_grad else 0
            group['delta_squared'] += float((after-before).square().sum())
            group['before_squared'] += float(before.square().sum())
        for group in groups.values():
            delta, norm = group.pop('delta_squared')**.5, group.pop('before_squared')**.5
            group.update(update_l2=delta, relative_update_l2=delta/norm if norm else None, actually_changed=delta > 0)
        append_json(self.folder/'parameter_updates.jsonl', dict(epoch=self.epoch, modules=groups))
        self.before = {}
