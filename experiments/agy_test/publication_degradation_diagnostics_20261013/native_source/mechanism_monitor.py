"""Observers. Never optimize, select checkpoints, or train on Unseen labels.

Cached-head monitoring is enabled by default; QIVR_MONITOR=0 disables it.
QIVR_BACKBONE_MONITOR=1: actual matcher history and joint-backbone gradients.
QIVR_MONITOR_GRAD_EVERY=100 controls expensive gradient sampling.
"""
import hashlib
import json
import os
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f"{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    temp.replace(path)


def append_json(path, value):
    with Path(path).open("a") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")


def gradient_relation(loss_a, loss_b, named_parameters):
    """Read gradients without writing .grad, consuming RNG, or freeing the graph."""
    params = [(name, p) for name, p in named_parameters if p.requires_grad]
    if not params or not torch.is_tensor(loss_a) or not torch.is_tensor(loss_b):
        return dict(status="missing_loss_or_trainable_parameters", cosine=None)
    if not loss_a.requires_grad or not loss_b.requires_grad:
        return dict(status="loss_not_connected", cosine=None)
    ga = torch.autograd.grad(loss_a, [p for _, p in params], retain_graph=True, allow_unused=True)
    gb = torch.autograd.grad(loss_b, [p for _, p in params], retain_graph=True, allow_unused=True)
    common = [(name, a.detach().double(), b.detach().double()) for (name, _), a, b in zip(params, ga, gb) if a is not None and b is not None]
    if not common:
        return dict(status="no_shared_gradient_parameters", cosine=None)
    dot = sum((a * b).sum().item() for _, a, b in common)
    na = sum((a * a).sum().item() for _, a, _ in common) ** .5
    nb = sum((b * b).sum().item() for _, _, b in common) ** .5
    finite = np.isfinite([dot, na, nb]).all()
    cosine = float(np.clip(dot / (na * nb), -1, 1)) if finite and na > 0 and nb > 0 else None
    return dict(status="ok" if cosine is not None else "zero_or_nonfinite_gradient", cosine=cosine,
                conflict=bool(cosine < 0) if cosine is not None else None,
                norm_a=float(na) if np.isfinite(na) else None, norm_b=float(nb) if np.isfinite(nb) else None,
                shared_parameter_tensors=len(common), parameter_names=[name for name, _, _ in common])


def run_folder(root, tag):
    folder = Path(root) / f"{tag}_{time.time_ns()}_pid{os.getpid()}"
    folder.mkdir(parents=True, exist_ok=False)
    return folder


class CachedHeadMonitor:
    """Current QIVR trains only this head: no localization/matcher trajectory exists."""
    def __init__(self, model, dataset, folder, gradient_every=100):
        if any(p not in ("S+", "S-") for p in dataset.partitions):
            raise ValueError("Mechanism training monitor requires Seen-only training")
        self.model, self.dataset, self.folder = model, dataset, Path(folder)
        self.gradient_every, self.steps = max(1, gradient_every), 0
        self.previous = None
        self.parameter_names = [name for name, _ in model.named_parameters() if name.startswith(("slot_mlp.", "mlp."))]
        chosen = []
        # A fixed Seen-only cohort; no random draws and no dependency on test.
        for part in ("S+", "S-"):
            pool = [i for i, p in enumerate(dataset.partitions) if p == part]
            pool.sort(key=lambda i: hashlib.sha256(str(dataset.qids[i]).encode()).hexdigest())
            chosen.extend(pool[:32])
        self.indices = torch.tensor(chosen, dtype=torch.long, device=dataset.slot_hs.device)
        labels = dataset.exist_labels.detach().cpu().numpy()
        proxy = dataset.hungarian.detach().cpu().numpy()
        histogram = np.bincount(proxy[labels == 1], minlength=dataset.slot_hs.shape[1]).tolist()
        save_json(self.folder / "metadata.json", dict(
            training_kind="frozen_cached_representation_head", backbone_updated=False,
            true_hungarian_counts="unavailable: original extractor stored argmax max-GT-IoU, not Hungarian assignment",
            cached_max_iou_proxy_histogram=histogram, cached_match_proxy_changes="structurally constant",
            localization_vs_existence_gradient="not_applicable: no localization loss or shared trainable backbone",
            measured_gradient="evidence_BCE versus sample_existence_BCE on shared verifier parameters",
            gradient_every=self.gradient_every, probe_qids=[dataset.qids[i] for i in chosen],
            probe_scope="fixed Seen training cohort, eval mode; evidence winner changes are NOT Hungarian assignment changes"))

    def observe(self, epoch, slot_loss, sample_loss):
        self.steps += 1
        if (self.steps - 1) % self.gradient_every:
            return
        parameters = [(n, p) for n, p in self.model.named_parameters() if n in self.parameter_names]
        result = gradient_relation(slot_loss, sample_loss, parameters)
        append_json(self.folder / "gradients.jsonl", dict(epoch=int(epoch), step=self.steps,
            loss_pair="evidence_BCE_vs_sample_BCE", evidence_loss=float(slot_loss.detach()),
            sample_loss=float(sample_loss.detach()), **result))

    def end_epoch(self, epoch):
        mode = self.model.training
        self.model.eval()
        d, idx = self.dataset, self.indices
        try:
            with torch.no_grad():
                hs, roi, q = d.slot_hs[idx], d.slot_roi[idx], d.query_v[idx]
                slot_logits, sample_logits = self.model(hs, roi, q)
                evidence = slot_logits.sigmoid().cpu().numpy()
                sample = sample_logits.sigmoid().cpu().numpy()
                attention, global_residual = None, None
                if hasattr(self.model, "gate_mlp"):
                    qe = q[:, None].expand_as(hs)
                    attention = self.model.gate_mlp(torch.cat([hs, roi, qe], -1)).squeeze(-1).softmax(-1).cpu().numpy()
                    global_residual = self.model.global_context(torch.cat([hs.max(1).values, hs.mean(1), q], -1)).view(-1).cpu().numpy()
        finally:
            self.model.train(mode)
        # Tie sets, rather than first-index argmax, avoid artificial winner flips.
        winners = evidence == evidence.max(axis=1, keepdims=True)
        flips = None if self.previous is None else float(np.mean(np.any(winners != self.previous, axis=1)))
        self.previous = winners.copy()
        subset = np.array([d.partitions[i] for i in idx.cpu().tolist()])
        summaries = {}
        for p in ("S+", "S-"):
            mask = subset == p
            if not mask.any():
                continue
            entry = dict(n=int(mask.sum()), mean_evidence_by_slot=evidence[mask].mean(0).tolist(),
                fraction_evidence_gt05_by_slot=(evidence[mask] > .5).mean(0).tolist(),
                mean_sample_score=float(sample[mask].mean()))
            if attention is not None:
                entry["mean_attention_by_slot"] = attention[mask].mean(0).tolist()
                entry["mean_absolute_global_residual_logit"] = float(np.abs(global_residual[mask]).mean())
            summaries[p] = entry
        append_json(self.folder / "epochs.jsonl", dict(epoch=int(epoch),
            evidence_winner_set_change_rate=flips, true_assignment_change_rate=None, subsets=summaries))
        payload = dict(qids=np.array([d.qids[i] for i in idx.cpu().tolist()]), partitions=subset,
                       evidence=evidence, sample_scores=sample, winner_sets=winners)
        if attention is not None:
            payload.update(attention=attention, global_residual_logits=global_residual)
        np.savez_compressed(self.folder / f"seen_probe_epoch_{epoch:04d}.npz", **payload)

    def save_best(self, epoch, state, seen_auc):
        torch.save(dict(model=state, epoch=int(epoch), seen_validation_auc=float(seen_auc)), self.folder / "best_head.pt")
        save_json(self.folder / "selection.json", dict(epoch=int(epoch), seen_validation_auc=float(seen_auc),
            criterion="maximum Seen-validation AUROC; observer does not modify selection"))

    def freeze_final(self, dataset, slot_logits, sample_logits, threshold, validation_dataset):
        assert all(p in ("S+", "S-") for p in validation_dataset.partitions), "Calibration must use Seen validation only"
        def file_hash(path):
            digest = hashlib.sha256()
            with Path(path).open("rb") as stream:
                for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                    digest.update(chunk)
            return digest.hexdigest()
        sources = [Path(d.source_path) for d in (self.dataset, validation_dataset, dataset)]
        save_json(self.folder / "FROZEN_CALIBRATION.json", dict(existence_threshold=float(threshold),
            threshold_source="original Seen-validation balanced-accuracy calibration",
            checkpoint_sha256=file_hash(self.folder / "best_head.pt"),
            source_sha256={str(p): file_hash(p) for p in sources},
            test_usage="one final diagnostic after Seen selection; not used by the observer for selection"))
        np.savez_compressed(self.folder / "final_test_evidence.npz", qids=np.array(dataset.qids), vids=np.array(dataset.vids),
            partitions=np.array(dataset.partitions), labels=dataset.exist_labels.detach().cpu().numpy(),
            slot_evidence=slot_logits.detach().sigmoid().cpu().numpy(),
            scores=sample_logits.detach().sigmoid().cpu().numpy(), threshold=float(threshold))


def cached_monitor_from_env(model, dataset, tag):
    if os.environ.get("QIVR_MONITOR", "1") != "1":
        return None
    root = Path(__file__).resolve().parents[1] / "monitoring" / "runs"
    root = Path(os.environ.get("QIVR_MONITOR_DIR", str(root)))
    return CachedHeadMonitor(model, dataset, run_folder(root, tag), int(os.environ.get("QIVR_MONITOR_GRAD_EVERY", "100")))


class BackboneMonitor:
    """Captures actual final-layer matcher output, including every GT in each sample."""
    def __init__(self, model, criterion, folder, gradient_every=100):
        self.model, self.criterion, self.folder = model, criterion, Path(folder)
        self.gradient_every, self.steps = max(1, gradient_every), 0
        self.previous, self.current = {}, {}
        self.pending, self.indices = None, None
        self.hook = criterion.matcher.register_forward_hook(self._capture)
        save_json(self.folder / "metadata.json", dict(training_kind="joint_backbone", matcher="actual criterion.matcher output; first call is final layer; auxiliary calls excluded",
            gt_identity="qid + normalized GT cxw rounded to 7 decimals; duplicate GT coordinates excluded from flip calculation",
            flip_definition="same GT changes slot across consecutive observed epochs in actual stochastic training; not deterministic probe stability",
            gradient_basis="intersection of connected trainable transformer parameter gradients", gradient_every=self.gradient_every,
            localization_losses="weighted span + GIoU + foreground/background losses, including auxiliary decoder losses",
            existence_loss="weighted loss_exist; saliency excluded", unseen_labels_used=False,
            history_scope="starts when observer is enabled; no recovery of prior epochs"))

    def _capture(self, module, args, output):
        if self.pending is not None and self.indices is None:
            self.indices = [(i.detach().cpu(), j.detach().cpu()) for i, j in output]

    def begin_epoch(self, epoch):
        self.epoch, self.current = int(epoch), {}
        self.counts = None
        self.comparable, self.flips, self.duplicate_gt = 0, 0, 0

    def begin_batch(self, metadata):
        if any(row.get("partition", "S+").startswith("U") for row in metadata):
            raise ValueError("Backbone monitoring must not train on Unseen")
        self.pending, self.indices = metadata, None

    def observe(self, outputs, targets, loss_dict):
        if self.indices is None:
            raise RuntimeError("No actual matcher call captured")
        q = outputs["pred_spans"].shape[1]
        if self.counts is None:
            self.counts = np.zeros(q, dtype=np.int64)
        for row, target, (slots, gt_ids) in zip(self.pending, targets["span_labels"], self.indices):
            coordinates = [tuple(round(float(x), 7) for x in span) for span in target["spans"].detach().cpu()]
            duplicates = Counter(coordinates)
            for slot, gid in zip(slots.tolist(), gt_ids.tolist()):
                self.counts[slot] += 1
                coord = coordinates[gid]
                if duplicates[coord] > 1:
                    self.duplicate_gt += 1
                    continue
                key = json.dumps([str(row["qid"]), list(coord)], separators=(",", ":"))
                if key in self.previous and self.previous[key][0] == self.epoch - 1:
                    self.comparable += 1
                    self.flips += int(self.previous[key][1] != slot)
                self.current[key] = (self.epoch, slot)
        self.pending = None
        self.steps += 1
        if (self.steps - 1) % self.gradient_every:
            return
        losses = [v * self.criterion.weight_dict[k] for k, v in loss_dict.items()
                  if k.startswith(("loss_span", "loss_giou", "loss_label")) and k in self.criterion.weight_dict]
        existence = loss_dict.get("loss_exist")
        if existence is not None:
            existence = existence * self.criterion.weight_dict.get("loss_exist", 0)
        params = [(n, p) for n, p in self.model.named_parameters() if n.startswith("transformer.")]
        relation = gradient_relation(sum(losses) if losses else None, existence, params)
        append_json(self.folder / "gradients.jsonl", dict(epoch=self.epoch + 1, step=self.steps,
            loss_pair="localization_vs_existence", **relation))

    def end_epoch(self):
        append_json(self.folder / "epochs.jsonl", dict(epoch=self.epoch + 1,
            actual_gt_matches_by_slot=self.counts.tolist() if self.counts is not None else [],
            comparable_gt_observations=self.comparable, assignment_flips=self.flips,
            assignment_flip_rate=self.flips / self.comparable if self.comparable else None,
            duplicate_coordinate_gt_excluded=self.duplicate_gt))
        np.savez_compressed(self.folder / f"assignments_epoch_{self.epoch + 1:04d}.npz",
            gt_keys=np.array(list(self.current)), slots=np.array([v[1] for v in self.current.values()], dtype=np.int64))
        self.previous = self.current.copy()


def backbone_monitor_from_env(model, criterion, opt):
    if os.environ.get("QIVR_BACKBONE_MONITOR", "0") != "1":
        return None
    monitor = getattr(model, "_mechanism_observer", None)
    if monitor is None:
        root = os.environ.get("QIVR_MONITOR_DIR", str(Path(opt.results_dir) / "mechanism_monitor"))
        monitor = BackboneMonitor(model, criterion, run_folder(root, "backbone"), int(os.environ.get("QIVR_MONITOR_GRAD_EVERY", "100")))
        model._mechanism_observer = monitor
    return monitor
