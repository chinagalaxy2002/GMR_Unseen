#!/usr/bin/env python3
"""Launch isolated two-GPU mechanism runs; refresh live and final reports."""
import argparse
import csv
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from mechanism_monitor import save_json


def read_json(path, default=None):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def rows(path):
    if not path.exists():
        return []
    result = []
    for line in path.read_text().splitlines():
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            pass  # Last JSONL line may be in flight.
    return result


def last_row(path):
    try:
        with path.open("rb") as stream:
            stream.seek(0, 2)
            size = stream.tell()
            stream.seek(max(0, size - 262144))
            lines = stream.read().splitlines()
        for line in reversed(lines):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    except OSError:
        pass
    return {}


def choose_job(pending, running, gpu):
    """Prefer different datasets and backbones on each GPU, then globally."""
    local = [r for r in running if r.get("gpu") == gpu]
    def priority(job):
        return (100 * sum(job["dataset"] != r["dataset"] for r in local)
                + 80 * sum(job["backbone"] != r["backbone"] for r in local)
                + 10 * sum(job["dataset"] != r["dataset"] for r in running)
                + 8 * sum(job["backbone"] != r["backbone"] for r in running))
    return max(range(len(pending)), key=lambda i:(priority(pending[i]), -i))


def live_report(output):
    manifest = read_json(output / "SUITE.json")
    status = read_json(output / "STATUS.json", {})
    lines = ["# Mechanism experiment live monitor", "", "Seen-only training, single seed; initialization and duration are frozen in SUITE.json. Incomplete runs are not scientific results. Training flips include stochasticity; fixed probes run in eval mode. Negative gradient cosines are descriptive measurements, not significance tests.", "", "| Job | State / epoch / batch | PID | Last training GT matches by slot | Train flip % | Fixed-probe flip % | Pure loc/exist cosine (valid samples) |", "|---|---|---:|---|---:|---:|---|"]
    snapshot = []
    response_lines = ["# Positive localization / positive existence / negative existence during training", "", "Training measurements only; active = valid span and foreground probability >0.5. Fixed eval probes are saved separately. Existence score is per query, not per slot.", "", "| Job | Epoch / step | S+ matched IoU | S+ localization L1 | S+ existence score | S− existence score | S+ / S− foreground slots | S+ / S− evidence slots |", "|---|---|---:|---:|---:|---:|---|---|"]
    for job in manifest["jobs"]:
        folder = output / job["tag"]
        state = read_json(folder / "STATUS.json", {})
        parent = status.get("jobs", {}).get(job["tag"], {})
        training = rows(folder / "monitor/epochs.jsonl")
        fixed = rows(folder / "monitor/fixed_probe.jsonl")
        gradients = [r for r in rows(folder / "monitor/representation_gradients.jsonl")
            if r["loss_pair"] == "localization_vs_existence" and r["subset"] == "all" and r.get("cosine") is not None]
        last, probe = (training[-1] if training else {}), (fixed[-1] if fixed else {})
        train_flip, fixed_flip = last.get("assignment_flip_rate"), probe.get("flip_rate")
        cosine = sum(r["cosine"] for r in gradients) / len(gradients) if gradients else None
        item = dict(tag=job["tag"], process=parent, training=state, last_completed_training_epoch=last,
            last_fixed_probe=probe, valid_representation_gradient_samples=len(gradients), mean_localization_existence_cosine=cosine,
            negative_cosine_fraction=sum(r["cosine"] < 0 for r in gradients) / len(gradients) if gradients else None)
        response = last_row(folder / "monitor/train_responses.jsonl")
        item["latest_parameter_updates"] = last_row(folder / "monitor/parameter_updates.jsonl")
        item["latest_training_responses"] = response
        item["latest_fixed_probe_responses"] = last_row(folder / "monitor/probe_responses.jsonl")
        def value(part, metric):
            v = response.get("subsets", {}).get(part, {}).get("metrics", {}).get(metric, {}).get("mean")
            return "N/A" if v is None else f"{v:.4f}"
        response_lines.append(f"| {job['tag']} | {response.get('epoch', '-')} / {response.get('step', '-')} | {value('S+', 'matched_iou')} | {value('S+', 'matched_l1')} | {value('S+', 'existence_score')} | {value('S-', 'existence_score')} | {value('S+', 'active_count')} / {value('S-', 'active_count')} | {value('S+', 'evidence_active_count')} / {value('S-', 'evidence_active_count')} |")
        snapshot.append(item)
        fmt = lambda value: "N/A" if value is None else f"{100*value:.2f}"
        lines.append(f"| {job['tag']} | {state.get('state', parent.get('state', 'queued'))} / {state.get('epoch', '-')} / {state.get('batches', '-')} | {parent.get('pid', '-')} | {last.get('actual_gt_matches_by_slot', '-')} | {fmt(train_flip)} | {fmt(fixed_flip)} | {cosine if cosine is not None else 'N/A'} ({len(gradients)}) |")
    save_json(output / "LIVE_STATUS.json", dict(updated=time.time(), jobs=snapshot))
    (output / "MONITORING.md").write_text("\n".join(lines) + "\n")
    (output / "RESPONSES.md").write_text("\n".join(response_lines) + "\n")
    return snapshot


def final_report(output):
    import monitor_qivr as diagnostic
    manifest = read_json(output / "SUITE.json")
    groups = {}
    for job in manifest["jobs"]:
        groups.setdefault((job["dataset"], job["split"], job["backbone"]), {})[job["variant"]] = output / job["tag"]
    lines = ["# Paired decoder self-attention training experiments", "", "Variant − reference means trained no-SA − trained with-SA, each selected independently on Seen validation under the same predeclared rule. Gap Reduction has the opposite sign of the gap change. Original frozen baseline comparisons and all absolute benchmark metrics are in each run's METRICS.md/metrics.csv. No full-split macro averages.", "", "| Setting | Metric | Seen Change [95% CI] | Unseen Net Gain [95% CI] | Gap Reduction [95% CI] |", "|---|---|---|---|---|"]
    csv_rows, completed = [], 0
    for (dataset, split, backbone), pair in groups.items():
        if set(pair) != {"with_sa", "no_sa"}:
            continue
        if not all(read_json(folder / "STATUS.json", {}).get("state") == "complete" for folder in pair.values()):
            continue
        a, b = (read_json(pair[v] / "CONFIG.json") for v in ("with_sa", "no_sa"))
        for key in ("initial_checkpoint_sha256", "seed", "learning_rate", "epochs", "batch_size", "release_sha256", "train_counts", "initialization", "model_kind"):
            assert a.get(key) == b.get(key), key
        destination = output / "pairs" / f"{dataset}_{split}_{backbone}"
        if not (destination / "comparison.json").exists():
            diagnostic.compare(pair["with_sa"] / "candidate_cache.pt", pair["no_sa"] / "candidate_cache.pt", destination,
                pair["with_sa"] / "predictions.npz", pair["no_sa"] / "predictions.npz")
            save_json(destination / "INTERVENTION.json", dict(reference_config=a, variant_config=b,
                reference_checkpoint_sha256=diagnostic.registry.sha(pair["with_sa"] / "best.ckpt"),
                variant_checkpoint_sha256=diagnostic.registry.sha(pair["no_sa"] / "best.ckpt"),
                independent_seen_selection=True, test_labels_used_for_selection=False))
        metrics = read_json(destination / "comparison.json")["metrics"]
        completed += 1
        fmt = lambda v: "undefined" if v["point"] is None or v["ci95"] is None else f"{v['point']:+.2f} [{v['ci95'][0]:+.2f}, {v['ci95'][1]:+.2f}]"
        for metric in ("auroc", "rej_f1", "gmiou1"):
            keys = [f"paired_change/S/{metric}", f"paired_change/U/{metric}", f"gap_reduction/{metric}"]
            lines.append(f"| {dataset}/{split}/{backbone} | {metric} | " + " | ".join(fmt(metrics[k]) for k in keys) + " |")
        lines.extend(["", f"**{dataset}/{split}/{backbone}: coverage and false responses**", "", "| Metric (no-SA − with-SA) | Point [95% CI] |", "|---|---|"])
        for key in ("paired_change/U+/coverage", "paired_change/U+/gt_recall", "paired_change/U+/top1_hit", "paired_change/U-/high_count", "paired_change/U-/relative_count", "paired_change/U-/false_acceptance"):
            lines.append(f"| {key} | {fmt(metrics[key])} |")
        lines.extend(["", "| Setting | Metric | Seen Change [95% CI] | Unseen Net Gain [95% CI] | Gap Reduction [95% CI] |", "|---|---|---|---|---|"])
        for key, value in metrics.items():
            csv_rows.append([dataset, split, backbone, key, value["point"], *(value["ci95"] or [None, None])])
    lines += ["", f"Completed paired settings: {completed}/{len(groups)}. Partial summaries remain partial. Rej-F1/G-mIoU depend on released subset class proportions. Coverage/Top1 candidate metrics use IoU≥0.5; activity thresholds are descriptive, whereas actual false acceptance uses each variant's frozen Seen-validation existence threshold. Cache Top1 treats an invalid highest-score slot as a miss; native G-mIoU removes invalid spans before choosing Top1."]
    (output / "PAIRED_RESULTS.md").write_text("\n".join(lines) + "\n")
    with (output / "PAIRED_RESULTS.csv").open("w") as stream:
        writer = csv.writer(stream)
        writer.writerow(["dataset", "split", "backbone", "metric", "point", "ci_low", "ci_high"])
        writer.writerows(csv_rows)
    return completed


def work(output):
    manifest = read_json(output / "SUITE.json")
    pending = list(manifest["jobs"])
    lock = threading.Lock()
    state = dict(state="running", controller_pid=os.getpid(), started=time.time(), jobs={j["tag"]:dict(state="queued") for j in manifest["jobs"]})
    save_json(output / "STATUS.json", state)

    def update(tag, **values):
        with lock:
            state["jobs"][tag].update(values)
            state["updated"] = time.time()
            save_json(output / "STATUS.json", state)
            live_report(output)

    def worker(gpu):
        while True:
            job = None
            with lock:
                if not pending:
                    return
                running = [dict(**next(j for j in manifest["jobs"] if j["tag"] == tag), gpu=s.get("gpu"))
                    for tag,s in state["jobs"].items() if s["state"] in ("running", "launching")]
                external = []
                for suite in manifest.get("respect_suites", []):
                    prior = read_json(Path(suite) / "STATUS.json", {})
                    for s in prior.get("jobs", {}).values():
                        if s.get("state") == "running" and s.get("gpu") == gpu:
                            try:
                                os.kill(s["pid"], 0)
                                external.append(s)
                            except (ProcessLookupError, KeyError):
                                pass
                if sum(r["gpu"] == gpu for r in running) + len(external) < manifest.get("jobs_per_gpu", 1):
                    job = pending.pop(choose_job(pending, running, gpu))
                    state["jobs"][job["tag"]].update(state="launching", gpu=gpu)
            if job is None:
                time.sleep(5)
                continue
            cmd = [sys.executable, "-u", str(ROOT / "run_mechanism_experiment.py"), "--dataset", job["dataset"],
                "--split", job["split"], "--backbone", job["backbone"], "--variant", job["variant"],
                "--output", str(output / job["tag"]), "--gpu", str(gpu), "--epochs", str(manifest["epochs"]),
                "--seed", str(manifest["seed"]), "--lr-factor", str(manifest["lr_factor"]),
                "--gradient-every", str(manifest["gradient_every"]), "--workers", str(manifest["workers"])]
            cmd += ["--initialization", manifest.get("initialization", "checkpoint"), "--model-kind", manifest.get("model_kind", "baseline")]
            logfile = output / "logs" / f"{job['tag']}.log"
            with logfile.open("w") as log:
                env = {**os.environ, "OMP_NUM_THREADS":"2", "MKL_NUM_THREADS":"2", "OPENBLAS_NUM_THREADS":"2"}
                process = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT, env=env)
                update(job["tag"], state="running", pid=process.pid, gpu=gpu, argv=cmd, log=str(logfile))
                while True:
                    try:
                        code = process.wait(timeout=15)
                        break
                    except subprocess.TimeoutExpired:
                        update(job["tag"], state="running")
            update(job["tag"], state="complete" if code == 0 else "failed", returncode=code, finished=time.time())
            with lock:
                final_report(output)
    with ThreadPoolExecutor(max_workers=len(manifest["gpus"]) * manifest.get("jobs_per_gpu", 1)) as pool:
        futures = [pool.submit(worker, gpu) for gpu in manifest["gpus"] for _ in range(manifest.get("jobs_per_gpu", 1))]
        for future in futures:
            future.result()
    state["state"] = "complete" if all(j["state"] == "complete" for j in state["jobs"].values()) else "partial_failed"
    state["finished"] = time.time()
    save_json(output / "STATUS.json", state)
    live_report(output)
    final_report(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("launch", "work", "status", "report"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gpus", default="0,1")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--seed", type=int, default=3407)
    parser.add_argument("--gradient-every", type=int, default=50)
    parser.add_argument("--lr-factor", type=float, default=1.)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--datasets", nargs="+", choices=("soccer", "clean_v3", "charades_cg_v2"), default=["soccer", "clean_v3", "charades_cg_v2"])
    parser.add_argument("--all-splits", action="store_true")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--jobs-per-gpu", type=int, default=2)
    parser.add_argument("--respect-suite", action="append", type=Path, default=[])
    parser.add_argument("--model-kind", choices=("baseline", "qivr"), default="qivr")
    parser.add_argument("--initialization", choices=("checkpoint", "fresh"), default="fresh")
    args = parser.parse_args()
    output = args.output.resolve()
    if args.mode == "launch":
        import monitor_qivr as diagnostic
        if output.exists():
            parser.error("output already exists; use a fresh suite directory")
        gpus = [int(g) for g in args.gpus.split(",")]
        assert len(gpus) == len(set(gpus)) and len(gpus) > 0
        if args.jobs_per_gpu < 1 or args.epochs < 1:
            parser.error("jobs-per-gpu and epochs must be positive")
        jobs = []
        for dataset in args.datasets:
            splits = diagnostic.registry.SPECS[dataset][2]
            for split in (splits if args.all_splits else splits[:1]):
                for bb in ("moment", "qd"):
                    for variant in ("with_sa", "no_sa"):
                        jobs.append(dict(dataset=dataset, split=split, backbone=bb, variant=variant, tag=f"{dataset}_{split}_{bb}_{variant}"))
        output.mkdir(parents=True)
        (output / "logs").mkdir()
        save_json(output / "SUITE.json", dict(jobs=jobs, gpus=gpus, epochs=args.epochs, seed=args.seed,
            jobs_per_gpu=args.jobs_per_gpu, initialization=args.initialization, model_kind=args.model_kind,
            respect_suites=[str(p.resolve()) for p in args.respect_suite],
            gradient_every=args.gradient_every, lr_factor=args.lr_factor, workers=args.workers,
            scope="paired full training; single seed; Seen-only selection; first split per dataset unless all-splits; FlashVTG not included",
            code_sha256={str(p):diagnostic.registry.sha(p) for p in (Path(__file__), ROOT / "run_mechanism_experiment.py")}))
        with (output / "controller.log").open("w") as log:
            process = subprocess.Popen([sys.executable, "-u", str(Path(__file__).resolve()), "work", "--output", str(output)],
                stdout=log, stderr=subprocess.STDOUT, start_new_session=True, cwd=ROOT)
        save_json(output / "LAUNCH.json", dict(controller_pid=process.pid, launched=time.time(), jobs=len(jobs)))
        print(json.dumps(dict(controller_pid=process.pid, output=str(output), jobs=len(jobs)), indent=2))
    elif args.mode == "work":
        try:
            work(output)
        except Exception as error:
            state = read_json(output / "STATUS.json", {})
            state.update(state="controller_failed", error=repr(error), updated=time.time())
            save_json(output / "STATUS.json", state)
            raise
    elif args.mode == "report":
        live_report(output)
        print("Completed pairs:", final_report(output))
    else:
        while True:
            snapshot = live_report(output)
            for job in snapshot:
                print(job["tag"], job["training"].get("state", job["process"].get("state")),
                    "epoch", job["training"].get("epoch"), "steps", job["training"].get("global_step"),
                    "pure loc/exist cosine", job["mean_localization_existence_cosine"], flush=True)
            if not args.watch or read_json(output / "STATUS.json", {}).get("state") in ("complete", "partial_failed", "controller_failed"):
                break
            time.sleep(15)


if __name__ == "__main__":
    main()
