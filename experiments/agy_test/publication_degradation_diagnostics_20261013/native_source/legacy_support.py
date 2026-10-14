#!/usr/bin/env python3
"""Native baseline Seen-only training with complete decoder-slot instrumentation."""
import argparse
import copy
import csv
import hashlib
import importlib
import json
import random
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import legacy_metrics as diagnostics
from mechanism_monitor import BackboneMonitor, append_json, save_json
from decoder_slot_monitor import DecoderSlotMonitor
from auroc_mechanism_monitor import AUROCMechanismMonitor, final_ranking_bootstrap, annotate_lengths, ObjectiveSplitMonitor
from response_monitor import ResponseMonitor, ParameterUpdateMonitor, frozen_records, training_records, summarize, save_records


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


@contextmanager
def preserve_rng():
    state = (random.getstate(), np.random.get_state(), torch.get_rng_state(), torch.cuda.get_rng_state_all())
    try:
        yield
    finally:
        random.setstate(state[0])
        np.random.set_state(state[1])
        torch.set_rng_state(state[2])
        torch.cuda.set_rng_state_all(state[3])


def stable_subset(dataset, per_partition):
    result = copy.copy(dataset)
    rows = []
    for partition in sorted({r["partition"] for r in dataset.data}):
        pool = [r for r in dataset.data if r["partition"] == partition]
        pool.sort(key=lambda r: hashlib.sha256(str(r["qid"]).encode()).hexdigest())
        rows.extend(pool[:per_partition])
    result.data = rows
    if hasattr(dataset,"preloaded_data"):
        lookup={str(meta["qid"]):(meta,inputs) for meta,inputs in dataset.preloaded_data}
        result.preloaded_data=[lookup[str(row["qid"])] for row in rows]
    return result


def make_dataset(paths, opt, module, name, labels):
    clip, slowfast = diagnostics.registry.video_dirs(paths["dataset"])
    filename = paths["release"] / f"{name}.jsonl"
    source = diagnostics.registry.rows(filename)
    # Fail before native dataset loading can silently skip and log missing data.
    for row in source:
        assert row["exist_label"] == int(bool(row["relevant_windows"]))
        stem = module.video_id_to_feature_stem(row["vid"])
        for file in (clip / f"{stem}.npz", slowfast / f"{stem}.npz", paths["text"] / f"qid{row['qid']}.npz"):
            if not file.exists():
                raise FileNotFoundError(file)
    if name in ("train", "val_seen"):
        assert all(r["partition"] in ("S+", "S-") for r in source)
    dataset = module.StartEndDataset(dset_name=opt.dset_name, domain=None, data_path=str(filename),
        v_feat_dirs=[str(clip), str(slowfast)], q_feat_dir=str(paths["text"]),
        ctx_mode=opt.ctx_mode, v_feat_types=opt.v_feat_types,
        max_q_l=opt.max_q_l, max_v_l=opt.max_v_l, max_a_l=opt.max_a_l,
        clip_len=opt.clip_length, max_windows=opt.max_windows, span_loss_type=opt.span_loss_type,
        load_labels=labels, mr_only=True, keep_empty_gt=True)
    assert len(dataset) == len(source)
    return dataset


def loader(dataset, module, batch_size, workers, shuffle=False, seed=3407):
    return DataLoader(dataset, batch_size=batch_size, num_workers=workers, shuffle=shuffle,
        collate_fn=module.start_end_collate, generator=torch.Generator().manual_seed(seed), pin_memory=True)


def loss_terms(criterion, losses, prefixes):
    values = [value * criterion.weight_dict[key] for key, value in losses.items()
              if key.startswith(prefixes) and key in criterion.weight_dict]
    return sum(values) if values else None


class RepresentationMonitor:
    """Capture the parent hs tensor actually shared by span/class/existence heads.

    outputs['hs'] is a separate view and is not an ancestor of the span loss.
    The transformer's first forward returns the common ancestor; QD's negative
    saliency forward is deliberately ignored.
    """
    def __init__(self, model, criterion, output):
        self.criterion, self.output, self.hs = criterion, output, None
        self.handle = model.transformer.register_forward_hook(self.capture)

    def capture(self, module, inputs, outputs):
        if self.hs is None:
            self.hs = outputs[0]

    def begin_batch(self):
        self.hs = None

    def observe(self, epoch, step, losses, metadata):
        terms = dict(localization=loss_terms(self.criterion, losses, ("loss_span", "loss_giou")),
                     slot_classification=loss_terms(self.criterion, losses, ("loss_label",)),
                     evidence=loss_terms(self.criterion, losses, ("loss_evidence",)),
                     existence=loss_terms(self.criterion, losses, ("loss_exist",)))
        gradients = {}
        for name, loss in terms.items():
            grad = torch.autograd.grad(loss, self.hs, retain_graph=True, allow_unused=True)[0] if torch.is_tensor(loss) and loss.requires_grad else None
            gradients[name] = None if grad is None else grad[-1].detach().double()
        labels = np.array([r["partition"] for r in metadata])
        for name in ("localization", "slot_classification", "evidence"):
            if terms[name] is None:
                continue
            for subset in ("all", "S+", "S-"):
                mask = np.ones(len(labels), dtype=bool) if subset == "all" else labels == subset
                if not mask.any():
                    continue
                a, b = gradients[name], gradients["existence"]
                row = dict(epoch=epoch, step=step, loss_pair=f"{name}_vs_existence", subset=subset, n=int(mask.sum()),
                    representation="final decoder layer hs; weighted losses; sample/slot/feature inner product")
                if a is None or b is None:
                    row.update(cosine=None, conflict=None, status="disconnected")
                else:
                    a, b = a[mask], b[mask]
                    dot = (a * b).sum().item()
                    na, nb = a.square().sum().sqrt().item(), b.square().sum().sqrt().item()
                    cosine = float(np.clip(dot / (na * nb), -1, 1)) if na > 0 and nb > 0 else None
                    row.update(cosine=cosine, conflict=cosine < 0 if cosine is not None else None,
                        status="ok" if cosine is not None else "zero_gradient", norm_a=na, norm_b=nb,
                        norm_a_by_slot=a.square().sum((0, 2)).sqrt().cpu().tolist(),
                        norm_b_by_slot=b.square().sum((0, 2)).sqrt().cpu().tolist())
                    qa, qb = a.square().sum((1, 2)).sqrt(), b.square().sum((1, 2)).sqrt()
                    valid = (qa > 0) & (qb > 0)
                    qc = ((a * b).sum((1, 2))[valid] / (qa[valid] * qb[valid])).clamp(-1, 1)
                    row.update(valid_queries=int(valid.sum()), mean_query_cosine=float(qc.mean()) if len(qc) else None,
                        query_conflict_fraction=float((qc < 0).double().mean()) if len(qc) else None)
                append_json(self.output / "representation_gradients.jsonl", row)


@torch.no_grad()
def fixed_probe(model, criterion, dataset, module, opt, output, epoch, previous, response_monitor=None, decoder_monitor=None, auroc_monitor=None):
    model.eval()
    assignment, counts = {}, np.zeros(opt.num_queries, dtype=np.int64)
    responses = []
    mechanism_rows = []
    with preserve_rng():
        for probe_batch, (metadata, batch) in enumerate(loader(dataset, module, opt.eval_bsz, 0), 1):
            if decoder_monitor is not None:
                decoder_monitor.begin("probe", epoch, 0, probe_batch)
            if auroc_monitor is not None: auroc_monitor.begin("probe",epoch,0,probe_batch)
            inputs, targets = module.prepare_batch_inputs(batch, opt.device)
            outputs = model(**inputs)
            indices = criterion.matcher(outputs, targets)
            if auroc_monitor is not None: mechanism_rows.extend(auroc_monitor.observe(outputs,metadata,inputs,indices,targets=targets))
            if decoder_monitor is not None:
                decoder_monitor.observe(outputs, targets, metadata, inputs, indices)
            if response_monitor is not None:
                responses.extend(training_records(outputs, targets, metadata, indices))
            for meta, target, (slots, ids) in zip(metadata, targets["span_labels"], indices):
                coords = [tuple(round(float(v), 7) for v in span) for span in target["spans"].cpu()]
                for slot, gid in zip(slots.tolist(), ids.tolist()):
                    counts[slot] += 1
                    if coords.count(coords[gid]) == 1:
                        key = json.dumps([str(meta["qid"]), coords[gid]], separators=(",", ":"))
                        assignment[key] = slot
    common = sorted(set(previous or {}) & set(assignment))
    flips = sum(previous[key] != assignment[key] for key in common) if previous is not None else 0
    append_json(output / "fixed_probe.jsonl", dict(epoch=epoch, n_queries=len(dataset), actual_gt_matches_by_slot=counts.tolist(),
        comparable_gt=len(common), flips=flips, flip_rate=flips / len(common) if common else None,
        scope="fixed Seen training cohort, eval mode; epoch 0 is pre-continuation"))
    np.savez_compressed(output / f"fixed_probe_epoch_{epoch:04d}.npz", gt_keys=np.array(list(assignment)), slots=np.array(list(assignment.values())))
    if response_monitor is not None:
        response_monitor.probe(epoch, responses)
    if auroc_monitor is not None: auroc_monitor.finish("probe",epoch,mechanism_rows)
    return assignment


@torch.no_grad()
def predict(model, dataset, module, opt, workers, with_candidates=False, auroc_monitor=None, phase="validation", epoch=0):
    model.eval()
    rows, candidate_rows, mechanism_rows = [], [], []
    with preserve_rng():
        for batch_index,(metadata, batch) in enumerate(loader(dataset, module, opt.eval_bsz, workers),1):
            if auroc_monitor is not None: auroc_monitor.begin(phase,epoch,0,batch_index)
            batch_geometry=[]
            inputs, _ = module.prepare_batch_inputs(batch, opt.device)
            outputs = model(**inputs)
            probs = outputs["pred_exist_logits"].sigmoid().cpu().numpy()
            foreground = outputs["pred_logits"].softmax(-1)[..., 0].cpu().numpy()
            cxw = outputs["pred_spans"].cpu().numpy()
            for i, meta in enumerate(metadata):
                xx = np.stack([cxw[i, :, 0] - .5 * cxw[i, :, 1], cxw[i, :, 0] + .5 * cxw[i, :, 1]], -1)
                # Native QD clips to duration; native Moment clips only to the configured global cap.
                sec = xx * meta["duration"]
                if getattr(opt, "native_clip_to_duration", True):
                    sec = np.clip(sec, 0, meta["duration"])
                sec = np.array([[float(f"{v:.4f}") for v in span] for span in sec], dtype=np.float32)
                sec = np.round(np.clip(sec, 0, float(getattr(opt, "max_ts_val", 150) or 150)) / opt.clip_length) * opt.clip_length
                scores = np.round(foreground[i], 4)
                ranked = sorted(range(len(scores)), key=lambda j: -foreground[i, j])
                valid_ranked = [j for j in ranked if sec[j, 1] > sec[j, 0]]
                gt = meta["relevant_windows"]
                overlaps = diagnostics.diag.iou_matrix(sec, gt) if gt else np.zeros((len(sec), 0))
                # Native top-1 set IoU divides its best overlap by number of GTs.
                # Native evaluator removes invalid spans before selecting top-1.
                accept_iou = float(overlaps[valid_ranked[0]].max() / len(gt)) if gt and valid_ranked else float(not gt and not valid_ranked)
                rows.append(dict(qid=str(meta["qid"]), vid=str(meta["vid"]), partition=meta["partition"],
                    label=int(meta["exist_label"]), score=float(np.round(probs[i], 4)), accept_iou=accept_iou, logit=float(outputs["pred_exist_logits"][i]), probability=float(probs[i])))
                if with_candidates or auroc_monitor is not None:
                    candidate_rows.append(dict(qid=str(meta["qid"]), vid=str(meta["vid"]), partition=meta["partition"],
                        exist_label=int(meta["exist_label"]), duration=meta["duration"], gt_windows=gt,
                        slot_spans_sec=sec.astype(np.float32), slot_scores=foreground[i].astype(np.float32),
                        iou_with_gt=overlaps.max(1).astype(np.float32) if gt else np.zeros(len(scores), np.float32)))
                    batch_geometry.append(candidate_rows[-1])
                    if 'pred_evidence_logits' in outputs:
                        candidate_rows[-1]['slot_evidence'] = outputs['pred_evidence_logits'][i].sigmoid().cpu().numpy()
            if auroc_monitor is not None: mechanism_rows.extend(auroc_monitor.observe(outputs,metadata,inputs,geometry=batch_geometry))
    if auroc_monitor is not None: auroc_monitor.finish(phase,epoch,mechanism_rows)
    frozen = dict(qids=np.array([r["qid"] for r in rows]), vids=np.array([r["vid"] for r in rows]),
        partitions=np.array([r["partition"] for r in rows]), labels=np.array([r["label"] for r in rows]),
        exist_logits=np.array([r["logit"] for r in rows]), exist_probabilities=np.array([r["probability"] for r in rows]), scores=np.array([r["score"] for r in rows]), accept_iou=np.array([r["accept_iou"] for r in rows]))
    return frozen, candidate_rows


def calibrate(frozen):
    assert set(frozen["partitions"]) <= {"S+", "S-"}
    y, scores = frozen["labels"], frozen["scores"]
    best = (-1., .5)
    for threshold in np.percentile(scores, np.linspace(5, 95, 91)):
        accept = scores >= threshold
        ba = .5 * (accept[y == 1].mean() + (~accept[y == 0]).mean())
        if ba > best[0]:
            best = (float(ba), float(threshold))
    return best[1]


def check_initial_validation(paths, initial, validation, output):
    original = {str(r["qid"]):r for r in diagnostics.registry.rows(paths["validation"])}
    annotations = {str(r["qid"]):r for r in validation.data}
    scores, ious = [], []
    for qid in initial["qids"]:
        row, gt = original[qid], annotations[qid]["relevant_windows"]
        valid = [w for w in row["pred_relevant_windows"] if w[1] > w[0]]
        scores.append(row["pred_exist_score"])
        ious.append(float(diagnostics.diag.iou_matrix([valid[0][:2]], gt).max() / len(gt)) if gt and valid else float(not gt and not valid))
    score_delta = float(np.abs(initial["scores"] - scores).max())
    iou_delta = float(np.abs(initial["accept_iou"] - ious).max())
    save_json(output / "INITIAL_BASELINE_PARITY.json", dict(score_max_absolute_difference=score_delta,
        set_iou_max_absolute_difference=iou_delta, validation_rows=len(scores),
        tolerance=dict(score=2e-4, set_iou=1e-6), source=str(paths["validation"])))
    assert score_delta <= 2e-4 and iou_delta <= 1e-6, "Initial +SA validation does not reproduce frozen baseline; investigate before training"


def metric_report(output, baseline, frozen, candidates, draws):
    for key in ("qids", "vids", "labels", "partitions"):
        np.testing.assert_array_equal(baseline[key], frozen[key])
    vids, universe, weights = diagnostics.bootstrap(candidates, draws)
    collector = diagnostics.diag.Collector(vids, universe, weights)
    diagnostics.benchmark(collector, "baseline", baseline)
    diagnostics.benchmark(collector, "experiment", frozen)
    features, matches = diagnostics.cache_features(candidates)
    for part in ("S+", "S-", "U+", "U-"):
        mask = frozen["partitions"] == part
        for key, values in features.items():
            collector.mean(f"candidates/{part}/{key}", values, mask, 100 if key in ("coverage", "gt_recall", "top1_hit") else 1)
    for metric in ("auroc", "rej_f1", "gmiou1"):
        for subset, name, sign in (("S", "seen_change", 1), ("U", "unseen_net_gain", 1), ("gap", "gap_reduction", -1)):
            collector.draws[f"comparison/{name}/{metric}"] = sign * (collector.draws[f"experiment/{subset}/{metric}"] - collector.draws[f"baseline/{subset}/{metric}"])
    metrics = diagnostics.summary(collector)
    counts = {p: int((frozen["partitions"] == p).sum()) for p in ("S+", "S-", "U+", "U-")}
    save_json(output / "metrics.json", dict(metrics=metrics, counts=counts, bootstrap_draws=draws, bootstrap_seed=3407,
        unit="target video cluster (Soccer IDs are clips)", limitation="Rej-F1 and G-mIoU gaps depend on subset prevalence; partial splits, no macro average"))
    keys = list(collector.draws)
    np.savez_compressed(output / "bootstrap.npz", keys=np.array(keys), draws=np.column_stack([collector.draws[k][1:] for k in keys]), videos=universe, cluster_counts=weights)
    np.savez_compressed(output / "candidate_diagnostics.npz", qids=frozen["qids"], matches_gt=matches, **features)
    with (output / "metrics.csv").open("w") as stream:
        writer = csv.writer(stream)
        writer.writerow(["metric", "point", "ci_low", "ci_high", "valid_draws"])
        for key, value in metrics.items():
            writer.writerow([key, value["point"], *(value["ci95"] or [None, None]), value["valid_draws"]])
    lines = ["# Frozen final evaluation", "", f"Counts: {counts}. Video-cluster bootstrap: {draws}; seed 3407. All checkpoints/thresholds use Seen validation only.", "", "| Metric (%) or change (pp) | Point | 95% CI |", "|---|---:|---|"]
    for key, value in metrics.items():
        point, ci = value["point"], value["ci95"]
        lines.append(f"| {key} | {point:.3f} | [{ci[0]:.3f}, {ci[1]:.3f}] |" if point is not None and ci else f"| {key} | undefined | undefined |")
    lines += ["", "Signed Gap = Seen − Unseen; negative gaps are retained. Rej-F1/G-mIoU depend on subset class proportions. Native baseline replication and initialization are recorded in CONFIG.json. Comparisons against historical predictions measure replication differences, not QIVR or a new-method gain. Baseline relative changes are undefined. No full five-split macro is available."]
    (output / "METRICS.md").write_text("\n".join(lines) + "\n")
