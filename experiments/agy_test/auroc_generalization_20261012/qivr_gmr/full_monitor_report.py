"""Read only overview of all baselines, including Flash temporal diagnostics."""
import json
from pathlib import Path
from mechanism_suite import read_json
from mechanism_monitor import save_json


def report(output):
    output=Path(output);manifest=read_json(output/'SUITE.json',{});state=read_json(output/'STATUS.json',{})
    rows=[];lines=['# Full baseline monitoring','',
        'Training on Seen only. Table uses the latest completed full Seen validation pass; incomplete training is not a final result. Decoder slots apply to Moment/QD; temporal candidates apply to Flash. Training diagnostics are sampled every 50 steps plus the first batch; fixed Seen probes and validation run every epoch.', '',
        '| Job | State / epoch | GPU | Seen AUROC | S+ probability median | S− probability median |',
        '|---|---|---:|---:|---:|---:|']
    for job in manifest.get('jobs',[]):
        folder=output/job['tag'];process=state.get('jobs',{}).get(job['tag'],{});run=read_json(folder/'STATUS.json',{})
        files=sorted((folder/'monitor/auroc_mechanisms').glob('validation_epoch_*_scores.json'))
        latest=read_json(files[-1],{}) if files else {}
        scores=latest.get('subsets',{}).get('S',{});prob=scores.get('raw_probability',{})
        def median(key):
            q=prob.get(key);return q[3] if q else None
        item=dict(**job,state=run.get('state',process.get('state','queued')),epoch=run.get('epoch',run.get('epochs')),gpu=process.get('gpu'),
            seen_auroc=scores.get('score',{}).get('ranking',{}),positive_probability_median=median('positive_quantiles'),negative_probability_median=median('negative_quantiles'),
            latest_complete_validation=str(files[-1]) if files else None)
        auc=(item['seen_auroc'] or {}).get('auroc')
        fmt=lambda v:'—' if v is None else f'{v:.4f}'
        lines.append(f"| {job['tag']} | {item['state']} / {item['epoch']} | {item['gpu']} | {fmt(auc)} | {fmt(item['positive_probability_median'])} | {fmt(item['negative_probability_median'])} |")
        rows.append(item)
    save_json(output/'FULL_MONITOR_STATUS.json',dict(jobs=rows))
    (output/'FULL_MONITORING.md').write_text('\n'.join(lines)+'\n')
