"""Train one Task-A enhancement using Train/Val only; E0 localization is immutable."""
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
import torch.nn.functional as F
from torch.utils.data import DataLoader

from environment import E0_RUN, ROOT, make_dataset, options, read_json, read_rows, seed_all, write_json, write_rows
from model import TaskAEnhancement, head_loss
from validation import predictions, validate
from models.flash_vtg_gmr.model import build_model1
from training.flash_vtg_gmr.dataset import prepare_batch_inputs, start_end_collate


def atomic_checkpoint(path, payload):
    temporary = path.with_suffix('.tmp')
    torch.save(payload, temporary)
    temporary.replace(path)


def set_training_mode(model):
    model.train()
    # Keep stochastic regularization only in new heads. The frozen localizer still needs
    # base.training=True because FlashVTG has different batched train/eval forward branches.
    trainable_modules = {module for module in model.modules() if any(p.requires_grad for p in module.parameters(recurse=False))}
    for module in model.base.modules():
        if isinstance(module, (torch.nn.Dropout, torch.nn.modules.batchnorm._BatchNorm)) and module not in trainable_modules:
            module.eval()


def hard_negative_loss(model, model_inputs):
    batch = model_inputs['src_txt'].shape[0]
    if batch < 2:
        return model_inputs['src_txt'].sum() * 0.0
    pooled = (model_inputs['src_txt'] * model_inputs['src_txt_mask'].unsqueeze(-1)).sum(1)
    denom = model_inputs['src_txt_mask'].sum(1, keepdim=True).clamp(min=1)
    pooled = F.normalize(pooled / denom, dim=-1)
    similarity = pooled @ pooled.t()
    similarity.fill_diagonal_(-1e4)
    source = similarity.argmax(1)
    negative_inputs = dict(model_inputs)
    negative_inputs['src_txt'] = model_inputs['src_txt'][source]
    negative_inputs['src_txt_mask'] = model_inputs['src_txt_mask'][source]
    negative_output = model(**negative_inputs, targets={})
    return F.binary_cross_entropy_with_logits(
        negative_output['pred_exist_logits'], torch.zeros_like(negative_output['pred_exist_logits'])
    )


def execute(args):
    jobs = read_json(ROOT / 'configs/jobs.json')['jobs']
    job = dict(next(row for row in jobs if row['run_id'] == args.job))
    if args.smoke:
        job['epochs'] = 1
    run = ROOT / ('tests/smoke' if args.smoke else 'runs') / args.job
    run.mkdir(parents=True, exist_ok=True)
    lock = (run / 'run.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if (run / 'COMPLETE.json').exists():
        print(f'{args.job} already complete')
        return

    identity = {'job': job, 'e0_checkpoint_sha256': hashlib.sha256((E0_RUN / 'best.ckpt').read_bytes()).hexdigest()}
    identity_sha = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    opt = options(job, args.device)
    seed_all(job['seed'])
    base, _criterion = build_model1(opt)
    model = TaskAEnhancement(base, job).to(opt.device)
    checkpoint = torch.load(E0_RUN / 'best.ckpt', map_location='cpu', weights_only=False)
    loaded = model.load_state_dict(checkpoint['model'], strict=False)
    unexpected = [name for name in loaded.unexpected_keys if 'exist_head' not in name]
    if unexpected:
        raise RuntimeError(f'unexpected E0 keys: {unexpected}')
    for name, parameter in model.named_parameters():
        parameter.requires_grad = ('exist_head' in name or name.startswith('fusion.'))
    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    frozen_snapshot = {
        name: tensor.detach().cpu().clone()
        for name, tensor in model.state_dict().items()
        if 'exist_head' not in name and not name.startswith('fusion.')
    }

    train_data = make_dataset(opt, 'train', args.smoke)
    val_data = make_dataset(opt, 'val', args.smoke)
    generator = torch.Generator().manual_seed(job['seed'])
    loader = DataLoader(
        train_data, batch_size=opt.bsz, shuffle=True, num_workers=0,
        collate_fn=start_end_collate, generator=generator,
    )
    optimizer = torch.optim.AdamW(trainable, lr=job['lr'], weight_decay=job['wd'], foreach=False)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=job.get('lr_drop', 12), gamma=0.5)
    start_epoch = 0
    best_auroc = -1.0
    stale = 0
    if (run / 'latest.ckpt').exists():
        saved = torch.load(run / 'latest.ckpt', map_location='cpu', weights_only=False)
        if saved['identity_sha256'] != identity_sha:
            raise RuntimeError('refusing resume: configuration changed')
        model.load_state_dict(saved['model'])
        optimizer.load_state_dict(saved['optimizer'])
        scheduler.load_state_dict(saved['scheduler'])
        start_epoch = saved['epoch']
        best_auroc = saved['best_auroc']
        stale = saved['stale']

    write_json(run / 'CONFIG.json', {
        'identity': identity,
        'identity_sha256': identity_sha,
        'trainable_parameters': sum(p.numel() for p in trainable),
        'total_parameters': sum(p.numel() for p in model.parameters()),
        'selection': 'Val AUROC only; Test is inaccessible',
        'localization_contract': 'E0 pred_relevant_windows_pre_exist must be exactly identical',
    })
    reference = E0_RUN / 'validation_predictions_pre_nms.jsonl'
    history = read_rows(run / 'trace.jsonl') if (run / 'trace.jsonl').exists() else []
    history = [row for row in history if row['epoch'] <= start_epoch]
    write_rows(run / 'trace.jsonl', history)

    for epoch in range(start_epoch, job['epochs']):
        began = time.time()
        set_training_mode(model)
        sums = {}
        batches = 0
        for batch_meta, batch_inputs in loader:
            model_inputs, targets = prepare_batch_inputs(batch_inputs, opt.device, non_blocking=False)
            targets.update(label=batch_meta, fps=torch.full((len(batch_meta),), 1.0 / opt.clip_length, device=opt.device))
            output = model(**model_inputs, targets=targets)
            loss, details = head_loss(output, batch_meta, targets, job)
            if job.get('hard_negative', False):
                negative = hard_negative_loss(model, model_inputs)
                loss = loss + float(job.get('hard_negative_weight', 0.5)) * negative
                details['loss_hard_negative'] = negative
                details['loss_total'] = loss
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            norm = torch.nn.utils.clip_grad_norm_(trainable, job['grad_clip'], error_if_nonfinite=True)
            optimizer.step()
            batches += 1
            for name, value in details.items():
                sums[name] = sums.get(name, 0.0) + float(value.detach())
            if batches == 1 or batches % 100 == 0:
                write_json(run / 'STATUS.json', {
                    'state': 'training', 'epoch': epoch + 1, 'batch': batches,
                    'pid': os.getpid(), 'loss': float(loss.detach()), 'grad_norm': float(norm),
                    'updated': time.time(),
                })
        scheduler.step()

        for name, tensor in frozen_snapshot.items():
            if not torch.equal(model.state_dict()[name].detach().cpu(), tensor):
                raise AssertionError(f'frozen parameter changed: {name}')
        model.eval()
        pre, post = predictions(model, val_data, opt)
        report = validate(pre, post, val_data.data, opt, reference)
        score = report['AUROC']
        improved = score > best_auroc
        if improved:
            best_auroc = score
            stale = 0
        else:
            stale += 1
        state = {
            'epoch': epoch + 1,
            'best_auroc': best_auroc,
            'stale': stale,
            'identity_sha256': identity_sha,
            'model': model.state_dict(),
            'optimizer': optimizer.state_dict(),
            'scheduler': scheduler.state_dict(),
        }
        if improved:
            atomic_checkpoint(run / 'best.ckpt', state)
            write_json(run / 'selected.json', {
                'epoch': epoch + 1, 'val_AUROC': score,
                'val_G_mIoU_04': report['gate_04']['G-mIoU@1'],
                'val_G_mIoU_05': report['fixed_05']['G-mIoU@1'],
                'native_pre_nms_mAP': report['native_pre_nms']['MR-full-mAP'],
                'raw_localizer_mAP': report['raw_localizer_pre_exist']['MR-full-mAP'],
                'localizer_fingerprint': report['localizer_fingerprint'],
                'selection_data': 'Val only', 'selection_metric': 'AUROC',
            })
            write_json(run / 'validation_metrics.json', report)
            write_rows(run / 'validation_predictions.jsonl', post)
            write_rows(run / 'validation_predictions_pre_nms.jsonl', pre)
        atomic_checkpoint(run / 'latest.ckpt', state)
        record = {
            'epoch': epoch + 1, 'seconds': time.time() - began, 'improved': improved,
            'losses': {name: value / batches for name, value in sums.items()}, 'val': report,
        }
        with (run / 'trace.jsonl').open('a') as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')
        write_json(run / 'STATUS.json', {
            'state': 'training', 'epoch': epoch + 1, 'best_AUROC': best_auroc,
            'stale': stale, 'updated': time.time(),
        })
        print(json.dumps({
            'epoch': epoch + 1, 'AUROC': score,
            'G1@0.4': report['gate_04']['G-mIoU@1'],
            'G1@0.5': report['fixed_05']['G-mIoU@1'],
            'native_mAP': report['native_pre_nms']['MR-full-mAP'],
            'raw_localizer_mAP': report['raw_localizer_pre_exist']['MR-full-mAP'],
            'fingerprint_ok': report['localizer_matches_e0'],
            'seconds': round(record['seconds'], 1),
        }), flush=True)
        if stale >= job.get('early_stop_patience', 8):
            break

    write_json(run / 'COMPLETE.json', {
        'state': 'complete', 'best_AUROC': best_auroc, 'test_evaluated': False,
        'localizer_immutable': True, 'updated': time.time(),
    })
    write_json(run / 'STATUS.json', {'state': 'complete', 'best_AUROC': best_auroc, 'updated': time.time()})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job', required=True)
    parser.add_argument('--device', default='cuda')
    parser.add_argument('--smoke', action='store_true')
    execute(parser.parse_args())


if __name__ == '__main__':
    main()
