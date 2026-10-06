"""Read-only metric recomputation for Table-2-style paper tables; no training."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import importlib.util
import json
import csv
import hashlib
import numpy as np
import torch
from sklearn.metrics import roc_auc_score, f1_score

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location('audited', ROOT/'experiments/agy_test/candidate_suite_final_audit_20261006/audit_final.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
from eval.metrics import compute_mAP, compute_mR, compute_mR_plus, prepare_submission_for_gmiou, compute_G_mIoU

LABELS = {'flash': 'FlashVTG', 'moment': 'Moment-DETR', 'qd': 'QD-DETR'}
COLS = ['AUROC', 'Rej-F1', 'mAP', 'mR@1', 'mR@5', 'mR+@5', 'G-mIoU@1', 'G-mIoU@3']

def group_metrics(score, threshold, d, gt, pred, mask, localization, fixed=False):
    ix = np.where(mask)[0]
    ys = d['labels'][ix]
    reject = score[ix] <= threshold if fixed else score[ix] < threshold
    raw = [{'qid': str(d['qids'][i]), 'pred_exist_score': float(not reject[j]),
            'pred_relevant_windows': pred[str(d['qids'][i])]['pred_relevant_windows']} for j, i in enumerate(ix)]
    subgt = [gt[str(d['qids'][i])] for i in ix]
    gated, _ = prepare_submission_for_gmiou(raw, .5, 10)
    return dict(localization, **{'AUROC': 100*float(roc_auc_score(ys, score[ix])),
        'Rej-F1': 100*float(f1_score(1-ys, reject, zero_division=0)),
        **compute_G_mIoU(gated, subgt, k_list=(1, 3))})

def table(rows, keys):
    headers = ['Model'] + keys
    lines = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---']*len(headers)) + ' |']
    for row in rows:
        vals = [row['Model']] + [('—' if row[k] is None else (f'{row[k]:.2f}' if isinstance(row[k], (float, int)) else str(row[k]))) for k in keys]
        lines.append('| ' + ' | '.join(vals) + ' |')
    return '\n'.join(lines)

def latex(rows, keys, caption, label):
    lines = ['\\begin{table*}[t]', '\\centering', '\\small', '\\caption{' + caption + '}', '\\label{' + label + '}',
             '\\resizebox{\\textwidth}{!}{%', '\\begin{tabular}{l' + 'r'*len(keys) + '}', '\\toprule', 'Model & ' + ' & '.join(k.replace('%', '\\%').replace('_', '\\_') for k in keys) + ' \\\\', '\\midrule']
    for r in rows:
        vals = [('---' if r[k] is None else (f'{r[k]:.2f}' if isinstance(r[k], (float, int)) else str(r[k]))) for k in keys]
        lines.append(r['Model'].replace('_', '\\_') + ' & ' + ' & '.join(vals) + ' \\\\')
    return '\n'.join(lines + ['\\bottomrule', '\\end{tabular}%', '}', '\\end{table*}', ''])

def main():
    audit = json.loads(a.record(a.OUT/'audit_metrics.json').read_text())
    bootstrap = json.loads(a.record(a.OUT/'bootstrap.json').read_text())
    details = []
    counts = {}
    for split in a.SPLITS:
        gt = {str(r['qid']): dict(r, qid=str(r['qid'])) for r in a.rows(ROOT/'data/release/semantic_existence_v2'/split/'test.jsonl')}
        counts[split] = {'all': len(gt), 'multi_moment_positive': sum(len(r['relevant_windows']) >= 2 for r in gt.values())}
        for bb in a.BBS:
            d = a.load(a.EXP/'cache'/split/bb/'test.npz')
            paths = {'flash': 'flash/test/hl_test_submission.jsonl', 'moment': 'moment/test/moment_detr_gmr_test_submission.jsonl', 'qd': 'qd/test/qd_detr_gmr_test_submission.jsonl'}
            pred = {str(r['qid']): r for r in a.rows(ROOT/'results/semantic_existence/multi_split_v2'/split/paths[bb])}
            assert set(pred) == set(gt) == set(map(str, d['qids']))
            masks = {'All': np.ones(len(d['labels']), dtype=bool), 'Seen': np.isin(d['partitions'], ['S+', 'S-']), 'Unseen': np.isin(d['partitions'], ['U+', 'U-'])}
            local = {}
            for group, mask in masks.items():
                qids = [str(q) for q in d['qids'][mask] if gt[str(q)]['exist_label'] == 1]
                gs = [gt[q] for q in qids]
                ps = [{'qid': q, 'pred_relevant_windows': pred[q]['pred_relevant_windows']} for q in qids]
                multi = sum(len(r['relevant_windows']) >= 2 for r in gs)
                local[group] = {'mAP': compute_mAP(ps, gs, num_workers=1)['mAP'],
                    **{k: v for k, v in compute_mR(ps, gs, k_list=(1, 5)).items() if k in ['mR@1', 'mR@5']},
                    'mR+@5': compute_mR_plus(ps, gs, k_list=(5,))['mR+@5'] if multi else None}
            models = [('Baseline', None, d['X'][:, 0], audit['splits'][split]['operating'][bb+'_base']['calibrated_tau'])]
            for seed in a.SEEDS:
                saved = a.load(a.EXP/'runs/target_specific'/('seed_'+str(seed))/split/'transfer_predictions.npz')
                name = f'target_specific_{seed}_{bb}_to_{bb}'
                models.append(('Verifier', seed, saved[f'pred_{bb}_to_{bb}'], audit['splits'][split]['operating'][name]['calibrated_tau']))
            if bb == 'flash':
                tr = a.load(a.EXP/'cache'/split/bb/'train.npz')
                va = a.load(a.EXP/'cache'/split/bb/'val.npz')
                for mode in ['fixed_prior', 'none', 'unsigned', 'no_direction', 'visual_only', 'kinetic_only']:
                    tx, vx = tr['X'].copy(), va['X'].copy()
                    if mode == 'unsigned': tx[:, 10:12] = abs(tx[:, 10:12]); vx[:, 10:12] = abs(vx[:, 10:12])
                    if mode == 'no_direction': tx[:, 10:12] = 0; vx[:, 10:12] = 0
                    torch.manual_seed(3407)
                    m = a.mod.TargetCandidateVerifier(ablation_mode=mode if mode in ['visual_only', 'kinetic_only'] else 'none').eval()
                    if mode == 'fixed_prior': sc = a.predict(m, a.h.rank(tx, d['X']))
                    else:
                        folder = a.EXP/'runs/ablation'/bb/split/mode
                        m.load_state_dict(torch.load(a.record(folder/'verifier.pt'), map_location='cpu'))
                        sc = a.load(folder/'predictions.npz')['preds']
                    vs = a.predict(m, a.h.rank(tx, vx))
                    th = a.operating(vs, va['labels'], sc, d)['calibrated_tau']
                    models.append(('Ablation:'+mode, 3407, sc, th))
            for model, seed, score, th in models:
                for protocol in ['Seen-val', 'Fixed-0.4']:
                    tau = th if protocol == 'Seen-val' else .4
                    for group, mask in masks.items():
                        metrics = group_metrics(score, tau, d, gt, pred, mask, local[group], protocol == 'Fixed-0.4')
                        details.append(dict(split=split, backbone=bb, model=model, seed=seed, group=group, protocol=protocol, threshold=tau, **metrics))
            print('completed', split, bb, flush=True)
    def aggregate(bb, model, group, protocol):
        rs = [r for r in details if r['backbone'] == bb and r['model'] == model and r['group'] == group and r['protocol'] == protocol]
        assert len(rs) == (15 if model == 'Verifier' else 5)
        return dict(Model=LABELS[bb] + (' + Verifier' if model == 'Verifier' else ''), **{k: None if rs[0][k] is None else float(np.mean([r[k] for r in rs])) for k in COLS})
    tables = {}
    for protocol in ['Seen-val', 'Fixed-0.4']:
        for group in ['All', 'Seen', 'Unseen']:
            tables[protocol+'/'+group] = [aggregate(bb, m, group, protocol) for bb in a.BBS for m in ['Baseline', 'Verifier']]
    degradation = []
    for bb in a.BBS:
        b = audit['macro'][bb+'_base']
        v = {k: float(np.mean([audit['macro'][f'target_specific_{s}_{bb}_to_{bb}'][k] for s in a.SEEDS])) for k in ['seen', 'unseen', 'gap']}
        shrink = b['gap']-v['gap']
        ci = bootstrap['transfer'][bb+'_to_'+bb]['gap_reduction']['ci95']
        degradation.append({'Model': LABELS[bb], 'Seen base': 100*b['seen'], 'Seen verified': 100*v['seen'],
            'Unseen base': 100*b['unseen'], 'Unseen verified': 100*v['unseen'], 'Gap base': 100*b['gap'], 'Gap verified': 100*v['gap'],
            'Gap reduction (pp)': 100*shrink, 'Relative reduction (%)': 100*shrink/b['gap'], '95% CI (pp)': f'[{100*ci[0]:.2f}, {100*ci[1]:.2f}]'})
    ablations = []
    for mode in ['fixed_prior', 'none', 'unsigned', 'no_direction', 'visual_only', 'kinetic_only']:
        row = aggregate('flash', 'Ablation:'+mode, 'Unseen', 'Seen-val'); row['Model'] = mode; ablations.append(row)
    tables['Ablations/Unseen'] = ablations
    output = {'protocol': 'Five equal-weight splits; verifier rows average metrics over 3 seeds (not prediction ensemble). Localization uses unchanged target own published proposals, positive queries, IoU 0.50:0.05:0.95, max 10 proposals. Seen-val: target Seen validation Youden J on 100 grid points [0.01,0.99], accept score>=tau. Fixed-0.4: original paper decision accept score>0.4. Metrics in percent; localization and G-mIoU computed with repository official functions, rounded per split to 2 decimals then averaged.',
              'counts': counts, 'degradation': degradation, 'tables': tables, 'per_split_seed_metrics': details}
    (OUT/'paper_metrics.json').write_text(json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    with (OUT/'per_split_seed_metrics.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(details[0])); writer.writeheader(); writer.writerows(details)
    headers = ['Seen base', 'Seen verified', 'Unseen base', 'Unseen verified', 'Gap base', 'Gap verified', 'Gap reduction (pp)', 'Relative reduction (%)', '95% CI (pp)']
    md = ['# GMR Table 2 风格实验表格（2026-10-06）', '', '## 1. AUROC 退化缓解幅度', '', table(degradation, headers), '',
          'Gap = Seen AUROC − Unseen AUROC；绝对缩小量 = Gap_base − Gap_verified；相对缩小比例 = 绝对缩小量 / Gap_base。所有 AUROC 和 Gap 使用百分数，绝对差使用百分点（pp）。95% CI 为独立审计的 2,000 次配对视频聚类 bootstrap，对三个固定种子的指标先求均值。', '',
          '## 2. Table 2 风格主表：Seen 验证集阈值标定', '', '本表使用当前 Charades-STA semantic_existence_v2 的五划分，与原论文 Soccer-GMR 数据集不同。+Verifier 为目标自身候选机制 A 的自验证，五划分等权宏平均，再对 3 seeds 的指标求均值，不是预测集成。阈值仅用对应目标骨干的 Seen 验证集挑选；基线同样独立标定。所有数值为 %，越高越好。', '']
    for group in ['All', 'Seen', 'Unseen']:
        md += ['### '+group, '', table(tables['Seen-val/'+group], COLS), '']
    md += ['## 3. 原论文固定 τ=0.4 的补充表', '', '固定阈值使用原论文 score > τ 接受、score ≤ τ 拒绝。数值不应与 Seen 标定表混用。AUROC 与阈值无关。', '']
    for group in ['All', 'Seen', 'Unseen']:
        md += ['### '+group, '', table(tables['Fixed-0.4/'+group], COLS), '']
    md += ['## 4. FlashVTG 消融：Unseen，Seen 标定阈值', '', table(ablations, COLS), '',
           '消融为单种子 3407；none 是完整模型，不能与 3-seed 主表数值混用。kinetic_only 仍保留 CLIP 动作端点方向变量，因此不能标注为纯 SlowFast。', '',
           '## 5. 指标与边界', '',
           '- Rej-F1 的正类是无对应时刻的负查询；G-mIoU 包含空集拒绝与时间定位。All、Seen、Unseen 分别在各自查询集合上计算，不能通过平均 Seen/Unseen 指标替代 All。',
           '- mAP、mR@1、mR@5 在正查询上评估原始、未经过存在性阈值筛选的时间窗口；Verifier 不修改这些窗口，所以对应基线与 Verifier 的定位分数相同。',
           '- 当前测试集没有多时刻正查询时，mR+@5 不适用，记为 —；不能把评估器空集默认的 0 当成模型结果。',
           '- 本表只使用已落盘预测、特征和检查点，没有重新训练或修改原实验。G-mIoU、定位指标直接调用 eval/metrics.py。',
           '- 有效结论以表格为准：AUROC Gap 缩小不自动保证任意阈值下 Rej-F1 或 G-mIoU 全部提升。', '',
           '复算：`/home/guoxiangyu/miniconda3/envs/univtg/bin/python experiments/agy_test/paper_tables_20261006/build_tables.py`。', '',
           'LaTeX 使用 `booktabs`、`graphicx` 宏包；完整精度与各 split/seed 阈值见 paper_metrics.json 和 per_split_seed_metrics.csv。']
    (OUT/'PAPER_TABLES.md').write_text('\n'.join(md)+'\n')
    tex = latex(degradation, headers, 'AUROC degradation reduction on five semantic splits. Verifier results average three seeds; confidence intervals use 2,000 paired video-cluster resamples. Scores in percent; absolute reductions in percentage points.', 'tab:degradation')
    for protocol in ['Seen-val', 'Fixed-0.4']:
        for group in ['All', 'Seen', 'Unseen']:
            tex += latex(tables[protocol+'/'+group], COLS, 'Table-2-style evaluation on '+group+' queries of Charades-STA semantic splits. '+('Thresholds selected only on Seen validation.' if protocol == 'Seen-val' else 'Fixed threshold $\\tau=0.4$.')+' Five-split macro averages; verifier metrics average three seeds. All values in percent. Multi-moment recall is unavailable for single-moment ground truth.', 'tab:'+protocol.replace('.', '')+'-'+group)
    tex += latex(ablations, COLS, 'FlashVTG verifier ablations on Unseen queries, seed 3407, Seen-validation thresholds. The kinetic-only variant retains CLIP action endpoint evidence.', 'tab:ablation')
    (OUT/'paper_tables.tex').write_text(tex)
    a.MANIFEST['eval/metrics.py'] = {'sha256': hashlib.sha256((ROOT/'eval/metrics.py').read_bytes()).hexdigest()}
    (OUT/'input_manifest.json').write_text(json.dumps(a.MANIFEST, indent=2)+'\n')
    print(table(degradation, headers), flush=True)
    print(table(tables['Seen-val/Unseen'], COLS), flush=True)

if __name__ == '__main__':
    main()
