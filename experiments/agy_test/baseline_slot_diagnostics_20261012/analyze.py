"""Frozen 33-setting candidate, localization, rejection and slot-index diagnostics."""
import argparse
import csv
import importlib.util
import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("registry", ROOT.parent / "training_free_auroc_20261012/common.py")
registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry)
N_BOOT, SEED = 2000, 3407


def read(path):
    return registry.rows(path)


def iou_matrix(a, b):
    a = np.asarray(a, dtype=float).reshape(-1, 2)
    b = np.asarray(b, dtype=float).reshape(-1, 2)
    inter = np.maximum(0, np.minimum(a[:, None, 1], b[None, :, 1]) - np.maximum(a[:, None, 0], b[None, :, 0]))
    union = (a[:, 1] - a[:, 0])[:, None] + (b[:, 1] - b[:, 0])[None, :] - inter
    return np.divide(inter, union, out=np.zeros_like(inter), where=union > 0)


def match_count(adjacency):
    """Maximum cardinality bipartite matching, not independent GT hits."""
    adjacency = np.asarray(adjacency, dtype=bool)
    owner = np.full(adjacency.shape[1], -1, dtype=int)
    def augment(candidate, visited):
        for gt in np.flatnonzero(adjacency[candidate]):
            if visited[gt]:
                continue
            visited[gt] = True
            if owner[gt] < 0 or augment(owner[gt], visited):
                owner[gt] = candidate
                return True
        return False
    return sum(augment(i, np.zeros(adjacency.shape[1], dtype=bool)) for i in range(len(adjacency)))


def valid_candidates(row):
    raw = np.array(row["pred_relevant_windows_pre_exist"], dtype=float).reshape(-1, 3)
    native = np.array(row["pred_relevant_windows"], dtype=float).reshape(-1, 3)
    assert raw.shape == native.shape and np.isfinite(raw).all() and np.isfinite(native).all()
    assert np.all(np.diff(raw[:, 2]) <= 1e-8), "Native ordering changed"
    # Native geometry includes clipping/rounding; foreground scores exclude the existence gate.
    paired = np.column_stack([native[:, :2], raw[:, 2]])
    return paired[paired[:, 1] > paired[:, 0]], raw, native


def query_features(row, gt, activity_reference):
    candidates, raw, native = valid_candidates(row)
    top = candidates[:10]
    p = np.maximum(top[:, 2], 0)
    features = dict(candidate_count=float(len(candidates)), invalid_fraction=float(1 - len(candidates) / max(len(raw), 1)))
    for key in ("foreground_top1", "foreground_mean5", "foreground_p2ratio", "high_abs_count", "high_rel_count", "high_seen90_count", "effective_n", "nms_distinct_count", "redundant_fraction", "anchor_cluster_mass"):
        features[key] = 0.0
    if len(top):
        features.update(foreground_top1=float(p[0]), foreground_mean5=float(p[:5].mean()),
            foreground_p2ratio=float(p[1] / p[0]) if len(p) > 1 and p[0] > 0 else 0.0,
            high_abs_count=float((p > 0.5).sum()), high_rel_count=float(((p >= 0.5 * p[0]) & (p > 0)).sum()),
            high_seen90_count=float((p > activity_reference).sum()),
            effective_n=float(p.sum() ** 2 / np.dot(p, p)) if np.dot(p, p) > 0 else 0.0)
        pairwise = iou_matrix(top[:, :2], top[:, :2])
        upper = pairwise[np.triu_indices(len(top), 1)]
        features["redundant_fraction"] = float((upper >= 0.5).mean()) if upper.size else 0.0
        kept = []
        for i in range(len(top)):
            if not kept or np.all(pairwise[i, kept] < 0.5):
                kept.append(i)
        features["nms_distinct_count"] = float(len(kept))
        features["anchor_cluster_mass"] = float(p[pairwise[0] >= 0.5].sum() / p.sum()) if p.sum() > 0 else 0.0
    positive_keys = ("top1_max_iou", "oracle5_iou", "oracle10_iou", "oracle_all_iou", "gt_recall10", "gt_recall_all", "active_gt_recall10", "relative_gt_recall10", "matched_prediction_fraction", "duplicate_matched_fraction", "local_candidate_auc", "best_match_rank")
    features.update({key: np.nan for key in positive_keys})
    if not len(gt):
        return features
    overlap = iou_matrix(candidates[:, :2], gt)
    best = overlap.max(axis=1) if len(candidates) else np.array([])
    n = len(gt)
    covered = best >= 0.5
    first = float(best[0]) if best.size else 0.0
    features.update(top1_max_iou=first, oracle5_iou=float(best[:5].max()) if best.size else 0.0,
        oracle10_iou=float(best[:10].max()) if best.size else 0.0,
        oracle_all_iou=float(best.max()) if best.size else 0.0,
        gt_recall10=match_count(overlap[:10] >= 0.5) / n,
        gt_recall_all=match_count(overlap >= 0.5) / n,
        active_gt_recall10=match_count(overlap[:10][p > 0.5] >= 0.5) / n,
        relative_gt_recall10=match_count(overlap[:10][(p >= 0.5 * p[0]) & (p > 0)] >= 0.5) / n if len(p) else 0.0,
        matched_prediction_fraction=float(covered[:10].mean()) if len(top) else 0.0,
        duplicate_matched_fraction=float((covered[:10].sum() - match_count(overlap[:10] >= 0.5)) / covered[:10].sum()) if covered[:10].any() else 0.0,
        best_match_rank=float(np.flatnonzero(covered)[0] + 1) if covered.any() else 0.0)
    y = covered[:10]
    if y.any() and (~y).any():
        positive_scores, negative_scores = p[y], p[~y]
        features["local_candidate_auc"] = float(((positive_scores[:, None] > negative_scores) + 0.5 * (positive_scores[:, None] == negative_scores)).mean())
    return features


def auc_draws(labels, scores, mask, row_weights):
    y, s = labels[mask], scores[mask]
    if len(np.unique(y)) != 2:
        return np.full(len(row_weights), np.nan)
    order = np.argsort(s, kind="stable")
    starts = np.r_[0, np.flatnonzero(np.diff(s[order])) + 1]
    w = row_weights[:, mask][:, order]
    yp = y[order]
    positive = np.add.reduceat(w * yp, starts, axis=1)
    negative = np.add.reduceat(w * (1 - yp), starts, axis=1)
    denominator = positive.sum(1) * negative.sum(1)
    numerator = (positive * (np.cumsum(negative, axis=1) - 0.5 * negative)).sum(1)
    return np.divide(100 * numerator, denominator, out=np.full(len(w), np.nan), where=denominator > 0)


def summarize_draws(values):
    finite = values[1:][np.isfinite(values[1:])]
    point = float(values[0]) if np.isfinite(values[0]) else None
    return dict(point=point, ci95=np.percentile(finite, [2.5, 97.5]).tolist() if len(finite) else None, valid_draws=int(len(finite)))


class Collector:
    def __init__(self, vids, video_universe, cluster_weights):
        self.vi = np.searchsorted(video_universe, vids)
        np.testing.assert_array_equal(video_universe[self.vi], vids)
        self.weights = np.vstack([np.ones(len(video_universe)), cluster_weights])
        self.draws, self.metadata = {}, {}

    def mean(self, name, values, mask, scale=1):
        values = np.asarray(values, dtype=float)
        mask = mask & np.isfinite(values)
        denominator = np.bincount(self.vi, weights=mask, minlength=self.weights.shape[1])
        numerator = np.bincount(self.vi, weights=np.where(mask, values, 0), minlength=self.weights.shape[1])
        d = self.weights @ denominator
        num = self.weights @ numerator
        self.draws[name] = np.divide(scale * num, d, out=np.full(len(d), np.nan), where=d > 0)
        self.metadata[name] = dict(n=int(mask.sum()), numerator=float(numerator.sum()), denominator=int(mask.sum()), scale=scale)

    def f1(self, name, labels, accept, mask):
        tn = np.bincount(self.vi, weights=mask & (labels == 0) & ~accept, minlength=self.weights.shape[1])
        fp = np.bincount(self.vi, weights=mask & (labels == 0) & accept, minlength=self.weights.shape[1])
        fn = np.bincount(self.vi, weights=mask & (labels == 1) & ~accept, minlength=self.weights.shape[1])
        denominator = self.weights @ (2 * tn + fp + fn)
        numerator = self.weights @ (200 * tn)
        self.draws[name] = np.divide(numerator, denominator, out=np.full(len(denominator), np.nan), where=denominator > 0)
        self.metadata[name] = dict(n=int(mask.sum()), tn=float(tn.sum()), fp=float(fp.sum()), fn=float(fn.sum()))


def slot_indices(dataset, split, bb, metadata, native_predictions, output_dir):
    if bb == "flash":
        return dict(applicable=False, reason="Anchor candidates; decoder slot indices do not exist")
    p = registry.paths(dataset, split, bb)
    source = p["output"] if bb == "qd" else ROOT / "slot_exports" / dataset / split / "moment"
    results, saved = {}, {}
    for part in ("val_seen", "test"):
        file = source / f"{part}.npz"
        if not file.exists():
            raise FileNotFoundError(file)
        data = np.load(file, allow_pickle=False)
        annotations = read(p["release"] / f"{part}.jsonl")
        np.testing.assert_array_equal(data["qids"], [str(row["qid"]) for row in annotations])
        predictions = native_predictions if part == "test" else {str(row["qid"]): row for row in read(p["validation"])}
        match_flags = np.zeros_like(data["fg"], dtype=bool)
        parity = 0.0
        for index, row in enumerate(annotations):
            pred = predictions[str(row["qid"])]
            _, raw, native = valid_candidates(pred)
            parity = max(parity, float(np.abs(-np.sort(-data["fg"][index]) - raw[:, 2]).max()))
            spans = data["spans"][index]
            xy = np.column_stack([spans[:, 0] - spans[:, 1] / 2, spans[:, 0] + spans[:, 1] / 2]) * row["duration"]
            if bb == "qd":
                xy = np.clip(xy, 0, row["duration"])
            cost = np.max(np.abs(xy[:, None, :] - raw[None, :, :2]), axis=-1)
            cost += np.abs(data["fg"][index, :, None] - raw[None, :, 2])
            ii, jj = linear_sum_assignment(cost)
            assert cost[ii, jj].max() < 0.003, (dataset, split, bb, part, row["qid"], cost[ii, jj].max())
            if row["relevant_windows"]:
                overlaps = iou_matrix(native[:, :2], row["relevant_windows"]).max(axis=1)
                match_flags[index, ii] = overlaps[jj] >= 0.5
        assert parity < 6e-5, parity
        partitions = np.array([row["partition"] for row in annotations])
        labels = np.array([row["exist_label"] for row in annotations])
        fg = data["fg"].astype(float)
        top_ties = fg == fg.max(axis=1, keepdims=True)
        top_shares = top_ties / top_ties.sum(axis=1, keepdims=True)
        current = {}
        for name, mask in {"S+": partitions == "S+", "S-": partitions == "S-", "U+": partitions == "U+", "U-": partitions == "U-"}.items():
            if not mask.any():
                continue
            mass = fg[mask].sum(axis=0)
            distribution = mass / mass.sum() if mass.sum() > 0 else np.zeros(fg.shape[1])
            counts = top_shares[mask].mean(axis=0)
            mean_scores = fg[mask].mean(axis=0)
            quality = match_flags[mask].mean(axis=0) if labels[mask].all() else None
            current[name] = dict(n=int(mask.sum()), mean_foreground_by_index=mean_scores.tolist(),
                exact_top_tie_pct=float(100 * (top_ties[mask].sum(axis=1) > 1).mean()),
                activation_gt05_by_index=(fg[mask] > 0.5).mean(axis=0).tolist(), top1_index_share=counts.tolist(),
                foreground_mass_effective_indices=float(1 / np.dot(distribution, distribution)) if np.dot(distribution, distribution) else None,
                top1_effective_indices=float(1 / np.dot(counts, counts)), top4_top1_share_pct=float(100 * np.sort(counts)[-4:].sum()),
                matched_gt_by_index=quality.tolist() if quality is not None else None,
                confidence_quality_spearman=float(spearmanr(mean_scores, quality).statistic) if quality is not None and np.std(quality) > 0 and np.std(mean_scores) > 0 else None)
        results[part] = dict(source=str(file), source_sha256=registry.sha(file), foreground_parity_max_abs=parity, subsets=current)
        saved[f"{part}_qids"] = data["qids"]
        saved[f"{part}_foreground"] = fg
        saved[f"{part}_slot_match_flags"] = match_flags
    np.savez_compressed(output_dir / "slot_indices.npz", **saved)
    return dict(applicable=True, decoder_slots=int(fg.shape[1]), fixed_checkpoint_only=True, **results)


def analyze_setting(dataset, split, bb, video_universe, cluster_weights, force=False):
    out = ROOT / "results" / dataset / split / bb
    out.mkdir(parents=True, exist_ok=True)
    if (out / "metrics.json").exists() and not force:
        return
    paths = registry.paths(dataset, split, bb)
    source_files = list((paths["task"] / "runs" / bb / "test").glob("*submission.jsonl"))
    assert len(source_files) == 1, source_files
    annotations = read(paths["release"] / "test.jsonl")
    native = read(source_files[0])
    predictions = {str(row["qid"]): row for row in native}
    qids = np.array([str(row["qid"]) for row in annotations])
    assert len(predictions) == len(native) == len(qids) == len(set(qids))
    assert set(qids) == set(predictions)
    baseline = dict(np.load(paths["baseline"], allow_pickle=False))
    for key, expected in (("qids", qids), ("vids", [row["vid"] for row in annotations]), ("labels", [row["exist_label"] for row in annotations]), ("partitions", [row["partition"] for row in annotations])):
        np.testing.assert_array_equal(baseline[key], expected)
    labels, partitions, vids = baseline["labels"], baseline["partitions"], baseline["vids"]
    scores, threshold = baseline["scores"].astype(float), float(baseline["threshold"])
    score_key = "pred_exist_logit" if bb == "flash" else "pred_exist_score"
    np.testing.assert_allclose(scores, [predictions[q][score_key] for q in qids], atol=6e-7 if bb == "flash" else 1e-7, rtol=0)
    val_annotations = read(paths["release"] / "val_seen.jsonl")
    assert all(row["partition"] in ("S+", "S-") for row in val_annotations)
    val_predictions = {str(row["qid"]): row for row in read(paths["validation"])}
    assert len(val_predictions) == len(val_annotations)
    negative_peaks = []
    for row in val_annotations:
        if not row["exist_label"]:
            candidate, _, _ = valid_candidates(val_predictions[str(row["qid"])])
            negative_peaks.append(float(candidate[0, 2]) if len(candidate) else 0)
    activity_reference = float(np.percentile(negative_peaks, 90))
    registry.save(out / "FROZEN_CALIBRATION.json", dict(original=json.loads((paths["baseline"].parent / "FROZEN_CALIBRATION.json").read_text()),
        existence_threshold=threshold, foreground_seen_negative_peak_p90=activity_reference,
        foreground_threshold_used_for_diagnostics_only=True, validation_sha256=registry.sha(paths["release"] / "val_seen.jsonl")))
    records = [query_features(predictions[str(row["qid"])], row["relevant_windows"], activity_reference) for row in annotations]
    features = {key: np.array([row[key] for row in records]) for key in records[0]}
    n_gt = np.array([len(row["relevant_windows"]) for row in annotations])
    assert np.array_equal(labels.astype(bool), n_gt > 0)
    np.testing.assert_allclose(features["top1_max_iou"][labels == 1] / n_gt[labels == 1], baseline["accept_iou"][labels == 1], atol=2e-6, rtol=0)
    accept = scores >= threshold
    correct = features["top1_max_iou"] >= 0.5
    covered = features["oracle10_iou"] >= 0.5
    gmiou = np.where(accept, baseline["accept_iou"], labels == 0)
    groups = {p: partitions == p for p in ("S+", "S-", "U+", "U-")}
    groups.update({f"{p}_accepted": (partitions == p) & accept for p in ("S-", "U-")})
    groups.update({f"{p}_rejected": (partitions == p) & ~accept for p in ("S+", "U+")})
    groups.update({f"{p}_correct_rejected": (partitions == p) & correct & ~accept for p in ("S+", "U+")})
    collect = Collector(vids, video_universe, cluster_weights)
    all_rows = np.ones(len(qids), dtype=bool)
    for prefix, mask in [("S", np.char.startswith(partitions, "S")), ("U", np.char.startswith(partitions, "U")), ("overall", all_rows)]:
        collect.f1(f"baseline/{prefix}_rej_f1", labels, accept, mask)
        collect.mean(f"baseline/{prefix}_gmiou1", gmiou, mask, 100)
        collect.mean(f"baseline/{prefix}_rr", ~accept, mask, 100)
    for p in ("S+", "U+"):
        collect.mean(f"baseline/{p}_frr", ~accept, groups[p], 100)
        collect.mean(f"localization/{p}_top1_r05", correct, groups[p], 100)
        collect.mean(f"localization/{p}_oracle10_r05", covered, groups[p], 100)
        collect.mean(f"localization/{p}_oracle_all_r05", features["oracle_all_iou"] >= 0.5, groups[p], 100)
        collect.mean(f"localization/{p}_gated_top1_r05", correct & accept, groups[p], 100)
        collect.mean(f"localization/{p}_gate_loss_pp", correct & ~accept, groups[p], 100)
        collect.mean(f"localization/{p}_correct_frr", ~accept, groups[p] & correct, 100)
        collect.mean(f"localization/{p}_covered_frr", ~accept, groups[p] & covered, 100)
        errors = {"no_candidate": ~covered, "ranking_failure": covered & ~correct,
                  "correct_but_rejected": correct & ~accept, "correct_and_accepted": correct & accept}
        assert np.all(sum(v[groups[p]].astype(int) for v in errors.values()) == 1)
        for name, value in errors.items():
            collect.mean(f"errors/{p}_{name}", value, groups[p], 100)
        for label, count_mask in (("1", n_gt == 1), ("2", n_gt == 2), ("3", n_gt == 3), ("4plus", n_gt >= 4)):
            mask = groups[p] & count_mask
            for name in ("high_abs_count", "high_rel_count", "effective_n", "nms_distinct_count", "gt_recall10", "gt_recall_all"):
                collect.mean(f"gt_count/{p}/{label}/{name}", features[name], mask, 100 if name.startswith("gt_recall") else 1)
    for group, mask in groups.items():
        for name, value in features.items():
            scale = 100 if name.endswith("fraction") or name.endswith("mass") or "recall" in name or name == "local_candidate_auc" else 1
            collect.mean(f"profiles/{group}/{name}", value, mask, scale)
        for name in ("abs", "rel", "seen90"):
            collect.mean(f"profiles/{group}/multi_high_{name}_pct", features[f"high_{name}_count"] >= 2, mask, 100)
        collect.mean(f"profiles/{group}/existence_score", scores, mask)
    row_weights = np.vstack([np.ones(len(qids)), cluster_weights[:, collect.vi]])
    probes = {"native_exist": scores, **{name: features[name] for name in ("foreground_top1", "foreground_mean5", "high_abs_count", "effective_n", "foreground_p2ratio")}}
    weighted_auc_checks = []
    for name, value in probes.items():
        for prefix in ("S", "U"):
            mask = np.char.startswith(partitions, prefix)
            draw = auc_draws(labels, value, mask, row_weights)
            collect.draws[f"auc/{name}/{prefix}"] = draw
            assert np.isclose(draw[0], 100 * roc_auc_score(labels[mask], value[mask])), (dataset, split, bb, name, prefix)
            for j in (1, 2, 3):
                active = mask & (row_weights[j] > 0)
                expected = 100 * roc_auc_score(labels[active], value[active], sample_weight=row_weights[j, active])
                weighted_auc_checks.append(abs(expected - draw[j]))
        collect.draws[f"auc/{name}/gap_pp"] = collect.draws[f"auc/{name}/S"] - collect.draws[f"auc/{name}/U"]
        if name != "native_exist":
            for prefix in ("S", "U", "gap_pp"):
                sign = -1 if prefix == "gap_pp" else 1
                collect.draws[f"probe_delta/{name}/{prefix}"] = sign * (collect.draws[f"auc/{name}/{prefix}"] - collect.draws[f"auc/native_exist/{prefix}"])
    for prefix, p in (("S", "S+"), ("U", "U+")):
        collect.draws[f"localization/{p}_existence_quality_auc"] = auc_draws(correct.astype(int), scores, groups[p], row_weights)
        for condition, flag in (("correct", correct), ("covered", covered)):
            mask = np.char.startswith(partitions, prefix) & ((labels == 0) | flag)
            collect.draws[f"conditional_auc/{prefix}_{condition}_positives_vs_negatives"] = auc_draws(labels, scores, mask, row_weights)
    for metric in ("rej_f1", "gmiou1"):
        collect.draws[f"baseline/{metric}_gap_pp"] = collect.draws[f"baseline/S_{metric}"] - collect.draws[f"baseline/U_{metric}"]
    counts = {p: dict(n=int(mask.sum()), videos=int(len(np.unique(vids[mask])))) for p, mask in groups.items()}
    counts["all"] = dict(n=len(qids), videos=len(np.unique(vids)), positives=int(labels.sum()), negatives=int((labels == 0).sum()))
    indices = slot_indices(dataset, split, bb, annotations, predictions, out)
    source_paths = [source_files[0], paths["baseline"], paths["release"] / "test.jsonl", paths["release"] / "val_seen.jsonl", paths["validation"], paths["frozen"] / "MANIFEST.json"]
    registry.save(out / "SOURCES.json", dict(dataset=dataset, split=split, backbone=bb,
        checkpoint=str(paths["checkpoint"]), frozen_checkpoint_manifest=json.loads((paths["frozen"] / "MANIFEST.json").read_text()),
        files={str(path): registry.sha(path) for path in source_paths}, protocol_sha256=registry.sha(ROOT / "PROTOCOL.json")))
    np.savez_compressed(out / "per_query.npz", **baseline, gt_window_count=n_gt, accepted=accept, top1_correct=correct, oracle10_covered=covered, **features)
    keys = list(collect.draws)
    np.savez_compressed(out / "bootstrap_draws.npz", keys=np.array(keys), draws=np.column_stack([collect.draws[key][1:] for key in keys]))
    registry.save(out / "metrics.json", dict(dataset=dataset, split=split, backbone=bb, counts=counts,
        metrics={key: dict(**summarize_draws(value), **collect.metadata.get(key, {})) for key, value in collect.draws.items()},
        slot_indices=indices, verification=dict(native_prediction_alignment=True, native_top1_iou_parity=True,
            weighted_auc_sklearn_max_abs_error=max(weighted_auc_checks), foreground_scores_before_existence_gate=True)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dataset", choices=list(registry.SPECS))
    args = parser.parse_args()
    records, status = [], []
    for dataset, (_, _, splits) in registry.SPECS.items():
        if args.dataset and dataset != args.dataset:
            continue
        all_vids = set()
        for split in splits:
            all_vids.update(row["vid"] for row in read(registry.paths(dataset, split, "moment")["release"] / "test.jsonl"))
        videos = np.array(sorted(all_vids))
        rng = np.random.RandomState(SEED)
        counts = np.array([np.bincount(rng.randint(len(videos), size=len(videos)), minlength=len(videos)) for _ in range(N_BOOT)])
        folder = ROOT / "bootstrap_clusters"
        folder.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(folder / f"{dataset}.npz", videos=videos, counts=counts, seed=SEED)
        for split in splits:
            for bb in registry.BACKBONES:
                start = time.time()
                analyze_setting(dataset, split, bb, videos, counts, args.force)
                current = json.loads((ROOT / "results" / dataset / split / bb / "metrics.json").read_text())
                records.append(current)
                status.append(dict(dataset=dataset, split=split, backbone=bb, complete=True, seconds=round(time.time() - start, 2)))
                expected = len(splits) * 3 if args.dataset else 33
                suffix = f"_{args.dataset}" if args.dataset else ""
                registry.save(ROOT / f"ANALYSIS_STATUS{suffix}.json", dict(complete=len(status) == expected, completed=len(status), expected=expected, settings=status))
                print(status[-1], flush=True)
    suffix = f"_{args.dataset}" if args.dataset else ""
    with (ROOT / f"ALL_METRICS{suffix}.csv").open("w") as stream:
        fields = ("dataset", "split", "backbone", "metric", "point", "ci_low", "ci_high", "n", "valid_draws")
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for record in records:
            for key, value in record["metrics"].items():
                ci = value["ci95"] or [None, None]
                writer.writerow({**{k: record[k] for k in ("dataset", "split", "backbone")}, "metric": key, "point": value["point"], "ci_low": ci[0], "ci_high": ci[1], "n": value.get("n"), "valid_draws": value["valid_draws"]})
    registry.save(ROOT / f"ALL_METRICS{suffix}.json", records)


if __name__ == "__main__":
    main()
