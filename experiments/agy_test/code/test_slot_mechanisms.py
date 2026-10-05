from __future__ import annotations
import json, random, sys
from pathlib import Path
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score

REPO = Path(__file__).resolve().parents[3]
AGY_TEST = REPO / "experiments/agy_test"
sys.path.insert(0, str(REPO))

def set_seed(seed=3407):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def compute_auc(y_true, y_score):
    return float(roc_auc_score(y_true, y_score))

def pair_metrics(scores, labels, queries):
    groups = {}
    for i, q in enumerate(queries):
        groups.setdefault(q, []).append(i)
    accs, counts = [], []
    for q, idxs in groups.items():
        pos = [i for i in idxs if labels[i] == 1]
        neg = [i for i in idxs if labels[i] == 0]
        if not pos or not neg:
            continue
        vals = [1.0 if scores[p] > scores[n] else 0.5 if scores[p] == scores[n] else 0.0 for p in pos for n in neg]
        accs.append(float(np.mean(vals)))
        counts.append(len(vals))
    macro = float(np.mean(accs)) if accs else 0.5
    weighted = float(np.average(accs, weights=counts)) if accs else 0.5
    return {"macro_pair_acc": macro, "weighted_pair_acc": weighted, "pairs": int(sum(counts)), "queries": len(accs)}

def main():
    set_seed(3407)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load model and hook decoder slots
    from easydict import EasyDict
    from models.qd_detr_gmr import build_model
    from training.qd_detr_gmr.dataset import StartEndDataset, prepare_batch_inputs, start_end_collate
    from torch.utils.data import DataLoader
    
    ckpt_path = REPO / "experiments/gmr_evidence_transfer_20261005/02_clean_qd_token_baseline_A2alt/checkpoints/best.ckpt"
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    opt = EasyDict(ckpt["opt"])
    opt.device = str(device)
    model, _ = build_model(opt)
    model.load_state_dict(ckpt["model"])
    model.to(device).eval()
    
    captured = {}
    def hook_hs(_m, _i, out):
        captured["hs"] = out[0].detach() # [#layers, bsz, #queries, d]
    model.transformer.register_forward_hook(hook_hs)
    
    # Evaluate on Seen and U
    data_dir = REPO / "experiments/gmr_unseen_existence_20261005/cross_confirmation"
    view_dir = data_dir / "data_views/A2_alt"
    v_feat_dirs = ['/home/guoxiangyu/paper/新建文件夹/charades/vid_clip', '/home/guoxiangyu/paper/新建文件夹/charades/vid_slowfast']
    t_feat_dir = str(REPO / "features/semantic_existence_v2/A2_alt/clip_text")
    
    splits_data = {}
    for split_name, jsonl_name in [("seen", "seen.jsonl"), ("u", "u.jsonl")]:
        p = view_dir / jsonl_name
        rows = [json.loads(line) for line in open(p)]
        ds = StartEndDataset(
            dset_name=opt.dset_name, data_path=str(p), v_feat_dirs=v_feat_dirs,
            q_feat_dir=t_feat_dir, q_feat_type="last_hidden_state", max_q_l=int(opt.max_q_l),
            max_v_l=int(opt.max_v_l), ctx_mode=opt.ctx_mode, clip_len=int(opt.clip_length),
            max_windows=int(opt.max_windows), span_loss_type=opt.span_loss_type,
            load_labels=True, mr_only=True, keep_empty_gt=True
        )
        loader = DataLoader(ds, batch_size=32, shuffle=False, collate_fn=start_end_collate)
        
        all_hs = []
        all_orig_logits = []
        all_fg = []
        all_labels = []
        all_queries = []
        
        with torch.no_grad():
            for batch in loader:
                metas = batch[0]
                inputs, _ = prepare_batch_inputs(batch[1], device)
                out = model(**inputs)
                hs_last = captured["hs"][-1] # [B, 10, 256]
                all_hs.append(hs_last.cpu().numpy())
                all_orig_logits.append(out["pred_exist_logits"].cpu().numpy())
                all_fg.append(out["pred_logits"].softmax(-1)[..., 0].cpu().numpy())
                for m in metas:
                    lbl = m.get("exist_label", bool(m.get("relevant_windows")))
                    all_labels.append(int(lbl))
                    all_queries.append(m["query"])
                    
        splits_data[split_name] = {
            "hs": np.concatenate(all_hs, axis=0),
            "orig_logits": np.concatenate(all_orig_logits, axis=0),
            "fg": np.concatenate(all_fg, axis=0),
            "labels": np.array(all_labels, dtype=int),
            "queries": all_queries,
            "rows": rows
        }
        print(f"Extracted {split_name}: {len(all_labels)} samples")
        
    # Analyze existence mechanisms on decoder slots:
    # 1. Original GMR Adapter: MLP(max_i h_{i, :})
    # 2. Per-Slot Scoring: max_i MLP(h_i)
    # 3. FG-weighted Slot Scoring: max_i (MLP(h_i) + log(fg_i))
    # 4. Top-1 Slot by Foreground: MLP(h_{argmax(fg)})
    
    # Extract the original MLP weights from model.exist_head
    mlp = model.exist_head
    print("Original MLP:", mlp)
    
    with torch.no_grad():
        for split_name, d in splits_data.items():
            hs = torch.from_numpy(d["hs"]).to(device) # [N, 10, 256]
            fg = torch.from_numpy(d["fg"]).to(device) # [N, 10]
            
            # Method 1: Original coordinate max
            coord_max = hs.max(dim=1).values # [N, 256]
            orig_mlp_out = mlp.layers[1](F.relu(mlp.layers[0](coord_max))).squeeze(-1).cpu().numpy()
            
            # Method 2: Per-slot scoring -> scalar max
            # Apply MLP to each slot individually: [N*10, 256]
            n, k, dim = hs.shape
            slot_flat = hs.reshape(n * k, dim)
            slot_scores = mlp.layers[1](F.relu(mlp.layers[0](slot_flat))).reshape(n, k)
            per_slot_max = slot_scores.max(dim=1).values.cpu().numpy()
            
            # Method 3: Foreground-gated slot scoring
            fg_gated_scores = (slot_scores + torch.log(fg.clamp_min(1e-4))).max(dim=1).values.cpu().numpy()
            
            # Method 4: Slot corresponding to Top-1 foreground proposal
            top1_k = fg.argmax(dim=1, keepdim=True) # [N, 1]
            top1_slot_score = slot_scores.gather(1, top1_k).squeeze(1).cpu().numpy()
            
            d["m1_coord_max"] = orig_mlp_out
            d["m2_per_slot_max"] = per_slot_max
            d["m3_fg_gated_max"] = fg_gated_scores
            d["m4_top1_slot"] = top1_slot_score
            
    # Compute AUROC and Pair Acc for all methods
    mechanisms = [
        ("M1_Coord_Max (Original)", "m1_coord_max"),
        ("M2_Per_Slot_Max (Slot Witness)", "m2_per_slot_max"),
        ("M3_FG_Gated_Slot_Max", "m3_fg_gated_max"),
        ("M4_Top1_FG_Slot", "m4_top1_slot"),
    ]
    
    print("\n" + "="*85)
    print(f"{'Mechanism':<30} | {'Seen AUROC':<11} | {'Seen Pair':<11} | {'U AUROC':<11} | {'U Pair':<11}")
    print("-" * 85)
    
    comparison = {}
    for name, key in mechanisms:
        se_auc = compute_auc(splits_data["seen"]["labels"], splits_data["seen"][key])
        se_pair = pair_metrics(splits_data["seen"][key], splits_data["seen"]["labels"], splits_data["seen"]["queries"])["macro_pair_acc"]
        
        u_auc = compute_auc(splits_data["u"]["labels"], splits_data["u"][key])
        u_pair = pair_metrics(splits_data["u"][key], splits_data["u"]["labels"], splits_data["u"]["queries"])["macro_pair_acc"]
        
        print(f"{name:<30} | {se_auc:<11.4f} | {se_pair:<11.4f} | {u_auc:<11.4f} | {u_pair:<11.4f}")
        comparison[name] = {
            "Seen_AUROC": se_auc,
            "Seen_macro_pair_acc": se_pair,
            "U_AUROC": u_auc,
            "U_macro_pair_acc": u_pair,
        }
    print("="*85)
    
    out_file = AGY_TEST / "report/SLOT_MECHANISMS_COMPARISON.json"
    with open(out_file, "w") as f:
        json.dump(comparison, f, indent=2)
    print(f"Saved comparison to {out_file}")

if __name__ == "__main__":
    main()
