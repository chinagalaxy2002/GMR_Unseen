"""Build the pre-specified equal-logit A3/A4 read-only ensemble on Val."""
import copy
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))

from environment import E0_RUN, make_dataset, options, read_json, read_rows, write_json, write_rows
from validation import validate
from eval.metrics import compute_G_mIoU, prepare_submission_for_gmiou


def merge_rows(left_rows, right_rows):
    right = {row['qid']: row for row in right_rows}
    merged = []
    for left in left_rows:
        other = right[left['qid']]
        row = copy.deepcopy(left)
        logit = 0.5 * (float(left['pred_exist_logit_raw']) + float(other['pred_exist_logit_raw']))
        row['pred_exist_logit_raw'] = logit
        row['pred_exist_logit'] = round(logit, 6)
        row['pred_exist_score'] = round(1.0 / (1.0 + math.exp(-logit)), 6)
        if 'pred_multi_logits_raw' in left and 'pred_multi_logits_raw' in other:
            row['pred_multi_logits_raw'] = [
                0.5 * (float(a) + float(b))
                for a, b in zip(left['pred_multi_logits_raw'], other['pred_multi_logits_raw'])
            ]
        merged.append(row)
    return merged


def main():
    jobs = read_json(ROOT / 'configs/jobs.json')['jobs']
    opt = options(jobs[0], 'cpu')
    val_data = make_dataset(opt, 'val')
    left = ROOT / 'runs/A3_similarity_hardneg_s2024'
    right = ROOT / 'runs/A4_combined_readonly_s2024'
    output = ROOT / 'ensembles/A3_A4_equal_logit'
    output.mkdir(parents=True, exist_ok=True)
    pre = merge_rows(read_rows(left / 'validation_predictions_pre_nms.jsonl'), read_rows(right / 'validation_predictions_pre_nms.jsonl'))
    post = merge_rows(read_rows(left / 'validation_predictions.jsonl'), read_rows(right / 'validation_predictions.jsonl'))
    report = validate(pre, post, val_data.data, opt, E0_RUN / 'validation_predictions_pre_nms.jsonl')
    candidates = sorted({float(row['pred_exist_score']) for row in post})
    best = None
    for threshold in candidates:
        effective = float(np.nextafter(threshold, -np.inf))
        gated, _ = prepare_submission_for_gmiou(post, effective, 10)
        metrics = compute_G_mIoU(gated, val_data.data, (1, 3, 5))
        item = (metrics['G-mIoU@1'], threshold, metrics)
        if best is None or item[0] > best[0]:
            best = item
    report['val_G_mIoU_optimal_threshold'] = {
        'threshold': best[1], **best[2], 'selection_data': 'Val only'
    }
    write_rows(output / 'validation_predictions_pre_nms.jsonl', pre)
    write_rows(output / 'validation_predictions.jsonl', post)
    write_json(output / 'validation_metrics.json', report)
    write_json(output / 'CONFIG.json', {
        'members': [left.name, right.name], 'fusion': 'equal average of raw existence logits',
        'trainable_parameters_added': 0, 'test_evaluated': False,
        'localization_contract': 'same exact E0 fingerprint',
    })
    print(report)


if __name__ == '__main__':
    main()
