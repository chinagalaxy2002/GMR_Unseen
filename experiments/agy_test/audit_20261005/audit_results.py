"""Read-only audit of existing artifacts. Writes only into this audit directory.

No training or model selection. Bootstrap resamples the same video IDs jointly
across all five splits, preserving shared-video dependence and paired scores.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import torch
import torch.nn.functional as F
from scipy.special import expit
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SPLITS = ["A1", "A2_alt", "A3", "C1", "C2_alt"]
torch.set_num_threads(2)


def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""):
            h.update(b)
    return h.hexdigest()


def signals(d):
    hs = torch.from_numpy(d["hs"])
    mean = hs.mean(1, keepdim=True)
    return {
        "orig_logits": d["orig_logits"].reshape(-1),
        "cos_disp": (1 - (F.normalize(hs, dim=-1) * F.normalize(mean, dim=-1)).sum(-1).min(-1).values).numpy(),
        "slot_max_dev": (hs - mean).norm(dim=-1).max(-1).values.numpy(),
        "fg_max": torch.from_numpy(d["fg"]).max(-1).values.numpy(),
    }


def forward(sig, ckpt):
    state, stats = ckpt["model"], ckpt["val_stats"]
    weights = {
        "orig_logits": .5 + .7 * state["raw_w_orig"].sigmoid(),
        "cos_disp": .5 + 1.5 * state["raw_w_disp"].sigmoid(),
        "slot_max_dev": .2 + 1.3 * state["raw_w_dev"].sigmoid(),
        "fg_max": .1 + .9 * state["raw_w_fg"].sigmoid(),
    }
    terms = [weights[k] * torch.tensor((sig[k] - stats[k][0]) / stats[k][1], dtype=torch.float32) for k in weights]
    score = terms[0] + terms[1] + terms[2] + terms[3] + state["bias"]
    return score.numpy()


def threshold(score, y):
    candidates = np.unique(score)
    if len(candidates) > 1000:
        candidates = np.quantile(score, np.linspace(0, 1, 1000))
    best, chosen = -1., float(candidates[0])
    for t in candidates:
        pred = score >= t
        bal = .5 * (pred[y == 1].mean() + (~pred[y == 0]).mean())
        if bal > best:
            best, chosen = bal, float(t)
    return chosen


def metrics(score, d, pairs, th=None):
    parts, y = d["partitions"], d["labels"]
    sm = np.isin(parts, ["S+", "S-"])
    um = np.isin(parts, ["U+", "U-"])
    s, u = roc_auc_score(y[sm], score[sm]), roc_auc_score(y[um], score[um])
    lookup = {str(q): i for i, q in enumerate(d["qids"])}
    comparisons = []
    for p in pairs:
        a, b = score[lookup[str(p["positive_qid"])]], score[lookup[str(p["negative_qid"])]]
        comparisons.append(float(a > b) + .5 * float(a == b))
    out = dict(Seen_AUROC=float(s), Unseen_AUROC=float(u), Gap=float(s-u),
               Matched_PairAcc=float(np.mean(comparisons)), matched_pair_n=len(comparisons))
    if th is not None:
        accepted = score >= th
        out.update(Threshold=float(th), U_pos_FRR=float((~accepted[parts == "U+"]).mean()*100),
                   U_neg_RR=float((~accepted[parts == "U-"]).mean()*100))
        for prefix, mask in [("Seen", sm), ("Unseen", um)]:
            rej = ~accepted[mask]
            yy = y[mask]
            tp = np.sum(rej & (yy == 0))
            fp = np.sum(rej & (yy == 1))
            fn = np.sum(~rej & (yy == 0))
            out[prefix+"_RejF1"] = float(2*tp / (2*tp+fp+fn)) if 2*tp+fp+fn else 0.
            out[prefix+"_BalancedAccuracy"] = float(.5 * (accepted[mask][yy == 1].mean()+rej[yy == 0].mean()))
    return out


def prepared_auc(y, s, vids):
    order = np.argsort(s, kind="stable")
    y, s, vids = y[order], s[order], vids[order]
    starts = np.r_[0, np.flatnonzero(np.diff(s)) + 1]
    def calc(counts):
        w = counts[vids]
        pos = np.add.reduceat(w*(y == 1), starts)
        neg = np.add.reduceat(w*(y == 0), starts)
        if pos.sum() == 0 or neg.sum() == 0:
            return np.nan
        return (pos * (np.cumsum(neg) - .5*neg)).sum() / (pos.sum()*neg.sum())
    return calc


def main():
    report = {"scope": "existing checkpoints and cache; no retraining", "splits": {}, "sha256": {}}
    boot_data = {}
    mean_names = ["published_baseline", "cache_baseline_logit", "cache_baseline_rounded_probability", "final_logit", "final_rounded_probability"]
    for split in SPLITS:
        cache = ROOT / "experiments/agy_test/cache/hq" / split
        final = ROOT / "experiments/agy_test/e2e_training/results_final" / split
        baseline = ROOT / "results/semantic_existence/multi_split_v2" / split / "qd"
        release = ROOT / "data/release/semantic_existence_v2" / split
        d = {stage: dict(np.load(cache / (stage+".npz"))) for stage in ["train", "val", "test"]}
        ckpt = torch.load(final / "best.ckpt", map_location="cpu", weights_only=False)
        old = torch.load(baseline / "best.ckpt", map_location="cpu", weights_only=False)
        preds = rows(final / "predictions.jsonl")
        pmap = {str(x["qid"]): x for x in preds}
        test = d["test"]
        saved = np.array([pmap[str(q)]["pred_score"] for q in test["qids"]])
        v_sig, t_sig = signals(d["val"]), signals(test)
        v_score, t_score = forward(v_sig, ckpt), forward(t_sig, ckpt)
        seen_v = np.isin(d["val"]["partitions"], ["S+", "S-"])
        new_th = threshold(v_score[seen_v], d["val"]["labels"][seen_v])
        pairs = rows(release / "matched_u_pairs.jsonl")
        published = {str(x["qid"]): x for x in rows(baseline / "test/qd_detr_gmr_test_submission.jsonl")}
        pub_scores = np.array([published[str(q)]["pred_exist_score"] for q in test["qids"]])
        orig = test["orig_logits"]
        rounded = np.round(expit(orig.astype(np.float64)), 4)
        diag = json.loads((baseline / "diagnostics.json").read_text())
        base_th = threshold(v_sig["orig_logits"][seen_v], d["val"]["labels"][seen_v])
        final_round = np.round(expit(saved), 4)
        round_val = np.round(expit(v_score.astype(np.float64)), 4)
        round_th = threshold(round_val[seen_v], d["val"]["labels"][seen_v])
        r = {
            "published_baseline": metrics(pub_scores, test, pairs, diag["threshold"]),
            "cache_baseline_logit": metrics(orig, test, pairs, base_th),
            "cache_baseline_rounded_probability": metrics(rounded, test, pairs),
            "final_logit": metrics(saved, test, pairs, new_th),
            "final_rounded_probability": metrics(final_round, test, pairs, round_th),
            "signals": {k: metrics(x, test, pairs) for k, x in t_sig.items()},
            "checks": {},
        }
        checks = r["checks"]
        checks["checkpoint_parameter_count"] = sum(x.numel() for x in ckpt["model"].values())
        checks["checkpoint_prediction_max_abs_error"] = float(np.max(np.abs(t_score-saved)))
        checks["saved_metrics_max_abs_error"] = float(max(abs(r["final_logit"][k]-ckpt["metrics"][k]) for k in ["Seen_AUROC", "Unseen_AUROC", "Gap", "Matched_PairAcc", "U_pos_FRR", "U_neg_RR", "Threshold"]))
        checks["best_val_seen_auc_error"] = float(abs(roc_auc_score(d["val"]["labels"][seen_v], v_score[seen_v])-ckpt["metrics"]["best_val_seen_auc"]))
        checks["val_statistics_max_abs_error"] = float(max(max(abs(float(v_sig[k][seen_v].mean())-ckpt["val_stats"][k][0]), abs(float(v_sig[k][seen_v].std()+1e-6)-ckpt["val_stats"][k][1])) for k in v_sig))
        checks["duplicate_final_qids"] = len(preds)-len(pmap)
        checks["final_qid_set_matches_cache"] = set(pmap) == set(test["qids"].tolist())
        checks["final_partitions_match_cache"] = all(pmap[str(q)]["partition"] == p for q, p in zip(test["qids"], test["partitions"]))
        checks["cache_release"] = {}
        for stage, data in d.items():
            rr = {str(x["qid"]): x for x in rows(release / (stage+".jsonl"))}
            checks["cache_release"][stage] = {
                "qid_set_matches": set(rr) == set(data["qids"].tolist()),
                "no_duplicate_qids": len(np.unique(data["qids"])) == len(data["qids"]),
                "metadata_matches": all(rr[str(q)]["partition"] == p and str(rr[str(q)]["vid"]) == v and int(rr[str(q)]["exist_label"]) == int(y) for q,p,v,y in zip(data["qids"], data["partitions"], data["vids"], data["labels"])),
                "partition_counts": {str(k):int(v) for k,v in zip(*np.unique(data["partitions"], return_counts=True))},
            }
        checks["train_seen_only"] = bool(np.all(np.isin(d["train"]["partitions"], ["S+", "S-"])))
        checks["video_overlaps"] = {a+"_"+b:len(set(d[a]["vids"]) & set(d[b]["vids"])) for a,b in [("train","val"),("train","test"),("val","test")]}
        m = old["model"]
        hs = torch.from_numpy(test["hs"])
        old_pred = F.linear(F.relu(F.linear(hs.max(1).values, m["exist_head.layers.0.weight"], m["exist_head.layers.0.bias"])), m["exist_head.layers.1.weight"], m["exist_head.layers.1.bias"]).squeeze().numpy()
        checks["canonical_baseline_head_cache_logit_error"] = float(np.max(np.abs(old_pred-orig)))
        delta = np.abs(rounded-pub_scores)
        checks["cache_published_probability_error_quantiles"] = np.quantile(delta, [0,.5,.9,.99,1]).tolist()
        checks["cache_published_probability_diff_gt_001_n"] = int((delta>.01).sum())
        checks["cache_published_rounded_match_fraction"] = float(np.mean(rounded == pub_scores))
        checks["canonical_checkpoint_epoch"] = old.get("epoch")
        checks["canonical_eval_bsz"] = old["opt"].get("eval_bsz")
        checks["canonical_adapter_is_two_layer_mlp"] = [k for k in m if k.startswith("exist_head")]
        # Reproduce hard-gate top-1 localization from the cached spans, in both
        # plausible coordinate conventions; cache lacks a provenance manifest.
        gt = {str(x["qid"]):x for x in rows(release / "test.jsonl")}
        r["cache_localization"] = {}
        for convention in ["cxw", "xx"]:
            hits = []
            for i,q in enumerate(test["qids"]):
                k = int(test["fg"][i].argmax())
                a,b = map(float, test["spans"][i,k])
                if convention == "cxw":
                    a,b = a-b/2, a+b/2
                dur = float(test["durations"][i])
                a,b = np.clip([a*dur,b*dur],0,dur)
                best = 0.
                for c,e in gt[str(q)]["relevant_windows"]:
                    inter = max(0.,min(b,e)-max(a,c))
                    union = b-a+e-c-inter
                    best = max(best, inter/union if union>0 else 0.)
                hits.append(best >= .5)
            hits = np.array(hits)
            pos = test["partitions"] == "U+"
            r["cache_localization"][convention] = {"U_pos_raw_R1_iou05":float(hits[pos].mean()), "U_pos_baseline_gated_R1_iou05":float((hits[pos] & (orig[pos]>=base_th)).mean()), "U_pos_final_gated_R1_iou05":float((hits[pos] & (saved[pos]>=new_th)).mean())}
        report["splits"][split] = r
        boot_data[split] = dict(y=test["labels"], parts=test["partitions"], vids=test["vids"], original=orig, final=saved)
        for path in [final/"best.ckpt", final/"predictions.jsonl", final/"metrics.json", baseline/"best.ckpt", cache/"train.npz", cache/"val.npz", cache/"test.npz"]:
            report["sha256"][str(path.relative_to(ROOT))] = sha(path)
        print(split, json.dumps({k:r[k] for k in ["published_baseline", "cache_baseline_logit", "final_logit"]}), flush=True)
    keys = ["Seen_AUROC", "Unseen_AUROC", "Gap", "Matched_PairAcc"]
    report["macro_means"] = {name:{k:float(np.mean([report["splits"][s][name][k] for s in SPLITS])) for k in keys} for name in mean_names}
    all_vids = sorted(set(np.concatenate([x["vids"] for x in boot_data.values()])))
    vmap = {v:i for i,v in enumerate(all_vids)}
    funcs = []
    for s,d in boot_data.items():
        vi = np.array([vmap[v] for v in d["vids"]])
        group = []
        for parts in [["S+","S-"],["U+","U-"]]:
            mask = np.isin(d["parts"],parts)
            group.append([prepared_auc(d["y"][mask],d[k][mask],vi[mask]) for k in ["original","final"]])
        funcs.append(group)
    rng = np.random.default_rng(20261005)
    repeats = 2000
    deltas = np.empty((repeats, len(SPLITS), 3))
    for b in range(repeats):
        counts = np.bincount(rng.integers(len(all_vids), size=len(all_vids)), minlength=len(all_vids)).astype(float)
        for i,group in enumerate(funcs):
            ds,du = [f[1](counts)-f[0](counts) for f in group]
            deltas[b,i] = [ds,du,du-ds]
    names = ["delta_seen_final_minus_baseline", "delta_unseen_final_minus_baseline", "gap_reduction_baseline_minus_final"]
    ci = lambda arr:{name:np.nanquantile(arr[:,j],[.025,.975]).tolist() for j,name in enumerate(names)}
    report["paired_video_bootstrap"] = {"repeats":repeats, "seed":20261005, "video_clusters":len(all_vids), "baseline":"same-cache full precision logits", "note":"shared video resampling across splits; fixed models; exploratory test results, no training-seed uncertainty or search multiplicity correction", "per_split":{s:ci(deltas[:,i]) for i,s in enumerate(SPLITS)}, "macro":ci(np.nanmean(deltas,axis=1))}
    (OUT / "audit_metrics.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)+"\n")
    print('MACRO',json.dumps(report["macro_means"]),flush=True)
    print('BOOTSTRAP',json.dumps(report["paired_video_bootstrap"]),flush=True)


if __name__ == "__main__":
    main()
