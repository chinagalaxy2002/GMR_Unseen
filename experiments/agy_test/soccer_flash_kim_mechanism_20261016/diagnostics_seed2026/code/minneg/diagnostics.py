"""Read-only diagnostics adapted from diagnostics/detr-native-26ep-20261014.

No value produced here is used by a loss, checkpoint selection, or threshold
selection.  The Flash A3 path uses native mean pooling and its replacement
EventReadout ignores that pooled vector, so max-pool ownership is explicitly
labelled counterfactual unless ``exist_pool == 'max'``.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F


REFERENCE_COMMIT = "349becb99cdfba2b23630af9126af0a532506113"


def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(path)


def append_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + "\n")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def describe(values):
    x = np.asarray(values, dtype=float); x = x[np.isfinite(x)]
    if not len(x):
        return {"n": 0, "mean": None}
    return {"n": int(len(x)), "mean": float(x.mean()), "std": float(x.std()),
            "min": float(x.min()), "q05": float(np.quantile(x, .05)),
            "median": float(np.median(x)), "q95": float(np.quantile(x, .95)),
            "max": float(x.max())}


def overlap_matrix(a, b):
    a = np.asarray(a, float).reshape(-1, 2); b = np.asarray(b, float).reshape(-1, 2)
    if not len(a) or not len(b):
        return np.zeros((len(a), len(b)))
    inter = np.maximum(0, np.minimum(a[:, None, 1], b[None, :, 1]) - np.maximum(a[:, None, 0], b[None, :, 0]))
    union = (a[:, 1] - a[:, 0])[:, None] + (b[:, 1] - b[:, 0])[None, :] - inter
    return np.divide(inter, union, out=np.zeros_like(inter), where=union > 0)


def auc_pairs(pos, neg):
    pos, neg = np.asarray(pos), np.sort(np.asarray(neg))
    if not len(pos) or not len(neg): return None
    lo, hi = np.searchsorted(neg, pos, "left"), np.searchsorted(neg, pos, "right")
    return {"auroc": float(np.mean((lo + hi) * .5 / len(neg))),
            "strict_error_fraction": float(np.mean((len(neg) - hi) / len(neg))),
            "tie_fraction": float(np.mean((hi - lo) / len(neg))),
            "pairs": int(len(pos) * len(neg))}


def score_report(rows):
    labels = np.asarray([r["label"] for r in rows], bool)
    result = {"count": len(rows), "subsets": {}, "same_video": {}}
    for key in ("logit", "raw_probability", "score"):
        values = np.asarray([r[key] for r in rows], float)
        result["subsets"][key] = {
            "ranking": auc_pairs(values[labels], values[~labels]),
            "positive_quantiles": np.quantile(values[labels], [0, .05, .25, .5, .75, .95, 1]).tolist(),
            "negative_quantiles": np.quantile(values[~labels], [0, .05, .25, .5, .75, .95, 1]).tolist(),
            "unique_scores": int(len(np.unique(values))),
        }
    by_video = {}
    for row in rows: by_video.setdefault(row["vid"], []).append(row)
    values, weights = [], []
    for group in by_video.values():
        p = [r["logit"] for r in group if r["label"]]
        n = [r["logit"] for r in group if not r["label"]]
        item = auc_pairs(p, n)
        if item: values.append(item["auroc"]); weights.append(item["pairs"])
    result["same_video"] = {"videos_with_both_classes": len(values),
        "macro_auroc": float(np.mean(values)) if values else None,
        "pair_weighted_auroc": float(np.average(values, weights=weights)) if values else None}
    positives = sorted((r for r in rows if r["label"]), key=lambda r: r["logit"])[:10]
    negatives = sorted((r for r in rows if not r["label"]), key=lambda r: -r["logit"])[:10]
    result["worst_pairs"] = [{"margin": float(a["logit"] - b["logit"]),
        "positive_qid": a["qid"], "negative_qid": b["qid"], "same_video": a["vid"] == b["vid"]}
        for _, a, b in sorted(((a["logit"] - b["logit"], a, b) for a in positives for b in negatives),
                              key=lambda item: item[0])[:20]]
    return result


def response_rows(predictions, ground_truth):
    lookup = {str(p["qid"]): p for p in predictions}; rows = []
    for gt in ground_truth:
        pred = lookup[str(gt["qid"])]
        windows = np.asarray([w[:2] for w in pred.get("pred_relevant_windows_pre_exist", [])], float).reshape(-1, 2)
        truth = np.asarray(gt.get("relevant_windows", []), float).reshape(-1, 2)
        iou = overlap_matrix(windows, truth)
        rows.append({"qid": str(gt["qid"]), "vid": str(gt["vid"]), "label": int(bool(len(truth))),
            "gt_count": int(len(truth)), "existence_logit": float(pred["pred_exist_logit_raw"]),
            "existence_score": float(pred["pred_exist_score"]),
            "existence_bce": float(np.logaddexp(0, pred["pred_exist_logit_raw"]) - bool(len(truth)) * pred["pred_exist_logit_raw"]),
            "top1_iou": float(iou[0].max()) if iou.size else (0.0 if len(truth) else math.nan),
            "oracle_iou": float(iou.max()) if iou.size else (0.0 if len(truth) else math.nan),
            "top1_hit": bool(iou.size and iou[0].max() >= .5), "oracle_hit": bool(iou.size and iou.max() >= .5),
            "duration": float(gt.get("duration", 0.0))})
    return rows


def summarize_rows(rows):
    answer = {}
    for label, name in ((1, "S+"), (0, "S-")):
        group = [r for r in rows if r["label"] == label]
        keys = ("existence_logit", "existence_score", "existence_bce", "gt_count", "top1_iou", "oracle_iou", "top1_hit", "oracle_hit", "duration")
        answer[name] = {"n": len(group), "metrics": {k: describe([r[k] for r in group]) for k in keys}}
    return answer


def pool_provenance(internals, predictions, ground_truth, clip_length, native_pool):
    summaries, arrays = [], {"qid": [], "pool_source_slot": [], "pool_tie_count": [],
                             "owner_overlaps_gt": [], "owner_center_in_gt": []}
    for internal, pred, gt in zip(internals, predictions, ground_truth):
        units = np.asarray(internal["video_units"], np.float32)
        valid = np.asarray(internal["video_valid"], bool)
        original = np.flatnonzero(valid); h = units[valid]
        if not len(h): continue
        owner_local = h.argmax(0); owner = original[owner_local]
        selected = h[owner_local, np.arange(h.shape[1])]
        ties = (h == selected[None, :]).sum(0)
        duration = float(gt.get("duration", len(valid) * clip_length))
        spans = np.stack([original * clip_length, np.minimum((original + 1) * clip_length, duration)], 1)
        truth = np.asarray(gt.get("relevant_windows", []), float).reshape(-1, 2)
        overlap = overlap_matrix(spans, truth)
        any_overlap = overlap.max(1) > 0 if overlap.size else np.zeros(len(spans), bool)
        centers = spans.mean(1)
        center_hit = np.asarray([any(a <= c <= b for a, b in truth) for c in centers], bool)
        best = int(np.argmax(overlap.max(1))) if overlap.size else -1
        owner_overlap = any_overlap[owner_local]; owner_center = center_hit[owner_local]
        dimension = int(h.shape[1])
        ranked = np.asarray([w[:2] for w in pred.get("pred_relevant_windows_pre_exist", [])[:3]], float).reshape(-1, 2)
        ranked_iou = overlap_matrix(ranked, truth)
        ranked_hit = ranked_iou.max(1) >= .5 if ranked_iou.size else np.zeros(len(ranked), bool)
        slot_centers = spans.mean(1); topk = {}
        attention = np.asarray(internal.get("video_attention", []), np.float32)
        if attention.ndim == 2:
            attention = attention[:, valid]
        for k in (1, 2, 3):
            hit_windows = ranked[:k][ranked_hit[:k]]
            covered = np.asarray([any(a <= center <= b for a, b in hit_windows) for center in slot_centers], bool)
            owned = covered[owner_local] if len(covered) else np.zeros(dimension, bool)
            topk[f"top{k}_gt_hit"] = bool(ranked_hit[:k].any())
            topk[f"top{k}_gt_hit_pool_dimensions"] = int(owned.sum())
            topk[f"top{k}_gt_hit_pool_fraction"] = float(owned.mean())
            if attention.size:
                per_layer = attention[:, covered].sum(1) if covered.any() else np.zeros(attention.shape[0])
                topk[f"top{k}_gt_hit_attention_mass_by_layer"] = per_layer.tolist()
                topk[f"top{k}_gt_hit_attention_mass_mean"] = float(per_layer.mean())
                topk[f"top{k}_gt_hit_attention_mass_final"] = float(per_layer[-1])
            else:
                topk[f"top{k}_gt_hit_attention_mass_by_layer"] = []
                topk[f"top{k}_gt_hit_attention_mass_mean"] = None
                topk[f"top{k}_gt_hit_attention_mass_final"] = None
        probability = float(pred.get("pred_exist_score", 0.0))
        summaries.append({"qid": str(gt["qid"]), "vid": str(gt["vid"]), "label": int(bool(len(truth))),
            "dimension_count": dimension, "native_pooling": native_pool,
            "max_pool_role": "actual" if native_pool == "max" else "counterfactual_diagnostic_only",
            "actual_a3_mechanism": "sequential_cross_attention_readout",
            "argmax_gt_overlap_dimensions": int(owner_overlap.sum()),
            "argmax_gt_overlap_fraction": float(owner_overlap.mean()),
            "argmax_center_in_gt_dimensions": int(owner_center.sum()),
            "argmax_center_in_gt_fraction": float(owner_center.mean()),
            "best_gt_overlap_slot": int(original[best]) if best >= 0 else None,
            "best_gt_overlap_slot_dimensions": int((owner_local == best).sum()) if best >= 0 else 0,
            "best_gt_overlap_slot_fraction": float((owner_local == best).mean()) if best >= 0 else 0.0,
            "tied_dimensions": int((ties > 1).sum()), "valid_temporal_slots": int(len(h)),
            "existence_score": probability, "false_reject_at_0.4": bool(len(truth) and probability < .4),
            "false_reject_at_0.5": bool(len(truth) and probability < .5), **topk})
        arrays["qid"].append(str(gt["qid"])); arrays["pool_source_slot"].append(owner.astype(np.int32))
        arrays["pool_tie_count"].append(ties.astype(np.int16)); arrays["owner_overlaps_gt"].append(owner_overlap)
        arrays["owner_center_in_gt"].append(owner_center)
    return summaries, {k: np.asarray(v) for k, v in arrays.items()}


@torch.no_grad()
def add_a3_interventions(rows, internals, predictions, ground_truth, model, clip_length):
    """Paired causal readout interventions. They never re-run or alter localization."""
    device = next(model.parameters()).device
    head = model.base.exist_head
    for index, (row, internal, pred, gt) in enumerate(zip(rows, internals, predictions, ground_truth)):
        text = torch.as_tensor(internal["text_memory"], device=device).unsqueeze(0)
        text_valid = torch.as_tensor(internal["text_valid"], device=device).bool().unsqueeze(0)
        memories = torch.as_tensor(internal["video_memories"], device=device).unsqueeze(0)
        valid_np = np.asarray(internal["video_valid"], bool)
        valid = torch.as_tensor(valid_np, device=device).bool().unsqueeze(0)
        video = [memories[:, layer] for layer in range(memories.shape[1])]
        replay, _ = head.diagnostic_replay(text, text_valid, video, valid)
        row["actual_readout_replay_logit"] = float(replay[0])
        row["actual_readout_replay_abs_error"] = abs(float(replay[0]) - float(pred["pred_exist_logit_raw"]))
        original = np.flatnonzero(valid_np)
        duration = float(gt.get("duration", len(valid_np) * clip_length))
        spans = np.stack([original * clip_length, np.minimum((original + 1) * clip_length, duration)], 1)
        truth = np.asarray(gt.get("relevant_windows", []), float).reshape(-1, 2)
        ranked = np.asarray([w[:2] for w in pred.get("pred_relevant_windows_pre_exist", [])[:3]], float).reshape(-1, 2)
        riou = overlap_matrix(ranked, truth); hit = riou.max(1) >= .5 if riou.size else np.zeros(len(ranked), bool)
        centers = spans.mean(1)
        for k in (1, 2, 3):
            hit_windows = ranked[:k][hit[:k]]
            covered_local = np.asarray([any(a <= c <= b for a, b in hit_windows) for c in centers], bool)
            covered = np.zeros(len(valid_np), bool); covered[original] = covered_local
            remove = valid_np & ~covered
            only = valid_np & covered
            if not remove.any() or not only.any():
                row[f"top{k}_actual_remove_hit_logit"] = None
                row[f"top{k}_actual_remove_hit_logit_drop"] = None
                row[f"top{k}_actual_only_hit_logit"] = None
                continue
            removed, _ = head.diagnostic_replay(text, text_valid, video, torch.as_tensor(remove, device=device).unsqueeze(0))
            isolated, _ = head.diagnostic_replay(text, text_valid, video, torch.as_tensor(only, device=device).unsqueeze(0))
            row[f"top{k}_actual_remove_hit_logit"] = float(removed[0])
            row[f"top{k}_actual_remove_hit_logit_drop"] = float(replay[0] - removed[0])
            row[f"top{k}_actual_only_hit_logit"] = float(isolated[0])
        other = internals[(index + 1) % len(internals)]
        other_text = torch.as_tensor(other["text_memory"], device=device).unsqueeze(0)
        other_valid = torch.as_tensor(other["text_valid"], device=device).bool().unsqueeze(0)
        mismatch, _ = head.diagnostic_replay(other_text, other_valid, video, valid)
        row["actual_mismatched_text_logit"] = float(mismatch[0])
        row["actual_mismatched_text_logit_drop"] = float(replay[0] - mismatch[0])
    return rows


def gradient_relation(a, b, named_parameters):
    params = [(n, p) for n, p in named_parameters if p.requires_grad]
    ga = torch.autograd.grad(a, [p for _, p in params], retain_graph=True, allow_unused=True)
    gb = torch.autograd.grad(b, [p for _, p in params], retain_graph=True, allow_unused=True)
    pairs = [(n, x.detach().float(), y.detach().float()) for (n, _), x, y in zip(params, ga, gb) if x is not None and y is not None]
    if not pairs: return {"status": "no_shared_connected_parameters"}
    dot = sum(float((x * y).sum()) for _, x, y in pairs)
    na = math.sqrt(sum(float(x.square().sum()) for _, x, _ in pairs)); nb = math.sqrt(sum(float(y.square().sum()) for _, _, y in pairs))
    cosine = dot / max(na * nb, 1e-30)
    return {"status": "ok", "cosine": cosine, "conflict": cosine < 0, "norm_a": na, "norm_b": nb,
            "shared_parameter_tensors": len(pairs), "parameter_names": [n for n, _, _ in pairs]}


class DiagnosticsRecorder:
    def __init__(self, run, model, opt, job):
        self.run, self.model, self.opt, self.job = Path(run), model, opt, job
        self.monitor = self.run / "monitor"; self.auroc = self.monitor / "auroc_mechanisms"
        self.pool = self.auroc / "pool_sources"; self.selection = self.run / "selection"
        for folder in (self.monitor, self.auroc, self.pool, self.selection, self.monitor / "decoder_slots"):
            folder.mkdir(parents=True, exist_ok=True)
        self.before = None
        write_json(self.monitor / "metadata.json", {"reference_branch_commit": REFERENCE_COMMIT,
            "training_kind": "frozen Flash localizer plus trainable EventReadout", "gradient_every": 50,
            "history_scope": "clean rerun from epoch 1", "unseen_labels_used_for_selection": False,
            "localizer": "bitwise immutable and fingerprinted each epoch"})
        write_json(self.auroc / "METADATA.json", {"version": 3, "training_interval": 50,
            "optimization": "every native training step", "scores": "full validation every epoch",
            "pooling_provenance": "actual final Flash temporal units; exact argmax and ties",
            "native_pooling": getattr(opt, "exist_pool", "mean"),
            "max_pool_status": "actual" if getattr(opt, "exist_pool", "mean") == "max" else "counterfactual_diagnostic_only",
            "selection": "Val AUROC only; Test inaccessible until frozen"})
        write_json(self.monitor / "decoder_slots" / "METADATA.json", {"status": "not_applicable",
            "reason": "FlashVTG has temporal pyramid units, not DETR decoder/Hungarian slots",
            "replacement": "auroc_mechanisms/pool_sources plus readout_states.jsonl"})
        write_json(self.run / "DIAGNOSTIC_COVERAGE.json", {"reference_commit": REFERENCE_COMMIT,
            "covered": ["optimization", "objective_split", "existence_loss_contributions", "shared_gradients",
                "parameter_updates", "representation_gradients", "train/probe/validation responses",
                "full validation score reports", "fixed probe", "selection trace", "pool provenance",
                "raw compressed arrays", "CUDA memory", "RNG-resumable checkpoints"],
            "architecture_not_applicable": ["Hungarian assignment flips", "DETR decoder-slot self/cross attention"],
            "replacement": ["frozen localizer fingerprint", "Flash temporal-unit max-pool ownership", "EventReadout state statistics"]})

    def start_epoch(self, epoch):
        self.before = {n: p.detach().cpu().clone() for n, p in self.model.named_parameters()}

    def batch(self, epoch, step, output, details, negative, metadata, targets, norm, lr):
        if step != 1 and (step - 1) % 50 != 0:
            return
        labels = targets["exist_label"].detach().float().reshape(-1)
        logits = output["pred_exist_logits"].detach().reshape(-1)
        per = F.binary_cross_entropy_with_logits(logits, labels, reduction="none").cpu().numpy()
        record = {"epoch": epoch, "step": step, "losses": {k: float(v.detach()) for k, v in details.items()},
            "preclip_global_norm": float(norm), "clip_threshold": float(self.job["grad_clip"]),
            "clip_coefficient": min(1.0, float(self.job["grad_clip"]) / max(float(norm), 1e-30)), "lr": float(lr)}
        if torch.cuda.is_available():
            record["cuda"] = {"allocated": torch.cuda.memory_allocated(), "reserved": torch.cuda.memory_reserved(),
                              "max_allocated": torch.cuda.max_memory_allocated()}
        append_json(self.auroc / "optimization.jsonl", record)
        split = {}
        for flag, name in ((True, "S+"), (False, "S-")):
            mask = labels.cpu().numpy().astype(bool) == flag
            split[name] = {"n": int(mask.sum()), "existence_bce_mean": float(per[mask].mean()) if mask.any() else None,
                           "existence_bce_sum_over_batch": float(per[mask].sum() / len(per)) if mask.any() else 0.0}
            append_json(self.auroc / "existence_loss_contributions.jsonl", {"epoch": epoch, "step": step,
                "subset": name, **split[name]})
        append_json(self.auroc / "objective_split.jsonl", {"epoch": epoch, "step": step, "subsets": split,
            "hard_negative_loss": float(negative.detach()) if negative is not None else None,
            "hard_negative_status": "enabled" if negative is not None else "disabled_control",
            "plurality_loss": float(details.get("loss_multi", torch.tensor(float("nan"))).detach())})
        if step == 1 or (step - 1) % 50 == 0:
            main = details.get("loss_exist", details["loss_total"])
            relation = (gradient_relation(main, negative, self.model.named_parameters()) if negative is not None
                        else {"status": "not_applicable_hard_negative_disabled"})
            append_json(self.monitor / "gradients.jsonl", {"epoch": epoch, "step": step,
                "loss_pair": "existence_vs_hard_negative", **relation})
            append_json(self.auroc / "shared_gradients.jsonl", {"epoch": epoch, "step": step,
                "pair": "existence/hard_negative", **relation})
            # Stage logits are on the exact loss path.  The stacked hidden-state
            # snapshot is a sibling tensor and therefore is not differentiably
            # connected to the already-computed loss node.
            states = output.get("pred_stage_logits")
            grad = torch.autograd.grad(main, states, retain_graph=True, allow_unused=True)[0] if states is not None else None
            append_json(self.monitor / "representation_gradients.jsonl", {"epoch": epoch, "step": step,
                    "representation": "EventReadout per-stage existence logits", "status": "ok" if grad is not None else "not_connected",
                "norm": float(grad.detach().float().norm()) if grad is not None else None})
            rows = []
            probs = logits.sigmoid().cpu().numpy(); labs = labels.cpu().numpy().astype(int)
            for i, meta in enumerate(metadata):
                rows.append({"qid": str(meta["qid"]), "vid": str(meta["vid"]), "label": int(labs[i]),
                    "logit": float(logits[i]), "raw_probability": float(probs[i]), "score": float(round(float(probs[i]), 4)),
                    "gt_count": len(meta.get("relevant_windows", [])), "duration": float(meta.get("duration", 0))})
            for label, part in ((1, "S+"), (0, "S-")):
                group = [r for r in rows if r["label"] == label]
                append_json(self.auroc / "train_query_summary.jsonl", {"epoch": epoch, "step": step,
                    "partition": part, "n": len(group), "statistics": {k: describe([r[k] for r in group]) for k in ("logit", "raw_probability", "gt_count", "duration")}})
            if states is not None:
                s = states.detach().float()
                append_json(self.monitor / "readout_states.jsonl", {"epoch": epoch, "step": step,
                    "shape": list(s.shape), "l2": float(s.norm()), "mean": float(s.mean()), "std": float(s.std())})

    def finish_epoch(self, epoch, predictions, ground_truth, internals, report, score, best, improved, stale):
        modules = {}
        for name, parameter in self.model.named_parameters():
            root = name.split(".")[0] if not name.startswith("base.exist_head") else "exist_head"
            old = self.before[name]; new = parameter.detach().cpu(); delta = (new - old).double()
            item = modules.setdefault(root, {"parameters": 0, "update_sq": 0., "base_sq": 0., "max_abs_update": 0., "changed": False})
            item["parameters"] += parameter.numel(); item["update_sq"] += float(delta.square().sum()); item["base_sq"] += float(old.double().square().sum())
            item["max_abs_update"] = max(item["max_abs_update"], float(delta.abs().max())); item["changed"] |= bool(torch.any(delta != 0))
        for item in modules.values():
            item["update_l2"] = math.sqrt(item.pop("update_sq")); item["relative_update_l2"] = item["update_l2"] / max(math.sqrt(item.pop("base_sq")), 1e-30)
        append_json(self.monitor / "parameter_updates.jsonl", {"epoch": epoch, "modules": modules})
        rows = response_rows(predictions, ground_truth)
        summary = summarize_rows(rows)
        append_json(self.monitor / "validation_responses.jsonl", {"epoch": epoch, "threshold_usage": "0.5 descriptive only", "subsets": summary})
        append_json(self.monitor / "probe_responses.jsonl", {"epoch": epoch, "scope": "fixed first 128 validation queries", "subsets": summarize_rows(rows[:128])})
        score_rows = [{"qid": r["qid"], "vid": r["vid"], "label": r["label"], "logit": r["existence_logit"],
                       "raw_probability": r["existence_score"], "score": round(r["existence_score"], 4)} for r in rows]
        write_json(self.auroc / f"validation_epoch_{epoch:04d}_scores.json", score_report(score_rows))
        write_json(self.auroc / f"probe_epoch_{epoch:04d}_scores.json", score_report(score_rows[:128]))
        for label, part in ((1, "S+"), (0, "S-")):
            group = [r for r in score_rows if r["label"] == label]
            append_json(self.auroc / "validation_query_summary.jsonl", {"epoch": epoch, "partition": part, "n": len(group),
                "statistics": {k: describe([r[k] for r in group]) for k in ("logit", "raw_probability", "score")}})
        pool_rows, arrays = pool_provenance(internals, predictions, ground_truth, self.opt.clip_length, getattr(self.opt, "exist_pool", "mean"))
        pool_rows = add_a3_interventions(pool_rows, internals, predictions, ground_truth, self.model, self.opt.clip_length)
        epoch_dir = self.pool / "validation" / f"epoch_{epoch:04d}"; epoch_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(epoch_dir / "pool_provenance.npz", **arrays)
        write_json(epoch_dir / "summary.json", {"epoch": epoch, "positive_queries": int(sum(r["label"] for r in pool_rows)),
            "argmax_gt_overlap_fraction": describe([r["argmax_gt_overlap_fraction"] for r in pool_rows if r["label"]]),
            "argmax_center_in_gt_fraction": describe([r["argmax_center_in_gt_fraction"] for r in pool_rows if r["label"]]),
            "best_gt_overlap_slot_fraction": describe([r["best_gt_overlap_slot_fraction"] for r in pool_rows if r["label"]]),
            "topk_hit_pool_fraction": {str(k): describe([r[f"top{k}_gt_hit_pool_fraction"] for r in pool_rows if r[f"top{k}_gt_hit"]]) for k in (1, 2, 3)},
            "topk_hit_actual_attention_mass_final": {str(k): describe([r[f"top{k}_gt_hit_attention_mass_final"] for r in pool_rows if r[f"top{k}_gt_hit"]]) for k in (1, 2, 3)},
            "topk_hit_false_reject_actual_attention_mass_final_at_0.5": {str(k): describe([r[f"top{k}_gt_hit_attention_mass_final"] for r in pool_rows if r[f"top{k}_gt_hit"] and r["false_reject_at_0.5"]]) for k in (1, 2, 3)},
            "topk_hit_actual_remove_hit_logit_drop": {str(k): describe([r[f"top{k}_actual_remove_hit_logit_drop"] for r in pool_rows if r[f"top{k}_gt_hit"]]) for k in (1, 2, 3)},
            "topk_hit_false_reject_actual_remove_hit_logit_drop_at_0.5": {str(k): describe([r[f"top{k}_actual_remove_hit_logit_drop"] for r in pool_rows if r[f"top{k}_gt_hit"] and r["false_reject_at_0.5"]]) for k in (1, 2, 3)},
            "topk_hit_false_reject_pool_fraction_at_0.5": {str(k): describe([r[f"top{k}_gt_hit_pool_fraction"] for r in pool_rows if r[f"top{k}_gt_hit"] and r["false_reject_at_0.5"]]) for k in (1, 2, 3)},
            "per_query": pool_rows})
        append_json(self.monitor / "fixed_probe.jsonl", {"epoch": epoch, "n_queries": min(128, len(rows)),
            "AUROC": score_report(score_rows[:128])["subsets"]["logit"]["ranking"]})
        append_json(self.monitor / "epochs.jsonl", {"epoch": epoch, "val_AUROC": score,
            "native_mAP": report["native_pre_nms"]["MR-full-mAP"], "localizer_matches_e0": report["localizer_matches_e0"]})
        append_json(self.selection / "trace.jsonl", {"epoch": epoch, "score": score, "previous_best": best,
            "improved": improved, "stale": stale, "metric": "AUROC", "selection_data": "Val only",
            "role": "diagnostic_initialization_probe" if epoch == 0 else "formal_selection"})
        if improved and epoch > 0:
            write_json(self.selection / "selected.json", {"epoch": epoch, "score": score, "metric": "AUROC", "status": "training_provisional"})
            write_json(self.selection / "auroc_shadow.json", {"epoch": epoch, "auroc": score, "role": "formal_selection"})

    def freeze(self, checkpoint, epoch, score):
        write_json(self.selection / "frozen.json", {"epoch": epoch, "score": score, "metric": "Val AUROC",
            "checkpoint_sha256": sha256(checkpoint), "test_started": False})


def save_final_diagnostics(run, predictions, ground_truth, internals, epoch, clip_length, native_pool, model):
    run = Path(run); final = run / "final"; auroc = final / "monitor" / "auroc_mechanisms"
    rows = response_rows(predictions, ground_truth); score_rows = [{"qid": r["qid"], "vid": r["vid"], "label": r["label"],
        "logit": r["existence_logit"], "raw_probability": r["existence_score"], "score": round(r["existence_score"], 4)} for r in rows]
    write_json(auroc / f"test_epoch_{epoch:04d}_scores.json", score_report(score_rows))
    write_json(final / "test_responses.json", {"epoch": epoch, "subsets": summarize_rows(rows)})
    pool_rows, arrays = pool_provenance(internals, predictions, ground_truth, clip_length, native_pool)
    pool_rows = add_a3_interventions(pool_rows, internals, predictions, ground_truth, model, clip_length)
    folder = auroc / "pool_sources" / "test" / f"epoch_{epoch:04d}"; folder.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(folder / "pool_provenance.npz", **arrays)
    write_json(folder / "summary.json", {"epoch": epoch,
        "argmax_gt_overlap_fraction": describe([r["argmax_gt_overlap_fraction"] for r in pool_rows if r["label"]]),
        "argmax_center_in_gt_fraction": describe([r["argmax_center_in_gt_fraction"] for r in pool_rows if r["label"]]),
        "best_gt_overlap_slot_fraction": describe([r["best_gt_overlap_slot_fraction"] for r in pool_rows if r["label"]]),
        "topk_hit_pool_fraction": {str(k): describe([r[f"top{k}_gt_hit_pool_fraction"] for r in pool_rows if r[f"top{k}_gt_hit"]]) for k in (1, 2, 3)},
        "topk_hit_actual_attention_mass_final": {str(k): describe([r[f"top{k}_gt_hit_attention_mass_final"] for r in pool_rows if r[f"top{k}_gt_hit"]]) for k in (1, 2, 3)},
        "topk_hit_false_reject_actual_attention_mass_final_at_0.5": {str(k): describe([r[f"top{k}_gt_hit_attention_mass_final"] for r in pool_rows if r[f"top{k}_gt_hit"] and r["false_reject_at_0.5"]]) for k in (1, 2, 3)},
        "topk_hit_actual_remove_hit_logit_drop": {str(k): describe([r[f"top{k}_actual_remove_hit_logit_drop"] for r in pool_rows if r[f"top{k}_gt_hit"]]) for k in (1, 2, 3)},
        "topk_hit_false_reject_actual_remove_hit_logit_drop_at_0.5": {str(k): describe([r[f"top{k}_actual_remove_hit_logit_drop"] for r in pool_rows if r[f"top{k}_gt_hit"] and r["false_reject_at_0.5"]]) for k in (1, 2, 3)},
        "topk_hit_false_reject_pool_fraction_at_0.5": {str(k): describe([r[f"top{k}_gt_hit_pool_fraction"] for r in pool_rows if r[f"top{k}_gt_hit"] and r["false_reject_at_0.5"]]) for k in (1, 2, 3)},
        "per_query": pool_rows})
