#!/usr/bin/env python3
"""Run an immutable published native launcher, then freeze/calibrate/evaluate."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from publication_protocol import read_native_validation_log, selection_trace, calibrate_native, native_predictions


def save(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024), b''):
            result.update(chunk)
    return result.hexdigest()


def run_logged(cmd, cwd, env, log, output, phase):
    started = time.time()
    with log.open('w') as stream:
        process = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT)
        while True:
            try:
                code = process.wait(timeout=15)
                break
            except subprocess.TimeoutExpired:
                save(output/'STATUS.json', dict(state=phase, child_pid=process.pid,
                     elapsed_seconds=time.time()-started, updated=time.time()))
    if code:
        raise RuntimeError(f'{phase} failed with exit {code}; retained log: {log}')


def run(config, gpu):
    spec = json.loads(config.read_text())
    output = Path(spec['output_dir'])
    output.mkdir(parents=True, exist_ok=False)
    save(output/'CONFIG.json', spec)
    save(output/'STATUS.json', dict(state='preparing', updated=time.time()))
    source = Path(spec['native_source'])
    for name, digest in spec['source_sha256'].items():
        assert sha(Path(name)) == digest, name
    for name, digest in spec['input_sha256'].items():
        assert sha(Path(name)) == digest, name
    backbone = spec['backbone']
    run_root = output/'native_runs'
    features = output/'features'
    features.mkdir()
    (features/'val_seen.jsonl').symlink_to(Path(spec['training_release'])/'val_seen.jsonl')
    (features/'clip_text').symlink_to(spec['training_text_features'], target_is_directory=True)
    env = {**os.environ, 'OMP_NUM_THREADS':'2', 'MKL_NUM_THREADS':'2', 'OPENBLAS_NUM_THREADS':'2',
           'TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD':'1', 'CUDA_VISIBLE_DEVICES':str(gpu),
           'V3_NATIVE_REPO':str(source), 'TRAIN_GPU':str(gpu), 'RUN_ROOT':str(run_root),
           'DATA_ROOT':spec['training_release'], 'FEATURE_ROOT':str(features),
           'VIDEO_ROOT':spec['video_root'], 'GMR_PYTHON':spec['gmr_python'],
           'FLASH_PYTHON':spec['flash_python'], 'SEMANTIC_SEED':'3407'}
    cmd = ['bash', spec['launcher'], backbone]
    save(output/'COMMANDS.json', dict(training=cmd, cwd=str(source),
         environment={k:env[k] for k in ('CUDA_VISIBLE_DEVICES','V3_NATIVE_REPO','TRAIN_GPU','RUN_ROOT',
                      'DATA_ROOT','FEATURE_ROOT','VIDEO_ROOT','GMR_PYTHON','FLASH_PYTHON','SEMANTIC_SEED')}))
    run_logged(cmd, source, env, output/'launcher.log', output, 'training')
    trained = run_root/backbone
    if backbone == 'flash':
        folders = list(trained.glob('charadesSTA-*'))
        assert len(folders) == 1
        trained = folders[0]
    checkpoint = trained/('model_best.ckpt' if backbone=='flash' else 'best.ckpt')
    validation = trained/('best_charadesSTA_val_preds.jsonl' if backbone=='flash' else 'best_charades_semantic_existence_val_preds.jsonl')
    assert checkpoint.is_file() and validation.is_file()
    import numpy as np
    import torch
    from run_decoder_experiment import diagnostics, metric_report
    from auroc_mechanism_monitor import final_ranking_bootstrap
    saved = torch.load(checkpoint, map_location='cpu', weights_only=False)
    opt = dict(saved['opt']) if isinstance(saved['opt'], dict) else vars(saved['opt'])
    history = read_native_validation_log(opt['eval_log_filepath'])
    trace = selection_trace(backbone, history)
    assert len(trace) == len(history), 'Training continued beyond the published early-stop boundary'
    assert trace[-1]['best_epoch'] == int(saved['epoch']) + 1
    with (output/'SELECTION_TRACE.jsonl').open('w') as stream:
        for row in trace:
            stream.write(json.dumps(row) + '\n')
    frozen = output/'frozen_checkpoints'
    frozen.mkdir()
    shutil.copy2(checkpoint, frozen/checkpoint.name)
    shutil.copy2(validation, frozen/validation.name)
    val_rows = [json.loads(x) for x in (Path(spec['training_release'])/'val_seen.jsonl').read_text().splitlines() if x.strip()]
    val_pred = {str(x['qid']):x for x in map(json.loads, validation.read_text().splitlines())}
    assert set(val_pred)=={str(x['qid']) for x in val_rows}
    assert all(x['partition'] in ('S+','S-') for x in val_rows)
    score_key = 'pred_exist_logit' if backbone=='flash' else 'pred_exist_score'
    labels = np.array([x['exist_label'] for x in val_rows])
    scores = np.array([val_pred[str(x['qid'])][score_key] for x in val_rows], dtype=np.float32)
    threshold, best_ba = calibrate_native(labels, scores)
    calibration = dict(best_epoch=int(saved['epoch'])+1, threshold=threshold, seen_validation_ba=best_ba,
        selected_on='Published native Seen-validation localization metric',
        selection_metric=spec['selection_metric'], early_stop=trace[-1]['early_stop'],
        final_training_epoch=history[-1][0], patience=26, stop_comparison=spec['stop_comparison'],
        selected_checkpoint_sha256=sha(checkpoint), validation_predictions_sha256=sha(validation),
        validation_sha256=sha(Path(spec['training_release'])/'val_seen.jsonl'), test_evaluation_started=False)
    save(output/'FROZEN_CALIBRATION.json', calibration)
    np.savez_compressed(output/'validation_predictions.npz', qids=np.array([str(x['qid']) for x in val_rows]),
                        labels=labels, scores=scores, threshold=threshold)
    test = output/'native_test'
    test.mkdir()
    if backbone=='flash':
        cmd=[spec['flash_python'],'-m','training.flash_vtg_gmr.inference','configs/flash_vtg_gmr/model.py',
             '--resume',str(frozen/checkpoint.name),'--eval_split_name','test','--eval_path',spec['test_file'],
             '--eval_results_dir',str(test),'--device','0','--nms_thd','-1']
        prediction = test/'hl_test_submission.jsonl'
    else:
        cmd=[spec['gmr_python'],f'training/{backbone}_detr_gmr/evaluate.py','--dataset','charades_semantic_existence',
             '--model_path',str(frozen/checkpoint.name),'--split','test','--eval_path',spec['test_file'],
             '--t_feat_dir',spec['text_features'],'--v_feat_dirs',str(Path(spec['video_root'])/'vid_clip'),
             str(Path(spec['video_root'])/'vid_slowfast'),'--results_dir',str(test),
             '--device','cuda' if backbone=='moment' else 'cuda:0']
        prediction = test/(backbone+'_detr_gmr_test_submission.jsonl')
    run_logged(cmd, source, env, output/'inference.log', output, 'frozen_test_inference')
    records = [json.loads(x) for x in Path(spec['test_file']).read_text().splitlines() if x.strip()]
    pred = {str(x['qid']):x for x in map(json.loads,prediction.read_text().splitlines())}
    assert set(pred)=={str(x['qid']) for x in records}
    baseline = dict(np.load(spec['baseline_predictions'], allow_pickle=False))
    frozen_pred, records = native_predictions(records,pred,baseline['qids'],backbone,threshold,source)
    np.savez_compressed(output/'predictions.npz',**frozen_pred)
    width=max(len(pred[str(x['qid'])]['pred_relevant_windows']) for x in records)
    candidates=[]
    for row in records:
        windows=np.array(pred[str(row['qid'])]['pred_relevant_windows'],dtype=float).reshape(-1,3)
        windows=np.pad(windows,((0,width-len(windows)),(0,0)))
        overlap=diagnostics.diag.iou_matrix(windows[:,:2],row['relevant_windows']) if row['relevant_windows'] else np.zeros((width,0))
        candidates.append(dict(qid=str(row['qid']),vid=row['vid'],partition=row['partition'],exist_label=row['exist_label'],
            duration=row['duration'],gt_windows=row['relevant_windows'],slot_spans_sec=windows[:,:2],slot_scores=windows[:,2],
            iou_with_gt=overlap.max(1) if row['relevant_windows'] else np.zeros(width)))
    metric_report(output,baseline,frozen_pred,candidates,2000)
    final_ranking_bootstrap(output,diagnostics,frozen_pred)
    save(output/'STATUS.json',dict(state='complete',best_epoch=calibration['best_epoch'],
         epochs=calibration['final_training_epoch'],early_stop=calibration['early_stop'],
         scope='Three-setting published-native protocol reproduction; no other setting retrained',updated=time.time()))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True,type=Path)
    parser.add_argument('--gpu',required=True,type=int)
    args=parser.parse_args()
    try:
        run(args.config.resolve(),args.gpu)
    except Exception as error:
        spec=json.loads(args.config.read_text())
        output=Path(spec['output_dir'])
        if output.is_dir():
            save(output/'STATUS.json',dict(state='failed',error=repr(error),updated=time.time()))
        raise
