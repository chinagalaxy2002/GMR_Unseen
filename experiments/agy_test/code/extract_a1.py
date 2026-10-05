#!/usr/bin/env python3
"""
Feature extraction and standardization for split A1 across QD, Moment, and FlashVTG.
Also prepares unified data_views and feature caches for all 5 splits (A1, A2_alt, A3, C1, C2_alt) in experiments/agy_test.
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
from easydict import EasyDict
from torch.utils.data import DataLoader

REPO = Path(__file__).resolve().parents[3]
AGY_TEST = REPO / "experiments/agy_test"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments/gmr_unseen_existence_20261005/cross_confirmation/code"))

import common
from common import VIDEO_ROOT, checkpoint_path, sha256

def setup_unified_views_and_features():
    """Symlink / set up data views and existing features for A2_alt, A3, C1, C2_alt."""
    cross_conf = REPO / "experiments/gmr_unseen_existence_20261005/cross_confirmation"
    final_a1_qd = REPO / "experiments/gmr_unseen_existence_20261005/final_confirmation_A1_QD"
    
    views_dir = AGY_TEST / "data_views"
    features_dir = AGY_TEST / "cache/features"
    views_dir.mkdir(parents=True, exist_ok=True)
    features_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up A1 data views
    a1_views = views_dir / "A1"
    a1_views.mkdir(parents=True, exist_ok=True)
    for subset in ["train", "seen", "u"]:
        src = final_a1_qd / f"data_views/A1/{subset}.jsonl"
        dst = a1_views / f"{subset}.jsonl"
        if not dst.exists() and src.exists():
            shutil.copy2(src, dst)
            print(f"Copied A1 view {subset}.jsonl")
            
    # Set up other 4 splits views
    for sp in ["A2_alt", "A3", "C1", "C2_alt"]:
        sp_view = views_dir / sp
        sp_view.mkdir(parents=True, exist_ok=True)
        for subset in ["train", "seen", "u"]:
            src = cross_conf / f"data_views/{sp}/{subset}.jsonl"
            dst = sp_view / f"{subset}.jsonl"
            if not dst.exists() and src.exists():
                shutil.copy2(src, dst)
                
    # Set up other 4 splits features
    for sp in ["A2_alt", "A3", "C1", "C2_alt"]:
        sp_feat = features_dir / sp
        sp_feat.mkdir(parents=True, exist_ok=True)
        for bb in ["qd", "moment", "flash"]:
            bb_feat = sp_feat / bb
            bb_feat.mkdir(parents=True, exist_ok=True)
            for subset in ["train", "seen", "u"]:
                src_npz = cross_conf / f"cache/features/{sp}/{bb}/{subset}.npz"
                dst_npz = bb_feat / f"{subset}.npz"
                src_jsonl = cross_conf / f"cache/features/{sp}/{bb}/{subset}.jsonl"
                dst_jsonl = bb_feat / f"{subset}.jsonl"
                if not dst_npz.exists() and src_npz.exists():
                    try:
                        dst_npz.symlink_to(src_npz)
                    except Exception:
                        shutil.copy2(src_npz, dst_npz)
                if not dst_jsonl.exists() and src_jsonl.exists():
                    try:
                        dst_jsonl.symlink_to(src_jsonl)
                    except Exception:
                        shutil.copy2(src_jsonl, dst_jsonl)
    print("Unified data_views and features initialized for A2_alt, A3, C1, C2_alt.")

def standardize_a1_qd():
    """Standardize A1 QD features from final_confirmation_A1_QD to match cross_confirmation layout."""
    final_a1 = REPO / "experiments/gmr_unseen_existence_20261005/final_confirmation_A1_QD/cache/features/A1"
    target_dir = AGY_TEST / "cache/features/A1/qd"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    for subset in ["train", "seen", "u"]:
        src_npz = final_a1 / f"{subset}.npz"
        dst_npz = target_dir / f"{subset}.npz"
        dst_jsonl = target_dir / f"{subset}.jsonl"
        
        if dst_npz.exists() and dst_jsonl.exists():
            print(f"A1 QD {subset} already exists at {dst_npz}")
            continue
            
        print(f"Standardizing A1 QD {subset}...")
        data = np.load(src_npz)
        cxw = data["spans_cxw"]
        # Convert cxw to spans_xx [c - w/2, c + w/2]
        spans_xx = np.stack([cxw[..., 0] - cxw[..., 1] / 2, cxw[..., 0] + cxw[..., 1] / 2], axis=-1)
        spans_xx = np.clip(spans_xx, 0.0, 1.0)
        fg = data["foreground_scores"]
        mask = np.ones(fg.shape, dtype=bool)
        
        np.savez_compressed(
            dst_npz,
            local_video=data["local_video"],
            query_mean=data["query_mean"],
            spans_xx=spans_xx,
            foreground_scores=fg,
            candidate_mask=mask,
            original_exist_logits=data["original_exist_logits"],
            video_lengths=data["video_lengths"],
            labels=data["labels"],
            qids=data["qids"],
            vids=data["vids"],
            durations=data["durations"],
        )
        # Create metadata jsonl from data_views
        view_file = AGY_TEST / f"data_views/A1/{subset}.jsonl"
        rows = [json.loads(line) for line in view_file.read_text().splitlines() if line.strip()]
        dst_jsonl.write_text("".join(json.dumps({
            "qid": row["qid"], "vid": row["vid"], "query": row["query"],
            "label": int(bool(row.get("relevant_windows"))), "duration": float(row["duration"]),
            "gt_windows": row.get("relevant_windows", []),
        }, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
        print(f"Saved standardized A1 QD {subset}.npz ({len(rows)} rows)")

def crop_weighted_mean(video: torch.Tensor, span_xx: torch.Tensor, valid_length: int) -> torch.Tensor:
    n = int(valid_length)
    values = video[:n]
    start, end = span_xx.float().unbind(-1)
    start, end = start.clamp(0, 1), end.clamp(0, 1)
    bins = torch.arange(n, device=video.device, dtype=torch.float32)
    left, right = bins / n, (bins + 1) / n
    weights = (torch.minimum(end, right) - torch.maximum(start, left)).clamp_min(0)
    total = weights.sum()
    if float(total) <= 1e-8:
        idx = int(torch.clamp(torch.floor((start + end) * 0.5 * n), 0, n - 1))
        return values[idx]
    return (values * weights[:, None]).sum(0) / total

def extract_backbone_subset(split: str, backbone: str, subset: str, device_str: str):
    target_dir = AGY_TEST / f"cache/features/{split}/{backbone}"
    target_dir.mkdir(parents=True, exist_ok=True)
    dst_npz = target_dir / f"{subset}.npz"
    dst_jsonl = target_dir / f"{subset}.jsonl"
    if dst_npz.exists() and dst_jsonl.exists():
        print(f"{split}/{backbone}/{subset} already exists at {dst_npz}, skipping.")
        return

    device = torch.device(device_str)
    checkpoint_file = checkpoint_path(split, backbone)
    checkpoint = torch.load(checkpoint_file, map_location="cpu", weights_only=False)
    raw_opt = checkpoint["opt"]
    options = dict(raw_opt) if isinstance(raw_opt, dict) else vars(raw_opt).copy()
    options["device"] = str(device) if backbone != "flash" else device
    options["train_path"] = str(AGY_TEST / f"data_views/{split}/train.jsonl")
    options["eval_path"] = str(AGY_TEST / f"data_views/{split}/{subset}.jsonl")
    options["results_dir"] = str(AGY_TEST / f"runs/{split}/{backbone}")
    options["t_feat_dir"] = str(REPO / "features/semantic_existence_v2" / split / "clip_text")
    options["v_feat_dirs"] = [str(VIDEO_ROOT / "vid_slowfast"), str(VIDEO_ROOT / "vid_clip")] if backbone == "flash" else [str(VIDEO_ROOT / "vid_clip"), str(VIDEO_ROOT / "vid_slowfast")]
    options["num_workers"] = 0
    
    capture: dict[str, torch.Tensor] = {}

    if backbone == "moment":
        from training.moment_detr_gmr.dataset import StartEndDataset, prepare_batch_inputs, start_end_collate
        from models.moment_detr_gmr.moment_detr import build_model
        opt = EasyDict(options)
        model, _ = build_model(opt)
        dataset = StartEndDataset(
            dset_name=opt.dset_name, domain=None, data_path=opt.eval_path, v_feat_dirs=opt.v_feat_dirs,
            a_feat_dirs=None, q_feat_dir=opt.t_feat_dir, q_feat_type="last_hidden_state",
            v_feat_types=opt.v_feat_types, a_feat_types=None, max_q_l=int(opt.max_q_l),
            max_v_l=int(opt.max_v_l), max_a_l=int(getattr(opt, "max_a_l", 75)), ctx_mode=opt.ctx_mode,
            clip_len=int(opt.clip_length), max_windows=int(opt.max_windows), span_loss_type=opt.span_loss_type,
            load_labels=True, mr_only=True, keep_empty_gt=True,
        )
        loader_config = (prepare_batch_inputs, start_end_collate, int(opt.batch_size) if hasattr(opt, "batch_size") else 16)
    elif backbone == "flash":
        import nncore
        from training.flash_vtg_gmr.dataset import StartEndDataset, prepare_batch_inputs, start_end_collate
        from models.flash_vtg_gmr.model import build_model1
        opt = SimpleNamespace(**options)
        opt.cfg = nncore.Config.from_file(str(REPO / opt.config))
        model, _ = build_model1(opt)
        dataset = StartEndDataset(
            dset_name=opt.dset_name, data_path=opt.eval_path, v_feat_dirs=opt.v_feat_dirs,
            q_feat_dir=opt.t_feat_dir, q_feat_type=opt.q_feat_type, max_q_l=opt.max_q_l,
            max_v_l=opt.max_v_l, ctx_mode=opt.ctx_mode, data_ratio=1.0,
            normalize_v=not bool(getattr(opt, "no_norm_vfeat", False)),
            normalize_t=not bool(getattr(opt, "no_norm_tfeat", False)), clip_len=opt.clip_length,
            max_windows=opt.max_windows, load_labels=True, span_loss_type=opt.span_loss_type,
            txt_drop_ratio=0, dset_domain=getattr(opt, "dset_domain", None), mr_only=True, keep_empty_gt=True,
        )
        loader_config = (prepare_batch_inputs, start_end_collate, 1)
    else:
        raise ValueError(f"Unsupported backbone: {backbone}")

    missing, unexpected = model.load_state_dict(checkpoint["model"], strict=False)
    if missing or unexpected:
        print(f"Warning for {split}/{backbone}: missing={len(missing)}, unexpected={len(unexpected)}")
    model.to(device).eval()

    hooks = [
        model.input_vid_proj.register_forward_hook(lambda _m, _i, out: capture.__setitem__("video", out.detach())),
        model.input_txt_proj.register_forward_hook(lambda _m, _i, out: capture.__setitem__("text", out.detach())),
    ]

    prepare_batch_inputs, collate, default_batch = loader_config
    batch_size = 1 if backbone == "flash" else default_batch
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0, collate_fn=collate)

    local_parts, qmean_parts, span_parts, fg_parts, mask_parts, exist_parts, vlen_parts = [], [], [], [], [], [], []
    metadata = []

    print(f"Extracting {split}/{backbone}/{subset} on {device} ({len(dataset)} items)...", flush=True)
    with torch.no_grad():
        for batch_idx, batch in enumerate(loader):
            batch_meta = batch[0]
            model_inputs, targets = prepare_batch_inputs(batch[1], device)
            capture.clear()
            if backbone == "flash":
                flash_targets = {} if targets is None else targets
                flash_targets["label"] = batch_meta
                output = model(**model_inputs, targets=flash_targets)
                boundary = output.get("_out", {}).get("boundary")
                boundaries = boundary[:, :2].unsqueeze(0).float()
                scores = boundary[:, 2].unsqueeze(0).float()
                spans = torch.stack(((boundaries[..., 0] + boundaries[..., 1]) / 2,
                                     (boundaries[..., 1] - boundaries[..., 0]).clamp_min(0)), dim=-1)
                durations = torch.tensor([float(row["duration"]) for row in batch_meta], device=device)
                spans = spans / durations[:, None, None].clamp_min(1e-8)
            else:
                output = model(**model_inputs)
                cxw = output["pred_spans"].float()
                spans = torch.stack((cxw[..., 0] - cxw[..., 1] / 2, cxw[..., 0] + cxw[..., 1] / 2), dim=-1).clamp(0, 1)
                scores = output["pred_logits"].float().softmax(-1)[..., 0]

            video_proj = capture["video"].float()
            text_proj = capture["text"].float()
            video_mask = model_inputs["src_vid_mask"].bool()
            text_mask = model_inputs["src_txt_mask"].bool()

            local_batch, qmean_batch, lens = [], [], []
            for bi, row in enumerate(batch_meta):
                valid_v = int(video_mask[bi].sum().item())
                valid_q = int(text_mask[bi].sum().item())
                proposals = spans[bi]
                local_batch.append(torch.stack([crop_weighted_mean(video_proj[bi], proposals[ki], valid_v)
                                                for ki in range(proposals.shape[0])]))
                qmean_batch.append(text_proj[bi, :valid_q].mean(dim=0))
                lens.append(valid_v)

            local_parts.append(torch.stack(local_batch).cpu().numpy().astype(np.float32))
            qmean_parts.append(torch.stack(qmean_batch).cpu().numpy().astype(np.float32))
            span_parts.append(spans.cpu().numpy().astype(np.float32))
            fg_parts.append(scores.cpu().numpy().astype(np.float32))
            mask_parts.append(np.ones(scores.shape, dtype=np.bool_))
            exist_parts.append(output["pred_exist_logits"].reshape(-1).float().cpu().numpy().astype(np.float32))
            vlen_parts.append(np.asarray(lens, dtype=np.int32))
            metadata.extend(batch_meta)

            if (batch_idx + 1) % 200 == 0 or (batch_idx + 1) == len(loader):
                print(f"  {split}/{backbone}/{subset}: {batch_idx + 1}/{len(loader)}", flush=True)

    labels = np.asarray([int(bool(row.get("relevant_windows"))) for row in metadata], dtype=np.int8)
    max_candidates = max(part.shape[1] for part in local_parts)

    def pad_candidates(parts, fill_value):
        padded = []
        for part in parts:
            pad_k = max_candidates - part.shape[1]
            if part.ndim == 3:
                padded.append(np.pad(part, ((0, 0), (0, pad_k), (0, 0)), constant_values=fill_value))
            else:
                padded.append(np.pad(part, ((0, 0), (0, pad_k)), constant_values=fill_value))
        return np.concatenate(padded)

    np.savez_compressed(
        dst_npz,
        local_video=pad_candidates(local_parts, 0),
        query_mean=np.concatenate(qmean_parts),
        spans_xx=pad_candidates(span_parts, 0),
        foreground_scores=pad_candidates(fg_parts, -np.inf),
        candidate_mask=pad_candidates(mask_parts, False),
        original_exist_logits=np.concatenate(exist_parts),
        video_lengths=np.concatenate(vlen_parts),
        labels=labels,
        qids=np.asarray([str(row["qid"]) for row in metadata], dtype="U64"),
        vids=np.asarray([str(row["vid"]) for row in metadata], dtype="U128"),
        durations=np.asarray([float(row["duration"]) for row in metadata], dtype=np.float32),
    )
    dst_jsonl.write_text("".join(json.dumps({
        "qid": row["qid"], "vid": row["vid"], "query": row["query"],
        "label": int(bool(row.get("relevant_windows"))), "duration": float(row["duration"]),
        "gt_windows": row.get("relevant_windows", []),
    }, ensure_ascii=False) + "\n" for row in metadata), encoding="utf-8")

    for hook in hooks:
        hook.remove()
    del model, dataset, checkpoint
    if device.type == "cuda":
        torch.cuda.empty_cache()
    print(f"Completed {split}/{backbone}/{subset} saved to {dst_npz}", flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backbone", choices=["moment", "flash", "setup_only"], default="setup_only")
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()

    setup_unified_views_and_features()
    standardize_a1_qd()

    if args.backbone == "moment":
        for subset in ["seen", "u", "train"]:
            extract_backbone_subset("A1", "moment", subset, args.device)
    elif args.backbone == "flash":
        for subset in ["seen", "u", "train"]:
            extract_backbone_subset("A1", "flash", subset, args.device)

if __name__ == "__main__":
    main()
