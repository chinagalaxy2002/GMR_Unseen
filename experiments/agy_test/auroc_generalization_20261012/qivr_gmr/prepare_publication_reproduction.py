#!/usr/bin/env python3
"""Freeze published source and prepare exactly three native-protocol reruns."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tarfile

import torch

from publication_protocol import read_native_validation_log, selection_trace

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
REFERENCE = '2677cfecddd0101b187d0ab413f2b51fe09ea201'
SETTINGS = [('charades_cg_v2','C3_CG','moment'), ('clean_v3','A1_v3','qd'), ('clean_v3','A2_v3','flash')]


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024), b''):
            result.update(chunk)
    return result.hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def prepare(output, diagnostic_output):
    output.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('publication_baseline_registry',REPO/'experiments/agy_test/training_free_auroc_20261012/common.py')
    registry=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(registry)
    source=output/'published_source'
    source.mkdir()
    selections=[]
    for experiment in ['charades_cg_baselines_20261010','v3_release_baselines_20261009']:
        prefix='experiments/agy_test/'+experiment
        selections += [prefix+'/native_source',prefix+'/launch_native.sh']
    with subprocess.Popen(['git','archive',REFERENCE,*selections],cwd=REPO,stdout=subprocess.PIPE) as process:
        with tarfile.open(fileobj=process.stdout,mode='r|') as archive:
            archive.extractall(source,filter='data')
        assert process.wait()==0
    configs=output/'configs'
    configs.mkdir()
    jobs=[]
    audits=[]
    for dataset,split,backbone in SETTINGS + [('charades_cg_v2','C3_CG','qd')]:
        paths=registry.paths(dataset,split,backbone)
        experiment='charades_cg_baselines_20261010' if dataset=='charades_cg_v2' else 'v3_release_baselines_20261009'
        original=REPO/'experiments/agy_test'/experiment
        original_release=original/'groups'/split/'release'/split
        for name in ['train.jsonl','val_seen.jsonl']:
            assert digest(original_release/name)==digest(paths['release']/name)
        checkpoint=torch.load(paths['checkpoint'],map_location='cpu',weights_only=False)
        opt=dict(checkpoint['opt']) if isinstance(checkpoint['opt'],dict) else vars(checkpoint['opt'])
        trace=selection_trace(backbone,read_native_validation_log(opt['eval_log_filepath']))
        assert trace[-1]['best_epoch']==int(checkpoint['epoch'])+1
        tag=f'{dataset}_{split}_{backbone}_'+('native' if backbone=='flash' else 'with_sa')
        prior=diagnostic_output/tag
        audit=dict(dataset=dataset,split=split,backbone=backbone,
            published_best_epoch=int(checkpoint['epoch'])+1,published_final_epoch=trace[-1]['epoch'],
            published_stop_counter=trace[-1]['non_improving_epochs'],published_early_stop=trace[-1]['early_stop'],
            diagnostic_best_epoch=json.loads((prior/'STATUS.json').read_text())['best_epoch'],
            diagnostic_final_epoch=json.loads((prior/'STATUS.json').read_text())['epochs'],
            diagnostic_checkpoint_files=[p.name for p in prior.glob('*.ckpt')],
            published_checkpoint_sha256=digest(paths['checkpoint']),
            train_equal_to_published=True,seen_validation_equal_to_published=True,
            published_data_loader_workers=opt.get('num_workers'),diagnostic_data_loader_workers=2,
            diagnostic_data_order='Independent generator with seed 3407+epoch',
            published_data_order='Original native DataLoader/global RNG; original num_workers',
            metrics=json.loads((prior/'metrics.json').read_text())['metrics'],
            native_selection_trace=trace)
        audits.append(audit)
        if (dataset,split,backbone) not in SETTINGS:
            continue
        native=source/'experiments/agy_test'/experiment/'native_source'
        launcher=source/'experiments/agy_test'/experiment/'launch_native.sh'
        hashes={str(p):digest(p) for p in native.rglob('*') if p.is_file()}
        hashes[str(launcher)]=digest(launcher)
        for path in [original_release/'train.jsonl',original_release/'val_seen.jsonl']:
            assert all(json.loads(line)['partition'] in ('S+','S-') for line in path.read_text().splitlines() if line.strip())
        job_tag='publication_'+tag
        output_dir=output/job_tag
        value=dict(dataset=dataset,split=split,backbone=backbone,variant='native' if backbone=='flash' else 'with_sa',
            seed=3407,maximum_epochs=100,max_es_cnt=26,
            stop_comparison='>=' if backbone=='moment' else '>',
            selection_metric='Seen validation mean R1@0.5/R1@0.7' if backbone=='flash' else 'Seen validation MR-full-mAP',
            native_source=str(native),launcher=str(launcher),output_dir=str(output_dir),
            training_release=str(original_release),text_features=str(paths['text']),test_file=str(paths['release']/'test.jsonl'),
            training_text_features=str(original/'features/clip_text'),
            video_root='/home/guoxiangyu/paper/新建文件夹/charades',
            gmr_python='/home/guoxiangyu/miniconda3/envs/gmr/bin/python',flash_python='/home/guoxiangyu/miniconda3/envs/univtg/bin/python',
            baseline_predictions=str(paths['baseline']),published_reference_commit=REFERENCE,
            historical_checkpoint=str(paths['checkpoint']),historical_best_epoch=int(checkpoint['epoch'])+1,
            source_sha256=hashes,input_sha256={str(p):digest(p) for p in [original_release/'train.jsonl',original_release/'val_seen.jsonl']},
            instrumentation='Unmodified native training; native losses/validation/selection trace. Existing full diagnostic trajectories preserved separately.')
        config=configs/(job_tag+'.json')
        save(config,value)
        jobs.append(dict(tag=job_tag,dataset=dataset,split=split,backbone=backbone,
            variant=value['variant'],runner='publication_reproduction',config=str(config),output_dir=str(output_dir)))
    save(output/'PROTOCOL_AUDIT.json',dict(reference_commit=REFERENCE,jobs=audits,
        rerun_settings=SETTINGS,no_other_setting_retrained=True,
        prior_results_preserved=True,native_code_frozen_from_git=True,
        early_stop_tests='Historical logs replayed; synthetic ties and 26/27 boundaries checked'))
    save(output/'JOBS.json',dict(jobs=jobs))
    lines=['# 发表协议复现核查','',f'参考 commit：`{REFERENCE}`。仅重跑 CG Moment、Clean A1 QD、Clean A2 Flash。','',
        '|设置|发表 best epoch|发表停止 epoch|未改善轮数|诊断 best epoch|诊断训练轮数|','|---|---:|---:|---:|---:|---:|']
    for a in audits:
        lines.append(f"|{a['dataset']}/{a['split']}/{a['backbone']}|{a['published_best_epoch']}|{a['published_final_epoch']}|{a['published_stop_counter']}|{a['diagnostic_best_epoch']}|{a['diagnostic_final_epoch']}|")
    lines+=['','Moment 的停止条件为 `es_cnt >= 26`；QD/Flash 为 `es_cnt > 26`。严格大于才更新 best，相等计入未改善。最多 100 epochs。','',
        '发表 Moment/QD 使用 Seen MR-full-mAP，Flash 使用 Seen R1@0.5/R1@0.7 均值；原诊断使用 Seen AUROC。发表 DETR DataLoader 使用 4 workers，Flash 使用 0；原诊断使用 2。原生 DataLoader 的随机流与原诊断逐 epoch 独立 seed 不同。训练和 Seen 验证标注字节一致。','',
        '三个原诊断目录均仅保留 best.ckpt 与 last.ckpt；发表最佳轮次对应的诊断逐轮权重未保留。原结果保持原始 AUROC 选模标签，新复现单独存储。','',
        '原生训练入口不加入额外前向或梯度诊断；保留原生 train/eval 日志，并输出逐轮 SELECTION_TRACE.jsonl。已有完整监控轨迹保持原样。', '',
        '|设置|指标|发表 Seen|诊断 Seen|变化 pp|发表 Unseen|诊断 Unseen|变化 pp|','|---|---|---:|---:|---:|---:|---:|---:|']
    for a in audits:
        for metric in ['auroc','rej_f1','gmiou1']:
            m=a['metrics'];b=[m[f'baseline/{s}/{metric}']['point'] for s in ['S','U']];d=[m[f'experiment/{s}/{metric}']['point'] for s in ['S','U']]
            lines.append(f"|{a['dataset']}/{a['split']}/{a['backbone']}|{metric}|{b[0]:.3f}|{d[0]:.3f}|{d[0]-b[0]:+.3f}|{b[1]:.3f}|{d[1]:.3f}|{d[1]-b[1]:+.3f}|")
    (output/'PROTOCOL_AUDIT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(output=str(output),jobs=jobs,reference=REFERENCE)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--diagnostic-output',required=True,type=Path)
    args=parser.parse_args()
    prepare(args.output.resolve(),args.diagnostic_output.resolve())
