#!/usr/bin/env python3
"""Audit existing frozen-cache runs; compare paired candidate caches for SA ablations.

Does not train, regenerate caches, modify original results, or infer past gradients.
"""
import argparse
import csv
import importlib.util
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
REPO = Path('/home/guoxiangyu/paper/Openword/generalized-moment-retrieval')
sys.path.insert(0, str(ROOT / "src"))
from mechanism_monitor import save_json


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


diag = load_module("baseline_slot_diagnostics", REPO / "experiments/agy_test/baseline_slot_diagnostics_20261012/analyze.py")
registry = diag.registry


def status():
    processes = []
    for folder in Path("/proc").iterdir():
        if not folder.name.isdigit():
            continue
        try:
            args = (folder / "cmdline").read_bytes().decode(errors="replace").split("\0")
            cwd = str((folder / "cwd").resolve(strict=True))
        except (OSError, PermissionError):
            continue
        if args and "python" in Path(args[0]).name and ("qivr_gmr" in cwd or any("qivr_gmr" in a for a in args[1:])) and int(folder.name) != os.getpid():
            processes.append(dict(pid=int(folder.name), cwd=cwd, argv=args))
    return dict(observed_at=datetime.now().astimezone().isoformat(), processes=processes,
                note="A process snapshot, not a persistent background service")


def cache_features(records):
    qids = np.array([str(r["qid"]) for r in records])
    assert len(qids) == len(set(qids))
    features = dict(coverage=np.full(len(records), np.nan), gt_recall=np.full(len(records), np.nan),
                    top1_hit=np.full(len(records), np.nan), high_count=np.zeros(len(records)),
                    relative_count=np.zeros(len(records)))
    by_slot = np.zeros((len(records), len(records[0]["slot_scores"])), dtype=bool)
    for i, r in enumerate(records):
        score = np.asarray(r["slot_scores"])
        xy = np.asarray(r["slot_spans_sec"])
        valid = xy[:, 1] > xy[:, 0]
        features["high_count"][i] = ((score > .5) & valid).sum()
        features["relative_count"][i] = ((score >= .5 * score.max()) & (score > 0) & valid).sum()
        if r["gt_windows"]:
            overlaps = diag.iou_matrix(xy, r["gt_windows"])
            overlaps[~valid] = 0
            matches = overlaps >= .5
            by_slot[i] = matches.any(axis=1)
            features["coverage"][i] = float(matches.any())
            features["gt_recall"][i] = diag.match_count(matches) / len(r["gt_windows"])
            features["top1_hit"][i] = float(matches[int(np.argmax(score))].any())
            np.testing.assert_allclose(overlaps.max(axis=1), r["iou_with_gt"], atol=2e-6, rtol=0)
    return features, by_slot


def bootstrap(records, count=2000):
    vids = np.array([r["vid"] for r in records])
    universe = np.unique(vids)
    rng = np.random.RandomState(3407)
    weights = np.array([np.bincount(rng.randint(len(universe), size=len(universe)), minlength=len(universe)) for _ in range(count)])
    return vids, universe, weights


def summary(collector):
    return {key: dict(**diag.summarize_draws(values), **collector.metadata.get(key, {})) for key, values in collector.draws.items()}


def benchmark(collector, prefix, frozen):
    y, p, scores = frozen["labels"], frozen["partitions"], frozen["scores"].astype(float)
    accept = scores >= float(frozen["threshold"])
    gmiou = np.where(accept, frozen["accept_iou"], y == 0)
    row_weights = collector.weights[:, collector.vi]
    for subset in ("S", "U", "overall"):
        mask = np.ones(len(y), dtype=bool) if subset == "overall" else np.char.startswith(p, subset)
        collector.f1(f"{prefix}/{subset}/rej_f1", y, accept, mask)
        collector.mean(f"{prefix}/{subset}/gmiou1", gmiou, mask, 100)
        collector.mean(f"{prefix}/{subset}/rr", ~accept, mask, 100)
        if subset != "overall":
            collector.draws[f"{prefix}/{subset}/auroc"] = diag.auc_draws(y, scores, mask, row_weights)
    for part in ("S+", "U+"):
        collector.mean(f"{prefix}/{part}/frr", ~accept, p == part, 100)
    collector.mean(f"{prefix}/U-/false_acceptance", accept, p == "U-", 100)
    for metric in ("auroc", "rej_f1", "gmiou1"):
        collector.draws[f"{prefix}/gap/{metric}"] = collector.draws[f"{prefix}/S/{metric}"] - collector.draws[f"{prefix}/U/{metric}"]


def audit(output):
    output.mkdir(parents=True, exist_ok=True)
    records_out = []
    for train_file in sorted((ROOT / "cache").rglob("*train.pt")):
        bb = train_file.name.split("_")[0]
        legacy = train_file.parent == ROOT / "cache"
        dataset, split = ("soccer", "A1_soccer") if legacy else (train_file.parent.parent.name, train_file.parent.name)
        tag = f"{dataset}_{split}_{bb}"
        destination = output / tag
        destination.mkdir(exist_ok=True)
        train = torch.load(train_file, map_location="cpu", weights_only=False)
        assert all(r["partition"] in ("S+", "S-") for r in train)
        tiou = np.stack([r["iou_with_gt"] for r in train])
        positive = np.array([r["exist_label"] == 1 for r in train])
        proxy = np.array([r["hungarian_match_idx"] for r in train])
        np.testing.assert_array_equal(proxy[positive], tiou[positive].argmax(axis=1))
        train_stats = dict(rows=len(train), positives=int(positive.sum()), negatives=int((~positive).sum()),
            gt_windows=sum(len(r["gt_windows"]) for r in train), multi_gt_queries=sum(len(r["gt_windows"]) > 1 for r in train),
            max_iou_proxy_by_slot=np.bincount(proxy[positive], minlength=tiou.shape[1]).tolist(),
            high_iou_evidence_positives_by_slot=((tiou >= .5) & positive[:, None]).sum(0).tolist(),
            positive_queries_without_hit=int((positive & (tiou.max(axis=1) < .5)).sum()),
            positive_queries_fallback_overwritten_by_negative=int((positive & (tiou.max(axis=1) < .1)).sum()),
            actual_hungarian_history=None, assignment_flips=None,
            explanation="Cached index equals argmax(max IoU over GT), one index per query even when GT>1; not actual Hungarian. At maxIoU<0.1 the fallback positive is overwritten by the low-IoU negative rule.")
        del train
        test_file = train_file.with_name(f"{bb}_test.pt")
        test = torch.load(test_file, map_location="cpu", weights_only=False)
        features, matches = cache_features(test)
        vids, universe, weights = bootstrap(test)
        collect = diag.Collector(vids, universe, weights)
        parts = np.array([r["partition"] for r in test])
        for p in ("S+", "S-", "U+", "U-"):
            mask = parts == p
            for name in ("coverage", "gt_recall", "top1_hit"):
                collect.mean(f"cache/{p}/{name}", features[name], mask, 100)
            for name in ("high_count", "relative_count"):
                collect.mean(f"cache/{p}/{name}", features[name], mask)
            collect.mean(f"cache/{p}/multi_relative_pct", features["relative_count"] >= 2, mask, 100)
        pred_file = ROOT / "results" / bb / "hybrid_qivr/predictions.npz" if legacy else ROOT / "results" / dataset / split / bb / "predictions.npz"
        prediction = dict(np.load(pred_file, allow_pickle=False)) if pred_file.exists() else None
        baseline_file = registry.paths(dataset, split, bb)["baseline"]
        baseline = dict(np.load(baseline_file, allow_pickle=False))
        expected = dict(qids=[r["qid"] for r in test], vids=vids, labels=[r["exist_label"] for r in test], partitions=parts)
        for key, value in expected.items():
            np.testing.assert_array_equal(baseline[key], value)
            if prediction is not None:
                np.testing.assert_array_equal(prediction[key], value)
        benchmark(collect, "baseline", baseline)
        if prediction is not None:
            benchmark(collect, "qivr", prediction)
            accepted = prediction["scores"] >= float(prediction["threshold"])
            collect.mean("cache/U-_qivr_accepted/multi_relative_pct", features["relative_count"] >= 2, (parts == "U-") & accepted, 100)
            for metric in ("auroc", "rej_f1", "gmiou1"):
                for subset in ("S", "U", "gap"):
                    sign = -1 if subset == "gap" else 1
                    collect.draws[f"paired_change/{subset}/{metric}"] = sign * (collect.draws[f"qivr/{subset}/{metric}"] - collect.draws[f"baseline/{subset}/{metric}"])
        keys = list(collect.draws)
        np.savez_compressed(destination / "bootstrap.npz", keys=np.array(keys), draws=np.column_stack([collect.draws[k][1:] for k in keys]), videos=universe, cluster_counts=weights)
        np.savez_compressed(destination / "frozen_test_diagnostics.npz", **baseline, candidate_matches_gt=matches, **features)
        if prediction is not None:
            np.savez_compressed(destination / "qivr_frozen_predictions.npz", **prediction)
        count_info = {p: dict(n=int((parts == p).sum()), videos=int(len(np.unique(vids[parts == p])))) for p in ("S+", "S-", "U+", "U-")}
        report = dict(dataset=dataset, split=split, backbone=bb, train_cache=train_stats, counts=count_info, metrics=summary(collect),
            statuses=dict(localization_vs_existence_gradient="N/A: frozen representations, no localization loss", no_sa_effect="unavailable: current QIVR never removes backbone SA; no paired trained -SA checkpoint/cache"),
            sources={str(f): registry.sha(f) for f in (train_file, test_file, baseline_file) + ((pred_file,) if pred_file.exists() else ())},
            seed_note="Persisted predictions only. Legacy A1 is the saved single-run prediction, not the 3-seed mean in README.",
            bootstrap=dict(draws=2000, seed=3407, unit="target-video cluster; Soccer IDs denote clips"),
            frozen_threshold=float(prediction["threshold"]) if prediction is not None else None,
            calibration_provenance="Original source code selects on Seen validation; original runs did not persist head checkpoints or a complete calibration manifest. This audit cannot retroactively certify training history.")
        save_json(destination / "audit.json", report)
        records_out.append(report)
        print("Audited", tag, "fallback overwritten", train_stats["positive_queries_fallback_overwritten_by_negative"], flush=True)
    save_json(output / "AUDIT.json", dict(status=status(), settings=records_out, completed=len(records_out), new_training=False))
    with (output / "METRICS.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=("dataset", "split", "backbone", "metric", "point", "ci_low", "ci_high", "n"))
        writer.writeheader()
        for r in records_out:
            for key, value in r["metrics"].items():
                ci = value["ci95"] or [None, None]
                writer.writerow(dict(dataset=r["dataset"], split=r["split"], backbone=r["backbone"], metric=key,
                    point=value["point"], ci_low=ci[0], ci_high=ci[1], n=value.get("n")))
    write_report(output, records_out)


def write_report(output, records_out):
    lines = ["# Existing frozen-cache mechanism audit", "", "All eight settings are separate; no five-split macro is available. Current QIVR does not update DETR, perform Hungarian matching during head training, or remove self-attention. Historical matcher changes and localization/existence gradients cannot be recovered.", "",
        "| Dataset / split / backbone | Train positive queries | Train GT windows | IoU<0.1 fallback overwritten | U+ cache coverage % | U+ cache top1 hit % | QIVR U− false acceptance % |", "|---|---:|---:|---:|---:|---:|---:|"]
    for r in records_out:
        m, t = r["metrics"], r["train_cache"]
        fmt = lambda key: "N/A" if key not in m or m[key]["point"] is None else f"{m[key]['point']:.2f}"
        lines.append(f"| {r['dataset']} / {r['split']} / {r['backbone']} | {t['positives']} | {t['gt_windows']} | {t['positive_queries_fallback_overwritten_by_negative']} | {fmt('cache/U+/coverage')} | {fmt('cache/U+/top1_hit')} | {fmt('qivr/U-/false_acceptance')} |")
    lines += ["", "## Frozen benchmark metrics", "", "Percentages; signed Gap = Seen − Unseen. Rej-F1 and G-mIoU gaps depend on subset positive/negative proportions. All absolute/gap/paired intervals and counts are in METRICS.csv and each audit.json; bootstrap arrays and frozen prediction snapshots are retained.", "",
        "| Setting | Source | S AUROC | U AUROC | AUROC Gap | S Rej-F1 | U Rej-F1 | F1 Gap | S G-mIoU | U G-mIoU | G-mIoU Gap | Overall F1 / RR / G-mIoU | S+ / U+ FRR | S+ / S− / U+ / U− counts |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|"]
    for r in records_out:
        m = r["metrics"]
        for source in ("baseline", "qivr"):
            if f"{source}/S/auroc" not in m:
                continue
            keys = [f"{source}/{s}/{metric}" for metric in ("auroc", "rej_f1", "gmiou1") for s in ("S", "U", "gap")]
            values = [f"{m[k]['point']:.2f}" for k in keys]
            extra = [" / ".join(f"{m[f'{source}/{s}/{metric}']['point']:.2f}" for s, metric in pairs) for pairs in
                ((("overall", "rej_f1"), ("overall", "rr"), ("overall", "gmiou1")), (("S+", "frr"), ("U+", "frr")))]
            counts = " / ".join(str(r["counts"][p]["n"]) for p in ("S+", "S-", "U+", "U-"))
            lines.append("| " + " / ".join(r[k] for k in ("dataset", "split", "backbone")) + " | " + source + " | " + " | ".join(values + extra + [counts]) + " |")
    lines += ["", "## Paired baseline comparisons", "", "Changes in percentage points, with paired video-cluster bootstrap 95% CIs. Seen Change and Unseen Net Gain = QIVR − baseline; Gap Reduction = baseline gap − QIVR gap. Baseline relative changes are undefined.", "", "| Setting | Metric | Seen Change [95% CI] | Unseen Net Gain [95% CI] | Gap Reduction [95% CI] |", "|---|---|---|---|---|"]
    for r in records_out:
        for metric in ("auroc", "rej_f1", "gmiou1"):
            values = []
            for subset in ("S", "U", "gap"):
                value = r["metrics"].get(f"paired_change/{subset}/{metric}")
                if value is None or value["ci95"] is None:
                    values.append("N/A")
                else:
                    lo, hi = value["ci95"]
                    values.append(f"{value['point']:+.2f} [{lo:+.2f}, {hi:+.2f}]")
            lines.append("| " + " / ".join(r[k] for k in ("dataset", "split", "backbone")) + " | " + metric + " | " + " | ".join(values) + " |")
    (output / "AUDIT.md").write_text("\n".join(lines) + "\n")


def compare(reference_file, variant_file, output, reference_predictions=None, variant_predictions=None):
    """Paired geometry/response diagnostic, not evidence that -SA was trained."""
    reference = torch.load(reference_file, map_location="cpu", weights_only=False)
    variant_raw = torch.load(variant_file, map_location="cpu", weights_only=False)
    lookup = {r["qid"]: r for r in variant_raw}
    assert len(lookup) == len(variant_raw) == len(reference)
    assert set(lookup) == {r["qid"] for r in reference}
    variant = [lookup[r["qid"]] for r in reference]
    for a, b in zip(reference, variant):
        for key in ("vid", "partition", "exist_label", "gt_windows", "duration"):
            assert a[key] == b[key], (a["qid"], key)
        assert len(a["slot_scores"]) == len(b["slot_scores"]), "Use the same candidate budget"
    vids, universe, weights = bootstrap(reference)
    collector = diag.Collector(vids, universe, weights)
    parts = np.array([r["partition"] for r in reference])
    for label, records in (("reference", reference), ("variant", variant)):
        features, _ = cache_features(records)
        for part in ("S+", "S-", "U+", "U-"):
            mask = parts == part
            for key in ("coverage", "gt_recall", "top1_hit", "high_count", "relative_count"):
                collector.mean(f"{label}/{part}/{key}", features[key], mask, 100 if key in ("coverage", "gt_recall", "top1_hit") else 1)
    if reference_predictions is not None and variant_predictions is not None:
        for label, file in (("reference", reference_predictions), ("variant", variant_predictions)):
            frozen = dict(np.load(file, allow_pickle=False))
            lookup = {str(q): i for i, q in enumerate(frozen["qids"])}
            assert len(lookup) == len(reference) and set(lookup) == {str(r["qid"]) for r in reference}
            order = np.array([lookup[str(r["qid"])] for r in reference])
            for key, value in frozen.items():
                if value.ndim and len(value) == len(order):
                    frozen[key] = value[order]
            for key, expected in (("qids", [str(r["qid"]) for r in reference]), ("vids", vids),
                                  ("labels", [r["exist_label"] for r in reference]), ("partitions", parts)):
                np.testing.assert_array_equal(frozen[key], expected)
            benchmark(collector, label, frozen)
    for key in list(collector.draws):
        if key.startswith("reference/"):
            suffix = key[len("reference/"):]
            collector.draws[f"paired_change/{suffix}"] = collector.draws[f"variant/{suffix}"] - collector.draws[key]
            if suffix.startswith("gap/"):
                collector.draws[f"gap_reduction/{suffix[len('gap/'):]}"] = -collector.draws[f"paired_change/{suffix}"]
    output.mkdir(parents=True, exist_ok=True)
    save_json(output / "comparison.json", dict(metrics=summary(collector), reference_sha256=registry.sha(reference_file), variant_sha256=registry.sha(variant_file),
        frozen_prediction_sources={str(p): registry.sha(p) for p in (reference_predictions, variant_predictions) if p is not None},
        warning="Cache comparison alone does not certify a trained -SA intervention. Attach checkpoint/config/Seen-selection manifests; inference-only SA disabling is a distribution shift diagnostic, not a trained ablation. U− activity is not an actual false-acceptance rate; benchmark false-acceptance rates are computed only when both frozen prediction files are supplied."))
    keys = list(collector.draws)
    np.savez_compressed(output / "bootstrap.npz", keys=np.array(keys), draws=np.column_stack([collector.draws[k][1:] for k in keys]), videos=universe, cluster_counts=weights)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("status", "audit", "compare-caches"))
    parser.add_argument("--output", type=Path, default=ROOT / "monitoring" / "audit_20261012")
    parser.add_argument("--reference-cache", type=Path)
    parser.add_argument("--variant-cache", type=Path)
    parser.add_argument("--reference-predictions", type=Path)
    parser.add_argument("--variant-predictions", type=Path)
    args = parser.parse_args()
    if args.mode == "status":
        print(json.dumps(status(), ensure_ascii=False, indent=2))
    elif args.mode == "audit":
        audit(args.output)
    else:
        if args.reference_cache is None or args.variant_cache is None:
            parser.error("compare-caches requires --reference-cache and --variant-cache")
        if (args.reference_predictions is None) != (args.variant_predictions is None):
            parser.error("Supply both prediction files, or neither")
        compare(args.reference_cache, args.variant_cache, args.output, args.reference_predictions, args.variant_predictions)
