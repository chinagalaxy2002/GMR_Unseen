"""Reproduce baseline/DEC point estimates, tables and paired video-bootstrap CIs."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
from dec import SPLITS, BACKBONES, score, select_threshold

METRICS = ('seen_auc','unseen_auc','gap','rej_f1','rr','s_frr','u_frr','gmiou1')


def metrics(data, scores, threshold, backbone):
    labels, partitions = data['labels'], data['partitions']
    accept = scores >= threshold
    seen, unseen = np.char.startswith(partitions, 'S'), np.char.startswith(partitions, 'U')
    s, u = roc_auc_score(labels[seen], scores[seen]), roc_auc_score(labels[unseen], scores[unseen])
    tn = np.sum((labels == 0) & ~accept)
    fp = np.sum((labels == 0) & accept)
    fn = np.sum((labels == 1) & ~accept)
    return dict(seen_auc=float(s), unseen_auc=float(u), gap=float(s-u),
                rej_f1=float(100 * 2 * tn / (2 * tn + fp + fn)),
                rr=float(100 * (~accept).mean()),
                s_frr=float(100 * (~accept[partitions == 'S+']).mean()),
                u_frr=float(100 * (~accept[partitions == 'U+']).mean()),
                gmiou1=float(100 * np.where(accept, data[backbone+'_accept_iou'], data['reject_iou']).mean()))


def restore_window_metrics(data, path):
    """Compute top-1 set IoU from archived native windows, checking cached values."""
    windows = {r['qid']: r for r in map(json.loads, path.read_text().splitlines())}
    assert set(windows) == set(data['qids'].astype(str))
    def set_iou(prediction, truth):
        if not prediction and not truth: return 1.0
        if not prediction or not truth: return 0.0
        assert len(prediction) == 1
        p = np.asarray(prediction[0], dtype=np.float64)
        g = np.asarray(truth, dtype=np.float64)
        inter = np.clip(np.minimum(p[1], g[:,1])-np.maximum(p[0], g[:,0]), 0, None)
        union = (p[1]-p[0]) + (g[:,1]-g[:,0]) - inter
        return float(np.max(inter/union) / len(truth))
    rejects = np.array([set_iou([], windows[str(q)]['gt']) for q in data['qids']])
    np.testing.assert_array_equal(rejects, data['reject_iou'])
    data['reject_iou'] = rejects
    for bb in BACKBONES:
        values = np.array([set_iou(windows[str(q)]['pred'][bb], windows[str(q)]['gt']) for q in data['qids']])
        np.testing.assert_allclose(values, data[bb+'_accept_iou'], rtol=0, atol=1e-14)
        data[bb+'_accept_iou'] = values


def auc_plan(labels, scores, video_indices):
    order = np.argsort(scores, kind='stable')
    ordered_scores = scores[order]
    starts = np.r_[0, np.flatnonzero(np.diff(ordered_scores)) + 1]
    return labels[order], video_indices[order], starts


def weighted_auc(plan, video_counts):
    labels, videos, starts = plan
    weights = video_counts[videos]
    positive = np.add.reduceat(weights * labels, starts)
    negative = np.add.reduceat(weights * (1-labels), starts)
    if positive.sum() == 0 or negative.sum() == 0:
        return np.nan
    return np.sum(positive * (np.cumsum(negative) - .5 * negative)) / (positive.sum() * negative.sum())


def bootstrap(datasets, count):
    """One shared-video draw across all splits/backbones; paired score differences."""
    videos = np.unique(np.concatenate([d['vids'] for d in datasets.values()]))
    plans = {}
    for split, data in datasets.items():
        vi = np.searchsorted(videos, data['vids'])
        for bb in BACKBONES:
            for subset, prefix in [('seen','S'),('unseen','U')]:
                mask = np.char.startswith(data['partitions'], prefix)
                for method in ('baseline','dec'):
                    plans[split,bb,subset,method] = auc_plan(data['labels'][mask],data[bb+'_'+method][mask],vi[mask])
    rng = np.random.RandomState(3407)
    estimates = {(split,bb,subset):[] for split in SPLITS for bb in BACKBONES for subset in ('seen','unseen')}
    valid = 0
    for _ in range(count):
        counts = np.bincount(rng.choice(len(videos),len(videos),replace=True), minlength=len(videos))
        draw = {}
        for key in estimates:
            split,bb,subset = key
            draw[key] = weighted_auc(plans[split,bb,subset,'dec'],counts)-weighted_auc(plans[split,bb,subset,'baseline'],counts)
        if not all(np.isfinite(list(draw.values()))):
            continue  # Whole draw discarded, never silently average fewer splits.
        valid += 1
        for key,value in draw.items(): estimates[key].append(float(value))
    if valid == 0: raise ValueError('No valid bootstrap draws')
    output = {}
    for key, values in estimates.items():
        output['|'.join(key)] = (100*np.percentile(values,[2.5,97.5])).tolist()
    for bb in BACKBONES:
        for subset in ('seen','unseen'):
            macro = np.mean([estimates[split,bb,subset] for split in SPLITS],axis=0)
            output['|'.join(('MACRO',bb,subset))] = (100*np.percentile(macro,[2.5,97.5])).tolist()
    return dict(requested_draws=count, valid_draws=valid,seed=3407,unit='shared video cluster',ci_unit='percentage points',intervals=output)


def write_tables(records, intervals, directory):
    all_records = records.copy()
    for bb in BACKBONES:
        for method in ('baseline','dec'):
            rr = [r for r in records if r['backbone']==bb and r['method']==method]
            all_records.append(dict(split='MACRO',backbone=bb,method=method,
                                    threshold=None,**{k:float(np.mean([r[k] for r in rr])) for k in METRICS}))
    fields = ['split','backbone','method','threshold'] + list(METRICS)
    with (directory/'metrics.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(all_records)
    comparisons=[]
    for split in list(SPLITS)+['MACRO']:
        for bb in BACKBONES:
            b,d = [next(r for r in all_records if r['split']==split and r['backbone']==bb and r['method']==m) for m in ('baseline','dec')]
            row=dict(split=split,backbone=bb,delta_unseen_pp=100*(d['unseen_auc']-b['unseen_auc']),delta_seen_pp=100*(d['seen_auc']-b['seen_auc']),gap_reduction_pp=100*(b['gap']-d['gap']),delta_rej_f1_pp=d['rej_f1']-b['rej_f1'],delta_gmiou1_pp=d['gmiou1']-b['gmiou1'])
            if intervals:
                for subset in ('seen','unseen'):
                    lo,hi=intervals['intervals'][f'{split}|{bb}|{subset}'];row[f'{subset}_ci_lo_pp']=lo;row[f'{subset}_ci_hi_pp']=hi
            comparisons.append(row)
    with (directory/'comparisons.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(comparisons[0]));w.writeheader();w.writerows(comparisons)
    lines=['# 完整结果：DEC 幂律乘积门控与 baseline','',
           '五划分为 A1、A2_alt、A3、C1、C2_alt；MACRO 是五划分等权算术平均，不是合并样本指标。AUROC 为 0–1，其他指标与变化为百分比或百分点。', '',
           '## 表一：存在性排序','',
           '| 划分 | Backbone | 方法 | Seen AUROC | Unseen AUROC | Gap (S−U) |','|---|---|---|---:|---:|---:|']
    for r in all_records:lines.append(f"| {r['split']} | {r['backbone']} | {r['method']} | {r['seen_auc']:.4f} | {r['unseen_auc']:.4f} | {r['gap']:.4f} |")
    lines+=['','## 表一补充：配对变化与置信区间','', '| 划分 | Backbone | ΔUnseen (pp) | 95% CI | ΔSeen (pp) | 95% CI | Gap 缩小 (pp) |','|---|---|---:|---|---:|---|---:|']
    for r in comparisons:
        ci=lambda s: f"[{r[s+'_ci_lo_pp']:.2f}, {r[s+'_ci_hi_pp']:.2f}]" if intervals else '未计算'
        lines.append(f"| {r['split']} | {r['backbone']} | {r['delta_unseen_pp']:+.2f} | {ci('unseen')} | {r['delta_seen_pp']:+.2f} | {ci('seen')} | {r['gap_reduction_pp']:.2f} |")
    lines+=['','## 表二：同协议阈值下的拒绝与定位','', '| 划分 | Backbone | 方法 | All Rej-F1 (%) | RR (%) | S+ FRR (%) | U+ FRR (%) | All G-mIoU@1 (%) |','|---|---|---|---:|---:|---:|---:|---:|']
    for r in all_records:lines.append(f"| {r['split']} | {r['backbone']} | {r['method']} | {r['rej_f1']:.2f} | {r['rr']:.2f} | {r['s_frr']:.2f} | {r['u_frr']:.2f} | {r['gmiou1']:.2f} |")
    lines+=['','## 阈值与定义','', '每个划分、backbone、方法独立在 Seen 验证集的第 5–95 百分位共 91 个候选阈值中最大化 Balanced Accuracy；平局取最先遇到的阈值。score ≥ threshold 接受。不是对所有唯一分数的精确穷举。逐项阈值见 metrics.csv。', '',
            'Rej-F1 将拒绝负例视为正类：2TN/(2TN+FP+FN)。RR 为所有样本拒绝率，FRR 为指定正例分区的误拒率。G-mIoU@1 使用各 backbone 原始第一个合法定位窗口，门控只改变接受/拒绝；预测和真值均为空时得 1 分。', '',
            'CI 为固定训练 CDF、固定验证阈值下的视频聚类配对 bootstrap，所有划分共享同一次视频抽样；重新训练、重新拟合 CDF、调参不在区间覆盖范围内。']
    if intervals:lines+=['',f"本次重新复算：{intervals['requested_draws']} 次抽样，{intervals['valid_draws']} 次有效，seed=3407，百分位 95% 区间。历史 bootstrap 均值不作为原始样本上的点估计。"]
    (directory/'FULL_RESULTS.md').write_text('\n'.join(lines)+'\n')
    (directory/'metrics.json').write_text(json.dumps(all_records,indent=2)+'\n')


def run(methods=('baseline','dec')):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=Path(__file__).resolve().parent/'data')
    p.add_argument('--output',type=Path,default=Path('reproduced_results'))
    p.add_argument('--bootstrap',type=int,default=2000)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    datasets,records={},[]
    for split in SPLITS:
        train,val,test=[dict(np.load(a.data/split/f'{part}.npz',allow_pickle=False)) for part in ('train','val','test')]
        restore_window_metrics(test, a.data/split/'windows.jsonl')
        for bb in BACKBONES:
            for method in ('baseline','dec'):
                sc=score(train,test,bb,method);threshold=select_threshold(val['labels'],score(train,val,bb,method))
                test[bb+'_'+method]=sc
                if method in methods:records.append(dict(split=split,backbone=bb,method=method,threshold=threshold,**metrics(test,sc,threshold,bb)))
        datasets[split]=test
    if len(methods)==1:
        (a.output/'baseline.json').write_text(json.dumps(records,indent=2)+'\n')
        print('Baseline reproduced for 15 settings:',a.output);return
    ci=bootstrap(datasets,a.bootstrap) if a.bootstrap>0 else None
    write_tables(records,ci,a.output)
    if ci:(a.output/'bootstrap.json').write_text(json.dumps(ci,indent=2)+'\n')
    print('Baseline/DEC reproduced for 15 settings and five-split macro means:',a.output)

if __name__=='__main__':run()
