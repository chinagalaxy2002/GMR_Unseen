#!/usr/bin/env python3
"""
End-to-End Training and Evaluation for Quality-Aware Slot Witness (QSW) QD-DETR.
Trains directly on video/text dataset batches, completely self-contained in experiments/agy_test/e2e_training.
"""
from __future__ import annotations
import argparse
import datetime
import json
import os
import random
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
import torch.nn.functional as F
from easydict import EasyDict
from sklearn.metrics import roc_auc_score
from torch import nn
from torch.utils.data import DataLoader
from tqdm import tqdm

REPO = Path(__file__).resolve().parents[3]
AGY_TEST = REPO / "experiments/agy_test"
sys.path.insert(0, str(REPO / "experiments/gmr_unseen_existence_20261005/cross_confirmation/code"))
sys.path.insert(0, str(REPO))

import common
from common import VIDEO_ROOT, checkpoint_path
from experiments.agy_test.e2e_training.models.qsw_qd_detr import build_qsw_qd_model
from experiments.agy_test.e2e_training.models.qsw_adapter import compute_qsw_existence_loss
from training.qd_detr_gmr.dataset import StartEndDataset, prepare_batch_inputs, start_end_collate

def set_seed(seed=3407):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def compute_auc(y_true, y_score):
    try:
        y = np.asarray(y_true, dtype=np.int8)
        s = np.asarray(y_score, dtype=np.float64)
        if len(np.unique(y)) < 2:
            return 0.5
        return float(roc_auc_score(y, s))
    except Exception:
        return 0.5

def youden_threshold(y_true, y_score):
    y_true = np.asarray(y_true, dtype=bool)
    n_pos = y_true.sum()
    n_neg = len(y_true) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float(np.median(y_score))
    thresholds = np.unique(y_score)
    if len(thresholds) > 1000:
        thresholds = np.quantile(y_score, np.linspace(0, 1, 1000))
    best_j, best_th = -1.0, float(thresholds[0])
    for th in thresholds:
        pred = y_score >= th
        tpr = (pred & y_true).sum() / n_pos
        fpr = (pred & ~y_true).sum() / n_neg
        j = tpr - fpr
        if j > best_j:
            best_j = j
            best_th = float(th)
    return best_th

def eval_epoch(model, loader, device, desc="Eval"):
    model.eval()
    all_scores, all_labels, all_qids, all_vids, all_durations = [], [], [], [], []
    all_spans, all_fg, all_gt_windows = [], [], []

    with torch.no_grad():
        for batch in loader:
            batch_meta = batch[0]
            model_inputs, targets = prepare_batch_inputs(batch[1], device)
            outputs = model(**model_inputs)

            exist_logits = outputs["pred_exist_logits"].detach().cpu().numpy()
            cxw = outputs["pred_spans"].detach().cpu().numpy() # [B, 10, 2]
            spans_xx = np.stack([cxw[..., 0] - cxw[..., 1] / 2, cxw[..., 0] + cxw[..., 1] / 2], axis=-1)
            fg_scores = outputs["pred_logits"].softmax(dim=-1)[..., 0].detach().cpu().numpy() # [B, 10]

            for bi, row in enumerate(batch_meta):
                all_scores.append(float(exist_logits[bi]))
                all_labels.append(int(bool(row.get("relevant_windows"))))
                all_qids.append(str(row["qid"]))
                all_vids.append(str(row["vid"]))
                all_durations.append(float(row["duration"]))
                all_spans.append(spans_xx[bi])
                all_fg.append(fg_scores[bi])
                all_gt_windows.append(row.get("relevant_windows", []))

    all_scores = np.asarray(all_scores, dtype=np.float32)
    all_labels = np.asarray(all_labels, dtype=np.int8)
    all_spans = np.asarray(all_spans, dtype=np.float32)
    all_fg = np.asarray(all_fg, dtype=np.float32)
    all_durations = np.asarray(all_durations, dtype=np.float32)

    auc = compute_auc(all_labels, all_scores)
    return {
        "auc": auc,
        "scores": all_scores,
        "labels": all_labels,
        "qids": all_qids,
        "vids": all_vids,
        "durations": all_durations,
        "spans": all_spans,
        "fg_scores": all_fg,
        "gt_windows": all_gt_windows,
    }

def eval_full_metrics(eval_res, threshold, split, is_test_u=False):
    scores = eval_res["scores"]
    labels = eval_res["labels"]
    qids = eval_res["qids"]
    vids = eval_res["vids"]
    durations = eval_res["durations"]
    spans = eval_res["spans"]
    fg_scores = eval_res["fg_scores"]
    gt_windows = eval_res["gt_windows"]

    auc = compute_auc(labels, scores)

    # 1. Matched PairAcc
    matched_pair_acc = None
    if is_test_u:
        pairs_file = REPO / f"data/release/semantic_existence_v2/{split}/matched_u_pairs.jsonl"
        if pairs_file.exists():
            pairs = [json.loads(l) for l in pairs_file.read_text().splitlines() if l.strip()]
            qid_to_score = {q: s for q, s in zip(qids, scores)}
            p_accs = []
            for p in pairs:
                pq, nq = str(p.get("positive_qid")), str(p.get("negative_qid"))
                if pq in qid_to_score and nq in qid_to_score:
                    sp, sn = qid_to_score[pq], qid_to_score[nq]
                    p_accs.append(1.0 if sp > sn else 0.5 if sp == sn else 0.0)
            matched_pair_acc = float(np.mean(p_accs)) if p_accs else 0.5

    # 2. Same Query PairAcc
    q_groups = {}
    for i, q in enumerate(qids):
        q_groups.setdefault(q, []).append(i)
    sq_accs = []
    for q, idxs in q_groups.items():
        pos = [i for i in idxs if labels[i] == 1]
        neg = [i for i in idxs if labels[i] == 0]
        for p in pos:
            for n in neg:
                sq_accs.append(1.0 if scores[p] > scores[n] else 0.5 if scores[p] == scores[n] else 0.0)
    same_q_acc = float(np.mean(sq_accs)) if sq_accs else None

    # 3. Detection and Gating
    raw_hits, gated_hits = [], []
    pos_total, pos_refused = 0, 0
    neg_total, neg_accepted = 0, 0

    for i in range(len(labels)):
        is_pos = (labels[i] == 1)
        dur = float(durations[i])
        accepted = (scores[i] >= threshold)

        if is_pos:
            pos_total += 1
            if not accepted:
                pos_refused += 1
            top1_k = int(np.argmax(fg_scores[i]))
            t_st, t_ed = spans[i, top1_k] * dur
            best_iou = 0.0
            for gw in gt_windows[i]:
                gst, ged = float(gw[0]), float(gw[1])
                inter = max(0.0, min(t_ed, ged) - max(t_st, gst))
                union = max(1e-12, t_ed - t_st + ged - gst - inter)
                best_iou = max(best_iou, inter / union)
            hit = (best_iou >= 0.5)
            raw_hits.append(float(hit))
            gated_hits.append(float(hit and accepted))
        else:
            neg_total += 1
            if accepted:
                neg_accepted += 1

    u_frr = (pos_refused / pos_total * 100.0) if pos_total > 0 else 0.0
    u_rr = ((1.0 - neg_accepted / neg_total) * 100.0) if neg_total > 0 else 0.0
    raw_r1 = (float(np.mean(raw_hits)) * 100.0) if raw_hits else 0.0
    gated_r1 = (float(np.mean(gated_hits)) * 100.0) if gated_hits else 0.0

    return {
        "AUROC": auc,
        "matched_pair_acc": matched_pair_acc,
        "same_query_pair_acc": same_q_acc,
        "U_pos_FRR": u_frr,
        "U_neg_RR": u_rr,
        "raw_R1@0.5": raw_r1,
        "gated_R1@0.5": gated_r1,
    }

def train_split(split: str, device_str: str = "cuda:0", n_epoch: int = 15, lr: float = 1e-4, train_mode: str = "adapter_and_decoder", seed: int = 3407):
    set_seed(seed)
    device = torch.device(device_str)

    run_dir = AGY_TEST / f"e2e_training/runs/{split}/qd"
    run_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Checkpoint and Build Options
    checkpoint_file = checkpoint_path(split, "qd")
    checkpoint = torch.load(checkpoint_file, map_location="cpu", weights_only=False)
    raw_opt = checkpoint["opt"]
    options = dict(raw_opt) if isinstance(raw_opt, dict) else vars(raw_opt).copy()
    options["device"] = str(device)
    options["train_path"] = str(AGY_TEST / f"data_views/{split}/train.jsonl")
    options["eval_path"] = str(AGY_TEST / f"data_views/{split}/seen.jsonl")
    options["test_path"] = str(AGY_TEST / f"data_views/{split}/u.jsonl")
    options["t_feat_dir"] = str(REPO / "features/semantic_existence_v2" / split / "clip_text")
    options["v_feat_dirs"] = [str(VIDEO_ROOT / "vid_clip"), str(VIDEO_ROOT / "vid_slowfast")]
    options["num_workers"] = 0
    opt = EasyDict(options)

    # 2. Build Model & Datasets
    model, criterion = build_qsw_qd_model(opt, checkpoint_file, device_str)

    train_dataset = StartEndDataset(
        dset_name=opt.dset_name, data_path=opt.train_path, v_feat_dirs=opt.v_feat_dirs,
        q_feat_dir=opt.t_feat_dir, q_feat_type="last_hidden_state", max_q_l=int(opt.max_q_l),
        max_v_l=int(opt.max_v_l), ctx_mode=opt.ctx_mode, clip_len=int(opt.clip_length),
        max_windows=int(opt.max_windows), span_loss_type=opt.span_loss_type,
        load_labels=True, mr_only=True, keep_empty_gt=True,
    )
    seen_dataset = StartEndDataset(
        dset_name=opt.dset_name, data_path=opt.eval_path, v_feat_dirs=opt.v_feat_dirs,
        q_feat_dir=opt.t_feat_dir, q_feat_type="last_hidden_state", max_q_l=int(opt.max_q_l),
        max_v_l=int(opt.max_v_l), ctx_mode=opt.ctx_mode, clip_len=int(opt.clip_length),
        max_windows=int(opt.max_windows), span_loss_type=opt.span_loss_type,
        load_labels=True, mr_only=True, keep_empty_gt=True,
    )
    u_dataset = StartEndDataset(
        dset_name=opt.dset_name, data_path=opt.test_path, v_feat_dirs=opt.v_feat_dirs,
        q_feat_dir=opt.t_feat_dir, q_feat_type="last_hidden_state", max_q_l=int(opt.max_q_l),
        max_v_l=int(opt.max_v_l), ctx_mode=opt.ctx_mode, clip_len=int(opt.clip_length),
        max_windows=int(opt.max_windows), span_loss_type=opt.span_loss_type,
        load_labels=True, mr_only=True, keep_empty_gt=True,
    )

    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True, num_workers=0, collate_fn=start_end_collate)
    seen_loader = DataLoader(seen_dataset, batch_size=16, shuffle=False, num_workers=0, collate_fn=start_end_collate)
    u_loader = DataLoader(u_dataset, batch_size=16, shuffle=False, num_workers=0, collate_fn=start_end_collate)

    # 3. Setup Parameter Groups & Optimizer
    if train_mode == "adapter_only":
        for p in model.parameters():
            p.requires_grad = False
        for p in model.qsw_adapter.parameters():
            p.requires_grad = True
        optimizer = torch.optim.AdamW(model.qsw_adapter.parameters(), lr=lr, weight_decay=1e-4)
    elif train_mode == "adapter_and_decoder":
        for p in model.parameters():
            p.requires_grad = False
        # Train decoder and QSW adapter
        for p in model.transformer.decoder.parameters():
            p.requires_grad = True
        for p in model.qsw_adapter.parameters():
            p.requires_grad = True
        params = [
            {"params": model.transformer.decoder.parameters(), "lr": lr * 0.1},
            {"params": model.qsw_adapter.parameters(), "lr": lr},
        ]
        optimizer = torch.optim.AdamW(params, weight_decay=1e-4)
    else:
        optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    # 4. Initial Baseline Check on Seen
    print(f"\n[{split}] Initializing Seen-validation evaluation (Epoch 0)...")
    init_seen = eval_epoch(model, seen_loader, device, desc="Epoch 0 Seen")
    print(f"[{split}] Epoch 0 Seen AUROC: {init_seen['auc']:.4f}")

    best_seen_auc = init_seen["auc"]
    best_epoch = 0
    best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
    history = []

    print(f"\n[{split}] Starting {n_epoch} epochs training ({train_mode}) on {device}...")
    for epoch in range(1, n_epoch + 1):
        model.train()
        total_loss, total_exist_loss = 0.0, 0.0
        n_batches = 0

        for batch in train_loader:
            batch_meta = batch[0]
            model_inputs, targets = prepare_batch_inputs(batch[1], device)
            outputs = model(**model_inputs)

            exist_labels = torch.tensor([int(bool(r.get("relevant_windows"))) for r in batch_meta], device=device)
            vids = [str(r["vid"]) for r in batch_meta]

            loss_exist = compute_qsw_existence_loss(
                outputs["pred_exist_logits"],
                exist_labels,
                pairwise_vids=vids,
                pair_weight=0.2
            )

            if train_mode == "adapter_only":
                loss = loss_exist
            else:
                loss_dict = criterion(outputs, targets)
                loc_loss = sum(loss_dict[k] * criterion.weight_dict[k] for k in loss_dict.keys() if k in criterion.weight_dict and k != "loss_exist")
                loss = loc_loss + loss_exist

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += float(loss.item())
            total_exist_loss += float(loss_exist.item())
            n_batches += 1

        # Validation after each epoch strictly on Seen
        seen_res = eval_epoch(model, seen_loader, device, desc=f"Epoch {epoch} Seen")
        seen_auc = seen_res["auc"]
        avg_loss = total_loss / max(1, n_batches)
        avg_exist = total_exist_loss / max(1, n_batches)

        is_best = seen_auc > best_seen_auc
        if is_best:
            best_seen_auc = seen_auc
            best_epoch = epoch
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        history.append({
            "epoch": epoch,
            "loss": avg_loss,
            "exist_loss": avg_exist,
            "seen_auc": seen_auc,
            "is_best": is_best
        })
        print(f"  [{split}] Ep {epoch:02d}/{n_epoch:02d} | Loss: {avg_loss:.4f} (Exist: {avg_exist:.4f}) | Seen AUC: {seen_auc:.4f} {'*** BEST' if is_best else ''}", flush=True)

    # 5. Final Evaluation with Best Checkpoint
    print(f"\n[{split}] Training complete. Loading best checkpoint from Epoch {best_epoch} (Seen AUC: {best_seen_auc:.4f})...")
    model.load_state_dict(best_state)
    best_ckpt_file = run_dir / "best_qsw.pt"
    torch.save({"model": best_state, "opt": opt, "best_epoch": best_epoch, "best_seen_auc": best_seen_auc}, best_ckpt_file)

    # Evaluate on Seen to calibrate Youden threshold
    final_seen = eval_epoch(model, seen_loader, device, desc="Final Seen")
    th_seen = youden_threshold(final_seen["labels"], final_seen["scores"])
    seen_metrics = eval_full_metrics(final_seen, th_seen, split, is_test_u=False)

    # Evaluate on Unseen test set
    print(f"[{split}] Evaluating on frozen Unseen test set (threshold = {th_seen:.4f})...")
    final_u = eval_epoch(model, u_loader, device, desc="Final Unseen")
    u_metrics = eval_full_metrics(final_u, th_seen, split, is_test_u=True)

    # Video Permutation Control (Dependency Test)
    # Permute videos across batches to test null hypothesis
    u_perm_scores = []
    with torch.no_grad():
        for batch in u_loader:
            batch_meta = batch[0]
            model_inputs, _ = prepare_batch_inputs(batch[1], device)
            # Permute video features in the batch
            n_b = model_inputs["src_vid"].shape[0]
            if n_b > 1:
                p_idx = torch.randperm(n_b, device=device)
                model_inputs["src_vid"] = model_inputs["src_vid"][p_idx]
                model_inputs["src_vid_mask"] = model_inputs["src_vid_mask"][p_idx]
            outputs = model(**model_inputs)
            u_perm_scores.extend(outputs["pred_exist_logits"].cpu().numpy().tolist())
    shuffled_u_auc = compute_auc(final_u["labels"], u_perm_scores)

    report = {
        "split": split,
        "backbone": "qd",
        "method": "QSW_QD_DETR",
        "train_mode": train_mode,
        "best_epoch": best_epoch,
        "seen_threshold": float(th_seen),
        "Seen_AUROC": seen_metrics["AUROC"],
        "Unseen_AUROC": u_metrics["AUROC"],
        "Seen_Unseen_Gap": seen_metrics["AUROC"] - u_metrics["AUROC"],
        "Matched_PairAcc": u_metrics["matched_pair_acc"],
        "Same_Query_PairAcc": u_metrics["same_query_pair_acc"],
        "U_pos_FRR": u_metrics["U_pos_FRR"],
        "U_neg_RR": u_metrics["U_neg_RR"],
        "Raw_R1@0.5": u_metrics["raw_R1@0.5"],
        "Gated_R1@0.5": u_metrics["gated_R1@0.5"],
        "Shuffled_Video_U_AUROC": shuffled_u_auc,
        "history": history,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    # Save raw predictions for complete reproducibility and verification
    np.savez_compressed(
        run_dir / "predictions.npz",
        seen_scores=final_seen["scores"],
        seen_labels=final_seen["labels"],
        seen_qids=final_seen["qids"],
        u_scores=final_u["scores"],
        u_labels=final_u["labels"],
        u_qids=final_u["qids"],
        u_perm_scores=np.asarray(u_perm_scores, dtype=np.float32),
    )

    report_file = run_dir / "results.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n==================== [{split}] FINAL EVALUATION ====================", flush=True)
    print(f"  Seen AUROC:       {seen_metrics['AUROC']:.4f}", flush=True)
    print(f"  Unseen AUROC:     {u_metrics['AUROC']:.4f}", flush=True)
    print(f"  Seen-Unseen Gap:  {seen_metrics['AUROC'] - u_metrics['AUROC']:.4f}", flush=True)
    print(f"  Matched PairAcc:  {u_metrics['matched_pair_acc']:.4f}", flush=True)
    print(f"  U+ False Refusal: {u_metrics['U_pos_FRR']:.1f}%", flush=True)
    print(f"  U- Rejection:     {u_metrics['U_neg_RR']:.1f}%", flush=True)
    print(f"  Gated R1@0.5:     {u_metrics['gated_R1@0.5']:.1f}%", flush=True)
    print(f"  Shuffled-U AUC:   {shuffled_u_auc:.4f}", flush=True)
    print(f"===================================================================\n", flush=True)
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="A1")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--train_mode", default="adapter_and_decoder", choices=["adapter_only", "adapter_and_decoder", "full"])
    parser.add_argument("--seed", type=int, default=3407)
    args = parser.parse_args()

    train_split(args.split, args.device, n_epoch=args.epochs, lr=args.lr, train_mode=args.train_mode, seed=args.seed)

if __name__ == "__main__":
    main()
