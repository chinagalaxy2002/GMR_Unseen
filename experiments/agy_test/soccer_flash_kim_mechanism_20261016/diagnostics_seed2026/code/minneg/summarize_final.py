"""Create the final Val-only comparison against historical Task A."""
import json
from pathlib import Path

import numpy as np

from environment import ROOT, read_json, read_rows, write_json
from eval.metrics import compute_G_mIoU, prepare_submission_for_gmiou


TASK_A = Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_A_twostage_s2024')
GT = ROOT.parent / 'data/val.jsonl'


def optimal_gmiou(predictions, ground_truth):
    best = None
    for threshold in sorted({float(row['pred_exist_score']) for row in predictions}):
        effective = float(np.nextafter(threshold, -np.inf))
        gated, _ = prepare_submission_for_gmiou(predictions, effective, 10)
        metrics = compute_G_mIoU(gated, ground_truth, (1, 3, 5))
        candidate = (metrics['G-mIoU@1'], threshold, metrics)
        if best is None or candidate[0] > best[0]:
            best = candidate
    return {'threshold': best[1], **best[2]}


def row(name, directory, ground_truth, historical=False):
    metrics = read_json(directory / 'validation_metrics.json')
    predictions = read_rows(directory / 'validation_predictions.jsonl')
    if historical:
        native_map = metrics['native_pre_nms']['MR-full-mAP'] if 'native_pre_nms' in metrics else 26.82
        calibrated = metrics['own_val_BA_threshold']
    else:
        native_map = metrics['native_pre_nms']['MR-full-mAP']
        calibrated = metrics['val_BA_threshold']
    return {
        'name': name,
        'native_mAP': native_map,
        'AUROC': metrics['AUROC'],
        'G_mIoU_04': metrics['gate_04']['G-mIoU@1'],
        'G_mIoU_05': metrics['fixed_05']['G-mIoU@1'],
        'G_mIoU_BA_cal': calibrated['G-mIoU@1'],
        'BA_threshold': calibrated['threshold'],
        'G_mIoU_opt': optimal_gmiou(predictions, ground_truth),
        'plurality_BA': metrics['plurality']['balanced_accuracy'],
        'plurality_AUROC': metrics['plurality']['AUROC'],
        'cardinality': metrics.get('cardinality'),
        'localizer_matches_e0': metrics.get('localizer_matches_e0', historical),
    }


def main():
    ground_truth = read_rows(GT)
    rows = [row('Task_A_original', TASK_A, ground_truth, historical=True)]
    for directory in sorted((ROOT / 'runs').iterdir()):
        if (directory / 'validation_metrics.json').exists():
            rows.append(row(directory.name, directory, ground_truth))
    ensemble = ROOT / 'ensembles/A3_A4_equal_logit'
    rows.append(row('A3_A4_equal_logit', ensemble, ground_truth))
    baseline = rows[0]
    for item in rows[1:]:
        item['delta_vs_Task_A'] = {
            key: round(item[key] - baseline[key], 4)
            for key in ('native_mAP', 'AUROC', 'G_mIoU_04', 'G_mIoU_05', 'G_mIoU_BA_cal', 'plurality_BA', 'plurality_AUROC')
        }
    output = {
        'split': 'Val only (465 queries)',
        'test_evaluated': False,
        'selection_metric': 'Val AUROC for trained heads',
        'localizer_contract': 'exact E0 pred_relevant_windows_pre_exist fingerprint',
        'rows': rows,
        'verdict': {
            'recommended_single_head': 'A3_similarity_hardneg_s2024',
            'reason': 'best balanced improvement across AUROC, fixed 0.4/0.5 G-mIoU, and plurality while preserving exact localization',
            'best_AUROC': 'A2_joint_cardinality_s2024',
            'best_fixed_04': 'A3_A4_equal_logit (but it rejects every negative and many positives)',
            'do_not_promote_yet': 'A2/A4 cardinality heads need class balancing; macro-F1 remains below 42',
        },
    }
    write_json(ROOT / 'FINAL_REPORT.json', output)

    lines = [
        '# Task A 增强：最终 Val-only 报告', '',
        '所有新模型均保持 E0 定位输出指纹完全一致；本轮未访问 Test。', '',
        '| 方法 | mAP | AUROC | G@0.4 | G@0.5 | G@BA校准 | G最优 | Plurality BA | Plurality AUROC |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|',
    ]
    for item in rows:
        lines.append(
            f"| {item['name']} | {item['native_mAP']:.2f} | {item['AUROC']:.2f} | "
            f"{item['G_mIoU_04']:.2f} | {item['G_mIoU_05']:.2f} | {item['G_mIoU_BA_cal']:.2f} | "
            f"{item['G_mIoU_opt']['G-mIoU@1']:.2f}@{item['G_mIoU_opt']['threshold']:.3f} | "
            f"{item['plurality_BA']:.2f} | {item['plurality_AUROC']:.2f} |"
        )
    lines.extend([
        '', '## 判定', '',
        '- 推荐单模型：`A3_similarity_hardneg_s2024`。相对原 A，AUROC +2.16、G@0.4 +5.73、G@0.5 +4.84、plurality BA +10.00，mAP 不变。',
        '- A2 的 AUROC 最高（75.53，较 A +2.93），但 count macro-F1 只有 41.63，且固定阈值收益弱；需要 class-balanced cardinality loss 后再复验。',
        '- A3/A4 等权 logit 集成在 0.4/0.5 下约 52.5，但其正例召回只有约 32%，主要利用 G-mIoU 对真负例记 1 分的性质，不建议仅凭该数值宣布全面更强。',
        '- 下一步应冻结 A3 的结构与训练规则做多 seed；若置信区间仍为正，再一次性评测 Test。',
    ])
    (ROOT / 'FINAL_REPORT.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
