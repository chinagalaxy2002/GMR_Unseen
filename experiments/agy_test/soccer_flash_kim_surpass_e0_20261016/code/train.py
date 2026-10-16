"""Full training entry incorporating Schemes A, B, C, D:
- Scheme A: Two-Stage Decoupled Training (freeze backbone, train Event Query)
- Scheme B: Plurality-Conditioned Dynamic Filtering in evaluation
- Scheme C: Focal Loss for Presence + Aligned Weights (lambda_exist=0.1, lambda_multi=0.01)
- Scheme D: Dual Synthetic Data Augmentation (tau_no=0.08, tau_mul=0.05)
- Dual Checkpoint Saving: best.ckpt (GMR composite) and best_loc.ckpt (Localization peak)
- Strict budget: at most 60 epochs
"""
import argparse
import fcntl
import os
import time
import json
import random
import hashlib
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

from environment import ROOT, options, make_dataset, seed_all, write_json, write_rows, read_json, read_rows
from models.flash_vtg_gmr.model import build_model1
from training.flash_vtg_gmr.dataset import start_end_collate, prepare_batch_inputs
from model import RetrievalModel, plurality_loss
from data_augmentation import apply_kim_augmentation
from validation import predictions, validate, evaluate_on_test

def atomic_checkpoint(path, payload):
    temp = path.with_suffix('.tmp')
    torch.save(payload, temp)
    temp.replace(path)

def compute_focal_loss(logits, targets, gamma=2.0, alpha=0.5):
    """Focal Loss (Scheme C) to suppress overconfident positive gradients and center decision boundary at 0.5."""
    p = torch.sigmoid(logits)
    p_t = p * targets + (1.0 - p) * (1.0 - targets)
    alpha_t = alpha * targets + (1.0 - alpha) * (1.0 - targets)
    focal_weight = alpha_t * ((1.0 - p_t) ** gamma)
    loss = -focal_weight * torch.log(p_t.clamp(min=1e-7))
    return loss.mean()

def execute(a):
    jobs = read_json(ROOT / 'configs/jobs.json')['jobs']
    job = next(j for j in jobs if j['run_id'] == a.job)
    job = {**job}
    if a.smoke:
        job['epochs'] = a.smoke_epochs

    identity = {
        'job': job,
        'smoke': a.smoke,
        'initialization': 'scratch',
        'baseline': 'E0',
        'selection': 'GMR composite & native pre-NMS mAP on Val only'
    }
    cfg_hash = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    run = ROOT / ('tests/smoke' if a.smoke else 'runs') / (a.smoke_name if a.smoke else a.job)
    run.mkdir(parents=True, exist_ok=True)
    
    lock = (run / 'run.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

    if (run / 'COMPLETE.json').exists():
        print(f"Job {a.job} already completed. Skipping.")
        return

    opt = options(job, a.device)
    if a.smoke:
        torch.use_deterministic_algorithms(True)
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True

    seed_all(job['seed'])
    base, criterion = build_model1(opt)
    model = RetrievalModel(base, job).to(opt.device)

    if job.get('init_from_e0', False):
        e0_path = ROOT.parents[0] / 'soccer_flash_event_query_20261015/runs/E0/best.ckpt'
        if e0_path.exists():
            print(f"Initializing backbone from E0 baseline checkpoint: {e0_path}...", flush=True)
            e0_ck = torch.load(e0_path, map_location='cpu', weights_only=False)
            load_res = model.load_state_dict(e0_ck['model'], strict=False)
            print(f"Loaded E0 weights. Missing: {len(load_res.missing_keys)}, unexpected: {len(load_res.unexpected_keys)}", flush=True)
            if job.get('freeze_backbone', True):
                for name, param in model.named_parameters():
                    param.requires_grad = ('exist_head' in name)
                trainable_cnt = sum(p.numel() for p in model.parameters() if p.requires_grad)
                print(f"Frozen backbone parameters. Trainable parameters for Event Query: {trainable_cnt}", flush=True)

    seed_all(job['seed'])
    train_ds = make_dataset(opt, 'train', a.smoke)
    val_ds = make_dataset(opt, 'val', a.smoke)
    generator = torch.Generator().manual_seed(job['seed'])

    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=job['lr'], weight_decay=job['wd'], foreach=False)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, opt.lr_drop, gamma=0.5)

    start_epoch = 0
    best_loc_score = -float('inf') if a.smoke else 0.0
    best_gmr_score = -float('inf') if a.smoke else 0.0
    es_count = 0

    if (run / 'latest.ckpt').exists():
        ck = torch.load(run / 'latest.ckpt', map_location='cpu', weights_only=False)
        model.load_state_dict(ck['model'])
        optimizer.load_state_dict(ck['optimizer'])
        scheduler.load_state_dict(ck['scheduler'])
        generator.set_state(ck['sampler_rng'])
        random.setstate(ck['python_rng'])
        np.random.set_state(ck['numpy_rng'])
        torch.set_rng_state(ck['torch_rng'])
        if torch.cuda.is_available():
            torch.cuda.set_rng_state_all(ck['cuda_rng'])
        start_epoch = ck['epoch']
        best_loc_score = ck.get('best_loc', ck.get('best', 0.0))
        best_gmr_score = ck.get('best_gmr', 0.0)
        es_count = ck['es']
        history = read_rows(run / 'trace.jsonl') if (run / 'trace.jsonl').exists() else []
        write_rows(run / 'trace.jsonl', [r for r in history if r['epoch'] <= start_epoch])

    write_json(run / 'CONFIG.json', {
        'identity': identity,
        'identity_sha256': cfg_hash,
        'runtime': {
            'pid': os.getpid(),
            'CUDA_VISIBLE_DEVICES': os.environ.get('CUDA_VISIBLE_DEVICES'),
            'torch': torch.__version__,
            'parameters': sum(p.numel() for p in model.parameters()),
            'n_train': len(train_ds),
            'n_val': len(val_ds),
            'train_bsz': opt.bsz,
            'eval_bsz': 1,
            'device': str(opt.device)
        }
    })

    loader = DataLoader(
        train_ds, batch_size=opt.bsz, shuffle=True,
        num_workers=0, collate_fn=start_end_collate, generator=generator
    )

    # Weights alignment (Kim AAAI 2026 Page 6)
    base_weights = dict(criterion.weight_dict)
    base_weights['loss_exist'] = job.get('exist_weight', 0.1)
    if job.get('multi_weight', 0.0) > 0.0:
        base_weights['loss_multi'] = job['multi_weight']

    do_da = job.get('data_aug_no_target', False)
    tau_no = job.get('tau_no', 0.08)
    tau_mul = job.get('tau_mul', 0.05)
    use_focal = job.get('use_focal_loss', False)
    is_two_stage = job.get('two_stage', False)
    stage1_epochs = job.get('stage1_epochs', 20)

    print(f"Starting training job {a.job} on {opt.device} (budget: {job['epochs']} epochs, lr_drop={opt.lr_drop})...", flush=True)

    for epoch in range(start_epoch, job['epochs']):
        begin = time.time()
        
        # Scheme A: Two-Stage Transition Check
        if is_two_stage:
            if epoch < stage1_epochs:
                # Stage 1: pure localization for first 40 epochs
                curr_weights = dict(base_weights)
                curr_weights['loss_exist'] = 0.0
                curr_weights['loss_multi'] = 0.0
                curr_do_da = False
            else:
                # Stage 2: Pick best checkpoint from Stage 1, freeze backbone, and fine-tune auxiliary heads
                if epoch == stage1_epochs:
                    print(f"\n[Stage 2 Transition at Epoch {epoch+1}] Loading BEST checkpoint from Stage 1: stage1_best.ckpt...", flush=True)
                    if (run / 'stage1_best.ckpt').exists():
                        stage1_ck = torch.load(run / 'stage1_best.ckpt', map_location='cpu', weights_only=False)
                        model.load_state_dict(stage1_ck['model'])
                        print(f"Successfully loaded Stage 1 best checkpoint from Epoch {stage1_ck['epoch']} with Val mAP={stage1_ck.get('best_loc', stage1_ck.get('best', 0.0)):.2f}%.", flush=True)
                    else:
                        print("Warning: stage1_best.ckpt not found, continuing with latest weights.", flush=True)
                    
                    # Freeze backbone parameters
                    for name, param in model.named_parameters():
                        is_aux = any(h in name for h in ['exist_head', 'multi_head', 'event_head', 'text', 'temporal', 'query'])
                        param.requires_grad = is_aux
                    trainable_params = [p for p in model.parameters() if p.requires_grad]
                    print(f"Frozen backbone parameters. Stage 2 trainable parameters: {sum(p.numel() for p in trainable_params)}", flush=True)
                    optimizer = torch.optim.AdamW(trainable_params, lr=job.get('stage2_lr', job['lr']), weight_decay=job['wd'], foreach=False)
                    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)
                curr_weights = dict(base_weights)
                curr_do_da = do_da
        else:
            curr_weights = dict(base_weights)
            curr_do_da = do_da

        model.train()
        criterion.train()
        sums = {}
        norms = []
        batches = 0
        positive_count = 0
        aug_no_total = 0
        aug_mul_total = 0

        for batch in loader:
            batch_meta, batch_inputs = batch[0], batch[1]
            model_inputs, targets = prepare_batch_inputs(batch_inputs, opt.device, non_blocking=False)
            
            # Scheme D: Dual Synthetic Data Augmentation
            if curr_do_da:
                model_inputs, targets, batch_meta, a_no, a_mul = apply_kim_augmentation(
                    model_inputs, targets, batch_meta, tau_no=tau_no, tau_mul=tau_mul
                )
                aug_no_total += a_no
                aug_mul_total += a_mul

            targets.update(label=batch_meta, fps=torch.full((len(batch_meta),), 1.0 / opt.clip_length, device=opt.device))
            outputs = model(**model_inputs, targets=targets)
            losses = criterion((batch_meta, batch_inputs), outputs, targets)
            
            # Scheme C: Focal Loss for Presence
            if use_focal and 'pred_exist_logits' in outputs:
                losses['loss_exist'] = compute_focal_loss(outputs['pred_exist_logits'], targets['exist_label'])
            
            if job['variant'] == 'E2M':
                losses['loss_multi'] = plurality_loss(outputs, batch_meta, targets['exist_label'])
            
            losses = {k: v for k, v in losses.items() if k in curr_weights and 'loss' in k}
            total_loss = sum(curr_weights[k] * v for k, v in losses.items())
            assert bool(torch.isfinite(total_loss)), 'Nonfinite loss'
            optimizer.zero_grad(set_to_none=True)
            total_loss.backward()

            norm = torch.nn.utils.clip_grad_norm_(model.parameters(), job['grad_clip'], error_if_nonfinite=True)
            optimizer.step()

            norms.append(float(norm))
            batches += 1
            positive_count += sum(bool(r['relevant_windows']) for r in batch_meta)
            for k, v in losses.items():
                sums[k] = sums.get(k, 0.0) + float(v.detach())

            if batches == 1 or batches % 50 == 0:
                status = {
                    'state': 'training', 'pid': os.getpid(), 'epoch': epoch + 1, 'batch': batches,
                    'updated': time.time(), 'loss': float(total_loss.detach()),
                    'grad_norm_before_clip': float(norm), 'aug_no': aug_no_total, 'aug_mul': aug_mul_total
                }
                write_json(run / 'STATUS.json', status)

        scheduler.step()
        
        # Validation
        model.eval()
        pre, post = predictions(model, val_ds, opt)
        report = validate(pre, post, val_ds.data, opt)
        loc_score = report['native_pre_nms']['MR-full-mAP']
        gmr_calib = report['own_val_BA_threshold']['G-mIoU@1']
        assert np.isfinite(loc_score) and np.isfinite(gmr_calib)

        # Composite GMR score balancing localization and presence
        composite_score = float(np.sqrt(max(0.0, loc_score) * max(0.0, gmr_calib)))
        improved_loc = loc_score > best_loc_score
        improved_gmr = composite_score > best_gmr_score

        if improved_loc:
            best_loc_score = loc_score
        if improved_gmr:
            best_gmr_score = composite_score
            es_count = 0
        else:
            es_count += 1

        record = {
            'epoch': epoch + 1,
            'native_mAP': loc_score,
            'best_loc_mAP': best_loc_score,
            'gmr_calibrated_mIoU': gmr_calib,
            'composite_score': composite_score,
            'best_composite': best_gmr_score,
            'improved': improved_gmr,
            'early_stop_count': es_count,
            'seconds': time.time() - begin,
            'losses': {k: v / batches for k, v in sums.items()},
            'positive_examples': positive_count,
            'aug_no_examples': aug_no_total,
            'aug_mul_examples': aug_mul_total,
            'batches': batches,
            'gradient': {
                'mean_global_norm': float(np.mean(norms)),
                'fraction_clipped': float(np.mean(np.array(norms) > job['grad_clip']))
            },
            'val': report
        }

        ckpt_state = {
            'epoch': epoch + 1,
            'best': best_loc_score,
            'best_loc': best_loc_score,
            'best_gmr': best_gmr_score,
            'composite_score': composite_score,
            'es': es_count,
            'identity_sha256': cfg_hash,
            'model': model.state_dict(),
            'optimizer': optimizer.state_dict(),
            'scheduler': scheduler.state_dict(),
            'sampler_rng': generator.get_state(),
            'python_rng': random.getstate(),
            'numpy_rng': np.random.get_state(),
            'torch_rng': torch.get_rng_state(),
            'cuda_rng': torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []
        }

        # Save peak generalized checkpoint (best.ckpt)
        if improved_gmr:
            atomic_checkpoint(run / 'best.ckpt', ckpt_state)
            write_json(run / 'selected.json', {
                'epoch': epoch + 1,
                'composite_score': composite_score,
                'native_pre_nms_mAP': loc_score,
                'gmr_calibrated': gmr_calib,
                'selection_data': 'Val only',
                'selection_metric': 'sqrt(mAP * G-mIoU_calib)',
                'stage': 'pre-NMS'
            })
            write_json(run / 'validation_metrics.json', report)
            write_rows(run / 'validation_predictions.jsonl', post)
            write_rows(run / 'validation_predictions_pre_nms.jsonl', pre)

        # Save peak localization checkpoint (best_loc.ckpt)
        if improved_loc:
            atomic_checkpoint(run / 'best_loc.ckpt', ckpt_state)
            if is_two_stage and epoch < stage1_epochs:
                atomic_checkpoint(run / 'stage1_best.ckpt', ckpt_state)
            write_json(run / 'selected_loc.json', {
                'epoch': epoch + 1,
                'native_pre_nms_mAP': loc_score,
                'selection_metric': 'MR-full-mAP'
            })

        atomic_checkpoint(run / 'latest.ckpt', ckpt_state)
        with (run / 'trace.jsonl').open('a') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

        write_json(run / 'STATUS.json', {
            'state': 'training', 'pid': os.getpid(), 'epoch': epoch + 1,
            'committed_epochs': epoch + 1, 'best_loc_mAP': best_loc_score,
            'best_composite': best_gmr_score, 'updated': time.time()
        })

        print(json.dumps({
            'epoch': epoch + 1,
            'native_mAP': loc_score,
            'best_loc': best_loc_score,
            'AUROC': report['AUROC'],
            'GmIoU1_04': report['gate_04']['G-mIoU@1'],
            'GmIoU1_05': report['fixed_05']['G-mIoU@1'],
            'GmIoU1_calib': gmr_calib,
            'composite': round(composite_score, 2),
            'seconds': round(record['seconds'], 1)
        }), flush=True)

        if a.stop_after_epoch and epoch + 1 >= a.stop_after_epoch:
            return

        patience = job.get('early_stop_patience', 25)
        if not a.smoke and es_count >= patience:
            print(f"Early stopping triggered after {es_count} epochs without composite improvement.")
            break

    if not (run / 'best.ckpt').exists():
        raise RuntimeError('No best checkpoint recorded.')

    # Load best checkpoint and perform final official Test evaluation
    if not a.smoke:
        print("\nLoading best GMR checkpoint for final official Test evaluation...", flush=True)
        best_ck = torch.load(run / 'best.ckpt', map_location='cpu', weights_only=False)
        model.load_state_dict(best_ck['model'])
        model.eval()
        test_report = evaluate_on_test(model, opt, run)
        print("Official Test evaluation complete for best.ckpt!", flush=True)
        loc = test_report['positive_localization']
        print(f"Test mAP: {loc['mAP']:.2f}% | AUROC: {test_report['AUROC']:.2f}% | G-mIoU@1(0.4): {test_report['gate_04']['G-mIoU@1']:.2f}% | G-mIoU@1(0.5): {test_report['fixed_05']['G-mIoU@1']:.2f}% | G-mIoU@1(calib): {test_report['own_val_BA_threshold']['G-mIoU@1']:.2f}%")

    selected = read_json(run / 'selected.json')
    write_json(run / 'COMPLETE.json', {
        'state': 'complete',
        'trained_epochs': read_json(run / 'STATUS.json').get('committed_epochs', start_epoch),
        'selected': selected,
        'test_evaluated': not a.smoke,
        'updated': time.time()
    })
    write_json(run / 'STATUS.json', {'state': 'complete', 'selected': selected, 'updated': time.time()})

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--job', required=True)
    p.add_argument('--device', default='cuda')
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--smoke-name', default='fixture')
    p.add_argument('--smoke-epochs', type=int, default=1)
    p.add_argument('--stop-after-epoch', type=int)
    a = p.parse_args()
    execute(a)

if __name__ == '__main__':
    main()
