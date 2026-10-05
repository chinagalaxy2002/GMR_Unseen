#!/usr/bin/env python3
"""
Full Canonical Test Replay with Dual-Pooling Adapter on GPU at eval_bsz=16.

Verifies:
1. Baseline probabilities match published official QD-DETR baseline with 0.0 error.
2. Both baseline exist head and trained DualPool adapter evaluate on IDENTICAL fresh decoder states.
3. Computes exact full-test metrics and 2,000-repeat paired video cluster bootstrap CIs.
"""
from pathlib import Path
import json
import sys
import numpy as np
import torch
import torch.nn.functional as F
from easydict import EasyDict
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/agy_test/audit_20261005"))

from models.qd_detr_gmr import build_model
from training.qd_detr_gmr.dataset import StartEndDataset, start_end_collate, prepare_batch_inputs
from audit_results import SPLITS, rows, prepared_auc

OUT_DIR = Path(__file__).resolve().parent / "fresh_replay_results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

torch.set_num_threads(2)

def extract_dual_pool_from_tensor(hs_tensor):
    # hs_tensor: [B, 10, 256]
    p_max = hs_tensor.max(dim=1).values # [B, 256]
    p_mean = hs_tensor.mean(dim=1)      # [B, 256]
    norm_hs = F.normalize(hs_tensor, p=2, dim=-1)
    norm_mean = F.normalize(p_mean.unsqueeze(1), p=2, dim=-1)
    cos_disp = (1.0 - (norm_hs * norm_mean).sum(dim=-1).min(dim=-1).values).unsqueeze(-1) # [B, 1]
    dev = (hs_tensor - p_mean.unsqueeze(1)).norm(p=2, dim=-1).max(dim=-1).values.unsqueeze(-1) # [B, 1]
    return torch.cat([p_max, p_mean, cos_disp, dev], dim=-1) # [B, 514]

def run_fresh_replay(model_type="scaled_c05"):
    ckpt_root = Path(__file__).resolve().parent / f"runs_{model_type}"
    print(f"\n=======================================================")
    print(f"Running Fresh Canonical Test Replay for: {model_type}")
    print(f"=======================================================")
    
    report = {"model_type": model_type, "splits": {}}
    boot_data = {}
    
    for split in SPLITS:
        base_dir = ROOT / "results/semantic_existence/multi_split_v2" / split / "qd"
        release_dir = ROOT / "data/release/semantic_existence_v2" / split
        
        # Load canonical QD checkpoint
        qd_ckpt = torch.load(base_dir / "best.ckpt", map_location="cpu", weights_only=False)
        opt = EasyDict(qd_ckpt["opt"])
        opt.device = "cuda:0"
        model, _ = build_model(opt)
        model.load_state_dict(qd_ckpt["model"])
        model.cuda().eval()
        
        # Load trained DualPool adapter checkpoint
        adapter_ckpt = torch.load(ckpt_root / split / "adapter_checkpoint.pt", map_location="cpu", weights_only=False)
        w = torch.tensor(adapter_ckpt["coef"], dtype=torch.float32, device="cuda:0") # [514]
        b = float(adapter_ckpt["intercept"])
        th = float(adapter_ckpt["threshold"])
        
        scaler = adapter_ckpt.get("scaler")
        scale_mean = torch.tensor(scaler["mean"], dtype=torch.float32, device="cuda:0") if scaler else None
        scale_scale = torch.tensor(scaler["scale"], dtype=torch.float32, device="cuda:0") if scaler else None
        
        # Register hook to capture fresh hs
        captured = {}
        def hook(_m, _i, outputs):
            captured["hs"] = outputs[0][-1].detach()
        handle = model.transformer.register_forward_hook(hook)
        
        ds = StartEndDataset(
            dset_name=opt.dset_name,
            data_path=str(release_dir / "test.jsonl"),
            v_feat_dirs=opt.v_feat_dirs,
            q_feat_dir=opt.t_feat_dir,
            q_feat_type="last_hidden_state",
            max_q_l=int(opt.max_q_l),
            max_v_l=int(opt.max_v_l),
            ctx_mode=opt.ctx_mode,
            clip_len=int(opt.clip_length),
            max_windows=int(opt.max_windows),
            span_loss_type=opt.span_loss_type,
            load_labels=False,
            mr_only=True,
            keep_empty_gt=True,
        )
        loader = DataLoader(ds, batch_size=16, shuffle=False, num_workers=0, collate_fn=start_end_collate)
        
        base_logits_parts = []
        dual_logits_parts = []
        metadata = []
        
        for bi, batch in enumerate(loader):
            inputs, _ = prepare_batch_inputs(batch[1], "cuda:0")
            with torch.no_grad():
                result = model(**inputs)
                hs_fresh = captured["hs"] # [B, 10, 256] on GPU
                feat_fresh = extract_dual_pool_from_tensor(hs_fresh) # [B, 514]
                
                if scaler is not None:
                    feat_fresh = (feat_fresh - scale_mean) / scale_scale
                    
                dual_logits = (feat_fresh * w).sum(dim=-1) + b # [B]
                base_logits = result["pred_exist_logits"]      # [B]
                
                base_logits_parts.append(base_logits.cpu().numpy())
                dual_logits_parts.append(dual_logits.cpu().numpy())
                metadata.extend(batch[0])
                
            if bi % 100 == 0:
                print(f"  {split} batches: {bi+1}/{len(loader)}", flush=True)
                
        handle.remove()
        del model
        torch.cuda.empty_cache()
        
        base_logits = np.concatenate(base_logits_parts)
        dual_logits = np.concatenate(dual_logits_parts)
        
        qids = np.array([str(x["qid"]) for x in metadata])
        labels = np.array([int(x["exist_label"]) for x in metadata])
        parts = np.array([x["partition"] for x in metadata])
        vids = np.array([x["vid"] for x in metadata])
        
        # Verify 0.0 error with published probability
        base_prob = torch.from_numpy(base_logits).sigmoid().numpy().astype(float)
        rounded_base_prob = np.array([float(f"{x:.4f}") for x in base_prob])
        pub_rows = {str(x["qid"]): x for x in rows(base_dir / "test/qd_detr_gmr_test_submission.jsonl")}
        pub_scores = np.array([pub_rows[q]["pred_exist_score"] for q in qids])
        max_pub_err = float(np.max(np.abs(rounded_base_prob - pub_scores)))
        assert max_pub_err < 1e-4, f"Published probability mismatch in {split}: max err = {max_pub_err}"
        
        sm = (parts == "S+") | (parts == "S-")
        um = (parts == "U+") | (parts == "U-")
        
        base_s_auc = float(roc_auc_score(labels[sm], base_logits[sm]))
        base_u_auc = float(roc_auc_score(labels[um], base_logits[um]))
        base_gap = base_s_auc - base_u_auc
        
        dual_s_auc = float(roc_auc_score(labels[sm], dual_logits[sm]))
        dual_u_auc = float(roc_auc_score(labels[um], dual_logits[um]))
        dual_gap = dual_s_auc - dual_u_auc
        
        # Matched PairAcc
        pairs_file = release_dir / "matched_u_pairs.jsonl"
        qid_to_score = dict(zip(qids, dual_logits))
        qid_to_base = dict(zip(qids, base_logits))
        pair_accs, base_pair_accs = [], []
        if pairs_file.exists():
            for p in rows(pairs_file):
                pq, nq = str(p["positive_qid"]), str(p["negative_qid"])
                if pq in qid_to_score and nq in qid_to_score:
                    pair_accs.append(1.0 if qid_to_score[pq] > qid_to_score[nq] else 0.5 if qid_to_score[pq] == qid_to_score[nq] else 0.0)
                    base_pair_accs.append(1.0 if qid_to_base[pq] > qid_to_base[nq] else 0.5 if qid_to_base[pq] == qid_to_base[nq] else 0.0)
        pair_acc = float(np.mean(pair_accs)) if pair_accs else 0.5
        base_pair_acc = float(np.mean(base_pair_accs)) if base_pair_accs else 0.5
        
        split_res = {
            "split": split,
            "published_prob_max_err": max_pub_err,
            "baseline_fresh": {
                "Seen_AUROC": base_s_auc,
                "Unseen_AUROC": base_u_auc,
                "Gap": base_gap,
                "Matched_PairAcc": base_pair_acc,
            },
            "dual_pool": {
                "Seen_AUROC": dual_s_auc,
                "Unseen_AUROC": dual_u_auc,
                "Gap": dual_gap,
                "Matched_PairAcc": pair_acc,
                "delta_seen": dual_s_auc - base_s_auc,
                "delta_unseen": dual_u_auc - base_u_auc,
                "gap_reduction": base_gap - dual_gap,
            }
        }
        report["splits"][split] = split_res
        boot_data[split] = dict(y=labels, parts=parts, vids=vids, original=base_logits, final=dual_logits)
        print(f"  {split} Finished: Base Seen={base_s_auc:.4f}, Dual Seen={dual_s_auc:.4f} | Base Unseen={base_u_auc:.4f}, Dual Unseen={dual_u_auc:.4f} | Base Gap={base_gap:.4f}, Dual Gap={dual_gap:.4f}")
        
    # Bootstrap
    all_vids = sorted(set(np.concatenate([x["vids"] for x in boot_data.values()])))
    vmap = {v: i for i, v in enumerate(all_vids)}
    funcs = []
    for d in boot_data.values():
        vi = np.array([vmap[v] for v in d["vids"]])
        group = []
        for parts in [["S+", "S-"], ["U+", "U-"]]:
            mask = np.isin(d["parts"], parts)
            group.append([prepared_auc(d["y"][mask], d[k][mask], vi[mask]) for k in ["original", "final"]])
        funcs.append(group)
        
    rng = np.random.default_rng(20261005)
    deltas = np.empty((2000, len(SPLITS), 3))
    for b in range(2000):
        counts = np.bincount(rng.integers(len(all_vids), size=len(all_vids)), minlength=len(all_vids)).astype(float)
        for i, group in enumerate(funcs):
            ds, du = [f[1](counts) - f[0](counts) for f in group]
            deltas[b, i] = [ds, du, du - ds]
            
    names = ["delta_seen", "delta_unseen", "gap_reduction"]
    ci = lambda arr: {names[j]: [float(np.nanquantile(arr[:, j], 0.025)), float(np.nanquantile(arr[:, j], 0.975))] for j in range(3)}
    report["bootstrap_95ci"] = ci(np.nanmean(deltas, axis=1))
    
    macro_base = {k: float(np.mean([r["baseline_fresh"][k] for r in report["splits"].values()])) for k in ["Seen_AUROC", "Unseen_AUROC", "Gap", "Matched_PairAcc"]}
    macro_dual = {k: float(np.mean([r["dual_pool"][k] for r in report["splits"].values()])) for k in ["Seen_AUROC", "Unseen_AUROC", "Gap", "Matched_PairAcc", "delta_seen", "delta_unseen", "gap_reduction"]}
    report["macro"] = {"baseline": macro_base, "dual_pool": macro_dual}
    
    out_file = OUT_DIR / f"{model_type}_fresh_replay_metrics.json"
    out_file.write_text(json.dumps(report, indent=2) + "\n")
    print(f"\nMacro Summary for {model_type}:")
    print(f"  Seen AUROC:       Base={macro_base['Seen_AUROC']:.4f} -> Dual={macro_dual['Seen_AUROC']:.4f} ({macro_dual['delta_seen']*100:+.2f} pp)")
    print(f"  Unseen AUROC:     Base={macro_base['Unseen_AUROC']:.4f} -> Dual={macro_dual['Unseen_AUROC']:.4f} ({macro_dual['delta_unseen']*100:+.2f} pp)")
    print(f"  Gap:              Base={macro_base['Gap']:.4f} -> Dual={macro_dual['Gap']:.4f} ({-macro_dual['gap_reduction']*100:+.2f} pp)")
    print(f"  Matched PairAcc:  Base={macro_base['Matched_PairAcc']:.4f} -> Dual={macro_dual['Matched_PairAcc']:.4f} ({(macro_dual['Matched_PairAcc'] - macro_base['Matched_PairAcc'])*100:+.2f} pp)")
    print(f"  95% CI delta_unseen:  [{report['bootstrap_95ci']['delta_unseen'][0]*100:+.2f} pp, {report['bootstrap_95ci']['delta_unseen'][1]*100:+.2f} pp]")
    print(f"  95% CI gap_reduction: [{report['bootstrap_95ci']['gap_reduction'][0]*100:+.2f} pp, {report['bootstrap_95ci']['gap_reduction'][1]*100:+.2f} pp]")
    return report

def main():
    res_scaled = run_fresh_replay("scaled_c05")
    res_unscaled = run_fresh_replay("unscaled_c10")
    print("\nAll fresh canonical replays completed successfully!")

if __name__ == "__main__":
    main()
