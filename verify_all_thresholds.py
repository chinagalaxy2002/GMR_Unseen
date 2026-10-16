"""One-click evaluation script for official test set (1,036 samples)
across fixed thresholds: 0.4, 0.5, 0.6 for:
1. E0 Baseline
2. Task A (Two-Stage Decoupled Fine-Tuning)
3. min neg (A3 Similarity Hard-Negative Contrastive Mining)
"""
import json
import sys
from pathlib import Path

# Add eval directory to python path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'eval'))
from eval_main import compute_gmr_cls, prepare_submission_for_gmiou, compute_G_mIoU

TEST_GT_PATH = Path('experiments/agy_test/soccer_flash_kim_mechanism_20261016/data/test.jsonl')
assert TEST_GT_PATH.exists(), f"Missing ground truth: {TEST_GT_PATH}"

MODELS = [
    {
        'name': 'E0 Baseline',
        'preds': Path('experiments/agy_test/soccer_flash_event_query_20261015/runs/E0/test_predictions.jsonl'),
        'mAP': 26.14,
        'AUROC': 74.27,
    },
    {
        'name': 'Task A (Decoupled)',
        'preds': Path('experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_A_twostage_s2024/test_predictions.jsonl'),
        'mAP': 26.18,
        'AUROC': 73.19,
    },
    {
        'name': 'min neg (A3 Hard-Negative)',
        'preds': Path('experiments/agy_test/soccer_flash_kim_mechanism_20261016/task_a_enhancement/runs/A3_similarity_hardneg_s2024/test_predictions.jsonl'),
        'mAP': 26.18,
        'AUROC': 75.03,
    }
]

THRESHOLDS = [0.4, 0.5, 0.6]


def evaluate_all():
    with open(TEST_GT_PATH) as f:
        ground_truth = [json.loads(line) for line in f]

    print("=" * 86)
    print("OFFICIAL TEST EVALUATION REPORT (1,036 SAMPLES: 544 POSITIVE + 492 NEGATIVE)")
    print("Fixed Thresholds: 0.4, 0.5, 0.6")
    print("=" * 86)

    table_data = []

    for m in MODELS:
        with open(m['preds']) as f:
            preds = [json.loads(line) for line in f]
        
        row_dict = {
            'name': m['name'],
            'mAP': m['mAP'],
            'AUROC': m['AUROC'],
            'thresholds': {}
        }

        for th in THRESHOLDS:
            gated, _ = prepare_submission_for_gmiou(preds, th, 10)
            gm = compute_G_mIoU(gated, ground_truth, (1, 3, 5))
            cls_res = compute_gmr_cls(preds, ground_truth, (th,))['per_threshold']
            c = next(iter(cls_res.values()))

            row_dict['thresholds'][th] = {
                'G-mIoU@1': gm['G-mIoU@1'],
                'G-mIoU@3': gm['G-mIoU@3'],
                'G-mIoU@5': gm['G-mIoU@5'],
                'Rej-F1': c['Rej-F1'],
                'N-acc': c['Rej-R'],
                'Pos-Rec': round(100.0 * c['TP'] / (c['TP'] + c['FN']), 2),
                'TP': c['TP'], 'TN': c['TN'], 'FP': c['FP'], 'FN': c['FN']
            }
        table_data.append(row_dict)

    # Print summary table
    print(f"\n{'Model':<28} | {'Thresh':<6} | {'G-mIoU@1':<8} | {'G-mIoU@3':<8} | {'G-mIoU@5':<8} | {'Rej-F1':<8} | {'N-acc':<8} | {'Pos-Rec':<8}")
    print("-" * 100)

    for item in table_data:
        for i, th in enumerate(THRESHOLDS):
            t_data = item['thresholds'][th]
            m_label = item['name'] if i == 0 else ""
            print(f"{m_label:<28} | {th:<6.1f} | {t_data['G-mIoU@1']:>7.2f}% | {t_data['G-mIoU@3']:>7.2f}% | {t_data['G-mIoU@5']:>7.2f}% | {t_data['Rej-F1']:>7.2f}% | {t_data['N-acc']:>7.2f}% | {t_data['Pos-Rec']:>7.2f}%")
        print("-" * 100)

    # Print relative gains table
    print("\n" + "=" * 86)
    print("RELATIVE GAINS (DELTA) COMPARED TO E0 BASELINE")
    print("=" * 86)
    e0_data = table_data[0]['thresholds']
    for item in table_data[1:]:
        print(f"\n>>> {item['name']} vs E0 Baseline:")
        for th in THRESHOLDS:
            cur = item['thresholds'][th]
            base = e0_data[th]
            d_gm1 = cur['G-mIoU@1'] - base['G-mIoU@1']
            d_gm3 = cur['G-mIoU@3'] - base['G-mIoU@3']
            d_gm5 = cur['G-mIoU@5'] - base['G-mIoU@5']
            d_f1 = cur['Rej-F1'] - base['Rej-F1']
            d_nacc = cur['N-acc'] - base['N-acc']
            print(f"  Threshold {th:.1f}: G-mIoU@1: {d_gm1:+6.2f} pp | G-mIoU@3: {d_gm3:+6.2f} pp | G-mIoU@5: {d_gm5:+6.2f} pp | Rej-F1: {d_f1:+6.2f} pp | N-acc: {d_nacc:+6.2f} pp")

    return table_data


if __name__ == '__main__':
    evaluate_all()
