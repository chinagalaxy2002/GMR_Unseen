"""Training script for Moment-Conditioned Event Verification (MCEV)."""
import argparse
import fcntl
import hashlib
import json
import os
import random
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

from environment import ROOT, E0_CHECKPOINTS, E0_VAL_PREDICTIONS, make_dataset, options, read_json, seed_all, write_json, write_rows
from model import MCEVModel, compute_mcev_loss
from validation import predictions, validate
from models.flash_vtg_gmr.model import build_model1
from training.flash_vtg_gmr.dataset import prepare_batch_inputs, start_end_collate


def atomic_checkpoint(path, payload):
    temporary = path.with_suffix('.tmp')
    torch.save(payload, temporary)
    temporary.replace(path)


def set_training_mode(model):
    model.train()
    # Keep dropout in trainable modules; freeze dropout in the frozen localizer backbone
    trainable_modules = {module for module in model.modules() if any(p.requires_grad for p in module.parameters(recurse=False))}
    for module in model.base.modules():
        if isinstance(module, (torch.nn.Dropout, torch.nn.modules.batchnorm._BatchNorm)) and module not in trainable_modules:
            module.eval()


def execute(args):
    jobs = read_json(ROOT / 'configs/jobs.json')['jobs']
    job_cfg = next(row for row in jobs if row['run_id'] == args.job)
    job = dict(job_cfg)
    job.update(seed=args.seed, epochs=args.epochs, early_stop_patience=args.patience)
    
    run_name = args.run_name or f"{args.job}_s{args.seed}"
    run_dir = ROOT / 'runs' / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    
    lock_file = (run_dir / 'run.lock').open('a')
    fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    
    if (run_dir / 'COMPLETE.json').exists():
        print(f"{run_name} already complete.")
        return

    init_checkpoint = E0_CHECKPOINTS[args.seed]
    if not init_checkpoint.exists():
        raise FileNotFoundError(f"Missing E0 baseline checkpoint for seed {args.seed}: {init_checkpoint}")
        
    ref_predictions = E0_VAL_PREDICTIONS[args.seed]
    if not ref_predictions.exists():
        raise FileNotFoundError(f"Missing E0 Val reference predictions for seed {args.seed}: {ref_predictions}")

    opt = options(job, args.device)
    try:
        torch.use_deterministic_algorithms(True)
    except Exception:
        pass
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    seed_all(job['seed'])

    base, _ = build_model1(opt)
    model = MCEVModel(base, job).to(opt.device)

    checkpoint = torch.load(init_checkpoint, map_location='cpu', weights_only=False)
    loaded = model.load_state_dict(checkpoint['model'], strict=False)
    
    # Freeze all localizer parameters
    for name, parameter in model.named_parameters():
        parameter.requires_grad = ('exist_head' in name)
        
    trainable = [p for p in model.parameters() if p.requires_grad]
    frozen_snapshot = {
        name: tensor.detach().cpu().clone()
        for name, tensor in model.state_dict().items()
        if 'exist_head' not in name
    }

    train_data = make_dataset(opt, 'train')
    val_data = make_dataset(opt, 'val')

    generator = torch.Generator().manual_seed(job['seed'])
    loader = DataLoader(
        train_data, batch_size=opt.bsz, shuffle=True, num_workers=0,
        collate_fn=start_end_collate, generator=generator,
    )
    
    optimizer = torch.optim.AdamW(trainable, lr=job.get('lr', 3e-5), weight_decay=job.get('wd', 1e-4), foreach=False)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=job.get('lr_drop', 12), gamma=0.5)

    selection_metric = job.get('selection_metric', 'AUROC') # 'AUROC' or 'val_G'
    best_score = -1.0
    stale = 0
    start_epoch = 0

    write_json(run_dir / 'CONFIG.json', {
        'job': job,
        'seed': args.seed,
        'device': args.device,
        'trainable_params': sum(p.numel() for p in trainable),
        'frozen_params': sum(p.numel() for p in model.parameters() if not p.requires_grad),
        'selection_metric': selection_metric,
        'init_checkpoint': str(init_checkpoint),
        'localizer_contract': 'pred_relevant_windows_pre_exist must be bitwise invariant to E0',
    })

    print(f"\n[{run_name}] Started training on {args.device} (Seed {args.seed})")
    print(f"[{run_name}] Selection Metric: {selection_metric}, Trainable params: {sum(p.numel() for p in trainable):,}")

    for epoch in range(start_epoch, job['epochs']):
        epoch_start = time.time()
        set_training_mode(model)
        total_losses = {}
        batches = 0

        for batch_meta, batch_inputs in loader:
            model_inputs, targets = prepare_batch_inputs(batch_inputs, opt.device, non_blocking=False)
            targets.update(label=batch_meta, fps=torch.full((len(batch_meta),), 1.0 / opt.clip_length, device=opt.device))

            output = model(**model_inputs, targets=targets)
            loss, details = compute_mcev_loss(output, batch_meta, targets, job, model=model, model_inputs=model_inputs)

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            norm = torch.nn.utils.clip_grad_norm_(trainable, job.get('grad_clip', 0.1), error_if_nonfinite=True)
            optimizer.step()

            batches += 1
            for name, value in details.items():
                total_losses[name] = total_losses.get(name, 0.0) + float(value.detach())

            if batches == 1 or batches % 100 == 0:
                write_json(run_dir / 'STATUS.json', {
                    'state': 'training', 'epoch': epoch + 1, 'batch': batches,
                    'loss': float(loss.detach()), 'grad_norm': float(norm),
                    'updated': time.time(),
                })

        scheduler.step()

        # Invariance check: verify zero drift in frozen localizer
        for name, tensor in frozen_snapshot.items():
            if not torch.equal(model.state_dict()[name].detach().cpu(), tensor):
                raise AssertionError(f"Frozen parameter drift detected in {name}!")

        # Validation
        model.eval()
        pre, post = predictions(model, val_data, opt)
        report = validate(pre, post, val_data.data, opt, reference_path=ref_predictions)

        current_score = report['AUROC'] if selection_metric == 'AUROC' else report['val_G_threshold']['G-mIoU@1']
        improved = current_score > best_score
        if improved:
            best_score = current_score
            stale = 0
        else:
            stale += 1

        state = {
            'epoch': epoch + 1,
            'best_score': best_score,
            'stale': stale,
            'model': model.state_dict(),
            'optimizer': optimizer.state_dict(),
            'scheduler': scheduler.state_dict(),
        }

        if improved:
            atomic_checkpoint(run_dir / 'best.ckpt', state)
            write_json(run_dir / 'validation_metrics.json', report)
            write_rows(run_dir / 'validation_predictions.jsonl', post)
            write_rows(run_dir / 'validation_predictions_pre_nms.jsonl', pre)
            write_json(run_dir / 'selected.json', {
                'epoch': epoch + 1,
                'score': current_score,
                'AUROC': report['AUROC'],
                'val_G_05': report['fixed_05']['G-mIoU@1'],
                'val_G_calib': report['val_G_threshold']['G-mIoU@1'],
                'val_BA_calib': report['val_BA_threshold']['G-mIoU@1'],
                'neg_rec_05': report['fixed_05']['negative_recall'],
                'pos_rec_05': report['fixed_05']['positive_recall'],
            })

        atomic_checkpoint(run_dir / 'latest.ckpt', state)

        record = {
            'epoch': epoch + 1,
            'seconds': round(time.time() - epoch_start, 1),
            'improved': improved,
            'losses': {k: v / batches for k, v in total_losses.items()},
            'AUROC': report['AUROC'],
            'G@0.4': report['gate_04']['G-mIoU@1'],
            'G@0.5': report['fixed_05']['G-mIoU@1'],
            'G@Val_G': report['val_G_threshold']['G-mIoU@1'],
            'NegRec@0.5': report['fixed_05']['negative_recall'],
            'PosRec@0.5': report['fixed_05']['positive_recall'],
            'max_gmiou_scan': report['max_gmiou_scan'],
        }

        with (run_dir / 'trace.jsonl').open('a') as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')

        print(f"[{run_name} Epoch {epoch+1:02d}] AUROC: {report['AUROC']:.2f}% | "
              f"G@0.5: {report['fixed_05']['G-mIoU@1']:.2f}% | "
              f"Val-G: {report['val_G_threshold']['G-mIoU@1']:.2f}% | "
              f"NegRec: {report['fixed_05']['negative_recall']:.1f}% | "
              f"PosRec: {report['fixed_05']['positive_recall']:.1f}% | "
              f"Loss: {record['losses']['loss_total']:.4f} "
              f"{'(★ New Best!)' if improved else ''}", flush=True)

        if stale >= job.get('early_stop_patience', 15):
            print(f"[{run_name}] Early stopping triggered after {stale} stagnant epochs.")
            break

    write_json(run_dir / 'COMPLETE.json', {
        'state': 'complete',
        'best_score': best_score,
        'selection_metric': selection_metric,
        'epochs_trained': epoch + 1,
        'completed_at': time.time(),
    })
    write_json(run_dir / 'STATUS.json', {'state': 'complete', 'best_score': best_score, 'updated': time.time()})
    print(f"[{run_name}] Training finished successfully. Best {selection_metric}: {best_score:.2f}%")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job', required=True)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--seed', type=int, default=2026)
    parser.add_argument('--epochs', type=int, default=40)
    parser.add_argument('--patience', type=int, default=15)
    parser.add_argument('--run-name')
    args = parser.parse_args()
    execute(args)


if __name__ == '__main__':
    main()
